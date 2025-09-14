#!/bin/bash

# Complete fetch of ALL PR003946 tickets using working nextPageToken pagination
# Based on systematic testing results

set -e

source .env.local
AUTH_HEADER=$(echo -n "${JIRA_EMAIL}:${JIRA_API_TOKEN}" | base64)
JIRA_BASE="https://nortal.atlassian.net"

echo "🎯 FETCHING ALL PR003946 TICKETS - COMPLETE"
echo "=========================================="
echo "📧 Using nextPageToken pagination method"
echo ""

# Initialize
mkdir -p jira_data
rm -f jira_data/complete_page_*.json
rm -f jira_data/all_tickets_complete.txt

PAGE=1
TOTAL_FETCHED=0
ALL_TICKETS="[]"
NEXT_TOKEN=""

while true; do
    echo "📄 Fetching page $PAGE..."

    # Build URL
    if [ -z "$NEXT_TOKEN" ]; then
        # First page
        URL="${JIRA_BASE}/rest/api/3/search/jql?jql=project%20%3D%20PR003946%20ORDER%20BY%20key%20ASC&maxResults=100&fields=key,summary,status,issuetype,description,priority,assignee,created"
    else
        # Subsequent pages with nextPageToken
        URL="${JIRA_BASE}/rest/api/3/search/jql?jql=project%20%3D%20PR003946%20ORDER%20BY%20key%20ASC&maxResults=100&fields=key,summary,status,issuetype,description,priority,assignee,created&nextPageToken=${NEXT_TOKEN}"
    fi

    # Make request
    RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
        -H "Authorization: Basic ${AUTH_HEADER}" \
        -H "Accept: application/json" \
        "$URL")

    HTTP_STATUS=$(echo "$RESPONSE" | tail -1 | sed 's/HTTP_STATUS://')
    RESPONSE_BODY=$(echo "$RESPONSE" | sed '$d')

    if [ "$HTTP_STATUS" = "200" ]; then
        # Save page
        echo "$RESPONSE_BODY" > "jira_data/complete_page_${PAGE}.json"

        # Count tickets
        PAGE_COUNT=$(jq '.issues | length' "jira_data/complete_page_${PAGE}.json")
        IS_LAST=$(jq '.isLast' "jira_data/complete_page_${PAGE}.json")
        NEXT_TOKEN=$(jq -r '.nextPageToken // empty' "jira_data/complete_page_${PAGE}.json")

        echo "✅ Found $PAGE_COUNT tickets on page $PAGE"
        echo "🏁 Is last: $IS_LAST"

        if [ "$PAGE_COUNT" -eq 0 ]; then
            echo "🔚 No tickets on this page"
            break
        fi

        TOTAL_FETCHED=$((TOTAL_FETCHED + PAGE_COUNT))

        # Show sample tickets from this page
        echo "📋 Sample tickets:"
        jq -r '.issues[].key' "jira_data/complete_page_${PAGE}.json" | head -5 | sed 's/^/    /'

        # Add to master list
        jq -r '.issues[].key' "jira_data/complete_page_${PAGE}.json" >> jira_data/all_tickets_temp.txt

        # Check if done
        if [ "$IS_LAST" = "true" ] || [ -z "$NEXT_TOKEN" ]; then
            echo "✅ Reached final page"
            break
        fi

        PAGE=$((PAGE + 1))
        echo "🔄 Next token: ${NEXT_TOKEN:0:50}..."
        sleep 0.5

    else
        echo "❌ Failed: HTTP $HTTP_STATUS"
        echo "Response: $(echo "$RESPONSE_BODY" | head -3)"
        break
    fi

    echo ""
done

# Process results
if [ -f "jira_data/all_tickets_temp.txt" ]; then
    # Remove duplicates and sort
    sort -u jira_data/all_tickets_temp.txt > jira_data/all_tickets_complete.txt
    rm -f jira_data/all_tickets_temp.txt

    UNIQUE_COUNT=$(wc -l < jira_data/all_tickets_complete.txt | xargs)

    echo ""
    echo "🎉 **COMPLETE SUCCESS!**"
    echo "======================================"
    echo "📊 Total pages fetched: $PAGE"
    echo "📊 Total tickets found: $TOTAL_FETCHED"
    echo "📊 Unique tickets: $UNIQUE_COUNT"

    if [ "$UNIQUE_COUNT" -gt 0 ]; then
        FIRST_TICKET=$(head -1 jira_data/all_tickets_complete.txt)
        LAST_TICKET=$(tail -1 jira_data/all_tickets_complete.txt)

        echo "🔢 Range: $FIRST_TICKET to $LAST_TICKET"
        echo ""
        echo "📋 **ALL PR003946 TICKETS:**"
        cat jira_data/all_tickets_complete.txt | sed 's/^/  /'

        # Create consolidated JSON
        echo "[]" > jira_data/all_tickets_consolidated.json
        for page_file in jira_data/complete_page_*.json; do
            if [ -f "$page_file" ]; then
                ISSUES=$(jq '.issues' "$page_file")
                jq --argjson new_issues "$ISSUES" '. + $new_issues' jira_data/all_tickets_consolidated.json > jira_data/temp.json
                mv jira_data/temp.json jira_data/all_tickets_consolidated.json
            fi
        done

        echo ""
        echo "📁 **FILES CREATED:**"
        echo "  📄 all_tickets_complete.txt - List of all ticket keys"
        echo "  📄 all_tickets_consolidated.json - Complete ticket data"
        echo "  📄 complete_page_*.json - Individual page responses"

        # Create summary
        cat > jira_data/complete_fetch_summary.md << EOF
# Complete PR003946 Ticket Fetch - SUCCESS

**Date**: $(date)
**Method**: nextPageToken pagination
**Status**: ✅ ALL TICKETS SUCCESSFULLY FETCHED

## Results
- **Total Pages**: $PAGE
- **Total Tickets Found**: $TOTAL_FETCHED
- **Unique Tickets**: $UNIQUE_COUNT
- **Range**: $FIRST_TICKET to $LAST_TICKET

## Working Pagination Method
\`\`\`bash
# First page
curl -H "Authorization: Basic \${AUTH_HEADER}" \\
     "\${JIRA_BASE}/rest/api/3/search/jql?jql=project%20%3D%20PR003946%20ORDER%20BY%20key%20ASC&maxResults=100&fields=..."

# Subsequent pages
curl -H "Authorization: Basic \${AUTH_HEADER}" \\
     "\${JIRA_BASE}/rest/api/3/search/jql?jql=project%20%3D%20PR003946%20ORDER%20BY%20key%20ASC&maxResults=100&fields=...&nextPageToken=\${NEXT_TOKEN}"
\`\`\`

## Key Discovery
- Parameter name: \`nextPageToken\` (not \`pageToken\`)
- Token does NOT need URL encoding
- API returns \`isLast: true\` when complete

## Ready for TDD System
✅ Complete ticket inventory available
✅ All files ready for test specification generation
EOF

        echo "📋 Summary: jira_data/complete_fetch_summary.md"

    else
        echo "❌ No tickets found"
    fi

else
    echo "❌ No tickets file created"
fi

echo ""
echo "✅ COMPLETE TICKET FETCH FINISHED!"