#!/bin/bash
# Jira API v3 Ticket Fetch using cURL
# Uses the new /rest/api/3/search/jql endpoint

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
    exit 1
fi

# Create output directory
mkdir -p jira_data

# Create auth header
AUTH_HEADER=$(echo -n "$JIRA_EMAIL:$JIRA_TOKEN" | base64)

echo "🔍 Fetching CMZ Jira tickets using API v3..."
echo "📊 Base URL: $JIRA_BASE_URL"
echo "👤 Email: $JIRA_EMAIL"
echo ""

# Use the new /rest/api/3/search/jql endpoint
fetch_with_jql() {
    local jql="$1"
    local query_name="$2"

    echo "🔍 Testing: $query_name"
    echo "📝 JQL: $jql"

    # Create JSON payload for POST request
    local payload=$(cat << EOF
{
  "jql": "$jql",
  "startAt": 0,
  "maxResults": 100,
  "fields": ["key", "summary", "description", "status", "issuetype", "assignee", "created", "updated", "priority"]
}
EOF
)

    # Make POST request to new endpoint
    local response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
        -X POST \
        -H "Authorization: Basic $AUTH_HEADER" \
        -H "Content-Type: application/json" \
        -H "Accept: application/json" \
        -d "$payload" \
        "${JIRA_BASE_URL}/rest/api/3/search/jql")

    # Extract status and body
    local http_status=$(echo "$response" | tail -1 | sed 's/HTTP_STATUS://')
    local response_body=$(echo "$response" | sed '$d')

    if [ "$http_status" = "200" ]; then
        # Save response
        local output_file="jira_data/cmz_tickets_${query_name}.json"
        echo "$response_body" > "$output_file"

        # Count tickets
        local ticket_count=$(echo "$response_body" | grep -o '"key"' | wc -l | tr -d ' ')
        echo "✅ Success: Found $ticket_count tickets"
        echo "📄 Saved to: $output_file"

        if [ "$ticket_count" -gt 0 ]; then
            echo "📋 Sample tickets:"
            echo "$response_body" | grep -o '"key":"[^"]*"' | head -5 | sed 's/"key":"/  • /' | sed 's/"//'
            echo ""
            return $ticket_count
        fi
    else
        echo "❌ HTTP $http_status"
        echo "$response_body" | head -3
    fi

    echo ""
    return 0
}

# Try different JQL patterns
declare -A QUERIES=(
    ["project_cmz"]="project = CMZ"
    ["project_full_name"]="project = 'Cougar Mountain Zoo'"
    ["summary_search"]="summary ~ CMZ OR summary ~ Zoo OR summary ~ 'Cougar Mountain'"
    ["description_search"]="description ~ CMZ OR description ~ Zoo"
    ["multiple_projects"]="project in (CMZ, PR003946)"
    ["key_pattern"]="key ~ CMZ-"
    ["all_projects"]="project is not empty"
)

TOTAL_FOUND=0

for query_name in "${!QUERIES[@]}"; do
    jql="${QUERIES[$query_name]}"
    count=$(fetch_with_jql "$jql" "$query_name")
    TOTAL_FOUND=$((TOTAL_FOUND + count))
done

echo "🎯 **FINAL SUMMARY:**"
echo "📊 Total tickets found: $TOTAL_FOUND"

if [ "$TOTAL_FOUND" -gt 0 ]; then
    echo "✅ SUCCESS: Found CMZ tickets!"
    echo "📁 Raw data in jira_data/ directory"

    # List all created files
    echo ""
    echo "📋 Created files:"
    ls -la jira_data/cmz_tickets_*.json 2>/dev/null | awk '{print "  📄", $9, "(" $5, "bytes)"}'

else
    echo "❌ No CMZ tickets found"
    echo ""
    echo "🔍 **Next Steps:**"
    echo "1. Check if CMZ project exists in this Jira instance"
    echo "2. Verify project permissions"
    echo "3. Try manual Jira search to identify correct project key"
    echo "4. Consider tickets might be in different Jira workspace"
fi

# Also save a summary
cat > jira_data/fetch_summary.txt << EOF
Jira Fetch Summary - $(date)
================================
Total tickets found: $TOTAL_FOUND
API Endpoint: ${JIRA_BASE_URL}/rest/api/3/search/jql
Authentication: $JIRA_EMAIL
Status: $([ "$TOTAL_FOUND" -gt 0 ] && echo "SUCCESS" || echo "NO_TICKETS_FOUND")

Queries attempted:
$(printf '%s\n' "${!QUERIES[@]}" | sed 's/^/- /')

Files created:
$(ls jira_data/cmz_tickets_*.json 2>/dev/null | sed 's/^/- /' || echo "- None")
EOF

echo ""
echo "📋 Summary saved to: jira_data/fetch_summary.txt"