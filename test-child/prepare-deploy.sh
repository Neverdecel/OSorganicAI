#!/bin/bash
#
# Prepare test-child for Vercel deployment
#
# This script copies necessary files from the mother repository
# into the test-child directory so Vercel can deploy it standalone.
#

set -e

echo "🚀 Preparing test-child for Vercel deployment..."
echo ""

# Check we're in the right place
if [ ! -f "vercel.json" ]; then
    echo "❌ Error: Must run from test-child directory"
    exit 1
fi

# Check mother repo exists
if [ ! -d "../src" ]; then
    echo "❌ Error: Mother repository src/ not found"
    echo "   Are you in the correct directory structure?"
    exit 1
fi

echo "📦 Copying mother repository source files..."

# Create lib directory for mother repo code
mkdir -p lib

# Copy entire src directory from mother repo
echo "  - Copying src/ (agents, models, utils, config)..."
cp -r ../src lib/

# Copy db directory
echo "  - Copying db/ (schema)..."
mkdir -p lib/db
cp -r ../src/db/* lib/db/ 2>/dev/null || true

echo "✅ Mother repository files copied to lib/"
echo ""

echo "🔧 Updating import paths..."

# Update webhooks.py to use lib instead of dynamic paths
if [ -f "api/webhooks.py" ]; then
    # Create backup
    cp api/webhooks.py api/webhooks.py.bak

    # Replace the sys.path manipulation with simpler imports
    sed -i 's|parent_dir = Path(__file__).*|# Imports from lib/ directory|' api/webhooks.py 2>/dev/null || \
    sed -i '' 's|parent_dir = Path(__file__).*|# Imports from lib/ directory|' api/webhooks.py

    sed -i 's|sys.path.insert(0, str(parent_dir))||' api/webhooks.py 2>/dev/null || \
    sed -i '' 's|sys.path.insert(0, str(parent_dir))||' api/webhooks.py

    sed -i 's|from src\.|from lib.src.|g' api/webhooks.py 2>/dev/null || \
    sed -i '' 's|from src\.|from lib.src.|g' api/webhooks.py

    echo "  - Updated api/webhooks.py"
fi

# Update health.py
if [ -f "api/health.py" ]; then
    cp api/health.py api/health.py.bak

    sed -i 's|parent_dir = Path(__file__).*|# Imports from lib/ directory|' api/health.py 2>/dev/null || \
    sed -i '' 's|parent_dir = Path(__file__).*|# Imports from lib/ directory|' api/health.py

    sed -i 's|sys.path.insert(0, str(parent_dir))||' api/health.py 2>/dev/null || \
    sed -i '' 's|sys.path.insert(0, str(parent_dir))||' api/health.py

    sed -i 's|from src\.|from lib.src.|g' api/health.py 2>/dev/null || \
    sed -i '' 's|from src\.|from lib.src.|g' api/health.py

    echo "  - Updated api/health.py"
fi

# Update specialized agents
if [ -f "src/agents/product_owner.py" ]; then
    cp src/agents/product_owner.py src/agents/product_owner.py.bak

    sed -i 's|parent_dir = Path(__file__).*|# Imports from lib/ directory|' src/agents/product_owner.py 2>/dev/null || \
    sed -i '' 's|parent_dir = Path(__file__).*|# Imports from lib/ directory|' src/agents/product_owner.py

    sed -i 's|sys.path.insert(0, str(parent_dir))||' src/agents/product_owner.py 2>/dev/null || \
    sed -i '' 's|sys.path.insert(0, str(parent_dir))||' src/agents/product_owner.py

    sed -i 's|^from src\.|from lib.src.|g' src/agents/product_owner.py 2>/dev/null || \
    sed -i '' 's|^from src\.|from lib.src.|g' src/agents/product_owner.py

    echo "  - Updated src/agents/product_owner.py"
fi

if [ -f "src/agents/developer.py" ]; then
    cp src/agents/developer.py src/agents/developer.py.bak

    sed -i 's|parent_dir = Path(__file__).*|# Imports from lib/ directory|' src/agents/developer.py 2>/dev/null || \
    sed -i '' 's|parent_dir = Path(__file__).*|# Imports from lib/ directory|' src/agents/developer.py

    sed -i 's|sys.path.insert(0, str(parent_dir))||' src/agents/developer.py 2>/dev/null || \
    sed -i '' 's|sys.path.insert(0, str(parent_dir))||' src/agents/developer.py

    sed -i 's|^from src\.|from lib.src.|g' src/agents/developer.py 2>/dev/null || \
    sed -i '' 's|^from src\.|from lib.src.|g' src/agents/developer.py

    echo "  - Updated src/agents/developer.py"
fi

echo "✅ Import paths updated"
echo ""

echo "📋 Deployment checklist:"
echo ""
echo "1. ✅ Mother repository files copied"
echo "2. ✅ Import paths updated"
echo "3. ⏳ Configure environment variables in Vercel:"
echo "     - AI_MODEL_PROVIDER"
echo "     - AI_API_KEY (or OPENAI_API_KEY)"
echo "     - GITHUB_TOKEN"
echo "     - GITHUB_REPO"
echo "     - GITHUB_WEBHOOK_SECRET"
echo "     - SUPABASE_URL"
echo "     - SUPABASE_SERVICE_ROLE_KEY"
echo ""
echo "4. ⏳ Deploy:"
echo "     vercel --prod"
echo ""
echo "5. ⏳ Configure GitHub webhook:"
echo "     - URL: https://your-deployment.vercel.app/api/webhooks/github"
echo "     - Secret: (use GITHUB_WEBHOOK_SECRET value)"
echo "     - Events: Issues, Issue comments, Pull requests"
echo ""

echo "✨ Ready for deployment!"
echo ""
echo "Next: cd test-child && vercel --prod"
