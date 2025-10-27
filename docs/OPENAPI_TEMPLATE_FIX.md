# OpenAPI Template Fix Documentation

## Problem Statement

The OpenAPI Generator was producing broken Flask controllers with:
1. **Missing or concatenated request body parameters** in function signatures
2. **Incorrect import paths** for utility modules
3. **Missing package name** in generated imports

This caused all PUT/POST operations to fail with 500 errors and prevented authentication from working.

## Root Causes

1. **Mustache Template Bug**: The controller.mustache template had incorrect parameter separator logic using `{{#hasMore}}` instead of `{{^-last}}`
2. **Package Name Resolution**: The `{{package}}` variable wasn't being passed to the generator
3. **Import Path Issues**: Templates referenced incorrect module paths

## Solution Implementation

### 1. Fixed Controller Template Parameter Separation

**File**: `backend/api/templates/python-flask/controller.mustache`

**Fix**: Changed parameter separator from `{{#hasMore}}` to `{{^-last}}`:
```mustache
# Before (broken):
def {{operationId}}({{#allParams}}{{paramName}}{{#hasMore}}, {{/hasMore}}{{/allParams}}):

# After (fixed):
def {{operationId}}({{#allParams}}{{paramName}}{{^-last}}, {{/-last}}{{/allParams}}):
```

### 2. Fixed Package Name in Makefile

**File**: `Makefile`

**Fix**: Added packageName to generator options:
```makefile
# Before:
OPENAPI_GEN_OPTS ?= --template-dir /local/backend/api/templates/python-flask

# After:
OPENAPI_GEN_OPTS ?= --template-dir /local/backend/api/templates/python-flask --additional-properties=packageName=openapi_server
```

### 3. Fixed __main__ Template Imports

**File**: `backend/api/templates/python-flask/__main__.mustache`

**Fix**: Hardcoded correct package name instead of using variable:
```python
# Before (broken):
from {{package}} import encoder

# After (fixed):
from openapi_server import encoder
```

### 4. Post-Generation Fixes

After generation, the following import corrections are needed in controllers:
```bash
# Fix util import path
find backend/api/src/main/python/openapi_server/controllers -name "*.py" \
  -exec sed -i '' 's/from openapi_server.controllers import util/from openapi_server import util/g' {} \;

# Fix error model import
find backend/api/src/main/python/openapi_server/controllers -name "*.py" \
  -exec sed -i '' 's/from openapi_server.controllers.models.error/from openapi_server.models.error/g' {} \;

# Fix impl import path
find backend/api/src/main/python/openapi_server/controllers -name "*.py" \
  -exec sed -i '' 's/from openapi_server.controllers.impl/from openapi_server.impl/g' {} \;
```

## Usage

### Generate API with Fixed Templates
```bash
make generate-api
```

### Copy Generated Code to Source
```bash
cp backend/api/generated/app/openapi_server/__main__.py backend/api/src/main/python/openapi_server/
cp backend/api/generated/app/openapi_server/util.py backend/api/src/main/python/openapi_server/
cp -r backend/api/generated/app/openapi_server/controllers/*.py backend/api/src/main/python/openapi_server/controllers/
```

### Apply Post-Generation Fixes
Run the import path corrections listed above.

### Build and Run
```bash
make build-api
make run-api
```

## Validation

Test that authentication works:
```bash
curl -X POST http://localhost:8080/auth \
  -H "Content-Type: application/json" \
  -d '{"username": "test@cmz.org", "password": "testpass123"}'
```

Test Animal Config endpoint:
```bash
curl -X PATCH http://localhost:8080/animal_config?animalId=a001 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name": "Leo", "species": "Lion"}'
```

## Permanent Solution

To make this fix permanent:

1. **Keep custom templates** in `backend/api/templates/python-flask/`
2. **Maintain Makefile settings** with packageName property
3. **Create post-generation script** to automate import fixes:

```bash
#!/bin/bash
# scripts/fix_generated_controllers.sh

echo "Fixing generated controller imports..."

# Fix util import
find backend/api/src/main/python/openapi_server/controllers -name "*.py" \
  -exec sed -i '' 's/from openapi_server.controllers import util/from openapi_server import util/g' {} \;

# Fix model imports
find backend/api/src/main/python/openapi_server/controllers -name "*.py" \
  -exec sed -i '' 's/from openapi_server.controllers.models/from openapi_server.models/g' {} \;

# Fix impl imports
find backend/api/src/main/python/openapi_server/controllers -name "*.py" \
  -exec sed -i '' 's/from openapi_server.controllers.impl/from openapi_server.impl/g' {} \;

echo "Controller imports fixed!"
```

4. **Update generation workflow**:
```bash
make generate-api
./scripts/fix_generated_controllers.sh
make build-api
```

## Key Learnings

1. **OpenAPI Generator templates can have bugs** - Always validate generated code
2. **Mustache template syntax is tricky** - `{{^-last}}` works better than `{{#hasMore}}` for lists
3. **Package resolution issues are common** - Sometimes hardcoding is more reliable than variables
4. **Post-generation scripts are essential** - Not all issues can be fixed in templates
5. **Test immediately after generation** - Don't assume generated code works

## Related Issues Fixed

- Authentication endpoint failures (missing body parameter)
- All PUT/POST operations returning 500 errors
- Animal Config validation blocked
- Parameter concatenation in function signatures (animal_idanimal_config_update)
- Import errors preventing server startup