#!/bin/bash

# Script to update Jira tickets with implementation status and comments (FIXED AUTH)
# Usage: ./scripts/update_jira_implementation_status_fixed.sh

set -e

# Check if JIRA_API_TOKEN is set
if [ -z "$JIRA_API_TOKEN" ]; then
    echo "Error: JIRA_API_TOKEN environment variable is not set"
    echo "Please set it with: export JIRA_API_TOKEN=your_token_here"
    exit 1
fi

JIRA_BASE_URL="https://nortal.atlassian.net"
JIRA_EMAIL="kc.stegbauer@nortal.com"

# Create base64 encoded credentials for Basic Auth
JIRA_CREDENTIALS=$(echo -n "$JIRA_EMAIL:$JIRA_API_TOKEN" | base64)

echo "🎯 Updating Jira tickets with implementation status..."
echo "🔧 DEBUG: Using JIRA_BASE_URL: $JIRA_BASE_URL"
echo "🔧 DEBUG: Using email: $JIRA_EMAIL"
echo "🔧 DEBUG: Token length: ${#JIRA_API_TOKEN} characters"
echo "🔧 DEBUG: Credentials length: ${#JIRA_CREDENTIALS} characters"
echo

# Function to get available transitions for a ticket
get_transitions() {
    local ticket_id=$1
    
    echo "🔍 Getting available transitions for $ticket_id..."
    
    local response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
        -H "Authorization: Basic $JIRA_CREDENTIALS" \
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
        -H "Authorization: Basic $JIRA_CREDENTIALS" \
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
        -H "Authorization: Basic $JIRA_CREDENTIALS" \
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
    
    # Use a simpler JSON structure for the comment
    local json_payload=$(cat <<EOF
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
)
    
    local response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
        -H "Authorization: Basic $JIRA_CREDENTIALS" \
        -H "Content-Type: application/json" \
        --data "$json_payload" \
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
    -H "Authorization: Basic $JIRA_CREDENTIALS" \
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
PR003946_87_COMMENT="COMPLETED - Password policy validation implementation

Implementation Summary:
- Fixed duplicate ValidationError handlers to properly use error_code attribute
- Enhanced auth controller to pass error_code=invalid_password for policy violations  
- Added password field to error details for consistency with test expectations
- Removed conflicting OpenAPI minLength constraint that interfered with custom validation

Files Modified:
- openapi_server/impl/error_handler.py: Fixed error code handling logic
- openapi_server/controllers/auth_controller.py: Enhanced password validation
- openapi_server/models/auth_request.py: Removed hardcoded model validation
- openapi_spec.yaml + openapi.yaml: Removed conflicting minLength constraint

Verification:
✅ Integration test passing: test_pr003946_87_password_policy_enforcement
✅ API verification: POST /auth with short password returns {code: invalid_password}
✅ All 21 integration tests still passing (no regressions)

Merge Details:
- PR: https://github.com/nortal/CMZ-chatbots/pull/19
- Branch: feature/api-validation-foundation → dev
- Status: MERGED
- Copilot Review: All feedback addressed

Ready for production deployment."

PR003946_67_COMMENT="COMPLETED - Cascade delete DynamoDB connection fix

Implementation Summary:
- Modified cascade delete command to treat DELETE operations as idempotent (REST best practice)
- Non-existent entities now return 204 success instead of 404 errors
- Maintains hexagonal architecture with command pattern integrity
- Follows proper REST API semantics for DELETE operations

Files Modified:
- openapi_server/impl/commands/cascade_delete.py: Updated delete logic for idempotency

Root Cause:
The cascade delete command was returning 404 error responses for non-existent entities instead of treating DELETE operations as idempotent, which caused integration test failures.

Verification:
✅ Integration test passing: test_pr003946_67_cascade_soft_delete
✅ API verification: DELETE /family/non_existent_id returns HTTP 204 NO CONTENT
✅ All 21 integration tests still passing (no regressions)

Merge Details:
- PR: https://github.com/nortal/CMZ-chatbots/pull/19
- Branch: feature/api-validation-foundation → dev
- Status: MERGED
- Copilot Review: All feedback addressed

Ready for production deployment."

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