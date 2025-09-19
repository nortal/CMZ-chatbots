#!/bin/bash

# Script to create Chat and Chat History Epic tickets in Jira
# Based on existing successful ticket creation scripts

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
PROJECT_KEY="PR003946"
EPIC_KEY="PR003946-61"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "=================================================="
echo "Creating Chat and Chat History Epic tickets"
echo "=================================================="
echo ""

# Keep track of created tickets
> created_tickets.txt

# Ticket 1: ChatGPT Integration
echo "Creating ticket 1: ChatGPT Integration with Animal Personalities..."

TICKET1_BODY=$(cat <<'EOF'
{
  "fields": {
    "project": {
      "key": "PR003946"
    },
    "summary": "[Backend] Implement ChatGPT Integration with Animal Personalities",
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
              "text": "Integrate the /convo_turn endpoint with ChatGPT API to enable real conversations with animal personalities. Each animal will have a unique ChatGPT endpoint URL and system prompt configuration."
            }
          ]
        },
        {
          "type": "heading",
          "attrs": {"level": 2},
          "content": [{"type": "text", "text": "Technical Requirements"}]
        },
        {
          "type": "bulletList",
          "content": [
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Modify handle_convo_turn_post in conversation.py"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Load animal personality configuration from DynamoDB"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Construct system prompt with animal personality traits"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Call ChatGPT API with animal-specific endpoint URL"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Handle API errors and rate limiting"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Support conversation context (last 10 messages)"}]}]}
          ]
        },
        {
          "type": "heading",
          "attrs": {"level": 2},
          "content": [{"type": "text", "text": "Acceptance Criteria"}]
        },
        {
          "type": "orderedList",
          "content": [
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Message with animalId calls ChatGPT API with correct animal personality"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Animal custom endpoint URL is used when configured"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Last 10 messages included as conversation context"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Graceful fallback message on ChatGPT API failure"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Rate limit handling with retry-after header"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Default friendly response when animal has no chat config"}]}]}
          ]
        },
        {
          "type": "heading",
          "attrs": {"level": 2},
          "content": [{"type": "text", "text": "Story Points"}]
        },
        {
          "type": "paragraph",
          "content": [
            {
              "type": "text",
              "text": "8 story points - Complex integration with external API, error handling, and configuration management"
            }
          ]
        }
      ]
    },
    "issuetype": {
      "name": "Task"
    },
    "priority": {
      "name": "Highest"
    },
    "labels": ["backend", "chatgpt", "api", "integration", "chat-history"],
    "customfield_10225": {
      "value": "Billable"
    },
    "customfield_10014": "PR003946-61"
  }
}
EOF
)

RESPONSE1=$(curl -s -X POST \
    "$JIRA_BASE_URL/rest/api/3/issue" \
    -H "Authorization: Basic $AUTH" \
    -H "Accept: application/json" \
    -H "Content-Type: application/json" \
    -d "$TICKET1_BODY")

if echo "$RESPONSE1" | grep -q '"key"'; then
    TICKET1_KEY=$(echo "$RESPONSE1" | jq -r '.key')
    echo -e "${GREEN}✓ Created ticket: $TICKET1_KEY${NC}"
    echo "$TICKET1_KEY" >> created_tickets.txt
else
    echo -e "${RED}✗ Failed to create ticket 1${NC}"
    echo "Response: $RESPONSE1"
fi

echo ""

# Ticket 2: Response Streaming with SSE
echo "Creating ticket 2: Response Streaming with Server-Sent Events..."

TICKET2_BODY=$(cat <<'EOF'
{
  "fields": {
    "project": {
      "key": "PR003946"
    },
    "summary": "[Backend] Implement Response Streaming with Server-Sent Events",
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
              "text": "Implement real-time response streaming using Server-Sent Events (SSE) to display ChatGPT responses as they are generated, providing a more engaging user experience."
            }
          ]
        },
        {
          "type": "heading",
          "attrs": {"level": 2},
          "content": [{"type": "text", "text": "Technical Requirements"}]
        },
        {
          "type": "bulletList",
          "content": [
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Create new endpoint POST /convo_turn/stream"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Implement SSE response format"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Stream ChatGPT API responses token by token"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Handle connection drops and reconnection"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Buffer management for partial tokens"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Cleanup on client disconnect"}]}]}
          ]
        },
        {
          "type": "heading",
          "attrs": {"level": 2},
          "content": [{"type": "text", "text": "Acceptance Criteria"}]
        },
        {
          "type": "orderedList",
          "content": [
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Streaming endpoint returns tokens in real-time"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Client can reconnect and continue on connection drop"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Server cleanup occurs on client disconnect"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Partial tokens buffered until complete words"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Complete event fires when streaming finishes"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Error event sent on streaming failure"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Multiple concurrent streams work independently"}]}]}
          ]
        },
        {
          "type": "heading",
          "attrs": {"level": 2},
          "content": [{"type": "text", "text": "Story Points"}]
        },
        {
          "type": "paragraph",
          "content": [
            {
              "type": "text",
              "text": "13 story points - Complex real-time streaming implementation with connection management"
            }
          ]
        }
      ]
    },
    "issuetype": {
      "name": "Task"
    },
    "priority": {
      "name": "Highest"
    },
    "labels": ["backend", "streaming", "sse", "realtime", "chat-history"],
    "customfield_10225": {
      "value": "Billable"
    },
    "customfield_10014": "PR003946-61"
  }
}
EOF
)

