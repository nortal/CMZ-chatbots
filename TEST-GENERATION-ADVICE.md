# TEST-GENERATION-ADVICE.md

## Overview
Best practices, troubleshooting guide, and lessons learned for using the test generation agent to create comprehensive, authentic test coverage.

## Critical Directive

**🚨 ALWAYS VERIFY TEST AUTHENTICITY**

Tests can pass for the wrong reasons:
- **OpenAPI Generation Issues**: Handler routing broken, calls wrong implementation
- **Stub Code**: "do some magic!" placeholders return 200 without doing anything
- **Mocking Gone Wrong**: Tests mock everything, never touch real code
- **False Success**: Returns 200 but doesn't persist to DynamoDB

**Before trusting any test result:**
1. Check implementation for stub code
2. Verify DynamoDB operations actually execute
3. Confirm data persists between operations
4. Test against real endpoints, not mocks (for integration/E2E)

## Test Generation Workflow

### Phase 1: Discovery (Always Start Here)

**1. Feature Analysis**
```bash
# Define scope clearly
FEATURE="Animal Configuration Management"
ENDPOINTS="GET/PATCH /animal_config, POST/PUT/DELETE /animal"
BUSINESS_LOGIC="Config validation, DynamoDB persistence, temperature range 0-1"
```

**2. Existing Test Discovery**
```bash
# Find ALL existing tests
find . -name "*test*animal*" -o -name "*animal*test*"
find . -name "*config*test*" -o -name "*test*config*"
```

**3. Coverage Gap Analysis**
Create coverage matrix showing:
- Which test types exist (unit, integration, E2E, validation)
- Which endpoints are covered
- Which edge cases are missing
- **CRITICAL**: Which tests verify DynamoDB operations

### Phase 2: Generation Priorities

**Priority 1: DynamoDB Verification Tests**
If existing tests don't verify DynamoDB, this is TOP priority.

```python
def test_data_actually_persists():
    """CRITICAL: Verify data goes to DynamoDB"""
    # Act - Update via API
    response = api_client.patch('/animal_config?animalId=X', data)

    # Assert - Check DynamoDB directly
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('quest-dev-animal')
    item = table.get_item(Key={'animalId': 'X'})

    assert item['Item']['temperature'] == data['temperature']
```

**Priority 2: Edge Cases**
Most bugs live at boundaries:
- Null inputs
- Empty strings
- Values at limits (0.0, 1.0 for temperature)
- Non-existent resources
- Malformed data

**Priority 3: Error Scenarios**
- Database connection failures
- Concurrent update conflicts
- Authentication failures
- Validation errors

**Priority 4: Happy Path Tests**
Only after edge cases and errors are covered.

### Phase 3: Implementation Verification

**Check for Stub Code**
```bash
# Search for stub indicators
grep -r "do some magic\|not implemented\|TODO.*implement\|pass  # stub" \
  backend/api/src/main/python/openapi_server/

# Check specific handler
grep -A 10 "def handle_animal_config_patch" impl/animals.py
```

**Verify DynamoDB Operations**
```bash
# Handler must contain DynamoDB operations
grep -c "dynamodb\|table\|put_item\|get_item\|update_item" impl/animals.py

# Should be > 0, otherwise implementation is incomplete
```

**Check Controller Routing**
```bash
# Verify controller calls handler
grep -A 5 "def animal_config.*patch" controllers/animal_controller.py

# Should call impl.animals.handle_animal_config_patch, not generic handler
```

### Phase 4: Test Execution & Validation

**Run Tests with Verification**
```bash
# Run test
pytest tests/unit/test_animals.py::test_config_update -v

# If test passes, verify:
# 1. Check test output for "not implemented" or 501 errors
# 2. Confirm test actually called DynamoDB (check logs/mocks)
# 3. Run same test against broken implementation - should fail

# If test passes with broken implementation, it's a false positive!
```

## Common Anti-Patterns

### Anti-Pattern 1: Mock Everything
```python
# ❌ BAD: Mocks hide real issues
@patch('boto3.resource')
@patch('impl.animals.validate_config')
@patch('impl.animals.update_dynamodb')
def test_update_config(mock_db, mock_validate, mock_boto):
    # Test passes but doesn't touch real code!
    pass
```

```python
# ✅ GOOD: Test real integration
def test_update_config_integration():
    """Test with real DynamoDB (test environment)"""
    # Uses actual AWS, verifies real behavior
    dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
    table = dynamodb.Table('quest-dev-animal')

    # Real API call
    response = requests.patch(...)

    # Real DynamoDB verification
    item = table.get_item(Key={'animalId': test_id})
    assert item['Item']['temperature'] == expected_value
```

