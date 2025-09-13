#!/bin/bash
# Simple Jira API v3 Fetch - Compatible version

set -e

# Load environment
if [ -f ".env.local" ]; then
    source .env.local
fi

# Check auth
if [ -z "$JIRA_API_TOKEN" ]; then
    echo "❌ Error: JIRA_API_TOKEN not found in .env.local"
    exit 1
fi

# Configuration
JIRA_BASE_URL="https://nortal.atlassian.net"
AUTH_HEADER=$(echo -n "$JIRA_EMAIL:$JIRA_API_TOKEN" | base64)

mkdir -p jira_data

echo "🔍 Fetching CMZ Jira tickets using API v3..."
echo "📊 Base URL: $JIRA_BASE_URL"
echo "👤 Email: $JIRA_EMAIL"
echo ""

# Simple function to test one JQL query
test_jql() {
    local jql="$1"
    local name="$2"

    echo "🔍 Testing: $name"
    echo "📝 JQL: $jql"

    # Create JSON payload
    local payload="{\"jql\":\"$jql\",\"startAt\":0,\"maxResults\":100,\"fields\":[\"key\",\"summary\",\"description\",\"status\",\"issuetype\"]}"

    # Make request
    local response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
        -X POST \
        -H "Authorization: Basic $AUTH_HEADER" \
        -H "Content-Type: application/json" \
        -d "$payload" \
        "${JIRA_BASE_URL}/rest/api/3/search/jql")

    # Parse response
    local http_status=$(echo "$response" | tail -1 | sed 's/HTTP_STATUS://')
    local response_body=$(echo "$response" | sed '$d')

    if [ "$http_status" = "200" ]; then
        local output_file="jira_data/tickets_${name}.json"
        echo "$response_body" > "$output_file"

        local count=$(echo "$response_body" | grep -c '"key"' || echo "0")
        echo "✅ Success: Found $count tickets"

        if [ "$count" -gt 0 ]; then
            echo "📋 Sample keys:"
            echo "$response_body" | grep -o '"key":"[^"]*"' | head -3 | sed 's/"key":"/ • /' | sed 's/"//'
        fi

        echo "📄 Saved: $output_file"
        echo ""
        return $count
    else
        echo "❌ HTTP $http_status"
        echo "$response_body" | head -2
        echo ""
        return 0
    fi
}

# Test multiple JQL patterns
TOTAL=0

# Test 1: Simple project search
TOTAL=$((TOTAL + $(test_jql "project = CMZ" "project_cmz")))

# Test 2: Project with full name
TOTAL=$((TOTAL + $(test_jql "project = 'Cougar Mountain Zoo'" "project_full")))

# Test 3: Summary search
TOTAL=$((TOTAL + $(test_jql "summary ~ CMZ OR summary ~ Zoo" "summary_search")))

# Test 4: All projects (to see what's available)
TOTAL=$((TOTAL + $(test_jql "project is not empty ORDER BY key DESC" "all_projects")))

# Test 5: Try with the PR number we've seen
TOTAL=$((TOTAL + $(test_jql "key ~ PR003946" "pr_keys")))

echo "🎯 **RESULTS:**"
echo "📊 Total unique tickets found: $TOTAL"

if [ "$TOTAL" -gt 0 ]; then
    echo "✅ SUCCESS: Found Jira tickets!"
    echo "📁 Data saved in jira_data/ directory"

    echo ""
    echo "📋 Files created:"
    ls -la jira_data/tickets_*.json | awk '{print "  📄", $9, "(" $5, "bytes)"}'

else
    echo "❌ No tickets found"
    echo "💡 Next steps:"
    echo "  1. Check project permissions in Jira"
    echo "  2. Verify correct Jira instance"
    echo "  3. Manual search in Jira web interface"
fi