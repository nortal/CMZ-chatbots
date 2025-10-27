# Fix Strategy for xxxId vs xxx_id Parameter Naming Issues

## The Problem
OpenAPI spec and Connexion have a naming conflict:
- OpenAPI spec uses `animalId` (camelCase) in path parameters
- Connexion converts these to `animal_id` (snake_case) at runtime to follow Python conventions
- Controllers expect one format but receive another, causing TypeErrors

## Root Causes
1. **OpenAPI Convention**: Uses camelCase (`animalId`, `userId`, `familyId`)
2. **Python Convention**: Uses snake_case (`animal_id`, `user_id`, `family_id`)
3. **Connexion Behavior**: Automatically converts parameter names to avoid Python reserved words and follow conventions
4. **Template Generation**: OpenAPI generator creates controllers with the original OpenAPI names

## Permanent Solution Options

### Option 1: Custom OpenAPI Templates (RECOMMENDED)
Create custom templates that generate controllers with both parameter variations:

```python
def animal_get(animal_id=None, animalId=None, **kwargs):
    """Handle both parameter naming conventions"""
    actual_id = animal_id or animalId or kwargs.get('animal_id') or kwargs.get('animalId')
    # ... rest of function
```

**Implementation Steps:**
1. Create custom templates in `backend/api/templates/python-flask/`
2. Modify controller template to accept both parameter formats
3. Update `make generate-api` to use custom templates
4. Run post-generation script to ensure consistency

### Option 2: Post-Generation Script (CURRENT WORKAROUND)
Run a Python script after generation to fix all parameter mismatches:

```bash
#!/usr/bin/env python3
# scripts/fix_parameter_naming.py
import re
import glob

def fix_controller_parameters(file_path):
    """Fix parameter naming in controller files"""
    with open(file_path, 'r') as f:
        content = f.read()

    # Fix patterns like def animal_get(animalId) to def animal_get(animal_id)
    patterns = [
        (r'def animal_(\w+)\(animalId', r'def animal_\1(animal_id'),
        (r'def user_(\w+)\(userId', r'def user_\1(user_id'),
        (r'def family_(\w+)\(familyId', r'def family_\1(family_id'),
        # Add more patterns as needed
    ]

    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)

    with open(file_path, 'w') as f:
        f.write(content)

# Apply to all controllers
for controller in glob.glob('backend/api/src/main/python/openapi_server/controllers/*_controller.py'):
    fix_controller_parameters(controller)
```

### Option 3: OpenAPI Spec Modification
Change the OpenAPI spec to use snake_case consistently:

```yaml
# Before:
/animal/{animalId}:

# After:
/animal/{animal_id}:
```

**Pros:** Consistent with Python conventions
**Cons:** Breaks API backward compatibility, not RESTful convention

### Option 4: Handler-Level Solution (FLEXIBLE)
Make handlers accept multiple parameter formats:

```python
def handle_animal_get(*args, **kwargs):
    """Accept any parameter naming convention"""
    # Try all possible parameter names
    actual_id = (
        kwargs.get('animal_id') or
        kwargs.get('animalId') or
        kwargs.get('id') or
        kwargs.get('id_') or
        (args[0] if args else None)
    )
    # ... rest of handler
```

## Current Implementation Status
- ✅ Fixed in handlers.py for animal endpoints
- ✅ Fixed controller parameter names manually
- ⚠️ Will break on next `make generate-api` without post-generation fix

## Immediate Actions Required

1. **Add to Makefile**:
```makefile
post-generate: generate-api
	@echo ">> Fixing parameter naming issues..."
	@python scripts/fix_parameter_naming.py
	@echo ">> Running general post-generation fixes..."
	@python scripts/post_generate_fixes.py
```

2. **Create fix script**: `scripts/fix_parameter_naming.py`

3. **Update documentation**: Add to CLAUDE.md about this issue

## Testing Strategy

```bash
# Test script to verify all endpoints work with both parameter formats
curl -X GET http://localhost:8080/animal/test-id
curl -X PUT http://localhost:8080/animal/test-id -d '{"name":"Test"}'
curl -X DELETE http://localhost:8080/animal/test-id

# Check logs for TypeErrors
docker logs cmz-openapi-api-dev 2>&1 | grep "TypeError.*keyword argument"
```

## Long-term Recommendation
1. Use custom OpenAPI templates (Option 1) for permanent fix
2. Standardize on snake_case in OpenAPI spec for v2 API
3. Document parameter naming convention in API guidelines
4. Add automated tests to catch parameter mismatches early