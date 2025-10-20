# Test Instructions: Backend Response Streaming with Server-Sent Events

## Ticket Information
- **Ticket**: PR003946-158
- **Type**: Task
- **Priority**: Highest
- **Component**: Integration

## Test Objective
Validate Server-Sent Events (SSE) implementation for real-time streaming of chat responses with proper event formatting and Flask integration.

## Prerequisites
- [ ] Backend services running on localhost:8080
- [ ] Flask application with SSE support
- [ ] curl or EventSource client for testing
- [ ] Python environment with asyncio support
- [ ] Environment variables loaded from .env.local

## Test Steps (Sequential Execution Required)

### 1. Setup Phase
- Verify Flask SSE endpoint configuration
- Prepare SSE client for testing
- Set up event monitoring tools

### 2. Execution Phase
- Test SSE event formatting
- Verify streaming chat responses
- Test typing indicators
- Validate conversation history streaming
- Test error event handling

### 3. Validation Phase
- Verify SSE format compliance
- Check event types and data structure
- Validate streaming performance
- Confirm proper connection handling
- Test reconnection behavior

## Pass/Fail Criteria

### ✅ PASS Conditions:
- [ ] SSE events properly formatted with data/event/id fields
- [ ] Chat responses stream in real-time chunks
- [ ] Typing indicators sent correctly
- [ ] Error events handle failures gracefully
- [ ] Flask Response headers set correctly

### ❌ FAIL Conditions:
- [ ] Malformed SSE events break client
- [ ] Streaming chunks arrive out of order
- [ ] Connection drops without proper closure
- [ ] Missing CORS or cache headers
- [ ] Events not properly terminated with newlines

## Substeps and Multiple Test Scenarios

### Substep 1: Test SSE Format
- **Test**: Generate SSE formatted events
- **Expected**: Proper data:, event:, id: fields with double newline
- **Pass Criteria**: Client can parse events correctly

### Substep 2: Stream Chat Response
- **Test**: Stream multi-chunk response via SSE
- **Expected**: metadata → message chunks → complete event
- **Pass Criteria**: Full response assembled correctly

### Substep 3: Test Typing Indicator
- **Test**: Send typing start/stop events
- **Expected**: Typing events with status field
- **Pass Criteria**: Duration and timing correct

### Substep 4: Test Error Handling
- **Test**: Simulate streaming error
- **Expected**: Error event with details
- **Pass Criteria**: Client receives error gracefully

## Evidence Collection
- SSE event format examples
- Streaming response timeline
- Network traffic showing chunked transfer
- Error event examples
- Performance metrics (chunk timing)

## Sequential Reasoning Checkpoints
- **Pre-Test Prediction**: SSE should handle all streaming scenarios
- **Expected Outcome**: Real-time streaming with proper event structure
- **Variance Analysis**: Document streaming performance variations
- **Root Cause Assessment**: Analyze any connection failures

## Test Commands
```bash
# Test SSE endpoint with curl
curl -N -H "Accept: text/event-stream" \
  http://localhost:8080/convo_turn_stream \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "animalId": "lion_001", "stream": true}'

# Python test client
import requests
import sseclient

response = requests.post(
    'http://localhost:8080/convo_turn_stream',
    json={'message': 'Hello!', 'animalId': 'lion_001', 'stream': True},
    stream=True,
    headers={'Accept': 'text/event-stream'}
)

client = sseclient.SSEClient(response)
for event in client.events():
    print(f"Event: {event.event}, Data: {event.data}")
```

## Python Unit Test
```python
from openapi_server.impl.streaming_response import SSEStreamer

# Test SSE formatting
streamer = SSEStreamer()
formatted = streamer.format_sse(
    data='{"content": "Hello"}',
    event='message',
    id='123'
)
assert 'event: message\n' in formatted
assert 'data: {"content": "Hello"}\n' in formatted
assert formatted.endswith('\n\n')

# Test streaming generator
async def test_stream():
    async def mock_generator():
        yield "Hello "
        yield "World!"

    result = []
    async for event in streamer.stream_chat_response(
        mock_generator(),
        'session123',
        'lion_001'
    ):
        result.append(event)

    # Should have metadata, content chunks, and complete events
    assert any('metadata' in e for e in result)
    assert any('complete' in e for e in result)
```

## Troubleshooting
### Common Issues and Solutions

**Issue**: Connection drops immediately
- **Solution**: Check Flask Response headers (Cache-Control, X-Accel-Buffering)
- **Check**: Verify no proxy buffering interfering

**Issue**: Events not received by client
- **Solution**: Ensure double newline after each event
- **Check**: Use network inspector to see raw response

**Issue**: CORS errors in browser
- **Solution**: Add Access-Control-Allow-Origin header
- **Check**: Verify CORS configuration for production

---
*Generated: 2025-09-18*
*Test Category: Integration*
*CMZ TDD Framework v1.0*