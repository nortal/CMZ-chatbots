# CMZ API Testing Documentation

## Overview

The Cougar Mountain Zoo (CMZ) API uses a comprehensive integration test framework designed for Test-Driven Development (TDD) against Jira ticket requirements. This framework validates the API implementation against the comprehensive API Validation Epic and ensures all business requirements are properly implemented.

## Project Architecture

### API Structure
```
backend/api/
├── openapi_spec.yaml              # OpenAPI 3.0 specification (source of truth)
├── src/main/python/
│   ├── openapi_server/
│   │   ├── impl/                  # Business logic implementation
│   │   ├── controllers/           # Generated API controllers
│   │   ├── models/                # Generated data models
│   │   └── test/                  # Generated test stubs
│   ├── tests/                     # Integration test framework
│   │   ├── conftest.py           # Test configuration and fixtures
│   │   ├── integration/
│   │   │   ├── test_api_validation_epic.py  # Jira ticket validation tests
│   │   │   └── test_endpoints.py            # Endpoint-specific tests
│   │   └── README.md             # Test framework documentation
│   ├── requirements.txt          # Production dependencies
│   ├── requirements-test.txt     # Test dependencies
│   ├── pytest.ini               # Test configuration
│   └── run_integration_tests.py # Test runner script
├── Dockerfile                    # Container definition
└── tox.ini                      # Test configuration
```

## Test Framework Architecture

### 1. Integration Test Framework

The integration test framework is specifically designed to validate API implementation against Jira ticket requirements from the **API Validation Epic (PR003946-61)**.

#### Core Components:

- **Test Configuration (`conftest.py`)**: Provides fixtures for DynamoDB mocking, authentication, sample data, and validation helpers
- **API Validation Tests (`test_api_validation_epic.py`)**: Direct mapping to 26 Jira tickets (PR003946-66 through PR003946-91)
- **Endpoint Tests (`test_endpoints.py`)**: Comprehensive endpoint testing by functional area
- **Test Runner (`run_integration_tests.py`)**: TDD-enabled test execution with file watching

### 2. Jira Ticket Mapping

The test framework maps directly to Jira tickets from the API Validation Epic:

| Ticket Range | Test Class | Validation Focus |
|-------------|------------|------------------|
| PR003946-66-68 | TestSoftDeleteSemantics | Soft-delete enforcement across entities |
| PR003946-69-70 | TestIDValidation | Server-generated IDs, reject client IDs |
| PR003946-71-72, 87-88 | TestAuthenticationValidation | JWT tokens, roles, password policy |
| PR003946-73-75 | TestDataIntegrityValidation | Foreign keys, data consistency |
| PR003946-79-80 | TestFamilyManagementValidation | Family membership constraints |
| PR003946-81-82 | TestPaginationValidation | Pagination and filtering |
| PR003946-83-85 | TestAnalyticsValidation | Time windows, log levels, metrics |
| PR003946-86 | TestBillingValidation | Period format validation |
| PR003946-89, 91 | TestInputValidation | Media upload, message length limits |
| PR003946-90 | TestErrorHandlingValidation | Consistent Error schema |

### 3. TDD Workflow Integration

The framework supports a complete TDD workflow:

1. **Red Phase**: Write failing tests for Jira requirements
2. **Green Phase**: Implement minimal code to pass tests
3. **Refactor Phase**: Improve implementation while maintaining test coverage

## Getting Started

### Prerequisites

- Python 3.9+
- Docker (for containerized development)
- AWS CLI configured for DynamoDB access

### Installation

1. **Install Production Dependencies**
   ```bash
   cd backend/api/src/main/python
   pip install -r requirements.txt
   ```

2. **Install Test Dependencies**
   ```bash
   pip install -r requirements-test.txt
   ```

3. **Verify Installation**
   ```bash
   python -m pytest --version
   python run_integration_tests.py --help
   ```

## Development Workflow

### 1. Standard Development Cycle

```bash
# Regenerate API from OpenAPI spec
make generate-api

# Build and run API server
make build-api && make run-api

# In another terminal, run tests
python run_integration_tests.py --tdd
```

### 2. TDD Workflow for New Features

