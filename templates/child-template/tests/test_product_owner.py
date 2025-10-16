"""
Unit tests for domain-specialized Product Owner Agent.

TODO: Customize these tests for your domain by:
1. Updating test_has_domain_context() to check for your domain terms
2. Adding domain-specific test cases
3. Verifying your clarifying questions are domain-relevant
"""

import pytest
from unittest.mock import Mock
import sys
from pathlib import Path

# Add parent directories to path
parent_dir = Path(__file__).resolve().parent.parent.parent
child_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(child_dir))

from src.agents.product_owner import ProductOwnerAgent


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
def specialized_agent(mock_llm, mock_vcs_client, mock_db_client):
    """Create your domain-specialized Product Owner Agent."""
    return ProductOwnerAgent(
        llm=mock_llm,
        vcs_client=mock_vcs_client,
        db_client=mock_db_client
    )


class TestSpecializedProductOwnerAgent:
    """Test suite for domain-specialized Product Owner Agent."""

    def test_agent_instantiation(self, specialized_agent):
        """Test that the specialized agent can be instantiated."""
        assert specialized_agent is not None
        assert specialized_agent.agent_name == "ProductOwnerAgent"

    def test_has_domain_context(self, specialized_agent):
        """
        Test that the agent has domain-specific context.

        TODO: Update the assertion to check for YOUR domain terms.
        """
        context = specialized_agent.get_domain_context()

        assert context != ""
        assert len(context) > 100, "Domain context should be substantial"

        # TODO: Replace with your domain-specific checks
        # Example for fintech:
        # assert "fintech" in context.lower() or "kyc" in context.lower()

        # Example for healthcare:
        # assert "hipaa" in context.lower() or "patient" in context.lower()

        # Generic check (remove when you add specific checks):
        assert "domain" in context.lower() or "TODO" in context

    def test_domain_context_no_todos(self, specialized_agent):
        """
        Test that domain context has been customized (no TODOs remain).

        This test will FAIL until you customize get_domain_context().
        """
        context = specialized_agent.get_domain_context()

        # This assertion should pass after customization
        if "TODO" in context:
            pytest.skip("Domain context not yet customized - still contains TODOs")

        assert "TODO" not in context, "Domain context still contains TODOs - needs customization!"

    def test_system_prompt_inherited(self, specialized_agent):
        """Test that system prompt is inherited from mother repo."""
        prompt = specialized_agent.get_system_prompt()

        assert prompt != ""
        assert "Product Owner" in prompt or "Business Analyst" in prompt

    def test_build_messages_includes_domain_context(self, specialized_agent):
        """Test that message building includes domain context."""
        messages = specialized_agent.build_messages(
            user_input="Test issue analysis"
        )

        assert len(messages) >= 2  # System message + user message

        # System message should include domain context
        system_message = messages[0]
        assert len(system_message.content) > 0

    def test_inherits_from_mother_repo(self, specialized_agent):
        """Test that this agent inherits from mother repo's agent."""
        from src.agents.product_owner import ProductOwnerAgent as MotherPO

        assert isinstance(specialized_agent, MotherPO)

    # TODO: Add domain-specific tests
    # Example for e-commerce:
    # def test_payment_feature_questions(self, specialized_agent):
    #     """Test that payment features trigger payment-specific questions."""
    #     customized = specialized_agent.customize_prompt("Add payment processing")
    #     assert "payment" in customized.lower()

    # Example for fintech:
    # def test_compliance_considerations(self, specialized_agent):
    #     """Test that financial features trigger compliance questions."""
    #     context = specialized_agent.get_domain_context()
    #     assert "kyc" in context.lower() or "aml" in context.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
