# Test Plan: Renaming `id` to `animalId`

## Overview
This test plan validates that renaming the generic `id` parameter to `animalId` in the OpenAPI spec resolves the Connexion `id_` issue and doesn't break any functionality.

## Test Objectives
1. Verify the `id_` parameter issue is resolved
2. Ensure all animal CRUD operations work correctly
3. Validate frontend-backend integration remains functional
4. Confirm no regressions in other endpoints

## Test Phases

### Phase 1: Pre-Change Validation (Baseline)
**Purpose**: Document current issues with `id` parameter

#### Test Cases:
| Test ID | Endpoint | Method | Expected | Actual | Status |
|---------|----------|--------|----------|--------|--------|
| T1.1 | `/animal/{id}` | GET | 200 | 500 (id_ error) | ❌ FAIL |
| T1.2 | `/animal/{id}` | PUT | 200 | 500 (id_ error) | ❌ FAIL |
| T1.3 | `/animal/{id}` | DELETE | 200/405 | 500 (id_ error) | ❌ FAIL |

**Known Issue**: `TypeError: animal_id_get() got an unexpected keyword argument 'id_'`

### Phase 2: Implementation Steps
1. **Update OpenAPI Spec**
   ```yaml
   # Change all occurrences of:
   /animal/{id}:
   # To:
   /animal/{animalId}:
   ```

2. **Regenerate API**
   ```bash
   make post-generate
   make build-api
   make run-api
   ```

3. **Update Frontend** (if needed)
   - Search for `/animal/${id}` or `/animal/{id}`
   - Replace with `/animal/${animalId}`

### Phase 3: Post-Change Validation

#### API Tests
```bash
# Test 1: GET Animal by ID
curl -X GET "http://localhost:8080/animal/maya-test-2025"
# Expected: 200 OK with animal data
# Success Criteria: No id_ error

# Test 2: PUT Update Animal
curl -X PUT "http://localhost:8080/animal/maya-test-2025" \
  -H "Content-Type: application/json" \
  -d '{
    "animalId": "maya-test-2025",
    "animalName": "Maya Updated",
    "scientificName": "Updated Species"
  }'
# Expected: 200 OK
# Success Criteria: Update successful, no id_ error

# Test 3: DELETE Animal
curl -X DELETE "http://localhost:8080/animal/maya-test-2025"
# Expected: 200 OK or 405 Method Not Allowed
# Success Criteria: No id_ error

# Test 4: List Animals
curl -X GET "http://localhost:8080/animals"
# Expected: 200 OK with array of animals
# Success Criteria: List returns correctly
```

#### Frontend Integration Tests (Playwright)
```javascript
// Test 1: View Animal Details
await page.goto('http://localhost:3000/animals');
await page.click('button:has-text("View Details")');
// Verify: No console errors, animal details load

// Test 2: Edit Animal (if available)
await page.click('button:has-text("Edit")');
await page.fill('input[name="animalName"]', 'Updated Name');
await page.click('button:has-text("Save")');
// Verify: Save successful, no API errors

// Test 3: Animal Config Dialog
await page.click('button:has-text("Configure")');
// Verify: Dialog opens, data loads correctly
```

### Phase 4: Regression Testing

#### Other Endpoints (Should Not Be Affected)
| Endpoint | Method | Expected | Test Command |
|----------|--------|----------|--------------|
| `/family/{familyId}` | GET | 200 | `curl -X GET http://localhost:8080/family/test-family-1` |
| `/user/{userId}` | GET | 200 | `curl -X GET http://localhost:8080/user/user-123` |
| `/conversations/sessions` | GET | 200 | `curl -X GET http://localhost:8080/conversations/sessions` |
| `/auth` | POST | 200 | `curl -X POST http://localhost:8080/auth -d '{"username":"test@cmz.org","password":"testpass123"}'` |

### Phase 5: Controller Validation

#### Check Generated Controller
```bash
# Verify parameter name is correct
grep -A 10 "def animal_animal_id_get" backend/api/src/main/python/openapi_server/controllers/animal_controller.py

# Should see:
# def animal_animal_id_get(animal_id):  # NOT id_ or id
```

#### Check Implementation Handler
```bash
# Verify handler receives correct parameter
grep -A 5 "def handle_animal.*get" backend/api/src/main/python/openapi_server/impl/animals.py

# Should receive animal_id directly, no conversion needed
```

## Success Criteria

### Must Pass (Critical)
- [ ] No more `id_` errors in animal endpoints
- [ ] GET /animal/{animalId} returns 200
- [ ] PUT /animal/{animalId} returns 200
- [ ] Frontend can view animal details
- [ ] No regression in other endpoints

### Should Pass (Important)
- [ ] DELETE /animal/{animalId} works (200 or 405)
- [ ] Frontend can edit animals
- [ ] Swagger UI shows animalId parameter
- [ ] No TypeScript errors in frontend

### Nice to Have
- [ ] Consistent naming across all endpoints
- [ ] Updated API documentation
- [ ] Test coverage for new parameter name

## Test Execution Checklist

### Before Change
- [x] Document current errors
- [x] Save error logs for comparison
- [x] Note failing test cases

### During Change
- [ ] Update OpenAPI spec
- [ ] Run `make post-generate`
- [ ] Check for generation errors
- [ ] Build and deploy

### After Change
- [ ] Run API test suite
- [ ] Run frontend integration tests
- [ ] Check for console errors
- [ ] Verify no regressions
- [ ] Document improvements

## Risk Assessment

### Low Risk
- Change is isolated to animal endpoints
- Other endpoints already use specific IDs
- Frontend changes are find/replace

### Mitigation
- Keep backup of current working state
- Test thoroughly before committing
- Can revert if issues arise

## Rollback Plan
If issues occur:
1. `git stash` or `git reset --hard HEAD`
2. Rebuild with original spec
3. Document any unexpected issues

## Expected Outcome
After renaming `id` to `animalId`:
- ✅ No more Connexion `id_` parameter issues
- ✅ Clearer, self-documenting API
- ✅ Consistent parameter naming
- ✅ Reduced maintenance burden