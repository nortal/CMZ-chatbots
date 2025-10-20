# /fix-code-review-issues - Systematic Code Review Issue Resolution

## Purpose
Safely apply fixes from comprehensive code review with automated testing, rollback on regression, and complete documentation trail.

## Prerequisites
- Completed `/comprehensive-code-review` with generated reports
- `reports/code-review/COMPREHENSIVE_REVIEW.md` exists
- Clean git working directory (no uncommitted changes)
- Development environment running and healthy (backend + frontend)
- On feature branch (not main/master)

## Command Usage
```bash
/fix-code-review-issues [options]

Options:
  --groups <1,2,4>    Apply specific fix groups only (default: 1,2,4 - skips auth)
  --skip-baseline     Skip baseline establishment if already done
  --quick             Use fast test subset instead of full e2e suite
  --dry-run           Show what would be done without applying fixes
  --include-auth      Include Group 3 auth refactoring (HIGH RISK - manual review recommended)
```

## Workflow Overview

### Phase 1: Pre-Flight Safety Checks (CRITICAL)
**Purpose**: Ensure safe starting conditions before any modifications

**Steps**:
1. **Read Critical Documentation**
   - Read `ENDPOINT-WORK.md` into memory (prevent reintroducing fixed issues)
   - Parse `reports/code-review/COMPREHENSIVE_REVIEW.md` for issue list
   - Extract priorities: CRITICAL, HIGH, MEDIUM, LOW
   - Read `AUTH-ADVICE.md` for auth-specific concerns

2. **CMZ-Specific Pre-Checks** (NEW - CRITICAL)
   ```bash
   # Verify no pending OpenAPI changes that could trigger regeneration
   git diff backend/api/openapi_spec.yaml
   if [ $? -ne 0 ]; then
       echo "⚠️ WARNING: OpenAPI spec has uncommitted changes - regeneration risk!"
       exit 1
   fi

   # Check auth system health before starting
   pytest backend/api/src/main/python/tests/test_auth_contract.py
   if [ $? -ne 0 ]; then
       echo "⚠️ WARNING: Auth contract tests failing - proceed with caution!"
   fi

   # Baseline Playwright auth tests (Step 1 only for speed)
   cd backend/api/src/main/python/tests/playwright
   ./run-step1-validation.sh
   cd -
   ```

3. **Verify Git State**
   - Check working directory is clean
   - Confirm on feature branch (not main/master)
   - Ensure latest code pulled from remote
   - Verify current branch is NOT dev or main

4. **Environment Health Check**
   - Backend API: `curl http://localhost:8080/system/health`
   - Frontend: `curl http://localhost:3001`
   - DynamoDB: `aws dynamodb list-tables --profile cmz`
   - Verify JWT token generation working

5. **Create Feature Branch**
   ```bash
   git checkout -b fix/code-review-$(date +%Y%m%d)
   ```

**Success Criteria**:
- All services healthy
- Git state clean
- Issue list parsed
- Ready to establish baseline

**Failure Actions**:
- If services unhealthy: Start services, retry
- If git dirty: Stash or commit existing changes
- If no review found: Run `/comprehensive-code-review` first

---

### Phase 2: Baseline Establishment (CRITICAL)
**Purpose**: Create safe checkpoint and measure initial test state

**Steps**:
1. **Run Complete E2E Test Suite**
   ```bash
   cd backend/api/src/main/python/tests/playwright
   FRONTEND_URL=http://localhost:3001 npx playwright test \
     --config config/playwright.config.js \
     --reporter=json > baseline-results.json
   ```

2. **Parse Baseline Results**
   - Total tests run
   - Pass count
   - Fail count (document pre-existing failures)
   - Failed test names
   - Duration

3. **Create Checkpoint Commit (CRITICAL)**
   ```bash
   git add -A
   git commit -m "checkpoint: baseline before code review fixes

   Baseline test results:
   - Total: X tests
   - Passing: Y tests
   - Failing: Z tests (pre-existing)

   Starting systematic fix application from code review findings."
   ```

4. **Tag Checkpoint**
   ```bash
   git tag code-review-baseline-$(date +%Y%m%d-%H%M)
   ```

