#!/bin/bash

# Script to update Jira tickets with implementation status and comments (DEBUG VERSION)
# Usage: ./scripts/update_jira_implementation_status_debug.sh

set -e

# Check if JIRA_API_TOKEN is set
if [ -z "$JIRA_API_TOKEN" ]; then
    echo "Error: JIRA_API_TOKEN environment variable is not set"
    echo "Please set it with: export JIRA_API_TOKEN=your_token_here"
    exit 1
fi

JIRA_BASE_URL="https://nortal.atlassian.net"
JIRA_EMAIL="kc.stegbauer@nortal.com"

echo "🎯 Updating Jira tickets with implementation status..."
echo "🔧 DEBUG: Using JIRA_BASE_URL: $JIRA_BASE_URL"
echo "🔧 DEBUG: Token length: ${#JIRA_API_TOKEN} characters"
echo

# Function to get available transitions for a ticket
get_transitions() {
    local ticket_id=$1
    
    echo "🔍 Getting available transitions for $ticket_id..."
    
    local response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
        -H "Authorization: Bearer $JIRA_API_TOKEN" \
        -H "Content-Type: application/json" \
        "$JIRA_BASE_URL/rest/api/3/issue/$ticket_id/transitions")
    
    local http_status=$(echo "$response" | grep "HTTP_STATUS:" | cut -d: -f2)
    local body=$(echo "$response" | sed '/HTTP_STATUS:/d')
    
    echo "🔧 DEBUG: HTTP Status: $http_status"
    echo "🔧 DEBUG: Response body: $body"
    echo
    
    if [ "$http_status" != "200" ]; then
        echo "❌ Failed to get transitions for $ticket_id"
        return 1
    fi
    
    echo "✅ Available transitions retrieved for $ticket_id"
    return 0
}

# Function to get current ticket status
get_ticket_status() {
    local ticket_id=$1
    
    echo "📋 Getting current status for $ticket_id..."
    
    local response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
        -H "Authorization: Bearer $JIRA_API_TOKEN" \
        -H "Content-Type: application/json" \
        "$JIRA_BASE_URL/rest/api/3/issue/$ticket_id?fields=status")
    
    local http_status=$(echo "$response" | grep "HTTP_STATUS:" | cut -d: -f2)
    local body=$(echo "$response" | sed '/HTTP_STATUS:/d')
    
    echo "🔧 DEBUG: HTTP Status: $http_status"
    echo "🔧 DEBUG: Response body: $body"
    echo
    
    if [ "$http_status" != "200" ]; then
        echo "❌ Failed to get status for $ticket_id"
        return 1
    fi
    
    echo "✅ Current status retrieved for $ticket_id"
    return 0
}

# Function to transition ticket status
transition_ticket() {
    local ticket_id=$1
    local transition_id=$2
    local transition_name=$3
    
    echo "📋 Transitioning $ticket_id to '$transition_name' (transition ID: $transition_id)..."
    
    local response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
        -H "Authorization: Bearer $JIRA_API_TOKEN" \
        -H "Content-Type: application/json" \
        --data "{
            \"transition\": {
                \"id\": \"$transition_id\"
            }
        }" \
        "$JIRA_BASE_URL/rest/api/3/issue/$ticket_id/transitions")
    
    local http_status=$(echo "$response" | grep "HTTP_STATUS:" | cut -d: -f2)
    local body=$(echo "$response" | sed '/HTTP_STATUS:/d')
    
    echo "🔧 DEBUG: HTTP Status: $http_status"
    echo "🔧 DEBUG: Response body: $body"
    echo
    
    if [ "$http_status" = "204" ] || [ "$http_status" = "200" ]; then
        echo "✅ Successfully transitioned $ticket_id to '$transition_name'"
        return 0
    else
        echo "❌ Failed to transition $ticket_id (HTTP $http_status)"
        return 1
    fi
}

