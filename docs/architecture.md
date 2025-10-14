# 🏗️ System Architecture

## Overview

OSOrganicAI operates on **two architectural levels**:

1. **Meta-Template Architecture** — How the mother repository structures, tests, and spawns child instances
2. **Instance Architecture** — How each child instance operates as an autonomous AI development system

This document covers both architectural perspectives, beginning with the meta-template layer and then detailing the operational architecture inherited by all child instances.

---

## 🏭 Meta-Template Architecture

### The Three-Layer Model

```
┌─────────────────────────────────────────────────────────┐
│                    TEMPLATE LAYER                       │
│                  (Mother Repository)                    │
│                                                         │
│  • Generic agent scaffolds (base classes)               │
│  • Reusable CI/CD templates                             │
│  • Vercel/Supabase configurations                       │
│  • Spawn scripts and tooling                            │
│  • Documentation and conventions                        │
└─────────────────┬───────────────────────────────────────┘
                  │
                  │ defines patterns for
                  ↓
┌─────────────────────────────────────────────────────────┐
│                    TESTING LAYER                        │
│                  (Internal test-child/)                 │
│                                                         │
│  • Sandbox for template validation                      │
│  • Proof-of-concept implementation                      │
│  • Feedback loop for template improvements              │
│  • Fast iteration without external dependencies         │
└─────────────────┬───────────────────────────────────────┘
                  │
                  │ validates before spawning
                  ↓
┌─────────────────────────────────────────────────────────┐
│                    INSTANCE LAYER                       │
│              (Spawned Child Repositories)               │
│                                                         │
│  • Inherits agent scaffolds                             │
│  • Specializes for domain (e-commerce, fintech, etc.)   │
│  • Operates autonomously                                │
│  • Can opt-in to template updates                       │
└─────────────────────────────────────────────────────────┘
```

### Template Layer Components

#### 1. Base Agent Classes (`src/agents/base.py`)
```python
class BaseAgent:
    """
    Generic agent scaffold inherited by all child instances.
    Provides core functionality without domain specifics.
    """
    def __init__(self, llm_client, github_client, supabase_client):
        self.llm = llm_client
        self.github = github_client
        self.supabase = supabase_client

    def log_action(self, action_type, payload):
        """All children inherit action logging"""
        self.supabase.table('agent_actions').insert({
            'agent_type': self.__class__.__name__,
            'action_type': action_type,
            'payload': payload
        }).execute()

    # Extension points for child instances
    def get_domain_context(self) -> str:
        """Override in child instances for domain-specific context"""
        return ""

    def customize_prompt(self, base_prompt: str) -> str:
        """Override to add domain-specific prompt modifications"""
        return base_prompt
```

#### 2. Template Directory Structure
```
templates/
├── child-template/           # Complete child project scaffold
│   ├── api/                  # Serverless function templates
│   ├── src/                  # Agent templates
│   ├── tests/                # Test templates
│   └── vercel.json           # Deployment config template
├── agent-configs/            # Generic agent configurations
├── vercel-configs/           # Deployment templates
└── github-workflows/         # CI/CD pipeline templates
```

#### 3. Spawn Tooling
```bash
# scripts/init-child.sh
#!/bin/bash
# Spawns a new child instance from the template

CHILD_NAME=$1

echo "🏗️  Spawning child instance: $CHILD_NAME"

# Copy template
cp -r templates/child-template/ ../$CHILD_NAME

# Initialize git
cd ../$CHILD_NAME
git init

# Update project name
sed -i "s/child-template/$CHILD_NAME/g" vercel.json
sed -i "s/child-template/$CHILD_NAME/g" README.md

echo "✅ Child instance created at ../$CHILD_NAME"
echo "📝 Next steps:"
echo "   1. cd ../$CHILD_NAME"
echo "   2. Customize src/agents/ for your domain"
echo "   3. vercel link && vercel --prod"
```

### Testing Layer: Internal test-child/

