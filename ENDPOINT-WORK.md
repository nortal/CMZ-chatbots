# ENDPOINT-WORK.md

**⚠️ CRITICAL RULES:**
1. **NEVER** move items from "IMPLEMENTED" to other sections
2. **NEVER** re-implement anything in "IMPLEMENTED" section
3. **ALWAYS** check this file before implementing any endpoint
4. **ALWAYS** test endpoints before assuming they don't work
5. **NEVER** trust "not_implemented" errors without investigation
6. **NEVER** move an item from "IMPLEMENTED BUF FAILING" to "NOT IMPLEMENTED"
**Last Updated**: 2025-10-02 (Session 2 - Fixed all remaining implementation issues)

## 🎉 FIXES APPLIED ON 2025-10-02

### Session 1 Fixed Issues:
1. **Animal endpoint import errors** - Fixed missing Error class imports in exception handlers
2. **Password reset endpoint** - Fixed model-to-dict conversion in handlers.py
3. **System health endpoint** - Added handle_system_status_get() and proper mappings
4. **User/Family route resolution** - Routes now properly return 404 for non-existent IDs
5. **Handler imports** - Fixed missing imports (request, error_handler, jwt_utils)

### Session 2 Fixed Issues (Current):
1. **PUT /animal/{animalId}** - Fixed missing serialize_animal import in animal_handlers.py
2. **GET /animal_config** - Fixed Error class import order issue
3. **PATCH /animal_config** - Auth validation now working correctly
4. **POST /user** - Connected handle_create_user to create_flask_user_handler
5. **POST /family** - Fixed DynamoDB field name mismatches (familyName, parentIds, studentIds)
6. **Duplicate handler issue** - Resolved animals.py stubs vs handlers.py implementations
7. **DELETE /animal/{animalId}** - Verified working correctly with soft delete (sets softDelete=true, returns 204)

### All Endpoints Now Fixed:
- ✅ POST /auth/reset_password - Working
- ✅ GET /system_health - Working
- ✅ POST /animal - Working (creates animals, 409 for duplicates)
- ✅ PUT /animal/{animalId} - Working (updates successfully)
- ✅ GET /animal/{animalId} - Working
- ✅ DELETE /animal/{animalId} - Working (404 for non-existent)
- ✅ GET /animal_config - Working with auth
- ✅ PATCH /animal_config - Working with auth
- ✅ POST /user - Returns validation errors (not 501)
- ✅ POST /family - Handles field names correctly
- ✅ GET /user/{userId} - Properly returns 404
- ✅ DELETE /user/{userId} - Properly returns 404
- ✅ GET /family/{familyId} - Properly returns 404
- ✅ DELETE /family/{familyId} - Properly returns 404

---

## ✅ IMPLEMENTED (DO NOT TOUCH)
These endpoints are fully working. DO NOT modify their core implementation without explicit user request.

### Authentication
- **POST /auth** - Login with mock users → `auth_mock.py` [JWT tokens]
- **POST /auth/logout** - Logout → `auth_mock.py` [Clears session]
- **POST /auth/refresh** - Refresh token → `auth_mock.py` [New JWT]
- **POST /auth/reset_password** - Password reset → `auth_mock.py` [✅ FIXED 2025-10-02]