5. **Save Baseline Test Results**
   ```bash
   mkdir -p reports/code-review/test-results
   cp baseline-results.json reports/code-review/test-results/baseline-$(date +%Y%m%d-%H%M).json
   ```

6. **Document in History**
   Create entry in `history/{user}_{date}_{time}.md`:
   ```markdown
   ## Baseline Established (TIMESTAMP)
   - Tests: X total, Y passing, Z failing
   - Checkpoint: {commit_hash}
   - Tag: code-review-baseline-YYYYMMDD-HHMM
   ```

**Success Criteria**:
- Checkpoint commit created
- Tag applied
- Test results saved
- Baseline metrics documented

**Critical Note**: This checkpoint is the SAFETY NET. All fixes can be reverted to this point.

---

### Phase 3: Fix Group Application
**Purpose**: Apply related fixes together, test, and decide to keep or revert

#### Fix Groups (CMZ-Adapted Intelligent Grouping)

**Group 1: Dead Code Removal** ✅ DEFAULT
- **Issues**: Remove deprecated later.py (CRITICAL)
- **Risk**: LOW (if verified unused)
- **Expected Test Impact**: None (should be zero impact)
- **Files Modified**: 1 (deletion only)
- **CMZ Note**: Safe to apply automatically

**Group 2: Data Handling Improvements** ✅ DEFAULT
- **Issues**: Extract model conversion utility + Add input validation (HIGH)
- **Risk**: MEDIUM (changes data flow)
- **Expected Test Impact**: Should be neutral or improved
- **Files Modified**: 3-5 (impl/utils/model_converters.py, handlers.py, family.py, animals.py)
- **CMZ Note**: Must preserve DynamoDB patterns in impl/utils/dynamo.py

**Group 3: Auth Refactoring** ⚠️ SKIP BY DEFAULT - HIGH RISK FOR CMZ
- **Issues**: Create shared auth utilities + Separate auth from business logic (CRITICAL + HIGH)
- **Risk**: EXTREME (CMZ has persistent auth issues after every OpenAPI regeneration)
- **Expected Test Impact**: High regression probability due to JWT token structure requirements
- **Files Modified**: 8-10 (adapters/common/auth_utils.py, multiple auth handlers)
- **CMZ WARNING**:
  - Auth endpoints break after EVERY OpenAPI regeneration
  - JWT tokens must maintain exact 3-part structure for frontend
  - impl/utils/jwt_utils.py is CRITICAL - DO NOT MODIFY without extensive testing
  - Requires manual review and Playwright Step 1 validation after EVERY change
  - **Recommendation**: SKIP or apply MANUALLY with extreme caution

**Group 4: Code Organization** ✅ DEFAULT
- **Issues**: Refactor jwt_utils + Standardize naming + Consolidate error handling (MEDIUM)
- **Risk**: LOW-MEDIUM (cleanup and standardization)
- **Expected Test Impact**: Should be neutral
- **Files Modified**: 5-7 (various handlers, dynamo.py - jwt_utils.py EXCLUDED)
- **CMZ Note**: MUST NOT trigger OpenAPI regeneration

#### Per-Group Workflow

**For Each Fix Group**:

