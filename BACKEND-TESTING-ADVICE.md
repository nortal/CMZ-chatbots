# Backend Testing Agent - Best Practices and Advice

**Purpose**: Guidance for using the backend comprehensive testing agent effectively

**Related Files:**
- `.claude/commands/backend-testing.md` - Agent command and methodology
- `ENDPOINT-WORK-ADVICE.md` - OpenAPI generation patterns and troubleshooting
- `VALIDATE-DATA-PERSISTENCE-ADVICE.md` - DynamoDB verification patterns
- `TEST-ORCHESTRATION-ADVICE.md` - Multi-layer testing coordination

---

## Overview

The backend testing agent provides comprehensive REST API testing with:
- OpenAPI specification validation
- Edge case testing (25+ per field)
- DynamoDB persistence verification
- Intelligent error classification
- Automatic test cleanup
- Integration with root-cause-analyst for "not implemented" errors

---

## When to Use Backend Testing Agent

### Primary Use Cases

**1. New Feature Development**
- After implementing backend endpoint
- Before frontend integration
- To validate OpenAPI spec completeness
- To discover edge case handling gaps

**2. OpenAPI Specification Changes**
- After adding/modifying endpoints
- After changing field validation rules
- After updating data models
- To verify spec-implementation alignment

**3. Bug Validation**
- To reproduce reported backend issues
- To verify bug fixes don't introduce regressions
- To validate edge cases after fixes

**4. Pre-Deployment Validation**
- Complete backend endpoint testing
- OpenAPI specification completeness check
- DynamoDB persistence verification
- Edge case handling validation

### Integration Points

**Works With:**
- `test-orchestrator` - Delegates backend testing
- `frontend-comprehensive-testing` - Backend health validation
- `backend-architect` - Reports findings and recommendations
- `root-cause-analyst` - Investigates "not implemented" errors
- `feature-documentation` - Updates docs with validated behavior

**Input From:**
- `backend/api/openapi_spec.yaml` - API specification
- `claudedocs/features/*/backend/` - Feature documentation
- `backend/api/src/main/python/openapi_server/impl/` - Implementation code

**Output To:**
- `claudedocs/testing/backend/` - Test reports
- Teams channel - Test result notifications
- Feature documentation - Validated edge cases

---

## Best Practices

### OpenAPI Specification Validation

**DO:**
- ✅ Validate OpenAPI spec BEFORE testing endpoints
- ✅ Report missing validations as bugs with severity
- ✅ Test reasonable boundaries even if spec incomplete
- ✅ Document assumptions made when spec unclear
- ✅ Recommend specific OpenAPI constraints

**DON'T:**
- ❌ Skip OpenAPI validation phase
- ❌ Assume reasonable defaults without documenting
- ❌ Report spec gaps as implementation bugs
- ❌ Test without understanding expected behavior

**Example Report:**
```markdown
## OpenAPI Specification Gaps

### CRITICAL - No Validation Constraints
- **Endpoint**: POST /animal
- **Field**: systemPrompt
- **Issue**: No minLength, maxLength specified
- **Risk**: Unlimited input → DoS attack vector
- **Test Approach**: Testing with maxLength=5000 (reasonable default)
- **Recommendation**: Add `maxLength: 5000, minLength: 1`
```

### Edge Case Testing

**DO:**
- ✅ Test ALL edge cases for ALL fields
- ✅ Include Unicode tests (Chinese, Arabic, emoji)
- ✅ Test security inputs (XSS, SQL injection, command injection)
- ✅ Test boundary conditions (min, max, below, above)
- ✅ Test type mismatches (string for number, etc.)
- ✅ Document expected behavior for each edge case

**DON'T:**
- ❌ Skip edge cases due to time pressure
- ❌ Assume validation works without testing
- ❌ Test only happy path scenarios
- ❌ Forget to test very large inputs
- ❌ Skip Unicode testing (international users exist!)

**Edge Case Categories:**

