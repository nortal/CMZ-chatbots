# VALIDATE-CHAT-DYNAMODB-ADVICE.md

Best practices, troubleshooting guide, and lessons learned for Chat and Chat History validation with DynamoDB verification.

## Best Practices

### 1. Pre-Validation Setup
**Always verify environment before testing:**
```bash
# Check all services are running
curl -s http://localhost:8080/health || echo "Backend not running"
curl -s http://localhost:3001 || echo "Frontend not running"
aws dynamodb list-tables --output table || echo "AWS access issue"

# Record baseline metrics
aws dynamodb scan --table-name quest-dev-conversations --select COUNT --output json
```

### 2. Timing Considerations
**Account for asynchronous operations:**
- **Message Persistence**: Allow 2-3 seconds after sending for DynamoDB write
- **UI Updates**: Chat History may take 1-2 seconds to reflect new conversations
- **Network Latency**: Add wait times between actions for stability
- **Animation Delays**: Some UI elements have transition animations (300-500ms)

### 3. Data Consistency Checks
**Verify at multiple levels:**
```javascript
// Level 1: UI displays message
const uiMessage = await page.textContent('[data-message]');

// Level 2: API returns message
const apiResponse = await fetch('/api/conversations/' + convId);

// Level 3: DynamoDB contains message
const dbItem = await dynamodb.getItem({
  TableName: 'quest-dev-messages',
  Key: { messageId: { S: msgId } }
});

// All three should match
assert(uiMessage === apiResponse.text === dbItem.Item.text.S);
```

### 4. Test User Management
**Use dedicated test accounts:**
- `test@cmz.org` / `testpass123` - General testing
- `parent1@test.cmz.org` / `testpass123` - Parent role testing
- `student1@test.cmz.org` / `testpass123` - Student role testing

**Clean up test data after validation:**
```bash
# Delete test conversations
aws dynamodb delete-item \
  --table-name quest-dev-conversations \
  --key '{"conversationId": {"S": "test_conv_123"}}'
```

## Common Pitfalls and Solutions

### Issue 1: Race Conditions
**Problem**: UI shows data before DynamoDB write completes
**Solution**:
```javascript
// Add explicit waits for DynamoDB
await page.click('button[type="submit"]');
await page.waitForTimeout(2000); // Allow DynamoDB write
const dbResult = await checkDynamoDB();
```

### Issue 2: Stale Data in Chat History
**Problem**: Chat History doesn't show recent conversations
**Solution**:
```javascript
// Force refresh of Chat History
await page.goto('http://localhost:3001/chat-history');
await page.reload(); // Force fresh data fetch
await page.waitForSelector('[data-conversation-row]');
```

### Issue 3: Authentication Token Expiry
**Problem**: Tests fail midway due to JWT expiration
**Solution**:
```javascript
// Re-authenticate if needed
const response = await page.goto('/api/health');
if (response.status() === 401) {
  await loginTestUser();
}
```

### Issue 4: DynamoDB Throttling
**Problem**: Too many rapid queries cause throttling
**Solution**:
```bash
# Use exponential backoff
for i in 1 2 4 8; do
  aws dynamodb get-item ... && break
  sleep $i
done
```

### Issue 5: Browser Memory Leaks
**Problem**: Long-running tests cause browser slowdown
**Solution**:
```javascript
// Periodically restart browser context
if (testCount % 10 === 0) {
  await context.close();
  context = await browser.newContext();
  page = await context.newPage();
}
```

## Integration Guidelines

### Working with Chat History Epic
The Chat History Epic (PR003946-170) introduces several components to validate:

1. **Conversation List Component**:
   - Displays all user conversations
   - Real-time updates when new messages arrive
   - Pagination for large datasets

2. **Filter System**:
   - Date range filtering (today, week, month, all)
   - Animal personality filtering
   - User role-based filtering (parent/student)

3. **Statistics Dashboard**:
   - Total conversations count
   - Average conversation length
   - Most active animals
   - Peak usage times

4. **Conversation Viewer**:
   - Full message history
   - Export functionality
   - Share conversation feature

### DynamoDB Schema Validation
```javascript
// Expected conversation structure
{
  conversationId: "conv_[timestamp]",
  userId: "user@email.com",
  animalId: "animal_name",
  startTime: "ISO8601_timestamp",
  endTime: "ISO8601_timestamp",
  messageCount: 10,
  metadata: {
    userRole: "student|parent|guest",
    sessionDuration: 300,
    device: "desktop|mobile"
  }
}

// Expected message structure
{
  messageId: "msg_[timestamp]",
  conversationId: "conv_[timestamp]",
  text: "Message content",
  role: "user|assistant",
  timestamp: "ISO8601_timestamp",
  metadata: {
    sentiment: "positive|neutral|negative",
    wordCount: 25
  }
}
```

## Troubleshooting Procedures