1. **Pre-Fix CMZ Safeguards** (CRITICAL)
   ```bash
   # CMZ-specific safety checks before EVERY group
   cmz_safety_check() {
       local GROUP_NUM=$1

       # 1. Verify OpenAPI spec unchanged (CRITICAL)
       if git diff backend/api/openapi_spec.yaml | grep -q '^[+-]'; then
           echo "❌ ABORT: OpenAPI spec has changes - regeneration risk!"
           echo "Run: git checkout backend/api/openapi_spec.yaml"
           return 1
       fi

       # 2. Check critical files not modified
       CRITICAL_FILES=(
           "backend/api/src/main/python/openapi_server/impl/utils/jwt_utils.py"
           "backend/api/src/main/python/openapi_server/impl/utils/dynamo.py"
           "backend/api/src/main/python/openapi_server/impl/auth.py"
       )

       if [ "$GROUP_NUM" != "3" ]; then  # Skip check if auth group
           for file in "${CRITICAL_FILES[@]}"; do
               if git diff --name-only | grep -q "$file"; then
                   echo "⚠️ WARNING: Critical file modified: $file"
                   echo "Requires extra validation!"
               fi
           done
       fi

       # 3. Read ENDPOINT-WORK.md for known issues
       if [ -f "ENDPOINT-WORK.md" ]; then
           # Check for problematic patterns
           if grep -q "/auth/login" modified_files.txt; then
               echo "❌ ABORT: Detected /auth/login pattern (should be /auth)"
               return 1
           fi
           if grep -q "'/health'" modified_files.txt; then
               echo "❌ ABORT: Detected /health pattern (should be /system/health)"
               return 1
           fi
       fi

       # 4. Verify no controller regeneration needed
       if grep -q "controllers.*do some magic" backend/api/src/main/python/openapi_server/controllers/*.py; then
           echo "❌ ABORT: Controllers contain 'do some magic' - regeneration needed"
           echo "This will break auth! Fix manually first."
           return 1
       fi

       return 0
   }

   # Run before each group
   cmz_safety_check $GROUP_NUM || exit 1
   ```

2. **Apply All Fixes in Group**
   - Make all related changes atomically
   - Use MultiEdit for multi-file changes
   - Ensure code compiles/lints

3. **Run CMZ-Specific Test Suite** (ENHANCED)
   ```bash
   # Group-specific testing strategy
   case $GROUP_NUMBER in
     1)  # Dead code removal - quick validation
         pytest --co  # Verify code compiles
         ;;
     2)  # Data handling - validate persistence
         pytest backend/api/src/main/python/openapi_server/test/
         /validate-data-persistence --quick  # CMZ-specific validation
         ;;
     3)  # Auth refactoring - CRITICAL validation (if --include-auth)
         pytest backend/api/src/main/python/tests/test_auth_contract.py
         cd backend/api/src/main/python/tests/playwright
         ./run-step1-validation.sh  # Must pass ALL browsers
         npx playwright test --grep "auth" --reporter=json > group-3-results.json
         cd -
         ;;
     4)  # Code organization - standard tests
         pytest backend/api/src/main/python/openapi_server/test/
         npx playwright test --reporter=json > group-4-results.json
         ;;
   esac
   ```

4. **Compare Test Results**
   Use `scripts/lib/test_comparison.py`:
   ```python
   result = compare_results(baseline, current)
   # Returns: ('keep'|'revert'|'stop', reason, details)
   ```

5. **Decision Logic**

   **Scenario A: No Regressions** (Keep)
   - Pass count same or improved
   - No new test failures
   - Action: Commit changes
   ```bash
   git add -A
   git commit -m "fix(group-N): {description}

   Test results:
   - Before: X/Y passing
   - After: X/Y passing
   - Status: No regressions detected"
   ```

   **Scenario B: Regression Detected** (Attempt Fix)
   - Pass count decreased
   - New test failures appeared
   - Action: Attempt automatic regression fix
   ```python
   fix_result = attempt_regression_fix(new_failures)
   if fix_result == 'fixed':
       rerun_tests()
       if tests_pass:
           commit_changes()
       else:
           revert_changes()
           STOP()
   else:
       revert_changes()
       STOP()
   ```

   **Scenario C: Unfixable Regression** (Stop)
   - Regression detected
   - Cannot fix automatically
   - Action: Revert and STOP
   ```bash
   git reset --hard HEAD~1
   echo "⚠️ STOPPING: Unfixable regression in Group N"
   echo "Manual intervention required"
   save_state()
   exit 1
   ```

