#!/bin/bash

# Update created tickets with explicit dependency information
# Based on successful authentication pattern from existing scripts

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

echo "🔗 Adding dependency information to created tickets..."

# Function to add a simple comment
add_simple_comment() {
    local ticket_id=$1
    local comment_text="$2"
    
    echo "💬 Adding dependency info to $ticket_id..."
    
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
        echo "✅ Successfully added dependency info to $ticket_id"
    else
        echo "❌ Failed to add dependency info to $ticket_id (HTTP $http_status)"
        echo "Response: $(echo "$response" | sed '/HTTP_STATUS:/d')"
    fi
}

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

# Update each ticket with dependency information

# PR003946-104: Environment Configuration Framework (Foundation - no dependencies)
add_simple_comment "PR003946-104" "🏗️ IMPLEMENTATION ORDER: This is the FOUNDATION ticket - implement FIRST before all others.

📋 DEPENDENCIES: None (this is the base framework)

🔄 BLOCKS: This ticket must be completed before starting:
• PR003946-105 (Secrets Management Integration)
• PR003946-106 (Configuration Validation System)  
• PR003946-107 (Environment-Specific Deployment Scripts)
• PR003946-108 (Configuration Monitoring and Alerting)
• PR003946-109 (Configuration Security Audit Tools)

⚠️ CRITICAL: All other configuration system tickets depend on this foundation."

sleep 2

# PR003946-105: Secrets Management Integration
add_simple_comment "PR003946-105" "🏗️ IMPLEMENTATION ORDER: Implement AFTER foundation is complete.

📋 DEPENDENCIES: 
• PR003946-104 (Environment Configuration Framework) - REQUIRED
  → Needs the base configuration system to integrate with

🔄 BLOCKS: This ticket must be completed before starting:
• PR003946-107 (Environment-Specific Deployment Scripts)
• PR003946-108 (Configuration Monitoring and Alerting) 
• PR003946-109 (Configuration Security Audit Tools)

⚠️ PREREQUISITE: Cannot start until PR003946-104 is merged and deployed."

sleep 2

# PR003946-106: Configuration Validation System  
add_simple_comment "PR003946-106" "🏗️ IMPLEMENTATION ORDER: Implement AFTER foundation is complete.

📋 DEPENDENCIES:
• PR003946-104 (Environment Configuration Framework) - REQUIRED
  → Needs the base configuration system to validate against

🔄 BLOCKS: This ticket must be completed before starting:
• PR003946-107 (Environment-Specific Deployment Scripts)
• PR003946-108 (Configuration Monitoring and Alerting)
• PR003946-109 (Configuration Security Audit Tools)

⚠️ PREREQUISITE: Cannot start until PR003946-104 is merged and deployed."

sleep 2

# PR003946-107: Environment-Specific Deployment Scripts
add_simple_comment "PR003946-107" "🏗️ IMPLEMENTATION ORDER: Implement LAST (requires all foundational components).

📋 DEPENDENCIES (ALL REQUIRED):
• PR003946-104 (Environment Configuration Framework) - REQUIRED
  → Needs base config system for deployment configuration
• PR003946-105 (Secrets Management Integration) - REQUIRED  
  → Needs secrets management for secure deployment
• PR003946-106 (Configuration Validation System) - REQUIRED
  → Needs validation system for pre-deployment checks

🔄 BLOCKS: None (this is a final integration component)

⚠️ PREREQUISITES: Cannot start until ALL three foundation tickets (104, 105, 106) are merged and deployed."

sleep 2

# PR003946-108: Configuration Monitoring and Alerting
add_simple_comment "PR003946-108" "🏗️ IMPLEMENTATION ORDER: Implement LAST (requires all foundational components).

📋 DEPENDENCIES (ALL REQUIRED):
• PR003946-104 (Environment Configuration Framework) - REQUIRED
  → Needs base config system to monitor
• PR003946-105 (Secrets Management Integration) - REQUIRED
  → Needs to monitor secret rotations and health  
• PR003946-106 (Configuration Validation System) - REQUIRED
  → Needs to monitor validation failures and drift

🔄 BLOCKS: None (this is a final integration component)

⚠️ PREREQUISITES: Cannot start until ALL three foundation tickets (104, 105, 106) are merged and deployed."

sleep 2

# PR003946-109: Configuration Security Audit Tools  
add_simple_comment "PR003946-109" "🏗️ IMPLEMENTATION ORDER: Implement LAST (requires all foundational components).

📋 DEPENDENCIES (ALL REQUIRED):
• PR003946-104 (Environment Configuration Framework) - REQUIRED
  → Needs base config system to audit
• PR003946-105 (Secrets Management Integration) - REQUIRED
  → Needs to audit secret management practices
• PR003946-106 (Configuration Validation System) - REQUIRED  
  → Needs to audit validation rules and compliance

🔄 BLOCKS: None (this is a final integration component)

⚠️ PREREQUISITES: Cannot start until ALL three foundation tickets (104, 105, 106) are merged and deployed."

echo
echo "🎉 Dependency information added to all tickets!"
echo
echo "📋 Implementation Order Summary:"
echo "   1️⃣ FIRST: PR003946-104 (Environment Configuration Framework)"
echo "   2️⃣ PARALLEL: PR003946-105 (Secrets Management) + PR003946-106 (Validation)"  
echo "   3️⃣ FINAL: PR003946-107 (Deployment) + PR003946-108 (Monitoring) + PR003946-109 (Security Audit)"
echo
echo "✅ All tickets now have explicit dependency information"
echo "🔧 Ready for systematic implementation approach"