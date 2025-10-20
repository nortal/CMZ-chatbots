#!/bin/bash
# CMZ Implementation Discovery Tool
# Prevents re-implementing existing functionality

set -e

OPERATION=${1:-}
FEATURE=${2:-}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "========================================="
echo "CMZ Implementation Discovery Tool"
echo "========================================="

if [ -z "$OPERATION" ]; then
    echo "Usage: $0 <operation_name> [feature_area]"
    echo "Example: $0 family_list_get family"
    echo "Example: $0 auth_login auth"
    exit 1
fi

echo -e "\n${BLUE}Searching for: ${OPERATION}${NC}"
if [ -n "$FEATURE" ]; then
    echo -e "${BLUE}Feature area: ${FEATURE}${NC}"
fi

IMPL_DIR="backend/api/src/main/python/openapi_server/impl"

echo -e "\n${YELLOW}=== 1. Checking Handler Implementations ===${NC}"
echo "Searching for handle_${OPERATION} functions..."
if grep -r "def handle_${OPERATION}" "$IMPL_DIR" 2>/dev/null; then
    echo -e "${GREEN}✅ Handler implementation found${NC}"
else
    echo -e "${RED}❌ No handler implementation found${NC}"
fi

echo -e "\n${YELLOW}=== 2. Checking Handler Mappings ===${NC}"
echo "Searching in handlers.py..."
if grep "'${OPERATION}':" "$IMPL_DIR/handlers.py" 2>/dev/null; then
    echo -e "${GREEN}✅ Handler mapping exists${NC}"
else
    echo -e "${RED}❌ No handler mapping found${NC}"
    echo "  Add to handler_map in handlers.py:"
    echo "  '${OPERATION}': handle_${OPERATION},"
fi

echo -e "\n${YELLOW}=== 3. Checking DynamoDB Models ===${NC}"
if [ -n "$FEATURE" ]; then
    echo "Searching for ${FEATURE} models..."
    if ls "$IMPL_DIR/utils/orm/models/"*"${FEATURE}"* 2>/dev/null; then
        echo -e "${GREEN}✅ DynamoDB models found:${NC}"
        ls -la "$IMPL_DIR/utils/orm/models/"*"${FEATURE}"*
    else
        echo -e "${YELLOW}⚠️  No DynamoDB models found for ${FEATURE}${NC}"
    fi
fi

echo -e "\n${YELLOW}=== 4. Checking Mock Implementations ===${NC}"
if [ -n "$FEATURE" ]; then
    echo "Searching for ${FEATURE}_mock..."
    if ls "$IMPL_DIR/"*"${FEATURE}"*mock* 2>/dev/null; then
        echo -e "${GREEN}✅ Mock implementation found:${NC}"
        ls -la "$IMPL_DIR/"*"${FEATURE}"*mock*
    else
        echo -e "${YELLOW}⚠️  No mock implementation${NC}"
    fi
fi

echo -e "\n${YELLOW}=== 5. Checking Controller ===${NC}"
CONTROLLER_DIR="backend/api/src/main/python/openapi_server/controllers"
if [ -n "$FEATURE" ]; then
    echo "Searching for ${FEATURE}_controller.py..."
    if [ -f "$CONTROLLER_DIR/${FEATURE}_controller.py" ]; then
        echo -e "${GREEN}✅ Controller exists${NC}"
        echo "Checking for operation..."
        if grep "def ${OPERATION}" "$CONTROLLER_DIR/${FEATURE}_controller.py" 2>/dev/null; then
            echo -e "${GREEN}✅ Operation defined in controller${NC}"
        else
            echo -e "${RED}❌ Operation not in controller${NC}"
        fi
    else
        echo -e "${RED}❌ Controller not found${NC}"
    fi
fi

echo -e "\n${YELLOW}=== 6. Testing Endpoint ===${NC}"
# Try to determine endpoint from operation name
# Common patterns: operation_get -> GET /operation
#                  operation_post -> POST /operation
#                  operation_id_get -> GET /operation/{id}

if [[ $OPERATION == *"_get" ]]; then
    METHOD="GET"
elif [[ $OPERATION == *"_post" ]]; then
    METHOD="POST"
elif [[ $OPERATION == *"_put" ]]; then
    METHOD="PUT"
elif [[ $OPERATION == *"_patch" ]]; then
    METHOD="PATCH"
elif [[ $OPERATION == *"_delete" ]]; then
    METHOD="DELETE"
else
    METHOD="GET"
fi

# Try to construct endpoint
if [ -n "$FEATURE" ]; then
    ENDPOINT="/${FEATURE}"
    echo "Testing: curl -X $METHOD http://localhost:8080${ENDPOINT}"

    if curl -s -o /dev/null -w "%{http_code}" -X "$METHOD" "http://localhost:8080${ENDPOINT}" | grep -q "200\|201\|204"; then
        echo -e "${GREEN}✅ Endpoint is working${NC}"
    else
        STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X "$METHOD" "http://localhost:8080${ENDPOINT}")
        echo -e "${YELLOW}⚠️  Endpoint returned: $STATUS${NC}"
    fi
fi

echo -e "\n${YELLOW}=== 7. Git History ===${NC}"
echo "Recent commits related to ${OPERATION} or ${FEATURE}:"
git log --oneline --grep="${OPERATION}\|${FEATURE}" -i | head -5 || echo "No related commits found"

echo -e "\n${YELLOW}=== 8. Related Files ===${NC}"
echo "Files that might be relevant:"
find "$IMPL_DIR" -name "*${FEATURE}*" -type f 2>/dev/null | head -10 || echo "No related files found"

echo -e "\n${BLUE}=========================================${NC}"
echo -e "${BLUE}Summary:${NC}"
echo -e "${BLUE}=========================================${NC}"

# Provide recommendation
if grep -q "def handle_${OPERATION}" "$IMPL_DIR"/**/*.py 2>/dev/null; then
    echo -e "${GREEN}✅ Implementation exists - DO NOT RE-IMPLEMENT${NC}"
    echo "Check for routing/mapping issues if not working"
elif ls "$IMPL_DIR/utils/orm/models/"*"${FEATURE}"* 2>/dev/null; then
    echo -e "${YELLOW}⚠️  DynamoDB models exist - Use existing models${NC}"
    echo "Implement handler using existing DynamoDB models"
else
    echo -e "${RED}❌ No implementation found - Safe to implement${NC}"
    echo "Create new implementation following existing patterns"
fi