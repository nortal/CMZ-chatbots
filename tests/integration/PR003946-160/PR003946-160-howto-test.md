# Test Instructions: Frontend Real-time Chat Streaming UI Support

## Ticket Information
- **Ticket**: PR003946-160
- **Type**: Task
- **Priority**: Highest
- **Component**: Integration

## Test Objective
Validate backend support for frontend real-time chat streaming including SSE endpoints, event protocols, and response formatting.

## Prerequisites
- [ ] Backend services running on localhost:8080
- [ ] Frontend development server (localhost:3001)
- [ ] Browser with EventSource support
- [ ] Network tools for monitoring SSE
- [ ] Environment variables loaded from .env.local

## Test Steps (Sequential Execution Required)

### 1. Setup Phase
- Verify SSE endpoint accessibility
- Configure CORS for frontend access
- Prepare test client (browser or script)

### 2. Execution Phase
- Test streaming endpoint with stream flag
- Verify event protocol compliance
- Test non-streaming fallback
- Validate response format for UI
- Test connection management

### 3. Validation Phase
- Verify events receivable by browser
- Check response format matches UI needs
- Validate error handling for frontend
- Confirm reconnection support
- Test performance under load

## Pass/Fail Criteria

### ✅ PASS Conditions:
- [ ] SSE endpoint accessible from frontend origin
- [ ] Events formatted for EventSource API
- [ ] Stream and non-stream modes work
- [ ] Response format matches frontend expectations
- [ ] CORS headers properly configured

### ❌ FAIL Conditions:
- [ ] CORS blocks frontend requests
- [ ] Events not parseable by EventSource
- [ ] Connection drops without recovery
- [ ] Response format incompatible with UI
- [ ] Missing required event types

## Substeps and Multiple Test Scenarios

### Substep 1: Test Streaming Mode
- **Test**: POST with stream=true flag
- **Expected**: SSE response with proper headers
- **Pass Criteria**: Browser EventSource receives events

### Substep 2: Test Non-Streaming Mode
- **Test**: POST without stream flag
- **Expected**: Complete JSON response
- **Pass Criteria**: Response usable by frontend

### Substep 3: Test Event Protocol
- **Test**: Monitor SSE event types
- **Expected**: metadata, message, complete, error events
- **Pass Criteria**: All event types properly formatted

### Substep 4: Test CORS Support
- **Test**: Cross-origin request from frontend
- **Expected**: Request succeeds with CORS headers
- **Pass Criteria**: No CORS errors in browser

## Evidence Collection
- Browser console showing EventSource events
- Network tab showing SSE connection
- Response headers with CORS settings
- Event timeline with all types
- Performance metrics

## Sequential Reasoning Checkpoints
- **Pre-Test Prediction**: Backend should support both streaming modes
- **Expected Outcome**: Frontend can consume real-time events
- **Variance Analysis**: Document browser compatibility issues
- **Root Cause Assessment**: Analyze any frontend integration failures

## Test Commands
```javascript
// Browser JavaScript test
const eventSource = new EventSource('http://localhost:8080/convo_turn_stream');

eventSource.addEventListener('metadata', (e) => {
    console.log('Metadata:', JSON.parse(e.data));
});

eventSource.addEventListener('message', (e) => {
    console.log('Message chunk:', JSON.parse(e.data));
});

eventSource.addEventListener('complete', (e) => {
    console.log('Complete:', JSON.parse(e.data));
    eventSource.close();
});

eventSource.addEventListener('error', (e) => {
    console.error('Error:', e);
});

// Send initial message to trigger streaming
fetch('http://localhost:8080/convo_turn', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        message: 'Hello!',
        animalId: 'lion_001',
        stream: true
    })
});
```

## React Component Test
```jsx
// Frontend integration test component
import React, { useState, useEffect } from 'react';

function ChatStreamTest() {
    const [messages, setMessages] = useState([]);
    const [streaming, setStreaming] = useState(false);

    const startStream = async () => {
        setStreaming(true);
        const eventSource = new EventSource(
            'http://localhost:8080/convo_turn_stream'
        );

        let currentMessage = '';

        eventSource.addEventListener('message', (e) => {
            const data = JSON.parse(e.data);
            currentMessage += data.content;
            setMessages(prev => [...prev.slice(0, -1), currentMessage]);
        });

        eventSource.addEventListener('complete', (e) => {
            setStreaming(false);
            eventSource.close();
        });
    };

    return (
        <div>
            <button onClick={startStream} disabled={streaming}>
                Start Chat
            </button>
            <div>
                {messages.map((msg, idx) => (
                    <p key={idx}>{msg}</p>
                ))}
            </div>
        </div>
    );
}
```

## Troubleshooting
### Common Issues and Solutions

**Issue**: CORS errors in browser
- **Solution**: Ensure Access-Control-Allow-Origin header set
- **Check**: Backend returns proper CORS headers

**Issue**: EventSource connection fails
- **Solution**: Verify text/event-stream content type
- **Check**: Response headers in network tab

**Issue**: Events not received
- **Solution**: Check event formatting (data: prefix, double newline)
- **Check**: Use curl to inspect raw response

**Issue**: Connection keeps dropping
- **Solution**: Implement reconnection logic
- **Check**: Server timeout settings

---
*Generated: 2025-09-18*
*Test Category: Integration*
*CMZ TDD Framework v1.0*