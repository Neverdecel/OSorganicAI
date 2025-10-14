# 🤖 OSOrganicAI - Meta-Template for AI Software Factories

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF?logo=github-actions&logoColor=white)](https://github.com/features/actions)
[![Vercel](https://img.shields.io/badge/deployed%20on-Vercel-000000?logo=vercel&logoColor=white)](https://vercel.com)
[![Supabase](https://img.shields.io/badge/database-Supabase-3ECF8E?logo=supabase&logoColor=white)](https://supabase.com)
[![Template](https://img.shields.io/badge/template-ready-brightgreen.svg)](docs/template-usage.md)

> **The mother repository for autonomous AI development systems** — A living template that spawns, tests, and evolves AI-driven software factories.

---

## 🌟 What is OSOrganicAI?

OSOrganicAI is not a product—it's a **platform template**. It serves as the **mother repository**, a meta-system that defines how autonomous AI agents collaborate to build, test, and ship software.

### Template vs. Instance

| 🏭 Mother Repository (This Repo) | 🚀 Child Instance (Your Project) |
|----------------------------------|----------------------------------|
| Generic agent scaffolds | Specialized agents for your domain |
| Reusable CI/CD pipelines | Inherited and customized pipelines |
| Template definitions | Live implementation |
| Self-testing infrastructure | Independent operation |
| **Defines patterns** | **Executes patterns** |

### What Child Instances Do

Each child instance spawned from OSOrganicAI inherits:

- 📝 **Product Owner Agent** — Refines requirements and clarifies user requests
- 💻 **Developer Agent** — Generates clean, tested code
- 🔄 **Automated CI/CD** — Tests and deploys to Vercel
- 🔒 **Security First** — Isolated serverless execution
- 📊 **Full Transparency** — All actions logged in GitHub and Supabase

Simply spawn a child instance, customize for your domain, and watch AI agents transform GitHub issues into deployed features!

---

## 🚀 Quick Start

### Two Ways to Use OSOrganicAI

#### Option 1: Spawn a Child Instance (Recommended)
Create your own AI development system from this template:

```bash
# Use GitHub template feature
# 1. Click "Use this template" on GitHub
# 2. Create your new repository
# 3. Clone and customize

# Or clone directly
git clone https://github.com/yourusername/osorganicai.git my-ai-project
cd my-ai-project

# Follow the template usage guide
# See: docs/template-usage.md
```

**→ [Full Template Usage Guide](docs/template-usage.md)**

#### Option 2: Develop the Mother Repository
Contribute to the core template itself:

```bash
# Clone the mother repository
git clone https://github.com/yourusername/osorganicai.git
cd osorganicai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Vercel CLI
npm install -g vercel

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys and configuration

# Test with internal test-child
cd test-child/
vercel dev
```

### Prerequisites

- Python 3.10+
- Node.js 18+ (for Vercel CLI)
- GitHub account
- Vercel account (free tier available)
- Supabase account (free tier available)
- API key for AI model (OpenAI, Anthropic, or compatible)

### Configuration

Create a `.env` file with the following:

```env
# AI Model Configuration
AI_MODEL_PROVIDER=openai  # or 'anthropic', 'ollama'
AI_API_KEY=your_api_key_here

# GitHub Configuration
GITHUB_TOKEN=your_github_token
GITHUB_REPO=yourusername/osorganicai
GITHUB_WEBHOOK_SECRET=your_webhook_secret

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Vercel Deployment
VERCEL_ENV=production
```

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [🎯 Architectural Vision](docs/vision.md) | **START HERE** - Meta-template concept and philosophy |
| [📘 Template Usage Guide](docs/template-usage.md) | **How to spawn a child instance** |
| [📋 Project Plan](docs/project-plan.md) | Complete framework overview and roadmap |
| [🏗️ Architecture](docs/architecture.md) | Technical architecture and template layers |
| [🛠️ Setup Guide](docs/setup.md) | Development environment setup |
| [☁️ Vercel Deployment](docs/vercel-deployment.md) | Deployment guide for Vercel & Supabase |
| [🤝 Contributing](docs/contributing.md) | Guidelines for contributing to the template |

---

## 🎯 How It Works

### The Template Lifecycle

```
┌─────────────────────────────────────────────────────────┐
│                  MOTHER REPOSITORY                      │
│                   (OSOrganicAI)                         │
│  • Defines agent patterns                               │
│  • Maintains CI/CD templates                            │
│  • Tests via internal test-child/                       │
└─────────────────┬───────────────────────────────────────┘
                  │
                  │ spawn
                  ▼
┌─────────────────────────────────────────────────────────┐
│                  CHILD INSTANCE                         │
│                (Your AI Project)                        │
│  1. Inherit agent scaffolds                             │
│  2. Customize for domain                                │
│  3. Deploy to Vercel/Supabase                           │
│  4. Operate autonomously                                │
└─────────────────────────────────────────────────────────┘
```

### Child Instance Workflow

Once spawned, each child instance operates independently:

1. **User Creates GitHub Issue**
   - Label: `feature`, `improvement`, or `bug`
   - Natural language description

2. **Product Owner Agent Engages**
   - Asks clarifying questions
   - Refines requirements (with your domain context)
   - Marks issue "Ready for Development"

3. **Developer Agent Builds**
   - Generates code (in your tech stack)
   - Writes tests
   - Creates Pull Request

4. **Automated CI/CD**
   - Runs linting and tests
   - Deploys to Vercel
   - Logs activity in Supabase
   - Reports status to GitHub issue

---

## 💡 Example: From Template to Production

### Scenario: E-commerce Startup

**Step 1: Spawn Child Instance**
```bash
git clone https://github.com/org/osorganicai.git ecommerce-ai
cd ecommerce-ai
# Customize agents for e-commerce domain
```

**Step 2: Specialize Agents**
```python
# src/agents/product_owner.py
class ProductOwnerAgent(BaseAgent):
    domain_context = """
    E-commerce system. Consider:
    - Inventory management
    - Payment processing
    - Order fulfillment
    """
```

**Step 3: Create Feature via GitHub Issue**
```
Issue: "Add shopping cart with persistent sessions"
Label: feature
```

**Product Owner Agent (Your Specialized Version):**
```
💬 Should cart persist across devices?
💬 How long should abandoned carts be retained?
💬 Do you need guest checkout?
```

**You Reply:**
```
Yes, persist across devices via user account.
Retain for 30 days.
Support guest checkout.
```

**Developer Agent (Your Specialized Version):**
```
✅ Generated PR #42: Implement shopping cart
📦 Includes:
   - Cart model with Redis caching
   - Session persistence
   - Guest checkout flow
🧪 Tests: 23 passed
🚀 Deployed to https://ecommerce-ai.vercel.app
```

**Result:** Feature live in production, built by AI agents customized for your domain!

---

## 🧩 Key Features

### As a Meta-Template
- 🏭 **Mother Repository** — Living template that evolves
- 🚀 **Spawn Child Instances** — Create unlimited AI development systems
- 🧪 **Self-Testing** — Internal test-child for validation
- 📦 **Template Inheritance** — Share patterns, customize implementations
- 🔄 **Backward Compatible** — Children remain stable during template updates

### In Child Instances
- ✨ **Natural Language Input** — No technical specs required
- 🤖 **Specialized AI Agents** — Customized for your domain
- 🔄 **Full Automation** — From issue to deployment
- 🛡️ **Security First** — Serverless isolation, secret management
- 📊 **Full Transparency** — All actions logged in GitHub + Supabase
- 🔌 **Extensible** — Add new agent types as needed

---

## 🏗️ Tech Stack

- **Language:** Python 3.10+
- **AI Framework:** LangChain / Pydantic AI
- **CI/CD:** GitHub Actions
- **Deployment:** Vercel (Serverless Functions)
- **Database:** Supabase (PostgreSQL + Realtime + Auth)
- **Version Control:** GitHub
- **API:** FastAPI (running on Vercel)

---

## 🗺️ Roadmap

### Phase 1: Mother Repository Foundation (Current)
- [x] Meta-template architecture defined
- [x] Architectural vision documented
- [x] Template usage guide created
- [ ] Internal test-child/ implementation
- [ ] Core agent scaffolds (Product Owner, Developer)
- [ ] Vercel/Supabase baseline configuration
- [ ] Template spawn scripts

### Phase 2: Template Maturity
- [ ] Multi-language support (Python, JavaScript, Go, Rust)
- [ ] Additional agent types (Security, Documentation, Review)
- [ ] Template versioning system
- [ ] Automated child initialization
- [ ] Child instance examples (e-commerce, blog, data pipeline)

### Phase 3: Platform Evolution
- [ ] Template marketplace (community variants)
- [ ] Cross-instance knowledge sharing
- [ ] Centralized analytics dashboard
- [ ] Self-improving agents (feedback loop)
- [ ] Advanced deployment targets (AWS, GCP, Azure)

---

## 🤝 Contributing

We welcome contributions to the **mother repository**! Please see our [Contributing Guide](docs/contributing.md) for details.

### Ways to Contribute

1. **Improve Core Agents** — Enhance generic agent scaffolds
2. **Add Template Patterns** — Create reusable configurations
3. **Improve Documentation** — Clarify the meta-template concept
4. **Test with test-child/** — Validate changes internally
5. **Share Child Examples** — Show your spawned instances in action

### Quick Contribution Steps

1. Fork the mother repository
2. Create a feature branch (`git checkout -b feature/amazing-template-feature`)
3. Test with `test-child/` before committing
4. Commit your changes (`git commit -m 'Add template feature'`)
5. Push to the branch (`git push origin feature/amazing-template-feature`)
6. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Inspired by the vision of autonomous software development
- Built with modern AI frameworks and best practices
- Community-driven and open-source

---

## 📬 Contact

- **Issues:** [GitHub Issues](https://github.com/yourusername/osorganicai/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourusername/osorganicai/discussions)

---

<div align="center">

**[Vision](docs/vision.md)** • **[Template Usage](docs/template-usage.md)** • **[Architecture](docs/architecture.md)** • **[Contributing](docs/contributing.md)**

---

**OSOrganicAI**: The factory and the laboratory — a meta-template where agents build, test, and refine their own systems.

Made with ❤️ by the OSOrganicAI community

</div>
