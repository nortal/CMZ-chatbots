#!/bin/bash

###############################################################################
# Assistant Management E2E Test Runner
#
# Runs comprehensive E2E tests for Assistant Management feature using
# Playwright with visible browser mode.
#
# Prerequisites:
# - Frontend running on http://localhost:3000
# - Backend running on http://localhost:8081
# - Test user credentials: test@cmz.org / testpass123
#
# Usage:
#   ./run-assistant-tests.sh [test-name]
#
# Examples:
#   ./run-assistant-tests.sh                    # Run all tests
#   ./run-assistant-tests.sh "Authentication"   # Run specific test
###############################################################################

set -e

# Configuration
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3000}"
BACKEND_URL="${BACKEND_URL:-http://localhost:8081}"
TEST_DIR="tests/e2e"
REPORT_DIR="tests/reports"
SCREENSHOT_DIR="tests/screenshots"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}======================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}======================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

check_service() {
    local service_name=$1
    local service_url=$2

    echo -n "Checking $service_name at $service_url... "
    if curl -s -f -o /dev/null "$service_url"; then
        print_success "$service_name is running"
        return 0
    else
        print_error "$service_name is not responding"
        return 1
    fi
}

# Main execution
print_header "Assistant Management E2E Test Suite"

# Pre-flight checks
echo ""
print_header "Pre-flight Checks"

if ! check_service "Frontend" "$FRONTEND_URL"; then
    print_error "Frontend is not running. Please start it with: cd frontend && npm start"
    exit 1
fi

if ! check_service "Backend" "$BACKEND_URL/health"; then
    print_warning "Backend health check failed. Trying auth endpoint..."
    if ! check_service "Backend Auth" "$BACKEND_URL/auth"; then
        print_error "Backend is not running. Please start it with: make run-api"
        exit 1
    fi
fi

# Create directories
echo ""
print_header "Setting up test environment"
mkdir -p "$REPORT_DIR"
mkdir -p "$SCREENSHOT_DIR"
print_success "Test directories created"

# Install Playwright if needed
if ! command -v npx playwright &> /dev/null; then
    print_warning "Playwright not found. Installing..."
    npm install -D @playwright/test
    npx playwright install chromium
    print_success "Playwright installed"
fi

# Run tests
echo ""
print_header "Running E2E Tests"

export FRONTEND_URL
export BACKEND_URL

if [ -z "$1" ]; then
    # Run all tests
    print_warning "Running all Assistant Management tests..."
    npx playwright test assistant-management.spec.js --config=playwright.config.js
else
    # Run specific test
    print_warning "Running test matching: $1"
    npx playwright test assistant-management.spec.js --config=playwright.config.js --grep "$1"
fi

TEST_EXIT_CODE=$?

# Results
echo ""
print_header "Test Results"

if [ $TEST_EXIT_CODE -eq 0 ]; then
    print_success "All tests passed!"
    echo ""
    echo "Screenshots saved to: $SCREENSHOT_DIR"
    echo "HTML report: $REPORT_DIR/html/index.html"
    echo "JSON results: $REPORT_DIR/results.json"
else
    print_error "Tests failed with exit code: $TEST_EXIT_CODE"
    echo ""
    echo "Check screenshots in: $SCREENSHOT_DIR"
    echo "View HTML report: $REPORT_DIR/html/index.html"
fi

# Open report if available
if [ -f "$REPORT_DIR/html/index.html" ]; then
    echo ""
    read -p "Open HTML report in browser? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        open "$REPORT_DIR/html/index.html"
    fi
fi

exit $TEST_EXIT_CODE
