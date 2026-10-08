from typing import Any, Dict, Optional
from fastapi import APIRouter
from pydantic import BaseModel

from app.ai.ollama_client import local_ai_client
from app.models.findings import Finding
from app.services.remediation import RemediationService

router = APIRouter(prefix="/api/ai", tags=["AI Analysis"])


class AnalyzeFindingRequest(BaseModel):
    finding: Finding
    model: Optional[str] = None


@router.post("/analyze")
async def analyze_finding(payload: AnalyzeFindingRequest) -> Dict[str, Any]:
    """
    Submits a detected finding for deep AI security reasoning.
    Uses local Ollama if available; seamlessly falls back to the deterministic
    security advisor engine if Ollama is offline.
    """
    return await local_ai_client.analyze_finding(
        finding=payload.finding,
        custom_model=payload.model,
    )


@router.post("/patch")
async def generate_openapi_patch(finding: Finding) -> Dict[str, str]:
    """
    Generates an OpenAPI 3.0 remediation patch in YAML for a given finding.
    """
    patch_yaml = RemediationService.generate_patch(finding)
    return {
        "finding_id": finding.id,
        "endpoint": finding.endpoint,
        "suggested_patch": patch_yaml,
    }