The mother repository includes a fully functional child instance for internal testing:

```
test-child/                   # Internal validation environment
├── src/
│   └── agents/
│       ├── product_owner.py  # Test implementation
│       └── developer.py      # Test implementation
├── api/                      # Test serverless functions
├── tests/                    # Integration tests
├── vercel.json               # Test deployment config
└── .github/
    └── workflows/
        └── test-child-ci.yml # Dedicated CI for test child
```

**Purpose:**
1. **Validation**: Every template change is tested via test-child before merging
2. **Documentation**: Serves as living example of how to specialize agents
3. **Feedback Loop**: Reveals template issues before they affect external children

**Workflow:**
```
1. Update base agent in src/agents/base.py
   ↓
2. Test change in test-child/
   ↓
3. Deploy test-child to Vercel preview
   ↓
4. Validate end-to-end functionality
   ↓
5. If successful, merge to main
   ↓
6. External children can pull updates
```

### Instance Layer: Agent Delegation

**Agents remain generic in mother, specialize in children.**

#### Mother Repository (Generic)
```python
# src/agents/product_owner.py (mother repo)
class ProductOwnerAgent(BaseAgent):
    """Generic Product Owner logic"""

    def analyze_issue(self, issue_text: str):
        domain_context = self.get_domain_context()  # Extension point
        base_prompt = self.build_analysis_prompt(issue_text)
        customized_prompt = self.customize_prompt(base_prompt)  # Extension point

        return self.llm.analyze(customized_prompt)
```

#### Child Instance (Specialized)
```python
# child-repo/src/agents/product_owner.py (e-commerce instance)
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

    def customize_prompt(self, base_prompt: str) -> str:
        # Add e-commerce specific instructions
        return f"{base_prompt}\n\nAlways consider impact on checkout flow and cart abandonment."
```

**Key Benefits:**
- ✅ Mother repo stays clean and reusable
- ✅ Children inherit proven patterns
- ✅ Easy to pull template updates
- ✅ Domain expertise isolated in child repos

---

## 🎨 Instance Architecture (Operational)

The following architecture is **inherited by all child instances** spawned from the mother repository. Each child operates as an independent, event-driven AI development system.

### High-Level Architecture (Serverless)

```
┌─────────────────────────────────────────────────────────────┐
│                         GitHub                               │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐│
│  │  Issues  │   │   PRs    │   │ Comments │   │ Webhooks ││
│  └────┬─────┘   └────┬─────┘   └────┬─────┘   └────┬─────┘│
└───────┼──────────────┼──────────────┼──────────────┼───────┘
        │              │              │              │
        └──────────────┴──────────────┴──────────────┘
                            │
                ┌───────────▼────────────┐
                │   Vercel Edge Network  │
                │  (Serverless Functions)│
                └───────────┬────────────┘
                            │
                    ┌───────▼────────┐
                    │ Webhook Handler│
                    │  (api/webhooks)│
                    └───────┬────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
┌───────▼────────┐  ┌───────▼────────┐  ┌──────▼───────┐
│ Product Owner  │  │   Developer    │  │   Future:    │
│     Agent      │  │     Agent      │  │  Security,   │
│                │  │                │  │  Reviewer,   │
│  - Clarifies   │  │  - Generates   │  │  Docs Agents │
│  - Refines     │  │  - Tests       │  │              │
│  - Validates   │  │  - Commits     │  │              │
└───────┬────────┘  └───────┬────────┘  └──────────────┘
        │                   │
        │          ┌────────▼────────┐
        │          │   Code Storage  │
        │          │   (Git/GitHub)  │
        │          └────────┬────────┘
        │                   │
        └───────────────────┼───────────────────┐
                            │                   │
                    ┌───────▼────────┐  ┌───────▼────────┐
                    │   CI Pipeline  │  │ Vercel Deploy  │
                    │ (GitHub Actions)│  │   (Automatic)  │
                    │  - Lint        │  │  - Build       │
                    │  - Test        │  │  - Deploy      │
                    │  - Report      │  │  - Preview     │
                    └───────┬────────┘  └───────┬────────┘
                            │                   │
                            └───────────────────┘
                                      │
                            ┌─────────▼──────────┐
                            │     Supabase       │
                            │  ┌──────────────┐  │
                            │  │  PostgreSQL  │  │
                            │  │   (State)    │  │
                            │  ├──────────────┤  │
                            │  │   Realtime   │  │
                            │  │  (Pub/Sub)   │  │
                            │  ├──────────────┤  │
                            │  │     Auth     │  │
                            │  │   (Future)   │  │
                            │  └──────────────┘  │
                            └────────────────────┘
```

