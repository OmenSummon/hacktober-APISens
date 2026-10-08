from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.routes import (
    ai_router,
    findings_router,
    health_router,
    openapi_router,
    scan_router,
    traffic_router,
)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "AI-Powered API Drift & Shadow Endpoint Detector.\n"
        "Compares declared OpenAPI 3.x specifications against observed production/staging traffic "
        "to pinpoint shadow endpoints (OWASP API9) and security misconfigurations (OWASP API8)."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(health_router)
app.include_router(openapi_router)
app.include_router(traffic_router)
app.include_router(scan_router)
app.include_router(findings_router)
app.include_router(ai_router)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint welcoming clients and linking to Swagger docs."""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
        "description": "AI-Powered API Drift & Shadow Endpoint Detector",
        "documentation": "/docs",
        "health": "/api/health",
        "owasp_targets": [
            "API9:2023 Improper Inventory Management",
            "API8:2023 Security Misconfiguration",
            "API3:2023 Broken Object Property Level Authorization",
        ],
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Sanitizes unexpected exceptions to prevent internal stack trace leakage."""
    origin = request.headers.get("origin")
    headers = {}
    if origin:
        headers["Access-Control-Allow-Origin"] = origin
        headers["Access-Control-Allow-Credentials"] = "true"
        
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred while processing the request.",
            "detail": str(exc),
        },
        headers=headers,
    )
