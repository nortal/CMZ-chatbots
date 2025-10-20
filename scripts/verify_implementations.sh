#!/bin/bash
# Comprehensive Implementation Verification Tool
# Tests actual functionality of each endpoint

set -e

API_URL=${API_URL:-http://localhost:8080}
IMPL_DIR="backend/api/src/main/python/openapi_server/impl"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "========================================="
echo "CMZ Implementation Verification Report"
echo "$(date)"
echo "========================================="

# Track statistics
TOTAL=0
WORKING=0
STUB=0
ERROR=0
NOT_FOUND=0

# Function to test an endpoint
test_endpoint() {
    local method=$1
    local path=$2
    local description=$3
    local body=${4:-}

    TOTAL=$((TOTAL + 1))

    echo -e "\n${BLUE}Testing: $description${NC}"
    echo "  $method $path"

    if [ -n "$body" ]; then
        RESPONSE=$(curl -s -w "\n%{http_code}" -X "$method" "$API_URL$path" \
                   -H "Content-Type: application/json" \
                   -d "$body" 2>/dev/null || echo "000")
    else
        RESPONSE=$(curl -s -w "\n%{http_code}" -X "$method" "$API_URL$path" 2>/dev/null || echo "000")
    fi

    STATUS=$(echo "$RESPONSE" | tail -1)
    BODY=$(echo "$RESPONSE" | head -n -1)

    case $STATUS in
        200|201|204)
            echo -e "  ${GREEN}✅ WORKING (Status: $STATUS)${NC}"
            WORKING=$((WORKING + 1))

            # Check if it's actually implemented or just a stub
            if echo "$BODY" | grep -q "not_implemented\|not yet implemented"; then
                echo -e "  ${YELLOW}   ⚠️  But returns 'not_implemented' message${NC}"
                STUB=$((STUB + 1))
                WORKING=$((WORKING - 1))
            fi
            ;;
        501)
            echo -e "  ${YELLOW}⚠️  STUB (Not Implemented)${NC}"
            STUB=$((STUB + 1))
            ;;
        404)
            echo -e "  ${RED}❌ NOT FOUND (Route missing)${NC}"
            NOT_FOUND=$((NOT_FOUND + 1))
            ;;
        500)
            echo -e "  ${RED}❌ ERROR (Internal Server Error)${NC}"
            ERROR=$((ERROR + 1))
            # Show error details if available
            if echo "$BODY" | grep -q "message"; then
                ERROR_MSG=$(echo "$BODY" | grep -o '"message":"[^"]*"' | head -1)
                echo -e "     ${RED}Error: $ERROR_MSG${NC}"
            fi
            ;;
        *)
            echo -e "  ${YELLOW}⚠️  UNEXPECTED (Status: $STATUS)${NC}"
            ;;
    esac

    # Check implementation file
    echo -n "  Implementation: "
    OPERATION=$(echo "$path" | sed 's/[{}\/]/_/g' | sed 's/__/_/g' | sed 's/^_//')

    if grep -r "def.*$OPERATION" "$IMPL_DIR" 2>/dev/null | head -1; then
        echo -e "${GREEN}Found${NC}"
    else
        echo -e "${YELLOW}Not found in impl/${NC}"
    fi
}

echo -e "\n${YELLOW}=== Authentication Endpoints ===${NC}"
test_endpoint "POST" "/auth" "Login" '{"email":"test@cmz.org","password":"testpass123"}'
test_endpoint "POST" "/auth/logout" "Logout"
test_endpoint "POST" "/auth/refresh" "Refresh Token"
test_endpoint "POST" "/auth/reset-password" "Reset Password" '{"email":"test@cmz.org"}'

echo -e "\n${YELLOW}=== UI Endpoints ===${NC}"
test_endpoint "GET" "/" "Homepage"
test_endpoint "GET" "/admin" "Admin Dashboard"

