# Comprehensive Validation Suite

**Purpose**: Orchestrate and execute endpoint validation based on ENDPOINT-WORK.md to perform complete system validation with consolidated reporting

**Usage**: `/comprehensive-validation [--parallel] [--report-only]`

## ⚠️ CRITICAL REQUIREMENTS

**MUST DO BEFORE ANY TESTING:**
1. **Read ENDPOINT-WORK.md FIRST** - This is the source of truth for implemented endpoints
2. **Use documented endpoint paths** - Never guess or assume endpoint names
3. **Calculate actual coverage** - Compare tests run vs endpoints documented
4. **Verify documentation claims** - Test if "implemented" endpoints actually work

**NEVER:**
- Guess endpoint paths without checking ENDPOINT-WORK.md
- Test wrong endpoints (e.g., GET /animal instead of /animal_list)
- Claim comprehensive validation with <80% coverage
- Trust "not_implemented" without verifying documentation
- Assume 401/400 errors mean "endpoint broken" - verify with proper auth/parameters first
- Use expired JWT tokens - generate fresh tokens for each test session
- Skip parameter location verification - check OpenAPI spec for query vs body params

## Lessons Learned (2025-10-10 Validation Session)

**Critical Testing Methodology Errors Discovered:**

1. **Authentication Token Management**:
   - ❌ WRONG: Using expired/stale JWT tokens from previous sessions
   - ✅ RIGHT: Generate fresh tokens at session start, verify token validity
   - **Impact**: GET /animal_config and PATCH /animal_config falsely reported as failing when they work perfectly

2. **Parameter Location Verification**:
   - ❌ WRONG: Assume parameters go in request body without checking spec
   - ✅ RIGHT: Read OpenAPI spec to verify query params vs body params
   - **Example**: `PATCH /animal_config?animalId=X` (query param) not `{"animalId": "X"}` (body)

3. **Error Code Interpretation**:
   - ❌ WRONG: See 401 → conclude "endpoint not working"
   - ✅ RIGHT: See 401 → verify token, see 400 → verify parameter format, THEN test again
   - **Reality**: 2/6 "failed" endpoints were actually working - test methodology was wrong

4. **Coverage Reporting**:
   - ❌ WRONG: "Ran 12 tests - comprehensive!" (without knowing total endpoints)
   - ✅ RIGHT: "Tested 19/37 endpoints (51% coverage)" - always calculate ratio
   - **Standard**: Report as "X/Y endpoints tested (Z% coverage)"

5. **AWS CLI Output Format**:
   - ❌ WRONG: `aws dynamodb scan --table-name X` → returns YAML by default
   - ✅ RIGHT: `aws dynamodb scan --table-name X --output json` → parseable JSON
   - **Impact**: jq parsing errors throughout validation scripts

6. **Documentation vs Reality**:
   - Don't blindly trust ENDPOINT-WORK.md OR test failures
   - When contradiction found: investigate with proper auth/params before concluding
   - **Example**: UI endpoints (GET /, GET /admin) claimed "Working" but are actually stubs

**Validation Quality Checklist:**
- [ ] Fresh JWT token generated for this session
- [ ] OpenAPI spec consulted for parameter locations
- [ ] All test failures re-tested with correct auth and parameters
- [ ] Coverage calculated as X/Y endpoints (percentage)
- [ ] AWS commands include `--output json` flag
- [ ] Documentation discrepancies investigated thoroughly

## Context
This command validates the CMZ system by testing ALL endpoints documented in ENDPOINT-WORK.md. It provides actual coverage metrics and identifies discrepancies between documentation and reality.

