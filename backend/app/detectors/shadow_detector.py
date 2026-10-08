import hashlib
from collections import defaultdict
from typing import Dict, List, Set, Tuple

from app.detectors.risk_scorer import RiskScorer
from app.models.findings import Finding, FindingDetail, FindingType
from app.models.openapi import NormalizedSpec
from app.models.traffic import TrafficRequest
from app.services.normalizer import PathNormalizer


class ShadowEndpointDetector:
    """
    Detects undocumented endpoints present in observed traffic
    that do not exist in the declared OpenAPI specification (OWASP API9).
    """

    @classmethod
    def detect(
        cls, spec: NormalizedSpec, traffic: List[TrafficRequest]
    ) -> Tuple[List[Finding], Set[Tuple[str, str]]]:
        """
        Returns:
            - List of SHADOW_ENDPOINT findings
            - Set of (method, path) tuples representing all observed unique endpoints
        """
        documented_map: Dict[str, Set[str]] = defaultdict(set)
        for ep in spec.endpoints:
            documented_map[ep.method].add(ep.path)

        declared_templates = list({ep.path for ep in spec.endpoints})

        # Group observed traffic by resolved (method, path)
        grouped_requests: Dict[Tuple[str, str], List[TrafficRequest]] = defaultdict(list)
        all_observed_endpoints: Set[Tuple[str, str]] = set()

        for req in traffic:
            resolved_path, matched = PathNormalizer.resolve_path(
                req.path, declared_templates
            )
            key = (req.method, resolved_path)
            all_observed_endpoints.add(key)
            grouped_requests[key].append(req)

        findings: List[Finding] = []

        for (method, path), req_list in grouped_requests.items():
            # Check if this endpoint is documented in spec
            is_documented = path in documented_map.get(method, set())

            if not is_documented:
                # Also check if path exists with OTHER methods (handled by DriftDetector)
                path_exists_in_other_methods = any(
                    path in documented_map.get(m, set()) for m in documented_map
                )
                
                # If path doesn't exist anywhere in spec, it's a true shadow endpoint!
                if not path_exists_in_other_methods:
                    sample = req_list[0]
                    has_auth = bool(
                        sample.headers.get("authorization")
                        or sample.headers.get("Authorization")
                        or sample.headers.get("x-api-key")
                    )

                    score, severity = RiskScorer.score_finding(
                        FindingType.SHADOW_ENDPOINT, path, has_auth
                    )

                    fid_seed = f"shadow-{method.lower()}-{path}"
                    finding_id = f"finding-{hashlib.md5(fid_seed.encode()).hexdigest()[:8]}"

                    findings.append(
                        Finding(
                            id=finding_id,
                            type=FindingType.SHADOW_ENDPOINT,
                            severity=severity,
                            method=method,
                            endpoint=f"{method} {path}",
                            path=path,
                            title=f"Undocumented API Endpoint: {path}",
                            description=(
                                f"Endpoint '{method} {path}' was observed in live traffic "
                                f"({len(req_list)} requests) but is absent from the OpenAPI specification."
                            ),
                            observed_count=len(req_list),
                            risk_score=score,
                            details=FindingDetail(
                                is_authenticated=has_auth,
                                owasp_category="API9:2023 Improper Inventory Management",
                                impact=(
                                    "Shadow endpoints bypass security reviews and automated scanning, "
                                    "frequently exposing sensitive data or internal admin utilities."
                                ),
                                sample_request={
                                    "method": sample.method,
                                    "path": sample.path,
                                    "query_params": sample.query_params,
                                    "headers": {
                                        k: v
                                        for k, v in sample.headers.items()
                                        if k.lower() != "authorization"
                                    },
                                    "status_code": sample.status_code,
                                },
                            ),
                        )
                    )

        return findings, all_observed_endpoints
