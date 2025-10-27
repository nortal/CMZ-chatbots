# Test Generation Agent

**Purpose**: Comprehensive test generation and coverage completion by seasoned QA engineer with Python and Playwright expertise

**Agent Profile**: Quality Assurance Engineer specializing in:
- Python test frameworks (pytest, unittest)
- Playwright E2E testing
- DynamoDB integration testing
- Test coverage analysis and gap identification
- Edge case discovery and validation
- Test result authenticity verification

## ⚠️ CRITICAL REQUIREMENTS

**Test Authenticity Verification:**
- NEVER trust "passing" tests without verifying actual implementation exists
- ALWAYS check code for "not implemented", "do some magic", or stub responses
- VERIFY DynamoDB operations actually read/write data (not just return 200)
- CONFIRM test results represent real functionality, not implementation gaps
- INVESTIGATE any 501/404 responses - could indicate OpenAPI generation issues

**Coverage Completeness:**
- Generate tests for ALL test types: E2E, integration, unit, validation
- Include edge cases: boundary values, null inputs, error conditions
- Verify data persistence: Read from AND write to DynamoDB in tests
- Maintain living test plan and coverage map
- Update coverage map as tests are added/modified

## Delegation Pattern

**Basic Usage:**
```python
Task(
    subagent_type="general-purpose",
    description="Generate comprehensive tests for feature X",
    prompt="""You are a seasoned QA engineer specializing in Python and Playwright testing.

FEATURE TO TEST: {feature_name}

YOUR MISSION:
1. Analyze existing test coverage for this feature
2. Identify gaps in E2E, integration, unit, and validation tests
3. Generate missing tests with edge cases
4. Verify DynamoDB read/write operations in tests
5. Create/update test plan and coverage map
6. CRITICAL: Verify test results are authentic (not false positives)

DELIVERABLES:
- Complete test suite covering all test types
- Test plan document
- Coverage map showing gaps filled
- Verification report confirming tests are real

See .claude/commands/generate-tests.md for complete methodology.
"""
)
```

## Test Generation Methodology

### Phase 1: Discovery and Analysis

#### Step 1: Feature Analysis
```bash
# Identify the feature scope
echo "=== Feature Analysis ==="

# What is the feature?
FEATURE_NAME="Animal Configuration Management"
FEATURE_SCOPE="CRUD operations for animal config, DynamoDB persistence"

# What endpoints are involved?
ENDPOINTS=(
    "GET /animal_config?animalId=X"
    "PATCH /animal_config?animalId=X"
    "POST /animal"
    "PUT /animal/{id}"
    "DELETE /animal/{id}"
)

# What business logic exists?
BUSINESS_LOGIC="
- Animal config validation
- Temperature range validation (0.0-1.0)
- SystemPrompt updates
- DynamoDB persistence to quest-dev-animal table
"

# Document in test plan
cat > test_plan_${FEATURE_NAME// /_}.md << 'EOF'
# Test Plan: ${FEATURE_NAME}

## Feature Scope
${FEATURE_SCOPE}

## Endpoints Under Test
${ENDPOINTS[@]}

## Business Logic
${BUSINESS_LOGIC}

## Test Types Required
- [ ] Unit Tests
- [ ] Integration Tests
- [ ] E2E Tests (Playwright)
- [ ] Validation Tests
- [ ] DynamoDB Persistence Tests
EOF
```

#### Step 2: Existing Test Discovery
```bash
# Find all existing tests for this feature
echo "=== Discovering Existing Tests ==="

# Unit tests
UNIT_TESTS=$(find backend/api/src/main/python/tests/unit -name "*animal*" -o -name "*config*" 2>/dev/null)
echo "Unit Tests Found: $UNIT_TESTS"

# Integration tests
INTEGRATION_TESTS=$(find backend/api/src/main/python/tests/integration -name "*animal*" 2>/dev/null)
echo "Integration Tests Found: $INTEGRATION_TESTS"

# E2E tests
E2E_TESTS=$(find backend/api/src/main/python/tests/playwright -name "*animal*config*" 2>/dev/null)
echo "E2E Tests Found: $E2E_TESTS"

# Validation tests
VALIDATION_TESTS=$(find tests -name "validate-animal*" 2>/dev/null)
echo "Validation Tests Found: $VALIDATION_TESTS"

# Regression tests
REGRESSION_TESTS=$(find backend/api/src/main/python/tests/regression -name "*animal*" 2>/dev/null)
echo "Regression Tests Found: $REGRESSION_TESTS"
```

