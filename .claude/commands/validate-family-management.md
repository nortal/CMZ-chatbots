# /validate-family-management

Command to validate frontend Family Groups functionality and verify DynamoDB persistence.

## Usage

```bash
/validate-family-management [--focus <functionality>]
```

## Options

- `--focus <functionality>`: Focus on specific functionality (add-family, edit-family, list-families, delete-family)

## Description

This command performs comprehensive E2E validation of the Family Groups management system, testing frontend user interactions and verifying that data is correctly persisted in DynamoDB.

## Validation Phases

### Phase 1: Environment Setup
- Start frontend development server
- Start backend API server
- Verify service health
- Login with test credentials

### Phase 2: Add Family Validation
- Open Add New Family modal via button click
- Fill all form fields (family name, parents, students, address, programs)
- Add multiple parents and students dynamically
- Submit the form
- Verify success message
- Check DynamoDB for new family record with correct structure

### Phase 3: List Families Validation
- Navigate to Family Groups > Manage Families
- Verify family list loads
- Check pagination if applicable
- Verify family cards display correct information
- Confirm API call to GET /family_list

### Phase 4: Edit Family Validation
- Click View Details on a family
- Click Edit Family Details button
- Verify edit mode activates
- Modify family information
- Save changes
- Verify DynamoDB update with modified timestamp

### Phase 5: Search and Filter Validation
- Test family search by name
- Test filtering by status
- Test filtering by program enrollment
- Verify filtered results match DynamoDB queries

### Phase 6: Delete Family Validation
- Select a test family
- Click delete button
- Confirm deletion dialog
- Verify soft delete in DynamoDB (softDelete: true)
- Confirm family no longer appears in list

## Success Criteria

### Frontend Success
- ✅ Add New Family button opens modal
- ✅ Form submission creates family
- ✅ Edit button enables edit mode
- ✅ Save updates family data
- ✅ Delete removes family from UI
- ✅ List displays all families
- ✅ Search/filter works correctly

### Backend Success
- ✅ POST /family creates DynamoDB record
- ✅ GET /family_list returns all non-deleted families
- ✅ GET /family/{id} returns specific family
- ✅ PATCH /family/{id} updates family
- ✅ DELETE /family/{id} soft deletes

### DynamoDB Success
- ✅ Family records have unique familyId
- ✅ Audit stamps (created/modified) present
- ✅ Soft delete flag works
- ✅ Parent/student arrays stored correctly
- ✅ Additional fields preserved

## Test Data

### Test Family 1
```json
{
  "familyName": "Johnson Family",
  "parents": [
    {
      "name": "Sarah Johnson",
      "email": "sarah.johnson@test.cmz.org",
      "phone": "555-0101",
      "isPrimary": true,
      "isEmergencyContact": true
    },
    {
      "name": "Mike Johnson",
      "email": "mike.johnson@test.cmz.org",
      "phone": "555-0102",
      "isPrimary": false,
      "isEmergencyContact": true
    }
  ],
  "students": [
    {
      "name": "Emma Johnson",
      "age": "10",
      "grade": "5th",
      "interests": "animals, science",
      "allergies": "peanuts"
    },
    {
      "name": "Liam Johnson",
      "age": "8",
      "grade": "3rd",
      "interests": "dinosaurs, art",
      "allergies": "none"
    }
  ],
  "address": {
    "street": "123 Zoo Lane",
    "city": "Issaquah",
    "state": "WA",
    "zip": "98027"
  },
  "preferredPrograms": ["Junior Zookeeper", "Conservation Club"],
  "status": "active"
}
```

## Implementation

```bash
# Phase 1: Setup
echo "🔧 Starting services..."
make run-api &
cd frontend && npm run dev &
sleep 10

# Phase 2: Browser Testing with Playwright
npx playwright test --config playwright.config.js specs/family-management.spec.js

# Phase 3: Direct DynamoDB Validation
aws dynamodb scan \
  --table-name quest-dev-family \
  --filter-expression "begins_with(familyId, :prefix)" \
  --expression-attribute-values '{":prefix":{"S":"family_"}}' \
  --profile cmz \
  --region us-west-2

# Phase 4: API Testing
# Test list families
curl -X GET http://localhost:8080/family_list

# Test create family
curl -X POST http://localhost:8080/family \
  -H "Content-Type: application/json" \
  -d @test-family.json

# Phase 5: Cleanup
# Soft delete test families
aws dynamodb update-item \
  --table-name quest-dev-family \
  --key '{"familyId":{"S":"family_test_001"}}' \
  --update-expression "SET softDelete = :true" \
  --expression-attribute-values '{":true":{"BOOL":true}}' \
  --profile cmz \
  --region us-west-2
```

## Common Issues and Solutions

### Issue: Add New Family button not working
**Solution**: Ensure AddFamilyModal is imported and state management is set up in FamilyManagement.tsx

### Issue: Family not appearing in DynamoDB
**Solution**: Check backend logs for errors, verify FAMILY_DYNAMO_TABLE_NAME environment variable

### Issue: Edit mode not activating
**Solution**: Verify isEditMode state toggle and form field disabled attributes

### Issue: Soft delete not working
**Solution**: Check family.py implementation for softDelete flag handling

## Related Commands

- `/validate-animal-config`: Similar validation for Animal Config
- `/validate-data-persistence`: General data persistence validation
- `/validate-backend-health`: Backend health check validation

## Notes

- Test families are prefixed with "family_test_" for easy cleanup
- Soft deleted families should not appear in list but remain in DynamoDB
- Frontend uses mock data if backend is unavailable - ensure backend is running
- Use Chrome DevTools Network tab to verify API calls