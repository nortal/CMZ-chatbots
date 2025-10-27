# /validate-family-management

Command to validate Family Management with bidirectional references, role-based access control, and visible browser testing.

## Usage

```bash
/validate-family-management [--mode <test-mode>] [--role <user-role>] [--visible]
```

## Options

- `--mode <test-mode>`: Testing mode (quick, comprehensive, rbac, bidirectional, all)
- `--role <user-role>`: Test as specific role (admin, parent, student)
- `--visible`: Force visible browser testing with Playwright MCP

## Description

This command performs comprehensive E2E validation of the Family Management system with:
- **Bidirectional References**: Families store user IDs, users store family IDs
- **Role-Based Access Control**: Admin edit, member view-only
- **Visible Testing**: Real browser interaction for confidence
- **DynamoDB Verification**: Direct database validation

## Test Architecture

### Data Model
```
Family:                          User:
├── familyId: "family_123"       ├── userId: "user_456"
├── parentIds: ["user_456"]      ├── familyIds: ["family_123"]
├── studentIds: ["user_789"]     └── role: "parent"
└── canEdit: true/false (admin)
```

## Visible Testing Approach

### Phase 1: Environment Verification
```bash
# Start services with visible status
echo "🚀 Starting development environment..."
make run-api
cd frontend && npm run dev
echo "⏳ Waiting for services..."
sleep 5

# Health check with visible output
curl -s http://localhost:8080/system_health | jq '.'
curl -s http://localhost:3001 | grep -q "React" && echo "✅ Frontend ready"
```

### Phase 2: Browser-Based Testing with Playwright MCP

#### Admin User Testing (Full Permissions)
```javascript
// Using Playwright MCP for visible browser testing
test('Admin can create and edit families - VISIBLE', async ({ browser }) => {
  // Navigate and login as admin
  await browser.navigate({ url: 'http://localhost:3001' });
  await browser.snapshot();  // Show current state

  // Login as admin
  await browser.type({
    element: "Email input",
    ref: "[data-testid='email-input']",
    text: "admin@cmz.org"
  });
  await browser.type({
    element: "Password input",
    ref: "[data-testid='password-input']",
    text: "admin123"
  });
  await browser.click({
    element: "Login button",
    ref: "[data-testid='login-button']"
  });

  // Wait for dashboard
  await browser.wait_for({ text: "Dashboard" });
  await browser.snapshot();  // Show logged-in state

  // Navigate to Family Management
  await browser.click({ element: "Family Groups", ref: "text=Family Groups" });
  await browser.click({ element: "Manage Families", ref: "text=Manage Families" });
  await browser.snapshot();  // Show family management page

  // Verify admin UI elements
  console.log("🔍 Verifying admin UI elements...");
  await browser.snapshot();
  // Should see: Add New Family button, Edit/Delete icons

  // Create new family
  await browser.click({
    element: "Add New Family button",
    ref: "button:has-text('Add New Family')"
  });
  await browser.wait_for({ text: "Create New Family" });

  // Fill family details
  await browser.fill_form({
    fields: [
      {
        name: "Family Name",
        ref: "[name='familyName']",
        type: "textbox",
        value: "Test Bidirectional Family"
      },
      {
        name: "Parent Email",
        ref: "[name='parent[0].email']",
        type: "textbox",
        value: "newparent@test.com"
      },
      {
        name: "Parent Name",
        ref: "[name='parent[0].name']",
        type: "textbox",
        value: "Test Parent"
      }
    ]
  });

  await browser.click({
    element: "Create Family button",
    ref: "button:has-text('Create Family')"
  });

  // Verify success
  await browser.wait_for({ text: "Family created successfully" });
  await browser.snapshot();  // Show success state
});
```

#### Parent User Testing (View-Only)
```javascript
test('Parent can only view families - VISIBLE', async ({ browser }) => {
  // Login as parent
  await browser.navigate({ url: 'http://localhost:3001' });
  await browser.type({
    element: "Email input",
    ref: "[data-testid='email-input']",
    text: "parent1@test.cmz.org"
  });
  await browser.type({
    element: "Password input",
    ref: "[data-testid='password-input']",
    text: "testpass123"
  });
  await browser.click({
    element: "Login button",
    ref: "[data-testid='login-button']"
  });

  // Navigate to families
  await browser.wait_for({ text: "Dashboard" });
  await browser.click({ element: "Family Groups", ref: "text=Family Groups" });
  await browser.click({ element: "Manage Families", ref: "text=Manage Families" });

  // Verify restricted UI
  console.log("🔒 Verifying parent restrictions...");
  await browser.snapshot();
  // Should NOT see: Add New Family button
  // Should see: Lock icons instead of Edit/Delete

  // Try to view family details
  await browser.click({
    element: "View Details button",
    ref: "[title='View Details']"
  });
  await browser.wait_for({ text: "Family Details" });
  await browser.snapshot();  // Show read-only view
});
```

### Phase 3: DynamoDB Validation (Visible Output)

```bash
# Show bidirectional references in DynamoDB
echo "📊 Validating DynamoDB bidirectional references..."

# Check family has user IDs (not names)
aws dynamodb get-item \
  --table-name quest-dev-family \
  --key '{"familyId":{"S":"family_test_001"}}' \
  --profile cmz \
  --region us-west-2 | jq '.Item | {
    familyId: .familyId.S,
    parentIds: .parentIds.SS,
    studentIds: .studentIds.SS,
    familyName: .familyName.S
  }'

# Check user has family IDs
aws dynamodb get-item \
  --table-name quest-dev-user \
  --key '{"userId":{"S":"user_parent_001"}}' \
  --profile cmz \
  --region us-west-2 | jq '.Item | {
    userId: .userId.S,
    familyIds: .familyIds.SS,
    role: .role.S,
    displayName: .displayName.S
  }'

# Show relationship consistency
echo "🔄 Verifying bidirectional consistency..."
```