#### Step 3: Coverage Gap Analysis
```bash
# Analyze what's missing
echo "=== Coverage Gap Analysis ==="

# Create coverage matrix
cat > coverage_matrix.md << 'EOF'
# Test Coverage Matrix: Animal Configuration

## Test Type Coverage

| Test Type | Exists | Count | Coverage | Gaps |
|-----------|--------|-------|----------|------|
| Unit | Yes | 12 | 70% | Missing edge cases, null handling |
| Integration | Yes | 5 | 50% | Missing error scenarios |
| E2E (Playwright) | Yes | 8 | 60% | Missing DynamoDB verification |
| Validation | Yes | 3 | 40% | Missing comprehensive validation |
| Regression | Partial | 2 | 30% | Missing Bug #1, Bug #7 tests |

## Endpoint Coverage

| Endpoint | Unit | Integration | E2E | Validation | DynamoDB Verified |
|----------|------|-------------|-----|------------|-------------------|
| GET /animal_config | ✅ | ✅ | ✅ | ⚠️ Partial | ❌ Not verified |
| PATCH /animal_config | ✅ | ⚠️ Partial | ✅ | ❌ Missing | ❌ Not verified |
| POST /animal | ✅ | ✅ | ❌ Missing | ❌ Missing | ❌ Not verified |
| PUT /animal/{id} | ✅ | ❌ Missing | ❌ Missing | ❌ Missing | ❌ Not verified |
| DELETE /animal/{id} | ⚠️ Partial | ❌ Missing | ❌ Missing | ❌ Missing | ❌ Not verified |

## Edge Cases Coverage

| Edge Case | Covered | Test Location |
|-----------|---------|---------------|
| Null animalId | ❌ | - |
| Invalid temperature (< 0) | ⚠️ Partial | tests/unit/test_animals.py:45 |
| Invalid temperature (> 1) | ⚠️ Partial | tests/unit/test_animals.py:47 |
| Empty systemPrompt | ❌ | - |
| Non-existent animalId | ❌ | - |
| Concurrent updates | ❌ | - |
| DynamoDB connection failure | ❌ | - |
| Malformed JSON | ⚠️ Partial | tests/unit/test_animals.py:52 |

## DynamoDB Operations Coverage

| Operation | Covered | Verified Read | Verified Write |
|-----------|---------|---------------|----------------|
| get_item | ✅ | ❌ | N/A |
| put_item | ✅ | N/A | ❌ |
| update_item | ⚠️ Partial | ❌ | ❌ |
| delete_item | ❌ | ❌ | N/A |
| scan | ✅ | ❌ | N/A |

## Priority Gaps (Must Fix)

1. **CRITICAL**: DynamoDB read/write verification in ALL tests
2. **CRITICAL**: Edge case coverage for null/invalid inputs
3. **HIGH**: Missing E2E tests for POST, PUT, DELETE operations
4. **HIGH**: Missing validation tests for PATCH endpoint
5. **MEDIUM**: Integration tests for error scenarios
6. **MEDIUM**: Regression tests for known bugs
EOF

echo "Coverage gaps documented in coverage_matrix.md"
```

### Phase 2: Test Generation

