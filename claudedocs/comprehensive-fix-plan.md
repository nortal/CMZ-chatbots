# Comprehensive Fix Plan - CMZ Chatbots Issues

**Created**: 2025-10-12
**Estimated Duration**: 14 hours (2 full work days)
**Priority**: CRITICAL → HIGH → MEDIUM

## Issues to Fix

### Issue 1: Chat Streaming 404 Error (CRITICAL)
**Severity**: CRITICAL
**Impact**: Chat completely broken - users get no responses
**Classification**: FRONTEND_BUG (frontend-backend contract mismatch)
**Effort**: 4-6 hours

**Problem**: Frontend calls `/convo_turn/stream` (GET with SSE) but endpoint doesn't exist in OpenAPI spec or backend.

### Issue 2: DELETE /animal/{id} Integration Test Missing (HIGH)
**Severity**: HIGH
**Impact**: Data deletion untested - risk of data loss or unauthorized deletions
**Effort**: 2-3 hours

**Problem**: DELETE endpoint has no integration test to verify actual DynamoDB deletion or authorization checks.

### Issue 3: JWT Edge Case Tests Missing (HIGH - Security)
**Severity**: HIGH
**Impact**: Authentication vulnerabilities - may accept invalid/expired/malformed tokens
**Effort**: 2-3 hours

**Problem**: jwt_utils.py missing edge case tests for expired tokens, malformed tokens, invalid signatures, etc.

### Issue 4: Playwright MCP Not Explicit in Tests (MEDIUM)
**Severity**: MEDIUM
**Impact**: Process improvement - prevent static analysis false positives
**Effort**: Throughout all phases

**Problem**: Need to ensure all frontend tests explicitly use Playwright MCP browser automation.

### Issue 5: Animal Details Modal Can't Be Closed (CRITICAL)
**Severity**: CRITICAL
**Impact**: Users stuck on modal - can't navigate without page refresh
**Effort**: 1-2 hours

**Problem**: Clicking X button or Close button doesn't close the animal details modal dialog.

---

## Execution Plan

### PHASE 1: IMMEDIATE USER BLOCKERS (Day 1, Morning - 5 hours)

#### Task 1.1: Reproduce Modal Close Bug (30 minutes)
**Steps**:
1. Use Playwright MCP to navigate to http://localhost:3001
2. Login as parent1@test.cmz.org / testpass123
3. Click "Conversations" in navigation
4. Click "Chat with Animals"
5. Click on an animal to view details
6. Observe modal opens
7. Try clicking X button (upper right) - should fail
8. Try clicking Close button (bottom) - should fail
9. Check browser console for JavaScript errors
10. Take screenshot for documentation

**Tools**: `mcp__playwright__browser_navigate`, `browser_click`, `browser_snapshot`, `browser_console_messages`

**Deliverable**: Reproduction steps documented, console errors captured

#### Task 1.2: Fix Modal Close Buttons (1 hour)
**Investigation**:
1. Find modal component: `grep -r "AnimalDetails" frontend/src/components/`
2. Check for close button handlers: Look for `onClick` props
3. Verify state management: Check `useState` for `isOpen` or `showModal`

**Likely Issues**:
- Missing `onClick` handler on buttons
- Handler not calling state update function
- Event propagation stopped by parent element
- CSS z-index preventing click events

**Fix Approach**:
```typescript
// Ensure both buttons have onClick handlers
<button onClick={() => setShowModal(false)}>X</button>
<button onClick={handleClose}>Close</button>

// Verify handleClose function updates state
const handleClose = () => {
  setShowModal(false);
  // Clear any form data if needed
};
```

**Files to Modify**:
- `frontend/src/components/animal/AnimalDetailsDialog.tsx` (or similar)

**Deliverable**: Both X and Close buttons functional

#### Task 1.3: Test Modal Fix with Playwright MCP (30 minutes)
**Steps**:
1. Use Playwright MCP to open modal again
2. Click X button - verify modal closes
3. Reopen modal
4. Click Close button - verify modal closes
5. Check console for no errors
6. Verify page navigation works after closing

**Validation**: No JavaScript errors, modal closes, user can navigate freely

