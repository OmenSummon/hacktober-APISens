from typing import List, Optional
from fastapi import APIRouter, Query

from app.models.findings import Finding, SeverityLevel, FindingType
from app.routes.scan import get_latest_findings

router = APIRouter(prefix="/api/findings", tags=["Findings"])


@router.get("", response_model=List[Finding])
async def list_findings(
    severity: Optional[SeverityLevel] = Query(None, description="Filter findings by severity"),
    finding_type: Optional[FindingType] = Query(None, description="Filter findings by type"),
):
    """
    Retrieves security findings from the most recent scan.
    """
    findings = get_latest_findings()

    if severity:
        findings = [f for f in findings if f.severity == severity]

    if finding_type:
        findings = [f for f in findings if f.type == finding_type]

    return findings
