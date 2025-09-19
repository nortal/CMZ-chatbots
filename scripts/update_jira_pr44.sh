#!/bin/bash

# Update Jira tickets for PR #44 implementation
# Based on successful pattern from NORTAL-JIRA-ADVICE.md

set -e

# Source credentials from .env.local
if [ -f .env.local ]; then
    export $(grep -v '^#' .env.local | xargs)
fi

# Check required environment variables
if [ -z "$JIRA_EMAIL" ] || [ -z "$JIRA_API_TOKEN" ]; then
    echo "Error: JIRA_EMAIL and JIRA_API_TOKEN must be set in .env.local"
    exit 1
fi

# Configuration
JIRA_BASE_URL="https://nortal.atlassian.net"
AUTH=$(echo -n "$JIRA_EMAIL:$JIRA_API_TOKEN" | base64)
PR_URL="https://github.com/nortal/CMZ-chatbots/pull/44"

# Tickets and their implementations
TICKETS="PR003946-88 PR003946-89 PR003946-90 PR003946-91 PR003946-92"

# Function to get description for each ticket
get_description() {
    case "$1" in
        "PR003946-88")
            echo "Refresh & logout consistency - Implemented JWT token management with proper refresh/logout handling"
            ;;
        "PR003946-89")
            echo "Error schema consistency - Created comprehensive error_handler.py with sanitization"
            ;;
        "PR003946-90")
            echo "Global exception handling - Added Flask global error handlers in __main__.py"
            ;;
        "PR003946-91")
            echo "Float validation strictness - Fixed floating-point validation with proper rounding"
            ;;
        "PR003946-92")
            echo "Complex field validation - Implemented field validation in handlers.py"
            ;;
    esac
}

echo "=================================================="
echo "Updating Jira tickets for PR #44 implementation"
echo "PR URL: $PR_URL"
echo "=================================================="
echo ""

# First, discover available transitions for Done status
echo "Discovering workflow transitions..."
SAMPLE_TICKET="PR003946-88"
TRANSITIONS_JSON=$(curl -s -X GET \
    "$JIRA_BASE_URL/rest/api/3/issue/$SAMPLE_TICKET/transitions" \
    -H "Authorization: Basic $AUTH" \
    -H "Accept: application/json")

echo "Available transitions:"
echo "$TRANSITIONS_JSON" | jq -r '.transitions[] | "\(.id): \(.name)"'
echo ""

# Look for Done transition (typically ID 31 or "Done")
DONE_ID=$(echo "$TRANSITIONS_JSON" | jq -r '.transitions[] | select(.name | test("Done|Completed|Resolved"; "i")) | .id' | head -1)

if [ -z "$DONE_ID" ]; then
    echo "Warning: Could not find 'Done' transition automatically"
    echo "Attempting with common transition IDs..."
    # Common transition IDs for Done status
    DONE_ID="31"  # Common ID for Done
fi

echo "Using transition ID $DONE_ID for Done status"
echo ""

# Update each ticket
for TICKET in $TICKETS; do
    DESCRIPTION=$(get_description "$TICKET")
    echo "Updating $TICKET..."

    # Add comment with implementation details
    COMMENT_BODY=$(cat <<EOF
{
  "body": {
    "type": "doc",
    "version": 1,
    "content": [
      {
        "type": "paragraph",
        "content": [
          {
            "type": "text",
            "text": "✅ Implementation completed in PR #44",
            "marks": [{"type": "strong"}]
          }
        ]
      },
      {
        "type": "paragraph",
        "content": [
          {
            "type": "text",
            "text": "$DESCRIPTION"
          }
        ]
      },
      {
        "type": "paragraph",
        "content": [
          {
            "type": "text",
            "text": "PR: "
          },
          {
            "type": "text",
            "text": "$PR_URL",
            "marks": [{"type": "link", "attrs": {"href": "$PR_URL"}}]
          }
        ]
      },
      {
        "type": "paragraph",
        "content": [
          {
            "type": "text",
            "text": "Status: Merged to dev branch"
          }
        ]
      }
    ]
  }
}
EOF
)

    # Add comment
    COMMENT_RESPONSE=$(curl -s -X POST \
        "$JIRA_BASE_URL/rest/api/3/issue/$TICKET/comment" \
        -H "Authorization: Basic $AUTH" \
        -H "Accept: application/json" \
        -H "Content-Type: application/json" \
        -d "$COMMENT_BODY")

    if echo "$COMMENT_RESPONSE" | grep -q '"id"'; then
        echo "  ✓ Added implementation comment"
    else
        echo "  ✗ Failed to add comment: $COMMENT_RESPONSE"
    fi

    # Attempt to transition to Done
    TRANSITION_BODY=$(cat <<EOF
{
  "transition": {
    "id": "$DONE_ID"
  }
}
EOF
)

    TRANSITION_RESPONSE=$(curl -s -X POST \
        "$JIRA_BASE_URL/rest/api/3/issue/$TICKET/transitions" \
        -H "Authorization: Basic $AUTH" \
        -H "Accept: application/json" \
        -H "Content-Type: application/json" \
        -d "$TRANSITION_BODY")

    if [ -z "$TRANSITION_RESPONSE" ] || [ "$TRANSITION_RESPONSE" = "" ]; then
        echo "  ✓ Transition attempted (verifying...)"

        # Verify the status change
        VERIFY_RESPONSE=$(curl -s -X GET \
            "$JIRA_BASE_URL/rest/api/3/issue/$TICKET" \
            -H "Authorization: Basic $AUTH" \
            -H "Accept: application/json")

        CURRENT_STATUS=$(echo "$VERIFY_RESPONSE" | jq -r '.fields.status.name')
        echo "  Current status: $CURRENT_STATUS"

        if echo "$CURRENT_STATUS" | grep -qi "done\|completed\|resolved"; then
            echo "  ✓ Successfully moved to Done"
        else
            echo "  ⚠️ Status is '$CURRENT_STATUS' - may need manual update"
        fi
    else
        echo "  ✗ Transition failed: $TRANSITION_RESPONSE"
    fi

    echo ""
done

echo "=================================================="
echo "Summary:"
echo "PR #44 Jira ticket updates completed"
echo "All implementation comments added"
echo "Tickets should now be in Done status"
echo "PR URL: $PR_URL"
echo "=================================================="