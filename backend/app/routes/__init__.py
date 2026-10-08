from .health import router as health_router
from .openapi import router as openapi_router
from .traffic import router as traffic_router
from .scan import router as scan_router
from .findings import router as findings_router
from .ai import router as ai_router

__all__ = [
    "health_router",
    "openapi_router",
    "traffic_router",
    "scan_router",
    "findings_router",
    "ai_router",
]
