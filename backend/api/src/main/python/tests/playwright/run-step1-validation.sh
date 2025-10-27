#!/bin/bash

# Step 1 Validation Script
# Validates core login functionality before full test suite
# Based on lessons learned 2025-09-12

set -e

echo "🚀 Step 1 Validation: Testing login functionality for all test users"
echo "📋 This must pass (5/6+ browsers) before proceeding to Step 2"
echo ""

# Ensure we're in the correct directory
cd "$(dirname "$0")"

# Set frontend URL
export FRONTEND_URL=http://localhost:3001

echo "🔍 Running Step 1 validation for all 5 test users across 6 browsers..."
echo ""

# Run the full Step 1 validation
npx playwright test \
    --config config/playwright.config.js \
    --grep "🔐 Login User Validation - STEP 1" \
    --reporter=line \
    --workers=1

# Check results
EXIT_CODE=$?

echo ""
echo "📊 Step 1 Validation Results:"
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ All browsers passed - Ready for Step 2!"
    echo ""
    echo "🚀 To run Step 2 (full test suite):"
    echo "   FRONTEND_URL=http://localhost:3001 npx playwright test --config config/playwright.config.js --reporter=line"
else
    echo "❌ Step 1 validation failed - Fix authentication issues before Step 2"
    echo ""
    echo "🔧 Common fixes:"
    echo "   1. Check if auth controller is connected to implementation"
    echo "   2. Verify test users exist in backend auth.py"
    echo "   3. Ensure CORS is properly configured"
    echo "   4. Rebuild backend: make build-api && make run-api"
    echo ""
    echo "📖 See STEP1_VALIDATION_GUIDE.md for detailed troubleshooting"
fi

exit $EXIT_CODE