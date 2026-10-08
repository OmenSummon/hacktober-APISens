from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional, Set, Tuple
from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile

from app.detectors.drift_detector import DriftDetector
from app.detectors.risk_scorer import RiskScorer
from app.detectors.shadow_detector import ShadowEndpointDetector
from app.models.findings import Finding, FindingType
from app.models.openapi import NormalizedSpec
from app.models.scan import EndpointInventoryItem, ScanRequest, ScanResponse, ScanSummary
from app.models.traffic import TrafficRequest
from app.services.demo_data import DEMO_OPENAPI_SPEC, DEMO_TRAFFIC_REQUESTS
from app.services.normalizer import PathNormalizer
from app.services.openapi_parser import OpenAPIParser
from app.services.traffic_service import traffic_service

router = APIRouter(prefix="/api", tags=["Scan"])

# In-memory storage for latest scan result
_latest_scan_result: Optional[ScanResponse] = None


def get_latest_findings() -> List[Finding]:
    if _latest_scan_result:
        return _latest_scan_result.findings
    return []


def execute_scan(spec: NormalizedSpec, traffic: List[TrafficRequest]) -> ScanResponse:
    global _latest_scan_result

    # 1. Detect Shadow Endpoints
    shadow_findings, observed_endpoints = ShadowEndpointDetector.detect(spec, traffic)

    # 2. Detect Drift (methods, parameters, schema, auth)
    drift_findings = DriftDetector.detect(spec, traffic)

    all_findings = shadow_findings + drift_findings

    # 3. Deterministic Risk Scoring
    risk_score, risk_level = RiskScorer.calculate_system_risk(all_findings)

    # 4. Count discrepancies
    shadow_count = sum(1 for f in all_findings if f.type == FindingType.SHADOW_ENDPOINT)
    schema_count = sum(1 for f in all_findings if f.type == FindingType.SCHEMA_DRIFT)
    param_count = sum(1 for f in all_findings if f.type == FindingType.PARAMETER_DRIFT)

    # 5. Build Endpoint Inventory Table
    # Documented endpoints map
    documented_set: Set[Tuple[str, str]] = {(ep.method, ep.path) for ep in spec.endpoints}
    declared_templates = list({ep.path for ep in spec.endpoints})

    # Traffic request counts per normalized endpoint
    endpoint_traffic_counts: Dict[Tuple[str, str], int] = Counter()
    for req in traffic:
        resolved_path, _ = PathNormalizer.resolve_path(req.path, declared_templates)
        endpoint_traffic_counts[(req.method, resolved_path)] += 1

    all_endpoint_keys = set(documented_set).union(observed_endpoints)
    inventory_items: List[EndpointInventoryItem] = []

    # Map findings by endpoint for quick status assignment
    findings_by_ep: Dict[Tuple[str, str], List[Finding]] = defaultdict(list)
    for f in all_findings:
        findings_by_ep[(f.method, f.path)].append(f)

    for method, path in sorted(all_endpoint_keys, key=lambda x: (x[1], x[0])):
        is_doc = (method, path) in documented_set
        is_obs = (method, path) in observed_endpoints
        req_count = endpoint_traffic_counts.get((method, path), 0)

        ep_findings = findings_by_ep.get((method, path), [])

        if not is_doc and is_obs:
            status = "SHADOW"
            max_ep_score = max((f.risk_score for f in ep_findings), default=80)
        elif ep_findings:
            status = "DRIFT"
            max_ep_score = max((f.risk_score for f in ep_findings), default=45)
        elif is_doc and is_obs:
            status = "HEALTHY"
            max_ep_score = 0
        else:
            status = "UNOBSERVED"
            max_ep_score = 0

        if max_ep_score >= 90:
            ep_risk = "CRITICAL"
        elif max_ep_score >= 70:
            ep_risk = "HIGH"
        elif max_ep_score >= 40:
            ep_risk = "MEDIUM"
        else:
            ep_risk = "LOW"

        inventory_items.append(
            EndpointInventoryItem(
                method=method,
                endpoint=path,
                documented=is_doc,
                observed=is_obs,
                status=status,
                risk=ep_risk,
                request_count=req_count,
            )
        )

    summary = ScanSummary(
        total_documented_endpoints=len(spec.endpoints),
        total_observed_endpoints=len(observed_endpoints),
        shadow_endpoints=shadow_count,
        schema_drifts=schema_count,
        parameter_drifts=param_count,
        risk_score=risk_score,
        risk_level=risk_level,
    )

    response = ScanResponse(
        summary=summary,
        inventory=inventory_items,
        findings=all_findings,
    )

    _latest_scan_result = response
    return response


@router.post("/scan", response_model=ScanResponse)
async def run_scan(
    request: Request,
    payload: Optional[ScanRequest] = None,
    spec_file: Optional[UploadFile] = File(None),
    traffic_file: Optional[UploadFile] = File(None),
):
    """
    Primary API Sentinel Scan Engine.
    Accepts OpenAPI specification (YAML/JSON) and observed traffic.
    Compares specification vs reality, performs deterministic detection,
    and returns summary, inventory table, and prioritized findings.
    Supports both application/json body and multipart/form-data file uploads.
    """
    spec_text = ""
    traffic_list: List[TrafficRequest] = []

    content_type = request.headers.get("content-type", "")

    if "application/json" in content_type:
        try:
            body_json = await request.json()
            if isinstance(body_json, dict):
                req_obj = ScanRequest(**body_json)
                spec_text = req_obj.openapi_spec or ""
                traffic_list = req_obj.traffic or []
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON payload: {str(e)}")
    elif "multipart/form-data" in content_type:
        form = await request.form()
        uploaded_spec = form.get("spec_file")
        uploaded_traffic = form.get("traffic_file")
        raw_spec_field = form.get("openapi_spec")

        if uploaded_spec and hasattr(uploaded_spec, "read"):
            spec_bytes = await uploaded_spec.read()
            spec_text = spec_bytes.decode("utf-8", errors="replace")
        elif raw_spec_field and isinstance(raw_spec_field, str):
            spec_text = raw_spec_field

        if uploaded_traffic and hasattr(uploaded_traffic, "read"):
            t_bytes = await uploaded_traffic.read()
            traffic_list = traffic_service.parse_from_json(t_bytes)
    else:
        # Fallback if parsed by FastAPI dependency
        if payload:
            spec_text = payload.openapi_spec or ""
            traffic_list = payload.traffic or []

    # If no traffic provided, fallback to in-memory store
    if not traffic_list:
        traffic_list = traffic_service.get_all()

    if not spec_text:
        raise HTTPException(
            status_code=400,
            detail="OpenAPI specification is required. Provide 'openapi_spec' in body or upload 'spec_file'.",
        )

    if not traffic_list:
        raise HTTPException(
            status_code=400,
            detail="Observed traffic is required. Provide 'traffic' array or upload 'traffic_file'.",
        )

    try:
        spec = OpenAPIParser.parse(spec_text)
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=f"Failed to parse OpenAPI specification: {str(e)}",
        )

    return execute_scan(spec, traffic_list)


@router.post("/demo", response_model=ScanResponse)
async def run_demo_scan():
    """
    Instantly runs a full security scan using realistic demo data.
    Demonstrates shadow endpoint detection, schema drift, and risk scoring.
    """
    spec = OpenAPIParser.parse(DEMO_OPENAPI_SPEC)
    traffic = [TrafficRequest(**item) for item in DEMO_TRAFFIC_REQUESTS]
    traffic_service.clear()
    traffic_service.ingest(traffic)
    return execute_scan(spec, traffic)