#### Step 1: Unit Test Generation
```python
# Generate unit tests for missing coverage
cat > backend/api/src/main/python/tests/unit/test_animal_config_edge_cases.py << 'EOF'
"""
Unit tests for Animal Config edge cases and error handling
Generated: 2025-10-12
Feature: Animal Configuration Management
"""
import pytest
from unittest.mock import Mock, patch
from openapi_server.impl.domain.animal_service import AnimalService
from botocore.exceptions import ClientError

class TestAnimalConfigEdgeCases:
    """Edge case testing for animal configuration"""

    @pytest.fixture
    def animal_service(self):
        """Create animal service instance"""
        return AnimalService()

    def test_null_animal_id(self, animal_service):
        """Test handling of null animalId"""
        with pytest.raises(ValueError, match="animalId cannot be null"):
            animal_service.get_config(None)

    def test_empty_animal_id(self, animal_service):
        """Test handling of empty string animalId"""
        with pytest.raises(ValueError, match="animalId cannot be empty"):
            animal_service.get_config("")

    def test_invalid_temperature_negative(self, animal_service):
        """Test temperature validation: negative value"""
        config = {"temperature": -0.5}
        with pytest.raises(ValueError, match="Temperature must be between 0.0 and 1.0"):
            animal_service.update_config("charlie_003", config)

    def test_invalid_temperature_above_one(self, animal_service):
        """Test temperature validation: value > 1.0"""
        config = {"temperature": 1.5}
        with pytest.raises(ValueError, match="Temperature must be between 0.0 and 1.0"):
            animal_service.update_config("charlie_003", config)

    def test_empty_system_prompt(self, animal_service):
        """Test handling of empty systemPrompt"""
        config = {"systemPrompt": ""}
        # Should allow empty but not None
        result = animal_service.update_config("charlie_003", config)
        assert result is not None

    def test_none_system_prompt(self, animal_service):
        """Test handling of None systemPrompt"""
        config = {"systemPrompt": None}
        with pytest.raises(ValueError, match="systemPrompt cannot be None"):
            animal_service.update_config("charlie_003", config)

    def test_non_existent_animal_id(self, animal_service):
        """Test retrieval of non-existent animal"""
        with pytest.raises(KeyError, match="Animal not found"):
            animal_service.get_config("nonexistent_animal_999")

    @patch('boto3.resource')
    def test_dynamodb_connection_failure(self, mock_boto, animal_service):
        """Test handling of DynamoDB connection failure"""
        mock_boto.side_effect = ClientError(
            {'Error': {'Code': 'ServiceUnavailable', 'Message': 'Service unavailable'}},
            'get_item'
        )

        with pytest.raises(ConnectionError, match="DynamoDB unavailable"):
            animal_service.get_config("charlie_003")

    def test_malformed_config_json(self, animal_service):
        """Test handling of malformed configuration"""
        malformed = "{'invalid': json}"  # Not valid JSON
        with pytest.raises(ValueError, match="Invalid JSON"):
            animal_service.update_config("charlie_003", malformed)

    def test_concurrent_update_conflict(self, animal_service):
        """Test handling of concurrent update conflicts"""
        # Simulate version conflict
        with patch('boto3.resource') as mock_dynamodb:
            mock_dynamodb.return_value.Table.return_value.update_item.side_effect = ClientError(
                {'Error': {'Code': 'ConditionalCheckFailedException'}},
                'update_item'
            )

            with pytest.raises(ConflictError, match="Resource was modified"):
                animal_service.update_config("charlie_003", {"temperature": 0.7})

# CRITICAL: DynamoDB Verification Tests
class TestAnimalConfigDynamoDBPersistence:
    """Verify actual DynamoDB read/write operations"""

    @pytest.fixture
    def real_dynamodb_table(self):
        """Get real DynamoDB table (test environment)"""
        import boto3
        dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
        return dynamodb.Table('quest-dev-animal')

    def test_config_persisted_to_dynamodb(self, real_dynamodb_table):
        """CRITICAL: Verify config is actually written to DynamoDB"""
        # Arrange
        animal_id = "test_animal_persistence_001"
        test_config = {
            "temperature": 0.75,
            "systemPrompt": "Test persistence prompt"
        }

        # Act - Update config via API
        from openapi_server.impl.animals import handle_animal_config_patch
        response, status_code = handle_animal_config_patch(animal_id, test_config)

        assert status_code == 200, f"API call failed: {response}"

        # CRITICAL: Verify data in DynamoDB directly
        dynamodb_item = real_dynamodb_table.get_item(Key={'animalId': animal_id})

        assert 'Item' in dynamodb_item, "Animal not found in DynamoDB!"
        assert dynamodb_item['Item']['temperature'] == 0.75, "Temperature not persisted!"
        assert "Test persistence prompt" in dynamodb_item['Item']['systemPrompt'], "SystemPrompt not persisted!"

        # Cleanup
        real_dynamodb_table.delete_item(Key={'animalId': animal_id})

    def test_config_read_from_dynamodb(self, real_dynamodb_table):
        """CRITICAL: Verify config is actually read from DynamoDB"""
        # Arrange - Put data directly in DynamoDB
        animal_id = "test_animal_read_001"
        real_dynamodb_table.put_item(Item={
            'animalId': animal_id,
            'temperature': 0.65,
            'systemPrompt': 'Direct DynamoDB insert'
        })

        # Act - Get config via API
        from openapi_server.impl.animals import handle_animal_config_get
        response, status_code = handle_animal_config_get(animal_id)

        # Assert - Verify API returns DynamoDB data
        assert status_code == 200, f"API call failed: {response}"
        assert response['temperature'] == 0.65, "Did not read from DynamoDB!"
        assert response['systemPrompt'] == 'Direct DynamoDB insert', "Did not read from DynamoDB!"

        # Cleanup
        real_dynamodb_table.delete_item(Key={'animalId': animal_id})
EOF

echo "Unit tests generated: tests/unit/test_animal_config_edge_cases.py"
```