### Anti-Pattern 2: Testing HTTP Status Only
```python
# ❌ BAD: Status code doesn't prove data persisted
def test_update_config():
    response = client.patch('/animal_config', data)
    assert response.status_code == 200
    # What if handler just returns 200 without saving?
```

```python
# ✅ GOOD: Verify data persistence
def test_update_config_persists():
    response = client.patch('/animal_config', data)
    assert response.status_code == 200

    # CRITICAL: Check DynamoDB
    db_item = dynamodb_table.get_item(Key={'animalId': test_id})
    assert db_item['Item']['temperature'] == data['temperature']
```

### Anti-Pattern 3: Trusting "Not Implemented" as "Working"
```python
# ❌ BAD: 501 might mean handler is broken
def test_delete_animal():
    response = client.delete('/animal/123')
    # Test passes if it gets 501!
    # But 501 means "not implemented"
```

```python
# ✅ GOOD: Verify implementation exists first
def test_delete_animal():
    # First, check implementation exists
    from impl.animals import handle_animal_delete
    assert callable(handle_animal_delete), "Handler not implemented!"

    # Then test behavior
    response = client.delete('/animal/123')
    assert response.status_code == 200, "Delete should succeed"

    # Verify deletion
    db_item = dynamodb_table.get_item(Key={'animalId': '123'})
    assert 'Item' not in db_item, "Animal should be deleted from DynamoDB"
```

## Test Type Best Practices

### Unit Tests
**Purpose**: Test individual functions in isolation

**Best Practices:**
- Test one function/method per test
- Mock external dependencies (DB, APIs) but not internal logic
- Cover edge cases exhaustively
- Include error condition testing

**Example Structure:**
```python
class TestAnimalValidation:
    """Test validation logic only"""

    def test_valid_temperature(self):
        assert validate_temperature(0.5) == True

    def test_temperature_below_zero(self):
        with pytest.raises(ValueError):
            validate_temperature(-0.1)

    def test_temperature_above_one(self):
        with pytest.raises(ValueError):
            validate_temperature(1.1)

    def test_temperature_at_boundaries(self):
        assert validate_temperature(0.0) == True
        assert validate_temperature(1.0) == True
```

### Integration Tests
**Purpose**: Test API endpoints with real database

**Best Practices:**
- Use real AWS DynamoDB (test environment)
- Test complete request/response cycle
- Verify data persistence
- Clean up test data after each test

**Example Structure:**
```python
class TestAnimalConfigAPI:
    """Test API with real DynamoDB"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self, dynamodb_table):
        """Setup and cleanup for each test"""
        # Setup
        test_id = f"test_{uuid.uuid4()}"
        yield test_id
        # Cleanup
        dynamodb_table.delete_item(Key={'animalId': test_id})

    def test_patch_endpoint_persists(self, dynamodb_table, setup_teardown):
        test_id = setup_teardown

        # Act - Call API
        response = api_client.patch(f'/animal_config?animalId={test_id}', ...)

        # Assert - Check DynamoDB
        item = dynamodb_table.get_item(Key={'animalId': test_id})
        assert item['Item']['temperature'] == expected_value
```

### E2E Tests (Playwright)
**Purpose**: Test complete user workflows

**Best Practices:**
- Test from user perspective
- Include UI interactions
- Verify backend persistence
- Use AWS SDK to check DynamoDB in tests

**Example Structure:**
```javascript
test('User updates animal config', async ({ page }) => {
    const testId = `e2e_${Date.now()}`;

    // Setup - Create test data
    await dynamodb.put({
        TableName: 'quest-dev-animal',
        Item: { animalId: testId, temperature: 0.5 }
    }).promise();

    // Act - User workflow
    await page.goto('/admin/animals');
    await page.click(`[data-animal-id="${testId}"]`);
    await page.fill('input[name="temperature"]', '0.8');
    await page.click('button:has-text("Save")');

    // Assert - UI feedback
    await expect(page.locator('.success')).toBeVisible();

    // Assert - DynamoDB persistence
    const result = await dynamodb.get({
        TableName: 'quest-dev-animal',
        Key: { animalId: testId }
    }).promise();

    expect(result.Item.temperature).toBe(0.8);

    // Cleanup
    await dynamodb.delete({
        TableName: 'quest-dev-animal',
        Key: { animalId: testId }
    }).promise();
});
```

## Troubleshooting

### Issue: Test Passes But Feature Doesn't Work

