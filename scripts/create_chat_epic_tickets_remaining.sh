#!/bin/bash

# Script to create the remaining 11 Chat and Chat History Epic tickets in Jira
# Continues from tickets 156-158 already created

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
echo "Creating remaining Chat and Chat History Epic tickets"
echo "=================================================="
echo ""

# Keep track of created tickets
> created_tickets_remaining.txt

# Ticket 4: Session List Endpoint
echo "Creating ticket 4: Conversation Session List Endpoint..."

TICKET4_BODY=$(cat <<'EOF'
{
  "fields": {
    "project": {
      "key": "PR003946"
    },
    "summary": "[Backend] Create Conversation Session List Endpoint",
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
              "text": "Create GET /conversations/sessions endpoint to retrieve a paginated list of conversation sessions for users to browse their chat history."
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
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Query by userId with pagination"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Include session metadata (animal, message count, last activity)"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Support date range filtering"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Sort by most recent first"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Implement caching for performance"}]}]}
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
              "text": "5 story points"
            }
          ]
        }
      ]
    },
    "issuetype": {
      "name": "Task"
    },
    "priority": {
      "name": "High"
    },
    "labels": ["backend", "api", "sessions", "history", "chat-history"],
    "customfield_10225": {
      "value": "Billable"
    },
    "customfield_10014": "PR003946-61"
  }
}
EOF
)

RESPONSE4=$(curl -s -X POST \
    "$JIRA_BASE_URL/rest/api/3/issue" \
    -H "Authorization: Basic $AUTH" \
    -H "Accept: application/json" \
    -H "Content-Type: application/json" \
    -d "$TICKET4_BODY")

if echo "$RESPONSE4" | grep -q '"key"'; then
    TICKET4_KEY=$(echo "$RESPONSE4" | jq -r '.key')
    echo -e "${GREEN}✓ Created ticket: $TICKET4_KEY${NC}"
    echo "$TICKET4_KEY" >> created_tickets_remaining.txt
else
    echo -e "${RED}✗ Failed to create ticket 4${NC}"
    echo "Response: $RESPONSE4"
fi

echo ""

# Ticket 5: RBAC for History
echo "Creating ticket 5: Role-Based Access Control for History..."

TICKET5_BODY=$(cat <<'EOF'
{
  "fields": {
    "project": {
      "key": "PR003946"
    },
    "summary": "[Backend] Implement Role-Based Access Control for History",
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
              "text": "Implement comprehensive role-based access control to ensure users can only view appropriate conversation histories based on their role and relationships."
            }
          ]
        },
        {
          "type": "heading",
          "attrs": {"level": 2},
          "content": [{"type": "text", "text": "Access Rules"}]
        },
        {
          "type": "bulletList",
          "content": [
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Visitor: No access to any conversation history"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "User: View own conversations only"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Parent: View own and children's conversations"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Zookeeper: View all conversations (read-only)"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Administrator: Full access to all conversations"}]}]}
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
              "text": "8 story points"
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
    "labels": ["backend", "security", "rbac", "permissions", "chat-history"],
    "customfield_10225": {
      "value": "Billable"
    },
    "customfield_10014": "PR003946-61"
  }
}
EOF
)

RESPONSE5=$(curl -s -X POST \
    "$JIRA_BASE_URL/rest/api/3/issue" \
    -H "Authorization: Basic $AUTH" \
    -H "Accept: application/json" \
    -H "Content-Type: application/json" \
    -d "$TICKET5_BODY")

if echo "$RESPONSE5" | grep -q '"key"'; then
    TICKET5_KEY=$(echo "$RESPONSE5" | jq -r '.key')
    echo -e "${GREEN}✓ Created ticket: $TICKET5_KEY${NC}"
    echo "$TICKET5_KEY" >> created_tickets_remaining.txt
else
    echo -e "${RED}✗ Failed to create ticket 5${NC}"
    echo "Response: $RESPONSE5"
fi

echo ""

# Ticket 6: History Retrieval Endpoint
echo "Creating ticket 6: Conversation History Retrieval Endpoint..."

