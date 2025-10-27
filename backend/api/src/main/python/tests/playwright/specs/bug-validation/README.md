# Bug Validation Test Suite - Quick Reference

**Session**: October 24th, 2025 8:47 AM | **Branch**: 003-animal-assistant-mgmt

## Quick Start

### 1. Start Services

```bash
# Terminal 1: Backend
make run-api

# Terminal 2: Frontend
cd frontend && npm start
```

### 2. Run Tests

```bash
# From playwright directory
cd backend/api/src/main/python/tests/playwright

# Run all bug validation tests
./run-bug-validation.sh

# OR run individual test files
FRONTEND_URL=http://localhost:3001 npx playwright test \
  --config config/playwright.config.js \
  specs/bug-validation/01-critical-data-loading.spec.js \
  --reporter=line --workers=1 --headed
```

## Test Files

| File | Bugs Tested | Severity |
|------|-------------|----------|
| `01-critical-data-loading.spec.js` | #1-4 | CRITICAL |
| `02-high-severity-dialogs.spec.js` | #5-7 | HIGH |
| `03-medium-navigation-structure.spec.js` | #8-11 | MEDIUM |

## Bug Coverage

### CRITICAL (Bugs #1-4)
- ✓ Assistant Management sub-elements non-functional
- ✓ Animal Details "Failed to fetch" error
- ✓ Chat with Animals "Unable to load animals"
- ✓ Family Groups "Failed to load families"

### HIGH (Bugs #5-7)
- ✓ Create Sandbox Assistant cancel button
- ✓ Guardrails disappearing after dialog close
- ✓ Chat History authentication issues

### MEDIUM (Bugs #8-11)
- ✓ Guardrails in wrong navigation section
- ✓ Incorrect user role names
- ✓ Department field access control
- ✓ Unnecessary "Roles and Permissions" section

## Test Users

| Email | Password | Role |
|-------|----------|------|
| test@cmz.org | testpass123 | admin |
| parent1@test.cmz.org | testpass123 | parent |
| student1@test.cmz.org | testpass123 | student |

## Common Commands

```bash
# Run specific bug test
npx playwright test --grep "Animal Details" --headed

# Debug mode (step through tests)
npx playwright test specs/bug-validation/ --debug

# Chromium only (faster)
npx playwright test --project=chromium --headed

# View last test report
npx playwright show-report ../../../../../../backend/reports/playwright/html-report
```

## Test Structure

Each test follows BDD pattern:

```javascript
test('should [behavior]', async ({ page }) => {
  // Given: Setup
  await loginAs(page, 'admin');

  // When: Action
  await page.click('button');

  // Then: Verification
  await expect(page.locator('result')).toBeVisible();
});
```

## Success Criteria

- ✓ All CRITICAL tests pass
- ✓ All HIGH tests pass
- ✓ All MEDIUM tests pass
- ✓ No regressions in existing functionality
- ✓ Tests run in visible browser mode

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Services not running | Check `make run-api` and `npm start` |
| Test timeout | Increase timeout or check service health |
| Selector not found | Verify UI element exists and is visible |
| Auth failure | Check test user credentials in database |

## Next Steps

1. **Run tests**: Execute full test suite
2. **Fix bugs**: Address failures one by one
3. **Verify fixes**: Re-run tests after fixes
4. **Prevent regression**: Keep tests running in CI/CD

---

For complete documentation, see: `/BUG-VALIDATION-TEST-SUITE.md`