#### Step 2: Integration Test Generation
```python
# Generate integration tests
cat > backend/api/src/main/python/tests/integration/test_animal_config_integration.py << 'EOF'
"""
Integration tests for Animal Config API endpoints
Tests full request/response cycle with DynamoDB
Generated: 2025-10-12
"""
import pytest
import requests
import boto3
from datetime import datetime

BASE_URL = "http://localhost:8080"
DYNAMODB_TABLE = "quest-dev-animal"

@pytest.fixture
def auth_token():
    """Get authentication token"""
    response = requests.post(
        f"{BASE_URL}/auth",
        json={"username": "parent1@test.cmz.org", "password": "testpass123"}
    )
    return response.json()['token']

@pytest.fixture
def dynamodb_table():
    """Get DynamoDB table for verification"""
    dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
    return dynamodb.Table(DYNAMODB_TABLE)

class TestAnimalConfigIntegration:
    """Full integration tests with DynamoDB verification"""

    def test_patch_config_full_cycle(self, auth_token, dynamodb_table):
        """
        CRITICAL: Test complete PATCH flow with DynamoDB verification

        Flow: API Request → Handler → Domain → DynamoDB → Verify
        """
        animal_id = f"integration_test_{datetime.now().timestamp()}"

        # Setup - Create initial animal
        initial_data = {
            "animalId": animal_id,
            "name": "Integration Test Animal",
            "temperature": 0.5
        }
        dynamodb_table.put_item(Item=initial_data)

        # Act - Update via API
        update_data = {"temperature": 0.8, "systemPrompt": "Updated via API"}
        response = requests.patch(
            f"{BASE_URL}/animal_config",
            params={"animalId": animal_id},
            json=update_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        # Assert - API response
        assert response.status_code == 200, f"API failed: {response.text}"

        # CRITICAL: Verify in DynamoDB
        db_item = dynamodb_table.get_item(Key={'animalId': animal_id})
        assert 'Item' in db_item, "Item not found in DynamoDB after update!"
        assert db_item['Item']['temperature'] == 0.8, "Temperature not updated in DynamoDB!"
        assert db_item['Item']['systemPrompt'] == "Updated via API", "SystemPrompt not updated in DynamoDB!"

        # Cleanup
        dynamodb_table.delete_item(Key={'animalId': animal_id})

    def test_error_handling_invalid_animal(self, auth_token):
        """Test error handling for non-existent animal"""
        response = requests.patch(
            f"{BASE_URL}/animal_config",
            params={"animalId": "nonexistent_999"},
            json={"temperature": 0.7},
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 404, "Should return 404 for non-existent animal"
        assert "not found" in response.text.lower()

    def test_validation_error_invalid_temperature(self, auth_token):
        """Test validation error handling"""
        response = requests.patch(
            f"{BASE_URL}/animal_config",
            params={"animalId": "charlie_003"},
            json={"temperature": 1.5},  # Invalid: > 1.0
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 400, "Should return 400 for invalid temperature"
        assert "temperature" in response.text.lower()
        assert "0.0" in response.text and "1.0" in response.text
EOF

echo "Integration tests generated: tests/integration/test_animal_config_integration.py"
```

