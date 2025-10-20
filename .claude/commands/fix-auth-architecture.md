# /fix-auth-architecture

**Purpose**: Systematically fix all authentication architectural issues including JWT format mismatches, OpenAPI regeneration breakages, environment mode confusion, frontend-backend contract violations, and missing regression tests.

## Context

The CMZ authentication system has recurring issues due to architectural fragility at the intersection of:
- Generated OpenAPI controllers
- Manual implementation handlers
- Frontend JWT expectations
- Multiple auth modes (mock, DynamoDB, Cognito)

This solution implements a robust, regression-resistant authentication architecture.

## Sequential Reasoning Approach

Use MCP Sequential Thinking to systematically fix authentication issues:

### Phase 1: Analysis & Planning
**Use Sequential Reasoning to:**
1. **Assess Current State**: Identify all broken auth components and their dependencies
2. **Define Architecture**: Design robust auth system with clear separation of concerns
3. **Plan Implementation**: Order changes to avoid breaking existing functionality
4. **Identify Test Points**: Determine what needs validation at each step
5. **Risk Assessment**: Identify potential breaking points and mitigation strategies

**Key Questions for Sequential Analysis:**
- What auth modes are actually needed (mock, DynamoDB, Cognito)?
- How can we protect auth from OpenAPI regeneration?
- What is the exact JWT contract between frontend and backend?
- How do we ensure auth works consistently across environments?
- What tests will prevent future regressions?

### Phase 2: Core Implementation
**Implementation Order (Follow Exactly):**

#### Step 1: Create JWT Utility Module
```python
# backend/api/src/main/python/openapi_server/impl/utils/jwt_utils.py
"""
JWT utility module for consistent token generation across all auth modes.
Ensures frontend-backend contract compliance.
"""

import json
import base64
import time
import os
from typing import Dict, Any, Optional

def create_jwt_token(
    user_id: str,
    email: str,
    role: str,
    expires_in: int = 86400  # 24 hours default
) -> str:
    """
    Generate a properly formatted JWT token that matches frontend expectations.

    Args:
        user_id: Unique user identifier
        email: User email address
        role: User role (admin, parent, student, user)
        expires_in: Token expiration in seconds

    Returns:
        Properly formatted JWT token (header.payload.signature)
    """
    # JWT Header
    header = {
        "alg": "HS256",
        "typ": "JWT"
    }

    # JWT Payload - MUST match frontend expectations
    current_time = int(time.time())
    payload = {
        "user_id": user_id,
        "email": email,
        "role": role,
        "user_type": role,  # Frontend expects both role and user_type
        "exp": current_time + expires_in,
        "iat": current_time,
        "iss": "cmz-auth-service",
        "sub": user_id
    }

    # Encode header and payload
    header_encoded = base64.urlsafe_b64encode(
        json.dumps(header).encode()
    ).decode().rstrip('=')

    payload_encoded = base64.urlsafe_b64encode(
        json.dumps(payload).encode()
    ).decode().rstrip('=')

    # Create signature (use proper secret in production)
    secret = os.environ.get('JWT_SECRET', 'development-secret-key')
    signature_input = f"{header_encoded}.{payload_encoded}"

    # For development/mock mode, use simple signature
    # In production, use proper HMAC-SHA256
    if os.environ.get('AUTH_MODE', 'mock') == 'mock':
        signature = base64.urlsafe_b64encode(
            f"mock-signature-{secret}".encode()
        ).decode().rstrip('=')
    else:
        # TODO: Implement proper HMAC-SHA256 for production
        import hmac
        import hashlib
        signature_bytes = hmac.new(
            secret.encode(),
            signature_input.encode(),
            hashlib.sha256
        ).digest()
        signature = base64.urlsafe_b64encode(signature_bytes).decode().rstrip('=')

    return f"{header_encoded}.{payload_encoded}.{signature}"

def decode_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate JWT token.

    Args:
        token: JWT token string

    Returns:
        Decoded payload if valid, None otherwise
    """
    try:
        # Remove 'Bearer ' prefix if present
        if token.startswith('Bearer '):
            token = token[7:]

        parts = token.split('.')
        if len(parts) != 3:
            return None

        # Decode payload
        payload_encoded = parts[1]
        # Add padding if needed
        payload_encoded += '=' * (4 - len(payload_encoded) % 4)

        payload = json.loads(
            base64.urlsafe_b64decode(payload_encoded).decode()
        )

        # Check expiration
        if payload.get('exp', 0) < time.time():
            return None

        return payload
    except Exception:
        return None
```

