# Bug Validation Test Execution Guide

**Created**: October 24th, 2025 | **Session**: 8:47 AM | **Branch**: 003-animal-assistant-mgmt

## Executive Summary

This guide provides step-by-step instructions for executing the comprehensive Playwright test suite that validates all 11 reported bugs in the CMZ Animal Assistant Management System.

## Test Suite Overview

### Coverage Statistics

- **Total Bugs Tested**: 11
- **Test Files**: 3
- **Individual Tests**: 45+
- **Severity Levels**: CRITICAL (4), HIGH (3), MEDIUM (4)
- **Execution Mode**: Visible browser (headed)
- **Estimated Runtime**: 15-20 minutes for full suite

### Test Architecture

```
Bug Validation Suite
├── CRITICAL: Data Loading Failures (4 bugs, ~12 tests)
├── HIGH: Dialog Functionality Issues (3 bugs, ~15 tests)
└── MEDIUM: Navigation & Structure Issues (4 bugs, ~18 tests)
```

## Pre-Execution Checklist

### Environment Setup

- [ ] Backend service running at http://localhost:8080
- [ ] Frontend service running at http://localhost:3001
- [ ] Test users exist in database or mock data
- [ ] Node.js and npm installed
- [ ] Playwright dependencies installed

### Service Verification

```bash
# Check backend health
curl http://localhost:8080/health

# Check frontend availability
curl http://localhost:3001

# Verify test users
aws dynamodb get-item \
  --table-name quest-dev-users \
  --key '{"userId":{"S":"test@cmz.org"}}' \
  --profile cmz
```

## Execution Methods

### Method 1: Automated Full Suite (Recommended)

**Best for**: Complete validation, CI/CD integration, regression testing

```bash
cd backend/api/src/main/python/tests/playwright
./run-bug-validation.sh
```

**Expected Output**:
```
╔════════════════════════════════════════════════════════════════╗
║         CMZ Bug Validation Test Suite                         ║
║         Session: October 24th, 2025                            ║
╚════════════════════════════════════════════════════════════════╝

[1/5] Verifying services...
  ✓ Frontend is running at http://localhost:3001
  ✓ Backend is running at http://localhost:8080

[2/5] Running CRITICAL severity tests...
  ✓ Bug #1: Assistant Management sub-elements
  ✓ Bug #2: Animal Details "Failed to fetch"
  ✓ Bug #3: Chat with Animals loading
  ✓ Bug #4: Family Groups loading

[3/5] Running HIGH severity tests...
  ✓ Bug #5: Sandbox dialog cancel button
  ✓ Bug #6: Guardrails persistence
  ✓ Bug #7: Chat History authentication

[4/5] Running MEDIUM severity tests...
  ✓ Bug #8: Guardrails navigation location
  ✓ Bug #9: User role naming
  ✓ Bug #10: Department field access control
  ✓ Bug #11: Roles and Permissions section

[5/5] Generating test report...
  ✓ HTML report generated

╔════════════════════════════════════════════════════════════════╗
║         Bug Validation Test Suite Complete                     ║
╚════════════════════════════════════════════════════════════════╝
```

### Method 2: Individual Test Files

**Best for**: Focused debugging, iterative bug fixing, rapid feedback

```bash
cd backend/api/src/main/python/tests/playwright

# Test CRITICAL bugs only
FRONTEND_URL=http://localhost:3001 npx playwright test \
  --config config/playwright.config.js \
  specs/bug-validation/01-critical-data-loading.spec.js \
  --reporter=line --workers=1 --headed

# Test HIGH severity bugs only
FRONTEND_URL=http://localhost:3001 npx playwright test \
  --config config/playwright.config.js \
  specs/bug-validation/02-high-severity-dialogs.spec.js \
  --reporter=line --workers=1 --headed

# Test MEDIUM severity bugs only
FRONTEND_URL=http://localhost:3001 npx playwright test \
  --config config/playwright.config.js \
  specs/bug-validation/03-medium-navigation-structure.spec.js \
  --reporter=line --workers=1 --headed
```

### Method 3: Specific Bug Testing

**Best for**: Verifying specific bug fixes, targeted validation

```bash
cd backend/api/src/main/python/tests/playwright

# Test Bug #2 (Animal Details "Failed to fetch")
FRONTEND_URL=http://localhost:3001 npx playwright test \
  --config config/playwright.config.js \
  --grep "Animal Details.*Failed to fetch" \
  --reporter=line --workers=1 --headed

# Test Bug #5 (Sandbox dialog cancel)
FRONTEND_URL=http://localhost:3001 npx playwright test \
  --config config/playwright.config.js \
  --grep "Sandbox Assistant dialog cancel" \
  --reporter=line --workers=1 --headed

# Test Bug #9 (User role naming)
FRONTEND_URL=http://localhost:3001 npx playwright test \
  --config config/playwright.config.js \
  --grep "User Role Naming" \
  --reporter=line --workers=1 --headed
```

### Method 4: Debug Mode

**Best for**: Step-by-step test execution, investigating failures

