#!/bin/bash

# Systematic testing of Jira pagination to get ALL PR003946 tickets
# Using sequential reasoning to solve pagination issues

set -e

source .env.local
AUTH_HEADER=$(echo -n "${JIRA_EMAIL}:${JIRA_API_TOKEN}" | base64)
JIRA_BASE="https://nortal.atlassian.net"

echo "🔍 SYSTEMATIC JIRA PAGINATION TESTING"
echo "====================================="
echo ""

# Test 1: Higher maxResults to find API limits
echo "🧪 TEST 1: Higher maxResults (1000)"
RESPONSE1=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
    -H "Authorization: Basic ${AUTH_HEADER}" \
    -H "Accept: application/json" \
    "${JIRA_BASE}/rest/api/3/search/jql?jql=project%20%3D%20PR003946%20ORDER%20BY%20key%20ASC&maxResults=1000&fields=key,summary")

HTTP_STATUS1=$(echo "$RESPONSE1" | tail -1 | sed 's/HTTP_STATUS://')
RESPONSE_BODY1=$(echo "$RESPONSE1" | sed '$d')

if [ "$HTTP_STATUS1" = "200" ]; then
    echo "$RESPONSE_BODY1" > jira_data/test1_maxResults1000.json
    COUNT1=$(jq '.issues | length' jira_data/test1_maxResults1000.json)
    IS_LAST1=$(jq '.isLast' jira_data/test1_maxResults1000.json)

    echo "✅ HTTP 200 - Found $COUNT1 tickets"
    echo "🏁 Is Last: $IS_LAST1"

    if [ "$IS_LAST1" = "true" ]; then
        echo "🎉 ALL TICKETS FOUND IN ONE REQUEST!"
        jq -r '.issues[].key' jira_data/test1_maxResults1000.json > jira_data/all_tickets_final.txt
        FINAL_COUNT=$(wc -l < jira_data/all_tickets_final.txt)
        echo "📊 Total tickets: $FINAL_COUNT"
        echo "📋 Range: $(head -1 jira_data/all_tickets_final.txt) to $(tail -1 jira_data/all_tickets_final.txt)"
        exit 0
    else
        echo "⚠️ More tickets exist - need pagination"
        NEXT_TOKEN1=$(jq -r '.nextPageToken // empty' jira_data/test1_maxResults1000.json)
        echo "🔄 Next token: ${NEXT_TOKEN1}"
    fi
else
    echo "❌ HTTP $HTTP_STATUS1"
    echo "Response: $(echo "$RESPONSE_BODY1" | head -3)"
fi

echo ""

