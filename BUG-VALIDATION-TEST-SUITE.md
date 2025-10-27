# CMZ Bug Validation Test Suite

**Created**: October 24th, 2025 8:47 AM
**Branch**: `003-animal-assistant-mgmt`
**Purpose**: Comprehensive Playwright tests to validate all reported UI bugs and prevent regressions

## Overview

This test suite provides comprehensive validation for **11 critical bugs** reported in the CMZ Animal Assistant Management System. Each bug has dedicated test coverage with visible browser execution to ensure proper validation.

## Test Organization

### File Structure

```
backend/api/src/main/python/tests/playwright/
├── specs/bug-validation/
│   ├── 01-critical-data-loading.spec.js      # CRITICAL bugs (1-4)
│   ├── 02-high-severity-dialogs.spec.js      # HIGH bugs (5-7)
│   └── 03-medium-navigation-structure.spec.js # MEDIUM bugs (8-11)
├── run-bug-validation.sh                      # Test runner script
└── config/playwright.config.js                # Playwright configuration
```

### Bug Categories

#### CRITICAL Severity (4 bugs)
**File**: `01-critical-data-loading.spec.js`

1. **Assistant Management sub-elements non-functional**
   - Active Assistants section loading
   - Create Assistant dialog functionality
   - Personality Templates section loading

2. **Animal Details page shows "Failed to fetch" error**
   - Animal list loading without errors
   - Backend API integration
   - Error handling for service unavailability

3. **Chat with Animals shows "Unable to load animals"**
   - Animal selection interface loading
   - Available animals fetching
   - Animal selection for chat sessions

4. **Family Groups shows "Failed to load families"**
   - Family list loading without errors
   - DynamoDB data fetching
   - Proper handling of empty states

#### HIGH Severity (3 bugs)
**File**: `02-high-severity-dialogs.spec.js`

5. **Create Sandbox Assistant dialog cancel button doesn't work**
   - Cancel button closes dialog
   - No form submission on cancel
   - Form data cleared after cancel
   - Escape key handling

6. **Guardrails disappear after closing creation dialog**
   - Guardrails persist after dialog interactions
   - No duplicate rendering
   - Proper list refresh

7. **Chat History shows "no sessions found" and "not authenticated" for admin users**
   - Authentication verification for logged-in admins
   - Chat history fetching with auth tokens
   - Proper empty state vs error messaging
   - Session metadata display

#### MEDIUM Severity (4 bugs)
**File**: `03-medium-navigation-structure.spec.js`

8. **Guardrails are in System/Safety Management instead of Animal Management**
   - Guardrails under Animal Management navigation
   - NOT under System or Safety sections
   - Correct breadcrumb hierarchy

9. **User roles include incorrect names**
   - NO "Visitor" role
   - "Parent" instead of "Educator"
   - "Student" instead of "Member"
   - Correct roles: Admin, Zookeeper, Parent, Student

10. **Department field enabled for all roles**
    - Enabled ONLY for Administrator and Zookeeper
    - Disabled for Parent and Student
    - Dynamic updates when role changes

11. **"Roles and Permissions" subsection exists**
    - NO separate "Roles and Permissions" section
    - Role selection integrated into user form

## Running the Tests

### Prerequisites

1. **Backend service running**:
   ```bash
   make run-api
   # Backend should be at http://localhost:8080
   ```

2. **Frontend service running**:
   ```bash
   cd frontend && npm start
   # Frontend should be at http://localhost:3001
   ```

3. **Test users available** (from DynamoDB or mock data):
   - `test@cmz.org` / `testpass123` (admin)
   - `parent1@test.cmz.org` / `testpass123` (parent)
   - `student1@test.cmz.org` / `testpass123` (student)

### Run All Bug Validation Tests

```bash
cd backend/api/src/main/python/tests/playwright
./run-bug-validation.sh
```

This script will:
1. Verify both services are running
2. Run CRITICAL severity tests
3. Run HIGH severity tests
4. Run MEDIUM severity tests
5. Generate HTML test report

### Run Individual Test Files

```bash
# CRITICAL severity bugs only
FRONTEND_URL=http://localhost:3001 npx playwright test \
  --config config/playwright.config.js \
  specs/bug-validation/01-critical-data-loading.spec.js \
  --reporter=line --workers=1 --headed

# HIGH severity bugs only
FRONTEND_URL=http://localhost:3001 npx playwright test \
  --config config/playwright.config.js \
  specs/bug-validation/02-high-severity-dialogs.spec.js \
  --reporter=line --workers=1 --headed

# MEDIUM severity bugs only
FRONTEND_URL=http://localhost:3001 npx playwright test \
  --config config/playwright.config.js \
  specs/bug-validation/03-medium-navigation-structure.spec.js \
  --reporter=line --workers=1 --headed
```

### Run Specific Bug Test

```bash
# Test specific bug by test name pattern
FRONTEND_URL=http://localhost:3001 npx playwright test \
  --config config/playwright.config.js \
  --grep "should load Animal Details page without" \
  --reporter=line --workers=1 --headed
```

## Test Configuration

### Visible Browser Mode

All tests run with `--headed` flag so you can:
- See exactly what's happening
- Verify UI interactions visually
- Debug failures more easily
- Build confidence in test accuracy

### Test Execution Options

```bash
# Run with debug mode (step through tests)
FRONTEND_URL=http://localhost:3001 npx playwright test \
  --config config/playwright.config.js \
  specs/bug-validation/ \
  --debug

# Run specific browser only
FRONTEND_URL=http://localhost:3001 npx playwright test \
  --config config/playwright.config.js \
  specs/bug-validation/ \
  --project=chromium \
  --headed

# Generate trace for failed tests
FRONTEND_URL=http://localhost:3001 npx playwright test \
  --config config/playwright.config.js \
  specs/bug-validation/ \
  --trace on
```

