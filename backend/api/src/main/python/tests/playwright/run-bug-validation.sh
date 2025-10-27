#!/bin/bash

###############################################################################
# Bug Validation Test Suite Runner
#
# Runs comprehensive Playwright tests for all reported bugs in the
# CMZ Animal Assistant Management System
#
# Session: Friday, October 24th, 2025 8:47 AM
# Branch: 003-animal-assistant-mgmt
###############################################################################

set -e

# Configuration
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3001}"
BACKEND_URL="${BACKEND_URL:-http://localhost:8080}"
PLAYWRIGHT_CONFIG="config/playwright.config.js"
SPECS_DIR="specs/bug-validation"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         CMZ Bug Validation Test Suite                         ║${NC}"
echo -e "${BLUE}║         Session: October 24th, 2025                            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Verify services are running
echo -e "${YELLOW}[1/5] Verifying services...${NC}"

check_service() {
    local url=$1
    local name=$2

    if curl -s -o /dev/null -w "%{http_code}" "$url" | grep -q "200\|404"; then
        echo -e "${GREEN}  ✓ $name is running at $url${NC}"
        return 0
    else
        echo -e "${RED}  ✗ $name is NOT running at $url${NC}"
        return 1
    fi
}

if ! check_service "$FRONTEND_URL" "Frontend"; then
    echo -e "${RED}ERROR: Frontend is not running. Please start it first.${NC}"
    echo "  Run: cd frontend && npm start"
    exit 1
fi

if ! check_service "$BACKEND_URL/health" "Backend" && ! check_service "$BACKEND_URL" "Backend"; then
    echo -e "${RED}ERROR: Backend is not running. Please start it first.${NC}"
    echo "  Run: make run-api"
    exit 1
fi

echo ""

# Run test categories
echo -e "${YELLOW}[2/5] Running CRITICAL severity tests...${NC}"
FRONTEND_URL=$FRONTEND_URL npx playwright test \
    --config $PLAYWRIGHT_CONFIG \
    "$SPECS_DIR/01-critical-data-loading.spec.js" \
    --reporter=line \
    --workers=1 \
    --headed

echo ""
echo -e "${YELLOW}[3/5] Running HIGH severity tests...${NC}"
FRONTEND_URL=$FRONTEND_URL npx playwright test \
    --config $PLAYWRIGHT_CONFIG \
    "$SPECS_DIR/02-high-severity-dialogs.spec.js" \
    --reporter=line \
    --workers=1 \
    --headed

echo ""
echo -e "${YELLOW}[4/5] Running MEDIUM severity tests...${NC}"
FRONTEND_URL=$FRONTEND_URL npx playwright test \
    --config $PLAYWRIGHT_CONFIG \
    "$SPECS_DIR/03-medium-navigation-structure.spec.js" \
    --reporter=line \
    --workers=1 \
    --headed

echo ""
echo -e "${YELLOW}[5/5] Generating test report...${NC}"

# Generate summary
REPORT_DIR="../../../../../../backend/reports/playwright"
HTML_REPORT="$REPORT_DIR/html-report/index.html"

if [ -f "$HTML_REPORT" ]; then
    echo -e "${GREEN}  ✓ HTML report generated at: $HTML_REPORT${NC}"
    echo ""
    echo -e "${BLUE}To view the report, run:${NC}"
    echo -e "  npx playwright show-report $REPORT_DIR/html-report"
else
    echo -e "${YELLOW}  ⚠ HTML report not found${NC}"
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║         Bug Validation Test Suite Complete                     ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Test Coverage:${NC}"
echo "  • CRITICAL (4 bugs): Data loading failures"
echo "  • HIGH (3 bugs): Dialog functionality issues"
echo "  • MEDIUM (4 bugs): Navigation and structure issues"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo "  1. Review test results in the HTML report"
echo "  2. Fix failing tests by addressing the underlying bugs"
echo "  3. Re-run tests to verify fixes"
echo "  4. Create regression prevention tickets for any new bugs found"
echo ""
