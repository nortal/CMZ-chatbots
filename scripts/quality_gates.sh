#!/bin/bash
set -e

echo "🔍 Running CMZ Quality Gates..."

# Function to run check and track results
run_check() {
    local check_name="$1"
    local command="$2"
    echo "🔄 Running $check_name..."

    if eval "$command"; then
        echo "✅ $check_name: PASSED"
        return 0
    else
        echo "❌ $check_name: FAILED"
        return 1
    fi
}

cd "$(dirname "$0")/.."
failed_checks=0

# Python import validation
if ! run_check "Python Import Validation" "cd backend/api/src/main/python && python -c 'from openapi_server.models import *; from openapi_server.impl import handlers' 2>/dev/null"; then
    ((failed_checks++))
fi

# Unit tests
if ! run_check "Unit Tests" "pytest backend/api/src/main/python/openapi_server/test/ -v 2>/dev/null"; then
    ((failed_checks++))
fi

# Code formatting
if ! run_check "Code Formatting" "black --check backend/api/src/main/python/openapi_server/impl/ 2>/dev/null"; then
    echo "   Run: black backend/api/src/main/python/openapi_server/impl/"
    ((failed_checks++))
fi

# Linting
if ! run_check "Code Linting" "flake8 backend/api/src/main/python/openapi_server/impl/ 2>/dev/null"; then
    ((failed_checks++))
fi

# Security scanning (if bandit is available)
if command -v bandit >/dev/null 2>&1; then
    if ! run_check "Security Scan" "bandit -r backend/api/src/main/python/openapi_server/impl/ -ll 2>/dev/null"; then
        ((failed_checks++))
    fi
fi

# API health check (if running)
if curl -f http://localhost:8080/health >/dev/null 2>&1; then
    if ! run_check "API Health Check" "curl -f http://localhost:8080/health"; then
        ((failed_checks++))
    fi
else
    echo "⚠️  API not running - skipping health check"
fi

# Summary
echo "📊 Quality Gates Summary:"
if [ $failed_checks -eq 0 ]; then
    echo "✅ All quality gates passed!"
    exit 0
else
    echo "❌ $failed_checks quality gate(s) failed"
    echo "   Fix issues before creating MR"
    exit 1
fi