TICKET6_BODY=$(cat <<'EOF'
{
  "fields": {
    "project": {
      "key": "PR003946"
    },
    "summary": "[Backend] Implement Conversation History Retrieval Endpoint",
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
              "text": "Create GET /conversations/history/{sessionId} endpoint to retrieve complete conversation history for a specific session with proper access controls."
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
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Get session metadata and validate access permissions"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Query all messages in session from DynamoDB"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Calculate conversation statistics"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Include animal information"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Support pagination for long conversations"}]}]}
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
              "text": "5 story points"
            }
          ]
        }
      ]
    },
    "issuetype": {
      "name": "Task"
    },
    "priority": {
      "name": "High"
    },
    "labels": ["backend", "api", "history", "retrieval", "chat-history"],
    "customfield_10225": {
      "value": "Billable"
    },
    "customfield_10014": "PR003946-61"
  }
}
EOF
)

RESPONSE6=$(curl -s -X POST \
    "$JIRA_BASE_URL/rest/api/3/issue" \
    -H "Authorization: Basic $AUTH" \
    -H "Accept: application/json" \
    -H "Content-Type: application/json" \
    -d "$TICKET6_BODY")

if echo "$RESPONSE6" | grep -q '"key"'; then
    TICKET6_KEY=$(echo "$RESPONSE6" | jq -r '.key')
    echo -e "${GREEN}✓ Created ticket: $TICKET6_KEY${NC}"
    echo "$TICKET6_KEY" >> created_tickets_remaining.txt
else
    echo -e "${RED}✗ Failed to create ticket 6${NC}"
    echo "Response: $RESPONSE6"
fi

echo ""

# Ticket 7: Frontend Chat History List Page
echo "Creating ticket 7: Chat History List Page with 21st.dev..."

TICKET7_BODY=$(cat <<'EOF'
{
  "fields": {
    "project": {
      "key": "PR003946"
    },
    "summary": "[Frontend] Create Chat History List Page with 21st.dev",
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
              "text": "Create a chat history list page using 21st.dev components that displays all accessible conversation sessions with filtering and search capabilities."
            }
          ]
        },
        {
          "type": "heading",
          "attrs": {"level": 2},
          "content": [{"type": "text", "text": "UI Requirements"}]
        },
        {
          "type": "bulletList",
          "content": [
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Use 21st.dev data table component for session list"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Implement filter sidebar with date range picker"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Add search bar for finding specific conversations"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Include animal avatar badges"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Responsive design for mobile/tablet/desktop"}]}]}
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
              "text": "8 story points"
            }
          ]
        }
      ]
    },
    "issuetype": {
      "name": "Task"
    },
    "priority": {
      "name": "High"
    },
    "labels": ["frontend", "ui", "21st.dev", "history", "chat-history"],
    "customfield_10225": {
      "value": "Billable"
    },
    "customfield_10014": "PR003946-61"
  }
}
EOF
)

RESPONSE7=$(curl -s -X POST \
    "$JIRA_BASE_URL/rest/api/3/issue" \
    -H "Authorization: Basic $AUTH" \
    -H "Accept: application/json" \
    -H "Content-Type: application/json" \
    -d "$TICKET7_BODY")

if echo "$RESPONSE7" | grep -q '"key"'; then
    TICKET7_KEY=$(echo "$RESPONSE7" | jq -r '.key')
    echo -e "${GREEN}✓ Created ticket: $TICKET7_KEY${NC}"
    echo "$TICKET7_KEY" >> created_tickets_remaining.txt
else
    echo -e "${RED}✗ Failed to create ticket 7${NC}"
    echo "Response: $RESPONSE7"
fi

echo ""

# Ticket 8: Frontend Conversation Viewer
echo "Creating ticket 8: Conversation Viewer Page with 21st.dev..."

TICKET8_BODY=$(cat <<'EOF'
{
  "fields": {
    "project": {
      "key": "PR003946"
    },
    "summary": "[Frontend] Create Conversation Viewer Page with 21st.dev",
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
              "text": "Build a conversation viewer page using 21st.dev chat components to display historical conversations with proper formatting and metadata."
            }
          ]
        },
        {
          "type": "heading",
          "attrs": {"level": 2},
          "content": [{"type": "text", "text": "UI Requirements"}]
        },
        {
          "type": "bulletList",
          "content": [
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Use 21st.dev chat/message components"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Implement message bubbles with sender identification"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Add timestamp displays"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Include animal avatar in header"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Support message metadata tooltips"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Export to PDF/Text functionality"}]}]}
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
              "text": "8 story points"
            }
          ]
        }
      ]
    },
    "issuetype": {
      "name": "Task"
    },
    "priority": {
      "name": "High"
    },
    "labels": ["frontend", "ui", "21st.dev", "viewer", "chat-history"],
    "customfield_10225": {
      "value": "Billable"
    },
    "customfield_10014": "PR003946-61"
  }
}
EOF
)

