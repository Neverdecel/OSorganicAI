# 🚀 Vercel & Supabase Deployment Guide

This guide covers deployment for **both the mother repository and child instances** of OSOrganicAI.

---

## 🏭 Deployment Scenarios

OSOrganicAI operates on a **meta-template model** with different deployment needs:

### Scenario 1: Deploying the Mother Repository (Template Maintenance)
**Purpose:** For testing template changes via the internal `test-child/` before releasing to external children.

**Who:** Template maintainers and contributors
**What's Deployed:** The `test-child/` validation environment
**Frequency:** On every template change (preview deployments)

### Scenario 2: Deploying a Child Instance (Your AI Project)
**Purpose:** Production deployment of your specialized AI development system.

**Who:** Teams using OSOrganicAI as a template
**What's Deployed:** Your customized child instance (e.g., e-commerce-ai, fintech-ai)
**Frequency:** Continuous deployment on every merge to main

---

## 🎯 Choose Your Deployment Path

### Option A: Deploying Mother Repository (Template Development)
**→ [Jump to Mother Repository Deployment](#mother-repository-deployment)**

Use this if you're:
- Contributing to the OSOrganicAI template
- Testing template changes in `test-child/`
- Validating agent scaffolds before release

### Option B: Deploying Child Instance (Your Project)
**→ [Jump to Child Instance Deployment](#child-instance-deployment)**

Use this if you're:
- Building your AI development system from the template
- Deploying your specialized agents (e-commerce, fintech, etc.)
- Running an autonomous AI project in production

---

## 📋 Prerequisites (All Deployments)

Before you begin, make sure you have:

- [x] GitHub account with your OSOrganicAI repository
- [x] Vercel account (sign up at [vercel.com](https://vercel.com))
- [x] Supabase account (sign up at [supabase.com](https://supabase.com))
- [x] OpenAI or Anthropic API key
- [x] GitHub Personal Access Token

---

## 🏭 Mother Repository Deployment

This section is for **template maintainers** testing changes via the internal `test-child/`.

### Overview

The mother repository uses `test-child/` as a self-contained validation environment:

```
osorganicai/ (mother repo)
├── test-child/              # Internal test instance
│   ├── api/                 # Serverless functions
│   ├── src/agents/          # Test agent implementations
│   ├── vercel.json          # Test deployment config
│   └── .env.test            # Test environment variables
```

### Step 1: Set Up Test Child Environment

```bash
# Navigate to test-child directory
cd test-child/

# Copy environment template
cp .env.example .env.test

# Edit with test credentials
nano .env.test
```

**Test Environment Variables:**
```env
# Use separate Supabase project for testing
SUPABASE_URL=https://test-osorganicai.supabase.co
SUPABASE_ANON_KEY=your-test-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-test-service-key

# Test AI configuration (use cheaper models)
AI_MODEL_PROVIDER=openai
AI_API_KEY=sk-your-test-key
AI_MODEL_NAME=gpt-3.5-turbo  # Cheaper for testing

# Test GitHub configuration
GITHUB_TOKEN=ghp_your-token
GITHUB_REPO=yourusername/osorganicai-test
GITHUB_WEBHOOK_SECRET=test-webhook-secret

APP_ENV=test
LOG_LEVEL=DEBUG
```

### Step 2: Deploy Test Child to Vercel

```bash
# From test-child/ directory
vercel login

# Link to a separate Vercel project
vercel link

# Deploy to preview
vercel

# The test-child gets its own URL:
# https://test-child-abc123.vercel.app
```

### Step 3: Test Template Changes

```bash
# Make changes to base agents in mother repo
vim ../src/agents/base.py

# Test changes in test-child
cd test-child/
vim src/agents/product_owner.py  # Uses base agent

# Deploy preview to test
vercel

# Validate webhook integration
# Create test issue in osorganicai-test repo
```

### Step 4: Validate Before Merging

**Checklist before merging template changes:**
- [ ] test-child deploys successfully to Vercel
- [ ] Webhook receives GitHub events
- [ ] Agents can connect to Supabase
- [ ] Agent logic executes without errors
- [ ] Database operations work correctly
- [ ] CI/CD pipeline passes

### Supabase for Test Child

**Best Practice:** Use a separate Supabase project for test-child to avoid polluting production data.

```
Production:  osorganicai.supabase.co
Test Child:  test-osorganicai.supabase.co
```

Run the same database schema (see below) in both projects.

---

## 🚀 Child Instance Deployment

This section is for **teams building their own AI systems** from the OSOrganicAI template.

### Overview

When you spawn a child instance, you get a complete, independent system:

```
my-ai-project/ (child instance)
├── api/                     # Your serverless functions
├── src/agents/              # Your specialized agents
├── vercel.json              # Your deployment config
└── .env                     # Your production secrets
```

---

## 🗄️ Step 1: Set Up Supabase (Child Instance)

### 1.1 Create a New Supabase Project

1. Go to [app.supabase.com](https://app.supabase.com)
2. Click **"New Project"**
3. Fill in the details:
   - **Name:** `my-ai-project` (or your child instance name)
   - **Database Password:** (save this securely!)
   - **Region:** Choose closest to your users
   - **Pricing Plan:** Free tier is sufficient for MVP
4. Click **"Create new project"**
5. Wait for the project to be provisioned (2-3 minutes)

**Note:** Each child instance should have its own Supabase project for complete independence.

### 1.2 Get Your Supabase Credentials

Once your project is ready:

1. Go to **Settings** → **API**
2. Copy the following values (you'll need these later):
   - **Project URL:** `https://your-project.supabase.co`
   - **anon/public key:** `eyJhbGc...` (safe to expose in frontend)
   - **service_role key:** `eyJhbGc...` (⚠️ KEEP SECRET!)

### 1.3 Create Database Schema

1. Go to **SQL Editor** in the Supabase dashboard
2. Click **"New Query"**
3. Paste and execute this schema:

```sql
-- ============================================
-- OSOrganicAI Database Schema
-- ============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Conversations table: tracks GitHub issue interactions
CREATE TABLE conversations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  issue_id BIGINT NOT NULL,
  issue_number INTEGER NOT NULL,
  repo_full_name TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('analyzing', 'needs_clarification', 'ready_for_dev', 'in_progress', 'completed')),
  analysis JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Agent actions table: logs all agent activities
CREATE TABLE agent_actions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
  agent_type TEXT NOT NULL CHECK (agent_type IN ('product_owner', 'developer', 'security', 'reviewer')),
  action_type TEXT NOT NULL,
  payload JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Code generations table: tracks generated code and PRs
CREATE TABLE code_generations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
  pr_number INTEGER,
  pr_url TEXT,
  files_changed JSONB,
  tests_generated JSONB,
  status TEXT NOT NULL CHECK (status IN ('generating', 'created', 'merged', 'failed')),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for faster queries
CREATE INDEX idx_conversations_issue_id ON conversations(issue_id);
CREATE INDEX idx_conversations_status ON conversations(status);
CREATE INDEX idx_conversations_created_at ON conversations(created_at DESC);
CREATE INDEX idx_agent_actions_conversation_id ON agent_actions(conversation_id);
CREATE INDEX idx_code_generations_conversation_id ON code_generations(conversation_id);

-- Enable Row Level Security (RLS)
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_actions ENABLE ROW LEVEL SECURITY;
ALTER TABLE code_generations ENABLE ROW LEVEL SECURITY;

-- Create policies (allow service role to do everything for now)
CREATE POLICY "Service role can do everything on conversations"
  ON conversations
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Service role can do everything on agent_actions"
  ON agent_actions
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Service role can do everything on code_generations"
  ON code_generations
  FOR ALL
  TO service_role
  USING (true)
  WITH CHECK (true);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers to auto-update updated_at
CREATE TRIGGER update_conversations_updated_at
  BEFORE UPDATE ON conversations
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_code_generations_updated_at
  BEFORE UPDATE ON code_generations
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();
```

4. Click **"Run"** to execute the schema

### 1.4 (Optional) Enable Realtime

1. Go to **Database** → **Replication**
2. Enable replication for these tables:
   - `conversations`
   - `agent_actions`
   - `code_generations`

This allows real-time subscriptions for live updates!

---

## ☁️ Step 2: Deploy to Vercel (Child Instance)

### 2.1 Import Your Repository

1. Go to [vercel.com/new](https://vercel.com/new)
2. Select **"Import Git Repository"**
3. Choose your **child instance** repository (e.g., `my-ai-project`)
4. Click **"Import"**

### 2.2 Configure Project Settings

On the import screen:

1. **Framework Preset:** Select **"Other"**
2. **Root Directory:** Leave as default (`.`)
3. **Build Command:** Leave empty (we're using serverless functions)
4. **Output Directory:** Leave empty
5. **Install Command:** `pip install -r requirements.txt`

### 2.3 Add Environment Variables

Click **"Environment Variables"** and add the following:

| Name | Value | Notes |
|------|-------|-------|
| `AI_MODEL_PROVIDER` | `openai` or `anthropic` | Your AI provider |
| `AI_API_KEY` | `sk-...` | Your AI API key |
| `AI_MODEL_NAME` | `gpt-4` | Model to use |
| `GITHUB_TOKEN` | `ghp_...` | Your GitHub PAT |
| `GITHUB_REPO` | `username/my-ai-project` | Your child instance repo |
| `GITHUB_WEBHOOK_SECRET` | `your-secret` | Generate a random string |
| `SUPABASE_URL` | `https://xxx.supabase.co` | From Supabase dashboard |
| `SUPABASE_ANON_KEY` | `eyJhbGc...` | From Supabase dashboard |
| `SUPABASE_SERVICE_ROLE_KEY` | `eyJhbGc...` | ⚠️ From Supabase dashboard |
| `APP_ENV` | `production` | Environment |
| `LOG_LEVEL` | `INFO` | Logging level |

**🔒 Security Tips:**
- Never commit these values to Git
- Use Vercel's **"Sensitive"** toggle for API keys
- The service role key is extremely powerful - keep it secret!

### 2.4 Deploy!

1. Click **"Deploy"**
2. Wait for the deployment to complete (2-3 minutes)
3. You'll get a URL like: `https://my-ai-project.vercel.app`

**Your child instance is now live!** 🎉

---

## 🔗 Step 3: Configure GitHub Webhook

Now that your Vercel app is deployed, set up the GitHub webhook to receive events.

### 3.1 Get Your Webhook URL

Your webhook endpoint will be:
```
https://your-app.vercel.app/api/webhooks
```

### 3.2 Create the Webhook

1. Go to your GitHub repository
2. Navigate to **Settings** → **Webhooks** → **Add webhook**
3. Fill in the details:
   - **Payload URL:** `https://your-app.vercel.app/api/webhooks`
   - **Content type:** `application/json`
   - **Secret:** (use the same value as `GITHUB_WEBHOOK_SECRET` from Vercel)
4. Select **"Let me select individual events":**
   - ✅ Issues
   - ✅ Issue comments
   - ✅ Pull requests
   - ✅ Pull request reviews
5. Make sure **"Active"** is checked
6. Click **"Add webhook"**

### 3.3 Test the Webhook

1. Click on the webhook you just created
2. Scroll to **"Recent Deliveries"**
3. Click **"Redeliver"** on any recent delivery
4. Check the response - it should return `200 OK`

---

## ✅ Step 4: Verify Deployment

### 4.1 Test the Health Endpoint

Visit your health check endpoint:
```
https://your-app.vercel.app/api/health
```

You should see:
```json
{
  "status": "healthy",
  "service": "osorganicai",
  "timestamp": "2025-10-14T..."
}
```

### 4.2 Test with a GitHub Issue

1. Create a test issue in your repository
2. Add label: `feature`
3. Title: "Test AI Agent"
4. Body: "Please create a simple hello world function"

The Product Owner Agent should respond within 30 seconds!

### 4.3 Check Supabase Data

1. Go to Supabase dashboard → **Table Editor**
2. Check the `conversations` table
3. You should see a new row for your test issue

### 4.4 Check Vercel Logs

1. Go to Vercel dashboard → Your project → **Functions**
2. Click on `/api/webhooks`
3. View the function logs to see the request/response

---

## 🔧 Step 5: Advanced Configuration

### 5.1 Custom Domain (Optional)

1. Go to Vercel project → **Settings** → **Domains**
2. Add your custom domain
3. Follow DNS instructions
4. Update GitHub webhook URL to use your domain

### 5.2 Vercel Function Configuration

Edit `vercel.json` to adjust serverless function settings:

```json
{
  "functions": {
    "api/**/*.py": {
      "memory": 3008,        // Max memory (MB)
      "maxDuration": 60      // Max execution time (seconds)
    }
  }
}
```

### 5.3 Enable Vercel Analytics

1. Go to Vercel project → **Analytics**
2. Enable analytics
3. Monitor performance metrics

### 5.4 Set Up Preview Deployments

Vercel automatically creates preview deployments for every PR!

To customize:
1. Go to project → **Settings** → **Git**
2. Configure:
   - ✅ **Production Branch:** `main`
   - ✅ **Preview Deployments:** Enabled
   - ✅ **Automatic Preview Deployments**

---

## 🚨 Troubleshooting

### Issue: Webhook returns 500 error

**Solution:**
- Check Vercel function logs
- Verify all environment variables are set
- Ensure Supabase credentials are correct
- Check that webhook secret matches

### Issue: Database connection fails

**Solution:**
```bash
# Test Supabase connection locally
python -c "from supabase import create_client; \
  client = create_client('YOUR_URL', 'YOUR_KEY'); \
  print(client.table('conversations').select('*').execute())"
```

### Issue: Function timeout

**Solution:**
- Increase `maxDuration` in `vercel.json`
- Optimize AI model calls (use streaming)
- Consider async processing for long tasks

### Issue: Cold start delays

**Solution:**
- Use Vercel Pro for better cold start performance
- Implement request warming
- Cache AI responses when possible

---

## 📊 Monitoring

### Vercel Dashboard

Monitor your deployment at:
```
https://vercel.com/your-username/osorganicai
```

Key metrics to watch:
- **Function invocations** - Request count
- **Execution duration** - Performance
- **Error rate** - Reliability
- **Bandwidth** - Usage

### Supabase Dashboard

Monitor your database at:
```
https://app.supabase.com/project/your-project
```

Key metrics:
- **Database size**
- **API requests**
- **Realtime connections**
- **Active users**

---

## 💰 Cost Estimation

### Free Tier Limits

**Vercel Free:**
- 100 GB bandwidth/month
- 100 hours serverless function execution
- Unlimited preview deployments

**Supabase Free:**
- 500 MB database storage
- 2 GB bandwidth
- 50,000 monthly active users

**Estimated Monthly Cost:** $0 for MVP testing!

### Scaling Costs

When you outgrow free tier:
- **Vercel Pro:** $20/month
- **Supabase Pro:** $25/month
- **Total:** ~$45/month for production

---

## 🔄 Multi-Instance Strategies

### Environment Variable Inheritance

Child instances inherit environment variable **patterns** from the template, not the values themselves.

**Template provides:**
- `.env.example` with all required variables
- Documentation on what each variable does
- Recommended values and formats

**Each child configures:**
- Their own Supabase credentials
- Their own AI API keys
- Their own GitHub webhook secrets
- Domain-specific settings

### Supabase Project Strategies

#### Strategy 1: One Supabase Project Per Child (Recommended)
```
Mother Repo Test:  test-osorganicai.supabase.co
Child Instance 1:  ecommerce-ai.supabase.co
Child Instance 2:  fintech-ai.supabase.co
Child Instance 3:  blog-platform-ai.supabase.co
```

**Pros:**
- ✅ Complete isolation and independence
- ✅ Per-instance scaling and billing
- ✅ No cross-contamination of data
- ✅ Can customize schema per domain

**Cons:**
- ⚠️ More Supabase projects to manage
- ⚠️ No shared analytics across instances

#### Strategy 2: Shared Supabase with Row-Level Security
```
Shared Database:   all-instances.supabase.co
├── Tenant: ecommerce-ai
├── Tenant: fintech-ai
└── Tenant: blog-platform-ai
```

**Pros:**
- ✅ Centralized analytics
- ✅ Easier to manage credentials
- ✅ Cross-instance insights possible

**Cons:**
- ⚠️ Requires careful RLS policy design
- ⚠️ Shared resource limits
- ⚠️ Risk of tenant data leakage if misconfigured

**Recommendation:** Use Strategy 1 (separate projects) for production child instances.

### Vercel Deployment Patterns

#### Pattern 1: One Vercel Project Per Child
```
Mother Repo Test:  test-child-osorganicai.vercel.app
Child Instance 1:  ecommerce-ai.vercel.app
Child Instance 2:  fintech-ai.vercel.app
```

Each child has:
- Independent deployment pipeline
- Separate environment variables
- Own custom domains
- Isolated preview deployments

#### Pattern 2: Monorepo with Multiple Vercel Projects
```
mono-ai-systems/
├── ecommerce-ai/     → ecommerce-ai.vercel.app
├── fintech-ai/       → fintech-ai.vercel.app
└── blog-platform-ai/ → blog-platform-ai.vercel.app
```

Use Vercel's monorepo support with `vercel.json`:
```json
{
  "version": 2,
  "builds": [
    { "src": "ecommerce-ai/api/**/*.py", "use": "@vercel/python" },
    { "src": "fintech-ai/api/**/*.py", "use": "@vercel/python" }
  ]
}
```

### Template Updates Across Instances

When you pull template updates into a child:

```bash
# In child instance
git remote add template https://github.com/org/osorganicai.git
git fetch template
git merge template/main
```

**Deployment Impact:**
- Vercel automatically triggers new deployment
- Preview deployment created for PR if using branches
- No downtime if deployment succeeds
- Automatic rollback if deployment fails

**Best Practice:**
1. Test template update in a feature branch first
2. Deploy to Vercel preview
3. Validate functionality
4. Merge to main for production deployment

---

## 🎉 Next Steps

1. **Test the full workflow:** Create issues, let agents respond
2. **Monitor performance:** Check Vercel and Supabase dashboards
3. **Iterate:** Improve agent prompts based on results
4. **Scale:** Upgrade plans when needed
5. **Add features:** Implement Security Agent, Documentation Agent, etc.

---

## 📚 Additional Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Supabase Documentation](https://supabase.com/docs)
- [Vercel Python Runtime](https://vercel.com/docs/runtimes#official-runtimes/python)
- [Supabase Python Client](https://github.com/supabase-community/supabase-py)

---

## 🆘 Getting Help

If you encounter issues:

1. Check [GitHub Issues](https://github.com/yourusername/osorganicai/issues)
2. Ask in [GitHub Discussions](https://github.com/yourusername/osorganicai/discussions)
3. Review [Vercel Community](https://github.com/vercel/vercel/discussions)
4. Check [Supabase Discord](https://discord.supabase.com/)

---

Happy deploying! 🚀