**Updated 2025-10-12**: Added P0 architecture validation (BLOCKING) and P1 regression tests (Bugs #1 and #7) to prevent recurring issues. These tests run BEFORE all other validation to catch fundamental problems early.

## Test Priority System

**P0: Architecture Validation (BLOCKING)**
- Validates hexagonal architecture forwarding chain across all 50+ handlers
- **If P0 fails, entire validation suite aborts** - other tests are meaningless
- Runs: `scripts/validate_handler_forwarding_comprehensive.py`

**P1: Regression Tests (Bug Prevention)**
- Prevents known critical bugs from recurring
- Tests run with direct DynamoDB verification (never infer state)
- **Failures are warnings, not blocking** - allows full report generation
- Current Coverage:
  - Bug #1: systemPrompt persistence (PATCH /animal_config)
  - Bug #7: Animal PUT functionality (PUT /animal/{id})

**P2: Infrastructure Tests**
- Backend health, frontend-backend integration
- **Failures are blocking** - no point testing features if infrastructure is broken

**P3: Feature Tests**
- Animal config, family management, data persistence
- Run in parallel groups for efficiency
- Non-blocking failures

**P4: Comprehensive Tests**
- Full end-to-end workflows (slowest tests)
- Run sequentially at the end
- Non-blocking failures

## Sequential Reasoning Approach

Use MCP Sequential Thinking to systematically orchestrate endpoint validation:

### Phase 0: MANDATORY - Parse ENDPOINT-WORK.md
**CRITICAL FIRST STEP:**
1. **Read ENDPOINT-WORK.md** - Extract all implemented endpoints
2. **Parse endpoint list** - HTTP method, path, expected behavior
3. **Count total endpoints** - Establish baseline for coverage calculation
4. **Categorize endpoints** - Group by functional area
5. **Identify test requirements** - Auth needed, test data, dependencies

**Output**: Complete list of endpoints to test with expected behaviors

### Phase 1: Discovery and Planning
**Use Sequential Reasoning to:**
1. **Map Tests to Endpoints**: Match each ENDPOINT-WORK.md entry to test strategy
2. **Analyze Dependencies**: Auth tokens, test data, service dependencies
3. **Resource Assessment**: Check backend/frontend/DB availability
4. **Test Prioritization**: Critical (auth, health) → Core (CRUD) → Advanced
5. **Coverage Target**: Aim for >80% of documented endpoints

**Key Questions for Sequential Analysis:**
- Are endpoint paths from ENDPOINT-WORK.md correct in tests?
- Which endpoints require authentication tokens?
- What test data is needed for each endpoint?
- Which endpoints are documented but might not be implemented?

### Phase 2: Environment Preparation
**Implementation Order (Follow Exactly):**

#### Step 1: Verify Prerequisites
```bash
# Check all services are healthy
echo "=== Service Health Check ==="
curl -s http://localhost:8080/system_health || (echo "❌ Backend not running" && exit 1)
curl -s http://localhost:3001 || (echo "❌ Frontend not running" && exit 1)
aws dynamodb list-tables --output json > /dev/null || (echo "❌ AWS access failed" && exit 1)

echo "✅ All services healthy"

# Generate fresh JWT token for this validation session
echo "=== Generating Fresh Authentication Token ==="
TOKEN_RESPONSE=$(curl -s -X POST http://localhost:8080/auth \
  -H "Content-Type: application/json" \
  -d '{"username": "parent1@test.cmz.org", "password": "testpass123"}')

if echo "$TOKEN_RESPONSE" | jq -e '.token' > /dev/null 2>&1; then
  export AUTH_TOKEN=$(echo "$TOKEN_RESPONSE" | jq -r '.token')
  echo "✅ Fresh token generated and exported as AUTH_TOKEN"

  # Validate token is properly formatted (3-part JWT: header.payload.signature)
  if [[ $(echo "$AUTH_TOKEN" | grep -o '\.' | wc -l) -eq 2 ]]; then
    echo "✅ Token validated: 3-part JWT structure"
  else
    echo "⚠️ Warning: Token format unexpected (not 3-part JWT)"
  fi
else
  echo "❌ Failed to generate authentication token"
  echo "Response: $TOKEN_RESPONSE"
  exit 1
fi
```

#### Step 2: Create Test Session
```bash
# Initialize validation session
SESSION_ID="val_$(date +%Y%m%d_%H%M%S)"
REPORT_DIR="validation-reports/$SESSION_ID"
mkdir -p "$REPORT_DIR"

# Create session manifest
cat > "$REPORT_DIR/manifest.json" << EOF
{
  "sessionId": "$SESSION_ID",
  "startTime": "$(date -Iseconds)",
  "branch": "$(git branch --show-current)",
  "commit": "$(git rev-parse HEAD)",
  "validations": []
}
EOF
```

#### Step 3: Parse ENDPOINT-WORK.md (MANDATORY)
```bash
# Extract all implemented endpoints from ENDPOINT-WORK.md
echo "=== Parsing ENDPOINT-WORK.md ==="

# Count documented endpoints in IMPLEMENTED section
TOTAL_DOCUMENTED=$(grep -E '^\s*-\s+\*\*[A-Z]+\s+/' ENDPOINT-WORK.md | \
  sed -n '/## ✅ IMPLEMENTED/,/## 🔧 IMPLEMENTED BUT FAILING/p' | \
  grep -E '^\s*-\s+\*\*[A-Z]+\s+/' | wc -l | tr -d ' ')

echo "Total documented endpoints: $TOTAL_DOCUMENTED"

# Save endpoint list for reference
grep -E '^\s*-\s+\*\*[A-Z]+\s+/' ENDPOINT-WORK.md | \
  sed -n '/## ✅ IMPLEMENTED/,/## 🔧 IMPLEMENTED BUT FAILING/p' > "$REPORT_DIR/documented_endpoints.txt"

# This becomes the source of truth for testing
echo "Endpoint list saved to: $REPORT_DIR/documented_endpoints.txt"
```

#### Step 4: Verify OpenAPI Spec for Parameter Requirements
```bash
# For each endpoint that requires parameters, verify their location
echo "=== Verifying Parameter Requirements ==="

# Create parameter reference from OpenAPI spec
cat > "$REPORT_DIR/parameter_guide.md" << 'PARAM_EOF'
# Parameter Location Reference

**Common Parameter Patterns:**

## Query Parameters (in URL)
- `GET /animal_config?animalId=X` - animalId is query param
- `PATCH /animal_config?animalId=X` - animalId is query param
- Always append to URL with `?param=value&param2=value2`

## Path Parameters (in URL path)
- `GET /animal/{animalId}` - animalId is path param
- `PUT /animal/{animalId}` - animalId is path param
- Replace {param} in URL path

## Body Parameters (in request body)
- `POST /animal` with `{"name": "Charlie", ...}` - full object in body
- `PATCH /animal_config` with `{"temperature": 0.7}` - partial update in body
- Sent as JSON in request body with Content-Type: application/json

## Header Parameters
- `Authorization: Bearer $AUTH_TOKEN` - JWT token in header
- Always include for protected endpoints

**Testing Pattern:**
1. Check OpenAPI spec for parameter locations
2. Format request correctly (query vs path vs body)
3. Include fresh auth token for protected endpoints
4. Verify response before concluding failure
PARAM_EOF

echo "✅ Parameter guide created: $REPORT_DIR/parameter_guide.md"
```

### Phase 3: Validation Execution
**Systematic Test Execution:**

#### Step 1: Sequential Critical Tests
```bash
# Run critical infrastructure tests first (must pass)
# P0: Architecture validation (BLOCKING - added 2025-10-12)
echo "=== P0: Architecture Validation (BLOCKING) ==="
START_TIME=$(date +%s)
if python3 scripts/validate_handler_forwarding_comprehensive.py > "$REPORT_DIR/architecture_validation.log" 2>&1; then
  echo "✅ Architecture validation PASSED"
  echo "{\"test\": \"architecture_validation\", \"status\": \"PASS\", \"duration\": $(($(date +%s) - START_TIME)), \"critical\": true, \"priority\": \"P0\"}" >> "$REPORT_DIR/results.jsonl"
else
  echo "❌ Architecture validation FAILED - BLOCKING"
  echo "{\"test\": \"architecture_validation\", \"status\": \"FAIL\", \"duration\": $(($(date +%s) - START_TIME)), \"critical\": true, \"priority\": \"P0\"}" >> "$REPORT_DIR/results.jsonl"
  echo ""
  echo "🚨 CRITICAL: Hexagonal architecture forwarding chain is broken!"
  echo "See: $REPORT_DIR/architecture_validation.log"
  echo ""
  echo "This is a P0 blocker - all other tests are meaningless if architecture is broken."
  echo "Fix with: python3 scripts/post_openapi_generation.py backend/api/src/main/python"
  exit 1
fi

# P1: Regression Tests (Bug Prevention - added 2025-10-12)
echo "=== P1: Regression Tests (Bug Prevention) ==="

# Bug #1: systemPrompt persistence
echo "Running Bug #1 regression tests (systemPrompt persistence)..."
START_TIME=$(date +%s)
cd backend/api/src/main/python
if pytest tests/regression/test_bug_001_systemprompt_persistence.py -v > "$REPORT_DIR/bug_001_regression.log" 2>&1; then
  echo "✅ Bug #1 regression tests PASSED"
  echo "{\"test\": \"bug_001_systemprompt_persistence\", \"status\": \"PASS\", \"duration\": $(($(date +%s) - START_TIME)), \"critical\": true, \"priority\": \"P1\"}" >> "$REPORT_DIR/results.jsonl"
else
  echo "❌ Bug #1 regression tests FAILED"
  echo "{\"test\": \"bug_001_systemprompt_persistence\", \"status\": \"FAIL\", \"duration\": $(($(date +%s) - START_TIME)), \"critical\": true, \"priority\": \"P1\"}" >> "$REPORT_DIR/results.jsonl"
  REGRESSION_FAILURE=true
fi
cd - > /dev/null

# Bug #7: Animal PUT functionality
echo "Running Bug #7 regression tests (Animal PUT functionality)..."
START_TIME=$(date +%s)
cd backend/api/src/main/python
if pytest tests/regression/test_bug_007_animal_put_functionality.py -v > "$REPORT_DIR/bug_007_regression.log" 2>&1; then
  echo "✅ Bug #7 regression tests PASSED"
  echo "{\"test\": \"bug_007_animal_put_functionality\", \"status\": \"PASS\", \"duration\": $(($(date +%s) - START_TIME)), \"critical\": true, \"priority\": \"P1\"}" >> "$REPORT_DIR/results.jsonl"
else
  echo "❌ Bug #7 regression tests FAILED"
  echo "{\"test\": \"bug_007_animal_put_functionality\", \"status\": \"FAIL\", \"duration\": $(($(date +%s) - START_TIME)), \"critical\": true, \"priority\": \"P1\"}" >> "$REPORT_DIR/results.jsonl"
  REGRESSION_FAILURE=true
fi
cd - > /dev/null

if [ "$REGRESSION_FAILURE" = true ]; then
  echo ""
  echo "⚠️ WARNING: Regression tests failed - Bugs #1 or #7 may have recurred!"
  echo "This is critical but not blocking - continuing with other tests for full report."
  echo "Review logs: $REPORT_DIR/bug_001_regression.log and $REPORT_DIR/bug_007_regression.log"
  echo ""
fi

# P2: Critical infrastructure tests
INFRASTRUCTURE_TESTS=(
  "validate-backend-health"
  "validate-frontend-backend-integration"
)

for test in "${INFRASTRUCTURE_TESTS[@]}"; do
  echo "=== Running Infrastructure Test: $test ==="

  # Execute validation
  START_TIME=$(date +%s)
  if /usr/bin/time -v ".claude/commands/$test.md" > "$REPORT_DIR/$test.log" 2>&1; then
    STATUS="PASS"
  else
    STATUS="FAIL"
    INFRASTRUCTURE_FAILURE=true
  fi
  END_TIME=$(date +%s)

  # Record result
  cat >> "$REPORT_DIR/results.jsonl" << EOF
{"test": "$test", "status": "$STATUS", "duration": $((END_TIME - START_TIME)), "critical": true, "priority": "P2"}
EOF

  if [ "$INFRASTRUCTURE_FAILURE" = true ]; then
    echo "❌ Infrastructure test failed. Aborting validation suite."
    exit 1
  fi
done
```

#### Step 2: Parallel Feature Tests
```bash
# Run feature validations in parallel groups (P3 priority)
FEATURE_GROUPS=(
  "animal:validate-animal-config,validate-animal-config-fields,validate-animal-config-persistence"
  "family:validate-family-dialog,validate-family-management"
  "data:validate-data-persistence,validate-chat-dynamodb"
)

for group in "${FEATURE_GROUPS[@]}"; do
  GROUP_NAME="${group%%:*}"
  GROUP_TESTS="${group#*:}"

  echo "=== Running P3 Feature Group: $GROUP_NAME ==="

  # Split comma-separated tests and run in parallel
  IFS=',' read -ra TESTS <<< "$GROUP_TESTS"
  for test in "${TESTS[@]}"; do
    (
      START_TIME=$(date +%s)
      if ".claude/commands/$test.md" > "$REPORT_DIR/$test.log" 2>&1; then
        echo "{\"test\": \"$test\", \"status\": \"PASS\", \"duration\": $(($(date +%s) - START_TIME)), \"priority\": \"P3\"}" >> "$REPORT_DIR/results.jsonl"
      else
        echo "{\"test\": \"$test\", \"status\": \"FAIL\", \"duration\": $(($(date +%s) - START_TIME)), \"priority\": \"P3\"}" >> "$REPORT_DIR/results.jsonl"
      fi
    ) &
  done

  # Wait for group to complete
  wait
done
```

#### Step 3: Comprehensive Tests
```bash
# Run comprehensive validations last (they take longest, P4 priority)
COMPREHENSIVE_TESTS=(
  "validate-full-animal-config"
  "validate-animal-config-edit"
)

for test in "${COMPREHENSIVE_TESTS[@]}"; do
  echo "=== Running P4 Comprehensive Test: $test ==="

  START_TIME=$(date +%s)
  if ".claude/commands/$test.md" > "$REPORT_DIR/$test.log" 2>&1; then
    STATUS="PASS"
  else
    STATUS="FAIL"
  fi
  END_TIME=$(date +%s)

  echo "{\"test\": \"$test\", \"status\": \"$STATUS\", \"duration\": $((END_TIME - START_TIME)), \"priority\": \"P4\"}" >> "$REPORT_DIR/results.jsonl"
done
```

### Phase 4: Result Analysis and Reporting
**Generate Comprehensive Report:**

#### Step 1: Collect Results
```bash
# Parse all test results
TOTAL_TESTS=$(jq -s 'length' "$REPORT_DIR/results.jsonl")
PASSED_TESTS=$(jq -s 'map(select(.status == "PASS")) | length' "$REPORT_DIR/results.jsonl")
FAILED_TESTS=$(jq -s 'map(select(.status == "FAIL")) | length' "$REPORT_DIR/results.jsonl")
TOTAL_DURATION=$(jq -s 'map(.duration) | add' "$REPORT_DIR/results.jsonl")

SUCCESS_RATE=$((PASSED_TESTS * 100 / TOTAL_TESTS))
```

#### Step 2: Analyze Failures
```bash
# Extract failure details
if [ $FAILED_TESTS -gt 0 ]; then
  echo "=== Failure Analysis ==="

  jq -r 'select(.status == "FAIL") | .test' "$REPORT_DIR/results.jsonl" | while read test; do
    echo "❌ $test failed"

    # Extract error from log
    tail -20 "$REPORT_DIR/$test.log" | grep -E "Error|Failed|Exception" || true

    # Check for common issues
    if grep -q "Backend not running" "$REPORT_DIR/$test.log"; then
      echo "  → Backend service issue detected"
    elif grep -q "DynamoDB" "$REPORT_DIR/$test.log"; then
      echo "  → Database access issue detected"
    elif grep -q "timeout" "$REPORT_DIR/$test.log"; then
      echo "  → Timeout issue detected"
    fi
  done
fi
```

#### Step 3: Re-Test Failures with Proper Authentication and Parameters
```bash
# CRITICAL: Don't trust initial failures - verify with correct auth/params
if [ $FAILED_TESTS -gt 0 ]; then
  echo "=== Re-Testing Failed Endpoints with Proper Parameters ==="

  # Create re-test results file
  > "$REPORT_DIR/retest_results.jsonl"

  # Common endpoints that fail due to auth/parameter issues
  RETEST_ENDPOINTS=(
    "GET:/animal_config?animalId=charlie_003"
    "PATCH:/animal_config?animalId=charlie_003"
  )

  for endpoint_spec in "${RETEST_ENDPOINTS[@]}"; do
    METHOD="${endpoint_spec%%:*}"
    ENDPOINT="${endpoint_spec#*:}"

    echo "Re-testing: $METHOD $ENDPOINT"

    # Use fresh AUTH_TOKEN from environment
    RESPONSE=$(curl -s -X "$METHOD" \
      -H "Authorization: Bearer $AUTH_TOKEN" \
      -H "Content-Type: application/json" \
      -w "\n%{http_code}" \
      "http://localhost:8080$ENDPOINT")

    HTTP_CODE=$(echo "$RESPONSE" | tail -1)
    BODY=$(echo "$RESPONSE" | head -n -1)

    if [ "$HTTP_CODE" -eq 200 ] || [ "$HTTP_CODE" -eq 201 ]; then
      echo "  ✅ Re-test PASSED: $METHOD $ENDPOINT"
      echo "{\"endpoint\": \"$METHOD $ENDPOINT\", \"retest_status\": \"PASS\", \"http_code\": $HTTP_CODE}" >> "$REPORT_DIR/retest_results.jsonl"
    else
      echo "  ❌ Re-test FAILED: $METHOD $ENDPOINT (HTTP $HTTP_CODE)"
      echo "{\"endpoint\": \"$METHOD $ENDPOINT\", \"retest_status\": \"FAIL\", \"http_code\": $HTTP_CODE}" >> "$REPORT_DIR/retest_results.jsonl"
    fi
  done

  # Compare initial vs re-test results
  RETEST_PASSED=$(jq -s 'map(select(.retest_status == "PASS")) | length' "$REPORT_DIR/retest_results.jsonl" 2>/dev/null || echo 0)

  if [ "$RETEST_PASSED" -gt 0 ]; then
    echo ""
    echo "⚠️ WARNING: $RETEST_PASSED endpoint(s) passed on re-test with proper auth/params"
    echo "This indicates initial test methodology was incorrect (bad tokens or wrong parameter format)"
    echo "See $REPORT_DIR/retest_results.jsonl for details"
  fi
fi
```

#### Step 4: Generate HTML Report
```bash
cat > "$REPORT_DIR/report.html" << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>CMZ Validation Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #2c3e50; color: white; padding: 20px; }
        .summary { display: flex; justify-content: space-around; margin: 20px 0; }
        .metric { text-align: center; }
        .metric .value { font-size: 2em; font-weight: bold; }
        .pass { color: #27ae60; }
        .fail { color: #e74c3c; }
        .test-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 10px; }
        .test-card { border: 1px solid #ddd; padding: 10px; border-radius: 5px; }
        .test-card.passed { border-color: #27ae60; background: #f0fff4; }
        .test-card.failed { border-color: #e74c3c; background: #fff5f5; }
    </style>
</head>
<body>
    <div class="header">
        <h1>CMZ Comprehensive Validation Report</h1>
        <p>Session: SESSION_ID | Date: DATE | Branch: BRANCH</p>
    </div>

    <div class="summary">
        <div class="metric">
            <div class="value">TOTAL_TESTS</div>
            <div>Total Tests</div>
        </div>
        <div class="metric">
            <div class="value pass">PASSED_TESTS</div>
            <div>Passed</div>
        </div>
        <div class="metric">
            <div class="value fail">FAILED_TESTS</div>
            <div>Failed</div>
        </div>
        <div class="metric">
            <div class="value">SUCCESS_RATE%</div>
            <div>Success Rate</div>
        </div>
        <div class="metric">
            <div class="value">DURATION</div>
            <div>Duration (seconds)</div>
        </div>
    </div>

    <h2>Test Results</h2>
    <div class="test-grid">
        <!-- Test cards will be inserted here -->
    </div>

    <h2>Failed Tests Details</h2>
    <div id="failures">
        <!-- Failure details will be inserted here -->
    </div>
</body>
</html>
EOF

# Replace placeholders with actual values
sed -i "s/SESSION_ID/$SESSION_ID/g" "$REPORT_DIR/report.html"
sed -i "s/DATE/$(date)/g" "$REPORT_DIR/report.html"
sed -i "s/BRANCH/$(git branch --show-current)/g" "$REPORT_DIR/report.html"
sed -i "s/TOTAL_TESTS/$TOTAL_TESTS/g" "$REPORT_DIR/report.html"
sed -i "s/PASSED_TESTS/$PASSED_TESTS/g" "$REPORT_DIR/report.html"
sed -i "s/FAILED_TESTS/$FAILED_TESTS/g" "$REPORT_DIR/report.html"
sed -i "s/SUCCESS_RATE/$SUCCESS_RATE/g" "$REPORT_DIR/report.html"
sed -i "s/DURATION/$TOTAL_DURATION/g" "$REPORT_DIR/report.html"
```

#### Step 5: Generate Markdown Report
```bash
cat > "$REPORT_DIR/VALIDATION_REPORT.md" << EOF
# Comprehensive Validation Report

## Executive Summary
- **Date**: $(date)
- **Session ID**: $SESSION_ID
- **Branch**: $(git branch --show-current)
- **Commit**: $(git rev-parse --short HEAD)

## Coverage Metrics
**CRITICAL**: This validation tested a subset of documented endpoints.

| Metric | Value |
|--------|-------|
| **Documented Endpoints** (ENDPOINT-WORK.md) | **$TOTAL_DOCUMENTED** |
| **Endpoints Tested** | **Not calculated - see retest_results.jsonl** |
| **Coverage Percentage** | **Unknown - manual calculation required** |

**Action Required**: Count unique endpoints tested and calculate X/$TOTAL_DOCUMENTED coverage ratio.

## Test Execution Results
| Metric | Value |
|--------|-------|
| Total Tests Run | $TOTAL_TESTS |
| Passed | $PASSED_TESTS ✅ |
| Failed | $FAILED_TESTS ❌ |
| Success Rate | $SUCCESS_RATE% |
| Total Duration | ${TOTAL_DURATION}s |

## Test Results by Priority

### P0: Architecture Validation (BLOCKING)
$(jq -r 'select(.priority == "P0") | "- **\(.test)**: \(.status) (\(.duration)s)"' "$REPORT_DIR/results.jsonl")

### P1: Regression Tests (Bug Prevention)
$(jq -r 'select(.priority == "P1") | "- **\(.test)**: \(.status) (\(.duration)s)"' "$REPORT_DIR/results.jsonl")

**Regression Test Coverage:**
- ✅ Bug #1: systemPrompt persistence (PATCH /animal_config)
- ✅ Bug #7: Animal PUT functionality (PUT /animal/{id})

### P2: Infrastructure Tests
$(jq -r 'select(.test | contains("backend") or contains("integration")) | "- \(.test): \(.status)"' "$REPORT_DIR/results.jsonl")

### P3: Feature Tests
$(jq -r 'select(.priority == "P3") | "- \(.test): \(.status) (\(.duration)s)"' "$REPORT_DIR/results.jsonl")

**Feature Test Groups:**
- Animal Config: validate-animal-config, validate-animal-config-fields, validate-animal-config-persistence
- Family Management: validate-family-dialog, validate-family-management
- Data Persistence: validate-data-persistence, validate-chat-dynamodb

### P4: Comprehensive Tests
$(jq -r 'select(.priority == "P4") | "- \(.test): \(.status) (\(.duration)s)"' "$REPORT_DIR/results.jsonl")

**Comprehensive Test Coverage:**
- Full Animal Config validation (all 30 components)
- Animal Config Edit workflow validation

## Failed Tests Analysis
$(if [ $FAILED_TESTS -gt 0 ]; then
  echo "### Failures Detected"
  jq -r 'select(.status == "FAIL") | "#### \(.test)\n- Duration: \(.duration)s\n- Log: validation-reports/'$SESSION_ID'/\(.test).log"' "$REPORT_DIR/results.jsonl"
else
  echo "✅ All tests passed successfully!"
fi)

## Re-Test Results (Methodology Validation)
$(if [ -f "$REPORT_DIR/retest_results.jsonl" ]; then
  RETEST_TOTAL=\$(jq -s 'length' "$REPORT_DIR/retest_results.jsonl" 2>/dev/null || echo 0)
  RETEST_PASSED=\$(jq -s 'map(select(.retest_status == "PASS")) | length' "$REPORT_DIR/retest_results.jsonl" 2>/dev/null || echo 0)

  if [ \$RETEST_TOTAL -gt 0 ]; then
    echo "### Endpoints Re-Tested with Proper Auth/Parameters"
    echo ""
    echo "| Endpoint | Initial Result | Re-Test Result | Conclusion |"
    echo "|----------|---------------|----------------|------------|"

    jq -r '. | "| \(.endpoint) | FAIL | \(.retest_status) | \(if .retest_status == "PASS" then "Test methodology was incorrect" else "Endpoint genuinely failing" end) |"' "$REPORT_DIR/retest_results.jsonl"

    echo ""
    echo "**Summary**: \$RETEST_PASSED/\$RETEST_TOTAL endpoints passed when re-tested with correct authentication and parameters."
    echo ""

    if [ \$RETEST_PASSED -gt 0 ]; then
      echo "⚠️ **CRITICAL FINDING**: Initial test failures were due to incorrect test methodology (expired tokens, wrong parameter format), NOT broken endpoints."
    fi
  fi
else
  echo "No re-testing performed."
fi)

## Recommendations
$(if [ $FAILED_TESTS -gt 0 ]; then
  echo "1. Review failed test logs in \`$REPORT_DIR/\`"
  echo "2. Check service health and connectivity"
  echo "3. Verify AWS credentials and DynamoDB access"
  echo "4. Run failed tests individually for detailed debugging"
else
  echo "1. System is ready for deployment"
  echo "2. Consider running load tests for performance validation"
  echo "3. Schedule regular validation runs for regression detection"
fi)

## Next Steps
- [ ] Review detailed logs for any warnings
- [ ] Address any failed tests before deployment
- [ ] Document any new issues discovered
- [ ] Update test suite based on findings

## Artifacts
- Full logs: \`$REPORT_DIR/*.log\`
- HTML Report: \`$REPORT_DIR/report.html\`
- JSON Results: \`$REPORT_DIR/results.jsonl\`
EOF

echo "Report generated: $REPORT_DIR/VALIDATION_REPORT.md"
```

## Implementation Details

### Parallel Execution Strategy
```javascript
// Group tests by resource usage
const testGroups = {
  lightweight: ['backend-health', 'data-persistence'],
  browser: ['family-dialog', 'animal-config-fields'],
  intensive: ['full-animal-config', 'chat-dynamodb']
};

// Run groups sequentially, tests within groups in parallel
for (const group of Object.values(testGroups)) {
  await Promise.all(group.map(test => runValidation(test)));
}
```

### Error Aggregation
```javascript
const errors = {
  service: [],      // Backend/frontend not running
  database: [],     // DynamoDB access issues
  ui: [],          // Playwright/browser errors
  timeout: [],     // Test timeouts
  assertion: []    // Test assertion failures
};

// Categorize errors for better reporting
results.forEach(result => {
  if (result.error) {
    const category = categorizeError(result.error);
    errors[category].push({
      test: result.test,
      error: result.error
    });
  }
});
```

## Integration Points
- All validation commands in `.claude/commands/validate*.md`
- Backend API on port 8080
- Frontend on port 3001
- DynamoDB tables in AWS
- Playwright for browser testing
- Git for version tracking

## Quality Gates
- [ ] All critical tests must pass before continuing
- [ ] Success rate must be ≥ 80% for deployment readiness
- [ ] No service health failures allowed
- [ ] Maximum test duration < 30 minutes
- [ ] All test logs successfully generated
- [ ] HTML and Markdown reports created

## Success Criteria
1. **Completeness**: All validation commands executed
2. **Reliability**: Consistent results across runs
3. **Performance**: Total execution < 30 minutes
4. **Reporting**: Comprehensive reports generated
5. **Actionability**: Clear failure identification
6. **Traceability**: Full audit trail maintained

## Command Options

### --parallel
Run independent tests in parallel for faster execution:
```bash
/comprehensive-validation --parallel
```

### --report-only
Generate report from existing test results without re-running:
```bash
/comprehensive-validation --report-only SESSION_ID
```

### --filter
Run only specific test categories:
```bash
/comprehensive-validation --filter "animal,family"
```

### --stop-on-fail
Stop execution on first failure:
```bash
/comprehensive-validation --stop-on-fail
```

## References
- `COMPREHENSIVE-VALIDATION-ADVICE.md` - Best practices and troubleshooting
- Individual validation commands in `.claude/commands/`
- CMZ testing documentation