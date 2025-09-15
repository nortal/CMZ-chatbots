# VALIDATE-DATA-PERSISTENCE-ADVICE.md

Best practices and troubleshooting guide for the validate-data-persistence command.

## Overview

The `validate-data-persistence` command provides comprehensive end-to-end validation of data flow from UI form interactions to DynamoDB storage. Unlike `validate-animal-config-edit` which focuses on UI validation, this command tests the complete data persistence pipeline.

## Key Differences from validate-animal-config-edit

| Aspect | validate-animal-config-edit | validate-data-persistence |
|--------|----------------------------|---------------------------|
| **Scope** | UI validation and form interaction | Complete data flow (UI → API → Database) |
| **Focus** | Form rendering, tab navigation, field validation | Data integrity, persistence accuracy, API processing |
| **Tools** | Playwright for UI automation | Playwright + AWS MCP + Sequential Reasoning |
| **Validation** | Form state and error handling | Database records vs UI input comparison |
| **Complexity** | Single-phase UI testing | Four-phase systematic analysis |

## Command Usage Patterns

### Basic Usage
```bash
/validate-data-persistence
# Validates animal config save operations with standard test scenarios
```

### Entity-Specific Validation
```bash
/validate-data-persistence --entity animals
/validate-data-persistence --entity families
/validate-data-persistence --entity users
```

### Scenario-Specific Testing
```bash
/validate-data-persistence --scenarios create,update,delete
/validate-data-persistence --scenarios edge-cases
/validate-data-persistence --scenarios large-payloads
```

### Debug Mode
```bash
/validate-data-persistence --debug
# Provides detailed step-by-step analysis with intermediate data captures
```

## Implementation Strategy

### Phase 1: Environment Setup & Data Baseline
**Purpose**: Establish clean testing environment and capture baseline state

**Key Actions**:
- Verify all services running (frontend:3000, backend:8080, DynamoDB accessible)
- Authenticate test user and capture session tokens
- Document current database state for affected entities
- Set up network request monitoring for API call tracing

**Common Issues**:
- **Service Unavailable**: Use `make start-dev` to ensure all services running
- **Authentication Failures**: Clear browser storage and re-authenticate
- **Network Monitoring Setup**: Ensure Playwright can capture network requests

### Phase 2: UI Interaction & Data Capture
**Purpose**: Execute form interactions while capturing exact data flow

**Key Actions**:
- Navigate to target forms using Playwright automation
- Fill forms with controlled test data scenarios
- Capture form values before submission (exact data state)
- Monitor API requests/responses during form submission
- Record success/error notifications and timing

**Critical Implementation Notes**:
- **Data Capture Timing**: Capture form data immediately before submission, not after
- **Network Request Monitoring**: Use `page.route()` to intercept and log API calls
- **Error State Handling**: Distinguish between validation errors and persistence failures
- **Timing Sensitivity**: Allow adequate time for async operations to complete

### Phase 3: Database Verification
**Purpose**: Verify data accurately persisted to DynamoDB with correct structure

**Key Actions**:
- Query DynamoDB directly using AWS MCP tools
- Compare UI input data with stored database records
- Validate data type consistency and transformation accuracy
- Check audit trails, timestamps, and metadata fields

**Database Query Patterns**:
```python
# Animal config validation
aws dynamodb get-item \
  --table-name quest-dev-animal \
  --key '{"animalId": {"S": "test-animal-id"}}'

# Family data validation
aws dynamodb get-item \
  --table-name quest-dev-family \
  --key '{"familyId": {"S": "test-family-id"}}'
```

**Data Comparison Algorithm**:
- **Type Normalization**: Handle string/number conversions properly
- **Null Handling**: Distinguish between null, undefined, empty string
- **Object Structure**: Verify nested objects maintain correct structure
- **Array Preservation**: Ensure arrays persist with correct ordering

### Phase 4: Data Consistency Analysis & Reporting
**Purpose**: Generate actionable insights with specific remediation steps

**Report Structure**:
```markdown
## Data Persistence Validation Results

### Test Scenarios Executed
- ✅ Animal Config Create: [success/failure details]
- ❌ Family Update: [specific issue description]
- ⚠️ User Profile Edge Case: [data loss detected]

### Data Integrity Analysis
**Successful Persistence**: X/Y scenarios passed
**Data Discrepancies Found**: [specific field mismatches]
**Performance Metrics**: [timing and response data]

### Issues Requiring Attention
1. **Critical**: [data loss or corruption issues]
2. **Warning**: [non-critical inconsistencies]
3. **Enhancement**: [optimization opportunities]

### Remediation Recommendations
[Specific actionable steps with code examples]
```

## Common Issues & Solutions

### Issue: Form Data Not Reaching Database
**Symptoms**: UI shows success but database has no records
**Diagnosis**:
```bash
# Check API request logs
grep -r "POST\|PUT\|PATCH" logs/
# Verify API endpoint implementation
curl -X POST http://localhost:8080/animal-config/test-id -H "Content-Type: application/json" -d '{test data}'
```
**Solutions**:
- Verify API endpoint implementations are not returning 501 Not Implemented
- Check route handlers properly call business logic functions
- Validate API authentication and authorization

