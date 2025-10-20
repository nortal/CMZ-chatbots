#!/bin/bash

# Secure Environment Configuration System Ticket Creation Script
# Creates 6 tickets for comprehensive environment configuration management
# Follows successful authentication pattern from update_jira_simple.sh

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

echo "🎯 Creating Secure Environment Configuration System tickets..."

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

# Arrays to store created ticket keys and their relationships
declare -a CREATED_TICKETS=()

# Variables to store individual ticket keys (compatible with older bash)
CONFIG_FRAMEWORK_KEY=""
SECRETS_MANAGEMENT_KEY=""
CONFIG_VALIDATION_KEY=""
DEPLOYMENT_SCRIPTS_KEY=""
MONITORING_ALERTING_KEY=""
SECURITY_AUDIT_KEY=""

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

# Function to create a Jira ticket
create_ticket() {
    local summary="$1"
    local description="$2"
    local story_points="$3"
    local issue_type="$4"
    local ticket_name="$5"
    
    echo "🎫 Creating ticket: $summary"
    
    # Create temp file with ticket JSON
    local temp_file=$(mktemp)
    cat > "$temp_file" <<EOF
{
    "fields": {
        "project": {
            "key": "PR003946"
        },
        "summary": "$summary",
        "description": {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": "$description"
                        }
                    ]
                }
            ]
        },
        "issuetype": {
            "name": "$issue_type"
        },
        "customfield_10225": {
            "value": "Billable",
            "id": "10564"
        },
        "customfield_10014": "PR003946-61"
    }
}
EOF
    
    local response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
        -H "Authorization: Basic $JIRA_CREDENTIALS" \
        -H "Content-Type: application/json" \
        --data @"$temp_file" \
        "$JIRA_BASE_URL/rest/api/3/issue")
    
    local http_status=$(echo "$response" | grep "HTTP_STATUS:" | cut -d: -f2)
    
    rm -f "$temp_file"
    
    if [ "$http_status" = "201" ]; then
        local ticket_key=$(echo "$response" | sed '/HTTP_STATUS:/d' | jq -r '.key')
        echo "✅ Successfully created ticket: $ticket_key"
        CREATED_TICKETS+=("$ticket_key")
        
        # Store ticket key in appropriate variable
        case "$ticket_name" in
            "config_framework") CONFIG_FRAMEWORK_KEY="$ticket_key" ;;
            "secrets_management") SECRETS_MANAGEMENT_KEY="$ticket_key" ;;
            "config_validation") CONFIG_VALIDATION_KEY="$ticket_key" ;;
            "deployment_scripts") DEPLOYMENT_SCRIPTS_KEY="$ticket_key" ;;
            "monitoring_alerting") MONITORING_ALERTING_KEY="$ticket_key" ;;
            "security_audit") SECURITY_AUDIT_KEY="$ticket_key" ;;
        esac
        
        # Add story points as a comment
        echo "💬 Adding story points comment to $ticket_key..."
        sleep 1
        add_simple_comment "$ticket_key" "Story Points (soft estimate): $story_points — 1 point = 0.5 day"
        
        return 0
    else
        echo "❌ Failed to create ticket: $summary (HTTP $http_status)"
        echo "Response: $(echo "$response" | sed '/HTTP_STATUS:/d')"
        return 1
    fi
}

# Function to create issue link (dependency relationship)
create_issue_link() {
    local dependent_ticket="$1"
    local dependency_ticket="$2"
    local link_type="$3"
    
    echo "🔗 Creating dependency: $dependent_ticket depends on $dependency_ticket"
    
    # Create temp file with link JSON
    local temp_file=$(mktemp)
    cat > "$temp_file" <<EOF
{
    "type": {
        "name": "$link_type"
    },
    "inwardIssue": {
        "key": "$dependency_ticket"
    },
    "outwardIssue": {
        "key": "$dependent_ticket"
    }
}
EOF
    
    local response=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
        -H "Authorization: Basic $JIRA_CREDENTIALS" \
        -H "Content-Type: application/json" \
        --data @"$temp_file" \
        "$JIRA_BASE_URL/rest/api/3/issueLink")
    
    local http_status=$(echo "$response" | grep "HTTP_STATUS:" | cut -d: -f2)
    
    rm -f "$temp_file"
    
    if [ "$http_status" = "201" ]; then
        echo "✅ Successfully linked $dependent_ticket → $dependency_ticket"
        return 0
    else
        echo "❌ Failed to link tickets (HTTP $http_status)"
        echo "Response: $(echo "$response" | sed '/HTTP_STATUS:/d')"
        return 1
    fi
}

