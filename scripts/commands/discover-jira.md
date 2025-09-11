# /discover-jira Command

## Purpose
Strategic Jira analysis using dependency mapping and implementation synergies to select the optimal next 5 tickets.

## Execution Steps

### Step 1: Query All Open Jira Tickets
```bash
# Load Jira credentials from .env.local
if [ -f ".env.local" ]; then
    source .env.local
elif [ -f "../.env.local" ]; then  
    source ../.env.local
else
    echo "❌ Error: .env.local not found. Jira credentials required."
    echo "Please ensure .env.local exists with JIRA_EMAIL and JIRA_API_TOKEN"
    exit 1
fi

# Validate required credentials
if [[ -z "$JIRA_EMAIL" || -z "$JIRA_API_TOKEN" ]]; then
    echo "❌ Error: Missing Jira credentials in .env.local"
    echo "Required: JIRA_EMAIL=your.email@nortal.com"
    echo "Required: JIRA_API_TOKEN=your_token_here"
    exit 1
fi

# Query ALL open tickets in the epic (not just next 5)
AUTH_HEADER=$(echo -n "$JIRA_EMAIL:$JIRA_API_TOKEN" | base64)
JIRA_BASE_URL="https://nortal.atlassian.net"

# Test connectivity first
echo "🔗 Testing Jira API connectivity..."
TEST_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
  -H "Authorization: Basic $AUTH_HEADER" \
  -H "Content-Type: application/json" \
  "$JIRA_BASE_URL/rest/api/3/myself")

HTTP_STATUS=$(echo "$TEST_RESPONSE" | tail -n1 | cut -d: -f2)
if [[ "$HTTP_STATUS" != "200" ]]; then
    echo "❌ Jira API connectivity failed (HTTP $HTTP_STATUS)"
    echo "Response: $(echo "$TEST_RESPONSE" | head -n -1)"
    
    # Log to advice file
    echo "## $(date '+%Y-%m-%d %H:%M:%S') - /discover-jira API Connection Failure" >> NORTAL-JIRA-ADVICE.md
    echo "**Issue**: Jira API returned HTTP $HTTP_STATUS" >> NORTAL-JIRA-ADVICE.md
    echo "**Credentials**: Using .env.local with email=$JIRA_EMAIL" >> NORTAL-JIRA-ADVICE.md  
    echo "**URL**: $JIRA_BASE_URL/rest/api/3/myself" >> NORTAL-JIRA-ADVICE.md
    echo "**Resolution**: Check token expiration, network connectivity, API permissions" >> NORTAL-JIRA-ADVICE.md
    echo "" >> NORTAL-JIRA-ADVICE.md
    
    exit 1
fi

echo "✅ Jira API connectivity successful"

# Query tickets with error handling
echo "📋 Querying open tickets in PR003946 epic..."
TICKETS_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
  -H "Authorization: Basic $AUTH_HEADER" \
  -H "Content-Type: application/json" \
  "$JIRA_BASE_URL/rest/api/3/search?jql=project=PR003946%20AND%20status!=Done&maxResults=100&fields=key,summary,description,priority,status,assignee,created,updated")

TICKETS_HTTP_STATUS=$(echo "$TICKETS_RESPONSE" | tail -n1 | cut -d: -f2)
if [[ "$TICKETS_HTTP_STATUS" != "200" ]]; then
    echo "❌ Failed to query tickets (HTTP $TICKETS_HTTP_STATUS)"
    
    # Log failure to advice file
    echo "## $(date '+%Y-%m-%d %H:%M:%S') - /discover-jira Ticket Query Failure" >> NORTAL-JIRA-ADVICE.md
    echo "**Issue**: Ticket query failed with HTTP $TICKETS_HTTP_STATUS" >> NORTAL-JIRA-ADVICE.md
    echo "**JQL**: project=PR003946 AND status!=Done" >> NORTAL-JIRA-ADVICE.md
    echo "**Response**: $(echo "$TICKETS_RESPONSE" | head -n -1 | head -c 200)..." >> NORTAL-JIRA-ADVICE.md
    echo "**Resolution**: Validate JQL syntax, check project permissions, verify project key" >> NORTAL-JIRA-ADVICE.md
    echo "" >> NORTAL-JIRA-ADVICE.md
    
    exit 1
fi

# Extract ticket data
TICKETS_JSON=$(echo "$TICKETS_RESPONSE" | head -n -1)
TICKET_COUNT=$(echo "$TICKETS_JSON" | jq -r '.total // 0')

echo "✅ Successfully retrieved $TICKET_COUNT tickets"

# Log success to advice file
echo "## $(date '+%Y-%m-%d %H:%M:%S') - /discover-jira Successful Execution" >> NORTAL-JIRA-ADVICE.md
echo "**Result**: Retrieved $TICKET_COUNT tickets successfully" >> NORTAL-JIRA-ADVICE.md
echo "**Credentials**: .env.local authentication working properly" >> NORTAL-JIRA-ADVICE.md
echo "**Performance**: Query completed in $(date '+%H:%M:%S')" >> NORTAL-JIRA-ADVICE.md
echo "**Next Steps**: Proceeding with strategic analysis of retrieved tickets" >> NORTAL-JIRA-ADVICE.md
echo "" >> NORTAL-JIRA-ADVICE.md

# Extract comprehensive ticket data:
# - Ticket IDs, titles, and full descriptions  
# - Current status, priority levels, and assignment
# - Implementation requirements from descriptions
# - Any noted dependencies or relationships
```