### Issue: Data Type Mismatches
**Symptoms**: API returns validation errors despite UI validation passing
**Common Patterns**:
- Frontend sends arrays, backend expects objects (guardrails field)
- Number fields sent as strings requiring type conversion
- Date/timestamp format inconsistencies

**Solution Strategy**:
1. **Frontend Validation**: Update form validation to match API expectations
2. **Backend Tolerance**: Add type coercion in API handlers
3. **Schema Alignment**: Ensure OpenAPI spec matches frontend models

### Issue: Incomplete Data Persistence
**Symptoms**: Some form fields save, others are missing or null
**Diagnosis**:
```javascript
// Check form data extraction in browser console
console.log('Form data before submit:', formData);
// Compare with database record
console.log('Database record:', dbRecord);
```
**Solutions**:
- Verify all form fields included in data extraction logic
- Check for null/undefined handling in validation functions
- Ensure optional fields have proper default values

### Issue: Authentication/Authorization Failures
**Symptoms**: API returns 401/403 errors during testing
**Solutions**:
- Verify JWT token format matches backend expectations
- Check token expiration times
- Validate user roles and permissions for target operations
- Clear browser storage and re-authenticate

## Best Practices

### Test Data Management
- **Predictable Data**: Use consistent test data for reproducible results
- **Cleanup Strategy**: Remove test data after validation or use dedicated test environment
- **Edge Case Coverage**: Test with special characters, large payloads, boundary values

### Error Handling
- **Graceful Degradation**: Test how system handles partial failures
- **User Experience**: Verify error messages are helpful and actionable
- **Recovery Scenarios**: Test ability to retry failed operations

### Performance Considerations
- **Timing Sensitivity**: Allow adequate time for async operations
- **Concurrent Operations**: Test behavior under concurrent user actions
- **Large Payload Handling**: Validate system handles maximum expected data sizes

### Security Validation
- **Input Sanitization**: Verify malicious input is properly handled
- **Authorization Checks**: Test access control for different user roles
- **Data Exposure**: Ensure sensitive data not logged or exposed

## Integration with Existing Workflows

### MR Preparation Workflow
```bash
# Before creating MR, run data persistence validation
/validate-data-persistence --comprehensive

# Include results in MR description
# Add validation report to claudedocs/ directory
```

### CI/CD Integration
- **Pre-deployment**: Run validation against staging environment
- **Post-deployment**: Verify production data integrity
- **Regression Testing**: Include in automated test suites

### Quality Gates
- **Data Integrity**: 100% accuracy required for critical user data
- **Performance**: Submit-to-persist time <3 seconds for standard operations
- **Error Recovery**: Clear error messages and recovery paths for all failure modes

## Troubleshooting Guide

### Environment Issues
```bash
# Verify all services running
make status

# Check service health
curl http://localhost:3000  # Frontend
curl http://localhost:8080/health  # Backend
aws dynamodb list-tables  # Database connectivity
```

### Authentication Issues
```bash
# Clear browser storage
# Re-authenticate with test credentials
# Verify JWT token structure in browser developer tools
```

### Data Issues
```bash
# Check database table structure
aws dynamodb describe-table --table-name quest-dev-animal

# Verify recent data changes
aws dynamodb scan --table-name quest-dev-animal --limit 5
```

### Network Issues
```bash
# Test API connectivity
curl -X GET http://localhost:8080/animal-config/test-id

# Check for CORS issues in browser console
# Verify API proxy configuration in vite.config.ts
```

## Advanced Usage

### Custom Test Scenarios
Create custom validation scenarios in `claudedocs/test-scenarios/`:
```yaml
# custom-animal-validation.yml
scenarios:
  stress_test:
    description: "Test with maximum allowed data"
    animal_count: 50
    concurrent_users: 5

  edge_cases:
    description: "Test boundary conditions"
    data_types: [null, empty_string, max_length, unicode]
```

### Integration with Other Commands
```bash
# Combine with infrastructure validation
/systematic-cmz-infrastructure-hardening
/validate-data-persistence

# Use with API development workflow
/nextfive PR003946-XX
/validate-data-persistence --entity animals
```

### Custom Reporting
Generate custom reports by extending the command:
```bash
/validate-data-persistence --report-format json --output claudedocs/validation-results.json
```

## Success Criteria

### Primary Validation Goals
- **100% Data Integrity**: UI input matches database storage exactly
- **Complete Workflow Coverage**: All CRUD operations tested successfully
- **Error Scenario Handling**: All failure modes identified and documented
- **Performance Standards**: Operations complete within acceptable timeframes

### Quality Metrics
- **Test Coverage**: All major entity types and operations tested
- **Issue Detection**: All data discrepancies identified with specific field-level detail
- **Reproducibility**: Test scenarios can be repeated with consistent results
- **Actionability**: All issues include specific remediation steps

### Business Value
- **User Experience**: Data saves work reliably from user perspective
- **Data Quality**: Critical business data persists accurately
- **System Reliability**: Persistence layer operates consistently under various conditions
- **Development Velocity**: Issues detected early in development cycle rather than production

## Related Commands
- `validate-animal-config-edit` - UI-focused validation for form interactions
- `systematic-cmz-infrastructure-hardening` - Infrastructure reliability validation
- `/nextfive` - API implementation validation and development
- `create-tracking-version` - Version consistency validation across environments