# Ticket 1: Environment Configuration Framework (5 points)
create_ticket \
    "Environment Configuration Framework" \
    "**IMPORTANT: Use Sequential Reasoning MCP when implementing this ticket for systematic analysis and planning.**

Implement a centralized configuration framework that manages environment-specific settings across development, staging, and production environments.

**Key Features:**
- Hierarchical configuration system (base → environment-specific → local overrides)
- Type-safe configuration loading with validation
- Environment variable resolution with fallbacks
- Configuration change tracking and versioning

**Technical Requirements:**
- Support for YAML, JSON, and environment variable sources
- Configuration schema validation
- Hot-reload capability for non-sensitive settings
- Integration with existing Flask/Connexion application structure

**Implementation Approach:**
- Use Sequential Reasoning MCP to analyze current configuration patterns
- Design schema-first approach with comprehensive validation
- Implement systematic testing of all configuration scenarios

**Acceptance Criteria:**
1. Configuration framework loads settings from multiple sources with proper precedence
2. All configuration changes are validated against defined schemas
3. Environment-specific overrides work correctly for dev/staging/prod
4. Configuration loading errors provide clear, actionable feedback
5. Framework integrates seamlessly with existing application startup

**Story Points:** 5 (Complex system design and implementation)" \
    5 \
    "Task" \
    "config_framework"

sleep 2

# Ticket 2: Secrets Management Integration (4 points)
create_ticket \
    "Secrets Management Integration" \
    "**IMPORTANT: Use Sequential Reasoning MCP when implementing this ticket for systematic security analysis and planning.**

Integrate secure secrets management with support for multiple backends including AWS Secrets Manager, HashiCorp Vault, and local development secrets.

**Key Features:**
- Multi-backend secrets management (AWS Secrets Manager, Vault, local)
- Automatic secret rotation detection and reload
- Secure credential caching with TTL expiration
- Development environment support with local secrets

**Technical Requirements:**
- Encrypted secrets caching with memory protection
- Fallback mechanisms for secret retrieval failures
- Integration with environment configuration framework
- Audit logging for all secret access operations

**Implementation Approach:**
- Use Sequential Reasoning MCP to analyze security requirements and threat models
- Design fail-safe mechanisms for secret retrieval and caching
- Implement comprehensive security testing and validation

**Security Considerations:**
- No plaintext secrets in logs or error messages
- Secure memory handling for cached credentials
- Proper cleanup of sensitive data structures
- Compliance with security best practices

**Acceptance Criteria:**
1. Secrets are retrieved securely from configured backends
2. Automatic rotation detection triggers credential refresh
3. Fallback mechanisms handle backend failures gracefully
4. All secret operations are properly audited and logged
5. Development workflow supports local secrets without compromising security

**Story Points:** 4 (Security-critical implementation with multiple integrations)" \
    4 \
    "Task" \
    "secrets_management"

sleep 2

# Ticket 3: Configuration Validation System (3 points)
create_ticket \
    "Configuration Validation System" \
    "**IMPORTANT: Use Sequential Reasoning MCP when implementing this ticket for systematic validation design and testing.**

Implement comprehensive validation system for all configuration sources with schema enforcement, constraint checking, and detailed error reporting.

**Key Features:**
- JSON Schema-based configuration validation
- Custom validation rules for business logic
- Cross-environment consistency checking
- Detailed validation error reporting with suggestions

**Technical Requirements:**
- Schema-driven validation with versioning support
- Performance-optimized validation for startup times
- Integration with configuration framework and secrets management
- Extensible validation rule system for custom constraints

**Implementation Approach:**
- Use Sequential Reasoning MCP to analyze validation requirements across all config types
- Design comprehensive error reporting with actionable feedback
- Implement systematic testing of all validation scenarios

**Validation Categories:**
- Structural validation (required fields, data types)
- Business logic validation (ranges, relationships)
- Security validation (credential formats, encryption requirements)
- Environment consistency validation

**Acceptance Criteria:**
1. All configuration sources are validated against defined schemas
2. Custom validation rules can be added for specific business requirements
3. Validation errors provide clear, actionable feedback for resolution
4. Cross-environment validation ensures consistency between environments
5. Validation performance does not significantly impact startup time

**Story Points:** 3 (Systematic validation implementation)" \
    3 \
    "Task" \
    "config_validation"

sleep 2

# Ticket 4: Environment-Specific Deployment Scripts (3 points)
create_ticket \
    "Environment-Specific Deployment Scripts" \
    "**IMPORTANT: Use Sequential Reasoning MCP when implementing this ticket for systematic deployment analysis and automation.**

