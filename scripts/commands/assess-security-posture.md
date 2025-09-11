# /assess-security-posture Command

## Purpose  
AI-powered comprehensive security assessment leveraging GitHub pipeline SAST tools and identifying security debt across the CMZ chatbot platform.

## Execution

Use sequential reasoning MCP to perform security posture analysis integrated with existing GitHub security tooling:

**Security Posture Assessment Prompt:**
```
Analyze the security posture of the CMZ chatbot system using AI-first comprehensive evaluation with GitHub pipeline integration:

**PROJECT CONTEXT:**
- **Platform**: Educational chatbot for zoo visitors with family/student data
- **Technology Stack**: Python Flask, OpenAPI, AWS DynamoDB, Docker
- **Data Sensitivity**: User profiles, family groups, conversation history
- **Threat Model**: Web application with API endpoints, data persistence, AWS integration
- **Existing Security**: GitHub Advanced Security, Dependabot, CodeQL scanning

**COMPREHENSIVE SECURITY ANALYSIS:**

### 1. **Application Security**
- **Input Validation**: API endpoint input sanitization and validation
- **Authentication & Authorization**: User authentication patterns and access control
- **Session Management**: Session handling and token security
- **Data Validation**: OpenAPI schema validation effectiveness
- **Error Handling**: Information disclosure in error messages

### 2. **Infrastructure Security**
- **AWS Configuration**: DynamoDB access patterns, IAM policies, VPC setup
- **Container Security**: Docker image security, base image vulnerabilities
- **Secrets Management**: Environment variables, API keys, configuration security
- **Network Security**: API exposure, encryption in transit
- **Access Controls**: Principle of least privilege implementation

### 3. **Data Security**
- **Data Classification**: Sensitivity levels of stored data (PII, educational content)
- **Encryption**: Data at rest and in transit encryption
- **Data Access Patterns**: Who can access what data and when
- **Data Retention**: Data lifecycle and deletion policies
- **Privacy Controls**: COPPA/FERPA compliance for educational content

### 4. **Dependency Security**
- **Third-Party Libraries**: Vulnerability assessment of Python dependencies
- **Supply Chain**: Package integrity and source verification
- **Dependency Updates**: Security update practices and automation
- **License Compliance**: Open source license security implications
- **Version Management**: Outdated dependencies with known vulnerabilities

### 5. **GitHub Security Integration**
- **SAST Results**: Current CodeQL and security scan findings
- **Dependency Alerts**: Dependabot vulnerability notifications
- **Secret Scanning**: Exposed secrets detection results
- **Security Policy**: Repository security policy compliance
- **Automated Security**: Security automation effectiveness

**MEASUREMENT METHODOLOGY:**
1. **Integrate GitHub Security Data**: Pull existing security scan results
2. **Manual Security Review**: AI-powered analysis of security patterns
3. **Threat Modeling**: Identify attack vectors and security requirements
4. **Compliance Assessment**: Educational data privacy requirements
5. **Risk Prioritization**: Impact vs likelihood security risk scoring

**DELIVERABLE REQUIREMENTS:**
```json
{
  "security_assessment": {
    "analysis_timestamp": "2025-09-11T17:30:00Z",
    "overall_rating": "good",
    "security_score": 0.78,
    "risk_level": "medium",
    
    "application_security": {
      "score": 0.82,
      "input_validation": "strong",
      "authentication": "implemented",
      "authorization": "basic",
      "session_management": "secure",
      "error_handling": "secure",
      "critical_vulnerabilities": 0,
      "medium_vulnerabilities": 2
    },
    
    "infrastructure_security": {
      "score": 0.85,
      "aws_configuration": "secure",
      "container_security": "good",
      "secrets_management": "good", 
      "network_security": "strong",
      "access_controls": "implemented",
      "high_risk_configurations": 0
    },
    
    "data_security": {
      "score": 0.75,
      "data_classification": "partial",
      "encryption_at_rest": "enabled",
      "encryption_in_transit": "enforced",
      "access_patterns": "controlled",
      "retention_policies": "defined",
      "privacy_compliance": "needs_review"
    },
    
    "dependency_security": {
      "score": 0.70,
      "vulnerable_dependencies": 3,
      "high_severity_vulns": 0,
      "medium_severity_vulns": 2,
      "low_severity_vulns": 1,
      "outdated_packages": 8,
      "license_issues": 0
    },
    
    "github_security_integration": {
      "sast_enabled": true,
      "dependency_scanning": true,
      "secret_scanning": true,
      "security_advisories": 2,
      "automated_updates": true,
      "policy_compliance": "good"
    }
  },
  
  "high_priority_findings": [
    {
      "category": "data_security",
      "finding": "Family data access not fully restricted by user role",
      "severity": "medium",
      "impact": "data_exposure",
      "remediation": "Implement role-based data access controls",
      "effort": "medium"
    },
    {
      "category": "dependency_security", 
      "finding": "requests library has medium severity vulnerability",
      "severity": "medium",
      "impact": "potential_rce",
      "remediation": "Update to requests >= 2.31.0",
      "effort": "low"
    }
  ],
  
  "compliance_assessment": {
    "coppa_compliance": "partial",
    "ferpa_compliance": "needs_review",
    "gdpr_considerations": "minimal_impact",
    "aws_security_framework": "aligned",
    "owasp_top10": "mostly_covered"
  },
  
  "security_debt": [
    {
      "area": "Authentication system",
      "debt": "No multi-factor authentication for admin users",
      "impact": "medium",
      "remediation_effort": "high"
    },
    {
      "area": "Audit logging",
      "debt": "Limited audit trail for data access",
      "impact": "low",
      "remediation_effort": "medium"
    }
  ],
  
  "recommendations": {
    "immediate_actions": [
      "Update vulnerable dependencies identified by Dependabot",
      "Implement role-based access control for family data"
    ],
    "strategic_improvements": [
      "Establish comprehensive audit logging",
      "Implement automated security testing in CI/CD"
    ],
    "compliance_actions": [
      "Complete COPPA compliance review for family features",
      "Document data retention and deletion procedures"
    ]
  }
}
```

**GITHUB SECURITY INTEGRATION:**
- **Pull Security Scan Results**: Integrate current CodeQL and SAST findings
- **Dependency Vulnerability Data**: Use Dependabot alerts and vulnerability database
- **Secret Scanning Results**: Review exposed secrets detection outcomes  
- **Security Advisory Integration**: Incorporate GitHub security advisories
- **Automated Security Metrics**: Leverage GitHub security insights and metrics

**THREAT MODEL FOCUS:**
- **Educational Data**: Student/family information protection
- **API Security**: Public endpoint security and rate limiting
- **AWS Integration**: Cloud service security configuration
- **Container Security**: Docker deployment security
- **Supply Chain**: Dependency and build pipeline security

**SUCCESS CRITERIA:**
- **Comprehensive Coverage**: All security dimensions assessed systematically
- **GitHub Integration**: Leverages existing security tooling effectively  
- **Risk-Based Prioritization**: Security findings prioritized by business impact
- **Compliance Alignment**: Educational data privacy requirements addressed
- **Actionable Roadmap**: Clear security improvement plan with effort estimates
```

## Integration with GitHub Pipeline
- **Leverages Existing SAST**: Builds on current CodeQL and security scanning
- **Dependabot Integration**: Uses existing vulnerability alerts and updates
- **Secret Scanning Results**: Incorporates exposed secrets detection
- **Security Policy Compliance**: Aligns with repository security policies
- **Automated Security Metrics**: Uses GitHub security insights data

## Success Criteria
- **AI-Enhanced Analysis**: Goes beyond automated scanning with contextual assessment
- **GitHub Tool Integration**: Maximizes existing security infrastructure investment
- **Educational Compliance**: Addresses COPPA/FERPA requirements specifically
- **Risk-Based Prioritization**: Security debt prioritized by business impact
- **Continuous Security**: Establishes security posture tracking over time