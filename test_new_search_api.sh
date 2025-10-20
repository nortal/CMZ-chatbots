#!/bin/bash

# Test the new /rest/api/3/search/jql API endpoint
# Based on Atlassian migration guidelines

set -e

# Load environment
source .env.local

# Create auth header
AUTH_HEADER=$(echo -n "${JIRA_EMAIL}:${JIRA_API_TOKEN}" | base64)
JIRA_BASE="https://nortal.atlassian.net"

echo "🔍 Testing NEW Jira Search API: /rest/api/3/search/jql"
echo "======================================================="
echo ""

# Try different payload formats for the new API

# Method 1: Simple POST with JSON body (minimal)
echo "🧪 METHOD 1: Simple JSON payload"
PAYLOAD1='{"jql": "project = PR003946", "maxResults": 10}'
echo "Payload: ${PAYLOAD1}"

RESPONSE1=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
    -X POST \
    -H "Authorization: Basic ${AUTH_HEADER}" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json" \
    -d "$PAYLOAD1" \
    "${JIRA_BASE}/rest/api/3/search/jql")

HTTP_STATUS1=$(echo "$RESPONSE1" | tail -1 | sed 's/HTTP_STATUS://')
RESPONSE_BODY1=$(echo "$RESPONSE1" | sed '$d')

echo "HTTP Status: ${HTTP_STATUS1}"
if [ "$HTTP_STATUS1" = "200" ]; then
    echo "✅ Method 1 WORKS!"
    TICKET_COUNT=$(echo "$RESPONSE_BODY1" | grep -c '"key":' || echo "0")
    echo "📊 Found ${TICKET_COUNT} tickets"
    echo "$RESPONSE_BODY1" > jira_data/method1_success.json
else
    echo "❌ Method 1 failed"
    echo "Response: $(echo "$RESPONSE_BODY1" | head -3)"
fi

echo ""

# Method 2: Full structured payload
echo "🧪 METHOD 2: Full structured payload"
PAYLOAD2='{"jql": "project = PR003946 ORDER BY key ASC", "startAt": 0, "maxResults": 50, "fields": ["key", "summary", "status", "issuetype", "description"]}'
echo "Payload: ${PAYLOAD2}"

RESPONSE2=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
    -X POST \
    -H "Authorization: Basic ${AUTH_HEADER}" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json" \
    -d "$PAYLOAD2" \
    "${JIRA_BASE}/rest/api/3/search/jql")

HTTP_STATUS2=$(echo "$RESPONSE2" | tail -1 | sed 's/HTTP_STATUS://')
RESPONSE_BODY2=$(echo "$RESPONSE2" | sed '$d')

echo "HTTP Status: ${HTTP_STATUS2}"
if [ "$HTTP_STATUS2" = "200" ]; then
    echo "✅ Method 2 WORKS!"
    TICKET_COUNT=$(echo "$RESPONSE_BODY2" | grep -c '"key":' || echo "0")
    echo "📊 Found ${TICKET_COUNT} tickets"
    echo "$RESPONSE_BODY2" > jira_data/method2_success.json

    # Show sample tickets
    echo "📋 Sample tickets:"
    echo "$RESPONSE_BODY2" | grep -o '"key":"[^"]*"' | head -10 | sed 's/"key":"/ • /' | sed 's/"//'

else
    echo "❌ Method 2 failed"
    echo "Response: $(echo "$RESPONSE_BODY2" | head -3)"
fi

echo ""

# Method 3: Try GET method with URL parameters (fallback)
echo "🧪 METHOD 3: GET method with URL parameters"
JQL_ENCODED=$(echo "project = PR003946 ORDER BY key ASC" | sed 's/ /%20/g' | sed 's/=/%3D/g')
GET_URL="${JIRA_BASE}/rest/api/3/search/jql?jql=${JQL_ENCODED}&maxResults=10&fields=key,summary,status"

echo "URL: ${GET_URL}"

RESPONSE3=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
    -H "Authorization: Basic ${AUTH_HEADER}" \
    -H "Accept: application/json" \
    "$GET_URL")

HTTP_STATUS3=$(echo "$RESPONSE3" | tail -1 | sed 's/HTTP_STATUS://')
RESPONSE_BODY3=$(echo "$RESPONSE3" | sed '$d')

