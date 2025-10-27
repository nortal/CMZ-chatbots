#!/bin/bash
# Verify all endpoints listed as IMPLEMENTED in ENDPOINT-WORK.md
# Based on documentation last updated: 2025-10-09

set -e

BASE_URL="${BASE_URL:-http://localhost:8080}"
RESULTS_FILE="/tmp/implemented_endpoints_verification.json"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Initialize results
echo '{
  "timestamp": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'",
  "baseUrl": "'$BASE_URL'",
  "source": "ENDPOINT-WORK.md (last updated 2025-10-09)",
  "categories": {}
}' > "$RESULTS_FILE"

total_tests=0
passed_tests=0
failed_tests=0

# Test function
test_endpoint() {
    local method="$1"
    local path="$2"
    local expected_status="$3"
    local description="$4"
    local data="$5"
    local category="$6"

    total_tests=$((total_tests + 1))

    printf "  %-50s" "$description"

    if [ -n "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$BASE_URL$path" \
            -H "Content-Type: application/json" \
            -d "$data" 2>/dev/null || echo -e "\n000")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$BASE_URL$path" 2>/dev/null || echo -e "\n000")
    fi

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    # Check if response matches expected status or acceptable alternatives
    if [ "$http_code" = "$expected_status" ] || \
       { [ "$expected_status" = "2XX" ] && [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; } || \
       { [ "$expected_status" = "4XX" ] && [ "$http_code" -ge 400 ] && [ "$http_code" -lt 500 ]; }; then
        echo -e "${GREEN}✓ $http_code${NC}"
        passed_tests=$((passed_tests + 1))
        status="PASS"
    else
        echo -e "${RED}✗ $http_code (expected $expected_status)${NC}"
        failed_tests=$((failed_tests + 1))
        status="FAIL"
        # Show error body if available
        if [ -n "$body" ] && [ "$body" != "null" ]; then
            echo "    Error: $(echo "$body" | jq -r '.message // .detail // .error // "Unknown error"' 2>/dev/null || echo "$body" | head -c 200)"
        fi
    fi

    # Store result
    jq --arg cat "$category" \
       --arg method "$method" \
       --arg path "$path" \
       --arg expected "$expected_status" \
       --arg actual "$http_code" \
       --arg status "$status" \
       --arg desc "$description" \
       '.categories[$cat] += [{"method": $method, "path": $path, "expectedStatus": $expected, "actualStatus": $actual, "status": $status, "description": $desc}]' \
       "$RESULTS_FILE" > "${RESULTS_FILE}.tmp" && mv "${RESULTS_FILE}.tmp" "$RESULTS_FILE"
}

echo "================================================================"
echo "  Verifying IMPLEMENTED Endpoints from ENDPOINT-WORK.md"
echo "================================================================"
echo "Base URL: $BASE_URL"
echo "Time: $(date)"
echo ""

# Get auth token for protected endpoints
echo -e "${BLUE}=== Getting Authentication Token ===${NC}"
TOKEN=$(curl -s -X POST "$BASE_URL/auth" \
  -H "Content-Type: application/json" \
  -d '{"username": "test@cmz.org", "password": "testpass123"}' | \
  jq -r '.token // empty' 2>/dev/null)

if [ -n "$TOKEN" ]; then
    echo -e "${GREEN}✓ Auth token obtained${NC}"
else
    echo -e "${RED}✗ Failed to get auth token${NC}"
    TOKEN="dummy_token"
fi
echo ""

# Authentication Endpoints
echo -e "${BLUE}=== Authentication (4 endpoints) ===${NC}"
test_endpoint "POST" "/auth" "200" "Login with mock users" '{"username":"test@cmz.org","password":"testpass123"}' "Authentication"
test_endpoint "POST" "/auth/logout" "200" "Logout" '{}' "Authentication"
test_endpoint "POST" "/auth/refresh" "2XX" "Refresh token" '{"token":"'$TOKEN'"}' "Authentication"
test_endpoint "POST" "/auth/reset_password" "2XX" "Password reset" '{"email":"test@cmz.org"}' "Authentication"
echo ""

# UI Endpoints
echo -e "${BLUE}=== UI Endpoints (2 endpoints) ===${NC}"
test_endpoint "GET" "/" "200" "Homepage" "" "UI"
test_endpoint "GET" "/admin" "200" "Admin dashboard" "" "UI"
echo ""

# Family Management
echo -e "${BLUE}=== Family Management (5 endpoints) ===${NC}"
test_endpoint "GET" "/family_list" "200" "List families" "" "Family"
test_endpoint "GET" "/family" "200" "List families (alt)" "" "Family"

# Create test family
family_response=$(curl -s -X POST "$BASE_URL/family" \
    -H "Content-Type: application/json" \
    -d '{"familyName":"Test Family Verify","parentIds":["parent_001"],"studentIds":["student_001"]}')
family_id=$(echo "$family_response" | jq -r '.familyId // empty')

test_endpoint "POST" "/family" "2XX" "Create family" '{"familyName":"Test Family 2","parentIds":["parent_002"],"studentIds":["student_002"]}' "Family"

if [ -n "$family_id" ]; then
    test_endpoint "GET" "/family/$family_id" "200" "Get family by ID" "" "Family"
    test_endpoint "DELETE" "/family/$family_id" "2XX" "Delete family" "" "Family"
else
    echo -e "  ${YELLOW}⚠ Skipping family GET/DELETE tests - no family ID${NC}"
    total_tests=$((total_tests + 2))
    failed_tests=$((failed_tests + 2))
fi
echo ""

# Animal Management
echo -e "${BLUE}=== Animal Management (7 endpoints) ===${NC}"
test_endpoint "GET" "/animal_list" "200" "List animals" "" "Animal"

# Create test animal
animal_response=$(curl -s -X POST "$BASE_URL/animal" \
    -H "Content-Type: application/json" \
    -d '{"name":"Verify Lion","scientificName":"Panthera leo","species":"Lion","status":"active"}')
animal_id=$(echo "$animal_response" | jq -r '.animalId // empty')

test_endpoint "POST" "/animal" "2XX" "Create animal" '{"name":"Test Animal 2","species":"Test Species","status":"active"}' "Animal"

if [ -n "$animal_id" ]; then
    test_endpoint "GET" "/animal/$animal_id" "200" "Get animal by ID" "" "Animal"
    test_endpoint "PUT" "/animal/$animal_id" "2XX" "Update animal" '{"name":"Updated Lion","status":"active"}' "Animal"
    test_endpoint "GET" "/animal_config?animalId=$animal_id" "2XX" "Get animal config" "" "Animal"
    test_endpoint "PATCH" "/animal_config?animalId=$animal_id" "2XX" "Update animal config" '{"personality":"friendly"}' "Animal"
    test_endpoint "DELETE" "/animal/$animal_id" "2XX" "Delete animal (soft)" "" "Animal"
else
    echo -e "  ${YELLOW}⚠ Skipping animal tests - no animal ID${NC}"
    total_tests=$((total_tests + 5))
    failed_tests=$((failed_tests + 5))
fi
echo ""

# System Endpoints
echo -e "${BLUE}=== System Endpoints (1 endpoint) ===${NC}"
test_endpoint "GET" "/system_health" "200" "System health check" "" "System"
echo ""

# Guardrails Management
echo -e "${BLUE}=== Guardrails Management (9 endpoints) ===${NC}"
test_endpoint "GET" "/guardrails" "2XX" "List guardrails" "" "Guardrails"
test_endpoint "GET" "/guardrails/templates" "200" "Get templates" "" "Guardrails"

guardrail_response=$(curl -s -X POST "$BASE_URL/guardrails" \
    -H "Content-Type: application/json" \
    -d '{"name":"Test Guardrail","type":"ALWAYS","rule":"Test rule","description":"Test description"}')
guardrail_id=$(echo "$guardrail_response" | jq -r '.guardrailId // empty')

test_endpoint "POST" "/guardrails" "2XX" "Create guardrail" '{"name":"Test 2","type":"NEVER","rule":"Never do this","description":"Test"}' "Guardrails"

if [ -n "$guardrail_id" ]; then
    test_endpoint "GET" "/guardrails/$guardrail_id" "2XX" "Get guardrail by ID" "" "Guardrails"
    test_endpoint "PUT" "/guardrails/$guardrail_id" "2XX" "Update guardrail" '{"name":"Updated","type":"ENCOURAGE","rule":"Encourage this"}' "Guardrails"
    test_endpoint "DELETE" "/guardrails/$guardrail_id" "2XX" "Delete guardrail" "" "Guardrails"
else
    echo -e "  ${YELLOW}⚠ Skipping guardrail tests - no guardrail ID${NC}"
    total_tests=$((total_tests + 3))
    failed_tests=$((failed_tests + 3))
fi

if [ -n "$animal_id" ]; then
    test_endpoint "GET" "/animal/$animal_id/guardrails/effective" "2XX" "Get effective guardrails" "" "Guardrails"
    test_endpoint "GET" "/animal/$animal_id/guardrails/system-prompt" "2XX" "Get system prompt" "" "Guardrails"
else
    total_tests=$((total_tests + 2))
    failed_tests=$((failed_tests + 2))
fi
echo ""

# User Management
echo -e "${BLUE}=== User Management (5 endpoints) ===${NC}"
test_endpoint "GET" "/user" "200" "List users" "" "User"

user_response=$(curl -s -X POST "$BASE_URL/user" \
    -H "Content-Type: application/json" \
    -d '{"displayName":"Test User","email":"test@verify.com","role":"user"}')
user_id=$(echo "$user_response" | jq -r '.userId // empty')

test_endpoint "POST" "/user" "2XX" "Create user" '{"displayName":"Test User 2","email":"test2@verify.com","role":"user"}' "User"

if [ -n "$user_id" ]; then
    test_endpoint "GET" "/user/$user_id" "200" "Get user by ID" "" "User"
    test_endpoint "PATCH" "/user/$user_id" "2XX" "Update user" '{"displayName":"Updated User"}' "User"
    test_endpoint "DELETE" "/user/$user_id" "2XX" "Delete user" "" "User"
else
    echo -e "  ${YELLOW}⚠ Skipping user tests - no user ID${NC}"
    total_tests=$((total_tests + 3))
    failed_tests=$((failed_tests + 3))
fi
echo ""

# Calculate statistics
pass_rate=0
if [ $total_tests -gt 0 ]; then
    pass_rate=$(echo "scale=1; ($passed_tests * 100) / $total_tests" | bc)
fi

# Summary
echo "================================================================"
echo "  Verification Summary"
echo "================================================================"
echo "Total Endpoints Tested: $total_tests"
echo -e "Passed:                 ${GREEN}$passed_tests${NC} (${pass_rate}%)"
echo -e "Failed:                 ${RED}$failed_tests${NC}"
echo ""

# Update summary in JSON
jq --arg total "$total_tests" \
   --arg passed "$passed_tests" \
   --arg failed "$failed_tests" \
   --arg pass_rate "$pass_rate" \
   '.summary = {"totalTests": ($total | tonumber), "passed": ($passed | tonumber), "failed": ($failed | tonumber), "passRate": ($pass_rate | tonumber)}' \
   "$RESULTS_FILE" > "${RESULTS_FILE}.tmp" && mv "${RESULTS_FILE}.tmp" "$RESULTS_FILE"

echo "Detailed results saved to: $RESULTS_FILE"
echo ""

# Status message
if [ $failed_tests -eq 0 ]; then
    echo -e "${GREEN}✓ All implemented endpoints are still working!${NC}"
    exit 0
elif [ $passed_tests -gt $((total_tests / 2)) ]; then
    echo -e "${YELLOW}⚠ Most endpoints working, but $failed_tests failures detected${NC}"
    exit 1
else
    echo -e "${RED}✗ Significant failures detected ($failed_tests/$total_tests)${NC}"
    exit 1
fi
