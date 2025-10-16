"""
Health check endpoint for test-child (E-commerce instance).

This endpoint verifies that the test-child instance is operational
and that specialized agents can be instantiated correctly.
"""

from datetime import datetime
from typing import Dict, Any
from fastapi import FastAPI
from fastapi.responses import JSONResponse

import sys
from pathlib import Path

# Add parent directory to path
parent_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(parent_dir))

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


def check_specialized_agents() -> Dict[str, Any]:
    """
    Verify that specialized e-commerce agents can be loaded.

    Returns:
        Dict with agent status
    """
    try:
        # Import specialized agents
        test_child_dir = Path(__file__).resolve().parent.parent
        sys.path.insert(0, str(test_child_dir))

        from src.agents.product_owner import ProductOwnerAgent
        from src.agents.developer import DeveloperAgent

        # Check that they have domain context
        po_has_context = bool(ProductOwnerAgent.get_domain_context(ProductOwnerAgent))
        dev_has_context = bool(DeveloperAgent.get_domain_context(DeveloperAgent))

        return {
            "status": "healthy" if (po_has_context and dev_has_context) else "degraded",
            "product_owner_specialized": po_has_context,
            "developer_specialized": dev_has_context,
            "specialization": "e-commerce"
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@app.get("/api/health")
async def health_check():
    """
    Health check endpoint for test-child e-commerce instance.

    Returns system status, configuration, and agent specialization info.

    Returns:
        JSONResponse: Health check data
    """
    settings_status = check_settings()
    agents_status = check_specialized_agents()

    # Overall status is healthy only if both are healthy
    overall_status = "healthy"
    if settings_status["status"] == "unhealthy" or agents_status["status"] == "unhealthy":
        overall_status = "unhealthy"
    elif settings_status["status"] == "degraded" or agents_status["status"] == "degraded":
        overall_status = "degraded"

    health_data = {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": "OSOrganicAI Test-Child",
        "instance": "test-child-ecommerce",
        "version": "1.0.0",
        "environment": settings_status.get("checks", {}).get("environment", "unknown"),
        "components": {
            "settings": settings_status,
            "agents": agents_status,
            "api": {
                "status": "healthy",
                "framework": "FastAPI"
            }
        }
    }

    # Return 200 if healthy/degraded, 503 if unhealthy
    status_code = 200 if overall_status != "unhealthy" else 503

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
            "instance": "test-child-ecommerce",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        },
        status_code=200
    )


# Vercel serverless function handler
handler = app
