# Chat and Chat History Validation with DynamoDB

**Purpose**: Comprehensive E2E validation of chat functionality including backend DynamoDB persistence using visible Playwright browser automation

**Usage**: `/validate-chat-dynamodb`

## Context
This validation ensures the Chat History Epic (PR003946-170) is fully functional by testing both the chat interface and chat history windows while verifying data persistence in DynamoDB. The test uses visible browser automation so you can observe the validation in real-time.

## Sequential Reasoning Approach

Use MCP Sequential Thinking to systematically validate chat functionality:

### Phase 1: Environment Setup and Verification
**Use Sequential Reasoning to:**
1. **Service Health Check**: Verify backend API and frontend are running
2. **DynamoDB Access**: Confirm AWS credentials and table access
3. **Browser Setup**: Initialize Playwright with visible browser
4. **Test User Authentication**: Login with test credentials
5. **Baseline Data**: Record initial DynamoDB state

**Key Questions for Sequential Analysis:**
- Are all required services healthy and accessible?
- Can we connect to DynamoDB tables (conversations, messages)?
- Is the test user authenticated with proper JWT token?
- What's the current conversation count in the database?

### Phase 2: Chat Interface Testing
**Implementation Order (Follow Exactly):**

#### Step 1: Navigate to Chat Interface
```bash
# Using Playwright MCP with visible browser
mcp__playwright__browser_navigate --url "http://localhost:3001/chat"
mcp__playwright__browser_snapshot  # Capture initial state
```

#### Step 2: Send Test Messages
```bash
# Send a series of test messages with timestamps
TEST_MESSAGE_1="Test message $(date +%s) - Hello from validation"
TEST_MESSAGE_2="Follow-up message - Testing real-time updates"
TEST_MESSAGE_3="Final message - Checking persistence"

# Type and send each message
mcp__playwright__browser_type --element "chat-input" --text "$TEST_MESSAGE_1" --submit true
mcp__playwright__browser_wait_for --time 2  # Allow for response

mcp__playwright__browser_type --element "chat-input" --text "$TEST_MESSAGE_2" --submit true
mcp__playwright__browser_wait_for --time 2

mcp__playwright__browser_type --element "chat-input" --text "$TEST_MESSAGE_3" --submit true
mcp__playwright__browser_wait_for --time 2
```

#### Step 3: Capture Conversation ID
```bash
# Extract conversation ID from UI or network requests
mcp__playwright__browser_evaluate --function "() => {
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.get('conversationId') || document.querySelector('[data-conversation-id]')?.dataset.conversationId;
}"
```

#### Step 4: Verify DynamoDB Persistence
```bash
# Query DynamoDB for the conversation
aws dynamodb get-item \
  --table-name quest-dev-conversations \
  --key '{"conversationId": {"S": "CONVERSATION_ID_HERE"}}' \
  --output json

# Verify messages are stored
aws dynamodb query \
  --table-name quest-dev-messages \
  --key-condition-expression "conversationId = :cid" \
  --expression-attribute-values '{":cid": {"S": "CONVERSATION_ID_HERE"}}' \
  --output json
```

### Phase 3: Chat History Validation
**Validation Steps:**

#### Step 1: Navigate to Chat History
```bash
mcp__playwright__browser_navigate --url "http://localhost:3001/chat-history"
mcp__playwright__browser_wait_for --text "Chat History"
mcp__playwright__browser_snapshot  # Capture chat history page
```

#### Step 2: Verify Conversation Appears
```bash
# Check if our test conversation is listed
mcp__playwright__browser_wait_for --text "$TEST_MESSAGE_1"

# Verify statistics updated
mcp__playwright__browser_evaluate --function "() => {
  const stats = document.querySelector('[data-total-conversations]');
  return stats ? stats.textContent : 'Stats not found';
}"
```

#### Step 3: Test Filtering and Sorting
```bash
# Test date filter
mcp__playwright__browser_click --element "date-filter" --ref "button[aria-label='Date filter']"
mcp__playwright__browser_click --element "today-option" --ref "option[value='today']"
mcp__playwright__browser_wait_for --time 1

# Test animal filter
mcp__playwright__browser_click --element "animal-filter" --ref "select[aria-label='Animal filter']"
mcp__playwright__browser_select_option --element "animal-filter" --values ["Leo the Lion"]

# Test sorting
mcp__playwright__browser_click --element "sort-dropdown" --ref "button[aria-label='Sort options']"
mcp__playwright__browser_click --element "sort-newest" --ref "option[value='newest']"
```

#### Step 4: Open Conversation Viewer
```bash
# Click on the test conversation
mcp__playwright__browser_click --element "conversation-row" --ref "tr[data-conversation-id]"
mcp__playwright__browser_wait_for --text "Conversation Details"

# Verify all messages are displayed
mcp__playwright__browser_evaluate --function "() => {
  const messages = document.querySelectorAll('[data-message]');
  return messages.length;
}"
```

### Phase 4: Data Integrity Verification
**Cross-Validation Checklist:**

