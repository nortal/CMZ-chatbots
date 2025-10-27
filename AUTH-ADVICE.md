# Authentication Architecture & Troubleshooting Guide

## Overview

The CMZ authentication system uses mock JWT tokens for development with support for multiple authentication backends (mock, DynamoDB, Cognito). Authentication failures are a recurring issue after OpenAPI code regeneration.

## Architecture

### Core Components

1. **Controller Layer**: `openapi_server/controllers/auth_controller.py` (GENERATED - changes lost on regeneration)
2. **Routing Layer**: `openapi_server/impl/auth.py` (CRITICAL - must contain `handle_()` function)
3. **Handler Layer**: `openapi_server/impl/handlers.py` (contains `handle_login_post`, `handle_auth_post`, etc.)
4. **Service Layer**: `openapi_server/impl/auth_mock.py` (contains `authenticate_user()` function)

### Request Flow

```
POST /auth
    ↓
auth_controller.py::auth_post()
    ↓ tries to import impl.auth.handle_
    ↓
impl/auth.py::handle_()  ← CRITICAL: This function MUST exist
    ↓
impl/handlers.py::handle_login_post()
    ↓
impl/auth_mock.py::authenticate_user()
    ↓
Returns JWT token
```

## Common Problem: Authentication Breaks After OpenAPI Regeneration

### Symptoms
- `POST /auth` returns 401 "Invalid email or password"
- OR returns 501 "Handler for handle_ not implemented"
- Authentication was working before running `make generate-api`

### Root Cause
When `make generate-api` regenerates `auth_controller.py`, it creates code that tries to import `handle_()` from `impl.auth`. If this function doesn't exist in `impl/auth.py`, authentication fails.

### The Fix

**File**: `openapi_server/impl/auth.py`

This file MUST contain a `handle_()` function that routes to the appropriate handler:

```python
def handle_(*args, **kwargs) -> Tuple[Any, int]:
    """
    Passthrough to handle_auth_post since auth controller calls handle_() by default.
    The auth_post controller function will call this when impl.auth.handle_ exists.
    """
    # The only endpoint using handle_() in auth controller is auth_post (login)
    # So we route it to the login handler
    return handlers.handle_login_post(*args, **kwargs)
```

**Why This Works**:
- The generated `auth_controller.py` tries to import `handle_` from `impl.auth` (line 111-112)
- If found, it calls `impl.auth.handle_()` with the request body
- Our `handle_()` function routes to `handlers.handle_login_post()`
- Which calls `auth_mock.authenticate_user()` to validate credentials

## Test Users

The mock authentication system has these test users:

```python
'test@cmz.org': {'password': 'testpass123', 'role': 'admin', 'name': 'Test User'}
'parent1@test.cmz.org': {'password': 'testpass123', 'role': 'parent', 'name': 'Test Parent One'}
'student1@test.cmz.org': {'password': 'testpass123', 'role': 'student', 'name': 'Test Student One'}
'student2@test.cmz.org': {'password': 'testpass123', 'role': 'student', 'name': 'Test Student Two'}
'user_parent_001@cmz.org': {'password': 'testpass123', 'role': 'parent', 'name': 'Test Parent'}
```

## Testing Authentication

### Quick Test
```bash
curl -X POST "http://localhost:8080/auth" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@cmz.org", "password": "testpass123"}'
```

Expected response (200):
```json
{
  "token": "eyJhbGciOiAiSFMyNTYi...",
  "user": {
    "email": "test@cmz.org",
    "role": "admin",
    "name": "Test User"
  },
  "expiresIn": 86400
}
```

### Testing Authenticated Endpoints
```bash
# Get token
TOKEN=$(curl -s -X POST "http://localhost:8080/auth" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@cmz.org", "password": "testpass123"}' | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['token'])")

# Use token
curl -X GET "http://localhost:8080/animal_list" \
  -H "Authorization: Bearer $TOKEN"
```

## Troubleshooting Steps

### Step 1: Verify auth.py has handle_() function

```bash
grep -n "def handle_" openapi_server/impl/auth.py
```

Expected output should include:
```
12:def handle_(*args, **kwargs) -> Tuple[Any, int]:
```

If missing, add the function shown in "The Fix" section above.

### Step 2: Check handler routing

Verify `handle_login_post` exists in handlers.py:
```bash
grep -n "def handle_login_post" openapi_server/impl/handlers.py
```

### Step 3: Verify authenticate_user function exists

