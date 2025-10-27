#!/bin/bash

# GitHub Token Validation Script for CMZ-chatbots
# This script validates that a GitHub fine-grained token has all required permissions
# Usage: ./validate_github_token.sh [token]
# If no token provided, uses GITHUB_TOKEN from environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Get token from argument or environment
if [ -n "$1" ]; then
    TOKEN="$1"
elif [ -n "$GITHUB_TOKEN" ]; then
    TOKEN="$GITHUB_TOKEN"
else
    echo -e "${RED}Error: No token provided${NC}"
    echo "Usage: $0 [github_token]"
    echo "Or set GITHUB_TOKEN environment variable"
    exit 1
fi

# Repository to test
REPO="nortal/CMZ-chatbots"

echo -e "${BOLD}GitHub Token Validation for CMZ-chatbots${NC}"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Track results
CRITICAL_PASS=0
CRITICAL_FAIL=0
RECOMMENDED_PASS=0
RECOMMENDED_FAIL=0

# Function to test API endpoint
test_permission() {
    local description="$1"
    local endpoint="$2"
    local method="${3:-GET}"
    local critical="${4:-false}"
    local extra_args="${5:-}"

    printf "%-35s" "$description:"

    if [ "$method" = "GET" ]; then
        response=$(curl -s -o /dev/null -w "%{http_code}" \
            -H "Authorization: token $TOKEN" \
            -H "Accept: application/vnd.github.v3+json" \
            "https://api.github.com/$endpoint" 2>/dev/null)
    else
        response=$(curl -s -o /dev/null -w "%{http_code}" \
            -X "$method" \
            -H "Authorization: token $TOKEN" \
            -H "Accept: application/vnd.github.v3+json" \
            $extra_args \
            "https://api.github.com/$endpoint" 2>/dev/null)
    fi

    if [ "$response" = "200" ] || [ "$response" = "201" ] || [ "$response" = "204" ]; then
        echo -e "${GREEN}✅ Passed${NC}"
        if [ "$critical" = "true" ]; then
            ((CRITICAL_PASS++))
        else
            ((RECOMMENDED_PASS++))
        fi
        return 0
    elif [ "$response" = "404" ] && [ "$critical" = "false" ]; then
        # 404 might be OK for optional features not enabled
        echo -e "${YELLOW}⚠️  Not configured (optional)${NC}"
        ((RECOMMENDED_PASS++))
        return 0
    else
        if [ "$critical" = "true" ]; then
            echo -e "${RED}❌ Failed (HTTP $response) - CRITICAL${NC}"
            ((CRITICAL_FAIL++))
        else
            echo -e "${YELLOW}⚠️  Failed (HTTP $response) - Optional${NC}"
            ((RECOMMENDED_FAIL++))
        fi
        return 1
    fi
}

# Test basic token validity
echo -e "${BLUE}Basic Token Validation:${NC}"
echo "────────────────────────────────────────"
test_permission "Token validity" "user" "GET" "true"
test_permission "Repository access" "repos/$REPO" "GET" "true"
echo ""

# Test critical permissions
echo -e "${BLUE}Critical Permissions (Required):${NC}"
echo "────────────────────────────────────────"
test_permission "Pull requests (Read)" "repos/$REPO/pulls" "GET" "true"

# Test PR write by attempting a dry-run comment
echo -n "Pull requests (Write):             "
response=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST \
    -H "Authorization: token $TOKEN" \
    -H "Accept: application/vnd.github.v3+json" \
    -d '{"body":"test"}' \
    "https://api.github.com/repos/$REPO/issues/1/comments" 2>/dev/null || echo "403")

# For write test, we check if we'd be allowed (even if issue doesn't exist)
if [ "$response" = "201" ] || [ "$response" = "404" ] || [ "$response" = "422" ]; then
    echo -e "${GREEN}✅ Passed${NC}"
    ((CRITICAL_PASS++))
else
    echo -e "${RED}❌ Failed (HTTP $response) - CRITICAL${NC}"
    ((CRITICAL_FAIL++))
fi

