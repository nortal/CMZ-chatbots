# /discover-tests Command

## Purpose
Run integration tests to identify what's actually broken and needs immediate fixing.

## Execution Steps

### Step 1: Execute Integration Test Suite
```bash
# Run the API validation integration tests
python -m pytest src/main/python/tests/integration/test_api_validation_epic.py -v --tb=short

# Capture both stdout and return codes
# Focus on getting clean, parseable test results
```

### Step 2: Parse Test Results
Extract specific information from test output:
```bash
# Parse failing test methods to identify:
# - Test method names (test_pr003946_XX_description) 
# - Associated ticket numbers from method names
# - Brief failure reason from error messages
# - Test categories (authentication, validation, CRUD, etc.)
```

### Step 3: Categorize Failures
Analyze failure patterns:
```python
failure_categories = {
    "missing_endpoint": "404 Not Found - endpoint not implemented",
    "validation_error": "400 Bad Request - validation logic missing", 
    "auth_failure": "401/403 - authentication/authorization issues",
    "data_error": "500 Internal Server Error - data handling problems",
    "schema_mismatch": "OpenAPI schema validation failures"
}
```

### Step 4: Output Technical Reality
```json
{
  "session_id": "discover_tests_YYYYMMDD_HHMMSS",
  "test_execution": {
    "total_tests": 21,
    "passing_tests": 16, 
    "failing_tests": 5,
    "execution_time": "0.62s"
  },
  "failing_tickets": [
    {
      "ticket_id": "PR003946-75",
      "test_method": "test_pr003946_75_knowledge_endpoint",
      "failure_category": "missing_endpoint",
      "failure_message": "404 Not Found: GET /api/v1/knowledge",
      "technical_issue": "Knowledge endpoint not implemented in controllers",
      "quick_fix_possible": true
    },
    {
      "ticket_id": "PR003946-76", 
      "test_method": "test_pr003946_76_knowledge_validation",
      "failure_category": "validation_error",
      "failure_message": "400 Bad Request: missing required field 'content'",
      "technical_issue": "Knowledge validation logic missing in impl",
      "quick_fix_possible": true
    }
  ],
  "passing_tickets": [
    {
      "ticket_id": "PR003946-66",
      "test_method": "test_pr003946_66_soft_delete_flag_consistency", 
      "status": "implemented",
      "note": "Soft delete functionality working correctly"
    }
  ],
  "summary": {
    "immediate_work_available": 5,
    "categories": {
      "missing_endpoint": 3,
      "validation_error": 2
    },
    "estimated_fix_time": "6-8 hours total",
    "complexity": "mostly_simple_crud"
  },
  "recommendations": [
    "Focus on missing endpoints first - quick wins",
    "Validation errors can be grouped together", 
    "All failing tickets appear to be straightforward CRUD implementations"
  ]
}
```

## Success Criteria
- Real test execution results (not predictions)
- Clear identification of failing vs passing tickets
- Technical categorization of failure types
- Realistic effort estimates based on actual error messages
- Clean data structure for use by other commands

## Error Handling
- If pytest fails to run, diagnose environment issues first
- If test parsing fails, provide raw output for manual analysis
- If no tests are failing, recommend looking for new feature opportunities
- Save results even if analysis is incomplete