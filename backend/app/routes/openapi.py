from typing import Optional
from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.models.openapi import NormalizedSpec
from app.services.openapi_parser import OpenAPIParser

router = APIRouter(prefix="/api/openapi", tags=["OpenAPI"])


class ParseSpecPayload(BaseModel):
    spec: str


@router.post("/parse", response_model=NormalizedSpec)
async def parse_openapi_spec(
    payload: Optional[ParseSpecPayload] = None,
    file: Optional[UploadFile] = File(None),
):
    """
    Parses and normalizes an OpenAPI 3.x specification from raw text or uploaded file.
    """
    content = ""
    if file:
        file_bytes = await file.read()
        content = file_bytes.decode("utf-8", errors="replace")
    elif payload and payload.spec:
        content = payload.spec
    else:
        raise HTTPException(
            status_code=400,
            detail="Either a spec payload string or a file upload must be provided.",
        )

    try:
        normalized = OpenAPIParser.parse(content)
        return normalized
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=f"Failed to parse OpenAPI specification: {str(e)}",
        )
