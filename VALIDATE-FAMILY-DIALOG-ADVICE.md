# VALIDATE-FAMILY-DIALOG-ADVICE.md

## Best Practices for Family Dialog Validation

### When to Use This Validation

**Ideal Scenarios:**
- After any changes to AddFamilyModalEnhanced component
- Before merging family management features
- As part of regression testing suite
- When debugging family creation issues
- For demonstrating functionality to stakeholders

**Not Recommended When:**
- Backend services are unstable
- Database is undergoing migration
- Quick smoke tests are sufficient (use simpler validation)

### Test Data Setup Best Practices

#### Creating Reliable Test Users
```bash
# Script to create test users before validation
cat > setup-test-users.sh << 'EOF'
#!/bin/bash
echo "Creating test users for family validation..."

# Create parent users
aws dynamodb put-item --table-name quest-dev-user \
  --item '{"userId":{"S":"test-parent-001"},"email":{"S":"parent1@test.com"},"displayName":{"S":"Test Parent One"},"role":{"S":"parent"}}' \
  --condition-expression "attribute_not_exists(userId)"

aws dynamodb put-item --table-name quest-dev-user \
  --item '{"userId":{"S":"test-parent-002"},"email":{"S":"parent2@test.com"},"displayName":{"S":"Test Parent Two"},"role":{"S":"parent"}}' \
  --condition-expression "attribute_not_exists(userId)"

# Create student users
aws dynamodb put-item --table-name quest-dev-user \
  --item '{"userId":{"S":"test-student-001"},"email":{"S":"student1@test.com"},"displayName":{"S":"Test Student One"},"role":{"S":"student"},"age":{"N":"10"}}' \
  --condition-expression "attribute_not_exists(userId)"

aws dynamodb put-item --table-name quest-dev-user \
  --item '{"userId":{"S":"test-student-002"},"email":{"S":"student2@test.com"},"displayName":{"S":"Test Student Two"},"role":{"S":"student"},"age":{"N":"12"}}' \
  --condition-expression "attribute_not_exists(userId)"

echo "Test users created successfully"
EOF
chmod +x setup-test-users.sh
```

#### Cleaning Up Previous Test Data
```bash
# Remove families from previous test runs
aws dynamodb scan --table-name quest-dev-family \
  --filter-expression "begins_with(familyName, :prefix)" \
  --expression-attribute-values '{":prefix":{"S":"Test"}}' \
  --query 'Items[].familyId.S' \
  --output text | xargs -I {} aws dynamodb delete-item \
  --table-name quest-dev-family \
  --key '{"familyId":{"S":"{}"}}'
```

### Common Pitfalls and Solutions

#### 1. Typeahead Search Timing Issues
**Problem**: Typeahead doesn't show results immediately
```javascript
// ❌ Wrong - No wait for debounce
await page.fill('input', 'search term');
await page.click('[role="option"]'); // Fails - no results yet

// ✅ Correct - Wait for debounced search
await page.fill('input', 'search term');
await page.waitForSelector('[role="listbox"]', { timeout: 3000 });
await page.click('[role="option"]:first-child');
```

#### 2. Stale Element References
**Problem**: Elements change after interactions
```javascript
// ❌ Wrong - Element reference becomes stale
const button = await page.$('button:has-text("Add Child")');
await button.click();
// ... other actions ...
await button.click(); // Fails - element changed

// ✅ Correct - Fresh selector each time
await page.click('button:has-text("Add Child")');
// ... other actions ...
await page.click('button:has-text("Add Child")'); // Works
```

#### 3. DynamoDB Eventual Consistency
**Problem**: Data not immediately available after write
```javascript
// ✅ Correct approach with retries
async function waitForFamilyInDB(familyName, maxRetries = 5) {
  for (let i = 0; i < maxRetries; i++) {
    const result = await queryDynamoDB(familyName);
    if (result.Items && result.Items.length > 0) {
      return result.Items[0];
    }
    await new Promise(resolve => setTimeout(resolve, 2000));
  }
  throw new Error('Family not found in database after retries');
}
```

#### 4. Authentication Token Expiry
**Problem**: Long-running tests may exceed token lifetime
```javascript
// ✅ Implement token refresh
async function ensureAuthenticated(page) {
  const isLoginPage = await page.url().includes('/login');
  if (isLoginPage) {
    console.log('Session expired, re-authenticating...');
    await page.fill('input[type="email"]', 'test@cmz.org');
    await page.fill('input[type="password"]', 'testpass123');
    await page.click('button:has-text("Sign In")');
    await page.waitForURL('**/dashboard');
    await page.goto('http://localhost:3000/families/manage');
  }
}
```

