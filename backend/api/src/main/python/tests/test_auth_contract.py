"""
Authentication Contract Tests for CMZ API
Ensures frontend-backend auth contract is maintained
"""

import pytest
import json
import base64
import os
import sys
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from openapi_server.impl.auth import authenticate_user, authenticate_user_mock
from openapi_server.impl.utils.jwt_utils import (
    generate_jwt_token,
    decode_jwt_payload,
    verify_jwt_token,
    create_auth_response
)


class TestJWTFormat:
    """Test JWT token format requirements"""

    def test_jwt_has_three_parts(self):
        """JWT must have exactly 3 parts separated by dots"""
        user_data = {'email': 'test@cmz.org', 'role': 'user'}
        token = generate_jwt_token(user_data)

        parts = token.split('.')
        assert len(parts) == 3, f"Token should have 3 parts, got {len(parts)}"

    def test_jwt_header_format(self):
        """JWT header must be properly formatted"""
        user_data = {'email': 'test@cmz.org', 'role': 'user'}
        token = generate_jwt_token(user_data)

        header_encoded = token.split('.')[0]
        # Add padding if necessary
        padding = 4 - (len(header_encoded) % 4)
        if padding != 4:
            header_encoded += '=' * padding

        header_json = base64.urlsafe_b64decode(header_encoded)
        header = json.loads(header_json)

        assert 'alg' in header, "Header must contain 'alg' field"
        assert 'typ' in header, "Header must contain 'typ' field"
        assert header['typ'] == 'JWT', "Header typ must be 'JWT'"

    def test_jwt_payload_required_fields(self):
        """JWT payload must contain all required fields"""
        user_data = {'email': 'test@cmz.org', 'role': 'admin', 'user_id': 'test_user'}
        token = generate_jwt_token(user_data)

        payload = decode_jwt_payload(token)
        assert payload is not None, "Payload should be decodable"

        # Required fields for frontend
        required_fields = ['email', 'role', 'exp', 'iat']
        for field in required_fields:
            assert field in payload, f"Payload missing required field: {field}"

        # Either user_id or userId should be present
        assert 'user_id' in payload or 'userId' in payload, "Payload must have user_id or userId"

    def test_jwt_payload_user_id_formats(self):
        """JWT payload should support both user_id and userId"""
        user_data = {'email': 'test@cmz.org', 'role': 'user'}
        token = generate_jwt_token(user_data)

        payload = decode_jwt_payload(token)
        # Should have both formats for compatibility
        assert 'user_id' in payload, "Payload should have user_id (snake_case)"
        assert 'userId' in payload, "Payload should have userId (camelCase)"
        assert payload['user_id'] == payload['userId'], "Both user_id formats should match"


class TestAuthResponse:
    """Test authentication response structure"""

    def test_response_structure(self):
        """Auth response must match frontend expectations"""
        user_data = {'email': 'test@cmz.org', 'role': 'admin'}
        response = create_auth_response(user_data)

        # Required top-level fields
        assert 'token' in response, "Response must contain 'token'"
        assert 'user' in response, "Response must contain 'user'"
        assert 'expiresIn' in response, "Response must contain 'expiresIn'"

        # Token should NOT have 'Bearer ' prefix
        assert not response['token'].startswith('Bearer '), "Token should not have 'Bearer ' prefix"

        # User object fields
        user = response['user']
        assert 'email' in user, "User must have 'email'"
        assert 'role' in user, "User must have 'role'"
        assert 'userId' in user, "User must have 'userId'"

    def test_expires_in_format(self):
        """expiresIn should be a number in seconds"""
        user_data = {'email': 'test@cmz.org', 'role': 'user'}
        response = create_auth_response(user_data)

        assert isinstance(response['expiresIn'], int), "expiresIn must be an integer"
        assert response['expiresIn'] > 0, "expiresIn must be positive"
        assert response['expiresIn'] <= 86400, "expiresIn should be reasonable (max 24 hours)"


class TestMockAuthentication:
    """Test mock authentication mode"""

    @patch.dict(os.environ, {'AUTH_MODE': 'mock'})
    def test_mock_users_available(self):
        """All test users should authenticate successfully in mock mode"""
        test_credentials = [
            ('admin@cmz.org', 'admin123', 'admin'),
            ('test@cmz.org', 'testpass123', 'user'),
            ('parent1@test.cmz.org', 'testpass123', 'parent'),
            ('student1@test.cmz.org', 'testpass123', 'student'),
            ('student2@test.cmz.org', 'testpass123', 'student'),
            ('user_parent_001@cmz.org', 'testpass123', 'parent'),
        ]

        for email, password, expected_role in test_credentials:
            response = authenticate_user_mock(email, password)

            assert 'token' in response, f"Response for {email} must have token"
            assert response['user']['email'] == email, f"Email mismatch for {email}"
            assert response['user']['role'] == expected_role, f"Role mismatch for {email}"

    @patch.dict(os.environ, {'AUTH_MODE': 'mock'})
    def test_mock_invalid_credentials(self):
        """Invalid credentials should raise error in mock mode"""
        with pytest.raises(ValueError) as exc_info:
            authenticate_user_mock('invalid@cmz.org', 'wrongpass')
        assert "Invalid email or password" in str(exc_info.value)

        # Wrong password for valid user
        with pytest.raises(ValueError) as exc_info:
            authenticate_user_mock('admin@cmz.org', 'wrongpass')
        assert "Invalid email or password" in str(exc_info.value)