---

## 🧩 Component Breakdown

### 1. **Event Handler / Webhook Listener (Vercel Serverless Function)**

**Purpose:** Receives and routes GitHub events to appropriate agents.

**Technology:**
- **Vercel Serverless Functions** (auto-scaling, zero-config)
- **FastAPI** (optimized for serverless)
- **Supabase** for state management and event queuing

**File:** `api/webhooks.py`

**Key Responsibilities:**
- Authenticate webhook requests using HMAC signatures
- Parse event payloads
- Route to appropriate agent based on event type
- Store events in Supabase for async processing
- Handle retries via Supabase triggers

**Event Types:**
- `issues.opened` → Product Owner Agent
- `issues.labeled` → Product Owner Agent
- `issue_comment.created` → Product Owner Agent
- `pull_request.opened` → CI/CD Pipeline
- `pull_request.closed` → Deployment Pipeline

**Serverless Benefits:**
- **Auto-scaling:** Handles traffic spikes automatically
- **Cost-effective:** Pay only for actual invocations
- **Zero maintenance:** No server management required
- **Global edge network:** Low latency worldwide

---

### 2. **Product Owner Agent**

**Purpose:** Manages requirements gathering and task refinement.

**Core Components:**

```python
from supabase import create_client

class ProductOwnerAgent:
    def __init__(self, llm_client, github_client, supabase_client):
        self.llm = llm_client
        self.github = github_client
        self.supabase = supabase_client
        self.knowledge_base = KnowledgeBase()

    def process_issue(self, issue):
        # Analyze issue content
        analysis = self.analyze_requirements(issue)

        # Store conversation state in Supabase
        self.supabase.table('conversations').insert({
            'issue_id': issue.id,
            'status': 'analyzing',
            'analysis': analysis.dict()
        }).execute()

        # Ask clarifying questions if needed
        if analysis.needs_clarification:
            self.post_questions(issue, analysis.questions)
            # Update state
            self.supabase.table('conversations').update({
                'status': 'needs_clarification'
            }).eq('issue_id', issue.id).execute()

        # Mark as ready when complete
        if analysis.is_complete:
            self.mark_ready_for_dev(issue)
            self.supabase.table('conversations').update({
                'status': 'ready_for_dev'
            }).eq('issue_id', issue.id).execute()
```

**AI Prompt Structure:**
```
System: You are a Product Owner analyzing a feature request.
Context: {project_conventions, codebase_summary}
Task: Analyze this issue and determine if clarification is needed.
Issue: {issue_body}
Output: JSON with {needs_clarification, questions, refined_description}
```

**State Management (Supabase):**
- Issue labels: `needs-clarification` → `ready-for-dev`
- Conversation history stored in Supabase `conversations` table
- Context maintained across multiple interactions using Supabase queries
- Real-time updates via Supabase Realtime subscriptions

---

### 3. **Developer Agent**

**Purpose:** Generates code, writes tests, and creates pull requests.

**Core Components:**

