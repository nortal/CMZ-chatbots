"""
PR003946-72: Role-Based Access Control Implementation

This module provides JWT authentication and role-based authorization
for the CMZ API endpoints.
"""

import jwt
import os
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, g

from openapi_server.impl.error_handler import AuthenticationError, AuthorizationError


# JWT configuration
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'test-secret-key')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

# Role hierarchy (higher values have more permissions)
# Updated to match OpenAPI schema enum values
ROLE_HIERARCHY = {
    'visitor': 1,
    'user': 2,
    'member': 3,
    'editor': 4,
    'admin': 5
}

# Valid user types
VALID_USER_TYPES = ['none', 'student', 'parent']


def generate_jwt_token(user_id, email, role='member', user_type='none'):
    """Generate a JWT token for authenticated user."""
    
    if role not in ROLE_HIERARCHY:
        raise ValueError(f"Invalid role: {role}")
    
    if user_type not in VALID_USER_TYPES:
        raise ValueError(f"Invalid user_type: {user_type}")
    
    payload = {
        'user_id': user_id,
        'email': email,
        'role': role,
        'user_type': user_type,
        'exp': datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS),
        'iat': datetime.now(timezone.utc)
    }
    
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_jwt_token(token):
    """Decode and validate a JWT token."""
    
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token has expired")
    except jwt.InvalidTokenError:
        raise AuthenticationError("Invalid token")


def extract_token_from_request():
    """Extract JWT token from request headers."""
    
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None
    
    # Handle "Bearer <token>" format
    if auth_header.startswith('Bearer '):
        return auth_header[7:]  # Remove "Bearer " prefix
    
    return auth_header


def get_current_user():
    """Get current user information from request context."""
    
    token = extract_token_from_request()
    if not token:
        raise AuthenticationError("Authentication token is required")
    
    payload = decode_jwt_token(token)
    
    # Store user info in request context
    g.current_user = {
        'user_id': payload['user_id'],
        'email': payload['email'], 
        'role': payload['role'],
        'user_type': payload['user_type']
    }
    
    return g.current_user


def check_role_permission(required_role, user_role):
    """Check if user role has sufficient permissions."""
    
    if required_role not in ROLE_HIERARCHY:
        raise ValueError(f"Invalid required_role: {required_role}")
    
    if user_role not in ROLE_HIERARCHY:
        return False
    
    return ROLE_HIERARCHY[user_role] >= ROLE_HIERARCHY[required_role]


def requires_auth(f):
    """Decorator that requires valid authentication."""
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            get_current_user()
        except AuthenticationError:
            raise AuthenticationError("Valid authentication is required to access this endpoint")
        
        return f(*args, **kwargs)
    
    return decorated_function


def requires_role(required_role):
    """Decorator that requires a specific role or higher."""
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                user = get_current_user()
            except AuthenticationError:
                raise AuthenticationError("Authentication is required to access this endpoint")
            
            user_role = user['role']
            
            if not check_role_permission(required_role, user_role):
                raise AuthorizationError(
                    f"This endpoint requires {required_role} role or higher",
                    required_role=required_role,
                    details={"current_role": user_role}
                )
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator


def requires_admin(f):
    """Decorator that requires admin role."""
    return requires_role('admin')(f)


def requires_keeper(f):
    """Decorator that requires keeper role or higher."""
    return requires_role('keeper')(f)


def requires_parent(f):
    """Decorator that requires parent role or higher.""" 
    return requires_role('parent')(f)


