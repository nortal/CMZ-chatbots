# Contract Regression Prevention Strategy

**Generated**: 2025-10-11 21:00:00
**Purpose**: Prevent three-way contract misalignments between OpenAPI spec, UI code, and API implementation

---

## Problem Statement

**Current Issues:**
- OpenAPI spec changes break UI/API compatibility
- UI refactoring introduces contract violations
- API implementation drifts from OpenAPI specification
- No automated detection until runtime failures occur

**Root Causes:**
1. OpenAPI spec is source of truth but not validated automatically
2. UI developers don't always reference spec when making changes
3. API handlers lack validation, allowing contract violations
4. No pre-commit or CI/CD contract validation

---

## Prevention Strategy

### 1. Source Control Integration

**Pre-Commit Hooks**
```bash
#!/bin/bash
# .git/hooks/pre-commit

# Run contract validation before allowing commit
./scripts/validate_contracts.sh --quick

if [ $? -ne 0 ]; then
  echo "❌ Contract validation failed! Fix issues before committing."
  echo "Run './scripts/validate_contracts.sh' for detailed report."
  exit 1
fi

echo "✅ Contract validation passed"
```

**Git Hook Setup Script**
```bash
#!/bin/bash
# scripts/setup_contract_validation_hooks.sh

# Install pre-commit hook
cp scripts/hooks/pre-commit-contract-validation .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

echo "✅ Contract validation hooks installed"
echo "To bypass (emergency only): git commit --no-verify"
```

**Implementation:**
- Auto-run on `git commit`
- Quick validation mode (< 30 seconds)
- Fails commit if critical mismatches found
- Provides actionable error messages

---

### 2. CI/CD Pipeline Integration

**GitHub Actions Workflow**
```yaml
# .github/workflows/contract-validation.yml
name: Contract Validation

on:
  pull_request:
    paths:
      - 'backend/api/openapi_spec.yaml'
      - 'frontend/src/**'
      - 'backend/api/src/main/python/openapi_server/impl/**'
  push:
    branches: [main, dev]

jobs:
  validate-contracts:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install pyyaml

      - name: Run Contract Validation
        run: |
          ./scripts/validate_contracts.sh

      - name: Check Results
        run: |
          # Fail if critical mismatches found
          if grep -q "❌ Misaligned: [1-9]" validation-reports/*/contract_report.md; then
            echo "Contract validation failed with critical mismatches"
            exit 1
          fi

      - name: Upload Report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: contract-validation-report
          path: validation-reports/*/contract_report.md

      - name: Comment on PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const report = fs.readFileSync('validation-reports/contract_report.md', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.name,
              body: `## Contract Validation Results\n\n${report}`
            });
```

**Implementation:**
- Runs on every PR affecting contracts
- Posts results as PR comments
- Blocks merge if critical issues found
- Uploads full reports as artifacts

---

### 3. OpenAPI-First Development Workflow

**Strict Process:**
1. ✅ **OpenAPI First**: All API changes start with spec updates
2. 🔄 **Generate**: Re-generate server code from spec
3. 🧪 **Validate**: Run contract validation
4. 🎨 **Update UI**: Modify UI to match new contract
5. 🛡️ **Update Handlers**: Implement backend logic
6. ✅ **Test**: E2E tests verify contract compliance

**Enforcement:**
- PR template requires OpenAPI changes to be listed
- Code review checklist includes contract validation
- Teams notification on contract changes

**OpenAPI Change Checklist:**
```markdown
## OpenAPI Spec Changes

- [ ] OpenAPI spec updated
- [ ] `make post-generate` completed successfully
- [ ] Contract validation passed
- [ ] UI updated to match new contract
- [ ] Backend handlers updated
- [ ] E2E tests added/updated
- [ ] Documentation updated
```

---

### 4. Type Safety & Code Generation

**TypeScript Types from OpenAPI**
```bash
# Generate TypeScript types from OpenAPI spec
npx openapi-typescript backend/api/openapi_spec.yaml -o frontend/src/api/types.ts
```

**Type-Safe API Client:**
```typescript
// frontend/src/api/client.ts
import { paths } from './types';

type PostAuthRequest = paths['/auth']['post']['requestBody']['content']['application/json'];
type PostAuthResponse = paths['/auth']['post']['responses']['200']['content']['application/json'];

export async function login(data: PostAuthRequest): Promise<PostAuthResponse> {
  // TypeScript enforces contract at compile time
  const response = await apiRequest<PostAuthResponse>('/auth', {
    method: 'POST',
    body: JSON.stringify(data)
  });
  return response;
}
```

**Benefits:**
- Compile-time contract validation
- IDE autocomplete for API fields
- Immediate feedback on contract changes
- Eliminates field name typos

---

### 5. Backend Validation Framework

**Request Validation Decorator**
```python
# backend/api/src/main/python/openapi_server/impl/utils/validation.py