```python
class DeveloperAgent:
    def __init__(self, llm_client, github_client, code_executor):
        self.llm = llm_client
        self.github = github_client
        self.executor = code_executor
        self.context_retriever = CodeContextRetriever()

    def generate_code(self, issue):
        # Retrieve relevant code context
        context = self.context_retriever.get_relevant_files(issue)

        # Generate code with AI
        code = self.llm.generate(
            requirements=issue.body,
            context=context,
            language="python"
        )

        # Generate tests
        tests = self.llm.generate_tests(code)

        # Create branch and PR
        self.create_pull_request(code, tests, issue)
```

**AI Prompt Structure:**
```
System: You are a senior Python developer.
Context: {relevant_files, coding_standards, test_patterns}
Task: Implement the following feature with tests.
Requirements: {refined_issue_description}
Output:
  - File path and code
  - Test file path and tests
  - Commit message
```

**Code Generation Strategy:**
1. **Context Retrieval:** Use vector embeddings to find relevant existing code
2. **Generation:** Create new code based on requirements and context
3. **Testing:** Generate unit tests alongside implementation
4. **Validation:** Syntax check before committing
5. **Documentation:** Add inline comments and docstrings

---

### 4. **CI/CD Pipeline**

**Technology:** GitHub Actions + Vercel

**CI Workflow (`.github/workflows/ci.yml`):**

```yaml
name: Continuous Integration

on:
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov black flake8

      - name: Lint
        run: |
          black --check .
          flake8 .

      - name: Run tests
        run: |
          pytest --cov=src tests/

      - name: Report results
        if: always()
        uses: actions/github-script@v6
        with:
          script: |
            // Post test results as PR comment
```

**CD Workflow (Vercel Automatic Deployment):**

Vercel automatically deploys:
- **Preview deployments** for every PR
- **Production deployments** when merging to `main`

**Optional: Manual Vercel Deploy via GitHub Actions:**

```yaml
name: Deploy to Vercel

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install Vercel CLI
        run: npm install -g vercel

      - name: Deploy to Vercel
        run: vercel --prod --token=${{ secrets.VERCEL_TOKEN }}
        env:
          VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
          VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}

      - name: Notify deployment
        uses: actions/github-script@v6
        with:
          script: |
            // Post deployment URL to PR
```

**Vercel Preview Deployments:**
- Each PR gets a unique preview URL
- Test changes before merging
- Automatic rollback on failures

---

### 5. **Vercel Serverless Environment**

**Purpose:** Isolated, auto-scaling execution environment for the application.

**Security Measures:**

1. **Serverless Isolation:**
   - Each function invocation runs in an isolated environment
   - Automatic sandboxing by Vercel infrastructure
   - No persistent file system (read-only except `/tmp`)
   - Network access controlled via Vercel settings

2. **Function Configuration (`vercel.json`):**
   ```json
   {
     "version": 2,
     "builds": [
       {
         "src": "api/**/*.py",
         "use": "@vercel/python"
       }
     ],
     "routes": [
       {
         "src": "/api/webhooks",
         "dest": "api/webhooks.py"
       },
       {
         "src": "/api/health",
         "dest": "api/health.py"
       }
     ],
     "env": {
       "SUPABASE_URL": "@supabase-url",
       "SUPABASE_ANON_KEY": "@supabase-anon-key"
     },
     "functions": {
       "api/**/*.py": {
         "memory": 1024,
         "maxDuration": 30
       }
     }
   }
   ```

3. **Resource Limits:**
   - **Memory:** 1024 MB per function (configurable)
   - **Duration:** 30 seconds max (can extend to 60s on Pro plan)
   - **Concurrent executions:** Auto-scaled based on demand
   - **Cold start optimization:** Uses edge caching

4. **Security Best Practices:**
   - All secrets stored in Vercel Environment Variables
   - HTTPS enforced for all endpoints
   - Automatic DDoS protection via Vercel Edge Network
   - Rate limiting can be configured via middleware

---

## 🔄 Data Flow

### Issue to Deployment Flow

