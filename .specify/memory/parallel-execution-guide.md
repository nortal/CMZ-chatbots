# Parallel Task Execution Guide for CMZ Chatbots

## Strategy 1: Multi-Developer Parallel Execution

### Team Assignment (3-4 developers)

**Developer 1: Handler & Backend**
```bash
# Branch: feature/phase1-handlers
git checkout -b feature/phase1-handlers
# Tasks: T001-T006 (Handler forwarding fixes)
```

**Developer 2: Test Coverage**
```bash
# Branch: feature/phase1-tests
git checkout -b feature/phase1-tests
# Tasks: T007-T012 (Unit/Integration tests)
```

**Developer 3: E2E Tests**
```bash
# Branch: feature/phase1-e2e
git checkout -b feature/phase1-e2e
# Tasks: T013-T019 (Playwright tests)
```

**Developer 4: Documentation & Tools**
```bash
# Branch: feature/phase1-docs
git checkout -b feature/phase1-docs
# Tasks: T006, T020-T025 (Documentation & logging setup)
```

## Strategy 2: Single Developer with AI Agents (Claude Code)

### Using Task Tool for Parallel AI Execution

```python
# Example: Execute multiple analysis tasks in parallel
from Task import Task

# Launch parallel analysis agents
tasks = [
    Task(
        subagent_type="general-purpose",
        description="Analyze handlers",
        prompt="Analyze all impl modules for forwarding issues in backend/api/src/main/python/openapi_server/impl/"
    ),
    Task(
        subagent_type="general-purpose",
        description="Generate unit tests",
        prompt="Create unit tests for uncovered handlers in impl/handlers.py"
    ),
    Task(
        subagent_type="general-purpose",
        description="Create E2E tests",
        prompt="Create Playwright test for admin role login and dashboard"
    )
]

# These run in PARALLEL, not sequentially
```

### Claude Code Parallel Commands

```bash
# Use multiple terminal sessions or tmux/screen
# Terminal 1: Backend fixes
/sc:task "Fix all handler forwarding in family.py and users.py"

# Terminal 2: Test generation
/sc:task "Generate unit tests for all uncovered handlers"

# Terminal 3: E2E tests
/sc:task "Create Playwright tests for all 6 user roles"

# Terminal 4: Documentation
/sc:task "Document forwarding patterns and create FORWARDING-PATTERN.md"
```

## Strategy 3: Automated Parallel Execution Script

### Create Parallel Execution Runner

```bash
#!/bin/bash
# scripts/parallel_tasks.sh

# Run test tasks in parallel
(
    echo "Starting Test Coverage Tasks (T007-T012)..."
    python scripts/generate_unit_tests.py &
    python scripts/generate_integration_tests.py &
    python scripts/generate_contract_tests.py &
) &

# Run E2E tasks in parallel
(
    echo "Starting E2E Test Tasks (T013-T019)..."
    npx playwright codegen http://localhost:3001 --save-storage=auth-admin.json &
    npx playwright codegen http://localhost:3001 --save-storage=auth-zookeeper.json &
    npx playwright codegen http://localhost:3001 --save-storage=auth-parent.json &
) &

# Run documentation tasks
(
    echo "Starting Documentation Tasks..."
    python scripts/generate_api_docs.py &
    python scripts/analyze_code_coverage.py &
) &

wait # Wait for all background jobs to complete
echo "All parallel tasks completed!"
```

## Strategy 4: Make Targets for Parallel Execution

### Update Makefile for Parallel Tasks

```makefile
# Makefile additions

# Run all Phase 1 tasks in parallel
phase1-parallel:
	@echo "Starting Phase 1 parallel tasks..."
	@$(MAKE) -j4 fix-handlers test-coverage e2e-tests docs

fix-handlers:
	python scripts/validate_handler_forwarding_comprehensive.py
	python scripts/fix_handler_forwarding.py

test-coverage:
	pytest --cov=openapi_server --cov-report=html
	python scripts/generate_missing_tests.py

e2e-tests:
	cd backend/api/src/main/python/tests/playwright && \
	npm run test:parallel

docs:
	python scripts/generate_documentation.py

# Run with: make -j4 phase1-parallel
```

## Strategy 5: GitHub Actions for CI/CD Parallel Execution

### .github/workflows/parallel-tasks.yml

```yaml
name: Parallel Task Execution

on:
  push:
    branches: [feature/phase1-*]

jobs:
  handler-fixes:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Fix Handler Forwarding
        run: |
          python scripts/fix_handler_forwarding.py
          python scripts/validate_handler_forwarding.py

  test-coverage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Generate Tests
        run: |
          python scripts/generate_unit_tests.py
          pytest --cov=openapi_server

  e2e-tests:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        role: [admin, zookeeper, educator, parent, student, visitor]
    steps:
      - uses: actions/checkout@v2
      - name: E2E Test for ${{ matrix.role }}
        run: |
          npx playwright test --grep "${{ matrix.role }}"

  documentation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Generate Documentation
        run: |
          python scripts/generate_documentation.py
```