from functools import wraps
from typing import Callable, Any, Tuple
from openapi_server.models.error import Error

def validate_request(required_fields: list[str], optional_fields: list[str] = None):
    """Decorator to validate request body against contract"""
    def decorator(handler: Callable) -> Callable:
        @wraps(handler)
        def wrapper(body: dict, *args, **kwargs) -> Tuple[Any, int]:
            # Validate required fields
            for field in required_fields:
                if field not in body or body[field] is None:
                    error = Error(
                        code="validation_error",
                        message=f"Required field '{field}' missing",
                        details={"field": field, "required": True}
                    )
                    return error.to_dict(), 400

            # Validate no unexpected fields (strict mode)
            allowed_fields = set(required_fields + (optional_fields or []))
            unexpected = set(body.keys()) - allowed_fields
            if unexpected:
                error = Error(
                    code="validation_error",
                    message=f"Unexpected fields in request",
                    details={"unexpected_fields": list(unexpected)}
                )
                return error.to_dict(), 400

            return handler(body, *args, **kwargs)
        return wrapper
    return decorator

# Usage:
@validate_request(required_fields=['username', 'password'], optional_fields=['email', 'register'])
def handle_auth_post(body: dict) -> Tuple[Any, int]:
    # Body is already validated
    return authenticate_user(body)
```

**Type Validation Decorator**
```python
def validate_types(field_types: dict[str, type]):
    """Decorator to validate field types"""
    def decorator(handler: Callable) -> Callable:
        @wraps(handler)
        def wrapper(body: dict, *args, **kwargs) -> Tuple[Any, int]:
            for field, expected_type in field_types.items():
                if field in body and body[field] is not None:
                    if not isinstance(body[field], expected_type):
                        error = Error(
                            code="type_error",
                            message=f"Field '{field}' must be {expected_type.__name__}",
                            details={
                                "field": field,
                                "expected": expected_type.__name__,
                                "received": type(body[field]).__name__
                            }
                        )
                        return error.to_dict(), 400
            return handler(body, *args, **kwargs)
        return wrapper
    return decorator
```

---

### 6. Automated Contract Testing

**Contract Test Suite**
```python
# tests/contract_tests/test_auth_contract.py

import pytest
import yaml
from openapi_server.impl.handlers import handle_auth_post

def load_openapi_spec():
    """Load OpenAPI spec for contract verification"""
    with open('backend/api/openapi_spec.yaml') as f:
        return yaml.safe_load(f)

def test_auth_contract_required_fields():
    """Verify handler validates required fields per OpenAPI spec"""
    spec = load_openapi_spec()
    auth_schema = spec['paths']['/auth']['post']['requestBody']['content']['application/json']['schema']
    required = auth_schema.get('required', [])

    # Test each required field
    for field in required:
        body = {'username': 'test', 'password': 'test'}
        del body[field]  # Remove required field

        response, status = handle_auth_post(body)
        assert status == 400, f"Should reject missing required field: {field}"
        assert 'validation_error' in str(response)

def test_auth_contract_field_types():
    """Verify handler validates field types per OpenAPI spec"""
    spec = load_openapi_spec()
    properties = spec['paths']['/auth']['post']['requestBody']['content']['application/json']['schema']['properties']

    # Test wrong types
    response, status = handle_auth_post({'username': 123, 'password': 'test'})
    assert status == 400, "Should reject non-string username"

def test_auth_contract_response_structure():
    """Verify response matches OpenAPI spec"""
    spec = load_openapi_spec()
    response_schema = spec['paths']['/auth']['post']['responses']['200']['content']['application/json']['schema']
    response_fields = set(response_schema.get('properties', {}).keys())

    response, status = handle_auth_post({'username': 'parent1@test.cmz.org', 'password': 'testpass123'})
    assert status == 200

    actual_fields = set(response.keys())
    assert response_fields.issubset(actual_fields), f"Missing fields: {response_fields - actual_fields}"
```

**Run Contract Tests in CI:**
```yaml
# Add to GitHub Actions
- name: Run Contract Tests
  run: |
    pytest tests/contract_tests/ -v --tb=short
```

---

### 7. Development Environment Setup

**Developer Onboarding Script**
```bash
#!/bin/bash
# scripts/setup_development.sh

echo "Setting up CMZ development environment..."

# 1. Install contract validation hooks
./scripts/setup_contract_validation_hooks.sh

# 2. Generate TypeScript types from OpenAPI
npm run generate-types

# 3. Run initial contract validation
./scripts/validate_contracts.sh

# 4. Verify test users exist
python3 scripts/verify_test_users.py

