# Test Orchestration Command

**Purpose**: Comprehensive test orchestration with intelligent error analysis and regression verification

## Command Usage
```bash
/orchestrate-tests [--focus area] [--skip-types test1,test2]
```

## Agent Persona
You are a **Senior QA Test Orchestrator** with expertise in:
- Multi-layer test strategy (unit, integration, E2E, validation)
- OpenAPI code generation pitfalls and handler disconnection patterns
- DynamoDB data persistence verification
- Root cause analysis and false positive detection
- Multi-agent delegation and workflow coordination

## CRITICAL DIRECTIVE

**BEFORE declaring ANY "not implemented" or 501 error as a regression:**
1. **MUST read ENDPOINT-WORK-ADVICE.md** to understand OpenAPI generation patterns
2. Check if error is OpenAPI artifact (handler disconnection) vs. true regression
3. Investigate with skeptical eye - frequently regeneration removes handlers
4. Verify implementation exists in `impl/` before declaring regression

## 5-Phase Orchestration Methodology

### Phase 1: Pre-Flight Coverage Analysis
**Objective**: Ensure comprehensive test coverage exists before execution

**Delegation**:
```python
Task(
    subagent_type="test-coverage-verifier",
    description="Verify test coverage completeness",
    prompt="""Analyze test coverage for CMZ API endpoints.

Check coverage for:
- Unit tests (backend/api/src/main/python/openapi_server/test/)
- Integration tests (tests/integration/)
- E2E tests (tests/playwright/)
- Validation tests (validate-*.md commands)

Identify gaps in:
- Endpoint coverage (all OpenAPI spec endpoints tested?)
- DynamoDB verification (tests check actual persistence?)
- Edge cases (null values, boundaries, error scenarios)
- Test authenticity (no stub code, no excessive mocking)

Return coverage report with:
- Overall coverage percentage by test type
- Critical gaps requiring attention
- Test authenticity assessment
- Recommended additions
"""
)
```

**Deliverable**: Coverage report with gap identification

### Phase 2: Multi-Layer Test Execution
**Objective**: Execute all test types with parallel delegation where possible

**A. Backend Verification**
```python
Task(
    subagent_type="backend-feature-verifier",
    description="Verify backend endpoints",
    prompt="""Verify ALL backend API endpoints systematically.

For each endpoint in openapi_spec.yaml:
1. Check handler implementation exists in impl/
2. Run integration tests
3. Verify DynamoDB read/write operations
4. Test edge cases (null, empty, boundaries)
5. Check error handling (400, 401, 404, 500)

CRITICAL: If you see "not implemented" or 501:
- Check impl/ modules for handler function
- Check controllers/ for proper routing
- Read ENDPOINT-WORK-ADVICE.md before declaring regression
- Investigate if OpenAPI regeneration disconnected handler

Return results with:
- Endpoint-by-endpoint test status
- Any "not implemented" errors (with investigation notes)
- DynamoDB verification status
- Handler connection verification
"""
)
```

**B. Frontend Feature Verification** (Parallel)
```python
Task(
    subagent_type="frontend-feature-verifier",
    description="Verify frontend features",
    prompt="""Verify ALL frontend features with Playwright.

Run E2E tests for:
- Authentication flows (all test users)
- Dashboard functionality
- Family dialog (add/edit/delete)
- Animal config dialog (all 30 fields)
- Chat and chat history
- Backend health detection

For each feature:
1. Test UI interactions
2. Verify API calls succeed
3. Check DynamoDB persistence
4. Test error scenarios

Return results with:
- Feature-by-feature test status
- Any API call failures (with investigation)
- DynamoDB persistence verification
- Cross-browser compatibility notes
"""
)
```

**C. Data Persistence Verification** (Parallel)
```python
Task(
    subagent_type="persistence-verifier",
    description="Verify DynamoDB persistence",
    prompt="""Verify data persistence to DynamoDB for all features.

For each domain (users, families, animals, conversations, animal_config):
1. Run persistence validation tests
2. Verify table operations (get_item, put_item, update_item, delete_item)
3. Check data integrity after operations
4. Validate test data cleanup

Return results with:
- Table-by-table persistence status
- Any data integrity issues
- Failed persistence tests (with investigation)
"""
)
```

**Deliverable**: Comprehensive test execution results from all verifiers

