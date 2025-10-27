# /discover Command (Orchestrator)

## Purpose
Orchestrate both `/discover-tests` and `/discover-jira` then correlate results to create unified work priorities.

## Execution Steps

### Step 1: Run Technical Discovery
```bash
# Execute /discover-tests to get actual failing test data
# This provides the technical reality of what's broken right now
/discover-tests

# Expected output: JSON with failing tickets, categories, and technical details
# Save results to /tmp/discover_tests_YYYYMMDD_HHMMSS.json
```

### Step 2: Run Strategic Discovery  
```bash
# Execute /discover-jira to get strategic ticket prioritization
# This provides business context and dependency analysis
/discover-jira

# Expected output: JSON with strategic analysis and optimal ticket selection
# Save results to /tmp/discover_jira_YYYYMMDD_HHMMSS.json
```

### Step 3: Correlate Results with Sequential Reasoning

Use sequential reasoning MCP to analyze and correlate both data sources:

**Correlation Analysis Prompt:**
```
Correlate technical reality with strategic priorities to create unified implementation plan:

**TECHNICAL REALITY DATA:**
{discover_tests_results}

**STRATEGIC ANALYSIS DATA:**  
{discover_jira_results}

**CORRELATION ANALYSIS REQUIREMENTS:**

1. **Priority Reconciliation:**
   - Where do failing tests align with strategically optimal tickets? (High Priority)
   - Which strategic priorities don't have failing tests? (Should we still include?)
   - Are there failing tests for tickets not in strategic top 5? (Lower priority?)
   - How do we balance "fix what's broken" vs "build what's strategic"?

2. **Implementation Feasibility Assessment:**
   - Do the failing tests provide clear implementation guidance?
   - Are the strategic priorities achievable given current technical debt?
   - Which approach (fix-first vs strategy-first) minimizes overall effort?
   - Are there quick wins from failing tests that enable strategic work?

3. **Unified Priority Ranking:**
   - Create single prioritized list considering both technical needs and strategic value
   - Weight factors: business impact, technical enablement, implementation ease, risk level
   - Identify tickets that satisfy both "failing test" AND "strategic priority" criteria
   - Recommend approach for handling mismatches

4. **Risk and Dependency Validation:**
   - Do failing tests reveal dependency issues not captured in strategic analysis?
   - Are there technical blockers that affect strategic implementation sequence?
   - Which combination provides the most stable foundation for future work?

5. **Implementation Strategy Optimization:**
   - Can we achieve both "fix failing tests" and "strategic progress" in same effort?
   - What's the optimal sequence that addresses both concerns?
   - Are there synergies between fixing technical debt and building strategic capabilities?

**DELIVERABLE REQUIREMENTS:**

1. **Unified Priority List**: Single ranked list of next 5 tickets considering both technical and strategic factors
2. **Correlation Analysis**: Clear explanation of how technical and strategic priorities align or conflict  
3. **Implementation Approach**: Recommended strategy for balancing fix-what's-broken vs build-what's-strategic
4. **Risk Assessment**: How the unified approach manages both technical debt and strategic progress
5. **Success Metrics**: Clear criteria for measuring progress on both technical quality and strategic goals
```

### Step 4: Generate Unified Implementation Plan

Output correlated analysis and final recommendations:

```json
{
  "session_id": "discover_correlation_YYYYMMDD_HHMMSS",
  "correlation_timestamp": "2025-09-11T13:00:00Z",
  
  "input_summary": {
    "technical_reality": {
      "failing_tests": 5,
      "failing_tickets": ["PR003946-75", "PR003946-76", "PR003946-78", "PR003946-82", "PR003946-85"],
      "primary_issues": ["missing_endpoints", "validation_errors"],
      "estimated_fix_time": "6-8 hours"
    },
    "strategic_priorities": {
      "optimal_tickets": ["PR003946-69", "PR003946-71", "PR003946-75", "PR003946-76", "PR003946-72"],
      "foundation_focus": ["ID generation", "JWT validation"],
      "strategic_approach": "foundations_first",
      "estimated_time": "15-18 hours"
    }
  },

  "correlation_analysis": {
    "alignment_matches": [
      {
        "ticket": "PR003946-75",
        "alignment": "perfect",
        "reason": "Failing test AND strategic priority - knowledge CRUD implementation",
        "priority_boost": "Both technical debt and strategic value"
      },
      {
        "ticket": "PR003946-76", 
        "alignment": "perfect",
        "reason": "Failing test AND strategic priority - knowledge validation logic",
        "priority_boost": "Completes knowledge system while fixing technical issues"
      }
    ],
    
    "strategic_only": [
      {
        "ticket": "PR003946-69",
        "status": "strategic_priority_no_failing_test",
        "justification": "Foundation ticket - ID generation needed by failing tickets",
        "include_reason": "Enables fixing technical debt more effectively"
      },
      {
        "ticket": "PR003946-71",
        "status": "strategic_priority_no_failing_test", 
        "justification": "Foundation ticket - JWT validation enables protected endpoints",
        "include_reason": "Required infrastructure for several failing tests"
      }
    ],

    "technical_only": [
      {
        "ticket": "PR003946-78",
        "status": "failing_test_not_strategic_priority",
        "decision": "defer",
        "reason": "Can be addressed after foundational work reduces implementation complexity"
      },
      {
        "ticket": "PR003946-82", 
        "status": "failing_test_not_strategic_priority",
        "decision": "defer",
        "reason": "Lower strategic value, can be grouped with similar tickets later"
      }
    ]
  },

  "unified_approach_strategy": {
    "approach": "foundation_enabled_fix_strategy",
    "rationale": "Build strategic foundations that make fixing technical debt easier and more sustainable",
    "benefits": [
      "Foundation tickets (ID generation, JWT) enable cleaner fixes for failing tests",
      "Avoid technical debt by establishing proper patterns before fixing symptoms", 
      "Strategic priorities align with 40% of failing tests (2 of 5)",
      "Remaining failing tests become easier to fix with established foundations"
    ]
  },

  "final_unified_priorities": [
    {
      "rank": 1,
      "ticket": "PR003946-69",
      "title": "Server-generated ID standardization",
      "rationale": "Foundation enabler: Required by failing PR003946-75, PR003946-76 for proper implementation",
      "addresses": "strategic_foundation + technical_debt_prevention",
      "impact": "Enables clean implementation of 2 failing tests plus future work",
      "estimated_hours": 4
    },
    {
      "rank": 2, 
      "ticket": "PR003946-71",
      "title": "JWT token validation enhancement", 
      "rationale": "Security foundation: Enables proper auth patterns for protected endpoints",
      "addresses": "strategic_foundation + future_technical_debt_prevention",
      "impact": "Infrastructure for user-specific operations and secure endpoint access",
      "estimated_hours": 5
    },
    {
      "rank": 3,
      "ticket": "PR003946-75",
      "title": "Knowledge Management CRUD implementation",
      "rationale": "Perfect alignment: Fixes failing test AND strategic priority using established foundations",
      "addresses": "failing_test + strategic_value + pattern_establishment",
      "impact": "Resolves technical debt while delivering business value and establishing CRUD patterns",
      "estimated_hours": 3
    },
    {
      "rank": 4,
      "ticket": "PR003946-76", 
      "title": "Knowledge validation and metadata",
      "rationale": "Perfect alignment: Fixes failing test AND completes strategic knowledge system",
      "addresses": "failing_test + strategic_completion + validation_patterns",
      "impact": "Resolves technical debt while completing knowledge management capability",
      "estimated_hours": 2
    },
    {
      "rank": 5,
      "ticket": "PR003946-72",
      "title": "Role-based access control",
      "rationale": "Strategic completion: Completes authentication system using JWT foundation",
      "addresses": "strategic_completion + security_infrastructure",
      "impact": "Complete auth/authz system enabling user-differentiated workflows",
      "estimated_hours": 4
    }
  ],

  "implementation_sequence": {
    "phase_1_foundations": {
      "tickets": ["PR003946-69", "PR003946-71"],
      "approach": "sequential_required",
      "outcome": "Establishes ID and auth patterns for clean technical debt resolution"
    },
    "phase_2_aligned_fixes": {
      "tickets": ["PR003946-75", "PR003946-76"],
      "approach": "parallel_possible", 
      "outcome": "Fixes failing tests using established patterns, delivers business value"
    },
    "phase_3_completion": {
      "tickets": ["PR003946-72"],
      "approach": "dependent_on_jwt",
      "outcome": "Completes strategic authentication infrastructure"
    }
  },

  "deferred_work_plan": {
    "remaining_failing_tests": ["PR003946-78", "PR003946-82", "PR003946-85"],
    "handling_strategy": "address_in_next_cycle", 
    "rationale": "Can be implemented more efficiently after foundations are established",
    "estimated_effort_reduction": "30-40% easier with proper patterns in place"
  },

  "success_metrics": {
    "technical_debt_reduction": "2 of 5 failing tests resolved using clean patterns",
    "strategic_progress": "Complete knowledge management system + auth infrastructure",
    "foundation_enablement": "ID generation + JWT patterns enable efficient future development",
    "business_value": "Educational content management + secure user operations",
    "efficiency_gain": "Remaining technical debt becomes easier to resolve"
  },

  "recommendation": {
    "proceed_with_unified_plan": true,
    "total_estimated_time": "18 hours across 3 phases",
    "confidence_level": "high",
    "next_command": "/implement with foundation-first approach"
  }
}
```

## Success Criteria
- Both technical reality and strategic priorities analyzed and correlated
- Unified priority list that optimally balances fixing technical debt with strategic progress
- Clear rationale for how selected tickets address both immediate needs and long-term goals
- Implementation sequence that leverages foundations to make technical debt resolution more efficient
- Deferred work plan showing how remaining issues will be addressed more effectively later

## Error Handling
- If either sub-command fails, provide analysis based on available data
- If correlation analysis is inconclusive, present both perspectives for manual decision
- Save individual results even if correlation fails  
- Provide fallback recommendations based on partial data