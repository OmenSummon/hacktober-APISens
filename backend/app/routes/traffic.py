from typing import Optional
from fastapi import APIRouter, File, HTTPException, UploadFile

from app.models.traffic import TrafficBatch, TrafficRequest
from app.services.traffic_service import traffic_service

router = APIRouter(prefix="/api/traffic", tags=["Traffic"])


@router.post("")
async def ingest_traffic(
    batch: Optional[TrafficBatch] = None,
    file: Optional[UploadFile] = File(None),
):
    """
    Ingests observed API traffic requests via JSON batch body or JSON file upload.
    """
    if file:
        file_bytes = await file.read()
        try:
            requests = traffic_service.parse_from_json(file_bytes)
            count = traffic_service.ingest(requests)
            return {
                "message": f"Successfully ingested {count} requests from file '{file.filename}'.",
                "total_stored": len(traffic_service.get_all()),
                "sample_count": count,
            }
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid traffic file: {str(e)}")

    elif batch and batch.requests:
        count = traffic_service.ingest(batch.requests)
        return {
            "message": f"Successfully ingested {count} requests.",
            "total_stored": len(traffic_service.get_all()),
            "sample_count": count,
        }
    else:
        raise HTTPException(
            status_code=400,
            detail="Must provide requests array in body or upload a JSON traffic file.",
        )


@router.get("")
async def get_traffic():
    """Returns all currently stored traffic requests."""
    stored = traffic_service.get_all()
    return {
        "count": len(stored),
        "requests": stored[:100],  # Return up to 100 for inspection
    }


@router.delete("")
async def clear_traffic():
    """Clears the stored traffic buffer."""
    traffic_service.clear()
    return {"message": "Traffic store cleared successfully."}
