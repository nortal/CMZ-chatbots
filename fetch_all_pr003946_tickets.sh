#!/bin/bash

# Fetch ALL PR003946 tickets using working GET method with token-based pagination
# Based on successful Method 3 discovery

set -e

# Load environment
source .env.local

# Create auth header
AUTH_HEADER=$(echo -n "${JIRA_EMAIL}:${JIRA_API_TOKEN}" | base64)
JIRA_BASE="https://nortal.atlassian.net"

echo "🎯 Fetching ALL PR003946 tickets using working GET method"
echo "========================================================"
echo "📧 Email: ${JIRA_EMAIL}"
echo "🏢 Base URL: ${JIRA_BASE}"
echo ""

# Prepare output
mkdir -p jira_data
rm -f jira_data/pr003946_page_*.json
rm -f jira_data/all_pr003946_tickets.json

# Initialize pagination
PAGE_NUM=1
TOTAL_FETCHED=0
ALL_TICKETS="[]"
NEXT_PAGE_TOKEN=""

while true; do
    echo "📄 Fetching page ${PAGE_NUM}..."

    # Build URL - use nextPageToken if available
    JQL_ENCODED=$(echo "project = PR003946 ORDER BY key ASC" | sed 's/ /%20/g' | sed 's/=/%3D/g')
    if [ -z "$NEXT_PAGE_TOKEN" ]; then
        # First page
        URL="${JIRA_BASE}/rest/api/3/search/jql?jql=${JQL_ENCODED}&maxResults=50&fields=key,summary,status,issuetype,description,priority,assignee,created,updated"
    else
        # Subsequent pages with token
        URL="${JIRA_BASE}/rest/api/3/search/jql?jql=${JQL_ENCODED}&maxResults=50&fields=key,summary,status,issuetype,description,priority,assignee,created,updated&pageToken=${NEXT_PAGE_TOKEN}"
    fi

    echo "🔗 URL: ${URL}"

    # Make request
    PAGE_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
        -H "Authorization: Basic ${AUTH_HEADER}" \
        -H "Accept: application/json" \
        "$URL")

    # Parse response
    HTTP_STATUS=$(echo "$PAGE_RESPONSE" | tail -1 | sed 's/HTTP_STATUS://')
    RESPONSE_BODY=$(echo "$PAGE_RESPONSE" | sed '$d')

    echo "HTTP Status: ${HTTP_STATUS}"

    if [ "$HTTP_STATUS" = "200" ]; then
        # Save raw page response
        echo "$RESPONSE_BODY" > "jira_data/pr003946_page_${PAGE_NUM}.json"

        # Count tickets on this page
        PAGE_COUNT=$(echo "$RESPONSE_BODY" | grep -c '"key":"PR003946-' || echo "0")
        echo "✅ Found ${PAGE_COUNT} tickets on page ${PAGE_NUM}"

        if [ "$PAGE_COUNT" -eq 0 ]; then
            echo "🔚 No tickets on this page - ending"
            break
        fi

        TOTAL_FETCHED=$((TOTAL_FETCHED + PAGE_COUNT))

        # Extract ticket keys for this page
        echo "📋 Tickets on this page:"
        echo "$RESPONSE_BODY" | grep -o '"key":"PR003946-[^"]*"' | sed 's/"key":"/ • /' | sed 's/"//'

        # Check for next page token
        NEXT_PAGE_TOKEN=$(echo "$RESPONSE_BODY" | grep -o '"nextPageToken":"[^"]*"' | sed 's/"nextPageToken":"//' | sed 's/"//' || echo "")
        IS_LAST=$(echo "$RESPONSE_BODY" | grep -o '"isLast":[^,}]*' | sed 's/"isLast"://' | sed 's/,//' || echo "true")

        echo "🔄 Next page token: ${NEXT_PAGE_TOKEN:-"none"}"
        echo "🏁 Is last page: ${IS_LAST}"

        # Merge tickets into consolidated array
        PAGE_ISSUES=$(echo "$RESPONSE_BODY" | grep -o '"issues":\[[^]]*\]' | sed 's/"issues"://' || echo "[]")
        ALL_TICKETS=$(echo "$ALL_TICKETS $PAGE_ISSUES" | jq -s 'add // []')

        # Check if this is the last page
        if [ "$IS_LAST" = "true" ] || [ -z "$NEXT_PAGE_TOKEN" ]; then
            echo "🏁 Reached last page"
            break
        fi

        PAGE_NUM=$((PAGE_NUM + 1))
        sleep 0.5  # Rate limiting

    else
        echo "❌ Request failed"
        echo "Response: $(echo "$RESPONSE_BODY" | head -5)"
        break
    fi

    echo ""
