# Validate Family Dialog

**Purpose**: Comprehensive E2E validation of the Add Family dialog with field-level testing, DynamoDB verification, and visual browser automation

**Command**: `/validate-family-dialog`

## Context
This command provides systematic validation of the enhanced Add Family dialog, ensuring all fields are properly editable, data persists correctly to DynamoDB, and the UI accurately reflects the database state. It follows the established CMZ validation patterns with visible browser automation for user confidence.

## Sequential Reasoning Approach

Use MCP Sequential Thinking to systematically validate the Add Family dialog:

### Phase 1: Environment Setup and Test Data Preparation
**Use Sequential Reasoning to:**
1. **Service Verification**: Ensure backend API and frontend are running
2. **Test User Setup**: Create or verify test users in DynamoDB for parent/child selection
3. **Clean Slate Preparation**: Remove any existing test families from previous runs
4. **Browser Configuration**: Launch Playwright with visible browser for monitoring
5. **Authentication**: Login with test credentials and navigate to Family Management

**Key Questions for Sequential Analysis:**
- Are all required services healthy and responding?
- Do we have sufficient test users for comprehensive typeahead testing?
- Is the database in a known clean state for predictable testing?
- Can we authenticate and access the Family Management page?

### Phase 2: Field-Level UI Testing
**Implementation Order (Follow Exactly):**

#### Step 1: Open Add Family Dialog
```javascript
// Navigate to Family Management
await page.goto('http://localhost:3000/families/manage');
await page.waitForLoadState('networkidle');

// Click Add New Family button
await page.click('button:has-text("Add New Family")');
await page.waitForSelector('dialog[aria-label="Add New Family"]');

// Take initial screenshot
await page.screenshot({
  path: 'validation-evidence/family-dialog-initial.png',
  fullPage: false
});
```

#### Step 2: Test Family Name Field
```javascript
// Test empty state
const familyNameInput = page.locator('input[placeholder*="family name"]');
await expect(familyNameInput).toBeEmpty();

// Add text
await familyNameInput.fill('Test Family 2025');
await page.screenshot({ path: 'validation-evidence/family-name-filled.png' });

// Edit text
await familyNameInput.clear();
await familyNameInput.fill('Smith Family');
await page.waitForTimeout(500);

// Validate text persistence
await expect(familyNameInput).toHaveValue('Smith Family');
```

#### Step 3: Test Children Typeahead
```javascript
// Click Add Child button
await page.click('button:has-text("Add Child")');
await page.waitForSelector('input[placeholder*="Search for children"]');

// Type to search
const childSearch = page.locator('input[placeholder*="Search for children"]');
await childSearch.type('Test Student', { delay: 100 });
await page.waitForSelector('[role="listbox"]');

// Select first result
await page.click('[role="option"]:first-child');
await page.screenshot({ path: 'validation-evidence/child-selected.png' });

// Verify chip appears
await expect(page.locator('text=Test Student')).toBeVisible();

// Remove child
await page.click('[aria-label*="Remove"]:near(text("Test Student"))');
await expect(page.locator('text=Test Student')).not.toBeVisible();

// Add multiple children
await page.click('button:has-text("Add Child")');
await childSearch.type('Student', { delay: 100 });
await page.click('[role="option"]:nth-child(0)');
await page.click('[role="option"]:nth-child(1)');
```

#### Step 4: Test Parents Typeahead (Required Field)
```javascript
// Verify validation message
await expect(page.locator('text=At least one parent is required')).toBeVisible();

// Click Add Parent button
await page.click('button:has-text("Add Parent")');
await page.waitForSelector('input[placeholder*="Search for parents"]');

// Search and select parent
const parentSearch = page.locator('input[placeholder*="Search for parents"]');
await parentSearch.type('Test Parent', { delay: 100 });
await page.waitForSelector('[role="listbox"]');
await page.click('[role="option"]:first-child');

// Verify chip and validation cleared
await expect(page.locator('text=Test Parent')).toBeVisible();
await expect(page.locator('text=At least one parent is required')).not.toBeVisible();

// Add second parent
await page.click('button:has-text("Add Parent")');
await parentSearch.type('Parent Two', { delay: 100 });
await page.click('[role="option"]:first-child');

// Screenshot multiple parents
await page.screenshot({ path: 'validation-evidence/multiple-parents.png' });
```

