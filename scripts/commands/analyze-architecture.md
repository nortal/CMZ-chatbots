# /analyze-architecture Command

## Purpose
AI-powered comprehensive analysis of system architecture patterns, compliance with hexagonal architecture principles, and identification of architectural debt.

## Execution

Use sequential reasoning MCP to perform comprehensive architecture analysis:

**Architecture Analysis Prompt:**
```
Analyze the CMZ chatbot system architecture comprehensively using AI-first principles:

**PROJECT CONTEXT:**
- **Architecture Pattern**: Hexagonal architecture with OpenAPI-first development
- **Core Technologies**: Python Flask, OpenAPI 3.0, AWS DynamoDB, Docker
- **Key Constraint**: All business logic must be in `impl/` directory, never in generated code
- **Domain Boundaries**: Animals, Families, Users, Conversations, Knowledge, Auth

**COMPREHENSIVE ANALYSIS REQUIRED:**

### 1. **Hexagonal Architecture Compliance**
- **Port-Adapter Analysis**: Examine separation between business logic and external concerns
- **Dependency Direction**: Verify dependencies point inward toward business domain
- **Boundary Enforcement**: Check that `impl/` contains only business logic
- **Generated Code Isolation**: Verify controllers/models are never modified directly

### 2. **OpenAPI-First Compliance**
- **Specification Driven**: Verify all APIs defined in `openapi_spec.yaml` first
- **Code Generation Integrity**: Check generated code consistency with spec
- **API Evolution**: Assess backward compatibility and versioning
- **Schema Consistency**: Validate models match API specifications

### 3. **Domain Architecture Analysis**  
- **Domain Boundaries**: Analyze separation between business domains
- **Cross-Domain Dependencies**: Identify and evaluate domain interactions
- **Cohesion Assessment**: Measure domain internal cohesion
- **Coupling Analysis**: Identify unnecessary coupling between domains

### 4. **AWS Integration Architecture**
- **DynamoDB Patterns**: Analyze data access patterns and table design
- **AWS Service Integration**: Evaluate serverless and cloud-native patterns
- **Configuration Management**: Review environment and secrets handling
- **Scalability Readiness**: Assess architecture scalability characteristics

### 5. **Code Organization Patterns**
- **Directory Structure**: Evaluate organization effectiveness
- **Import Patterns**: Analyze dependency management and circular imports
- **Pattern Consistency**: Check consistent application of design patterns
- **Technical Debt**: Identify architectural debt and improvement opportunities

**ANALYSIS METHODOLOGY:**
1. **Read Project Structure**: Use file system tools to understand organization
2. **Examine Key Files**: Analyze critical architecture files and patterns
3. **Dependency Analysis**: Map actual vs intended dependency relationships
4. **Pattern Recognition**: Identify consistent vs inconsistent architectural patterns
5. **Compliance Scoring**: Rate compliance with architectural principles (0-1.0 scale)

**DELIVERABLE REQUIREMENTS:**
```json
{
  "architecture_analysis": {
    "analysis_timestamp": "2025-09-11T17:30:00Z",
    "compliance_score": 0.85,
    "hexagonal_architecture": {
      "score": 0.90,
      "port_adapter_compliance": "high",
      "dependency_direction": "correct",
      "boundary_violations": 2,
      "business_logic_isolation": "excellent"
    },
    "openapi_first": {
      "score": 0.95,
      "specification_driven": true,
      "code_generation_integrity": "high",
      "api_evolution_readiness": "good",
      "schema_consistency": "excellent"
    },
    "domain_architecture": {
      "score": 0.80,
      "domain_boundaries": "clear",
      "cross_domain_coupling": "acceptable",
      "cohesion_level": "high",
      "coupling_level": "low"
    },
    "aws_integration": {
      "score": 0.85,
      "dynamodb_patterns": "consistent",
      "cloud_native_readiness": "high",
      "configuration_management": "secure",
      "scalability_readiness": "good"
    },
    "code_organization": {
      "score": 0.75,
      "directory_structure": "logical",
      "import_patterns": "mostly_clean",
      "pattern_consistency": "good",
      "technical_debt_level": "moderate"
    }
  },
  "architectural_debt": {
    "high_priority_issues": [
      {
        "area": "impl/animals.py",
        "issue": "Business logic mixed with data access",
        "impact": "medium",
        "effort": "low"
      }
    ],
    "improvement_opportunities": [
      {
        "area": "Cross-domain communication",
        "opportunity": "Implement domain events pattern",
        "benefit": "Reduced coupling, better testability",
        "effort": "medium"
      }
    ]
  },
  "recommendations": {
    "immediate_actions": [
      "Refactor mixed concerns in animals domain",
      "Establish domain event patterns"
    ],
    "strategic_improvements": [
      "Implement CQRS for read/write separation",
      "Add domain service layer"
    ],
    "architectural_evolution": [
      "Consider microservices extraction points",
      "Evaluate event sourcing for audit requirements"
    ]
  }
}
```

**FOCUS AREAS:**
- **Practical Assessment**: Real architecture state vs intended patterns
- **Actionable Insights**: Specific improvements with effort/benefit analysis  
- **Compliance Measurement**: Quantitative scores for tracking improvement
- **Evolution Guidance**: Strategic direction for architectural growth

Perform comprehensive analysis and generate structured JSON results for downstream use in quality gates and decision making.
```

## Success Criteria
- **Comprehensive Coverage**: All architectural dimensions analyzed systematically
- **Quantitative Scoring**: Numerical compliance scores for trend tracking
- **Actionable Recommendations**: Specific improvements with effort estimates
- **JSON Output**: Structured results for integration with other validation steps
- **AI-First Approach**: Leverage AI reasoning for pattern recognition and debt identification

## Integration Notes
- Results used by enhanced validation phase for architecture compliance checking
- Compliance scores influence quality gate decisions
- Recommendations feed into scope expansion if architectural improvements needed
- Historical analysis enables architectural trend tracking over time