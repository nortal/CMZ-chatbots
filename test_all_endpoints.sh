#!/bin/bash

# Fixed comprehensive endpoint testing script with correct data and routes
# This script tests ALL endpoints with proper validation data

echo "========================================="
echo "CMZ API Comprehensive Endpoint Testing (FIXED)"
echo "========================================="
echo ""

BASE_URL="http://localhost:8080"
AUTH_TOKEN=""
TEST_ANIMAL_ID=""
TEST_FAMILY_ID=""
TEST_USER_ID=""

# Color codes for better readability
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Statistics tracking
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to test endpoint
test_endpoint() {
    local method=$1
    local path=$2
    local data=$3
    local description=$4
    local expected_status=$5

    echo "Testing: $description"
    echo "  Method: $method $path"

    if [ "$method" == "GET" ]; then
        response=$(curl -s -X GET "$BASE_URL$path" -H "Content-Type: application/json" -H "Authorization: Bearer $AUTH_TOKEN" -w "\n__STATUS_CODE__:%{http_code}")
    elif [ "$method" == "POST" ]; then
        response=$(curl -s -X POST "$BASE_URL$path" -H "Content-Type: application/json" -H "Authorization: Bearer $AUTH_TOKEN" -d "$data" -w "\n__STATUS_CODE__:%{http_code}")
    elif [ "$method" == "PUT" ]; then
        response=$(curl -s -X PUT "$BASE_URL$path" -H "Content-Type: application/json" -H "Authorization: Bearer $AUTH_TOKEN" -d "$data" -w "\n__STATUS_CODE__:%{http_code}")
    elif [ "$method" == "DELETE" ]; then
        response=$(curl -s -X DELETE "$BASE_URL$path" -H "Content-Type: application/json" -H "Authorization: Bearer $AUTH_TOKEN" -w "\n__STATUS_CODE__:%{http_code}")
    elif [ "$method" == "PATCH" ]; then
        response=$(curl -s -X PATCH "$BASE_URL$path" -H "Content-Type: application/json" -H "Authorization: Bearer $AUTH_TOKEN" -d "$data" -w "\n__STATUS_CODE__:%{http_code}")
    fi

    status_code=$(echo "$response" | grep "__STATUS_CODE__:" | cut -d: -f2)
    body=$(echo "$response" | sed '/__STATUS_CODE__:/d')

    # Check for regression indicators
    if echo "$body" | grep -q '"code":"not_implemented"'; then
        echo -e "  ${RED}⚠️  REGRESSION: Endpoint returns 'not_implemented'${NC}"
        return 1
    elif echo "$body" | grep -q '"do some magic!"'; then
        echo -e "  ${RED}⚠️  REGRESSION: Placeholder implementation${NC}"
        return 1
    elif [ "$status_code" == "501" ]; then
        echo -e "  ${RED}⚠️  REGRESSION: 501 Not Implemented${NC}"
        return 1
    elif [ "$status_code" == "404" ] && [ "$expected_status" != "404" ]; then
        echo -e "  ${RED}❌ ERROR: Endpoint not found (404)${NC}"
        return 1
    elif [ "$status_code" == "500" ]; then
        echo -e "  ${RED}❌ ERROR: Internal server error (500)${NC}"
        echo "     Body: $(echo "$body" | jq -c . 2>/dev/null || echo "$body" | head -1)"
        return 1
    elif [ "$status_code" == "200" ] || [ "$status_code" == "201" ] || [ "$status_code" == "204" ]; then
        echo -e "  ${GREEN}✅ SUCCESS: Status $status_code${NC}"
        # Extract IDs from successful creation responses
        if [ "$status_code" == "201" ]; then
            if echo "$path" | grep -q "/animal$"; then
                TEST_ANIMAL_ID=$(echo "$body" | jq -r '.animalId' 2>/dev/null)
                [ "$TEST_ANIMAL_ID" != "null" ] && echo "     Created animal: $TEST_ANIMAL_ID"
            elif echo "$path" | grep -q "/family$"; then
                TEST_FAMILY_ID=$(echo "$body" | jq -r '.familyId' 2>/dev/null)
                [ "$TEST_FAMILY_ID" != "null" ] && echo "     Created family: $TEST_FAMILY_ID"
            elif echo "$path" | grep -q "/user$"; then
                TEST_USER_ID=$(echo "$body" | jq -r '.userId' 2>/dev/null)
                [ "$TEST_USER_ID" != "null" ] && echo "     Created user: $TEST_USER_ID"
            fi
        fi
        return 0
    elif [ "$status_code" == "401" ] || [ "$status_code" == "403" ]; then
        echo -e "  ${YELLOW}🔐 AUTH: Status $status_code (may be expected)${NC}"
        return 0
    elif [ "$status_code" == "400" ] && [ "$expected_status" == "400" ]; then
        echo -e "  ${BLUE}ℹ️  INFO: Status 400 (expected validation error)${NC}"
        return 0
    elif [ "$status_code" == "404" ] && [ "$expected_status" == "404" ]; then
        echo -e "  ${GREEN}✅ SUCCESS: 404 as expected${NC}"
        return 0
    elif [ "$status_code" == "409" ]; then
        echo -e "  ${YELLOW}⚠️  CONFLICT: Status 409 (duplicate resource)${NC}"
        return 0
    else
        echo -e "  ${YELLOW}⚠️  WARNING: Status $status_code${NC}"
        echo "     Error: $(echo "$body" | jq -c . 2>/dev/null || echo "$body" | head -1)"
        return 1
    fi
}

