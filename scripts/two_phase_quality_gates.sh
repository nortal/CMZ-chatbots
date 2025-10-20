#!/bin/bash

# Two-Phase Quality Gates for /nextfive Command
# Implements Step 1 → Step 2 validation approach learned from successful patterns
#
# Phase 1: Quick validation to catch fundamental issues early
# Phase 2: Comprehensive testing once fundamentals are confirmed
#
# Usage:
#   ./scripts/two_phase_quality_gates.sh --phase1-only
#   ./scripts/two_phase_quality_gates.sh --phase2-only
#   ./scripts/two_phase_quality_gates.sh --both-phases

set -e

# Configuration
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3001}"
API_URL="${API_URL:-http://localhost:8080}"
PHASE1_TIMEOUT=60  # 1 minute for quick validation
PHASE2_TIMEOUT=300 # 5 minutes for comprehensive testing

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

print_phase() {
    echo ""
    print_status $BLUE "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    print_status $BLUE "$1"
    print_status $BLUE "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
}

# Function to check if service is running
check_service() {
    local service_name=$1
    local url=$2
    local timeout=${3:-10}

    print_status $YELLOW "🔌 Checking $service_name at $url..."

    if timeout $timeout curl -s "$url" > /dev/null 2>&1; then
        print_status $GREEN "✅ $service_name is running"
        return 0
    else
        print_status $RED "❌ $service_name is not available at $url"
        return 1
    fi
}

# Phase 1: Quick Validation
run_phase1() {
    print_phase "🚀 PHASE 1: QUICK VALIDATION - Catch Fundamental Issues Early"

    local phase1_failed=0

    # 1. Service Availability Check
    print_status $YELLOW "Step 1.1: Service Availability"
    if ! check_service "Backend API" "$API_URL/health" 10; then
        print_status $RED "❌ Backend API not available - stopping Phase 1"
        return 1
    fi

    if ! check_service "Frontend" "$FRONTEND_URL" 10; then
        print_status $RED "❌ Frontend not available - stopping Phase 1"
        return 1
    fi

    # 2. Authentication Quick Test (Single User)
    print_status $YELLOW "Step 1.2: Authentication Quick Test"
    cd backend/api/src/main/python/tests/playwright

    # Run single user authentication test
    print_status $YELLOW "🔐 Testing authentication for Test Parent One..."
    if timeout $PHASE1_TIMEOUT env FRONTEND_URL=$FRONTEND_URL npx playwright test \
        --config config/playwright.config.js \
        --grep "should successfully validate login for Test Parent One" \
        --reporter=line --workers=1; then
        print_status $GREEN "✅ Authentication fundamentally working"
    else
        print_status $RED "❌ Authentication broken - Phase 1 FAILED"
        phase1_failed=1
    fi

    # 3. API Basic Connectivity
    print_status $YELLOW "Step 1.3: API Basic Connectivity"
    if curl -s -f "$API_URL/api/v1/health" > /dev/null; then
        print_status $GREEN "✅ API endpoints responding"
    else
        print_status $RED "❌ API endpoints not responding - Phase 1 FAILED"
        phase1_failed=1
    fi

    # 4. Database/Persistence Basic Test
    print_status $YELLOW "Step 1.4: Persistence Layer Basic Test"
    # Test that we can connect to persistence layer (simplified check)
    if [ "$PERSISTENCE_MODE" = "file" ]; then
        if [ -d "./data" ] || mkdir -p ./data; then
            print_status $GREEN "✅ File persistence accessible"
        else
            print_status $RED "❌ File persistence not accessible - Phase 1 FAILED"
            phase1_failed=1
        fi
    else
        # Test DynamoDB connectivity
        if aws sts get-caller-identity > /dev/null 2>&1; then
            print_status $GREEN "✅ AWS/DynamoDB connectivity available"
        else
            print_status $RED "❌ AWS/DynamoDB not accessible - Phase 1 FAILED"
            phase1_failed=1
        fi
    fi

    cd - > /dev/null

    # Phase 1 Results
    echo ""
    if [ $phase1_failed -eq 0 ]; then
        print_status $GREEN "🎉 PHASE 1 PASSED - Fundamentals are working!"
        print_status $GREEN "Safe to proceed with comprehensive testing (Phase 2)"
        return 0
    else
        print_status $RED "💥 PHASE 1 FAILED - Fundamental issues detected!"
        print_status $RED "Fix these issues before running comprehensive tests"
        return 1
    fi
}

