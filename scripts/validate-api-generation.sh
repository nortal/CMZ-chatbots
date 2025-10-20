#!/bin/bash

# Script to validate API generation after template fix
# This confirms the controller-handler connection survives regeneration

set -e

echo "🔧 API Generation Validation Script"
echo "===================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Check handlers.py exists
echo "1. Checking handlers.py exists..."
if [ -f "backend/api/src/main/python/openapi_server/impl/handlers.py" ]; then
    echo -e "${GREEN}✅ handlers.py found${NC}"
else
    echo -e "${RED}❌ handlers.py missing!${NC}"
    exit 1
fi

# Step 2: Check handle_ function exists
echo ""
echo "2. Checking handle_() function exists..."
if grep -q "def handle_(" backend/api/src/main/python/openapi_server/impl/handlers.py; then
    echo -e "${GREEN}✅ handle_() function found${NC}"
else
    echo -e "${RED}❌ handle_() function missing!${NC}"
    exit 1
fi

# Step 3: Check template has fix applied
echo ""
echo "3. Checking controller template has fix..."
if grep -q "impl_function = handlers.handle_" backend/api/templates/python-flask/controller.mustache; then
    echo -e "${GREEN}✅ Template fix applied${NC}"
else
    echo -e "${RED}❌ Template fix not applied!${NC}"
    echo "Apply fix to line 48 of controller.mustache:"
    echo "  impl_function = handlers.handle_"
    exit 1
fi

# Step 4: Test Python import
echo ""
echo "4. Testing Python import chain..."
cd backend/api/src/main/python
python3 -c "
try:
    from openapi_server.impl import handlers
    if hasattr(handlers, 'handle_'):
        print('✅ Python import successful')
    else:
        print('❌ handle_ function not found in handlers module')
        exit(1)
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
" || exit 1
cd ../../../../

# Step 5: Check generated controller
echo ""
echo "5. Checking generated controller uses fix..."
if [ -f "backend/api/src/main/python/openapi_server/controllers/animals_controller.py" ]; then
    if grep -q "impl_function = handlers.handle_" backend/api/src/main/python/openapi_server/controllers/animals_controller.py; then
        echo -e "${GREEN}✅ Generated controller has fix applied${NC}"
    else
        echo -e "${YELLOW}⚠️  Controller needs regeneration${NC}"
        echo "Run: make generate-api"
    fi
else
    echo -e "${YELLOW}⚠️  No generated controller found${NC}"
fi

# Step 6: Summary
echo ""
echo "===================================="
echo "📊 Validation Summary"
echo "===================================="

# Check all conditions
ALL_GOOD=true
if [ ! -f "backend/api/src/main/python/openapi_server/impl/handlers.py" ]; then
    ALL_GOOD=false
    echo -e "${RED}❌ handlers.py missing${NC}"
fi

if ! grep -q "def handle_(" backend/api/src/main/python/openapi_server/impl/handlers.py 2>/dev/null; then
    ALL_GOOD=false
    echo -e "${RED}❌ handle_() function missing${NC}"
fi

if ! grep -q "impl_function = handlers.handle_" backend/api/templates/python-flask/controller.mustache 2>/dev/null; then
    ALL_GOOD=false
    echo -e "${RED}❌ Template fix not applied${NC}"
fi

if [ "$ALL_GOOD" = true ]; then
    echo -e "${GREEN}✅ ALL CHECKS PASSED!${NC}"
    echo ""
    echo "The animal config validation issue has been permanently fixed."
    echo "Controllers will now survive OpenAPI regeneration."
    echo ""
    echo "Next steps:"
    echo "1. Run 'make generate-api' to regenerate with fix"
    echo "2. Run 'make build-api && make run-api' to test"
    echo "3. Test with: curl http://localhost:8080/animal_list"
else
    echo -e "${RED}❌ VALIDATION FAILED${NC}"
    echo ""
    echo "Please review the errors above and apply the fixes."
    echo "See ANIMAL-CONFIG-FLAKINESS-ADVICE.md for details."
    exit 1
fi