echo -e "\n${YELLOW}=== User Endpoints ===${NC}"
test_endpoint "GET" "/user/list" "List Users"
test_endpoint "POST" "/user" "Create User" '{"email":"new@test.com","name":"Test User"}'
test_endpoint "GET" "/user/details/test@cmz.org" "Get User Details"
test_endpoint "PUT" "/user/test@cmz.org" "Update User" '{"name":"Updated Name"}'
test_endpoint "DELETE" "/user/test@cmz.org" "Delete User"

echo -e "\n${YELLOW}=== Family Endpoints ===${NC}"
test_endpoint "GET" "/family/list" "List Families"
test_endpoint "POST" "/family" "Create Family" '{"name":"Test Family"}'
test_endpoint "GET" "/family/details/test-family" "Get Family Details"
test_endpoint "PATCH" "/family/details/test-family" "Update Family" '{"name":"Updated Family"}'
test_endpoint "DELETE" "/family/details/test-family" "Delete Family"

echo -e "\n${YELLOW}=== Animal Endpoints ===${NC}"
test_endpoint "GET" "/animal/list" "List Animals"
test_endpoint "POST" "/animal" "Create Animal" '{"name":"Test Animal","species":"Test Species"}'
test_endpoint "GET" "/animal/test-animal" "Get Animal Details"
test_endpoint "PUT" "/animal/test-animal" "Update Animal" '{"name":"Updated Animal"}'
test_endpoint "DELETE" "/animal/test-animal" "Delete Animal"
test_endpoint "GET" "/animal/config/test-animal" "Get Animal Config"
test_endpoint "POST" "/animal/config" "Save Animal Config" '{"animalId":"test","config":{}}'

echo -e "\n${YELLOW}=== Conversation Endpoints ===${NC}"
test_endpoint "POST" "/conversation" "Start Conversation" '{"userId":"test","animalId":"test"}'
test_endpoint "GET" "/conversation/list" "List Conversations"
test_endpoint "POST" "/conversation/chat" "Send Chat Message" '{"conversationId":"test","message":"Hello"}'

echo -e "\n${BLUE}=========================================${NC}"
echo -e "${BLUE}Summary Report${NC}"
echo -e "${BLUE}=========================================${NC}"
echo -e "Total Endpoints Tested: $TOTAL"
echo -e "${GREEN}✅ Working: $WORKING${NC}"
echo -e "${YELLOW}⚠️  Stubs: $STUB${NC}"
echo -e "${RED}❌ Errors: $ERROR${NC}"
echo -e "${RED}❌ Not Found: $NOT_FOUND${NC}"
echo ""
IMPL_PERCENT=$((WORKING * 100 / TOTAL))
echo -e "Implementation Progress: ${IMPL_PERCENT}%"

echo -e "\n${YELLOW}=== Recommendations ===${NC}"
if [ $NOT_FOUND -gt 0 ]; then
    echo "• Fix routing: $NOT_FOUND endpoints return 404 (check OpenAPI spec paths)"
fi
if [ $ERROR -gt 0 ]; then
    echo "• Fix errors: $ERROR endpoints have internal server errors"
fi
if [ $STUB -gt 0 ]; then
    echo "• Implement stubs: $STUB endpoints return 'not_implemented'"
fi

# Write report to file
REPORT_FILE="implementation_status_$(date +%Y%m%d_%H%M%S).txt"
{
    echo "CMZ Implementation Status Report"
    echo "Generated: $(date)"
    echo "================================="
    echo ""
    echo "Statistics:"
    echo "  Working: $WORKING/$TOTAL"
    echo "  Stubs: $STUB/$TOTAL"
    echo "  Errors: $ERROR/$TOTAL"
    echo "  Not Found: $NOT_FOUND/$TOTAL"
    echo ""
    echo "Implementation: ${IMPL_PERCENT}%"
} > "$REPORT_FILE"

echo -e "\n${GREEN}Report saved to: $REPORT_FILE${NC}"