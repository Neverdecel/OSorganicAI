# 📘 OSOrganicAI Template Usage Guide

**Target Audience**: Developers and teams who want to spawn a new AI-driven development system from the OSOrganicAI meta-template.

---

## 🎯 Overview

This guide walks you through:
1. **Spawning a child instance** from OSOrganicAI
2. **Customizing agents** for your specific domain
3. **Deploying to Vercel/Supabase**
4. **Operating independently**
5. **Pulling template updates** (optional)

---

## 🌱 Spawning a Child Instance

### Step 1: Clone the Mother Repository

```bash
# Clone OSOrganicAI as your new project
git clone https://github.com/yourusername/osorganicai.git my-ai-project
cd my-ai-project

# Remove mother repo git history (optional - for clean start)
rm -rf .git
git init
git add .
git commit -m "Initial commit from OSOrganicAI template"
```

**Alternative: Use GitHub Template**
1. Go to the OSOrganicAI repository on GitHub
2. Click **"Use this template"** → **"Create a new repository"**
3. Name your new project
4. Clone your new repository

### Step 2: Rename the Project

```bash
# Update project name in configuration files
# vercel.json
sed -i 's/"osorganicai"/"my-ai-project"/g' vercel.json

# README.md
sed -i 's/osorganicai/my-ai-project/g' README.md

# Or manually edit these files
```

**Files to Update:**
- `vercel.json` → `"name": "my-ai-project"`
- `README.md` → Project title and descriptions
- `docs/` → Any references to "osorganicai"

### Step 3: Initialize Your Repository

```bash
# Create a new GitHub repository for your child instance
gh repo create my-org/my-ai-project --public --source=.

# Push your child instance
git remote add origin https://github.com/my-org/my-ai-project.git
git push -u origin main
```

---

## 🔧 Customizing for Your Domain

### Agent Specialization

The mother repository provides **generic agent scaffolds**. You'll specialize them for your domain.

#### Example: E-commerce Project

**Before (Generic Product Owner Agent):**
```python
# src/agents/product_owner.py
class ProductOwnerAgent:
    def analyze_issue(self, issue_text: str):
        # Generic requirement analysis
        return self.llm.analyze(issue_text)
```

**After (E-commerce Specialized):**
```python
# src/agents/product_owner.py
class ProductOwnerAgent:
    def __init__(self, llm_client, github_client, supabase_client):
        super().__init__(llm_client, github_client, supabase_client)
        # Add e-commerce specific context
        self.domain_context = """
        This is an e-commerce system. When analyzing requirements:
        - Consider inventory management
        - Address payment processing security
        - Think about order fulfillment workflows
        - Ensure GDPR/PCI compliance
        """

    def analyze_issue(self, issue_text: str):
        # E-commerce context + generic analysis
        enhanced_prompt = f"{self.domain_context}\n\nUser Request: {issue_text}"
        return self.llm.analyze(enhanced_prompt)
```

#### Customization Points

| File | What to Customize | Example |
|------|-------------------|---------|
| `src/agents/product_owner.py` | Domain context, clarifying questions | E-commerce: inventory, payments |
| `src/agents/developer.py` | Code generation patterns, tech stack | REST API patterns, DB schemas |
| `src/workflows/issue_handler.py` | Business logic flow | Multi-step approval process |
| `src/utils/` | Domain-specific utilities | Payment gateway integration |

### Adding Domain-Specific Code

Create a new `src/domain/` directory for your specialized logic:

```bash
mkdir -p src/domain

# Example: E-commerce domain models
touch src/domain/inventory.py
touch src/domain/payments.py
touch src/domain/orders.py
```

**Example Domain Model:**
```python
# src/domain/orders.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class OrderItem(BaseModel):
    product_id: str
    quantity: int
    unit_price: float

class Order(BaseModel):
    order_id: str
    customer_id: str
    items: List[OrderItem]
    total: float
    status: str  # pending, confirmed, shipped, delivered
    created_at: datetime

    def calculate_total(self) -> float:
        return sum(item.quantity * item.unit_price for item in self.items)
```

---

## ☁️ Deploying Your Child Instance

### Step 1: Set Up Supabase