**String Fields (25+ tests):**
```python
edge_cases = {
    # Length boundaries
    "empty": "",
    "single_char": "a",
    "at_min": "a" * min_length,
    "at_max": "a" * max_length,
    "below_min": "a" * (min_length - 1),  # Should fail
    "above_max": "a" * (max_length + 1),  # Should fail
    "very_large": "a" * 100000,           # Should fail

    # Unicode
    "chinese": "这是一个测试",
    "arabic": "هذا اختبار",
    "russian": "Это тест",
    "japanese": "これはテストです",
    "hebrew": "זה מבחן",
    "emojis": "🦁🐯🐻🦊",
    "mixed_unicode": "Hello 你好 مرحبا",
    "rtl": "مرحبا بك",  # Right-to-left text

    # Security (should all fail)
    "html_tags": "<script>alert('xss')</script>",
    "img_onerror": "<img src=x onerror=alert('xss')>",
    "sql_injection": "'; DROP TABLE animals; --",
    "command_injection": "; rm -rf /",
    "path_traversal": "../../etc/passwd",
    "null_bytes": "test\x00malicious",

    # Whitespace
    "leading_spaces": "  test",
    "trailing_spaces": "test  ",
    "multiple_spaces": "test    multiple",
    "only_spaces": "     ",
    "tabs": "test\t\ttabs",
    "newlines": "test\n\nnewlines",
    "mixed_whitespace": "  test \t\n  ",

    # Large content
    "lorem_ipsum": LOREM_500_CHARS,
    "five_paragraphs": LOREM_2000_CHARS,
    "very_large_block": "a" * 10000,
}
```

**Numeric Fields (15+ tests):**
```python
edge_cases = {
    # Boundaries
    "zero": 0,
    "negative_one": -1,
    "negative_large": -999999,
    "at_minimum": minimum,        # If specified in OpenAPI
    "below_minimum": minimum - 1, # Should fail
    "at_maximum": maximum,        # If specified in OpenAPI
    "above_maximum": maximum + 1, # Should fail
    "very_large": 10**100,        # Should fail
    "very_small": -10**100,       # Should fail

    # Decimal precision (for floats)
    "high_precision": 0.123456789,
    "scientific_notation": 1e10,

    # Special values (should fail)
    "infinity": float('inf'),
    "negative_infinity": float('-inf'),
    "nan": float('nan'),

    # Type mismatches (should fail)
    "string": "not_a_number",
    "array": [1, 2, 3],
    "object": {"value": 5},
}
```

### DynamoDB Persistence Verification

**DO:**
- ✅ Verify EVERY successful request persists to DynamoDB
- ✅ Compare ALL field values (not just primary key)
- ✅ Check nested objects preserved correctly
- ✅ Verify arrays contain correct items
- ✅ Validate timestamps populated
- ✅ Test data type preservation (number vs string)

**DON'T:**
- ❌ Assume persistence works without verification
- ❌ Only check if item exists (verify ALL fields)
- ❌ Skip verification for "simple" endpoints
- ❌ Forget to check nested/complex data structures

**Verification Pattern:**
```bash
# 1. Make REST API call
curl -X POST http://localhost:8080/animal \
  -H "Content-Type: application/json" \
  -d '{
    "animalId": "test_12345",
    "systemPrompt": "Test prompt",
    "temperature": 0.7,
    "details": {
      "age": 5,
      "habitat": "Forest"
    },
    "tags": ["mammal", "carnivore"]
  }' \
  -o response.json

# 2. Query DynamoDB
aws dynamodb get-item \
  --table-name cmz-animals \
  --key '{"animalId": {"S": "test_12345"}}' \
  --profile cmz \
  --output json > dynamo_item.json

# 3. Compare request with DynamoDB item
# Verify ALL fields match:
EXPECTED_PROMPT="Test prompt"
ACTUAL_PROMPT=$(jq -r '.Item.systemPrompt.S' dynamo_item.json)

if [ "$EXPECTED_PROMPT" != "$ACTUAL_PROMPT" ]; then
  echo "❌ PERSISTENCE MISMATCH: systemPrompt"
  echo "Expected: $EXPECTED_PROMPT"
  echo "Actual: $ACTUAL_PROMPT"
fi

# Verify nested objects
EXPECTED_AGE=5
ACTUAL_AGE=$(jq -r '.Item.details.M.age.N' dynamo_item.json)

if [ "$EXPECTED_AGE" != "$ACTUAL_AGE" ]; then
  echo "❌ PERSISTENCE MISMATCH: details.age"
fi

# Verify arrays
EXPECTED_TAG_COUNT=2
ACTUAL_TAG_COUNT=$(jq '.Item.tags.L | length' dynamo_item.json)

if [ "$EXPECTED_TAG_COUNT" != "$ACTUAL_TAG_COUNT" ]; then
  echo "❌ PERSISTENCE MISMATCH: tags array length"
fi
```

### Test Cleanup