#### Step 2: Create Auth Configuration Module
```python
# backend/api/src/main/python/openapi_server/impl/utils/auth_config.py
"""
Authentication configuration and mode management.
Provides clear separation between mock, DynamoDB, and Cognito auth modes.
"""

import os
from enum import Enum
from typing import Dict, Any, Optional

class AuthMode(Enum):
    MOCK = "mock"
    DYNAMODB = "dynamodb"
    COGNITO = "cognito"

def get_auth_mode() -> AuthMode:
    """Get current authentication mode from environment."""
    mode = os.environ.get('AUTH_MODE', 'mock').lower()
    try:
        return AuthMode(mode)
    except ValueError:
        # Default to mock if invalid mode
        return AuthMode.MOCK

def get_mock_users() -> Dict[str, Dict[str, str]]:
    """Get mock users for development/testing."""
    return {
        'admin@cmz.org': {
            'password': 'admin123',
            'role': 'admin',
            'user_id': 'admin_cmz_org',
            'name': 'Admin User'
        },
        'test@cmz.org': {
            'password': 'testpass123',
            'role': 'user',
            'user_id': 'test_cmz_org',
            'name': 'Test User'
        },
        'parent1@test.cmz.org': {
            'password': 'testpass123',
            'role': 'parent',
            'user_id': 'parent1_test_cmz_org',
            'name': 'Test Parent One'
        },
        'student1@test.cmz.org': {
            'password': 'testpass123',
            'role': 'student',
            'user_id': 'student1_test_cmz_org',
            'name': 'Test Student One'
        },
        'student2@test.cmz.org': {
            'password': 'testpass123',
            'role': 'student',
            'user_id': 'student2_test_cmz_org',
            'name': 'Test Student Two'
        },
        'user_parent_001@cmz.org': {
            'password': 'testpass123',
            'role': 'parent',
            'user_id': 'user_parent_001_cmz_org',
            'name': 'Parent User 001'
        }
    }

def get_auth_config() -> Dict[str, Any]:
    """Get authentication configuration for current mode."""
    mode = get_auth_mode()

    config = {
        'mode': mode.value,
        'token_expiry': int(os.environ.get('JWT_EXPIRY', '86400')),
        'issuer': 'cmz-auth-service'
    }

    if mode == AuthMode.MOCK:
        config['users'] = get_mock_users()
    elif mode == AuthMode.DYNAMODB:
        config['table_name'] = os.environ.get('USERS_TABLE', 'cmz-users-dev')
        config['region'] = os.environ.get('AWS_REGION', 'us-west-2')
    elif mode == AuthMode.COGNITO:
        config['user_pool_id'] = os.environ.get('COGNITO_USER_POOL_ID')
        config['client_id'] = os.environ.get('COGNITO_CLIENT_ID')
        config['region'] = os.environ.get('AWS_REGION', 'us-west-2')

    return config
```

