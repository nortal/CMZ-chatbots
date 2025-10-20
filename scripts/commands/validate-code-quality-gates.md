# /validate-code-quality-gates Command

## Purpose
AI-powered validation of code quality gates using GitHub pipeline integration, leveraging existing linting, SAST, and code quality tools for comprehensive quality assessment.

## Execution

Use sequential reasoning MCP to perform code quality gate validation with GitHub integration:

**Code Quality Gates Validation Prompt:**
```
Validate code quality gates for implemented changes using GitHub pipeline integration and AI-enhanced quality assessment:

**INTEGRATION CONTEXT:**
- **GitHub Pipeline Tools**: CodeQL SAST, Dependabot, GitHub Advanced Security
- **Python Linting**: flake8, pylint, black formatting, mypy type checking
- **Security Scanning**: Existing SAST configuration and security alerts
- **Quality Baselines**: Established from project health assessment
- **Implementation Changes**: {implemented_changes_summary}

**COMPREHENSIVE QUALITY GATES VALIDATION:**

### 1. **GitHub Pipeline Integration**
- **SAST Results**: Pull and analyze current CodeQL security findings
- **Dependency Scanning**: Review Dependabot alerts and vulnerability status
- **Secret Scanning**: Check for any exposed secrets in recent changes
- **Security Advisories**: Assess impact of GitHub security advisories
- **Automated Checks**: Validate that all automated security checks pass

### 2. **Python Code Quality Validation**
- **Linting Compliance**: flake8 and pylint results for new/modified code
- **Code Formatting**: Black formatting compliance and consistency
- **Type Checking**: mypy type checking results and type safety
- **Import Organization**: Import sorting and dependency management
- **Docstring Quality**: Documentation completeness and quality

### 3. **Security Quality Gates**
- **Vulnerability Assessment**: Analysis of security vulnerabilities in changes
- **Input Validation**: Verification of proper input sanitization and validation
- **Authentication/Authorization**: Security controls in new endpoints
- **Data Protection**: PII handling and data security compliance
- **Error Handling**: Security-conscious error handling patterns

### 4. **Code Complexity and Maintainability**
- **Cyclomatic Complexity**: Complexity metrics for new/modified functions
- **Code Duplication**: Detection of duplicated code patterns
- **Method Length**: Validation of method and function size guidelines
- **Class Design**: Object-oriented design principle compliance
- **Test Coverage**: Unit test coverage for new functionality

### 5. **Performance and Efficiency**
- **Algorithm Efficiency**: Analysis of algorithmic complexity
- **Resource Usage**: Memory and CPU efficiency assessment
- **Database Query Optimization**: DynamoDB query pattern efficiency
- **API Response Time**: Performance implications of changes
- **Scalability Considerations**: Impact on system scalability

**VALIDATION METHODOLOGY:**
1. **GitHub API Integration**: Pull security scan results and alerts
2. **Static Analysis Integration**: Run and analyze Python linting tools
3. **AI-Enhanced Review**: AI analysis of code quality beyond automated tools
4. **Baseline Comparison**: Compare metrics against project health baseline
5. **Quality Scoring**: Quantitative assessment with pass/fail thresholds

**DELIVERABLE REQUIREMENTS:**
```json
{
  "quality_gates": {
    "validation_timestamp": "2025-09-11T18:00:00Z",
    "overall_score": 0.85,
    "gate_status": "passed",
    "critical_issues": 0,
    
    "github_pipeline_results": {
      "sast_scan": {
        "status": "passed",
        "critical_findings": 0,
        "medium_findings": 1,
        "low_findings": 2,
        "new_findings": 0
      },
      "dependency_scanning": {
        "status": "passed",
        "vulnerable_dependencies": 0,
        "security_advisories": 1,
        "auto_updates_applied": 2
      },
      "secret_scanning": {
        "status": "passed",
        "exposed_secrets": 0,
        "false_positives": 1
      },
      "automated_checks": {
        "all_passing": true,
        "failed_checks": []
      }
    },
    
    "python_code_quality": {
      "score": 0.88,
      "linting": {
        "flake8_score": 9.5,
        "pylint_score": 8.8,
        "violations": 3,
        "critical_violations": 0
      },
      "formatting": {
        "black_compliant": true,
        "formatting_violations": 0
      },
      "type_checking": {
        "mypy_score": 0.92,
        "type_errors": 0,
        "type_warnings": 2
      },
      "documentation": {
        "docstring_coverage": 0.85,
        "missing_docstrings": 2,
        "quality_score": 0.80
      }
    },
    
    "security_quality": {
      "score": 0.90,
      "vulnerability_count": 0,
      "input_validation": "comprehensive",
      "authentication_security": "implemented",
      "data_protection": "compliant",
      "error_handling": "secure",
      "security_debt": "low"
    },
    
    "complexity_maintainability": {
      "score": 0.82,
      "average_complexity": 4.2,
      "high_complexity_methods": 1,
      "code_duplication": 0.05,
      "method_length_violations": 0,
      "design_principle_compliance": 0.85,
      "test_coverage": 0.78
    },
    
    "performance_efficiency": {
      "score": 0.80,
      "algorithm_efficiency": "good",
      "resource_usage": "efficient",
      "database_queries": "optimized",
      "api_response_impact": "minimal",
      "scalability_impact": "positive"
    }
  },
  
  "quality_improvements": [
    {
      "area": "Test coverage",
      "improvement": "Added comprehensive unit tests for new endpoints",
      "baseline": 0.65,
      "current": 0.78,
      "impact": "Better reliability and maintainability"
    },
    {
      "area": "Type safety",
      "improvement": "Enhanced type annotations for better IDE support",
      "baseline": 0.70,
      "current": 0.92,
      "impact": "Improved developer experience and error prevention"
    }
  ],
  
  "remaining_issues": [
    {
      "category": "documentation",
      "issue": "Missing docstrings for 2 public methods",
      "severity": "low",
      "impact": "Developer experience",
      "remediation": "Add comprehensive docstrings",
      "effort": "low"
    },
    {
      "category": "complexity",
      "issue": "One method has complexity score of 12 (threshold: 10)",
      "severity": "medium", 
      "impact": "Maintainability",
      "remediation": "Refactor method into smaller functions",
      "effort": "medium"
    }
  ],
  
  "gate_thresholds": {
    "minimum_overall_score": 0.75,
    "maximum_critical_issues": 0,
    "maximum_security_vulnerabilities": 0,
    "minimum_test_coverage": 0.70,
    "maximum_complexity_violations": 2
  },
  
  "gate_decisions": {
    "security_gate": "passed",
    "quality_gate": "passed", 
    "performance_gate": "passed",
    "maintainability_gate": "passed",
    "overall_decision": "approved_for_submission"
  },
  
  "recommendations": {
    "before_submission": [
      "Address high complexity method in impl/animals.py",
      "Add missing docstrings for public methods"
    ],
    "continuous_improvement": [
      "Increase unit test coverage to 85%+",
      "Set up automated complexity monitoring",
      "Implement pre-commit hooks for quality checks"
    ],
    "monitoring_setup": [
      "Add quality metrics to development dashboard",
      "Set up alerts for quality regression",
      "Schedule regular technical debt review"
    ]
  }
}
```

**GITHUB INTEGRATION COMMANDS:**
```bash
# Pull SAST results
gh api repos/nortal/CMZ-chatbots/code-scanning/alerts --field state=open

