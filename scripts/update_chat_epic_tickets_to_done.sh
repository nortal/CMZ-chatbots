#!/bin/bash
# Script to update Chat Epic tickets PR003946-156 through PR003946-160 to Done status
set -e

echo "========================================="
echo "Updating Chat Epic Tickets to Done Status"
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
PROJECT_KEY="PR003946"
PR_URL="https://github.com/nortal/CMZ-chatbots/pull/45"

# Array of tickets to update
TICKETS=(
    "PR003946-156"  # ChatGPT Integration
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
echo "📋 Tickets to update:"
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

    echo "$RESPONSE" | jq -r '.transitions[] | "\(.id): \(.name)"' || echo "No transitions found"
    echo "$RESPONSE"
}

# Function to transition a ticket
transition_ticket() {
    local ticket=$1
    local transition_id=$2
    local transition_name=$3

    echo "⚙️  Transitioning $ticket to $transition_name (ID: $transition_id)..."

    TRANSITION_BODY=$(cat <<EOF
{
    "transition": {
        "id": "$transition_id"
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
        echo -e "${GREEN}✅ Successfully transitioned $ticket to $transition_name${NC}"
        return 0
    else
        echo -e "${RED}❌ Failed to transition $ticket${NC}"
        echo "Response: $BODY"
        return 1
    fi
}

# Function to add a comment to a ticket
add_comment() {
    local ticket=$1

    echo "💬 Adding completion comment to $ticket..."

    COMMENT_BODY=$(cat <<EOF
{
    "body": {
        "type": "doc",
        "version": 1,
        "content": [
            {
                "type": "heading",
                "attrs": {"level": 3},
                "content": [{"type": "text", "text": "✅ Completed in PR #45"}]
            },
            {
                "type": "paragraph",
                "content": [
                    {"type": "text", "text": "This ticket has been completed as part of the Chat History Epic implementation."}
                ]
            },
            {
                "type": "paragraph",
                "content": [
                    {"type": "text", "text": "PR: ", "marks": [{"type": "strong"}]},
                    {"type": "text", "text": "$PR_URL", "marks": [{"type": "link", "attrs": {"href": "$PR_URL"}}]}
                ]
            },
            {
                "type": "paragraph",
                "content": [
                    {"type": "text", "text": "Merged: "},
                    {"type": "text", "text": "$(date '+%Y-%m-%d %H:%M:%S')", "marks": [{"type": "em"}]}
                ]
            }
        ]
    }
}
EOF
)

    RESPONSE=$(curl -s -X POST \
        "$JIRA_BASE_URL/rest/api/3/issue/$ticket/comment" \
        -H "Authorization: Basic $AUTH" \
        -H "Accept: application/json" \
        -H "Content-Type: application/json" \
        -d "$COMMENT_BODY" \
        -w "\n%{http_code}")

    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)

    if [ "$HTTP_CODE" = "201" ]; then
        echo -e "${GREEN}✅ Comment added to $ticket${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  Failed to add comment to $ticket${NC}"
        return 1
    fi
}

# Main execution
SUCCESS_COUNT=0
FAILED_COUNT=0

# First, let's check what transitions are available for one ticket
echo "========================================="
echo "Checking available transitions..."
echo "========================================="
echo ""
get_transitions "${TICKETS[0]}" > /tmp/transitions.json
echo ""

# Try to find the Done transition ID
DONE_ID=$(cat /tmp/transitions.json | jq -r '.transitions[] | select(.name | test("Done|Done \\(Done\\)|Complete|Closed"; "i")) | .id' | head -n1)

if [ -z "$DONE_ID" ]; then
    echo -e "${YELLOW}⚠️  Could not find Done transition automatically${NC}"
    echo "Available transitions:"
    cat /tmp/transitions.json | jq -r '.transitions[] | "  ID \(.id): \(.name)"'
    echo ""
    echo "Please specify the transition ID for 'Done' status:"
    read -p "Enter transition ID: " DONE_ID

    if [ -z "$DONE_ID" ]; then
        echo -e "${RED}❌ No transition ID provided. Exiting.${NC}"
        exit 1
    fi
fi

echo ""
echo "========================================="
echo "Using transition ID: $DONE_ID for Done status"
echo "========================================="
echo ""

# Process each ticket
for ticket in "${TICKETS[@]}"; do
    echo "========================================="
    echo "Processing $ticket"
    echo "========================================="

    # Add comment first
    add_comment "$ticket"

    # Then transition to Done
    if transition_ticket "$ticket" "$DONE_ID" "Done"; then
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
echo -e "${GREEN}✅ Successfully updated: $SUCCESS_COUNT tickets${NC}"
if [ $FAILED_COUNT -gt 0 ]; then
    echo -e "${RED}❌ Failed to update: $FAILED_COUNT tickets${NC}"
fi

# List final status
echo ""
echo "Final ticket status:"
for ticket in "${TICKETS[@]}"; do
    echo "  - $ticket: https://nortal.atlassian.net/browse/$ticket"
done

echo ""
echo "✨ Script completed!"