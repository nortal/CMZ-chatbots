# /validate-architecture-compliance Command

## Purpose
AI-powered validation of architecture compliance during the enhanced validation phase, ensuring implementation maintains hexagonal architecture principles and OpenAPI-first development patterns.

## Execution

Use sequential reasoning MCP to perform architecture compliance validation:

**Architecture Compliance Validation Prompt:**
```
Validate architecture compliance of the implemented changes against established architectural principles:

**IMPLEMENTATION CONTEXT:**
- **Recently Implemented Changes**: {implemented_changes_summary}
- **Baseline Architecture Score**: {baseline_architecture_score}
- **Project Patterns**: Hexagonal architecture, OpenAPI-first, AWS DynamoDB integration
- **Quality Gates**: Architecture compliance must be maintained or improved

**COMPREHENSIVE COMPLIANCE VALIDATION:**

### 1. **Hexagonal Architecture Compliance**
- **Boundary Enforcement**: Verify business logic remains in `impl/` directory only
- **Dependency Direction**: Confirm dependencies point inward toward business domain
- **Port-Adapter Pattern**: Validate external concerns are properly isolated
- **Domain Purity**: Check that business logic is free from infrastructure concerns
- **Generated Code Integrity**: Ensure no business logic leaked into generated controllers/models

### 2. **OpenAPI-First Development Compliance**
- **Specification Driven**: Verify all API changes started with OpenAPI spec updates
- **Code Generation Consistency**: Validate generated code matches specifications
- **Backward Compatibility**: Ensure API changes maintain backward compatibility where required
- **Schema Validation**: Confirm request/response schemas are properly enforced
- **Documentation Alignment**: Verify API documentation reflects actual implementation

### 3. **Domain Architecture Validation**
- **Domain Boundary Respect**: Check that changes respect established domain boundaries
- **Cross-Domain Communication**: Validate proper patterns for cross-domain interactions
- **Business Logic Cohesion**: Ensure related business logic is properly grouped
- **Data Access Patterns**: Verify consistent application of data access abstractions
- **Domain Event Handling**: Check for proper domain event patterns where applicable

### 4. **AWS Integration Compliance**
- **DynamoDB Patterns**: Validate consistent use of established DynamoDB access patterns
- **Configuration Management**: Verify proper separation of configuration from code
- **Security Compliance**: Check that AWS integration follows security best practices
- **Resource Usage**: Ensure efficient and appropriate use of AWS services
- **Error Handling**: Validate proper handling of AWS service errors and edge cases

### 5. **Code Organization Compliance**
- **Directory Structure**: Verify changes follow established directory organization
- **Import Patterns**: Check for clean import dependencies and no circular references
- **Naming Conventions**: Validate consistent application of naming patterns
- **Pattern Consistency**: Ensure new code follows established design patterns
- **Documentation Standards**: Check that code changes include appropriate documentation

**VALIDATION METHODOLOGY:**
1. **Before/After Analysis**: Compare pre and post-implementation architecture
2. **Pattern Consistency Check**: Verify new code follows established patterns
3. **Dependency Analysis**: Validate dependency relationships and boundaries
4. **Generated Code Review**: Ensure no inappropriate modifications to generated code
5. **Compliance Scoring**: Quantitative assessment of compliance levels

**DELIVERABLE REQUIREMENTS:**
```json
{
  "architecture_compliance": {
    "validation_timestamp": "2025-09-11T18:00:00Z",
    "overall_status": "compliant",
    "score": 0.88,
    "improvement_from_baseline": 0.03,
    
    "hexagonal_architecture": {
      "score": 0.92,
      "status": "compliant",
      "boundary_enforcement": "excellent",
      "dependency_direction": "correct",
      "port_adapter_pattern": "maintained",
      "domain_purity": "high",
      "generated_code_integrity": "preserved",
      "violations": []
    },
    
    "openapi_first_development": {
      "score": 0.95,
      "status": "compliant",
      "specification_driven": true,
      "code_generation_consistency": "excellent",
      "backward_compatibility": "maintained",
      "schema_validation": "enforced",
      "documentation_alignment": "complete",
      "violations": []
    },
    
    "domain_architecture": {
      "score": 0.85,
      "status": "compliant",
      "boundary_respect": "maintained",
      "cross_domain_communication": "appropriate",
      "business_logic_cohesion": "good",
      "data_access_patterns": "consistent",
      "violations": [
        {
          "area": "impl/animals.py line 45",
          "issue": "Minor coupling to family domain logic",
          "severity": "low",
          "recommendation": "Consider extracting shared logic to common service"
        }
      ]
    },
    
    "aws_integration": {
      "score": 0.90,
      "status": "compliant",
      "dynamodb_patterns": "consistent",
      "configuration_management": "proper",
      "security_compliance": "good",
      "resource_usage": "efficient",
      "error_handling": "comprehensive",
      "violations": []
    },
    
    "code_organization": {
      "score": 0.80,
      "status": "mostly_compliant",
      "directory_structure": "follows_standards",
      "import_patterns": "clean",
      "naming_conventions": "consistent", 
      "pattern_consistency": "good",
      "documentation_standards": "adequate",
      "violations": [
        {
          "area": "impl/utils/family_helpers.py",
          "issue": "Missing docstring for public method",
          "severity": "low",
          "recommendation": "Add comprehensive docstring"
        }
      ]
    }
  },
  
  "compliance_improvements": [
    {
      "area": "Domain architecture",
      "improvement": "Better separation of animal and family domain concerns",
      "impact": "Improved maintainability",
      "effort": "low"
    },
    {
      "area": "Documentation",
      "improvement": "Added comprehensive API documentation",
      "impact": "Better developer experience",
      "effort": "completed"
    }
  ],
  
  "remaining_violations": [
    {
      "severity": "low",
      "count": 2,
      "categories": ["domain_coupling", "documentation"],
      "remediation_effort": "low",
      "impact_on_compliance": "minimal"
    }
  ],
  
  "recommendations": {
    "immediate_fixes": [
      "Add missing docstring to family_helpers.py",
      "Consider extracting shared animal-family logic"
    ],
    "strategic_improvements": [
      "Establish domain event patterns for cross-domain communication",
      "Create architectural decision records for future reference"
    ],
    "monitoring_additions": [
      "Add architecture compliance checks to CI/CD pipeline",
      "Set up alerts for architecture pattern violations"
    ]
  },
  
  "quality_gates": {
    "minimum_score_required": 0.80,
    "current_score": 0.88,
    "gate_status": "passed",
    "critical_violations": 0,
    "blocker_violations": 0,
    "recommendation": "proceed_to_submission"
  }
}
```

**VALIDATION FOCUS AREAS:**
- **Pattern Adherence**: Strict compliance with established architectural patterns
- **Boundary Integrity**: Verification that architectural boundaries remain intact
- **Quality Improvement**: Ensure changes improve or maintain architectural quality
- **Future Maintainability**: Assess impact on long-term system maintainability
- **Standards Compliance**: Adherence to coding and architectural standards

**COMPLIANCE SCORING:**
- **0.90-1.00**: Excellent compliance, architectural best practices followed
- **0.80-0.89**: Good compliance, minor violations that don't affect system integrity
- **0.70-0.79**: Acceptable compliance, some violations requiring attention
- **Below 0.70**: Poor compliance, significant violations requiring immediate attention

**SUCCESS CRITERIA:**
- **Quantitative Assessment**: Clear numerical scores for tracking compliance trends
- **Violation Identification**: Specific issues identified with remediation guidance
- **Quality Gate Integration**: Clear pass/fail criteria for validation pipeline
- **Continuous Improvement**: Recommendations for ongoing architectural enhancement
- **Pattern Preservation**: Verification that established patterns are maintained
```

## Integration with Enhanced Validation Phase
- **Post-Implementation Check**: Validates changes after implementation is complete
- **Quality Gate Function**: Provides pass/fail decision for validation pipeline
- **Compliance Trending**: Tracks architectural compliance over time
- **Feedback Loop**: Identifies areas for architectural improvement
- **Standards Enforcement**: Ensures adherence to established patterns

## Success Criteria
- **Strict Pattern Compliance**: Hexagonal and OpenAPI-first patterns maintained
- **Quality Gate Integration**: Clear criteria for validation pipeline decisions
- **Actionable Feedback**: Specific violations with clear remediation guidance
- **Trend Analysis**: Compliance scoring enables architectural quality tracking
- **Continuous Improvement**: Recommendations drive ongoing architectural enhancement