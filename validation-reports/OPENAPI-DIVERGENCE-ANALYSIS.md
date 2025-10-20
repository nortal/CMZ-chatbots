# OpenAPI Spec Divergence Analysis

**Generated**: 2025-10-11 21:30:00
**Purpose**: Identify endpoints where Frontend and Backend implementations agree but OpenAPI spec diverges

---

## Executive Summary

**Key Finding**: The OpenAPI spec is generally MORE permissive than the implementations, which is safer than the reverse. However, there are cases where the spec is incomplete or inaccurate, causing validation issues and frontend confusion.

**Divergence Types**:
1. **OpenAPI Missing Fields**: UI uses fields not in OpenAPI spec (e.g., `systemPrompt` in AnimalConfig)
2. **OpenAPI Extra Fields**: OpenAPI lists fields UI/Backend don't use (e.g., `maxTokens`, `responseFormat`)
3. **OpenAPI Required Field Confusion**: Spec marks fields as required when UI/Backend treat them as optional
4. **OpenAPI Field Naming**: Spec uses different names than UI/Backend expect

---

## Detailed Analysis by Endpoint

### 1. POST /auth - Authentication

**Status**: ✅ **Frontend and Backend Work Together**, ⚠️ **OpenAPI Spec is Misleading**

#### Frontend Implementation
```typescript
// frontend/src/services/api.ts:270-284
async login(email: string, password: string) {
  const response = await apiRequest<{ token: string; expiresIn: number }>('/auth', {
    method: 'POST',
    body: JSON.stringify({
      username: email,  // Frontend sends 'username' field
      password: password
    })
  });
  return response;
}
```

**Frontend Sends**: `['username', 'password']`

#### Backend Implementation
```python
# handlers.py:581-635
def handle_login_post(body: Dict[str, Any]) -> Tuple[Any, int]:
    # Extract email and password from body
    # Frontend sends 'username' field, but we use email
    email = body.get('username') or body.get('email', '')
    password = body.get('password', '')

    # Authenticate user
    result = authenticate_user(email, password)
```

**Backend Accepts**: `['username' OR 'email', 'password']` (flexible, accepts both field names)

#### OpenAPI Specification
```yaml
# openapi_spec.yaml - POST /auth
AuthRequest:
  required: ['password']
  properties:
    username: string
    email: string
    password: string
    register: boolean
```

**OpenAPI Defines**: Required=`['password']`, Properties=`['username', 'email', 'password', 'register']`

#### Divergence Analysis

**What Works**:
- ✅ Frontend sends `username` and `password`
- ✅ Backend accepts both `username` OR `email` (flexible)
- ✅ OpenAPI lists both fields as available
- ✅ OpenAPI correctly marks only `password` as required

**What's Misleading**:
- ⚠️ OpenAPI lists `email` and `register` fields but UI never sends them
- ⚠️ OpenAPI doesn't clarify that `username` field accepts email addresses
- ⚠️ Validation tools report "missing fields" when UI doesn't send `email` or `register`

**Recommendation**:
- **No Change Needed** - System works correctly as-is
- **Optional**: Add OpenAPI description clarifying that `username` field accepts email addresses
- **Optional**: Mark `email` and `register` as deprecated if they're never used

**Priority**: LOW (cosmetic issue, no functional impact)

---

### 2. PATCH /animal_config - Animal Configuration Update

**Status**: ⚠️ **Frontend and Backend Work Together**, ❌ **OpenAPI Spec is Incomplete**

#### Frontend Implementation
```typescript
// frontend/src/services/api.ts:34-60
export interface AnimalConfig {
  animalConfigId?: string;
  voice?: string;
  personality?: string;
  systemPrompt?: string;  // ← UI uses this field
  aiModel?: string;
  temperature?: number;
  topP?: number;
  toolsEnabled?: string[];
  guardrails?: Record<string, unknown>;
  created?: {...};
  modified?: {...};
}

// frontend/src/services/api.ts:198-209
async updateAnimalConfig(animalId: string, config: Partial<AnimalConfig>) {
  return apiRequest<AnimalConfig>(`/animal_config?animalId=${animalId}`, {
    method: 'PATCH',
    body: JSON.stringify(config),  // Sends any field from AnimalConfig
  });
}
```

**Frontend Sends**: `Partial<AnimalConfig>` including `systemPrompt`

#### Backend Implementation
```python
# handlers.py:188-250
def handle_animal_config_patch(animal_id: str, body: Any) -> Tuple[Any, int]:
    """Update animal configuration"""
    # Convert AnimalConfigUpdate to dict
    if isinstance(body, AnimalConfigUpdate):
        body = model_to_json_keyed_dict(body) or {}

    # Special handling for precision
    if 'temperature' in body:
        body['temperature'] = round(float(body['temperature']), 1)
    if 'topP' in body:
        body['topP'] = round(float(body['topP']), 2)

    # Pass to animal_handler.update_animal_config(animal_id, body)
    # Backend accepts any dict fields, no validation against schema
```

