# Fix OpenAPI Generation Templates

**Trigger**: `/fix-openapi-templates`

**Purpose**: Systematically resolve the fundamental OpenAPI code generation template issues that are producing broken controllers with missing request body parameters, blocking all PUT/POST operations and authentication.

## Problem Statement

The OpenAPI Generator is producing broken Flask controllers that are missing request body parameters in their function signatures. This causes Connexion to fail when routing requests with bodies, resulting in:
- Authentication failures (missing body parameter)
- All PUT/POST operations failing with 500 errors
- Animal Config validation blocked
- Systematic failures across all endpoints that accept request bodies

## Root Cause Analysis

Use sequential thinking MCP to analyze why the OpenAPI code generation templates are producing broken controllers:

```bash
# Step 1: Examine current generated controller patterns
grep -A 5 -B 5 "def " backend/api/src/main/python/openapi_server/controllers/*.py | grep -E "(post|put|patch)"

# Step 2: Check OpenAPI Generator configuration
cat backend/api/.openapi-generator-config.json
ls -la backend/api/templates/

# Step 3: Compare generated vs expected signatures
# Generated (broken):
def auth_login_post():  # Missing body parameter
    return 'do some magic!'

# Expected (working):
def auth_login_post(body):  # Has body parameter
    return auth.login(body)

# Step 4: Analyze Connexion routing expectations
grep -r "operationId" backend/api/openapi_spec.yaml
```

**Key Finding**: The default OpenAPI Generator templates for python-flask don't properly handle request body parameters in the controller function signatures.

## Implementation Strategy

### Phase 1: Template Discovery and Analysis
```bash
# Discover current template usage
docker run --rm openapitools/openapi-generator-cli:latest author template \
  -g python-flask \
  -o /tmp/flask-templates

# Examine controller template
cat /tmp/flask-templates/controller.mustache

# Identify the broken pattern in template
# Look for: {{#operations}}{{#operation}}
# Missing: proper handling of {{#bodyParam}}
```

### Phase 2: Create Custom Templates
```bash
# Create custom templates directory
mkdir -p backend/api/templates/

# Create fixed controller template
cat > backend/api/templates/controller.mustache << 'EOF'
{{>partial_header}}
from typing import Dict
from typing import Tuple
from typing import Union

from {{apiPackage}} import util
{{#imports}}
{{import}}
{{/imports}}
{{#operations}}

{{#operation}}
def {{operationId}}({{#allParams}}{{paramName}}{{^required}}=None{{/required}}{{^-last}}, {{/-last}}{{/allParams}}):  # noqa: E501
    """{{summary}}{{^summary}}{{operationId}}{{/summary}}

    {{notes}} # noqa: E501

    {{#allParams}}
    :param {{paramName}}: {{description}}
    :type {{paramName}}: {{dataType}}
    {{/allParams}}

    :rtype: Union[{{returnType}}{{^returnType}}None{{/returnType}}, Tuple[{{returnType}}{{^returnType}}None{{/returnType}}, int], Tuple[{{returnType}}{{^returnType}}None{{/returnType}}, int, Dict[str, str]]]
    """
    {{#allParams}}
    {{^isContainer}}
    {{#isDate}}
    {{paramName}} = util.deserialize_date({{paramName}})
    {{/isDate}}
    {{#isDateTime}}
    {{paramName}} = util.deserialize_datetime({{paramName}})
    {{/isDateTime}}
    {{/isContainer}}
    {{/allParams}}
    return 'do some magic!'
{{/operation}}
{{/operations}}
EOF
```

### Phase 3: Configure Generator to Use Custom Templates
```bash
# Update Makefile to use custom templates
cat >> backend/api/Makefile << 'EOF'
generate-api-with-templates:
	@echo "Generating OpenAPI server code with custom templates..."
	docker run --rm \
		-v ${PWD}:/local \
		openapitools/openapi-generator-cli:latest generate \
		-i /local/openapi_spec.yaml \
		-g python-flask \
		-o /local/generated/app \
		-t /local/templates \
		--additional-properties=packageName=openapi_server
	@echo "Copying generated code to source directory..."
	cp -r generated/app/openapi_server/* src/main/python/openapi_server/
	@echo "API generation with custom templates complete!"
EOF
```

