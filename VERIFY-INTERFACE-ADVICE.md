# Interface Verification Agent - Best Practices and Integration

**Purpose**: Guidance for using the interface verification agent to detect and classify contract drift between frontend, API, and OpenAPI specification

**Related Files:**
- `.claude/commands/verify-interface.md` - Agent command and methodology
- `.claude/commands/validate-contracts.md` - Existing validation command
- `VALIDATE-CONTRACTS-ADVICE.md` - Contract validation best practices
- `scripts/validate_contracts.py` - Python validation script
- `scripts/validate_contracts.sh` - Bash validation wrapper

---

## Overview

The interface verification agent provides systematic three-way alignment checking with intelligent classification of drift sources. Unlike the `/validate-contracts` command, this is a **delegatable agent** designed for:
- Early execution by test-orchestrator (before other testing)
- Read-only analysis (reports but doesn't fix)
- Intelligent classification (FRONTEND_BUG vs API_BUG vs SPEC_BUG)
- Evidence-based error attribution

---

## When to Use Interface Verification Agent

### Primary Use Cases

**1. Test Orchestration Phase 0 (BEFORE other testing)**
- Called by test-orchestrator as first verification step
- Detects contract drift before functional testing begins
- Prevents false test failures due to contract misalignment
- Un blocks backend and frontend testing agents

**2. Pre-Deployment Validation**
- Systematic check before production deployment
- Comprehensive drift detection across all endpoints
- Classification helps prioritize fixes

**3. Post-OpenAPI Regeneration**
- After `make generate-api` runs
- Verify frontend and backend still aligned with new spec
- Catch regressions from code generation

**4. CI/CD Pipeline Integration**
- Automated validation on every PR
- Fail build if CRITICAL drift detected
- Generate reports for code reviewers

### vs. `/validate-contracts` Command

| Feature | verify-interface Agent | validate-contracts Command |
|---------|----------------------|---------------------------|
| **Usage** | Delegatable agent | Direct command |
| **Classification** | FRONTEND_BUG vs API_BUG vs SPEC_BUG | Generic mismatches |
| **Fixes** | Read-only, reports only | Can suggest fixes |
| **Orchestration** | Called by test-orchestrator | Called manually or CI/CD |
| **Evidence** | Provides detailed evidence | General detection |
| **Integration** | Part of test workflow | Standalone validation |

**When to use verify-interface**: During test orchestration, need classification
**When to use validate-contracts**: Manual validation, need fix suggestions

---

## Integration with Existing Patterns

### Uses Existing Validation Scripts

The verify-interface agent leverages existing validation infrastructure:

**1. Python Validation Script** (`scripts/validate_contracts.py`):
```python
# Agent uses existing script for contract parsing
python3 scripts/validate_contracts.py \
  --openapi backend/api/openapi_spec.yaml \
  --ui frontend/src \
  --api backend/api/src/main/python/openapi_server/impl \
  --output /tmp/contracts.json \
  --format json
```

**2. Shell Wrapper** (`scripts/validate_contracts.sh`):
```bash
# Agent can invoke shell wrapper for complete workflow
./scripts/validate_contracts.sh
```

**3. Classification Layer**:
The agent adds intelligent classification on top of existing detection:
```json
{
  "mismatch": {
    "field": "animalId",
    "openapi": "animalId",
    "frontend": "animal_id",
    "backend": "animalId"
  },
  "classification": "FRONTEND_BUG",
  "evidence": {
    "openapi_source": "openapi_spec.yaml:245",
    "frontend_source": "animalService.js:27",
    "backend_source": "impl/animals.py:45",
    "reasoning": "OpenAPI and API both use 'animalId', only frontend differs"
  }
}
```

### References Existing Advice

The agent follows patterns from `VALIDATE-CONTRACTS-ADVICE.md`:
- Field name mismatch detection
- Parameter location validation
- Required field checking
- Type mismatch identification
- Response structure alignment
- Error response consistency

---

## Classification Methodology

### Decision Tree for Error Attribution

**When mismatch detected between any two sources:**

```
MISMATCH FOUND
├─ All three sources different?
│  └─ MULTIPLE (requires investigation)
│
├─ Two sources match, one differs?
│  ├─ OpenAPI + API match, Frontend differs → FRONTEND_BUG
│  ├─ OpenAPI + Frontend match, API differs → API_BUG
│  └─ Frontend + API match, OpenAPI differs → SPEC_BUG
│
└─ Cannot determine alignment?
   └─ AMBIGUOUS (delegate to root-cause-analyst)
```

### Classification Examples

**Example 1: FRONTEND_BUG**
```
Field: animalId (request body)
- OpenAPI:  "animalId" ✅
- API Reads: "animalId" ✅
- Frontend Sends: "animal_id" ❌

Classification: FRONTEND_BUG
Reasoning: Two sources agree (OpenAPI + API), frontend deviates
```

**Example 2: API_BUG**
```
Field: temperature (required vs optional)
- OpenAPI:  required=false ✅
- Frontend: always sends (compatible) ✅
- API: uses body['temperature'] (will error if missing) ❌

Classification: API_BUG
Reasoning: API violates optional field contract in OpenAPI
```

**Example 3: SPEC_BUG**
```
Field: systemPrompt (response)
- OpenAPI:  "system_prompt" ❌
- API Returns: "systemPrompt" ✅
- Frontend Expects: "systemPrompt" ✅

Classification: SPEC_BUG
Reasoning: Implementation and frontend agree on camelCase, spec has snake_case
```

**Example 4: MULTIPLE**
```
Field: configId
- OpenAPI:  "animalConfigId"
- API Returns: "config_id"
- Frontend Expects: "configId"

Classification: MULTIPLE
Reasoning: All three sources use different names - systemic issue
```

---

## Result Validation (Self-Checking)

### Agent Must Validate Its Own Results

**CRITICAL**: The agent must verify its analysis is correct before reporting.

**Self-Validation Checklist:**

**1. Contract Map Completeness**
```python
# Verify all three contract maps populated
assert len(openapi_contract_map) > 0, "OpenAPI map empty"
assert len(api_contract_map) > 0, "API map empty"
assert len(frontend_contract_map) > 0, "Frontend map empty"

# Verify endpoint coverage
openapi_endpoints = set(openapi_contract_map.keys())
for endpoint in openapi_endpoints:
    assert endpoint in api_contract_map, f"API missing endpoint: {endpoint}"
    # Note: Frontend may not call all endpoints (that's OK)
```

**2. Classification Evidence Validation**
```python
# For each classification, verify evidence exists
for mismatch in mismatches:
    assert 'classification' in mismatch, "Missing classification"
    assert 'evidence' in mismatch, "Missing evidence"
    assert mismatch['classification'] in [
        'FRONTEND_BUG', 'API_BUG', 'SPEC_BUG', 'MULTIPLE', 'AMBIGUOUS'
    ], f"Invalid classification: {mismatch['classification']}"

    # Verify evidence has source locations
    evidence = mismatch['evidence']
    assert 'openapi' in evidence, "Missing OpenAPI evidence"
    assert 'file' in evidence['openapi'], "Missing OpenAPI file location"
    assert 'line' in evidence['openapi'] or 'section' in evidence['openapi'], \
        "Missing OpenAPI line/section number"
```

**3. Classification Logic Validation**
```python
# Verify classification matches evidence
for mismatch in mismatches:
    classification = mismatch['classification']
    evidence = mismatch['evidence']

    if classification == 'FRONTEND_BUG':
        # Verify OpenAPI and API match, frontend differs
        assert evidence['openapi']['value'] == evidence['api']['value'], \
            "FRONTEND_BUG but OpenAPI and API don't match"
        assert evidence['frontend']['value'] != evidence['openapi']['value'], \
            "FRONTEND_BUG but frontend matches OpenAPI"

    elif classification == 'API_BUG':
        # Verify OpenAPI and frontend match (or frontend compatible), API differs
        assert evidence['api']['value'] != evidence['openapi']['value'], \
            "API_BUG but API matches OpenAPI"

    elif classification == 'SPEC_BUG':
        # Verify API and frontend match, OpenAPI differs
        assert evidence['api']['value'] == evidence['frontend']['value'], \
            "SPEC_BUG but API and frontend don't match"
        assert evidence['openapi']['value'] != evidence['api']['value'], \
            "SPEC_BUG but OpenAPI matches implementation"

    elif classification == 'MULTIPLE':
        # Verify all three differ
        values = set([
            evidence['openapi']['value'],
            evidence['api']['value'],
            evidence['frontend']['value']
        ])
        assert len(values) == 3, "MULTIPLE but not all sources differ"
```

**4. Severity Assignment Validation**
```python
# Verify severity matches impact
for mismatch in mismatches:
    severity = mismatch['impact']
    assert severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'], \
        f"Invalid severity: {severity}"

    # CRITICAL = Complete failure (field name mismatch in response)
    # HIGH = Partial failure (required field mismatch)
    # MEDIUM = Contract violation but works (optional field treated as required)
    # LOW = Cosmetic (extraneous field, ignored)

    if severity == 'CRITICAL':
        # Must have evidence of data loss or complete failure
        assert 'data_loss' in mismatch or 'complete_failure' in mismatch, \
            "CRITICAL severity but no evidence of critical impact"
```

**5. Report Completeness Validation**
```python
# Verify report has all required sections
assert 'executive_summary' in report, "Missing executive summary"
assert 'mismatches_by_endpoint' in report, "Missing endpoint details"
assert 'classification_summary' in report, "Missing classification summary"
assert 'recommendations' in report, "Missing recommendations"

# Verify numbers add up
total_endpoints = report['executive_summary']['total_endpoints']
aligned = report['executive_summary']['perfect_alignment']
mismatched = report['executive_summary']['mismatches_found']
assert aligned + mismatched == total_endpoints, "Endpoint count mismatch"

# Verify classification counts
frontend_bugs = len([m for m in mismatches if m['classification'] == 'FRONTEND_BUG'])
api_bugs = len([m for m in mismatches if m['classification'] == 'API_BUG'])
spec_bugs = len([m for m in mismatches if m['classification'] == 'SPEC_BUG'])
multiple = len([m for m in mismatches if m['classification'] == 'MULTIPLE'])
ambiguous = len([m for m in mismatches if m['classification'] == 'AMBIGUOUS'])

assert (frontend_bugs + api_bugs + spec_bugs + multiple + ambiguous) == len(mismatches), \
    "Classification count mismatch"
```

### Validation Output

The agent should report its self-validation results:

```markdown
## Verification Quality Metrics

**Self-Validation Results**:
- ✅ Contract maps complete (OpenAPI: 37, API: 37, Frontend: 35)
- ✅ All classifications have evidence (42 mismatches)
- ✅ Classification logic validated (100% pass)
- ✅ Severity assignments validated (42 mismatches)
- ✅ Report completeness verified (all sections present)
- ✅ Arithmetic checks passed (totals match)

**Confidence Level**: HIGH
**Recommendation**: Results are reliable, safe to proceed with delegated fixes
```

---

## Best Practices

### 1. Call Early in Test Workflow

**DO:**
```python
# Test orchestrator Phase 0
Task(
    subagent_type="general-purpose",
    description="Verify interface alignment",
    prompt="""Interface Verification Agent - verify contracts FIRST.

    If CRITICAL issues found, BLOCK further testing.
    Report to user immediately."""
)

# Then proceed with other testing ONLY if no blockers
```

**DON'T:**
```python
# Running after functional tests have already failed
# Wastes time debugging test failures that are contract issues
```

### 2. Respect Classification

**DO:**
```python
# After verification, delegate fixes to appropriate agents
if classification == 'FRONTEND_BUG':
    Task(subagent_type="frontend-architect",
         description="Fix frontend contract issues", ...)
elif classification == 'API_BUG':
    Task(subagent_type="backend-architect",
         description="Fix API contract issues", ...)
elif classification == 'SPEC_BUG':
    # Requires manual decision - update spec or implementation?
    report_to_user("Spec bug found - manual decision required")
```

**DON'T:**
```python
# Ignore classification and guess at root cause
# Leads to fixing wrong component
```

### 3. Use Evidence for Debugging

**DO:**
```bash
# Use exact file:line references from evidence
# Evidence: "frontend/src/services/animalService.js:27"
vim frontend/src/services/animalService.js +27

# Check the specific line mentioned
# "animal_id: animalId,"  ← Found it!
```

**DON'T:**
```bash
# Manually search for issues
# Wastes time when evidence provides exact location
```

### 4. Validate Before Reporting

**DO:**
```python
# Agent self-validates before generating report
self.validate_contract_maps()
self.validate_classifications()
self.validate_severity_assignments()
self.validate_report_completeness()

# Only then generate final report
if all_validations_passed:
    return self.generate_report()
else:
    return self.generate_error_report("Self-validation failed")
```

**DON'T:**
```python
# Generate report without validation
# May contain incorrect classifications or incomplete evidence
```

---

## Troubleshooting

### Issue: Agent Reports "AMBIGUOUS" Classifications

**Symptoms:**
- Multiple mismatches classified as AMBIGUOUS
- No clear error attribution

**Possible Causes:**
1. **Complex Mismatch Pattern**: All three sources different
2. **Insufficient Evidence**: Can't determine which source is authoritative
3. **Edge Case**: Unconventional pattern not in decision tree

**Solution:**
```python
# Delegate AMBIGUOUS cases to root-cause-analyst
Task(
    subagent_type="root-cause-analyst",
    description="Investigate ambiguous contract drift",
    prompt="""Investigate ambiguous contract mismatch.

    Field: {field_name}
    OpenAPI: {openapi_value}
    API: {api_value}
    Frontend: {frontend_value}

    Determine root cause and proper classification.
    Provide detailed evidence for decision."""
)
```

### Issue: Classification Doesn't Match Intuition

**Symptoms:**
- Agent classifies as FRONTEND_BUG but looks like API_BUG
- Evidence seems contradictory

**Investigation Steps:**
1. **Check Evidence Sources**:
   ```bash
   # Verify exact file:line references
   cat backend/api/openapi_spec.yaml | sed -n '245p'
   cat frontend/src/services/animalService.js | sed -n '27p'
   cat backend/api/src/main/python/openapi_server/impl/animals.py | sed -n '45p'
   ```

2. **Verify Contract Values**:
   ```bash
   # OpenAPI spec
   yq eval '.paths."/animal".post.requestBody.content."application/json".schema.properties.animalId' \
     backend/api/openapi_spec.yaml

   # API handler
   grep -A5 "def handle_animal_post" impl/animals.py

   # Frontend code
   grep -A10 "fetch.*animal" frontend/src/services/animalService.js
   ```

3. **Re-run Classification**:
   ```python
   # Manually verify classification logic
   if openapi_value == api_value and openapi_value != frontend_value:
       correct_classification = "FRONTEND_BUG"  # OpenAPI + API agree
   elif openapi_value == frontend_value and openapi_value != api_value:
       correct_classification = "API_BUG"  # OpenAPI + Frontend agree
   # etc.
   ```

### Issue: Agent Finds No Mismatches But Issues Exist

**Symptoms:**
- Agent reports 100% alignment
- But runtime errors occur

**Possible Causes:**
1. **Edge Cases Not Detected**:
   - Type coercion (JavaScript "0.7" → 0.7)
   - Null vs undefined differences
   - Whitespace handling
   - Case sensitivity
   - Array ordering

2. **Business Logic Issues**:
   - Validation rules not in OpenAPI
   - Database constraints
   - Authentication/authorization

3. **Incomplete Coverage**:
   - Agent missed some API calls
   - Agent didn't analyze all files

**Solution:**
```bash
# Run full validation suite
./scripts/validate_contracts.sh

# Check for edge cases manually
cat VALIDATE-CONTRACTS-ADVICE.md | grep "Edge Cases"

# Run integration tests to catch business logic issues
pytest tests/integration/
```

### Issue: Report Too Large

**Symptoms:**
- Hundreds of mismatches reported
- Difficult to prioritize

**Solution:**
```python
# Filter by severity
critical_mismatches = [m for m in mismatches if m['impact'] == 'CRITICAL']
high_mismatches = [m for m in mismatches if m['impact'] == 'HIGH']

# Report CRITICAL and HIGH only
report_summary = {
    'critical': critical_mismatches,
    'high': high_mismatches,
    'other_count': len(mismatches) - len(critical_mismatches) - len(high_mismatches)
}

# Group by classification
frontend_bugs = [m for m in critical_mismatches if m['classification'] == 'FRONTEND_BUG']
api_bugs = [m for m in critical_mismatches if m['classification'] == 'API_BUG']

# Prioritize: Fix all FRONTEND_BUG in one PR, all API_BUG in another
```

---

## Integration Patterns

### Pattern 1: Test Orchestration Phase 0

```python
# Test orchestrator calls interface verification FIRST
Task(
    subagent_type="general-purpose",
    description="Phase 0: Interface verification",
    prompt="""Interface Verification Agent.

    Analyze OpenAPI spec, API implementation, frontend code.
    Classify all contract drift with evidence.
    Report findings without fixes.

    CRITICAL: If CRITICAL issues found, STOP and report immediately.
    BLOCK further testing until contracts aligned.

    See .claude/commands/verify-interface.md for methodology."""
)

# Agent returns report with classifications
# Orchestrator decides:
if critical_issues_found:
    report_to_user("Critical contract drift found - fix before testing")
    delegate_fixes_to_appropriate_agents()
    STOP_TESTING = True
else:
    proceed_with_backend_testing()
    proceed_with_frontend_testing()
```

### Pattern 2: CI/CD Pipeline

```yaml
# .github/workflows/contract-verification.yml
- name: Interface Verification
  run: |
    # Delegate to interface verification agent
    claude-code /verify-interface --all-endpoints

    # Check for critical issues
    if grep -q "CRITICAL" interface-verification-report.md; then
      echo "::error::Critical contract drift detected"
      cat interface-verification-report.md
      exit 1
    fi
```

### Pattern 3: Pre-Deployment Check

```bash
# scripts/pre_deploy_validation.sh

echo "Running interface verification before deployment..."

# Delegate to verification agent
claude-code /verify-interface --all-endpoints

# Check results
if [ -f "interface-verification-report.md" ]; then
  CRITICAL_COUNT=$(grep -c "CRITICAL" interface-verification-report.md || echo "0")

  if [ "$CRITICAL_COUNT" -gt 0 ]; then
    echo "❌ CRITICAL contract issues found - cannot deploy"
    cat interface-verification-report.md
    exit 1
  else
    echo "✅ Interface verification passed"
  fi
fi
```

---

## Success Metrics

**Verification Coverage:**
- ✅ 100% of OpenAPI endpoints analyzed
- ✅ All request parameters checked (path, query, body)
- ✅ All request body fields verified
- ✅ All response schemas validated
- ✅ All field names, types, required status compared

**Classification Accuracy:**
- ✅ 100% of mismatches classified with evidence
- ✅ <5% AMBIGUOUS classifications (most resolved)
- ✅ Clear delegation targets identified
- ✅ Severity appropriately assigned

**Self-Validation:**
- ✅ Contract maps complete and validated
- ✅ Classification logic verified
- ✅ Evidence present for all findings
- ✅ Report arithmetic checks passed

**Integration Success:**
- ✅ Called early by test-orchestrator
- ✅ Blocks testing when CRITICAL issues found
- ✅ Proper delegation to fix agents
- ✅ Re-verification confirms fixes

---

## Related Documentation

**Essential Reading:**
- `.claude/commands/verify-interface.md` - Agent command
- `.claude/commands/validate-contracts.md` - Validation command
- `VALIDATE-CONTRACTS-ADVICE.md` - Contract validation patterns
- `ENDPOINT-WORK-ADVICE.md` - OpenAPI generation patterns

**Related Agents:**
- `test-orchestrator` - Calls this agent in Phase 0
- `frontend-architect` - Fixes FRONTEND_BUG issues
- `backend-architect` - Fixes API_BUG issues
- `root-cause-analyst` - Investigates AMBIGUOUS cases

**Scripts:**
- `scripts/validate_contracts.py` - Python validation
- `scripts/validate_contracts.sh` - Shell wrapper
