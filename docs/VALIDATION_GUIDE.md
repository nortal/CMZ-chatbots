# CMZ Chatbots Comprehensive Validation Guide

This guide explains how to run all validation tests across your entire CMZ Chatbots project stack.

## 🚀 Quick Start

### Run All Validations
```bash
./scripts/run_all_validations.sh
# or
./scripts/run_all_validations.sh --all
```

### Quick Smoke Tests
```bash
./scripts/run_all_validations.sh --quick
```

### Show Available Options
```bash
./scripts/run_all_validations.sh --help
```

## 📋 Available Validation Types

### 🏗️ Build Validation (`--build-only`)
Validates your API build pipeline:
- **API Code Generation**: `make generate-api`
- **API Build**: `make build-api`
- **Docker Container**: Validates containerization

**When to use**: Before deployment, after OpenAPI spec changes

```bash
./scripts/run_all_validations.sh --build-only
```

### 🧪 Unit Tests (`--unit-only`)
Runs Python unit tests for business logic:
- **Location**: `backend/api/src/main/python/tests/unit/`
- **Framework**: pytest with coverage reporting
- **Scope**: Individual functions and classes

**When to use**: During development, before commits

```bash
./scripts/run_all_validations.sh --unit-only
```

### 🔗 Integration Tests (`--integration-only`)
Tests API endpoints and database connectivity:
- **API Validation Epic**: Core endpoint testing
- **Endpoint Integration**: Full request/response cycles
- **Database Persistence**: DynamoDB connectivity

**When to use**: Before merging, after API changes

```bash
./scripts/run_all_validations.sh --integration-only
```

### 🎭 Playwright E2E Tests (`--playwright-only`)
Browser-based end-to-end testing:
- **Step 1 Validation**: Critical login functionality (≥5/6 browsers must pass)
- **Persistence Tests**: UI → API → Database verification
- **User Journey Testing**: Complete workflows

**Requirements**:
- Frontend running at `http://localhost:3001`
- API running at `http://localhost:8080`

```bash
# Ensure services are running first
make run-api &
cd frontend && npm run dev &

# Run E2E tests
./scripts/run_all_validations.sh --playwright-only
```

### 🔒 Security Tests (`--security`)
Security scanning and vulnerability assessment:
- **Security Environment Check**: Dependencies and configuration
- **Secret Detection**: Scans for exposed secrets
- **Vulnerability Assessment**: Known security issues

**When to use**: Before production deployment, regularly as maintenance

```bash
./scripts/run_all_validations.sh --security
```

### 📊 TDD Coverage Analysis (`--tdd-only`)
Comprehensive test-driven development analysis:
- **Test Analysis**: 16 files, 343 test methods analyzed
- **Coverage Calculation**: 22% ticket coverage (22/100 tickets)
- **Persistence Verification**: Both mandatory tests implemented
- **Chart Generation**: Professional CMZ-branded coverage charts

**When to use**: Weekly TDD health checks, before reporting

```bash
./scripts/run_all_validations.sh --tdd-only
```

### ✅ Code Quality (`--quality-only`)
Code quality and style validation:
- **Python Linting**: flake8, black formatting
- **TypeScript Checking**: Frontend type validation
- **Complexity Analysis**: Code maintainability metrics

**When to use**: Before code reviews, regularly during development

```bash
./scripts/run_all_validations.sh --quality-only
```

## 🎯 Recommended Validation Workflows

### 📦 Pre-Commit Workflow
```bash
# Quick validation before commits
./scripts/run_all_validations.sh --quick
```
**Includes**: Environment + Build + Unit Tests

### 🔄 Pre-Merge Workflow
```bash
# Comprehensive validation before merging
./scripts/run_all_validations.sh --api-only
```
**Includes**: Environment + Build + Unit + Integration Tests

### 🚀 Pre-Deployment Workflow
```bash
# Full validation before production
./scripts/run_all_validations.sh --all
```
**Includes**: All validation categories

### 🎭 UI Development Workflow
```bash
# Start services
make run-api &
cd frontend && npm run dev &

# Test E2E functionality
./scripts/run_all_validations.sh --playwright-only
```

### 📊 Weekly TDD Review
```bash
# Generate TDD coverage reports
./scripts/run_all_validations.sh --tdd-only

# View generated chart
open tdd_coverage_charts/tdd_coverage_overview.png
```

## 🔧 Configuration & Environment

### Required Commands
The validation script checks for these required commands:
- `python3` - Python runtime
- `node` - Node.js runtime
- `npm` - Package manager
- `docker` - Container runtime
- `make` - Build system
- `git` - Version control

### Environment Variables
```bash
# API Configuration
API_URL=http://localhost:8080              # API server URL
FRONTEND_URL=http://localhost:3001         # Frontend URL

# Optional: Jira Integration
JIRA_API_TOKEN=your_token_here            # Enables Jira reporting
JIRA_EMAIL=your_email@company.com         # Jira authentication

# Optional: Teams Integration
TEAMS_WEBHOOK_URL=your_webhook_url        # Enables Teams reporting

# Optional: AWS Configuration
AWS_PROFILE=your_profile                  # AWS credentials
DYNAMODB_ENDPOINT_URL=http://localhost:8000  # Local DynamoDB
```

