#!/bin/bash

# Simple script to get ALL PR003946 tickets
source .env.local

AUTH_HEADER=$(echo -n "${JIRA_EMAIL}:${JIRA_API_TOKEN}" | base64)

echo "Fetching all PR003946 tickets..."

# Get first 100 tickets
curl -s -H "Authorization: Basic ${AUTH_HEADER}" \
     -H "Accept: application/json" \
     "https://nortal.atlassian.net/rest/api/3/search/jql?jql=project%20%3D%20PR003946%20ORDER%20BY%20key%20ASC&maxResults=100&fields=key,summary,status,issuetype" \
     > jira_data/first_100_tickets.json

# Check if successful and count tickets
if [ -f "jira_data/first_100_tickets.json" ]; then
    TICKET_COUNT=$(jq '.issues | length' jira_data/first_100_tickets.json 2>/dev/null || echo "0")
    IS_LAST=$(jq '.isLast' jira_data/first_100_tickets.json 2>/dev/null || echo "true")

    echo "✅ Found ${TICKET_COUNT} tickets on first page"
    echo "🏁 Is last page: ${IS_LAST}"

    if [ "$TICKET_COUNT" -gt 0 ]; then
        echo ""
        echo "📋 All ticket keys found:"
        jq -r '.issues[].key' jira_data/first_100_tickets.json | sort -V > jira_data/all_tickets_list.txt
        cat jira_data/all_tickets_list.txt

        FINAL_COUNT=$(wc -l < jira_data/all_tickets_list.txt | xargs)
        echo ""
        echo "📊 Total tickets: ${FINAL_COUNT}"

        # If not the last page, get more tickets
        if [ "$IS_LAST" != "true" ]; then
            echo "⚠️ More tickets available - need pagination"
            NEXT_TOKEN=$(jq -r '.nextPageToken // empty' jira_data/first_100_tickets.json)
            echo "🔄 Next page token: ${NEXT_TOKEN:-"none"}"
        else
            echo "✅ All tickets fetched successfully!"
        fi
    fi
else
    echo "❌ Failed to fetch tickets"
fi