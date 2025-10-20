# Test Instructions: Infrastructure Setup DynamoDB Tables

## Ticket Information
- **Ticket**: PR003946-156
- **Type**: Task
- **Priority**: Highest
- **Component**: Integration

## Test Objective
Validate that DynamoDB infrastructure for conversation management is properly set up and functional with correct table operations and access patterns.

## Prerequisites
- [ ] Backend services running on localhost:8080
- [ ] AWS credentials configured (AWS_PROFILE=cmz)
- [ ] DynamoDB access to us-west-2 region
- [ ] Python environment with boto3 installed
- [ ] Environment variables loaded from .env.local

## Test Steps (Sequential Execution Required)

### 1. Setup Phase
- Verify AWS credentials are configured correctly
- Confirm connection to DynamoDB in us-west-2 region
- Check if required tables exist or need creation

### 2. Execution Phase
- Test table creation functions for conversations and sessions
- Verify session creation with unique IDs
- Test conversation turn storage with metadata
- Validate history retrieval with pagination
- Test role-based access control functions

### 3. Validation Phase
- Confirm tables are accessible via boto3
- Verify data structure matches specifications
- Test CRUD operations on both tables
- Validate access control returns correct permissions
- Check analytics generation functions

## Pass/Fail Criteria

### ✅ PASS Conditions:
- [ ] DynamoDB tables accessible and operational
- [ ] Session creation returns unique session IDs
- [ ] Conversation turns stored with all metadata
- [ ] History retrieval returns chronological order
- [ ] Role-based access control functions correctly

### ❌ FAIL Conditions:
- [ ] Unable to connect to DynamoDB
- [ ] Table operations fail or timeout
- [ ] Data corruption or incorrect structure
- [ ] Access control allows unauthorized access
- [ ] Missing required fields in stored data

## Substeps and Multiple Test Scenarios

### Substep 1: Create Conversation Session
- **Test**: Call create_conversation_session() with user and animal IDs
- **Expected**: Returns unique session ID, timestamps set correctly
- **Pass Criteria**: Session retrievable from DynamoDB

### Substep 2: Store Conversation Turn
- **Test**: Store user message and assistant reply with metadata
- **Expected**: Turn stored with unique ID, session updated
- **Pass Criteria**: Turn retrievable with correct data

### Substep 3: Retrieve Conversation History
- **Test**: Get history for session with pagination
- **Expected**: Returns turns in chronological order
- **Pass Criteria**: Pagination works, order correct

### Substep 4: Test Access Control
- **Test**: Check access for different user roles
- **Expected**: Users see own, parents see children's, admins see all
- **Pass Criteria**: Permissions enforced correctly

## Evidence Collection
- DynamoDB table screenshots showing structure
- Session creation response with unique IDs
- Stored conversation data with metadata
- Access control test results for each role
- Performance metrics for operations

## Sequential Reasoning Checkpoints
- **Pre-Test Prediction**: DynamoDB utilities should handle all CRUD operations
- **Expected Outcome**: Tables created/accessed, data persisted correctly
- **Variance Analysis**: Document any deviations from expected behavior
- **Root Cause Assessment**: Analyze any failures systematically

## Test Commands
```python
# Test session creation
from openapi_server.impl.utils.conversation_dynamo import *
session_id = create_conversation_session('user123', 'lion_001')
print(f"Created session: {session_id}")

# Test turn storage
turn_id = store_conversation_turn(
    session_id,
    "Hello!",
    "Hi there! I'm Leo the Lion!",
    {"tokens": 10, "latency": 50}
)
print(f"Stored turn: {turn_id}")

# Test history retrieval
history = get_conversation_history(session_id, limit=10)
print(f"Retrieved {len(history)} turns")

# Test access control
has_access = check_user_access_to_session('user123', session_id, 'user')
print(f"User access: {has_access}")
```

## Troubleshooting
### Common Issues and Solutions

**Issue**: Cannot connect to DynamoDB
- **Solution**: Verify AWS_PROFILE=cmz and AWS_REGION=us-west-2
- **Check**: Run `aws dynamodb list-tables` to test connection

**Issue**: Tables don't exist
- **Solution**: Tables should be created automatically or manually
- **Check**: Use AWS Console to verify table existence

**Issue**: Permission denied errors
- **Solution**: Check IAM permissions for DynamoDB operations
- **Check**: Verify AWS credentials have necessary permissions

---
*Generated: 2025-09-18*
*Test Category: Integration*
*CMZ TDD Framework v1.0*