#### Step 3: E2E Test Generation (Playwright)
```python
# Generate Playwright E2E tests
cat > backend/api/src/main/python/tests/playwright/specs/animal-config-e2e-complete.spec.js << 'EOF'
/**
 * E2E Tests for Animal Configuration Management
 * Tests complete user workflows with DynamoDB verification
 * Generated: 2025-10-12
 */
const { test, expect } = require('@playwright/test');
const AWS = require('aws-sdk');

// Configure AWS
AWS.config.update({ region: 'us-west-2' });
const dynamodb = new AWS.DynamoDB.DocumentClient();
const TABLE_NAME = 'quest-dev-animal';

test.describe('Animal Configuration E2E', () => {
    let page;

    test.beforeEach(async ({ browser }) => {
        page = await browser.newPage();

        // Login
        await page.goto('http://localhost:3001/login');
        await page.fill('input[name="email"]', 'parent1@test.cmz.org');
        await page.fill('input[name="password"]', 'testpass123');
        await page.click('button[type="submit"]');
        await page.waitForURL('**/dashboard');
    });

    test('Complete Animal Config Update with DynamoDB Verification', async () => {
        const testAnimalId = `e2e_test_${Date.now()}`;

        // Setup - Create test animal in DynamoDB
        await dynamodb.put({
            TableName: TABLE_NAME,
            Item: {
                animalId: testAnimalId,
                name: 'E2E Test Animal',
                temperature: 0.5,
                systemPrompt: 'Initial prompt'
            }
        }).promise();

        // Navigate to animal config
        await page.goto('http://localhost:3001/admin/animals');
        await page.click(`[data-animal-id="${testAnimalId}"]`);

        // Open edit dialog
        await page.click('button:has-text("Edit Config")');

        // Update temperature
        await page.fill('input[name="temperature"]', '0.75');

        // Update system prompt
        await page.fill('textarea[name="systemPrompt"]', 'Updated via E2E test');

        // Save
        await page.click('button:has-text("Save")');

        // Wait for success message
        await expect(page.locator('.success-message')).toBeVisible();

        // CRITICAL: Verify data in DynamoDB
        const dbResult = await dynamodb.get({
            TableName: TABLE_NAME,
            Key: { animalId: testAnimalId }
        }).promise();

        expect(dbResult.Item).toBeDefined();
        expect(dbResult.Item.temperature).toBe(0.75);
        expect(dbResult.Item.systemPrompt).toBe('Updated via E2E test');

        // Cleanup
        await dynamodb.delete({
            TableName: TABLE_NAME,
            Key: { animalId: testAnimalId }
        }).promise();
    });

    test('Edge Case: Invalid Temperature Shows Error', async () => {
        await page.goto('http://localhost:3001/admin/animals');
        await page.click('[data-animal-id="charlie_003"]');
        await page.click('button:has-text("Edit Config")');

        // Try invalid temperature
        await page.fill('input[name="temperature"]', '1.5');
        await page.click('button:has-text("Save")');

        // Should show validation error
        await expect(page.locator('.error-message')).toContainText('must be between 0.0 and 1.0');

        // Should NOT update DynamoDB
        const dbResult = await dynamodb.get({
            TableName: TABLE_NAME,
            Key: { animalId: 'charlie_003' }
        }).promise();

        // Temperature should be unchanged
        expect(dbResult.Item.temperature).not.toBe(1.5);
    });
});
EOF

echo "E2E tests generated: tests/playwright/specs/animal-config-e2e-complete.spec.js"
```

### Phase 3: Test Authenticity Verification

#### Step 1: Implementation Verification
```bash
# CRITICAL: Verify tests aren't passing due to missing implementation
echo "=== Verifying Test Authenticity ==="

verify_implementation() {
    local endpoint=$1
    local handler_file=$2

    echo "Checking implementation for: $endpoint"

    # Check for stub responses
    if grep -q "do some magic\|not implemented\|TODO\|pass  # stub" "$handler_file"; then
        echo "⚠️ WARNING: Stub code found in $handler_file"
        echo "Tests may be passing against non-functional code!"
        return 1
    fi

    # Check for actual business logic
    if grep -q "dynamodb\|table\|put_item\|get_item" "$handler_file"; then
        echo "✅ Real implementation found (DynamoDB operations present)"
        return 0
    else
        echo "❌ CRITICAL: No DynamoDB operations found!"
        echo "Implementation may be incomplete!"
        return 1
    fi
}

# Verify each endpoint
verify_implementation "PATCH /animal_config" "backend/api/src/main/python/openapi_server/impl/animals.py"
verify_implementation "GET /animal_config" "backend/api/src/main/python/openapi_server/impl/animals.py"
```

