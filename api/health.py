"""
Health check endpoint for Vercel serverless functions.

Provides system status, version info, and dependency checks.

Deployed as a Vercel serverless function at /api/health
"""

from datetime import datetime
from typing import Dict, Any
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.config.settings import get_settings


app = FastAPI()


def check_settings() -> Dict[str, Any]:
    """
    Check if all required settings are configured.

    Returns:
        Dict with status and details
    """
    try:
        settings = get_settings()

        checks = {
            "ai_configured": bool(settings.ai_api_key and settings.ai_model_provider),
            "github_configured": bool(settings.github_token and settings.github_repo),
            "supabase_configured": bool(settings.supabase_url and settings.supabase_service_role_key),
            "environment": settings.app_env,
            "debug_mode": settings.debug,
        }

        all_healthy = all([
            checks["ai_configured"],
            checks["github_configured"],
            checks["supabase_configured"]
        ])

        return {
            "status": "healthy" if all_healthy else "degraded",
            "checks": checks
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@app.get("/api/health")
async def health_check():
    """
    Health check endpoint.

    Returns system status, configuration, and version information.

    Returns:
        JSONResponse: Health check data
    """
    settings_status = check_settings()

    health_data = {
        "status": settings_status["status"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": "OSOrganicAI",
        "version": "1.0.0",
        "environment": settings_status.get("checks", {}).get("environment", "unknown"),
        "components": {
            "settings": settings_status,
            "api": {
                "status": "healthy",
                "framework": "FastAPI"
            }
        }
    }

    # Return 200 if healthy/degraded, 503 if unhealthy
    status_code = 200 if settings_status["status"] != "unhealthy" else 503

    return JSONResponse(
        content=health_data,
        status_code=status_code
    )


@app.get("/api/health/ping")
async def ping():
    """
    Simple ping endpoint for basic connectivity checks.

    Returns:
        JSONResponse: Pong response
    """
    return JSONResponse(
        content={
            "message": "pong",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        },
        status_code=200
    )


# Vercel serverless function handler
handler = app
