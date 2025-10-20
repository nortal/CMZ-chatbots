# TEST-ORCHESTRATION-ADVICE.md

## Overview
Best practices, troubleshooting guide, and lessons learned for orchestrating comprehensive test execution across multiple test types with intelligent error classification.

## Critical Directives

### 🚨 NEVER Skip Error Investigation
**The Problem**: "Not implemented" or 501 errors are often OpenAPI artifacts, not true regressions.

**The Rule**:
1. **ALWAYS read ENDPOINT-WORK-ADVICE.md** before declaring regression
2. Check if handler exists in impl/ modules
3. Verify controller routing is correct
4. Classify error (true regression vs. artifact)

**Why This Matters**:
- OpenAPI regeneration frequently disconnects handlers from controllers
- Tests may pass with "not implemented" placeholder code
- False regressions waste developer time and erode trust in testing

### 🎯 Test Orchestration is NOT Test Execution
**Test Orchestration**:
- Coordinates multiple test types
- Delegates to specialized verifiers
- Analyzes errors across test types
- Classifies failures (true vs. artifact)
- Generates comprehensive reports

**Test Execution**:
- Runs specific test suite
- Reports pass/fail
- Shows stack traces

**Don't Confuse**: Orchestration is strategic coordination, execution is tactical running.

## Orchestration Workflow

### Phase 1: Coverage Analysis
**Purpose**: Understand what tests exist before running them

**Best Practices**:
```python
# Good - Comprehensive coverage check
Task(
    subagent_type="test-coverage-verifier",
    prompt="""Analyze coverage for:
    - Unit tests (all impl/ modules have test_*.py)
    - Integration tests (all endpoints have integration tests)
    - E2E tests (all user journeys covered)
    - Validation tests (all critical features validated)

    For each gap, specify:
    - What's missing (endpoint, feature, edge case)
    - Priority (critical, important, nice-to-have)
    - Estimated effort to add
    """
)
```

```python
# Bad - Vague coverage request
Task(
    subagent_type="test-coverage-verifier",
    prompt="Check test coverage"
)
```

**Common Gaps**:
- DynamoDB verification missing from integration tests
- Error scenarios untested (400, 401, 404, 500)
- Edge cases not covered (null, empty, boundaries)
- Cross-browser E2E tests missing

### Phase 2: Parallel Test Execution
**Purpose**: Run all test types efficiently with delegation

**Parallel Execution Pattern**:
```python
# CORRECT - Parallel independent verifications
from concurrent.futures import ThreadPoolExecutor

tasks = [
    Task(subagent_type="backend-feature-verifier", ...),
    Task(subagent_type="frontend-feature-verifier", ...),
    Task(subagent_type="persistence-verifier", ...)
]

# All three run simultaneously
```

**Sequential Execution Anti-Pattern**:
```python
# WRONG - Sequential execution wastes time
Task(subagent_type="backend-feature-verifier", ...)  # Wait...
Task(subagent_type="frontend-feature-verifier", ...)  # Wait...
Task(subagent_type="persistence-verifier", ...)  # Wait...
```

**When to Use Sequential**:
- Output of one phase feeds into next
- Resource constraints (single test environment)
- Debugging specific failure chain

### Phase 3: Root Cause Analysis
**Purpose**: Understand WHY tests failed, not just THAT they failed

**Investigation Priority**:
1. **Critical Errors First**: Authentication failures, data loss, security issues
2. **High-Impact Errors**: Core user journeys broken
3. **"Not Implemented" Errors**: ALWAYS investigate with skepticism
4. **Low-Impact Errors**: Edge cases, non-critical features

**Evidence Collection**:
```bash
# For each error, collect:

# 1. Error message and stack trace
grep -A 20 "ERROR" test_results.log

# 2. Implementation check
find backend/api/src/main/python/openapi_server/impl -name "*.py" -exec grep -l "handle_<endpoint>" {} \;

# 3. Controller routing check
grep -A 10 "def <endpoint_name>" backend/api/src/main/python/openapi_server/controllers/*.py

# 4. Git history
git log --oneline --all --since="7 days ago" --grep="generate-api"

# 5. Manual verification
curl -X POST http://localhost:8080/api/v1/<endpoint> -H "Content-Type: application/json" -d '{...}'
```

**Root Cause Analyst Delegation**:
```python
Task(
    subagent_type="root-cause-analyst",
    description="Investigate test failures",
    prompt="""For each failure, determine root cause using evidence:

Failure: POST /animal returns 501 "Not Implemented"

Investigation Steps:
1. Read ENDPOINT-WORK-ADVICE.md (✅ Done)
2. Check impl/animals.py for handle_animal_post (✅ Exists)
3. Check controllers/animal_controller.py routing (❌ Routes to generic handler)
4. Git history check (✅ OpenAPI regeneration 2 days ago)

Classification: OPENAPI ARTIFACT
- Handler exists and is complete
- Controller routing broken by regeneration
- Fix: Run `make post-generate`
- Prevention: Add post-generate to CI/CD

Evidence:
- impl/animals.py:245 - handle_animal_post() complete implementation
- controllers/animal_controller.py:123 - routes to generic util.deserialize()
- git log shows "make generate-api" on 2025-01-12
"""
)
```

