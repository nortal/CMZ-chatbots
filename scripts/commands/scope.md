# /scope Command

## Purpose
If fewer than 5 tickets are discovered, analyze OpenAPI spec and codebase to identify additional implementation opportunities.

## Execution Steps

### Step 1: Analyze Current Discovery Results
```bash
# Check if we have fewer than 5 tickets from discovery
DISCOVERED_COUNT=$(jq -r '.selected_optimal_tickets | length' /tmp/discover_correlation_*.json 2>/dev/null || echo "0")

if [[ "$DISCOVERED_COUNT" -ge 5 ]]; then
    echo "✅ Sufficient work identified ($DISCOVERED_COUNT tickets). Scope expansion not needed."
    exit 0
fi

echo "🔍 Only $DISCOVERED_COUNT tickets discovered. Expanding scope to find additional opportunities..."
```

### Step 2: OpenAPI Spec Analysis
```bash
# Examine OpenAPI spec for unimplemented endpoints
echo "📋 Analyzing OpenAPI specification for missing implementations..."

# Extract all endpoint paths
grep -A 2 -B 2 "paths:" backend/api/openapi_spec.yaml
grep -E "(get:|post:|put:|delete:)" backend/api/openapi_spec.yaml | head -20

# Look for endpoints without corresponding impl files
ls backend/api/src/main/python/openapi_server/impl/*.py
```

### Step 3: Sequential Reasoning Expansion Analysis

Use sequential reasoning MCP to identify expansion opportunities:

**Expansion Analysis Prompt:**
```
Identify additional implementation opportunities to reach 5 total tickets:

**CURRENT SITUATION:**
- Discovered tickets: {current_discovered_tickets}
- Current count: {discovered_count}
- Need additional: {5 - discovered_count} tickets

**AVAILABLE DATA:**
- OpenAPI Specification: {openapi_endpoints_analysis}
- Current Implementations: {impl_directory_contents}
- Existing Patterns: {established_patterns}

**EXPANSION ANALYSIS:**

1. **Missing Endpoint Opportunities:**
   - Which OpenAPI endpoints lack implementation files?
   - Are there CRUD operations that are partially implemented?
   - What endpoints would complement the already discovered work?

2. **Enhancement Opportunities:**
   - Which existing implementations could be enhanced or extended?
   - Are there validation, error handling, or feature gaps?
   - What would make current implementations more complete?

3. **Infrastructure Opportunities:**
   - What shared utilities or middleware could benefit multiple endpoints?
   - Are there testing, logging, or monitoring capabilities missing?
   - What would improve developer experience or system reliability?

4. **Business Value Opportunities:**
   - What user workflows are incomplete due to missing endpoints?
   - Which additional implementations would unlock significant business value?
   - Are there admin, analytics, or operational capabilities missing?

**SELECTION CRITERIA:**
- Complement existing discovered work (synergies)
- Reasonable implementation effort (2-4 hours each)
- Clear business or technical value
- Build on established patterns where possible

**DELIVERABLE:**
Select {5 - discovered_count} additional tickets with:
- Clear implementation approach
- Synergy with discovered work
- Realistic effort estimates
- Business value justification
```

### Step 4: Expanded Scope Output

```json
{
  "session_id": "scope_expansion_YYYYMMDD_HHMMSS",
  "original_discovered_count": 3,
  "expansion_target": 5,
  "additional_needed": 2,
  
  "expansion_opportunities": [
    {
      "category": "missing_endpoints",
      "opportunities": [
        {
          "endpoint": "GET /api/v1/media",
          "implementation_effort": "2-3 hours",
          "synergy": "Uses same CRUD patterns as knowledge management",
          "business_value": "Media asset browsing capability"
        },
        {
          "endpoint": "POST /api/v1/analytics/events",
          "implementation_effort": "2-3 hours", 
          "synergy": "Uses established ID generation and auth patterns",
          "business_value": "Usage tracking and analytics foundation"
        }
      ]
    },
    {
      "category": "enhancement_opportunities", 
      "opportunities": [
        {
          "enhancement": "Family member invitation system",
          "implementation_effort": "3-4 hours",
          "synergy": "Builds on family management and auth infrastructure",
          "business_value": "Complete family onboarding workflow"
        }
      ]
    }
  ],

  "selected_additional_tickets": [
    {
      "ticket": "NEW-MEDIA-01",
      "title": "Media Management CRUD Implementation",
      "rationale": "Complements knowledge management, uses established CRUD patterns",
      "estimated_hours": 3,
      "synergies": ["DynamoDB patterns", "ID generation", "Error handling"],
      "business_value": "Media asset management for educational content"
    },
    {
      "ticket": "NEW-ANALYTICS-01", 
      "title": "Basic Analytics Events Collection",
      "rationale": "Uses auth and ID foundations, enables future analytics features",
      "estimated_hours": 3,
      "synergies": ["JWT validation", "ID generation", "Event logging patterns"],
      "business_value": "Usage tracking foundation for system optimization"
    }
  ],

  "final_expanded_scope": {
    "total_tickets": 5,
    "original_discovered": 3,
    "newly_identified": 2,
    "total_estimated_time": "20-24 hours",
    "implementation_approach": "Build new tickets using patterns established by discovered work"
  },

  "implementation_integration": {
    "sequence": "Implement discovered foundational work first, then use established patterns for new tickets",
    "synergy_benefits": "New tickets leverage foundations and patterns from discovered work",
    "risk_mitigation": "Lower risk implementations that build on proven patterns"
  }
}
```

## Success Criteria
- Identified sufficient additional work to reach 5 total tickets
- New opportunities complement and synergize with discovered work
- Realistic effort estimates based on established patterns
- Clear business value for additional implementations
- Integration plan showing how new work builds on discovered foundations

## Error Handling
- If OpenAPI analysis fails, focus on codebase enhancement opportunities
- If no additional opportunities identified, proceed with discovered work only
- Save expansion analysis even if target count not reached