# Check dependency vulnerabilities  
gh api repos/nortal/CMZ-chatbots/dependabot/alerts --field state=open

# Review security advisories
gh api repos/nortal/CMZ-chatbots/security-advisories

# Get workflow run status
gh run list --workflow=".github/workflows/security.yml" --limit=1
```

**PYTHON QUALITY COMMANDS:**
```bash
# Run linting
flake8 backend/api/src/main/python/ --statistics
pylint backend/api/src/main/python/openapi_server/impl/

# Check formatting
black --check backend/api/src/main/python/

# Type checking
mypy backend/api/src/main/python/openapi_server/impl/

# Test coverage
pytest --cov=openapi_server --cov-report=json
```

**QUALITY GATE CRITERIA:**
- **Security**: Zero critical vulnerabilities, all SAST checks passing
- **Code Quality**: Minimum 0.75 overall score, adherence to linting standards
- **Test Coverage**: Minimum 70% coverage for new/modified code
- **Complexity**: Maximum cyclomatic complexity of 10 per method
- **Documentation**: All public methods have docstrings

**SUCCESS CRITERIA:**
- **GitHub Pipeline Integration**: Leverages existing security and quality infrastructure
- **Comprehensive Assessment**: Covers security, quality, performance, and maintainability
- **Quantitative Scoring**: Clear metrics for quality trend tracking
- **Actionable Feedback**: Specific issues with remediation guidance
- **Gate Integration**: Clear pass/fail criteria for validation pipeline
```

## GitHub Pipeline Integration Benefits
- **Leverages Existing Investment**: Uses established GitHub Advanced Security tools
- **Automated Security Scanning**: Integrates CodeQL SAST and dependency scanning
- **Secret Detection**: Incorporates GitHub secret scanning capabilities
- **Workflow Integration**: Builds on existing GitHub Actions workflows
- **Centralized Security**: Uses GitHub security dashboard for visibility

## Success Criteria
- **Comprehensive Quality Assessment**: Security, code quality, performance, maintainability
- **Pipeline Integration**: Seamlessly integrates with existing GitHub security tools
- **Quality Gate Function**: Provides clear pass/fail decisions for validation
- **Continuous Improvement**: Identifies quality improvement opportunities
- **AI-Enhanced Analysis**: Goes beyond automated tools with contextual assessment