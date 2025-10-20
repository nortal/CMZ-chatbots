# /validate Command

## Purpose
Test and verify implementations work correctly using sequential reasoning for prediction and comprehensive validation.

## Execution Steps

### Step 1: Load Implementation Results
```bash
# Load the most recent implementation results
IMPLEMENT_FILE=$(ls -t /tmp/implement_*.json 2>/dev/null | head -1)
if [[ -z "$IMPLEMENT_FILE" ]]; then
    echo "❌ No implementation results found. Run /implement first."
    exit 1
fi

# Extract implemented tickets and endpoints
IMPLEMENTED_TICKETS=$(jq -r '.implementation_summary.tickets_completed[]' "$IMPLEMENT_FILE")
echo "🧪 Validating implementations for: $IMPLEMENTED_TICKETS"
```

### Step 2: Sequential Reasoning Validation Prediction

Use sequential reasoning MCP to predict validation outcomes:

**Validation Prediction Prompt:**
```
Predict validation outcomes and plan comprehensive testing for implemented tickets:

**IMPLEMENTED WORK:**
{implementation_results_json}

**CURRENT SYSTEM STATE:**
- Docker container status: {container_status}
- System health: {system_health_check}
- DynamoDB connectivity: {db_status}
- Available endpoints: {endpoint_analysis}

**VALIDATION PREDICTION ANALYSIS:**

1. **Endpoint Functionality Prediction:**
   - Which endpoints should respond successfully?
   - What are the expected response formats and status codes?
   - Which operations (GET, POST, PUT, DELETE) should work?
   - What edge cases might cause failures?

2. **Error Handling Prediction:**
   - What validation errors should be properly handled?
   - Which missing data scenarios should return appropriate errors?
   - How should authentication failures be handled?
   - What database connectivity issues might occur?

3. **Integration Test Prediction:**
   - Which previously failing tests should now pass?
   - Are there tests that might still fail and why?
   - What new test failures might be introduced?
   - Which test scenarios need manual verification?

4. **Performance and Reliability Prediction:**
   - Which operations might have latency or timeout issues?
   - Are there resource consumption concerns?
   - What scalability limitations might exist?
   - Which failure modes should be tested?

5. **Comprehensive Testing Strategy:**
   - What is the optimal sequence for validation testing?
   - Which tests can be automated vs manual?
   - What data setup is needed for effective testing?
   - How should testing results be interpreted?

**DELIVERABLE:**
- Predicted validation outcomes for each implemented feature
- Comprehensive testing plan with expected results
- Risk assessment for potential validation failures
- Remediation strategies for predicted issues
```

### Step 3: System Health Validation

```bash
# Verify system components are healthy
echo "🏥 Checking system health..."

# Container status
CONTAINER_STATUS=$(docker ps --format "table {{.Names}}\t{{.Status}}" | grep cmz || echo "No CMZ containers running")
echo "Container: $CONTAINER_STATUS"

# API accessibility
API_RESPONSE=$(curl -s http://localhost:8080/ | jq -r '.status // "unreachable"')
echo "API Status: $API_RESPONSE"

# System health endpoint
HEALTH_CHECK=$(curl -s http://localhost:8080/system_health | jq -r '.status // "unknown"')
echo "System Health: $HEALTH_CHECK"

if [[ "$HEALTH_CHECK" != "ok" && "$HEALTH_CHECK" != "degraded" ]]; then
    echo "⚠️ System health issues detected. Validation may be unreliable."
fi
```

### Step 4: Endpoint Validation Testing

For each implemented ticket, perform comprehensive endpoint testing:

```bash
echo "🔍 Testing implemented endpoints..."

# Test each endpoint systematically
for TICKET in $IMPLEMENTED_TICKETS; do
    echo "Testing $TICKET..."
    
    case $TICKET in
        *69*) # ID generation functionality
            echo "  Testing ID generation patterns..."
            # Test endpoints that create entities to verify ID generation
            ;;
            
        *71*) # JWT validation  
            echo "  Testing JWT validation..."
            # Test protected endpoints with and without valid tokens
            curl -s http://localhost:8080/api/v1/auth/validate \
              -H "Authorization: Bearer invalid_token" | jq '.code // "no_error_code"'
            ;;
            
        *75*) # Knowledge CRUD
            echo "  Testing Knowledge Management CRUD..."
            
            # Test CREATE operation
            CREATE_RESPONSE=$(curl -s -X POST http://localhost:8080/api/v1/knowledge \
              -H "Content-Type: application/json" \
              -d '{"title": "Test Knowledge", "content": "Test content", "category": "test"}')
            echo "    CREATE: $(echo "$CREATE_RESPONSE" | jq -r '.code // "success"')"
            
            # Extract ID from create response for further testing
            KNOWLEDGE_ID=$(echo "$CREATE_RESPONSE" | jq -r '.knowledgeId // "unknown"')
            
            # Test READ operation
            if [[ "$KNOWLEDGE_ID" != "unknown" ]]; then
                READ_RESPONSE=$(curl -s http://localhost:8080/api/v1/knowledge/$KNOWLEDGE_ID)
                echo "    READ: $(echo "$READ_RESPONSE" | jq -r '.title // "not_found"')"
            fi
            
            # Test LIST operation
            LIST_RESPONSE=$(curl -s http://localhost:8080/api/v1/knowledge)
            ITEM_COUNT=$(echo "$LIST_RESPONSE" | jq -r '.items | length // 0' 2>/dev/null || echo "0")
            echo "    LIST: $ITEM_COUNT items returned"
            
            # Test validation errors
            VALIDATION_ERROR=$(curl -s -X POST http://localhost:8080/api/v1/knowledge \
              -H "Content-Type: application/json" \
              -d '{}' | jq -r '.code // "no_validation"')
            echo "    VALIDATION: $VALIDATION_ERROR"
            ;;
            
        *76*) # Knowledge validation
            echo "  Testing Knowledge validation and metadata..."
            # Test content validation rules
            # Test metadata handling
            ;;
            
        *72*) # Role-based access
            echo "  Testing role-based access control..."
            # Test different role access scenarios
            ;;
    esac
done
```

