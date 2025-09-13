#!/bin/bash
# Working Jira API v3 Fetch - Using correct project key and GET method
# Based on sequential reasoning: PR003946 is the actual project key

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

echo "🔍 Fetching ALL CMZ tickets using correct API approach..."
echo "📊 Base URL: $JIRA_BASE_URL"
echo "👤 Email: $JIRA_EMAIL"
echo "🔑 Project Key: PR003946 (discovered from test references)"
echo ""

# Function to fetch tickets with pagination
fetch_all_tickets() {
    local project_key="$1"
    local start_at=0
    local max_results=50
    local all_tickets_file="jira_data/all_${project_key,,}_tickets.json"
    local total_fetched=0

    echo "[]" > "$all_tickets_file"

    echo "🚀 Starting paginated fetch for project: $project_key"

    while true; do
        echo "📄 Fetching page: startAt=$start_at, maxResults=$max_results"

        # Build JQL query with proper encoding
        local jql="project = $project_key ORDER BY key ASC"
        local encoded_jql=$(echo "$jql" | sed 's/ /%20/g' | sed 's/=/%3D/g')

        # Build URL with parameters
        local url="${JIRA_BASE_URL}/rest/api/3/search"
        url="${url}?jql=${encoded_jql}"
        url="${url}&startAt=${start_at}"
        url="${url}&maxResults=${max_results}"
        url="${url}&fields=key,summary,description,status,issuetype,assignee,created,updated,priority,labels,customfield_10028"

        # Make GET request
        local response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
            -H "Authorization: Basic $AUTH_HEADER" \
            -H "Accept: application/json" \
            "$url")

        # Parse response
        local http_status=$(echo "$response" | tail -1 | sed 's/HTTP_STATUS://')
        local response_body=$(echo "$response" | sed '$d')

        if [ "$http_status" = "200" ]; then
            # Parse JSON response (basic parsing without jq)
            local issues_count=$(echo "$response_body" | grep -c '"key":' || echo "0")
            local total_available=$(echo "$response_body" | grep -o '"total":[0-9]*' | head -1 | cut -d: -f2 || echo "0")

            echo "✅ Success: Found $issues_count tickets on this page"
            echo "📊 Total available: $total_available tickets"

            if [ "$issues_count" -eq 0 ]; then
                echo "🔚 No more tickets to fetch"
                break
            fi

            # Save this page
            local page_file="jira_data/page_${start_at}_${project_key,,}.json"
            echo "$response_body" > "$page_file"

            # Extract just the issues array and append to all_tickets
            echo "$response_body" | grep -o '"issues":\[[^]]*\]' | sed 's/"issues"://' > "temp_issues.json"

            # Merge with existing tickets (simple concatenation approach)
            if [ "$total_fetched" -eq 0 ]; then
                cp "temp_issues.json" "$all_tickets_file"
            else
                # Simple merge - we'll clean this up later
                cat "temp_issues.json" >> "$all_tickets_file"
            fi

            rm -f "temp_issues.json"
            total_fetched=$((total_fetched + issues_count))

            # Show sample ticket keys
            echo "📋 Sample tickets from this page:"
            echo "$response_body" | grep -o '"key":"[^"]*"' | head -3 | sed 's/"key":"/ • /' | sed 's/"//'

            # Check if we've got everything
            if [ "$issues_count" -lt "$max_results" ]; then
                echo "📄 Reached end of results (got $issues_count < $max_results)"
                break
            fi

            start_at=$((start_at + max_results))

            # Rate limiting
            sleep 0.5

        else
            echo "❌ HTTP $http_status"
            echo "$response_body" | head -3
            break
        fi
    done

    echo ""
    echo "🎯 **FETCH COMPLETE for $project_key:**"
    echo "📊 Total tickets fetched: $total_fetched"
    echo "📄 Saved to: $all_tickets_file"

    return $total_fetched
}

# Fetch tickets for the correct project key
TOTAL_TICKETS=$(fetch_all_tickets "PR003946")

