"""
Contract Tests for Authentication Endpoints

These tests validate that the authentication implementation adheres to the
OpenAPI contract, preventing regressions after code generation or refactoring.

Purpose:
- Catch contract violations before deployment
- Verify request/response schemas match OpenAPI spec
- Ensure validation decorators are working correctly
- Prevent auth regressions after OpenAPI regeneration

Run: pytest tests/contract_tests/test_auth_contract.py -v
"""

import pytest
import json
from typing import Dict, Any
from openapi_server.models.auth_response import AuthResponse
from openapi_server.models.error import Error


class TestAuthContractCompliance:
    """
    Contract tests for POST /auth (login) endpoint

    Tests validate:
    1. Request body schema compliance
    2. Response body schema compliance
    3. Error response schema compliance
    4. Required field enforcement
    5. Type validation
    """

    # Test data following OpenAPI AuthRequest schema
    valid_auth_request = {
        "username": "test@cmz.org",
        "password": "testpass123"
    }

    def test_successful_login_response_contract(self):
        """
        Contract Test: Successful login returns AuthResponse schema

        OpenAPI spec defines AuthResponse with:
        - token (string, required)
        - user (UserSummary object, required)
        - expiresIn (integer, optional)
        """
        from openapi_server.impl.handlers import handle_login_post

        result, status_code = handle_login_post(self.valid_auth_request)

        # Verify status code
        assert status_code == 200, f"Expected 200, got {status_code}"

        # Verify response structure matches AuthResponse schema
        assert 'token' in result, "Missing required field: token"
        assert 'user' in result, "Missing required field: user"
        assert 'expiresIn' in result, "Missing optional field: expiresIn"

        # Verify field types
        assert isinstance(result['token'], str), f"token must be string, got {type(result['token'])}"
        assert isinstance(result['user'], dict), f"user must be dict, got {type(result['user'])}"
        assert isinstance(result['expiresIn'], int), f"expiresIn must be int, got {type(result['expiresIn'])}"

        # Verify user object structure (UserSummary schema)
        user = result['user']
        assert 'userId' in user, "User missing required field: userId"
        assert 'email' in user, "User missing required field: email"
        assert 'role' in user, "User missing required field: role"

        # Verify JWT token format (3 parts separated by dots)
        token_parts = result['token'].split('.')
        assert len(token_parts) == 3, f"JWT token must have 3 parts, got {len(token_parts)}"

    def test_failed_login_error_contract(self):
        """
        Contract Test: Failed login returns Error schema

        OpenAPI spec defines Error with:
        - code (string, required)
        - message (string, required)
        - details (object, optional)
        """
        from openapi_server.impl.handlers import handle_login_post

        invalid_request = {
            "username": "invalid@cmz.org",
            "password": "wrongpassword"
        }

        result, status_code = handle_login_post(invalid_request)

        # Verify error status code
        assert status_code == 401, f"Expected 401 for invalid credentials, got {status_code}"

        # Verify response structure matches Error schema
        assert 'code' in result, "Error missing required field: code"
        assert 'message' in result, "Error missing required field: message"

        # Verify field types
        assert isinstance(result['code'], str), f"code must be string, got {type(result['code'])}"
        assert isinstance(result['message'], str), f"message must be string, got {type(result['message'])}"

        # Verify error code value
        assert result['code'] == 'invalid_credentials', \
            f"Expected error code 'invalid_credentials', got '{result['code']}'"

    def test_missing_username_contract(self):
        """
        Contract Test: Missing required field returns 400 with Error schema

        OpenAPI AuthRequest schema requires username field.
        Missing required fields should return 400 Bad Request with Error response.
        """
        from openapi_server.impl.examples.decorated_auth_handler import handle_login_with_field_validation

        missing_username = {
            "password": "testpass123"
            # username missing
        }

        result, status_code = handle_login_with_field_validation(missing_username)

        # Verify validation failure status
        assert status_code == 400, f"Expected 400 for missing field, got {status_code}"

        # Verify Error schema compliance
        assert 'error' in result, "Validation error missing 'error' field"
        assert 'missing_fields' in result, "Validation error should list missing_fields"
        assert 'username' in result['missing_fields'], "Should identify 'username' as missing"

    def test_missing_password_contract(self):
        """
        Contract Test: Missing password field returns 400 with Error schema
        """
        from openapi_server.impl.examples.decorated_auth_handler import handle_login_with_field_validation

        missing_password = {
            "username": "test@cmz.org"
            # password missing
        }

        result, status_code = handle_login_with_field_validation(missing_password)

        # Verify validation failure
        assert status_code == 400, f"Expected 400 for missing field, got {status_code}"
        assert 'error' in result, "Validation error missing 'error' field"
        assert 'missing_fields' in result, "Validation error should list missing_fields"
        assert 'password' in result['missing_fields'], "Should identify 'password' as missing"

    def test_invalid_body_type_contract(self):
        """
        Contract Test: Invalid body type returns 400

        OpenAPI spec requires body to be JSON object.
        Non-dict types should be rejected with 400 error.
        """
        from openapi_server.impl.examples.decorated_auth_handler import handle_login_full_validation

        # Test with non-dict body (will fail type validation)
        with pytest.raises(Exception):
            # Type validation decorator will catch this before handler execution
            handle_login_full_validation("not_a_dict")

    def test_response_expires_in_type(self):
        """
        Contract Test: expiresIn field must be integer

        OpenAPI AuthResponse schema defines expiresIn as integer.
        String or float values violate the contract.
        """
        from openapi_server.impl.handlers import handle_login_post

        result, status_code = handle_login_post(self.valid_auth_request)

        assert status_code == 200
        assert 'expiresIn' in result

        # CRITICAL: Must be integer, not string
        expires_in = result['expiresIn']
        assert isinstance(expires_in, int), \
            f"expiresIn must be integer per OpenAPI spec, got {type(expires_in)}"

        # Additional validation: reasonable value (not negative, not too large)
        assert 0 < expires_in <= 86400 * 7, \
            f"expiresIn should be between 1 second and 7 days, got {expires_in}"

    def test_token_format_contract(self):
        """
        Contract Test: Token must be valid JWT format

        While OpenAPI spec just says "string", JWT tokens have specific format:
        header.payload.signature (3 base64-encoded parts separated by dots)
        """
        from openapi_server.impl.handlers import handle_login_post

        result, status_code = handle_login_post(self.valid_auth_request)

        assert status_code == 200
        token = result['token']

        # JWT structure validation
        parts = token.split('.')
        assert len(parts) == 3, \
            f"JWT must have 3 parts (header.payload.signature), got {len(parts)}"

        # Each part should be base64-encoded (non-empty)
        for i, part in enumerate(parts):
            assert len(part) > 0, f"JWT part {i} is empty"

    def test_user_summary_contract(self):
        """
        Contract Test: User object matches UserSummary schema

        OpenAPI UserSummary schema requires:
        - userId (string)
        - email (string)
        - role (string, enum: admin|parent|student|visitor|zookeeper)
        """
        from openapi_server.impl.handlers import handle_login_post

        result, status_code = handle_login_post(self.valid_auth_request)

        assert status_code == 200
        user = result['user']

        # Required fields
        assert 'userId' in user, "UserSummary missing userId"
        assert 'email' in user, "UserSummary missing email"
        assert 'role' in user, "UserSummary missing role"

        # Field types
        assert isinstance(user['userId'], str), "userId must be string"
        assert isinstance(user['email'], str), "email must be string"
        assert isinstance(user['role'], str), "role must be string"

        # Role enum validation
        valid_roles = ['admin', 'parent', 'student', 'visitor', 'zookeeper', 'member']
        assert user['role'] in valid_roles, \
            f"Role '{user['role']}' not in valid roles: {valid_roles}"

        # Email format validation
        assert '@' in user['email'], f"Email '{user['email']}' missing @ symbol"
        assert '.' in user['email'].split('@')[1], f"Email '{user['email']}' missing domain extension"


