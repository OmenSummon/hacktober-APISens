from app.detectors.drift_detector import DriftDetector
from app.models.findings import FindingType
from app.models.traffic import TrafficRequest
from app.services.demo_data import DEMO_OPENAPI_SPEC
from app.services.openapi_parser import OpenAPIParser


def test_detect_undocumented_method():
    spec = OpenAPIParser.parse(DEMO_OPENAPI_SPEC)
    # DELETE /users is not defined in spec
    traffic = [
        TrafficRequest(method="DELETE", path="/users"),
    ]
    findings = DriftDetector.detect(spec, traffic)
    method_findings = [f for f in findings if f.type == FindingType.UNDOCUMENTED_METHOD]
    assert len(method_findings) == 1
    assert method_findings[0].endpoint == "DELETE /users"


def test_detect_parameter_drift():
    spec = OpenAPIParser.parse(DEMO_OPENAPI_SPEC)
    traffic = [
        TrafficRequest(
            method="GET",
            path="/users",
            query_params={"role": "superadmin", "show_deleted": "true"},
        ),
    ]
    findings = DriftDetector.detect(spec, traffic)
    param_findings = [f for f in findings if f.type == FindingType.PARAMETER_DRIFT]
    assert len(param_findings) == 1
    assert "role" in param_findings[0].details.undocumented_params
    assert "show_deleted" in param_findings[0].details.undocumented_params


def test_detect_schema_drift():
    spec = OpenAPIParser.parse(DEMO_OPENAPI_SPEC)
    traffic = [
        TrafficRequest(
            method="POST",
            path="/orders",
            headers={"Authorization": "Bearer sample_token"},
            body={
                "item_id": "item_123",
                "quantity": 1,
                "coupon": "SAVE50_SECRET",  # Undocumented field!
            },
        ),
    ]
    findings = DriftDetector.detect(spec, traffic)
    schema_findings = [f for f in findings if f.type == FindingType.SCHEMA_DRIFT]
    assert len(schema_findings) == 1
    assert schema_findings[0].details.undocumented_field == "coupon"


def test_detect_auth_mismatch():
    spec = OpenAPIParser.parse(DEMO_OPENAPI_SPEC)
    # POST /orders requires BearerAuth, but sent without auth headers and 200 status
    traffic = [
        TrafficRequest(
            method="POST",
            path="/orders",
            headers={},
            body={"item_id": "item_123", "quantity": 1},
            status_code=200,
        ),
    ]
    findings = DriftDetector.detect(spec, traffic)
    auth_findings = [f for f in findings if f.type == FindingType.AUTH_MISMATCH]
    assert len(auth_findings) == 1
    assert auth_findings[0].path == "/orders"
