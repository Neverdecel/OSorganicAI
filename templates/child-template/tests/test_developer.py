"""
Unit tests for domain-specialized Developer Agent.

TODO: Customize these tests for your tech stack.
"""

import pytest
from unittest.mock import Mock
import sys
from pathlib import Path

parent_dir = Path(__file__).resolve().parent.parent.parent
child_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(child_dir))

from src.agents.developer import DeveloperAgent


@pytest.fixture
def mock_llm():
    llm = Mock()
    llm.invoke = Mock(return_value=Mock(content='{"files": []}'))
    return llm


@pytest.fixture
def specialized_dev_agent(mock_llm):
    return DeveloperAgent(
        llm=mock_llm,
        vcs_client=Mock(),
        db_client=Mock()
    )


class TestSpecializedDeveloperAgent:
    def test_has_tech_stack_context(self, specialized_dev_agent):
        """TODO: Update to check for YOUR tech stack."""
        context = specialized_dev_agent.get_domain_context()
        assert len(context) > 100

    def test_inherits_from_mother_repo(self, specialized_dev_agent):
        from src.agents.developer import DeveloperAgent as MotherDev
        assert isinstance(specialized_dev_agent, MotherDev)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
