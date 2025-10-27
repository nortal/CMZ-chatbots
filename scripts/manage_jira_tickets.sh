#!/bin/bash

# Enhanced Jira ticket management script for /nextfive command
# Manages ticket transitions: To Do → In Progress → Done
# Usage: ./manage_jira_tickets.sh <action> <ticket_id> [comment]
#   Actions: start, done, comment
#   Example: ./manage_jira_tickets.sh start PR003946-91 "Starting implementation"
#   Example: ./manage_jira_tickets.sh done PR003946-91 "MR ready for merge"

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

# Create base64 encoded credentials for Basic Auth
JIRA_CREDENTIALS=$(echo -n "$JIRA_EMAIL:$JIRA_API_TOKEN" | base64)

# Get command arguments
ACTION="${1:-}"
TICKET_ID="${2:-}"
COMMENT_TEXT="${3:-}"

# Validate arguments
if [ -z "$ACTION" ] || [ -z "$TICKET_ID" ]; then
    echo "Usage: $0 <action> <ticket_id> [comment]"
    echo "  Actions: start, done, comment, status"
    echo "  Example: $0 start PR003946-91 'Starting implementation'"
    exit 1
fi

# Function to test API connectivity
test_connectivity() {
    local test_response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
        -H "Authorization: Basic $JIRA_CREDENTIALS" \
        -H "Content-Type: application/json" \
        "$JIRA_BASE_URL/rest/api/3/myself")

    local test_http_status=$(echo "$test_response" | grep "HTTP_STATUS:" | cut -d: -f2)

    if [ "$test_http_status" != "200" ]; then
        echo "❌ API connectivity test failed"
        exit 1
    fi
}

# Function to get current ticket status
get_ticket_status() {
    local ticket_id=$1

    local response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
        -H "Authorization: Basic $JIRA_CREDENTIALS" \
        -H "Content-Type: application/json" \
        "$JIRA_BASE_URL/rest/api/3/issue/$ticket_id?fields=status")

    local http_status=$(echo "$response" | grep "HTTP_STATUS:" | cut -d: -f2)

    if [ "$http_status" = "200" ]; then
        # Extract status name from JSON response
        local status_name=$(echo "$response" | sed '/HTTP_STATUS:/d' | grep -o '"status":{"[^}]*"name":"[^"]*"' | sed 's/.*"name":"\([^"]*\)".*/\1/')
        echo "$status_name"
    else
        echo "ERROR"
    fi
}

# Function to get available transitions for a ticket
get_transitions() {
    local ticket_id=$1

    local response=$(curl -s \
        -H "Authorization: Basic $JIRA_CREDENTIALS" \
        -H "Content-Type: application/json" \
        "$JIRA_BASE_URL/rest/api/3/issue/$ticket_id/transitions")

    echo "$response"
}

# Function to find transition ID by name
find_transition_id() {
    local ticket_id=$1
    local target_status=$2

    local transitions=$(get_transitions "$ticket_id")

    # Try to find exact match first
    local transition_id=$(echo "$transitions" | grep -o "\"id\":\"[0-9]*\",\"name\":\"$target_status\"" | head -1 | sed 's/.*"id":"\([0-9]*\)".*/\1/')

    # If no exact match, try partial matches for common transitions
    if [ -z "$transition_id" ]; then
        case "$target_status" in
            "In Progress")
                # Try common variations
                transition_id=$(echo "$transitions" | grep -i -o "\"id\":\"[0-9]*\",\"name\":\"[^\"]*progress[^\"]*\"" | head -1 | sed 's/.*"id":"\([0-9]*\)".*/\1/')
                if [ -z "$transition_id" ]; then
                    transition_id=$(echo "$transitions" | grep -i -o "\"id\":\"[0-9]*\",\"name\":\"start[^\"]*\"" | head -1 | sed 's/.*"id":"\([0-9]*\)".*/\1/')
                fi
                ;;
            "Done")
                # Try common variations
                transition_id=$(echo "$transitions" | grep -i -o "\"id\":\"[0-9]*\",\"name\":\"done\"" | head -1 | sed 's/.*"id":"\([0-9]*\)".*/\1/')
                if [ -z "$transition_id" ]; then
                    transition_id=$(echo "$transitions" | grep -i -o "\"id\":\"[0-9]*\",\"name\":\"complete[^\"]*\"" | head -1 | sed 's/.*"id":"\([0-9]*\)".*/\1/')
                fi
                if [ -z "$transition_id" ]; then
                    transition_id=$(echo "$transitions" | grep -i -o "\"id\":\"[0-9]*\",\"name\":\"resolve[^\"]*\"" | head -1 | sed 's/.*"id":"\([0-9]*\)".*/\1/')
                fi
                ;;
        esac
    fi

    echo "$transition_id"
}