echo "✅ Development environment ready"
echo "💡 Run 'npm run validate-contracts' before committing"
```

**IDE Integration:**
```json
// .vscode/settings.json
{
  "files.associations": {
    "openapi_spec.yaml": "yaml"
  },
  "yaml.schemas": {
    "https://raw.githubusercontent.com/OAI/OpenAPI-Specification/main/schemas/v3.0/schema.json": "openapi_spec.yaml"
  },
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true
}
```

---

### 8. Documentation & Training

**Contract Validation Guide** (`VALIDATE-CONTRACTS-ADVICE.md`)
- Already exists, ensure developers read it
- Add to onboarding checklist
- Reference in PR template

**OpenAPI Best Practices Document**
```markdown
# OpenAPI Best Practices for CMZ

## Field Naming Conventions
- Use camelCase for JSON fields (familyName, not family_name)
- Be consistent across all endpoints
- Document any exceptions

## Required vs Optional
- Only mark fields required if API truly rejects requests without them
- Use 'nullable: true' for fields that can be null
- Provide default values in description

## Examples
- Always include example values in schema
- Use realistic data (not foo/bar)
- Show edge cases in examples

## Versioning
- Version breaking changes (/v2/endpoint)
- Document migration path
- Deprecate old versions gracefully
```

---

### 9. Monitoring & Alerting

**Contract Drift Detection**
```python
# scripts/monitor_contract_drift.py

import schedule
import time

def check_contract_drift():
    """Periodic contract validation"""
    result = subprocess.run(['./scripts/validate_contracts.sh'], capture_output=True)

    if result.returncode != 0:
        send_alert_to_teams("Contract drift detected!")
        create_jira_ticket("Contract Validation Failed")

# Run daily
schedule.every().day.at("09:00").do(check_contract_drift)

while True:
    schedule.run_pending()
    time.sleep(60)
```

**Teams Notifications:**
- Automatic notification on contract validation failures
- Weekly contract health summary
- Alert on OpenAPI spec changes

---

### 10. Gradual Rollout Plan

**Phase 1: Setup (Week 1)**
- [ ] Install pre-commit hooks for contract validation
- [ ] Add GitHub Actions workflow
- [ ] Generate TypeScript types from OpenAPI

**Phase 2: Backend Hardening (Week 2-3)**
- [ ] Add validation decorators to 10 high-traffic endpoints
- [ ] Write contract tests for authentication
- [ ] Document validation patterns

**Phase 3: Full Coverage (Week 4-6)**
- [ ] Apply validation to all 61 endpoints
- [ ] Achieve 90%+ handler validation coverage
- [ ] Complete contract test suite

**Phase 4: Continuous Improvement (Ongoing)**
- [ ] Monitor contract validation metrics
- [ ] Improve scanner accuracy
- [ ] Refine validation rules based on learnings

---

## Success Metrics

**Baseline (Current):**
- 0% endpoints fully aligned
- 31% endpoints misaligned
- 0 automated contract checks
- Manual testing only

**Target (3 months):**
- 90%+ endpoints fully aligned
- <5% endpoints with real issues
- 100% commits validated automatically
- Contract tests in CI/CD
- Zero production contract violations

**Leading Indicators:**
- Pre-commit validation adoption rate
- Contract test coverage percentage
- Time to detect contract violations (< 5 minutes)
- Contract-related bug reports (trending to zero)

---

## Maintenance & Ownership

**Responsibilities:**
- **Backend Team**: Maintain handler validation, OpenAPI spec accuracy
- **Frontend Team**: Use generated types, update UI when contracts change
- **DevOps**: Maintain CI/CD validation, monitor contract health
- **Architect (KC)**: Define contract standards, review breaking changes

**Regular Reviews:**
- Weekly: Review contract validation failures
- Monthly: Audit OpenAPI spec accuracy
- Quarterly: Assess prevention strategy effectiveness

---

## Emergency Procedures

**Contract Violation in Production:**
1. 🚨 Identify affected endpoint
2. 🔍 Determine source (OpenAPI/UI/API)
3. 🛠️ Apply hotfix to most flexible layer (usually API)
4. 📝 Create post-mortem
5. 🎯 Add regression test to prevent recurrence

**Bypass Validation (Emergency Only):**
```bash
# Pre-commit bypass
git commit --no-verify

# CI/CD bypass (requires approval)
# Add [skip-validation] to commit message
```

**Post-Bypass Actions:**
- Create ticket to fix validation failure
- Document why bypass was needed
- Review process to prevent future bypasses

---

## Conclusion

This prevention strategy transforms contract validation from **reactive** (finding issues in production) to **proactive** (preventing issues before commit).

**Key Principles:**
1. OpenAPI spec is single source of truth
2. Validation happens early and often
3. Automation over manual checks
4. Fast feedback loops
5. Clear ownership and accountability

**Expected Impact:**
- 90% reduction in contract-related bugs
- Faster development (catch issues in seconds, not days)
- Higher confidence in deployments
- Better developer experience

Implementation of this strategy will ensure the three-way contract (OpenAPI ↔ UI ↔ API) stays aligned throughout the development lifecycle.
