#!/bin/bash
# Script to transition Chat Epic tickets to Resolved status with Done resolution
set -e

echo "========================================="
echo "Resolving Chat Epic Tickets"
echo "========================================="

# Load environment variables
if [ -f .env.local ]; then
    export $(grep -v '^#' .env.local | xargs)
fi

# Validate required environment variables
if [ -z "$JIRA_EMAIL" ] || [ -z "$JIRA_API_TOKEN" ]; then
    echo "❌ Error: JIRA_EMAIL and JIRA_API_TOKEN must be set in .env.local"
    exit 1
fi

# Configuration
JIRA_BASE_URL="https://nortal.atlassian.net"
AUTH=$(echo -n "$JIRA_EMAIL:$JIRA_API_TOKEN" | base64)

# Array of tickets to update (excluding PR003946-156 which is already done)
TICKETS=(
    "PR003946-157"  # Response Streaming
    "PR003946-158"  # DynamoDB Storage
    "PR003946-159"  # Session List Endpoint
    "PR003946-160"  # RBAC for History
)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo "📋 Tickets to resolve:"
for ticket in "${TICKETS[@]}"; do
    echo "  - $ticket"
done
echo ""

# Function to get available transitions for a ticket
get_transitions() {
    local ticket=$1
    echo "🔍 Getting available transitions for $ticket..."

    RESPONSE=$(curl -s -X GET \
        "$JIRA_BASE_URL/rest/api/3/issue/$ticket/transitions" \
        -H "Authorization: Basic $AUTH" \
        -H "Accept: application/json")

    echo "$RESPONSE"
}

# Function to transition and resolve a ticket
resolve_ticket() {
    local ticket=$1

    echo "⚙️  Processing $ticket..."

    # First, get available transitions
    TRANSITIONS=$(get_transitions "$ticket")

    # Try to find the "Resolve" or "Done" transition
    RESOLVE_ID=$(echo "$TRANSITIONS" | jq -r '.transitions[] | select(.name | test("Resolve|Resolved|Done|Close"; "i")) | .id' | head -n1)

    if [ -z "$RESOLVE_ID" ]; then
        # Try "In Progress" first, then "Resolve"
        IN_PROGRESS_ID=$(echo "$TRANSITIONS" | jq -r '.transitions[] | select(.name | test("In Progress|Start Progress"; "i")) | .id' | head -n1)

        if [ -n "$IN_PROGRESS_ID" ]; then
            echo "  Moving to In Progress first (ID: $IN_PROGRESS_ID)..."

            TRANSITION_BODY=$(cat <<EOF
{
    "transition": {
        "id": "$IN_PROGRESS_ID"
    }
}
EOF
)
            curl -s -X POST \
                "$JIRA_BASE_URL/rest/api/3/issue/$ticket/transitions" \
                -H "Authorization: Basic $AUTH" \
                -H "Accept: application/json" \
                -H "Content-Type: application/json" \
                -d "$TRANSITION_BODY" > /dev/null

            sleep 1

            # Get transitions again
            TRANSITIONS=$(get_transitions "$ticket")
            RESOLVE_ID=$(echo "$TRANSITIONS" | jq -r '.transitions[] | select(.name | test("Resolve|Resolved|Done"; "i")) | .id' | head -n1)
        fi
    fi

    if [ -z "$RESOLVE_ID" ]; then
        echo -e "${YELLOW}⚠️  Could not find Resolve transition for $ticket${NC}"
        echo "Available transitions:"
        echo "$TRANSITIONS" | jq -r '.transitions[] | "  ID \(.id): \(.name)"'
        return 1
    fi

    # Transition to Resolved with resolution
    echo "  Resolving ticket (Transition ID: $RESOLVE_ID)..."

    TRANSITION_BODY=$(cat <<EOF
{
    "transition": {
        "id": "$RESOLVE_ID"
    },
    "fields": {
        "resolution": {
            "name": "Done"
        },
        "assignee": {
            "accountId": "5f34582173a268004d409ef7"
        }
    }
}
EOF
)

    RESPONSE=$(curl -s -X POST \
        "$JIRA_BASE_URL/rest/api/3/issue/$ticket/transitions" \
        -H "Authorization: Basic $AUTH" \
        -H "Accept: application/json" \
        -H "Content-Type: application/json" \
        -d "$TRANSITION_BODY" \
        -w "\n%{http_code}")

    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | sed '$d')

    if [ "$HTTP_CODE" = "204" ]; then
        echo -e "${GREEN}✅ Successfully resolved $ticket${NC}"
        return 0
    else
        echo -e "${RED}❌ Failed to resolve $ticket${NC}"
        echo "Response: $BODY"
        return 1
    fi
}

# Main execution
SUCCESS_COUNT=0
FAILED_COUNT=0

for ticket in "${TICKETS[@]}"; do
    echo "========================================="
    echo "Processing $ticket"
    echo "========================================="

    if resolve_ticket "$ticket"; then
        ((SUCCESS_COUNT++))
    else
        ((FAILED_COUNT++))
        echo -e "${YELLOW}⚠️  Continuing with next ticket...${NC}"
    fi

    echo ""
    sleep 1  # Be nice to the API
done

# Summary
echo "========================================="
echo "Summary"
echo "========================================="
echo -e "${GREEN}✅ Successfully resolved: $SUCCESS_COUNT tickets${NC}"
if [ $FAILED_COUNT -gt 0 ]; then
    echo -e "${RED}❌ Failed to resolve: $FAILED_COUNT tickets${NC}"
fi

# List final status
echo ""
echo "Final ticket status:"
echo "  - PR003946-156: https://nortal.atlassian.net/browse/PR003946-156 (Already Resolved)"
for ticket in "${TICKETS[@]}"; do
    echo "  - $ticket: https://nortal.atlassian.net/browse/$ticket"
done

echo ""
echo "✨ Script completed!"