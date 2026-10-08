import yaml
from app.models.findings import Finding, FindingDetail, FindingType, SeverityLevel
from app.services.remediation import RemediationService


def test_remediation_shadow_endpoint_patch():
    finding = Finding(
        id="f-test-patch",
        type=FindingType.SHADOW_ENDPOINT,
        severity=SeverityLevel.HIGH,
        method="GET",
        endpoint="GET /admin/users",
        path="/admin/users",
        title="Shadow endpoint",
        description="Observed undocumented route",
        details=FindingDetail(),
    )
    patch_yaml = RemediationService.generate_patch(finding)
    assert "/admin/users" in patch_yaml
    parsed = yaml.safe_load(patch_yaml)
    assert "paths" in parsed
    assert "/admin/users" in parsed["paths"]
    assert "get" in parsed["paths"]["/admin/users"]


def test_remediation_parameter_drift_patch():
    finding = Finding(
        id="f-test-param",
        type=FindingType.PARAMETER_DRIFT,
        severity=SeverityLevel.MEDIUM,
        method="GET",
        endpoint="GET /users",
        path="/users",
        title="Undocumented params",
        description="Params found",
        details=FindingDetail(undocumented_params=["role", "show_deleted"]),
    )
    patch_yaml = RemediationService.generate_patch(finding)
    parsed = yaml.safe_load(patch_yaml)
    parameters = parsed["paths"]["/users"]["get"]["parameters"]
    names = [p["name"] for p in parameters]
    assert "role" in names
    assert "show_deleted" in names
