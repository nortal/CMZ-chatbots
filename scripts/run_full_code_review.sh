#!/bin/bash
# Full Code Review Orchestration Script
# Runs complete multi-phase code review with GPT-3.5-turbo for cost optimization

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REPORT_DIR="reports/code-review"
BACKEND_IMPL="backend/api/src/main/python/openapi_server/impl"
FRONTEND_SRC="frontend/src"
MODEL="gpt-3.5-turbo"  # Use cheaper model for first pass

# Check prerequisites
echo -e "${BLUE}🔍 Checking prerequisites...${NC}"

if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${RED}❌ Error: OPENAI_API_KEY not set${NC}"
    echo "Set it with: export OPENAI_API_KEY='sk-...'"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Error: python3 not found${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites OK${NC}"
echo ""

# Phase 1: Discovery (already completed)
echo -e "${BLUE}📊 Phase 1: Discovery & Architecture Mapping${NC}"
echo "Structure report: $REPORT_DIR/structure.md"
echo "Metrics report: $REPORT_DIR/metrics.md"
echo ""

# Phase 2: Module-by-Module Analysis
echo -e "${BLUE}🔍 Phase 2: Module-by-Module Analysis (using $MODEL)${NC}"
echo "This will analyze backend implementation files for:"
echo "  • Style (PEP 8, naming, organization)"
echo "  • Security (SQL injection, XSS, secrets, auth)"
echo "  • DRY (code duplication, repeated patterns)"
echo "  • SOLID (design principles)"
echo ""

# Priority modules (business logic)
PRIORITY_MODULES=(
    "$BACKEND_IMPL/animals.py"
    "$BACKEND_IMPL/family.py"
    "$BACKEND_IMPL/auth.py"
    "$BACKEND_IMPL/conversation.py"
    "$BACKEND_IMPL/chatgpt_integration.py"
    "$BACKEND_IMPL/handlers.py"
)

echo -e "${YELLOW}Analyzing priority modules...${NC}"
for module in "${PRIORITY_MODULES[@]}"; do
    if [ -f "$module" ]; then
        basename=$(basename "$module")
        echo "  → $basename"

        python3 scripts/openai_code_review.py \
            --file "$module" \
            --focus "style,security,dry,solid" \
            --output "$REPORT_DIR/${basename}.analysis.json" \
            --model "$MODEL" || echo "    ⚠️ Analysis failed for $basename"

        # Rate limiting
        sleep 1
    fi
done

# Utility modules
UTIL_MODULES=(
    "$BACKEND_IMPL/utils/dynamo.py"
    "$BACKEND_IMPL/utils/jwt_utils.py"
    "$BACKEND_IMPL/utils/auth_decorator.py"
    "$BACKEND_IMPL/utils/chatgpt_integration.py"
)

echo -e "${YELLOW}Analyzing utility modules...${NC}"
for module in "${UTIL_MODULES[@]}"; do
    if [ -f "$module" ]; then
        basename=$(basename "$module")
        echo "  → $basename"

        python3 scripts/openai_code_review.py \
            --file "$module" \
            --focus "security,dry,solid" \
            --output "$REPORT_DIR/${basename}.analysis.json" \
            --model "$MODEL" || echo "    ⚠️ Analysis failed for $basename"

        sleep 1
    fi
done

echo ""

# Phase 3: Code Duplication Detection
echo -e "${BLUE}🔍 Phase 3: Code Duplication Detection${NC}"
echo "Analyzing backend implementation for similar code..."
echo ""

python3 scripts/detect_code_duplication.py \
    --paths "$BACKEND_IMPL" \
    --threshold 0.85 \
    --output "$REPORT_DIR/duplication.json" || echo "⚠️ Duplication detection failed"

echo ""

# Phase 3.5: Security Scan
echo -e "${BLUE}🔒 Phase 3.5: Security Pattern Scan${NC}"
echo "Scanning for security vulnerabilities..."

cat > "$REPORT_DIR/security-scan.md" << 'EOF'
# Security Pattern Scan

## Hardcoded Secrets
EOF

# Search for hardcoded secrets
echo "Checking for hardcoded secrets..."
if grep -rn "password\s*=\s*['\"]" "$BACKEND_IMPL" --include="*.py" >> "$REPORT_DIR/security-scan.md" 2>/dev/null; then
    echo "⚠️ Found potential hardcoded passwords"
else
    echo "✅ No hardcoded passwords found" >> "$REPORT_DIR/security-scan.md"
fi

echo "" >> "$REPORT_DIR/security-scan.md"
echo "## SQL Injection Patterns" >> "$REPORT_DIR/security-scan.md"

# SQL injection check (should be none - using DynamoDB)
echo "Checking for SQL injection patterns..."
if grep -rn "execute.*%\|format.*SELECT" "$BACKEND_IMPL" --include="*.py" >> "$REPORT_DIR/security-scan.md" 2>/dev/null; then
    echo "⚠️ Found potential SQL injection patterns"
else
    echo "✅ No SQL injection patterns found (using DynamoDB)" >> "$REPORT_DIR/security-scan.md"
fi

echo ""

# Summary
echo -e "${GREEN}✅ Analysis Complete!${NC}"
echo ""
echo "📁 Reports generated in: $REPORT_DIR/"
echo ""
echo "Next steps:"
echo "  1. Review individual module analyses: $REPORT_DIR/*.analysis.json"
echo "  2. Check duplication report: $REPORT_DIR/duplication.json"
echo "  3. Review security scan: $REPORT_DIR/security-scan.md"
echo ""
echo -e "${BLUE}Ready for Claude's deep analysis...${NC}"