#### Step 2: Test Result Validation
```bash
# Run tests and validate results are real
echo "=== Validating Test Results ==="

validate_test_results() {
    local test_file=$1
    local test_name=$2

    echo "Running: $test_name"

    # Run test
    pytest "$test_file" -v > /tmp/test_output.log 2>&1
    local exit_code=$?

    # Check for suspicious patterns in output
    if grep -q "501\|Not Implemented\|404.*handler" /tmp/test_output.log; then
        echo "⚠️ WARNING: Test may be hitting unimplemented endpoints"
        echo "Output:"
        grep -A 5 "501\|Not Implemented" /tmp/test_output.log
        return 1
    fi

    # Check for DynamoDB operations in test
    if ! grep -q "dynamodb\|Table\|get_item\|put_item" "$test_file"; then
        echo "⚠️ WARNING: Test does not verify DynamoDB operations"
        echo "Cannot confirm data persistence!"
        return 1
    fi

    if [ $exit_code -eq 0 ]; then
        echo "✅ Test passed with verified implementation"
        return 0
    else
        echo "❌ Test failed"
        return 1
    fi
}

# Validate all generated tests
validate_test_results "tests/unit/test_animal_config_edge_cases.py" "Unit Tests"
validate_test_results "tests/integration/test_animal_config_integration.py" "Integration Tests"
```

#### Step 3: Coverage Map Update
```bash
# Update coverage map with verification status
echo "=== Updating Coverage Map ==="

cat >> coverage_matrix.md << 'EOF'

## Test Authenticity Verification

| Test File | DynamoDB Verified | Implementation Checked | False Positive Risk |
|-----------|-------------------|------------------------|---------------------|
| test_animal_config_edge_cases.py | ✅ Yes | ✅ Verified | ✅ Low |
| test_animal_config_integration.py | ✅ Yes | ✅ Verified | ✅ Low |
| animal-config-e2e-complete.spec.js | ✅ Yes | ✅ Verified | ✅ Low |

## Implementation Verification Results

| Endpoint | Handler File | DynamoDB Ops | Stub Code | Status |
|----------|--------------|--------------|-----------|--------|
| PATCH /animal_config | impl/animals.py | ✅ Found | ❌ None | ✅ Real Implementation |
| GET /animal_config | impl/animals.py | ✅ Found | ❌ None | ✅ Real Implementation |
| POST /animal | impl/animals.py | ✅ Found | ❌ None | ✅ Real Implementation |

## Critical Findings

- ✅ All tests verify actual DynamoDB read/write operations
- ✅ No stub code or "do some magic" placeholders found
- ✅ Implementation files contain real business logic
- ✅ Tests are authenticated against real endpoints
- ✅ Low risk of false positives

## Coverage Improvement Summary

Before Test Generation:
- Unit Test Coverage: 70%
- Integration Test Coverage: 50%
- E2E Test Coverage: 60%
- DynamoDB Verification: 0%

After Test Generation:
- Unit Test Coverage: 95%
- Integration Test Coverage: 85%
- E2E Test Coverage: 90%
- DynamoDB Verification: 100%

Improvement: +25% average, 100% DynamoDB verification
EOF

echo "Coverage map updated with verification status"
```

### Phase 4: Test Plan Maintenance

#### Step 1: Create Test Plan Document
```markdown
# Test Plan: Animal Configuration Management
## Generated: 2025-10-12

### Feature Overview
Complete CRUD operations for animal configurations with DynamoDB persistence.

### Test Strategy

**Test Types:**
1. **Unit Tests**: Individual function/method testing
2. **Integration Tests**: API endpoint testing with DynamoDB
3. **E2E Tests**: Full user workflow testing (Playwright)
4. **Validation Tests**: Cross-system validation
5. **Regression Tests**: Known bug prevention

**Quality Gates:**
- All tests must verify DynamoDB read/write
- No "not implemented" responses allowed
- Edge cases must be covered
- 90%+ code coverage target

### Test Execution Order

**Phase 1: Unit Tests** (Fast feedback)
```bash
pytest tests/unit/test_animal_config_edge_cases.py -v
```

**Phase 2: Integration Tests** (API + DB)
```bash
pytest tests/integration/test_animal_config_integration.py -v
```

**Phase 3: E2E Tests** (Full workflow)
```bash
FRONTEND_URL=http://localhost:3001 npx playwright test specs/animal-config-e2e-complete.spec.js
```

**Phase 4: Validation Tests** (System-wide)
```bash
/validate-animal-config-persistence
```

### Test Maintenance

**When to Update Tests:**
- Feature changes
- New edge cases discovered
- Bug fixes (add regression test)
- OpenAPI spec changes
- DynamoDB schema changes

**Test Review Schedule:**
- Weekly: Quick review of failed tests
- Monthly: Full test suite audit
- Per Release: Comprehensive coverage review

### Success Criteria

✅ All test types present for each endpoint
✅ DynamoDB operations verified in every test
✅ No false positives (implementation verified)
✅ Edge cases covered
✅ 90%+ code coverage achieved
✅ Zero "not implemented" responses
```

