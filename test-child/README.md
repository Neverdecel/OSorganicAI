# Test-Child: E-commerce Specialized Instance

> **Internal test instance demonstrating OSOrganicAI template inheritance pattern**

This test-child instance showcases how to specialize the mother repository's generic AI agents for a specific domain: **e-commerce**.

## 🎯 Purpose

The test-child serves three critical functions:

1. **Validation**: Ensures template changes in the mother repository work end-to-end
2. **Documentation**: Demonstrates how to create domain-specialized child instances
3. **Testing**: Provides a safe sandbox for iterating on agent patterns

## 🏗️ Architecture

```
Mother Repository (Generic)
    ↓ inherits
Test-Child (E-commerce Specialized)
    ↓ validates
Template Pattern
```

### Inheritance Pattern

The test-child **inherits** core functionality from the mother repository and **specializes** it for e-commerce:

| Component | Mother Repo | Test-Child |
|-----------|-------------|------------|
| **Product Owner Agent** | Generic requirement refinement | + E-commerce context (payments, inventory, shipping) |
| **Developer Agent** | Generic code generation | + E-commerce tech stack (FastAPI, Stripe, Supabase) |
| **Webhook Handler** | Generic GitHub event routing | + E-commerce agent instantiation |
| **Health Check** | Basic status | + Agent specialization verification |

## 📦 What's Inside

### Specialized Agents

#### 1. Product Owner Agent (`src/agents/product_owner.py`)

**Specialization**: E-commerce domain context

**Adds**:
- Inventory management considerations
- Payment processing questions (PCI-DSS compliance)
- Shipping and fulfillment concerns
- Cart and checkout flow optimization
- Order lifecycle management

**Example Questions** (auto-generated for payment features):
```
🤔 Clarification Needed

1. What payment gateways should be supported (Stripe, PayPal)?
2. Should we support guest checkout or require account creation?
3. What should happen if payment fails?
4. Do we need to handle recurring payments or subscriptions?
```

#### 2. Developer Agent (`src/agents/developer.py`)

**Specialization**: E-commerce tech stack

**Defines**:
- **Backend**: Python 3.10+ with FastAPI
- **Database**: Supabase PostgreSQL
- **Payments**: Stripe API integration
- **Models**: Product, Order, Cart, Customer

**Code Patterns**:
```python
# Pydantic models for e-commerce
class Product(BaseModel):
    id: str
    name: str
    price: Decimal
    stock_quantity: int

# FastAPI endpoints with validation
@router.post("/api/orders")
async def create_order(order: OrderCreate):
    # E-commerce specific logic
    pass

# Stripe payment integration
intent = stripe.PaymentIntent.create(
    amount=int(total * 100),
    currency='usd'
)
```

## 🚀 Quick Start

### Prerequisites

1. Python 3.10+
2. Vercel CLI (for deployment)
3. GitHub repository
4. Supabase project
5. OpenAI/Anthropic API key

### Local Testing

```bash
# From test-child directory
cd test-child

# Install dependencies
pip install -r ../requirements.txt
pip install -r ../requirements-dev.txt

# Run tests
pytest tests/ -v

# Run specific test suite
pytest tests/test_product_owner.py -v
pytest tests/test_developer.py -v
pytest tests/test_integration.py -v
```

### Deployment to Vercel

```bash
# From test-child directory
vercel link

# Set environment variables
vercel env add AI_API_KEY
vercel env add GITHUB_TOKEN
vercel env add GITHUB_REPO
vercel env add SUPABASE_URL
vercel env add SUPABASE_SERVICE_ROLE_KEY
vercel env add GITHUB_WEBHOOK_SECRET

# Deploy
vercel --prod
```

## 🧪 Testing

The test-child includes comprehensive tests:

### Unit Tests

**Product Owner Agent** (`tests/test_product_owner.py`):
- ✅ Domain context includes e-commerce terms
- ✅ Prompt customization adds payment/inventory guidance
- ✅ Inherits core methods from mother repo
- ✅ Generates e-commerce specific questions

**Developer Agent** (`tests/test_developer.py`):
- ✅ Tech stack specifies FastAPI, Supabase, Stripe
- ✅ Code patterns include e-commerce models
- ✅ Security guidance for payments (PCI-DSS)
- ✅ Inherits code generation logic

### Integration Tests

**Complete Workflow** (`tests/test_integration.py`):
- ✅ Payment feature workflow (PO → Dev)
- ✅ Inventory feature workflow
- ✅ Shopping cart workflow
- ✅ Issue comment handling
- ✅ Agent collaboration

**Run all tests**:
```bash
pytest test-child/tests/ -v --cov=test-child/src
```

## 📊 Test Results

Expected test coverage:

```
tests/test_product_owner.py ............ [ 40% ]
tests/test_developer.py ............... [ 75% ]
tests/test_integration.py ............. [100% ]

==================== 45 passed in 12.5s ====================
Coverage: 87%
```

## 🔍 How Specialization Works

### Step 1: Import Base Agent

```python
# test-child/src/agents/product_owner.py
from src.agents.product_owner import ProductOwnerAgent as BaseProductOwnerAgent

class ProductOwnerAgent(BaseProductOwnerAgent):
    # Inherits all methods from mother repo
    pass
```

### Step 2: Override `get_domain_context()`

