#!/bin/bash
# Use the new /rest/api/3/search/jql endpoint as required by HTTP 410 response

set -e

# Load environment
if [ -f ".env.local" ]; then
    source .env.local
fi

# Configuration
JIRA_BASE_URL="https://nortal.atlassian.net"
AUTH_HEADER=$(echo -n "$JIRA_EMAIL:$JIRA_API_TOKEN" | base64)

mkdir -p jira_data

echo "🔍 Using new /rest/api/3/search/jql endpoint..."

# Test different JQL queries to find CMZ tickets
declare -a QUERIES=(
    "project = PR003946"
    "key ~ PR003946"
    "summary ~ CMZ OR summary ~ Zoo OR summary ~ 'Cougar Mountain'"
    "project is not empty ORDER BY key DESC"
)

TOTAL_FOUND=0

for i in "${!QUERIES[@]}"; do
    JQL="${QUERIES[$i]}"
    echo ""
    echo "🔍 Testing JQL $((i+1)): $JQL"

    # Create proper JSON payload for new endpoint
    PAYLOAD=$(cat << EOF
{
    "jql": "$JQL",
    "startAt": 0,
    "maxResults": 100,
    "fields": [
        "key",
        "summary",
        "description",
        "status",
        "issuetype",
        "assignee",
        "created",
        "updated"
    ]
}
EOF
)

    # Make POST request to the new endpoint
    RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
        -X POST \
        -H "Authorization: Basic $AUTH_HEADER" \
        -H "Content-Type: application/json" \
        -H "Accept: application/json" \
        -d "$PAYLOAD" \
        "${JIRA_BASE_URL}/rest/api/3/search/jql")

    # Parse response
    HTTP_STATUS=$(echo "$RESPONSE" | tail -1 | sed 's/HTTP_STATUS://')
    RESPONSE_BODY=$(echo "$RESPONSE" | sed '$d')

    if [ "$HTTP_STATUS" = "200" ]; then
        OUTPUT_FILE="jira_data/query_${i}_results.json"
        echo "$RESPONSE_BODY" > "$OUTPUT_FILE"

        TICKET_COUNT=$(echo "$RESPONSE_BODY" | grep -c '"key":' || echo "0")
        echo "✅ Success: Found $TICKET_COUNT tickets"

        if [ "$TICKET_COUNT" -gt 0 ]; then
            echo "📋 Sample tickets:"
            echo "$RESPONSE_BODY" | grep -o '"key":"[^"]*"' | head -5 | sed 's/"key":"/ • /' | sed 's/"//'

            # Show total available
            TOTAL_AVAILABLE=$(echo "$RESPONSE_BODY" | grep -o '"total":[0-9]*' | head -1 | cut -d: -f2 || echo "unknown")
            echo "📊 Total available: $TOTAL_AVAILABLE"
        fi

        TOTAL_FOUND=$((TOTAL_FOUND + TICKET_COUNT))
        echo "📄 Saved: $OUTPUT_FILE"

    else
        echo "❌ HTTP $HTTP_STATUS"
        case $HTTP_STATUS in
            400)
                echo "$RESPONSE_BODY" | grep -o '"message":"[^"]*"' | sed 's/"message":"/Error: /' | sed 's/"//'
                ;;
            401)
                echo "Authentication failed - check JIRA_API_TOKEN"
                ;;
            403)
                echo "Permission denied - check project access"
                ;;
            *)
                echo "$RESPONSE_BODY" | head -2
                ;;
        esac
    fi
done

echo ""
echo "🎯 **FINAL RESULTS:**"
echo "📊 Total tickets found: $TOTAL_FOUND"

if [ "$TOTAL_FOUND" -gt 0 ]; then
    echo "✅ SUCCESS: Found CMZ tickets!"
    echo ""
    echo "📁 Result files created:"
    ls -la jira_data/query_*_results.json | awk '{print "  📄", $9, "(" $5, "bytes)"}'

    echo ""
    echo "🎫 All unique ticket keys:"
    find jira_data -name "query_*_results.json" -exec grep -h -o '"key":"[^"]*"' {} \; | sort -u | sed 's/"key":"/ • /' | sed 's/"//'

    # Create combined file
    echo ""
    echo "🔄 Creating combined results file..."

    # Combine all successful queries
    echo '{"combined_results": [' > jira_data/combined_cmz_tickets.json
    first_file=true

    for result_file in jira_data/query_*_results.json; do
        if [ -f "$result_file" ] && [ -s "$result_file" ]; then
            issues_content=$(cat "$result_file" | grep -o '"issues":\[[^]]*\]' | sed 's/"issues"://')

            if [ "$first_file" = "true" ]; then
                echo "$issues_content" | sed 's/^\[//' | sed 's/\]$//' >> jira_data/combined_cmz_tickets.json
                first_file=false
            else
                echo ",$issues_content" | sed 's/^\[,//' | sed 's/\]$//' >> jira_data/combined_cmz_tickets.json
            fi
        fi
    done

    echo ']}' >> jira_data/combined_cmz_tickets.json
    echo "📄 Combined file: jira_data/combined_cmz_tickets.json"

else
    echo "❌ No CMZ tickets found with any search pattern"
    echo ""
    echo "🔍 **Troubleshooting suggestions:**"
    echo "1. Verify project exists: manually search Jira for CMZ or PR003946"
    echo "2. Check permissions: ensure access to the project"
    echo "3. Try different Jira instance: tickets might be elsewhere"
    echo "4. Manual export: export tickets to CSV from Jira web interface"
fi

echo ""
echo "📋 Summary saved to jira_data/ directory"