### Phase 4: Implement Handler Connection Pattern
```bash
# Create handler connection script
cat > backend/api/scripts/connect_handlers.py << 'EOF'
#!/usr/bin/env python3
"""Connect generated controllers to implementation handlers."""

import os
import re
from pathlib import Path

def update_controller(controller_path, impl_module):
    """Update a controller to import and call the implementation."""

    with open(controller_path, 'r') as f:
        content = f.read()

    # Add import at the top
    import_line = f"from ..impl import {impl_module}"
    if import_line not in content:
        # Find the last import line
        import_pattern = r'(from .+ import .+\n)+'
        match = re.search(import_pattern, content)
        if match:
            end_pos = match.end()
            content = content[:end_pos] + import_line + '\n' + content[end_pos:]

    # Replace 'do some magic!' with handler calls
    def replace_magic(match):
        func_name = match.group(1)
        params = match.group(2)
        # Convert operationId to handler function name
        handler_func = func_name.replace('_controller', '').replace('_', '_')

        if params.strip():
            return f"def {func_name}({params}):  # noqa: E501\n    return {impl_module}.{handler_func}({params})"
        else:
            return f"def {func_name}({params}):  # noqa: E501\n    return {impl_module}.{handler_func}()"

    pattern = r"def (\w+)\((.*?)\):.*?return 'do some magic!'"
    content = re.sub(pattern, replace_magic, content, flags=re.DOTALL)

    with open(controller_path, 'w') as f:
        f.write(content)

# Map controllers to implementation modules
CONTROLLER_MAPPINGS = {
    'auth_controller.py': 'auth',
    'animals_controller.py': 'animals',
    'family_controller.py': 'family',
    'users_controller.py': 'users',
    'conversation_controller.py': 'conversation',
    'knowledge_controller.py': 'knowledge',
    'media_controller.py': 'media',
    'analytics_controller.py': 'analytics',
    'admin_controller.py': 'admin',
    'system_controller.py': 'system',
    'ui_controller.py': 'ui'
}

def main():
    controllers_dir = Path('src/main/python/openapi_server/controllers')

    for controller_file, impl_module in CONTROLLER_MAPPINGS.items():
        controller_path = controllers_dir / controller_file
        if controller_path.exists():
            print(f"Connecting {controller_file} to {impl_module}...")
            update_controller(controller_path, impl_module)

    print("Controller connection complete!")

if __name__ == '__main__':
    main()
EOF

chmod +x backend/api/scripts/connect_handlers.py
```

### Phase 5: Test and Validate
```bash
# Test the fix with a clean generation
cd backend/api
make clean-api
make generate-api-with-templates
python scripts/connect_handlers.py

# Verify the generated controllers have proper signatures
grep -A 2 "def auth_login_post" src/main/python/openapi_server/controllers/auth_controller.py
# Should show: def auth_login_post(body):

# Test with Docker
make build-api
make run-api

# Validate authentication works
curl -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test@cmz.org", "password": "testpass123"}'

# Validate Animal Config PUT works
curl -X PUT http://localhost:8080/animals/a001/config \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name": "Leo", "species": "Lion"}'
```

## Validation Criteria

### Success Indicators
- ✅ All generated controllers have proper function signatures with body parameters
- ✅ Authentication endpoint accepts and processes login requests
- ✅ Animal Config PUT endpoint accepts and processes configuration updates
- ✅ All PUT/POST/PATCH operations work correctly
- ✅ Integration tests pass without 500 errors
- ✅ Playwright E2E tests can complete authentication flow

### Test Commands
```bash
# Unit test validation
cd backend/api
pytest src/main/python/openapi_server/test/

# Integration test validation
pytest tests/integration/test_api_validation_epic.py -v

# E2E validation
cd src/main/python/tests/playwright
FRONTEND_URL=http://localhost:3001 npx playwright test --config config/playwright.config.js --grep "authentication" --reporter=line
```

## Rollback Strategy

If the custom templates cause issues:

```bash
# Revert to standard generation
cd backend/api
git checkout -- src/main/python/openapi_server/controllers/
make generate-api  # Use standard generation without templates

# Apply manual fixes to critical endpoints
# Edit auth_controller.py, animals_controller.py manually to add body parameters
```

## Long-term Solution

### Option 1: Maintain Custom Templates
- Keep templates in version control
- Update templates when OpenAPI spec changes
- Document template customizations

### Option 2: Switch to Different Generator
```bash
# Consider alternative generators
# FastAPI with automatic validation
pip install fastapi uvicorn
# OR
# Connexion 3.x with better OpenAPI 3.0 support
pip install "connexion[flask]>=3.0"
```

### Option 3: Post-Generation Script
```bash
# Always run after generation
make generate-api && python scripts/connect_handlers.py
```

## Documentation Updates

Update `CLAUDE.md` with permanent fix:

```markdown
## OpenAPI Template Solution

The project uses custom OpenAPI Generator templates to fix the controller-body parameter issue:

1. **Custom Templates**: Located in `backend/api/templates/`
2. **Generation Command**: `make generate-api-with-templates`
3. **Handler Connection**: Run `python scripts/connect_handlers.py` after generation
4. **Why**: Default templates don't properly handle request body parameters

This eliminates the "do some magic!" placeholder and ensures all endpoints work correctly.
```

## Related Documentation

- `docs/OPENAPI_TEMPLATE_SOLUTION.md` - Detailed explanation of the template fix
- `ANIMAL-CONFIG-FLAKINESS-ADVICE.md` - Troubleshooting guide for related issues
- `scripts/fix_generated_code.sh` - Automated fix script (if created)

## Command Usage

```bash
/fix-openapi-templates

# This will:
# 1. Analyze the current broken state
# 2. Create custom templates
# 3. Configure the generator
# 4. Implement handler connections
# 5. Test and validate the fix
# 6. Update documentation
```

## Key Learnings

1. **Root Cause**: Default OpenAPI Generator templates for python-flask don't handle request bodies correctly
2. **Solution**: Custom templates + post-generation handler connection
3. **Prevention**: Always test generated code before assuming it works
4. **Documentation**: Critical to document non-standard build processes

## Success Metrics

- 🎯 0 controller generation errors
- 🎯 100% of endpoints with bodies have correct signatures
- 🎯 Authentication flow works end-to-end
- 🎯 Animal Config validation can proceed
- 🎯 No manual intervention required after generation