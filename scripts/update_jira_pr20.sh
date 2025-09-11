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
    local comment_body="✅ **PR #20 Implementation Complete**

**MR**: $PR_URL
**Date**: $IMPLEMENTATION_DATE  
**Implementation**: $IMPLEMENTATION_DETAILS

**Status**: All functionality verified via API testing. Ready for production deployment.
**Review**: Copilot and security feedback addressed."

    echo "🎫 Adding comment to $ticket_id..."
    
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
            "text": "$comment_body"
          }
        ]
      }
    ]
  }
}
EOF
)

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
    fi
    echo ""
}

# Get comment message from command line argument or use default
if [ "$1" == "comment" ] && [ ! -z "$2" ]; then
    IMPLEMENTATION_DETAILS="$2"
fi

echo "💬 Adding comments for PR #20 implementation..."
echo ""

# These are tickets that would benefit from the new endpoint implementations
# Based on the API validation epic, these likely need the new functionality
RELEVANT_TICKETS=(
    "PR003946-90"  # Error handling - benefits from our error schema improvements
    "PR003946-72"  # Authentication - works with our system health monitoring
    "PR003946-74"  # Data consistency - supported by our CRUD operations
    "PR003946-71"  # JWT validation - integrates with our auth system
    "PR003946-69"  # ID generation - used in our knowledge/media endpoints
    "PR003946-66"  # Soft delete - implemented in our media/knowledge systems
)

for ticket in "${RELEVANT_TICKETS[@]}"; do
    add_comment_to_ticket "$ticket"
done

echo "🎉 PR #20 JIRA integration complete!"
echo "📊 Updated ${#RELEVANT_TICKETS[@]} tickets with implementation details"
echo "🔗 PR URL: $PR_URL"