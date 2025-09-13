#!/bin/bash
# Fetch All CMZ Jira Tickets using cURL
# Gets all tickets from Cougar Mountain Zoo project with acceptance criteria

set -e

# Load environment from .env.local if it exists
if [ -f ".env.local" ]; then
    echo "📄 Loading environment from .env.local..."
    export $(cat .env.local | grep -v '^#' | grep -v '^$' | xargs)
elif [ -f "../.env.local" ]; then
    echo "📄 Loading environment from ../.env.local..."
    export $(cat ../.env.local | grep -v '^#' | grep -v '^$' | xargs)
fi

# Configuration
JIRA_BASE_URL="https://nortal.atlassian.net"
JIRA_EMAIL="${JIRA_EMAIL:-kc.stegbauer@nortal.com}"
JIRA_TOKEN="${JIRA_API_TOKEN}"

# Output files
OUTPUT_DIR="jira_data"
TICKETS_FILE="$OUTPUT_DIR/all_cmz_tickets.json"
ANALYSIS_FILE="$OUTPUT_DIR/ticket_analysis.json"
LOG_FILE="$OUTPUT_DIR/fetch_log.txt"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Check authentication
if [ -z "$JIRA_TOKEN" ]; then
    echo "❌ Error: JIRA_API_TOKEN environment variable not set"
    echo "Please set: export JIRA_API_TOKEN='your-token-here'"
    exit 1
fi

# Create auth header
AUTH_HEADER=$(echo -n "$JIRA_EMAIL:$JIRA_TOKEN" | base64)

echo "🔍 Fetching ALL CMZ Jira tickets..." | tee "$LOG_FILE"
echo "📊 Base URL: $JIRA_BASE_URL" | tee -a "$LOG_FILE"
echo "👤 Email: $JIRA_EMAIL" | tee -a "$LOG_FILE"
echo "📁 Output: $OUTPUT_DIR" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Function to fetch tickets with pagination
fetch_cmz_tickets() {
    local start_at=0
    local max_results=50
    local total_fetched=0
    local all_tickets="[]"

    # Try different project identification patterns
    local jql_patterns=(
        "project = CMZ ORDER BY key ASC"
        "project = 'Cougar Mountain Zoo' ORDER BY key ASC"
        "summary ~ 'CMZ' OR summary ~ 'Zoo' OR summary ~ 'Cougar Mountain' ORDER BY key ASC"
        "description ~ 'CMZ' OR description ~ 'Zoo' OR description ~ 'Cougar Mountain' ORDER BY key ASC"
        "key ~ 'CMZ-' ORDER BY key ASC"
        "project in (CMZ, 'Cougar Mountain Zoo', PR003946) ORDER BY key ASC"
    )

    for jql_query in "${jql_patterns[@]}"; do
        echo "🔍 Trying JQL: $jql_query" | tee -a "$LOG_FILE"

        start_at=0
        local pattern_tickets="[]"

        while true; do
            # Build API URL with parameters
            local api_url="${JIRA_BASE_URL}/rest/api/3/search"
            local query_params="jql=$(echo "$jql_query" | jq -sRr @uri)&startAt=${start_at}&maxResults=${max_results}&fields=key,summary,description,status,issuetype,assignee,created,updated,priority,labels"

            echo "📡 Fetching page: startAt=$start_at, maxResults=$max_results" | tee -a "$LOG_FILE"

            # Make API request
            local response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
                -H "Authorization: Basic $AUTH_HEADER" \
                -H "Content-Type: application/json" \
                -H "Accept: application/json" \
                "$api_url?$query_params")

            # Extract HTTP status
            local http_status=$(echo "$response" | tail -1 | sed 's/HTTP_STATUS://')
            local response_body=$(echo "$response" | sed '$d')

            if [ "$http_status" -eq 200 ]; then
                # Parse response
                local issues=$(echo "$response_body" | jq -r '.issues')
                local total=$(echo "$response_body" | jq -r '.total')
                local issue_count=$(echo "$issues" | jq 'length')

                echo "✅ Success: Found $issue_count issues (total available: $total)" | tee -a "$LOG_FILE"

                if [ "$issue_count" -eq 0 ]; then
                    echo "🔚 No more issues for this pattern" | tee -a "$LOG_FILE"
                    break
                fi

                # Merge tickets
                pattern_tickets=$(echo "$pattern_tickets $issues" | jq -s 'add')
                total_fetched=$((total_fetched + issue_count))

                # Check if we've fetched all available
                if [ "$issue_count" -lt "$max_results" ]; then
                    echo "📄 Reached end of results for this pattern" | tee -a "$LOG_FILE"
                    break
                fi

                start_at=$((start_at + max_results))

            elif [ "$http_status" -eq 400 ]; then
                echo "⚠️ Bad Request (400): Invalid JQL - $jql_query" | tee -a "$LOG_FILE"
                break
            elif [ "$http_status" -eq 401 ]; then
                echo "❌ Unauthorized (401): Check authentication" | tee -a "$LOG_FILE"
                break
            elif [ "$http_status" -eq 403 ]; then
                echo "❌ Forbidden (403): Insufficient permissions" | tee -a "$LOG_FILE"
                break
            else
                echo "❌ HTTP Error $http_status for pattern: $jql_query" | tee -a "$LOG_FILE"
                echo "Response: $response_body" | tee -a "$LOG_FILE"
                break
            fi

            # Rate limiting
            sleep 0.5
        done

        # Merge with all tickets (removing duplicates by key)
        if [ "$(echo "$pattern_tickets" | jq 'length')" -gt 0 ]; then
            echo "📊 Pattern '$jql_query' found $(echo "$pattern_tickets" | jq 'length') tickets" | tee -a "$LOG_FILE"
            all_tickets=$(echo "$all_tickets $pattern_tickets" | jq -s 'add | unique_by(.key)')
            echo "📈 Total unique tickets so far: $(echo "$all_tickets" | jq 'length')" | tee -a "$LOG_FILE"
        fi

        echo "" | tee -a "$LOG_FILE"
    done

    echo "$all_tickets"
}