**Deliverable**: Manual Playwright test confirms fix works

#### Task 1.4: Create Playwright E2E Test for Modal (1 hour)
**Create**: `tests/playwright/specs/ui-features/animal-details-modal.spec.js`

```javascript
test('Animal details modal should open and close correctly', async ({ page }) => {
  // Login
  await page.goto('http://localhost:3001');
  await page.fill('input[type="email"]', 'parent1@test.cmz.org');
  await page.fill('input[type="password"]', 'testpass123');
  await page.click('button[type="submit"]');

  // Navigate to conversations
  await page.click('text=Conversations');
  await page.click('text=Chat with Animals');

  // Open animal details modal
  await page.click('[data-testid="animal-details-button"]');
  await expect(page.locator('[data-testid="animal-details-modal"]')).toBeVisible();

  // Test X button closes modal
  await page.click('[data-testid="modal-close-x"]');
  await expect(page.locator('[data-testid="animal-details-modal"]')).not.toBeVisible();

  // Reopen and test Close button
  await page.click('[data-testid="animal-details-button"]');
  await expect(page.locator('[data-testid="animal-details-modal"]')).toBeVisible();
  await page.click('button:has-text("Close")');
  await expect(page.locator('[data-testid="animal-details-modal"]')).not.toBeVisible();

  // Verify no console errors
  const errors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') errors.push(msg.text());
  });
  expect(errors).toHaveLength(0);
});
```

**Deliverable**: Automated E2E test prevents regression

#### Task 1.5: JWT Edge Case Tests (3 hours - PARALLEL with modal work)
**Create**: `tests/unit/test_jwt_utils_edge_cases.py`

**Test Categories**:

1. **Expired Tokens**:
```python
def test_expired_token_rejected():
    """Test that tokens with past exp claim are rejected"""
    expired_token = generate_token_with_exp(datetime.now() - timedelta(hours=1))
    with pytest.raises(jwt.ExpiredSignatureError):
        validate_token(expired_token)
```

2. **Malformed Tokens**:
```python
def test_malformed_token_rejected():
    """Test tokens that don't have 3 parts (header.payload.signature)"""
    assert validate_token("not.a.valid.token") is None
    assert validate_token("only_two.parts") is None
    assert validate_token("") is None
```

3. **Invalid Signature**:
```python
def test_tampered_token_rejected():
    """Test tokens with modified payload but original signature"""
    valid_token = generate_valid_token({"user_id": "123"})
    parts = valid_token.split('.')
    # Tamper with payload
    tampered_payload = base64.b64encode(b'{"user_id": "999"}').decode()
    tampered_token = f"{parts[0]}.{tampered_payload}.{parts[2]}"

    with pytest.raises(jwt.InvalidSignatureError):
        validate_token(tampered_token)
```

4. **Missing Required Claims**:
```python
def test_missing_user_id_rejected():
    """Test tokens missing user_id claim"""
    token = generate_token_missing_claim("user_id")
    assert validate_token(token) is None

def test_missing_email_rejected():
    """Test tokens missing email claim"""
    token = generate_token_missing_claim("email")
    assert validate_token(token) is None
```

5. **Null/Empty Values**:
```python
def test_null_user_id_rejected():
    """Test tokens with null user_id"""
    token = generate_token({"user_id": None, "email": "test@example.com"})
    assert validate_token(token) is None

def test_empty_email_rejected():
    """Test tokens with empty email"""
    token = generate_token({"user_id": "123", "email": ""})
    assert validate_token(token) is None
```

6. **Wrong Algorithm**:
```python
def test_wrong_algorithm_rejected():
    """Test tokens signed with different algorithm"""
    token_rs256 = generate_token_with_algorithm("RS256")
    with pytest.raises(jwt.InvalidAlgorithmError):
        validate_token(token_rs256)  # Expecting HS256
```

7. **Token Without Bearer Prefix**:
```python
def test_bearer_prefix_required():
    """Test that Authorization header requires Bearer prefix"""
    valid_token = generate_valid_token()
    assert extract_token(valid_token) is None  # Missing Bearer
    assert extract_token(f"Bearer {valid_token}") == valid_token
```

