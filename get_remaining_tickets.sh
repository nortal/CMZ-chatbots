#!/bin/bash

source .env.local
AUTH_HEADER=$(echo -n "${JIRA_EMAIL}:${JIRA_API_TOKEN}" | base64)

echo "Fetching remaining PR003946 tickets (page 2)..."

NEXT_TOKEN="Cjhpc3N1ZUtleSZpc3N1ZUtleSZPUkRFUl9BU0MjU3RyaW5nJlVGSXdNRE01TkRZPSVJbnQmTVRNdxBkGLjK0auUMyIjcHJvamVjdCA9IFBSMDAzOTQ2IE9SREVSIEJZIGtleSBBU0M="

curl -s -H "Authorization: Basic ${AUTH_HEADER}" \
     "https://nortal.atlassian.net/rest/api/3/search/jql?jql=project%20%3D%20PR003946%20ORDER%20BY%20key%20ASC&maxResults=100&fields=key,summary&pageToken=${NEXT_TOKEN}" \
     > jira_data/second_100_tickets.json

if [ -f "jira_data/second_100_tickets.json" ]; then
    TICKET_COUNT=$(jq '.issues | length' jira_data/second_100_tickets.json 2>/dev/null || echo "0")
    IS_LAST=$(jq '.isLast' jira_data/second_100_tickets.json 2>/dev/null || echo "true")

    echo "✅ Found ${TICKET_COUNT} tickets on second page"
    echo "🏁 Is last page: ${IS_LAST}"

    if [ "$TICKET_COUNT" -gt 0 ]; then
        echo ""
        echo "📋 Additional tickets:"
        jq -r '.issues[].key' jira_data/second_100_tickets.json | sort -V > jira_data/second_page_tickets.txt
        cat jira_data/second_page_tickets.txt

        # Combine with first page
        cat jira_data/all_tickets_list.txt jira_data/second_page_tickets.txt | sort -V > jira_data/combined_tickets_list.txt

        TOTAL_COUNT=$(wc -l < jira_data/combined_tickets_list.txt | xargs)
        echo ""
        echo "📊 Total tickets across both pages: ${TOTAL_COUNT}"

        echo ""
        echo "🎯 COMPLETE TICKET LIST:"
        cat jira_data/combined_tickets_list.txt

        if [ "$IS_LAST" = "true" ]; then
            echo ""
            echo "✅ ALL PR003946 TICKETS SUCCESSFULLY FETCHED!"
            echo "📁 Complete list saved to: jira_data/combined_tickets_list.txt"
        else
            echo ""
            echo "⚠️ More pages may exist"
        fi
    fi
fi