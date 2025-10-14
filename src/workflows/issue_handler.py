"""
Issue workflow orchestration for OSOrganicAI.

This module orchestrates the complete workflow from issue creation
to pull request generation.

Follows Single Responsibility Principle - only orchestrates workflows.
"""

from typing import Dict, Any, Optional
from datetime import datetime

from src.agents.product_owner import ProductOwnerAgent
from src.agents.developer import DeveloperAgent
from src.utils.logger import get_logger, RequestLogger
from src.models.issue_analysis import ConversationState
from src.models.code_generation import CodeGenerationResult


logger = get_logger(__name__)


class IssueWorkflowOrchestrator:
    """
    Orchestrates the complete issue-to-PR workflow.

    This class coordinates between Product Owner and Developer agents
    to handle the full lifecycle of an issue.

    Attributes:
        po_agent: Product Owner Agent instance
        dev_agent: Developer Agent instance
    """

    def __init__(
        self,
        po_agent: ProductOwnerAgent,
        dev_agent: DeveloperAgent
    ):
        """
        Initialize workflow orchestrator.

        Args:
            po_agent: Product Owner Agent instance
            dev_agent: Developer Agent instance
        """
        self.po_agent = po_agent
        self.dev_agent = dev_agent

        logger.info("Workflow orchestrator initialized")

    def handle_new_issue(
        self,
        issue_number: int,
        issue_id: int,
        issue_title: str,
        issue_body: str,
        repo_full_name: str
    ) -> ConversationState:
        """
        Handle a newly created issue.

        Triggers Product Owner Agent to analyze and clarify requirements.

        Args:
            issue_number: GitHub issue number
            issue_id: GitHub issue ID
            issue_title: Issue title
            issue_body: Issue description
            repo_full_name: Full repository name (owner/repo)

        Returns:
            ConversationState: Current conversation state

        Example:
            >>> state = orchestrator.handle_new_issue(
            ...     issue_number=42,
            ...     issue_id=123456,
            ...     issue_title="Add cart",
            ...     issue_body="Users need shopping cart",
            ...     repo_full_name="org/repo"
            ... )
        """
        with RequestLogger("handle_new_issue", issue_number=issue_number):
            logger.info(
                "Handling new issue",
                issue_number=issue_number,
                repo=repo_full_name
            )

            # Delegate to Product Owner Agent
            state = self.po_agent.handle_issue_workflow(
                issue_number=issue_number,
                issue_id=issue_id,
                issue_title=issue_title,
                issue_body=issue_body,
                repo_full_name=repo_full_name
            )

            logger.info(
                "New issue handled",
                issue_number=issue_number,
                status=state.status
            )

            return state

    def handle_issue_comment(
        self,
        issue_number: int,
        comment_body: str,
        repo_full_name: str
    ) -> Optional[ConversationState]:
        """
        Handle a comment on an issue (user response to questions).

        If the issue is in "needs-clarification" status, this processes
        the user's response and determines next steps.

        Args:
            issue_number: GitHub issue number
            comment_body: Comment text
            repo_full_name: Full repository name

        Returns:
            Optional[ConversationState]: Updated state or None if not handled

        Example:
            >>> state = orchestrator.handle_issue_comment(
            ...     issue_number=42,
            ...     comment_body="Stripe and PayPal",
            ...     repo_full_name="org/repo"
            ... )
        """
        with RequestLogger("handle_issue_comment", issue_number=issue_number):
            logger.info(
                "Handling issue comment",
                issue_number=issue_number
            )

            # Get conversation from database
            conversation = self.po_agent.db_client.get_conversation(
                issue_number=issue_number,
                repo_full_name=repo_full_name
            )

            if not conversation:
                logger.warning(
                    "No conversation found for comment",
                    issue_number=issue_number
                )
                return None

            # Only process if needs clarification
            if conversation["status"] != "needs_clarification":
                logger.info(
                    "Issue not in needs_clarification status, skipping",
                    issue_number=issue_number,
                    current_status=conversation["status"]
                )
                return None

            # Process user response
            analysis = self.po_agent.process_user_response(
                conversation_id=conversation["id"],
                user_responses=[comment_body]
            )

            # Update conversation
            self.po_agent.update_conversation_state(
                conversation_id=conversation["id"],
                status="ready_for_dev" if analysis.is_complete else "needs_clarification",
                analysis=analysis.model_dump()
            )

            # Take action based on updated analysis
            if analysis.needs_clarification:
                # Still need more info
                self.po_agent.ask_clarifying_questions(
                    issue_number=issue_number,
                    questions=analysis.questions
                )
            elif analysis.is_complete:
                # Ready for dev
                self.po_agent.mark_ready_for_development(
                    issue_number=issue_number,
                    refined_description=analysis.refined_description or "",
                    acceptance_criteria=analysis.acceptance_criteria,
                    suggested_labels=analysis.suggested_labels
                )

                # Optionally trigger automatic development
                # (commented out for now - can be enabled per child instance)
                # self.trigger_development(conversation["id"], issue_number, analysis)

            logger.info(
                "Issue comment handled",
                issue_number=issue_number,
                needs_clarification=analysis.needs_clarification
            )

            # Build state (simplified)
            state = ConversationState(
                issue_id=conversation["issue_id"],
                issue_number=issue_number,
                repo_full_name=repo_full_name,
                status="ready_for_dev" if analysis.is_complete else "needs_clarification",
                current_analysis=analysis
            )

            return state

    def handle_label_added(
        self,
        issue_number: int,
        label_name: str,
        repo_full_name: str
    ) -> Optional[CodeGenerationResult]:
        """
        Handle a label being added to an issue.

        If "ready-for-dev" label is added, trigger Developer Agent.

        Args:
            issue_number: GitHub issue number
            label_name: Label that was added
            repo_full_name: Full repository name

        Returns:
            Optional[CodeGenerationResult]: Result if dev was triggered

        Example:
            >>> result = orchestrator.handle_label_added(
            ...     issue_number=42,
            ...     label_name="ready-for-dev",
            ...     repo_full_name="org/repo"
            ... )
        """
        with RequestLogger("handle_label_added", issue_number=issue_number, label=label_name):
            logger.info(
                "Handling label added",
                issue_number=issue_number,
                label=label_name
            )

            # Only trigger on ready-for-dev label
            if label_name != "ready-for-dev":
                logger.debug(
                    "Ignoring non-trigger label",
                    label=label_name
                )
                return None

            # Get conversation
            conversation = self.po_agent.db_client.get_conversation(
                issue_number=issue_number,
                repo_full_name=repo_full_name
            )

            if not conversation:
                logger.warning(
                    "No conversation found for ready-for-dev label",
                    issue_number=issue_number
                )
                return None

            # Extract requirements from analysis
            analysis = conversation.get("analysis", {})
            requirements = analysis.get("refined_description", "")
            acceptance_criteria = analysis.get("acceptance_criteria", [])

            if not requirements:
                logger.warning(
                    "No refined requirements found, cannot trigger dev",
                    issue_number=issue_number
                )
                return None

            # Trigger Developer Agent
            result = self.dev_agent.handle_ready_for_dev_issue(
                conversation_id=conversation["id"],
                issue_number=issue_number,
                requirements=requirements,
                acceptance_criteria=acceptance_criteria
            )

            logger.info(
                "Development triggered",
                issue_number=issue_number,
                pr_created=result.pr_number is not None
            )

            return result

    def handle_pr_opened(
        self,
        pr_number: int,
        issue_number: Optional[int],
        repo_full_name: str
    ) -> None:
        """
        Handle a pull request being opened.

        Updates conversation state and logs the event.

        Args:
            pr_number: PR number
            issue_number: Optional linked issue number
            repo_full_name: Full repository name
        """
        logger.info(
            "Handling PR opened",
            pr_number=pr_number,
            issue_number=issue_number
        )

        if issue_number:
            # Update conversation status
            conversation = self.po_agent.db_client.get_conversation(
                issue_number=issue_number,
                repo_full_name=repo_full_name
            )

            if conversation:
                self.po_agent.update_conversation_state(
                    conversation_id=conversation["id"],
                    status="in_development"
                )

        logger.info(
            "PR opened event processed",
            pr_number=pr_number
        )

    def get_workflow_status(
        self,
        issue_number: int,
        repo_full_name: str
    ) -> Dict[str, Any]:
        """
        Get current workflow status for an issue.

        Args:
            issue_number: GitHub issue number
            repo_full_name: Full repository name

        Returns:
            Dict[str, Any]: Workflow status information

        Example:
            >>> status = orchestrator.get_workflow_status(42, "org/repo")
            >>> print(status["stage"])  # "needs_clarification", "ready_for_dev", etc.
        """
        conversation = self.po_agent.db_client.get_conversation(
            issue_number=issue_number,
            repo_full_name=repo_full_name
        )

        if not conversation:
            return {
                "exists": False,
                "stage": "not_started"
            }

        # Get related actions
        actions = self.po_agent.db_client.get_agent_actions(
            conversation_id=conversation["id"],
            limit=50
        )

        # Get code generation if exists
        code_gens = self.po_agent.db_client.select(
            table="code_generations",
            filters={"conversation_id": conversation["id"]},
            limit=1,
            order_by="-created_at"
        )

        return {
            "exists": True,
            "stage": conversation["status"],
            "issue_number": conversation["issue_number"],
            "created_at": conversation["created_at"],
            "updated_at": conversation["updated_at"],
            "action_count": len(actions),
            "has_code_generation": len(code_gens) > 0,
            "pr_number": code_gens[0]["pr_number"] if code_gens else None,
            "analysis": conversation.get("analysis")
        }


def create_workflow_orchestrator(
    po_agent: ProductOwnerAgent,
    dev_agent: DeveloperAgent
) -> IssueWorkflowOrchestrator:
    """
    Factory function to create workflow orchestrator.

    Args:
        po_agent: Product Owner Agent
        dev_agent: Developer Agent

    Returns:
        IssueWorkflowOrchestrator: Configured orchestrator

    Example:
        >>> orchestrator = create_workflow_orchestrator(po_agent, dev_agent)
    """
    return IssueWorkflowOrchestrator(po_agent, dev_agent)
