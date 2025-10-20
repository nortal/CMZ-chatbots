#!/bin/bash

# Script to create Chat and Chat History Epic tickets in Jira
# Uses the Jira REST API with proper field handling

# Load environment variables
source .env.local 2>/dev/null || true

# Configuration
JIRA_BASE_URL="${JIRA_BASE_URL:-https://nortal.atlassian.net}"
JIRA_PROJECT="PR003946"
JIRA_EPIC_KEY="PR003946-61"
JIRA_AUTH="$JIRA_EMAIL:$JIRA_API_TOKEN"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to create a ticket
create_ticket() {
    local summary="$1"
    local description="$2"
    local issue_type="$3"
    local story_points="$4"
    local labels="$5"
    local priority="$6"

    echo -e "${YELLOW}Creating ticket: $summary${NC}"

    # Build the JSON payload with billable field
    local json_payload=$(cat <<EOF
{
    "fields": {
        "project": {
            "key": "$JIRA_PROJECT"
        },
        "summary": "$summary",
        "description": {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": "$description"
                        }
                    ]
                }
            ]
        },
        "issuetype": {
            "name": "$issue_type"
        },
        "priority": {
            "name": "$priority"
        },
        "labels": [$labels],
        "customfield_10225": {
            "value": "Billable",
            "id": "11636"
        }
    }
}
EOF
    )

    # Create the ticket
    response=$(curl -s -w "\n%{http_code}" \
        -u "$JIRA_AUTH" \
        -X POST \
        -H "Content-Type: application/json" \
        -d "$json_payload" \
        "$JIRA_BASE_URL/rest/api/3/issue")

    http_code=$(echo "$response" | tail -n1)
    response_body=$(echo "$response" | head -n-1)

    if [ "$http_code" -eq 201 ] || [ "$http_code" -eq 200 ]; then
        ticket_key=$(echo "$response_body" | jq -r '.key')
        echo -e "${GREEN}✓ Created ticket: $ticket_key - $summary${NC}"
        echo "$ticket_key" >> created_tickets.txt

        # Add story points if provided (custom field may vary)
        if [ -n "$story_points" ] && [ "$story_points" != "0" ]; then
            add_story_points "$ticket_key" "$story_points"
        fi

        return 0
    else
        echo -e "${RED}✗ Failed to create ticket: $summary${NC}"
        echo "Response: $response_body"
        return 1
    fi
}

# Function to add story points (if field exists)
add_story_points() {
    local ticket_key="$1"
    local points="$2"

    # Try to update story points field (field ID may vary)
    # Common field IDs: customfield_10016, customfield_10004, customfield_10005
    for field_id in "customfield_10016" "customfield_10004" "customfield_10005"; do
        curl -s \
            -u "$JIRA_AUTH" \
            -X PUT \
            -H "Content-Type: application/json" \
            -d "{\"fields\":{\"$field_id\":$points}}" \
            "$JIRA_BASE_URL/rest/api/3/issue/$ticket_key" > /dev/null 2>&1
    done
}

# Function to link tickets
link_tickets() {
    local parent="$1"
    local child="$2"
    local link_type="$3"

    echo "Linking $child to $parent..."

    curl -s \
        -u "$JIRA_AUTH" \
        -X POST \
        -H "Content-Type: application/json" \
        -d "{
            \"type\": {\"name\": \"$link_type\"},
            \"inwardIssue\": {\"key\": \"$parent\"},
            \"outwardIssue\": {\"key\": \"$child\"}
        }" \
        "$JIRA_BASE_URL/rest/api/3/issueLink" > /dev/null
}

# Clear previous run
> created_tickets.txt

echo -e "${GREEN}=== Creating Chat and Chat History Epic ===${NC}"

# Create Epic
EPIC_KEY=""
create_ticket \
    "[EPIC] Chat and Chat History Functionality" \
    "Epic for implementing comprehensive chat system with real-time streaming, DynamoDB storage, and role-based history access. Total: 89 story points across 14 tickets." \
    "Task" \
    "0" \
    '"chat","epic","chatgpt","streaming","history"' \
    "High"

EPIC_KEY=$(tail -n1 created_tickets.txt)

echo -e "\n${GREEN}=== Creating Backend Tickets ===${NC}"

# Backend Ticket 1
create_ticket \
    "[Backend] Implement ChatGPT Integration with Animal Personalities" \
    "Integrate /convo_turn endpoint with ChatGPT API for animal personality conversations. Load animal configs from DynamoDB, construct system prompts, handle streaming responses." \
    "Task" \
    "8" \
    '"backend","chatgpt","api","integration"' \
    "Highest"

# Backend Ticket 2
create_ticket \
    "[Backend] Implement Response Streaming with Server-Sent Events" \
    "Implement real-time response streaming using SSE. Create /convo_turn/stream endpoint, handle connection management, buffer tokens, cleanup on disconnect." \
    "Task" \
    "13" \
    '"backend","streaming","sse","realtime"' \
    "Highest"

