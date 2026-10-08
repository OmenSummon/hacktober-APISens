from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class TrafficRequest(BaseModel):
    method: str = Field(..., description="HTTP Method (GET, POST, etc.)")
    path: str = Field(..., description="Observed request path (e.g. /users/42)")
    query_params: Dict[str, Any] = Field(default_factory=dict)
    headers: Dict[str, str] = Field(default_factory=dict)
    body: Optional[Any] = None
    status_code: Optional[int] = 200
    timestamp: Optional[str] = None

    @field_validator("method")
    @classmethod
    def normalize_method(cls, v: str) -> str:
        return v.strip().upper()

    @field_validator("path")
    @classmethod
    def clean_path(cls, v: str) -> str:
        p = v.strip()
        if not p.startswith("/"):
            p = "/" + p
        # strip query parameters if mistakenly included in path
        if "?" in p:
            p = p.split("?")[0]
        # remove trailing slash except root
        if len(p) > 1 and p.endswith("/"):
            p = p.rstrip("/")
        return p


class TrafficBatch(BaseModel):
    requests: List[TrafficRequest] = Field(default_factory=list)