### Phase 4: Error Classification
**Purpose**: Distinguish true regressions from artifacts

**Classification Framework**:

| Error Type | Handler Exists? | Controller Routes Correctly? | Recent Regen? | Classification |
|------------|----------------|------------------------------|---------------|----------------|
| ✅ | ✅ | ✅ | Any | **Test Artifact** (test config issue) |
| ✅ | ❌ | Any | Any | **True Regression** (implementation broken) |
| ✅ | ✅ | ❌ | ✅ | **OpenAPI Artifact** (regeneration broke routing) |
| ✅ | ✅ | ❌ | ❌ | **True Regression** (routing manually broken) |
| ❌ | N/A | N/A | ❌ | **True Regression** (implementation never added) |
| ❌ | N/A | N/A | ✅ | **OpenAPI Artifact** (regeneration deleted handler) |

**Example Classifications**:

**TRUE REGRESSION**:
```
Error: POST /family returns 500 "AttributeError: 'NoneType' object has no attribute 'get'"
Handler: impl/family.py:handle_family_post() exists
Controller: Routes correctly to impl.family.handle_family_post
Recent Regen: No
Investigation: Code has null pointer bug in line 67
Classification: TRUE REGRESSION - Code bug in implementation
```

**OPENAPI ARTIFACT**:
```
Error: PATCH /animal_config returns 501 "Not Implemented"
Handler: impl/animals.py:handle_animal_config_patch() exists and works
Controller: Routes to generic util.deserialize() instead of impl handler
Recent Regen: Yes (2 days ago)
Investigation: make generate-api disconnected handler from controller
Classification: OPENAPI ARTIFACT - Regeneration broke routing
Fix: make post-generate
```

**TEST ARTIFACT**:
```
Error: DELETE /animal/{id} returns 401 "Unauthorized"
Handler: impl/animals.py:handle_animal_delete() exists
Controller: Routes correctly
Recent Regen: No
Manual Test: curl works with proper auth headers
Investigation: Test not sending auth headers
Classification: TEST ARTIFACT - Test setup missing authentication
```

### Phase 5: Reporting and Documentation
**Purpose**: Communicate results clearly and preserve knowledge

**Report Structure**:
```json
{
  "test_orchestration_summary": {
    "execution_summary": {
      "total_tests": 500,
      "passed": 485,
      "failed": 15,
      "pass_rate": "97.0%",
      "execution_time": "12m 34s"
    },
    "coverage_analysis": {
      "unit_tests": {
        "coverage": "92%",
        "modules_covered": 45,
        "modules_total": 49,
        "critical_gaps": ["utils/jwt_utils.py edge cases"]
      },
      "integration_tests": {
        "coverage": "88%",
        "endpoints_covered": 42,
        "endpoints_total": 48,
        "critical_gaps": ["DELETE /animal/{id}", "POST /knowledge"]
      },
      "e2e_tests": {
        "coverage": "85%",
        "user_journeys_covered": 17,
        "user_journeys_total": 20,
        "critical_gaps": ["Parent bulk operations", "Student chat export"]
      }
    },
    "error_classification": {
      "true_regressions": [
        {
          "endpoint": "POST /family",
          "error": "500 AttributeError",
          "root_cause": "Null pointer in line 67",
          "priority": "CRITICAL",
          "fix_required": true
        }
      ],
      "openapi_artifacts": [
        {
          "endpoint": "PATCH /animal_config",
          "error": "501 Not Implemented",
          "root_cause": "Regeneration disconnected handler",
          "fix": "make post-generate",
          "prevention": "Add post-generate to CI/CD"
        }
      ],
      "test_artifacts": [
        {
          "endpoint": "DELETE /animal/{id}",
          "error": "401 Unauthorized",
          "root_cause": "Test missing auth headers",
          "fix": "Update test setup"
        }
      ]
    },
    "dynamodb_verification": {
      "tables_verified": [
        "quest-dev-family",
        "quest-dev-animal",
        "quest-dev-conversation"
      ],
      "persistence_verified": true,
      "issues": []
    },
    "recommendations": [
      "Add unit tests for jwt_utils.py edge cases",
      "Implement DELETE /animal/{id} integration test",
      "Add POST /knowledge E2E test",
      "Automate post-generate in CI/CD to prevent OpenAPI artifacts"
    ]
  }
}
```