### Troubleshooting Guide

#### Issue: "Cannot find Add New Family button"
**Diagnosis Steps:**
1. Check if you're on the correct page: `console.log(await page.url())`
2. Verify authentication: `await page.screenshot({ path: 'debug-no-button.png' })`
3. Check for loading states: `await page.waitForLoadState('networkidle')`

**Solution:**
```javascript
// Ensure proper navigation and wait
await page.goto('http://localhost:3000/families/manage', {
  waitUntil: 'networkidle'
});
await page.waitForSelector('button:has-text("Add New Family")', {
  timeout: 10000
});
```

#### Issue: "Typeahead returns no results"
**Diagnosis Steps:**
1. Check backend is running: `curl http://localhost:8080/user?query=test`
2. Verify test users exist: `aws dynamodb scan --table-name quest-dev-user`
3. Check network tab in browser for API calls

**Solution:**
```javascript
// Add explicit waits and error handling
try {
  await page.fill('input[placeholder*="Search"]', 'Test');
  await page.waitForResponse(resp =>
    resp.url().includes('/user') && resp.status() === 200
  );
  await page.waitForSelector('[role="listbox"]');
} catch (error) {
  console.error('API not responding, checking backend...');
  // Implement backend health check
}
```

#### Issue: "Family not saved to DynamoDB"
**Diagnosis Steps:**
1. Check for JavaScript errors: `const errors = await page.evaluate(() => window.errors)`
2. Verify API response: Monitor network tab for POST /family
3. Check DynamoDB table permissions: `aws dynamodb describe-table --table-name quest-dev-family`

**Solution:**
```javascript
// Capture and validate API response
const [response] = await Promise.all([
  page.waitForResponse(resp =>
    resp.url().includes('/family') && resp.method() === 'POST'
  ),
  page.click('button:has-text("Add Family")')
]);

const responseData = await response.json();
console.log('Family created:', responseData);
assert(responseData.familyId, 'Family ID should be returned');
```

### Advanced Usage Scenarios

#### 1. Testing with Multiple Windows/Tabs
```javascript
// Test concurrent family creation
const context = await browser.newContext();
const page1 = await context.newPage();
const page2 = await context.newPage();

// Login in both tabs
await Promise.all([
  loginAndNavigate(page1),
  loginAndNavigate(page2)
]);

// Create families simultaneously to test race conditions
await Promise.all([
  createFamily(page1, 'Family A'),
  createFamily(page2, 'Family B')
]);
```

#### 2. Performance Testing
```javascript
// Measure dialog load time
const startTime = Date.now();
await page.click('button:has-text("Add New Family")');
await page.waitForSelector('dialog[aria-label="Add New Family"]');
const loadTime = Date.now() - startTime;

console.log(`Dialog load time: ${loadTime}ms`);
assert(loadTime < 2000, 'Dialog should load within 2 seconds');
```

#### 3. Accessibility Testing
```javascript
// Test keyboard navigation
await page.keyboard.press('Tab'); // Focus first field
await page.keyboard.type('Test Family');
await page.keyboard.press('Tab'); // Move to next field

// Test screen reader announcements
const ariaLive = await page.getAttribute('[aria-live]', 'aria-live');
assert(ariaLive === 'polite', 'Form should have aria-live regions');
```

#### 4. Data-Driven Testing
```javascript
// Test multiple family configurations
const testFamilies = [
  { name: 'Single Parent', parents: 1, children: 1 },
  { name: 'Large Family', parents: 2, children: 4 },
  { name: 'No Children', parents: 2, children: 0 },
  { name: 'Extended Family', parents: 3, children: 3 }
];

for (const config of testFamilies) {
  await testFamilyCreation(page, config);
  await validateInDatabase(config);
  await cleanupFamily(config.name);
}
```

### Integration Guidelines

#### CI/CD Pipeline Integration
```yaml
# .gitlab-ci.yml or .github/workflows/test.yml
family-validation:
  stage: e2e-test
  before_script:
    - npm install
    - ./scripts/setup-test-users.sh
    - make start-dev &
    - npx wait-on http://localhost:3000 http://localhost:8080
  script:
    - npx playwright test validate-family-dialog.spec.js
  after_script:
    - ./scripts/cleanup-test-data.sh
  artifacts:
    when: always
    paths:
      - validation-evidence/
      - playwright-report/
      - test-results/
```