RESPONSE8=$(curl -s -X POST \
    "$JIRA_BASE_URL/rest/api/3/issue" \
    -H "Authorization: Basic $AUTH" \
    -H "Accept: application/json" \
    -H "Content-Type: application/json" \
    -d "$TICKET8_BODY")

if echo "$RESPONSE8" | grep -q '"key"'; then
    TICKET8_KEY=$(echo "$RESPONSE8" | jq -r '.key')
    echo -e "${GREEN}✓ Created ticket: $TICKET8_KEY${NC}"
    echo "$TICKET8_KEY" >> created_tickets_remaining.txt
else
    echo -e "${RED}✗ Failed to create ticket 8${NC}"
    echo "Response: $RESPONSE8"
fi

echo ""

# Ticket 9: Frontend Streaming UI
echo "Creating ticket 9: Real-time Chat Streaming UI with 21st.dev..."

TICKET9_BODY=$(cat <<'EOF'
{
  "fields": {
    "project": {
      "key": "PR003946"
    },
    "summary": "[Frontend] Implement Real-time Chat Streaming UI with 21st.dev",
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
              "text": "Enhance the chat interface to support real-time streaming responses using Server-Sent Events, displaying text as it's generated by ChatGPT."
            }
          ]
        },
        {
          "type": "heading",
          "attrs": {"level": 2},
          "content": [{"type": "text", "text": "UI Requirements"}]
        },
        {
          "type": "bulletList",
          "content": [
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Use 21st.dev streaming text component"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Implement typing indicator animation"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Add message status indicators"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Support partial message rendering"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Handle connection status"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Smooth text appearance animation"}]}]}
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
              "text": "10 story points"
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
    "labels": ["frontend", "ui", "streaming", "realtime", "21st.dev", "chat-history"],
    "customfield_10225": {
      "value": "Billable"
    },
    "customfield_10014": "PR003946-61"
  }
}
EOF
)

RESPONSE9=$(curl -s -X POST \
    "$JIRA_BASE_URL/rest/api/3/issue" \
    -H "Authorization: Basic $AUTH" \
    -H "Accept: application/json" \
    -H "Content-Type: application/json" \
    -d "$TICKET9_BODY")

if echo "$RESPONSE9" | grep -q '"key"'; then
    TICKET9_KEY=$(echo "$RESPONSE9" | jq -r '.key')
    echo -e "${GREEN}✓ Created ticket: $TICKET9_KEY${NC}"
    echo "$TICKET9_KEY" >> created_tickets_remaining.txt
else
    echo -e "${RED}✗ Failed to create ticket 9${NC}"
    echo "Response: $RESPONSE9"
fi

echo ""

# Ticket 10: Frontend Family View
echo "Creating ticket 10: Family View for Parent History Access with 21st.dev..."

TICKET10_BODY=$(cat <<'EOF'
{
  "fields": {
    "project": {
      "key": "PR003946"
    },
    "summary": "[Frontend] Add Family View for Parent History Access with 21st.dev",
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
              "text": "Create a family-oriented view for parents to monitor their children's conversations using 21st.dev family/group components."
            }
          ]
        },
        {
          "type": "heading",
          "attrs": {"level": 2},
          "content": [{"type": "text", "text": "UI Requirements"}]
        },
        {
          "type": "bulletList",
          "content": [
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Use 21st.dev tab/accordion components for child separation"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Implement family member selector"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Add child safety indicators"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Include parental controls"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Show engagement metrics and popular animals"}]}]}
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
              "text": "5 story points"
            }
          ]
        }
      ]
    },
    "issuetype": {
      "name": "Task"
    },
    "priority": {
      "name": "Medium"
    },
    "labels": ["frontend", "ui", "family", "parental", "21st.dev", "chat-history"],
    "customfield_10225": {
      "value": "Billable"
    },
    "customfield_10014": "PR003946-61"
  }
}
EOF
)

RESPONSE10=$(curl -s -X POST \
    "$JIRA_BASE_URL/rest/api/3/issue" \
    -H "Authorization: Basic $AUTH" \
    -H "Accept: application/json" \
    -H "Content-Type: application/json" \
    -d "$TICKET10_BODY")

if echo "$RESPONSE10" | grep -q '"key"'; then
    TICKET10_KEY=$(echo "$RESPONSE10" | jq -r '.key')
    echo -e "${GREEN}✓ Created ticket: $TICKET10_KEY${NC}"
    echo "$TICKET10_KEY" >> created_tickets_remaining.txt
