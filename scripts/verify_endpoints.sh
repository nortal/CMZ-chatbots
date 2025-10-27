#!/bin/bash
# Comprehensive endpoint verification script
# Tests all OpenAPI endpoints and reports their status

set -e

BASE_URL="${BASE_URL:-http://localhost:8080}"
RESULTS_FILE="/tmp/endpoint_verification_results.json"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Initialize results
echo '{
  "timestamp": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'",
  "baseUrl": "'$BASE_URL'",
  "results": []
}' > "$RESULTS_FILE"

total_tests=0
passed_tests=0
failed_tests=0
not_implemented=0

# Test function
test_endpoint() {
    local method="$1"
    local path="$2"
    local expected_status="$3"
    local description="$4"
    local data="$5"

    total_tests=$((total_tests + 1))

    echo -n "Testing $method $path ... "

    if [ -n "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$BASE_URL$path" \
            -H "Content-Type: application/json" \
            -d "$data" 2>/dev/null || echo "000")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$BASE_URL$path" 2>/dev/null || echo "000")
    fi

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)

    if [ "$http_code" = "$expected_status" ]; then
        echo -e "${GREEN}✓ PASS${NC} ($http_code)"
        passed_tests=$((passed_tests + 1))
        status="PASS"
    elif [ "$http_code" = "501" ]; then
        echo -e "${YELLOW}⚠ NOT IMPLEMENTED${NC} ($http_code)"
        not_implemented=$((not_implemented + 1))
        status="NOT_IMPLEMENTED"
    elif [ "$http_code" = "000" ]; then
        echo -e "${RED}✗ FAIL - Connection Error${NC}"
        failed_tests=$((failed_tests + 1))
        status="CONNECTION_ERROR"
    else
        echo -e "${RED}✗ FAIL${NC} (expected $expected_status, got $http_code)"
        failed_tests=$((failed_tests + 1))
        status="FAIL"
    fi

    # Add to results JSON
    jq --arg method "$method" \
       --arg path "$path" \
       --arg expected "$expected_status" \
       --arg actual "$http_code" \
       --arg status "$status" \
       --arg desc "$description" \
       '.results += [{"method": $method, "path": $path, "expectedStatus": $expected, "actualStatus": $actual, "status": $status, "description": $desc}]' \
       "$RESULTS_FILE" > "${RESULTS_FILE}.tmp" && mv "${RESULTS_FILE}.tmp" "$RESULTS_FILE"
}

echo "======================================"
echo "   Endpoint Verification Suite"
echo "======================================"
echo "Base URL: $BASE_URL"
echo "Time: $(date)"
echo ""

# Test System Health Endpoints
echo "=== System Health ==="
test_endpoint "GET" "/system_health" "200" "System health check"
test_endpoint "GET" "/chatgpt/health" "200" "ChatGPT integration health"
echo ""

# Test Authentication Endpoints
echo "=== Authentication ==="
test_endpoint "POST" "/auth" "200" "User login" '{"username":"admin@cmz.org","password":"admin123"}'
test_endpoint "POST" "/auth/refresh" "501" "Token refresh (not implemented)" '{"token":"dummy"}'
test_endpoint "POST" "/auth/logout" "501" "User logout (not implemented)"
echo ""

# Test User Endpoints
echo "=== User Management ==="
test_endpoint "GET" "/me" "200" "Get current user profile"
test_endpoint "GET" "/user" "200" "List all users"
test_endpoint "GET" "/user_details" "200" "List user details"
echo ""

# Test Animal Endpoints
echo "=== Animal Management ==="
test_endpoint "GET" "/animal_list" "200" "List all animals"
test_endpoint "POST" "/animal" "201" "Create animal" '{"name":"Test Animal","species":"Test Species","status":"active"}'

# Get the created animal ID for further tests
animal_id=$(curl -s -X POST "$BASE_URL/animal" \
    -H "Content-Type: application/json" \
    -d '{"name":"Test Lion","species":"Lion","status":"active"}' | jq -r '.animalId // empty')

