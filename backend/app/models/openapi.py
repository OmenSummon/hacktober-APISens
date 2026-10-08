from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class NormalizedParameter(BaseModel):
    name: str
    in_location: str = Field(..., description="'path', 'query', 'header', or 'cookie'")
    required: bool = False
    param_type: str = "string"
    default: Optional[Any] = None
    description: Optional[str] = None


class NormalizedEndpoint(BaseModel):
    method: str = Field(..., description="HTTP method in UPPERCASE (e.g. GET, POST)")
    path: str = Field(..., description="Canonical path template (e.g. /users/{id})")
    summary: Optional[str] = None
    description: Optional[str] = None
    parameters: List[NormalizedParameter] = Field(default_factory=list)
    request_body_schema: Optional[Dict[str, Any]] = None
    response_schemas: Dict[str, Any] = Field(default_factory=dict)
    security: List[str] = Field(default_factory=list)
    is_authenticated: bool = False

    @property
    def key(self) -> str:
        return f"{self.method} {self.path}"


class NormalizedSpec(BaseModel):
    title: str = "API Specification"
    version: str = "1.0.0"
    description: Optional[str] = None
    endpoints: List[NormalizedEndpoint] = Field(default_factory=list)
    raw_paths_count: int = 0