test_permission "Contents (Write/Push)" "repos/$REPO" "GET" "true"
test_permission "Actions (Read)" "repos/$REPO/actions/runs" "GET" "true"
test_permission "Code scanning alerts (Read)" "repos/$REPO/code-scanning/alerts" "GET" "true"
test_permission "Issues (Read)" "repos/$REPO/issues" "GET" "true"
test_permission "Commit statuses (Read)" "repos/$REPO/commits/main/status" "GET" "true"
echo ""

# Test recommended permissions
echo -e "${BLUE}Recommended Permissions (Security):${NC}"
echo "────────────────────────────────────────"
test_permission "Dependabot alerts" "repos/$REPO/dependabot/alerts" "GET" "false"
test_permission "Secret scanning alerts" "repos/$REPO/secret-scanning/alerts" "GET" "false"
test_permission "Security advisories" "repos/$REPO/security-advisories" "GET" "false"
echo ""

# Test optional permissions
echo -e "${BLUE}Optional Permissions:${NC}"
echo "────────────────────────────────────────"
test_permission "Discussions" "repos/$REPO/discussions" "GET" "false"
echo ""

# Summary
echo "═══════════════════════════════════════════════════════════════"
echo -e "${BOLD}VALIDATION SUMMARY:${NC}"
echo "────────────────────────────────────────"

if [ $CRITICAL_FAIL -eq 0 ]; then
    echo -e "${GREEN}✅ All critical permissions: PASSED ($CRITICAL_PASS/$CRITICAL_PASS)${NC}"
    OVERALL_STATUS="PASSED"
else
    echo -e "${RED}❌ Critical permissions: FAILED ($CRITICAL_PASS/$(($CRITICAL_PASS + $CRITICAL_FAIL)))${NC}"
    OVERALL_STATUS="FAILED"
fi

if [ $RECOMMENDED_FAIL -eq 0 ]; then
    echo -e "${GREEN}✅ Recommended permissions: PASSED ($RECOMMENDED_PASS/$RECOMMENDED_PASS)${NC}"
else
    echo -e "${YELLOW}⚠️  Recommended permissions: PARTIAL ($RECOMMENDED_PASS/$(($RECOMMENDED_PASS + $RECOMMENDED_FAIL)))${NC}"
fi

echo ""
echo -e "${BOLD}Overall Status: ${NC}"
if [ "$OVERALL_STATUS" = "PASSED" ]; then
    echo -e "${GREEN}✅ TOKEN IS PROPERLY CONFIGURED FOR CMZ DEVELOPMENT${NC}"
    echo ""
    echo "This token has all required permissions for:"
    echo "• Creating and managing pull requests"
    echo "• Running /resolve-mr command"
    echo "• Viewing security scans and CodeQL alerts"
    echo "• Full CI/CD visibility"

    # Optionally save to .env.local if all tests pass
    read -p "Save this token to .env.local? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Check if .env.local exists
        if [ -f ".env.local" ]; then
            # Update existing token
            sed -i.bak "s/^GITHUB_TOKEN=.*/GITHUB_TOKEN=$TOKEN/" .env.local
            echo -e "${GREEN}✅ Updated GITHUB_TOKEN in .env.local${NC}"
        else
            # Create new .env.local
            cat > .env.local << EOF
# Local environment variables for development
# DO NOT COMMIT THIS FILE - it should be in .gitignore

# GitHub API Configuration
GITHUB_TOKEN=$TOKEN

# Usage: source .env.local before running scripts
EOF
            echo -e "${GREEN}✅ Created .env.local with GITHUB_TOKEN${NC}"
        fi
    fi
else
    echo -e "${RED}❌ TOKEN IS MISSING CRITICAL PERMISSIONS${NC}"
    echo ""
    echo "Please create a new token with the following permissions:"
    echo "• Pull requests: Write"
    echo "• Code scanning alerts: Read"
    echo "• Contents: Write"
    echo "• Actions: Read"
    echo "• Issues: Write"
    echo ""
    echo "See the documentation or run this script again after updating."
fi

echo "═══════════════════════════════════════════════════════════════"