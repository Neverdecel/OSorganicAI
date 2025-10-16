"""
Domain-Specialized Product Owner Agent for CHILD_TEMPLATE.

TODO: Customize this agent for your specific domain by:
1. Replacing CHILD_TEMPLATE with your project name
2. Updating get_domain_context() with your domain knowledge
3. (Optional) Customizing customize_prompt() for extra guidance

This agent inherits from the mother repository's ProductOwnerAgent
and adds domain-specific context and behavior.
"""

from typing import Optional, List, Dict, Any

# Import the mother repository's base Product Owner Agent
import sys
from pathlib import Path

# Add parent directory to path to import from mother repo
parent_dir = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(parent_dir))

from src.agents.product_owner import ProductOwnerAgent as BaseProductOwnerAgent


class ProductOwnerAgent(BaseProductOwnerAgent):
    """
    Domain-specialized Product Owner Agent.

    TODO: Update this docstring with your domain name and key specializations.

    This agent inherits all core functionality from the mother repository's
    ProductOwnerAgent but adds [YOUR DOMAIN] specific context when analyzing
    issues and asking clarifying questions.

    **[YOUR DOMAIN] Specialization:**
    TODO: List your domain-specific concerns here, for example:
    - [Key concern 1]
    - [Key concern 2]
    - [Key concern 3]

    **Extension Pattern:**
    - get_domain_context(): Adds domain knowledge
    - All other methods inherited without modification
    """

    def get_domain_context(self) -> str:
        """
        Get domain-specific context for this agent.

        TODO: Replace this placeholder with your actual domain context.

        Returns:
            str: Domain context string

        Example for Fintech:
            return '''
            ## Fintech Domain Context

            You are analyzing requirements for a fintech application.
            Always consider:
            1. **Regulatory Compliance**
               - KYC/AML requirements
               - SOC2, PCI-DSS compliance
               - Financial reporting standards

            2. **Transaction Security**
               - Encryption at rest and in transit
               - Fraud detection
               - Multi-factor authentication

            3. **Financial Operations**
               - Multi-currency support
               - Transaction reconciliation
               - Audit trails
            '''
        """
        return """
## YOUR DOMAIN Context

TODO: Replace this with your domain-specific context.

You are analyzing requirements for a [YOUR DOMAIN] application.
Always consider the following when analyzing issues:

### Core [YOUR DOMAIN] Concerns:
1. **[Key Area 1]**
   - [Specific consideration 1a]
   - [Specific consideration 1b]

2. **[Key Area 2]**
   - [Specific consideration 2a]
   - [Specific consideration 2b]

3. **[Key Area 3]**
   - [Specific consideration 3a]
   - [Specific consideration 3b]

### Compliance & Security:
- **[Regulation 1]**: [Description]
- **[Regulation 2]**: [Description]

### Performance Considerations:
- [Performance concern 1]
- [Performance concern 2]

When analyzing issues, **always ask clarifying questions** about these concerns
if they are not explicitly addressed in the issue description.

---
💡 **Tip**: Look at test-child/src/agents/product_owner.py for a complete e-commerce example.
"""

    def customize_prompt(self, base_prompt: str) -> str:
        """
        Customize prompts with domain-specific instructions.

        TODO: (Optional) Add extra prompt engineering for your domain.

        This method adds extra guidance to ensure the agent asks
        domain-relevant questions.

        Args:
            base_prompt: Base prompt from parent class

        Returns:
            str: Customized prompt

        Example:
            customization = '''
            When analyzing this issue, pay special attention to:
            - [Domain-specific aspect 1]
            - [Domain-specific aspect 2]
            '''
            return base_prompt + customization
        """
        customization = """

## [YOUR DOMAIN] Specific Instructions:
TODO: Add domain-specific instructions here.

When analyzing this issue, pay special attention to:
- [Key aspect 1]
- [Key aspect 2]
- [Key aspect 3]

If the issue involves [common domain scenario], ALWAYS ask about:
- [Question type 1]?
- [Question type 2]?
- [Question type 3]?
"""
        return base_prompt + customization


# Verification code (for testing)
if __name__ == "__main__":
    print("✅ Product Owner Agent template loaded")
    print("\n⚠️  TODO: Customize get_domain_context() with your domain knowledge")
    print("\nDomain Context Preview:")
    agent_class = ProductOwnerAgent
    context = agent_class.get_domain_context(agent_class)

    if "TODO" in context:
        print("❌ Domain context still contains TODOs - needs customization!")
    else:
        print("✅ Domain context has been customized")

    print(f"\nContext length: {len(context)} characters")
