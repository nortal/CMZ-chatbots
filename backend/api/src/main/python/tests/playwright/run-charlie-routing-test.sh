#!/bin/bash

# CRITICAL TEST: Validate Charlie Routing Fix
# Purpose: Verify ChatWrapper extracts animalId and Charlie responds as elephant

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "🐘 CHARLIE ROUTING FIX VALIDATION TEST"
echo "=========================================="
echo ""
echo "PURPOSE: Verify that the ChatWrapper component correctly extracts"
echo "animalId from URL and Charlie responds as an elephant (not default Zara)"
echo ""
echo "WHAT WAS FIXED:"
echo "- Added ChatWrapper component with useSearchParams()"
echo "- Modified /chat route to extract animalId from URL"
echo "- ChatWrapper passes animalId prop to Chat component"
echo ""
echo "CRITICAL VALIDATIONS:"
echo "✓ Frontend extracts animalId='charlie_003' from URL"
echo "✓ Backend receives animalId='charlie_003' (NOT 'default')"
echo "✓ Charlie identifies as an ELEPHANT"
echo "✓ Charlie uses motherly language (dear, little one, sweetheart)"
echo "✓ No Zara or generic zoo ambassador responses"
echo ""
echo "=========================================="
echo ""

# Create screenshots directory
mkdir -p screenshots

# Check frontend is running
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3001}"
echo "🔍 Checking frontend at: $FRONTEND_URL"
if ! curl -sf "$FRONTEND_URL" > /dev/null; then
    echo "❌ ERROR: Frontend is not running at $FRONTEND_URL"
    echo "Please start the frontend with: cd frontend && npm run dev"
    exit 1
fi
echo "✅ Frontend is running"
echo ""

# Check backend is running
BACKEND_URL="${BACKEND_URL:-http://localhost:8080}"
echo "🔍 Checking backend at: $BACKEND_URL"
# Check if port is accessible (accept any response including 501)
if ! curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL" | grep -q "[0-9]"; then
    echo "❌ ERROR: Backend is not running at $BACKEND_URL"
    echo "Please start the backend with: cd backend && make run-api"
    exit 1
fi
echo "✅ Backend is running"
echo ""

# Run Playwright test with visible browser
echo "🎬 Running Playwright test with VISIBLE browser..."
echo "=========================================="
echo ""

FRONTEND_URL="$FRONTEND_URL" npx playwright test \
    --config config/playwright.config.js \
    --headed \
    --workers=1 \
    specs/validate-charlie-routing-fix.spec.js \
    --reporter=list

TEST_EXIT_CODE=$?

echo ""
echo "=========================================="
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "🎉 SUCCESS: Charlie routing fix validation PASSED!"
    echo ""
    echo "VERIFIED:"
    echo "✅ animalId correctly extracted from URL"
    echo "✅ animalId='charlie_003' sent to backend"
    echo "✅ Charlie responds as elephant"
    echo "✅ Charlie uses motherly personality"
    echo "✅ No default/Zara personality issues"
    echo ""
    echo "📸 Screenshots saved to: $SCRIPT_DIR/screenshots/"
else
    echo "❌ FAILED: Charlie routing fix validation FAILED"
    echo ""
    echo "TROUBLESHOOTING:"
    echo "1. Check screenshots in: $SCRIPT_DIR/screenshots/"
    echo "2. Review browser console logs (shown above)"
    echo "3. Check API logs for animalId values"
    echo "4. Verify ChatWrapper component is being used in App.tsx"
    echo "5. Verify /chat route uses ChatWrapper (not Chat directly)"
    echo ""
fi
echo "=========================================="

exit $TEST_EXIT_CODE