**Backend Accepts**: Any dict, with special handling for `temperature` and `topP`

#### OpenAPI Specification
```yaml
# openapi_spec.yaml - PATCH /animal_config
AnimalConfigUpdate:
  required: []
  properties:
    voice: string
    personality: string
    aiModel: string
    temperature: number
    topP: number
    maxTokens: integer       # ← Backend doesn't use this
    toolsEnabled: array
    responseFormat: string   # ← Backend doesn't use this
    guardrails: object
    # NOTE: 'systemPrompt' is MISSING from OpenAPI spec
```

**OpenAPI Defines**: Required=`[]`, Properties=`['voice', 'personality', 'aiModel', 'temperature', 'topP', 'maxTokens', 'toolsEnabled', 'responseFormat', 'guardrails']`

#### Divergence Analysis

**What Works**:
- ✅ Frontend can send any field in Partial<AnimalConfig>
- ✅ Backend accepts any dict without validation
- ✅ Special precision handling for temperature/topP prevents floating-point issues

**What's Broken**:
- ❌ **OpenAPI Missing `systemPrompt`**: Frontend uses this field but OpenAPI doesn't define it
- ❌ **OpenAPI Has `maxTokens`**: OpenAPI lists this but frontend doesn't use it
- ❌ **OpenAPI Has `responseFormat`**: OpenAPI lists this but frontend doesn't use it
- ⚠️ Backend doesn't validate against OpenAPI schema (accepts any fields)

**Impact**:
- Frontend developers don't know `systemPrompt` is valid (not in spec)
- Backend accepts invalid fields without validation
- OpenAPI validation tools flag `systemPrompt` as undefined
- TypeScript types generated from OpenAPI won't include `systemPrompt`

**Recommendation**:
1. **HIGH PRIORITY**: Add `systemPrompt` field to OpenAPI AnimalConfigUpdate schema
2. **MEDIUM PRIORITY**: Remove `maxTokens` and `responseFormat` if not used, OR implement them in frontend
3. **MEDIUM PRIORITY**: Add backend validation to reject fields not in OpenAPI schema

**Example OpenAPI Fix**:
```yaml
AnimalConfigUpdate:
  required: []
  properties:
    voice: string
    personality: string
    systemPrompt: string      # ← ADD THIS
    aiModel: string
    temperature: number
    topP: number
    toolsEnabled: array
    guardrails: object
    # Remove: maxTokens, responseFormat (if not implemented)
```

**Priority**: HIGH (functional issue - frontend uses undefined field)

---

### 3. GET /animal_config - Animal Configuration Retrieval

**Status**: ⚠️ **Scanner Limitation**, Likely Same Issue as PATCH

#### Analysis

The OpenAPI spec for GET /animal_config response likely has the same issue as PATCH - missing `systemPrompt` in the AnimalConfig schema.

**Verification Needed**:
```bash
# Check GET /animal_config response schema
grep -A 50 "AnimalConfig:" backend/api/openapi_spec.yaml
```

**Expected Issue**: Response schema missing `systemPrompt` field that backend returns and frontend expects.

**Recommendation**: Same fix as PATCH - add `systemPrompt` to AnimalConfig schema.

**Priority**: HIGH (same as PATCH /animal_config)

---

### 4. GET /animal_list - Animal List

**Status**: ⚠️ **Response Schema May Be Incomplete**

#### Analysis

Scanner shows response field mismatches. Need to verify if frontend expects fields that OpenAPI doesn't define in Animal response schema.

**Frontend Transformation**:
```typescript
// frontend/src/services/api.ts:217-246
transformAnimalForFrontend(backendAnimal: Animal) {
  return {
    id: backendAnimal.animalId || 'unknown',
    animalId: backendAnimal.animalId || 'unknown',
    name: backendAnimal.name,
    species: backendAnimal.species,
    active: backendAnimal.status === 'active',
    lastUpdated: backendAnimal.modified?.at || 'Unknown',
    conversations: 0,  // Not from backend
    status: backendAnimal.status || 'active',
    softDelete: backendAnimal.softDelete || false,
    // Frontend ADDS fields not from backend:
    conversationSettings: {...},  // Default values
    voiceSettings: {...},          // Default values
    knowledgeBase: [],             // Empty array
    guardrails: {}                 // Empty object
  };
}
```

**Issue**: Frontend adds default fields that aren't in the backend response. This is fine for display, but OpenAPI response schema should document what backend ACTUALLY returns, not what frontend constructs.