**DO:**
- ✅ Delete ALL test data after EVERY test
- ✅ Verify deletion succeeded
- ✅ Use unique identifiers (UUIDs) for test data
- ✅ Query for remaining test items at end
- ✅ Generate cleanup report

**DON'T:**
- ❌ Leave test data in production tables
- ❌ Assume deletion succeeded without verification
- ❌ Use static test IDs (causes conflicts)
- ❌ Skip cleanup on test failures

**Cleanup Pattern:**
```bash
# Generate unique test ID
TEST_ID="test_$(uuidgen)"

# Use in test
curl -X POST http://localhost:8080/animal \
  -d '{"animalId": "'${TEST_ID}'", ...}'

# After test (success or failure)
aws dynamodb delete-item \
  --table-name cmz-animals \
  --key '{"animalId": {"S": "'${TEST_ID}'"}}' \
  --profile cmz

# Verify deletion
ITEM=$(aws dynamodb get-item \
  --table-name cmz-animals \
  --key '{"animalId": {"S": "'${TEST_ID}'"}}' \
  --profile cmz \
  --output json)

if [ -n "$(echo $ITEM | jq '.Item')" ]; then
  echo "⚠️ CLEANUP FAILED: Item still exists"
else
  echo "✅ Cleanup successful"
fi
```

**Final Verification (End of Testing):**
```bash
# Query for ALL test items
aws dynamodb scan \
  --table-name cmz-animals \
  --filter-expression "begins_with(animalId, :prefix)" \
  --expression-attribute-values '{":prefix": {"S": "test_"}}' \
  --profile cmz \
  --output json

# Should return 0 items
ITEM_COUNT=$(echo $RESULT | jq '.Items | length')

if [ "$ITEM_COUNT" -eq 0 ]; then
  echo "✅ ALL test data cleaned up"
else
  echo "⚠️ WARNING: $ITEM_COUNT test items remain in DynamoDB"
  echo "Items: $(echo $RESULT | jq '.Items[].animalId.S')"
fi
```

### "Not Implemented" Error Handling

**CRITICAL**: DO NOT immediately report as backend bug!

**DO:**
- ✅ Delegate to root-cause-analyst FIRST
- ✅ Check if handler exists in impl/ modules
- ✅ Verify controller routing is correct
- ✅ Check OpenAPI generation timestamps
- ✅ Look for "do some magic!" placeholders
- ✅ Classify error with evidence

**DON'T:**
- ❌ Report as backend bug without investigation
- ❌ Skip root cause analysis due to time pressure
- ❌ Assume all 501 errors are unimplemented features

**Why This Matters:**
```
OpenAPI regeneration FREQUENTLY disconnects handlers from controllers!

Symptoms:
- HTTP 501 Not Implemented
- "do some magic!" in controller
- Handler exists in impl/ but isn't called

Root Cause:
- `make generate-api` regenerates controllers
- Generated controller doesn't import handler
- Handler exists and works, but isn't connected

Solution:
- Run `make post-generate` after generation
- Fixes controller routing automatically
- Handler reconnected, endpoint works again
```

**Investigation Pattern:**
```python
# ALWAYS delegate to root-cause-analyst
Task(
    subagent_type="root-cause-analyst",
    description="Investigate not implemented error",
    prompt="""Investigate 501/not implemented error on POST /animal.

    CRITICAL: Read ENDPOINT-WORK-ADVICE.md to understand OpenAPI patterns.

    Test Details:
    - Endpoint: POST /animal
    - Method: POST
    - Request: {"animalId": "test_123", "systemPrompt": "test"}
    - Response: {"error": "Not implemented"}
    - HTTP Status: 501

    Investigation Steps:
    1. Check if handler exists:
       grep -r "def handle_" backend/api/src/main/python/openapi_server/impl/animals.py

    2. Check controller routing:
       grep -A5 "def animal_post" backend/api/src/main/python/openapi_server/controllers/animal_controller.py

    3. Check for OpenAPI artifacts:
       grep "do some magic" backend/api/src/main/python/openapi_server/controllers/*.py

    4. Check generation timestamp:
       ls -la backend/api/src/main/python/openapi_server/controllers/

    Classify Error:
    - TRUE BUG: Handler missing or broken
    - OPENAPI ARTIFACT: Handler exists but controller disconnected
    - TEST ARTIFACT: Test setup issue (wrong URL, auth, etc.)

    Provide Evidence:
    - Handler location: impl/animals.py:45
    - Handler signature: def handle_animal_post(body)
    - Controller imports: from impl import animals vs. pass
    - "do some magic!" found: Yes/No
    - Generation timestamp: 2025-01-14 10:30 (after last impl/ change)
    - Classification: OPENAPI_ARTIFACT

    If OPENAPI_ARTIFACT:
    Recommendation: Run `make post-generate` to fix controller routing
    """
)

# WAIT for root-cause-analyst response
# THEN classify error based on evidence
```

