# OpenAPI Generation Preservation Strategy

## Overview

This document describes how we preserve custom fixes and business logic when regenerating the OpenAPI server code.

## Problem

When running `make generate-api`, the OpenAPI generator overwrites:
- Controllers
- Models
- Test stubs

This can lose critical fixes for:
- Field name conversions (camelCase ↔ snake_case)
- Custom error handling
- Business logic routing
- Database field mappings

## Solution Architecture

### 1. Custom Templates
**Location**: `/backend/api/templates/python-flask/`

These Mustache templates customize the code generation:
- `controller.mustache` - Routes to handlers module instead of "do some magic!"
- `model.mustache` - Generates proper model classes with validation

**Applied via**: `--template-dir` flag in Makefile

### 2. Post-Generation Validation
**Script**: `/scripts/post_generation_validation.py`

Validates that:
- Controllers connect to implementations
- Frontend-backend contracts match
- No "do some magic!" placeholders remain

### 3. Family Management Fixes
**Script**: `/scripts/post_generate_family_fixes.sh`

Applies specific fixes for Family Management:
- Converts `zipCode` ↔ `zip_code` for PynamoDB compatibility
- Adds `DoesNotExist` import for proper error handling
- Fixes handler to convert `family_name` → `familyName`
- Updates ORM model Address field mapping

### 4. Makefile Integration

The complete generation flow:
```makefile
generate-api: generate-api-raw validate-api
    # 1. Generate from OpenAPI spec with templates
    # 2. Run validation and fixes
```

`validate-api` target includes:
1. Comprehensive validation (`post_generation_validation.py`)
2. Controller signature fixes (`fix_controller_signatures.py`)
3. **Family Management fixes** (`post_generate_family_fixes.sh`)
4. Frontend-backend contract testing

## Family Management Specific Issues

### Issue 1: Field Name Conversion
- **Problem**: OpenAPI uses camelCase (familyName), Python uses snake_case (family_name)
- **Solution**: Handler converts between formats before passing to business logic

### Issue 2: Address Field Mapping
- **Problem**: OpenAPI has `zipCode`, PynamoDB expects `zip_code`
- **Solution**:
  - ORM model uses `zip_code = UnicodeAttribute(attr_name='zipCode')`
  - Create function converts `zipCode` → `zip_code` before saving

### Issue 3: Error Handling
- **Problem**: `DoesNotExist` exception not imported by default
- **Solution**: Post-generation script adds import automatically

## How to Use

### Normal Regeneration
```bash
make generate-api
# or
make post-generate
```
This automatically applies all fixes.

### Manual Fix Application
```bash
./scripts/post_generate_family_fixes.sh
```

### Verify Fixes
```bash
/tmp/validate_family_complete.sh
```

## Adding New Fixes

### For Template-Level Issues
1. Edit the appropriate template in `/backend/api/templates/python-flask/`
2. Test regeneration with `make generate-api`

### For Post-Generation Issues
1. Add fix to `/scripts/post_generate_family_fixes.sh`
2. Follow the pattern:
   - Check if fix is needed
   - Apply fix with sed/awk
   - Verify fix was applied

### Example Fix Pattern
```bash
# Check if fix needed
if ! grep -q "pattern_to_find" target_file.py; then
    # Apply fix
    sed -i.bak 's/old_pattern/new_pattern/' target_file.py
fi

# Verify
if grep -q "new_pattern" target_file.py; then
    echo "  ✓ Fix verified"
fi
```

## Files Protected from Regeneration

These files are NEVER regenerated (implementation layer):
- `/backend/api/src/main/python/openapi_server/impl/*.py`
- `/backend/api/src/main/python/openapi_server/impl/utils/**`

## Testing After Regeneration

1. **Unit Tests**
```bash
pytest backend/api/src/main/python/openapi_server/test/
```

2. **Integration Tests**
```bash
/tmp/validate_family_complete.sh
```

3. **Manual Test**
```bash
curl -X POST http://localhost:8080/family \
  -H "Content-Type: application/json" \
  -H "X-User-Id: user_test_cmz_org" \
  -d '{
    "familyName": "Test Family",
    "parents": ["parent_test_001"],
    "students": ["student_test_001"],
    "address": {
      "street": "123 Test St",
      "city": "Seattle",
      "state": "WA",
      "zipCode": "98101"
    }
  }'
```

## Troubleshooting

### If Family Creation Fails After Regeneration

1. Check DoesNotExist import:
```bash
grep "DoesNotExist" backend/api/src/main/python/openapi_server/impl/family_bidirectional.py
```

2. Check zipCode conversion:
```bash
grep "zip_code.*zipCode" backend/api/src/main/python/openapi_server/impl/family_bidirectional.py
```

3. Check handler conversion:
```bash
grep "familyName.*family_name" backend/api/src/main/python/openapi_server/impl/handlers.py
```

4. Run manual fixes:
```bash
./scripts/post_generate_family_fixes.sh
```

## Key Files

### Templates
- `/backend/api/templates/python-flask/controller.mustache`
- `/backend/api/templates/python-flask/model.mustache`

### Scripts
- `/scripts/post_generation_validation.py`
- `/scripts/post_generate_family_fixes.sh`
- `/scripts/fix_controller_signatures.py`

### Implementation (Never Regenerated)
- `/backend/api/src/main/python/openapi_server/impl/family_bidirectional.py`
- `/backend/api/src/main/python/openapi_server/impl/handlers.py`
- `/backend/api/src/main/python/openapi_server/impl/utils/orm/models/family_bidirectional.py`

### Validation
- `/tmp/validate_family_complete.sh`

## Success Criteria

After regeneration, all of these should work:
- ✅ GET /family returns 200
- ✅ POST /family creates with all fields
- ✅ familyName persists correctly
- ✅ address.zipCode saves to DynamoDB
- ✅ No "do some magic!" errors
- ✅ No 501 Not Implemented responses