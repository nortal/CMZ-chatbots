#!/bin/bash

# Security Environment Check
# Validates security configuration and dependencies

echo "🔍 Running security environment check..."

# Check for required security dependencies
echo "Checking frontend dependencies..."
cd frontend

MISSING_DEPS=()

if ! npm list dompurify >/dev/null 2>&1; then
    MISSING_DEPS+=("dompurify")
fi

if ! npm list yup >/dev/null 2>&1; then
    MISSING_DEPS+=("yup")
fi

if [ ${#MISSING_DEPS[@]} -eq 0 ]; then
    echo "✅ All security dependencies are installed"
else
    echo "❌ Missing security dependencies: ${MISSING_DEPS[*]}"
    echo "Run: npm install ${MISSING_DEPS[*]}"
fi

# Check for vulnerable test files
cd ..
echo "Checking for vulnerable test files..."

if [ -f "backend/api/src/main/python/tests/playwright/specs/dynamodb-consistency-validation.spec.js.vulnerable" ]; then
    echo "✅ Original vulnerable file backed up"
else
    echo "⚠️ Original file not backed up"
fi

# Check for security utilities
if [ -f "frontend/src/utils/inputValidation.ts" ]; then
    echo "✅ Input validation utilities present"
else
    echo "❌ Input validation utilities missing"
fi

if [ -f "frontend/src/hooks/useSecureFormHandling.ts" ]; then
    echo "✅ Secure form handling hook present"
else
    echo "❌ Secure form handling hook missing"
fi

if [ -f "frontend/src/config/security.ts" ]; then
    echo "✅ Security configuration present"
else
    echo "❌ Security configuration missing"
fi

echo "Security check complete!"