class TestAuthRegressionPrevention:
    """
    Regression tests to prevent common auth issues after OpenAPI regeneration

    These tests catch specific issues that have occurred in the past:
    1. Auth handler routing breaks after code generation
    2. JWT token generation missing required fields
    3. Response field name mismatches (expires_in vs expiresIn)
    """

    def test_auth_handler_exists_and_callable(self):
        """
        Regression Test: Auth handler must exist and be callable

        ISSUE: After OpenAPI regeneration, auth_controller.py sometimes
        looks for wrong handler name, causing 501 Not Implemented errors.
        """
        from openapi_server.impl import handlers

        # Verify handler function exists
        assert hasattr(handlers, 'handle_login_post'), \
            "handle_login_post handler missing - check post-generation fixes"

        # Verify it's callable
        assert callable(handlers.handle_login_post), \
            "handle_login_post exists but is not callable"

        # Verify it can be called with proper arguments
        test_body = {"username": "test@cmz.org", "password": "testpass123"}
        result = handlers.handle_login_post(test_body)

        # Should return tuple (response, status_code)
        assert isinstance(result, tuple), \
            f"Handler should return tuple, got {type(result)}"
        assert len(result) == 2, \
            f"Handler should return (response, status_code), got {len(result)} elements"

    def test_jwt_token_includes_user_id(self):
        """
        Regression Test: JWT payload must include userId

        ISSUE: JWT tokens sometimes generated without userId field,
        causing frontend auth failures even with valid tokens.
        """
        from openapi_server.impl.handlers import handle_login_post
        from openapi_server.impl.utils.jwt_utils import decode_jwt_token
        import json
        import base64

        result, status_code = handle_login_post({
            "username": "test@cmz.org",
            "password": "testpass123"
        })

        assert status_code == 200
        token = result['token']

        # Decode JWT payload (middle part)
        parts = token.split('.')
        payload_encoded = parts[1]

        # Add padding if needed for base64 decoding
        padding = 4 - len(payload_encoded) % 4
        if padding != 4:
            payload_encoded += '=' * padding

        payload_json = base64.urlsafe_b64decode(payload_encoded)
        payload = json.loads(payload_json)

        # CRITICAL: userId must be in JWT payload for frontend auth
        assert 'userId' in payload or 'user_id' in payload, \
            f"JWT payload missing userId field. Payload keys: {list(payload.keys())}"

    def test_response_field_names_camelcase(self):
        """
        Regression Test: Response fields must use camelCase per OpenAPI spec

        ISSUE: Python code uses snake_case, but OpenAPI spec uses camelCase.
        Response field name mismatches cause frontend parsing failures.
        """
        from openapi_server.impl.handlers import handle_login_post

        result, status_code = handle_login_post({
            "username": "test@cmz.org",
            "password": "testpass123"
        })

        assert status_code == 200

        # Verify camelCase field names (NOT snake_case)
        assert 'expiresIn' in result, \
            "Response missing 'expiresIn' field (camelCase per OpenAPI spec)"

        # Should NOT have snake_case version
        assert 'expires_in' not in result, \
            "Response has 'expires_in' (snake_case) but OpenAPI spec requires 'expiresIn' (camelCase)"

        assert 'userId' in result['user'], \
            "User object missing 'userId' field (camelCase per OpenAPI spec)"

        # Should NOT have snake_case version
        assert 'user_id' not in result['user'], \
            "User object has 'user_id' (snake_case) but OpenAPI spec requires 'userId' (camelCase)"