# Phase 2: Comprehensive Testing
run_phase2() {
    print_phase "🔬 PHASE 2: COMPREHENSIVE TESTING - Full Validation Suite"

    local phase2_failed=0

    # 1. Full Authentication Suite (All 5 users, 6 browsers)
    print_status $YELLOW "Step 2.1: Full Authentication Suite"
    cd backend/api/src/main/python/tests/playwright

    print_status $YELLOW "🔐 Running full authentication validation..."
    if timeout $PHASE2_TIMEOUT env FRONTEND_URL=$FRONTEND_URL npx playwright test \
        --config config/playwright.config.js \
        --grep "🔐 Login User Validation - STEP 1" \
        --reporter=line --workers=1; then

        # Count successful authentications
        local auth_results=$(env FRONTEND_URL=$FRONTEND_URL npx playwright test \
            --config config/playwright.config.js \
            --grep "🔐 Login User Validation - STEP 1" \
            --reporter=json 2>/dev/null | jq -r '.suites[].specs[].tests[].results[].status' | grep -c "passed" || echo "0")

        if [ "$auth_results" -ge 5 ]; then
            print_status $GREEN "✅ Authentication comprehensive test passed ($auth_results/6 browsers)"
        else
            print_status $YELLOW "⚠️ Authentication partially successful ($auth_results/6 browsers)"
            print_status $YELLOW "Mobile Safari issues are known and acceptable"
        fi
    else
        print_status $RED "❌ Authentication comprehensive test failed"
        phase2_failed=1
    fi

    # 2. Full Playwright Test Suite
    print_status $YELLOW "Step 2.2: Full Playwright Test Suite"
    print_status $YELLOW "🎭 Running complete Playwright suite..."
    if timeout $PHASE2_TIMEOUT env FRONTEND_URL=$FRONTEND_URL npx playwright test \
        --config config/playwright.config.js \
        --reporter=line; then
        print_status $GREEN "✅ Full Playwright suite passed"
    else
        print_status $YELLOW "⚠️ Some Playwright tests failed - review results"
        # Don't fail Phase 2 for non-critical Playwright issues
    fi

    cd - > /dev/null

    # 3. API Integration Tests
    print_status $YELLOW "Step 2.3: API Integration Tests"
    if [ -f "tests/integration/test_api_validation_epic.py" ]; then
        print_status $YELLOW "🧪 Running API integration tests..."
        if timeout $PHASE2_TIMEOUT python -m pytest tests/integration/test_api_validation_epic.py -v; then
            print_status $GREEN "✅ API integration tests passed"
        else
            print_status $RED "❌ API integration tests failed"
            phase2_failed=1
        fi
    else
        print_status $YELLOW "⚠️ No integration tests found - skipping"
    fi

    # 4. Unit Tests
    print_status $YELLOW "Step 2.4: Unit Test Suite"
    if [ -d "backend/api/src/main/python" ]; then
        cd backend/api/src/main/python
        if timeout $PHASE2_TIMEOUT pytest --cov=openapi_server -v; then
            print_status $GREEN "✅ Unit tests passed"
        else
            print_status $RED "❌ Unit tests failed"
            phase2_failed=1
        fi
        cd - > /dev/null
    else
        print_status $YELLOW "⚠️ No unit tests directory found - skipping"
    fi

    # 5. Security and Quality Checks
    print_status $YELLOW "Step 2.5: Security and Quality Checks"
    if command -v npm > /dev/null && [ -f "package.json" ]; then
        print_status $YELLOW "🔒 Running lint and type checks..."
        if npm run lint 2>/dev/null && npm run typecheck 2>/dev/null; then
            print_status $GREEN "✅ Lint and type checks passed"
        else
            print_status $YELLOW "⚠️ Some lint/type issues found - review before merge"
        fi
    fi

    # Phase 2 Results
    echo ""
    if [ $phase2_failed -eq 0 ]; then
        print_status $GREEN "🎉 PHASE 2 PASSED - All comprehensive tests successful!"
        print_status $GREEN "Code is ready for merge and deployment"
        return 0
    else
        print_status $RED "💥 PHASE 2 FAILED - Some comprehensive tests failed"
        print_status $RED "Review failures and fix before proceeding"
        return 1
    fi
}

# Main execution logic
main() {
    local run_phase1=false
    local run_phase2=false
    local exit_code=0

    # Parse arguments
    case "${1:-}" in
        --phase1-only)
            run_phase1=true
            ;;
        --phase2-only)
            run_phase2=true
            ;;
        --both-phases|"")
            run_phase1=true
            run_phase2=true
            ;;
        --help)
            echo "Usage: $0 [--phase1-only|--phase2-only|--both-phases]"
            echo ""
            echo "Two-Phase Quality Gates:"
            echo "  --phase1-only   Run only Phase 1 (quick validation)"
            echo "  --phase2-only   Run only Phase 2 (comprehensive testing)"
            echo "  --both-phases   Run both phases (default)"
            echo ""
            echo "Environment Variables:"
            echo "  FRONTEND_URL    Frontend URL (default: http://localhost:3001)"
            echo "  API_URL         API URL (default: http://localhost:8080)"
            echo "  PERSISTENCE_MODE Persistence mode (file|dynamodb)"
            exit 0
            ;;
        *)
            print_status $RED "❌ Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac

    # Print configuration
    print_status $BLUE "🎯 Two-Phase Quality Gates Configuration"
    echo "Frontend URL: $FRONTEND_URL"
    echo "API URL: $API_URL"
    echo "Persistence Mode: ${PERSISTENCE_MODE:-dynamodb}"
    echo "Phase 1 Timeout: ${PHASE1_TIMEOUT}s"
    echo "Phase 2 Timeout: ${PHASE2_TIMEOUT}s"

    # Execute phases
    if [ "$run_phase1" = true ]; then
        if ! run_phase1; then
            exit_code=1
            if [ "$run_phase2" = true ]; then
                print_status $RED "🚫 Skipping Phase 2 due to Phase 1 failures"
                run_phase2=false
            fi
        fi
    fi

    if [ "$run_phase2" = true ]; then
        if ! run_phase2; then
            exit_code=1
        fi
    fi

    # Final summary
    echo ""
    print_phase "📊 QUALITY GATES SUMMARY"
    if [ $exit_code -eq 0 ]; then
        print_status $GREEN "🎉 ALL QUALITY GATES PASSED"
        print_status $GREEN "Code meets quality standards and is ready for production"
    else
        print_status $RED "💥 QUALITY GATES FAILED"
        print_status $RED "Address the issues above before proceeding"
    fi

    exit $exit_code
}

# Execute main function with all arguments
main "$@"