from typing import List, Tuple
from app.models.findings import Finding, FindingType, SeverityLevel

SENSITIVE_PATH_KEYWORDS = {
    "admin", "debug", "internal", "secret", "private", "actuator",
    "root", "backdoor", "management", "config", "env", "dump"
}


class RiskScorer:
    """
    Deterministic rule-based risk scoring system for API Sentinel.
    Scores individual findings and overall system risk according to
    OWASP API Security Top 10 impact.
    """

    @classmethod
    def score_finding(
        cls, finding_type: FindingType, path: str, is_authenticated: bool = False
    ) -> Tuple[int, SeverityLevel]:
        """
        Calculates deterministic risk score (0-100) and severity for an individual finding.
        """
        clean_path_lower = path.lower()
        is_sensitive = any(kw in clean_path_lower for kw in SENSITIVE_PATH_KEYWORDS)

        if finding_type == FindingType.SHADOW_ENDPOINT:
            if is_sensitive:
                return 95, SeverityLevel.CRITICAL
            if not is_authenticated:
                return 85, SeverityLevel.HIGH
            return 75, SeverityLevel.HIGH

        if finding_type == FindingType.UNDOCUMENTED_METHOD:
            if is_sensitive:
                return 85, SeverityLevel.HIGH
            return 70, SeverityLevel.HIGH

        if finding_type == FindingType.AUTH_MISMATCH:
            return 75, SeverityLevel.HIGH

        if finding_type == FindingType.PARAMETER_DRIFT:
            # Sensitive query param names like debug, role, admin
            if any(kw in clean_path_lower for kw in ("role", "admin", "debug")):
                return 60, SeverityLevel.MEDIUM
            return 45, SeverityLevel.MEDIUM

        if finding_type == FindingType.SCHEMA_DRIFT:
            return 40, SeverityLevel.MEDIUM

        return 20, SeverityLevel.LOW

    @classmethod
    def calculate_system_risk(cls, findings: List[Finding]) -> Tuple[int, str]:
        """
        Calculates aggregate system risk score (0-100) and qualitative risk level.
        Formula: min(100, round(max_score * 0.6 + min(40, len(findings) * 5)))
        """
        if not findings:
            return 0, "CLEAN"

        max_score = max((f.risk_score for f in findings), default=0)
        finding_count_weight = min(40, len(findings) * 5)
        total_score = min(100, round(max_score * 0.6 + finding_count_weight))

        if total_score >= 90:
            level = "CRITICAL"
        elif total_score >= 75:
            level = "HIGH"
        elif total_score >= 40:
            level = "MEDIUM"
        elif total_score > 0:
            level = "LOW"
        else:
            level = "CLEAN"

        return total_score, level