**Error Classification:**
```markdown
## Not Implemented Error Investigation

### Endpoint: POST /animal

**Error**: HTTP 501 Not Implemented

**Root Cause Analysis**: DELEGATED to root-cause-analyst

**Evidence Collected**:
- ✅ Handler EXISTS: `impl/animals.py:45`
- ✅ Handler signature: `def handle_animal_post(body)`
- ❌ Controller routing: Contains "do some magic!" placeholder
- ❌ Controller imports: `pass` instead of `from impl import animals`
- ⚠️ Generation timestamp: 2025-01-14 10:30 (AFTER handler implemented)

**Classification**: OPENAPI ARTIFACT (NOT a backend bug)

**Root Cause**: OpenAPI regeneration disconnected handler from controller

**Fix Required**: Run `make post-generate` to reconnect handler

**Test Status**: BLOCKED (not a test failure, infrastructure issue)

**Recommendation**: DO NOT report as backend bug
```

---

## Troubleshooting

### Issue: Tests Pass but Data Not in DynamoDB

**Symptoms:**
- HTTP 200/201 responses
- No errors in logs
- DynamoDB query returns empty

**Possible Causes:**

1. **Wrong Table Name**
   ```bash
   # Check environment variable
   echo $FAMILY_DYNAMO_TABLE_NAME

   # Verify table exists
   aws dynamodb describe-table \
     --table-name $FAMILY_DYNAMO_TABLE_NAME \
     --profile cmz
   ```

2. **Wrong Primary Key**
   ```bash
   # Check key schema
   aws dynamodb describe-table \
     --table-name cmz-animals \
     --profile cmz \
     --query 'Table.KeySchema'

   # Verify using correct key in query
   ```

3. **Async Write (Eventual Consistency)**
   ```bash
   # Add delay before verification
   sleep 2

   # Query again
   aws dynamodb get-item ...
   ```

4. **Wrong AWS Profile**
   ```bash
   # Verify profile
   aws sts get-caller-identity --profile cmz

   # Should show CMZ account: 195275676211
   ```

### Issue: Edge Cases Accepted When Should Reject

**Symptoms:**
- Very large inputs accepted (should reject)
- Invalid Unicode accepted (should reject)
- Security inputs accepted (should reject)

**Possible Causes:**

1. **OpenAPI Validation Not Enforced**
   - Backend doesn't validate against OpenAPI spec
   - No validator middleware configured
   - Handler doesn't check input constraints

   **Solution:**
   ```markdown
   ## Bug Report: Input Validation Not Enforced

   **Endpoint**: POST /animal
   **Field**: systemPrompt
   **Issue**: Accepts 100,000 character input (OpenAPI says maxLength: 5000)

   **Reproduction**:
   curl -X POST http://localhost:8080/animal \
     -d '{"systemPrompt": "'$(python -c "print('a' * 100000)")'"}'
   # Returns HTTP 201 (should return HTTP 400)

   **Root Cause**: Backend doesn't validate maxLength constraint

   **Recommendation**:
   1. Add connexion validator middleware
   2. OR add validation in handler:
      if len(body['systemPrompt']) > 5000:
          return {"error": "systemPrompt too long"}, 400
   ```

2. **OpenAPI Spec Missing Constraints**
   - Field has no validation rules defined
   - Testing with reasonable defaults

   **Solution:**
   ```markdown
   ## OpenAPI Specification Gap

   **Endpoint**: POST /animal
   **Field**: systemPrompt
   **Issue**: No maxLength constraint defined

   **Test Approach**: Testing with maxLength=5000 (reasonable default)

   **Recommendation**: Add to OpenAPI spec:
   systemPrompt:
     type: string
     minLength: 1
     maxLength: 5000
   ```

### Issue: DynamoDB Cleanup Fails

**Symptoms:**
- Test items remain in DynamoDB after testing
- "Item still exists" warnings

**Possible Causes:**

