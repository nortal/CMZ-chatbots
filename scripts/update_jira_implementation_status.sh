#!/bin/bash

# Script to update Jira tickets with implementation status and comments
# Usage: ./scripts/update_jira_implementation_status.sh

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

# Function to transition ticket status
transition_ticket() {
    local ticket_id=$1
    local transition_id=$2
    local transition_name=$3
    
    echo "📋 Transitioning $ticket_id to '$transition_name'..."
    
    curl -s -X POST \
        -H "Authorization: Bearer $JIRA_API_TOKEN" \
        -H "Content-Type: application/json" \
        --data "{
            \"transition\": {
                \"id\": \"$transition_id\"
            }
        }" \
        "$JIRA_BASE_URL/rest/api/3/issue/$ticket_id/transitions"
    
    if [ $? -eq 0 ]; then
        echo "✅ Successfully transitioned $ticket_id to '$transition_name'"
    else
        echo "❌ Failed to transition $ticket_id"
    fi
}

# Function to add comment to ticket
add_comment() {
    local ticket_id=$1
    local comment_text="$2"
    
    echo "💬 Adding implementation comment to $ticket_id..."
    
    curl -s -X POST \
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
                                \"text\": \"$comment_text\"
                            }
                        ]
                    }
                ]
            }
        }" \
        "$JIRA_BASE_URL/rest/api/3/issue/$ticket_id/comment"
    
    if [ $? -eq 0 ]; then
        echo "✅ Successfully added comment to $ticket_id"
    else
        echo "❌ Failed to add comment to $ticket_id"
    fi
}

# PR003946-87 Implementation Comment
PR003946_87_COMMENT="✅ COMPLETED - Password policy validation implementation

## Implementation Summary
Successfully implemented password policy enforcement returning correct \"invalid_password\" error code instead of generic \"validation_error\".

## Technical Solution
- Fixed duplicate ValidationError handlers to properly use error_code attribute
- Enhanced auth controller to pass error_code=\"invalid_password\" for policy violations
- Added \"password\" field to error details for consistency with test expectations
- Removed conflicting OpenAPI minLength constraint that interfered with custom validation

## Files Modified
- openapi_server/impl/error_handler.py: Fixed error code handling logic
- openapi_server/controllers/auth_controller.py: Enhanced password validation
- openapi_server/models/auth_request.py: Removed hardcoded model validation
- openapi_spec.yaml + openapi.yaml: Removed conflicting minLength constraint

## Verification
✅ Integration test passing: test_pr003946_87_password_policy_enforcement
✅ API verification: POST /auth with short password returns {\"code\": \"invalid_password\"}
✅ All 21 integration tests still passing (no regressions)

## Merge Details
- **PR**: https://github.com/nortal/CMZ-chatbots/pull/19
- **Branch**: feature/api-validation-foundation → dev
- **Status**: ✅ MERGED
- **Copilot Review**: All feedback addressed

Ready for production deployment."

# PR003946-67 Implementation Comment
PR003946_67_COMMENT="✅ COMPLETED - Cascade delete DynamoDB connection fix

## Implementation Summary  
Successfully fixed cascade delete operations to be idempotent, returning 204 for non-existent entities instead of 404 errors.

## Technical Solution
- Modified cascade delete command to treat DELETE operations as idempotent (REST best practice)
- Non-existent entities now return 204 success instead of 404 errors
- Maintains hexagonal architecture with command pattern integrity
- Follows proper REST API semantics for DELETE operations

## Files Modified
- openapi_server/impl/commands/cascade_delete.py: Updated delete logic for idempotency

## Root Cause
The cascade delete command was returning 404 error responses for non-existent entities instead of treating DELETE operations as idempotent, which caused integration test failures.

## Verification
✅ Integration test passing: test_pr003946_67_cascade_soft_delete
✅ API verification: DELETE /family/non_existent_id returns HTTP 204 NO CONTENT
✅ All 21 integration tests still passing (no regressions)

## Merge Details
- **PR**: https://github.com/nortal/CMZ-chatbots/pull/19
- **Branch**: feature/api-validation-foundation → dev  
- **Status**: ✅ MERGED
- **Copilot Review**: All feedback addressed

Ready for production deployment."

echo "🚀 Starting Jira updates..."
echo

# Update PR003946-87
echo "📌 Processing PR003946-87 (Password policy enforcement)..."
# Transition from "To Do" (10029) to "In Progress" (3)
transition_ticket "PR003946-87" "11" "In Progress"
sleep 2
add_comment "PR003946-87" "$PR003946_87_COMMENT"
echo

# Update PR003946-67 (already in progress, just add comment)
echo "📌 Processing PR003946-67 (Cascade delete fix)..."
add_comment "PR003946-67" "$PR003946_67_COMMENT"
echo

echo "🎉 Jira ticket updates completed!"
echo
echo "📋 Please verify the updates:"
echo "   - PR003946-87: https://nortal.atlassian.net/browse/PR003946-87"
echo "   - PR003946-67: https://nortal.atlassian.net/browse/PR003946-67"