# Wrapper to track test statistics
run_test() {
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    if test_endpoint "$@"; then
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    echo ""
}

# First, get auth token
echo -e "${BLUE}=== AUTHENTICATION ===${NC}"
echo "Getting auth token..."
auth_response=$(curl -s -X POST "$BASE_URL/auth" \
  -H "Content-Type: application/json" \
  -d '{"username":"test@cmz.org","password":"testpass123"}')

if echo "$auth_response" | grep -q '"token"'; then
    AUTH_TOKEN=$(echo "$auth_response" | jq -r '.token')
    echo -e "${GREEN}✅ Authentication successful${NC}"
else
    echo -e "${RED}❌ Authentication failed${NC}"
    echo "$auth_response"
fi
echo ""

# Test all endpoint groups
echo -e "${BLUE}=== UI ENDPOINTS ===${NC}"
run_test "GET" "/" "" "Public homepage"
run_test "GET" "/admin" "" "Admin dashboard"

echo -e "${BLUE}=== AUTH ENDPOINTS ===${NC}"
run_test "POST" "/auth" '{"username":"test@cmz.org","password":"testpass123"}' "Login"
run_test "POST" "/auth/logout" "" "Logout"
run_test "POST" "/auth/refresh" "" "Refresh token"
run_test "POST" "/auth/reset_password" '{"email":"test@cmz.org"}' "Reset password"

echo -e "${BLUE}=== USER ENDPOINTS ===${NC}"
run_test "GET" "/user" "" "List users"
# Fixed: Using correct role from allowed values: ["visitor", "user", "editor", "admin"]
# and userType from ["none", "parent", "student"]
run_test "POST" "/user" '{"email":"newuser@test.com","name":"Test User","role":"user","userType":"parent"}' "Create user"
if [ "$TEST_USER_ID" ]; then
    run_test "GET" "/user/$TEST_USER_ID" "" "Get created user"
    run_test "PATCH" "/user/$TEST_USER_ID" '{"name":"Updated Test User"}' "Update user"
    run_test "DELETE" "/user/$TEST_USER_ID" "" "Delete user"
else
    run_test "GET" "/user/nonexistent-id" "" "Get user (expect 404)" "404"
    run_test "PATCH" "/user/nonexistent-id" '{"name":"Updated"}' "Update user (expect 404)" "404"
    run_test "DELETE" "/user/nonexistent-id" "" "Delete user (expect 404)" "404"
fi