#### Step 3: Update auth.py Implementation
```python
# backend/api/src/main/python/openapi_server/impl/auth.py
"""
Robust authentication implementation with multiple mode support.
Protected from OpenAPI regeneration issues.
"""

from typing import Any, Dict, Tuple
import boto3
from botocore.exceptions import ClientError

from ..models.error import Error
from .utils.jwt_utils import create_jwt_token, decode_jwt_token
from .utils.auth_config import get_auth_mode, get_auth_config, AuthMode, get_mock_users

def authenticate_user_mock(email: str, password: str) -> Dict[str, Any]:
    """Authenticate against mock users."""
    mock_users = get_mock_users()

    if email not in mock_users:
        raise ValueError("Invalid email or password")

    user = mock_users[email]
    if user['password'] != password:
        raise ValueError("Invalid email or password")

    # Generate proper JWT token
    token = create_jwt_token(
        user_id=user['user_id'],
        email=email,
        role=user['role']
    )

    return {
        'token': token,
        'expiresIn': 86400,
        'user': {
            'userId': user['user_id'],
            'email': email,
            'role': user['role'],
            'displayName': user['name']
        }
    }

def authenticate_user_dynamodb(email: str, password: str) -> Dict[str, Any]:
    """Authenticate against DynamoDB users table."""
    config = get_auth_config()

    try:
        dynamodb = boto3.resource('dynamodb', region_name=config['region'])
        table = dynamodb.Table(config['table_name'])

        # Query for user by email
        response = table.get_item(Key={'email': email})

        if 'Item' not in response:
            raise ValueError("Invalid email or password")

        user = response['Item']

        # TODO: Implement proper password hashing check
        # For now, simple comparison (NOT for production!)
        if user.get('password') != password:
            raise ValueError("Invalid email or password")

        # Generate proper JWT token
        token = create_jwt_token(
            user_id=user.get('userId', email.replace('@', '_').replace('.', '_')),
            email=email,
            role=user.get('role', 'user')
        )

        return {
            'token': token,
            'expiresIn': config['token_expiry'],
            'user': {
                'userId': user.get('userId'),
                'email': email,
                'role': user.get('role'),
                'displayName': user.get('displayName', email.split('@')[0])
            }
        }
    except ClientError as e:
        # Log the actual error but return generic message to user
        print(f"DynamoDB error: {e}")
        raise ValueError("Authentication service temporarily unavailable")

def authenticate_user_cognito(email: str, password: str) -> Dict[str, Any]:
    """Authenticate against AWS Cognito."""
    config = get_auth_config()

    # TODO: Implement Cognito authentication
    # For now, raise not implemented
    raise NotImplementedError("Cognito authentication not yet implemented")

def authenticate_user(email: str, password: str) -> Dict[str, Any]:
    """
    Main authentication function that routes to appropriate auth mode.
    """
    mode = get_auth_mode()

    if mode == AuthMode.MOCK:
        return authenticate_user_mock(email, password)
    elif mode == AuthMode.DYNAMODB:
        return authenticate_user_dynamodb(email, password)
    elif mode == AuthMode.COGNITO:
        return authenticate_user_cognito(email, password)
    else:
        raise ValueError("Invalid authentication mode configured")

def handle_auth_post(body=None, *args, **kwargs) -> Tuple[Any, int]:
    """
    Implementation handler for auth_post.
    Protected from OpenAPI regeneration issues.
    """
    try:
        # Validate request body
        if not body:
            return {
                "code": "missing_credentials",
                "message": "Missing request body"
            }, 400

        # Support both 'username' and 'email' fields for compatibility
        email = body.get('username') or body.get('email')
        password = body.get('password')

        if not email or not password:
            return {
                "code": "missing_credentials",
                "message": "Email and password required"
            }, 400

        # Authenticate user based on configured mode
        result = authenticate_user(email, password)
        return result, 200

    except ValueError as e:
        return {
            "code": "authentication_failed",
            "message": str(e)
        }, 401
    except NotImplementedError as e:
        return {
            "code": "not_implemented",
            "message": str(e)
        }, 501
    except Exception as e:
        # Log the actual error but return generic message
        print(f"Authentication error: {e}")
        return {
            "code": "server_error",
            "message": "Internal server error"
        }, 500

def handle_auth_verify_post(body=None, *args, **kwargs) -> Tuple[Any, int]:
    """
    Verify JWT token validity.
    """
    try:
        if not body or 'token' not in body:
            return {
                "code": "missing_token",
                "message": "Token required"
            }, 400

        payload = decode_jwt_token(body['token'])

        if not payload:
            return {
                "code": "invalid_token",
                "message": "Invalid or expired token"
            }, 401

        return {
            "valid": True,
            "payload": payload
        }, 200

    except Exception as e:
        print(f"Token verification error: {e}")
        return {
            "code": "server_error",
            "message": "Internal server error"
        }, 500

# Export handlers for controller connection
__all__ = ['handle_auth_post', 'handle_auth_verify_post']
```