1. **Delete Using Wrong Key**
   ```bash
   # Check table key schema
   aws dynamodb describe-table \
     --table-name cmz-animals \
     --profile cmz \
     --query 'Table.KeySchema'

   # Use correct key in delete
   # If composite key (PK + SK):
   aws dynamodb delete-item \
     --table-name cmz-animals \
     --key '{"animalId": {"S": "test_123"}, "sortKey": {"S": "value"}}' \
     --profile cmz
   ```

2. **Conditional Delete Failing**
   ```bash
   # Remove condition expressions if present
   # Simple delete without conditions:
   aws dynamodb delete-item \
     --table-name cmz-animals \
     --key '{"animalId": {"S": "test_123"}}' \
     --profile cmz
   ```

3. **Permissions Issue**
   ```bash
   # Verify delete permissions
   aws iam get-user --profile cmz

   # Check dynamodb:DeleteItem permission
   ```

**Solution**: Batch delete remaining items
```bash
# Find all test items
ITEMS=$(aws dynamodb scan \
  --table-name cmz-animals \
  --filter-expression "begins_with(animalId, :prefix)" \
  --expression-attribute-values '{":prefix": {"S": "test_"}}' \
  --profile cmz \
  --output json)

# Delete each item
echo $ITEMS | jq -r '.Items[].animalId.S' | while read ITEM_ID; do
  aws dynamodb delete-item \
    --table-name cmz-animals \
    --key "{\"animalId\": {\"S\": \"$ITEM_ID\"}}" \
    --profile cmz
  echo "Deleted: $ITEM_ID"
done
```

### Issue: Too Many Tests, Takes Too Long

**Symptoms:**
- Testing takes hours
- 1000+ edge case tests per endpoint

**Solutions:**

1. **Prioritize Edge Cases**
   ```python
   # Test critical edge cases first
   critical_cases = [
       "empty",           # Length: empty string
       "above_max",       # Length: exceed maximum
       "sql_injection",   # Security: SQL injection
       "html_tags",       # Security: XSS
       "chinese",         # Unicode: non-English
       "very_large",      # DoS: huge input
   ]

   # Test all edge cases only if critical tests pass
   ```

2. **Parallel Testing**
   ```bash
   # Test multiple endpoints in parallel
   /backend-testing --endpoint "POST /animal" &
   /backend-testing --endpoint "POST /family" &
   /backend-testing --endpoint "POST /conversation" &
   wait

   # Combine reports
   ```

3. **Focus on High-Risk Fields**
   ```python
   # Prioritize fields that:
   # - Accept user input directly
   # - Are used in security contexts (auth, permissions)
   # - Are displayed to other users (XSS risk)
   # - Are used in queries (SQL injection risk)
   # - Have complex validation rules

   # Skip comprehensive testing for:
   # - Auto-generated fields (IDs, timestamps)
   # - Internal-only fields
   # - Enum fields with 2-3 values
   ```

---

## Integration Patterns

### Pattern 1: Complete Feature Testing

**Use Case**: Testing new feature end-to-end

```python
# Step 1: Backend testing
Task(
    subagent_type="general-purpose",
    description="Backend comprehensive testing",
    prompt="""You are the Backend Testing Agent.

    Test animal-configuration feature comprehensively.

    See .claude/commands/backend-testing.md for methodology.

    Focus:
    - OpenAPI specification validation
    - All edge cases for all fields
    - DynamoDB persistence verification
    - Test cleanup

    Report findings in claudedocs/testing/backend/animal-configuration/
    """
)

# Step 2: Frontend testing (uses backend test results)
Task(
    subagent_type="general-purpose",
    description="Frontend comprehensive testing",
    prompt="""You are the Frontend Testing Agent.

    Test animal-configuration UI comprehensively.

    Prerequisites:
    - Backend testing complete (see report)
    - Backend endpoints verified working

    See .claude/commands/frontend-comprehensive-testing.md
    """
)

# Step 3: Documentation update
Task(
    subagent_type="general-purpose",
    description="Update feature documentation",
    prompt="""You are the Feature Documentation Agent.

    Update animal-configuration documentation with:
    - Validated edge cases from backend testing
    - Confirmed OpenAPI constraints
    - DynamoDB schema verified

    Input: claudedocs/testing/backend/animal-configuration/report.md

    See .claude/commands/document-features.md
    """
)

# Step 4: Teams notification
Task(
    subagent_type="general-purpose",
    description="Send test results to Teams",
    prompt="""You are the Teams Reporting Agent.

    Send animal-configuration test results.

    Read TEAMS-WEBHOOK-ADVICE.md, then:
    python3 scripts/send_teams_report.py test-results \
      --data claudedocs/testing/backend/animal-configuration/summary.json
    """
)
```

