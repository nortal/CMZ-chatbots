#!/bin/bash

# Two-Step Playwright Validation
# PR003946-96: Validate login users first, then run full suite
# Usage: ./run-two-step-validation.sh [--headed] [--debug]

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
cd "$SCRIPT_DIR"

# Parse command line arguments
HEADED=""
DEBUG=""
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3001}"

while [[ $# -gt 0 ]]; do
  case $1 in
    --headed)
      HEADED="--headed"
      shift
      ;;
    --debug)
      DEBUG="--debug"
      shift
      ;;
    *)
      echo "Unknown argument: $1"
      echo "Usage: $0 [--headed] [--debug]"
      exit 1
      ;;
  esac
done

echo "🎭 CMZ Chatbot Two-Step Playwright Validation"
echo "============================================="
echo ""
echo "📋 Step 1: Login User Validation"
echo "📋 Step 2: Full Test Suite (only if Step 1 passes)"
echo ""
echo "🌐 Frontend URL: $FRONTEND_URL"
echo "🖥️  Backend URL: http://localhost:8080"
echo ""

# Check if servers are running
echo "🔍 Checking server availability..."

if ! curl -s "http://localhost:3001" > /dev/null 2>&1; then
  echo "❌ Frontend server not running at http://localhost:3001"
  echo "   Please run: cd frontend && npm run dev"
  exit 1
fi
echo "✅ Frontend server running"

if ! curl -s "http://localhost:8080" > /dev/null 2>&1; then
  echo "❌ Backend server not running at http://localhost:8080"  
  echo "   Please run: make run-api"
  exit 1
fi
echo "✅ Backend server running"

echo ""
echo "🚀 Starting STEP 1: Login User Validation..."
echo "============================================="

# Run Step 1: Login validation
STEP1_EXIT_CODE=0
FRONTEND_URL="$FRONTEND_URL" npx playwright test \
  --config config/playwright.config.js \
  validate-login-users.js \
  --reporter=line \
  --workers=1 \
  $HEADED $DEBUG || STEP1_EXIT_CODE=$?

if [ $STEP1_EXIT_CODE -ne 0 ]; then
  echo ""
  echo "❌ STEP 1 FAILED: Login user validation failed"
  echo "🛑 Stopping here - resolve login issues before proceeding to full test suite"
  echo ""
  echo "💡 Common solutions:"
  echo "   • Check if both frontend (3001) and backend (8080) servers are running"
  echo "   • Verify CORS configuration between frontend and backend"
  echo "   • Check test data in test_data.json contains expected users"
  echo "   • Review browser console for JavaScript errors"
  echo ""
  exit $STEP1_EXIT_CODE
fi

echo ""
echo "✅ STEP 1 PASSED: All login users validated successfully!"
echo ""
echo "🚀 Starting STEP 2: Full Playwright Test Suite..."
echo "================================================="

# Run Step 2: Full test suite
STEP2_EXIT_CODE=0
FRONTEND_URL="$FRONTEND_URL" npx playwright test \
  --config config/playwright.config.js \
  specs/ \
  --reporter=html \
  --reporter=junit \
  --reporter=json \
  --reporter=line \
  $HEADED $DEBUG || STEP2_EXIT_CODE=$?

echo ""
if [ $STEP2_EXIT_CODE -eq 0 ]; then
  echo "🎉 SUCCESS: Both validation steps completed!"
  echo "✅ STEP 1: Login user validation - PASSED"
  echo "✅ STEP 2: Full test suite - PASSED"
else
  echo "⚠️  MIXED RESULTS:"
  echo "✅ STEP 1: Login user validation - PASSED"
  echo "❌ STEP 2: Full test suite - SOME FAILURES"
  echo ""
  echo "💡 This is expected during development. Step 1 success means"
  echo "   the login infrastructure is working correctly."
fi

echo ""
echo "📊 DETAILED REPORTS:"
echo "   🎭 Playwright HTML Report: reports/html-report/index.html"
echo "   📊 JSON Results: reports/test-results.json" 
echo "   📄 JUnit XML: reports/junit-results.xml"

exit $STEP2_EXIT_CODE