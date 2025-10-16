# Test-Child Deployment Guide

This guide walks you through deploying the test-child e-commerce instance to Vercel.

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Vercel CLI**: Install globally
   ```bash
   npm install -g vercel
   ```
3. **Supabase Project**: Create at [supabase.com](https://supabase.com)
4. **GitHub Repository**: Have a test repository ready
5. **AI API Key**: OpenAI or Anthropic API key

## Step 1: Prepare for Deployment

From the test-child directory, run the preparation script:

```bash
cd test-child
./prepare-deploy.sh
```

This script:
- ✅ Copies mother repository source files to `lib/`
- ✅ Updates import paths for Vercel
- ✅ Prepares the project for standalone deployment

**Output**: You should see "✨ Ready for deployment!"

## Step 2: Set Up Supabase Database

### Option A: Using the Setup Script (Recommended)

```bash
cd ..  # Back to mother repo root
python scripts/setup-supabase.py \
  --url https://your-project.supabase.co \
  --key your-service-role-key
```

### Option B: Manual Setup

1. Go to your Supabase project dashboard
2. Navigate to SQL Editor
3. Copy contents of `src/db/schema.sql`
4. Execute the SQL
5. Verify tables created: `conversations`, `agent_actions`, `code_generations`

## Step 3: Configure Environment Variables

You'll need these values ready:

### Required Variables

| Variable | Description | Where to Get It |
|----------|-------------|-----------------|
| `AI_MODEL_PROVIDER` | AI provider (`openai`, `anthropic`, or `ollama`) | Your choice |
| `AI_API_KEY` | API key for your provider | OpenAI/Anthropic dashboard |
| `OPENAI_API_KEY` | OpenAI API key (if using OpenAI) | https://platform.openai.com/api-keys |
| `GITHUB_TOKEN` | GitHub Personal Access Token | https://github.com/settings/tokens |
| `GITHUB_REPO` | Repository name (`owner/repo`) | Your test repository |
| `GITHUB_WEBHOOK_SECRET` | Webhook secret (choose a random string) | Generate: `openssl rand -hex 32` |
| `SUPABASE_URL` | Supabase project URL | Supabase project settings |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key | Supabase project API settings |

### GitHub Token Permissions

Your GitHub token needs these scopes:
- ✅ `repo` (full control)
- ✅ `workflow` (if using GitHub Actions)

## Step 4: Deploy to Vercel

### First-Time Setup

```bash
cd test-child
vercel
```

Follow the prompts:
- **Set up and deploy?** Yes
- **Which scope?** Choose your account
- **Link to existing project?** No
- **Project name?** osorganicai-test-child-ecommerce (or your choice)
- **Directory?** `.` (current directory)
- **Override settings?** No

### Add Environment Variables

After the initial deployment, add environment variables:

```bash
# AI Configuration
vercel env add AI_MODEL_PROVIDER
# Enter: openai (or anthropic)

vercel env add OPENAI_API_KEY
# Enter: sk-...your-key...

# GitHub Configuration
vercel env add GITHUB_TOKEN
# Enter: ghp_...your-token...

vercel env add GITHUB_REPO
# Enter: yourusername/your-test-repo

vercel env add GITHUB_WEBHOOK_SECRET
# Enter: your-random-secret

# Supabase Configuration
vercel env add SUPABASE_URL
# Enter: https://yourproject.supabase.co

vercel env add SUPABASE_SERVICE_ROLE_KEY
# Enter: eyJ...your-key...

# Optional: Model Configuration
vercel env add OPENAI_MODEL
# Enter: gpt-4-1106-preview

vercel env add OPENAI_TEMPERATURE
# Enter: 0.7
```

### Production Deployment

```bash
vercel --prod
```

**Save the deployment URL!** You'll need it for the webhook.

Example: `https://osorganicai-test-child-ecommerce.vercel.app`

## Step 5: Verify Deployment

### Test Health Endpoint

```bash
curl https://your-deployment.vercel.app/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "OSOrganicAI Test-Child",
  "instance": "test-child-ecommerce",
  "components": {
    "settings": {"status": "healthy"},
    "agents": {
      "status": "healthy",
      "product_owner_specialized": true,
      "developer_specialized": true,
      "specialization": "e-commerce"
    }
  }
}
```

### Test Ping Endpoint

```bash
curl https://your-deployment.vercel.app/api/health/ping
```

Expected:
```json
{
  "message": "pong",
  "instance": "test-child-ecommerce",
  "timestamp": "2024-10-14T..."
}
```

## Step 6: Configure GitHub Webhook

1. Go to your test repository on GitHub
2. Navigate to **Settings** → **Webhooks** → **Add webhook**

### Webhook Configuration

- **Payload URL**: `https://your-deployment.vercel.app/api/webhooks/github`
- **Content type**: `application/json`
- **Secret**: Use the same value as `GITHUB_WEBHOOK_SECRET`
- **SSL verification**: Enable
- **Events**: Select individual events:
  - ✅ Issues
  - ✅ Issue comments
  - ✅ Pull requests
- **Active**: ✅ Checked

Click **Add webhook**

### Verify Webhook

GitHub will send a `ping` event. Check the "Recent Deliveries" tab:
- Status should be ✅ 200
- Response body should show: `"message": "Pong from test-child e-commerce instance!"`

## Step 7: Test End-to-End

### Create Test Issue

In your GitHub repository, create a new issue:

**Title**: `Add payment processing to checkout`

**Body**:
```
We need to add payment processing functionality to our checkout flow.
Users should be able to pay with credit cards.
```

### Expected Behavior

1. **Within 30 seconds**, the Product Owner Agent should comment with **e-commerce specific questions**:
   ```
   🤔 Clarification Needed

   Thank you for the feature request! To ensure we build this correctly, I need to clarify a few things:

   1. What payment gateways should be supported (Stripe, PayPal, etc.)?
   2. Should we support guest checkout or require account creation?
   3. What should happen if payment fails?
   4. Do we need to handle recurring payments or subscriptions?

   Technical Considerations:
   - PCI-DSS compliance
   - Payment security

   Please respond with your answers, and I'll refine the requirements.
   ```

2. The issue should be labeled: **`needs-clarification`**

3. **Respond to the questions**:
   ```
   1. Use Stripe
   2. Support guest checkout
   3. Show user-friendly error message
   4. No subscriptions, one-time payments only
   ```

4. **Within 30 seconds**, the agent should respond and add label: **`ready-for-dev`**

### Troubleshooting

If the agent doesn't respond:

1. **Check Vercel Logs**:
   ```bash
   vercel logs
   ```

2. **Check Webhook Delivery**:
   - Go to GitHub Settings → Webhooks
   - Click on your webhook
   - Check "Recent Deliveries"
   - View request/response details

3. **Common Issues**:
   - ❌ **401 Invalid signature**: Check `GITHUB_WEBHOOK_SECRET` matches
   - ❌ **500 Error**: Check environment variables are set correctly
   - ❌ **Timeout**: Increase function timeout in `vercel.json`
   - ❌ **Import errors**: Re-run `./prepare-deploy.sh`

## Step 8: Monitor Deployment

### View Logs

```bash
# Real-time logs
vercel logs --follow

# Filter by function
vercel logs api/webhooks.py --follow
```

### Check Supabase Data

After successful interactions, verify data in Supabase:

1. **Conversations table**: Should have entries for issues
2. **Agent actions table**: Should log all agent actions
3. **Code generations table**: Will populate when PRs are created

## Updating Deployment

When you make changes:

```bash
# Re-run preparation (if mother repo changed)
./prepare-deploy.sh

# Deploy updated version
vercel --prod
```

## Deployment Checklist

- [ ] Supabase database set up (tables created)
- [ ] Environment variables configured in Vercel
- [ ] Deployment successful (`vercel --prod`)
- [ ] Health endpoint responds correctly
- [ ] GitHub webhook configured
- [ ] Webhook ping successful
- [ ] Test issue created
- [ ] Agent responds with e-commerce questions
- [ ] Agent logs visible in Vercel
- [ ] Data appearing in Supabase

## Next Steps

After successful deployment:

1. **Test with Real Scenarios**:
   - Create payment feature requests
   - Create inventory management issues
   - Create shipping-related issues
   - Verify e-commerce context in all responses

2. **Monitor Performance**:
   - Check Vercel function execution times
   - Monitor Supabase database growth
   - Review AI token usage

3. **Create External Child**:
   - Use this deployment as reference
   - Spawn a new child for different domain
   - Deploy to separate Vercel project

## Support

If you encounter issues:

1. Check Vercel logs: `vercel logs`
2. Review GitHub webhook deliveries
3. Verify Supabase connection
4. Check environment variables: `vercel env ls`

## Security Notes

- 🔒 Never commit `.env` file
- 🔒 Use Vercel environment variables for secrets
- 🔒 Rotate `GITHUB_WEBHOOK_SECRET` if compromised
- 🔒 Use service role key only server-side
- 🔒 Enable Supabase Row Level Security (RLS)

---

**Congratulations!** Your test-child e-commerce instance is now live and ready to handle GitHub issues with domain-specialized AI agents!
