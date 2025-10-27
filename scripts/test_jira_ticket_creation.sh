#!/bin/bash

# Test script for creating a single Jira ticket with proper authentication

# Load environment variables
source .env.local

# Configuration
JIRA_BASE_URL="https://nortal.atlassian.net"
JIRA_PROJECT="CMZ"

echo "Testing Jira ticket creation..."
echo "Using email: $JIRA_EMAIL"

# Create a simple test ticket
curl -v \
    -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{
        "fields": {
            "project": {
                "key": "CMZ"
            },
            "summary": "[TEST] Chat Epic Test Ticket",
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Test ticket for chat epic creation"
                            }
                        ]
                    }
                ]
            },
            "issuetype": {
                "name": "Task"
            },
            "customfield_10225": {
                "value": "Billable"
            }
        }
    }' \
    "$JIRA_BASE_URL/rest/api/3/issue" 2>&1 | tail -20