## Practical Parallel Execution Plan

### Week 1: Maximum Parallelization

**Monday Morning (4 parallel streams):**
```bash
# Stream 1: Handler Fixes (T001-T006)
git checkout -b fix/handlers
./scripts/fix_all_handlers.sh &

# Stream 2: Test Generation (T007-T012)
git checkout -b test/coverage
./scripts/generate_all_tests.sh &

# Stream 3: E2E Setup (T013-T019)
git checkout -b test/e2e
./scripts/create_e2e_suite.sh &

# Stream 4: Documentation (T006, prep for Phase 2)
git checkout -b docs/phase1
./scripts/document_patterns.sh &
```

**Using GNU Parallel for File Operations:**
```bash
# Install GNU parallel
brew install parallel

# Process multiple files in parallel
find backend/api/src/main/python/openapi_server/impl -name "*.py" | \
  parallel -j8 python scripts/validate_handler.py {}

# Generate tests in parallel
echo "handlers users family animals" | \
  parallel -j4 pytest-generate --module {}
```

## Task Groupings for Parallel Execution

### Group A: No Dependencies (Can start immediately)
- T006: Document forwarding pattern
- T007-T011: All unit/integration tests
- T013-T018: All E2E tests
- T020-T024: Logging setup
- T026-T031: Metrics collection

### Group B: Sequential Within, Parallel Across
- Handler fixes (T001→T002→T003→T004→T005)
- But can run parallel to Group A

### Group C: Phase 2 Prep (While Phase 1 runs)
- T020-T025: Logging (parallel to fixes)
- T033-T038: Tracing setup
- T039-T045: Cache design

## Tools for Parallel Task Management

### 1. Task Runners
```bash
# Using npm-run-all
npm install --save-dev npm-run-all
# package.json
"scripts": {
  "parallel": "run-p test:* e2e:* lint:*"
}
```

### 2. Process Managers
```bash
# Using PM2
npm install -g pm2
pm2 start scripts/task1.js
pm2 start scripts/task2.js
pm2 start scripts/task3.js
pm2 status # Monitor all parallel tasks
```

### 3. Docker Compose for Service Parallelization
```yaml
# docker-compose.parallel.yml
version: '3.8'
services:
  test-runner:
    build: .
    command: pytest

  e2e-runner:
    build: .
    command: npx playwright test

  doc-generator:
    build: .
    command: python generate_docs.py
```

## Monitoring Parallel Execution

### Progress Dashboard
```bash
# Create a simple progress monitor
watch -n 1 'echo "=== PARALLEL TASK STATUS ==="; \
  echo "Handlers: $(grep -c "✓" logs/handlers.log)/6"; \
  echo "Tests: $(pytest --collect-only -q | wc -l)"; \
  echo "E2E: $(find tests/e2e -name "*.spec.js" | wc -l)"; \
  echo "Coverage: $(coverage report | grep TOTAL | awk "{print $4}")"; '
```

## Recommended Approach for Solo Developer

If you're working alone, here's the most practical approach:

1. **Use Claude Code agents in parallel** (multiple Task calls)
2. **Set up Make targets** for parallel execution
3. **Create batch scripts** for related tasks
4. **Use Git branches** to isolate parallel work
5. **Leverage CI/CD** for automated parallel testing

### Example Solo Developer Day:
```bash
# Morning: Start 3 parallel AI agents
/sc:task "Fix all handler forwarding issues"
/sc:task "Generate comprehensive test suite"
/sc:task "Create E2E tests for all roles"

# Afternoon: Merge results
git merge fix/handlers
git merge test/coverage
git merge test/e2e

# Evening: Deploy and validate
make validate-all
git push origin feature/phase1-complete
```

## Key Benefits of Parallel Execution

1. **Time Reduction**: 70 tasks in parallel = ~1 week vs 70 sequential = ~3 months
2. **Early Problem Detection**: Issues found simultaneously, not sequentially
3. **Resource Utilization**: Max out CPU, memory, and human resources
4. **Momentum**: Visible progress maintains motivation
5. **Risk Mitigation**: Parallel branches allow safe experimentation

## Remember: Not Everything Can Be Parallel

Some tasks MUST be sequential:
- T001 → T005 (analyze → fix → validate)
- T012 (coverage report needs tests complete)
- Phase dependencies (Phase 1 → Phase 2 → Phase 3)

But within phases, maximize parallelization!