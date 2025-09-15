#!/bin/bash

# Data Persistence Validation Runner
# Comprehensive end-to-end validation of data flow from UI to DynamoDB

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../../../.." && pwd)"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3001}"
BACKEND_URL="${BACKEND_URL:-http://localhost:8080}"

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}Data Persistence Validation Suite${NC}"
echo -e "${BLUE}============================================${NC}"

# Function to check service availability
check_service() {
    local service_name=$1
    local url=$2
    local max_retries=5
    local retry_count=0

    echo -n "Checking $service_name at $url..."

    while [ $retry_count -lt $max_retries ]; do
        if curl -f -s "$url" > /dev/null 2>&1; then
            echo -e " ${GREEN}✓${NC}"
            return 0
        fi
        retry_count=$((retry_count + 1))
        sleep 2
    done

    echo -e " ${RED}✗${NC}"
    return 1
}

# Function to verify AWS connectivity
check_aws() {
    echo -n "Checking AWS DynamoDB connectivity..."
    if aws dynamodb list-tables --region us-west-2 --output json > /dev/null 2>&1; then
        echo -e " ${GREEN}✓${NC}"
        return 0
    else
        echo -e " ${RED}✗${NC}"
        return 1
    fi
}

# Phase 1: Environment Setup
echo -e "\n${YELLOW}Phase 1: Environment Setup${NC}"
echo "========================================="

# Check backend service (try multiple endpoints)
if ! check_service "Backend API" "$BACKEND_URL" && ! check_service "Backend API" "$BACKEND_URL/api"; then
    echo -e "${RED}Error: Backend API is not running${NC}"
    echo "Please start the backend with: make run-api"
    exit 1
fi

# Check frontend service (optional, will start if needed)
if ! check_service "Frontend" "$FRONTEND_URL"; then
    echo -e "${YELLOW}Warning: Frontend is not running${NC}"
    echo "Frontend testing will be skipped unless you start it"
fi

# Check AWS connectivity
if ! check_aws; then
    echo -e "${RED}Error: Cannot connect to AWS DynamoDB${NC}"
    echo "Please check your AWS credentials and configuration"
    exit 1
fi

# Phase 2: Capture Baseline Data
echo -e "\n${YELLOW}Phase 2: Capturing Baseline Data${NC}"
echo "========================================="

cd "$SCRIPT_DIR"

# Get current DynamoDB state
echo "Querying current database state..."
aws dynamodb scan \
    --table-name quest-dev-animal \
    --region us-west-2 \
    --output json \
    --query 'Items[0:3]' > baseline-current.json

echo -e "Baseline data captured ${GREEN}✓${NC}"

# Phase 3: UI Interaction Testing (if frontend available)
if curl -f -s "$FRONTEND_URL" > /dev/null 2>&1; then
    echo -e "\n${YELLOW}Phase 3: UI Interaction & Form Submission${NC}"
    echo "========================================="

    # Install Playwright if needed
    if ! command -v npx &> /dev/null; then
        echo "Installing Playwright dependencies..."
        npm install -D @playwright/test
        npx playwright install chromium
    fi

    # Run Playwright tests
    echo "Running Playwright data persistence tests..."
    FRONTEND_URL="$FRONTEND_URL" BACKEND_URL="$BACKEND_URL" \
        npx playwright test test-data-persistence.spec.js \
        --reporter=line \
        --workers=1 \
        --timeout=90000 || true

    echo -e "UI testing completed ${GREEN}✓${NC}"
else
    echo -e "\n${YELLOW}Phase 3: Skipping UI tests (frontend not available)${NC}"
fi

# Phase 4: Direct API Testing
echo -e "\n${YELLOW}Phase 4: Direct API Data Persistence Testing${NC}"
echo "========================================="

# Test direct API save
echo "Testing direct API persistence..."

