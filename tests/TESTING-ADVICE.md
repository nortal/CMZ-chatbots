# CMZ Project Testing Framework

## Overview
Systematic test-driven development approach for CMZ AI-Based Animal Interaction Platform (PR003946).

**Project Context**: Flask-based API server with OpenAPI-driven development, DynamoDB persistence, Docker containerization, and comprehensive AWS integration for zoo digital ambassador chatbot platform.

**Critical**:  Make sure the front and backend are running before starting tests and validate the versions of both.  If they are not running start them.  If you encounter problems starting them use sequential reasoning to resolve the problem and start the services.  If they cannot be resolved do not continue testing but inform the user.

## Testing Philosophy
- **Evidence-Based**: All test results must be reproducible and measurable
- **Comprehensive Coverage**: Every testable Jira ticket gets systematic test specifications
- **Historical Tracking**: Maintain complete test execution history for trend analysis
- **Multi-Layer Testing**: Integration, Unit, Playwright (E2E), and Security test coverage
- **Sequential Reasoning**: Apply systematic analysis throughout all testing processes

## Project Integration

### Existing Infrastructure Integration
**Authentication Pattern**:
- Test users: `parent1@test.cmz.org`, `student1@test.cmz.org`, `test@cmz.org`, etc.
- Password: `testpass123` for all test accounts
- JWT token generation through existing auth endpoints
- Frontend: `localhost:3001`, Backend: `localhost:8080`

**AWS/DynamoDB Integration**:
- Tables: `quest-dev-family`, `quest-dev-users`, `quest-dev-conversations`, etc.
- AWS Profile: `cmz` configured for us-west-2 region
- Environment: Use existing `.env.local` for credentials

**Docker Workflow**:
- Standard commands: `make generate-api && make build-api && make run-api`
- Live reloading enabled for development
- API container running on port 8080

**Existing Playwright Infrastructure**:
- Configuration: `backend/api/src/main/python/tests/playwright/config/playwright.config.js`
- Two-step testing approach: Step 1 validation, then full suite
- Browser compatibility across 6 browsers (Chrome, Firefox, Safari, Edge, Mobile Chrome, Mobile Safari)

## Test Execution Workflow

### 1. Pre-Test Preparation
- **Environment Setup**: Ensure backend/frontend services are running
- **Review Ticket ADVICE.md**: Understand acceptance criteria and requirements
- **Validate Infrastructure**: Confirm test users, DynamoDB tables, and endpoints are accessible
- **Sequential Reasoning**: Predict expected outcomes before test execution

### 2. Test Execution Process
- **Follow howto-test.md Instructions**: Execute step-by-step test procedures exactly as documented
- **Evidence Collection**: Capture screenshots, logs, performance metrics as specified
- **Real-time Documentation**: Record actual vs expected results during execution
- **Error Handling**: Apply systematic root cause analysis for any failures

### 3. Results Documentation
- **Create Timestamped Results File**: Use YYYY-MM-DD-HHMMSS format for chronological sorting
- **Include Sequential Analysis**: Document reasoning process and variance analysis
- **Update Historical Tracking**: Add pass/fail status to history.txt file
- **Link Evidence**: Reference all collected screenshots, logs, and metrics

### 4. Post-Test Analysis
- **Sequential Reasoning Review**: Assess results against predictions
- **Trend Analysis**: Compare with historical test results
- **System Impact Assessment**: Evaluate broader implications of test outcomes
- **Next Steps Planning**: Determine follow-up actions based on results

## Test Types and Scope

### Integration Tests (`tests/integration/`)
**Focus**: API endpoints, database integration, service communication
**Success Criteria**:
- API endpoints respond with correct HTTP status codes
- DynamoDB operations execute successfully with proper data persistence
- Service-to-service communication works as specified
- Error handling behaves correctly for invalid inputs

**Sample Integration Test Categories**:
- Authentication flow validation
- CRUD operations for all domain entities (families, users, animals, conversations)
- Cross-service data consistency
- API schema compliance

### Unit Tests (`tests/unit/`)
**Focus**: Individual functions, business logic, data transformations
**Success Criteria**:
- Functions return expected outputs for given inputs
- Edge cases handled correctly
- Error conditions raise appropriate exceptions
- Business logic follows specified requirements

**Sample Unit Test Categories**:
- DynamoDB utility functions in `impl/utils/dynamo.py`
- Data model transformations between OpenAPI and DynamoDB formats
- Business logic in `impl/` modules (animals, family, users, etc.)
- Validation functions and error handling logic

### Playwright Tests (`tests/playwright/`)
**Focus**: End-to-end user workflows, UI functionality, cross-browser compatibility
**Success Criteria**:
- User workflows complete successfully across multiple browsers
- UI elements render correctly and are accessible
- Form submissions and interactions work as designed
- Cross-browser compatibility maintained

**Sample Playwright Test Categories**:
- Complete authentication flows (login, logout, role-based access)
- Family management workflows (create, edit, delete families and members)
- Animal chatbot interactions and conversation flows
- Dashboard functionality and navigation

### Security Tests (`tests/security/`)
**Focus**: Authentication, authorization, input validation, vulnerability assessment
**Success Criteria**:
- Authentication mechanisms secure against common attacks
- Authorization properly enforced for role-based access
- Input validation prevents injection and XSS vulnerabilities
- Sensitive data protected in transit and at rest