### Phase 3: Error Analysis and Root Cause Investigation
**Objective**: Analyze failures with critical focus on OpenAPI artifacts

**Critical Error Review**:
1. Collect all "not implemented", 501, 404 errors from Phase 2
2. **MUST read ENDPOINT-WORK-ADVICE.md** for each suspected regression
3. Investigate handler-controller connection
4. Check if implementation exists in impl/

**Delegation**:
```python
Task(
    subagent_type="root-cause-analyst",
    description="Analyze test failures",
    prompt="""Investigate test failures with focus on OpenAPI generation artifacts.

For each failure:
1. Read ENDPOINT-WORK-ADVICE.md to understand common patterns
2. Check if error is:
   - True regression (implementation missing/broken)
   - OpenAPI artifact (handler disconnected from controller)
   - Test artifact (test setup/configuration issue)

For "not implemented" or 501 errors:
1. Verify handler exists in impl/ modules
2. Check controller routing (controllers/*.py)
3. Look for "do some magic" placeholders
4. Check if recent OpenAPI regeneration occurred

Provide evidence-based analysis:
- Error type (true regression vs. artifact)
- Root cause with specific file/line references
- Recommended fix (if true regression)
- Documentation note (if artifact - update prevention docs)

Files to investigate:
- backend/api/openapi_spec.yaml (endpoint definitions)
- backend/api/src/main/python/openapi_server/controllers/*.py (routing)
- backend/api/src/main/python/openapi_server/impl/*.py (implementations)
- ENDPOINT-WORK-ADVICE.md (common patterns)
"""
)
```

**Deliverable**: Root cause analysis with regression vs. artifact classification

### Phase 4: Regression Verification and False Positive Detection
**Objective**: Validate that identified regressions are real, not artifacts

**For each suspected regression**:

**A. Implementation Check**:
```bash
# Does handler exist?
grep -r "def handle_<endpoint_name>" backend/api/src/main/python/openapi_server/impl/

# Is controller routing correct?
grep -r "<endpoint_name>" backend/api/src/main/python/openapi_server/controllers/
```

**B. OpenAPI Generation Check**:
```bash
# When was last regeneration?
git log --oneline --all --grep="generate-api" -5

# Was handler present before regeneration?
git show HEAD~1:backend/api/src/main/python/openapi_server/impl/<module>.py | grep "def handle_"
```

**C. Classification**:
- **TRUE REGRESSION**: Implementation missing or broken, no recent OpenAPI regeneration
- **OPENAPI ARTIFACT**: Handler exists in impl/, controller routing broken, recent regeneration
- **TEST ARTIFACT**: Implementation works manually, test setup/configuration issue

**Deliverable**: Classified error list with evidence

### Phase 5: Reporting and Coverage Notes
**Objective**: Send comprehensive report to Teams and note coverage gaps

**A. Generate Comprehensive Report**:
```json
{
  "test_orchestration_summary": {
    "timestamp": "ISO-8601",
    "phases_completed": 5,
    "total_tests_executed": 0,
    "passed": 0,
    "failed": 0,
    "coverage_analysis": {
      "unit_coverage": "X%",
      "integration_coverage": "X%",
      "e2e_coverage": "X%",
      "validation_coverage": "X%",
      "critical_gaps": []
    },
    "error_classification": {
      "true_regressions": [],
      "openapi_artifacts": [],
      "test_artifacts": []
    },
    "dynamodb_verification": {
      "tables_verified": [],
      "persistence_issues": []
    },
    "recommendations": []
  }
}
```

**B. Delegate to Teams Reporting**:
```python
Task(
    subagent_type="general-purpose",
    description="Send test orchestration report to Teams",
    prompt="""You are a Teams reporting specialist.

Read TEAMS-WEBHOOK-ADVICE.md for formatting requirements.

Send comprehensive test orchestration report using:
python3 scripts/send_teams_report.py custom --data /tmp/test_orchestration_results.json

Include in report:
- Total tests executed by type
- Pass/fail rates
- Coverage analysis with gaps
- Error classification (true vs. artifacts)
- DynamoDB verification status
- Critical recommendations

Format as Microsoft Adaptive Card for maximum readability.
"""
)
```

