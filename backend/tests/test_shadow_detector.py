from app.detectors.shadow_detector import ShadowEndpointDetector
from app.models.findings import FindingType, SeverityLevel
from app.models.traffic import TrafficRequest
from app.services.demo_data import DEMO_OPENAPI_SPEC
from app.services.openapi_parser import OpenAPIParser


def test_detect_shadow_endpoints():
    spec = OpenAPIParser.parse(DEMO_OPENAPI_SPEC)
    traffic = [
        TrafficRequest(method="GET", path="/users"),
        TrafficRequest(method="GET", path="/users/42"),
        TrafficRequest(method="GET", path="/admin/users"),
        TrafficRequest(method="GET", path="/debug"),
    ]

    findings, observed_eps = ShadowEndpointDetector.detect(spec, traffic)

    # /admin/users and /debug must be flagged as shadow endpoints
    shadow_paths = {f.path for f in findings if f.type == FindingType.SHADOW_ENDPOINT}
    assert "/admin/users" in shadow_paths
    assert "/debug" in shadow_paths

    # /users and /users/{id} must NOT be flagged as shadow endpoints
    assert "/users" not in shadow_paths
    assert "/users/{id}" not in shadow_paths

    # Verify severity
    admin_finding = next(f for f in findings if f.path == "/admin/users")
    assert admin_finding.severity in (SeverityLevel.HIGH, SeverityLevel.CRITICAL)
    assert admin_finding.risk_score >= 80
