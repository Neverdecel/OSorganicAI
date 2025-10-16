# Child Instance Template

> **Copy this template to create your own domain-specialized OSOrganicAI instance**

This template provides a starting point for creating a new child instance with specialized AI agents for your specific domain.

## 🚀 Quick Start

### Option 1: Using the Spawn Script (Recommended)

```bash
# From the mother repository
cd osorganicai
./scripts/init-child.sh my-project-name my-domain

# Example: Create a fintech instance
./scripts/init-child.sh my-fintech-app fintech
```

### Option 2: Manual Setup

```bash
# Copy this template
cp -r templates/child-template ../my-project

# Initialize git
cd ../my-project
git init
```

## 📝 Customization Checklist

After copying this template, follow these steps:

### 1. Update Agent Domain Context

**File: `src/agents/product_owner.py`**

Replace the placeholder domain context with your specific domain:

```python
def get_domain_context(self) -> str:
    return """
    ## YOUR DOMAIN Context

    You are analyzing requirements for a [YOUR DOMAIN] application.
    Always consider:
    - [Key concern 1]
    - [Key concern 2]
    - [Key concern 3]
    """
```

**Examples by Domain**:

- **Fintech**: KYC/AML compliance, transaction security, regulatory reporting
- **Healthcare**: HIPAA compliance, patient privacy, medical data security
- **E-commerce**: Inventory, payments, shipping (see test-child for full example)
- **SaaS**: Multi-tenancy, subscription billing, API rate limiting
- **Content Management**: SEO, media handling, content workflows

### 2. Update Developer Tech Stack

**File: `src/agents/developer.py`**

Specify your tech stack and code patterns:

```python
def get_domain_context(self) -> str:
    return """
    ## YOUR DOMAIN Tech Stack

    Backend: [Your framework]
    Database: [Your database]
    Key Libraries: [Your dependencies]

    Code Patterns:
    [Provide examples of your data models, API patterns, etc.]
    """
```

### 3. Configure Environment

**File: `.env`**

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
# Edit .env with your actual credentials
```

Required variables:
- `AI_API_KEY`: Your OpenAI/Anthropic API key
- `GITHUB_TOKEN`: GitHub Personal Access Token
- `GITHUB_REPO`: Your repository (owner/repo)
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_SERVICE_ROLE_KEY`: Supabase service role key
- `GITHUB_WEBHOOK_SECRET`: Secret for webhook verification

### 4. Update Project Name

Replace `CHILD_TEMPLATE` with your project name in:
- `vercel.json` (line 3: `"name"`)
- This README
- Any other references

### 5. Write Tests

**Files: `tests/test_*.py`**

Update tests to verify your domain-specific context:
- Test that your domain context includes domain-specific terms
- Test that prompts are customized for your use case
- Add integration tests for your workflows

### 6. Test Locally

```bash
# Install dependencies
pip install -r ../requirements.txt
pip install -r ../requirements-dev.txt

# Run tests
pytest tests/ -v

# Verify agents have domain context
python -c "
from src.agents.product_owner import ProductOwnerAgent
po = ProductOwnerAgent.__new__(ProductOwnerAgent)
assert len(po.get_domain_context()) > 0
print('✅ Domain context configured')
"
```

### 7. Deploy to Vercel

```bash
# Link to Vercel project
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

### 8. Set Up Supabase

```bash
# From mother repository
cd ../osorganicai
python scripts/setup-supabase.py \
  --url https://your-project.supabase.co \
  --key your-service-role-key
```

### 9. Configure GitHub Webhook

In your GitHub repository settings:

1. Go to Settings → Webhooks → Add webhook
2. Payload URL: `https://your-vercel-domain.vercel.app/api/webhooks/github`
3. Content type: `application/json`
4. Secret: Use the same value as `GITHUB_WEBHOOK_SECRET`
5. Events: Select "Issues", "Issue comments", "Pull requests"
6. Save webhook

### 10. Test End-to-End

Create a test issue in your GitHub repository:

```
Title: Test AI Agent
Body: This is a test issue to verify the AI agents are working.
```

Expected behavior:
- Product Owner Agent analyzes the issue
- Posts clarifying questions (with your domain context)
- Adds "needs-clarification" label

## 📁 Template Structure

```
child-template/
├── README.md                    # This file
├── src/
│   └── agents/
│       ├── __init__.py
│       ├── product_owner.py     # TODO: Customize domain context
│       └── developer.py         # TODO: Customize tech stack
├── api/
│   ├── webhooks.py              # GitHub webhook handler
│   └── health.py                # Health check endpoint
├── tests/
│   ├── __init__.py
│   ├── test_product_owner.py    # TODO: Update for your domain
│   ├── test_developer.py        # TODO: Update for your domain
│   └── test_integration.py      # TODO: Add domain-specific tests
├── vercel.json                  # TODO: Update project name
├── .env.example                 # Environment variables template
└── .gitignore                   # Standard Python .gitignore
```

## 🎓 Learning Resources

**See test-child for a complete example**:
- `test-child/src/agents/product_owner.py` - E-commerce domain context
- `test-child/src/agents/developer.py` - E-commerce tech stack
- `test-child/README.md` - Detailed documentation

**Mother repository documentation**:
- `docs/architecture.md` - System architecture
- `docs/project-plan.md` - Project vision and roadmap
- `README.md` - Getting started guide

## 🔍 Verification

After customization, verify your child instance:

```bash
# 1. Tests pass
pytest tests/ -v

# 2. Agents have domain context
python -c "
from src.agents.product_owner import ProductOwnerAgent
from src.agents.developer import DeveloperAgent

po = ProductOwnerAgent.__new__(ProductOwnerAgent)
dev = DeveloperAgent.__new__(DeveloperAgent)

po_ctx = po.get_domain_context()
dev_ctx = dev.get_domain_context()

assert len(po_ctx) > 100, 'PO needs more domain context'
assert len(dev_ctx) > 100, 'Dev needs more tech stack context'

print(f'✅ PO context: {len(po_ctx)} chars')
print(f'✅ Dev context: {len(dev_ctx)} chars')
"

# 3. Health check works
curl https://your-vercel-domain.vercel.app/api/health
```

## 🤝 Contributing Back to Template

If you improve the template structure or find bugs, please contribute back to the mother repository!

## 📄 License

Same license as mother repository (OSOrganicAI).

---

**Ready to build autonomous AI agents for your domain!**