#### Step 1: Write Failing Test (Red Phase)
```bash
# Example: Implementing password policy validation (PR003946-87)

# Add test to test_api_validation_epic.py
def test_pr003946_87_password_policy_enforcement(self, client, validation_helper, data_factory):
    """PR003946-87: Password policy enforcement with configurable rules"""
    
    # Test weak password
    auth_data = data_factory.create_auth_request(password="123")  # Too short
    
    response = client.post('/auth', json=auth_data)
    assert response.status_code == 400
    
    data = response.json()
    validation_helper.assert_error_schema(data, "invalid_password")
    assert "password" in data.get("details", {}), "Should provide password policy guidance"

# Run specific test
python run_integration_tests.py --ticket PR003946-87
```

#### Step 2: Implement Feature (Green Phase)
```python
# Update impl/auth.py or similar to implement password validation
def validate_password(password: str) -> bool:
    """Validate password meets policy requirements"""
    if len(password) < 6:
        return False
    # Add additional validation rules
    return True
```

#### Step 3: Refactor and Verify (Refactor Phase)
```bash
# Run all tests to ensure no regression
python run_integration_tests.py --coverage

# Generate comprehensive report
python run_integration_tests.py --report
```

### 3. Testing Specific Requirements

#### Test by Jira Ticket
```bash
# Test specific ticket requirements
python run_integration_tests.py --ticket PR003946-90

# Test authentication requirements  
python run_integration_tests.py --auth

# Test soft delete requirements
python run_integration_tests.py --soft-delete
```

#### Test by Functional Area
```bash
# Test all endpoint validations
python run_integration_tests.py --endpoints

# Test API validation epic
python run_integration_tests.py --validation

# Test data integrity
python run_integration_tests.py --data-integrity
```

## Test Categories and Markers

Tests are organized with pytest markers for easy filtering:

### Core Markers
- `integration`: All integration tests
- `validation`: Jira ticket validation tests
- `auth`: Authentication and authorization tests
- `data_integrity`: Data integrity and foreign key tests
- `soft_delete`: Soft delete functionality tests
- `pagination`: Pagination and filtering tests
- `error_handling`: Error response format tests

### Usage Examples
```bash
# Run only authentication tests
pytest tests/integration/ -m "auth" -v

# Run data integrity tests
pytest tests/integration/ -m "data_integrity" -v

# Run tests that require database
pytest tests/integration/ -m "requires_db" -v

# Run all except slow tests
pytest tests/integration/ -m "not slow" -v
```

## Testing Best Practices

### 1. Test Structure
Follow the **Arrange-Act-Assert** pattern:

```python
def test_user_creation_validation(self, client, validation_helper, data_factory):
    # Arrange: Set up test data
    user_data = data_factory.create_user_request(email="invalid-email")
    
    # Act: Make API call
    response = client.post('/user', json=user_data)
    
    # Assert: Validate response
    assert response.status_code == 400
    validation_helper.assert_error_schema(response.json(), "invalid_email")
```

### 2. Use Fixtures for Consistency
```python
def test_animal_details(self, client, db_helper, sample_animal, validation_helper):
    # Use fixtures for consistent test data
    animal = db_helper.insert_test_animal(sample_animal)
    
    response = client.get(f'/animal_details?animalId={animal["animalId"]}')
    
    if response.status_code == 200:
        validation_helper.assert_audit_fields(response.json())
```

### 3. Document Expected vs Current Behavior
```python
def test_pr003946_69_server_generated_ids(self, client, validation_helper):
    """PR003946-69: Server generates all entity IDs, rejects client-provided IDs"""
    
    response = client.post('/animal', json=animal_data)
    
    if response.status_code == 201:
        # Feature implemented correctly
        validation_helper.assert_server_generated_id(response.json(), 'animalId')
    else:
        # Document current behavior - implementation needed
        assert response.status_code in [404, 501]
```

## Continuous Integration

### GitHub Actions Integration
```yaml
name: CMZ API Tests

on: [push, pull_request]

jobs:
  integration-tests:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        cd backend/api/src/main/python
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    
    - name: Run integration tests
      run: |
        cd backend/api/src/main/python
        python run_integration_tests.py --junit --html-report --coverage
    
    - name: Upload test reports
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: test-reports
        path: backend/api/src/main/python/reports/
```

### Docker Integration
```dockerfile
# Add to existing Dockerfile for test stage
FROM python:3.9 AS test

WORKDIR /app
COPY backend/api/src/main/python/ .

RUN pip install -r requirements.txt -r requirements-test.txt

# Run tests during build
RUN python run_integration_tests.py --report

# Copy test reports to final stage if needed
FROM python:3.9
COPY --from=test /app/reports/ /app/reports/
```