**Teams Report Best Practices**:
- Use Adaptive Cards for readability
- Color-code sections (green=pass, red=fail, yellow=investigate)
- Include actionable recommendations
- Link to detailed logs
- Highlight true regressions vs. artifacts

**Documentation for Test Generation**:
```markdown
# Test Generation Notes - 2025-01-14

## Critical Coverage Gaps
1. **DELETE /animal/{id}** - No integration test exists
   - Priority: HIGH
   - User Impact: Cannot delete test animals
   - Test Type Needed: Integration test with DynamoDB verification

2. **jwt_utils.py edge cases** - Token generation untested for expired tokens
   - Priority: MEDIUM
   - Security Impact: Token validation bypasses possible
   - Test Type Needed: Unit tests for all edge cases

## False Regression Indicators Detected
1. **PATCH /animal_config** - OpenAPI artifact (handler exists, routing broken)
   - Root Cause: make generate-api disconnected handler
   - Prevention: Add `make post-generate` to CI/CD
   - Documentation: Update OPENAPI-ADVICE.md

## Test Authenticity Concerns
1. **POST /conversation tests** - Return 200 but don't verify DynamoDB
   - Issue: Tests check status code only, not persistence
   - Fix Needed: Add DynamoDB verification to all POST /conversation tests
   - Pattern: All POST endpoints should verify persistence
```

## Common Issues and Solutions

### Issue 1: "Not Implemented" Errors Everywhere
**Symptoms**:
- Multiple endpoints returning 501
- All tests failing with "Not Implemented"
- Manual cURL also returns 501

**Root Cause**: OpenAPI regeneration without post-generate fixes

**Solution**:
```bash
# Fix immediately
cd backend/api
make post-generate

# Verify fix
make run-api
curl -X GET http://localhost:8080/api/v1/families

# Prevention
# Add to .github/workflows/ci.yml:
- name: OpenAPI Code Generation
  run: |
    cd backend/api
    make generate-api
    make post-generate  # CRITICAL - Never skip this
```

### Issue 2: Orchestration Takes Too Long
**Symptoms**:
- Orchestration runs for >30 minutes
- Sequential execution of independent tests
- Timeout errors in CI/CD

**Root Cause**: Not using parallel delegation

**Solution**:
```python
# BEFORE - Sequential (slow)
backend_result = delegate_to_backend_verifier()  # 10 min
frontend_result = delegate_to_frontend_verifier()  # 10 min
persistence_result = delegate_to_persistence_verifier()  # 8 min
# Total: 28 minutes

# AFTER - Parallel (fast)
from concurrent.futures import ThreadPoolExecutor, as_completed

tasks = {
    executor.submit(delegate_to_backend_verifier): "backend",
    executor.submit(delegate_to_frontend_verifier): "frontend",
    executor.submit(delegate_to_persistence_verifier): "persistence"
}

results = {}
for future in as_completed(tasks):
    name = tasks[future]
    results[name] = future.result()
# Total: 10 minutes (slowest task)
```

### Issue 3: Too Many False Positives
**Symptoms**:
- "Not implemented" errors that resolve after restart
- Tests fail in CI but pass locally
- Errors disappear without code changes

**Root Cause**: Not investigating errors thoroughly

**Solution**:
```python
# MANDATORY investigation for "not implemented" errors
def investigate_not_implemented(endpoint, error):
    # 1. Read advice documentation
    advice = read_file("ENDPOINT-WORK-ADVICE.md")

    # 2. Check implementation
    handler_exists = check_impl_exists(endpoint)

    # 3. Check controller routing
    routing_correct = check_controller_routing(endpoint)

    # 4. Check git history
    recent_regen = check_recent_regeneration()

    # 5. Classify
    if handler_exists and not routing_correct and recent_regen:
        return "OPENAPI_ARTIFACT", "Run make post-generate"
    elif not handler_exists and not recent_regen:
        return "TRUE_REGRESSION", "Implementation missing"
    else:
        return "TEST_ARTIFACT", "Investigate test setup"
```

### Issue 4: DynamoDB Verification Missing
**Symptoms**:
- Tests pass but data not persisted
- Manual checks show empty DynamoDB tables
- API returns 200 but nothing saved

**Root Cause**: Tests only check HTTP status, not persistence

**Solution**:
```python
# BAD - Only checks status
def test_create_family():
    response = api_client.post('/families', data=test_family)
    assert response.status_code == 201  # Not enough!

# GOOD - Verifies persistence
def test_create_family(dynamodb_table):
    # Act
    response = api_client.post('/families', data=test_family)
    assert response.status_code == 201

    # CRITICAL - Verify persistence
    family_id = response.json()['familyId']
    db_item = dynamodb_table.get_item(Key={'familyId': family_id})

    assert 'Item' in db_item, "Family not found in DynamoDB!"
    assert db_item['Item']['familyName'] == test_family['familyName']
    assert db_item['Item']['parentEmail'] == test_family['parentEmail']
```