1. **Create a New Supabase Project**
   - Go to [app.supabase.com](https://app.supabase.com)
   - Click "New Project"
   - Name: `my-ai-project-db`
   - Region: Choose closest to your users

2. **Run Database Schema**
   - Go to **SQL Editor**
   - Copy schema from [`docs/vercel-deployment.md`](vercel-deployment.md#13-create-database-schema)
   - Execute the SQL

3. **Get Credentials**
   - Go to **Settings** → **API**
   - Copy:
     - `SUPABASE_URL`
     - `SUPABASE_ANON_KEY`
     - `SUPABASE_SERVICE_ROLE_KEY`

### Step 2: Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit with your values
nano .env
```

**Required Variables:**
```env
# AI Model
AI_MODEL_PROVIDER=openai
AI_API_KEY=sk-your-openai-key

# GitHub
GITHUB_TOKEN=ghp_your_github_token
GITHUB_REPO=my-org/my-ai-project
GITHUB_WEBHOOK_SECRET=generate-random-string

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Application
APP_ENV=production
LOG_LEVEL=INFO
```

### Step 3: Deploy to Vercel

```bash
# Install Vercel CLI (if not already installed)
npm install -g vercel

# Login to Vercel
vercel login

# Link to your Vercel project
vercel link

# Add environment variables to Vercel
vercel env add AI_MODEL_PROVIDER
vercel env add AI_API_KEY
vercel env add GITHUB_TOKEN
vercel env add GITHUB_REPO
vercel env add GITHUB_WEBHOOK_SECRET
vercel env add SUPABASE_URL
vercel env add SUPABASE_ANON_KEY
vercel env add SUPABASE_SERVICE_ROLE_KEY

# Deploy to production
vercel --prod
```

**Your app will be live at:** `https://my-ai-project.vercel.app`

### Step 4: Configure GitHub Webhook

1. Go to your GitHub repository
2. Navigate to **Settings** → **Webhooks** → **Add webhook**
3. Configure:
   - **Payload URL:** `https://my-ai-project.vercel.app/api/webhooks`
   - **Content type:** `application/json`
   - **Secret:** (same as `GITHUB_WEBHOOK_SECRET`)
   - **Events:** Issues, Issue comments, Pull requests, PR reviews
4. Click **Add webhook**

---

## 🧪 Testing Your Child Instance

### Step 1: Verify Health Endpoint

```bash
curl https://my-ai-project.vercel.app/api/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "my-ai-project",
  "timestamp": "2025-10-14T12:00:00Z"
}
```

### Step 2: Create a Test Issue

1. Go to your GitHub repository
2. Create a new issue:
   - **Title:** "Test: Simple Hello World Function"
   - **Label:** `feature`
   - **Body:** "Create a Python function that returns 'Hello, World!'"

3. Watch for:
   - Product Owner Agent comment (clarifying questions)
   - Developer Agent creating a PR
   - CI/CD running tests
   - Deployment to Vercel

### Step 3: Monitor Logs

**Vercel Dashboard:**
```
https://vercel.com/your-org/my-ai-project
```

**Check Function Logs:**
- Go to **Functions** → `/api/webhooks`
- View invocation logs
- Check for errors

**Supabase Dashboard:**
```
https://app.supabase.com/project/your-project
```

**Check Database:**
- Go to **Table Editor** → `conversations`
- Verify new conversation row
- Check `agent_actions` table for activity

---

## 🔄 Operating Independently

### Your Child Instance is Now Autonomous

Once deployed, your child instance:
- ✅ Receives GitHub webhooks independently
- ✅ Runs agents with your customized logic
- ✅ Deploys to your Vercel account
- ✅ Stores data in your Supabase project
- ✅ Operates without dependency on mother repo

### Day-to-Day Operations

1. **Create Issues**: Users/team create GitHub issues
2. **Agents Respond**: Product Owner and Developer agents collaborate
3. **PRs Generated**: Developer agent creates pull requests
4. **CI/CD Runs**: Tests execute automatically
5. **Deploy**: Successful PRs deploy to production

### Monitoring

**Key Metrics:**
- Issue → PR cycle time
- PR success rate (tests passing)
- Deployment frequency
- Agent intervention rate (human needed?)

**Tools:**
- GitHub Insights
- Vercel Analytics
- Supabase Dashboard
- Custom logging (check `src/utils/logger.py`)

---

## 🔁 Pulling Template Updates (Optional)

### When to Pull Updates

Pull updates from the mother repository when:
- 🐛 Bug fixes in core agent logic
- ✨ New features you want (e.g., Security Agent)
- 🔧 Performance improvements
- 📚 Documentation updates

### How to Pull Updates

```bash
# Add mother repo as remote (one-time setup)
git remote add template https://github.com/original-org/osorganicai.git

# Fetch latest changes
git fetch template

# Review what's changed
git log template/main

# Merge updates (may require conflict resolution)
git merge template/main

# Or cherry-pick specific commits
git cherry-pick <commit-hash>

# Test thoroughly before deploying
vercel dev

# Deploy if all looks good
vercel --prod
```

### Handling Merge Conflicts

If you've heavily customized your child instance, conflicts are expected:

```bash
# When merge conflicts occur
# 1. Review conflicting files
git status

# 2. Manually resolve conflicts
vim src/agents/product_owner.py

# 3. Keep your customizations while adopting template improvements
# 4. Test thoroughly

# 5. Complete the merge
git add .
git commit -m "Merge template updates from OSOrganicAI"
```

**Best Practice:** Create a feature branch for template updates:
```bash
git checkout -b update/template-sync
git merge template/main
# Test, review, then merge to main
```

---

## 🎨 Advanced Customization

### Custom Agent Types

Add new agent types beyond Product Owner and Developer:

```bash
# Create new agent
touch src/agents/security_agent.py
```

**Example: Security Agent**
```python
# src/agents/security_agent.py
from src.agents.base import BaseAgent

class SecurityAgent(BaseAgent):
    """Scans code for security vulnerabilities"""

    def scan_pr(self, pr_number: int):
        # Get PR diff
        diff = self.github.get_pr_diff(pr_number)

        # Scan for vulnerabilities
        vulnerabilities = self.llm.scan_security(diff)

        # Comment on PR if issues found
        if vulnerabilities:
            self.github.comment_on_pr(
                pr_number,
                f"🔒 Security scan found {len(vulnerabilities)} issues:\n" +
                "\n".join(f"- {v}" for v in vulnerabilities)
            )

        return vulnerabilities
```

**Register in Workflow:**
```python
# src/workflows/issue_handler.py
from src.agents.security_agent import SecurityAgent

class IssueWorkflow:
    def __init__(self):
        self.product_owner = ProductOwnerAgent(...)
        self.developer = DeveloperAgent(...)
        self.security = SecurityAgent(...)  # New!

    def handle_pr_created(self, pr_number):
        # Run security scan
        self.security.scan_pr(pr_number)
```

### Custom Workflows

Modify `src/workflows/issue_handler.py` for your business logic:

**Example: Multi-Stage Approval**
```python
class IssueWorkflow:
    def handle_issue(self, issue):
        # Stage 1: Product Owner refines
        refined = self.product_owner.refine(issue)

        # Stage 2: Wait for human approval
        if not self.requires_approval(issue):
            return

        # Stage 3: Developer generates code
        pr = self.developer.generate_code(refined)

        # Stage 4: Security scan
        security_ok = self.security.scan_pr(pr.number)

        # Stage 5: Auto-merge if all checks pass
        if security_ok and pr.tests_passed:
            self.github.merge_pr(pr.number)
```

### Environment-Specific Configuration

Support multiple environments (dev, staging, prod):

```bash
# .env.development
APP_ENV=development
SUPABASE_URL=https://dev-project.supabase.co

# .env.staging
APP_ENV=staging
SUPABASE_URL=https://staging-project.supabase.co

# .env.production
APP_ENV=production
SUPABASE_URL=https://prod-project.supabase.co
```

**Load based on environment:**
```python
# src/config/settings.py
from dotenv import load_dotenv
import os

# Load environment-specific config
env = os.getenv('APP_ENV', 'development')
load_dotenv(f'.env.{env}')
```

---

## 🐛 Troubleshooting

### Issue: Agents Not Responding

**Check:**
1. Webhook delivery in GitHub (Settings → Webhooks → Recent Deliveries)
2. Vercel function logs for errors
3. Environment variables are set correctly
4. Supabase connection is working

**Debug:**
```bash
# Test webhook locally
vercel dev

# Trigger webhook manually
gh api repos/my-org/my-ai-project/dispatches \
  -F event_type=test
```

### Issue: Deployment Fails

**Check:**
1. `vercel.json` syntax is valid
2. Python dependencies in `requirements.txt`
3. Vercel function timeout (increase if needed)

**Fix:**
```json
// vercel.json
{
  "functions": {
    "api/**/*.py": {
      "memory": 1024,
      "maxDuration": 60  // Increase from 30s
    }
  }
}
```

### Issue: Database Connection Errors

**Check:**
1. Supabase project is active
2. Credentials are correct (URL, keys)
3. Row Level Security policies allow service role

**Test Connection:**
```bash
python -c "
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()
client = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_ROLE_KEY')
)
print(client.table('conversations').select('*').execute())
"
```

---

## 📚 Best Practices

### 1. Keep Core Logic Generic
- Extend base agent classes, don't rewrite them
- Add domain logic in `src/domain/`, not in core agents
- This makes pulling template updates easier

### 2. Document Your Customizations
- Update `README.md` with your specific setup
- Document custom agents in `docs/`
- Keep a changelog of template modifications

### 3. Test Before Deploying
```bash
# Always test locally first
vercel dev

# Run tests
pytest

# Check linting
black . --check
flake8 .
```

### 4. Version Control
- Commit often with clear messages
- Tag releases: `git tag v1.0.0`
- Use branches for experiments

### 5. Monitor Production
- Set up error tracking (Sentry)
- Monitor Vercel function performance
- Review Supabase database size

---

## 🎓 Examples

### Example 1: E-commerce System
```
✅ Spawned from OSOrganicAI
✅ Specialized Product Owner for inventory management
✅ Custom Developer Agent for REST API patterns
✅ Added Security Agent for PCI compliance
✅ Domain models: Orders, Products, Customers
```

### Example 2: Blog Platform
```
✅ Spawned from OSOrganicAI
✅ Specialized for content management
✅ Custom workflow: draft → review → publish
✅ Added Documentation Agent for auto-generating docs
✅ Domain models: Posts, Authors, Categories
```

### Example 3: Data Pipeline
```
✅ Spawned from OSOrganicAI
✅ Specialized for ETL workflows
✅ Custom Developer Agent for data transformation logic
✅ Added Monitoring Agent for pipeline health
✅ Domain models: DataSources, Transformations, Destinations
```

---

## 🆘 Getting Help

### Resources
- 📖 [OSOrganicAI Documentation](https://github.com/org/osorganicai/tree/main/docs)
- 💬 [GitHub Discussions](https://github.com/org/osorganicai/discussions)
- 🐛 [Issue Tracker](https://github.com/org/osorganicai/issues)
- 📚 [Vercel Docs](https://vercel.com/docs)
- 🗄️ [Supabase Docs](https://supabase.com/docs)

### Community
- Share your child instance in [Show & Tell](https://github.com/org/osorganicai/discussions/categories/show-and-tell)
- Ask questions in [Q&A](https://github.com/org/osorganicai/discussions/categories/q-a)
- Report bugs in [Issues](https://github.com/org/osorganicai/issues)

---

## ✅ Checklist: Spawning a Child Instance

Use this checklist when creating a new child instance:

- [ ] Clone OSOrganicAI repository
- [ ] Rename project in configuration files
- [ ] Create new GitHub repository for child
- [ ] Customize agents for your domain
- [ ] Add domain-specific models/logic
- [ ] Set up Supabase project and run schema
- [ ] Configure environment variables (.env)
- [ ] Deploy to Vercel
- [ ] Add environment variables to Vercel
- [ ] Configure GitHub webhook
- [ ] Test health endpoint
- [ ] Create test issue and verify agent response
- [ ] Monitor logs (Vercel + Supabase)
- [ ] Document your customizations
- [ ] Set up continuous deployment
- [ ] (Optional) Add mother repo as remote for updates

---

**Ready to spawn your first child instance?** Follow this guide step-by-step, and you'll have an autonomous AI development system running in under an hour!

Happy building! 🚀