```bash
cd backend/api/src/main/python/tests/playwright

# Debug specific test file
FRONTEND_URL=http://localhost:3001 npx playwright test \
  --config config/playwright.config.js \
  specs/bug-validation/01-critical-data-loading.spec.js \
  --debug

# Debug specific test
FRONTEND_URL=http://localhost:3001 npx playwright test \
  --config config/playwright.config.js \
  --grep "should load Animal Details" \
  --debug
```

**Debug Mode Features**:
- Step through test line by line
- Inspect page state at each step
- Execute commands in browser console
- Modify test execution flow

## Test Execution Workflow

### Standard Execution Flow

```
1. Start Services
   ├─ make run-api (backend on :8080)
   └─ npm start (frontend on :3001)

2. Navigate to Test Directory
   └─ cd backend/api/src/main/python/tests/playwright

3. Execute Tests
   └─ ./run-bug-validation.sh (full suite)
      OR
   └─ npx playwright test [options] (targeted)

4. Review Results
   ├─ Console output (real-time)
   ├─ Browser window (visible execution)
   └─ HTML report (post-execution)

5. Investigate Failures
   ├─ Screenshots (test-results/)
   ├─ Videos (test-results/)
   └─ Error messages (console/report)

6. Fix Bugs
   └─ Address root causes identified

7. Verify Fixes
   └─ Re-run failed tests

8. Regression Check
   └─ Run full suite to ensure no new bugs
```

### Iterative Bug Fixing Workflow

```
FOR EACH BUG:
  1. Run specific bug test
  2. IF test fails:
     a. Review failure details
     b. Fix underlying bug
     c. Re-run test
     d. REPEAT until test passes
  3. Run full test file for that severity
  4. IF new failures:
     a. Investigate regression
     b. Fix regression
     c. Re-run tests
  5. Run full test suite
  6. Commit fix with test validation
```

## Understanding Test Results

### Success Indicators

**Console Output**:
```
✓ should load Active Assistants section without errors (2.5s)
✓ should open Create Assistant dialog successfully (1.8s)
✓ should load Personality Templates section without errors (2.1s)

3 passed (7.2s)
```

**Browser Behavior**:
- Pages load smoothly
- No error messages visible
- Expected elements appear
- User interactions work correctly

### Failure Indicators

**Console Output**:
```
✗ should load Animal Details page without "Failed to fetch" error (5.2s)

  Error: Timed out 5000ms waiting for expect(locator).not.toBeVisible()

  Locator: text=/failed to fetch/i
  Expected: not visible
  Received: visible at <div class="error-message">Failed to fetch</div>
```

**Browser Behavior**:
- Error messages displayed
- Elements not found or not visible
- Unexpected page states
- Network request failures

### Analyzing Failures

**For Each Failed Test**:

1. **Review Console Error**:
   - Error type (timeout, assertion failure, network error)
   - Expected vs actual behavior
   - Element selector that failed

2. **Check Screenshot**:
   - Location: `backend/reports/playwright/test-results/`
   - Shows exact UI state at failure
   - Reveals visual issues not obvious in code

3. **Watch Video**:
   - Full test execution recording
   - Shows interaction sequence
   - Identifies timing issues

4. **Inspect Network Requests**:
   - Check browser DevTools (if headed mode)
   - Look for failed API calls
   - Verify request/response payloads

5. **Verify Service Health**:
   - Backend responding correctly
   - Frontend loading properly
   - Database accessible

## Test Reports

### HTML Report

**View Report**:
```bash
npx playwright show-report backend/reports/playwright/html-report
```

**Report Contents**:
- Test execution timeline
- Pass/fail statistics
- Individual test details
- Screenshots and videos
- Error stack traces
- Test duration metrics

### JSON Report

**Programmatic Access**:
```bash
# View test results as JSON
cat backend/reports/playwright/test-results.json | jq '.'

# Get only failed tests
cat backend/reports/playwright/test-results.json | jq '.suites[].specs[] | select(.ok == false)'

# Get test statistics
cat backend/reports/playwright/test-results.json | jq '{
  total: .suites[].specs | length,
  passed: [.suites[].specs[] | select(.ok == true)] | length,
  failed: [.suites[].specs[] | select(.ok == false)] | length
}'
```

### JUnit XML Report

**Location**: `backend/reports/playwright/junit-results.xml`

**Use Cases**:
- CI/CD integration (GitLab, Jenkins, etc.)
- Test trend tracking
- Quality metrics dashboards

## Troubleshooting

### Common Issues and Solutions

#### Issue: "Cannot find module 'playwright'"

**Cause**: Playwright not installed

**Solution**:
```bash
cd backend/api/src/main/python/tests/playwright
npm install
npx playwright install
```

#### Issue: "Connection refused" errors

**Cause**: Services not running

**Solution**:
```bash
# Check if services are running
lsof -i :8080  # Backend
lsof -i :3001  # Frontend

# Start services if needed
make run-api   # Backend
cd frontend && npm start  # Frontend
```

#### Issue: "Test timeout after 30000ms"

