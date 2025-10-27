#!/bin/bash

# Test Jira API Access Systematically
# Following sequential reasoning approach to resolve API access

set -e

# Load environment
source .env.local

# Create auth header
AUTH_HEADER=$(echo -n "${JIRA_EMAIL}:${JIRA_API_TOKEN}" | base64)
JIRA_BASE="https://nortal.atlassian.net"

echo "🔍 Testing Jira API Access Systematically"
echo "=========================================="
echo "📧 Email: ${JIRA_EMAIL}"
echo "🏢 Base URL: ${JIRA_BASE}"
echo ""

# Test 1: Basic API connectivity with projects endpoint
echo "🧪 TEST 1: Basic API Connectivity"
echo "Endpoint: /rest/api/3/project"
PROJECT_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
    -H "Authorization: Basic ${AUTH_HEADER}" \
    -H "Accept: application/json" \
    "${JIRA_BASE}/rest/api/3/project")

HTTP_STATUS=$(echo "$PROJECT_RESPONSE" | tail -1 | sed 's/HTTP_STATUS://')
RESPONSE_BODY=$(echo "$PROJECT_RESPONSE" | sed '$d')

echo "HTTP Status: ${HTTP_STATUS}"
if [ "$HTTP_STATUS" = "200" ]; then
    echo "✅ Basic API access works"
    # Check if PR003946 exists
    if echo "$RESPONSE_BODY" | grep -q "PR003946"; then
        echo "✅ Project PR003946 found"
    else
        echo "⚠️ Project PR003946 not found in project list"
        echo "📋 Available projects:"
        echo "$RESPONSE_BODY" | grep -o '"key":"[^"]*"' | head -10
    fi
else
    echo "❌ Basic API access failed"
    echo "Response: $(echo "$RESPONSE_BODY" | head -3)"
    exit 1
fi

echo ""

# Test 2: Try to get a known ticket (PR003946-90 from documentation)
echo "🧪 TEST 2: Individual Ticket Access"
echo "Testing known ticket: PR003946-90"
TICKET_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
    -H "Authorization: Basic ${AUTH_HEADER}" \
    -H "Accept: application/json" \
    "${JIRA_BASE}/rest/api/3/issue/PR003946-90")

HTTP_STATUS=$(echo "$TICKET_RESPONSE" | tail -1 | sed 's/HTTP_STATUS://')
RESPONSE_BODY=$(echo "$TICKET_RESPONSE" | sed '$d')

echo "HTTP Status: ${HTTP_STATUS}"
if [ "$HTTP_STATUS" = "200" ]; then
    echo "✅ Individual ticket access works"
    TICKET_SUMMARY=$(echo "$RESPONSE_BODY" | grep -o '"summary":"[^"]*"' | head -1)
    echo "📋 Ticket summary: ${TICKET_SUMMARY}"
else
    echo "❌ Individual ticket access failed"
    echo "Response: $(echo "$RESPONSE_BODY" | head -3)"
fi

echo ""

# Test 3: Try different search API endpoints
echo "🧪 TEST 3: Search API Methods"

# Method A: POST to /rest/api/3/search with JSON payload
echo "Method A: POST /rest/api/3/search with JSON payload"
SEARCH_PAYLOAD='{"jql":"project = PR003946","startAt":0,"maxResults":10,"fields":["key","summary","status"]}'
SEARCH_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
    -X POST \
    -H "Authorization: Basic ${AUTH_HEADER}" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json" \
    -d "$SEARCH_PAYLOAD" \
    "${JIRA_BASE}/rest/api/3/search")

HTTP_STATUS=$(echo "$SEARCH_RESPONSE" | tail -1 | sed 's/HTTP_STATUS://')
RESPONSE_BODY=$(echo "$SEARCH_RESPONSE" | sed '$d')
echo "HTTP Status: ${HTTP_STATUS}"

