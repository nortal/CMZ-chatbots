#!/bin/bash

# Script to update Chat Epic tickets with CHAT-ADVICE.md requirements
# Updates tickets PR003946-156 through PR003946-169

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
NEW_EPIC_KEY="PR003946-170"  # Will create this new epic first

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "=================================================="
echo "Creating new Enable Chat Epic"
echo "=================================================="
echo ""

# Create new Enable Chat Epic
EPIC_BODY=$(cat <<'EOF'
{
  "fields": {
    "project": {
      "key": "PR003946"
    },
    "summary": "[EPIC] Enable Chat - ChatGPT Integration with Real-time Streaming",
    "description": {
      "type": "doc",
      "version": 1,
      "content": [
        {
          "type": "heading",
          "attrs": {"level": 2},
          "content": [{"type": "text", "text": "Overview"}]
        },
        {
          "type": "paragraph",
          "content": [
            {
              "type": "text",
              "text": "Epic for implementing comprehensive chat system with ChatGPT integration, real-time streaming via SSE, DynamoDB storage, and role-based history access. All implementation teams should collaborate through CHAT-ADVICE.md for shared learnings."
            }
          ]
        },
        {
          "type": "heading",
          "attrs": {"level": 2},
          "content": [{"type": "text", "text": "Scope"}]
        },
        {
          "type": "bulletList",
          "content": [
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "ChatGPT API integration with animal personalities"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Server-Sent Events for real-time response streaming"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "DynamoDB conversation storage and retrieval"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Role-based access control for history viewing"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Frontend UI with 21st.dev components"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Security, privacy, and compliance controls"}]}]}
          ]
        },
        {
          "type": "heading",
          "attrs": {"level": 2},
          "content": [{"type": "text", "text": "Total Scope"}]
        },
        {
          "type": "paragraph",
          "content": [
            {
              "type": "text",
              "text": "14 tickets, 89 story points, estimated 3-4 sprints"
            }
          ]
        },
        {
          "type": "heading",
          "attrs": {"level": 2},
          "content": [{"type": "text", "text": "Collaboration"}]
        },
        {
          "type": "paragraph",
          "content": [
            {
              "type": "text",
              "text": "All teams must read CHAT-ADVICE.md at the start of their work and update it with learnings for other teams."
            }
          ]
        }
      ]
    },
    "issuetype": {
      "name": "Epic"
    },
    "priority": {
      "name": "Highest"
    },
    "labels": ["chat", "epic", "chatgpt", "streaming", "history", "enable-chat"],
    "customfield_10225": {
      "value": "Billable"
    },
    "customfield_10011": "Enable Chat Epic"
  }
}
EOF
)

echo "Creating new Enable Chat Epic..."
EPIC_RESPONSE=$(curl -s -X POST \
    "$JIRA_BASE_URL/rest/api/3/issue" \
    -H "Authorization: Basic $AUTH" \
    -H "Accept: application/json" \
    -H "Content-Type: application/json" \
    -d "$EPIC_BODY")

if echo "$EPIC_RESPONSE" | grep -q '"key"'; then
    NEW_EPIC_KEY=$(echo "$EPIC_RESPONSE" | jq -r '.key')
    echo -e "${GREEN}✓ Created new Epic: $NEW_EPIC_KEY${NC}"
else
    echo -e "${RED}✗ Failed to create new Epic${NC}"
    echo "Response: $EPIC_RESPONSE"
    echo "Attempting to use PR003946-170 as epic key..."
    NEW_EPIC_KEY="PR003946-170"
fi

echo ""
echo "=================================================="
echo "Updating Chat Tickets with CHAT-ADVICE.md Requirements"
echo "=================================================="
echo ""

