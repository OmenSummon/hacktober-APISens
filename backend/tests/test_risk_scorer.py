from app.detectors.risk_scorer import RiskScorer
from app.models.findings import Finding, FindingDetail, FindingType, SeverityLevel


def test_score_individual_finding():
    # Sensitive shadow endpoint should be CRITICAL (score >= 90)
    score_admin, sev_admin = RiskScorer.score_finding(
        FindingType.SHADOW_ENDPOINT, "/admin/system_info", is_authenticated=False
    )
    assert score_admin >= 90
    assert sev_admin == SeverityLevel.CRITICAL

    # Standard shadow endpoint without auth
    score_std, sev_std = RiskScorer.score_finding(
        FindingType.SHADOW_ENDPOINT, "/custom/data", is_authenticated=False
    )
    assert score_std == 85
    assert sev_std == SeverityLevel.HIGH

    # Schema drift
    score_schema, sev_schema = RiskScorer.score_finding(
        FindingType.SCHEMA_DRIFT, "/orders", is_authenticated=True
    )
    assert score_schema == 40
    assert sev_schema == SeverityLevel.MEDIUM


def test_calculate_system_risk_clean():
    score, level = RiskScorer.calculate_system_risk([])
    assert score == 0
    assert level == "CLEAN"


def test_calculate_system_risk_high():
    findings = [
        Finding(
            id="1",
            type=FindingType.SHADOW_ENDPOINT,
            severity=SeverityLevel.HIGH,
            method="GET",
            endpoint="GET /admin/users",
            path="/admin/users",
            title="Undocumented endpoint",
            description="desc",
            risk_score=85,
            details=FindingDetail(),
        ),
        Finding(
            id="2",
            type=FindingType.SCHEMA_DRIFT,
            severity=SeverityLevel.MEDIUM,
            method="POST",
            endpoint="POST /orders",
            path="/orders",
            title="Extra field",
            description="desc",
            risk_score=40,
            details=FindingDetail(),
        ),
    ]
    score, level = RiskScorer.calculate_system_risk(findings)
    assert score >= 60
    assert level in ("HIGH", "MEDIUM")