if [ "$HTTP_STATUS" = "200" ]; then
    echo "✅ POST search method works!"
    TICKET_COUNT=$(echo "$RESPONSE_BODY" | grep -c '"key":' || echo "0")
    echo "📊 Found ${TICKET_COUNT} tickets"
    if [ "$TICKET_COUNT" -gt 0 ]; then
        echo "📋 Sample tickets:"
        echo "$RESPONSE_BODY" | grep -o '"key":"[^"]*"' | head -5
        # Save successful response
        echo "$RESPONSE_BODY" > jira_data/successful_search.json
        echo "💾 Full response saved to jira_data/successful_search.json"
    fi
    SEARCH_WORKING="true"
else
    echo "❌ POST search method failed"
    echo "Response: $(echo "$RESPONSE_BODY" | head -3)"
    SEARCH_WORKING="false"
fi

echo ""

# Test 4: If search worked, try pagination to get all tickets
if [ "$SEARCH_WORKING" = "true" ]; then
    echo "🧪 TEST 4: Paginated Search for All Tickets"
    ALL_TICKETS="[]"
    START_AT=0
    MAX_RESULTS=50
    TOTAL_FETCHED=0

    while true; do
        echo "📄 Fetching page: startAt=${START_AT}, maxResults=${MAX_RESULTS}"

        SEARCH_PAYLOAD="{\"jql\":\"project = PR003946 ORDER BY key ASC\",\"startAt\":${START_AT},\"maxResults\":${MAX_RESULTS},\"fields\":[\"key\",\"summary\",\"status\",\"issuetype\",\"description\"]}"

        PAGE_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
            -X POST \
            -H "Authorization: Basic ${AUTH_HEADER}" \
            -H "Content-Type: application/json" \
            -H "Accept: application/json" \
            -d "$SEARCH_PAYLOAD" \
            "${JIRA_BASE}/rest/api/3/search")

        HTTP_STATUS=$(echo "$PAGE_RESPONSE" | tail -1 | sed 's/HTTP_STATUS://')
        RESPONSE_BODY=$(echo "$PAGE_RESPONSE" | sed '$d')

        if [ "$HTTP_STATUS" = "200" ]; then
            TICKET_COUNT=$(echo "$RESPONSE_BODY" | grep -c '"key":' || echo "0")
            echo "✅ Found ${TICKET_COUNT} tickets on this page"

            if [ "$TICKET_COUNT" -eq 0 ]; then
                echo "🔚 No more tickets"
                break
            fi

            # Save this page
            echo "$RESPONSE_BODY" > "jira_data/page_${START_AT}.json"
            TOTAL_FETCHED=$((TOTAL_FETCHED + TICKET_COUNT))

            # Check if we got fewer results than requested (end of results)
            if [ "$TICKET_COUNT" -lt "$MAX_RESULTS" ]; then
                echo "📄 Reached end of results"
                break
            fi

            START_AT=$((START_AT + MAX_RESULTS))
            sleep 0.5  # Rate limiting

        else
            echo "❌ Pagination failed at startAt=${START_AT}"
            echo "Response: $(echo "$RESPONSE_BODY" | head -3)"
            break
        fi
    done

    echo ""
    echo "🎯 **FINAL RESULTS:**"
    echo "📊 Total tickets fetched: ${TOTAL_FETCHED}"

    if [ "$TOTAL_FETCHED" -gt 0 ]; then
        echo "✅ SUCCESS: Found all PR003946 tickets!"
        echo "📁 Data saved in jira_data/page_*.json files"

        # Create consolidated ticket list
        echo "📋 All ticket keys found:"
        find jira_data -name "page_*.json" -exec grep -ho '"key":"[^"]*"' {} \; | sort -u | sed 's/"key":"/ • /' | sed 's/"//'

    else
        echo "❌ No tickets found"
    fi

else
    echo "⚠️ Skipping pagination test - search method not working"
fi

echo ""
echo "🏁 API Testing Complete"
echo "📁 Results saved in jira_data/ directory"