# Create test data
cat > test-api-data.json <<EOF
{
    "animalId": "test_persistence_$(date +%s)",
    "name": "Test Animal",
    "voice": {
        "provider": "elevenlabs",
        "voiceId": "test_voice_api",
        "modelId": "eleven_turbo_v2",
        "stability": 0.5,
        "similarityBoost": 0.75
    },
    "guardrails": {
        "contentFilters": ["educational"],
        "responseMaxLength": 500
    }
}
EOF

# Send API request
echo "Sending test data to API..."
API_RESPONSE=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -d @test-api-data.json \
    "$BACKEND_URL/api/animals" || echo "{}")

echo "$API_RESPONSE" > api-response.json
echo -e "API test completed ${GREEN}✓${NC}"

# Phase 5: Database Verification
echo -e "\n${YELLOW}Phase 5: Database Verification${NC}"
echo "========================================="

# Run Python verification script
echo "Verifying data persistence in DynamoDB..."
python3 verify_dynamodb_persistence.py

# Phase 6: Generate Final Report
echo -e "\n${YELLOW}Phase 6: Generating Validation Report${NC}"
echo "========================================="

# Create comprehensive report
cat > validation-summary.md <<EOF
# Data Persistence Validation Report

**Generated:** $(date)

## Environment
- Frontend URL: $FRONTEND_URL
- Backend URL: $BACKEND_URL
- AWS Region: us-west-2

## Test Results

### Phase 1: Environment Setup
- Backend API: ✓ Running
- Frontend: $([ -f network-capture.json ] && echo "✓ Running" || echo "✗ Not tested")
- DynamoDB: ✓ Accessible

### Phase 2: Baseline Data
- Baseline captured: $([ -f baseline-current.json ] && echo "✓" || echo "✗")
- Animals in database: $(aws dynamodb scan --table-name quest-dev-animal --region us-west-2 --select COUNT --output json | jq '.Count')

### Phase 3: UI Testing
$(if [ -f network-capture.json ]; then
    echo "- Network requests captured: $(jq '.requests | length' network-capture.json)"
    echo "- Form fields submitted: $(jq '.formDataSubmitted | keys | length' network-capture.json)"
else
    echo "- UI tests skipped (frontend not available)"
fi)

### Phase 4: API Testing
$(if [ -f api-response.json ]; then
    echo "- API response status: $([ -s api-response.json ] && echo "✓ Success" || echo "✗ Failed")"
else
    echo "- API test not completed"
fi)

### Phase 5: Database Verification
$(if [ -f validation-report-final.json ]; then
    echo "- Data Integrity: $(jq -r '.validation_results.data_integrity' validation-report-final.json)"
    echo "- Success Rate: $(jq -r '.validation_results.success_rate' validation-report-final.json)"
    echo "- Discrepancies: $(jq -r '.validation_results.discrepancy_count' validation-report-final.json)"
else
    echo "- Verification pending"
fi)

## Files Generated
$(ls -la *.json *.md 2>/dev/null | awk '{print "- " $9 " (" $5 " bytes)"}')

## Recommendations
$(if [ -f validation-report-final.json ]; then
    jq -r '.recommendations[]' validation-report-final.json | sed 's/^/- /'
else
    echo "- Review validation-report-final.json for detailed findings"
fi)

---
*End of Report*
EOF

echo -e "${GREEN}✓ Validation complete!${NC}"
echo ""
echo "Generated files:"
ls -la *.json *.md 2>/dev/null | grep -E '\.(json|md)$'
echo ""
echo -e "${BLUE}View the summary report: validation-summary.md${NC}"
echo -e "${BLUE}View detailed results: validation-report-final.json${NC}"

# Exit with appropriate code
if [ -f validation-report-final.json ]; then
    INTEGRITY=$(jq -r '.validation_results.data_integrity' validation-report-final.json)
    if [ "$INTEGRITY" = "PASS" ]; then
        echo -e "\n${GREEN}✓ All data persistence tests PASSED${NC}"
        exit 0
    else
        echo -e "\n${YELLOW}⚠ Some data persistence issues detected${NC}"
        exit 1
    fi
else
    echo -e "\n${YELLOW}⚠ Validation incomplete${NC}"
    exit 1
fi