class TestTokenVerification:
    """Test JWT token verification"""

    def test_verify_valid_token(self):
        """Valid tokens should verify successfully"""
        user_data = {'email': 'test@cmz.org', 'role': 'user'}
        token = generate_jwt_token(user_data)

        is_valid, payload = verify_jwt_token(token)
        assert is_valid is True, "Valid token should verify successfully"
        assert payload is not None, "Valid token should return payload"
        assert payload['email'] == 'test@cmz.org', "Payload should contain correct email"

    def test_verify_expired_token(self):
        """Expired tokens should fail verification"""
        user_data = {'email': 'test@cmz.org', 'role': 'user'}
        # Generate token with negative expiration
        token = generate_jwt_token(user_data, expiration_seconds=-1)

        is_valid, payload = verify_jwt_token(token)
        assert is_valid is False, "Expired token should fail verification"

    def test_verify_malformed_token(self):
        """Malformed tokens should fail verification"""
        invalid_tokens = [
            'not.a.token',
            'only.two',
            'invalid_base64.xxx.yyy',
            '',
            'Bearer token.without.parts'
        ]

        for invalid_token in invalid_tokens:
            is_valid, payload = verify_jwt_token(invalid_token)
            assert is_valid is False, f"Malformed token should fail: {invalid_token}"


class TestAuthModeRouting:
    """Test authentication mode routing"""

    @patch.dict(os.environ, {'AUTH_MODE': 'mock'})
    def test_mock_mode_routing(self):
        """AUTH_MODE=mock should use mock authentication"""
        response = authenticate_user('admin@cmz.org', 'admin123')
        assert 'token' in response
        assert 'auth_mode' not in response['user'] or response['user'].get('auth_mode') == 'mock'

    @patch.dict(os.environ, {'AUTH_MODE': 'dynamodb'})
    @patch('openapi_server.impl.auth.table')
    def test_dynamodb_mode_routing(self, mock_table):
        """AUTH_MODE=dynamodb should attempt DynamoDB authentication"""
        # Mock DynamoDB response
        mock_table_instance = MagicMock()
        mock_table.return_value = mock_table_instance
        mock_table_instance.get_item.return_value = {
            'Item': {
                'email': {'S': 'test@cmz.org'},
                'password': {'S': 'testpass'},
                'role': {'S': 'user'}
            }
        }

        try:
            response = authenticate_user('test@cmz.org', 'testpass')
            # Should attempt to use DynamoDB
            mock_table.assert_called()
        except Exception:
            # It's okay if it fails, we just want to verify it tried DynamoDB
            mock_table.assert_called()

    @patch.dict(os.environ, {'AUTH_MODE': 'invalid'})
    def test_invalid_mode_defaults_to_mock(self):
        """Invalid AUTH_MODE should default to mock"""
        # Should fall back to mock mode
        response = authenticate_user('admin@cmz.org', 'admin123')
        assert 'token' in response


class TestFrontendCompatibility:
    """Test frontend compatibility requirements"""

    def test_token_decodable_by_frontend_pattern(self):
        """Token should be decodable using frontend's JWT decode pattern"""
        user_data = {'email': 'test@cmz.org', 'role': 'user'}
        response = create_auth_response(user_data)
        token = response['token']

        # Simulate frontend decode logic
        parts = token.split('.')
        assert len(parts) == 3, "Frontend expects 3 parts"

        # Frontend adds padding and decodes
        payload_encoded = parts[1]
        padding = 4 - (len(payload_encoded) % 4)
        if padding != 4:
            payload_encoded += '=' * padding

        # Should not raise exception
        payload_json = base64.urlsafe_b64decode(payload_encoded)
        payload = json.loads(payload_json)

        # Frontend expects these fields
        assert 'email' in payload
        assert 'exp' in payload
        assert 'iat' in payload

    def test_auth_response_for_frontend(self):
        """Complete auth flow should produce frontend-compatible response"""
        with patch.dict(os.environ, {'AUTH_MODE': 'mock'}):
            response = authenticate_user('admin@cmz.org', 'admin123')

            # Validate complete response structure
            assert isinstance(response, dict), "Response should be a dictionary"
            assert 'token' in response, "Response must have token"
            assert 'user' in response, "Response must have user"
            assert 'expiresIn' in response, "Response must have expiresIn"

            # Validate token format
            token_parts = response['token'].split('.')
            assert len(token_parts) == 3, "Token must have 3 parts"

            # Validate user object
            user = response['user']
            assert user['email'] == 'admin@cmz.org'
            assert user['role'] == 'admin'
            assert 'userId' in user


if __name__ == '__main__':
    pytest.main([__file__, '-v'])