# /measure-technical-debt Command

## Purpose
AI-powered assessment of technical debt across code quality, maintainability, and development velocity impact dimensions.

## Execution

Use sequential reasoning MCP to perform comprehensive technical debt measurement:

**Technical Debt Assessment Prompt:**
```
Analyze technical debt in the CMZ chatbot project using AI-first comprehensive evaluation:

**PROJECT CONTEXT:**
- **Technology Stack**: Python Flask, OpenAPI generation, AWS DynamoDB, Docker
- **Development Pattern**: Generated code + `impl/` business logic separation  
- **Quality Requirements**: Maintainable, scalable, secure chatbot platform
- **Business Critical**: Educational platform for zoo visitors

**COMPREHENSIVE TECHNICAL DEBT ANALYSIS:**

### 1. **Code Quality Debt**
- **Code Duplication**: Identify repeated code patterns and consolidation opportunities
- **Complexity Analysis**: Measure cyclomatic complexity and maintainability
- **Code Smells**: Detect long methods, large classes, inappropriate intimacy
- **Documentation Debt**: Assess missing or outdated documentation
- **Test Coverage**: Evaluate test completeness and quality

### 2. **Architectural Debt**  
- **Design Pattern Violations**: Identify deviations from intended patterns
- **Dependency Issues**: Circular dependencies, inappropriate coupling
- **Abstraction Debt**: Missing abstractions or over-abstraction
- **Technology Debt**: Outdated dependencies or inappropriate technology choices
- **Scalability Constraints**: Architecture limitations affecting growth

### 3. **Development Velocity Debt**
- **Build System Issues**: Slow or unreliable build/deployment processes
- **Development Environment**: Setup complexity and maintenance overhead
- **Debugging Difficulty**: Code that is hard to troubleshoot
- **Feature Implementation Speed**: How debt affects new feature development
- **Knowledge Transfer**: Code that is difficult for new developers

### 4. **Maintenance Debt**
- **Bug Fix Difficulty**: How hard it is to fix issues
- **Change Impact**: Ripple effects of modifications
- **Configuration Complexity**: Environment and deployment configuration debt
- **Monitoring Gaps**: Observability and debugging limitations
- **Security Maintenance**: Security update and vulnerability management debt

**MEASUREMENT METHODOLOGY:**
1. **Quantitative Analysis**: Use static analysis tools and metrics
2. **Pattern Recognition**: Identify recurring debt patterns
3. **Impact Assessment**: Measure debt impact on development velocity
4. **Trend Analysis**: Compare with historical debt levels if available
5. **Priority Scoring**: Rank debt by impact and remediation effort

**DELIVERABLE REQUIREMENTS:**
```json
{
  "technical_debt_assessment": {
    "analysis_timestamp": "2025-09-11T17:30:00Z",
    "overall_level": "moderate",
    "debt_score": 0.65,
    "velocity_impact": "medium",
    
    "code_quality_debt": {
      "score": 0.70,
      "duplication_percentage": 12.5,
      "average_complexity": 6.8,
      "critical_code_smells": 8,
      "documentation_coverage": 0.45,
      "test_coverage": 0.78
    },
    
    "architectural_debt": {
      "score": 0.75,
      "pattern_violations": 5,
      "circular_dependencies": 2,
      "abstraction_issues": 3,
      "technology_currency": 0.80,
      "scalability_constraints": 4
    },
    
    "development_velocity_debt": {
      "score": 0.60,
      "build_time_seconds": 120,
      "environment_setup_complexity": "moderate",
      "debugging_difficulty": "medium",
      "feature_implementation_slowdown": 1.4,
      "knowledge_transfer_difficulty": "medium"
    },
    
    "maintenance_debt": {
      "score": 0.55,
      "bug_fix_difficulty": "medium",
      "change_ripple_effect": "high", 
      "configuration_complexity": "moderate",
      "monitoring_coverage": 0.60,
      "security_update_difficulty": "low"
    }
  },
  
  "high_impact_debt": [
    {
      "area": "impl/animals.py",
      "type": "code_quality",
      "issue": "Method complexity > 15, difficult to test",
      "velocity_impact": "high",
      "remediation_effort": "medium",
      "priority": 1
    },
    {
      "area": "DynamoDB access patterns",
      "type": "architectural", 
      "issue": "Inconsistent data access abstraction",
      "velocity_impact": "medium",
      "remediation_effort": "high",
      "priority": 2
    }
  ],
  
  "refactoring_opportunities": [
    {
      "opportunity": "Extract common DynamoDB patterns",
      "effort": "medium",
      "benefit": "high",
      "affected_files": 8,
      "estimated_hours": 16
    },
    {
      "opportunity": "Consolidate duplicate validation logic",
      "effort": "low",
      "benefit": "medium", 
      "affected_files": 5,
      "estimated_hours": 6
    }
  ],
  
  "debt_trends": {
    "trend_direction": "stable",
    "debt_accumulation_rate": "slow",
    "remediation_rate": "moderate",
    "net_debt_change": "slight_decrease"
  },
  
  "recommendations": {
    "immediate_actions": [
      "Refactor high-complexity methods in animals domain",
      "Add missing unit tests for core business logic"
    ],
    "strategic_improvements": [
      "Establish DynamoDB access pattern library",
      "Implement automated complexity monitoring"
    ],
    "process_improvements": [
      "Add debt tracking to PR review process", 
      "Schedule regular technical debt review sessions"
    ]
  }
}
```

**ANALYSIS TOOLS INTEGRATION:**
- **Static Analysis**: Integrate with Python linting tools (flake8, pylint)
- **Complexity Metrics**: Use radon or similar for cyclomatic complexity
- **Duplication Detection**: Leverage code duplication detection tools
- **Dependency Analysis**: Analyze import patterns and dependency graphs
- **Git Analytics**: Examine code churn and change frequency patterns

**SUCCESS CRITERIA:**
- **Quantitative Measurement**: Numerical scores for tracking improvement
- **Actionable Prioritization**: Clear priority ranking for debt remediation
- **Business Impact**: Connect technical debt to development velocity impact
- **Trend Analysis**: Historical context for debt accumulation patterns
- **ROI Analysis**: Effort vs benefit analysis for remediation opportunities
```

## Integration with /nextfive Workflow
- **Health Assessment Phase**: Establishes technical debt baseline
- **Discovery Phase**: Influences ticket prioritization based on debt impact
- **Validation Phase**: Compares post-implementation debt levels
- **Learning Phase**: Tracks debt trends and remediation effectiveness

## Success Criteria
- **Comprehensive Assessment**: All debt dimensions measured systematically  
- **Business Alignment**: Debt impact connected to development velocity
- **Actionable Priorities**: Clear remediation roadmap with effort estimates
- **Trend Tracking**: Historical debt analysis for continuous improvement
- **Quality Gates Integration**: Debt thresholds for validation decisions