```python
def get_domain_context(self) -> str:
    return """
    ## E-commerce Domain Context

    You are analyzing requirements for an e-commerce platform.
    Always consider:
    - Inventory management
    - Payment processing (PCI-DSS)
    - Shipping and fulfillment
    - Cart and checkout flows
    """
```

### Step 3: (Optional) Override `customize_prompt()`

```python
def customize_prompt(self, base_prompt: str) -> str:
    return base_prompt + """

    If the issue involves payments, ALWAYS ask about:
    - Which payment gateways?
    - What happens if payment fails?
    """
```

### That's It!

All other methods (`analyze_issue`, `handle_issue_workflow`, etc.) are inherited without modification.

## 🔗 How Test-Child Relates to Mother

### Files Inherited (Used Directly)

- `src/config/settings.py` - Configuration management
- `src/utils/logger.py` - Structured logging
- `src/utils/llm_factory.py` - LLM creation
- `src/utils/supabase_client.py` - Database client
- `src/utils/github_api.py` - GitHub API client
- `src/models/` - Pydantic models
- `src/workflows/issue_handler.py` - Workflow orchestration
- `src/db/schema.sql` - Database schema

### Files Specialized (Overridden)

- `test-child/src/agents/product_owner.py` - E-commerce PO agent
- `test-child/src/agents/developer.py` - E-commerce Dev agent
- `test-child/api/webhooks.py` - Uses specialized agents
- `test-child/api/health.py` - Checks agent specialization

### Import Pattern

```python
# Add mother repo to path
import sys
from pathlib import Path

parent_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(parent_dir))

# Now can import from mother repo
from src.agents.product_owner import ProductOwnerAgent as BaseProductOwnerAgent
from src.utils.llm_factory import LLMFactory
from src.config.settings import get_settings
```

## 🎓 Learning from Test-Child

### For Creating Your Own Child Instance

1. **Copy the structure**: Use test-child as a template
2. **Change the domain**: Replace e-commerce with your domain (fintech, healthcare, etc.)
3. **Update `get_domain_context()`**: Add your domain-specific knowledge
4. **Update `get_system_prompt()`** (if needed): Customize agent behavior
5. **Update tech stack** (Developer Agent): Specify your frameworks and tools
6. **Test thoroughly**: Write tests to ensure specialization works

### Example: Creating a Fintech Child

```python
# fintech-child/src/agents/product_owner.py
def get_domain_context(self) -> str:
    return """
    ## Fintech Domain Context

    You are analyzing requirements for a fintech application.
    Always consider:
    - Regulatory compliance (SOC2, KYC, AML)
    - Transaction security and encryption
    - Fraud detection
    - Financial reporting requirements
    - Multi-currency support
    """
```

## 📝 API Endpoints

### Health Check

```bash
GET /api/health
```

**Response**:
```json
{
  "status": "healthy",
  "instance": "test-child-ecommerce",
  "components": {
    "settings": { "status": "healthy" },
    "agents": {
      "status": "healthy",
      "product_owner_specialized": true,
      "developer_specialized": true,
      "specialization": "e-commerce"
    }
  }
}
```

### Webhook Handler

```bash
POST /api/webhooks/github
X-GitHub-Event: issues
X-Hub-Signature-256: sha256=...
```

**Behavior**:
- Uses **e-commerce specialized agents**
- Asks domain-specific questions
- Generates e-commerce appropriate code

## 🔄 Development Workflow

### Making Changes to Mother Repo

```bash
# 1. Make changes to mother repo (e.g., src/agents/base.py)
vim src/agents/base.py

# 2. Test changes in test-child
pytest test-child/tests/ -v

# 3. If tests pass, merge to mother repo main branch
git add src/agents/base.py
git commit -m "feat: improve base agent logging"
git push origin main
```

### Making Changes to Test-Child

```bash
# 1. Make changes to specialized agents
vim test-child/src/agents/product_owner.py

# 2. Run tests
pytest test-child/tests/test_product_owner.py -v

# 3. Commit changes
git add test-child/
git commit -m "feat(test-child): add inventory clarification"
git push origin main
```

## 🚨 Important Notes

### Path Management

Test-child uses dynamic path insertion to import from mother repo:

```python
# This pattern is used throughout test-child
parent_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(parent_dir))
```

**Why?** Allows test-child to use mother repo code without package installation.

**For Production**: Child instances should be separate repositories that import OSOrganicAI as a package.

### Environment Variables

Test-child uses the **same environment variables** as mother repo. See `.env.example`.

### Deployment

Test-child can be deployed:
- **To Vercel**: As a separate Vercel project
- **With GitHub**: Connected to a separate GitHub repository
- **With Supabase**: Using the same or separate Supabase project

## 📚 Additional Resources

- [Mother Repository README](../README.md)
- [Architecture Documentation](../docs/architecture.md)
- [Project Plan](../docs/project-plan.md)
- [Template Usage Guide](../docs/template-usage.md)

## 🤝 Contributing

Test-child improvements help validate the template pattern. When contributing:

1. Add tests for new specialization features
2. Document any new domain context patterns
3. Update this README with examples
4. Ensure all tests pass before pushing

## 📄 License

Same license as mother repository.

---

**Built with ❤️ to validate OSOrganicAI template pattern**
