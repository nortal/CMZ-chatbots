#!/bin/bash

# Test GitHub Token Permissions Script
# Usage: ./test_github_token.sh [token]
# If no token is provided, it will use GITHUB_TOKEN environment variable

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get token from argument or environment
if [ -n "$1" ]; then
    TOKEN="$1"
    echo -e "${BLUE}Using token from command line argument${NC}"
elif [ -n "$GITHUB_TOKEN" ]; then
    TOKEN="$GITHUB_TOKEN"
    echo -e "${BLUE}Using token from GITHUB_TOKEN environment variable${NC}"
else
    echo -e "${RED}Error: No token provided${NC}"
    echo "Usage: $0 [token]"
    echo "Or set GITHUB_TOKEN environment variable"
    exit 1
fi

# Mask token for display
MASKED_TOKEN="${TOKEN:0:10}...${TOKEN: -4}"
echo -e "${BLUE}Testing token: ${MASKED_TOKEN}${NC}\n"

echo "========================================="
echo "1. TESTING BASIC AUTHENTICATION"
echo "========================================="

# Test basic authentication
AUTH_RESPONSE=$(curl -s -H "Authorization: token $TOKEN" https://api.github.com/user)

if echo "$AUTH_RESPONSE" | grep -q '"login"'; then
    USERNAME=$(echo "$AUTH_RESPONSE" | grep '"login"' | cut -d'"' -f4)
    echo -e "${GREEN}✓ Authentication successful${NC}"
    echo -e "  Logged in as: ${USERNAME}"

    # Get user ID and type
    USER_ID=$(echo "$AUTH_RESPONSE" | grep '"id"' | head -1 | grep -o '[0-9]*')
    USER_TYPE=$(echo "$AUTH_RESPONSE" | grep '"type"' | cut -d'"' -f4)
    echo -e "  User ID: ${USER_ID}"
    echo -e "  Account type: ${USER_TYPE}"
else
    echo -e "${RED}✗ Authentication failed${NC}"
    echo "$AUTH_RESPONSE" | head -3
    exit 1
fi

echo ""
echo "========================================="
echo "2. CHECKING TOKEN SCOPES"
echo "========================================="

# Get token scopes from response headers
SCOPES_RESPONSE=$(curl -sI -H "Authorization: token $TOKEN" https://api.github.com/user | grep -i "x-oauth-scopes:" | cut -d' ' -f2-)

if [ -n "$SCOPES_RESPONSE" ]; then
    echo -e "${GREEN}Token scopes:${NC}"
    IFS=',' read -ra SCOPES <<< "$SCOPES_RESPONSE"
    for scope in "${SCOPES[@]}"; do
        scope=$(echo "$scope" | xargs)  # Trim whitespace
        echo "  • $scope"
    done
else
    echo -e "${YELLOW}⚠ No scopes found (might be a fine-grained token)${NC}"
fi

echo ""
echo "========================================="
echo "3. TESTING REPOSITORY ACCESS"
echo "========================================="

# Test access to the CMZ-chatbots repository
REPO_RESPONSE=$(curl -s -H "Authorization: token $TOKEN" https://api.github.com/repos/nortal/CMZ-chatbots)

if echo "$REPO_RESPONSE" | grep -q '"full_name"'; then
    echo -e "${GREEN}✓ Can access nortal/CMZ-chatbots repository${NC}"

    # Check permissions
    PERMISSIONS=$(echo "$REPO_RESPONSE" | grep -A10 '"permissions"')

    # Parse permissions
    CAN_PULL=$(echo "$PERMISSIONS" | grep '"pull"' | grep -o 'true\|false')
    CAN_PUSH=$(echo "$PERMISSIONS" | grep '"push"' | grep -o 'true\|false')
    CAN_ADMIN=$(echo "$PERMISSIONS" | grep '"admin"' | grep -o 'true\|false')

    echo "  Permissions:"
    if [ "$CAN_PULL" = "true" ]; then
        echo -e "    ${GREEN}✓ Pull (read)${NC}"
    else
        echo -e "    ${RED}✗ Pull (read)${NC}"
    fi

    if [ "$CAN_PUSH" = "true" ]; then
        echo -e "    ${GREEN}✓ Push (write)${NC}"
    else
        echo -e "    ${RED}✗ Push (write)${NC}"
    fi

    if [ "$CAN_ADMIN" = "true" ]; then
        echo -e "    ${GREEN}✓ Admin${NC}"
    else
        echo -e "    ${YELLOW}○ Admin (not required for PRs)${NC}"
    fi
else
    echo -e "${RED}✗ Cannot access nortal/CMZ-chatbots repository${NC}"
    echo "$REPO_RESPONSE" | head -3
fi

echo ""
echo "========================================="
echo "4. TESTING ORGANIZATION ACCESS"
echo "========================================="

# Test organization membership
ORG_RESPONSE=$(curl -s -H "Authorization: token $TOKEN" https://api.github.com/user/memberships/orgs/nortal)

if echo "$ORG_RESPONSE" | grep -q '"organization"'; then
    echo -e "${GREEN}✓ Member of Nortal organization${NC}"

    # Get membership details
    ROLE=$(echo "$ORG_RESPONSE" | grep '"role"' | cut -d'"' -f4)
    STATE=$(echo "$ORG_RESPONSE" | grep '"state"' | cut -d'"' -f4)

    echo "  Role: $ROLE"
    echo "  State: $STATE"
else
    echo -e "${YELLOW}⚠ Not a member of Nortal organization (or no access)${NC}"
    echo "  This may limit PR creation abilities"
fi

echo ""
echo "========================================="
echo "5. TESTING PULL REQUEST PERMISSIONS"
echo "========================================="

# Test if we can list pull requests (basic PR permission check)
PR_LIST_RESPONSE=$(curl -s -H "Authorization: token $TOKEN" https://api.github.com/repos/nortal/CMZ-chatbots/pulls?state=all&per_page=1)

if echo "$PR_LIST_RESPONSE" | grep -q '\[' || echo "$PR_LIST_RESPONSE" | grep -q '"number"'; then
    echo -e "${GREEN}✓ Can list pull requests${NC}"
else
    echo -e "${RED}✗ Cannot list pull requests${NC}"
fi

# Check if token can create PRs (check for write access)
if [ "$CAN_PUSH" = "true" ]; then
    echo -e "${GREEN}✓ Should be able to create pull requests${NC}"
else
    echo -e "${RED}✗ Insufficient permissions to create pull requests${NC}"
    echo "  Token needs 'push' permission on the repository"
fi

echo ""
echo "========================================="
echo "6. TESTING API RATE LIMITS"
echo "========================================="

# Check rate limits
RATE_RESPONSE=$(curl -s -H "Authorization: token $TOKEN" https://api.github.com/rate_limit)

if echo "$RATE_RESPONSE" | grep -q '"rate"'; then
    LIMIT=$(echo "$RATE_RESPONSE" | grep -A3 '"core"' | grep '"limit"' | grep -o '[0-9]*')
    REMAINING=$(echo "$RATE_RESPONSE" | grep -A3 '"core"' | grep '"remaining"' | grep -o '[0-9]*')

    echo -e "API Rate Limit: ${REMAINING}/${LIMIT} requests remaining"

    if [ "$LIMIT" -gt 60 ]; then
        echo -e "${GREEN}✓ Authenticated rate limit (higher than anonymous)${NC}"
    else
        echo -e "${YELLOW}⚠ Low rate limit (might be unauthenticated)${NC}"
    fi
fi

echo ""
echo "========================================="
echo "SUMMARY"
echo "========================================="

# Determine overall status
CAN_CREATE_PR=true
ISSUES=""

if [ "$CAN_PUSH" != "true" ]; then
    CAN_CREATE_PR=false
    ISSUES="${ISSUES}\n  • Missing push permission on repository"
fi

if echo "$SCOPES_RESPONSE" | grep -q "repo" || [ -z "$SCOPES_RESPONSE" ]; then
    :  # Good - has repo scope or is fine-grained token
else
    CAN_CREATE_PR=false
    ISSUES="${ISSUES}\n  • Missing 'repo' scope in token"
fi

if [ "$CAN_CREATE_PR" = true ]; then
    echo -e "${GREEN}✓ Token appears to have sufficient permissions for creating PRs${NC}"
else
    echo -e "${RED}✗ Token does NOT have sufficient permissions for creating PRs${NC}"
    echo -e "\nIssues found:${ISSUES}"
    echo -e "\nTo fix:"
    echo "  1. Create a new personal access token at https://github.com/settings/tokens"
    echo "  2. Select the 'repo' scope (full control of private repositories)"
    echo "  3. If using an organization repository, ensure the token is authorized for the organization"
    echo "  4. Save the token to .env.local as GITHUB_TOKEN=<your_token>"
fi

echo ""
echo "========================================="
echo "For more details, see: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token"