import hashlib
from collections import defaultdict
from typing import Any, Dict, List, Set, Tuple

from app.detectors.risk_scorer import RiskScorer
from app.models.findings import Finding, FindingDetail, FindingType
from app.models.openapi import NormalizedEndpoint, NormalizedSpec
from app.models.traffic import TrafficRequest
from app.services.normalizer import PathNormalizer


class DriftDetector:
    """
    Detects API discrepancies and drifts:
    - Undocumented HTTP methods on known paths
    - Undocumented query parameters
    - Request body schema drift (unexpected fields)
    - Authentication security mismatches
    """

    @classmethod
    def detect(cls, spec: NormalizedSpec, traffic: List[TrafficRequest]) -> List[Finding]:
        findings: List[Finding] = []

        # Index documented endpoints by (method, path) and path -> List[NormalizedEndpoint]
        spec_by_endpoint: Dict[Tuple[str, str], NormalizedEndpoint] = {}
        paths_in_spec: Dict[str, List[NormalizedEndpoint]] = defaultdict(list)
        declared_templates = list({ep.path for ep in spec.endpoints})

        for ep in spec.endpoints:
            spec_by_endpoint[(ep.method, ep.path)] = ep
            paths_in_spec[ep.path].append(ep)

        # Group traffic by resolved (method, path)
        grouped_requests: Dict[Tuple[str, str], List[TrafficRequest]] = defaultdict(list)
        for req in traffic:
            resolved_path, _ = PathNormalizer.resolve_path(req.path, declared_templates)
            grouped_requests[(req.method, resolved_path)].append(req)

        # 1. Detect Undocumented HTTP Methods
        for (method, path), req_list in grouped_requests.items():
            if path in paths_in_spec and (method, path) not in spec_by_endpoint:
                score, severity = RiskScorer.score_finding(
                    FindingType.UNDOCUMENTED_METHOD, path
                )
                fid_seed = f"method-{method.lower()}-{path}"
                finding_id = f"finding-{hashlib.md5(fid_seed.encode()).hexdigest()[:8]}"
                findings.append(
                    Finding(
                        id=finding_id,
                        type=FindingType.UNDOCUMENTED_METHOD,
                        severity=severity,
                        method=method,
                        endpoint=f"{method} {path}",
                        path=path,
                        title=f"Undocumented HTTP Method {method} on {path}",
                        description=(
                            f"Path '{path}' exists in the OpenAPI specification, but method '{method}' "
                            f"is not documented (observed in {len(req_list)} requests)."
                        ),
                        observed_count=len(req_list),
                        risk_score=score,
                        details=FindingDetail(
                            owasp_category="API9:2023 Improper Inventory Management",
                            impact="Exposing undocumented HTTP verbs can allow unauthorized resource modifications.",
                        ),
                    )
                )

        # 2. Check Documented Endpoints for Parameter, Schema, and Auth Drifts
        for (method, path), req_list in grouped_requests.items():
            endpoint = spec_by_endpoint.get((method, path))
            if not endpoint:
                continue

            # A. Check Query Parameter Drift
            documented_params = {
                p.name.lower() for p in endpoint.parameters if p.in_location == "query"
            }
            observed_query_params: Set[str] = set()
            for r in req_list:
                if r.query_params and isinstance(r.query_params, dict):
                    observed_query_params.update(k.lower() for k in r.query_params.keys())

            undocumented_params = observed_query_params - documented_params
            if undocumented_params:
                score, severity = RiskScorer.score_finding(
                    FindingType.PARAMETER_DRIFT, path
                )
                params_list_str = ", ".join(sorted(undocumented_params))
                fid_seed = f"param-{method.lower()}-{path}-{params_list_str}"
                finding_id = f"finding-{hashlib.md5(fid_seed.encode()).hexdigest()[:8]}"
                findings.append(
                    Finding(
                        id=finding_id,
                        type=FindingType.PARAMETER_DRIFT,
                        severity=severity,
                        method=method,
                        endpoint=f"{method} {path}",
                        path=path,
                        title=f"Undocumented Query Parameters: {params_list_str}",
                        description=(
                            f"Observed requests to '{method} {path}' sent query parameters not declared "
                            f"in OpenAPI: [{params_list_str}]."
                        ),
                        observed_count=len(req_list),
                        risk_score=score,
                        details=FindingDetail(
                            undocumented_params=sorted(list(undocumented_params)),
                            owasp_category="API9:2023 Improper Inventory Management",
                            impact="Undocumented query parameters may enable filter bypasses or internal parameter injection.",
                        ),
                    )
                )

            # B. Check Request Body Schema Drift
            if endpoint.request_body_schema and isinstance(endpoint.request_body_schema, dict):
                declared_properties = set(
                    endpoint.request_body_schema.get("properties", {}).keys()
                )
                # If schema has declared properties, check for extra fields in request bodies
                if declared_properties:
                    extra_fields: Dict[str, Any] = {}
                    for r in req_list:
                        if isinstance(r.body, dict):
                            for body_key, val in r.body.items():
                                if body_key not in declared_properties:
                                    extra_fields[body_key] = val

                    for extra_field, sample_val in extra_fields.items():
                        score, severity = RiskScorer.score_finding(
                            FindingType.SCHEMA_DRIFT, path
                        )
                        fid_seed = f"schema-{method.lower()}-{path}-{extra_field}"
                        finding_id = f"finding-{hashlib.md5(fid_seed.encode()).hexdigest()[:8]}"
                        findings.append(
                            Finding(
                                id=finding_id,
                                type=FindingType.SCHEMA_DRIFT,
                                severity=severity,
                                method=method,
                                endpoint=f"{method} {path}",
                                path=path,
                                title=f"Undocumented Payload Property: {extra_field}",
                                description=(
                                    f"Payload for '{method} {path}' included undocumented field '{extra_field}' "
                                    f"absent from the OpenAPI requestBody schema."
                                ),
                                observed_count=len(req_list),
                                risk_score=score,
                                details=FindingDetail(
                                    undocumented_field=extra_field,
                                    observed_value=sample_val,
                                    owasp_category="API3:2023 Broken Object Property Level Authorization",
                                    impact="Accepting unexpected fields can lead to Mass Assignment vulnerabilities.",
                                ),
                            )
                        )

            # C. Check Authentication Mismatches
            if endpoint.is_authenticated:
                unauth_requests = [
                    r
                    for r in req_list
                    if not (
                        r.headers.get("authorization")
                        or r.headers.get("Authorization")
                        or r.headers.get("x-api-key")
                    )
                    and (r.status_code and r.status_code < 400)
                ]
                if unauth_requests:
                    score, severity = RiskScorer.score_finding(
                        FindingType.AUTH_MISMATCH, path
                    )
                    fid_seed = f"auth-{method.lower()}-{path}"
                    finding_id = f"finding-{hashlib.md5(fid_seed.encode()).hexdigest()[:8]}"
                    findings.append(
                        Finding(
                            id=finding_id,
                            type=FindingType.AUTH_MISMATCH,
                            severity=severity,
                            method=method,
                            endpoint=f"{method} {path}",
                            path=path,
                            title=f"Authentication Bypass Detected on {path}",
                            description=(
                                f"Endpoint '{method} {path}' is documented as requiring authentication, "
                                f"but {len(unauth_requests)} successful requests were received without credentials."
                            ),
                            observed_count=len(unauth_requests),
                            risk_score=score,
                            details=FindingDetail(
                                is_authenticated=False,
                                owasp_category="API8:2023 Security Misconfiguration",
                                impact="Unauthenticated access to protected resources allows unauthorized data access.",
                            ),
                        )
                    )

        return findings
