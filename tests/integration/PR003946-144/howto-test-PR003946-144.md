# How to Test PR003946-144: PUT /animal/{id} Endpoint

## Test Setup

### Prerequisites
1. Backend API running on port 8080
2. DynamoDB accessible (local or AWS)
3. Test data seeded in database
4. Authentication configured

### Test Data
```python
# Test animal for updates
test_animal = {
    "id": "test-lion-001",
    "name": "Leo",
    "species": "Lion",
    "status": "active",
    "version": 1,
    "created": {"at": "2025-01-15T09:00:00Z"},
    "modified": {"at": "2025-01-15T09:00:00Z"}
}
```

## Manual Testing with cURL

### 1. Full Update (All Fields)
```bash
curl -X PUT http://localhost:8080/animal/test-lion-001 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "id": "test-lion-001",
    "name": "Leo the Lion King",
    "species": "Lion",
    "status": "active",
    "description": "The mighty king of the savanna",
    "age": 5,
    "version": 1
  }'

# Expected: 200 OK with updated animal object
```

### 2. Partial Update (Only Changed Fields)
```bash
curl -X PUT http://localhost:8080/animal/test-lion-001 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "id": "test-lion-001",
    "name": "Leo the Brave",
    "version": 1
  }'

# Expected: 200 OK with updated name, other fields unchanged
```

### 3. ID Mismatch Error
```bash
curl -X PUT http://localhost:8080/animal/test-lion-001 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "id": "different-id",
    "name": "Leo",
    "species": "Lion",
    "status": "active"
  }'

# Expected: 400 Bad Request
# {
#   "code": "id_mismatch",
#   "message": "Animal ID in URL does not match ID in request body"
# }
```

### 4. Not Found Error
```bash
curl -X PUT http://localhost:8080/animal/non-existent-id \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "id": "non-existent-id",
    "name": "Ghost Animal",
    "species": "Unknown",
    "status": "active"
  }'

# Expected: 404 Not Found
# {
#   "code": "not_found",
#   "message": "Animal not found",
#   "details": {"id": "non-existent-id"}
# }
```

### 5. Validation Error
```bash
curl -X PUT http://localhost:8080/animal/test-lion-001 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "id": "test-lion-001",
    "name": "L",
    "species": "InvalidSpecies",
    "status": "invalid_status"
  }'

# Expected: 400 Bad Request
# {
#   "code": "validation_error",
#   "message": "Validation failed",
#   "details": {
#     "name": "Name too short: minimum 2 characters",
#     "species": "Invalid species",
#     "status": "Invalid status: must be active, inactive, or archived"
#   }
# }
```

### 6. Version Conflict
```bash
# First, get current version
curl -X GET http://localhost:8080/animal/test-lion-001

# Try to update with old version
curl -X PUT http://localhost:8080/animal/test-lion-001 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "id": "test-lion-001",
    "name": "Leo Updated",
    "species": "Lion",
    "status": "active",
    "version": 0
  }'

# Expected: 409 Conflict
# {
#   "code": "version_conflict",
#   "message": "Version conflict: resource has been modified",
#   "details": {"current_version": 2, "provided_version": 0}
# }
```

### 7. Unauthorized Access
```bash
curl -X PUT http://localhost:8080/animal/test-lion-001 \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test-lion-001",
    "name": "Leo Unauthorized",
    "species": "Lion",
    "status": "active"
  }'

# Expected: 401 Unauthorized
# {
#   "code": "unauthorized",
#   "message": "Authentication required"
# }
```

## Automated Testing

### Run Integration Test
```bash
# Run specific test for PR003946-144
pytest tests/integration/PR003946-144/test_put_animal_endpoint.py -v

# Run with coverage
pytest tests/integration/PR003946-144/test_put_animal_endpoint.py --cov=openapi_server.impl
```

### Expected Test Output
```
test_put_animal_endpoint.py::test_full_update_success PASSED
test_put_animal_endpoint.py::test_partial_update_success PASSED
test_put_animal_endpoint.py::test_id_mismatch_error PASSED
test_put_animal_endpoint.py::test_not_found_error PASSED
test_put_animal_endpoint.py::test_validation_errors PASSED
test_put_animal_endpoint.py::test_version_conflict PASSED
test_put_animal_endpoint.py::test_unauthorized_access PASSED
test_put_animal_endpoint.py::test_audit_trail_creation PASSED
```

## Database Verification

### Check DynamoDB After Update
```bash
aws dynamodb get-item \
  --table-name quest-dev-animal \
  --key '{"animalId": {"S": "test-lion-001"}}' \
  --profile cmz \
  --region us-west-2

# Verify:
# - Updated fields reflect changes
# - Version incremented
# - modified.at timestamp updated
# - Audit trail includes change history
```

## Playwright E2E Test
```javascript
// Navigate to animal edit page
await page.goto('http://localhost:3001/animals/test-lion-001/edit');

// Update animal name
await page.fill('[name="name"]', 'Leo the Magnificent');

// Save changes
await page.click('button[type="submit"]');

// Verify success message
await expect(page.locator('.success-message')).toContainText('Animal updated successfully');

// Verify data in list view
await page.goto('http://localhost:3001/animals');
await expect(page.locator('text=Leo the Magnificent')).toBeVisible();
```

## Success Criteria
- ✅ All 10 acceptance criteria met
- ✅ All test scenarios pass
- ✅ Data correctly persisted to DynamoDB
- ✅ Audit trail properly recorded
- ✅ Version control prevents conflicts
- ✅ Error messages are user-friendly
- ✅ Authorization properly enforced