# Function to update a ticket
update_ticket() {
    local ticket_key="$1"

    echo -e "${YELLOW}Updating ticket: $ticket_key${NC}"

    # First, get the current ticket to preserve existing content
    CURRENT_TICKET=$(curl -s -X GET \
        "$JIRA_BASE_URL/rest/api/3/issue/$ticket_key" \
        -H "Authorization: Basic $AUTH" \
        -H "Accept: application/json")

    if ! echo "$CURRENT_TICKET" | grep -q '"key"'; then
        echo -e "${RED}✗ Failed to get ticket $ticket_key${NC}"
        return 1
    fi

    # Get current description content
    CURRENT_DESC=$(echo "$CURRENT_TICKET" | jq '.fields.description.content')

    # Add CHAT-ADVICE.md requirement to the beginning of description
    UPDATED_DESC=$(echo "$CURRENT_DESC" | jq '. = [
        {
          "type": "paragraph",
          "content": [
            {
              "type": "text",
              "text": "📚 IMPORTANT: Start by reading CHAT-ADVICE.md for context and previous learnings from other chat implementation tickets.",
              "marks": [{"type": "strong"}]
            }
          ]
        },
        {
          "type": "paragraph",
          "content": [{"type": "text", "text": " "}]
        }
    ] + .')

    # Check if there's an Acceptance Criteria section and update it
    if echo "$CURRENT_DESC" | jq -e '.[] | select(.type == "heading") | .content[] | select(.text == "Acceptance Criteria")' > /dev/null; then
        # Add new acceptance criteria item
        UPDATED_DESC=$(echo "$UPDATED_DESC" | jq '
            . as $content |
            ($content | map(.type == "heading" and (.content[]?.text == "Acceptance Criteria")) | index(true)) as $ac_index |
            if $ac_index then
                # Find the next orderedList or bulletList after AC heading
                (($ac_index + 1) + ([$content[($ac_index + 1):][]] | map(.type == "orderedList" or .type == "bulletList") | index(true))) as $list_index |
                if $list_index and ($content[$list_index].type == "orderedList" or $content[$list_index].type == "bulletList") then
                    $content[:$list_index] +
                    [$content[$list_index] | .content += [
                        {
                            "type": "listItem",
                            "content": [
                                {
                                    "type": "paragraph",
                                    "content": [
                                        {
                                            "type": "text",
                                            "text": "Update CHAT-ADVICE.md with implementation learnings, patterns discovered, and notes for other tickets"
                                        }
                                    ]
                                }
                            ]
                        }
                    ]] +
                    $content[($list_index + 1):]
                else
                    $content
                end
            else
                $content + [
                    {
                        "type": "heading",
                        "attrs": {"level": 2},
                        "content": [{"type": "text", "text": "Additional Acceptance Criteria"}]
                    },
                    {
                        "type": "bulletList",
                        "content": [
                            {
                                "type": "listItem",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [
                                            {
                                                "type": "text",
                                                "text": "Update CHAT-ADVICE.md with implementation learnings, patterns discovered, and notes for other tickets"
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            end
        ')
    else
        # Add new AC section if it doesn't exist
        UPDATED_DESC=$(echo "$UPDATED_DESC" | jq '. += [
            {
                "type": "heading",
                "attrs": {"level": 2},
                "content": [{"type": "text", "text": "Additional Acceptance Criteria"}]
            },
            {
                "type": "bulletList",
                "content": [
                    {
                        "type": "listItem",
                        "content": [
                            {
                                "type": "paragraph",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": "Update CHAT-ADVICE.md with implementation learnings, patterns discovered, and notes for other tickets"
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]')
    fi

    # Create update payload
    UPDATE_BODY=$(cat <<EOF
{
    "fields": {
        "description": {
            "type": "doc",
            "version": 1,
            "content": $UPDATED_DESC
        },
        "customfield_10014": "$NEW_EPIC_KEY"
    }
}
EOF
    )

    # Update the ticket
    UPDATE_RESPONSE=$(curl -s -X PUT \
        "$JIRA_BASE_URL/rest/api/3/issue/$ticket_key" \
        -H "Authorization: Basic $AUTH" \
        -H "Accept: application/json" \
        -H "Content-Type: application/json" \
        -d "$UPDATE_BODY")

    # Check if update was successful (204 No Content is success for PUT)
    if [ -z "$UPDATE_RESPONSE" ] || ! echo "$UPDATE_RESPONSE" | grep -q "error"; then
        echo -e "${GREEN}✓ Updated ticket: $ticket_key${NC}"
        return 0
    else
        echo -e "${RED}✗ Failed to update ticket: $ticket_key${NC}"
        echo "Response: $UPDATE_RESPONSE"
        return 1
    fi
}

# Update all tickets from PR003946-156 to PR003946-169
echo "Updating tickets PR003946-156 through PR003946-169..."
echo ""

SUCCESS_COUNT=0
FAIL_COUNT=0

for i in {156..169}; do
    TICKET_KEY="PR003946-$i"
    if update_ticket "$TICKET_KEY"; then
        ((SUCCESS_COUNT++))
    else
        ((FAIL_COUNT++))
    fi
    echo ""
    sleep 1  # Rate limiting
done

echo "=================================================="
echo "Summary"
echo "=================================================="
echo ""
echo -e "${GREEN}Successfully updated: $SUCCESS_COUNT tickets${NC}"
if [ $FAIL_COUNT -gt 0 ]; then
    echo -e "${RED}Failed to update: $FAIL_COUNT tickets${NC}"
fi
echo ""
echo "New Epic: $NEW_EPIC_KEY"
echo "All tickets now include:"
echo "  - Requirement to read CHAT-ADVICE.md at start"
echo "  - Acceptance criteria to update CHAT-ADVICE.md with learnings"
echo "  - Association with new Enable Chat Epic"