# Fetch all tickets
echo "🚀 Starting ticket fetch process..." | tee -a "$LOG_FILE"
ALL_TICKETS=$(fetch_cmz_tickets)

# Save raw tickets
echo "$ALL_TICKETS" > "$TICKETS_FILE"

# Analyze tickets
TOTAL_TICKETS=$(echo "$ALL_TICKETS" | jq 'length')
echo "" | tee -a "$LOG_FILE"
echo "🎯 **FETCH RESULTS:**" | tee -a "$LOG_FILE"
echo "📊 Total Unique Tickets: $TOTAL_TICKETS" | tee -a "$LOG_FILE"

if [ "$TOTAL_TICKETS" -gt 0 ]; then
    # Extract ticket keys
    echo "$ALL_TICKETS" | jq -r '.[].key' | head -20 | while read key; do
        echo "  • $key" | tee -a "$LOG_FILE"
    done

    if [ "$TOTAL_TICKETS" -gt 20 ]; then
        echo "  ... and $((TOTAL_TICKETS - 20)) more" | tee -a "$LOG_FILE"
    fi

    # Analyze by status
    echo "" | tee -a "$LOG_FILE"
    echo "📋 **Status Breakdown:**" | tee -a "$LOG_FILE"
    echo "$ALL_TICKETS" | jq -r 'group_by(.fields.status.name) | .[] | "\(.length) tickets: \(.[0].fields.status.name)"' | tee -a "$LOG_FILE"

    # Analyze by type
    echo "" | tee -a "$LOG_FILE"
    echo "🏷️ **Issue Type Breakdown:**" | tee -a "$LOG_FILE"
    echo "$ALL_TICKETS" | jq -r 'group_by(.fields.issuetype.name) | .[] | "\(.length) tickets: \(.[0].fields.issuetype.name)"' | tee -a "$LOG_FILE"

    # Save analysis
    cat > "$ANALYSIS_FILE" << EOF
{
    "fetch_timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "total_tickets": $TOTAL_TICKETS,
    "status_breakdown": $(echo "$ALL_TICKETS" | jq 'group_by(.fields.status.name) | map({status: .[0].fields.status.name, count: length})'),
    "type_breakdown": $(echo "$ALL_TICKETS" | jq 'group_by(.fields.issuetype.name) | map({type: .[0].fields.issuetype.name, count: length})'),
    "sample_keys": $(echo "$ALL_TICKETS" | jq '[.[].key] | .[0:10]')
}
EOF

    echo "✅ SUCCESS: Fetched $TOTAL_TICKETS CMZ tickets"
    echo "📄 Raw data: $TICKETS_FILE"
    echo "📊 Analysis: $ANALYSIS_FILE"
    echo "📋 Log: $LOG_FILE"

else
    echo "❌ No CMZ tickets found with any search pattern"
    echo "💡 Possible issues:"
    echo "  - Project key might be different"
    echo "  - Permissions might be restricted"
    echo "  - CMZ tickets might be in a different Jira instance"
    exit 1
fi