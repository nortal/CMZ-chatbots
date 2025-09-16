# FIX-AUTH-ARCHITECTURE-ADVICE.md

## Best Practices and Implementation Guidance for Authentication Architecture Fix

### Overview
This document provides comprehensive guidance for implementing and maintaining the authentication architecture solution that addresses recurring JWT token issues, OpenAPI regeneration problems, and frontend-backend contract violations in the CMZ chatbot platform.

## Core Problem Summary

The authentication system has been experiencing persistent issues due to:
1. **JWT Token Format Mismatches**: Backend generating incompatible tokens for frontend
2. **OpenAPI Regeneration Breaking Points**: Generated code loses handler connections
3. **Environment Mode Confusion**: Unclear switching between mock/dynamodb/cognito
4. **Frontend-Backend Contract Violations**: Misaligned response structures
5. **No Regression Testing**: Issues reappear after code changes

## Implementation Strategy

### Phase 1: JWT Utility Module (PRIORITY: CRITICAL)

**Location**: `backend/api/src/main/python/openapi_server/impl/utils/jwt_utils.py`

**Key Implementation Points**:
- **ALWAYS** generate 3-part JWT tokens (header.payload.signature)
- **NEVER** use simple base64 encoding alone
- **ENSURE** all required fields are present in payload:
  - `user_id` or `userId` (frontend expects either)
  - `email`
  - `role` and `user_type`
  - `exp` (expiration timestamp)
  - `iat` (issued at timestamp)

**Common Pitfalls to Avoid**:
```python
# ❌ WRONG - Frontend will reject this
token = base64.b64encode(f"{email}:{timestamp}".encode()).decode()

# ✅ CORRECT - Proper JWT format
token = f"{header_encoded}.{payload_encoded}.{signature}"
```

### Phase 2: Environment Mode Configuration

**Location**: `backend/api/src/main/python/openapi_server/impl/auth_config.py`

**Environment Variable**: `AUTH_MODE`
- `mock` (default): Use hardcoded test users for development
- `dynamodb`: Use DynamoDB users table for staging
- `cognito`: Use AWS Cognito for production

**Critical Configuration**:
```python
# Always check environment on startup
AUTH_MODE = os.environ.get('AUTH_MODE', 'mock')
print(f"🔐 Auth Mode: {AUTH_MODE}")  # Visible confirmation

# Mode-specific initialization
if AUTH_MODE == 'mock':
    # No external dependencies
    pass
elif AUTH_MODE == 'dynamodb':
    # Verify table exists and is accessible
    verify_dynamodb_table()
elif AUTH_MODE == 'cognito':
    # Verify Cognito pool configuration
    verify_cognito_pool()
```

### Phase 3: OpenAPI Protection Strategy

**Problem**: OpenAPI Generator systematically breaks auth implementation:
- Removes `body` parameter from controller signatures
- Loses handler imports
- Resets implementations to "do some magic!"

**Solution Approach**:

1. **Custom Templates** (Recommended):
   ```bash
   # Use custom templates that preserve body parameters
   backend/api/templates/python-flask/controller.mustache
   ```

2. **Post-Generation Script** (Fallback):
   ```python
   # scripts/protect_auth_after_generation.py
   def fix_auth_controller():
       # Restore body parameter
       # Re-add handler imports
       # Preserve implementation
   ```

3. **Validation Script** (Always Run):
   ```bash
   # After ANY regeneration
   make post-generate  # This runs validation
   ```

### Phase 4: Contract Testing

**Location**: `backend/api/src/main/python/tests/test_auth_contract.py`

**Critical Test Cases**:
```python
def test_jwt_format():
    """JWT must have exactly 3 parts separated by dots"""
    response = login("test@cmz.org", "testpass123")
    token = response['token']
    assert len(token.split('.')) == 3

def test_jwt_payload_fields():
    """Payload must contain all required fields"""
    token = login_and_get_token()
    payload = decode_jwt_payload(token)
    required = ['user_id', 'email', 'role', 'exp', 'iat']
    for field in required:
        assert field in payload

def test_response_structure():
    """Response must match frontend expectations"""
    response = login("test@cmz.org", "testpass123")
    assert 'token' in response
    assert 'user' in response
    assert 'expiresIn' in response
```

## Troubleshooting Guide

### Issue: "Invalid email or password" with correct credentials

**Diagnosis Steps**:
1. Check AUTH_MODE environment variable
2. Verify mock users are loaded (if AUTH_MODE=mock)
3. Check JWT token format in browser DevTools
4. Verify backend is returning proper JWT structure

**Quick Fix**:
```bash
# Restart with explicit mock mode
export AUTH_MODE=mock
make stop-api && make run-api
```

### Issue: Frontend shows "Invalid token format"

**Root Cause**: Backend generating wrong token format

**Verification**:
```javascript
// Browser console
const token = localStorage.getItem('token');
console.log('Parts:', token.split('.').length);  // Must be 3
```

**Fix**:
```python
# Ensure jwt_utils.py is being used
from .utils.jwt_utils import generate_jwt_token
token = generate_jwt_token(user_data)  # NOT custom implementation
```

### Issue: OpenAPI regeneration breaks auth

**Prevention**:
```bash
# NEVER use standalone generate
❌ make generate-api

# ALWAYS use validated generation
✅ make post-generate
```