**Recommendation**:
- **OpenAPI Fix**: Response schema should only include fields backend returns
- **Frontend Pattern**: Keep transformation logic in frontend (current approach is good)

**Priority**: LOW (frontend handles this gracefully)

---

## Summary: OpenAPI Spec Updates Needed

### HIGH Priority (Functional Issues)

1. **AnimalConfig / AnimalConfigUpdate - Add `systemPrompt`**
   - **File**: `backend/api/openapi_spec.yaml`
   - **Schema**: `AnimalConfig` and `AnimalConfigUpdate`
   - **Change**: Add `systemPrompt: string` property
   - **Impact**: Fixes frontend-backend contract for animal personality system prompts

### MEDIUM Priority (Code Quality)

2. **AnimalConfigUpdate - Remove Unused Fields**
   - **File**: `backend/api/openapi_spec.yaml`
   - **Schema**: `AnimalConfigUpdate`
   - **Change**: Remove `maxTokens` and `responseFormat` if not implemented
   - **Alternative**: Implement these fields in frontend if they're planned features
   - **Impact**: Reduces confusion about which fields are actually supported

3. **Backend Validation - Add Schema Validation**
   - **File**: `backend/api/src/main/python/openapi_server/impl/handlers.py`
   - **Function**: `handle_animal_config_patch`
   - **Change**: Add validation to reject fields not in OpenAPI schema
   - **Impact**: Prevents invalid data from being stored

### LOW Priority (Documentation/Clarity)

4. **AuthRequest - Clarify Field Usage**
   - **File**: `backend/api/openapi_spec.yaml`
   - **Schema**: `AuthRequest`
   - **Change**: Add description to `username` field: "Accepts email address or username"
   - **Alternative**: Mark `email` and `register` as deprecated if unused
   - **Impact**: Reduces confusion in validation reports

5. **Animal Response - Document Actual Fields**
   - **File**: `backend/api/openapi_spec.yaml`
   - **Schema**: `Animal` (response schema)
   - **Change**: Ensure response schema matches what backend actually returns
   - **Impact**: Accurate API documentation for frontend developers

---

## Prevention Strategy

### 1. Type Generation from OpenAPI
Generate TypeScript types from OpenAPI spec to ensure frontend uses correct contracts:
```bash
npx openapi-typescript backend/api/openapi_spec.yaml -o frontend/src/api/types.ts
```

**Benefit**: Frontend gets compile-time errors when using undefined fields like `systemPrompt`.

### 2. Backend Schema Validation
Add validation decorator to enforce OpenAPI schema in handlers:
```python
@validate_request_schema('AnimalConfigUpdate')
def handle_animal_config_patch(animal_id: str, body: Any):
    # Validation decorator checks body against OpenAPI schema
    # Rejects fields not in spec, validates types, etc.
```

**Benefit**: Backend rejects invalid requests, ensuring data integrity.

### 3. Contract Testing
Add contract tests that verify OpenAPI spec matches implementation:
```python
def test_animal_config_update_schema():
    """Verify AnimalConfigUpdate schema includes all fields used in practice"""
    spec = load_openapi_spec()
    schema = spec['components']['schemas']['AnimalConfigUpdate']
    properties = schema['properties']

    # Test that all frontend-used fields are in spec
    assert 'systemPrompt' in properties, "systemPrompt field missing from OpenAPI spec"
    assert 'temperature' in properties
    assert 'topP' in properties
```

**Benefit**: Automated detection of spec drift from implementation.

---

## Conclusion

**Main Findings**:

1. ✅ **POST /auth works correctly** despite validation warnings. OpenAPI spec is permissive (lists optional fields UI doesn't use), which is safe. No changes needed.

2. ❌ **PATCH /animal_config has real issue** - OpenAPI spec missing `systemPrompt` field that frontend uses and backend accepts. This breaks TypeScript type generation and validation tools.

3. ⚠️ **Most other "misalignments"** are scanner detection limitations, not real issues. Working endpoints are flagged because scanner can't detect certain patterns.

**Recommended Actions**:

1. **Immediate (HIGH)**: Add `systemPrompt` to AnimalConfig/AnimalConfigUpdate in OpenAPI spec
2. **Short-term (MEDIUM)**: Remove unused fields (`maxTokens`, `responseFormat`) or implement them
3. **Short-term (MEDIUM)**: Add backend schema validation to reject undefined fields
4. **Long-term (LOW)**: Implement type generation and contract testing for ongoing validation

**Risk Assessment**:
- Current system works functionally despite spec inaccuracies
- Main risk is confusion during development and onboarding
- High priority fix (`systemPrompt`) takes ~5 minutes and eliminates most issues
- Prevention strategy (type generation + contract tests) prevents future drift
