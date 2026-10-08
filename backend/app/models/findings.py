from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class FindingType(str, Enum):
    SHADOW_ENDPOINT = "SHADOW_ENDPOINT"
    UNDOCUMENTED_METHOD = "UNDOCUMENTED_METHOD"
    PARAMETER_DRIFT = "PARAMETER_DRIFT"
    SCHEMA_DRIFT = "SCHEMA_DRIFT"
    AUTH_MISMATCH = "AUTH_MISMATCH"


class SeverityLevel(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class FindingDetail(BaseModel):
    is_authenticated: Optional[bool] = None
    owasp_category: Optional[str] = None
    impact: Optional[str] = None
    sample_request: Optional[Dict[str, Any]] = None
    undocumented_params: Optional[list[str]] = None
    undocumented_field: Optional[str] = None
    observed_value: Optional[Any] = None
    suggested_patch: Optional[str] = None
    extra: Dict[str, Any] = Field(default_factory=dict)


class Finding(BaseModel):
    id: str
    type: FindingType
    severity: SeverityLevel
    method: str
    endpoint: str
    path: str
    title: str
    description: str
    observed_count: int = 1
    risk_score: int = 50
    details: FindingDetail = Field(default_factory=FindingDetail)