**Cause**: Slow service responses or network issues

**Solution**:
```bash
# Increase timeout in config
# Edit config/playwright.config.js:
timeout: 60 * 1000,  # 60 seconds

# OR check service performance
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8080/animal
```

#### Issue: "Element not found" errors

**Cause**: UI changes or incorrect selectors

**Solution**:
1. Run test in debug mode to inspect page
2. Verify element exists with correct attributes
3. Update selector in test file
4. Re-run test to verify fix

#### Issue: Authentication failures

**Cause**: Test users don't exist or wrong credentials

**Solution**:
```bash
# Verify test user exists
aws dynamodb get-item \
  --table-name quest-dev-users \
  --key '{"userId":{"S":"test@cmz.org"}}' \
  --profile cmz

# If missing, create test user via API or backend
```

## Performance Optimization

### Parallel Execution (Advanced)

**Current**: Tests run sequentially (`--workers=1`)
**Reason**: Shared authentication state and browser context

**To Enable Parallel Execution**:
```bash
# Run with multiple workers (use cautiously)
FRONTEND_URL=http://localhost:3001 npx playwright test \
  --config config/playwright.config.js \
  specs/bug-validation/ \
  --workers=3
```

**Note**: May cause race conditions with shared state

### Selective Test Execution

```bash
# Run only CRITICAL tests (fastest feedback on major issues)
./run-bug-validation.sh | grep -A 100 "CRITICAL"

# Run only tests likely to fail (based on recent changes)
npx playwright test --grep "Animal Details|Chat History"
```

### Headless Mode (CI/CD)

```bash
# Run without visible browser (faster)
FRONTEND_URL=http://localhost:3001 npx playwright test \
  --config config/playwright.config.js \
  specs/bug-validation/ \
  --reporter=line --workers=1
```

**Trade-off**: Faster execution but less visibility during failures

## CI/CD Integration

### GitLab CI Example

```yaml
playwright-bug-validation:
  stage: test
  script:
    - make run-api &  # Start backend in background
    - cd frontend && npm start &  # Start frontend in background
    - sleep 30  # Wait for services to start
    - cd backend/api/src/main/python/tests/playwright
    - ./run-bug-validation.sh
  artifacts:
    when: always
    paths:
      - backend/reports/playwright/
    reports:
      junit: backend/reports/playwright/junit-results.xml
```

### GitHub Actions Example

```yaml
- name: Run Bug Validation Tests
  run: |
    make run-api &
    cd frontend && npm start &
    sleep 30
    cd backend/api/src/main/python/tests/playwright
    ./run-bug-validation.sh
```

## Best Practices

### Running Tests

1. **Always start fresh**: Restart services before full test runs
2. **Use visible browser**: Keep `--headed` for initial runs
3. **Run incrementally**: Test by severity level, then full suite
4. **Review failures immediately**: Don't wait until end
5. **Document unexpected behavior**: Note any new bugs found

### Debugging Tests

1. **Start with console output**: Often contains root cause
2. **Use debug mode**: Step through failing tests
3. **Check screenshots/videos**: Visual confirmation of issue
4. **Verify services**: Ensure backend/frontend are healthy
5. **Isolate the problem**: Run minimal reproduction case

### Maintaining Tests

1. **Update selectors**: When UI changes, update tests promptly
2. **Add new tests**: For newly discovered bugs
3. **Remove obsolete tests**: For features that no longer exist
4. **Document changes**: Clear commit messages for test updates
5. **Keep tests fast**: Optimize slow tests

## Success Criteria

### Definition of Done

- [ ] All CRITICAL tests pass
- [ ] All HIGH tests pass
- [ ] All MEDIUM tests pass
- [ ] No test flakiness (consistent pass/fail)
- [ ] HTML report generated successfully
- [ ] All bugs validated and documented

### Test Quality Metrics

- **Pass Rate**: ≥ 95% (target 100%)
- **Execution Time**: < 20 minutes for full suite
- **Flakiness Rate**: < 5% (tests failing intermittently)
- **Bug Detection**: 100% of reported bugs caught

## Next Steps After Execution

### If All Tests Pass

1. **Document success**: Note in session history
2. **Update bug tracker**: Mark bugs as validated
3. **Prepare for deployment**: Tests confirm system ready
4. **Schedule next run**: Regular regression testing

### If Tests Fail

1. **Triage failures**: Group by root cause
2. **Prioritize fixes**: CRITICAL → HIGH → MEDIUM
3. **Fix bugs iteratively**: One at a time, re-test each
4. **Verify no regressions**: Run full suite after all fixes
5. **Update documentation**: Note any new bugs discovered

## Related Documentation

- **Complete Test Suite Documentation**: `/BUG-VALIDATION-TEST-SUITE.md`
- **Quick Reference**: `specs/bug-validation/README.md`
- **Playwright Config**: `config/playwright.config.js`
- **Test Files**: `specs/bug-validation/*.spec.js`

---

**Maintained By**: Quality Engineering Team
**Last Updated**: October 24th, 2025
**Version**: 1.0.0