### Phase 4: Permission Testing (Visible API Calls)

```bash
# Test admin can edit
echo "✅ Testing admin edit permissions..."
curl -X PATCH http://localhost:8080/family/family_test_001 \
  -H "Content-Type: application/json" \
  -H "X-User-Id: admin_user_001" \
  -d '{"familyName":"Admin Updated Family"}' \
  -w "\nHTTP Status: %{http_code}\n" | jq '.'

# Test parent cannot edit (should get 403)
echo "🚫 Testing parent edit restriction..."
curl -X PATCH http://localhost:8080/family/family_test_001 \
  -H "Content-Type: application/json" \
  -H "X-User-Id: parent_user_001" \
  -d '{"familyName":"Parent Attempted Update"}' \
  -w "\nHTTP Status: %{http_code}\n" | jq '.'

# Test parent can view their family
echo "👁️ Testing parent view permission..."
curl -X GET http://localhost:8080/family/family_test_001 \
  -H "X-User-Id: parent_user_001" \
  -w "\nHTTP Status: %{http_code}\n" | jq '.'

# Test non-member cannot view (should get 403)
echo "❌ Testing non-member restriction..."
curl -X GET http://localhost:8080/family/family_test_001 \
  -H "X-User-Id: other_user_001" \
  -w "\nHTTP Status: %{http_code}\n" | jq '.'
```

## Comprehensive Test Script

```bash
#!/bin/bash
# Complete visible family management validation

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Family Management Validation - Visible Testing${NC}"
echo "=================================================="

# Phase 1: Environment Setup
echo -e "\n${YELLOW}Phase 1: Environment Setup${NC}"
make run-api &
API_PID=$!
cd frontend && npm run dev &
FRONTEND_PID=$!
sleep 10

# Phase 2: Health Check
echo -e "\n${YELLOW}Phase 2: Health Check${NC}"
if curl -s http://localhost:8080/system_health | jq '.status' | grep -q "healthy"; then
    echo -e "${GREEN}✅ API is healthy${NC}"
else
    echo -e "${RED}❌ API is not healthy${NC}"
    exit 1
fi

# Phase 3: Run Playwright tests with visible browser
echo -e "\n${YELLOW}Phase 3: Browser Testing (Visible)${NC}"
cd backend/api/src/main/python/tests/playwright
FRONTEND_URL=http://localhost:3001 npx playwright test \
    --config config/playwright.config.js \
    specs/family-management-visible.spec.js \
    --headed \
    --slowmo=500 \
    --reporter=line

# Phase 4: DynamoDB Validation
echo -e "\n${YELLOW}Phase 4: DynamoDB Validation${NC}"
./scripts/validate_dynamodb_families.sh

# Phase 5: API Permission Tests
echo -e "\n${YELLOW}Phase 5: Permission Tests${NC}"
./scripts/test_family_permissions.sh

# Cleanup
echo -e "\n${YELLOW}Cleanup${NC}"
kill $API_PID $FRONTEND_PID 2>/dev/null || true

echo -e "\n${GREEN}✅ Family Management Validation Complete!${NC}"
```

## Success Criteria

### Visual Confirmation
- ✅ Browser shows login flow
- ✅ Admin sees "Add New Family" button
- ✅ Parents see lock icons instead of edit buttons
- ✅ Role badges display correctly (purple for admin, green for parent)
- ✅ Family creation shows success message
- ✅ Edit modal appears for admins only

### Data Model Validation
- ✅ Families store parentIds/studentIds (not names)
- ✅ Users store familyIds array
- ✅ Bidirectional references remain consistent
- ✅ User details populated from /user endpoint

### Permission Validation
- ✅ Admin: 200 OK for all operations
- ✅ Parent: 200 OK for view, 403 for edit/delete
- ✅ Non-member: 403 for all operations
- ✅ UI hides/shows elements based on role

### Performance Metrics
- ✅ Family list loads < 2 seconds
- ✅ User population batch fetch < 500ms
- ✅ Permission checks < 100ms
- ✅ DynamoDB operations < 200ms

## Troubleshooting

### Issue: Browser tests not visible
**Solution**: Use Playwright MCP with browser.navigate/click/type instead of native Playwright

### Issue: Bidirectional references inconsistent
**Solution**: Check atomic operations in family_bidirectional.py, ensure transaction support

### Issue: Permissions not enforced
**Solution**: Verify JWT token includes role claim, check can_edit_family methods

### Issue: User names not displaying
**Solution**: Check batch user fetch in familyApi.ts, verify /users/batch endpoint

## Test Users

| Email | Password | Role | Purpose |
|-------|----------|------|---------|
| admin@cmz.org | admin123 | admin | Full permissions testing |
| parent1@test.cmz.org | testpass123 | parent | View-only testing |
| student1@test.cmz.org | testpass123 | student | Restricted access |
| test@cmz.org | testpass123 | user | Default user testing |

## Related Files

- `frontend/src/services/familyApi.ts` - API service with permissions
- `frontend/src/pages/FamilyManagementBidirectional.tsx` - Role-aware UI
- `backend/.../impl/family_bidirectional.py` - RBAC implementation
- `tests/e2e/test_family_frontend_backend.spec.js` - E2E test suite

## Notes

- Always test with visible browser for user confidence
- Validate both UI behavior and API responses
- Check DynamoDB for data integrity
- Use role-specific test flows for complete coverage
- Monitor console for JavaScript errors
- Screenshot key states for documentation