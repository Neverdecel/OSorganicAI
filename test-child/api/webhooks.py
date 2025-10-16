"""
GitHub webhook handler for test-child (E-commerce instance).

This is identical to the mother repository's webhook handler,
but uses the specialized e-commerce agents instead of generic ones.

This demonstrates that child instances can use the same webhook
infrastructure with specialized agents.
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

# Import SPECIALIZED agents from test-child
test_child_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(test_child_dir))

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
    title="Test-Child E-commerce Webhook Handler",
    description="GitHub webhook handler with e-commerce specialized agents",
    version="1.0.0"
)


def verify_github_signature(payload: bytes, signature: str, secret: str) -> bool:
    """
    Verify GitHub webhook signature.

    Args:
        payload: Request body as bytes
        signature: X-Hub-Signature-256 header value
        secret: Webhook secret

    Returns:
        bool: True if signature is valid
    """
    if not signature:
        return False

    if not signature.startswith("sha256="):
        return False

    expected_signature = signature.split("=")[1]

    mac = hmac.new(
        secret.encode(),
        msg=payload,
        digestmod=hashlib.sha256
    )
    computed_signature = mac.hexdigest()

    return hmac.compare_digest(computed_signature, expected_signature)


def create_agents():
    """
    Create and configure e-commerce specialized agents.

    This is the key difference from the mother repo: we instantiate
    the SPECIALIZED agents here instead of generic ones.

    Returns:
        Tuple of (ProductOwnerAgent, DeveloperAgent)
    """
    logger.info("Creating e-commerce specialized agents")

    # Create LLM
    llm = LLMFactory.from_settings(settings)

    # Create clients
    github_client = create_github_client(
        token=settings.github_token,
        repo_name=settings.github_repo
    )

    supabase_client = create_supabase_client(
        url=settings.supabase_url,
        key=settings.supabase_service_role_key
    )

    # Create SPECIALIZED e-commerce agents
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

    logger.info(
        "E-commerce agents created",
        po_agent=po_agent.agent_name,
        dev_agent=dev_agent.agent_name
    )

    return po_agent, dev_agent


@app.post("/api/webhooks/github")
async def github_webhook(request: Request):
    """
    Handle GitHub webhook events with e-commerce specialized agents.

    This endpoint is identical to the mother repo's webhook handler,
    but uses specialized agents under the hood.

    Returns:
        JSONResponse: Processing status
    """
    try:
        # Get headers
        event_type = request.headers.get("X-GitHub-Event")
        signature = request.headers.get("X-Hub-Signature-256")
        delivery_id = request.headers.get("X-GitHub-Delivery")

        logger.info(
            "Test-child webhook received",
            event_type=event_type,
            delivery_id=delivery_id,
            instance="test-child-ecommerce"
        )

        # Read body
        body = await request.body()

        # Verify signature
        if not verify_github_signature(body, signature, settings.github_webhook_secret):
            logger.warning(
                "Invalid webhook signature",
                delivery_id=delivery_id
            )
            raise HTTPException(status_code=401, detail="Invalid signature")

        # Parse JSON payload
        payload = await request.json()

        # Create specialized e-commerce agents
        po_agent, dev_agent = create_agents()

        # Create orchestrator (uses same workflow as mother)
        orchestrator = create_workflow_orchestrator(po_agent, dev_agent)

        # Route based on event type
        # (Same routing logic as mother repo)
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
                        "message": "Issue analyzed with e-commerce context",
                        "instance": "test-child-ecommerce",
                        "conversation_status": state.status
                    },
                    status_code=200
                )

        elif event_type == "ping":
            logger.info("Ping event received (test-child)")
            return JSONResponse(
                content={
                    "status": "success",
                    "message": "Pong from test-child e-commerce instance!",
                    "instance": "test-child-ecommerce"
                },
                status_code=200
            )

        else:
            logger.info(
                "Unsupported event type",
                event_type=event_type
            )
            return JSONResponse(
                content={
                    "status": "ignored",
                    "message": f"Event type '{event_type}' not handled",
                    "instance": "test-child-ecommerce"
                },
                status_code=200
            )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(
            "Test-child webhook processing failed",
            error=str(e),
            exc_info=True
        )
        return JSONResponse(
            content={
                "status": "error",
                "message": str(e),
                "instance": "test-child-ecommerce"
            },
            status_code=500
        )


# Vercel serverless function handler
handler = app
