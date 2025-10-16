"""
Integration tests for test-child e-commerce workflow.

These tests verify the complete workflow from issue creation to PR generation
using the specialized e-commerce agents.

Tests cover:
1. Full issue-to-PR workflow with e-commerce context
2. Agent collaboration (Product Owner → Developer)
3. E-commerce specific question flows
4. Webhook handler integration
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, AsyncMock
import sys
from pathlib import Path
import json

# Add parent directories to path
parent_dir = Path(__file__).resolve().parent.parent.parent
test_child_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(test_child_dir))

from src.workflows.issue_handler import create_workflow_orchestrator
from src.agents.product_owner import ProductOwnerAgent
from src.agents.developer import DeveloperAgent
from src.models.issue_analysis import IssueAnalysis
from src.models.code_generation import CodeGeneration, FileChange, CodeGenerationResult


@pytest.fixture
def mock_llm():
    """Create a mock LangChain LLM that returns e-commerce aware responses."""
    llm = Mock()
    return llm


@pytest.fixture
def mock_vcs_client():
    """Create a mock VCS client."""
    client = Mock()
    client.create_issue_comment = Mock()
    client.add_labels_to_issue = Mock()
    client.remove_labels_from_issue = Mock()
    client.create_branch = Mock(return_value=True)
    client.create_or_update_file = Mock(return_value=True)
    client.create_pull_request = Mock(return_value=Mock(number=123))
    return client


@pytest.fixture
def mock_db_client():
    """Create a mock database client."""
    client = Mock()
    client.create_conversation = Mock(return_value="conv-uuid-123")
    client.get_conversation = Mock(return_value=None)
    client.update_conversation_status = Mock()
    client.update_conversation_analysis = Mock()
    client.log_agent_action = Mock(return_value="action-uuid")
    client.create_code_generation = Mock(return_value="codegen-uuid")
    return client


@pytest.fixture
def ecommerce_po_agent(mock_llm, mock_vcs_client, mock_db_client):
    """Create e-commerce Product Owner Agent."""
    return ProductOwnerAgent(
        llm=mock_llm,
        vcs_client=mock_vcs_client,
        db_client=mock_db_client
    )


@pytest.fixture
def ecommerce_dev_agent(mock_llm, mock_vcs_client, mock_db_client):
    """Create e-commerce Developer Agent."""
    return DeveloperAgent(
        llm=mock_llm,
        vcs_client=mock_vcs_client,
        db_client=mock_db_client
    )


@pytest.fixture
def orchestrator(ecommerce_po_agent, ecommerce_dev_agent):
    """Create workflow orchestrator with e-commerce agents."""
    return create_workflow_orchestrator(ecommerce_po_agent, ecommerce_dev_agent)


class TestEcommerceWorkflowIntegration:
    """Test complete e-commerce workflow integration."""

    def test_payment_feature_workflow(self, orchestrator, mock_llm):
        """
        Test complete workflow for a payment-related feature.

        Verifies that:
        1. Product Owner asks e-commerce specific questions
        2. Developer generates e-commerce appropriate code
        """
        # Mock Product Owner LLM response (asking e-commerce questions)
        po_response = Mock()
        po_response.content = json.dumps({
            "needs_clarification": True,
            "is_complete": False,
            "questions": [
                "What payment gateways should be supported (Stripe, PayPal, etc.)?",
                "Should we support guest checkout or require account creation?",
                "What should happen if payment fails?",
                "Do we need to handle recurring payments or subscriptions?"
            ],
            "refined_description": None,
            "acceptance_criteria": [],
            "technical_considerations": ["PCI-DSS compliance", "Payment security"],
            "estimated_complexity": "high",
            "suggested_labels": ["feature", "payment", "high-priority"]
        })

        mock_llm.invoke = Mock(return_value=po_response)

        # Execute workflow for new issue
        state = orchestrator.handle_new_issue(
            issue_number=42,
            issue_id=123456,
            issue_title="Add payment processing to checkout",
            issue_body="Users need to be able to pay for their orders",
            repo_full_name="test-org/test-ecommerce"
        )

        # Verify state
        assert state is not None
        assert state.status == "needs_clarification"
        assert state.current_analysis.needs_clarification

        # Verify e-commerce specific questions were asked
        questions = state.current_analysis.questions
        assert any("payment" in q.lower() for q in questions)
        assert any("gateway" in q.lower() or "stripe" in q.lower() for q in questions)

        # Verify technical considerations include security
        assert any("pci" in tc.lower() or "security" in tc.lower()
                   for tc in state.current_analysis.technical_considerations)

    def test_inventory_feature_workflow(self, orchestrator, mock_llm):
        """
        Test workflow for an inventory-related feature.

        Verifies e-commerce inventory concerns are addressed.
        """
        po_response = Mock()
        po_response.content = json.dumps({
            "needs_clarification": True,
            "is_complete": False,
            "questions": [
                "Should we support multi-warehouse inventory?",
                "How should out-of-stock items be handled?",
                "Do we need low-stock notifications?",
                "Should we reserve inventory when items are added to cart?"
            ],
            "refined_description": None,
            "acceptance_criteria": [],
            "technical_considerations": ["Inventory race conditions", "Database transactions"],
            "estimated_complexity": "medium",
            "suggested_labels": ["feature", "inventory"]
        })

        mock_llm.invoke = Mock(return_value=po_response)

        state = orchestrator.handle_new_issue(
            issue_number=43,
            issue_id=123457,
            issue_title="Implement inventory tracking",
            issue_body="Track product stock levels",
            repo_full_name="test-org/test-ecommerce"
        )

        # Verify inventory-specific questions
        questions = state.current_analysis.questions
        assert any("inventory" in q.lower() or "stock" in q.lower() for q in questions)

        # Verify technical considerations mention race conditions
        assert any("race" in tc.lower() or "transaction" in tc.lower()
                   for tc in state.current_analysis.technical_considerations)

    def test_shopping_cart_workflow(self, orchestrator, mock_llm):
        """
        Test workflow for shopping cart feature.

        Verifies e-commerce cart concerns are addressed.
        """
        po_response = Mock()
        po_response.content = json.dumps({
            "needs_clarification": True,
            "is_complete": False,
            "questions": [
                "Should cart be session-based or database-persisted?",
                "Do we need cart abandonment recovery?",
                "Should anonymous users have carts?",
                "What is the cart expiration policy?"
            ],
            "refined_description": None,
            "acceptance_criteria": [],
            "technical_considerations": ["Session management", "Cart persistence"],
            "estimated_complexity": "medium",
            "suggested_labels": ["feature", "cart"]
        })

        mock_llm.invoke = Mock(return_value=po_response)

        state = orchestrator.handle_new_issue(
            issue_number=44,
            issue_id=123458,
            issue_title="Build shopping cart",
            issue_body="Users need to add products to cart",
            repo_full_name="test-org/test-ecommerce"
        )

        # Verify cart-specific questions
        questions = state.current_analysis.questions
        assert any("cart" in q.lower() for q in questions)
        assert any("session" in q.lower() or "persist" in q.lower() for q in questions)

    def test_issue_comment_handling(self, orchestrator, mock_llm, mock_db_client):
        """
        Test handling user responses to e-commerce questions.
        """
        # Mock existing conversation
        mock_db_client.get_conversation = Mock(return_value={
            "id": "conv-uuid",
            "issue_id": 123456,
            "issue_number": 42,
            "status": "needs_clarification",
            "analysis": {}
        })

        # Mock LLM response after user answers
        follow_up_response = Mock()
        follow_up_response.content = json.dumps({
            "needs_clarification": False,
            "is_complete": True,
            "questions": [],
            "refined_description": "Implement Stripe payment processing with guest checkout support",
            "acceptance_criteria": [
                "Users can pay with credit card via Stripe",
                "Guest checkout is supported",
                "Failed payments show user-friendly error messages"
            ],
            "technical_considerations": ["Use Stripe payment intents", "PCI-DSS compliance"],
            "estimated_complexity": "high",
            "suggested_labels": ["feature", "payment", "ready-for-dev"]
        })

        mock_llm.invoke = Mock(return_value=follow_up_response)

        # Handle user response
        state = orchestrator.handle_issue_comment(
            issue_number=42,
            comment_body="Use Stripe. Support guest checkout. Show clear error messages on failure.",
            repo_full_name="test-org/test-ecommerce"
        )

        # Verify issue is now ready for dev
        assert state is not None
        assert state.status == "ready_for_dev"
        assert state.current_analysis.is_complete
        assert len(state.current_analysis.acceptance_criteria) > 0


@pytest.mark.asyncio
class TestEcommerceWebhookIntegration:
    """Test webhook handler integration with e-commerce agents."""

    async def test_webhook_creates_ecommerce_agents(self):
        """
        Test that webhook handler instantiates e-commerce specialized agents.
        """
        # Import webhook app
        from test_child.api.webhooks import create_agents

        # Mock dependencies
        with patch('test_child.api.webhooks.LLMFactory') as mock_factory, \
             patch('test_child.api.webhooks.create_github_client') as mock_gh, \
             patch('test_child.api.webhooks.create_supabase_client') as mock_sb:

            mock_factory.from_settings = Mock(return_value=Mock())
            mock_gh.return_value = Mock()
            mock_sb.return_value = Mock()

            # Create agents
            po_agent, dev_agent = create_agents()

            # Verify they are e-commerce specialized
            assert po_agent is not None
            assert dev_agent is not None

            # Check they have e-commerce context
            assert len(po_agent.get_domain_context()) > 0
            assert len(dev_agent.get_domain_context()) > 0

            # Verify context includes e-commerce terms
            po_context = po_agent.get_domain_context().lower()
            dev_context = dev_agent.get_domain_context().lower()

            assert "ecommerce" in po_context or "commerce" in po_context or "inventory" in po_context
            assert "ecommerce" in dev_context or "fastapi" in dev_context or "stripe" in dev_context


class TestAgentCollaboration:
    """Test Product Owner and Developer agent collaboration."""

    def test_po_to_dev_handoff(self, ecommerce_po_agent, ecommerce_dev_agent, mock_llm, mock_db_client):
        """
        Test handoff from Product Owner to Developer.

        Simulates:
        1. PO refines requirements (with e-commerce context)
        2. Issue marked ready-for-dev
        3. Developer generates code (with e-commerce patterns)
        """
        # Step 1: PO analysis (ready for dev)
        po_response = Mock()
        po_response.content = json.dumps({
            "needs_clarification": False,
            "is_complete": True,
            "questions": [],
            "refined_description": "Implement REST API for product catalog with filtering by category and price range",
            "acceptance_criteria": [
                "GET /api/products returns all products",
                "Support category filter",
                "Support min/max price filters",
                "Return paginated results"
            ],
            "technical_considerations": ["Add database indexes", "Cache responses"],
            "estimated_complexity": "medium",
            "suggested_labels": ["feature", "api", "ready-for-dev"]
        })

        mock_llm.invoke = Mock(return_value=po_response)

        # Mock conversation
        mock_db_client.get_conversation = Mock(return_value={
            "id": "conv-uuid",
            "issue_id": 123456,
            "issue_number": 45,
            "status": "ready_for_dev",
            "analysis": {
                "refined_description": "Implement REST API for product catalog",
                "acceptance_criteria": ["GET /api/products returns all products"]
            }
        })

        # Step 2: Developer generates code
        dev_response = Mock()
        dev_response.content = json.dumps({
            "implementation_plan": "Create FastAPI router with product endpoints",
            "files": [
                {
                    "path": "api/routes/products.py",
                    "content": "# FastAPI product routes\nfrom fastapi import APIRouter",
                    "action": "create"
                }
            ],
            "tests": [
                {
                    "path": "tests/test_products.py",
                    "content": "# Product API tests\nimport pytest"
                }
            ],
            "dependencies": ["fastapi", "pydantic"],
            "technical_notes": ["Use Supabase for data", "Add caching"],
            "estimated_loc": 150
        })

        mock_llm.invoke = Mock(return_value=dev_response)
        mock_db_client.create_code_generation = Mock(return_value="codegen-uuid")

        # Generate code
        code_gen = ecommerce_dev_agent.generate_code(
            issue_number=45,
            requirements="Implement REST API for product catalog",
            acceptance_criteria=["GET /api/products returns all products"]
        )

        # Verify code generation includes e-commerce patterns
        assert code_gen is not None
        assert len(code_gen.files) > 0

        # Verify files mention e-commerce concepts
        file_contents = " ".join([f.content for f in code_gen.files])
        assert "fastapi" in file_contents.lower() or "api" in file_contents.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
