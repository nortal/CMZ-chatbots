#!/bin/bash

# Test script for id → animalId rename
# This script tests all animal endpoints before and after the rename

API_URL="${API_URL:-http://localhost:8080}"
TEST_ANIMAL_ID="maya-test-2025"

echo "================================================"
echo "Animal ID Rename Test Suite"
echo "API URL: $API_URL"
echo "Test Animal ID: $TEST_ANIMAL_ID"
echo "================================================"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test result counters
PASS_COUNT=0
FAIL_COUNT=0

# Function to test an endpoint
test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local expected_status=$4
    local description=$5

    echo -n "Testing: $description... "

    if [ "$method" == "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$API_URL$endpoint")
    elif [ "$method" == "PUT" ]; then
        response=$(curl -s -w "\n%{http_code}" -X PUT \
            -H "Content-Type: application/json" \
            -d "$data" \
            "$API_URL$endpoint")
    elif [ "$method" == "DELETE" ]; then
        response=$(curl -s -w "\n%{http_code}" -X DELETE "$API_URL$endpoint")
    fi

    # Extract status code (last line)
    status_code=$(echo "$response" | tail -n 1)
    # Extract body (everything except last line)
    body=$(echo "$response" | head -n -1)

    if [ "$status_code" == "$expected_status" ]; then
        echo -e "${GREEN}✓ PASS${NC} (Status: $status_code)"
        ((PASS_COUNT++))
    else
        echo -e "${RED}✗ FAIL${NC} (Expected: $expected_status, Got: $status_code)"
        if [ ! -z "$body" ]; then
            echo "  Response: $body" | head -c 200
            echo ""
        fi
        ((FAIL_COUNT++))
    fi
}

echo "================================"
echo "Phase 1: Testing Current State"
echo "================================"
echo ""

# Test GET animal
test_endpoint "GET" "/animal/$TEST_ANIMAL_ID" "" "200" "GET /animal/{id}"

# Test PUT animal (update)
update_data='{
  "animalId": "'$TEST_ANIMAL_ID'",
  "animalName": "Maya Test Updated",
  "scientificName": "Test Species Updated",
  "temperaturePersonality": "warm"
}'
test_endpoint "PUT" "/animal/$TEST_ANIMAL_ID" "$update_data" "200" "PUT /animal/{id}"

# Test DELETE animal (should fail with 405 or 501 if not implemented)
test_endpoint "DELETE" "/animal/$TEST_ANIMAL_ID" "" "405" "DELETE /animal/{id}"

echo ""
echo "================================"
echo "Phase 2: Testing List Endpoints"
echo "================================"
echo ""

# Test animal list (should always work)
test_endpoint "GET" "/animal" "" "200" "GET /animal (list all)"

# Test animal config
test_endpoint "GET" "/animal-config" "" "200" "GET /animal-config"

echo ""
echo "================================"
echo "Phase 3: Frontend Integration Test"
echo "================================"
echo ""

# Check if frontend is making calls to old or new endpoint
echo "Checking frontend API calls pattern..."
if [ -f "frontend/src/api/animalApi.js" ] || [ -f "frontend/src/api/animalApi.ts" ]; then
    grep -n "/animal/\${.*id" frontend/src/api/animal* 2>/dev/null || echo "No frontend API files found"
else
    echo "Checking all frontend files for animal API calls..."
    grep -r "/animal/\${.*id" frontend/src --include="*.js" --include="*.ts" --include="*.jsx" --include="*.tsx" | head -5
fi

echo ""
echo "================================"
echo "Test Summary"
echo "================================"
echo -e "Tests Passed: ${GREEN}$PASS_COUNT${NC}"
echo -e "Tests Failed: ${RED}$FAIL_COUNT${NC}"

if [ $FAIL_COUNT -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${YELLOW}Some tests failed. This may be expected if the id_ issue exists.${NC}"
    exit 1
fi