# CMZ Codebase Implementation Status

**Last Updated**: 2025-10-02
**Purpose**: Prevent re-implementation of existing functionality

## ✅ FULLY IMPLEMENTED & TESTED

### Authentication (`/auth/*`)
- **Location**: `impl/auth.py`, `impl/auth_mock.py`, `impl/utils/jwt_utils.py`
- **Storage**: Mock users in memory + JWT tokens
- **Endpoints Working**:
  - POST /auth - Login ✅
  - POST /auth/logout - Logout ✅
  - POST /auth/refresh - Token refresh ✅
- **Not Implemented**:
  - POST /auth/reset-password ❌ (returns 404)

### UI Endpoints (`/`, `/admin`)
- **Location**: `impl/ui.py`, `impl/system.py`
- **Endpoints Working**:
  - GET / - Homepage ✅
  - GET /admin - Admin dashboard ✅

## 🔧 IMPLEMENTED WITH DYNAMODB

### Family Management (`/family/*`)
- **Location**: `impl/family.py`, `impl/family_bidirectional.py`
- **DynamoDB Models**: `impl/utils/orm/models/family_bidirectional.py`
- **Table**: `quest-dev-family`
- **Features**:
  - Bidirectional user-family relationships
  - Soft delete support
  - Audit trail (created/modified)
- **Routing Issues**: Endpoints return 404 despite implementation existing

### User Management
- **Location**: `impl/utils/orm/models/user_bidirectional.py`
- **DynamoDB Models**: Complete PynamoDB implementation
- **Features**: Role-based access, family relationships

### Animals
- **Location**: `impl/animals.py`
- **DynamoDB**: Uses `impl/utils/dynamo.py` utilities
- **Current Issue**: Controller import errors (handle_exception_for_controllers)

## ⚠️ PARTIAL IMPLEMENTATION

### Conversations
- Handler stubs exist in `impl/handlers.py`
- No DynamoDB implementation yet
- All endpoints return 404

### Knowledge Base
- Models defined
- No implementation

## ❌ NOT IMPLEMENTED

- System endpoints (health, status)
- Analytics
- Media management
- Most conversation endpoints

## 🔍 DISCOVERY COMMANDS

Before implementing ANY feature, run these commands:

```bash
# 1. Check if implementation exists
grep -r "def handle_[operation_name]" backend/api/src/main/python/openapi_server/impl/

# 2. Check DynamoDB models
ls backend/api/src/main/python/openapi_server/impl/utils/orm/models/

# 3. Check handler mappings
grep "[operation_name]" backend/api/src/main/python/openapi_server/impl/handlers.py

# 4. Test endpoint first
curl -X [METHOD] http://localhost:8080/[endpoint]

# 5. Check for existing mocks
grep -r "mock.*[feature]" backend/api/src/main/python/openapi_server/impl/

# 6. Check git history
git log --oneline --grep="[feature]" | head -20
```

## 🚨 COMMON PITFALLS

1. **Re-implementing DynamoDB integrations**: Always check `impl/utils/orm/models/` first
2. **Creating mocks when DynamoDB exists**: Family, User, Animal all have DynamoDB
3. **Missing handler mappings**: Check handler_map in handlers.py
4. **Import errors in controllers**: Usually means function exists but import path wrong
5. **404 errors**: Usually routing/OpenAPI spec mismatch, not missing implementation

## 📋 PRE-IMPLEMENTATION CHECKLIST

- [ ] Ran discovery commands above
- [ ] Checked DynamoDB models directory
- [ ] Tested endpoint with curl
- [ ] Checked handlers.py for existing mapping
- [ ] Reviewed git history for context
- [ ] Checked for _bidirectional.py versions
- [ ] Verified OpenAPI spec matches implementation

## 🔧 FIXING COMMON ISSUES

### "not_implemented" but code exists
1. Check handler_map in handlers.py
2. Verify function name matches pattern
3. Check import statements

### 404 errors on implemented endpoints
1. Check OpenAPI spec path definitions
2. Verify controller routing
3. Check URL patterns in test vs implementation

### Import errors in controllers
1. Function exists in different module
2. Check error_handler.py imports
3. Verify __init__.py exports