# ID Parameter Mismatch - Connexion/OpenAPI Issue

## Problem Description
Connexion automatically renames path parameters named `id` to `id_` to avoid shadowing Python's built-in `id()` function. This causes `TypeError: function() got an unexpected keyword argument 'id_'` errors at runtime.

## Symptoms
- `TypeError: animal_id_put() got an unexpected keyword argument 'id_'. Did you mean 'id'?`
- Endpoints like `/animal/{id}`, `/family/{id}`, `/user/{id}` fail with 500 errors
- Works in unit tests but fails at runtime with real HTTP requests
- Affects ALL endpoints with `{id}` path parameters

## Root Cause Analysis
1. **OpenAPI spec** defines path parameter as `{id}`
2. **Generated controller** uses `id` as parameter name
3. **Connexion at runtime** renames `id` to `id_` to avoid Python builtin conflict
4. **Handler expects** `id` but receives `id_` → TypeError
5. **This happens on EVERY regeneration** of OpenAPI code

## Permanent Solution

### Pattern 1: Controller Fix (Preferred)
Make controllers accept both `id` and `id_` parameters:

```python
def animal_id_put(id=None, id_=None, body=None, **kwargs):
    """Update an existing animal"""
    # Handle both id and id_ parameters (Connexion may rename id to id_)
    if id is None:
        id = id_

    # Continue with normal processing...
```

### Pattern 2: Handler Fix (More Robust)
Make handlers accept flexible parameters using `*args, **kwargs`:

```python
def handle_animal_id_put(*args, **kwargs):
    """Update animal via PUT /animal/{id}"""
    # Handle positional arguments from controller
    animal_id = None
    body = None

    if len(args) >= 2:
        animal_id = args[0]  # First arg is id or id_
        body = args[1]       # Second arg is body

    # Also check kwargs for any missing parameters
    if animal_id is None:
        animal_id = kwargs.get('id') or kwargs.get('id_')
    if body is None:
        body = kwargs.get('body') or kwargs.get('animal_update')

    # Validate and continue...
```

## Automated Fix Script
Run `scripts/fix_id_parameter_mismatch.py` after OpenAPI code generation:

```bash
python3 scripts/fix_id_parameter_mismatch.py
```

This script:
- Detects all functions with `id` parameters
- Updates them to accept both `id` and `id_`
- Adds parameter handling code
- Can be integrated into `make post-generate`

## Prevention Strategy

### 1. Add to Post-Generation Process
Include in `scripts/post_openapi_generation.py`:
```python
# Fix id/id_ parameter mismatches
import fix_id_parameter_mismatch
fix_id_parameter_mismatch.main()
```

### 2. Use Custom Templates
Create custom OpenAPI templates that generate the correct signatures from the start.

### 3. Alternative: Rename in OpenAPI Spec
Change `{id}` to `{resourceId}` in OpenAPI spec:
- `/animal/{animalId}` instead of `/animal/{id}`
- `/family/{familyId}` instead of `/family/{id}`
- This avoids the Python builtin conflict entirely

## Testing
After fixing, test all affected endpoints:

```bash
# Test GET
curl -X GET "http://localhost:8080/animal/bella_002" -H "Authorization: Bearer $TOKEN"

# Test PUT
curl -X PUT "http://localhost:8080/animal/bella_002" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name": "Updated Name", "species": "Species", "status": "active"}'

# Test DELETE
curl -X DELETE "http://localhost:8080/animal/bella_002" -H "Authorization: Bearer $TOKEN"
```

## Related Issues
- Affects all resources with `{id}` path parameters
- Similar issue can occur with other Python builtins (type, input, etc.)
- Body parameter ordering issues often occur alongside this

## Resolution Date
- First documented: 2025-09-19
- Solution implemented and tested
- Automated fix script created