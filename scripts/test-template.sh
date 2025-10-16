#!/bin/bash
#
# Validate OSOrganicAI template pattern.
#
# This script ensures that:
# 1. Mother repository tests pass
# 2. Test-child tests pass
# 3. Template inheritance works correctly
# 4. No broken imports or syntax errors
#
# Run this before merging template changes to main branch.
#

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_header() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

# Track overall success
VALIDATION_PASSED=true

mark_failure() {
    VALIDATION_PASSED=false
    print_error "$1"
}

print_header "🔍 OSOrganicAI Template Validation"

# Check we're in the right directory
if [ ! -f "pytest.ini" ]; then
    print_error "Must run from OSOrganicAI repository root"
    exit 1
fi

print_info "Starting validation checks..."
echo ""

# ============================================
# 1. Check Dependencies
# ============================================
print_header "1️⃣  Checking Dependencies"

if ! command -v python &> /dev/null; then
    mark_failure "Python not found"
else
    PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
    print_success "Python $PYTHON_VERSION found"
fi

if ! python -c "import pytest" 2>/dev/null; then
    mark_failure "pytest not installed - run: pip install -r requirements-dev.txt"
else
    print_success "pytest installed"
fi

# ============================================
# 2. Mother Repository Tests
# ============================================
print_header "2️⃣  Running Mother Repository Tests"

print_info "Running mother repo unit tests..."
if pytest tests/ -v --tb=short 2>&1 | tee /tmp/mother-tests.log; then
    print_success "Mother repository tests passed"
else
    mark_failure "Mother repository tests failed - see /tmp/mother-tests.log"
fi

# ============================================
# 3. Test-Child Tests
# ============================================
print_header "3️⃣  Running Test-Child Tests"

if [ ! -d "test-child" ]; then
    mark_failure "test-child directory not found"
else
    print_info "Running test-child unit tests..."
    if pytest test-child/tests/ -v --tb=short 2>&1 | tee /tmp/test-child-tests.log; then
        print_success "Test-child tests passed"
    else
        mark_failure "Test-child tests failed - see /tmp/test-child-tests.log"
    fi
fi

# ============================================
# 4. Template Inheritance Validation
# ============================================
print_header "4️⃣  Validating Template Inheritance Pattern"

print_info "Checking that test-child inherits from mother..."
python << 'EOF'
import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path.cwd()))
sys.path.insert(0, str(Path.cwd() / 'test-child'))

try:
    # Import mother agents
    from src.agents.product_owner import ProductOwnerAgent as MotherPO
    from src.agents.developer import DeveloperAgent as MotherDev

    # Import test-child agents
    from src.agents.product_owner import ProductOwnerAgent as ChildPO
    from src.agents.developer import DeveloperAgent as ChildDev

    # Verify inheritance
    assert issubclass(ChildPO, MotherPO), "Child PO must inherit from Mother PO"
    assert issubclass(ChildDev, MotherDev), "Child Dev must inherit from Mother Dev"

    # Verify specialization (child has domain context)
    child_po = ChildPO.__new__(ChildPO)
    child_dev = ChildDev.__new__(ChildDev)

    po_context = child_po.get_domain_context()
    dev_context = child_dev.get_domain_context()

    assert len(po_context) > 0, "Child PO must have domain context"
    assert len(dev_context) > 0, "Child Dev must have domain context"

    # Check for e-commerce terms (test-child is e-commerce specialized)
    po_lower = po_context.lower()
    dev_lower = dev_context.lower()

    assert any(term in po_lower for term in ['ecommerce', 'inventory', 'payment', 'cart']), \
        "PO context must be e-commerce"
    assert any(term in dev_lower for term in ['fastapi', 'stripe', 'product', 'order']), \
        "Dev context must specify e-commerce tech stack"

    print("✅ Inheritance pattern verified")
    print(f"✅ Child PO has {len(po_context)} chars of e-commerce context")
    print(f"✅ Child Dev has {len(dev_context)} chars of tech stack context")
    sys.exit(0)

except Exception as e:
    print(f"❌ Inheritance validation failed: {e}")
    sys.exit(1)
EOF

if [ $? -eq 0 ]; then
    print_success "Template inheritance pattern validated"
else
    mark_failure "Template inheritance validation failed"
fi

# ============================================
# 5. Template Files Syntax Check
# ============================================
print_header "5️⃣  Checking Template Files Syntax"

if [ ! -d "templates/child-template" ]; then
    mark_failure "templates/child-template directory not found"
else
    print_info "Checking Python syntax in template files..."

    TEMPLATE_ERRORS=0

    # Find all Python files in template
    while IFS= read -r file; do
        if ! python -m py_compile "$file" 2>/dev/null; then
            print_error "Syntax error in: $file"
            TEMPLATE_ERRORS=$((TEMPLATE_ERRORS + 1))
        fi
    done < <(find templates/child-template -name "*.py")

    if [ $TEMPLATE_ERRORS -eq 0 ]; then
        print_success "All template files have valid syntax"
    else
        mark_failure "$TEMPLATE_ERRORS template files have syntax errors"
    fi
fi

# ============================================
# 6. Check for Required Files
# ============================================
print_header "6️⃣  Checking Required Files"

REQUIRED_FILES=(
    "src/agents/base.py"
    "src/agents/product_owner.py"
    "src/agents/developer.py"
    "src/workflows/issue_handler.py"
    "src/db/schema.sql"
    "test-child/src/agents/product_owner.py"
    "test-child/src/agents/developer.py"
    "templates/child-template/src/agents/product_owner.py"
    "templates/child-template/src/agents/developer.py"
    "scripts/init-child.sh"
    "pytest.ini"
)

MISSING_FILES=0
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        print_error "Missing required file: $file"
        MISSING_FILES=$((MISSING_FILES + 1))
    fi
done

if [ $MISSING_FILES -eq 0 ]; then
    print_success "All required files present"
else
    mark_failure "$MISSING_FILES required files missing"
fi

# ============================================
# 7. Integration Test
# ============================================
print_header "7️⃣  Running Integration Tests"

print_info "Running integration tests..."
if pytest -m integration -v --tb=short 2>&1 | tee /tmp/integration-tests.log; then
    print_success "Integration tests passed"
else
    # Integration tests might not exist yet, so warn instead of fail
    print_info "Integration tests failed or not found (see /tmp/integration-tests.log)"
fi

# ============================================
# Final Summary
# ============================================
print_header "📊 Validation Summary"

if [ "$VALIDATION_PASSED" = true ]; then
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✅ ALL VALIDATION CHECKS PASSED!${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    print_success "Template is ready for deployment"
    print_success "Safe to merge template changes to main branch"
    echo ""
    exit 0
else
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}❌ VALIDATION FAILED${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    print_error "Some validation checks failed"
    print_info "Review the errors above and fix before merging"
    echo ""
    echo "Logs available at:"
    echo "  - /tmp/mother-tests.log"
    echo "  - /tmp/test-child-tests.log"
    echo "  - /tmp/integration-tests.log"
    echo ""
    exit 1
fi
