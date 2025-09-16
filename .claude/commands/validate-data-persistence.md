# Validate Data Persistence

**Purpose**: Comprehensive end-to-end validation of data persistence from UI interactions to DynamoDB storage, ensuring data integrity across the complete save workflow.

## Context
This prompt addresses the critical need to validate that UI form submissions correctly persist to DynamoDB with accurate data integrity. Unlike basic UI validation (validate-animal-config-edit), this tests the complete data flow including API processing, database storage, and data consistency verification.

**Problem Solved**: Detecting data loss, transformation errors, and persistence failures that only surface during actual save operations.

## Sequential Reasoning Approach

Use MCP Sequential Thinking to systematically validate data persistence across the complete CMZ application stack:

### Phase 1: Environment Setup & Data Baseline
**Use Sequential Reasoning to:**
1. **Environment Verification**: Confirm all services (frontend, backend, DynamoDB) are operational
2. **Baseline Capture**: Document current database state for affected entities
3. **Test Scenario Planning**: Define specific data scenarios to test (create, update, delete operations)
4. **Authentication Setup**: Ensure proper user authentication for test operations
5. **Network Monitoring Setup**: Prepare to capture API requests and responses

**Key Questions for Sequential Analysis:**
- Are all required services running and accessible?
- What is the current state of test data in DynamoDB?
- Which entity types and operations need validation?
- What are the expected data transformation patterns?
- What authentication credentials are needed for test scenarios?

### Phase 2: UI Interaction & Data Capture
**Implementation Order (Follow Exactly):**

#### Step 1: Initialize Data Capture
```javascript
// Capture baseline data before UI interaction
const testData = {
  formData: {},
  networkRequests: [],
  timestamps: {
    start: new Date().toISOString()
  }
};
```

#### Step 2: Browser Automation Setup
```bash
# Use Playwright MCP for browser automation
# Navigate to target forms (animal config, family management, etc.)
# Set up network request monitoring
```

#### Step 3: Form Data Collection
- Navigate to target forms using Playwright
- Fill forms with test data scenarios
- Capture exact form values before submission
- Monitor form validation and error states

#### Step 4: Submit and Monitor
- Execute form submission
- Capture all network requests/responses
- Monitor for success/error notifications
- Record API response data and timing

### Phase 3: Database Verification
**Verification Order (Systematic):**

#### Step 1: Direct DynamoDB Query
```bash
# Use AWS MCP to query DynamoDB directly
# Verify data was saved with correct structure
# Check audit trails and timestamps
```

#### Step 2: Data Comparison Analysis
- Compare UI form data with database records
- Validate data type consistency (strings, numbers, booleans)
- Check for data transformation accuracy
- Verify required vs optional field handling

#### Step 3: Business Rule Validation
- Confirm business logic was applied correctly
- Validate guardrails and constraints enforcement
- Check audit trail completeness
- Verify soft delete scenarios if applicable

### Phase 4: Data Consistency Analysis & Reporting
**Analysis Framework:**

#### Step 1: Data Integrity Assessment
- Generate detailed comparison reports
- Identify any data discrepancies or losses
- Analyze transformation accuracy
- Document timing and performance metrics

#### Step 2: Error Pattern Detection
- Categorize any discovered issues
- Assess impact severity (critical, warning, info)
- Generate actionable remediation recommendations
- Create reproducible test scenarios for failures

#### Step 3: Comprehensive Reporting
- Generate summary report with pass/fail status
- Document all test scenarios and outcomes
- Provide specific examples of any data issues
- Include recommendations for fixes

## Implementation Details

### Test Entity Types
Support validation for:
- **Animal Configurations**: Voice settings, personality, guardrails
- **Family Management**: Parent-student relationships, group settings
- **User Management**: Profile updates, role assignments
- **Knowledge Base**: Content creation and updates

### Data Validation Scenarios
```yaml
test_scenarios:
  create_operations:
    - new_animal_config
    - new_family_group
    - new_user_profile

  update_operations:
    - modify_existing_animal
    - update_family_settings
    - change_user_roles

  edge_cases:
    - large_data_payloads
    - special_characters
    - null_optional_fields
    - concurrent_modifications
```

### Technical Integration
```bash
# Required MCP Servers
# - Playwright: Browser automation and form interaction
# - AWS: DynamoDB queries and data verification
# - Sequential: Systematic analysis and decision making

# Environment Variables
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8080
AWS_REGION=us-west-2
DYNAMO_TABLE_PREFIX=quest-dev-
```