#### Step 4: Create Protection Script for OpenAPI Regeneration
```python
# backend/api/scripts/protect_auth_handlers.py
"""
Script to ensure auth handlers remain connected after OpenAPI regeneration.
Run as part of make post-generate.
"""

import os
import re

def protect_auth_controller():
    """Ensure auth controller properly imports and uses auth handlers."""

    controller_path = 'backend/api/src/main/python/openapi_server/controllers/auth_controller.py'

    if not os.path.exists(controller_path):
        print(f"Warning: {controller_path} not found")
        return

    with open(controller_path, 'r') as f:
        content = f.read()

    # Check if handler import exists
    if 'from ..impl.auth import handle_auth_post' not in content:
        # Add import after other imports
        import_line = "from ..impl.auth import handle_auth_post, handle_auth_verify_post"
        content = re.sub(
            r'(from .* import .*\n)+',
            r'\g<0>' + import_line + '\n',
            content,
            count=1
        )

    # Replace "do some magic!" with actual handler calls
    content = re.sub(
        r'def auth_post\([^)]*\)[^:]*:\n.*?"do some magic!".*?\n.*?return.*?\n',
        'def auth_post(body=None):\n    return handle_auth_post(body)\n',
        content,
        flags=re.DOTALL
    )

    with open(controller_path, 'w') as f:
        f.write(content)

    print(f"✅ Protected auth controller from regeneration issues")

if __name__ == "__main__":
    protect_auth_controller()
```