6. **Document After Each Group** (ENHANCED WITH AUTOMATIC HISTORY)

   **Auto-Update History File**:
   ```bash
   # Automatic history update function
   update_history() {
       local GROUP_NUM=$1
       local GROUP_NAME=$2
       local STATUS=$3
       local COMMIT_HASH=$(git rev-parse HEAD)
       local TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
       local USER=$(whoami)

       # Create/update history file
       HISTORY_FILE="history/${USER}_$(date +%Y-%m-%d_%Hh-%Hh).md"

       cat >> "$HISTORY_FILE" <<EOF

## Fix Group ${GROUP_NUM}: ${GROUP_NAME} (${TIMESTAMP})
- **Status**: ${STATUS}
- **Commit**: ${COMMIT_HASH}
- **Issues addressed**:
$(grep -A 5 "Group ${GROUP_NUM}" reports/code-review/COMPREHENSIVE_REVIEW.md | grep "- ")
- **Files modified**: $(git diff-tree --no-commit-id --name-only -r HEAD | wc -l)
- **Test results**:
  - Before: ${TESTS_BEFORE_PASS}/${TESTS_BEFORE_TOTAL} passing
  - After: ${TESTS_AFTER_PASS}/${TESTS_AFTER_TOTAL} passing
- **CMZ-specific validations**:
  - Auth contract: ${AUTH_CONTRACT_STATUS:-"N/A"}
  - Playwright Step 1: ${PLAYWRIGHT_STEP1_STATUS:-"N/A"}
  - Data persistence: ${DATA_PERSISTENCE_STATUS:-"N/A"}
- **OpenAPI regeneration check**: No changes to openapi_spec.yaml ✅
- **Decision rationale**: ${DECISION_RATIONALE}

### Technical Details
\`\`\`bash
# Commands executed
${COMMANDS_EXECUTED}
\`\`\`

### Lessons Learned
${LESSONS_LEARNED:-"- None for this group"}

---
EOF
       echo "✅ History updated: $HISTORY_FILE"
   }

   # Call after each group
   update_history $GROUP_NUM "$GROUP_NAME" "$STATUS"
   ```

   **Create Group Report**:
   ```bash
   reports/code-review/fixes/group-N-{name}.md
   ```
   Contains:
   - What was fixed
   - Test comparison
   - Files modified
   - Commit hash
   - Any issues encountered
   - CMZ-specific validation results

   **Update Advice File** (if patterns discovered):
   - What worked well
   - What to avoid
   - Troubleshooting tips
   - CMZ-specific gotchas

7. **User Confirmation**
   ```
   ✅ Group N Complete: {description}
   Test Results: {X/Y} → {A/B} passing
   Status: KEPT

   Continue to Group N+1? [Y/n/skip]
   ```

---

### Phase 4: Completion and Final Report

**Steps**:

1. **Run Final Comprehensive Validation** (CMZ-SPECIFIC)
   ```bash
   # Run complete validation suite
   /comprehensive-validation

   # This runs ALL validation commands:
   # - /validate-backend-health
   # - /validate-data-persistence
   # - /validate-family-management
   # - /validate-chat-dynamodb
   # - /validate-frontend-backend-integration

   # Compare results with baseline
   diff reports/validation/baseline.json reports/validation/final.json

   # Document improvements
   echo "Validation Results:" >> history/${USER}_$(date +%Y-%m-%d_%Hh-%Hh).md
   cat reports/validation/summary.md >> history/${USER}_$(date +%Y-%m-%d_%Hh-%Hh).md
   ```

2. **Generate Summary Report**
   Create `reports/code-review/fix-summary.md`:
   ```markdown
   # Code Review Fixes Summary

   ## Execution Details
   - Date: {timestamp}
   - Baseline commit: {hash}
   - Final commit: {hash}
   - Duration: {time}

   ## Fix Groups Applied
   ✅ Group 1: Dead code removal
   ✅ Group 2: Data handling improvements
   ❌ Group 3: Auth refactoring (reverted - regressions)
   ✅ Group 4: Code organization

   ## Test Results
   - Baseline: 42/45 passing (3 pre-existing failures)
   - Final: 44/45 passing (1 pre-existing failure)
   - Improvement: +2 tests fixed
   - Regressions: 0

   ## Remaining Issues
   - Group 3 issues require manual attention
   - See: reports/code-review/fixes/group-3-auth-refactoring.md

   ## Recommendations
   - Merge current fixes
   - Address Group 3 issues separately
   - Monitor for integration issues
   ```