### Pattern 2: OpenAPI Spec Validation Only

**Use Case**: Quick validation after OpenAPI changes

```python
Task(
    subagent_type="general-purpose",
    description="Validate OpenAPI specification",
    prompt="""You are the Backend Testing Agent.

    Validate OpenAPI spec completeness (Phase 1 only).

    Steps:
    1. Read backend/api/openapi_spec.yaml
    2. For each endpoint, check all fields have:
       - minLength, maxLength (strings)
       - minimum, maximum (numbers)
       - required fields marked
       - examples provided
    3. Generate gap report
    4. Report critical gaps immediately

    DO NOT run tests. Only analyze specification.

    Output: claudedocs/testing/openapi-gaps-YYYY-MM-DD.md
    """
)
```

### Pattern 3: Regression Testing

**Use Case**: Verify bug fix doesn't introduce regressions

```python
Task(
    subagent_type="general-purpose",
    description="Regression testing after bug fix",
    prompt="""You are the Backend Testing Agent.

    Run regression tests for animal systemPrompt validation fix.

    Bug Fixed:
    - systemPrompt was accepting unlimited length
    - Fix: Added maxLength validation in handler

    Tests Required:
    1. Verify fix works:
       - Test systemPrompt with 5001 chars → should reject
       - Test systemPrompt with 5000 chars → should accept

    2. Verify no regressions:
       - Re-run ALL systemPrompt edge cases
       - Re-run other animal endpoint tests
       - Verify DynamoDB persistence still works

    Report any new failures immediately.

    See .claude/commands/backend-testing.md Phase 3
    """
)
```

### Pattern 4: Coordinated with Test Orchestrator

**Use Case**: Complete validation suite

```python
# Test orchestrator delegates to backend testing
Task(
    subagent_type="general-purpose",
    description="Orchestrate complete validation",
    prompt="""You are the Test Orchestrator.

    Coordinate complete validation for animal-configuration.

    Phase 2 (Backend Testing) - Delegate:
    - Backend comprehensive testing
    - OpenAPI validation
    - Edge case testing
    - DynamoDB verification

    Delegate to backend testing agent:

    Task(
        subagent_type="general-purpose",
        description="Backend testing phase",
        prompt="You are Backend Testing Agent. Test animal-configuration..."
    )

    See .claude/commands/orchestrate-tests.md Phase 2
    """
)
```

---

## Success Metrics

**Coverage Metrics:**
- ✅ 100% of endpoints tested
- ✅ 100% of fields tested
- ✅ ≥25 edge cases per text field
- ✅ ≥10 edge cases per numeric field
- ✅ 100% of enum values tested
- ✅ 100% of DynamoDB persistence verified

**Quality Metrics:**
- ✅ ≥95% test pass rate (excluding known issues)
- ✅ Zero false positives (tests passing when should fail)
- ✅ 100% of "not implemented" errors investigated
- ✅ All OpenAPI gaps documented
- ✅ 100% test cleanup (no artifacts in DynamoDB)

**Reporting Metrics:**
- ✅ Comprehensive test report generated
- ✅ Reproduction steps for 100% of failures
- ✅ Root cause identified for all errors
- ✅ Recommendations prioritized by severity
- ✅ Teams notification sent

**Integration Metrics:**
- ✅ Backend architect received findings
- ✅ Feature documentation updated
- ✅ Frontend testing unblocked (backend working)
- ✅ Test orchestrator received status

---

## Related Documentation

**Essential Reading:**
- `.claude/commands/backend-testing.md` - Agent command
- `ENDPOINT-WORK-ADVICE.md` - OpenAPI generation patterns
- `VALIDATE-DATA-PERSISTENCE-ADVICE.md` - DynamoDB verification

**Related Agents:**
- `frontend-comprehensive-testing.md` - Frontend UI testing
- `orchestrate-tests.md` - Overall test coordination
- `test-generation.md` - Test case generation
- `document-features.md` - Feature documentation
- `teams-report.md` - Test result reporting

**Implementation References:**
- `backend/api/openapi_spec.yaml` - API specification
- `backend/api/src/main/python/openapi_server/impl/` - Backend handlers
- `scripts/send_teams_report.py` - Teams notification script
