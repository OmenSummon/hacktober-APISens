from fastapi import APIRouter
from app.config import settings
from app.ai.ollama_client import local_ai_client

router = APIRouter(prefix="/api", tags=["Health"])


@router.get("/health")
async def health_check():
    """
    Health check endpoint returning system status and AI capability status.
    """
    ollama_online = await local_ai_client.is_available()
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "ai_status": "connected" if ollama_online else "offline (fallback active)",
        "ai_model": settings.OLLAMA_MODEL,
    }