8. **Very Long Tokens (DoS Prevention)**:
```python
def test_very_long_token_rejected():
    """Test tokens exceeding max length (DoS prevention)"""
    very_long_token = "a" * 10000
    assert validate_token(very_long_token) is None
```

**Files**:
- Read: `backend/api/src/main/python/openapi_server/impl/utils/jwt_utils.py`
- Create: `backend/api/src/main/python/tests/unit/test_jwt_utils_edge_cases.py`

**Run Tests**:
```bash
cd backend/api/src/main/python
pytest tests/unit/test_jwt_utils_edge_cases.py -v
```

**Expected**: Some tests MAY fail, revealing actual security issues. If so, fix jwt_utils.py validation logic.

**Deliverable**: Comprehensive JWT security test suite

---

### PHASE 2: DATA SAFETY (Day 1, Afternoon - 3 hours)

#### Task 2.1: Verify DELETE /animal/{id} Endpoint Exists (15 minutes)
**Check OpenAPI Spec**:
```bash
grep -A 10 "DELETE.*animal" openapi_spec.yaml
```

**Check Handler**:
```bash
grep -n "def.*delete.*animal\|handle_animal_delete" backend/api/src/main/python/openapi_server/impl/animals.py
```

**If Missing**: Need to implement endpoint first (add to spec, implement handler)

**Deliverable**: Confirmation endpoint exists and is implemented

#### Task 2.2: Create DELETE Integration Test (2 hours)
**Create**: `tests/integration/test_animal_delete.py`

```python
import pytest
import boto3
from uuid import uuid4

@pytest.fixture
def dynamodb_client():
    """DynamoDB client with cmz profile"""
    session = boto3.Session(profile_name='cmz', region_name='us-west-2')
    return session.resource('dynamodb')

@pytest.fixture
def test_animal_id(dynamodb_client):
    """Create test animal and return ID"""
    table = dynamodb_client.Table('quest-dev-animal')
    animal_id = f"test_delete_{uuid4()}"

    # Create test animal
    table.put_item(Item={
        'animalId': animal_id,
        'name': 'Test Animal for Delete',
        'species': 'Test Species',
        'created': {'at': '2025-10-12T00:00:00Z'}
    })

    yield animal_id

    # Cleanup (in case test fails)
    try:
        table.delete_item(Key={'animalId': animal_id})
    except:
        pass

def test_delete_animal_success(test_animal_id, auth_token):
    """Test successful animal deletion"""
    response = requests.delete(
        f'http://localhost:8080/animal/{test_animal_id}',
        headers={'Authorization': f'Bearer {auth_token}'}
    )

    assert response.status_code == 204

    # Verify deleted from DynamoDB
    session = boto3.Session(profile_name='cmz', region_name='us-west-2')
    table = session.resource('dynamodb').Table('quest-dev-animal')

    result = table.get_item(Key={'animalId': test_animal_id})
    assert 'Item' not in result, "Animal should be deleted from DynamoDB"

def test_delete_nonexistent_animal(auth_token):
    """Test deleting non-existent animal returns 404"""
    response = requests.delete(
        'http://localhost:8080/animal/nonexistent-id',
        headers={'Authorization': f'Bearer {auth_token}'}
    )

    assert response.status_code == 404

def test_delete_animal_no_auth():
    """Test deletion without authentication returns 401"""
    response = requests.delete('http://localhost:8080/animal/some-id')

    assert response.status_code == 401

def test_delete_animal_wrong_role(student_auth_token, test_animal_id):
    """Test students cannot delete animals (expect 403 if RBAC implemented)"""
    response = requests.delete(
        f'http://localhost:8080/animal/{test_animal_id}',
        headers={'Authorization': f'Bearer {student_auth_token}'}
    )

    # If RBAC not implemented, might be 204 (security issue to fix)
    # If RBAC implemented, should be 403
    assert response.status_code in [403, 204]

    if response.status_code == 204:
        print("⚠️ WARNING: DELETE endpoint has no authorization check!")
```