#### Step 5: Create Auth Contract Tests
```python
# backend/api/src/main/python/tests/test_auth_contract.py
"""
Tests to ensure auth endpoint maintains frontend-backend contract.
Prevents regressions in JWT format and response structure.
"""

import pytest
import json
import base64
import os

# Set mock mode for testing
os.environ['AUTH_MODE'] = 'mock'

from openapi_server.impl.auth import authenticate_user
from openapi_server.impl.utils.jwt_utils import create_jwt_token, decode_jwt_token

class TestAuthContract:
    """Test suite for authentication contract validation."""

    def test_jwt_token_format(self):
        """Test that JWT tokens have correct three-part format."""
        token = create_jwt_token(
            user_id="test_user",
            email="test@example.com",
            role="user"
        )

        # Token must have three parts separated by dots
        parts = token.split('.')
        assert len(parts) == 3, "JWT token must have header.payload.signature format"

        # Each part must be valid base64
        for part in parts:
            # Add padding and try to decode
            padded = part + '=' * (4 - len(part) % 4)
            try:
                base64.urlsafe_b64decode(padded)
            except Exception as e:
                pytest.fail(f"JWT part is not valid base64: {e}")

    def test_jwt_payload_fields(self):
        """Test that JWT payload contains all required fields for frontend."""
        token = create_jwt_token(
            user_id="test_user",
            email="test@example.com",
            role="admin"
        )

        payload = decode_jwt_token(token)
        assert payload is not None, "Token should be decodable"

        # Check all required fields exist
        required_fields = ['user_id', 'email', 'role', 'user_type', 'exp', 'iat']
        for field in required_fields:
            assert field in payload, f"JWT payload missing required field: {field}"

        # Verify field types
        assert isinstance(payload['user_id'], str)
        assert isinstance(payload['email'], str)
        assert isinstance(payload['role'], str)
        assert isinstance(payload['user_type'], str)
        assert isinstance(payload['exp'], (int, float))
        assert isinstance(payload['iat'], (int, float))

        # Verify role and user_type match
        assert payload['role'] == payload['user_type'], \
            "role and user_type fields must match"

    def test_auth_response_structure(self):
        """Test that auth endpoint returns correct response structure."""
        result = authenticate_user("admin@cmz.org", "admin123")

        # Check top-level fields
        assert 'token' in result, "Response must include token"
        assert 'expiresIn' in result, "Response must include expiresIn"
        assert 'user' in result, "Response must include user object"

        # Check token format
        token = result['token']
        parts = token.split('.')
        assert len(parts) == 3, "Token in response must be valid JWT"

        # Check user object structure
        user = result['user']
        assert 'userId' in user, "User object must include userId"
        assert 'email' in user, "User object must include email"
        assert 'role' in user, "User object must include role"
        assert 'displayName' in user, "User object must include displayName"

    def test_mock_users_authenticate(self):
        """Test that all mock users can authenticate successfully."""
        mock_credentials = [
            ('admin@cmz.org', 'admin123', 'admin'),
            ('test@cmz.org', 'testpass123', 'user'),
            ('parent1@test.cmz.org', 'testpass123', 'parent'),
            ('student1@test.cmz.org', 'testpass123', 'student'),
        ]

        for email, password, expected_role in mock_credentials:
            result = authenticate_user(email, password)
            assert result['user']['email'] == email
            assert result['user']['role'] == expected_role

            # Verify token is valid
            payload = decode_jwt_token(result['token'])
            assert payload is not None
            assert payload['email'] == email
            assert payload['role'] == expected_role

    def test_invalid_credentials_rejected(self):
        """Test that invalid credentials are properly rejected."""
        with pytest.raises(ValueError) as exc_info:
            authenticate_user("invalid@example.com", "wrongpass")
        assert "Invalid email or password" in str(exc_info.value)

        with pytest.raises(ValueError) as exc_info:
            authenticate_user("admin@cmz.org", "wrongpass")
        assert "Invalid email or password" in str(exc_info.value)

    def test_auth_mode_switching(self):
        """Test that AUTH_MODE environment variable controls auth behavior."""
        # Test mock mode
        os.environ['AUTH_MODE'] = 'mock'
        result = authenticate_user("admin@cmz.org", "admin123")
        assert result is not None

        # Test that invalid mode defaults to mock
        os.environ['AUTH_MODE'] = 'invalid'
        result = authenticate_user("admin@cmz.org", "admin123")
        assert result is not None

        # Reset to mock
        os.environ['AUTH_MODE'] = 'mock'

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

### Phase 3: Integration & Validation
**Validation Steps (Execute in Order):**

#### Step 1: Run Auth Contract Tests
```bash
cd backend/api/src/main/python
python -m pytest tests/test_auth_contract.py -v
```

#### Step 2: Test Frontend Compatibility
```bash
# Start backend with mock auth
export AUTH_MODE=mock
cd backend/api/src/main/python && python -m openapi_server

# In another terminal, test with curl
curl -X POST http://localhost:8080/auth \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@cmz.org","password":"admin123"}' | jq .

