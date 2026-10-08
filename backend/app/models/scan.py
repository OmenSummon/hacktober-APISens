from typing import List, Optional
from pydantic import BaseModel, Field
from .findings import Finding
from .traffic import TrafficRequest


class ScanSummary(BaseModel):
    total_documented_endpoints: int = 0
    total_observed_endpoints: int = 0
    shadow_endpoints: int = 0
    schema_drifts: int = 0
    parameter_drifts: int = 0
    risk_score: int = 0
    risk_level: str = "CLEAN"


class EndpointInventoryItem(BaseModel):
    method: str
    endpoint: str
    documented: bool
    observed: bool
    status: str = Field(..., description="'HEALTHY', 'SHADOW', 'DRIFT', or 'UNOBSERVED'")
    risk: str = Field(..., description="'LOW', 'MEDIUM', 'HIGH', or 'CRITICAL'")
    request_count: int = 0


class ScanRequest(BaseModel):
    openapi_spec: Optional[str] = Field(
        None, description="OpenAPI specification text in YAML or JSON format"
    )
    traffic: Optional[List[TrafficRequest]] = Field(
        None, description="List of observed requests to analyze"
    )


class ScanResponse(BaseModel):
    summary: ScanSummary
    inventory: List[EndpointInventoryItem] = Field(default_factory=list)
    findings: List[Finding] = Field(default_factory=list)