else
    echo -e "${RED}✗ Failed to create ticket 10${NC}"
    echo "Response: $RESPONSE10"
fi

echo ""

# Ticket 11: Security - Audit Logging
echo "Creating ticket 11: Audit Logging for Conversation Access..."

TICKET11_BODY=$(cat <<'EOF'
{
  "fields": {
    "project": {
      "key": "PR003946"
    },
    "summary": "[Security] Implement Audit Logging for Conversation Access",
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
              "text": "Implement comprehensive audit logging for all conversation history access to ensure compliance and security monitoring."
            }
          ]
        },
        {
          "type": "heading",
          "attrs": {"level": 2},
          "content": [{"type": "text", "text": "Audit Requirements"}]
        },
        {
          "type": "bulletList",
          "content": [
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Log conversation_viewed events"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Log conversation_exported events"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Log conversation_shared events"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Log conversation_deleted events"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Log unauthorized_access_attempt events"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Alert on suspicious activity patterns"}]}]}
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
              "text": "5 story points"
            }
          ]
        }
      ]
    },
    "issuetype": {
      "name": "Task"
    },
    "priority": {
      "name": "High"
    },
    "labels": ["security", "audit", "logging", "compliance", "chat-history"],
    "customfield_10225": {
      "value": "Billable"
    },
    "customfield_10014": "PR003946-61"
  }
}
EOF
)

RESPONSE11=$(curl -s -X POST \
    "$JIRA_BASE_URL/rest/api/3/issue" \
    -H "Authorization: Basic $AUTH" \
    -H "Accept: application/json" \
    -H "Content-Type: application/json" \
    -d "$TICKET11_BODY")

if echo "$RESPONSE11" | grep -q '"key"'; then
    TICKET11_KEY=$(echo "$RESPONSE11" | jq -r '.key')
    echo -e "${GREEN}✓ Created ticket: $TICKET11_KEY${NC}"
    echo "$TICKET11_KEY" >> created_tickets_remaining.txt
else
    echo -e "${RED}✗ Failed to create ticket 11${NC}"
    echo "Response: $RESPONSE11"
fi

echo ""

# Ticket 12: Security - Data Privacy Controls
echo "Creating ticket 12: Data Privacy Controls..."

TICKET12_BODY=$(cat <<'EOF'
{
  "fields": {
    "project": {
      "key": "PR003946"
    },
    "summary": "[Security] Implement Data Privacy Controls",
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
              "text": "Implement privacy controls including data retention, deletion, and anonymization capabilities for COPPA and GDPR compliance."
            }
          ]
        },
        {
          "type": "heading",
          "attrs": {"level": 2},
          "content": [{"type": "text", "text": "Privacy Features"}]
        },
        {
          "type": "bulletList",
          "content": [
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Auto-deletion after retention period"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "User-requested data deletion"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Data export for portability (GDPR)"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Conversation anonymization"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "PII detection and masking"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "COPPA compliance for child accounts"}]}]}
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
              "text": "5 story points"
            }
          ]
        }
      ]
    },
    "issuetype": {
      "name": "Task"
    },
    "priority": {
      "name": "High"
    },
    "labels": ["security", "privacy", "gdpr", "coppa", "chat-history"],
    "customfield_10225": {
      "value": "Billable"
    },
    "customfield_10014": "PR003946-61"
  }
}
EOF
)

RESPONSE12=$(curl -s -X POST \
    "$JIRA_BASE_URL/rest/api/3/issue" \
    -H "Authorization: Basic $AUTH" \
    -H "Accept: application/json" \
    -H "Content-Type: application/json" \
    -d "$TICKET12_BODY")

if echo "$RESPONSE12" | grep -q '"key"'; then
    TICKET12_KEY=$(echo "$RESPONSE12" | jq -r '.key')
    echo -e "${GREEN}✓ Created ticket: $TICKET12_KEY${NC}"
    echo "$TICKET12_KEY" >> created_tickets_remaining.txt
else
    echo -e "${RED}✗ Failed to create ticket 12${NC}"
    echo "Response: $RESPONSE12"
fi

echo ""

# Ticket 13: Infrastructure - DynamoDB Setup
echo "Creating ticket 13: Setup DynamoDB Tables and Indexes..."

