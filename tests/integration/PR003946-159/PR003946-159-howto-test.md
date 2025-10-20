# Test Instructions: Backend DynamoDB Conversation Storage

## Ticket Information
- **Ticket**: PR003946-159
- **Type**: Task
- **Priority**: Highest
- **Component**: Integration

## Test Objective
Validate DynamoDB conversation storage integration including session management, turn persistence, and metadata tracking.

## Prerequisites
- [ ] Backend services running on localhost:8080
- [ ] DynamoDB tables configured (conversations, sessions)
- [ ] AWS credentials with DynamoDB access
- [ ] Test user accounts available
- [ ] Environment variables loaded from .env.local

## Test Steps (Sequential Execution Required)

### 1. Setup Phase
- Verify DynamoDB table access
- Create test session
- Prepare test conversation data

### 2. Execution Phase
- Test automatic session creation
- Store multiple conversation turns
- Verify metadata persistence
- Test session updates
- Validate message count tracking

### 3. Validation Phase
- Query stored conversations from DynamoDB
- Verify data integrity and structure
- Check timestamps and metadata
- Validate session state updates
- Confirm analytics data generation

## Pass/Fail Criteria

### ✅ PASS Conditions:
- [ ] Sessions created with unique IDs
- [ ] Turns stored with all required fields
- [ ] Metadata preserved correctly
- [ ] Session lastActivity updates on each turn
- [ ] Message counts increment properly

### ❌ FAIL Conditions:
- [ ] Duplicate session IDs generated
- [ ] Data loss during storage
- [ ] Missing or corrupted metadata
- [ ] Session state inconsistencies
- [ ] Failed DynamoDB operations

## Substeps and Multiple Test Scenarios

### Substep 1: Create New Session
- **Test**: POST to /convo_turn without sessionId
- **Expected**: New session created automatically
- **Pass Criteria**: Session ID returned, retrievable from DB

### Substep 2: Store Conversation Turn
- **Test**: Send message with existing sessionId
- **Expected**: Turn stored, session updated
- **Pass Criteria**: Turn in DB with correct metadata

### Substep 3: Retrieve Conversation
- **Test**: GET /convo_history with sessionId
- **Expected**: All turns returned in order
- **Pass Criteria**: Complete history with metadata

### Substep 4: Verify Analytics
- **Test**: Check conversation analytics
- **Expected**: Message count, duration, engagement metrics
- **Pass Criteria**: Accurate analytics data

## Evidence Collection
- Session creation responses with IDs
- DynamoDB table screenshots
- Stored turn data with metadata
- Session update timestamps
- Analytics metrics output

## Sequential Reasoning Checkpoints
- **Pre-Test Prediction**: Storage should handle concurrent sessions
- **Expected Outcome**: All data persisted with integrity
- **Variance Analysis**: Document any storage anomalies
- **Root Cause Assessment**: Analyze any persistence failures

## Test Commands
```bash
# Test session creation and storage
curl -X POST http://localhost:8080/convo_turn \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Start new conversation",
    "animalId": "lion_001"
  }' | jq .

# Store turn with sessionId
SESSION_ID="<from-previous-response>"
curl -X POST http://localhost:8080/convo_turn \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Continue conversation",
    "animalId": "lion_001",
    "sessionId": "'$SESSION_ID'"
  }' | jq .

# Retrieve conversation history
curl -X GET "http://localhost:8080/convo_history?sessionId=$SESSION_ID" | jq .
```

## Python Validation Test
```python
import boto3
from datetime import datetime

# Connect to DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
sessions_table = dynamodb.Table('quest-dev-conversation-sessions')
conversations_table = dynamodb.Table('quest-dev-conversations')

# Verify session exists
session_id = '<test-session-id>'
response = sessions_table.get_item(Key={'sessionId': session_id})
session = response.get('Item')

assert session is not None
assert session['status'] == 'active'
assert session['messageCount'] > 0
print(f"Session verified: {session}")

# Verify conversation turns
response = conversations_table.query(
    KeyConditionExpression='sessionId = :sid',
    ExpressionAttributeValues={':sid': session_id}
)
turns = response.get('Items', [])

assert len(turns) > 0
assert all('userMessage' in turn for turn in turns)
assert all('assistantReply' in turn for turn in turns)
print(f"Found {len(turns)} conversation turns")
```

## Troubleshooting
### Common Issues and Solutions

**Issue**: Session not created
- **Solution**: Check table exists and permissions
- **Check**: Verify CONVERSATION_SESSION_TABLE_NAME env var

**Issue**: Turns not stored
- **Solution**: Check table write permissions
- **Check**: Monitor DynamoDB CloudWatch metrics

**Issue**: Metadata missing
- **Solution**: Verify metadata object structure
- **Check**: Review storage function parameters

---
*Generated: 2025-09-18*
*Test Category: Integration*
*CMZ TDD Framework v1.0*