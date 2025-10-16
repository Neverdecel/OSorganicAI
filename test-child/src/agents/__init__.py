"""
E-commerce specialized agents for test-child.

These agents inherit from the mother repository's base agents
and add e-commerce specific context and behavior.
"""

from test_child.src.agents.product_owner import ProductOwnerAgent
from test_child.src.agents.developer import DeveloperAgent


__all__ = [
    "ProductOwnerAgent",
    "DeveloperAgent",
]