**Recovery**:
```bash
# If already broken
git diff backend/api/src/main/python/openapi_server/controllers/auth_controller.py
# Restore body parameter and handler import manually or:
python scripts/protect_auth_after_generation.py
```

## Testing Procedures

### Manual Testing Checklist

1. **Mock Mode Testing**:
   ```bash
   # Start in mock mode
   export AUTH_MODE=mock
   make run-api

   # Test each mock user
   curl -X POST http://localhost:8080/auth \
     -H "Content-Type: application/json" \
     -d '{"username":"admin@cmz.org","password":"admin123"}'
   ```

2. **Frontend Integration Testing**:
   ```javascript
   // Browser console
   fetch('http://localhost:8080/auth', {
     method: 'POST',
     headers: {'Content-Type': 'application/json'},
     body: JSON.stringify({
       username: 'test@cmz.org',
       password: 'testpass123'
     })
   }).then(r => r.json()).then(console.log)
   ```

3. **JWT Validation Testing**:
   ```python
   # Decode and verify token structure
   import base64
   import json

   token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
   parts = token.split('.')
   assert len(parts) == 3

   payload = json.loads(base64.urlsafe_b64decode(parts[1] + '=='))
   print(payload)  # Verify all fields present
   ```

### Automated Testing

```bash
# Run auth contract tests
pytest backend/api/src/main/python/tests/test_auth_contract.py -v

# Run integration tests
pytest backend/api/src/main/python/tests/integration/test_auth_integration.py -v

# Run Playwright E2E tests
cd backend/api/src/main/python/tests/playwright
FRONTEND_URL=http://localhost:3001 npx playwright test --grep "authentication"
```

## Integration Checklist

### Before Deployment

- [ ] JWT utility module implemented and tested
- [ ] Auth config module with environment switching
- [ ] auth.py updated to use new modules
- [ ] OpenAPI protection script in place
- [ ] Contract tests passing
- [ ] Manual testing completed for all auth modes
- [ ] Frontend successfully decoding tokens
- [ ] No regressions in existing functionality

### After OpenAPI Regeneration

- [ ] Run `make post-generate` (never standalone generate)
- [ ] Verify auth_controller.py has body parameter
- [ ] Verify handler imports are present
- [ ] Run auth contract tests
- [ ] Test login via curl
- [ ] Test login via frontend

## Common Mistakes to Avoid

1. **Forgetting to restart API after auth changes**
   ```bash
   # Always restart to load new auth implementation
   make stop-api && make run-api
   ```

2. **Using wrong token format in mock mode**
   ```python
   # ❌ WRONG
   return {"token": f"Bearer {token}"}  # Frontend adds Bearer

   # ✅ CORRECT
   return {"token": token}  # Raw token, no prefix
   ```

3. **Missing required fields in JWT payload**
   ```python
   # ❌ INCOMPLETE
   payload = {"email": email}

   # ✅ COMPLETE
   payload = {
       "user_id": user_id,
       "email": email,
       "role": role,
       "user_type": role,
       "exp": expiration,
       "iat": issued_at
   }
   ```

4. **Not handling different userId formats**
   ```python
   # Frontend accepts both formats
   payload["user_id"] = user_id  # Snake case
   payload["userId"] = user_id   # Camel case (redundant but safe)
   ```

## Performance Considerations

### Token Generation
- Mock JWT generation: < 5ms
- DynamoDB lookup + JWT: < 50ms
- Cognito validation + JWT: < 200ms

### Caching Strategy
```python
# Consider caching for frequently accessed users
from functools import lru_cache

@lru_cache(maxsize=100)
def get_user_from_dynamodb(email):
    # Cache user lookups for 5 minutes
    pass
```

## Security Notes

### Mock Mode Security
- **NEVER** use mock mode in production
- Mock signatures are not cryptographically secure
- Intended only for local development and testing

### Production Requirements
- Use proper JWT signing with RS256 or HS256
- Rotate signing keys regularly
- Implement token refresh mechanism
- Add rate limiting on auth endpoint
- Log all authentication attempts

## Monitoring and Alerts

### Key Metrics to Track
- Authentication success rate
- Average auth response time
- JWT validation failures
- Token expiration events
- Failed login attempts by user

### Logging Requirements
```python
import logging
logger = logging.getLogger(__name__)

def authenticate_user(email, password):
    logger.info(f"Auth attempt for: {email}")
    try:
        # Authentication logic
        logger.info(f"Auth success for: {email}")
    except Exception as e:
        logger.error(f"Auth failed for {email}: {str(e)}")
        raise
```

## Version History

### v1.0 (2025-01-16)
- Initial comprehensive auth architecture fix
- JWT utility module implementation
- Environment mode configuration
- OpenAPI protection strategy
- Contract testing framework

## Related Documentation

- `.claude/commands/fix-auth-architecture.md` - Main implementation prompt
- `backend/api/src/main/python/openapi_server/impl/utils/jwt_utils.py` - JWT utilities
- `backend/api/src/main/python/openapi_server/impl/auth_config.py` - Auth configuration
- `backend/api/src/main/python/tests/test_auth_contract.py` - Contract tests
- `CLAUDE.md` - Project documentation with auth architecture reference