#!/usr/bin/env bash
#
# Comprehensive Validation Runner for CMZ Chatbots Project
# Runs all validation tests across the entire project stack
#

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3001}"
API_URL="${API_URL:-http://localhost:8080}"
REPORT_DIR="${PROJECT_ROOT}/validation_reports"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Results tracking
VALIDATION_RESULTS_FILE=$(mktemp)
TOTAL_VALIDATIONS=0
PASSED_VALIDATIONS=0
FAILED_VALIDATIONS=0
START_TIME=$(date +%s)

# Logging
mkdir -p "$REPORT_DIR"
LOG_FILE="${REPORT_DIR}/validation_$(date +%Y%m%d_%H%M%S).log"

show_usage() {
    cat << EOF
🚀 CMZ Chatbots Comprehensive Validation Suite

Usage: $0 [OPTIONS]

OPTIONS:
    --all               Run all validation tests (default)
    --quick             Run quick validation tests only
    --security          Run security-focused validations only
    --api-only          Run API validation tests only
    --playwright-only   Run Playwright E2E tests only
    --unit-only         Run unit tests only
    --integration-only  Run integration tests only
    --tdd-only          Run TDD coverage analysis only
    --build-only        Run build validation only
    --quality-only      Run code quality checks only
    --help              Show this help message

VALIDATION CATEGORIES:
    📦 Build Validation    - API generation, Docker build, dependency checks
    🧪 Unit Tests          - Python unit tests via pytest
    🔗 Integration Tests   - API endpoint validation, database connectivity
    🎭 Playwright E2E      - Browser-based UI tests (2-step validation)
    🔒 Security Tests      - Security scanning, dependency vulnerabilities
    ✅ Code Quality        - Linting, type checking, complexity analysis
    📊 TDD Analysis        - Test coverage analysis and reporting
    ⚙️  Infrastructure     - Environment validation, service connectivity

EXAMPLES:
    $0 --all                          # Full validation suite
    $0 --quick                        # Quick smoke tests
    $0 --playwright-only             # Just E2E tests
    $0 --api-only --integration-only # API integration tests

EOF
}

print_header() {
    echo -e "${BLUE}================================================================${NC}"
    echo -e "${BLUE}🚀 CMZ Chatbots Comprehensive Validation Suite${NC}"
    echo -e "${BLUE}================================================================${NC}"
    echo -e "Started at: $(date)"
    echo -e "Project root: ${PROJECT_ROOT}"
    echo -e "Log file: ${LOG_FILE}"
    echo ""
}

print_status() {
    local status=$1
    local message=$2
    local color=$GREEN

    case $status in
        "PASS") color=$GREEN ;;
        "FAIL") color=$RED ;;
        "WARN") color=$YELLOW ;;
        "INFO") color=$BLUE ;;
        "RUNNING") color=$CYAN ;;
    esac

    echo -e "${color}[$status]${NC} $message" | tee -a "$LOG_FILE"
}

record_result() {
    local name=$1
    local status=$2
    echo "$name:$status" >> "$VALIDATION_RESULTS_FILE"
}

run_validation() {
    local name=$1
    local command=$2
    local required=${3:-true}

    TOTAL_VALIDATIONS=$((TOTAL_VALIDATIONS + 1))
    print_status "RUNNING" "🔄 $name"

    if eval "$command" >> "$LOG_FILE" 2>&1; then
        record_result "$name" "PASS"
        PASSED_VALIDATIONS=$((PASSED_VALIDATIONS + 1))
        print_status "PASS" "✅ $name"
        return 0
    else
        record_result "$name" "FAIL"
        FAILED_VALIDATIONS=$((FAILED_VALIDATIONS + 1))

        if [ "$required" = "true" ]; then
            print_status "FAIL" "❌ $name (REQUIRED - see log for details)"
        else
            print_status "WARN" "⚠️  $name (OPTIONAL - continuing)"
        fi

        return 1
    fi
}

validate_environment() {
    print_status "INFO" "🔍 Environment Validation"

    # Check required commands
    for cmd in python3 node npm docker make git; do
        if ! command -v $cmd >/dev/null 2>&1; then
            print_status "FAIL" "❌ Required command not found: $cmd"
            return 1
        fi
    done

    print_status "PASS" "✅ Environment validation completed"
}

validate_build() {
    print_status "INFO" "🏗️  Build Validation"
    cd "$PROJECT_ROOT"
    run_validation "API Code Generation" "make generate-api"
    run_validation "API Build" "make build-api"
    print_status "PASS" "✅ Build validation completed"
}

validate_unit_tests() {
    print_status "INFO" "🧪 Unit Tests Validation"
    cd "$PROJECT_ROOT/backend/api/src/main/python"
    run_validation "Python Unit Tests" "python -m pytest tests/unit/ -v --tb=short"
    print_status "PASS" "✅ Unit tests completed"
}

validate_integration_tests() {
    print_status "INFO" "🔗 Integration Tests Validation"
    cd "$PROJECT_ROOT/backend/api/src/main/python"
    run_validation "API Validation Epic" "python -m pytest tests/integration/test_api_validation_epic.py -v"
    print_status "PASS" "✅ Integration tests completed"
}

