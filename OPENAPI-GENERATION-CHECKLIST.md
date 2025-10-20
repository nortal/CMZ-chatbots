# OpenAPI Generation Checklist

## MANDATORY: Run this checklist every time after `make generate-api`

### 1. Controller Import Verification
```bash
# Check that all controllers have necessary model imports
grep -l "from_dict" backend/api/src/main/python/openapi_server/controllers/*.py | while read file; do
    echo "Checking $file..."
    grep -q "^from openapi_server.models" "$file" || echo "❌ MISSING IMPORTS: $file"
done
```

### 2. Auth Controller Specific Check
```bash
# Auth controller MUST have these imports
grep -E "from openapi_server.models.(auth_request|auth_response|password_reset_request)" \
    backend/api/src/main/python/openapi_server/controllers/auth_controller.py || \
    echo "❌ AUTH CONTROLLER MISSING CRITICAL IMPORTS!"
```

### 3. Animals Controller Check
```bash
# Animals controller MUST have AnimalConfigUpdate import
grep "from openapi_server.models.animal_config_update import AnimalConfigUpdate" \
    backend/api/src/main/python/openapi_server/controllers/animals_controller.py || \
    echo "❌ ANIMALS CONTROLLER MISSING AnimalConfigUpdate!"
```

### 4. Handler Routing Pattern Check
```bash
# All controllers should use the generic handler pattern
grep -l "from openapi_server.impl import handlers" \
    backend/api/src/main/python/openapi_server/controllers/*.py | wc -l

# Should match total controller count
ls backend/api/src/main/python/openapi_server/controllers/*.py | wc -l
```

### 5. Quick Fix Script
If imports are missing, run this to add them:
```bash
# For auth_controller.py
sed -i '' '6i\
from openapi_server.models.auth_request import AuthRequest\
from openapi_server.models.auth_response import AuthResponse\
from openapi_server.models.password_reset_request import PasswordResetRequest
' backend/api/src/main/python/openapi_server/controllers/auth_controller.py

# For animals_controller.py
sed -i '' '6i\
from openapi_server.models.animal_config_update import AnimalConfigUpdate
' backend/api/src/main/python/openapi_server/controllers/animals_controller.py
```

### 6. Build and Test
```bash
# Rebuild after any fixes
make build-api && make stop-api && make run-api

# Test auth endpoint
curl -X POST http://localhost:8080/auth \
    -H "Content-Type: application/json" \
    -d '{"username":"admin@cmz.org","password":"admin123"}' -v

# Test animal config endpoint
curl -X PATCH http://localhost:8080/animal_config/test_id \
    -H "Content-Type: application/json" \
    -d '{"temperature":1.5,"topP":0.95}' -v
```

## Common Issues and Solutions

### Issue 1: "NameError: name 'AuthRequest' is not defined"
**Cause**: Missing model imports in auth_controller.py
**Solution**: Add imports as shown in step 5

### Issue 2: "TypeError: auth_post() missing 1 required positional argument"
**Cause**: Parameter not being passed correctly from Connexion
**Solution**: Ensure model imports exist and parameter names match OpenAPI spec

### Issue 3: Controller code lost after regeneration
**Cause**: Template not using generic handler pattern
**Solution**: Ensure controller.mustache template uses Pattern 2 (handlers.handle_)

## Prevention Strategy

### Before Running `make generate-api`:
1. Backup current controllers: `cp -r backend/api/src/main/python/openapi_server/controllers{,.bak}`
2. Note any custom imports added

### After Running `make generate-api`:
1. Run this entire checklist
2. Compare with backup: `diff -r backend/api/src/main/python/openapi_server/controllers{.bak,}`
3. Re-add any missing imports
4. Test critical endpoints (auth, animals)
5. Remove backup if all good: `rm -rf backend/api/src/main/python/openapi_server/controllers.bak`

## Automated Check Script
Save as `check-openapi-generation.sh`:
```bash
#!/bin/bash
echo "🔍 Checking OpenAPI Generation..."

# Check auth imports
if grep -q "from openapi_server.models.auth_request import AuthRequest" \
    backend/api/src/main/python/openapi_server/controllers/auth_controller.py; then
    echo "✅ Auth controller imports OK"
else
    echo "❌ Auth controller missing imports - FIXING..."
    # Add the fix here
fi

# Check animals imports
if grep -q "from openapi_server.models.animal_config_update import AnimalConfigUpdate" \
    backend/api/src/main/python/openapi_server/controllers/animals_controller.py; then
    echo "✅ Animals controller imports OK"
else
    echo "❌ Animals controller missing imports - FIXING..."
    # Add the fix here
fi

# Check handler pattern
HANDLER_COUNT=$(grep -l "from openapi_server.impl import handlers" \
    backend/api/src/main/python/openapi_server/controllers/*.py | wc -l)
CONTROLLER_COUNT=$(ls backend/api/src/main/python/openapi_server/controllers/*.py | wc -l)

if [ "$HANDLER_COUNT" -eq "$CONTROLLER_COUNT" ]; then
    echo "✅ All controllers use handler pattern"
else
    echo "⚠️ Some controllers missing handler pattern ($HANDLER_COUNT/$CONTROLLER_COUNT)"
fi

echo "🏁 Check complete!"
```