3. **Final History Update**
   ```markdown
   ## Code Review Fixes Complete (TIMESTAMP)
   - Groups applied: 1, 2, 4
   - Groups reverted: 3
   - Test improvement: +2 tests
   - Commits: 4
   - Final state: Ready for merge
   ```

4. **Update CLAUDE.md**
   - Add command reference
   - Link to fix summary
   - Document lessons learned

---

## Test Result Comparison Algorithm

**Comparison Function**:
```python
def compare_results(baseline, current):
    """
    Compare test results and determine action

    Returns: (decision, reason, details)
      decision: 'keep' | 'revert' | 'stop'
    """
    baseline_failed = set(baseline['failed_tests'])
    current_failed = set(current['failed_tests'])

    # Calculate differences
    new_failures = current_failed - baseline_failed
    fixed_tests = baseline_failed - current_failed

    # Decision matrix
    if new_failures and not fixed_tests:
        # Pure regression - try to fix
        return ('revert', 'Introduced regressions', {
            'new_failures': list(new_failures),
            'action': 'attempt_fix_then_revert_if_unfixable'
        })

    if fixed_tests and not new_failures:
        # Pure improvement
        return ('keep', 'Fixed tests without regressions', {
            'fixed': list(fixed_tests)
        })

    if new_failures and fixed_tests:
        # Mixed results - need manual review
        return ('stop', 'Mixed results require manual review', {
            'new_failures': list(new_failures),
            'fixed': list(fixed_tests)
        })

    # No changes or all improvements
    return ('keep', 'No regressions detected', {})
```

---

## Safety Mechanisms

### CRITICAL Safety Features

1. **Checkpoint Commit First**
   - MUST create before any fixes
   - Tagged for easy reference
   - Complete rollback point

2. **ENDPOINT-WORK.md Verification**
   - Read before each fix group
   - Prevents reintroducing fixed issues
   - Validates endpoint paths

3. **Atomic Group Application**
   - All fixes in group applied together
   - Single commit per group
   - Easy to revert as unit

4. **Stop on Unfixable Regression**
   - Don't continue if regression can't be fixed
   - Preserve working state
   - Require manual intervention

5. **Documentation After Each Step**
   - History updates
   - Group reports
   - Advice file updates
   - Complete audit trail

### Rollback Procedures

**Rollback Single Group**:
```bash
git reset --hard HEAD~1
```

**Rollback to Baseline**:
```bash
git reset --hard code-review-baseline-YYYYMMDD-HHMM
```

**Rollback with Stash** (if uncommitted changes):
```bash
git stash
git reset --hard HEAD~1
git stash pop  # Only if you want to keep changes
```

---

## Edge Cases and Error Handling

### Edge Case 1: Baseline Tests Already Failing
**Situation**: Some tests failing before fixes applied

**Handling**:
- Document pre-existing failures
- Don't penalize fixes for pre-existing issues
- Only flag NEW failures as regressions
- Track which specific tests were already broken

### Edge Case 2: Environment Failure During Test
**Situation**: Backend crashes, frontend unresponsive

**Handling**:
1. Detect infrastructure failure vs test failure
2. Check service health
3. Restart services if needed
4. Retry test run once
5. Abort if persistent infrastructure issues

### Edge Case 3: User Interruption (Ctrl+C)
**Situation**: Process interrupted mid-execution

**Handling**:
- Trap signals for cleanup
- Save current state
- Document incomplete groups
- Provide resume instructions

### Edge Case 4: OpenAPI Regeneration
**Situation**: User accidentally runs `make generate-api` during process

**Handling**:
- Detect generated file timestamp changes
- Warn about regeneration
- Abort and require restart
- Recommend completing fixes before regeneration

### Edge Case 5: Mixed Test Results
**Situation**: Some tests improve, others regress

**Handling**:
- Present detailed comparison to user
- Show trade-offs
- Request manual decision
- Document decision rationale

---

## Integration with Existing Workflows