### Step 5: Integration Test Validation

```bash
echo "🧪 Running integration test validation..."

# Run integration tests and capture results
INTEGRATION_RESULTS=$(python -m pytest src/main/python/tests/integration/test_api_validation_epic.py -v 2>&1)

# Parse results
TOTAL_TESTS=$(echo "$INTEGRATION_RESULTS" | grep -E "^.*test.*\.py" | wc -l)
PASSING_TESTS=$(echo "$INTEGRATION_RESULTS" | grep -c "PASSED" || echo "0")  
FAILING_TESTS=$(echo "$INTEGRATION_RESULTS" | grep -c "FAILED" || echo "0")

echo "Integration Tests: $PASSING_TESTS passed, $FAILING_TESTS failed out of $TOTAL_TESTS total"

# Identify specific failing tests
if [[ "$FAILING_TESTS" -gt 0 ]]; then
    echo "❌ Failing tests:"
    echo "$INTEGRATION_RESULTS" | grep "FAILED" | head -5
fi
```

### Step 6: Error Scenario Validation

```bash
echo "🚨 Testing error scenarios..."

# Test common error conditions
echo "  Testing 404 errors..."
curl -s http://localhost:8080/api/v1/nonexistent | jq -r '.code // "no_error_code"'

echo "  Testing validation errors..."
curl -s -X POST http://localhost:8080/api/v1/knowledge \
  -H "Content-Type: application/json" \
  -d 'invalid json' | jq -r '.code // "no_error_code"' 2>/dev/null || echo "json_parse_error"

echo "  Testing authentication errors..."
curl -s http://localhost:8080/api/v1/protected_endpoint \
  -H "Authorization: Bearer invalid" | jq -r '.code // "no_error_code"'
```

### Step 7: Performance and Load Testing

```bash
echo "⚡ Basic performance validation..."

# Simple load test for key endpoints
for i in {1..10}; do
    RESPONSE_TIME=$(curl -s -w "%{time_total}" -o /dev/null http://localhost:8080/api/v1/knowledge)
    echo "Request $i: ${RESPONSE_TIME}s"
done

# Memory usage check
CONTAINER_STATS=$(docker stats cmz-openapi-api-dev --no-stream --format "table {{.CPUPerc}}\t{{.MemUsage}}" 2>/dev/null || echo "Stats unavailable")
echo "Container resources: $CONTAINER_STATS"
```

### Step 8: Validation Results and Analysis

```json
{
  "session_id": "validate_YYYYMMDD_HHMMSS",
  "validation_timestamp": "2025-09-11T15:30:00Z",
  
  "system_health": {
    "container_status": "running",
    "api_accessibility": "ok", 
    "health_endpoint": "degraded",
    "overall_status": "functional"
  },

  "endpoint_validation": {
    "PR003946-69": {
      "feature": "ID generation",
      "status": "passing",
      "tests": ["Entity creation generates proper UUIDs", "ID format follows entity prefix pattern"],
      "issues": []
    },
    "PR003946-71": {
      "feature": "JWT validation",
      "status": "passing",
      "tests": ["Token validation works", "Invalid tokens rejected properly"],
      "issues": ["Token refresh not yet implemented"]
    },
    "PR003946-75": {
      "feature": "Knowledge CRUD",
      "status": "mostly_passing",
      "tests": ["CREATE works", "READ works", "LIST works", "Validation errors proper"],
      "issues": ["DELETE operation not yet tested", "UPDATE needs validation"]
    }
  },

  "integration_tests": {
    "before_implementation": {"passing": 16, "failing": 5},
    "after_implementation": {"passing": 19, "failing": 2}, 
    "improvement": "3 previously failing tests now pass",
    "remaining_failures": ["PR003946-78", "PR003946-82"]
  },

  "error_handling": {
    "validation_errors": "properly_handled",
    "authentication_errors": "proper_401_responses", 
    "not_found_errors": "proper_404_responses",
    "server_errors": "proper_500_with_error_schema"
  },

  "performance_metrics": {
    "average_response_time": "0.234s",
    "max_response_time": "0.456s", 
    "memory_usage": "142MB",
    "cpu_usage": "12%",
    "assessment": "acceptable_performance"
  },

  "validation_summary": {
    "overall_status": "successful",
    "implemented_features_working": "4 of 4",
    "integration_test_improvement": "+3 tests passing",
    "critical_issues": 0,
    "minor_issues": 2,
    "ready_for_submission": true
  },

  "recommendations": [
    "Implementations are working correctly and ready for MR submission",
    "Minor issues (DELETE operations, UPDATE validation) can be addressed in future iterations",
    "Performance is acceptable for current load expectations", 
    "Error handling follows proper patterns and provides good developer experience"
  ],

  "next_steps": {
    "proceed_to_submit": true,
    "address_minor_issues": "optional_future_work",
    "confidence_level": "high"
  }
}
```

## Success Criteria
- All implemented endpoints respond correctly via cURL testing
- Basic CRUD operations function as expected
- Error responses return proper Error schema structure
- Integration tests show measurable improvement
- Performance is acceptable for expected load
- Sequential reasoning predictions align with actual results

## Error Handling
- If system health checks fail, diagnose infrastructure issues first
- If endpoint tests fail, provide detailed failure analysis for debugging  
- If integration tests don't improve, analyze implementation gaps
- Save validation results even if issues are found for /submit phase reference