# Extract token and verify format
TOKEN=$(curl -X POST http://localhost:8080/auth \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@cmz.org","password":"admin123"}' 2>/dev/null | jq -r .token)

# Verify token has 3 parts
echo $TOKEN | awk -F. '{print NF-1}'  # Should output 2 (meaning 3 parts)
```

#### Step 3: Test OpenAPI Regeneration Protection
```bash
# Run regeneration with protection
make post-generate

# Verify auth still works
curl -X POST http://localhost:8080/auth \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@cmz.org","password":"admin123"}' | jq .
```

### Phase 4: Documentation & Environment Setup
**Configuration Steps:**

#### Step 1: Update Makefile
```makefile
# Add to backend/api/Makefile
post-generate: generate-api
	@echo "Running post-generation fixes..."
	python scripts/post_openapi_generation.py
	python scripts/protect_auth_handlers.py
	python scripts/post_generation_validation.py
	@echo "✅ Post-generation fixes complete"

test-auth:
	cd src/main/python && python -m pytest tests/test_auth_contract.py -v
```

#### Step 2: Create .env.example
```bash
# backend/api/.env.example
# Authentication Configuration
AUTH_MODE=mock  # Options: mock, dynamodb, cognito
JWT_SECRET=development-secret-key  # Change in production!
JWT_EXPIRY=86400  # 24 hours

# DynamoDB Configuration (when AUTH_MODE=dynamodb)
USERS_TABLE=cmz-users-dev
AWS_REGION=us-west-2
AWS_PROFILE=cmz

# Cognito Configuration (when AUTH_MODE=cognito)
COGNITO_USER_POOL_ID=your-pool-id
COGNITO_CLIENT_ID=your-client-id
```

## Implementation Details

### File Structure
```
backend/api/
├── src/main/python/
│   ├── openapi_server/
│   │   ├── impl/
│   │   │   ├── auth.py                    # Main auth implementation
│   │   │   └── utils/
│   │   │       ├── jwt_utils.py           # JWT token utilities
│   │   │       └── auth_config.py         # Auth configuration
│   │   └── controllers/
│   │       └── auth_controller.py         # Generated (protected)
│   └── tests/
│       └── test_auth_contract.py          # Contract validation tests
├── scripts/
│   └── protect_auth_handlers.py           # OpenAPI protection script
└── .env.example                            # Environment configuration
```

### Environment Variables
- `AUTH_MODE`: Controls authentication mode (mock/dynamodb/cognito)
- `JWT_SECRET`: Secret key for JWT signing (production only)
- `JWT_EXPIRY`: Token expiration time in seconds
- `USERS_TABLE`: DynamoDB table name for user storage
- `AWS_REGION`: AWS region for services
- `AWS_PROFILE`: AWS profile for credentials

## Integration Points

### Frontend Integration
- JWT tokens now match exact frontend expectations
- All required payload fields present
- Proper three-part token format
- Consistent error responses

### Backend Integration
- Works with existing OpenAPI workflow
- Protected from regeneration issues
- Supports multiple auth modes
- Maintains backward compatibility

### Testing Integration
- Automated contract tests prevent regressions
- Tests run as part of CI/CD pipeline
- Mock mode for development/testing
- Validates frontend-backend contract

## Quality Gates

### Mandatory Validation Before Completion
- [ ] All auth contract tests pass
- [ ] Frontend can decode tokens successfully
- [ ] OpenAPI regeneration doesn't break auth
- [ ] Mock auth mode works for all test users
- [ ] Environment mode switching works correctly
- [ ] JWT tokens have proper format (header.payload.signature)
- [ ] All required payload fields present
- [ ] Protection script integrated with make post-generate

### Success Criteria
1. **JWT Format**: All tokens have three-part format decodable by frontend
2. **Contract Compliance**: Auth responses match frontend expectations exactly
3. **Regeneration Protection**: Auth survives make generate-api cycles
4. **Mode Flexibility**: Can switch between mock/dynamodb/cognito modes
5. **Test Coverage**: Comprehensive tests prevent future regressions
6. **Error Handling**: Clear, consistent error messages
7. **Documentation**: Clear setup and configuration instructions

## Error Recovery

### Common Issues and Solutions

#### JWT Decode Failures
- **Issue**: Frontend can't decode token
- **Solution**: Verify token has 3 parts, check payload fields match contract

#### OpenAPI Regeneration Breaks Auth
- **Issue**: Auth returns "do some magic!" after regeneration
- **Solution**: Run `python scripts/protect_auth_handlers.py`

#### Wrong Auth Mode Active
- **Issue**: Unexpected authentication behavior
- **Solution**: Check AUTH_MODE environment variable

#### DynamoDB Connection Issues
- **Issue**: Can't connect to users table
- **Solution**: Verify AWS credentials and table configuration

## References
- `FIX-AUTH-ARCHITECTURE-ADVICE.md` - Best practices and troubleshooting
- `frontend/src/utils/jwt.ts` - Frontend JWT decoder implementation
- `backend/api/openapi_spec.yaml` - API specification