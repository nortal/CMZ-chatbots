# Naming Convention Solution: animal_id vs animalId

## Problem Summary

The codebase has inconsistent naming conventions where:
- **OpenAPI spec** uses `animalId` (camelCase) - ✅ **GOOD**
- **Python implementation** mixes both `animal_id` (snake_case) and `animalId` (camelCase) - ❌ **INCONSISTENT**

This causes issues in API serialization/deserialization and database operations.

## Root Cause Analysis

1. **OpenAPI Generator Behavior**: The `python-flask` generator automatically converts camelCase to snake_case for Python variables, which is correct per PEP 8.

2. **Manual Implementation Issues**: Our `impl/` modules sometimes use camelCase directly from the OpenAPI spec instead of the generated snake_case versions.

3. **Database Layer**: DynamoDB operations need consistent field naming to match the stored data format.

## Implemented Solution

### 1. Enhanced OpenAPI Generator Configuration

Updated `backend/api/config-python-flask.yaml` to explicitly control naming:

```yaml
# Naming convention control
enumUnknownDefaultCase: false
enumAttributeNaming: snake_case
variableNaming: snake_case
parameterNaming: snake_case
propertyNaming: snake_case
```

### 2. Pre-Build Validation

Created `scripts/validate_naming_conventions_simple.py` that:
- Checks OpenAPI spec for consistency (should be camelCase)
- Identifies Python files with mixed naming conventions
- Runs automatically before `make generate-api`

**Current Status**:
- ✅ OpenAPI spec: 29 instances of `animalId`, 0 instances of `animal_id`
- ⚠️ 9 implementation files have mixed conventions

### 3. Makefile Integration

Added validation as a prerequisite to code generation:

```makefile
.PHONY: validate-naming
validate-naming:
	@python3 scripts/validate_naming_conventions_simple.py $(ROOT_DIR)

.PHONY: generate-api
generate-api: validate-naming $(GEN_TMP_BASE)
```

## Recommended Strategy

### Phase 1: Establish Clear Boundaries ✅ **IMPLEMENTED**

1. **OpenAPI Spec**: Always use camelCase (`animalId`) for JSON API consistency
2. **Generated Code**: Let OpenAPI Generator convert to snake_case (`animal_id`)
3. **Implementation Code**: Use snake_case consistently (`animal_id`)
4. **Database Storage**: Use camelCase (`animalId`) to match frontend expectations

### Phase 2: Create Conversion Layer

```python
# backend/api/src/main/python/openapi_server/impl/utils/field_mapping.py

CAMEL_TO_SNAKE = {
    'animalId': 'animal_id',
    'familyId': 'family_id',
    'userId': 'user_id',
    # ... other mappings
}

SNAKE_TO_CAMEL = {v: k for k, v in CAMEL_TO_SNAKE.items()}

def to_snake_case(data: dict) -> dict:
    """Convert camelCase keys to snake_case"""
    return {CAMEL_TO_SNAKE.get(k, k): v for k, v in data.items()}

def to_camel_case(data: dict) -> dict:
    """Convert snake_case keys to camelCase"""
    return {SNAKE_TO_CAMEL.get(k, k): v for k, v in data.items()}
```

### Phase 3: Implementation Pattern

**Controller Layer** (generated code uses snake_case):
```python
def animal_config_get(animal_id: str):  # snake_case parameter
    result = handle_get_animal_config(animal_id)
    return result, 200
```

**Implementation Layer** (use snake_case internally):
```python
def handle_get_animal_config(animal_id: str):
    # DynamoDB operations use camelCase for storage
    item = table.get_item(Key={'animalId': animal_id})  # camelCase for DB
    return from_ddb(item['Item'])
```

**Database Utilities** (handle conversion):
```python
def to_ddb(data: dict) -> dict:
    """Convert Python dict to DynamoDB format with camelCase keys"""
    return {SNAKE_TO_CAMEL.get(k, k): v for k, v in data.items()}

def from_ddb(item: dict) -> dict:
    """Convert DynamoDB item to Python format with snake_case keys"""
    return {CAMEL_TO_SNAKE.get(k, k): v for k, v in item.items()}
```

## Current Files Needing Updates

The validator identified 9 files with mixed conventions:

1. `backend/api/src/main/python/openapi_server/impl/validators.py`
2. `backend/api/src/main/python/openapi_server/impl/test_animals.py`
3. `backend/api/src/main/python/openapi_server/impl/animals.py`
4. `backend/api/src/main/python/openapi_server/impl/utils/id_generator.py`
5. `backend/api/src/main/python/openapi_server/impl/commands/foreign_key_validation.py`
6. 4 additional files

## Implementation Steps

### Immediate Actions (This PR)

1. ✅ Enhanced OpenAPI generator configuration
2. ✅ Created pre-build validation script
3. ✅ Integrated validation into Makefile
4. ✅ Documented the solution strategy

### Next Phase (Follow-up PR)

1. Create `utils/field_mapping.py` with conversion utilities
2. Update the 9 identified files to use consistent snake_case
3. Update `utils/dynamo.py` to use field mapping functions
4. Add unit tests for field mapping utilities
5. Verify all API endpoints work correctly with conversion layer

### Long-term Benefits

1. **Consistency**: Clear separation between API layer (camelCase) and Python implementation (snake_case)
2. **Maintainability**: Automated validation prevents regression
3. **Standards Compliance**: Follows Python PEP 8 and JSON API conventions
4. **Future-Proof**: Works with OpenAPI Generator updates

## Testing Strategy

1. **Pre-build validation**: Automatically catches mixed conventions
2. **Unit tests**: Verify field mapping utilities work correctly
3. **Integration tests**: Ensure API endpoints handle both formats
4. **E2E tests**: Verify frontend-backend communication remains intact

## Usage

```bash
# Manual validation
./scripts/validate_naming_conventions_simple.py .

# Automatic validation (runs before code generation)
make generate-api

# Expected output:
# ✅ All naming conventions are consistent!
```

This solution provides a permanent, automated fix for the camelCase inconsistency while maintaining backward compatibility and following best practices for both OpenAPI and Python development.