```
1. User creates GitHub issue
   ↓
2. Webhook triggers Event Handler
   ↓
3. Event Handler routes to Product Owner Agent
   ↓
4. Product Owner Agent:
   - Analyzes requirements
   - Posts clarifying questions (if needed)
   - Waits for user response
   - Refines requirements
   - Labels issue as "ready-for-dev"
   ↓
5. Developer Agent triggered by "ready-for-dev" label:
   - Retrieves code context
   - Generates implementation code
   - Generates tests
   - Creates feature branch
   - Commits code
   - Opens Pull Request
   ↓
6. CI Pipeline triggered by PR:
   - Runs linting
   - Runs tests
   - Reports results on PR
   ↓
7. If tests pass:
   - PR marked as ready for review
   - Optional: Auto-merge if configured
   ↓
8. Vercel Deploy triggered by merge:
   - Builds serverless functions
   - Deploys to Vercel edge network
   - Runs health checks
   - Posts deployment status with preview URL
   ↓
9. User notified of completion with deployment URL
```

---

## 🗄️ Data Storage

### 1. **Code Storage**
- **Location:** GitHub repository
- **Structure:** Standard Git branching model
- **Branches:**
  - `main` — Production-ready code
  - `develop` — Integration branch
  - `feature/*` — AI-generated features
  - `bugfix/*` — AI-generated fixes

### 2. **Agent State (Supabase PostgreSQL)**
- **Location:** Supabase managed PostgreSQL
- **Tables:**

  **`conversations`:**
  ```sql
  CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    issue_id BIGINT NOT NULL,
    issue_number INTEGER NOT NULL,
    repo_full_name TEXT NOT NULL,
    status TEXT NOT NULL, -- 'analyzing', 'needs_clarification', 'ready_for_dev'
    analysis JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
  );
  ```

  **`agent_actions`:**
  ```sql
  CREATE TABLE agent_actions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id),
    agent_type TEXT NOT NULL, -- 'product_owner', 'developer'
    action_type TEXT NOT NULL,
    payload JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
  );
  ```

  **`code_generations`:**
  ```sql
  CREATE TABLE code_generations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id),
    pr_number INTEGER,
    files_changed JSONB,
    tests_generated JSONB,
    status TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
  );
  ```

- **Row Level Security (RLS):** Enabled for all tables
- **Realtime Subscriptions:** For live status updates
- **Indexes:** On `issue_id`, `status`, `created_at` for fast queries

### 3. **Logs and Analytics**
- **Location:** Vercel Analytics + Supabase
- **Vercel Logs:**
  - Function invocations
  - Error traces
  - Performance metrics
  - Request/response data
- **Supabase Audit:**
  - All database operations
  - Agent decisions logged in `agent_actions` table
  - AI model API calls tracked
  - GitHub API interactions

---

## 🔐 Security Architecture

### Authentication & Authorization

```
┌─────────────────────────────────────────────┐
│         GitHub OAuth / PAT                   │
└─────────────────┬───────────────────────────┘
                  │
         ┌────────▼────────┐
         │  Token Manager  │
         │  (Encrypted)    │
         └────────┬────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
┌───▼───┐   ┌─────▼─────┐  ┌───▼────┐
│  PO   │   │ Developer │  │  CI/CD │
│ Agent │   │   Agent   │  │ Runner │
└───────┘   └───────────┘  └────────┘
```

### Secret Management

- **GitHub Secrets:** Store API keys, tokens
- **Environment Variables:** Injected at runtime
- **Encryption:** Secrets encrypted at rest
- **Rotation:** Automated key rotation policy

### Audit Trail

Every action logged with:
- Timestamp
- Agent identifier
- Action performed
- Input/output data
- User who triggered (if applicable)

---

## 📈 Scalability Considerations

### Horizontal Scaling

```
┌──────────────────────────────────────┐
│      Load Balancer (NGINX)          │
└──────────┬────────┬────────┬─────────┘
           │        │        │
    ┌──────▼──┐ ┌───▼────┐ ┌▼────────┐
    │ Worker 1│ │Worker 2│ │Worker N │
    └──────┬──┘ └───┬────┘ └┬────────┘
           │        │        │
    ┌──────▼────────▼────────▼────────┐
    │    Shared State (Redis)         │
    └─────────────────────────────────┘
```