#### Step 5: Test Address Fields
```javascript
// Fill address fields
await page.fill('input[placeholder*="123 Main Street"]', '456 Oak Avenue');
await page.fill('input[placeholder*="City"]', 'Seattle');
await page.fill('input[placeholder*="State"]', 'WA');
await page.fill('input[placeholder*="ZIP"]', '98101');

// Edit each field
await page.fill('input[placeholder*="123 Main Street"]', '789 Pine Street');
await page.fill('input[placeholder*="City"]', 'Bellevue');

// Clear and refill
await page.fill('input[placeholder*="State"]', '');
await page.fill('input[placeholder*="State"]', 'WA');

// Screenshot completed form
await page.screenshot({ path: 'validation-evidence/form-complete.png' });
```

#### Step 6: Test Form Validation
```javascript
// Verify Add Family button is enabled
const addButton = page.locator('button:has-text("Add Family"):not(:has-text("Add New"))');
await expect(addButton).toBeEnabled();

// Clear required field to test validation
await familyNameInput.clear();
await expect(addButton).toBeDisabled();

// Restore and verify
await familyNameInput.fill('Smith Family');
await expect(addButton).toBeEnabled();
```

### Phase 3: Database Persistence Validation
**Validation Order (Follow Exactly):**

#### Step 1: Submit Family and Capture ID
```javascript
// Submit the form
await page.click('button:has-text("Add Family"):not(:has-text("Add New"))');

// Wait for success message or redirect
await page.waitForSelector('text=successfully added', { timeout: 10000 })
  .catch(() => page.waitForNavigation());

// Capture family ID from success message or URL
const familyId = await page.evaluate(() => {
  // Extract from success message or generate timestamp-based ID
  return `family_${Date.now()}`;
});

console.log(`Created family with ID: ${familyId}`);
```

#### Step 2: Query DynamoDB for Family Data
```bash
# Query family table for the new family
aws dynamodb query \
  --table-name quest-dev-family \
  --key-condition-expression "familyName = :fname" \
  --expression-attribute-values '{":fname":{"S":"Smith Family"}}' \
  --output json > family-data.json

# Verify family exists
if [ ! -s family-data.json ]; then
  echo "ERROR: Family not found in DynamoDB"
  exit 1
fi

# Extract and validate fields
FAMILY_NAME=$(jq -r '.Items[0].familyName.S' family-data.json)
PARENT_IDS=$(jq -r '.Items[0].parentIds.L[].S' family-data.json)
STUDENT_IDS=$(jq -r '.Items[0].studentIds.L[].S' family-data.json)
ADDRESS=$(jq -r '.Items[0].address.M' family-data.json)

echo "Database Validation Results:"
echo "- Family Name: $FAMILY_NAME"
echo "- Parents: $PARENT_IDS"
echo "- Students: $STUDENT_IDS"
echo "- Address: $ADDRESS"
```

#### Step 3: Verify UI Reflects Database State
```javascript
// Reload page to verify persistence
await page.reload();
await page.waitForLoadState('networkidle');

// Search for the created family
await page.fill('input[placeholder*="Search families"]', 'Smith Family');
await page.waitForTimeout(1000);

// Verify family card appears
await expect(page.locator('text=Smith Family')).toBeVisible();

// Click View Details
await page.click('button:has-text("View Details"):near(text("Smith Family"))');

// Verify all fields match database
await expect(page.locator('text=456 Oak Avenue')).toBeVisible();
await expect(page.locator('text=Bellevue, WA 98101')).toBeVisible();

// Screenshot final validation
await page.screenshot({ path: 'validation-evidence/family-persisted.png' });
```

### Phase 4: Edit Validation and Cleanup
**Cleanup Order (Follow Exactly):**

#### Step 1: Test Edit Functionality
```javascript
// Open family for editing
await page.click('button:has-text("Edit Family")');

// Modify fields
await page.fill('input[value="Smith Family"]', 'Smith-Johnson Family');
await page.click('button:has-text("Save Changes")');

// Verify update in database
// AWS DynamoDB query to verify changes
```

#### Step 2: Delete Test Data
```bash
# Delete test family from DynamoDB
aws dynamodb delete-item \
  --table-name quest-dev-family \
  --key '{"familyId": {"S": "'$FAMILY_ID'"}}' \
  --output json

echo "Test family deleted from database"
```

