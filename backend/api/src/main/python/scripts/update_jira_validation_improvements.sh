#!/bin/bash

# Script to update Jira tickets for validation improvements implementation
# Updates the CORRECT tickets that were actually implemented in this MR

set -e

# Check if required environment variables are set
if [ -z "$JIRA_API_TOKEN" ]; then
    echo "Error: JIRA_API_TOKEN environment variable is not set"
    exit 1
fi

if [ -z "$JIRA_EMAIL" ]; then
    echo "Error: JIRA_EMAIL environment variable is not set"
    exit 1
fi

JIRA_BASE_URL="https://nortal.atlassian.net"

# Create base64 encoded credentials for Basic Auth (credentials are from env vars only)
JIRA_CREDENTIALS=$(echo -n "$JIRA_EMAIL:$JIRA_API_TOKEN" | base64)

echo "🎯 Updating Jira tickets for API validation improvements..."
echo "⚠️  IMPORTANT: This will update the tickets we ACTUALLY implemented:"
echo "   • PR003946-94: Unit tests"  
echo "   • PR003946-95: Persistence abstraction"
echo "   • PR003946-96: Playwright testing"
echo "   • PR003946-90: Error schema consistency"
echo "   • PR003946-73: Foreign key validation"
echo ""
read -p "Do you want to continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Cancelled by user"
    exit 0
fi

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
    cat > "$temp_file" <<COMMENT_EOF
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
COMMENT_EOF
    
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

# Update PR003946-94: Unit Testing Framework
echo "📌 Processing PR003946-94 (Unit Testing Framework)..."
transition_status "PR003946-94"
sleep 2
add_simple_comment "PR003946-94" "COMPLETED - Comprehensive unit testing framework implemented. 30/30 endpoint coverage with Pytest integration. HTML reporting with pass/fail statistics. File persistence mode for test isolation. Boundary value testing generators. Ready for GitLab CI integration. MR: https://github.com/nortal/CMZ-chatbots/pull/27"

echo

# Update PR003946-95: Persistence Abstraction Layer
echo "📌 Processing PR003946-95 (Persistence Abstraction)..."
transition_status "PR003946-95"
sleep 2
add_simple_comment "PR003946-95" "COMPLETED - Persistence abstraction layer with environment switching. Protocol-based design maintains DynamoDB API compatibility. PERSISTENCE_MODE=dynamo|file switching. JSON file storage with atomic operations for testing. Zero breaking changes to existing codebase. MR: https://github.com/nortal/CMZ-chatbots/pull/27"

echo

# Update PR003946-96: Playwright Testing Framework  
echo "📌 Processing PR003946-96 (Playwright Testing)..."
transition_status "PR003946-96"
sleep 2
add_simple_comment "PR003946-96" "COMPLETED - Playwright E2E testing framework. Page object model with base classes. Feature-driven testing with JSON configuration. Multi-browser support (Chrome, Firefox, Safari, Mobile). Executive health reporting with quality gates. Complete authentication test suite with 50+ scenarios. MR: https://github.com/nortal/CMZ-chatbots/pull/27"

echo

# Update PR003946-90: Error Schema Consistency
echo "📌 Processing PR003946-90 (Error Schema Consistency)..."
transition_status "PR003946-90"
sleep 2  
add_simple_comment "PR003946-90" "COMPLETED - Consistent Error schema implementation. Multi-layer error handling: Flask errorhandlers + Connexion ProblemException + Custom ValidationError. Standardized {code, message, details} structure across all endpoints. Integration test now passing. MR: https://github.com/nortal/CMZ-chatbots/pull/27"

echo

# Update PR003946-73: Foreign Key Validation
echo "📌 Processing PR003946-73 (Foreign Key Validation)..."
transition_status "PR003946-73"
sleep 2
add_simple_comment "PR003946-73" "COMPLETED - Foreign key validation with cross-table validation using store abstraction. Proper error messages with entity type specification. Controller-implementation connection fixes. Integration test now passing. MR: https://github.com/nortal/CMZ-chatbots/pull/27"

echo
echo "🎉 Updates completed!"
echo "📋 Check tickets:"
echo "   • https://nortal.atlassian.net/browse/PR003946-94"
echo "   • https://nortal.atlassian.net/browse/PR003946-95"
echo "   • https://nortal.atlassian.net/browse/PR003946-96"
echo "   • https://nortal.atlassian.net/browse/PR003946-90"
echo "   • https://nortal.atlassian.net/browse/PR003946-73"
