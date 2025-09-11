#!/bin/bash

# Simple script to update Jira tickets
# This version focuses just on the working parts we identified

set -e

# Check if JIRA_API_TOKEN is set
if [ -z "$JIRA_API_TOKEN" ]; then
    echo "Error: JIRA_API_TOKEN environment variable is not set"
    exit 1
fi

JIRA_BASE_URL="https://nortal.atlassian.net"
JIRA_EMAIL="kc.stegbauer@nortal.com"

# Create base64 encoded credentials for Basic Auth
JIRA_CREDENTIALS=$(echo -n "$JIRA_EMAIL:$JIRA_API_TOKEN" | base64)

echo "🎯 Updating Jira tickets..."

# Test API connectivity first
echo "🔌 Testing API connectivity..."
test_response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
    -H "Authorization: Basic $JIRA_CREDENTIALS" \
    -H "Content-Type: application/json" \
    "$JIRA_BASE_URL/rest/api/3/myself")

test_http_status=$(echo "$test_response" | grep "HTTP_STATUS:" | cut -d: -f2)

if [ "$test_http_status" != "200" ]; then
    echo "❌ API connectivity test failed"
    exit 1
fi

echo "✅ API connectivity confirmed"

# Function to add a simple comment
add_simple_comment() {
    local ticket_id=$1
    local comment_text="$2"
    
    echo "💬 Adding comment to $ticket_id..."
    
    # Create temp file with simple comment
    local temp_file=$(mktemp)
    cat > "$temp_file" <<EOF
{
    "body": {
        "type": "doc",
        "version": 1,
        "content": [
            {
                "type": "paragraph",
                "content": [
                    {
                        "type": "text",
                        "text": "$comment_text"
                    }
                ]
            }
        ]
    }
}
EOF
    
    local response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
        -H "Authorization: Basic $JIRA_CREDENTIALS" \
        -H "Content-Type: application/json" \
        --data @"$temp_file" \
        "$JIRA_BASE_URL/rest/api/3/issue/$ticket_id/comment")
    
    local http_status=$(echo "$response" | grep "HTTP_STATUS:" | cut -d: -f2)
    
    rm -f "$temp_file"
    
    if [ "$http_status" = "201" ]; then
        echo "✅ Successfully added comment to $ticket_id"
    else
        echo "❌ Failed to add comment to $ticket_id (HTTP $http_status)"
        echo "Response: $(echo "$response" | sed '/HTTP_STATUS:/d')"
    fi
}

# Function to transition status
transition_status() {
    local ticket_id=$1
    
    echo "📋 Transitioning $ticket_id to In Progress..."
    
    local response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
        -H "Authorization: Basic $JIRA_CREDENTIALS" \
        -H "Content-Type: application/json" \
        --data '{"transition":{"id":"21"}}' \
        "$JIRA_BASE_URL/rest/api/3/issue/$ticket_id/transitions")
    
    local http_status=$(echo "$response" | grep "HTTP_STATUS:" | cut -d: -f2)
    
    if [ "$http_status" = "204" ]; then
        echo "✅ Successfully transitioned $ticket_id"
    else
        echo "❌ Failed to transition $ticket_id (HTTP $http_status)"
        echo "Response: $(echo "$response" | sed '/HTTP_STATUS:/d')"
    fi
}

# Update PR003946-87
echo "📌 Processing PR003946-87..."
transition_status "PR003946-87"
sleep 2
add_simple_comment "PR003946-87" "COMPLETED - Password policy validation implementation. Fixed duplicate ValidationError handlers. Enhanced auth controller with error_code=invalid_password. Integration test passing. PR https://github.com/nortal/CMZ-chatbots/pull/19 MERGED."

echo

# Update PR003946-67  
echo "📌 Processing PR003946-67..."
add_simple_comment "PR003946-67" "COMPLETED - Cascade delete DynamoDB connection fix. Modified cascade delete command for idempotent DELETE operations. Returns 204 for non-existent entities. Integration test passing. PR https://github.com/nortal/CMZ-chatbots/pull/19 MERGED."

echo
echo "🎉 Updates completed!"
echo "📋 Check: https://nortal.atlassian.net/browse/PR003946-87"
echo "📋 Check: https://nortal.atlassian.net/browse/PR003946-67"