## 📊 Validation Reports

### Report Locations
```
validation_reports/
├── validation_YYYYMMDD_HHMMSS.log          # Detailed execution log
├── validation_summary_YYYYMMDD_HHMMSS.md   # Summary report
└── ...
```

### Sample Report Structure
```markdown
# CMZ Chatbots Validation Report

**Generated**: Sat Sep 13 11:34:23 PDT 2025
**Duration**: 45 seconds
**Total Validations**: 12
**Passed**: 11
**Failed**: 1

## Results Summary

| Validation | Status |
|------------|--------|
| API Code Generation | ✅ PASS |
| Python Unit Tests | ✅ PASS |
| Playwright Step 1 Validation | ❌ FAIL |
| Security Environment Check | ✅ PASS |
```

## 🚨 Troubleshooting Common Issues

### API Tests Failing
```bash
# Ensure API server is running
make run-api

# Check API health
curl http://localhost:8080/health
```

### Playwright Tests Failing
```bash
# Ensure frontend is running
cd frontend && npm run dev

# Check frontend availability
curl http://localhost:3001
```

### Build Failures
```bash
# Clean and rebuild
make clean-api
make generate-api
make build-api
```

### Environment Issues
```bash
# Check command availability
which python3 node npm docker make git

# Check Python dependencies
cd backend/api/src/main/python
pip install -r requirements.txt
```

### Permission Issues
```bash
# Make script executable
chmod +x scripts/run_all_validations.sh

# Check Docker permissions
docker info
```

## 🔄 Integration with Other Commands

### Git Hooks Integration
```bash
# Setup TDD git hook
./scripts/setup_tdd_git_hook.sh

# The post-merge hook will automatically run validations
```

### Make Target Integration
Add to your `Makefile`:
```makefile
validate-quick:
	./scripts/run_all_validations.sh --quick

validate-all:
	./scripts/run_all_validations.sh --all

validate-playwright:
	make run-api &
	./scripts/run_all_validations.sh --playwright-only
	make stop-api
```

### CI/CD Integration
```yaml
# Example GitHub Actions integration
name: Validation Suite
on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Environment
        run: |
          # Setup Python, Node, etc.
      - name: Run Validation Suite
        run: ./scripts/run_all_validations.sh --all
```

## 🎯 Validation Success Criteria

### Build Validation
- ✅ OpenAPI code generation completes without errors
- ✅ Docker build succeeds
- ✅ All dependencies install correctly

### Unit Tests
- ✅ All unit tests pass
- ✅ Coverage threshold met (if configured)
- ✅ No critical test failures

### Integration Tests
- ✅ API endpoints respond correctly
- ✅ Database connectivity confirmed
- ✅ Business logic integration verified

### Playwright E2E
- ✅ Login validation passes ≥5/6 browsers
- ✅ Persistence tests verify UI→API→Database flow
- ✅ Critical user journeys complete successfully

### Security
- ✅ No high/critical vulnerabilities found
- ✅ No exposed secrets detected
- ✅ Security dependencies up to date

### TDD Coverage
- ✅ Both mandatory persistence tests implemented
- ✅ Coverage analysis completes successfully
- ✅ Charts generate without errors
- ✅ Daily calculations stored properly

## 📈 Continuous Improvement

### Daily Usage
```bash
# Morning: Quick health check
./scripts/run_all_validations.sh --quick

# During development: Specific validations
./scripts/run_all_validations.sh --unit-only
./scripts/run_all_validations.sh --integration-only

# End of day: Full validation
./scripts/run_all_validations.sh --all
```

### Weekly Reviews
```bash
# Generate TDD coverage report for team review
./scripts/run_all_validations.sh --tdd-only

# Security audit
./scripts/run_all_validations.sh --security

# Performance baseline
./scripts/run_all_validations.sh --playwright-only
```

## 🛠️ Customization

### Adding New Validation Categories
Edit `scripts/run_all_validations.sh`:

1. Add new validation function:
```bash
validate_your_category() {
    print_status "INFO" "🎯 Your Category Validation"
    run_validation "Your Specific Test" "your_test_command"
    print_status "PASS" "✅ Your category completed"
}
```

2. Add to main execution logic:
```bash
--your-category-only)
    print_header
    validate_environment
    validate_your_category
    generate_validation_report
    ;;
```

3. Update help documentation in `show_usage()`

### Custom Report Formats
The validation system generates both:
- **Markdown reports** (human-readable)
- **Detailed logs** (machine-readable)

You can customize report generation in the `generate_validation_report()` function.

---

## 🎉 Summary

The CMZ Chatbots validation suite provides comprehensive testing across your entire stack:

- **8 validation categories** covering build, tests, security, and quality
- **Flexible execution modes** from quick smoke tests to full validation
- **Professional reporting** with detailed logs and summaries
- **Integration-ready** for CI/CD and development workflows

**Quick Reference**:
```bash
./scripts/run_all_validations.sh --help     # Show all options
./scripts/run_all_validations.sh --quick    # Fast validation
./scripts/run_all_validations.sh --all      # Complete validation
./scripts/run_all_validations.sh --tdd-only # TDD coverage analysis
```

For questions or issues, check the troubleshooting section or review the detailed logs generated in `validation_reports/`.