# VALIDATE-FRONTEND-BACKEND-INTEGRATION-ADVICE.md

## Overview
This guide provides best practices, troubleshooting tips, and implementation guidance for the `/validate-frontend-backend-integration` command. This command performs comprehensive E2E validation of the CMZ chatbot platform including animal management, family management, user authentication, and chat/conversation features using Playwright MCP with visible browser testing and Teams webhook reporting.

## Command Purpose
Validate complete frontend-backend-database integration across all major features:
- **Service Health**: Backend API and frontend React app
- **Authentication**: All user roles (parent, student, member, admin)
- **Animal Management**: Chatbot personalities and configurations
- **Family Management**: Add Family dialog, form fields, DynamoDB persistence
- **User Management**: Login workflows and role-based access control
- **Chat/Conversation**: Message sending, AI responses, conversation history, DynamoDB persistence
- **Performance**: Response times, cross-browser compatibility
- **Reporting**: Automated Teams notification with validation results

## Prerequisites

### Environment Setup
```bash
# Backend must be running on port 8080
docker ps | grep cmz-api || make run-api

# Frontend must be running on port 3000
curl -s http://localhost:3000 || npm run dev

# Teams webhook URL must be configured
echo $TEAMS_WEBHOOK_URL
```

### Required Environment Variables
```bash
# AWS credentials for DynamoDB access
export AWS_PROFILE=cmz
export AWS_REGION=us-west-2

# Teams webhook URL (required for Step 10)
export TEAMS_WEBHOOK_URL="https://default7c359f6b9f2f4042bf2db08ce16c5c.c1.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/cba76b9b30b644aaae7784ead5b54be4/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=03f33nmke2hKhd0FhZqpLte_NVMWI3MQkd6jqLDAVqA"

# Frontend URL (defaults to localhost:3000)
export FRONTEND_URL=http://localhost:3000

# Backend URL (defaults to localhost:8080)
export BACKEND_URL=http://localhost:8080
```

### Test User Credentials
Ensure these users exist in DynamoDB quest-dev-user table:
- `parent1@test.cmz.org` / `testpass123` (parent role)
- `student1@test.cmz.org` / `testpass123` (student role)
- `student2@test.cmz.org` / `testpass123` (student role)
- `test@cmz.org` / `testpass123` (default member role)
- `user_parent_001@cmz.org` / `testpass123` (parent role)

## Step-by-Step Execution Guide

### Step 0: Service Startup & Health Validation
**Critical**: Always verify both services are running with latest code.

**Best Practices**:
- Stop and rebuild containers to ensure latest code: `make stop-api && make clean-api && make build-api && make run-api`
- Frontend: Kill existing processes before restart: `pkill -f vite && npm run dev`
- Wait for health checks to pass before proceeding
- Verify proxy configuration: `curl http://localhost:3000/api/` should return backend response

**Common Issues**:
- **Backend not responding**: Check `docker logs cmz-openapi-api` for errors
- **Frontend not starting**: Check port 3000 availability with `lsof -i :3000`
- **Proxy not working**: Verify vite.config.ts proxy configuration

### Step 1-4: Animal Management Validation
**Existing functionality** - validates chatbot personalities page and configuration.

**Key Checkpoints**:
- Admin login successful
- Animal Management navigation works
- Chatbot Personalities page loads
- Real animal data displays (Bella, Leo, Charlie)
- Animal configuration form opens with actual data

### Step 5: Family Management UI Testing
**New Feature** - validates Add Family dialog with visible browser.

**Playwright MCP Usage**:
```javascript
// Navigate after login
mcp__playwright__browser_navigate({ url: 'http://localhost:3000/families/manage' })

// Click Add New Family button
mcp__playwright__browser_snapshot() // Get element references
mcp__playwright__browser_click({
  element: 'Add New Family button',
  ref: '[exact ref from snapshot]'
})

// Fill family name
mcp__playwright__browser_type({
  element: 'Family Name input',
  ref: '[exact ref from snapshot]',
  text: 'Test Family 2025'
})

// Fill multiple fields efficiently
mcp__playwright__browser_fill_form({
  fields: [
    { name: 'Street', type: 'textbox', ref: '[ref]', value: '123 Test St' },
    { name: 'City', type: 'textbox', ref: '[ref]', value: 'Seattle' },
    { name: 'State', type: 'textbox', ref: '[ref]', value: 'WA' },
    { name: 'Zip', type: 'textbox', ref: '[ref]', value: '98101' }
  ]
})

// Submit form
mcp__playwright__browser_click({ element: 'Submit button', ref: '[ref]' })

// Take screenshot
mcp__playwright__browser_take_screenshot({ filename: 'family-created.png' })
```