def authenticate_user(email, password):
    """
    Authenticate user credentials and return JWT token.
    
    This is a simplified implementation for testing.
    In production, this would validate against a user database.
    """
    
    # Test users for development/testing
    test_users = {
        # Original test users
        'admin@cmz.org': {
            'password': 'admin123',
            'user_id': 'admin_001',
            'role': 'admin',
            'user_type': 'none'
        },
        'keeper@cmz.org': {
            'password': 'keeper123',
            'user_id': 'keeper_001',
            'role': 'editor',  # Changed from 'keeper' to 'editor' for schema compatibility
            'user_type': 'none'
        },
        'parent@cmz.org': {
            'password': 'parent123',
            'user_id': 'parent_001',
            'role': 'member',  # Changed from 'parent' to 'member' for schema compatibility
            'user_type': 'parent'
        },
        'member@cmz.org': {
            'password': 'member123',
            'user_id': 'member_001',
            'role': 'member', 
            'user_type': 'none'
        },
        # Playwright test users
        'parent1@test.cmz.org': {
            'password': 'testpass123',
            'user_id': 'user_test_parent_001',
            'role': 'member',  # Changed from 'parent' to 'member' for schema compatibility
            'user_type': 'parent'
        },
        'student1@test.cmz.org': {
            'password': 'testpass123',
            'user_id': 'user_test_student_001',
            'role': 'member',
            'user_type': 'student'
        },
        'student2@test.cmz.org': {
            'password': 'testpass123',
            'user_id': 'user_test_student_002',
            'role': 'member',
            'user_type': 'student'
        },
        'test@cmz.org': {
            'password': 'testpass123',
            'user_id': 'user_default_test',
            'role': 'member',
            'user_type': 'none'
        },
        'user_parent_001@cmz.org': {
            'password': 'testpass123',
            'user_id': 'user_parent_001',
            'role': 'member',  # Changed from 'parent' to 'member' for schema compatibility
            'user_type': 'parent'
        }
    }
    
    if email not in test_users:
        raise AuthenticationError("Invalid email or password")
    
    user_data = test_users[email]
    
    if user_data['password'] != password:
        raise AuthenticationError("Invalid email or password")
    
    # Generate JWT token
    token = generate_jwt_token(
        user_id=user_data['user_id'],
        email=email,
        role=user_data['role'],
        user_type=user_data['user_type']
    )
    
    return {
        'token': token,
        'user': {
            'user_id': user_data['user_id'],
            'email': email,
            'role': user_data['role'],
            'user_type': user_data['user_type']
        }
    }


def validate_password_policy(password):
    """
    Validate password against security policy requirements.
    
    PR003946-87: Password policy enforcement
    """
    
    errors = []
    
    if len(password) < 6:
        errors.append("Password must be at least 6 characters long")
    
    if len(password) > 128:
        errors.append("Password must not exceed 128 characters")
    
    if not any(c.isdigit() for c in password):
        errors.append("Password must contain at least one digit")
    
    if not any(c.isalpha() for c in password):
        errors.append("Password must contain at least one letter")
    
    if errors:
        from openapi_server.impl.error_handler import ValidationError
        raise ValidationError(
            "Password does not meet security requirements",
            field_errors=errors,
            details={"field": "password", "policy_violations": errors},
            error_code="invalid_password"
        )
    
    return True


def refresh_jwt_token(current_token):
    """
    Refresh an existing JWT token with extended expiration.
    
    PR003946-88: Token refresh consistency
    """
    
    try:
        # Decode current token (even if expired, for refresh purposes)
        payload = jwt.decode(
            current_token, 
            JWT_SECRET_KEY, 
            algorithms=[JWT_ALGORITHM],
            options={"verify_exp": False}  # Allow expired tokens for refresh
        )
    except jwt.InvalidTokenError:
        raise AuthenticationError("Invalid token for refresh")
    
    # Check if token is not too old (max 7 days for refresh)
    issued_at = datetime.fromtimestamp(payload['iat'], tz=timezone.utc)
    max_refresh_age = timedelta(days=7)
    
    if datetime.now(timezone.utc) - issued_at > max_refresh_age:
        raise AuthenticationError("Token is too old for refresh, please login again")
    
    # Generate new token with same user data
    new_token = generate_jwt_token(
        user_id=payload['user_id'],
        email=payload['email'],
        role=payload['role'],
        user_type=payload['user_type']
    )
    
    return {
        'token': new_token,
        'user': {
            'user_id': payload['user_id'],
            'email': payload['email'],
            'role': payload['role'],
            'user_type': payload['user_type']
        }
    }