# Function to transition ticket status
transition_status() {
    local ticket_id=$1
    local target_status=$2
    local comment_text="${3:-}"

    # Get current status
    local current_status=$(get_ticket_status "$ticket_id")

    if [ "$current_status" = "ERROR" ]; then
        echo "❌ Failed to get current status for $ticket_id"
        return 1
    fi

    echo "📊 Current status of $ticket_id: $current_status"

    # Check if already in target status
    if [ "$current_status" = "$target_status" ]; then
        echo "✅ $ticket_id is already in $target_status"
        if [ -n "$comment_text" ]; then
            add_comment "$ticket_id" "$comment_text"
        fi
        return 0
    fi

    # Find the transition ID
    local transition_id=$(find_transition_id "$ticket_id" "$target_status")

    if [ -z "$transition_id" ]; then
        echo "⚠️ No direct transition found from '$current_status' to '$target_status' for $ticket_id"
        echo "Available transitions:"
        get_transitions "$ticket_id" | grep -o '"name":"[^"]*"' | sed 's/"name":"\([^"]*\)"/  - \1/'
        return 1
    fi

    echo "🔄 Transitioning $ticket_id to $target_status (transition ID: $transition_id)..."

    local response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
        -H "Authorization: Basic $JIRA_CREDENTIALS" \
        -H "Content-Type: application/json" \
        --data "{\"transition\":{\"id\":\"$transition_id\"}}" \
        "$JIRA_BASE_URL/rest/api/3/issue/$ticket_id/transitions")

    local http_status=$(echo "$response" | grep "HTTP_STATUS:" | cut -d: -f2)

    if [ "$http_status" = "204" ]; then
        echo "✅ Successfully transitioned $ticket_id to $target_status"
        if [ -n "$comment_text" ]; then
            add_comment "$ticket_id" "$comment_text"
        fi
        return 0
    else
        echo "❌ Failed to transition $ticket_id (HTTP $http_status)"
        echo "Response: $(echo "$response" | sed '/HTTP_STATUS:/d')"
        return 1
    fi
}

# Function to add a comment to a ticket
add_comment() {
    local ticket_id=$1
    local comment_text="$2"

    if [ -z "$comment_text" ]; then
        return 0
    fi

    echo "💬 Adding comment to $ticket_id..."

    # Create temp file with comment
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
    fi
}

# Function to batch update multiple tickets
batch_update() {
    local action=$1
    shift
    local tickets=("$@")

    for ticket in "${tickets[@]}"; do
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        case "$action" in
            "start")
                transition_status "$ticket" "In Progress" "🚀 Starting implementation via /nextfive command"
                ;;
            "done")
                transition_status "$ticket" "Done" "✅ Implementation complete - MR ready for merge"
                ;;
        esac
        echo
    done
}

# Main execution
echo "🎯 Jira Ticket Management"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Test connectivity first
test_connectivity
echo "✅ API connectivity confirmed"
echo

case "$ACTION" in
    "start")
        transition_status "$TICKET_ID" "In Progress" "$COMMENT_TEXT"
        ;;
    "done")
        transition_status "$TICKET_ID" "Done" "$COMMENT_TEXT"
        ;;
    "comment")
        add_comment "$TICKET_ID" "$COMMENT_TEXT"
        ;;
    "status")
        current_status=$(get_ticket_status "$TICKET_ID")
        echo "📊 $TICKET_ID status: $current_status"
        ;;
    "batch-start")
        shift  # Remove 'batch-start' from arguments
        batch_update "start" "$@"
        ;;
    "batch-done")
        shift  # Remove 'batch-done' from arguments
        batch_update "done" "$@"
        ;;
    *)
        echo "❌ Unknown action: $ACTION"
        echo "Valid actions: start, done, comment, status, batch-start, batch-done"
        exit 1
        ;;
esac

if [ "$ACTION" != "status" ] && [ "$ACTION" != "batch-start" ] && [ "$ACTION" != "batch-done" ]; then
    echo
    echo "📋 View ticket: $JIRA_BASE_URL/browse/$TICKET_ID"
fi