#### Step 1: Compare UI with DynamoDB
```bash
# Get conversation count from UI
UI_COUNT=$(mcp__playwright__browser_evaluate --function "() => {
  const count = document.querySelector('[data-total-conversations]');
  return parseInt(count?.textContent || '0');
}")

# Get conversation count from DynamoDB
DB_COUNT=$(aws dynamodb scan \
  --table-name quest-dev-conversations \
  --select COUNT \
  --output json | jq '.Count')

# Compare counts
if [ "$UI_COUNT" -eq "$DB_COUNT" ]; then
  echo "✅ Conversation counts match: $UI_COUNT"
else
  echo "❌ Count mismatch - UI: $UI_COUNT, DB: $DB_COUNT"
fi
```

#### Step 2: Verify Message Content
```bash
# Extract messages from DynamoDB
aws dynamodb query \
  --table-name quest-dev-messages \
  --key-condition-expression "conversationId = :cid" \
  --expression-attribute-values '{":cid": {"S": "CONVERSATION_ID_HERE"}}' \
  --output json | jq '.Items[].messageText.S'

# Compare with UI messages
mcp__playwright__browser_evaluate --function "() => {
  const messages = Array.from(document.querySelectorAll('[data-message-text]'));
  return messages.map(m => m.textContent);
}"
```

#### Step 3: Generate Validation Report
```bash
cat > validation-report-$(date +%Y%m%d-%H%M%S).md << EOF
# Chat Validation Report

## Test Execution
- **Date**: $(date)
- **Branch**: $(git branch --show-current)
- **Test User**: test@cmz.org

## Results Summary
- **Chat Interface**: [PASS/FAIL]
- **Message Sending**: [PASS/FAIL]
- **DynamoDB Persistence**: [PASS/FAIL]
- **Chat History Display**: [PASS/FAIL]
- **Filtering/Sorting**: [PASS/FAIL]
- **Data Integrity**: [PASS/FAIL]

## DynamoDB Verification
- **Conversations Table**: $DB_COUNT records
- **Messages Persisted**: [COUNT]
- **Data Consistency**: [VERIFIED/ISSUES]

## Screenshots
- Chat Interface: .playwright-mcp/chat-interface.png
- Chat History: .playwright-mcp/chat-history.png
- Conversation Viewer: .playwright-mcp/conversation-viewer.png

## Issues Found
[List any issues discovered during validation]

## Recommendations
[Suggested fixes or improvements]
EOF
```

## Implementation Details

### Test Data
```javascript
// Test conversation structure in DynamoDB
{
  "conversationId": "conv_[timestamp]",
  "userId": "test@cmz.org",
  "animalId": "leo_lion",
  "startTime": "2024-01-19T10:00:00Z",
  "messages": [
    {
      "messageId": "msg_001",
      "text": "Test message",
      "timestamp": "2024-01-19T10:00:01Z",
      "role": "user"
    }
  ]
}
```

### Playwright Configuration
```javascript
// Visible browser settings
const browser = await chromium.launch({
  headless: false,  // Show browser
  slowMo: 500,     // Slow down for visibility
  viewport: { width: 1280, height: 720 }
});
```

### AWS CLI Queries
```bash
# List recent conversations
aws dynamodb scan \
  --table-name quest-dev-conversations \
  --filter-expression "startTime > :time" \
  --expression-attribute-values '{":time": {"S": "2024-01-19T00:00:00Z"}}' \
  --output table

# Get specific conversation with messages
aws dynamodb get-item \
  --table-name quest-dev-conversations \
  --key '{"conversationId": {"S": "conv_12345"}}' \
  --output json | jq '.'
```

## Integration Points
- **Backend API**: Must be running on port 8080
- **Frontend**: Must be running on port 3001
- **DynamoDB**: Requires AWS credentials and table access
- **Playwright MCP**: For browser automation
- **AWS CLI**: For DynamoDB verification

## Quality Gates
- [ ] All services health check passes
- [ ] Test user can authenticate successfully
- [ ] Messages persist to DynamoDB within 5 seconds
- [ ] Chat History shows new conversations immediately
- [ ] Conversation viewer displays all messages correctly
- [ ] UI conversation count matches DynamoDB count
- [ ] No console errors during test execution
- [ ] All screenshots captured successfully

## Success Criteria
1. **Real-time Updates**: Messages appear in chat within 2 seconds
2. **Data Persistence**: All messages stored in DynamoDB
3. **History Accuracy**: Chat History reflects all conversations
4. **Filter Functionality**: All filters work as expected
5. **Data Integrity**: 100% match between UI and database
6. **Performance**: Page loads under 3 seconds
7. **Cross-browser**: Works in Chrome, Firefox, Safari

## Error Handling

### Common Issues and Solutions
```bash
# Backend not running
if ! curl -s http://localhost:8080/system_health > /dev/null; then
  echo "Starting backend..."
  make run-api &
  sleep 5
fi

# Frontend not running
if ! curl -s http://localhost:3001 > /dev/null; then
  echo "Starting frontend..."
  cd frontend && npm run dev &
  sleep 5
fi

# DynamoDB access issues
if ! aws dynamodb list-tables > /dev/null 2>&1; then
  echo "Check AWS credentials: aws configure list"
  exit 1
fi
```

## References
- `VALIDATE-CHAT-DYNAMODB-ADVICE.md` - Best practices and troubleshooting
- Chat History Epic documentation (PR003946-170)
- DynamoDB table schemas in backend documentation