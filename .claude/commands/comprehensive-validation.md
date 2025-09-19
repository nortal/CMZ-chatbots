# Comprehensive Validation Suite

**Purpose**: Orchestrate and execute all validation commands in `.claude/commands/validate*.md` to perform complete system validation with consolidated reporting

**Usage**: `/comprehensive-validation [--parallel] [--report-only]`

## Context
This command runs all CMZ validation tests systematically, collecting results and generating a comprehensive validation report. It identifies failures across all features including animal config, family management, chat history, backend health, and frontend-backend integration.

## Sequential Reasoning Approach

Use MCP Sequential Thinking to systematically orchestrate all validations:

### Phase 1: Discovery and Planning
**Use Sequential Reasoning to:**
1. **Enumerate Validation Commands**: Discover all validate*.md files
2. **Analyze Dependencies**: Determine which tests can run in parallel
3. **Resource Assessment**: Check system capacity for parallel execution
4. **Test Prioritization**: Order tests by criticality and dependencies
5. **Execution Strategy**: Plan optimal execution sequence

**Key Questions for Sequential Analysis:**
- Which validations are independent and can run in parallel?
- What's the optimal execution order to minimize total time?
- Which tests are most likely to reveal critical issues?
- How much system resource does each validation consume?

### Phase 2: Environment Preparation
**Implementation Order (Follow Exactly):**

#### Step 1: Verify Prerequisites
```bash
# Check all services are healthy
echo "=== Service Health Check ==="
curl -s http://localhost:8080/health || (echo "❌ Backend not running" && exit 1)
curl -s http://localhost:3001 || (echo "❌ Frontend not running" && exit 1)
aws dynamodb list-tables > /dev/null || (echo "❌ AWS access failed" && exit 1)

echo "✅ All services healthy"
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

#### Step 3: Enumerate Validations
```bash
# List all validation commands
VALIDATIONS=(
  "validate-animal-config"
  "validate-animal-config-edit"
  "validate-animal-config-fields"
  "validate-animal-config-persistence"
  "validate-backend-health"
  "validate-chat-dynamodb"
  "validate-data-persistence"
  "validate-family-dialog"
  "validate-family-management"
  "validate-frontend-backend-integration"
  "validate-full-animal-config"
)

echo "Found ${#VALIDATIONS[@]} validation commands"
```

### Phase 3: Validation Execution
**Systematic Test Execution:**

#### Step 1: Sequential Critical Tests
```bash
# Run critical infrastructure tests first (must pass)
CRITICAL_TESTS=(
  "validate-backend-health"
  "validate-frontend-backend-integration"
)

for test in "${CRITICAL_TESTS[@]}"; do
  echo "=== Running Critical Test: $test ==="

  # Execute validation
  START_TIME=$(date +%s)
  if /usr/bin/time -v ".claude/commands/$test.md" > "$REPORT_DIR/$test.log" 2>&1; then
    STATUS="PASS"
  else
    STATUS="FAIL"
    CRITICAL_FAILURE=true
  fi
  END_TIME=$(date +%s)

  # Record result
  cat >> "$REPORT_DIR/results.jsonl" << EOF
{"test": "$test", "status": "$STATUS", "duration": $((END_TIME - START_TIME)), "critical": true}
EOF

  if [ "$CRITICAL_FAILURE" = true ]; then
    echo "❌ Critical test failed. Aborting validation suite."
    exit 1
  fi
done
```

#### Step 2: Parallel Feature Tests
```bash
# Run feature validations in parallel groups
FEATURE_GROUPS=(
  "animal:validate-animal-config,validate-animal-config-fields,validate-animal-config-persistence"
  "family:validate-family-dialog,validate-family-management"
  "data:validate-data-persistence,validate-chat-dynamodb"
)

for group in "${FEATURE_GROUPS[@]}"; do
  GROUP_NAME="${group%%:*}"
  GROUP_TESTS="${group#*:}"

  echo "=== Running Feature Group: $GROUP_NAME ==="

  # Split comma-separated tests and run in parallel
  IFS=',' read -ra TESTS <<< "$GROUP_TESTS"
  for test in "${TESTS[@]}"; do
    (
      START_TIME=$(date +%s)
      if ".claude/commands/$test.md" > "$REPORT_DIR/$test.log" 2>&1; then
        echo "{\"test\": \"$test\", \"status\": \"PASS\", \"duration\": $(($(date +%s) - START_TIME))}" >> "$REPORT_DIR/results.jsonl"
      else
        echo "{\"test\": \"$test\", \"status\": \"FAIL\", \"duration\": $(($(date +%s) - START_TIME))}" >> "$REPORT_DIR/results.jsonl"
      fi
    ) &
  done

  # Wait for group to complete
  wait
done
```

#### Step 3: Comprehensive Tests
```bash
# Run comprehensive validations last (they take longest)
COMPREHENSIVE_TESTS=(
  "validate-full-animal-config"
  "validate-animal-config-edit"
)

for test in "${COMPREHENSIVE_TESTS[@]}"; do
  echo "=== Running Comprehensive Test: $test ==="

  START_TIME=$(date +%s)
  if ".claude/commands/$test.md" > "$REPORT_DIR/$test.log" 2>&1; then
    STATUS="PASS"
  else
    STATUS="FAIL"
  fi
  END_TIME=$(date +%s)

  echo "{\"test\": \"$test\", \"status\": \"$STATUS\", \"duration\": $((END_TIME - START_TIME))}" >> "$REPORT_DIR/results.jsonl"
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

#### Step 3: Generate HTML Report
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

#### Step 4: Generate Markdown Report
```bash
cat > "$REPORT_DIR/VALIDATION_REPORT.md" << EOF
# Comprehensive Validation Report

## Executive Summary
- **Date**: $(date)
- **Session ID**: $SESSION_ID
- **Branch**: $(git branch --show-current)
- **Commit**: $(git rev-parse --short HEAD)

## Results Overview
| Metric | Value |
|--------|-------|
| Total Tests | $TOTAL_TESTS |
| Passed | $PASSED_TESTS ✅ |
| Failed | $FAILED_TESTS ❌ |
| Success Rate | $SUCCESS_RATE% |
| Total Duration | ${TOTAL_DURATION}s |

## Test Results by Category

### Infrastructure Tests
$(jq -r 'select(.test | contains("backend") or contains("integration")) | "- \(.test): \(.status)"' "$REPORT_DIR/results.jsonl")

### Animal Config Tests
$(jq -r 'select(.test | contains("animal")) | "- \(.test): \(.status)"' "$REPORT_DIR/results.jsonl")

### Family Management Tests
$(jq -r 'select(.test | contains("family")) | "- \(.test): \(.status)"' "$REPORT_DIR/results.jsonl")

### Data Persistence Tests
$(jq -r 'select(.test | contains("data") or contains("chat")) | "- \(.test): \(.status)"' "$REPORT_DIR/results.jsonl")

## Failed Tests Analysis
$(if [ $FAILED_TESTS -gt 0 ]; then
  echo "### Failures Detected"
  jq -r 'select(.status == "FAIL") | "#### \(.test)\n- Duration: \(.duration)s\n- Log: validation-reports/'$SESSION_ID'/\(.test).log"' "$REPORT_DIR/results.jsonl"
else
  echo "✅ All tests passed successfully!"
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