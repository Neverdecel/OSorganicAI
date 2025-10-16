"""
E-commerce Specialized Product Owner Agent for test-child.

This agent inherits from the mother repository's ProductOwnerAgent
and adds e-commerce specific domain context and behavior.

Demonstrates template inheritance pattern:
- Inherits core logic from src.agents.product_owner.ProductOwnerAgent
- Overrides get_domain_context() to add e-commerce knowledge
- Can override other methods for further customization
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
    E-commerce specialized Product Owner Agent.

    This agent inherits all core functionality from the mother repository's
    ProductOwnerAgent but adds e-commerce specific context when analyzing
    issues and asking clarifying questions.

    **E-commerce Specialization:**
    - Considers inventory management
    - Thinks about payment processing (PCI-DSS compliance)
    - Addresses shipping and fulfillment
    - Handles cart abandonment and checkout flows
    - Understands order lifecycle

    **Extension Pattern:**
    - get_domain_context(): Adds e-commerce knowledge
    - All other methods inherited without modification
    """

    def get_domain_context(self) -> str:
        """
        Get e-commerce specific domain context.

        This context is injected into all LLM prompts, ensuring the
        Product Owner Agent asks e-commerce relevant questions.

        Returns:
            str: E-commerce domain context
        """
        return """
## E-commerce Domain Context

You are analyzing requirements for an **e-commerce platform**.
Always consider the following when analyzing issues and asking questions:

### Core E-commerce Concerns:
1. **Inventory Management**
   - Product availability and stock tracking
   - Out-of-stock handling and backorders
   - Multi-warehouse or multi-location inventory

2. **Payment Processing**
   - Payment gateway integrations (Stripe, PayPal, etc.)
   - PCI-DSS compliance requirements
   - Multiple payment methods support
   - Currency conversion and multi-currency support
   - Payment security and fraud prevention

3. **Shopping Cart & Checkout**
   - Cart persistence (session vs. database)
   - Guest checkout vs. registered users
   - Cart abandonment recovery
   - Checkout flow optimization
   - Mobile checkout experience

4. **Order Management**
   - Order lifecycle (pending → paid → shipped → delivered)
   - Order status notifications
   - Order cancellation and refunds
   - Order history and tracking

5. **Shipping & Fulfillment**
   - Shipping method options
   - Shipping cost calculation
   - Delivery tracking integration
   - International shipping considerations
   - Pickup vs. delivery options

6. **Product Catalog**
   - Product variants (size, color, etc.)
   - Product categories and taxonomies
   - Product search and filtering
   - Product recommendations
   - Product reviews and ratings

7. **Customer Experience**
   - User authentication and accounts
   - Wishlists and favorites
   - Email notifications
   - Mobile responsiveness
   - Accessibility (WCAG compliance)

8. **Business Logic**
   - Pricing rules and discounts
   - Promotional campaigns
   - Tax calculation
   - Multi-currency support
   - Commission calculations (if marketplace)

### Compliance & Security:
- **PCI-DSS**: For handling payment card data
- **GDPR**: For user data privacy (EU customers)
- **CCPA**: For California customers
- **ADA/WCAG**: For accessibility

### Performance Considerations:
- High traffic during sales events
- Product catalog caching
- Search performance with large catalogs
- Image optimization for product photos

When analyzing issues, **always ask clarifying questions** about these concerns
if they are not explicitly addressed in the issue description.
"""

    def customize_prompt(self, base_prompt: str) -> str:
        """
        Customize prompts with e-commerce specific instructions.

        This method adds extra guidance to ensure the agent asks
        e-commerce relevant questions.

        Args:
            base_prompt: Base prompt from parent class

        Returns:
            str: Customized prompt with e-commerce focus
        """
        customization = """

## E-commerce Specific Instructions:
When analyzing this issue, pay special attention to:
- Payment processing and security implications
- Impact on the checkout flow
- Inventory and stock management concerns
- Order lifecycle considerations
- Mobile shopping experience

If the issue involves payments, ALWAYS ask about:
- Which payment gateways should be supported?
- What happens if payment fails?
- How should we handle refunds?

If the issue involves products/inventory, ALWAYS ask about:
- How should out-of-stock items be handled?
- Do we need product variants (sizes, colors)?
- What inventory tracking is needed?

If the issue involves checkout, ALWAYS ask about:
- Should we support guest checkout?
- What shipping options are needed?
- How should cart abandonment be handled?
"""
        return base_prompt + customization


# Example usage (for testing):
if __name__ == "__main__":
    from src.utils.llm_factory import LLMFactory
    from src.config.settings import get_settings

    # This would normally be imported from actual implementations
    print("E-commerce Product Owner Agent loaded successfully!")
    print("\nDomain Context Preview:")
    agent_class = ProductOwnerAgent
    # We can't instantiate without dependencies, but we can show the context
    print(agent_class.get_domain_context(agent_class))
