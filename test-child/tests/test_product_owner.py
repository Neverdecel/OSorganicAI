"""
Unit tests for E-commerce specialized Product Owner Agent.

These tests verify that:
1. The specialized agent inherits core functionality from mother repo
2. E-commerce domain context is properly added
3. Prompt customization works as expected
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import sys
from pathlib import Path

# Add parent directories to path
parent_dir = Path(__file__).resolve().parent.parent.parent
test_child_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(test_child_dir))

from src.agents.product_owner import ProductOwnerAgent
from src.models.issue_analysis import IssueAnalysis


@pytest.fixture
def mock_llm():
    """Create a mock LangChain LLM."""
    llm = Mock()
    llm.invoke = Mock(return_value=Mock(content='{"needs_clarification": true}'))
    return llm


@pytest.fixture
def mock_vcs_client():
    """Create a mock VCS client."""
    return Mock()


@pytest.fixture
def mock_db_client():
    """Create a mock database client."""
    return Mock()


@pytest.fixture
def ecommerce_agent(mock_llm, mock_vcs_client, mock_db_client):
    """Create an e-commerce specialized Product Owner Agent."""
    return ProductOwnerAgent(
        llm=mock_llm,
        vcs_client=mock_vcs_client,
        db_client=mock_db_client
    )


class TestEcommerceProductOwnerAgent:
    """Test suite for e-commerce specialized Product Owner Agent."""

    def test_agent_instantiation(self, ecommerce_agent):
        """Test that the specialized agent can be instantiated."""
        assert ecommerce_agent is not None
        assert ecommerce_agent.agent_name == "ProductOwnerAgent"

    def test_has_domain_context(self, ecommerce_agent):
        """Test that the agent has e-commerce domain context."""
        context = ecommerce_agent.get_domain_context()

        assert context != ""
        assert "e-commerce" in context.lower() or "ecommerce" in context.lower()

        # Check for key e-commerce concepts
        assert "inventory" in context.lower()
        assert "payment" in context.lower()
        assert "shipping" in context.lower() or "cart" in context.lower()

    def test_domain_context_includes_pci_dss(self, ecommerce_agent):
        """Test that domain context includes PCI-DSS compliance."""
        context = ecommerce_agent.get_domain_context()
        assert "pci" in context.lower() or "payment" in context.lower()

    def test_domain_context_includes_inventory(self, ecommerce_agent):
        """Test that domain context mentions inventory management."""
        context = ecommerce_agent.get_domain_context()
        assert "inventory" in context.lower() or "stock" in context.lower()

    def test_system_prompt_inherited(self, ecommerce_agent):
        """Test that system prompt is inherited from mother repo."""
        prompt = ecommerce_agent.get_system_prompt()

        assert prompt != ""
        assert "Product Owner" in prompt or "Business Analyst" in prompt

    def test_customize_prompt_adds_ecommerce_focus(self, ecommerce_agent):
        """Test that prompt customization adds e-commerce specific guidance."""
        base_prompt = "Analyze this issue."
        customized_prompt = ecommerce_agent.customize_prompt(base_prompt)

        # Customized prompt should be longer
        assert len(customized_prompt) > len(base_prompt)

        # Should contain base prompt
        assert base_prompt in customized_prompt

        # Should mention e-commerce concerns
        assert "payment" in customized_prompt.lower() or "ecommerce" in customized_prompt.lower()

    def test_build_messages_includes_ecommerce_context(self, ecommerce_agent):
        """Test that message building includes e-commerce domain context."""
        messages = ecommerce_agent.build_messages(
            user_input="Test issue analysis"
        )

        assert len(messages) >= 2  # System message + user message

        # System message should include domain context
        system_message = messages[0]
        assert "inventory" in system_message.content.lower() or "payment" in system_message.content.lower()

    def test_inherits_analyze_issue_method(self, ecommerce_agent, mock_llm):
        """Test that analyze_issue method is inherited and works."""
        # Mock LLM response with valid JSON
        mock_response = Mock()
        mock_response.content = """{
            "needs_clarification": true,
            "is_complete": false,
            "questions": ["What payment gateways should be supported?"],
            "refined_description": null,
            "acceptance_criteria": [],
            "technical_considerations": [],
            "estimated_complexity": "medium",
            "suggested_labels": ["feature"]
        }"""
        mock_llm.invoke.return_value = mock_response

        # Mock database client
        ecommerce_agent.db_client.log_agent_action = Mock(return_value="mock-uuid")

        # Call inherited method
        analysis = ecommerce_agent.analyze_issue(
            issue_number=1,
            issue_title="Add payment processing",
            issue_body="We need to accept payments"
        )

        assert isinstance(analysis, IssueAnalysis)
        assert analysis.needs_clarification == True
        assert len(analysis.questions) > 0

    def test_format_github_comment_includes_agent_name(self, ecommerce_agent):
        """Test that GitHub comments include agent signature."""
        comment = ecommerce_agent.format_github_comment("Test comment")

        assert "Test comment" in comment
        assert "ProductOwnerAgent" in comment or "🤖" in comment

    def test_ecommerce_context_differs_from_generic(self, ecommerce_agent):
        """
        Test that e-commerce context is different from generic (mother) agent.

        This verifies the specialization actually happened.
        """
        # Import mother repo's generic agent
        from src.agents.product_owner import ProductOwnerAgent as GenericProductOwnerAgent

        # Create a mock generic agent
        mock_llm = Mock()
        mock_vcs = Mock()
        mock_db = Mock()

        generic_agent = GenericProductOwnerAgent(
            llm=mock_llm,
            vcs_client=mock_vcs,
            db_client=mock_db
        )

        generic_context = generic_agent.get_domain_context()
        ecommerce_context = ecommerce_agent.get_domain_context()

        # E-commerce should have more context than generic (which is empty)
        assert len(ecommerce_context) > len(generic_context)

        # E-commerce should mention domain-specific terms
        assert "inventory" in ecommerce_context.lower()
        assert "payment" in ecommerce_context.lower()


class TestEcommercePromptCustomization:
    """Test suite specifically for e-commerce prompt customization."""

    def test_payment_processing_questions(self, ecommerce_agent):
        """Test that payment-related issues trigger payment questions."""
        customized = ecommerce_agent.customize_prompt("User wants to add payment")

        assert "payment" in customized.lower()
        assert "gateway" in customized.lower() or "stripe" in customized.lower()

    def test_inventory_considerations(self, ecommerce_agent):
        """Test that inventory concerns are included in customization."""
        customized = ecommerce_agent.customize_prompt("Product catalog needed")

        assert "inventory" in customized.lower() or "stock" in customized.lower()

    def test_checkout_flow_guidance(self, ecommerce_agent):
        """Test that checkout-related guidance is provided."""
        customized = ecommerce_agent.customize_prompt("Implement checkout")

        assert "checkout" in customized.lower() or "cart" in customized.lower()


@pytest.mark.integration
class TestEcommerceAgentIntegration:
    """Integration tests requiring more complex setup."""

    def test_full_workflow_with_ecommerce_context(self, ecommerce_agent, mock_llm):
        """
        Test a complete workflow to ensure e-commerce context flows through.
        """
        # Mock LLM to return e-commerce specific analysis
        mock_response = Mock()
        mock_response.content = """{
            "needs_clarification": true,
            "is_complete": false,
            "questions": [
                "What payment gateways should be supported (Stripe, PayPal)?",
                "Should we support guest checkout?",
                "What inventory tracking is needed?"
            ],
            "refined_description": null,
            "acceptance_criteria": [],
            "technical_considerations": ["PCI-DSS compliance"],
            "estimated_complexity": "high",
            "suggested_labels": ["feature", "payment"]
        }"""
        mock_llm.invoke.return_value = mock_response

        # Mock database
        ecommerce_agent.db_client.log_agent_action = Mock(return_value="uuid")
        ecommerce_agent.db_client.create_conversation = Mock(return_value="conv-uuid")
        ecommerce_agent.db_client.get_conversation = Mock(return_value=None)

        # Mock VCS
        ecommerce_agent.vcs_client.create_issue_comment = Mock()
        ecommerce_agent.vcs_client.add_labels_to_issue = Mock()

        # Execute workflow
        state = ecommerce_agent.handle_issue_workflow(
            issue_number=1,
            issue_id=123,
            issue_title="Add payment processing",
            issue_body="Users need to pay for products",
            repo_full_name="test/repo"
        )

        # Verify e-commerce specific behavior
        assert state is not None
        assert state.status in ["needs_clarification", "ready_for_dev"]

        # Verify LLM was called with e-commerce context
        assert mock_llm.invoke.called
        call_args = mock_llm.invoke.call_args[0][0]

        # Check that system message includes e-commerce context
        system_message = call_args[0]
        assert "inventory" in system_message.content.lower() or "payment" in system_message.content.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