### Data Comparison Algorithm
```python
def compare_ui_database_data(ui_data, db_data):
    """
    Compare UI form data with database records
    Handle type conversions and format differences
    """
    discrepancies = []

    for field, ui_value in ui_data.items():
        db_value = db_data.get(field)

        # Type normalization
        normalized_ui = normalize_value(ui_value)
        normalized_db = normalize_value(db_value)

        if normalized_ui != normalized_db:
            discrepancies.append({
                'field': field,
                'ui_value': ui_value,
                'db_value': db_value,
                'severity': assess_severity(field, ui_value, db_value)
            })

    return discrepancies
```

## Integration Points

### CMZ Project Integration
- **Make Commands**: Integrate with existing `make run-api` and frontend startup
- **Authentication**: Use existing admin credentials and JWT token handling
- **Error Handling**: Follow CMZ error reporting patterns
- **Git Workflow**: Support for feature branch testing and validation

### Existing Test Infrastructure
- Leverage existing Playwright configuration in `config/playwright.config.js`
- Use established test user accounts and authentication flows
- Integrate with existing DynamoDB table structure and naming conventions
- Follow established logging and reporting patterns

### MCP Server Coordination
- **Playwright MCP**: Primary tool for UI automation and form interaction
- **AWS MCP**: Essential for DynamoDB queries and data verification
- **Sequential Thinking**: Critical for systematic analysis and decision making

## Quality Gates

### Mandatory Validation Before Completion
- [ ] All target services are running and accessible
- [ ] Test authentication is working correctly
- [ ] Baseline database state has been captured
- [ ] UI forms are accessible and functional
- [ ] Network monitoring is capturing API requests
- [ ] DynamoDB queries are returning expected data structure
- [ ] Data comparison algorithms are working correctly
- [ ] Error scenarios are properly handled and reported

### Success Criteria Validation
- [ ] Complete data flow from UI to database verified
- [ ] All test scenarios executed successfully
- [ ] Any data discrepancies identified and documented
- [ ] Performance metrics captured and analyzed
- [ ] Comprehensive report generated with actionable insights

## Success Criteria

### Primary Objectives
1. **Data Integrity Verification**: Confirm UI data reaches DynamoDB unchanged
2. **Complete Workflow Testing**: Validate entire save process including error handling
3. **Comprehensive Coverage**: Test multiple entity types and operation scenarios
4. **Actionable Reporting**: Provide clear identification of any issues with remediation steps

### Performance Standards
- **Execution Time**: Complete validation within 10 minutes for standard scenarios
- **Accuracy**: 100% detection of data discrepancies when they exist
- **Reliability**: Consistent results across multiple test runs
- **Coverage**: Test all major entity types and operation scenarios

### Quality Metrics
- **Data Consistency**: 100% accuracy between UI input and database storage
- **Error Detection**: All persistence failures identified and categorized
- **Report Quality**: Clear, actionable insights with specific examples
- **Reproducibility**: Test scenarios can be repeated consistently

## Error Handling & Troubleshooting

### Common Failure Scenarios
1. **Service Unavailability**: Frontend/backend/database not accessible
2. **Authentication Failures**: Invalid credentials or expired tokens
3. **Network Issues**: API timeouts or connection failures
4. **Data Transformation Errors**: Type conversion or format issues
5. **Validation Failures**: Business rule violations or constraint errors

### Diagnostic Procedures
```bash
# Service Health Check
curl -f http://localhost:3000 && curl -f http://localhost:8080/health

# Database Connectivity
aws dynamodb list-tables --region us-west-2

# Authentication Validation
# Test login flow through Playwright automation
```

### Recovery Actions
- **Service Issues**: Restart required services using make commands
- **Authentication**: Clear browser storage and re-authenticate
- **Network Issues**: Verify service endpoints and retry with backoff
- **Data Issues**: Document discrepancies and continue with remaining tests

## Advanced Usage

### Custom Test Scenarios
```yaml
# Define custom test data scenarios
custom_scenarios:
  stress_test:
    description: "Test with maximum data payload sizes"
    data_size: "large"
    concurrent_users: 5

  edge_cases:
    description: "Test with special characters and edge values"
    include_unicode: true
    test_nulls: true
    test_empty_strings: true
```

### Performance Analysis
- Measure save operation timing
- Analyze database query performance
- Monitor memory usage during large data operations
- Track API response times and error rates

### Integration with CI/CD
```bash
# Example integration with automated testing
make validate-data-persistence --entity=animals --scenarios=standard
```

## References
- `VALIDATE-DATA-PERSISTENCE-ADVICE.md` - Best practices and troubleshooting guide
- `validate-animal-config-edit.md` - Related UI validation patterns
- CMZ project `CLAUDE.md` - Integration with existing workflows
- Playwright configuration in `config/playwright.config.js`