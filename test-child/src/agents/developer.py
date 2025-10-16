"""
E-commerce Specialized Developer Agent for test-child.

This agent inherits from the mother repository's DeveloperAgent
and adds e-commerce specific tech stack, code patterns, and testing strategies.

Demonstrates template inheritance pattern:
- Inherits core code generation logic from src.agents.developer.DeveloperAgent
- Overrides get_domain_context() to specify e-commerce tech stack
- Can override other methods for further customization
"""

from typing import Optional, List, Dict, Any

# Import the mother repository's base Developer Agent
import sys
from pathlib import Path

# Add parent directory to path to import from mother repo
parent_dir = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(parent_dir))

from src.agents.developer import DeveloperAgent as BaseDeveloperAgent


class DeveloperAgent(BaseDeveloperAgent):
    """
    E-commerce specialized Developer Agent.

    This agent inherits all core functionality from the mother repository's
    DeveloperAgent but adds e-commerce specific tech stack, code patterns,
    and development considerations.

    **E-commerce Specialization:**
    - Python + FastAPI backend
    - Supabase PostgreSQL database
    - Stripe payment integration patterns
    - RESTful API design
    - E-commerce specific models (Product, Order, Cart, etc.)
    - Testing with pytest

    **Extension Pattern:**
    - get_domain_context(): Defines e-commerce tech stack
    - All other methods inherited without modification
    """

    def get_domain_context(self) -> str:
        """
        Get e-commerce specific tech stack and code patterns.

        This context guides the LLM to generate code following
        e-commerce best practices and using the specified tech stack.

        Returns:
            str: E-commerce tech stack context
        """
        return """
## E-commerce Tech Stack Context

You are generating code for an **e-commerce platform** with the following tech stack:

### Backend:
- **Language**: Python 3.10+
- **Framework**: FastAPI (async-first, type-safe)
- **Database**: Supabase PostgreSQL
- **ORM**: Direct SQL with Supabase client (no traditional ORM)
- **Payment**: Stripe API integration
- **Authentication**: Supabase Auth (JWT tokens)
- **Deployment**: Vercel Serverless Functions

### Code Patterns:

#### 1. Database Models (Pydantic)
```python
from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal

class Product(BaseModel):
    id: str
    name: str
    description: Optional[str]
    price: Decimal
    stock_quantity: int
    category: str
    image_url: Optional[str]

class Order(BaseModel):
    id: str
    user_id: str
    status: str  # pending, paid, shipped, delivered, cancelled
    total_amount: Decimal
    payment_intent_id: Optional[str]  # Stripe payment intent
    created_at: str
```

#### 2. API Endpoints (FastAPI)
```python
from fastapi import APIRouter, HTTPException, Depends
from typing import List

router = APIRouter(prefix="/api/products", tags=["products"])

@router.get("/", response_model=List[Product])
async def list_products(
    category: Optional[str] = None,
    min_price: Optional[Decimal] = None,
    max_price: Optional[Decimal] = None
):
    \"\"\"List products with optional filters.\"\"\"
    # Implementation here
    pass

@router.get("/{product_id}", response_model=Product)
async def get_product(product_id: str):
    \"\"\"Get product by ID.\"\"\"
    # Implementation here
    pass
```

#### 3. Supabase Queries
```python
from src.utils.supabase_client import get_supabase_client

supabase = get_supabase_client()

# Select with filters
products = supabase.table('products').select('*').eq('category', 'electronics').execute()

# Insert
order = supabase.table('orders').insert({
    'user_id': user_id,
    'total_amount': str(total),
    'status': 'pending'
}).execute()

# Update
supabase.table('orders').update({'status': 'paid'}).eq('id', order_id).execute()
```

#### 4. Stripe Payment Integration
```python
import stripe
from src.config.settings import get_settings

settings = get_settings()
stripe.api_key = settings.stripe_secret_key

# Create payment intent
intent = stripe.PaymentIntent.create(
    amount=int(total * 100),  # Amount in cents
    currency='usd',
    metadata={'order_id': order_id}
)

# Confirm payment
stripe.PaymentIntent.confirm(intent.id, payment_method=payment_method_id)
```

#### 5. Testing Patterns (pytest)
```python
import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def mock_supabase():
    \"\"\"Mock Supabase client.\"\"\"
    # Return mock
    pass

def test_create_order(mock_supabase):
    \"\"\"Test order creation endpoint.\"\"\"
    client = TestClient(app)
    response = client.post('/api/orders', json={...})
    assert response.status_code == 201
```

### E-commerce Specific Considerations:

#### Security:
- **Never store credit card numbers** - use Stripe tokens
- Implement **rate limiting** on payment endpoints
- Use **Row Level Security** in Supabase
- Validate all decimal amounts to prevent rounding errors

#### Data Integrity:
- Use **database transactions** for order creation (inventory + order + payment)
- Implement **optimistic locking** for inventory updates
- Log all payment transactions for audit trail

#### Performance:
- **Cache** product catalog data
- Use **database indexes** on frequently queried fields (category, price, etc.)
- Implement **pagination** for product listings
- Use **async/await** for all I/O operations

#### Error Handling:
- Handle Stripe API errors gracefully
- Implement retry logic for payment processing
- Return user-friendly error messages
- Log all errors for debugging

### File Organization:
```
api/
├── routes/
│   ├── products.py      # Product endpoints
│   ├── orders.py        # Order endpoints
│   ├── cart.py          # Shopping cart endpoints
│   └── payments.py      # Payment endpoints
src/
├── models/
│   ├── product.py       # Product Pydantic models
│   ├── order.py         # Order Pydantic models
│   └── cart.py          # Cart Pydantic models
├── services/
│   ├── payment_service.py    # Stripe integration
│   ├── inventory_service.py  # Inventory management
│   └── order_service.py      # Order logic
tests/
├── test_products.py
├── test_orders.py
└── test_payments.py
```

### Code Quality Standards:
- **Type hints** on all functions
- **Docstrings** with examples
- **Input validation** using Pydantic
- **Error handling** with try/except
- **Logging** for debugging
- **Test coverage** > 80%

When generating code:
1. Follow the patterns above
2. Include comprehensive error handling
3. Write tests alongside implementation
4. Consider edge cases (out of stock, payment failures, etc.)
5. Use async/await for database and API calls
6. Add clear comments explaining business logic
"""

    def customize_prompt(self, base_prompt: str) -> str:
        """
        Customize prompts with e-commerce development instructions.

        Args:
            base_prompt: Base prompt from parent class

        Returns:
            str: Customized prompt with e-commerce focus
        """
        customization = """

## E-commerce Development Guidelines:

### Payment Processing:
- ALWAYS use Stripe payment intents (not direct charges)
- Handle 3D Secure authentication
- Store payment_intent_id with orders for reconciliation
- Never log sensitive payment data

### Inventory Management:
- Check stock availability before allowing add-to-cart
- Use database transactions when decrementing inventory
- Handle race conditions with optimistic locking
- Implement out-of-stock notifications

### Order Lifecycle:
- Orders should transition: pending → paid → processing → shipped → delivered
- Send email notifications at each status change
- Allow order cancellation only before shipping
- Handle refunds via Stripe API

### Testing Requirements:
- Mock Stripe API calls in tests
- Test inventory race conditions
- Test payment failure scenarios
- Test order cancellation flow
- Use pytest fixtures for test data

### Code Structure:
- Separate business logic into service classes
- Keep route handlers thin (delegate to services)
- Use Pydantic for request/response validation
- Implement proper error responses (4xx, 5xx)
"""
        return base_prompt + customization


# Example usage (for testing):
if __name__ == "__main__":
    print("E-commerce Developer Agent loaded successfully!")
    print("\nDomain Context Preview:")
    agent_class = DeveloperAgent
    print(agent_class.get_domain_context(agent_class))