done

# Save consolidated results
echo "$ALL_TICKETS" > jira_data/all_pr003946_tickets.json

# Generate summary
echo ""
echo "🎉 **FETCH COMPLETE!**"
echo "========================================"
echo "📊 Total tickets fetched: ${TOTAL_FETCHED}"
echo "📁 Raw pages saved: jira_data/pr003946_page_*.json"
echo "📄 Consolidated file: jira_data/all_pr003946_tickets.json"

if [ "$TOTAL_FETCHED" -gt 0 ]; then
    # Extract all ticket keys
    echo "$ALL_TICKETS" | jq -r '.[].key' | sort -V > jira_data/all_ticket_keys.txt

    echo ""
    echo "📋 **ALL PR003946 TICKETS FOUND:**"
    cat jira_data/all_ticket_keys.txt | sed 's/^/ • /'

    UNIQUE_COUNT=$(cat jira_data/all_ticket_keys.txt | wc -l | xargs)
    echo ""
    echo "📊 **FINAL COUNT: ${UNIQUE_COUNT} unique tickets**"

    # Generate analysis
    echo ""
    echo "📈 **STATUS BREAKDOWN:**"
    echo "$ALL_TICKETS" | jq -r 'group_by(.fields.status.name) | .[] | "\(.length) tickets: \(.[0].fields.status.name)"'

    echo ""
    echo "🏷️ **TYPE BREAKDOWN:**"
    echo "$ALL_TICKETS" | jq -r 'group_by(.fields.issuetype.name) | .[] | "\(.length) tickets: \(.[0].fields.issuetype.name)"' 2>/dev/null || echo "Type information not available"

    # Key ranges
    FIRST_TICKET=$(cat jira_data/all_ticket_keys.txt | head -1)
    LAST_TICKET=$(cat jira_data/all_ticket_keys.txt | tail -1)
    echo ""
    echo "🔢 **TICKET RANGE:** ${FIRST_TICKET} to ${LAST_TICKET}"

    # Save summary
    cat > jira_data/fetch_summary.md << EOF
# PR003946 Ticket Fetch Results

**Date**: $(date)
**Total Tickets**: ${UNIQUE_COUNT}
**Fetch Method**: GET /rest/api/3/search/jql with token-based pagination
**Status**: ✅ SUCCESS

## Ticket Range
- **First Ticket**: ${FIRST_TICKET}
- **Last Ticket**: ${LAST_TICKET}

## Status Breakdown
$(echo "$ALL_TICKETS" | jq -r 'group_by(.fields.status.name) | .[] | "- \(.length) tickets: \(.[0].fields.status.name)"')

## Files Created
- \`jira_data/all_pr003946_tickets.json\` - Complete ticket data
- \`jira_data/all_ticket_keys.txt\` - List of all ticket keys
- \`jira_data/pr003946_page_*.json\` - Individual page responses

## Ready for TDD System
✅ All PR003946 tickets successfully fetched and ready for test specification generation.
EOF

    echo "📋 Summary saved to: jira_data/fetch_summary.md"

else
    echo "❌ No tickets found"
fi

echo ""
echo "✅ Ready to proceed with TDD system creation!"