"""
Health check endpoint for CHILD_TEMPLATE.

TODO: Replace CHILD_TEMPLATE with your project name.
"""

from datetime import datetime
from typing import Dict, Any
from fastapi import FastAPI
from fastapi.responses import JSONResponse

import sys
from pathlib import Path

parent_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(parent_dir))

from src.config.settings import get_settings


app = FastAPI()


def check_settings() -> Dict[str, Any]:
    """Check if all required settings are configured."""
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
    """Health check endpoint."""
    settings_status = check_settings()

    health_data = {
        "status": settings_status["status"],
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": "CHILD_TEMPLATE",
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

    status_code = 200 if settings_status["status"] != "unhealthy" else 503

    return JSONResponse(
        content=health_data,
        status_code=status_code
    )


@app.get("/api/health/ping")
async def ping():
    """Simple ping endpoint."""
    return JSONResponse(
        content={
            "message": "pong",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        },
        status_code=200
    )


# Vercel serverless function handler
handler = app