# Function to add comment to ticket
add_comment() {
    local ticket_id=$1
    local comment_text="$2"
    
    echo "💬 Adding implementation comment to $ticket_id..."
    echo "🔧 DEBUG: Comment length: ${#comment_text} characters"
    
    # Escape quotes and newlines for JSON
    local escaped_comment=$(echo "$comment_text" | sed 's/"/\\"/g' | sed ':a;N;$!ba;s/\n/\\n/g')
    
    local response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
        -H "Authorization: Bearer $JIRA_API_TOKEN" \
        -H "Content-Type: application/json" \
        --data "{
            \"body\": {
                \"type\": \"doc\",
                \"version\": 1,
                \"content\": [
                    {
                        \"type\": \"paragraph\",
                        \"content\": [
                            {
                                \"type\": \"text\",
                                \"text\": \"$escaped_comment\"
                            }
                        ]
                    }
                ]
            }
        }" \
        "$JIRA_BASE_URL/rest/api/3/issue/$ticket_id/comment")
    
    local http_status=$(echo "$response" | grep "HTTP_STATUS:" | cut -d: -f2)
    local body=$(echo "$response" | sed '/HTTP_STATUS:/d')
    
    echo "🔧 DEBUG: HTTP Status: $http_status"
    echo "🔧 DEBUG: Response body: $body"
    echo
    
    if [ "$http_status" = "201" ] || [ "$http_status" = "200" ]; then
        echo "✅ Successfully added comment to $ticket_id"
        return 0
    else
        echo "❌ Failed to add comment to $ticket_id (HTTP $http_status)"
        return 1
    fi
}

# Test API connectivity first
echo "🔌 Testing API connectivity..."
test_response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
    -H "Authorization: Bearer $JIRA_API_TOKEN" \
    -H "Content-Type: application/json" \
    "$JIRA_BASE_URL/rest/api/3/myself")

test_http_status=$(echo "$test_response" | grep "HTTP_STATUS:" | cut -d: -f2)
test_body=$(echo "$test_response" | sed '/HTTP_STATUS:/d')

echo "🔧 DEBUG: API Test HTTP Status: $test_http_status"
echo "🔧 DEBUG: API Test Response: $test_body"
echo

if [ "$test_http_status" != "200" ]; then
    echo "❌ API connectivity test failed. Check your JIRA_API_TOKEN."
    exit 1
fi

echo "✅ API connectivity confirmed"
echo

# Short implementation comments (to avoid JSON issues)
PR003946_87_COMMENT="COMPLETED - Password policy validation implementation. Fixed duplicate ValidationError handlers to properly use error_code attribute. Enhanced auth controller to pass error_code=invalid_password for policy violations. Integration test passing: test_pr003946_87_password_policy_enforcement. PR: https://github.com/nortal/CMZ-chatbots/pull/19 MERGED."

PR003946_67_COMMENT="COMPLETED - Cascade delete DynamoDB connection fix. Modified cascade delete command to treat DELETE operations as idempotent (REST best practice). Non-existent entities now return 204 success instead of 404 errors. Integration test passing: test_pr003946_67_cascade_soft_delete. PR: https://github.com/nortal/CMZ-chatbots/pull/19 MERGED."

echo "🚀 Starting Jira updates..."
echo

# Update PR003946-87
echo "📌 Processing PR003946-87 (Password policy enforcement)..."
get_ticket_status "PR003946-87"
get_transitions "PR003946-87"

# Try to transition to In Progress - try common transition IDs
echo "🔄 Attempting transition to In Progress..."
transition_ticket "PR003946-87" "11" "In Progress" || \
transition_ticket "PR003946-87" "21" "In Progress" || \
transition_ticket "PR003946-87" "31" "In Progress" || \
transition_ticket "PR003946-87" "4" "In Progress" || \
echo "⚠️  Could not determine correct transition ID. Skipping status change."

sleep 2
add_comment "PR003946-87" "$PR003946_87_COMMENT"
echo

# Update PR003946-67 (already in progress, just add comment)
echo "📌 Processing PR003946-67 (Cascade delete fix)..."
get_ticket_status "PR003946-67"
add_comment "PR003946-67" "$PR003946_67_COMMENT"
echo

echo "🎉 Jira ticket updates completed!"
echo
echo "📋 Please verify the updates:"
echo "   - PR003946-87: https://nortal.atlassian.net/browse/PR003946-87"
echo "   - PR003946-67: https://nortal.atlassian.net/browse/PR003946-67"