"""
GitHub webhook handler for Vercel serverless functions.

This is the main entry point for GitHub events.
Receives webhooks, validates them, and routes to appropriate handlers.

Deployed as a Vercel serverless function at /api/webhooks
"""

import hmac
import hashlib
from typing import Dict, Any
from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.responses import JSONResponse

from src.config.settings import get_settings
from src.utils.logger import configure_logging, get_logger
from src.utils.llm_factory import LLMFactory
from src.utils.supabase_client import create_supabase_client
from src.utils.github_api import create_github_client
from src.agents.product_owner import ProductOwnerAgent
from src.agents.developer import DeveloperAgent
from src.workflows.issue_handler import create_workflow_orchestrator


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
    title="OSOrganicAI Webhook Handler",
    description="GitHub webhook handler for autonomous AI agents",
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

    Example:
        >>> is_valid = verify_github_signature(body, signature, secret)
    """
    if not signature:
        return False

    # GitHub sends signature as "sha256=<hash>"
    if not signature.startswith("sha256="):
        return False

    expected_signature = signature.split("=")[1]

    # Compute HMAC
    mac = hmac.new(
        secret.encode(),
        msg=payload,
        digestmod=hashlib.sha256
    )
    computed_signature = mac.hexdigest()

    # Constant-time comparison
    return hmac.compare_digest(computed_signature, expected_signature)


def create_agents():
    """
    Create and configure all agents.

    Returns:
        Tuple of (ProductOwnerAgent, DeveloperAgent)
    """
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

    # Create agents (dependency injection)
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
    """
    Handle GitHub webhook events.

    This endpoint receives all GitHub webhook events and routes them
    to the appropriate handlers.

    Returns:
        JSONResponse: Processing status
    """
    try:
        # Get headers
        event_type = request.headers.get("X-GitHub-Event")
        signature = request.headers.get("X-Hub-Signature-256")
        delivery_id = request.headers.get("X-GitHub-Delivery")

        logger.info(
            "Webhook received",
            event_type=event_type,
            delivery_id=delivery_id
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

        # Create agents
        po_agent, dev_agent = create_agents()

        # Create orchestrator
        orchestrator = create_workflow_orchestrator(po_agent, dev_agent)

        # Route based on event type
        if event_type == "issues":
            return await handle_issues_event(payload, orchestrator)

        elif event_type == "issue_comment":
            return await handle_issue_comment_event(payload, orchestrator)

        elif event_type == "pull_request":
            return await handle_pull_request_event(payload, orchestrator)

        elif event_type == "ping":
            logger.info("Ping event received")
            return JSONResponse(
                content={"status": "success", "message": "Pong!"},
                status_code=200
            )

        else:
            logger.info(
                "Unsupported event type",
                event_type=event_type
            )
            return JSONResponse(
                content={"status": "ignored", "message": f"Event type '{event_type}' not handled"},
                status_code=200
            )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(
            "Webhook processing failed",
            error=str(e),
            exc_info=True
        )
        return JSONResponse(
            content={"status": "error", "message": str(e)},
            status_code=500
        )


async def handle_issues_event(
    payload: Dict[str, Any],
    orchestrator
) -> JSONResponse:
    """
    Handle 'issues' event.

    Processes: opened, labeled, etc.

    Args:
        payload: GitHub webhook payload
        orchestrator: Workflow orchestrator

    Returns:
        JSONResponse: Processing status
    """
    action = payload.get("action")
    issue = payload.get("issue", {})
    repository = payload.get("repository", {})

    issue_number = issue.get("number")
    issue_id = issue.get("id")
    issue_title = issue.get("title")
    issue_body = issue.get("body", "")
    repo_full_name = repository.get("full_name")

    logger.info(
        "Processing issues event",
        action=action,
        issue_number=issue_number
    )

    if action == "opened":
        # New issue created
        state = orchestrator.handle_new_issue(
            issue_number=issue_number,
            issue_id=issue_id,
            issue_title=issue_title,
            issue_body=issue_body,
            repo_full_name=repo_full_name
        )

        return JSONResponse(
            content={
                "status": "success",
                "message": "Issue analyzed",
                "conversation_status": state.status
            },
            status_code=200
        )

    elif action == "labeled":
        # Label added to issue
        label = payload.get("label", {})
        label_name = label.get("name")

        result = orchestrator.handle_label_added(
            issue_number=issue_number,
            label_name=label_name,
            repo_full_name=repo_full_name
        )

        if result:
            return JSONResponse(
                content={
                    "status": "success",
                    "message": "Development triggered",
                    "pr_created": result.pr_number is not None,
                    "pr_number": result.pr_number
                },
                status_code=200
            )
        else:
            return JSONResponse(
                content={"status": "ignored", "message": "Label not a trigger"},
                status_code=200
            )

    else:
        return JSONResponse(
            content={"status": "ignored", "message": f"Action '{action}' not handled"},
            status_code=200
        )


async def handle_issue_comment_event(
    payload: Dict[str, Any],
    orchestrator
) -> JSONResponse:
    """
    Handle 'issue_comment' event.

    Processes user responses to clarifying questions.

    Args:
        payload: GitHub webhook payload
        orchestrator: Workflow orchestrator

    Returns:
        JSONResponse: Processing status
    """
    action = payload.get("action")
    issue = payload.get("issue", {})
    comment = payload.get("comment", {})
    repository = payload.get("repository", {})

    # Skip if comment is from a bot (avoid loops)
    if comment.get("user", {}).get("type") == "Bot":
        logger.info("Ignoring bot comment")
        return JSONResponse(
            content={"status": "ignored", "message": "Bot comment"},
            status_code=200
        )

    if action == "created":
        issue_number = issue.get("number")
        comment_body = comment.get("body", "")
        repo_full_name = repository.get("full_name")

        logger.info(
            "Processing issue comment",
            issue_number=issue_number
        )

        state = orchestrator.handle_issue_comment(
            issue_number=issue_number,
            comment_body=comment_body,
            repo_full_name=repo_full_name
        )

        if state:
            return JSONResponse(
                content={
                    "status": "success",
                    "message": "Comment processed",
                    "conversation_status": state.status
                },
                status_code=200
            )
        else:
            return JSONResponse(
                content={"status": "ignored", "message": "No active conversation"},
                status_code=200
            )

    return JSONResponse(
        content={"status": "ignored", "message": f"Action '{action}' not handled"},
        status_code=200
    )


async def handle_pull_request_event(
    payload: Dict[str, Any],
    orchestrator
) -> JSONResponse:
    """
    Handle 'pull_request' event.

    Updates conversation state when PR is opened/merged.

    Args:
        payload: GitHub webhook payload
        orchestrator: Workflow orchestrator

    Returns:
        JSONResponse: Processing status
    """
    action = payload.get("action")
    pr = payload.get("pull_request", {})
    repository = payload.get("repository", {})

    pr_number = pr.get("number")
    repo_full_name = repository.get("full_name")

    # Extract linked issue number from PR body
    pr_body = pr.get("body", "")
    issue_number = None

    # Simple parsing of "Closes #123" format
    if "Closes #" in pr_body or "closes #" in pr_body:
        import re
        match = re.search(r"[Cc]loses #(\d+)", pr_body)
        if match:
            issue_number = int(match.group(1))

    if action == "opened":
        orchestrator.handle_pr_opened(
            pr_number=pr_number,
            issue_number=issue_number,
            repo_full_name=repo_full_name
        )

        return JSONResponse(
            content={
                "status": "success",
                "message": "PR event processed"
            },
            status_code=200
        )

    return JSONResponse(
        content={"status": "ignored", "message": f"Action '{action}' not handled"},
        status_code=200
    )


# Vercel serverless function handler
# This is the actual entry point for Vercel
handler = app
