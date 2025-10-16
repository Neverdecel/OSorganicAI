#!/bin/bash
#
# Initialize a new child instance from the template.
#
# Usage: ./scripts/init-child.sh <project-name> <domain>
#
# Example:
#   ./scripts/init-child.sh my-fintech-app fintech
#   ./scripts/init-child.sh my-saas-platform saas
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_error() {
    echo -e "${RED}❌ Error: $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_header() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

# Check arguments
if [ $# -lt 1 ]; then
    print_error "Missing required arguments"
    echo ""
    echo "Usage: $0 <project-name> [domain]"
    echo ""
    echo "Arguments:"
    echo "  project-name   Name for your child instance (e.g., my-fintech-app)"
    echo "  domain         Optional domain name (e.g., fintech, healthcare, saas)"
    echo ""
    echo "Examples:"
    echo "  $0 my-fintech-app fintech"
    echo "  $0 my-healthcare-system healthcare"
    echo "  $0 my-ecommerce-store ecommerce"
    exit 1
fi

PROJECT_NAME="$1"
DOMAIN="${2:-generic}"

# Validate project name
if [[ ! "$PROJECT_NAME" =~ ^[a-z0-9-]+$ ]]; then
    print_error "Project name must contain only lowercase letters, numbers, and hyphens"
    exit 1
fi

print_header "🏗️  Spawning Child Instance: $PROJECT_NAME"

# Check if template exists
TEMPLATE_DIR="templates/child-template"
if [ ! -d "$TEMPLATE_DIR" ]; then
    print_error "Template directory not found: $TEMPLATE_DIR"
    print_info "Are you running this from the OSOrganicAI mother repository root?"
    exit 1
fi

# Check if destination already exists
DEST_DIR="../$PROJECT_NAME"
if [ -d "$DEST_DIR" ]; then
    print_error "Directory already exists: $DEST_DIR"
    print_warning "Please choose a different project name or remove the existing directory"
    exit 1
fi

print_info "Domain: $DOMAIN"
print_info "Destination: $DEST_DIR"
echo ""

# Copy template
print_info "Copying template files..."
cp -r "$TEMPLATE_DIR" "$DEST_DIR"
print_success "Template copied"

# Navigate to destination
cd "$DEST_DIR"

# Replace CHILD_TEMPLATE with project name
print_info "Updating project name references..."

# Files to update
files_to_update=(
    "README.md"
    "vercel.json"
    ".env.example"
    "src/__init__.py"
    "src/agents/__init__.py"
    "api/webhooks.py"
    "api/health.py"
    "tests/__init__.py"
)

for file in "${files_to_update[@]}"; do
    if [ -f "$file" ]; then
        # Use different sed syntax based on OS
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            sed -i '' "s/CHILD_TEMPLATE/$PROJECT_NAME/g" "$file"
        else
            # Linux
            sed -i "s/CHILD_TEMPLATE/$PROJECT_NAME/g" "$file"
        fi
    fi
done

print_success "Project name updated in all files"

# Initialize git repository
print_info "Initializing git repository..."
git init -q
print_success "Git repository initialized"

# Create initial .gitignore if not exists
if [ ! -f ".gitignore" ]; then
    cp "../osorganicai/templates/child-template/.gitignore" ".gitignore"
fi

print_success "Child instance created successfully!"

# Print next steps
print_header "📝 Next Steps"

echo "1. Navigate to your new project:"
echo -e "   ${GREEN}cd $DEST_DIR${NC}"
echo ""

echo "2. Customize the agents for your domain ($DOMAIN):"
echo -e "   ${GREEN}vim src/agents/product_owner.py${NC}  # Add $DOMAIN domain context"
echo -e "   ${GREEN}vim src/agents/developer.py${NC}      # Add $DOMAIN tech stack"
echo ""

echo "3. Configure environment variables:"
echo -e "   ${GREEN}cp .env.example .env${NC}"
echo -e "   ${GREEN}vim .env${NC}  # Add your actual credentials"
echo ""

echo "4. Install dependencies:"
echo -e "   ${GREEN}pip install -r ../osorganicai/requirements.txt${NC}"
echo -e "   ${GREEN}pip install -r ../osorganicai/requirements-dev.txt${NC}"
echo ""

echo "5. Run tests to verify setup:"
echo -e "   ${GREEN}pytest tests/ -v${NC}"
echo ""

echo "6. Deploy to Vercel:"
echo -e "   ${GREEN}vercel link${NC}"
echo -e "   ${GREEN}vercel env add AI_API_KEY${NC}"
echo -e "   ${GREEN}vercel env add GITHUB_TOKEN${NC}"
echo -e "   ${GREEN}vercel env add GITHUB_REPO${NC}"
echo -e "   ${GREEN}vercel env add SUPABASE_URL${NC}"
echo -e "   ${GREEN}vercel env add SUPABASE_SERVICE_ROLE_KEY${NC}"
echo -e "   ${GREEN}vercel env add GITHUB_WEBHOOK_SECRET${NC}"
echo -e "   ${GREEN}vercel --prod${NC}"
echo ""

print_header "📚 Customization Guide"

echo "Domain Context Examples by Domain:"
echo ""

if [ "$DOMAIN" = "fintech" ]; then
    echo "🏦 Fintech - Add to Product Owner Agent:"
    echo "  - KYC/AML compliance requirements"
    echo "  - Transaction security and fraud detection"
    echo "  - Multi-currency support"
    echo "  - Regulatory reporting (SOC2, PCI-DSS)"
    echo "  - Payment reconciliation"
    echo ""
    echo "🏦 Fintech - Add to Developer Agent:"
    echo "  - Integration with Plaid/Stripe"
    echo "  - Transaction processing patterns"
    echo "  - Audit logging requirements"
    echo "  - Encryption at rest and in transit"
elif [ "$DOMAIN" = "healthcare" ]; then
    echo "🏥 Healthcare - Add to Product Owner Agent:"
    echo "  - HIPAA compliance requirements"
    echo "  - Patient privacy and consent"
    echo "  - Medical data security (PHI)"
    echo "  - Clinical workflows"
    echo "  - Audit trail requirements"
    echo ""
    echo "🏥 Healthcare - Add to Developer Agent:"
    echo "  - FHIR standards integration"
    echo "  - HL7 message handling"
    echo "  - Secure patient data storage"
    echo "  - Role-based access control (RBAC)"
elif [ "$DOMAIN" = "ecommerce" ]; then
    echo "🛒 E-commerce - Add to Product Owner Agent:"
    echo "  - Inventory management"
    echo "  - Payment processing (PCI-DSS)"
    echo "  - Shipping and fulfillment"
    echo "  - Cart abandonment recovery"
    echo "  - Order lifecycle management"
    echo ""
    echo "🛒 E-commerce - Add to Developer Agent:"
    echo "  - Product catalog models"
    echo "  - Stripe payment integration"
    echo "  - Shopping cart persistence"
    echo "  - Order management APIs"
    echo ""
    echo "💡 See test-child/ for a complete e-commerce example!"
else
    echo "For your $DOMAIN domain:"
    echo "  - Identify key domain concerns and compliance requirements"
    echo "  - Define domain-specific data models"
    echo "  - Specify tech stack and integration patterns"
    echo "  - Add security and performance considerations"
fi

echo ""
print_header "✨ Happy Building!"

echo "Your specialized AI agents are ready to help build your $DOMAIN application!"
echo ""
echo "Need help? Check out:"
echo "  - test-child/README.md (complete e-commerce example)"
echo "  - docs/architecture.md (system architecture)"
echo "  - docs/project-plan.md (project vision)"
echo ""