# Test 2: Try different pagination parameter names
if [ "$HTTP_STATUS1" = "200" ] && [ "$IS_LAST1" != "true" ]; then
    echo "🧪 TEST 2: Different pagination parameters"

    # Method A: pageToken parameter
    echo "Method A: pageToken parameter"
    RESPONSE2A=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
        -H "Authorization: Basic ${AUTH_HEADER}" \
        -H "Accept: application/json" \
        "${JIRA_BASE}/rest/api/3/search/jql?jql=project%20%3D%20PR003946%20ORDER%20BY%20key%20ASC&maxResults=100&fields=key,summary&pageToken=${NEXT_TOKEN1}")

    HTTP_STATUS2A=$(echo "$RESPONSE2A" | tail -1 | sed 's/HTTP_STATUS://')
    RESPONSE_BODY2A=$(echo "$RESPONSE2A" | sed '$d')

    if [ "$HTTP_STATUS2A" = "200" ]; then
        echo "$RESPONSE_BODY2A" > jira_data/test2a_pageToken.json
        COUNT2A=$(jq '.issues | length' jira_data/test2a_pageToken.json)
        echo "✅ pageToken method: $COUNT2A tickets"

        # Check if we got different tickets
        FIRST_TICKET2A=$(jq -r '.issues[0].key' jira_data/test2a_pageToken.json)
        FIRST_TICKET_ORIGINAL=$(jq -r '.issues[0].key' jira_data/test1_maxResults1000.json)

        if [ "$FIRST_TICKET2A" != "$FIRST_TICKET_ORIGINAL" ]; then
            echo "✅ PAGINATION WORKING! Got different tickets"
            WORKING_METHOD="pageToken"
        else
            echo "❌ Got same tickets - pagination not working"
        fi
    else
        echo "❌ pageToken method failed: HTTP $HTTP_STATUS2A"
    fi

    echo ""

    # Method B: nextPageToken parameter
    echo "Method B: nextPageToken parameter"
    RESPONSE2B=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
        -H "Authorization: Basic ${AUTH_HEADER}" \
        -H "Accept: application/json" \
        "${JIRA_BASE}/rest/api/3/search/jql?jql=project%20%3D%20PR003946%20ORDER%20BY%20key%20ASC&maxResults=100&fields=key,summary&nextPageToken=${NEXT_TOKEN1}")

    HTTP_STATUS2B=$(echo "$RESPONSE2B" | tail -1 | sed 's/HTTP_STATUS://')
    RESPONSE_BODY2B=$(echo "$RESPONSE2B" | sed '$d')

    if [ "$HTTP_STATUS2B" = "200" ]; then
        echo "$RESPONSE_BODY2B" > jira_data/test2b_nextPageToken.json
        COUNT2B=$(jq '.issues | length' jira_data/test2b_nextPageToken.json)
        echo "✅ nextPageToken method: $COUNT2B tickets"

        FIRST_TICKET2B=$(jq -r '.issues[0].key' jira_data/test2b_nextPageToken.json)
        if [ "$FIRST_TICKET2B" != "$FIRST_TICKET_ORIGINAL" ]; then
            echo "✅ PAGINATION WORKING! Got different tickets"
            WORKING_METHOD="nextPageToken"
        else
            echo "❌ Got same tickets - pagination not working"
        fi
    else
        echo "❌ nextPageToken method failed: HTTP $HTTP_STATUS2B"
    fi

    echo ""

    # Method C: URL encode the token
    echo "Method C: URL-encoded pageToken"
    ENCODED_TOKEN=$(echo "$NEXT_TOKEN1" | sed 's/+/%2B/g' | sed 's/\//%2F/g' | sed 's/=/%3D/g')
    RESPONSE2C=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
        -H "Authorization: Basic ${AUTH_HEADER}" \
        -H "Accept: application/json" \
        "${JIRA_BASE}/rest/api/3/search/jql?jql=project%20%3D%20PR003946%20ORDER%20BY%20key%20ASC&maxResults=100&fields=key,summary&pageToken=${ENCODED_TOKEN}")

    HTTP_STATUS2C=$(echo "$RESPONSE2C" | tail -1 | sed 's/HTTP_STATUS://')
    RESPONSE_BODY2C=$(echo "$RESPONSE2C" | sed '$d')

    if [ "$HTTP_STATUS2C" = "200" ]; then
        echo "$RESPONSE_BODY2C" > jira_data/test2c_encodedToken.json
        COUNT2C=$(jq '.issues | length' jira_data/test2c_encodedToken.json)
        echo "✅ URL-encoded method: $COUNT2C tickets"

        FIRST_TICKET2C=$(jq -r '.issues[0].key' jira_data/test2c_encodedToken.json)
        if [ "$FIRST_TICKET2C" != "$FIRST_TICKET_ORIGINAL" ]; then
            echo "✅ PAGINATION WORKING! Got different tickets"
            WORKING_METHOD="encodedPageToken"
        else
            echo "❌ Got same tickets - pagination not working"
        fi
    else
        echo "❌ URL-encoded method failed: HTTP $HTTP_STATUS2C"
    fi
fi

echo ""

# Test 3: Fallback to startAt pagination if token-based fails
if [ -z "$WORKING_METHOD" ]; then
    echo "🧪 TEST 3: Fallback to startAt pagination"

    RESPONSE3=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
        -H "Authorization: Basic ${AUTH_HEADER}" \
        -H "Accept: application/json" \
        "${JIRA_BASE}/rest/api/3/search/jql?jql=project%20%3D%20PR003946%20ORDER%20BY%20key%20ASC&startAt=100&maxResults=100&fields=key,summary")

    HTTP_STATUS3=$(echo "$RESPONSE3" | tail -1 | sed 's/HTTP_STATUS://')
    RESPONSE_BODY3=$(echo "$RESPONSE3" | sed '$d')

    if [ "$HTTP_STATUS3" = "200" ]; then
        echo "$RESPONSE_BODY3" > jira_data/test3_startAt.json
        COUNT3=$(jq '.issues | length' jira_data/test3_startAt.json)
        echo "✅ startAt method: $COUNT3 tickets"

        if [ "$COUNT3" -gt 0 ]; then
            FIRST_TICKET3=$(jq -r '.issues[0].key' jira_data/test3_startAt.json)
            FIRST_TICKET_ORIGINAL=$(jq -r '.issues[0].key' jira_data/test1_maxResults1000.json)

            if [ "$FIRST_TICKET3" != "$FIRST_TICKET_ORIGINAL" ]; then
                echo "✅ PAGINATION WORKING! Got different tickets"
                WORKING_METHOD="startAt"
            else
                echo "❌ Got same tickets - pagination not working"
            fi
        fi
    else
        echo "❌ startAt method failed: HTTP $HTTP_STATUS3"
    fi
fi

echo ""
echo "🎯 **TEST RESULTS:**"
if [ -n "$WORKING_METHOD" ]; then
    echo "✅ Working pagination method: $WORKING_METHOD"
    echo "📝 Ready to implement complete fetch using this method"
else
    echo "❌ No working pagination method found"
    echo "💡 May need to investigate Jira API documentation further"
fi

echo ""
echo "📁 Test files saved in jira_data/"
ls -la jira_data/test*.json