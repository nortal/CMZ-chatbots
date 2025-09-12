# Offline Persistence Architecture (PR003946-95)

## Overview

The CMZ chatbot backend implements a persistence abstraction layer that allows switching between production DynamoDB storage and file-based storage for offline testing and development.

## Architecture Components

### 1. Persistence Protocol (`DynamoStore`)

```python
class DynamoStore(Protocol):
    def list(self, hide_soft_deleted: bool = True) -> List[Dict[str, Any]]: ...
    def get(self, pk: Any) -> Optional[Dict[str, Any]]: ...
    def create(self, item: Dict[str, Any]) -> None: ...
    def update_fields(self, pk: Any, fields: Dict[str, Any]) -> None: ...
    def soft_delete(self, pk: Any, soft_field: str = "softDelete") -> None: ...
```

### 2. Implementation Classes

#### PynamoStore (Production)
- **File**: `impl/utils/orm/store.py`
- **Purpose**: Production DynamoDB persistence via PynamoDB ORM
- **Features**:
  - Direct AWS DynamoDB integration
  - Automatic table creation
  - Strong consistency reads
  - Conditional writes for race condition prevention
  - Server-generated IDs (PR003946-69)
  - Soft-delete semantics (PR003946-66)

#### FileStore (Testing)
- **File**: `impl/utils/orm/file_store.py`
- **Purpose**: File-based JSON storage for offline testing
- **Features**:
  - JSON file storage in configurable directory
  - Pre-populated test data from source control
  - Same interface as DynamoDB implementation
  - No external service dependencies
  - Atomic file operations for consistency

### 3. Factory Function (`get_store`)

```python
def get_store(table_name: str, pk_name: str) -> DynamoStore:
    persistence_mode = os.getenv("PERSISTENCE_MODE", "dynamo").lower()
    
    if persistence_mode == "file":
        return FileStore(table_name, pk_name, id_generator)
    
    return PynamoStore(model_cls, expected_pk, id_generator)
```

## Environment Configuration

### Production Mode (Default)
```bash
PERSISTENCE_MODE=dynamo  # or unset
AWS_PROFILE=cmz
AWS_REGION=us-west-2
FAMILY_DYNAMO_TABLE_NAME=quest-dev-family
USER_DYNAMO_TABLE_NAME=quest-dev-user
# ... other DynamoDB configuration
```

### Testing Mode
```bash
PERSISTENCE_MODE=file
FILE_PERSISTENCE_DIR=/tmp/cmz_test_data  # optional, defaults to /tmp/cmz_test_data
```

## File Storage Structure

### Directory Layout
```
/tmp/cmz_test_data/
├── quest-dev-family.json
├── quest-dev-user.json
├── quest-dev-user-details.json
└── quest-dev-animal.json
```

### Test Data Initialization

Test data is automatically populated from `impl/utils/orm/test_data.json`:

```json
{
  "quest-dev-family": [
    {
      "familyId": "family_test_001",
      "familyName": "Test Family One",
      "parents": ["user_test_parent_001"],
      "students": ["user_test_student_001"],
      "created": {...},
      "modified": {...},
      "softDelete": false
    }
  ],
  "quest-dev-user": [...],
  "quest-dev-animal": [...]
}
```

## Usage Patterns

### In Implementation Files

```python
from openapi_server.impl.utils import get_store

def handle_list_users():
    store = get_store("quest-dev-user", "userId")
    return store.list()  # Works with both DynamoDB and file storage
```

### In Tests

```python
import os
os.environ["PERSISTENCE_MODE"] = "file"

# All store operations now use file storage
# No AWS credentials or DynamoDB access required
```

## Benefits

### Development Benefits
- **Offline Development**: No AWS credentials or internet connection required
- **Fast Test Execution**: File operations much faster than network calls
- **Deterministic Testing**: Pre-populated, consistent test data
- **CI/CD Friendly**: No external service dependencies in test pipelines

### Production Benefits  
- **Zero Production Impact**: File mode completely isolated from production data
- **Consistent Interface**: Same API for both persistence modes
- **Easy Debugging**: JSON files are human-readable for troubleshooting

## API Compatibility

The FileStore implementation maintains full compatibility with DynamoDB operations:

| Operation | DynamoDB Behavior | FileStore Behavior |
|-----------|-------------------|-------------------|
| `create()` | ConditionalCheckFailedException if exists | Same exception raised |
| `update_fields()` | ConditionalCheckFailedException if not exists | Same exception raised |
| `soft_delete()` | Sets softDelete=true | Same behavior |
| `list()` | Filters soft-deleted by default | Same filtering |
| `get()` | Returns None if not found | Same behavior |

## Error Handling

Both implementations raise the same `botocore.exceptions.ClientError` exceptions to maintain API compatibility:

- **ValidationException**: Invalid data or missing required fields
- **ConditionalCheckFailedException**: Item exists/doesn't exist when expected otherwise

## Performance Considerations

### FileStore Performance
- **Read Operations**: O(n) scan of JSON array - acceptable for test data sizes
- **Write Operations**: Full file rewrite - atomic but not optimized for high-frequency writes
- **Memory Usage**: Entire table loaded into memory - keep test datasets reasonable

### Recommended Test Data Limits
- **Maximum items per table**: 1,000
- **Maximum total test data size**: 10MB
- **File operations are synchronous**: No async complexity

## Integration Points

### Unit Tests (PR003946-94)
```python
# Unit tests automatically use file storage when PERSISTENCE_MODE=file
# No code changes required in test implementations
```

### Playwright Tests (PR003946-96) 
```bash
# Backend runs in file mode for Playwright tests
PERSISTENCE_MODE=file npm run e2e:test
```

### GitLab CI Pipeline
```yaml
test:
  variables:
    PERSISTENCE_MODE: file
  script:
    - pytest tests/
    - npm run e2e:test
```

## Migration Guide

### Existing Code
No changes required to existing implementation files. The persistence abstraction is already in place.

### New Features
When adding new persistence operations, ensure they work with both implementations:

1. Add method to `DynamoStore` Protocol
2. Implement in both `PynamoStore` and `FileStore`
3. Test with both `PERSISTENCE_MODE=dynamo` and `PERSISTENCE_MODE=file`

## Troubleshooting

### Common Issues

**File Permission Errors**
- Ensure `FILE_PERSISTENCE_DIR` is writable
- Default `/tmp/cmz_test_data` should work in most environments

**Test Data Not Loading**
- Verify `impl/utils/orm/test_data.json` exists and is valid JSON
- Check table names match environment variables

**Inconsistent Behavior**
- Ensure `PERSISTENCE_MODE` environment variable is set consistently
- FileStore creates missing files automatically, but may need write permissions

## Future Enhancements

1. **Performance Optimization**: Index support for common query patterns
2. **Data Validation**: JSON schema validation for test data
3. **Migration Tools**: Import/export between DynamoDB and file storage
4. **Multi-Environment**: Different test datasets for different scenarios