### Step 2: Analyze Current Codebase Context
```bash
# Examine existing implementations to understand current patterns
ls -la backend/api/src/main/python/openapi_server/impl/
find backend/api/src/main/python/openapi_server/impl/ -name "*.py" -exec basename {} \;

# Analyze OpenAPI spec for endpoint structure and dependencies
grep -E "(paths|/api/v1)" backend/api/openapi_spec.yaml | head -30

# Check DynamoDB table configurations and patterns
grep -r "DYNAMO_TABLE_NAME\|dynamo\|DynamoDB" backend/api/src/main/python/openapi_server/impl/ || echo "No DynamoDB patterns found"

# Identify existing authentication and validation patterns
grep -r "auth\|jwt\|token\|validate" backend/api/src/main/python/openapi_server/impl/ | head -10 || echo "No auth patterns found"
```

### Step 3: Strategic Sequential Reasoning Analysis

Use sequential reasoning MCP to perform comprehensive strategic analysis:

**Sequential Reasoning Prompt:**
```
Perform strategic analysis to select the optimal next 5 tickets from this Jira backlog:

**AVAILABLE DATA:**
- All Open Jira Tickets: {jira_tickets_json}
- Current Implementation State: {impl_directory_analysis}
- OpenAPI Endpoint Structure: {openapi_analysis}
- Existing Code Patterns: {codebase_patterns_analysis}

**STRATEGIC ANALYSIS FRAMEWORK:**

1. **Foundation Dependency Mapping:**
   - Which tickets provide critical infrastructure that other tickets depend on?
   - Are there ID generation, authentication, or database schema tickets that must come first?
   - What shared utilities or middleware need to be established?
   - Which tickets would cause significant rework if implemented later?

2. **Implementation Synergy Identification:**
   - Which tickets work with the same DynamoDB tables and can share CRUD patterns?
   - What validation logic, error handling, or business rules can be reused?
   - Are there endpoint groups that should be implemented together for consistency?
   - Which tickets benefit from being developed in parallel vs sequentially?

3. **Technical Risk and Complexity Assessment:**
   - Which foundational tickets have the highest risk if implemented incorrectly?
   - What tickets would reveal architectural problems or design issues early?
   - Which implementations establish patterns that affect many future tickets?
   - What's the optimal balance of foundational complexity vs quick wins?

4. **Business Value and Workflow Enablement:**
   - Which ticket combinations create complete, testable user workflows?
   - What implementations unlock the most business value when completed?
   - Are there opportunities to deliver user-facing features incrementally?
   - Which tickets enable better testing and validation of the overall system?

5. **Strategic Implementation Sequencing:**
   - Which tickets establish reusable patterns for the remaining backlog?
   - What sequence minimizes development time through pattern reuse?
   - Are there opportunities to validate technical approaches before broader implementation?
   - How can we maximize parallel development opportunities?

**ANALYSIS DEPTH REQUIREMENTS:**

For each potential ticket, evaluate:
- **Dependencies**: What must be completed before this ticket can be implemented?
- **Enablement**: What other tickets does completing this one make easier/possible?
- **Synergies**: What other tickets share implementation patterns or logic?
- **Risk Level**: How likely is this ticket to require architectural changes?
- **Business Impact**: How much user/business value does completion provide?
- **Implementation Effort**: Realistic time estimate based on complexity and dependencies

**DELIVERABLE REQUIREMENTS:**

1. **Complete Ticket Ranking**: All available tickets ranked by strategic implementation value
2. **Optimal Next 5 Selection**: Best 5 tickets with detailed strategic justification
3. **Dependency Mapping**: Clear visualization of what each selected ticket enables
4. **Implementation Sequence**: Recommended order within the 5 selected tickets
5. **Parallel Development Plan**: Which tickets can be developed simultaneously
6. **Risk Assessment**: Potential issues and mitigation strategies
7. **Business Value Projection**: Expected outcomes and user workflow completions

**SELECTION CRITERIA PRIORITIES:**
1. **Foundation First**: Prioritize tickets that enable multiple others
2. **Synergy Optimization**: Group tickets that share implementation patterns
3. **Risk Management**: Balance high-impact foundations with lower-risk implementations
4. **Business Value**: Ensure selected tickets deliver meaningful user capabilities
5. **Development Efficiency**: Maximize reuse and minimize rework
6. **Quality Assurance**: Enable comprehensive testing and validation opportunities
```

