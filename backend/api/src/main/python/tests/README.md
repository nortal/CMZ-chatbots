# CMZ API Integration Test Framework

This test framework provides comprehensive integration testing for the CMZ API, specifically designed to validate requirements against Jira tickets from the API Validation Epic (PR003946-61).

## Overview

The integration test framework validates:
- **API Validation Epic (PR003946-61)**: 26 tickets covering comprehensive API hardening
- **Authentication & Authorization**: Token validation, role enforcement, password policies
- **Data Integrity**: Soft-delete semantics, foreign key constraints, server-generated IDs
- **Input Validation**: Length limits, format validation, required fields
- **Error Handling**: Consistent error schema across all endpoints
- **Pagination & Filtering**: Query parameter validation, result consistency

## Framework Architecture

### Test Organization
```
tests/
├── conftest.py                    # Test configuration and fixtures
├── integration/
│   ├── test_api_validation_epic.py   # Core validation tests by ticket
│   ├── test_endpoints.py             # Endpoint-specific tests
│   └── __init__.py
├── pytest.ini                    # Pytest configuration
└── README.md                     # This file
```

### Key Components

#### 1. Test Fixtures (conftest.py)
- **DynamoDB Mocking**: Full DynamoDB mock with test tables
- **Flask App**: Configured test client with OpenAPI spec
- **Authentication**: JWT token generation for role testing
- **Test Data**: Sample animals, users, families with proper structure
- **Validation Helpers**: Schema validation, audit field checks, error format validation

#### 2. Test Suites

##### API Validation Epic Tests (`test_api_validation_epic.py`)
- **TestSoftDeleteSemantics**: PR003946-66, 67, 68
- **TestIDValidation**: PR003946-69, 70 (server-generated IDs)
- **TestAuthenticationValidation**: PR003946-71, 72, 87, 88
- **TestDataIntegrityValidation**: PR003946-73, 74, 75
- **TestFamilyManagementValidation**: PR003946-79, 80
- **TestPaginationValidation**: PR003946-81, 82
- **TestAnalyticsValidation**: PR003946-83, 84, 85
- **TestBillingValidation**: PR003946-86
- **TestInputValidation**: PR003946-89, 91
- **TestErrorHandlingValidation**: PR003946-90

##### Endpoint Tests (`test_endpoints.py`)
- **TestAuthenticationEndpoints**: /auth, /auth/refresh, /auth/logout
- **TestUserEndpoints**: /user CRUD operations with validation
- **TestAnimalEndpoints**: /animal_list, /animal_details, /animal_config
- **TestConversationEndpoints**: /convo_turn with input validation
- **TestFamilyEndpoints**: /family CRUD with constraint validation
- **TestAnalyticsEndpoints**: /performance_metrics, /logs, /billing
- **TestSystemEndpoints**: /system_health, /feature_flags

## Installation and Setup

### 1. Install Test Dependencies
```bash
pip install -r requirements-test.txt
```

### 2. Install Main Dependencies  
```bash
pip install -r requirements.txt
```

### 3. Verify Installation
```bash
python -m pytest --version
```

## Running Tests

### Basic Usage

#### Run All Integration Tests
```bash
python run_integration_tests.py
```

#### Run Specific Test Suites
```bash
# API Validation Epic tests only
python run_integration_tests.py --validation

# Endpoint-specific tests only
python run_integration_tests.py --endpoints

# Tests for specific ticket
python run_integration_tests.py --ticket PR003946-90
```

#### Run Tests by Category
```bash
# Authentication tests
python run_integration_tests.py --auth

# Data integrity tests  
python run_integration_tests.py --data-integrity

# Soft delete tests
python run_integration_tests.py --soft-delete
```

### Advanced Usage

#### TDD Mode (Recommended)
```bash
# Watch for file changes and re-run tests
python run_integration_tests.py --tdd
```

#### Coverage Reports
```bash
# Run with coverage reporting
python run_integration_tests.py --coverage

# Generate comprehensive report
python run_integration_tests.py --report
```

#### Parallel Execution
```bash
# Run tests in parallel (4 workers)
python run_integration_tests.py --parallel 4
```

#### CI/CD Integration
```bash
# Generate JUnit XML and HTML reports
python run_integration_tests.py --junit --html-report
```

### Direct Pytest Usage
```bash
# Run all integration tests
pytest tests/integration/ -v

# Run with markers
pytest tests/integration/ -m "auth" -v

# Run specific test class
pytest tests/integration/test_api_validation_epic.py::TestSoftDeleteSemantics -v

# Run specific test method
pytest tests/integration/test_endpoints.py::TestAuthenticationEndpoints::test_auth_post_endpoint_validation -v
```

## Test Markers

Tests are organized with pytest markers for easy filtering:

- `integration`: All integration tests
- `validation`: Jira ticket validation tests
- `auth`: Authentication and authorization tests  
- `data_integrity`: Data integrity and foreign key tests
- `soft_delete`: Soft delete functionality tests
- `pagination`: Pagination and filtering tests
- `error_handling`: Error response format tests
- `slow`: Tests that take longer to run
- `requires_db`: Tests that require DynamoDB
- `requires_auth`: Tests that require authentication

