#!/bin/bash
# Search for tickets in Chat Epic PR003946-170

set -e

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

echo "==========================================="
echo "Searching for Chat Epic (PR003946-170) tickets"
echo "==========================================="
echo ""

# Search for all tickets in the Chat Epic
JQL="parent=PR003946-170 ORDER BY priority DESC, created ASC"
JQL_ENCODED=$(echo "$JQL" | jq -Rr @uri)

echo "📋 Fetching tickets from Chat Epic PR003946-170..."
echo ""

RESPONSE=$(curl -s -X GET \
    "$JIRA_BASE_URL/rest/api/3/search/jql?jql=$JQL_ENCODED&maxResults=50&fields=key,summary,status,priority,issuetype" \
    -H "Authorization: Basic $AUTH" \
    -H "Accept: application/json")

# Check if request was successful
if echo "$RESPONSE" | jq -e '.issues' > /dev/null 2>&1; then
    TOTAL=$(echo "$RESPONSE" | jq -r '.total')
    echo "Found $TOTAL tickets in Chat Epic PR003946-170"
    echo ""

    # Group tickets by status
    echo "📊 Tickets by Status:"
    echo "===================="

    echo -e "\n✅ Done/Resolved:"
    echo "$RESPONSE" | jq -r '.issues[] | select(.fields.status.name == "Done" or .fields.status.name == "Resolved") | "  - \(.key): \(.fields.summary) [\(.fields.status.name)]"'

    echo -e "\n🔄 In Progress:"
    echo "$RESPONSE" | jq -r '.issues[] | select(.fields.status.name == "In Progress") | "  - \(.key): \(.fields.summary) [\(.fields.status.name)]"'

    echo -e "\n📋 To Do:"
    echo "$RESPONSE" | jq -r '.issues[] | select(.fields.status.name == "To Do") | "  - \(.key): \(.fields.summary) [Priority: \(.fields.priority.name)]"'

    echo -e "\n⏳ Other Status:"
    echo "$RESPONSE" | jq -r '.issues[] | select(.fields.status.name != "Done" and .fields.status.name != "Resolved" and .fields.status.name != "In Progress" and .fields.status.name != "To Do") | "  - \(.key): \(.fields.summary) [\(.fields.status.name)]"'

    # Count by status
    echo -e "\n📈 Summary:"
    echo "==========="
    TODO_COUNT=$(echo "$RESPONSE" | jq -r '[.issues[] | select(.fields.status.name == "To Do")] | length')
    IN_PROGRESS=$(echo "$RESPONSE" | jq -r '[.issues[] | select(.fields.status.name == "In Progress")] | length')
    DONE_COUNT=$(echo "$RESPONSE" | jq -r '[.issues[] | select(.fields.status.name == "Done" or .fields.status.name == "Resolved")] | length')
    OTHER_COUNT=$(echo "$RESPONSE" | jq -r '[.issues[] | select(.fields.status.name != "Done" and .fields.status.name != "Resolved" and .fields.status.name != "In Progress" and .fields.status.name != "To Do")] | length')

    echo "  To Do: $TODO_COUNT tickets"
    echo "  In Progress: $IN_PROGRESS tickets"
    echo "  Done/Resolved: $DONE_COUNT tickets"
    echo "  Other: $OTHER_COUNT tickets"
    echo "  -------------------"
    echo "  Total: $TOTAL tickets"

else
    echo "❌ Failed to fetch tickets"
    echo "$RESPONSE" | jq '.'
    exit 1
fi

echo ""
echo "✨ Search completed!"