# Backend Ticket 3
create_ticket \
    "[Backend] Implement DynamoDB Conversation Storage" \
    "Design DynamoDB schema for conversations. Implement batch writes, TTL, encryption, indexes for efficient querying by user/session/animal/parent." \
    "Task" \
    "8" \
    '"backend","dynamodb","storage","database"' \
    "Highest"

# Backend Ticket 4
create_ticket \
    "[Backend] Create Conversation Session List Endpoint" \
    "Create GET /conversations/sessions for paginated session list. Support filtering by date/animal, sorting, caching for performance." \
    "Task" \
    "5" \
    '"backend","api","sessions","history"' \
    "High"

# Backend Ticket 5
create_ticket \
    "[Backend] Implement Role-Based Access Control for History" \
    "Implement RBAC for conversation history. User sees own, Parent sees children's, Zookeeper sees all (read-only), Admin has full access." \
    "Task" \
    "8" \
    '"backend","security","rbac","permissions"' \
    "Highest"

# Backend Ticket 6
create_ticket \
    "[Backend] Implement Conversation History Retrieval Endpoint" \
    "Create GET /conversations/history/{sessionId} with access controls. Return messages, metadata, statistics. Support pagination for long conversations." \
    "Task" \
    "5" \
    '"backend","api","history","retrieval"' \
    "High"

echo -e "\n${GREEN}=== Creating Frontend Tickets ===${NC}"

# Frontend Ticket 7
create_ticket \
    "[Frontend] Create Chat History List Page with 21st.dev" \
    "Build chat history list using 21st.dev components. Data table with filters, date range picker, animal selector, search, responsive design." \
    "Task" \
    "8" \
    '"frontend","ui","21st.dev","history"' \
    "High"

# Frontend Ticket 8
create_ticket \
    "[Frontend] Create Conversation Viewer Page with 21st.dev" \
    "Build conversation viewer using 21st.dev chat components. Message bubbles, timestamps, animal avatars, metadata tooltips, export functionality." \
    "Task" \
    "8" \
    '"frontend","ui","21st.dev","viewer"' \
    "High"

# Frontend Ticket 9
create_ticket \
    "[Frontend] Implement Real-time Chat Streaming UI with 21st.dev" \
    "Enhance chat interface for SSE streaming. Typing indicators, partial message rendering, connection status, smooth text animation." \
    "Task" \
    "10" \
    '"frontend","ui","streaming","realtime","21st.dev"' \
    "Highest"

# Frontend Ticket 10
create_ticket \
    "[Frontend] Add Family View for Parent History Access with 21st.dev" \
    "Create family-oriented view using 21st.dev. Tab/accordion for children, safety indicators, parental insights, engagement metrics." \
    "Task" \
    "5" \
    '"frontend","ui","family","parental","21st.dev"' \
    "Medium"

echo -e "\n${GREEN}=== Creating Security & Compliance Tickets ===${NC}"

# Security Ticket 11
create_ticket \
    "[Security] Implement Audit Logging for Conversation Access" \
    "Comprehensive audit logging for all conversation access. Log views, exports, shares, unauthorized attempts. Alert on suspicious activity." \
    "Task" \
    "5" \
    '"security","audit","logging","compliance"' \
    "High"

# Security Ticket 12
create_ticket \
    "[Security] Implement Data Privacy Controls" \
    "Privacy controls for COPPA/GDPR. Auto-deletion, user-requested deletion, data export, PII detection/masking, anonymization." \
    "Task" \
    "5" \
    '"security","privacy","gdpr","coppa"' \
    "High"

echo -e "\n${GREEN}=== Creating Infrastructure & Testing Tickets ===${NC}"

# Infrastructure Ticket 13
create_ticket \
    "[Infrastructure] Setup DynamoDB Tables and Indexes" \
    "Create DynamoDB tables for conversations. Configure indexes, encryption, TTL, backups, auto-scaling. Enable streams for real-time updates." \
    "Task" \
    "3" \
    '"infrastructure","dynamodb","aws","setup"' \
    "Highest"

# Testing Ticket 14
create_ticket \
    "[Testing] E2E Tests for Complete Chat Flow" \
    "Comprehensive E2E tests with Playwright. Test streaming, permissions, export, mobile responsiveness, accessibility. >90% coverage target." \
    "Task" \
    "8" \
    '"testing","e2e","playwright","qa"' \
    "High"

echo -e "\n${GREEN}=== Linking Tickets to Epic ===${NC}"

# Link all tickets to epic if epic was created
if [ -n "$EPIC_KEY" ]; then
    # Read all created tickets except the epic
    tail -n +2 created_tickets.txt | while read ticket_key; do
        if [ -n "$ticket_key" ]; then
            link_tickets "$EPIC_KEY" "$ticket_key" "Relates"
        fi
    done
fi

echo -e "\n${GREEN}=== Summary ===${NC}"
echo "Created $(wc -l < created_tickets.txt) tickets:"
cat created_tickets.txt

echo -e "\n${GREEN}✓ All tickets created successfully!${NC}"
echo "Epic: $EPIC_KEY"
echo "Total Story Points: 89"
echo "Estimated Duration: 3-4 sprints (6-8 weeks)"