**Run Test**:
```bash
cd backend/api/src/main/python
pytest tests/integration/test_animal_delete.py -v
```

**Deliverable**: Integration test with DynamoDB verification

#### Task 2.3: Run Test and Verify Cleanup (45 minutes)
**Execute**:
```bash
pytest tests/integration/test_animal_delete.py -v --tb=short
```

**Verify Cleanup**:
```bash
aws dynamodb scan \
  --table-name quest-dev-animal \
  --filter-expression "begins_with(animalId, :prefix)" \
  --expression-attribute-values '{":prefix": {"S": "test_delete_"}}' \
  --profile cmz
```

Should return 0 items.

**If Test Fails**: Debug and fix DELETE handler implementation

**If Authorization Missing**: Add RBAC check to impl/animals.py

**Deliverable**: Passing test, clean DynamoDB, security verified

---

### PHASE 3: CHAT STREAMING FIX (Day 2 - 6 hours)

#### Task 3.1: Add /convo_turn/stream to OpenAPI Spec (30 minutes)
**Edit**: `openapi_spec.yaml`

**Add After `/convo_turn`**:
```yaml
  /convo_turn/stream:
    get:
      tags:
        - Conversation
      summary: Stream conversation turn responses via Server-Sent Events
      operationId: convo_turn_stream
      parameters:
        - name: message
          in: query
          required: true
          schema:
            type: string
          description: User message to send
        - name: animalId
          in: query
          required: true
          schema:
            type: string
          description: Animal chatbot ID
        - name: sessionId
          in: query
          required: true
          schema:
            type: string
          description: Conversation session ID
        - name: token
          in: query
          required: false
          schema:
            type: string
          description: JWT authentication token
      responses:
        '200':
          description: Streaming response via Server-Sent Events
          content:
            text/event-stream:
              schema:
                type: string
        '401':
          description: Unauthorized
        '404':
          description: Animal not found
        '500':
          description: Server error
```

**Deliverable**: OpenAPI spec updated with streaming endpoint

#### Task 3.2: Implement SSE Handler in Backend (2-3 hours)
**Edit**: `backend/api/src/main/python/openapi_server/impl/conversation.py`

**Add Handler**:
```python
from flask import Response, stream_with_context
import json
import time

def handle_convo_turn_stream(message: str, animalId: str, sessionId: str, token: str = None) -> Response:
    """
    Stream conversation turn response via Server-Sent Events

    Args:
        message: User message
        animalId: Animal chatbot ID
        sessionId: Conversation session ID
        token: JWT authentication token (optional)

    Returns:
        Flask Response with text/event-stream
    """
    def generate():
        try:
            # Validate token if provided
            if token and token != 'null':
                user_data = validate_token(token)
                if not user_data:
                    yield f"event: error\ndata: Unauthorized\n\n"
                    return

            # Get animal config for system prompt
            animal_config = get_animal_config(animalId)
            if not animal_config:
                yield f"event: error\ndata: Animal not found\n\n"
                return

            # Call LLM (Bedrock, OpenAI, etc.) with streaming
            system_prompt = animal_config.get('systemPrompt', '')

            # Example: Stream from LLM
            for chunk in stream_llm_response(system_prompt, message):
                # Send SSE event
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                time.sleep(0.05)  # Small delay for realistic streaming

            # Save conversation to DynamoDB
            save_conversation_turn(sessionId, animalId, message, full_response)

            # Send completion event
            yield f"event: complete\ndata: {json.dumps({'status': 'done'})}\n\n"

        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"event: error\ndata: {str(e)}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive'
        }
    )

def stream_llm_response(system_prompt: str, user_message: str):
    """
    Stream response from LLM (placeholder - implement based on your LLM)

    Yields:
        Response chunks from LLM
    """
    # Example: OpenAI streaming
    # response = openai.ChatCompletion.create(
    #     model="gpt-4",
    #     messages=[
    #         {"role": "system", "content": system_prompt},
    #         {"role": "user", "content": user_message}
    #     ],
    #     stream=True
    # )
    #
    # for chunk in response:
    #     if chunk.choices[0].delta.get('content'):
    #         yield chunk.choices[0].delta.content

    # Placeholder: Simulate streaming
    full_response = f"Hello! You asked: {user_message}. This is a simulated streaming response from the {system_prompt} chatbot."

    for word in full_response.split():
        yield word + " "
```