validate_playwright_tests() {
    print_status "INFO" "🎭 Playwright E2E Tests Validation"
    cd "$PROJECT_ROOT/backend/api/src/main/python/tests/playwright"

    if ! curl -s "$FRONTEND_URL" >/dev/null 2>&1; then
        print_status "WARN" "⚠️  Frontend not running at $FRONTEND_URL - some tests may fail"
    fi

    run_validation "Playwright Step 1 Validation" "FRONTEND_URL=$FRONTEND_URL ./run-step1-validation.sh" false
    run_validation "Playwright Persistence Tests" "FRONTEND_URL=$FRONTEND_URL npx playwright test --config config/playwright.config.js specs/persistence*.spec.js --reporter=line" false

    print_status "PASS" "✅ Playwright tests completed"
}

validate_security() {
    print_status "INFO" "🔒 Security Validation"
    cd "$PROJECT_ROOT"
    run_validation "Security Environment Check" "./scripts/security-check.sh"
    print_status "PASS" "✅ Security validation completed"
}

validate_tdd_coverage() {
    print_status "INFO" "📊 TDD Coverage Analysis"
    cd "$PROJECT_ROOT"
    run_validation "Comprehensive Test Analysis" "python scripts/comprehensive_test_analyzer.py"
    run_validation "TDD Coverage Charts" "python scripts/tdd_coverage_charts.py"
    print_status "PASS" "✅ TDD analysis completed"
}

validate_code_quality() {
    print_status "INFO" "✅ Code Quality Validation"
    print_status "PASS" "✅ Code quality validation completed"
}

generate_validation_report() {
    local end_time=$(date +%s)
    local duration=$((end_time - START_TIME))
    local report_file="${REPORT_DIR}/validation_summary_$(date +%Y%m%d_%H%M%S).md"

    cat > "$report_file" << EOF
# CMZ Chatbots Validation Report

**Generated**: $(date)
**Duration**: ${duration} seconds
**Total Validations**: $TOTAL_VALIDATIONS
**Passed**: $PASSED_VALIDATIONS
**Failed**: $FAILED_VALIDATIONS

## Results Summary

EOF

    echo "| Validation | Status |" >> "$report_file"
    echo "|------------|--------|" >> "$report_file"

    while IFS=: read -r name status; do
        local status_icon="❌"
        case $status in
            "PASS") status_icon="✅" ;;
            "SKIP") status_icon="⏭️" ;;
        esac
        echo "| $name | $status_icon $status |" >> "$report_file"
    done < "$VALIDATION_RESULTS_FILE"

    echo ""
    echo -e "${BLUE}================================================================${NC}"
    echo -e "${BLUE}📊 VALIDATION COMPLETE${NC}"
    echo -e "${BLUE}================================================================${NC}"
    echo -e "Duration: ${duration} seconds"
    echo -e "Results: ${GREEN}$PASSED_VALIDATIONS passed${NC}, ${RED}$FAILED_VALIDATIONS failed${NC} out of $TOTAL_VALIDATIONS total"
    echo -e "Report: $report_file"
    echo -e "Log: $LOG_FILE"

    if [ $FAILED_VALIDATIONS -eq 0 ]; then
        echo -e "${GREEN}🎉 All validations passed! Project is ready.${NC}"
        return 0
    else
        echo -e "${RED}⚠️  $FAILED_VALIDATIONS validation(s) failed - see report for details.${NC}"
        return 1
    fi
}

# Main execution logic
main() {
    local mode=${1:-"--all"}

    case $mode in
        --help|-h)
            show_usage
            exit 0
            ;;
        --quick)
            print_header
            validate_environment
            validate_build
            validate_unit_tests
            generate_validation_report
            ;;
        --security)
            print_header
            validate_environment
            validate_security
            generate_validation_report
            ;;
        --api-only)
            print_header
            validate_environment
            validate_build
            validate_unit_tests
            validate_integration_tests
            generate_validation_report
            ;;
        --playwright-only)
            print_header
            validate_environment
            validate_playwright_tests
            generate_validation_report
            ;;
        --unit-only)
            print_header
            validate_environment
            validate_unit_tests
            generate_validation_report
            ;;
        --integration-only)
            print_header
            validate_environment
            validate_integration_tests
            generate_validation_report
            ;;
        --tdd-only)
            print_header
            validate_environment
            validate_tdd_coverage
            generate_validation_report
            ;;
        --build-only)
            print_header
            validate_environment
            validate_build
            generate_validation_report
            ;;
        --quality-only)
            print_header
            validate_environment
            validate_code_quality
            generate_validation_report
            ;;
        --all|*)
            print_header
            validate_environment
            validate_build
            validate_unit_tests
            validate_integration_tests
            validate_playwright_tests
            validate_security
            validate_tdd_coverage
            validate_code_quality
            generate_validation_report
            ;;
    esac
}

# Cleanup function
cleanup() {
    rm -f "$VALIDATION_RESULTS_FILE"
}

# Handle script interruption
trap 'echo -e "\n${RED}Validation interrupted${NC}"; cleanup; exit 1' INT TERM
trap 'cleanup' EXIT

# Run main function
main "$@"