## TDD Workflow

### 1. Red Phase (Write Failing Test)
```bash
# Create test for new requirement
# Example: Add test for new validation rule

def test_new_validation_rule(self, client, validation_helper):
    """Test new validation requirement from ticket XYZ"""
    
    # Test invalid input
    response = client.post('/endpoint', data=invalid_data)
    assert response.status_code == 400
    
    validation_helper.assert_error_schema(response.json())
```

### 2. Green Phase (Make Test Pass)
```bash
# Run specific test
pytest tests/integration/ -k "test_new_validation_rule" -v

# Watch mode for continuous feedback
python run_integration_tests.py --tdd
```

### 3. Refactor Phase
```bash
# Run all tests to ensure no regression
python run_integration_tests.py --coverage
```

## Test Data Management

### Sample Data Creation
```python
# Use fixtures for consistent test data
def test_example(self, client, sample_animal, sample_user, db_helper):
    # Insert test data
    animal = db_helper.insert_test_animal(sample_animal)
    user = db_helper.insert_test_user(sample_user)
    
    # Test endpoint
    response = client.get(f'/animal/{animal["animalId"]}')
    assert response.status_code == 200
```

### Data Factory Usage
```python
def test_validation_example(self, client, data_factory, validation_helper):
    # Generate test data
    auth_request = data_factory.create_auth_request(password="weak")
    
    # Test validation
    response = client.post('/auth', json=auth_request)
    validation_helper.assert_error_schema(response.json())
```

## Validation Helpers

### Error Schema Validation
```python
def test_error_format(self, client, validation_helper):
    response = client.get('/non_existent')
    
    # Validates Error schema compliance (PR003946-90)
    validation_helper.assert_error_schema(
        response.json(), 
        expected_code="not_found"
    )
```

### Audit Field Validation
```python
def test_audit_fields(self, client, validation_helper):
    response = client.get('/user/123')
    
    # Validates created, modified, softDelete fields
    validation_helper.assert_audit_fields(response.json())
```

### Server ID Validation
```python
def test_server_ids(self, client, validation_helper):
    response = client.post('/animal', json=animal_data)
    
    # Validates server-generated ID (PR003946-69)
    validation_helper.assert_server_generated_id(
        response.json(), 
        'animalId'
    )
```

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Integration Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    - name: Run integration tests
      run: |
        python run_integration_tests.py --junit --html-report --coverage
    - name: Upload test results
      uses: actions/upload-artifact@v3
      with:
        name: test-reports
        path: reports/
```

### Docker Integration
```dockerfile
# Add to existing Dockerfile
RUN pip install -r requirements-test.txt
RUN python run_integration_tests.py --report
```

## Extending the Framework

### Adding New Test Suites
1. Create test file in `tests/integration/`
2. Use fixtures from `conftest.py`
3. Add appropriate markers
4. Update this README

### Adding New Fixtures
1. Add fixture to `conftest.py`
2. Document usage in docstring
3. Add to relevant test files

### Adding New Validation Helpers
1. Add method to `ValidationHelper` class in `conftest.py`
2. Document expected behavior
3. Use in test cases

## Troubleshooting

### Common Issues

#### DynamoDB Connection Errors
```bash
# Ensure moto is installed
pip install moto[dynamodb]
```

#### Import Errors
```bash
# Ensure Python path includes project root
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

#### Fixture Not Found
```bash
# Check fixture is defined in conftest.py
pytest --fixtures tests/integration/
```

### Debug Mode
```bash
# Run with verbose debugging
pytest tests/integration/ -vvv --tb=long

# Run single test with debugging
pytest tests/integration/test_endpoints.py::TestAuthEndpoints::test_auth_validation -vvv --pdb
```

## Best Practices

### Test Naming
- Use descriptive names that include ticket numbers
- Follow pattern: `test_pr003946_XX_requirement_description`

### Test Structure  
- **Arrange**: Set up test data using fixtures
- **Act**: Make API call
- **Assert**: Validate response using helpers

### Error Handling
- Always test both success and failure cases
- Validate error response format
- Check appropriate HTTP status codes

### Documentation
- Document expected vs actual behavior
- Note when features are not yet implemented
- Update tests when requirements change

## Jira Ticket Mapping

| Ticket | Test Class | Description |
|--------|------------|-------------|
| PR003946-66 | TestSoftDeleteSemantics | Soft-delete flag consistency |
| PR003946-69 | TestIDValidation | Server-generated IDs |
| PR003946-71 | TestAuthenticationValidation | JWT token validation |
| PR003946-79 | TestFamilyManagementValidation | Family membership constraints |
| PR003946-86 | TestBillingValidation | Billing period format validation |
| PR003946-87 | TestAuthenticationValidation | Password policy enforcement |
| PR003946-90 | TestErrorHandlingValidation | Consistent error schema |
| PR003946-91 | TestInputValidation | Conversation turn input limits |

For complete mapping, see test files with ticket references in test method names.