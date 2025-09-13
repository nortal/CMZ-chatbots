#!/bin/bash
# Fetch CMZ tickets using working API patterns

set -e

# Load environment
if [ -f ".env.local" ]; then
    source .env.local
fi

# Check auth
if [ -z "$JIRA_API_TOKEN" ]; then
    echo "❌ Error: JIRA_API_TOKEN not found"
    exit 1
fi

# Configuration
JIRA_BASE_URL="https://nortal.atlassian.net"
AUTH_HEADER=$(echo -n "$JIRA_EMAIL:$JIRA_API_TOKEN" | base64)

mkdir -p jira_data

echo "🔍 Fetching CMZ tickets using PR003946 project key..."
echo "📊 Base URL: $JIRA_BASE_URL"
echo ""

# Fetch tickets with pagination
START_AT=0
MAX_RESULTS=50
TOTAL_FETCHED=0

while true; do
    echo "📄 Fetching page: startAt=$START_AT"

    # Build URL with proper encoding
    JQL="project = PR003946 ORDER BY key ASC"
    ENCODED_JQL=$(echo "$JQL" | sed 's/ /%20/g' | sed 's/=/%3D/g')

    URL="${JIRA_BASE_URL}/rest/api/3/search"
    URL="${URL}?jql=${ENCODED_JQL}"
    URL="${URL}&startAt=${START_AT}"
    URL="${URL}&maxResults=${MAX_RESULTS}"
    URL="${URL}&fields=key,summary,description,status,issuetype,assignee,created,updated"

    # Make request
    RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
        -H "Authorization: Basic $AUTH_HEADER" \
        -H "Accept: application/json" \
        "$URL")

    # Parse response
    HTTP_STATUS=$(echo "$RESPONSE" | tail -1 | sed 's/HTTP_STATUS://')
    RESPONSE_BODY=$(echo "$RESPONSE" | sed '$d')

    if [ "$HTTP_STATUS" = "200" ]; then
        # Save page
        PAGE_FILE="jira_data/cmz_tickets_page_${START_AT}.json"
        echo "$RESPONSE_BODY" > "$PAGE_FILE"

        # Count tickets
        TICKET_COUNT=$(echo "$RESPONSE_BODY" | grep -c '"key":' || echo "0")
        TOTAL_AVAILABLE=$(echo "$RESPONSE_BODY" | grep -o '"total":[0-9]*' | head -1 | cut -d: -f2 || echo "0")

        echo "✅ Found $TICKET_COUNT tickets (total available: $TOTAL_AVAILABLE)"

        if [ "$TICKET_COUNT" -gt 0 ]; then
            echo "📋 Sample tickets:"
            echo "$RESPONSE_BODY" | grep -o '"key":"[^"]*"' | head -3 | sed 's/"key":"/ • /' | sed 's/"//'
        fi

        TOTAL_FETCHED=$((TOTAL_FETCHED + TICKET_COUNT))

        # Check if we're done
        if [ "$TICKET_COUNT" -lt "$MAX_RESULTS" ]; then
            echo "📄 Reached end of results"
            break
        fi

        START_AT=$((START_AT + MAX_RESULTS))
        sleep 0.5

    else
        echo "❌ HTTP $HTTP_STATUS"
        echo "$RESPONSE_BODY" | head -3
        break
    fi
done

echo ""
echo "🎯 **FETCH COMPLETE:**"
echo "📊 Total tickets fetched: $TOTAL_FETCHED"

if [ "$TOTAL_FETCHED" -gt 0 ]; then
    echo "✅ SUCCESS: Found CMZ tickets!"

    # Combine all pages into single file
    echo "🔄 Combining all pages into single file..."

    # Create combined tickets file
    echo '{"issues": [' > jira_data/all_cmz_tickets.json

    FIRST_FILE=true
    for page_file in jira_data/cmz_tickets_page_*.json; do
        if [ -f "$page_file" ]; then
            # Extract just the issues array content
            ISSUES_CONTENT=$(cat "$page_file" | grep -o '"issues":\[[^]]*\]' | sed 's/"issues":\[//' | sed 's/\]$//')

            if [ "$FIRST_FILE" = true ]; then
                echo "$ISSUES_CONTENT" >> jira_data/all_cmz_tickets.json
                FIRST_FILE=false
            else
                echo ",$ISSUES_CONTENT" >> jira_data/all_cmz_tickets.json
            fi
        fi
    done

    echo ']}' >> jira_data/all_cmz_tickets.json

    echo "📄 Combined file: jira_data/all_cmz_tickets.json"
    echo "📋 Individual pages: jira_data/cmz_tickets_page_*.json"

    # Show all ticket keys
    echo ""
    echo "🎫 All ticket keys found:"
    grep -h -o '"key":"[^"]*"' jira_data/cmz_tickets_page_*.json | sed 's/"key":"/ • /' | sed 's/"//' | sort

else
    echo "❌ No tickets found"
    echo "💡 Check project permissions or try manual Jira search"
fi

echo ""
echo "📋 Files created in jira_data/ directory"
ls -la jira_data/