**DynamoDB Validation**:
```bash
# Verify family was created
aws dynamodb scan \
  --table-name quest-dev-family \
  --filter-expression "familyName = :name" \
  --expression-attribute-values '{":name":{"S":"Test Family 2025"}}' \
  --profile cmz
```

**Common Issues**:
- **Dialog not opening**: Check for JavaScript errors with `browser_console_messages`
- **Fields not filling**: Verify element refs from snapshot are correct
- **Submit not working**: Check form validation - parent selection may be required
- **DynamoDB not persisting**: Check backend logs for API errors

### Step 6: User Management UI Testing
**New Feature** - validates login for all user roles.

**Best Practices**:
- Test each user sequentially, not in parallel
- Clear browser state between users with `browser_close` and new browser instance
- Verify JWT token in network requests with `browser_network_requests`
- Check for CORS errors in console messages

**Login Workflow Pattern**:
```javascript
// For each test user
mcp__playwright__browser_navigate({ url: 'http://localhost:3000/login' })
mcp__playwright__browser_snapshot()

mcp__playwright__browser_type({
  element: 'Email input',
  ref: '[email input ref]',
  text: 'parent1@test.cmz.org'
})

mcp__playwright__browser_type({
  element: 'Password input',
  ref: '[password input ref]',
  text: 'testpass123'
})

mcp__playwright__browser_click({ element: 'Login button', ref: '[button ref]' })

// Wait for redirect
mcp__playwright__browser_wait_for({ text: 'Dashboard', timeout: 5000 })

// Verify URL changed to dashboard
mcp__playwright__browser_snapshot() // Check current URL in response

// Take success screenshot
mcp__playwright__browser_take_screenshot({ filename: 'parent1-login-success.png' })
```

**Role-Based Access Validation**:
- Parent users should see "Family Management" link
- Student users should NOT see admin features
- Test navigation restrictions by attempting to access restricted URLs

**Common Issues**:
- **Login fails with CORS error**: Backend CORS configuration issue - check Flask-CORS setup
- **Token not generated**: Backend auth endpoint error - check auth.py and handlers.py
- **Redirect not happening**: Frontend routing issue - check React Router configuration
- **User not found**: Verify user exists in DynamoDB quest-dev-user table

### Step 7: Chat/Conversation UI Testing
**New Feature** - validates chat functionality with AI responses and DynamoDB persistence.

**Critical Timing Considerations**:
- Chat connection establishment can take 2-5 seconds
- ChatGPT API responses can take 3-10 seconds
- Always use `browser_wait_for` with adequate timeouts

**Chat Testing Pattern**:
```javascript
// Navigate to chat (after login)
mcp__playwright__browser_navigate({ url: 'http://localhost:3000/chat' })

// Wait for connection - input will be disabled until connected
mcp__playwright__browser_wait_for({ timeout: 10000 })
mcp__playwright__browser_snapshot()

// Verify chat input is enabled (check disabled attribute)
// If disabled=true, wait longer for connection

// Fill and send message
mcp__playwright__browser_type({
  element: 'Chat message input',
  ref: '[input ref]',
  text: 'Hello! Tell me about your quills.',
  submit: false // Don't auto-submit
})

// Click send and monitor network
mcp__playwright__browser_click({ element: 'Send button', ref: '[button ref]' })

// Wait for AI response (can take 5-10 seconds)
mcp__playwright__browser_wait_for({ text: 'quill', timeout: 15000 })

// Take screenshot showing message exchange
mcp__playwright__browser_take_screenshot({ filename: 'chat-message-sent.png' })

// Check network requests for /convo_turn
mcp__playwright__browser_network_requests()
```