**Sample Security Test Categories**:
- JWT token security and expiration handling
- Role-based access control enforcement
- Input sanitization for all API endpoints
- SQL injection and XSS prevention validation

## Quality Standards

### Test Specification Requirements
- **Clear Pass/Fail Criteria**: No ambiguity about success conditions
- **Reproduction Steps**: Complete step-by-step instructions for test execution
- **Evidence Requirements**: Specific screenshots, logs, or metrics to collect
- **Prerequisite Documentation**: Clear setup requirements and dependencies

### Result Documentation Standards
- **Timestamped Files**: YYYY-MM-DD-HHMMSS format for chronological organization
- **Sequential Analysis**: Include reasoning process and variance analysis
- **Evidence Linkage**: Reference all collected evidence and artifacts
- **Historical Context**: Compare results with previous test executions

### Quality Gates
- All tests must have measurable success criteria
- Failed tests require root cause analysis using sequential reasoning
- Test results must include reproduction steps and evidence
- Historical tracking enables trend analysis and reliability metrics

## Jira Integration

### Ticket Discovery and Categorization
**Project Key**: PR003946 (CMZ - AI-Based Animal Interaction)
**Testable Ticket Types**: Bug, Task, Story with acceptance criteria
**Known Tickets**: 48+ tickets already referenced in project documentation

### Test Specification Mapping
- **One-to-One Mapping**: Each testable ticket gets dedicated test specification
- **ADVICE.md Files**: Extract complete ticket information and requirements analysis
- **howto-test.md Files**: Provide executable test instructions
- **Results Tracking**: Maintain historical pass/fail records

### Integration Patterns
- **Authentication**: Use established `.env.local` credentials with Basic auth
- **Ticket Updates**: Follow patterns from `scripts/update_jira_simple.sh`
- **Status Transitions**: Use workflow discovery for "In Progress" transitions
- **Custom Fields**: Include `customfield_10225` with "Billable" value for new tickets

## Automation and Maintenance

### Periodic Evaluation
- **Weekly Ticket Scan**: Identify new testable tickets in PR003946
- **Test Specification Updates**: Refresh existing specifications when tickets change
- **Historical Analysis**: Generate trend reports and reliability metrics
- **Gap Analysis**: Identify areas lacking test coverage

### Automation Opportunities
- **Template Generation**: Auto-create test specifications for new tickets
- **Result Aggregation**: Compile cross-test-type coverage reports
- **Trend Analysis**: Automated detection of reliability patterns
- **Integration Monitoring**: Track test infrastructure health

## Usage Examples

### Creating New Test Specifications
1. **Identify Ticket**: New testable ticket discovered in PR003946
2. **Create ADVICE.md**: Extract requirements and analyze acceptance criteria
3. **Generate howto-test.md**: Create executable test instructions with clear success criteria
4. **Establish History Tracking**: Initialize history.txt file for the ticket
5. **Execute Initial Test**: Run test to establish baseline results

### Executing Existing Tests
1. **Review ADVICE.md**: Understand ticket context and requirements
2. **Follow howto-test.md**: Execute step-by-step instructions exactly
3. **Collect Evidence**: Gather specified screenshots, logs, and metrics
4. **Document Results**: Create timestamped results file with sequential analysis
5. **Update History**: Add pass/fail status to history.txt

### Analyzing Test Trends
1. **Review History Files**: Examine pass/fail patterns over time
2. **Identify Problem Areas**: Tickets with frequent failures or instability
3. **Sequential Analysis**: Apply reasoning to understand trend causes
4. **Improvement Planning**: Develop strategies to address reliability issues

## Success Metrics

### Coverage Metrics
- **Ticket Coverage**: Percentage of testable PR003946 tickets with test specifications
- **Test Type Distribution**: Balance across integration, unit, playwright, and security tests
- **Execution Frequency**: Regular execution of test specifications
- **Historical Depth**: Length and completeness of test history records

### Quality Metrics
- **Pass/Fail Rates**: Success percentages by test type and individual ticket
- **Trend Stability**: Consistency of results over time
- **Evidence Completeness**: Percentage of test results with full evidence collection
- **Sequential Analysis Quality**: Depth and accuracy of reasoning documentation

### System Health Indicators
- **Infrastructure Reliability**: Consistency of test environment performance
- **Integration Stability**: Success of cross-service and cross-component tests
- **Security Posture**: Results of security-focused test validations
- **User Experience Quality**: Playwright test results reflecting real user workflows

## Framework Evolution

This testing framework is designed to evolve with the CMZ project:

- **Adaptive Categorization**: New ticket types and test categories as project grows
- **Tool Integration**: Leverage new testing tools and techniques as they become available
- **Methodology Refinement**: Continuous improvement based on lessons learned
- **Scale Accommodation**: Framework scales from individual tickets to comprehensive system validation

The systematic approach ensures comprehensive test coverage while maintaining the flexibility to adapt to changing project requirements and technological evolution.

---

**Document Version**: 1.0
**Last Updated**: 2025-09-13
**Framework Status**: Active Development
**Integration Status**: Aligned with existing CMZ project infrastructure