# ============================================================================
# Test Fixtures and Utilities
# ============================================================================

@pytest.fixture
def mock_auth_request():
    """Fixture providing valid auth request data"""
    return {
        "username": "test@cmz.org",
        "password": "testpass123"
    }


@pytest.fixture
def invalid_auth_request():
    """Fixture providing invalid auth request data"""
    return {
        "username": "invalid@cmz.org",
        "password": "wrongpassword"
    }


# ============================================================================
# Usage Instructions
# ============================================================================

"""
HOW TO RUN THESE TESTS:

1. Run all contract tests:
   pytest tests/contract_tests/ -v

2. Run only auth contract tests:
   pytest tests/contract_tests/test_auth_contract.py -v

3. Run specific test:
   pytest tests/contract_tests/test_auth_contract.py::TestAuthContractCompliance::test_successful_login_response_contract -v

4. Run with coverage:
   pytest tests/contract_tests/test_auth_contract.py --cov=openapi_server.impl -v


WHEN TO RUN THESE TESTS:

1. ALWAYS: After OpenAPI code regeneration
2. ALWAYS: Before creating pull request
3. RECOMMENDED: In pre-commit hook
4. REQUIRED: In CI/CD pipeline
5. OPTIONAL: During development (TDD approach)


WHAT TO DO WHEN TESTS FAIL:

1. Contract compliance failure → Fix implementation to match OpenAPI spec
2. Regression test failure → Check post-generation fixes were applied
3. Field name mismatch → Update response to use camelCase per OpenAPI
4. Missing field → Add field to response or update OpenAPI spec
5. Type mismatch → Fix implementation or update OpenAPI schema


ADDING NEW CONTRACT TESTS:

1. Identify endpoint to test
2. Review OpenAPI spec for that endpoint
3. Create test class: Test{Endpoint}ContractCompliance
4. Add tests for:
   - Request schema validation
   - Response schema validation
   - Error response validation
   - Required field enforcement
   - Type validation
5. Add regression tests for known issues
6. Document any assumptions or dependencies
"""