**Multi-Turn Conversation Testing**:
```javascript
// Send follow-up message
mcp__playwright__browser_type({
  element: 'Chat input',
  ref: '[ref]',
  text: 'How many quills do you have?'
})
mcp__playwright__browser_click({ element: 'Send button', ref: '[ref]' })
mcp__playwright__browser_wait_for({ timeout: 15000 })

// Verify sessionId is same across turns (check network requests)
```

**Conversation History Validation**:
```javascript
// Navigate to conversation history
mcp__playwright__browser_navigate({ url: 'http://localhost:3000/conversations/history' })
mcp__playwright__browser_snapshot()

// Verify session appears in list
// Click session to view details
// Verify all messages display correctly
mcp__playwright__browser_take_screenshot({ filename: 'conversation-history.png' })
```

**DynamoDB Validation**:
```bash
# Query conversation turns by sessionId
aws dynamodb query \
  --table-name quest-dev-conversation-turn \
  --key-condition-expression "sessionId = :sid" \
  --expression-attribute-values '{":sid":{"S":"[sessionId from network request]"}}' \
  --profile cmz

# Should show all message turns with user and assistant messages
```

**Common Issues**:
- **Chat input disabled**: Connection not established - wait longer or check WebSocket connection
- **Message not sending**: Network error or backend down - check console errors
- **No AI response**: ChatGPT API error - check backend logs for OpenAI errors
- **History not showing**: DynamoDB query issue - verify sessionId format
- **Conversation context lost**: sessionId not consistent - check frontend state management

### Step 8: Performance & Cross-Browser Validation
**Best Practices**:
- Use `browser_network_requests` to measure API response times
- Check console for warnings/errors with `browser_console_messages`
- Test mobile viewport with `browser_resize`

### Step 9: Data Flow Analysis
**Sequential Reasoning Focus**:
- Trace data from DynamoDB → Backend → Frontend → UI
- Verify data transformations are correct (camelCase vs snake_case)
- Check error handling at each integration point

### Step 10: Teams Webhook Reporting
**CRITICAL**: This is the most common failure point. Follow these steps EXACTLY.

#### 10a: Read TEAMS-WEBHOOK-ADVICE.md (MANDATORY)
**Why this is critical**:
- Teams webhooks ONLY accept Microsoft Adaptive Card format
- Plain text or simple JSON will fail silently (202 response but no message)
- The webhook URL is a Power Automate endpoint with specific requirements

**Execution**:
```bash
# Read the advice file FIRST
cat /Users/keithstegbauer/repositories/CMZ-chatbots/TEAMS-WEBHOOK-ADVICE.md

# Key takeaways:
# 1. Message MUST have "type": "message"
# 2. MUST have "attachments" array with adaptive card
# 3. MUST have proper schema and version
# 4. MUST use "FactSet" for structured data
```

#### 10b: Generate Validation Report
**Data Collection**:
- Compile results from all previous steps (0-9)
- Count successes and failures
- Measure performance metrics
- Note any errors or warnings

**Report Structure**:
```python
validation_results = {
    'service_status': '✅ Backend & Frontend Running',
    'auth_results': '✅ 5/5 users validated',
    'animal_mgmt': '✅ All tests passed',
    'family_mgmt': '✅ Dialog, fields, persistence validated',
    'user_mgmt': '✅ All roles tested',
    'chat_convo': '✅ Messages, history, DynamoDB validated',
    'performance': '✅ <2s response times',
    'dynamodb': '✅ All tables verified',
    'overall': '✅ VALIDATION PASSED'
}
```

#### 10c: Send Teams Notification
**Critical Implementation Pattern** (from TEAMS-WEBHOOK-ADVICE.md):

