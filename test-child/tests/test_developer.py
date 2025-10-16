"""
Unit tests for E-commerce specialized Developer Agent.

These tests verify that:
1. The specialized agent inherits core functionality from mother repo
2. E-commerce tech stack context is properly added
3. Code generation guidance is specialized for e-commerce
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

from src.agents.developer import DeveloperAgent


@pytest.fixture
def mock_llm():
    """Create a mock LangChain LLM."""
    llm = Mock()
    llm.invoke = Mock(return_value=Mock(content='{"files": []}'))
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
def ecommerce_dev_agent(mock_llm, mock_vcs_client, mock_db_client):
    """Create an e-commerce specialized Developer Agent."""
    return DeveloperAgent(
        llm=mock_llm,
        vcs_client=mock_vcs_client,
        db_client=mock_db_client
    )


class TestEcommerceDeveloperAgent:
    """Test suite for e-commerce specialized Developer Agent."""

    def test_agent_instantiation(self, ecommerce_dev_agent):
        """Test that the specialized agent can be instantiated."""
        assert ecommerce_dev_agent is not None
        assert ecommerce_dev_agent.agent_name == "DeveloperAgent"

    def test_has_domain_context(self, ecommerce_dev_agent):
        """Test that the agent has e-commerce tech stack context."""
        context = ecommerce_dev_agent.get_domain_context()

        assert context != ""
        assert "e-commerce" in context.lower() or "ecommerce" in context.lower()

    def test_domain_context_includes_tech_stack(self, ecommerce_dev_agent):
        """Test that domain context specifies e-commerce tech stack."""
        context = ecommerce_dev_agent.get_domain_context()

        # Should mention key technologies
        assert "python" in context.lower()
        assert "fastapi" in context.lower()
        assert "supabase" in context.lower() or "postgresql" in context.lower()

    def test_domain_context_includes_payment_integration(self, ecommerce_dev_agent):
        """Test that context includes payment integration guidance."""
        context = ecommerce_dev_agent.get_domain_context()

        assert "stripe" in context.lower() or "payment" in context.lower()

    def test_domain_context_includes_code_patterns(self, ecommerce_dev_agent):
        """Test that context includes e-commerce code patterns."""
        context = ecommerce_dev_agent.get_domain_context()

        # Should mention e-commerce models
        assert "product" in context.lower() or "order" in context.lower() or "cart" in context.lower()

    def test_domain_context_includes_security_guidance(self, ecommerce_dev_agent):
        """Test that security guidance is included for payments."""
        context = ecommerce_dev_agent.get_domain_context()

        assert "pci" in context.lower() or "security" in context.lower()
        assert "card" in context.lower() or "payment" in context.lower()

    def test_system_prompt_inherited(self, ecommerce_dev_agent):
        """Test that system prompt is inherited from mother repo."""
        prompt = ecommerce_dev_agent.get_system_prompt()

        assert prompt != ""
        assert "developer" in prompt.lower() or "code" in prompt.lower()

    def test_customize_prompt_adds_ecommerce_guidance(self, ecommerce_dev_agent):
        """Test that prompt customization adds e-commerce development guidance."""
        base_prompt = "Generate code for this feature."
        customized_prompt = ecommerce_dev_agent.customize_prompt(base_prompt)

        # Should be longer
        assert len(customized_prompt) > len(base_prompt)

        # Should contain base
        assert base_prompt in customized_prompt

        # Should mention e-commerce concerns
        assert "payment" in customized_prompt.lower() or "inventory" in customized_prompt.lower() or "order" in customized_prompt.lower()

    def test_build_messages_includes_ecommerce_context(self, ecommerce_dev_agent):
        """Test that message building includes e-commerce tech stack."""
        messages = ecommerce_dev_agent.build_messages(
            user_input="Generate payment processing code"
        )

        assert len(messages) >= 2

        # System message should include tech stack
        system_message = messages[0]
        assert "fastapi" in system_message.content.lower() or "python" in system_message.content.lower()

    def test_ecommerce_context_differs_from_generic(self, ecommerce_dev_agent):
        """
        Test that e-commerce context is different from generic agent.

        This verifies the specialization actually happened.
        """
        # Import mother repo's generic agent
        from src.agents.developer import DeveloperAgent as GenericDeveloperAgent

        # Create mock generic agent
        mock_llm = Mock()
        mock_vcs = Mock()
        mock_db = Mock()

        generic_agent = GenericDeveloperAgent(
            llm=mock_llm,
            vcs_client=mock_vcs,
            db_client=mock_db
        )

        generic_context = generic_agent.get_domain_context()
        ecommerce_context = ecommerce_dev_agent.get_domain_context()

        # E-commerce should have more specific context
        assert len(ecommerce_context) > len(generic_context)

        # E-commerce should mention domain-specific patterns
        assert "product" in ecommerce_context.lower() or "order" in ecommerce_context.lower()


class TestEcommerceCodeGenerationGuidance:
    """Test suite for e-commerce code generation guidance."""

    def test_payment_processing_guidance(self, ecommerce_dev_agent):
        """Test that payment code generation includes security guidance."""
        context = ecommerce_dev_agent.get_domain_context()

        # Should warn about not storing card numbers
        assert "never" in context.lower() or "don't" in context.lower()
        assert "card" in context.lower()

    def test_inventory_management_guidance(self, ecommerce_dev_agent):
        """Test that inventory code includes race condition handling."""
        context = ecommerce_dev_agent.get_domain_context()

        # Should mention transactions or locking
        assert "transaction" in context.lower() or "lock" in context.lower() or "inventory" in context.lower()

    def test_testing_guidance(self, ecommerce_dev_agent):
        """Test that testing guidance is included."""
        context = ecommerce_dev_agent.get_domain_context()

        assert "test" in context.lower() or "pytest" in context.lower()

    def test_api_design_patterns(self, ecommerce_dev_agent):
        """Test that API design patterns are included."""
        context = ecommerce_dev_agent.get_domain_context()

        assert "fastapi" in context.lower() or "api" in context.lower()
        assert "endpoint" in context.lower() or "router" in context.lower() or "route" in context.lower()


class TestEcommercePromptCustomization:
    """Test suite for e-commerce prompt customization."""

    def test_payment_feature_customization(self, ecommerce_dev_agent):
        """Test customization for payment-related features."""
        customized = ecommerce_dev_agent.customize_prompt("Implement payment processing")

        assert "payment" in customized.lower()
        assert "stripe" in customized.lower() or "gateway" in customized.lower()

    def test_inventory_feature_customization(self, ecommerce_dev_agent):
        """Test customization for inventory-related features."""
        customized = ecommerce_dev_agent.customize_prompt("Implement inventory tracking")

        assert "inventory" in customized.lower() or "stock" in customized.lower()

    def test_order_lifecycle_guidance(self, ecommerce_dev_agent):
        """Test that order lifecycle guidance is included."""
        customized = ecommerce_dev_agent.customize_prompt("Implement order management")

        assert "order" in customized.lower()
        # Should mention states or status
        assert "status" in customized.lower() or "state" in customized.lower() or "lifecycle" in customized.lower()


@pytest.mark.integration
class TestEcommerceDeveloperIntegration:
    """Integration tests for e-commerce developer agent."""

    def test_format_github_comment_includes_agent_name(self, ecommerce_dev_agent):
        """Test that GitHub comments include agent signature."""
        comment = ecommerce_dev_agent.format_github_comment("Code generated")

        assert "Code generated" in comment
        assert "DeveloperAgent" in comment or "🤖" in comment

    def test_messages_include_full_context(self, ecommerce_dev_agent):
        """Test that built messages include all e-commerce context."""
        messages = ecommerce_dev_agent.build_messages(
            user_input="Generate product catalog API",
            additional_context={"framework": "FastAPI"}
        )

        system_message = messages[0]
        content = system_message.content.lower()

        # Should have tech stack
        assert "python" in content or "fastapi" in content

        # Should have e-commerce patterns
        assert "product" in content or "order" in content or "ecommerce" in content

        # Should have additional context
        assert "fastapi" in content

    def test_agent_can_log_actions(self, ecommerce_dev_agent, mock_db_client):
        """Test that agent can log actions to database."""
        mock_db_client.log_agent_action = Mock(return_value="action-uuid")

        action_id = ecommerce_dev_agent.log_action(
            action_type="code_generated",
            payload={"files": 3}
        )

        assert action_id == "action-uuid"
        assert mock_db_client.log_agent_action.called


class TestEcommerceTechStackValidation:
    """Validate that the e-commerce tech stack is properly specified."""

    def test_specifies_python_version(self, ecommerce_dev_agent):
        """Test that Python version is specified."""
        context = ecommerce_dev_agent.get_domain_context()

        assert "python" in context.lower()
        assert "3.10" in context or "3.11" in context or "3." in context

    def test_specifies_database(self, ecommerce_dev_agent):
        """Test that database technology is specified."""
        context = ecommerce_dev_agent.get_domain_context()

        assert "supabase" in context.lower() or "postgresql" in context.lower()

    def test_specifies_payment_provider(self, ecommerce_dev_agent):
        """Test that payment provider is specified."""
        context = ecommerce_dev_agent.get_domain_context()

        assert "stripe" in context.lower()

    def test_includes_code_examples(self, ecommerce_dev_agent):
        """Test that context includes code examples."""
        context = ecommerce_dev_agent.get_domain_context()

        # Should have code blocks
        assert "```python" in context or "```" in context

        # Should have example patterns
        assert "class" in context or "def" in context or "async" in context


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
