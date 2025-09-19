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

from openapi_server.impl.auth import authenticate_user, generate_jwt


class TestJWTFormat:
    """Test JWT token format requirements"""

    def test_jwt_has_three_parts(self):
        """JWT must have exactly 3 parts separated by dots"""
        user_data = {'email': 'test@cmz.org', 'role': 'user', 'userId': 'test_user'}
        token = generate_jwt(user_data)

        parts = token.split('.')
        assert len(parts) == 3, f"Token should have 3 parts, got {len(parts)}"

    def test_jwt_header_format(self):
        """JWT header must be properly formatted"""
        user_data = {'email': 'test@cmz.org', 'role': 'user', 'userId': 'test_user'}
        token = generate_jwt(user_data)

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
        user_data = {'email': 'test@cmz.org', 'role': 'admin', 'userId': 'test_user'}
        token = generate_jwt(user_data)

        payload_encoded = token.split('.')[1]
        # Add padding if necessary
        padding = 4 - (len(payload_encoded) % 4)
        if padding != 4:
            payload_encoded += '=' * padding

        payload_json = base64.urlsafe_b64decode(payload_encoded)
        payload = json.loads(payload_json)

        # Required fields for frontend
        required_fields = ['email', 'role', 'exp', 'iat']
        for field in required_fields:
            assert field in payload, f"Payload missing required field: {field}"

        # Either user_id or userId should be present
        assert 'user_id' in payload or 'userId' in payload, "Payload must have user_id or userId"

    def test_jwt_payload_user_id_formats(self):
        """JWT payload should support both user_id and userId"""
        user_data = {'email': 'test@cmz.org', 'role': 'user', 'userId': 'test_user'}
        token = generate_jwt(user_data)

        payload_encoded = token.split('.')[1]
        # Add padding if necessary
        padding = 4 - (len(payload_encoded) % 4)
        if padding != 4:
            payload_encoded += '=' * padding

        payload_json = base64.urlsafe_b64decode(payload_encoded)
        payload = json.loads(payload_json)

        # Should have both formats for compatibility
        assert 'user_id' in payload, "Payload should have user_id (snake_case)"
        assert 'userId' in payload, "Payload should have userId (camelCase)"
        assert payload['user_id'] == payload['userId'], "Both user_id formats should match"


class TestAuthResponse:
    """Test authentication response structure"""

    def test_response_structure(self):
        """Auth response must match frontend expectations"""
        response = authenticate_user('test@cmz.org', 'testpass123')

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
        response = authenticate_user('test@cmz.org', 'testpass123')

        assert isinstance(response['expiresIn'], int), "expiresIn must be an integer"
        assert response['expiresIn'] > 0, "expiresIn must be positive"
        assert response['expiresIn'] <= 86400, "expiresIn should be reasonable (max 24 hours)"


class TestMockAuthentication:
    """Test mock authentication mode"""

    def test_mock_users_available(self):
        """All test users should authenticate successfully"""
        test_credentials = [
            ('admin@cmz.org', 'admin123', 'admin'),
            ('test@cmz.org', 'testpass123', 'user'),
            ('parent1@test.cmz.org', 'testpass123', 'parent'),
            ('student1@test.cmz.org', 'testpass123', 'student'),
            ('student2@test.cmz.org', 'testpass123', 'student'),
            ('user_parent_001@cmz.org', 'testpass123', 'parent'),
        ]

        for email, password, expected_role in test_credentials:
            response = authenticate_user(email, password)

            assert 'token' in response, f"Response for {email} must have token"
            assert response['user']['email'] == email, f"Email mismatch for {email}"
            assert response['user']['role'] == expected_role, f"Role mismatch for {email}"

    def test_invalid_credentials(self):
        """Invalid credentials should raise error"""
        with pytest.raises(ValueError) as exc_info:
            authenticate_user('invalid@cmz.org', 'wrongpass')
        assert "Invalid email or password" in str(exc_info.value)

        # Wrong password for valid user
        with pytest.raises(ValueError) as exc_info:
            authenticate_user('admin@cmz.org', 'wrongpass')
        assert "Invalid email or password" in str(exc_info.value)


class TestFrontendCompatibility:
    """Test frontend compatibility requirements"""

    def test_token_decodable_by_frontend_pattern(self):
        """Token should be decodable using frontend's JWT decode pattern"""
        response = authenticate_user('test@cmz.org', 'testpass123')
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