```bash
grep -n "def authenticate_user" openapi_server/impl/auth_mock.py
```

### Step 4: Test authentication directly

```bash
python3 -c "
from openapi_server.impl.auth_mock import authenticate_user
result = authenticate_user('test@cmz.org', 'testpass123')
print('Success!' if result else 'Failed!')
print(result)
"
```

### Step 5: Check for import errors

Start Python and manually test imports:
```python
from openapi_server.impl import auth
print(hasattr(auth, 'handle_'))  # Should print: True

from openapi_server.impl import handlers
print(hasattr(handlers, 'handle_login_post'))  # Should print: True

from openapi_server.impl.auth_mock import authenticate_user
print(authenticate_user('test@cmz.org', 'testpass123'))  # Should return dict with token
```

## Post-Generation Validation

After running `make generate-api`, ALWAYS verify auth still works:

```bash
# Regenerate API
make generate-api

# Restart backend
make run-api

# Test auth (in another terminal)
curl -X POST "http://localhost:8080/auth" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@cmz.org", "password": "testpass123"}'
```

If authentication fails, apply the fix from "The Fix" section and restart.

## Prevention

### Option 1: Add to post-generation validation script

Add auth verification to `scripts/post_generation_validation.py`:

```python
def validate_auth_routing():
    """Ensure impl/auth.py has handle_() function"""
    auth_file = "openapi_server/impl/auth.py"
    with open(auth_file, 'r') as f:
        content = f.read()

    if 'def handle_(' not in content:
        print("❌ ERROR: impl/auth.py missing handle_() function")
        print("   Authentication will be broken!")
        return False

    print("✅ Auth routing validated")
    return True
```

### Option 2: Add to Makefile generate-api target

```makefile
generate-api:
    # ... existing generation steps ...
    @echo "Validating authentication routing..."
    @grep -q "def handle_" openapi_server/impl/auth.py || \
        (echo "❌ WARNING: Auth routing broken! Run: make fix-auth" && exit 1)
```

## Related Files

- `openapi_server/impl/auth.py` - Auth routing layer (CRITICAL - maintain handle_() function)
- `openapi_server/impl/handlers.py` - Handler implementations
- `openapi_server/impl/auth_mock.py` - Mock authentication service
- `openapi_server/impl/domain/auth_service.py` - Production auth service (Cognito)
- `openapi_server/controllers/auth_controller.py` - Generated controller (REGENERATED - changes lost)
- `openapi_server/impl/utils/jwt_utils.py` - JWT token utilities

## Authentication Modes

The system supports multiple authentication backends via environment variable:

```bash
# Mock authentication (default for development)
AUTH_MODE=mock

# DynamoDB-based authentication
AUTH_MODE=dynamodb

# AWS Cognito authentication
AUTH_MODE=cognito
```

## Common Errors & Solutions

### Error: "Invalid email or password" (but credentials are correct)

**Cause**: `authenticate_user()` is returning None
**Solution**: Check that test user exists in MOCK_USERS dict in auth_mock.py

### Error: "Handler for handle_ not implemented"

**Cause**: `impl/auth.py` missing `handle_()` function
**Solution**: Add the function shown in "The Fix" section

### Error: "cannot import name 'authenticate_user'"

**Cause**: Import path issue or function doesn't exist
**Solution**:
```bash
# Check function exists
grep "def authenticate_user" openapi_server/impl/auth_mock.py

# Test import
python3 -c "from openapi_server.impl.auth_mock import authenticate_user"
```

### Error: Python module caching prevents code changes

**Cause**: Python caches .pyc files
**Solution**:
```bash
# Clear cache
find . -name "*.pyc" -delete
find . -type d -name "__pycache__" -exec rm -rf {} +

# Restart with no bytecode
PYTHONDONTWRITEBYTECODE=1 python -m openapi_server
```

## JWT Token Format

Mock tokens have this structure:
```
header.payload.signature
```

Example payload:
```json
{
  "email": "test@cmz.org",
  "role": "admin",
  "exp": 1759999999,
  "iat": 1759806638,
  "sub": "test@cmz.org"
}
```

Tokens are base64-encoded but NOT cryptographically secure (mock only).

## Security Notes

⚠️ **IMPORTANT**: The mock authentication system is for development only:
- No password hashing
- Weak JWT signatures
- Hard-coded credentials
- No rate limiting

For production, use `AUTH_MODE=cognito` with proper AWS Cognito configuration.