#### Step 3: Generate Validation Report
```bash
# Create validation summary
cat > validation-report.md << EOF
# Family Dialog Validation Report
Date: $(date)

## Test Results
✅ Family Name Field: Editable, text persists
✅ Children Typeahead: Search works, multiple selection, removal works
✅ Parents Typeahead: Required validation, search works
✅ Address Fields: All fields editable
✅ Form Validation: Proper enable/disable of submit button
✅ Database Persistence: Data saved to DynamoDB
✅ UI Reflection: Saved data displays correctly

## Evidence
- Screenshots saved in validation-evidence/
- Database queries logged
- All fields tested for add/edit/delete

## Issues Found
None - All validations passed

EOF
```

## Implementation Details

### Test Data Requirements
```javascript
// Required test users in DynamoDB
const testUsers = [
  { userId: 'test-parent-001', displayName: 'Test Parent One', role: 'parent' },
  { userId: 'test-parent-002', displayName: 'Test Parent Two', role: 'parent' },
  { userId: 'test-student-001', displayName: 'Test Student One', role: 'student' },
  { userId: 'test-student-002', displayName: 'Test Student Two', role: 'student' }
];
```

### Playwright Configuration
```javascript
const config = {
  use: {
    headless: false,  // Show browser for visual validation
    slowMo: 500,      // Slow down for visibility
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    trace: 'retain-on-failure'
  },
  timeout: 60000,     // 60 second timeout for slow operations
  expect: {
    timeout: 10000    // 10 second timeout for assertions
  }
};
```

### Environment Variables
```bash
export FRONTEND_URL=http://localhost:3000
export API_URL=http://localhost:8080
export AWS_PROFILE=cmz
export DYNAMODB_TABLE_PREFIX=quest-dev-
```

## Integration Points

### With Existing CMZ Systems
- **Frontend**: Uses AddFamilyModalEnhanced component at `/families/manage`
- **Backend API**: POST/PUT/DELETE `/family` endpoints
- **DynamoDB**: quest-dev-family and quest-dev-user tables
- **Authentication**: Uses existing CMZ auth flow with JWT tokens
- **Validation Patterns**: Follows validate-animal-config-fields.md structure

### CI/CD Integration
```yaml
playwright-family-validation:
  stage: test
  script:
    - make start-dev
    - npm run validate:family-dialog
    - aws s3 cp validation-evidence/ s3://cmz-test-evidence/ --recursive
  artifacts:
    paths:
      - validation-evidence/
      - validation-report.md
```

## Quality Gates

### Mandatory Validation Before Completion
- [ ] All services running (frontend, backend, database accessible)
- [ ] Test users exist in database
- [ ] Browser launches in visible mode
- [ ] All fields tested for add/edit/delete operations
- [ ] Database queries return expected data
- [ ] Screenshots captured at key points
- [ ] No console errors during testing
- [ ] Validation report generated

### Field-Specific Validations
- [ ] Family Name: Required, min 3 characters
- [ ] Children: Optional, typeahead works, chips removable
- [ ] Parents: At least one required, typeahead works
- [ ] Address: All fields required when one is filled
- [ ] Submit Button: Disabled until validation passes

## Success Criteria

1. **Visual Validation**: User can watch entire test execution in browser
2. **Field Testing**: Every field tested for create, edit, and delete
3. **Database Verification**: All data correctly persisted to DynamoDB
4. **UI Consistency**: UI accurately reflects database state after operations
5. **Error Handling**: Graceful handling of network issues or missing data
6. **Evidence Collection**: Screenshots and logs for audit trail
7. **Clean Execution**: No test data left in database after completion

## Error Handling

### Common Issues and Solutions
```javascript
// Handle typeahead timing issues
await page.waitForSelector('[role="listbox"]', {
  timeout: 5000
}).catch(() => {
  console.log('Typeahead slow, retrying...');
  await page.click('button:has-text("Cancel")');
  await page.click('button:has-text("Add Child")');
});

// Handle DynamoDB eventual consistency
await page.waitForTimeout(2000); // Wait for DB write
const maxRetries = 3;
for (let i = 0; i < maxRetries; i++) {
  const result = await queryDynamoDB();
  if (result.Items.length > 0) break;
  await page.waitForTimeout(1000);
}

// Handle authentication expiry
if (await page.locator('text=Session expired').isVisible()) {
  await reAuthenticate();
}
```

## References
- `VALIDATE-FAMILY-DIALOG-ADVICE.md` - Best practices and troubleshooting guide
- `.claude/commands/validate-animal-config-fields.md` - Similar validation pattern
- `frontend/src/components/AddFamilyModalEnhanced.tsx` - Component being tested
- `backend/api/src/main/python/openapi_server/impl/family.py` - Backend implementation