TICKET13_BODY=$(cat <<'EOF'
{
  "fields": {
    "project": {
      "key": "PR003946"
    },
    "summary": "[Infrastructure] Setup DynamoDB Tables and Indexes",
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
              "text": "Create and configure DynamoDB tables for conversation storage with appropriate indexes, scaling, and backup policies."
            }
          ]
        },
        {
          "type": "heading",
          "attrs": {"level": 2},
          "content": [{"type": "text", "text": "Table Configuration"}]
        },
        {
          "type": "bulletList",
          "content": [
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Table name: cmz-conversations"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Configure GSI indexes for session, animal, and parent queries"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Enable encryption with KMS"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Configure TTL for 90-day retention"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Enable point-in-time recovery"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Setup auto-scaling"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Enable DynamoDB streams"}]}]}
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
              "text": "3 story points"
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
    "labels": ["infrastructure", "dynamodb", "aws", "setup", "chat-history"],
    "customfield_10225": {
      "value": "Billable"
    },
    "customfield_10014": "PR003946-61"
  }
}
EOF
)

RESPONSE13=$(curl -s -X POST \
    "$JIRA_BASE_URL/rest/api/3/issue" \
    -H "Authorization: Basic $AUTH" \
    -H "Accept: application/json" \
    -H "Content-Type: application/json" \
    -d "$TICKET13_BODY")

if echo "$RESPONSE13" | grep -q '"key"'; then
    TICKET13_KEY=$(echo "$RESPONSE13" | jq -r '.key')
    echo -e "${GREEN}✓ Created ticket: $TICKET13_KEY${NC}"
    echo "$TICKET13_KEY" >> created_tickets_remaining.txt
else
    echo -e "${RED}✗ Failed to create ticket 13${NC}"
    echo "Response: $RESPONSE13"
fi

echo ""

# Ticket 14: E2E Testing
echo "Creating ticket 14: E2E Tests for Complete Chat Flow..."

TICKET14_BODY=$(cat <<'EOF'
{
  "fields": {
    "project": {
      "key": "PR003946"
    },
    "summary": "[Testing] E2E Tests for Complete Chat Flow",
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
              "text": "Create comprehensive end-to-end tests covering the entire chat flow from initiation through history viewing with all permission scenarios."
            }
          ]
        },
        {
          "type": "heading",
          "attrs": {"level": 2},
          "content": [{"type": "text", "text": "Test Scenarios"}]
        },
        {
          "type": "bulletList",
          "content": [
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Complete chat flow with streaming"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Streaming message reception"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Error handling (network, timeout)"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Permission scenarios (user, parent, admin)"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Export and share functionality"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Mobile responsive behavior"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Performance under load"}]}]},
            {"type": "listItem", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Accessibility compliance (WCAG 2.1 AA)"}]}]}
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
              "text": "8 story points"
            }
          ]
        }
      ]
    },
    "issuetype": {
      "name": "Task"
    },
    "priority": {
      "name": "High"
    },
    "labels": ["testing", "e2e", "playwright", "qa", "chat-history"],
    "customfield_10225": {
      "value": "Billable"
    },
    "customfield_10014": "PR003946-61"
  }
}
EOF
)

RESPONSE14=$(curl -s -X POST \
    "$JIRA_BASE_URL/rest/api/3/issue" \
    -H "Authorization: Basic $AUTH" \
    -H "Accept: application/json" \
    -H "Content-Type: application/json" \
    -d "$TICKET14_BODY")

if echo "$RESPONSE14" | grep -q '"key"'; then
    TICKET14_KEY=$(echo "$RESPONSE14" | jq -r '.key')
    echo -e "${GREEN}✓ Created ticket: $TICKET14_KEY${NC}"
    echo "$TICKET14_KEY" >> created_tickets_remaining.txt
else
    echo -e "${RED}✗ Failed to create ticket 14${NC}"
    echo "Response: $RESPONSE14"
fi

echo ""
echo "=================================================="
echo "Summary"
echo "=================================================="
echo ""

if [ -s created_tickets_remaining.txt ]; then
    echo -e "${GREEN}Successfully created the following tickets:${NC}"
    cat created_tickets_remaining.txt
    echo ""
    echo "Total tickets created: $(wc -l < created_tickets_remaining.txt)"
    echo ""
    echo "Combined with previous tickets (PR003946-156, 157, 158),"
    echo "all 14 tickets for the Chat and Chat History Epic have been created."
else
    echo -e "${RED}No tickets were created successfully${NC}"
fi

echo ""
echo "Epic Scope Summary:"
echo "- 14 total tickets"
echo "- 89 story points"
echo "- 3-4 sprints estimated duration"
echo "- Covers backend, frontend, security, and infrastructure"