### Diagnostic Steps
1. **Check Service Health**:
```bash
# Backend health
curl http://localhost:8080/health

# Frontend status
curl http://localhost:3001

# DynamoDB access
aws dynamodb describe-table --table-name quest-dev-conversations
```

2. **Verify Authentication**:
```bash
# Test login
curl -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@cmz.org", "password": "testpass123"}'
```

3. **Check Browser Console**:
```javascript
// In Playwright
const logs = await page.evaluate(() => {
  return window.consoleErrors || [];
});
console.log('Browser errors:', logs);
```

4. **Inspect Network Traffic**:
```javascript
// Monitor API calls
page.on('response', response => {
  if (response.status() >= 400) {
    console.log(`Error: ${response.url()} - ${response.status()}`);
  }
});
```

### Recovery Procedures

**Service Recovery**:
```bash
# Restart backend
make stop-api && make run-api

# Restart frontend
cd frontend && pkill -f "npm run dev" && npm run dev

# Clear DynamoDB test data
./scripts/cleanup-test-data.sh
```

**Browser Recovery**:
```javascript
// Full browser restart
await browser.close();
browser = await playwright.chromium.launch({ headless: false });
page = await browser.newPage();
```

## Advanced Usage Scenarios

### 1. Multi-User Chat Testing
```javascript
// Simulate multiple concurrent users
const users = ['test1@cmz.org', 'test2@cmz.org', 'test3@cmz.org'];
const contexts = await Promise.all(
  users.map(async user => {
    const context = await browser.newContext();
    const page = await context.newPage();
    await loginUser(page, user);
    return { user, page };
  })
);

// Send messages from different users
for (const { user, page } of contexts) {
  await sendMessage(page, `Hello from ${user}`);
}
```

### 2. Load Testing
```javascript
// Send rapid messages to test performance
for (let i = 0; i < 100; i++) {
  await page.type('#message-input', `Load test message ${i}`);
  await page.press('#message-input', 'Enter');
  await page.waitForTimeout(100); // Small delay
}

// Verify all messages persisted
const dbCount = await getDynamoDBMessageCount(conversationId);
assert(dbCount === 100, 'All messages should persist');
```

### 3. Cross-Browser Validation
```javascript
const browsers = ['chromium', 'firefox', 'webkit'];
for (const browserType of browsers) {
  const browser = await playwright[browserType].launch();
  await runValidation(browser);
  await browser.close();
}
```

### 4. Data Export Verification
```javascript
// Test conversation export
await page.click('[data-export-button]');
const download = await page.waitForEvent('download');
const content = await download.path();

// Verify export contains all messages
const exportData = JSON.parse(fs.readFileSync(content));
assert(exportData.messages.length === expectedCount);
```

## Performance Benchmarks

### Expected Response Times
- **Message Send → UI Update**: < 500ms
- **Message Send → DynamoDB Write**: < 2s
- **Chat History Load**: < 1s for 100 conversations
- **Filter Application**: < 300ms
- **Conversation Open**: < 500ms

### Resource Usage Targets
- **Browser Memory**: < 500MB per test session
- **DynamoDB Read Units**: < 50 per validation run
- **DynamoDB Write Units**: < 20 per validation run
- **API Response Time**: p95 < 200ms

## Validation Metrics

### Key Performance Indicators
1. **Data Integrity Score**: (Matching Records / Total Records) * 100
2. **UI Responsiveness**: Average time for UI updates
3. **Persistence Reliability**: Successful writes / Total writes
4. **Filter Accuracy**: Correct results / Total filter applications
5. **Cross-Browser Compatibility**: Passing browsers / Total browsers

### Success Thresholds
- Data Integrity: ≥ 99%
- UI Responsiveness: ≤ 1s average
- Persistence Reliability: 100%
- Filter Accuracy: 100%
- Browser Compatibility: ≥ 80% (5/6 browsers)

## Continuous Improvement

### Recent Issues and Fixes
1. **Issue**: Chat History not updating in real-time
   - **Fix**: Added WebSocket connection for live updates
   - **Validation**: Test real-time sync between multiple browser sessions

2. **Issue**: DynamoDB pagination breaking with large datasets
   - **Fix**: Implemented cursor-based pagination
   - **Validation**: Test with 1000+ conversations

3. **Issue**: Memory leak in long chat sessions
   - **Fix**: Implemented message virtualization
   - **Validation**: Run 30-minute continuous chat test

### Future Enhancements
- Add screenshot comparison for visual regression testing
- Implement performance profiling during validation
- Create automated test data generation
- Add multi-region DynamoDB testing
- Implement chaos engineering scenarios

## Related Documentation
- `.claude/commands/validate-chat-dynamodb.md` - Main validation command
- `CHAT-HISTORY-EPIC.md` - Feature documentation
- `backend/api/impl/conversation.py` - Conversation implementation
- `frontend/src/pages/ChatHistory.tsx` - UI implementation