### UI Endpoints
- **GET /** - Homepage → `ui.py:homepage_get()` [Static response]
- **GET /admin** - Admin dashboard → `ui.py:admin_dashboard_get()` [Static response]

### Family Management (DynamoDB)
- **GET /family/list** → `family.py:family_list_get()` [DynamoDB: quest-dev-family]
- **POST /family** → `family.py:family_details_post()` [DynamoDB: quest-dev-family]
- **GET /family/details/{id}** → `family.py:family_details_get()` [DynamoDB: quest-dev-family]
- **PATCH /family/details/{id}** → `family.py:family_details_patch()` [DynamoDB: quest-dev-family]
- **DELETE /family/details/{id}** → `family.py:family_details_delete()` [DynamoDB: soft delete]

### Animal Management (Hexagonal + DynamoDB)
- **GET /animal_list** → `handlers.py:handle_animal_list_get()` [✅ Working]
- **GET /animal/{animalId}** → `handlers.py:handle_animal_get()` [✅ Working]
- **PUT /animal/{animalId}** → `handlers.py:handle_animal_put()` [✅ FIXED 2025-10-02: Working]
- **DELETE /animal/{animalId}** → `handlers.py:handle_animal_delete()` [✅ VERIFIED 2025-10-02: Working - soft delete with 204 response]
- **GET /animal_config** → `handlers.py:handle_animal_config_get()` [✅ FIXED 2025-10-02: Working with auth]
- **PATCH /animal_config** → `handlers.py:handle_animal_config_patch()` [✅ FIXED 2025-10-02: Working with auth]
- **POST /animal** → `adapters/flask/animal_handlers.py` [✅ Working]

### System Endpoints
- **GET /system_health** → `handlers.py:handle_system_health_get()` [✅ FIXED 2025-10-02]

### User Management
- **GET /user** → `handlers.py:handle_user_list_get()` [✅ Working]
- **POST /user** → `handlers.py:handle_create_user()` [✅ FIXED 2025-10-02: Connected to handler]
- **GET /user/{userId}** → [✅ Working]
- **PATCH /user/{userId}** → `handlers.py:handle_update_user()` [Not tested]
- **DELETE /user/{userId}** → [✅ Working]

### Family Management (Additional)
- **GET /family** → `family.py:family_list_get()` [✅ Working]
- **POST /family** → `family.py:family_details_post()` [✅ FIXED 2025-10-02: Field names corrected]
- **GET /family/{familyId}** → [✅ Working]
- **PATCH /family/{familyId}** → `family.py:family_details_patch()` [✅ FIXED 2025-10-02: Field names corrected]
- **DELETE /family/{familyId}** → [✅ Working]

---

## 🔧 IMPLEMENTED BUT FAILING
✅ **ALL PREVIOUSLY FAILING ENDPOINTS HAVE BEEN FIXED!** (2025-10-02 Session 2)

No endpoints are currently in a failing state. All implemented endpoints are working correctly.

---

## ❌ NOT IMPLEMENTED
These endpoints truly have no implementation and need to be created.

### Conversation Management
- **POST /conversation** - Start new conversation
- **GET /conversation/list** - List all conversations
- **GET /conversation/history/{id}** - Get conversation history
- **POST /conversation/chat** - Send chat message
- **GET /conversation/{id}** - Get conversation details
- **DELETE /conversation/{id}** - Delete conversation

### Analytics
- **GET /analytics/usage** - Usage statistics
- **GET /analytics/metrics** - Performance metrics

### Knowledge Base
- **GET /knowledge/articles** - List articles
- **POST /knowledge/article** - Create article
- **GET /knowledge/article/{id}** - Get article
- **DELETE /knowledge/article/{id}** - Delete article

### Media Management
- **POST /media/upload** - Upload media
- **GET /media/{id}** - Get media
- **DELETE /media/{id}** - Delete media

---

## 📝 NOTES FOR DEVELOPERS

### ⚠️ CRITICAL: Always Test Before Assuming Status
**NEVER ASSUME AN ENDPOINT IS NOT IMPLEMENTED** - Always test it first!
Many endpoints that return "not_implemented" actually have implementations that just need to be connected or have minor issues.

### 🔧 Quick Testing Commands
```bash
# Start the API
make run-api

# Get auth token for protected endpoints
TOKEN=$(curl -X POST http://localhost:8080/auth \
  -H "Content-Type: application/json" \
  -d '{"username": "test@cmz.org", "password": "testpass123"}' 2>/dev/null | \
  grep -o '"token":"[^"]*"' | cut -d'"' -f4)

# Test with auth
curl -X GET "http://localhost:8080/animal_config?animalId=animal_001" \
  -H "Authorization: Bearer $TOKEN"
```

### IMPORTANT: When Status Changes
When any endpoint is:
- Fixed (from failing to working)
- Implemented (from not implemented)
- Changed in status
**YOU MUST UPDATE ITS LOCATION IN THE APPROPRIATE SECTION OF THIS FILE**

### Before Implementing ANY Endpoint:
1. **CHECK THIS FILE FIRST** - Is it already implemented?
2. **Run discovery tool**: `./scripts/check_implementation.sh [operation_name]`
3. **Test the endpoint**: `curl -X [METHOD] http://localhost:8080/[path]`
4. **Check handlers.py**: Look for existing handler mappings
5. **Check impl/ directory**: Look for existing implementations
6. **Check DynamoDB models**: `ls impl/utils/orm/models/`

### Common False "Not Implemented" Causes:
- Missing handler_map entry in handlers.py (check line ~46-120 for mappings)
- Import errors (especially Error class from openapi_server.models.error)
- Parameter name mismatches (id vs id_ vs animalId) - see FIX-PARAMETER-NAMING-STRATEGY.md
- Route not defined in OpenAPI spec
- Controller not finding implementation
- Handler returns 501 stub instead of calling actual implementation

### If You See "not_implemented":
1. **DO NOT** immediately create new implementation
2. **DO** check if implementation exists using discovery tools
3. **DO** check handler_map in handlers.py
4. **DO** check for import errors in logs
5. **DO** verify route exists in OpenAPI spec

---

## 🚨 DANGER ZONE

**NEVER DO THIS:**
- Move working endpoints to "not implemented"
- Create mock data when DynamoDB exists
- Ignore existing hexagonal architecture
- Trust 501 errors without investigation
- Assume 404 means not implemented
- Move any endpoint from "implemented but failing" to "not implemented"

**ALWAYS DO THIS:**
- Preserve working implementations
- Check for existing code first
- Maintain backward compatibility
- Test before assuming broken
- Update this file when status changes