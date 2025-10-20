"""
Mock authentication module for development and testing.
Provides simple authentication without external dependencies.
"""

from typing import Dict, Any, Optional, Tuple
import hashlib
import time
import json
import base64

print("🔄🔄🔄 AUTH_MOCK.PY MODULE LOADED - VERSION 4.0 (JWT_UTILS INTEGRATION) 🔄🔄🔄")
from datetime import datetime, timedelta
from .utils.jwt_utils import generate_jwt_token

# Mock user database
MOCK_USERS = {
    'test@cmz.org': {'password': 'testpass123', 'role': 'admin', 'name': 'Test User'},
    'parent1@test.cmz.org': {'password': 'testpass123', 'role': 'parent', 'name': 'Test Parent One'},
    'student1@test.cmz.org': {'password': 'testpass123', 'role': 'student', 'name': 'Test Student One'},
    'student2@test.cmz.org': {'password': 'testpass123', 'role': 'student', 'name': 'Test Student Two'},
    'user_parent_001@cmz.org': {'password': 'testpass123', 'role': 'parent', 'name': 'Parent User 001'},
}

def generate_mock_token(email: str, role: str) -> str:
    """
    Generate a JWT token using centralized jwt_utils.
    This ensures frontend compatibility by including all required fields:
    - user_id, userId (both formats for compatibility)
    - email, role
    - user_type (some frontend code uses this)
    - exp, iat, iss, sub (standard JWT claims)
    """
    user_data = {
        'email': email,
        'role': role,
        # Generate user_id from email if not provided
        'user_id': email.replace('@', '_').replace('.', '_')
    }

    # Use centralized JWT generation to ensure frontend compatibility
    return generate_jwt_token(user_data, expiration_seconds=86400)  # 24 hours

def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Mock authentication function.
    Returns user data if credentials are valid, None otherwise.
    """
    print(f"🔥🔥🔥 AUTHENTICATE_USER FUNCTION EXECUTING NOW 🔥🔥🔥")
    print(f"🔍 DEBUG authenticate_user: email={email}, password={'*' * len(password) if password else 'EMPTY'}")
    print(f"🔍 DEBUG authenticate_user: email in MOCK_USERS={email in MOCK_USERS}")
    if email in MOCK_USERS:
        print(f"🔍 DEBUG authenticate_user: password matches={MOCK_USERS[email]['password'] == password}")

    if email in MOCK_USERS and MOCK_USERS[email]['password'] == password:
        user_data = MOCK_USERS[email].copy()
        token = generate_mock_token(email, user_data['role'])

        # Return the structure expected by the handler
        return {
            'token': token,
            'user': {
                'email': email,
                'role': user_data['role'],
                'name': user_data['name']
            }
        }
    return None

def handle_auth_logout_post() -> Tuple[Dict[str, Any], int]:
    """Handle logout - just return success"""
    return {"message": "Logout successful"}, 200

def handle_auth_refresh_post() -> Tuple[Dict[str, Any], int]:
    """Handle token refresh - return new mock token"""
    # In a real implementation, would validate old token first
    from openapi_server.models.auth_response import AuthResponse

    # Generate new token for default user
    token = generate_mock_token("test@cmz.org", "admin")

    response = AuthResponse(
        token=token,
        expires_in=3600,  # 1 hour
        user={"email": "test@cmz.org", "role": "admin", "name": "Test User"}
    )
    return response.to_dict(), 200

def handle_auth_reset_password_post(body: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    """Handle password reset request"""
    email = body.get('email')

    if email in MOCK_USERS:
        return {"message": f"Password reset link sent to {email}"}, 200

    from openapi_server.models.error import Error
    error = Error(
        code="user_not_found",
        message=f"User with email {email} not found"
    )
    return error.to_dict(), 404