#!/bin/bash

# Load environment
source .env.local

# Create data directory
mkdir -p jira_data

# Create auth header
AUTH_HEADER=$(echo -n "${JIRA_EMAIL}:${JIRA_API_TOKEN}" | base64)

# Fetch tickets
echo "Fetching PR003946 tickets..."
curl -s -H "Authorization: Basic ${AUTH_HEADER}" \
     -H "Accept: application/json" \
     "https://nortal.atlassian.net/rest/api/3/search?jql=project%20%3D%20PR003946%20ORDER%20BY%20key%20ASC&maxResults=50&fields=key,summary,description,status,issuetype" \
     > jira_data/pr003946_tickets.json

# Check results
if [ -f "jira_data/pr003946_tickets.json" ]; then
    TICKET_COUNT=$(grep -c '"key":' jira_data/pr003946_tickets.json || echo "0")
    echo "✅ Fetched ${TICKET_COUNT} tickets"

    if [ "$TICKET_COUNT" -gt 0 ]; then
        echo "📋 Sample tickets:"
        grep -o '"key":"[^"]*"' jira_data/pr003946_tickets.json | head -5 | sed 's/"key":"/ • /' | sed 's/"//'
        echo "📄 Data saved to: jira_data/pr003946_tickets.json"
    fi
else
    echo "❌ Failed to create ticket file"
fi