## Test Reports

### HTML Report

After test execution, view the detailed HTML report:

```bash
npx playwright show-report backend/reports/playwright/html-report
```

The HTML report includes:
- Test execution timeline
- Screenshots on failure
- Videos of failed tests
- Detailed error messages
- Test duration statistics

### JSON Report

Programmatic access to test results:

```bash
cat backend/reports/playwright/test-results.json | jq '.suites'
```

### JUnit XML Report

For CI/CD integration:

```
backend/reports/playwright/junit-results.xml
```

## Expected Test Results

### Success Criteria

Each test validates both **expected behavior** (what should happen) and **bug absence** (what should NOT happen):

**CRITICAL Tests**:
- Services load data successfully
- No "Failed to fetch" errors
- Backend API returns 200 status codes
- UI displays data or appropriate empty states

**HIGH Tests**:
- Dialog cancel buttons work
- Guardrails persist after dialog interactions
- Authenticated users access chat history
- No "not authenticated" errors for logged-in users

**MEDIUM Tests**:
- Navigation structure is correct
- User roles use proper names
- Department field has correct access control
- No unnecessary UI sections

### Failure Investigation

If tests fail:

1. **Check service health**:
   ```bash
   curl http://localhost:8080/health
   curl http://localhost:3001
   ```

2. **Review test screenshots** in `backend/reports/playwright/test-results/`

3. **Watch test video** to see exact failure point

4. **Check browser console** in headed mode for JavaScript errors

5. **Verify test users** exist and have correct credentials

## Bug Tracking Integration

### Creating Bug Tickets

When a test fails, create a bug ticket with:

- **Test name**: Exact test that failed
- **Expected behavior**: From test description
- **Actual behavior**: From test failure message
- **Screenshot**: From test-results directory
- **Severity**: Based on test file (CRITICAL/HIGH/MEDIUM)
- **Reproduction steps**: From test code

### Regression Prevention

After fixing a bug:

1. Run the specific test to verify the fix
2. Run the entire test suite to prevent regressions
3. Add additional edge case tests if needed
4. Update test documentation if bug revealed gaps

## Test Maintenance

### Updating Tests

When UI changes require test updates:

1. **Locate the test** in the appropriate severity file
2. **Update selectors** to match new UI structure
3. **Verify expectations** still validate the bug absence
4. **Run the updated test** to ensure it passes
5. **Document changes** in git commit message

### Adding New Bug Tests

To add tests for newly discovered bugs:

1. **Determine severity**: CRITICAL/HIGH/MEDIUM/LOW
2. **Add to appropriate file** or create new if needed
3. **Follow BDD pattern**: Given/When/Then structure
4. **Include both positive and negative tests**
5. **Add to bug tracking list** in this document

## Test Quality Standards

### Test Structure

Each test follows this pattern:

```javascript
test('should [expected behavior] when [condition]', async ({ page }) => {
  // Given: Setup and preconditions
  await loginAs(page, 'admin');
  await page.goto(`${FRONTEND_URL}/page`);

  // When: Action being tested
  await page.click('button');

  // Then: Verification of expected behavior
  await expect(page.locator('result')).toBeVisible();

  // And: Verification bug is NOT present
  await expect(page.locator('error')).not.toBeVisible();
});
```

### Test Reliability

Tests are designed to be:
- **Deterministic**: Same inputs produce same results
- **Independent**: Can run in any order
- **Isolated**: Each test cleans up after itself
- **Fast**: Complete in < 30 seconds each
- **Clear**: Failure messages indicate exact problem

## Troubleshooting

### Common Issues

**Tests timeout waiting for elements**:
- Verify services are running on correct ports
- Check network requests in browser DevTools
- Increase timeout if legitimate slow loading

**Authentication failures**:
- Verify test users exist in database
- Check JWT token generation in backend
- Verify frontend stores token correctly

**Selectors not found**:
- Update selectors to match current UI
- Use `data-testid` attributes for stability
- Check element is visible and not covered

**Services not available**:
- Start backend: `make run-api`
- Start frontend: `cd frontend && npm start`
- Verify ports 3001 and 8080 are available

## Success Metrics

### Test Coverage

- **11 bugs**: Comprehensive coverage of all reported issues
- **45+ individual tests**: Multiple tests per bug
- **3 severity levels**: CRITICAL, HIGH, MEDIUM
- **All user roles**: Admin, Parent, Student scenarios

### Validation Quality

- **Visible execution**: All tests run in headed mode
- **BDD structure**: Clear Given/When/Then organization
- **Error handling**: Tests for both success and failure paths
- **Regression prevention**: Tests catch bug reintroduction

### Continuous Improvement

- Regular test maintenance as UI evolves
- New tests for newly discovered bugs
- Performance optimization for test execution
- Integration with CI/CD pipeline

## Related Documentation

- **Playwright Configuration**: `config/playwright.config.js`
- **Test Users Guide**: `fixtures/test-users.js` (if exists)
- **Main Test Suite**: `specs/` directory
- **Test Reports**: `backend/reports/playwright/`

## Contact and Support

For questions or issues with the test suite:

1. Review test code in `specs/bug-validation/`
2. Check Playwright documentation: https://playwright.dev
3. Review test execution videos and screenshots
4. Contact QA team or test maintainer

---

**Last Updated**: October 24th, 2025
**Maintainer**: Quality Engineering Team
**Version**: 1.0.0
