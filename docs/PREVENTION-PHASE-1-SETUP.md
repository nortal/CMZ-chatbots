# Prevention Phase 1 Setup Guide

**Goal**: Prevent OpenAPI-Frontend-Backend contract misalignments through automation

**Timeline**: Week 1 implementation
**Effort**: 2-3 days
**Priority**: HIGH

---

## What Was Implemented

### 1. Pre-Commit Hooks ✅

Automatic contract validation runs before every commit to catch issues immediately.

**Files Created**:
- `scripts/hooks/pre-commit-contract-validation` - Hook script
- `scripts/setup_contract_validation_hooks.sh` - Installation script

**How to Install**:
```bash
# From repository root
./scripts/setup_contract_validation_hooks.sh
```

**How It Works**:
1. Developer runs `git commit`
2. Hook automatically runs `scripts/validate_contracts.py --quick`
3. If validation fails, commit is blocked
4. Developer fixes issues before committing

**Bypass (Emergency Only)**:
```bash
git commit --no-verify
```

---

### 2. GitHub Actions CI/CD Integration ✅

Automated validation runs on every Pull Request and push to main/dev branches.

**File Created**:
- `.github/workflows/contract-validation.yml`

**Triggers**:
- Pull requests affecting:
  - `backend/api/openapi_spec.yaml`
  - `frontend/src/**`
  - `backend/api/src/main/python/openapi_server/impl/**`
- Pushes to `main` or `dev` branches

**What It Does**:
1. Checks out code
2. Installs Python dependencies
3. Runs full contract validation
4. Uploads validation report as artifact
5. Comments on PR with results summary
6. Blocks merge if critical mismatches found

**View Results**:
- Check "Actions" tab in GitHub
- Download validation report artifact
- Review PR comment for summary

---

### 3. TypeScript Type Generation ✅

Automatic generation of TypeScript types from OpenAPI specification.

**Files Modified**:
- `frontend/package.json` - Added `openapi-typescript` dependency and npm script

**How to Use**:
```bash
# From frontend directory
cd frontend
npm install  # Install openapi-typescript if not already installed
npm run generate-types
```

**Output**:
- `frontend/src/api/types.ts` - Generated TypeScript types

**Integration Example**:
```typescript
// Before (manual type definitions)
interface AnimalConfig {
  voice?: string;
  personality?: string;
  systemPrompt?: string;  // Might be out of sync!
}

// After (generated from OpenAPI)
import { paths } from './api/types';

type AnimalConfig = paths['/animal_config']['get']['responses']['200']['content']['application/json'];
// Always in sync with OpenAPI spec!
```

**When to Run**:
- After modifying `backend/api/openapi_spec.yaml`
- Before implementing frontend changes
- Automatically in CI/CD (future enhancement)

---

## Next Steps

### Immediate (This Week)

1. **Install Pre-Commit Hooks** (All Developers)
   ```bash
   ./scripts/setup_contract_validation_hooks.sh
   ```

2. **Generate TypeScript Types** (Frontend Team)
   ```bash
   cd frontend
   npm install
   npm run generate-types
   ```

3. **Test the Workflow**
   - Make a small change to OpenAPI spec
   - Try to commit → hook should run
   - Create PR → GitHub Actions should validate

### Short-Term (Week 2)

4. **Refactor Frontend to Use Generated Types**
   - Update `frontend/src/services/api.ts` to import from `types.ts`
   - Remove manual type definitions
   - Benefit: Compile-time errors for contract violations

5. **Add Type Generation to CI/CD**
   - Add step to GitHub Actions workflow
   - Fail if generated types differ from committed types
   - Ensures types are always up-to-date

6. **Document OpenAPI-First Workflow**
   - Update CLAUDE.md with process
   - Add to developer onboarding
   - Create PR template checklist

---

## Troubleshooting

### Pre-Commit Hook Not Running

**Symptom**: Commits go through without validation

**Solutions**:
1. Check if hook is installed:
   ```bash
   ls -la .git/hooks/pre-commit
   ```

2. Reinstall hook:
   ```bash
   ./scripts/setup_contract_validation_hooks.sh
   ```

3. Verify hook is executable:
   ```bash
   chmod +x .git/hooks/pre-commit
   ```

### Type Generation Fails

**Symptom**: `npm run generate-types` errors

**Solutions**:
1. Ensure openapi-typescript is installed:
   ```bash
   npm install
   ```

2. Check OpenAPI spec is valid:
   ```bash
   python3 -c "import yaml; yaml.safe_load(open('backend/api/openapi_spec.yaml'))"
   ```

3. Verify file paths are correct:
   ```bash
   ls ../backend/api/openapi_spec.yaml
   ```

### GitHub Actions Fails

**Symptom**: PR blocked by failed workflow

**Solutions**:
1. Check "Actions" tab for error details
2. Download validation report artifact
3. Run validation locally:
   ```bash
   ./scripts/validate_contracts.sh
   ```
4. Fix reported issues
5. Push updated code

---

## Success Metrics

### Baseline (Before Phase 1)
- 0% commits validated automatically
- Manual testing only
- 0 automated contract checks

### Target (After Phase 1)
- 100% commits validated automatically
- Contract issues caught in < 5 minutes
- 100% PRs validated before merge

### Monitoring
- Track pre-commit hook usage
- Monitor GitHub Actions success rate
- Measure time-to-detect for contract violations

---

## Phase 2 Preview

**Coming in Week 2-3**: Backend Validation Hardening
- Validation decorators for request handling
- Contract tests for critical endpoints
- Standardized Error model usage

**Coming in Week 4**: Scanner Improvements
- AST parsing for better accuracy
- Call graph analysis
- Reduced false positive rate

---

**Last Updated**: 2025-10-11
**Status**: ✅ Phase 1 Complete - Ready for Team Rollout
**Next Review**: After 1 week of usage
