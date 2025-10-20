#!/bin/bash

# Post-generation script to apply Family Management fixes
# This ensures our fixes persist after OpenAPI regeneration

# Navigate to project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "Applying Family Management post-generation fixes..."

# Fix 1: Update Address model in family_bidirectional.py ORM
echo "  - Fixing Address model zip_code mapping..."
sed -i.bak 's/zip = UnicodeAttribute(null=True)/zip_code = UnicodeAttribute(null=True, attr_name="zipCode")  # Python uses snake_case, DynamoDB uses zipCode/' \
    backend/api/src/main/python/openapi_server/impl/utils/orm/models/family_bidirectional.py 2>/dev/null || true

# Fix 2: Add DoesNotExist import to family_bidirectional.py
echo "  - Adding DoesNotExist import..."
if ! grep -q "from pynamodb.exceptions import DoesNotExist" backend/api/src/main/python/openapi_server/impl/family_bidirectional.py; then
    sed -i.bak '/from botocore.exceptions import ClientError/a\
from pynamodb.exceptions import DoesNotExist' \
        backend/api/src/main/python/openapi_server/impl/family_bidirectional.py
fi

# Fix 3: Create or update handler fixes for Family
echo "  - Creating handler fixes for Family model conversion..."
cat > /tmp/family_handler_fix.py << 'EOF'
def handle_family_details_post(body: Any) -> Tuple[Any, int]:
    """Create new family with proper model handling"""
    from .family import family_details_post

    # Convert FamilyInput model object to dict if needed
    if hasattr(body, 'to_dict'):
        body_dict = body.to_dict()
        # The to_dict() method converts to snake_case, but we need camelCase for the family creation
        # Convert family_name back to familyName
        if 'family_name' in body_dict:
            body_dict['familyName'] = body_dict.pop('family_name')
        if 'preferred_programs' in body_dict:
            body_dict['preferredPrograms'] = body_dict.pop('preferred_programs')
    else:
        body_dict = body

    # Ensure all fields are present in the dictionary
    # The model might not include all fields if not regenerated
    if isinstance(body_dict, dict):
        # Log what we received for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Creating family with data: {body_dict}")

    return family_details_post(body_dict)
EOF

# Check if the fix needs to be applied to handlers.py
if grep -q "def handle_family_details_post" backend/api/src/main/python/openapi_server/impl/handlers.py; then
    echo "  - Family handler already exists, updating..."
    # Extract everything before and after the function
    awk '/def handle_family_details_post/{exit}1' backend/api/src/main/python/openapi_server/impl/handlers.py > /tmp/handlers_before.py
    awk '/^def handle_family_details_get|^def handle_family_/{f=1} f' backend/api/src/main/python/openapi_server/impl/handlers.py | tail -n +2 > /tmp/handlers_after.py

    # Combine with our fix
    cat /tmp/handlers_before.py /tmp/family_handler_fix.py > /tmp/handlers_new.py
    echo "" >> /tmp/handlers_new.py
    echo "" >> /tmp/handlers_new.py
    cat /tmp/handlers_after.py >> /tmp/handlers_new.py

    # Replace the file
    cp /tmp/handlers_new.py backend/api/src/main/python/openapi_server/impl/handlers.py
fi

# Fix 4: Ensure zipCode field conversion in family_bidirectional.py create function
echo "  - Adding zipCode to zip_code conversion in create_family_bidirectional..."
if ! grep -q "Convert zipCode to zip_code for PynamoDB" backend/api/src/main/python/openapi_server/impl/family_bidirectional.py; then
    # Find the line with "address = body.get('address', {})" and add conversion after
    sed -i.bak '/address = body.get.*address.*{}/a\
\
        # Convert zipCode to zip_code for PynamoDB (it expects snake_case)\
        if address and "zipCode" in address:\
            address["zip_code"] = address.pop("zipCode")' \
        backend/api/src/main/python/openapi_server/impl/family_bidirectional.py
fi

# Clean up backup files
rm -f backend/api/src/main/python/openapi_server/impl/*.bak
rm -f backend/api/src/main/python/openapi_server/impl/utils/orm/models/*.bak

echo "Family Management post-generation fixes applied successfully!"

# Run a quick test to verify
echo ""
echo "Verifying fixes..."
if grep -q "zip_code.*attr_name" backend/api/src/main/python/openapi_server/impl/utils/orm/models/family_bidirectional.py; then
    echo "  ✓ Address model fix verified"
fi
if grep -q "DoesNotExist" backend/api/src/main/python/openapi_server/impl/family_bidirectional.py; then
    echo "  ✓ DoesNotExist import verified"
fi
if grep -q "familyName.*family_name" backend/api/src/main/python/openapi_server/impl/handlers.py; then
    echo "  ✓ Handler conversion fix verified"
fi
if grep -q "zipCode.*zip_code" backend/api/src/main/python/openapi_server/impl/family_bidirectional.py; then
    echo "  ✓ zipCode conversion fix verified"
fi

echo ""
echo "Post-generation fixes complete!"