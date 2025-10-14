# 🛠️ Development Environment Setup

This guide covers setup for **both mother repository development and child instance development**.

---

## 🎯 Choose Your Setup Path

### Path A: Mother Repository Development (Template Maintenance)
You're **contributing to the OSOrganicAI template itself**.

**→ [Jump to Mother Repository Setup](#mother-repository-setup)**

Use this if you're:
- Improving base agent scaffolds
- Adding new template features
- Testing changes in `test-child/`
- Contributing to the core template

### Path B: Child Instance Development (Your AI Project)
You're **building your AI system from the template**.

**→ [Jump to Child Instance Setup](#child-instance-setup)**

Use this if you're:
- Developing your specialized AI agents (e-commerce, fintech, etc.)
- Customizing for your domain
- Building a production AI system

---

## 📋 Prerequisites (All Paths)

Before you begin, ensure you have the following installed:

### Required Software

- **Python 3.10 or higher**
  ```bash
  python --version  # Should be 3.10+
  ```

- **Git**
  ```bash
  git --version
  ```

- **Node.js 18+** (for Vercel CLI)
  ```bash
  node --version  # Should be 18+
  npm --version
  ```

### Required Accounts

- **GitHub Account** with repository access
- **Vercel Account** (free tier available at [vercel.com](https://vercel.com))
- **Supabase Account** (free tier available at [supabase.com](https://supabase.com))
- **AI Model Provider** (one of the following):
  - OpenAI API key (GPT-4)
  - Anthropic API key (Claude)
  - Local LLM setup (Ollama)

---

## 🏭 Mother Repository Setup

This section is for **template maintainers and contributors**.

### Overview

When developing the mother repository, you'll work with:
- Generic agent scaffolds in `src/agents/`
- Template structures in `templates/`
- The internal `test-child/` for validation

### 1. Clone the Mother Repository

```bash
# Clone via HTTPS
git clone https://github.com/yourusername/osorganicai.git

# Or via SSH
git clone git@github.com:yourusername/osorganicai.git

# Navigate to project directory
cd osorganicai
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows (Command Prompt):
venv\Scripts\activate.bat

# On Windows (PowerShell):
venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt
```

### 4. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your preferred editor
nano .env  # or vim, code, etc.
```

**Required Environment Variables:**

```env
# AI Model Configuration
AI_MODEL_PROVIDER=openai           # Options: openai, anthropic, ollama
AI_API_KEY=sk-your-api-key-here    # Your AI provider API key
AI_MODEL_NAME=gpt-4                # Model to use (gpt-4, claude-3-opus, etc.)

# GitHub Configuration
GITHUB_TOKEN=ghp_your_token_here   # GitHub Personal Access Token
GITHUB_REPO=yourusername/osorganicai
GITHUB_WEBHOOK_SECRET=your_webhook_secret_here

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here

# Application Configuration
APP_ENV=development                 # Options: development, staging, production
APP_PORT=8000
DEBUG=true

# Logging
LOG_LEVEL=INFO                     # Options: DEBUG, INFO, WARNING, ERROR
```

---

## 🔑 Getting API Keys

### Supabase Setup

1. Go to [app.supabase.com](https://app.supabase.com)
2. Click **"New Project"**
3. Fill in project details and create
4. Once ready, go to **Settings** → **API**
5. Copy these values to your `.env`:
   - `SUPABASE_URL`: Your project URL
   - `SUPABASE_ANON_KEY`: The anon/public key
   - `SUPABASE_SERVICE_ROLE_KEY`: The service role key (keep secret!)
6. See [Vercel Deployment Guide](vercel-deployment.md#step-1-set-up-supabase) for database schema setup

### OpenAI API Key

1. Go to [platform.openai.com](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to **API Keys** section
4. Click **Create new secret key**
5. Copy the key and add to `.env` as `AI_API_KEY`

### Anthropic API Key (Claude)

1. Go to [console.anthropic.com](https://console.anthropic.com/)
2. Sign up or log in
3. Navigate to **API Keys**
4. Create a new key
5. Copy the key and add to `.env` as `AI_API_KEY`

### GitHub Personal Access Token

1. Go to GitHub → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. Click **Generate new token (classic)**
3. Give it a descriptive name (e.g., "OSOrganicAI Development")
4. Select scopes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `workflow` (Update GitHub Action workflows)
   - ✅ `write:packages` (if using GitHub Container Registry)
5. Click **Generate token**
6. Copy the token and add to `.env` as `GITHUB_TOKEN`

---

## 🧪 Setting Up Internal Test Child

This section is for **mother repository developers** testing template changes.

### Overview

The `test-child/` directory is a fully functional child instance embedded in the mother repository for validation:

```
osorganicai/
├── test-child/              # Internal validation environment
│   ├── api/                 # Test serverless functions
│   ├── src/agents/          # Test agent implementations
│   ├── .env.test            # Test environment variables
│   └── vercel.json          # Test deployment config
```

### 1. Set Up Test Child Environment

```bash
# Navigate to test-child directory
cd test-child/

# Copy environment template
cp ../.env.example .env.test

# Edit with test credentials
nano .env.test
```

**Test-Specific Environment Variables:**
```env
# Use cheaper models for testing
AI_MODEL_PROVIDER=openai
AI_MODEL_NAME=gpt-3.5-turbo  # Cheaper than GPT-4

# Test GitHub repo (separate from production)
GITHUB_REPO=yourusername/osorganicai-test

# Separate Supabase project for testing
SUPABASE_URL=https://test-osorganicai.supabase.co
SUPABASE_ANON_KEY=your-test-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-test-service-key

APP_ENV=test
LOG_LEVEL=DEBUG
```

### 2. Install Test Child Dependencies

```bash
# From test-child/ directory
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r ../requirements.txt
```

### 3. Run Test Child Locally

```bash
# Option 1: Run with Vercel dev (recommended)
vercel dev

# Option 2: Run directly
cd ..  # Back to mother repo root
PYTHONPATH=test-child python test-child/api/webhooks.py
```

### 4. Deploy Test Child to Vercel

```bash
# From test-child/ directory
vercel login

# Link to separate Vercel project
vercel link

# Deploy preview
vercel

# You'll get: https://test-child-abc123.vercel.app
```

### 5. Test Template Changes

**Workflow:**
```
1. Make changes to base agent in mother repo
   vim ../src/agents/base.py

2. Test changes in test-child
   cd test-child/
   vim src/agents/product_owner.py  # Uses base agent

3. Run locally to verify
   vercel dev

4. Deploy preview to test end-to-end
   vercel

5. Create test issue in GitHub test repo

6. Verify agents respond correctly

7. If successful, merge changes to mother repo main
```

### Validation Checklist

Before merging template changes:
- [ ] test-child deploys successfully
- [ ] Webhook receives GitHub events
- [ ] Agents execute without errors
- [ ] Database operations work
- [ ] CI/CD pipeline passes
- [ ] All existing tests still pass

---

## 🚀 Child Instance Setup

This section is for **teams building their AI system** from the OSOrganicAI template.

### Overview

When you spawn a child instance, you create an independent AI development system:

```
my-ai-project/ (child instance)
├── api/                     # Your serverless functions
├── src/agents/              # Your specialized agents
├── domain/                  # Your domain logic
├── vercel.json              # Your deployment config
└── .env                     # Your production secrets
```

### 1. Spawn Your Child Instance

```bash
# Option 1: Use GitHub template feature
# 1. Go to OSOrganicAI on GitHub
# 2. Click "Use this template"
# 3. Create your repository
# 4. Clone your new repo

# Option 2: Clone and reset history
git clone https://github.com/org/osorganicai.git my-ai-project
cd my-ai-project
rm -rf .git
git init
git add .
git commit -m "Initial commit from OSOrganicAI template"
```

### 2. Customize for Your Domain

```bash
# Update project name in configs
sed -i 's/osorganicai/my-ai-project/g' vercel.json
sed -i 's/osorganicai/my-ai-project/g' README.md

# Create domain-specific directories
mkdir -p src/domain
```

### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit with your production credentials
nano .env
```

**Production Environment Variables:**
```env
# Your production AI configuration
AI_MODEL_PROVIDER=openai
AI_MODEL_NAME=gpt-4  # Production model
AI_API_KEY=sk-your-production-key

# Your GitHub repository
GITHUB_TOKEN=ghp_your_token
GITHUB_REPO=yourusername/my-ai-project
GITHUB_WEBHOOK_SECRET=generate-strong-secret

# Your Supabase project
SUPABASE_URL=https://my-ai-project.supabase.co
SUPABASE_ANON_KEY=your-production-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-production-service-key

APP_ENV=production
LOG_LEVEL=INFO
```

### 4. Specialize Your Agents

Edit agents to add your domain context:

```python
# src/agents/product_owner.py
from osorganicai.agents.base import BaseAgent

class ProductOwnerAgent(BaseAgent):
    """E-commerce specialized Product Owner"""

    def get_domain_context(self) -> str:
        return """
        E-commerce platform context:
        - Consider inventory management
        - Ensure PCI-DSS compliance for payments
        - Think about shipping logistics
        - Address order fulfillment workflows
        """
```

### 5. Deploy Your Child Instance

```bash
# Login to Vercel
vercel login

# Link to your Vercel project
vercel link

# Deploy to production
vercel --prod

# You'll get: https://my-ai-project.vercel.app
```

### 6. Set Up GitHub Webhook

Follow the [Vercel Deployment Guide](vercel-deployment.md#step-3-configure-github-webhook) to configure webhooks for your child instance.

### 7. Test Your Child Instance

```bash
# Create a test issue in your GitHub repo
# Label: feature
# Title: "Test: Create hello world function"
# Body: "Please create a simple hello world function"

# Watch for Product Owner Agent to respond
# Watch for Developer Agent to create PR
```

---

## 🧪 Running the Application

### Option 1: Run Locally (Development Mode)

```bash
# Ensure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run the main application
python src/main.py

# Or run with auto-reload (if using uvicorn/FastAPI)
uvicorn src.main:app --reload --port 8000
```

### Option 2: Run with Vercel Dev (Simulates Production)

```bash
# Login to Vercel (first time only)
vercel login

# Link to your project
vercel link

# Run development server with Vercel
vercel dev

# Your app will be available at http://localhost:3000
```

**Benefits of `vercel dev`:**
- Simulates the production serverless environment
- Tests Vercel functions locally
- Hot reload on file changes
- Environment variables from Vercel project

---

## 🧪 Testing

### Run All Tests

```bash
# Run tests with pytest
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Run Specific Tests

```bash
# Test specific file
pytest tests/test_agents.py

# Test specific function
pytest tests/test_agents.py::test_product_owner_agent

# Run with verbose output
pytest -v

# Run with print statements
pytest -s
```

### Linting and Formatting

```bash
# Format code with Black
black .

# Check formatting without making changes
black --check .

# Lint with flake8
flake8 .

# Type checking with mypy
mypy src/
```

---

## 🔧 Development Tools

### Recommended IDE Setup

#### VS Code

**Recommended Extensions:**
- Python
- Pylance
- Black Formatter
- Flake8
- GitLens
- Docker

**Settings (`.vscode/settings.json`):**
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "editor.formatOnSave": true,
  "python.testing.pytestEnabled": true
}
```

#### PyCharm

1. Open project in PyCharm
2. Configure Python interpreter: **Settings** → **Project** → **Python Interpreter** → Select `venv`
3. Enable pytest: **Settings** → **Tools** → **Python Integrated Tools** → Set Default test runner to **pytest**
4. Configure Black: **Settings** → **Tools** → **Black** → Enable

---

## 🌐 Setting Up GitHub Webhooks

For local development, you'll need to expose your local server to the internet to receive webhooks.

### Using ngrok (Recommended for Development)

```bash
# Install ngrok
# macOS
brew install ngrok

# Linux
snap install ngrok

# Or download from https://ngrok.com/download

# Start ngrok tunnel
ngrok http 8000

# Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
```

### Configure GitHub Webhook

1. Go to your GitHub repository
2. Navigate to **Settings** → **Webhooks** → **Add webhook**
3. Set **Payload URL** to: `https://your-ngrok-url.ngrok.io/webhooks/github`
4. Set **Content type** to: `application/json`
5. Set **Secret** to: The value of `GITHUB_WEBHOOK_SECRET` in your `.env`
6. Select **Let me select individual events:**
   - ✅ Issues
   - ✅ Issue comments
   - ✅ Pull requests
   - ✅ Pull request reviews
7. Click **Add webhook**

---

## 🗄️ Database Setup (Supabase)

This project uses Supabase as the primary database. Follow these steps:

### 1. Create Supabase Project

See the [Supabase Setup](#supabase-setup) section above for creating a project and getting credentials.

### 2. Run Database Migrations

The complete database schema is available in the [Vercel Deployment Guide](vercel-deployment.md#13-create-database-schema).

To set up your database:

1. Go to your Supabase project dashboard
2. Navigate to **SQL Editor**
3. Copy the schema from the deployment guide
4. Run the SQL to create tables and indexes

### 3. Verify Connection

Test your Supabase connection locally:

```bash
# Install supabase-py if not already installed
pip install supabase

# Test connection
python -c "from supabase import create_client; \
  import os; \
  from dotenv import load_dotenv; \
  load_dotenv(); \
  client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_ANON_KEY')); \
  print('✅ Connected to Supabase!'); \
  print(client.table('conversations').select('*').execute())"
```

You should see a successful connection message!

---

## 📦 Project Structure

After setup, your project should look like this:

```
osorganicai/
├── .env                      # Environment variables (not committed)
├── .env.example              # Example environment variables
├── .gitignore                # Git ignore file
├── README.md                 # Project overview
├── requirements.txt          # Python dependencies
├── requirements-dev.txt      # Development dependencies
├── Dockerfile                # Docker container definition
├── docker-compose.yml        # Multi-container setup
├── pytest.ini                # Pytest configuration
├── .github/
│   └── workflows/
│       ├── ci.yml            # CI pipeline
│       └── cd.yml            # CD pipeline
├── docs/
│   ├── project-plan.md       # Project plan
│   ├── architecture.md       # Architecture documentation
│   ├── setup.md              # This file
│   └── contributing.md       # Contribution guidelines
├── src/
│   ├── __init__.py
│   ├── main.py               # Application entry point
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py           # Base agent class
│   │   ├── product_owner.py  # Product Owner Agent
│   │   └── developer.py      # Developer Agent
│   ├── workflows/
│   │   ├── __init__.py
│   │   └── issue_handler.py  # GitHub issue workflow
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── github_api.py     # GitHub API client
│   │   ├── ai_client.py      # AI model client
│   │   └── logger.py         # Logging configuration
│   └── config/
│       ├── __init__.py
│       └── settings.py       # Configuration management
├── tests/
│   ├── __init__.py
│   ├── test_agents.py        # Agent tests
│   ├── test_workflows.py     # Workflow tests
│   └── fixtures/
│       └── sample_issues.json
└── scripts/
    ├── health-check.sh       # Health check script
    └── deploy.sh             # Deployment script
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. **Import Errors**

```bash
# Ensure you're in the virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

#### 2. **GitHub API Rate Limiting**

```bash
# Check rate limit status
curl -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/rate_limit
```

Solution: Use authenticated requests and implement caching.

#### 3. **Docker Build Fails**

```bash
# Clear Docker cache
docker system prune -a

# Rebuild with no cache
docker build --no-cache -t osorganicai:dev .
```

#### 4. **Port Already in Use**

```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process or use a different port
export APP_PORT=8001
```

#### 5. **Webhook Not Receiving Events**

- Check ngrok is running and URL is correct
- Verify webhook secret matches `.env`
- Check GitHub webhook delivery logs
- Ensure firewall allows incoming connections

---

## 🔄 Updating Dependencies

```bash
# Update pip
pip install --upgrade pip

# Update all packages
pip install --upgrade -r requirements.txt

# Update specific package
pip install --upgrade langchain

# Generate updated requirements
pip freeze > requirements.txt
```

---

## 📚 Additional Resources

- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)
- [GitHub API Documentation](https://docs.github.com/en/rest)
- [Docker Documentation](https://docs.docker.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LangChain Documentation](https://python.langchain.com/)

---

## ✅ Verification Checklist

Before you start developing, ensure:

- [ ] Python 3.10+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed successfully
- [ ] `.env` file configured with all required variables
- [ ] GitHub token has correct permissions
- [ ] AI API key is valid
- [ ] Application starts without errors
- [ ] Tests pass successfully
- [ ] Docker build succeeds (if using Docker)
- [ ] Webhook receives test events (if testing integrations)

---

## 🆘 Getting Help

If you encounter issues:

1. Check the [Troubleshooting](#-troubleshooting) section above
2. Search [GitHub Issues](https://github.com/yourusername/osorganicai/issues)
3. Ask in [GitHub Discussions](https://github.com/yourusername/osorganicai/discussions)
4. Review the [Architecture Documentation](architecture.md)

---

Happy coding! 🚀