**Symptoms:**
- Test shows green checkmark
- Manual testing shows feature broken
- API returns 200 but data not saved

**Root Causes:**
1. **Excessive Mocking**: Test mocks the actual functionality
2. **No DB Verification**: Test checks status code only
3. **Stub Implementation**: Handler returns 200 without doing work
4. **Wrong Environment**: Test uses mock DB, not real AWS

**Solution:**
```bash
# 1. Check what test actually tests
cat tests/integration/test_animals.py | grep -A 20 "def test_update"

# 2. Look for excessive mocking
grep -c "@patch\|@mock" tests/integration/test_animals.py
# Should be minimal for integration tests

# 3. Check for DynamoDB verification
grep -c "dynamodb.*get_item\|Table.*get_item" tests/integration/test_animals.py
# Should be > 0

# 4. Check implementation
grep -A 10 "def handle_animal_config_patch" impl/animals.py
# Should have real DynamoDB operations, not "pass" or "TODO"
```

### Issue: "Not Implemented" Response in Tests

**Symptoms:**
- Test gets 501 "Not Implemented"
- Or 404 response
- Handler appears to exist in code

**Root Causes:**
1. **OpenAPI Generation Issue**: Controller doesn't route to handler
2. **Import Error**: Handler not imported in controller
3. **Function Name Mismatch**: Controller expects different function name

**Solution:**
```bash
# 1. Check controller routing
grep -A 10 "animal_config.*patch" controllers/animal_controller.py

# Should show: impl.animals.handle_animal_config_patch
# NOT: controllers.animal_controller.handle_ (generic stub)

# 2. Verify import
grep "from.*impl.*animals import" controllers/animal_controller.py

# 3. If missing, run post-generation fix
make post-generate

# 4. Re-run tests after fix
pytest tests/integration/test_animals.py -v
```

### Issue: Tests Pass Locally But Fail in CI

**Symptoms:**
- Local tests pass
- CI tests fail with AWS errors
- DynamoDB connection failures

**Root Causes:**
1. **Missing AWS Credentials**: CI doesn't have AWS access
2. **Wrong Region**: CI configured for different region
3. **Table Doesn't Exist**: Test table not created in CI environment

**Solution:**
```yaml
# CI Configuration (GitHub Actions example)
- name: Configure AWS
  env:
    AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
    AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
    AWS_REGION: us-west-2
  run: |
    # Verify AWS access
    aws sts get-caller-identity

    # Check table exists
    aws dynamodb describe-table --table-name quest-dev-animal

- name: Run Integration Tests
  run: pytest tests/integration -v
```

## Coverage Map Maintenance

**Update Coverage Map After:**
- Generating new tests
- Discovering edge cases
- Finding bugs (add regression test)
- OpenAPI spec changes
- Feature additions

**Coverage Map Template:**
```markdown
# Test Coverage Matrix: {Feature Name}

## Current Coverage: {Date}

| Test Type | Count | Coverage % | DynamoDB Verified |
|-----------|-------|------------|-------------------|
| Unit | 25 | 92% | N/A |
| Integration | 12 | 85% | ✅ 100% |
| E2E | 8 | 75% | ✅ 100% |
| Validation | 3 | 60% | ✅ 100% |

## Gaps Remaining
- [ ] Unit: Error handling for concurrent updates
- [ ] Integration: Timeout scenarios
- [ ] E2E: Mobile browser testing

## Test Authenticity
- ✅ All tests verified against real implementations
- ✅ No stub code found in handlers
- ✅ DynamoDB operations confirmed in all integration/E2E tests
- ✅ Zero false positives detected
```

## Success Metrics

**Test Quality KPIs:**
- **Code Coverage**: ≥ 90% for unit tests
- **Endpoint Coverage**: 100% of documented endpoints
- **DynamoDB Verification**: 100% of integration/E2E tests
- **False Positive Rate**: < 1%
- **Edge Case Coverage**: All identified boundary conditions

**Test Maintenance KPIs:**
- **Test Execution Time**: < 5 minutes for unit, < 15 minutes for full suite
- **Test Flakiness**: < 2% failure rate on re-run
- **Coverage Map Currency**: Updated within 24 hours of changes
- **Documentation**: Test plan current with features

## References
- `.claude/commands/generate-tests.md` - Test generation agent command
- `.claude/commands/validate-*.md` - Validation test examples
- `backend/api/src/main/python/tests/` - Existing test patterns
- `pytest.ini` - Test configuration
- `playwright.config.js` - E2E test configuration