```python
#!/usr/bin/env python3
import os
import requests
from datetime import datetime

# Get webhook URL from environment
webhook_url = os.getenv('TEAMS_WEBHOOK_URL')
if not webhook_url:
    print("❌ ERROR: TEAMS_WEBHOOK_URL environment variable not set")
    exit(1)

# Build facts from validation results
validation_facts = [
    {"title": "🚀 Service Status", "value": "✅ Backend & Frontend Running"},
    {"title": "🔐 Authentication", "value": "✅ 5/5 users validated"},
    {"title": "🦁 Animal Management", "value": "✅ All tests passed"},
    {"title": "🏠 Family Management", "value": "✅ Dialog, fields, persistence validated"},
    {"title": "👥 User Management", "value": "✅ All roles tested"},
    {"title": "💬 Chat/Conversation", "value": "✅ Messages, history, DynamoDB validated"},
    {"title": "⚡ Performance", "value": "✅ <2s response times"},
    {"title": "💾 DynamoDB", "value": "✅ All tables verified"},
    {"title": "📊 Overall Status", "value": "✅ VALIDATION PASSED"}
]

# Create adaptive card - EXACT format from TEAMS-WEBHOOK-ADVICE.md
card = {
    "type": "message",
    "attachments": [
        {
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": {
                "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                "type": "AdaptiveCard",
                "version": "1.4",
                "body": [
                    {
                        "type": "TextBlock",
                        "text": "CMZ Frontend-Backend Integration Validation",
                        "size": "Large",
                        "weight": "Bolder",
                        "wrap": True
                    },
                    {
                        "type": "TextBlock",
                        "text": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        "size": "Small",
                        "isSubtle": True,
                        "wrap": True
                    },
                    {
                        "type": "FactSet",
                        "facts": validation_facts
                    }
                ]
            }
        }
    ]
}

# Send to Teams
response = requests.post(
    webhook_url,
    json=card,
    headers={"Content-Type": "application/json"}
)

# Validate response
if response.status_code == 202:
    print("✅ Teams notification sent successfully")
    print("✅ Check Teams channel for message delivery")
else:
    print(f"❌ Failed to send Teams notification: {response.status_code}")
    print(f"Response: {response.text}")
    exit(1)
```

**Save and Execute**:
```bash
# Save script
cat > /tmp/send_teams_notification.py << 'EOF'
[paste script above]
EOF

# Execute
python3 /tmp/send_teams_notification.py
```

#### 10d: Verify Teams Message Delivery
**Success Indicators**:
- ✅ HTTP 202 response from webhook
- ✅ Message appears in Teams channel within 5 seconds
- ✅ Adaptive card renders with title, timestamp, and facts
- ✅ All validation facts visible and properly formatted
- ✅ No raw JSON visible in Teams message

**Failure Indicators**:
- ❌ 202 response but no message in Teams → Using wrong format (plain text instead of adaptive card)
- ❌ 400 Bad Request → Malformed JSON or missing required fields
- ❌ Message shows raw JSON → Not using adaptive card format
- ❌ 500 Server Error → Power Automate flow error

**Troubleshooting**:
1. **202 but no message**: Re-read TEAMS-WEBHOOK-ADVICE.md and verify exact adaptive card structure
2. **400 Bad Request**: Validate JSON with `python3 -m json.tool` or online JSON validator
3. **Raw JSON in Teams**: Missing "contentType": "application/vnd.microsoft.card.adaptive"
4. **No timestamp**: Missing TextBlock with datetime.now()
5. **Facts not showing**: Check "FactSet" structure has "facts" array with "title" and "value"

## Common Pitfalls & Solutions

### Playwright MCP Usage
**Pitfall**: Trying to use element selectors directly instead of refs from snapshot
**Solution**: Always call `browser_snapshot()` first, get exact ref, then use in subsequent calls

**Pitfall**: Not waiting for dynamic content to load
**Solution**: Use `browser_wait_for` with adequate timeouts (5-15 seconds for AI responses)

**Pitfall**: Running tests with headless browser
**Solution**: Always use headless: false or browser will close too quickly to observe

### Teams Webhook
**Pitfall**: Sending plain text or simple JSON
**Solution**: ALWAYS use adaptive card format from TEAMS-WEBHOOK-ADVICE.md

**Pitfall**: Not reading TEAMS-WEBHOOK-ADVICE.md before implementation
**Solution**: Make Step 10a mandatory - read file before writing any code

**Pitfall**: Assuming 202 means message was delivered
**Solution**: 202 only means webhook accepted request, not that message rendered

### DynamoDB Validation
**Pitfall**: Querying immediately after UI operation
**Solution**: Wait 1-2 seconds for eventual consistency

**Pitfall**: Using wrong table names
**Solution**: Use exact table names: quest-dev-family, quest-dev-conversation, quest-dev-conversation-turn

### Service Health
**Pitfall**: Assuming services are running because they were yesterday
**Solution**: ALWAYS verify with health checks in Step 0