#### Parallel Test Execution
```javascript
// playwright.config.js
module.exports = {
  workers: 1, // Keep at 1 for family tests to avoid conflicts
  projects: [
    {
      name: 'Family Dialog - Chrome',
      use: { ...devices['Desktop Chrome'] }
    },
    {
      name: 'Family Dialog - Firefox',
      use: { ...devices['Desktop Firefox'] }
    }
  ]
};
```

#### Integration with Monitoring
```javascript
// Send results to monitoring system
async function reportToMonitoring(results) {
  await fetch('https://monitoring.example.com/api/test-results', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      test: 'family-dialog-validation',
      timestamp: new Date().toISOString(),
      success: results.success,
      duration: results.duration,
      errors: results.errors
    })
  });
}
```

### Performance Optimization

#### 1. Reuse Authentication
```javascript
// Save auth state for reuse
await page.context().storageState({ path: 'auth-state.json' });

// Reuse in subsequent tests
const context = await browser.newContext({
  storageState: 'auth-state.json'
});
```

#### 2. Parallel DynamoDB Operations
```javascript
// Query multiple tables simultaneously
const [families, users, audit] = await Promise.all([
  queryFamilyTable(),
  queryUserTable(),
  queryAuditTable()
]);
```

#### 3. Smart Waiting Strategies
```javascript
// Use specific waits instead of arbitrary timeouts
await page.waitForResponse(resp => resp.url().includes('/family'));
await page.waitForFunction(() => document.querySelectorAll('[role="option"]').length > 0);
await page.waitForLoadState('domcontentloaded');
```

### Security Considerations

#### 1. Test Data Isolation
- Always use dedicated test accounts
- Never use production data in tests
- Clean up test data after execution
- Use unique identifiers to avoid conflicts

#### 2. Credential Management
```bash
# Use environment variables, never hardcode
export TEST_USER_EMAIL=${{ secrets.TEST_USER_EMAIL }}
export TEST_USER_PASSWORD=${{ secrets.TEST_USER_PASSWORD }}
export AWS_ACCESS_KEY_ID=${{ secrets.AWS_ACCESS_KEY_ID }}
```

#### 3. Rate Limiting Protection
```javascript
// Add delays to avoid triggering rate limits
async function throttledOperation(operations, delayMs = 100) {
  for (const op of operations) {
    await op();
    await page.waitForTimeout(delayMs);
  }
}
```

### Debugging Techniques

#### 1. Enable Playwright Debug Mode
```bash
# Run with debug mode
PWDEBUG=1 npx playwright test validate-family-dialog.spec.js
```

#### 2. Capture HAR Files
```javascript
// Record network traffic
const context = await browser.newContext({
  recordHar: { path: 'network-trace.har' }
});
```

#### 3. Take Videos of Failures
```javascript
// playwright.config.js
use: {
  video: 'retain-on-failure',
  trace: 'retain-on-failure'
}
```

#### 4. Custom Debug Logging
```javascript
// Add debug helper
async function debugLog(page, message) {
  const timestamp = new Date().toISOString();
  const url = page.url();
  console.log(`[${timestamp}] ${message} - URL: ${url}`);
  await page.screenshot({
    path: `debug-${Date.now()}.png`
  });
}
```

### Maintenance Guidelines

#### Regular Updates Required
1. **Monthly**: Review and update test user data
2. **Per Sprint**: Update selectors if UI changes
3. **Quarterly**: Review and optimize test execution time
4. **Annually**: Refactor test structure for maintainability

#### Signs Tests Need Updating
- Consistent failures on specific steps
- Tests taking >5 minutes to complete
- Flaky results (intermittent failures)
- New features not covered
- Changed business requirements

#### Version Compatibility Matrix
| Component | Version | Notes |
|-----------|---------|-------|
| Playwright | 1.40+ | Required for component testing |
| Node.js | 18+ | For native fetch support |
| AWS CLI | 2.0+ | For DynamoDB operations |
| Chrome | 119+ | For container queries support |

### Related Documentation
- `/validate-family-dialog` - Main validation command
- `.claude/commands/validate-animal-config-fields.md` - Similar validation pattern
- `frontend/src/components/AddFamilyModalEnhanced.tsx` - Component source
- `backend/api/openapi_spec.yaml` - API specifications for family endpoints