# Also try some alternative patterns based on what we've seen
if [ "$TOTAL_TICKETS" -eq 0 ]; then
    echo ""
    echo "🔍 No tickets found for PR003946, trying alternative searches..."

    # Try just the number part
    TOTAL_TICKETS=$(fetch_all_tickets "003946")
fi

if [ "$TOTAL_TICKETS" -eq 0 ]; then
    # Try searching by key pattern
    echo ""
    echo "🔍 Trying key pattern search..."

    local jql="key ~ PR003946"
    local encoded_jql=$(echo "$jql" | sed 's/ /%20/g' | sed 's/~/%7E/g')
    local url="${JIRA_BASE_URL}/rest/api/3/search?jql=${encoded_jql}&maxResults=100&fields=key,summary,description,status"

    local response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
        -H "Authorization: Basic $AUTH_HEADER" \
        -H "Accept: application/json" \
        "$url")

    local http_status=$(echo "$response" | tail -1 | sed 's/HTTP_STATUS://')
    local response_body=$(echo "$response" | sed '$d')

    if [ "$http_status" = "200" ]; then
        echo "$response_body" > "jira_data/key_pattern_search.json"
        local count=$(echo "$response_body" | grep -c '"key":' || echo "0")
        echo "✅ Key pattern search found: $count tickets"
        TOTAL_TICKETS=$count
    fi
fi

# Final summary
echo ""
echo "🎯 **FINAL RESULTS:**"
echo "📊 Total CMZ tickets found: $TOTAL_TICKETS"

if [ "$TOTAL_TICKETS" -gt 0 ]; then
    echo "✅ SUCCESS: Found CMZ tickets in Nortal Jira!"
    echo ""
    echo "📁 Files created:"
    ls -la jira_data/ | grep -E "\.(json)$" | awk '{print "  📄", $9, "(" $5, "bytes)"}'

    echo ""
    echo "🔍 **Sample ticket keys found:**"
    find jira_data -name "*.json" -exec grep -h -o '"key":"[^"]*"' {} \; | head -10 | sed 's/"key":"/ • /' | sed 's/"//'

    echo ""
    echo "✅ **Next Steps:**"
    echo "1. ✅ Successfully fetched $TOTAL_TICKETS CMZ tickets"
    echo "2. 📝 Ready to extract acceptance criteria from descriptions"
    echo "3. 🔗 Ready to map ACs to existing 439 test methods"
    echo "4. 📊 Ready to calculate true TDD coverage percentage"

else
    echo "❌ No CMZ tickets found"
    echo ""
    echo "🔍 **Debugging suggestions:**"
    echo "1. Check project permissions in Nortal Jira"
    echo "2. Verify project key in Jira web interface"
    echo "3. Confirm tickets exist in this Jira instance"

    # Show what projects ARE available (if any)
    echo ""
    echo "🔍 Attempting to list available projects..."
    local response=$(curl -s -H "Authorization: Basic $AUTH_HEADER" \
        "${JIRA_BASE_URL}/rest/api/3/project" | head -500)

    if echo "$response" | grep -q '"key":'; then
        echo "📋 Available projects:"
        echo "$response" | grep -o '"key":"[^"]*"' | head -10 | sed 's/"key":"/ • /' | sed 's/"//'
    fi
fi

# Save summary
cat > jira_data/fetch_summary.txt << EOF
CMZ Jira Fetch Results - $(date)
=====================================

API Endpoint: $JIRA_BASE_URL/rest/api/3/search
Method: GET with URL parameters
Authentication: $JIRA_EMAIL
Project Key Attempted: PR003946

Results:
- Total tickets found: $TOTAL_TICKETS
- Status: $([ "$TOTAL_TICKETS" -gt 0 ] && echo "SUCCESS" || echo "NO_TICKETS_FOUND")

Files created: $(ls jira_data/*.json 2>/dev/null | wc -l || echo "0")

Next steps:
$([ "$TOTAL_TICKETS" -gt 0 ] && echo "✅ Ready for AC extraction and test mapping" || echo "❌ Need to resolve ticket access issues")
EOF

echo ""
echo "📋 Summary saved to: jira_data/fetch_summary.txt"