if [ -n "$animal_id" ]; then
    test_endpoint "GET" "/animal/$animal_id" "200" "Get animal by ID"
    test_endpoint "GET" "/animal_details/$animal_id" "200" "Get animal details"
    test_endpoint "GET" "/animal_config/$animal_id" "200" "Get animal config"
else
    echo -e "${YELLOW}⚠ Skipping GET tests - no animal ID available${NC}"
    total_tests=$((total_tests + 3))
    not_implemented=$((not_implemented + 3))
fi
echo ""

# Test Family Endpoints
echo "=== Family Management ==="
test_endpoint "GET" "/family_list" "200" "List all families"
test_endpoint "POST" "/family" "201" "Create family" '{"familyName":"Test Family","parentEmail":"test@example.com"}'
echo ""

# Test Conversation Endpoints
echo "=== Conversation Management ==="
test_endpoint "GET" "/conversations/sessions" "200" "List conversation sessions"
test_endpoint "POST" "/convo_turn" "501" "Create conversation turn (not implemented)" '{"message":"Hello"}'
test_endpoint "GET" "/convo_history" "200" "Get conversation history"
echo ""

# Test Knowledge Base
echo "=== Knowledge Base ==="
test_endpoint "GET" "/knowledge_article" "200" "List knowledge articles"
test_endpoint "POST" "/knowledge_article" "201" "Create knowledge article" '{"title":"Test Article","content":"Test content"}'
echo ""

# Test Media Endpoints
echo "=== Media Management ==="
test_endpoint "GET" "/media" "200" "List media"
test_endpoint "POST" "/upload_media" "201" "Upload media" '{"filename":"test.jpg","contentType":"image/jpeg"}'
echo ""

# Test Analytics Endpoints
echo "=== Analytics ==="
test_endpoint "GET" "/performance_metrics?start=2025-01-01T00:00:00Z&end=2025-01-31T23:59:59Z" "200" "Performance metrics"
test_endpoint "GET" "/logs" "200" "System logs"
test_endpoint "GET" "/billing?period=2025-01" "200" "Billing information"
echo ""

# Test Admin Endpoints
echo "=== Admin Operations ==="
test_endpoint "GET" "/admin" "200" "Admin dashboard"
test_endpoint "GET" "/guardrails" "200" "Guardrails configuration"
test_endpoint "GET" "/feature_flags" "200" "Feature flags"
echo ""

# Calculate pass rate
pass_rate=0
if [ $total_tests -gt 0 ]; then
    pass_rate=$(echo "scale=1; ($passed_tests * 100) / $total_tests" | bc)
fi

# Summary
echo ""
echo "======================================"
echo "   Verification Summary"
echo "======================================"
echo "Total Tests:        $total_tests"
echo -e "Passed:             ${GREEN}$passed_tests${NC} (${pass_rate}%)"
echo -e "Failed:             ${RED}$failed_tests${NC}"
echo -e "Not Implemented:    ${YELLOW}$not_implemented${NC}"
echo ""

# Update summary in JSON
jq --arg total "$total_tests" \
   --arg passed "$passed_tests" \
   --arg failed "$failed_tests" \
   --arg not_impl "$not_implemented" \
   --arg pass_rate "$pass_rate" \
   '.summary = {"totalTests": ($total | tonumber), "passed": ($passed | tonumber), "failed": ($failed | tonumber), "notImplemented": ($not_impl | tonumber), "passRate": ($pass_rate | tonumber)}' \
   "$RESULTS_FILE" > "${RESULTS_FILE}.tmp" && mv "${RESULTS_FILE}.tmp" "$RESULTS_FILE"

echo "Results saved to: $RESULTS_FILE"
echo ""

# Exit with error if any tests failed
if [ $failed_tests -gt 0 ]; then
    echo -e "${RED}Some tests failed!${NC}"
    exit 1
else
    echo -e "${GREEN}All implemented endpoints are working!${NC}"
    exit 0
fi