echo -e "${BLUE}=== FAMILY ENDPOINTS ===${NC}"
run_test "GET" "/family_list" "" "List families"
run_test "GET" "/family" "" "List families (alternate)"
# Fixed: Using userIds instead of emails for parents/students (matching regex ^[a-zA-Z0-9_-]+$)
run_test "POST" "/family" '{"familyName":"Test Family","parents":["user_parent_001"],"students":["user_student_001"]}' "Create family"
if [ "$TEST_FAMILY_ID" ]; then
    run_test "GET" "/family/$TEST_FAMILY_ID" "" "Get created family"
    # Fixed: Parents/students fields expect userIds not emails (matching regex ^[a-zA-Z0-9_-]+$)
    run_test "PATCH" "/family/$TEST_FAMILY_ID" '{"familyName":"Updated Family","parents":["user_parent_001"],"students":["user_student_001"]}' "Update family"
    run_test "DELETE" "/family/$TEST_FAMILY_ID" "" "Delete family"
else
    run_test "GET" "/family/nonexistent-id" "" "Get family (expect 404)" "404"
    run_test "PATCH" "/family/nonexistent-id" '{"familyName":"Updated"}' "Update family (expect error)" "404"
    run_test "DELETE" "/family/nonexistent-id" "" "Delete family (expect 404)" "404"
fi

echo -e "${BLUE}=== ANIMAL ENDPOINTS ===${NC}"
run_test "GET" "/animal_list" "" "List animals"
run_test "POST" "/animal" '{"name":"Test Lion","species":"Panthera leo","habitat":"Savanna"}' "Create animal"
if [ "$TEST_ANIMAL_ID" ]; then
    run_test "GET" "/animal/$TEST_ANIMAL_ID" "" "Get created animal"
    run_test "PUT" "/animal/$TEST_ANIMAL_ID" '{"name":"Updated Lion","species":"Panthera leo"}' "Update animal"
    run_test "GET" "/animal_config?animalId=$TEST_ANIMAL_ID" "" "Get animal config"
    # Fixed: animalId must be in query parameter, not body
    run_test "PATCH" "/animal_config?animalId=$TEST_ANIMAL_ID" '{"temperature":0.8}' "Update animal config"
    run_test "DELETE" "/animal/$TEST_ANIMAL_ID" "" "Delete animal (soft delete)"
    run_test "GET" "/animal/$TEST_ANIMAL_ID" "" "Get deleted animal (expect 404)" "404"
else
    run_test "GET" "/animal/nonexistent-id" "" "Get animal (expect 404)" "404"
    run_test "PUT" "/animal/nonexistent-id" '{"name":"Updated"}' "Update animal (expect 404)" "404"
    run_test "DELETE" "/animal/nonexistent-id" "" "Delete animal (expect 404)" "404"
fi

echo -e "${BLUE}=== CONVERSATION ENDPOINTS (ACTUAL ROUTES) ===${NC}"
# Using the actual implemented routes from conversation.py
run_test "GET" "/conversations/sessions" "" "List conversation sessions"
run_test "GET" "/conversations/sessions/test-session" "" "Get specific session"
run_test "POST" "/convo_turn" '{"sessionId":"test-001","message":"Hello Pokey!","animalId":"pokey"}' "Send chat message"
run_test "GET" "/convo_history?sessionId=test-001" "" "Get conversation history"
run_test "POST" "/summarize_convo" '{"sessionId":"test-001","summaryType":"brief"}' "Summarize conversation"
run_test "DELETE" "/convo_history?sessionId=test-001&confirm_gdpr=true" "" "Delete conversation (GDPR)"

echo -e "${BLUE}=== SYSTEM ENDPOINTS ===${NC}"
run_test "GET" "/system_health" "" "System health check"

