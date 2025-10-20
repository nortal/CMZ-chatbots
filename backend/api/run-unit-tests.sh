#!/bin/bash
# Fast Unit Test Runner for TDD Workflow
# Optimized for rapid red-green-refactor cycles

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PYTHON_DIR="src/main/python"
UNIT_TEST_DIR="tests/unit"

echo -e "${BLUE}🧪 Fast Unit Test Runner for TDD${NC}"
echo -e "${BLUE}================================${NC}"

# Check if we're in the right directory
if [ ! -d "$PYTHON_DIR" ]; then
    echo -e "${RED}❌ Error: Must run from backend/api directory${NC}"
    echo -e "${YELLOW}Current directory: $(pwd)${NC}"
    echo -e "${YELLOW}Expected to find: $PYTHON_DIR${NC}"
    exit 1
fi

# Change to Python directory
cd "$PYTHON_DIR"

# Check if unit tests exist
if [ ! -d "$UNIT_TEST_DIR" ]; then
    echo -e "${RED}❌ Error: Unit tests directory not found: $UNIT_TEST_DIR${NC}"
    exit 1
fi

# Count test files
UNIT_TEST_COUNT=$(find $UNIT_TEST_DIR -name "test_*.py" | wc -l)
echo -e "${BLUE}📊 Found $UNIT_TEST_COUNT unit test files${NC}"

# Function to run specific test categories
run_tests() {
    local marker="$1"
    local description="$2"
    
    echo -e "${YELLOW}🔍 Running $description tests...${NC}"
    
    if [ -z "$marker" ]; then
        # Run all unit tests
        pytest "$UNIT_TEST_DIR" \
            --tb=short \
            --disable-warnings \
            --maxfail=5 \
            -v \
            --durations=10
    else
        # Run specific marker
        pytest "$UNIT_TEST_DIR" \
            -m "$marker" \
            --tb=short \
            --disable-warnings \
            --maxfail=5 \
            -v \
            --durations=5
    fi
}

# Parse command line arguments
case "${1:-all}" in
    "auth"|"authentication")
        run_tests "auth" "Authentication"
        ;;
    "validation"|"valid")
        run_tests "validation" "Validation" 
        ;;
    "error"|"errors")
        run_tests "error_handling" "Error Handling"
        ;;
    "all"|"")
        echo -e "${GREEN}🚀 Running all unit tests for TDD workflow${NC}"
        start_time=$(date +%s)
        
        # Set environment for unit testing
        export PERSISTENCE_MODE=memory
        export JWT_SECRET_KEY=unit-test-secret-key
        export TESTING=true
        
        # Run all unit tests with optimized settings
        if pytest "$UNIT_TEST_DIR" \
            --tb=short \
            --disable-warnings \
            --maxfail=10 \
            -v \
            --durations=10; then
            
            end_time=$(date +%s)
            duration=$((end_time - start_time))
            
            echo -e "${GREEN}✅ All unit tests passed in ${duration}s${NC}"
            echo -e "${GREEN}🎯 TDD workflow ready!${NC}"
        else
            echo -e "${RED}❌ Some unit tests failed${NC}"
            echo -e "${YELLOW}💡 Fix failing tests and run again${NC}"
            exit 1
        fi
        ;;
    "fast"|"tdd")
        echo -e "${GREEN}⚡ Super-fast TDD mode${NC}"
        export PERSISTENCE_MODE=memory
        export JWT_SECRET_KEY=unit-test-secret-key
        export TESTING=true
        
        # Ultra-fast mode: fail on first error, minimal output
        pytest "$UNIT_TEST_DIR" \
            --tb=line \
            --disable-warnings \
            --maxfail=1 \
            -q \
            --durations=0
        ;;
    "watch")
        echo -e "${GREEN}👀 Watch mode: Re-running tests on file changes${NC}"
        echo -e "${YELLOW}Press Ctrl+C to exit${NC}"
        
        if command -v ptw >/dev/null 2>&1; then
            export PERSISTENCE_MODE=memory
            export JWT_SECRET_KEY=unit-test-secret-key
            export TESTING=true
            
            ptw "$UNIT_TEST_DIR" \
                --runner "pytest --tb=short --disable-warnings --maxfail=1 -q"
        else
            echo -e "${RED}❌ pytest-watch not installed${NC}"
            echo -e "${YELLOW}💡 Install with: pip install pytest-watch${NC}"
            exit 1
        fi
        ;;
    "help"|"-h"|"--help")
        echo -e "${BLUE}Usage: $0 [OPTION]${NC}"
        echo ""
        echo -e "${YELLOW}Options:${NC}"
        echo "  all         Run all unit tests (default)"
        echo "  auth        Run authentication tests only"
        echo "  validation  Run validation tests only"
        echo "  error       Run error handling tests only"
        echo "  fast        Ultra-fast mode for TDD (fail-fast)"
        echo "  watch       Watch mode - rerun on file changes"
        echo "  help        Show this help message"
        echo ""
        echo -e "${YELLOW}Examples:${NC}"
        echo "  $0              # Run all tests"
        echo "  $0 auth         # Run auth tests only"
        echo "  $0 fast         # TDD mode"
        echo "  $0 watch        # Watch mode"
        ;;
    *)
        echo -e "${RED}❌ Unknown option: $1${NC}"
        echo -e "${YELLOW}💡 Use '$0 help' for usage information${NC}"
        exit 1
        ;;
esac