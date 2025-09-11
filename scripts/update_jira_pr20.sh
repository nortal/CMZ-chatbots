#!/bin/bash

# JIRA Update Script for PR #20 - Missing API Endpoints Implementation
# This script adds comments to relevant tickets for our new implementation

set -e

# Source local environment file if it exists
if [ -f ".env.local" ]; then
    echo "📋 Loading credentials from .env.local..."
    source .env.local
elif [ -f "../.env.local" ]; then
    echo "📋 Loading credentials from ../.env.local..."
    source ../.env.local
fi

# Configuration
JIRA_BASE_URL="https://nortal.atlassian.net"
PROJECT_KEY="PR003946"

# Check for required environment variables
if [[ -z "$JIRA_EMAIL" || -z "$JIRA_API_TOKEN" ]]; then
    echo "❌ Error: Required environment variables not set"
    echo ""
    echo "Please run: ./scripts/setup_jira_credentials.sh"
    echo "Or manually set:"
    echo "  export JIRA_EMAIL='your.email@nortal.com'"
    echo "  export JIRA_API_TOKEN='your_jira_api_token'"
    exit 1
fi

# Create auth header
AUTH_HEADER=$(echo -n "$JIRA_EMAIL:$JIRA_API_TOKEN" | base64)

echo "🚀 Updating JIRA tickets for PR #20 - Missing API Endpoints Implementation"
echo "======================================================================="
echo ""

# PR #20 Implementation Details
PR_URL="https://github.com/nortal/CMZ-chatbots/pull/20"
IMPLEMENTATION_DATE="2025-09-11"
IMPLEMENTATION_DETAILS="Implemented 6 missing API endpoint groups with comprehensive AI conversation system:
1. Animal Details Enhancement - Extended profiles with descriptions and metadata
2. System Health Monitoring - Multi-component diagnostics with DynamoDB connectivity
3. Feature Flags Management - Dynamic rollout controls for 5 chatbot capabilities  
4. Knowledge Management CRUD - Educational content system with validation
5. Media Management - Metadata handling with type detection and soft-delete
6. AI Conversation Engine - Personality-based responses for Simba (Lion) and Koda (Bear) with keyword-driven contextual replies

All endpoints tested via comprehensive cURL validation. Addressed Copilot and GitHub Advanced Security review feedback. Production-ready with Docker workflow."

# Function to add comment to a JIRA ticket
add_comment_to_ticket() {
    local ticket_id=$1
    local specific_implementation=$2
    local comment_body="✅ **PR #20 Implementation Complete**

**MR**: $PR_URL
**Date**: $IMPLEMENTATION_DATE  
**Specific Implementation**: $specific_implementation

**Status**: Functionality verified via API testing. Ready for production deployment.
**Review**: Copilot and GitHub Advanced Security feedback addressed."

    echo "🎫 Adding comment to $ticket_id..."
    
    # Use jq to properly escape the JSON and handle special characters
    local json_payload=$(jq -n \
        --arg comment "$comment_body" \
        '{
            body: {
                type: "doc",
                version: 1,
                content: [
                    {
                        type: "paragraph",
                        content: [
                            {
                                type: "text",
                                text: $comment
                            }
                        ]
                    }
                ]
            }
        }')

    local response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
        -X POST \
        -H "Authorization: Basic $AUTH_HEADER" \
        -H "Content-Type: application/json" \
        -d "$json_payload" \
        "$JIRA_BASE_URL/rest/api/3/issue/$ticket_id/comment")

    local http_status=$(echo "$response" | tail -n1 | cut -d: -f2)
    local response_body=$(echo "$response" | head -n -1)

    if [[ "$http_status" == "201" ]]; then
        echo "✅ Successfully added comment to $ticket_id"
    else
        echo "❌ Failed to add comment to $ticket_id (HTTP $http_status)"
        echo "Response: $response_body"
        echo "Debug - JSON payload:"
        echo "$json_payload"
    fi
    echo ""
}

# Get comment message from command line argument or use default
if [ "$1" == "comment" ] && [ ! -z "$2" ]; then
    IMPLEMENTATION_DETAILS="$2"
fi

echo "💬 Adding comments for PR #20 implementation..."
echo ""

# Add ticket-specific comments based on actual implementation
echo "💬 Adding specific implementation comments..."
echo ""

add_comment_to_ticket "PR003946-90" "Enhanced error handling schema - Implemented consistent Error response objects with code/message/details structure across all 6 new endpoint groups. All endpoints now return standardized error responses for validation failures, missing resources, and system errors."

add_comment_to_ticket "PR003946-72" "Authentication system integration - System health monitoring endpoint (/system_health) includes authentication status checks and validates JWT token processing capabilities. Integrated with existing auth patterns for protected endpoint access."

add_comment_to_ticket "PR003946-74" "Data consistency validation - Implemented comprehensive data validation in Knowledge Management CRUD and Media Management endpoints. All operations validate entity relationships and prevent orphaned records through foreign key checks."

add_comment_to_ticket "PR003946-71" "JWT token validation - Enhanced system health monitoring includes JWT processing validation and token verification status. Authentication middleware properly validates tokens on protected endpoints with detailed error responses."

add_comment_to_ticket "PR003946-69" "ID generation standardization - Implemented UUID-based ID generation with entity-specific prefixes across all new endpoints (knowledge items, media objects, conversation turns). Consistent ID patterns: 'know_*', 'media_*', 'turn_*' formats."

add_comment_to_ticket "PR003946-66" "Soft delete implementation - Media Management and Knowledge Management endpoints implement soft-delete semantics with 'deleted' boolean flags. List operations properly filter soft-deleted items, maintaining data integrity while supporting recovery workflows."

echo "🎉 PR #20 JIRA integration complete!"
echo "📊 Updated 6 tickets with specific implementation details"
echo "🔗 PR URL: $PR_URL"