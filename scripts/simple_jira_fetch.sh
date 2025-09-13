#!/bin/bash
# Simple Jira Ticket Fetch using cURL
# Gets CMZ tickets and saves raw JSON

set -e

# Load environment
if [ -f ".env.local" ]; then
    source .env.local
elif [ -f "../.env.local" ]; then
    source ../.env.local
fi

# Configuration
JIRA_BASE_URL="https://nortal.atlassian.net"
JIRA_EMAIL="${JIRA_EMAIL:-kc.stegbauer@nortal.com}"
JIRA_TOKEN="${JIRA_API_TOKEN}"

# Check auth
if [ -z "$JIRA_TOKEN" ]; then
    echo "❌ Error: JIRA_API_TOKEN not found"
    echo "💡 Make sure .env.local exists with JIRA_API_TOKEN"
    exit 1
fi

# Create output directory
mkdir -p jira_data

# Create auth header
AUTH_HEADER=$(echo -n "$JIRA_EMAIL:$JIRA_TOKEN" | base64)

echo "🔍 Fetching CMZ Jira tickets..."
echo "📊 Base URL: $JIRA_BASE_URL"
echo "👤 Email: $JIRA_EMAIL"
echo ""

# Try different JQL queries to find CMZ tickets
declare -a JQL_QUERIES=(
    "project = CMZ"
    "project = 'Cougar Mountain Zoo'"
    "summary ~ CMZ OR summary ~ Zoo OR summary ~ 'Cougar Mountain'"
    "description ~ CMZ OR description ~ Zoo"
    "project in (CMZ, PR003946)"
    "key ~ CMZ-"
)

TOTAL_FOUND=0

for i in "${!JQL_QUERIES[@]}"; do
    JQL="${JQL_QUERIES[$i]}"
    echo "🔍 Testing JQL $((i+1)): $JQL"

    # URL encode the JQL
    ENCODED_JQL=$(echo "$JQL" | sed 's/ /%20/g' | sed 's/=/%3D/g' | sed 's/~/%7E/g' | sed "s/'/%27/g")

    # Build URL
    URL="${JIRA_BASE_URL}/rest/api/3/search?jql=${ENCODED_JQL}&startAt=0&maxResults=50&fields=key,summary,description,status,issuetype"

    # Make request
    RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
        -H "Authorization: Basic $AUTH_HEADER" \
        -H "Content-Type: application/json" \
        -H "Accept: application/json" \
        "$URL")

    # Extract status
    HTTP_STATUS=$(echo "$RESPONSE" | tail -1 | sed 's/HTTP_STATUS://')
    RESPONSE_BODY=$(echo "$RESPONSE" | sed '$d')

    if [ "$HTTP_STATUS" = "200" ]; then
        # Save raw response
        OUTPUT_FILE="jira_data/cmz_tickets_query_${i}.json"
        echo "$RESPONSE_BODY" > "$OUTPUT_FILE"

        # Try to count tickets (basic grep instead of jq)
        TICKET_COUNT=$(echo "$RESPONSE_BODY" | grep -o '"key"' | wc -l)
        echo "✅ Success: Found $TICKET_COUNT tickets"
        echo "📄 Saved to: $OUTPUT_FILE"

        TOTAL_FOUND=$((TOTAL_FOUND + TICKET_COUNT))

        # Show first few ticket keys if any found
        if [ "$TICKET_COUNT" -gt 0 ]; then
            echo "📋 Sample tickets:"
            echo "$RESPONSE_BODY" | grep -o '"key":"[^"]*"' | head -5 | sed 's/"key":"/  • /' | sed 's/"//'
        fi
    else
        echo "❌ HTTP $HTTP_STATUS: $(echo "$RESPONSE_BODY" | head -1)"
    fi

    echo ""
done

echo "🎯 **SUMMARY:**"
echo "📊 Total tickets found across all queries: $TOTAL_FOUND"

if [ "$TOTAL_FOUND" -gt 0 ]; then
    echo "✅ SUCCESS: Found CMZ tickets!"
    echo "📁 Data saved in jira_data/ directory"
    echo ""
    echo "📋 Files created:"
    ls -la jira_data/cmz_tickets_query_*.json 2>/dev/null || echo "  No files found"
else
    echo "❌ No CMZ tickets found with any query pattern"
    echo "💡 Possible issues:"
    echo "  - CMZ project might use different key/name"
    echo "  - Tickets might be in different Jira instance"
    echo "  - Access permissions might be limited"
fi