### After /comprehensive-code-review
```bash
# 1. Run comprehensive review
/comprehensive-code-review

# 2. Review findings
cat reports/code-review/COMPREHENSIVE_REVIEW.md

# 3. Apply fixes systematically
/fix-code-review-issues

# 4. Create MR if successful
/prepare-mr
```

### Before /prepare-mr
```bash
# Ensure all quality gates pass
make quality-check

# Apply code review fixes
/fix-code-review-issues

# Final validation
/comprehensive-validation

# Create merge request
/prepare-mr
```

---

## Success Criteria

**Workflow Successful If**:
- ✅ Checkpoint commit created before any changes
- ✅ CMZ pre-checks passed (no OpenAPI changes, auth healthy)
- ✅ Default fix groups attempted (1,2,4 - auth skipped unless --include-auth)
- ✅ Test results maintained or improved
- ✅ No unfixable regressions introduced
- ✅ No OpenAPI regeneration triggered
- ✅ Auth system remains functional (Step 1 validation passing)
- ✅ Critical files (jwt_utils.py, dynamo.py) unchanged or safely modified
- ✅ History file updated automatically after each group
- ✅ Comprehensive validation passes at end
- ✅ Final summary report generated

**Workflow Failed If**:
- ❌ OpenAPI spec changed (regeneration risk)
- ❌ Auth contract tests failing after changes
- ❌ Playwright Step 1 validation fails (auth broken)
- ❌ Unfixable regression detected
- ❌ Services became unhealthy
- ❌ Critical tests started failing
- ❌ "do some magic" found in controllers
- ❌ User manually aborted

---

## Output Artifacts

**Generated Files**:
```
reports/code-review/
├── test-results/
│   ├── baseline-YYYYMMDD-HHMM.json
│   ├── group-1-YYYYMMDD-HHMM.json
│   ├── group-2-YYYYMMDD-HHMM.json
│   └── group-4-YYYYMMDD-HHMM.json
├── fixes/
│   ├── group-1-dead-code-removal.md
│   ├── group-2-data-handling.md
│   └── group-4-code-organization.md
└── fix-summary.md

history/
└── {user}_{date}_{time}.md (updated with each group)
```

**Git Artifacts**:
```
Commits:
- checkpoint: baseline before code review fixes
- fix(dead-code): remove deprecated later.py
- fix(data-handling): extract model conversion + add validation
- refactor(code-org): standardize naming and error handling

Tags:
- code-review-baseline-YYYYMMDD-HHMM
```

---

## Performance Characteristics

**Estimated Duration**:
- Pre-flight checks: 1-2 minutes
- Baseline establishment: 3-5 minutes
- Per fix group: 5-10 minutes
- Total: 20-45 minutes (depends on test suite size)

**Resource Usage**:
- CPU: High during test execution
- Memory: Moderate (browser automation)
- Disk: ~100MB for test artifacts

**Optimization Options**:
- `--quick`: Use fast test subset (5x faster)
- `--groups`: Apply specific groups only
- `--skip-baseline`: Reuse existing baseline

---

## Troubleshooting

### Issue: "Checkpoint commit failed"
**Cause**: Uncommitted changes or git issues
**Solution**:
```bash
git status  # Check for issues
git stash   # If you have changes
# Then retry
```

### Issue: "Baseline tests timeout"
**Cause**: Services not responding
**Solution**:
```bash
make status  # Check service health
make start-dev  # Restart services
# Then retry
```

### Issue: "Regression in Group 3, cannot fix"
**Cause**: Auth changes broke existing functionality
**Solution**:
- Changes automatically reverted
- Manual intervention required
- Review Group 3 fixes separately
- May need staged approach

### Issue: "ENDPOINT-WORK.md not found"
**Cause**: File missing or renamed
**Solution**:
- Skip endpoint verification (risky)
- Manually verify endpoint paths
- Document which endpoints were validated

---

## See Also
- `/comprehensive-code-review` - Generate code review findings
- `/comprehensive-validation` - Run complete validation suite
- `/prepare-mr` - Create merge request after fixes
- `FIX-CODE-REVIEW-ISSUES-ADVICE.md` - Best practices and patterns
- `ENDPOINT-WORK.md` - Known endpoint issues and fixes