RESPONSE2=$(curl -s -X POST \
    "$JIRA_BASE_URL/rest/api/3/issue" \
    -H "Authorization: Basic $AUTH" \
    -H "Accept: application/json" \
    -H "Content-Type: application/json" \
    -d "$TICKET2_BODY")

if echo "$RESPONSE2" | grep -q '"key"'; then
    TICKET2_KEY=$(echo "$RESPONSE2" | jq -r '.key')
    echo -e "${GREEN}✓ Created ticket: $TICKET2_KEY${NC}"
    echo "$TICKET2_KEY" >> created_tickets.txt
else
    echo -e "${RED}✗ Failed to create ticket 2${NC}"
    echo "Response: $RESPONSE2"
fi

echo ""

# Ticket 3: DynamoDB Conversation Storage
echo "Creating ticket 3: DynamoDB Conversation Storage..."

TICKET3_BODY=$(cat <<'EOF'
{
  "fields": {
    "project": {
      "key": "PR003946"
    },
    "summary": "[Backend] Implement DynamoDB Conversation Storage",
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
              "text": "Design and implement DynamoDB schema for storing conversation history with efficient querying for session management and history retrieval."
            }
          ]
        },
        {
          "type": "heading",
          "attrs": {"level": 2},
          "content": [{"type": "text", "text": "DynamoDB Schema"}]
        },
        {
          "type": "paragraph",
          "content": [
            {
              "type": "text",
              "text": "Table: cmz-conversations | PK: userId | SK: sessionId#timestamp | GSI1: sessionId/timestamp | GSI2: animalId/timestamp | GSI3: parentUserId/timestamp"
            }
          ]
        },
        {
          "type": "heading",
          "attrs": {"level": 2},
          "content": [{"type": "text", "text": "Technical Requirements"}]
        },
        {
          "type": "bulletList",
          "content": [
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Design efficient DynamoDB schema with indexes"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Implement batch write for efficiency (25 items max)"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Configure TTL for old conversations (90 days)"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Enable encryption at rest"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Configure point-in-time recovery"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Setup auto-scaling configuration"}]}]}
          ]
        },
        {
          "type": "heading",
          "attrs": {"level": 2},
          "content": [{"type": "text", "text": "Acceptance Criteria"}]
        },
        {
          "type": "orderedList",
          "content": [
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Conversations saved with both user and assistant messages"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Query by sessionId returns all messages in order"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Query by userId returns all user sessions"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Query by parentUserId returns children conversations"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "TTL deletes conversations older than 90 days"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Batch writes with exponential backoff on failure"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Auto-scaling handles high load"}]}]}
          ]
        },
        {
          "type": "heading",
          "attrs": {"level": 2},
          "content": [{"type": "text", "text": "Story Points"}]
        },
        {
          "type": "paragraph",
          "content": [
            {
              "type": "text",
              "text": "8 story points - Database schema design and implementation with multiple access patterns"
            }
          ]
        }
      ]
    },
    "issuetype": {
      "name": "Task"
    },
    "priority": {
      "name": "Highest"
    },
    "labels": ["backend", "dynamodb", "storage", "database", "chat-history"],
    "customfield_10225": {
      "value": "Billable"
    },
    "customfield_10014": "PR003946-61"
  }
}
EOF
)

RESPONSE3=$(curl -s -X POST \
    "$JIRA_BASE_URL/rest/api/3/issue" \
    -H "Authorization: Basic $AUTH" \
    -H "Accept: application/json" \
    -H "Content-Type: application/json" \
    -d "$TICKET3_BODY")

if echo "$RESPONSE3" | grep -q '"key"'; then
    TICKET3_KEY=$(echo "$RESPONSE3" | jq -r '.key')
    echo -e "${GREEN}✓ Created ticket: $TICKET3_KEY${NC}"
    echo "$TICKET3_KEY" >> created_tickets.txt
else
    echo -e "${RED}✗ Failed to create ticket 3${NC}"
    echo "Response: $RESPONSE3"
fi

echo ""
echo "=================================================="
echo "Summary"
echo "=================================================="
echo ""

if [ -s created_tickets.txt ]; then
    echo -e "${GREEN}Successfully created the following tickets:${NC}"
    cat created_tickets.txt
    echo ""
    echo "Total tickets created: $(wc -l < created_tickets.txt)"
else
    echo -e "${RED}No tickets were created successfully${NC}"
fi

echo ""
echo "Note: This script created the first 3 critical backend tickets."
echo "Run additional scripts to create the remaining 11 tickets for the full epic."
echo "Total epic scope: 14 tickets, 89 story points, 3-4 sprints"