### Agent Concurrency

- Multiple issues processed in parallel
- Queue system for prioritization
- Rate limiting per AI model provider
- Caching for repeated queries

### Cost Optimization

- **Caching:** Cache AI responses for similar queries
- **Model Selection:** Use smaller models for simple tasks
- **Batch Processing:** Group similar operations
- **Monitoring:** Track token usage and optimize prompts

---

## 🧪 Testing Strategy

### Unit Tests
- Test individual agent functions
- Mock AI model responses
- Test GitHub API interactions

### Integration Tests
- Test full workflow from issue to PR
- Test CI/CD pipeline
- Test error handling and retries

### End-to-End Tests
- Create test issues in staging repo
- Verify complete automation flow
- Validate deployed results

---

## 🔮 Future Architecture Enhancements

1. **Multi-Language Support:** Language-specific agent specializations
2. **Agent Communication:** Direct agent-to-agent coordination
3. **Learning Loop:** Store successful patterns for reuse
4. **Human Review Interface:** Web dashboard for monitoring and intervention
5. **Distributed Agents:** Microservices architecture with service mesh
6. **Advanced Context:** Vector database for semantic code search

---

## 📚 Technology Choices Rationale

| Component | Technology | Why? |
|-----------|------------|------|
| **Language** | Python 3.10+ | Rich AI/ML ecosystem, readable, fast prototyping |
| **AI Framework** | LangChain/Pydantic AI | Modular, composable, type-safe |
| **API Server** | FastAPI | Async, fast, auto-documentation, serverless-ready |
| **CI/CD** | GitHub Actions | Native GitHub integration, free tier |
| **Deployment** | Vercel | Zero-config serverless, auto-scaling, global edge network |
| **Database** | Supabase PostgreSQL | Managed PostgreSQL, realtime, built-in auth |
| **Realtime** | Supabase Realtime | WebSocket subscriptions for live updates |
| **State Store** | Supabase (JSONB) | Fast queries, no separate Redis needed |
| **Caching** | Vercel Edge Cache | Built-in CDN and edge caching |
| **Monitoring** | Vercel Analytics | Real-time performance metrics, error tracking |

---

## 🔄 Template Updates & Maintenance

### Pulling Template Updates (Child Instance Perspective)

Child instances can optionally pull updates from the mother repository:

```bash
# In a child instance repository
# Add mother repo as remote (one-time)
git remote add template https://github.com/org/osorganicai.git

# Fetch latest changes
git fetch template

# Review changes
git log template/main --oneline

# Merge updates (may require conflict resolution)
git merge template/main

# Or cherry-pick specific improvements
git cherry-pick <commit-hash>
```

**When to Pull Updates:**
- 🐛 Bug fixes in base agent logic
- ✨ New agent types (Security, Documentation, Review)
- ⚡ Performance improvements
- 📚 Documentation updates

**Handling Conflicts:**
- Conflicts are expected if child has heavily customized agents
- Prioritize child's domain-specific logic
- Test thoroughly with internal test suite before deploying

### Mother Repository Development Cycle

```
1. Developer proposes template improvement
   ↓
2. Changes made to src/agents/base.py or templates/
   ↓
3. Test changes in test-child/
   ↓
4. Deploy test-child to Vercel preview
   ↓
5. Run integration tests
   ↓
6. If successful:
   - Merge to main
   - Document changes in CHANGELOG.md
   - Notify community (GitHub Discussions)
   ↓
7. Child instances can opt-in to updates
```

---

This architecture provides a **two-level foundation**: the template layer enables spawning and evolution, while the instance layer delivers autonomous AI-driven development. Together, they create a scalable, maintainable platform for building AI-powered software factories.