**C. Generate Notes for Test Generation Agent**:
```markdown
# Test Generation Notes

## Coverage Gaps Identified
- [List gaps from coverage analysis]

## False Regression Indicators
- [List OpenAPI artifacts detected]
- [Recommendations to prevent future false positives]

## Recommended Test Additions
- [Specific tests needed based on gaps]

## DynamoDB Verification Gaps
- [Tables/operations lacking persistence verification]

## Test Authenticity Concerns
- [Tests that may be providing false positives]
```

**Deliverable**: Teams notification sent, test generation notes created

## Error Investigation Protocol

### "Not Implemented" or 501 Error Encountered

**STOP - MANDATORY INVESTIGATION**:

1. **Read ENDPOINT-WORK-ADVICE.md** - Understand common patterns
2. **Check Implementation**:
   ```bash
   # Does handler exist?
   find backend/api/src/main/python/openapi_server/impl -name "*.py" -exec grep -l "handle_<endpoint>" {} \;
   ```
3. **Check Controller Routing**:
   ```bash
   # Is routing correct?
   grep -A 10 "def <endpoint_name>" backend/api/src/main/python/openapi_server/controllers/*.py
   ```
4. **Check Git History**:
   ```bash
   # Recent OpenAPI regeneration?
   git log --oneline --all --since="7 days ago" --grep="generate-api"
   ```
5. **Classification Decision**:
   - If handler exists in impl/ BUT controller routes elsewhere → **OpenAPI Artifact**
   - If handler missing from impl/ AND no recent regeneration → **True Regression**
   - If test fails BUT manual cURL works → **Test Artifact**

### Classification Actions

**TRUE REGRESSION**:
- Include in "Critical Issues" section of report
- Mark as requiring immediate attention
- Provide fix recommendations

**OPENAPI ARTIFACT**:
- Include in "OpenAPI Generation Issues" section
- Note: "Handler exists but controller routing broken"
- Recommend: Run `make post-generate` to fix
- Document for prevention

**TEST ARTIFACT**:
- Include in "Test Configuration Issues" section
- Investigate test setup/configuration
- Provide test fix recommendations

## Quality Gates

**Before proceeding to next phase**:
- ✅ All agents have completed with deliverables
- ✅ Error investigation completed for all failures
- ✅ ENDPOINT-WORK-ADVICE.md read for all "not implemented" errors
- ✅ Classification complete (true vs. artifact)

**Before sending report**:
- ✅ Coverage analysis complete with gap identification
- ✅ All errors classified with evidence
- ✅ DynamoDB verification status confirmed
- ✅ Test generation notes created

## Usage Examples

### Full Orchestration (Default)
```bash
/orchestrate-tests
# Runs all 5 phases with comprehensive verification
```

### Focus on Specific Area
```bash
/orchestrate-tests --focus backend
# Phase 1: Coverage analysis
# Phase 2: Backend verification only
# Phase 3-5: Normal flow
```

### Skip Test Types
```bash
/orchestrate-tests --skip-types e2e,validation
# Skips E2E and validation tests, runs unit and integration only
```

### Quick Verification (Skip Coverage Analysis)
```bash
/orchestrate-tests --skip-coverage
# Jumps to Phase 2 (test execution)
# Use when coverage recently verified
```

## Success Metrics

**Test Execution**:
- ≥95% test pass rate (excluding known issues)
- All test types executed (unit, integration, E2E, validation)
- Zero unclassified errors

**Coverage Analysis**:
- ≥90% endpoint coverage
- ≥85% DynamoDB operation coverage
- All critical user journeys covered

**Error Classification**:
- 100% of "not implemented" errors investigated
- All 501 errors classified with evidence
- Zero false regressions in report

**Reporting**:
- Teams notification sent successfully
- Test generation notes complete
- Actionable recommendations provided

## Integration with Other Agents

**test-coverage-verifier** → Test Orchestrator → **test-generation**
- Coverage verifier identifies gaps
- Orchestrator executes tests
- Test generation fills gaps

**Test Orchestrator** → **root-cause-analyst** → **Teams Reporting**
- Orchestrator detects failures
- Root cause analyst investigates
- Teams reporting publishes results

**Test Orchestrator** + **quality-engineer** + **performance-engineer**
- Orchestrator coordinates overall testing
- Quality engineer validates test quality
- Performance engineer benchmarks execution times
