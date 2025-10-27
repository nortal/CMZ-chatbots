#!/bin/bash
# OpenAPI Routing Validation Script
# Prevents the silent operationId regression that breaks Flask routing
# Usage: ./scripts/validate_openapi_routing.sh

set -e

echo "🔍 Validating OpenAPI routing configuration..."

SPEC_FILE="backend/api/openapi_spec.yaml"
EXPECTED_MIN_OPERATION_IDS=40

# 1. Count total operationIds
OPERATION_ID_COUNT=$(grep -c "operationId:" "$SPEC_FILE" || echo 0)
echo "📊 Total operationIds found: $OPERATION_ID_COUNT"

if [ "$OPERATION_ID_COUNT" -lt "$EXPECTED_MIN_OPERATION_IDS" ]; then
    echo "❌ CRITICAL: Too few operationIds! Expected at least $EXPECTED_MIN_OPERATION_IDS, found $OPERATION_ID_COUNT"
    echo "🚨 This indicates OpenAPI regeneration removed operationIds - Flask routing will be broken!"
    exit 1
fi

# 2. Check critical conversation endpoints
echo "🔍 Checking conversation endpoints..."
CONVERSATION_OPERATIONS=$(grep -c "operationId.*convo" "$SPEC_FILE" || echo 0)
EXPECTED_CONVO_OPS=4  # convo_turn_post, convo_turn_stream_get, convo_history_get, convo_history_delete

if [ "$CONVERSATION_OPERATIONS" -ne "$EXPECTED_CONVO_OPS" ]; then
    echo "❌ CRITICAL: Conversation endpoints missing operationIds!"
    echo "Expected $EXPECTED_CONVO_OPS conversation operationIds, found $CONVERSATION_OPERATIONS"
    echo "🔍 Current conversation operationIds:"
    grep -A2 -B2 "operationId.*convo" "$SPEC_FILE" || echo "None found!"
    exit 1
fi

# 3. List found conversation operationIds
echo "✅ Found conversation operationIds:"
grep "operationId.*convo" "$SPEC_FILE"

# 4. Test controller imports (if Python environment available)
if command -v python3 &> /dev/null; then
    echo "🔍 Testing controller imports..."
    cd backend/api/src/main/python
    if python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from openapi_server.controllers import conversation_controller
    convo_funcs = [f for f in dir(conversation_controller) if 'convo' in f]
    print('✅ Controller functions available:', convo_funcs)
    if len(convo_funcs) < 4:
        print('❌ Missing controller functions!')
        sys.exit(1)
except ImportError as e:
    print(f'❌ Controller import failed: {e}')
    sys.exit(1)
" 2>/dev/null; then
        echo "✅ Controller validation passed"
    else
        echo "❌ Controller validation failed"
        exit 1
    fi
    cd - > /dev/null
fi

echo "✅ OpenAPI routing validation passed!"
echo "🚀 All conversation endpoints properly configured for Flask routing"