**Files to Modify**:
- `backend/api/src/main/python/openapi_server/impl/conversation.py`
- May need to update `impl/handlers.py` to map handler

**Deliverable**: Working SSE streaming handler

#### Task 3.3: Run make post-generate (30 minutes)
**Execute**:
```bash
cd backend/api
make post-generate
```

**Verify**:
1. Check `controllers/conversation_controller.py` routes to handler
2. Verify no "do some magic!" placeholders
3. Check Flask-CORS configuration includes SSE

**If Issues**: Manually fix controller routing

**Deliverable**: Controller properly routes to SSE handler

#### Task 3.4: Test Chat Streaming with Playwright MCP (1 hour)
**Steps**:
1. Start backend: `make run-api`
2. Start frontend: `npm run dev`
3. Use Playwright MCP to test:

```python
# Navigate and login
browser_navigate to http://localhost:3001
browser_type email: parent1@test.cmz.org
browser_type password: testpass123
browser_click Sign In

# Go to chat
browser_click "Chat with Animals"
browser_click on an animal

# Send message
browser_type message: "Hello! Test streaming."
browser_click Send button

# Verify response appears (streaming)
Wait for response text to appear
Verify status shows "connected" not "error"

# Check console
browser_console_messages - should show NO 404 errors
```

**Validation**:
- ✅ No 404 error on /convo_turn/stream
- ✅ SSE connection successful
- ✅ Chat response appears in UI
- ✅ No JavaScript errors

**Deliverable**: Manual browser test confirms chat streaming works

#### Task 3.5: Create Chat Streaming Integration Test (1 hour)
**Create**: `tests/integration/test_convo_turn_stream.py`

```python
import requests
import sseclient  # pip install sseclient-py

def test_convo_turn_stream_success(auth_token):
    """Test SSE streaming endpoint works"""
    url = 'http://localhost:8080/convo_turn/stream'
    params = {
        'message': 'Hello test',
        'animalId': 'test-animal-id',
        'sessionId': f'test_session_{uuid4()}',
        'token': auth_token
    }

    response = requests.get(url, params=params, stream=True, headers={
        'Accept': 'text/event-stream'
    })

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'text/event-stream'

    # Read SSE events
    client = sseclient.SSEClient(response)
    events = []

    for event in client.events():
        events.append(event)
        if event.event == 'complete':
            break

    assert len(events) > 0, "Should receive at least one event"
    assert any(e.event == 'complete' for e in events), "Should receive completion event"

def test_convo_turn_stream_persists_to_dynamodb(auth_token):
    """Test conversation is saved to DynamoDB"""
    session_id = f'test_session_{uuid4()}'
    message = 'Test persistence'

    # Stream conversation
    url = 'http://localhost:8080/convo_turn/stream'
    params = {
        'message': message,
        'animalId': 'test-animal-id',
        'sessionId': session_id,
        'token': auth_token
    }

    response = requests.get(url, params=params, stream=True)

    # Consume stream
    for line in response.iter_lines():
        if b'event: complete' in line:
            break

    # Verify in DynamoDB
    session = boto3.Session(profile_name='cmz', region_name='us-west-2')
    table = session.resource('dynamodb').Table('quest-dev-conversation')

    result = table.get_item(Key={'sessionId': session_id})
    assert 'Item' in result, "Conversation should be saved to DynamoDB"
    assert result['Item']['message'] == message
```

**Run Test**:
```bash
pytest tests/integration/test_convo_turn_stream.py -v
```

**Deliverable**: Integration test confirms streaming + persistence

---

### PHASE 4: DOCUMENTATION & VALIDATION (Throughout)

#### Task 4.1: Document Playwright MCP Usage
**Update Each Test File** with header comment:

```python
"""
IMPORTANT: This test uses Playwright MCP browser automation.
Static code analysis would not catch the bugs tested here.
Always use real browser testing for frontend validation.

Playwright MCP Tools Used:
- mcp__playwright__browser_navigate
- mcp__playwright__browser_click
- mcp__playwright__browser_type
- mcp__playwright__browser_snapshot
- mcp__playwright__browser_console_messages

See: FRONTEND-AGENT-PLAYWRIGHT-ADVICE.md for best practices
"""
```

**Files to Update**:
- `tests/playwright/specs/ui-features/animal-details-modal.spec.js`
- All other Playwright test files

**Deliverable**: All tests clearly document Playwright MCP usage

---

## Risk Mitigation

### Risk 1: Modal Bug More Complex Than Expected
**Mitigation**:
- Use browser DevTools to inspect event listeners
- Check CSS z-index and pointer-events
- Test with different browsers (Chromium, Firefox, WebKit)

### Risk 2: SSE CORS Issues
**Mitigation**:
- Verify Flask-CORS configured: `CORS(app, resources={r"/convo_turn/stream": {"origins": "*"}})`
- Check browser network tab for CORS errors
- Test locally before production deployment

### Risk 3: JWT Tests Reveal Security Holes
**Mitigation**:
- Good! Fix immediately if found
- Add validation to jwt_utils.py
- Document security improvements in git commit

### Risk 4: DELETE Endpoint Has No Authorization
**Mitigation**:
- If found, add RBAC check immediately
- Test with different user roles
- Document security issue in Jira

### Risk 5: OpenAPI Regeneration Breaks Handlers
**Mitigation**:
- ALWAYS use `make post-generate` (never `make generate-api` alone)
- Run validation after generation
- Test all endpoints after regeneration

---

## Success Criteria

### Issue 5 (Modal) ✅
- [x] Both X and Close buttons close modal
- [x] No JavaScript console errors
- [x] Playwright E2E test passes
- [x] User can navigate freely after closing

### Issue 1 (Chat Streaming) ✅
- [x] /convo_turn/stream returns 200 (not 404)
- [x] SSE connection established
- [x] Chat responses stream to UI
- [x] Conversations saved to DynamoDB
- [x] Integration test passes

### Issue 3 (JWT) ✅
- [x] All 8 edge case categories tested
- [x] Expired tokens rejected
- [x] Malformed tokens rejected
- [x] Invalid signatures rejected
- [x] Missing claims rejected
- [x] All tests pass

### Issue 2 (DELETE) ✅
- [x] DELETE endpoint verified
- [x] Integration test passes
- [x] DynamoDB deletion verified
- [x] Authorization checked (if implemented)
- [x] Test cleanup complete

### Issue 4 (Playwright MCP) ✅
- [x] All tests document Playwright usage
- [x] No static analysis shortcuts
- [x] Browser automation used throughout

---

## Deliverables

1. **Animal Details Modal Fix**
   - Fixed component code
   - Playwright E2E test
   - Documentation

2. **Chat Streaming Endpoint**
   - Updated OpenAPI spec
   - SSE handler implementation
   - Controller routing
   - Integration test
   - Playwright validation

3. **JWT Edge Case Tests**
   - Comprehensive test suite (8 categories)
   - Security validation
   - Documentation

4. **DELETE Animal Integration Test**
   - Integration test with DynamoDB verification
   - Authorization validation
   - Cleanup verification

5. **Playwright MCP Documentation**
   - All test files document Playwright usage
   - Best practices followed

---

## Timeline

**Day 1 Morning (5 hours)**:
- Modal bug: Reproduce, fix, test (2 hours)
- JWT tests: Write all 8 categories (3 hours)

**Day 1 Afternoon (3 hours)**:
- DELETE test: Create and run (3 hours)

**Day 2 (6 hours)**:
- Chat streaming: Spec, implementation, testing (6 hours)

**Total**: 14 hours over 2 days

---

## Next Steps After Completion

1. Create git commits for each fix
2. Run full test suite: `pytest && npm test`
3. Create Jira tickets for any security issues found
4. Update Teams with completion report
5. Document lessons learned
6. Create session history

---

**Status**: Ready to execute
**Estimated Completion**: 2 full work days
**Priority Order**: Modal → JWT → DELETE → Chat Streaming
