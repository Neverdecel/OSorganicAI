"""
GitHub webhook handler for CHILD_TEMPLATE.

TODO: Replace CHILD_TEMPLATE with your project name.

This file uses your specialized agents instead of generic ones.
No modifications needed unless you want to customize webhook handling.
"""

import hmac
import hashlib
from typing import Dict, Any
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

# Import settings and utilities from mother repo
import sys
from pathlib import Path

parent_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(parent_dir))

from src.config.settings import get_settings
from src.utils.logger import configure_logging, get_logger
from src.utils.llm_factory import LLMFactory
from src.utils.supabase_client import create_supabase_client
from src.utils.github_api import create_github_client
from src.workflows.issue_handler import create_workflow_orchestrator

# Import YOUR SPECIALIZED agents
child_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(child_dir))

from src.agents.product_owner import ProductOwnerAgent
from src.agents.developer import DeveloperAgent


# Initialize settings
settings = get_settings()

# Configure logging
configure_logging(
    log_level=settings.log_level,
    log_format=settings.log_format
)

logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="CHILD_TEMPLATE Webhook Handler",
    description="GitHub webhook handler with domain-specialized agents",
    version="1.0.0"
)


def verify_github_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify GitHub webhook signature."""
    if not signature or not signature.startswith("sha256="):
        return False

    expected_signature = signature.split("=")[1]
    mac = hmac.new(secret.encode(), msg=payload, digestmod=hashlib.sha256)
    computed_signature = mac.hexdigest()

    return hmac.compare_digest(computed_signature, expected_signature)


def create_agents():
    """Create and configure domain-specialized agents."""
    logger.info("Creating specialized agents")

    llm = LLMFactory.from_settings(settings)

    github_client = create_github_client(
        token=settings.github_token,
        repo_name=settings.github_repo
    )

    supabase_client = create_supabase_client(
        url=settings.supabase_url,
        key=settings.supabase_service_role_key
    )

    # Create YOUR specialized agents
    po_agent = ProductOwnerAgent(
        llm=llm,
        vcs_client=github_client,
        db_client=supabase_client
    )

    dev_agent = DeveloperAgent(
        llm=llm,
        vcs_client=github_client,
        db_client=supabase_client
    )

    return po_agent, dev_agent


@app.post("/api/webhooks/github")
async def github_webhook(request: Request):
    """Handle GitHub webhook events with specialized agents."""
    try:
        event_type = request.headers.get("X-GitHub-Event")
        signature = request.headers.get("X-Hub-Signature-256")
        delivery_id = request.headers.get("X-GitHub-Delivery")

        logger.info(
            "Webhook received",
            event_type=event_type,
            delivery_id=delivery_id
        )

        body = await request.body()

        if not verify_github_signature(body, signature, settings.github_webhook_secret):
            logger.warning("Invalid webhook signature", delivery_id=delivery_id)
            raise HTTPException(status_code=401, detail="Invalid signature")

        payload = await request.json()

        # Create specialized agents
        po_agent, dev_agent = create_agents()
        orchestrator = create_workflow_orchestrator(po_agent, dev_agent)

        # Route based on event type
        if event_type == "issues":
            action = payload.get("action")
            if action == "opened":
                issue = payload.get("issue", {})
                repository = payload.get("repository", {})

                state = orchestrator.handle_new_issue(
                    issue_number=issue.get("number"),
                    issue_id=issue.get("id"),
                    issue_title=issue.get("title"),
                    issue_body=issue.get("body", ""),
                    repo_full_name=repository.get("full_name")
                )

                return JSONResponse(
                    content={
                        "status": "success",
                        "message": "Issue analyzed with domain context",
                        "conversation_status": state.status
                    },
                    status_code=200
                )

        elif event_type == "ping":
            logger.info("Ping event received")
            return JSONResponse(
                content={"status": "success", "message": "Pong!"},
                status_code=200
            )

        else:
            logger.info("Unsupported event type", event_type=event_type)
            return JSONResponse(
                content={"status": "ignored", "message": f"Event type '{event_type}' not handled"},
                status_code=200
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Webhook processing failed", error=str(e), exc_info=True)
        return JSONResponse(
            content={"status": "error", "message": str(e)},
            status_code=500
        )


# Vercel serverless function handler
handler = app