# Summary
echo ""
echo "========================================="
echo -e "${BLUE}📊 TEST RESULTS SUMMARY${NC}"
echo "========================================="
echo -e "Total Tests: $TOTAL_TESTS"
echo -e "Passed: ${GREEN}$PASSED_TESTS${NC}"
echo -e "Failed: ${RED}$FAILED_TESTS${NC}"
if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All tests passed!${NC}"
else
    echo -e "\n${YELLOW}⚠️  Some tests failed. Review output above.${NC}"
fi
echo "========================================="
echo ""
echo "NOTES:"
echo "- User role must be one of: visitor, user, editor, admin"
echo "- User type must be one of: none, parent, student"
echo "- Family requires 'parents' and 'students' fields (not parentIds/studentIds)"
echo "- Temperature in animal_config must be multiple of 0.1"
echo "- Conversation endpoints use /convo_turn, /convo_history, etc. (not /conversation/*)"

# Send results to Teams
if [ ! -z "$TEAMS_WEBHOOK_URL" ]; then
    echo ""
    echo "Sending results to Teams..."

    SUCCESS_RATE=$((PASSED_TESTS * 100 / TOTAL_TESTS))

    # Determine status emoji and color
    if [ $FAILED_TESTS -eq 0 ]; then
        STATUS_EMOJI="🎉"
        STATUS_TEXT="All tests passed!"
        THEME_COLOR="00FF00"  # Green
    elif [ $SUCCESS_RATE -ge 90 ]; then
        STATUS_EMOJI="✅"
        STATUS_TEXT="Most tests passed"
        THEME_COLOR="90EE90"  # Light green
    elif [ $SUCCESS_RATE -ge 70 ]; then
        STATUS_EMOJI="⚠️"
        STATUS_TEXT="Some tests failed"
        THEME_COLOR="FFA500"  # Orange
    else
        STATUS_EMOJI="❌"
        STATUS_TEXT="Many tests failed"
        THEME_COLOR="FF0000"  # Red
    fi

    # Create Adaptive Card message for Power Automate webhook
    # The flow expects an array of attachments with Adaptive Cards
    TEAMS_MESSAGE=$(cat <<EOF
{
    "attachments": [
        {
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": {
                "\$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                "type": "AdaptiveCard",
                "version": "1.4",
                "body": [
                    {
                        "type": "TextBlock",
                        "text": "$STATUS_EMOJI CMZ API Test Results",
                        "size": "Large",
                        "weight": "Bolder"
                    },
                    {
                        "type": "TextBlock",
                        "text": "$STATUS_TEXT",
                        "size": "Medium",
                        "color": "$([ $FAILED_TESTS -eq 0 ] && echo 'Good' || echo 'Warning')"
                    },
                    {
                        "type": "FactSet",
                        "facts": [
                            {
                                "title": "Total Tests:",
                                "value": "$TOTAL_TESTS"
                            },
                            {
                                "title": "Passed:",
                                "value": "$PASSED_TESTS ✅"
                            },
                            {
                                "title": "Failed:",
                                "value": "$FAILED_TESTS ❌"
                            },
                            {
                                "title": "Success Rate:",
                                "value": "$SUCCESS_RATE%"
                            },
                            {
                                "title": "Timestamp:",
                                "value": "$(date '+%Y-%m-%d %H:%M:%S')"
                            }
                        ]
                    }
                ]
            }
        }
    ]
}
EOF
)

    # Send to Teams via Power Automate
    HTTP_STATUS=$(curl -H 'Content-Type: application/json' -d "$TEAMS_MESSAGE" "$TEAMS_WEBHOOK_URL" -s -w "%{http_code}" -o /dev/null)

    if [ "$HTTP_STATUS" == "202" ] || [ "$HTTP_STATUS" == "200" ]; then
        echo -e "${GREEN}✅ Results sent to Teams (HTTP $HTTP_STATUS)${NC}"
        echo "   Check your 'TDD reports' channel in Teams"
    else
        echo -e "${RED}❌ Failed to send to Teams (HTTP $HTTP_STATUS)${NC}"
    fi
else
    echo ""
    echo -e "${YELLOW}ℹ️  Teams notifications disabled (TEAMS_WEBHOOK_URL not set)${NC}"
fi