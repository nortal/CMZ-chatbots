# /implement Command

## Purpose
Systematic implementation of selected tickets using sequential reasoning for planning and established patterns for execution.

## Parameters
- `ticket_list`: Comma-separated list of ticket IDs to implement (e.g., "PR003946-69,PR003946-71,PR003946-75")

## Execution Steps

### Step 1: Load Implementation Plan
```bash
# Load the most recent discovery results
DISCOVERY_FILE=$(ls -t /tmp/discover_correlation_*.json 2>/dev/null | head -1)
if [[ -z "$DISCOVERY_FILE" ]]; then
    echo "❌ No discovery results found. Run /discover first."
    exit 1
fi

# Extract selected tickets and implementation sequence
TICKETS=$(jq -r '.final_unified_priorities[].ticket' "$DISCOVERY_FILE" | tr '\n' ',' | sed 's/,$//')
echo "📋 Implementing tickets: $TICKETS"
```

### Step 2: Per-Ticket Implementation with Sequential Reasoning

For each ticket in the implementation sequence:

```bash
# For each ticket, use sequential reasoning to plan specific implementation
for TICKET in $(echo "$TICKETS" | tr ',' ' '); do
    echo "🎯 Planning implementation for $TICKET..."
    
    # Use sequential reasoning MCP to plan implementation approach
    # Sequential Reasoning Prompt per ticket:
    ```
    Plan the specific implementation approach for ticket $TICKET:
    
    **TICKET CONTEXT:**
    {ticket_details_from_discovery}
    
    **CURRENT CODEBASE STATE:**
    - Existing impl files: {current_impl_files}
    - DynamoDB patterns: {dynamo_utils_analysis}
    - Authentication patterns: {auth_patterns_analysis}
    - Error handling patterns: {error_handling_analysis}
    
    **IMPLEMENTATION PLANNING:**
    
    1. **File Structure Planning:**
       - Which files need to be created or modified?
       - What imports and dependencies are required?
       - How does this integrate with existing controller structure?
    
    2. **Pattern Application:**
       - Which existing patterns can be reused (DynamoDB CRUD, auth, validation)?
       - What new patterns need to be established?
       - How does this follow the established utils/dynamo.py approach?
    
    3. **Implementation Sequence:**
       - What order should components be implemented?
       - Which parts can be tested incrementally?
       - What dependencies exist within this ticket?
    
    4. **Error Handling Approach:**
       - What error scenarios need to be handled?
       - How should validation errors be structured?
       - What HTTP status codes are appropriate?
    
    5. **Testing Strategy:**
       - What should be tested to verify implementation?
       - Which cURL commands will validate functionality?
       - How can implementation be verified incrementally?
    
    **DELIVERABLE:**
    Detailed implementation plan with:
    - Specific files to create/modify
    - Code patterns to follow
    - Implementation sequence
    - Testing approach
    - Integration with existing codebase
    ```
    
    # Execute planned implementation
    echo "🔨 Implementing $TICKET based on sequential reasoning plan..."
    
    # Implementation follows the planned approach:
    # 1. Create/modify files in impl/ directory
    # 2. Use existing DynamoDB patterns from utils/dynamo.py
    # 3. Follow established error handling with Error schema
    # 4. Add audit timestamps and server-generated IDs
    # 5. Implement basic CRUD operations with proper validation
    
    echo "✅ Completed implementation for $TICKET"
done
```

### Step 3: Implementation Patterns

Follow these established patterns for all implementations:

#### DynamoDB CRUD Pattern
```python
from .utils.dynamo import (
    table, to_ddb, from_ddb, now_iso,
    model_to_json_keyed_dict, ensure_pk,
    error_response, not_found
)

def handle_operation(body):
    # Convert OpenAPI model to dict
    item = model_to_json_keyed_dict(body) if isinstance(body, ModelClass) else dict(body)
    
    # Ensure primary key exists (server-generated)
    ensure_pk(item, "primaryKeyField")
    
    # Add audit timestamps
    item.setdefault("created", {"at": now_iso()})
    item["modified"] = {"at": now_iso()}
    
    # DynamoDB operation with proper error handling
    try:
        result = _table().put_item(Item=to_ddb(item))
        return from_ddb(item), 201
    except ClientError as e:
        return error_response(e)
```

#### Error Response Pattern
```python
def error_response(error, status_code=500):
    return {
        "code": "server_error",
        "message": str(error),
        "details": {"error_type": type(error).__name__}
    }, status_code
```

#### Authentication Pattern
```python
# For protected endpoints
from .utils.auth import validate_jwt, check_permissions

def protected_operation():
    # JWT validation handled by middleware
    # Access user context from request
    pass
```

### Step 4: Incremental Testing

After each ticket implementation:

```bash
# Test the implemented endpoint
echo "🧪 Testing $TICKET implementation..."

# Basic endpoint connectivity
curl -s http://localhost:8080/api/v1/{endpoint} || echo "Endpoint not responding"

# CRUD operations testing (if applicable)
# CREATE test
curl -X POST http://localhost:8080/api/v1/{endpoint} \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}' || echo "Create operation failed"

# READ test  
curl -s http://localhost:8080/api/v1/{endpoint}/{id} || echo "Read operation failed"

# Validation error testing
curl -X POST http://localhost:8080/api/v1/{endpoint} \
  -H "Content-Type: application/json" \
  -d '{}' # Should return validation error

echo "✅ Basic testing complete for $TICKET"
```

### Step 5: Integration Validation

After all implementations:

```bash
# Run integration tests to verify implementations
echo "🧪 Running integration test validation..."
python -m pytest src/main/python/tests/integration/test_api_validation_epic.py -v

# Check for any new failures
# Verify that targeted tickets now pass
```

### Step 6: Implementation Summary

```json
{
  "session_id": "implement_YYYYMMDD_HHMMSS",
  "implementation_summary": {
    "tickets_completed": ["PR003946-69", "PR003946-71", "PR003946-75"],
    "files_created": ["impl/knowledge.py", "utils/id_generation.py"],
    "files_modified": ["impl/utils/dynamo.py", "impl/auth.py"],
    "total_time_spent": "14 hours",
    "integration_tests": {
      "before": "16 passing, 5 failing",
      "after": "19 passing, 2 failing"
    }
  },
  "implementation_notes": [
    "ID generation patterns established for system-wide use",
    "JWT validation enhanced with proper error handling",
    "Knowledge CRUD implemented using established DynamoDB patterns",
    "All implementations follow utils/dynamo.py patterns",
    "Error responses use consistent Error schema structure"
  ],
  "remaining_work": [
    "2 integration tests still failing - may need /scope expansion",
    "Consider additional validation rules for knowledge content",
    "Performance testing recommended for DynamoDB operations"
  ]
}
```

## Success Criteria
- All specified tickets implemented following established patterns
- Integration tests show improvement (fewer failing tests)
- All implementations use utils/dynamo.py patterns consistently
- Error responses follow Error schema structure  
- Basic CRUD operations work via cURL testing
- Sequential reasoning used for implementation planning
- Code follows project conventions and quality standards

## Error Handling
- If implementation fails, save progress and continue with remaining tickets
- If integration tests reveal issues, document problems for /validate phase
- Log implementation decisions and patterns for future reference
- Save implementation summary even if not all tickets completed