### Step 4: Strategic Implementation Plan Output

Generate comprehensive strategic analysis:

```json
{
  "session_id": "discover_jira_YYYYMMDD_HHMMSS",
  "analysis_timestamp": "2025-09-11T12:30:00Z",
  "jira_data_summary": {
    "total_open_tickets": 25,
    "priority_distribution": {
      "highest": 3,
      "high": 8, 
      "medium": 12,
      "low": 2
    },
    "status_distribution": {
      "to_do": 18,
      "in_progress": 5,
      "code_review": 2
    }
  },

  "strategic_analysis": {
    "foundation_dependencies": [
      {
        "foundation_ticket": "PR003946-69",
        "title": "Server-generated ID standardization",
        "dependency_reason": "ID generation patterns required by ALL create operations",
        "dependent_tickets": ["PR003946-75", "PR003946-76", "PR003946-80", "PR003946-82", "PR003946-85"],
        "impact_scope": "System-wide - affects 12+ future tickets",
        "implementation_risk": "High - patterns affect entire architecture"
      },
      {
        "foundation_ticket": "PR003946-71", 
        "title": "JWT token validation enhancement",
        "dependency_reason": "Authentication required for all protected endpoints",
        "dependent_tickets": ["PR003946-72", "PR003946-80", "PR003946-83", "PR003946-84"],
        "impact_scope": "Security infrastructure - enables user-specific operations", 
        "implementation_risk": "High - security implementation must be correct"
      }
    ],

    "implementation_synergies": [
      {
        "synergy_group": "Knowledge Management System",
        "tickets": ["PR003946-75", "PR003946-76"],
        "shared_patterns": [
          "DynamoDB knowledge table CRUD operations",
          "Content validation and metadata handling",
          "Educational content workflow logic"
        ],
        "efficiency_benefit": "Can implement together - shared table schema and validation patterns",
        "parallel_development": "Suitable for parallel implementation after foundations"
      },
      {
        "synergy_group": "Family Management Operations",
        "tickets": ["PR003946-79", "PR003946-80"],
        "shared_patterns": [
          "Family table relationship validation", 
          "Parent-student constraint checking",
          "Family membership business logic"
        ],
        "efficiency_benefit": "Common validation logic and business rules",
        "parallel_development": "Sequential preferred - build validation patterns first"
      },
      {
        "synergy_group": "Analytics and Reporting",
        "tickets": ["PR003946-83", "PR003946-84"],
        "shared_patterns": [
          "Time-window data processing",
          "Log aggregation and analysis", 
          "Reporting data structures"
        ],
        "efficiency_benefit": "Shared analytics infrastructure and data processing patterns",
        "parallel_development": "Can be developed in parallel after auth infrastructure"
      }
    ],

    "risk_assessment": {
      "high_risk_foundations": [
        {
          "ticket": "PR003946-69",
          "risk_factors": ["System-wide ID patterns", "Database schema impact", "Backward compatibility"],
          "mitigation_strategy": "Implement with comprehensive testing, validate with existing data"
        },
        {
          "ticket": "PR003946-71",
          "risk_factors": ["Security implementation", "Token processing logic", "Auth middleware integration"],
          "mitigation_strategy": "Security-focused testing, validate with existing auth patterns"
        }
      ],
      "architectural_validation_tickets": [
        {
          "ticket": "PR003946-75",
          "validation_value": "Establishes DynamoDB CRUD patterns for entire system",
          "early_feedback": "Tests table design, error handling, and API response patterns"
        }
      ]
    }
  },

  "selected_optimal_tickets": [
    {
      "rank": 1,
      "ticket": "PR003946-69",
      "title": "Server-generated ID standardization",
      "strategic_justification": "Critical foundation: ID generation patterns needed by ALL create operations in the system",
      "enables": [
        "PR003946-75 (Knowledge CRUD)",
        "PR003946-76 (Knowledge validation)", 
        "PR003946-80 (Family operations)",
        "12+ future create endpoints"
      ],
      "business_value": "Enables consistent entity management across entire platform",
      "complexity": "medium_foundational",
      "estimated_hours": 4,
      "implementation_approach": "Establish UUID patterns with entity-specific prefixes, update dynamo.py utilities",
      "dependencies": "None - pure foundation",
      "parallel_opportunities": "Must complete first",
      "risk_mitigation": "Comprehensive testing with existing data validation"
    },
    {
      "rank": 2,
      "ticket": "PR003946-71", 
      "title": "JWT token validation enhancement",
      "strategic_justification": "Authentication foundation: Required infrastructure for all user-specific and protected operations",
      "enables": [
        "PR003946-72 (Role-based access)",
        "PR003946-80 (Protected family ops)",
        "PR003946-83 (User analytics)",
        "All user-scoped endpoints"
      ],
      "business_value": "Enables secure user operations, role-based access control, and user-specific data",
      "complexity": "medium_security",
      "estimated_hours": 5,
      "implementation_approach": "Enhanced JWT processing in auth middleware, token validation utilities",
      "dependencies": "Can start after PR003946-69 patterns established",
      "parallel_opportunities": "Sequential with ID generation",
      "risk_mitigation": "Security-focused testing, integration with existing auth patterns"
    },
    {
      "rank": 3,
      "ticket": "PR003946-75",
      "title": "Knowledge Management CRUD implementation", 
      "strategic_justification": "Pattern validation: Establishes reusable DynamoDB CRUD template using foundation patterns",
      "enables": [
        "PR003946-76 (Knowledge validation)",
        "Educational content workflows",
        "CRUD patterns for other entities",
        "Content management capabilities"
      ],
      "business_value": "Core educational content management functionality",
      "complexity": "simple_crud",
      "estimated_hours": 3,
      "implementation_approach": "Knowledge table CRUD using established ID generation and auth patterns",
      "dependencies": "Requires PR003946-69 (ID patterns) completion",
      "parallel_opportunities": "Can implement with PR003946-76 after foundations",
      "risk_mitigation": "Validates architectural patterns with lower-risk implementation"
    },
    {
      "rank": 4,
      "ticket": "PR003946-76",
      "title": "Knowledge validation and metadata enhancement",
      "strategic_justification": "Synergy completion: Builds directly on PR003946-75 to complete knowledge management system",
      "enables": [
        "Complete educational content workflows",
        "Content validation patterns for other entities",
        "Metadata handling templates"
      ],
      "business_value": "Complete, production-ready knowledge management system",
      "complexity": "simple_validation",
      "estimated_hours": 2,
      "implementation_approach": "Extend knowledge.py with validation logic, metadata handling, content rules",
      "dependencies": "Requires PR003946-75 (knowledge CRUD) completion",
      "parallel_opportunities": "Can develop simultaneously with PR003946-75",
      "risk_mitigation": "Low risk - builds on proven CRUD patterns"
    },
    {
      "rank": 5,
      "ticket": "PR003946-72",
      "title": "Role-based access control implementation",
      "strategic_justification": "Security completion: Builds on JWT validation to provide complete authentication/authorization system",
      "enables": [
        "Admin-only operations",
        "User-specific data access controls", 
        "Security compliance features",
        "Role-differentiated workflows"
      ],
      "business_value": "Complete security infrastructure enabling role-differentiated user experiences",
      "complexity": "medium_security",
      "estimated_hours": 4,
      "implementation_approach": "Role-checking middleware using JWT validation, permission decorators",
      "dependencies": "Requires PR003946-71 (JWT validation) completion",
      "parallel_opportunities": "Can start after JWT validation complete",
      "risk_mitigation": "Builds on established auth patterns, comprehensive permission testing"
    }
  ],

  "implementation_strategy": {
    "phase_1_foundations": {
      "sequence": "Sequential - must complete in order",
      "tickets": ["PR003946-69", "PR003946-71"],
      "timeline": "7-9 hours total",
      "deliverable": "ID generation patterns + JWT authentication infrastructure",
      "validation": "Test ID generation with sample entities, validate JWT processing"
    },
    "phase_2_knowledge_system": {
      "sequence": "Parallel development possible",
      "tickets": ["PR003946-75", "PR003946-76"], 
      "timeline": "4-5 hours total (can parallelize to 3 hours)",
      "deliverable": "Complete knowledge management CRUD system with validation",
      "validation": "Full CRUD testing, content validation workflows"
    },
    "phase_3_auth_completion": {
      "sequence": "Dependent on JWT validation completion",
      "tickets": ["PR003946-72"],
      "timeline": "4 hours",
      "deliverable": "Complete role-based access control system",
      "validation": "Multi-role testing, permission boundary validation"
    }
  },

  "strategic_benefits": [
    "Foundation-first approach establishes reusable patterns and minimizes rework",
    "Parallel development opportunities in Phase 2 maximize development efficiency",
    "Each completion enables multiple future tickets and reduces implementation complexity",
    "Validates core architectural decisions (ID generation, auth, CRUD patterns) with lower-risk implementations",
    "Delivers complete knowledge management workflow plus full authentication infrastructure",
    "Establishes patterns and utilities that accelerate remaining backlog implementation"
  ],

  "business_value_projection": {
    "immediate_capabilities": [
      "Secure user authentication and role-based access",
      "Complete educational content management system",
      "Consistent entity ID management across platform"
    ],
    "enabled_future_work": [
      "12+ create endpoints can use established ID patterns", 
      "8+ protected endpoints can use auth infrastructure",
      "Content management patterns applicable to media, analytics, family data"
    ],
    "user_workflow_completions": [
      "Educational content creation and management",
      "Secure user login and role-appropriate access",
      "Foundation for family management and analytics"
    ]
  },

  "next_steps_recommendation": {
    "proceed_to_implementation": true,
    "scope_expansion_needed": false,
    "total_estimated_time": "15-18 hours across 3 phases",
    "confidence_level": "high",
    "risk_factors": "Foundation tickets require careful implementation but low overall risk"
  }
}
```

## Success Criteria
- All open Jira tickets analyzed for strategic value and dependencies
- 5 optimal tickets selected using foundation-first, synergy-optimized approach
- Clear dependency mapping showing what each ticket enables
- Implementation sequence with parallel development opportunities identified
- Risk assessment and mitigation strategies for foundational tickets
- Business value projection with specific capability deliveries

## Error Handling
- If Jira API fails, provide analysis based on cached ticket data or manual ticket review
- If sequential reasoning analysis is incomplete, flag specific tickets for manual review
- Save partial strategic analysis if any component fails
- Provide fallback recommendations based on available data