## API Development Commands

### Core Development Cycle
```bash
# Complete regeneration and deployment cycle
make generate-api && make build-api && make run-api

# Monitor running container
make logs-api

# Run tests against running API
python run_integration_tests.py --coverage

# Stop and cleanup
make stop-api && make clean-api
```

### Testing During Development
```bash
# TDD mode - watch for changes and re-run tests
python run_integration_tests.py --tdd

# Test specific implementation areas
python run_integration_tests.py --auth --verbose

# Generate reports for documentation
python run_integration_tests.py --report
```

## Validation Framework

### Error Schema Validation
All tests validate that error responses follow the consistent Error schema (PR003946-90):

```python
def validate_error_response(response):
    """Validate error follows required schema"""
    data = response.json()
    
    # Required fields
    assert "code" in data
    assert "message" in data
    assert isinstance(data["code"], str)
    assert isinstance(data["message"], str)
    
    # Optional field-level details
    if "details" in data:
        assert isinstance(data["details"], dict)
```

### Audit Field Validation
All entities must have proper audit fields:

```python
def validate_audit_fields(entity_data):
    """Validate entity has required audit fields"""
    assert "created" in entity_data
    assert "modified" in entity_data
    assert "softDelete" in entity_data
    
    for audit_field in ["created", "modified"]:
        if entity_data[audit_field]:
            assert "at" in entity_data[audit_field]
            assert "by" in entity_data[audit_field]
```

## Troubleshooting

### Common Issues

1. **DynamoDB Connection Errors**
   ```bash
   # Ensure moto is installed correctly
   pip install --upgrade 'moto[dynamodb]'
   ```

2. **Import Errors**
   ```bash
   # Add project root to Python path
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   ```

3. **Test Discovery Issues**
   ```bash
   # Verify test discovery
   pytest --collect-only tests/integration/
   ```

4. **API Server Not Running**
   ```bash
   # Start API server in separate terminal
   make run-api
   
   # Or run tests against mock (default behavior)
   python run_integration_tests.py
   ```

### Debug Mode
```bash
# Run with verbose debugging
pytest tests/integration/ -vvv --tb=long

# Run single test with debugger
pytest tests/integration/test_endpoints.py::TestAuthEndpoints::test_auth_validation -vvv --pdb

# Show all fixtures
pytest --fixtures tests/integration/
```

## Current Implementation Status

Based on analysis of Jira tickets vs current implementation:

### ✅ **Implemented**
- Basic OpenAPI specification
- Generated controllers and models
- Basic CRUD operations structure
- Docker containerization
- DynamoDB integration patterns

### ⚠️ **Partially Implemented**
- Error schema structure (exists but not consistently used)
- Audit fields (schema exists but no enforcement)
- Authentication endpoints (basic structure, no validation)

### ❌ **Missing Implementation**
- Comprehensive input validation (26 validation tickets)
- Role-based access control enforcement
- Soft-delete semantics enforcement
- Server-generated ID validation
- Password policy enforcement
- Foreign key constraint validation
- Pagination parameter validation

### 🎯 **Test-Driven Implementation Priority**
1. **Error Schema Consistency** (PR003946-90) - Affects all endpoints
2. **Authentication Framework** (PR003946-71, 72, 87, 88) - Security foundation
3. **Input Validation Framework** - Required for 20+ tickets
4. **Soft-Delete Enforcement** (PR003946-66-68) - Data integrity
5. **Server ID Generation** (PR003946-69-70) - Data consistency

## Contributing

### Adding New Tests
1. Create test file in appropriate directory
2. Use existing fixtures from `conftest.py`
3. Add appropriate pytest markers
4. Map test to specific Jira ticket when applicable
5. Document expected vs current behavior

### Extending Test Framework
1. Add new fixtures to `conftest.py` for reusable test components
2. Extend validation helpers for new validation patterns
3. Update test runner script for new execution modes
4. Update documentation with new capabilities

### Code Review Checklist
- [ ] Tests map to specific Jira requirements
- [ ] Both success and failure cases tested
- [ ] Error responses validated against schema
- [ ] Audit fields validated where applicable
- [ ] Test data uses fixtures consistently
- [ ] Documentation updated for new features

---

This testing framework provides a comprehensive foundation for implementing the CMZ API requirements using Test-Driven Development, ensuring all Jira ticket requirements are properly validated and implemented.