Create automated deployment scripts that handle environment-specific configuration, secret management, and validation for consistent deployments across all environments.

**Key Features:**
- Environment-specific deployment automation
- Pre-deployment configuration validation
- Automated secret provisioning and rotation
- Rollback mechanisms with configuration state management

**Technical Requirements:**
- Shell/Python scripts for deployment automation
- Integration with configuration framework and secrets management
- Pre-flight checks for environment readiness
- Deployment status monitoring and reporting

**Implementation Approach:**
- Use Sequential Reasoning MCP to analyze deployment workflows and failure scenarios
- Design fail-safe deployment processes with comprehensive rollback support
- Implement systematic testing of deployment procedures

**Deployment Phases:**
1. Pre-deployment validation (configuration, secrets, dependencies)
2. Configuration deployment with environment-specific overrides
3. Secret provisioning and verification
4. Application deployment with health checks
5. Post-deployment validation and monitoring setup

**Acceptance Criteria:**
1. Deployment scripts handle all environment-specific requirements automatically
2. Pre-deployment validation prevents invalid configurations from being deployed
3. Secrets are provisioned securely during deployment process
4. Rollback mechanisms can restore previous configuration state reliably
5. Deployment status is monitored and reported throughout the process

**Story Points:** 3 (Deployment automation with environment handling)" \
    3 \
    "Task" \
    "deployment_scripts"

sleep 2

# Ticket 5: Configuration Monitoring and Alerting (3 points)
create_ticket \
    "Configuration Monitoring and Alerting" \
    "**IMPORTANT: Use Sequential Reasoning MCP when implementing this ticket for systematic monitoring design and alerting strategy.**

Implement comprehensive monitoring and alerting for configuration changes, secret rotations, and system health related to environment configuration management.

**Key Features:**
- Real-time configuration change monitoring
- Secret rotation and expiration alerting
- Configuration drift detection between environments
- Health checks for configuration system components

**Technical Requirements:**
- Integration with existing monitoring infrastructure
- Configurable alert thresholds and escalation policies
- Dashboard for configuration system health visibility
- Automated remediation for common configuration issues

**Implementation Approach:**
- Use Sequential Reasoning MCP to analyze monitoring requirements and failure modes
- Design comprehensive alerting strategy with appropriate escalation
- Implement systematic testing of monitoring and alerting systems

**Monitoring Categories:**
- Configuration Changes: Track all modifications with attribution
- Secret Health: Monitor rotation status and expiration warnings
- System Performance: Track configuration loading times and caching efficiency
- Environment Consistency: Alert on configuration drift between environments

**Acceptance Criteria:**
1. All configuration changes are monitored and logged with proper attribution
2. Secret rotation and expiration events trigger appropriate alerts
3. Configuration drift between environments is detected and reported
4. System health monitoring provides visibility into configuration framework performance
5. Automated remediation handles common configuration issues without manual intervention

**Story Points:** 3 (Monitoring and alerting system implementation)" \
    3 \
    "Task" \
    "monitoring_alerting"

sleep 2

# Ticket 6: Configuration Security Audit Tools (3 points)
create_ticket \
    "Configuration Security Audit Tools" \
    "**IMPORTANT: Use Sequential Reasoning MCP when implementing this ticket for systematic security analysis and audit design.**

Develop comprehensive security audit tools for configuration management, including secret scanning, permission auditing, and compliance reporting.

**Key Features:**
- Automated secret scanning in configuration files
- Permission and access control auditing
- Compliance reporting for security standards
- Security best practices validation

**Technical Requirements:**
- Integration with existing security tools and workflows
- Automated scanning for hardcoded secrets and credentials
- Role-based access control validation
- Compliance reporting for SOC2, PCI-DSS, and other standards

**Implementation Approach:**
- Use Sequential Reasoning MCP to analyze security requirements and compliance needs
- Design comprehensive audit framework with automated reporting
- Implement systematic security testing and validation

**Audit Categories:**
- Secret Management: Scan for hardcoded secrets, validate rotation policies
- Access Control: Audit permissions and role assignments
- Configuration Security: Validate encryption, secure defaults, and security configurations
- Compliance: Generate reports for security standards and regulations

**Security Standards Coverage:**
- OWASP security best practices
- SOC2 compliance requirements
- Industry-specific regulations (PCI-DSS, HIPAA as applicable)
- Internal security policies and standards

**Acceptance Criteria:**
1. Automated secret scanning detects hardcoded credentials in all configuration sources
2. Permission auditing validates proper access controls are in place
3. Compliance reporting generates required documentation for security standards
4. Security validation ensures configuration follows established best practices
5. Audit tools integrate with existing security workflows and CI/CD processes

