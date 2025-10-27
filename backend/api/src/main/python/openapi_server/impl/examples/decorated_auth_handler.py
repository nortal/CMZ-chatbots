"""
Example: Authentication Handler with Contract Validation Decorators

This module demonstrates how to apply validation decorators to enforce
OpenAPI contract alignment at runtime, preventing contract drift.

IMPORTANT: This is a reference implementation showing best practices.
Apply similar patterns to production handlers in impl/handlers.py.
"""

from typing import Any, Tuple, Dict
from ..utils.validation import (
    validate_request,
    validate_types,
    validate_required_fields_decorator,
    validate_response_schema
)
from openapi_server.models.error import Error


# Example 1: Basic Request Validation
@validate_request('post', '/auth')
def handle_login_with_validation(body: Dict[str, Any]) -> Tuple[Any, int]:
    """
    Login handler with automatic OpenAPI schema validation

    The @validate_request decorator:
    - Validates body against /auth POST requestBody schema
    - Returns 400 with detailed error if validation fails
    - Only calls handler if request matches OpenAPI spec
    """
    from ..auth_mock import authenticate_user

    # Extract credentials
    email = body.get('username') or body.get('email', '')
    password = body.get('password', '')

    # Authenticate
    result = authenticate_user(email, password)

    if result is None:
        error = Error(
            code="invalid_credentials",
            message="Invalid email or password",
            details={"error": "Authentication failed"}
        )
        return error.to_dict(), 401

    # Return successful auth response
    response_dict = {
        'token': result['token'],
        'user': result['user'],
        'expiresIn': 86400  # 24 hours
    }
    return response_dict, 200


# Example 2: Combined Validation (Request + Required Fields)
@validate_request('post', '/auth')
@validate_required_fields_decorator('username', 'password')
def handle_login_with_field_validation(body: Dict[str, Any]) -> Tuple[Any, int]:
    """
    Login handler with request schema AND required field validation

    Decorators applied (bottom-to-top execution):
    1. @validate_required_fields_decorator - Checks username/password present
    2. @validate_request - Validates against OpenAPI schema

    Validation order: required fields → schema → handler logic
    """
    from ..auth_mock import authenticate_user

    email = body['username']  # Safe to access - validated by decorator
    password = body['password']  # Safe to access - validated by decorator

    result = authenticate_user(email, password)

    if result is None:
        error = Error(
            code="invalid_credentials",
            message="Invalid email or password",
            details={"error": "Authentication failed"}
        )
        return error.to_dict(), 401

    return {
        'token': result['token'],
        'user': result['user'],
        'expiresIn': 86400
    }, 200


# Example 3: Full Validation Stack (Request + Response + Types)
@validate_request('post', '/auth')
@validate_types(body=dict)
@validate_response_schema('post', '/auth')
def handle_login_full_validation(body: Dict[str, Any]) -> Tuple[Any, int]:
    """
    Login handler with complete validation stack

    Decorators applied (bottom-to-top execution):
    1. @validate_response_schema - Logs if response doesn't match OpenAPI
    2. @validate_types - Ensures body parameter is dict type
    3. @validate_request - Validates request against OpenAPI schema

    This is the RECOMMENDED pattern for critical endpoints.
    """
    from ..auth_mock import authenticate_user

    email = body.get('username') or body.get('email', '')
    password = body.get('password', '')

    result = authenticate_user(email, password)

    if result is None:
        error = Error(
            code="invalid_credentials",
            message="Invalid email or password",
            details={"error": "Authentication failed"}
        )
        return error.to_dict(), 401

    # Response will be validated against OpenAPI schema before returning
    return {
        'token': result['token'],
        'user': result['user'],
        'expiresIn': 86400
    }, 200


# Example 4: Type Validation for ID Parameters
@validate_types(animal_id=str, body=dict)
@validate_request('put', '/animal/{id}')
def handle_animal_update_with_validation(animal_id: str, body: Dict[str, Any]) -> Tuple[Any, int]:
    """
    Animal update handler with type and request validation

    Demonstrates:
    - Type checking for path parameters (animal_id must be str)
    - Type checking for body parameter (must be dict)
    - Request body validation against OpenAPI schema
    """
    # animal_id guaranteed to be string
    # body guaranteed to be dict and match AnimalUpdate schema

    from ..animals import update_animal
    result = update_animal(animal_id, body)
    return result, 200


# Example 5: Simple Required Fields Check
@validate_required_fields_decorator('email')
def handle_password_reset(body: Dict[str, Any]) -> Tuple[Any, int]:
    """
    Password reset handler with required field validation

    Use @validate_required_fields_decorator when you need quick
    field presence checks without full schema validation.
    """
    email = body['email']  # Safe - guaranteed to exist by decorator

    # Send password reset email logic here
    return {"message": f"Password reset email sent to {email}"}, 200


# ============================================================================
# Usage Patterns & Best Practices
# ============================================================================

"""
BEST PRACTICE 1: Layer Validation by Criticality

HIGH CRITICALITY (auth, payment, data modification):
    @validate_request(method, path)      # OpenAPI schema validation
    @validate_types(...)                 # Type safety
    @validate_response_schema(...)       # Response verification
    def critical_handler(...): pass

MEDIUM CRITICALITY (most CRUD operations):
    @validate_request(method, path)      # OpenAPI schema validation
    @validate_types(...)                 # Type safety
    def standard_handler(...): pass

LOW CRITICALITY (read-only, public endpoints):
    @validate_required_fields_decorator(...)  # Minimal validation
    def simple_handler(...): pass


BEST PRACTICE 2: Decorator Order Matters

Correct order (outer to inner / bottom to top):
    @validate_response_schema(...)       # 4. Validate response (optional)
    @validate_request(...)               # 3. Validate request body
    @validate_types(...)                 # 2. Check parameter types
    @validate_required_fields_decorator  # 1. Check required fields
    def handler(...): pass

Execution flow: required fields → types → request → handler → response


BEST PRACTICE 3: Contract Tests Complement Decorators

Decorators provide RUNTIME validation (catch issues in production).
Contract tests provide BUILD-TIME validation (catch issues before deployment).

Recommended approach:
1. Add decorators to handlers (this file's examples)
2. Write contract tests for critical endpoints (see test_auth_contract.py)
3. Run contract tests in CI/CD pipeline
4. Monitor decorator validation failures in production


BEST PRACTICE 4: Error Responses Are Standardized

All decorators return consistent error format:
{
    "error": "Request validation failed",
    "details": "...",
    "path": [...]
}

This matches the Error model in OpenAPI spec, ensuring contract compliance
even for validation failures.


BEST PRACTICE 5: Performance Considerations

- OpenAPI spec is cached after first load (no I/O overhead)
- Schema validation adds ~1-5ms per request
- Response validation is non-blocking (logs warnings only)
- For high-throughput endpoints, consider using type validation only


MIGRATION PATH:

Week 1: Apply to authentication endpoints (highest risk)
Week 2: Apply to data modification endpoints (POST, PUT, PATCH)
Week 3: Apply to all remaining endpoints
Week 4: Add contract tests and monitoring
"""

# Example contract test location (see Task 4.2)
# tests/contract_tests/test_auth_contract.py