**Pitfall**: Not rebuilding after code changes
**Solution**: Stop, clean, rebuild containers for latest code

## Performance Optimization

### Parallel Execution
**Do NOT parallelize**:
- Sequential user logins (state management issues)
- Chat message sending (sessionId consistency)
- Family creation (race conditions)

**CAN parallelize**:
- Taking screenshots
- Reading multiple advice files
- Multiple DynamoDB queries for different tables

### Screenshot Management
```bash
# Create evidence directory at start
mkdir -p /tmp/cmz-validation-evidence

# Take screenshots with descriptive names
browser_take_screenshot({
  filename: '/tmp/cmz-validation-evidence/step5-family-dialog-opened.png'
})
```

### Network Request Monitoring
```javascript
// Check network requests periodically
mcp__playwright__browser_network_requests()

// Filter for specific endpoints
// Look for 4xx/5xx status codes
// Measure response times
```

## Success Metrics

### Validation Passes If:
- ✅ All 5 users can login successfully
- ✅ Animal management page loads with real data
- ✅ Family dialog opens, accepts input, and persists to DynamoDB
- ✅ Chat messages send and receive AI responses
- ✅ Conversation history displays correctly
- ✅ All API response times < 2 seconds
- ✅ No console errors or warnings
- ✅ Teams notification delivers successfully with proper formatting

### Validation Fails If:
- ❌ Any service fails to start
- ❌ >20% of users cannot login
- ❌ Critical features completely broken (chat, family creation)
- ❌ DynamoDB persistence failures
- ❌ Multiple console errors
- ❌ Performance >5 seconds for any operation

## Advanced Techniques

### Debugging Failed Tests
```javascript
// Capture full page state
mcp__playwright__browser_snapshot() // Shows all elements

// Check console for errors
mcp__playwright__browser_console_messages({ onlyErrors: true })

// Check network for failed requests
mcp__playwright__browser_network_requests()

// Take full page screenshot
mcp__playwright__browser_take_screenshot({ fullPage: true })
```

### Mobile Viewport Testing
```javascript
// Resize to mobile viewport
mcp__playwright__browser_resize({ width: 375, height: 667 }) // iPhone size

// Run tests
// ...

// Resize back to desktop
mcp__playwright__browser_resize({ width: 1280, height: 720 })
```

### Form Validation Testing
```javascript
// Try to submit empty form
mcp__playwright__browser_click({ element: 'Submit', ref: '[ref]' })

// Check for validation errors
mcp__playwright__browser_snapshot()
// Should see error messages

// Fill required fields only
mcp__playwright__browser_fill_form({
  fields: [
    { name: 'Family Name', type: 'textbox', ref: '[ref]', value: 'Test' }
  ]
})

// Try submit again
mcp__playwright__browser_click({ element: 'Submit', ref: '[ref]' })
// Should succeed or show remaining validation errors
```

## References
- [TEAMS-WEBHOOK-ADVICE.md](/Users/keithstegbauer/repositories/CMZ-chatbots/TEAMS-WEBHOOK-ADVICE.md) - **MUST READ before Step 10**
- [Playwright MCP Documentation](https://github.com/executeautomation/playwright-mcp-server)
- [Microsoft Adaptive Cards](https://adaptivecards.io/)
- [Adaptive Card Designer](https://adaptivecards.io/designer/)

## Lessons Learned

### From Production Runs
1. **Always read TEAMS-WEBHOOK-ADVICE.md** - Most common failure is wrong message format
2. **Wait for chat connection** - Input disabled until WebSocket/connection established
3. **Sequential user testing** - Parallel logins cause state management issues
4. **DynamoDB eventual consistency** - Wait 1-2 seconds before querying
5. **Screenshot everything** - Evidence is critical for debugging failures
6. **Service health first** - Never skip Step 0 health checks
7. **Visible browser required** - User needs to see validation happening
8. **Network timing varies** - ChatGPT can take 10+ seconds, use generous timeouts

### Best Practices Discovered
- Take screenshots BEFORE and AFTER each major action
- Use `browser_console_messages` proactively to catch JavaScript errors early
- Verify DynamoDB persistence immediately after UI operations
- Test error cases (invalid login, empty forms) not just happy paths
- Keep Teams notification short and focused - use FactSet for structured data
- Save validation evidence in organized directory structure