**Story Points:** 3 (Security audit tooling and compliance)" \
    3 \
    "Task" \
    "security_audit"

# Phase 2: Create Dependencies
echo
echo "🔗 Creating ticket dependencies..."

if [ ${#CREATED_TICKETS[@]} -eq 6 ]; then
    # Dependency mapping:
    # 1. config_framework → Foundation (no dependencies)
    # 2. secrets_management → Depends on config_framework
    # 3. config_validation → Depends on config_framework  
    # 4. deployment_scripts → Depends on config_framework, secrets_management, config_validation
    # 5. monitoring_alerting → Depends on config_framework, secrets_management, config_validation
    # 6. security_audit → Depends on config_framework, secrets_management, config_validation
    
    echo "📋 Setting up logical dependencies..."
    
    # Secrets Management depends on Configuration Framework
    create_issue_link "$SECRETS_MANAGEMENT_KEY" "$CONFIG_FRAMEWORK_KEY" "Blocks"
    sleep 1
    
    # Configuration Validation depends on Configuration Framework
    create_issue_link "$CONFIG_VALIDATION_KEY" "$CONFIG_FRAMEWORK_KEY" "Blocks"
    sleep 1
    
    # Deployment Scripts depends on all foundational components
    create_issue_link "$DEPLOYMENT_SCRIPTS_KEY" "$CONFIG_FRAMEWORK_KEY" "Blocks"
    sleep 1
    create_issue_link "$DEPLOYMENT_SCRIPTS_KEY" "$SECRETS_MANAGEMENT_KEY" "Blocks"
    sleep 1
    create_issue_link "$DEPLOYMENT_SCRIPTS_KEY" "$CONFIG_VALIDATION_KEY" "Blocks"
    sleep 1
    
    # Monitoring & Alerting depends on all foundational components
    create_issue_link "$MONITORING_ALERTING_KEY" "$CONFIG_FRAMEWORK_KEY" "Blocks"
    sleep 1
    create_issue_link "$MONITORING_ALERTING_KEY" "$SECRETS_MANAGEMENT_KEY" "Blocks"
    sleep 1
    create_issue_link "$MONITORING_ALERTING_KEY" "$CONFIG_VALIDATION_KEY" "Blocks"
    sleep 1
    
    # Security Audit depends on all foundational components
    create_issue_link "$SECURITY_AUDIT_KEY" "$CONFIG_FRAMEWORK_KEY" "Blocks"
    sleep 1
    create_issue_link "$SECURITY_AUDIT_KEY" "$SECRETS_MANAGEMENT_KEY" "Blocks"
    sleep 1
    create_issue_link "$SECURITY_AUDIT_KEY" "$CONFIG_VALIDATION_KEY" "Blocks"
    
    echo "✅ All dependencies created successfully!"
else
    echo "⚠️ Not all tickets created successfully, skipping dependency creation"
fi

echo
echo "🎉 Ticket creation and dependency setup completed!"
echo "📊 Summary: Created ${#CREATED_TICKETS[@]} tickets"
echo

if [ ${#CREATED_TICKETS[@]} -gt 0 ]; then
    echo "📋 Created tickets with dependencies:"
    for ticket in "${CREATED_TICKETS[@]}"; do
        echo "   • $ticket: https://nortal.atlassian.net/browse/$ticket"
    done
    echo
    echo "🔗 Dependency Structure:"
    echo "   📦 $CONFIG_FRAMEWORK_KEY (Foundation)"
    echo "   ├── $SECRETS_MANAGEMENT_KEY (depends on foundation)"
    echo "   ├── $CONFIG_VALIDATION_KEY (depends on foundation)"
    echo "   ├── $DEPLOYMENT_SCRIPTS_KEY (depends on foundation + secrets + validation)"
    echo "   ├── $MONITORING_ALERTING_KEY (depends on foundation + secrets + validation)"
    echo "   └── $SECURITY_AUDIT_KEY (depends on foundation + secrets + validation)"
    echo
    echo "📈 Total Story Points: 21"
    echo "🎯 Epic: Secure Environment Configuration System"
    echo "🔄 Implementation Order: Foundation first, then parallel development of dependent components"
    echo
    echo "✅ All tickets include Sequential Reasoning MCP implementation instructions"
    echo "🔗 All logical dependencies configured in Jira"
    echo "🔧 Ready for systematic implementation approach"
else
    echo "❌ No tickets were created successfully"
    exit 1
fi