echo "HTTP Status: ${HTTP_STATUS3}"
if [ "$HTTP_STATUS3" = "200" ]; then
    echo "✅ Method 3 WORKS!"
    TICKET_COUNT=$(echo "$RESPONSE_BODY3" | grep -c '"key":' || echo "0")
    echo "📊 Found ${TICKET_COUNT} tickets"
    echo "$RESPONSE_BODY3" > jira_data/method3_success.json
else
    echo "❌ Method 3 failed"
    echo "Response: $(echo "$RESPONSE_BODY3" | head -3)"
fi

echo ""

# Find which method worked and use it for full fetch
if [ "$HTTP_STATUS1" = "200" ]; then
    WORKING_METHOD="1"
elif [ "$HTTP_STATUS2" = "200" ]; then
    WORKING_METHOD="2"
elif [ "$HTTP_STATUS3" = "200" ]; then
    WORKING_METHOD="3"
else
    WORKING_METHOD="none"
fi

if [ "$WORKING_METHOD" != "none" ]; then
    echo "🎯 Method ${WORKING_METHOD} worked - proceeding with full ticket fetch"
    echo ""

    # Use the working method to get ALL tickets with pagination
    echo "🚀 FULL TICKET FETCH - Method ${WORKING_METHOD}"
    START_AT=0
    MAX_RESULTS=100
    TOTAL_FETCHED=0

    while true; do
        echo "📄 Fetching page: startAt=${START_AT}"

        if [ "$WORKING_METHOD" = "1" ]; then
            PAYLOAD="{\"jql\": \"project = PR003946 ORDER BY key ASC\", \"startAt\": ${START_AT}, \"maxResults\": ${MAX_RESULTS}}"
            ENDPOINT="${JIRA_BASE}/rest/api/3/search/jql"
            METHOD="POST"
        elif [ "$WORKING_METHOD" = "2" ]; then
            PAYLOAD="{\"jql\": \"project = PR003946 ORDER BY key ASC\", \"startAt\": ${START_AT}, \"maxResults\": ${MAX_RESULTS}, \"fields\": [\"key\", \"summary\", \"status\", \"issuetype\", \"description\"]}"
            ENDPOINT="${JIRA_BASE}/rest/api/3/search/jql"
            METHOD="POST"
        elif [ "$WORKING_METHOD" = "3" ]; then
            JQL_ENCODED=$(echo "project = PR003946 ORDER BY key ASC" | sed 's/ /%20/g' | sed 's/=/%3D/g')
            ENDPOINT="${JIRA_BASE}/rest/api/3/search/jql?jql=${JQL_ENCODED}&startAt=${START_AT}&maxResults=${MAX_RESULTS}&fields=key,summary,status,issuetype,description"
            METHOD="GET"
        fi

        if [ "$METHOD" = "POST" ]; then
            PAGE_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
                -X POST \
                -H "Authorization: Basic ${AUTH_HEADER}" \
                -H "Content-Type: application/json" \
                -H "Accept: application/json" \
                -d "$PAYLOAD" \
                "$ENDPOINT")
        else
            PAGE_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
                -H "Authorization: Basic ${AUTH_HEADER}" \
                -H "Accept: application/json" \
                "$ENDPOINT")
        fi

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
            echo "$RESPONSE_BODY" > "jira_data/all_tickets_page_${START_AT}.json"
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
    echo "🎉 **COMPLETE SUCCESS!**"
    echo "📊 Total PR003946 tickets fetched: ${TOTAL_FETCHED}"
    echo "📁 Data saved in jira_data/all_tickets_page_*.json files"

    # Create consolidated list
    echo ""
    echo "📋 **ALL PR003946 TICKETS:**"
    find jira_data -name "all_tickets_page_*.json" -exec grep -ho '"key":"[^"]*"' {} \; | sort -u > jira_data/all_ticket_keys.txt
    cat jira_data/all_ticket_keys.txt | sed 's/"key":"/ • /' | sed 's/"//'

    FINAL_COUNT=$(cat jira_data/all_ticket_keys.txt | wc -l | xargs)
    echo ""
    echo "📊 **FINAL COUNT: ${FINAL_COUNT} unique tickets**"

else
    echo "❌ None of the methods worked"
    echo "🔍 Need to investigate further API changes"
fi