### Issue 5: Coverage Report Inaccurate
**Symptoms**:
- Coverage shows 95% but obvious gaps exist
- Critical features show as "covered" but have no tests
- Coverage drops after adding tests

**Root Cause**: Coverage tool measures code execution, not feature coverage

**Solution**:
```python
# Use feature-based coverage, not code coverage

# Code Coverage (Misleading):
# "95% of lines executed" - but which features?

# Feature Coverage (Accurate):
coverage_map = {
    "Authentication": {
        "login_success": "✅ Covered",
        "login_failure": "✅ Covered",
        "token_validation": "❌ Not Covered",
        "token_refresh": "❌ Not Covered"
    },
    "Family Management": {
        "create_family": "✅ Covered",
        "update_family": "✅ Covered",
        "delete_family": "❌ Not Covered",
        "list_families": "✅ Covered"
    }
}
```

## Performance Optimization

### Parallel Execution
**Guideline**: Any test type that doesn't depend on another should run in parallel

**Independent Test Types** (Run in Parallel):
- Unit tests (no external dependencies)
- Integration tests (each endpoint isolated)
- Frontend E2E tests (separate browser instances)
- Persistence verification (read-only checks)

**Dependent Test Types** (Run Sequentially):
- Data setup → Tests using that data
- Service startup → Health checks → Tests
- Cleanup operations (must wait for tests to complete)

### Resource Management
**Test Environment Limits**:
- Max concurrent Playwright browsers: 5
- Max concurrent DynamoDB operations: 10
- Max concurrent API requests: 20

**Batch Sizing**:
```python
# Good - Batched execution
def run_integration_tests(endpoints):
    batch_size = 10
    for i in range(0, len(endpoints), batch_size):
        batch = endpoints[i:i+batch_size]
        results = run_parallel(batch)
        yield results

# Bad - All at once (resource exhaustion)
def run_integration_tests(endpoints):
    return run_parallel(endpoints)  # 50+ concurrent!
```

### Caching Strategies
```python
# Cache expensive operations
cache = {}

def get_coverage_analysis():
    if 'coverage' in cache:
        age = time.time() - cache['coverage']['timestamp']
        if age < 300:  # 5 minutes
            return cache['coverage']['data']

    # Expensive operation
    coverage = analyze_all_tests()
    cache['coverage'] = {
        'timestamp': time.time(),
        'data': coverage
    }
    return coverage
```

## Integration with CI/CD

### GitHub Actions Example
```yaml
name: Test Orchestration

on:
  pull_request:
  push:
    branches: [main, dev]

jobs:
  orchestrate-tests:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Setup Environment
        run: |
          cd backend/api
          make venv-api
          make install-api

      - name: OpenAPI Generation
        run: |
          cd backend/api
          make generate-api
          make post-generate  # CRITICAL

      - name: Start Services
        run: |
          scripts/start_development_environment.sh
          scripts/wait_for_healthy.sh

      - name: Run Test Orchestration
        run: |
          /orchestrate-tests

      - name: Upload Results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: /tmp/test_orchestration_results.json

      - name: Send Teams Notification
        if: always()
        run: |
          python3 scripts/send_teams_report.py custom \
            --data /tmp/test_orchestration_results.json
        env:
          TEAMS_WEBHOOK_URL: ${{ secrets.TEAMS_WEBHOOK_URL }}
```

## Success Metrics

### Execution Metrics
- **Total Execution Time**: <15 minutes for full orchestration
- **Test Pass Rate**: ≥95% (excluding known issues)
- **Parallel Efficiency**: ≥60% (parallel time vs. sequential time)

### Quality Metrics
- **Coverage Completeness**: ≥90% feature coverage across all test types
- **DynamoDB Verification**: 100% of integration tests verify persistence
- **Error Classification**: 100% of errors classified (true vs. artifact)
- **False Positive Rate**: <5% (errors initially marked as regression but later reclassified)

### Reporting Metrics
- **Teams Notification Success**: 100% (all reports delivered)
- **Report Clarity**: All stakeholders understand status without asking questions
- **Actionability**: All recommendations have specific next steps
- **Documentation**: All artifacts and false positives documented

## References
- `.claude/commands/orchestrate-tests.md` - Orchestration command
- `TEST-GENERATION-ADVICE.md` - Test generation best practices
- `ENDPOINT-WORK-ADVICE.md` - OpenAPI generation patterns
- `VALIDATE-*-ADVICE.md` - Individual validation guides
- `TEAMS-REPORTING-ADVICE.md` - Teams notification formatting