## Delegation Templates

### Complete Feature Test Generation
```python
Task(
    subagent_type="general-purpose",
    description="Generate comprehensive test suite for Animal Config",
    prompt="""You are a seasoned QA engineer. Generate complete test coverage for Animal Configuration Management.

FEATURE: Animal Configuration Management
ENDPOINTS:
- GET /animal_config?animalId=X
- PATCH /animal_config?animalId=X
- POST /animal
- PUT /animal/{id}
- DELETE /animal/{id}

REQUIREMENTS:
1. Analyze existing test coverage
2. Generate missing tests (unit, integration, E2E, validation)
3. Include edge cases and error scenarios
4. CRITICAL: Verify DynamoDB read/write in ALL tests
5. Create test plan and coverage map
6. Verify test authenticity (no false positives)

DELIVERABLES:
- tests/unit/test_animal_config_edge_cases.py
- tests/integration/test_animal_config_integration.py
- tests/playwright/specs/animal-config-e2e-complete.spec.js
- test_plan_animal_config.md
- coverage_matrix.md

VERIFICATION:
- Check for "not implemented" responses
- Verify actual DynamoDB operations
- Confirm no stub code in handlers
- Validate test results are real

See .claude/commands/generate-tests.md for complete methodology.
"""
)
```

### Targeted Test Generation (Specific Type)
```python
Task(
    subagent_type="general-purpose",
    description="Generate E2E tests with DynamoDB verification",
    prompt="""You are a Playwright expert. Generate E2E tests for Animal Config with DynamoDB verification.

FOCUS: End-to-end user workflows

TESTS NEEDED:
1. Complete config update flow (UI → API → DynamoDB)
2. Edge case: Invalid temperature validation
3. Edge case: Empty system prompt handling
4. Error handling: Non-existent animal

CRITICAL: Each test must:
- Perform action in UI
- Verify API response
- Check DynamoDB directly for persistence
- Clean up test data

Use AWS SDK in tests to verify DynamoDB operations.
"""
)
```

## Quality Standards

**Test Quality Checklist:**
- [ ] Tests run independently (no dependencies)
- [ ] Tests clean up after themselves
- [ ] Tests verify DynamoDB operations directly
- [ ] Tests include edge cases
- [ ] Tests have clear, descriptive names
- [ ] Tests include helpful failure messages
- [ ] No "skip" or "xfail" without justification
- [ ] Implementation verified (no stubs)
- [ ] Test results authenticated

**Coverage Standards:**
- Unit Tests: 90%+ code coverage
- Integration Tests: All API endpoints
- E2E Tests: All user workflows
- Edge Cases: All boundary conditions
- DynamoDB: 100% verification rate

## Success Criteria

1. **Completeness**: All test types present for every feature
2. **Authenticity**: All tests verified against real implementations
3. **Coverage**: 90%+ code coverage achieved
4. **DynamoDB Verification**: 100% of tests verify data persistence
5. **Edge Cases**: All boundary conditions tested
6. **Documentation**: Test plan and coverage map maintained
7. **No False Positives**: Zero tests passing against unimplemented code

## References
- `TEST-GENERATION-ADVICE.md` - Best practices and troubleshooting
- `.claude/commands/validate-*.md` - Validation test examples
- `TEAMS-WEBHOOK-ADVICE.md` - For reporting test results
- `backend/api/src/main/python/tests/` - Existing test patterns
