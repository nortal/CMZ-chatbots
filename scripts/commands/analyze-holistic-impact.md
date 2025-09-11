# /analyze-holistic-impact Command

## Purpose
AI-powered analysis of system-wide impact and ripple effects before implementation begins, providing comprehensive understanding of how proposed changes affect the entire project architecture.

## Execution

Use sequential reasoning MCP to perform holistic impact analysis:

**Holistic Impact Analysis Prompt:**
```
Analyze the system-wide impact and ripple effects of the proposed implementation changes using AI-first comprehensive evaluation:

**CURRENT IMPLEMENTATION CONTEXT:**
- **Discovered Tickets**: {ticket_list_from_discovery}
- **Project Health Status**: {health_assessment_results}
- **Architecture Compliance**: {architecture_score}
- **Technical Debt Level**: {debt_assessment}
- **Security Posture**: {security_rating}

**COMPREHENSIVE IMPACT ANALYSIS:**

### 1. **Architecture Impact Assessment**
- **Hexagonal Architecture**: How do changes affect port-adapter boundaries?
- **Domain Boundaries**: Which business domains are affected and how?
- **Dependency Changes**: New dependencies or modifications to existing ones?
- **Pattern Consistency**: Do changes align with or deviate from established patterns?
- **Generated Code Impact**: How do changes interact with OpenAPI generation?

### 2. **Cross-Service Effects Analysis**
- **Service Boundaries**: Which services or modules will be affected?
- **API Contract Changes**: Do changes modify existing API contracts?
- **Data Flow Impact**: How do changes affect data movement through the system?
- **Integration Points**: Which external integrations might be affected?
- **AWS Resource Impact**: Changes to DynamoDB tables, Lambda functions, etc.?

### 3. **Data Impact Assessment**
- **Schema Changes**: Database schema modifications and migration requirements?
- **Data Migration**: Existing data compatibility and migration needs?
- **Access Pattern Changes**: Modifications to how data is read/written?
- **Performance Impact**: Effect on database queries and API response times?
- **Data Privacy**: Impact on PII handling and compliance requirements?

### 4. **Testing Impact Scope**
- **Unit Test Changes**: Which unit tests need updates or additions?
- **Integration Test Expansion**: New integration test requirements?
- **E2E Test Modifications**: End-to-end testing scenario changes?
- **Performance Test Needs**: Performance testing requirements?
- **Security Test Updates**: Security testing scope changes?

### 5. **Deployment and Operations Impact**
- **Infrastructure Changes**: Docker, AWS, or environment configuration updates?
- **Deployment Process**: Changes to build, test, or deployment procedures?
- **Monitoring Requirements**: New monitoring or alerting needs?
- **Configuration Management**: Environment variable or configuration changes?
- **Rollback Considerations**: Rollback complexity and safety measures?

### 6. **Development Workflow Impact**
- **Team Coordination**: Which teams or developers need coordination?
- **Dependency Ordering**: Implementation sequence requirements?
- **Knowledge Sharing**: Documentation or training needs?
- **Review Complexity**: Code review scope and complexity assessment?
- **Timeline Effects**: Impact on other planned development work?

**ANALYSIS METHODOLOGY:**
1. **System Mapping**: Map all components and their relationships
2. **Change Propagation**: Trace how changes ripple through the system
3. **Dependency Analysis**: Identify all affected dependencies
4. **Risk Assessment**: Evaluate implementation risks and mitigation strategies
5. **Resource Planning**: Estimate required resources and timeline impact

**DELIVERABLE REQUIREMENTS:**
```json
{
  "holistic_impact_analysis": {
    "analysis_timestamp": "2025-09-11T17:30:00Z",
    "scope_complexity": "moderate",
    "overall_risk": "medium",
    "coordination_required": true,
    
    "architecture_impact": {
      "severity": "low",
      "hexagonal_compliance": "maintained",
      "domain_boundaries_affected": ["animals", "families"],
      "new_dependencies": 2,
      "pattern_alignment": "consistent",
      "generated_code_changes": "minimal"
    },
    
    "cross_service_effects": [
      {
        "service": "animal_management",
        "impact_type": "api_extension",
        "severity": "low",
        "description": "New endpoint addition, backward compatible"
      },
      {
        "service": "family_management", 
        "impact_type": "data_access_pattern",
        "severity": "medium",
        "description": "Modified data access for cascade operations"
      }
    ],
    
    "data_impact": {
      "schema_changes": false,
      "migration_required": false,
      "access_pattern_changes": true,
      "performance_impact": "minimal",
      "privacy_implications": false
    },
    
    "integration_testing_scope": {
      "estimated_tests": 12,
      "new_test_scenarios": 5,
      "modified_test_scenarios": 7,
      "e2e_test_updates": 3,
      "performance_test_needs": false
    },
    
    "deployment_impact": {
      "infrastructure_changes": false,
      "deployment_process_changes": false,
      "new_monitoring_needs": ["cascade_delete_metrics"],
      "configuration_updates": ["family_table_permissions"],
      "rollback_complexity": "low"
    },
    
    "coordination_requirements": {
      "teams_involved": ["backend_team"],
      "external_dependencies": [],
      "sequential_implementation_required": true,
      "parallel_work_opportunities": ["testing", "documentation"],
      "knowledge_sharing_needs": ["cascade_delete_patterns"]
    }
  },
  
  "risk_assessment": {
    "high_risk_areas": [],
    "medium_risk_areas": [
      {
        "area": "Family data consistency",
        "risk": "Cascade delete operations might affect data integrity",
        "mitigation": "Comprehensive integration testing of delete scenarios",
        "probability": "low",
        "impact": "medium"
      }
    ],
    "low_risk_areas": [
      "New endpoint implementation",
      "OpenAPI specification updates"
    ]
  },
  
  "implementation_strategy": {
    "recommended_sequence": [
      "1. Implement core business logic in impl/ modules",
      "2. Update OpenAPI specifications",
      "3. Regenerate API code",
      "4. Update integration tests",
      "5. Validate all scenarios"
    ],
    "parallel_opportunities": [
      "Documentation updates can happen in parallel",
      "Test case development can start early"
    ],
    "critical_path": ["business_logic", "api_specification", "integration_testing"],
    "estimated_timeline": "16-20 hours total implementation"
  },
  
  "quality_assurance_impact": {
    "additional_test_coverage": 8,
    "code_review_complexity": "moderate",
    "documentation_updates": ["api_docs", "architecture_decisions"],
    "performance_monitoring": ["api_response_times", "database_operations"],
    "security_considerations": ["data_access_controls", "cascade_permissions"]
  },
  
  "recommendations": {
    "before_implementation": [
      "Review cascade delete business rules with stakeholders",
      "Prepare comprehensive test data scenarios",
      "Set up monitoring for new operations"
    ],
    "during_implementation": [
      "Implement business logic first, API changes second",
      "Test each component before integration",
      "Monitor performance during development"
    ],
    "after_implementation": [
      "Validate all cascade scenarios thoroughly",
      "Update operational documentation",
      "Monitor production metrics closely"
    ]
  }
}
```

**ANALYSIS SCOPE:**
- **System-Wide Perspective**: Look beyond individual tickets to overall system impact
- **Ripple Effect Mapping**: Identify all downstream effects of proposed changes
- **Risk-Benefit Analysis**: Evaluate implementation risks vs business value
- **Resource Planning**: Realistic timeline and coordination requirements
- **Quality Impact**: How changes affect overall system quality and maintainability

**SUCCESS CRITERIA:**
- **Comprehensive Impact Map**: All affected system components identified
- **Risk Mitigation Plan**: Clear strategy for managing implementation risks
- **Coordination Plan**: Team and timeline coordination requirements defined
- **Quality Assurance**: Testing and validation scope clearly defined
- **Strategic Alignment**: Changes align with overall system architecture goals
```

## Integration with /nextfive Workflow
- **Post-Discovery Analysis**: Runs after ticket discovery to understand system impact
- **Pre-Implementation Planning**: Informs implementation strategy and sequencing
- **Risk Management**: Provides risk assessment for validation planning
- **Resource Planning**: Estimates coordination and timeline requirements
- **Quality Planning**: Defines comprehensive testing and validation scope

## Success Criteria
- **System-Wide Understanding**: Comprehensive view of change impact across all components
- **Risk-Informed Planning**: Implementation strategy based on thorough risk assessment
- **Coordination Clarity**: Clear understanding of team and timeline coordination needs
- **Quality Assurance Scope**: Comprehensive testing and validation requirements defined
- **Strategic Alignment**: Changes evaluated for consistency with architectural goals