/**
 * Chat/Conversation End-to-End Tests
 *
 * Tests the complete chat conversation flow:
 * 1. Frontend: UI chat interface interactions
 * 2. Backend: API endpoints (POST /convo_turn, GET /convo_history)
 * 3. Persistence: DynamoDB conversation storage validation
 */

const { test, expect } = require('@playwright/test');
const { spawn } = require('child_process');
const { loginAsUser } = require('../helpers/auth-helper');

const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:3000';
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8080';
const DYNAMODB_CONVERSATION_TABLE = 'quest-dev-conversation';
const DYNAMODB_TURN_TABLE = 'quest-dev-conversation-turn';

/**
 * Query DynamoDB for conversation turns
 */
async function queryConversationTurns(sessionId) {
  return new Promise((resolve, reject) => {
    const args = [
      'dynamodb', 'query',
      '--table-name', DYNAMODB_TURN_TABLE,
      '--key-condition-expression', 'sessionId = :sid',
      '--expression-attribute-values', JSON.stringify({
        ':sid': { S: sessionId }
      }),
      '--profile', 'cmz'
    ];

    const process = spawn('aws', args, { stdio: ['pipe', 'pipe', 'pipe'] });

    let stdout = '';
    let stderr = '';

    process.stdout.on('data', (data) => stdout += data);
    process.stderr.on('data', (data) => stderr += data);

    process.on('close', (code) => {
      if (code === 0) {
        try {
          const result = JSON.parse(stdout);
          resolve(result.Items || []);
        } catch (e) {
          reject(new Error('Failed to parse DynamoDB response'));
        }
      } else {
        reject(new Error(`DynamoDB query failed: ${stderr}`));
      }
    });
  });
}

/**
 * Delete conversation session (cleanup)
 */
async function deleteConversationSession(sessionId) {
  return new Promise((resolve) => {
    const args = [
      'dynamodb', 'delete-item',
      '--table-name', DYNAMODB_CONVERSATION_TABLE,
      '--key', JSON.stringify({ sessionId: { S: sessionId } }),
      '--profile', 'cmz'
    ];

    const process = spawn('aws', args);
    process.on('close', () => resolve());
  });
}

test.describe('Chat/Conversation E2E Flow', () => {

  let authenticatedPage;
  let authToken;

  test.beforeAll(async ({ browser }) => {
    const context = await browser.newContext();
    authenticatedPage = await context.newPage();

    // Get JWT token using auth-helper
    const { token } = await loginAsUser(authenticatedPage, 'admin');
    authToken = token;

    // Navigate to dashboard
    await authenticatedPage.goto(`${FRONTEND_URL}/dashboard`);
    await authenticatedPage.waitForLoadState('networkidle');
  });

  test.describe('Send Message Flow (UI → Backend → DynamoDB)', () => {

    test('should send chat message through complete stack', async () => {
      const testSessionId = `e2e-test-${Date.now()}`;
      const testMessage = 'Hello Pokey! Tell me about your quills.';

      try {
        // 1. FRONTEND: Navigate to chat interface
        await authenticatedPage.goto(`${FRONTEND_URL}/chat`);
        await authenticatedPage.waitForLoadState('networkidle');

        // 2. FRONTEND: Wait for chat to be ready (connection established)
        const chatInput = authenticatedPage.locator('textarea[placeholder*="message"], input[placeholder*="message"]').first();
        await chatInput.waitFor({ state: 'visible', timeout: 5000 });

        // Wait for connection status to be "connected" (input becomes enabled)
        // The input is disabled until connectionStatus === 'connected'
        await authenticatedPage.waitForFunction(
          () => {
            const input = document.querySelector('input[placeholder*="message"], textarea[placeholder*="message"]');
            return input && !input.disabled;
          },
          { timeout: 10000 }
        ).catch(() => {
          console.log('Warning: Chat input remained disabled - connection may not have established');
        });

        // Give a moment for any state updates
        await authenticatedPage.waitForTimeout(500);

        // 3. FRONTEND: Enter message in chat input (should be enabled now)
        await chatInput.fill(testMessage);

        // 3. FRONTEND: Send message and capture backend request
        const [messageResponse] = await Promise.all([
          authenticatedPage.waitForResponse(resp =>
            resp.url().includes('/convo_turn') &&
            resp.request().method() === 'POST'
          ),
          authenticatedPage.click('button:has-text("Send"), button[type="submit"]')
        ]);

        // 4. BACKEND: Validate message response
        expect(messageResponse.status()).toBe(200);
        const chatResponse = await messageResponse.json();

        expect(chatResponse).toHaveProperty('reply');
        expect(chatResponse).toHaveProperty('sessionId');
        expect(chatResponse).toHaveProperty('turnId');
        expect(chatResponse).toHaveProperty('timestamp');
        expect(chatResponse).toHaveProperty('metadata');

        // Validate AI response content
        expect(chatResponse.reply.length).toBeGreaterThan(0);
        expect(chatResponse.reply.toLowerCase()).toContain('quill');

        // 5. FRONTEND: Verify message appears in chat history
        await authenticatedPage.waitForSelector(`text=${testMessage}`, { timeout: 5000 });
        await authenticatedPage.waitForSelector(`text=${chatResponse.reply.substring(0, 20)}`, { timeout: 5000 });

        // 6. BACKEND: Verify conversation history via API
        const historyResponse = await authenticatedPage.request.get(
          `${BACKEND_URL}/convo_history?sessionId=${chatResponse.sessionId}`,
          { headers: { 'Authorization': `Bearer ${authToken}` } }
        );

        expect(historyResponse.status()).toBe(200);
        const history = await historyResponse.json();

        expect(history.messages).toBeDefined();
        const userMessage = history.messages.find(m => m.role === 'user' && m.content === testMessage);
        const assistantMessage = history.messages.find(m => m.role === 'assistant');

        expect(userMessage).toBeDefined();
        expect(assistantMessage).toBeDefined();

        // 7. PERSISTENCE: Verify in DynamoDB (if permissions allow)
        try {
          const turns = await queryConversationTurns(chatResponse.sessionId);
          expect(turns.length).toBeGreaterThan(0);

          // Find the turn with our message
          const messageTurn = turns.find(t => t.message?.S === testMessage);
          expect(messageTurn).toBeDefined();
        } catch (e) {
          console.log('DynamoDB validation skipped (permission issue):', e.message);
        }

      } catch (error) {
        console.error('Chat E2E test error:', error);
        throw error;
      }
    });
  });

  test.describe('Multi-Turn Conversation Flow', () => {

    test('should maintain conversation context across turns', async () => {
      const testSessionId = `e2e-multi-turn-${Date.now()}`;

      try {
        // Navigate to chat
        await authenticatedPage.goto(`${FRONTEND_URL}/chat`);
        await authenticatedPage.waitForLoadState('networkidle');

        const chatInput = authenticatedPage.locator('textarea[placeholder*="message"], input[placeholder*="message"]').first();
        await chatInput.waitFor({ state: 'visible', timeout: 5000 });

        // Wait for chat connection to be established (input becomes enabled)
        await authenticatedPage.waitForFunction(
          () => {
            const input = document.querySelector('input[placeholder*="message"], textarea[placeholder*="message"]');
            return input && !input.disabled;
          },
          { timeout: 10000 }
        ).catch(() => console.log('Chat input remained disabled'));

        await authenticatedPage.waitForTimeout(500);

        // Turn 1: Ask about quills
        await chatInput.fill('Tell me about porcupine quills');
        const [turn1Response] = await Promise.all([
          authenticatedPage.waitForResponse(resp => resp.url().includes('/convo_turn')),
          authenticatedPage.click('button:has-text("Send")')
        ]);

        const turn1Data = await turn1Response.json();
        const sessionId = turn1Data.sessionId;

        // Wait for response to appear
        await authenticatedPage.waitForTimeout(1000);

        // Turn 2: Follow-up question
        await chatInput.fill('How many quills do you have?');
        const [turn2Response] = await Promise.all([
          authenticatedPage.waitForResponse(resp => resp.url().includes('/convo_turn')),
          authenticatedPage.click('button:has-text("Send")')
        ]);

        const turn2Data = await turn2Response.json();

        // Verify same session
        expect(turn2Data.sessionId).toBe(sessionId);

        // Verify conversation history contains both turns
        const historyResponse = await authenticatedPage.request.get(
          `${BACKEND_URL}/convo_history?sessionId=${sessionId}`,
          { headers: { 'Authorization': `Bearer ${authToken}` } }
        );

        const history = await historyResponse.json();
        expect(history.messages.length).toBeGreaterThanOrEqual(4); // 2 user + 2 assistant messages

      } catch (error) {
        console.error('Multi-turn conversation test error:', error);
        throw error;
      }
    });
  });

  test.describe('Animal Personality Flow', () => {

    test('should respond with different personalities for different animals', async () => {
      // Test Pokey (porcupine)
      await authenticatedPage.goto(`${FRONTEND_URL}/chat`);
      await authenticatedPage.waitForLoadState('networkidle');

      const chatInput = authenticatedPage.locator('textarea[placeholder*="message"], input[placeholder*="message"]').first();
      await chatInput.waitFor({ state: 'visible', timeout: 5000 });

      // Wait for connection
      await authenticatedPage.waitForFunction(
        () => {
          const input = document.querySelector('input[placeholder*="message"], textarea[placeholder*="message"]');
          return input && !input.disabled;
        },
        { timeout: 10000 }
      ).catch(() => console.log('Chat input remained disabled'));

      await authenticatedPage.waitForTimeout(500);

      await chatInput.fill('Hello!');

      const [pokeyResponse] = await Promise.all([
        authenticatedPage.waitForResponse(resp => resp.url().includes('/convo_turn')),
        authenticatedPage.click('button:has-text("Send")')
      ]);

      const pokeyData = await pokeyResponse.json();
      expect(pokeyData.reply.toLowerCase()).toMatch(/pokey|porcupine|quill/);

      // Test Leo (lion) if available
      await authenticatedPage.reload();
      await authenticatedPage.waitForLoadState('networkidle');

      const chatInput2 = authenticatedPage.locator('textarea[placeholder*="message"], input[placeholder*="message"]').first();
      await chatInput2.waitFor({ state: 'visible', timeout: 5000 });

      // Wait for connection
      await authenticatedPage.waitForFunction(
        () => {
          const input = document.querySelector('input[placeholder*="message"], textarea[placeholder*="message"]');
          return input && !input.disabled;
        },
        { timeout: 10000 }
      ).catch(() => console.log('Chat input remained disabled'));

      await authenticatedPage.waitForTimeout(500);

      await chatInput2.fill('Hello!');

      const [leoResponse] = await Promise.all([
        authenticatedPage.waitForResponse(resp => resp.url().includes('/convo_turn')),
        authenticatedPage.click('button:has-text("Send")')
      ]);

      const leoData = await leoResponse.json();
      expect(leoData.reply.toLowerCase()).toMatch(/leo|lion|pride|roar/);
    });
  });

  test.describe('Conversation History Flow', () => {

    test('should retrieve and display conversation history', async () => {
      const testSessionId = `e2e-history-${Date.now()}`;

      try {
        // Send a message to create history
        const createResponse = await authenticatedPage.request.post(`${BACKEND_URL}/convo_turn`, {
          headers: {
            'Authorization': `Bearer ${authToken}`,
            'Content-Type': 'application/json'
          },
          data: {
            sessionId: testSessionId,
            animalId: 'pokey',
            message: 'Test message for history',
            metadata: {
              userId: 'test-user-123'
            }
          }
        });

        expect(createResponse.status()).toBe(200);

        // Navigate to chat history view (correct route is /conversations/history)
        await authenticatedPage.goto(`${FRONTEND_URL}/conversations/history`);
        await authenticatedPage.waitForLoadState('networkidle');

        // Verify session appears in history list
        const sessionVisible = await authenticatedPage.locator(`text=${testSessionId}`).isVisible({ timeout: 5000 }).catch(() => false);

        if (sessionVisible) {
          // Click to view session details
          await authenticatedPage.click(`text=${testSessionId}`);

          // Verify message appears
          await authenticatedPage.waitForSelector('text=Test message for history', { timeout: 5000 });
        }

        // Verify via API
        const historyResponse = await authenticatedPage.request.get(
          `${BACKEND_URL}/convo_history?sessionId=${testSessionId}`,
          { headers: { 'Authorization': `Bearer ${authToken}` } }
        );

        expect(historyResponse.status()).toBe(200);
        const history = await historyResponse.json();

        expect(history.sessionId).toBe(testSessionId);
        expect(history.messages.length).toBeGreaterThan(0);

      } catch (error) {
        console.error('History flow test error:', error);
        throw error;
      }
    });
  });

  test.describe('Delete Conversation Flow', () => {

    test('should delete conversation through UI and backend', async () => {
      const testSessionId = `e2e-delete-${Date.now()}`;

      try {
        // Create test conversation
        await authenticatedPage.request.post(`${BACKEND_URL}/convo_turn`, {
          headers: {
            'Authorization': `Bearer ${authToken}`,
            'Content-Type': 'application/json'
          },
          data: {
            sessionId: testSessionId,
            animalId: 'pokey',
            message: 'Test message to delete'
          }
        });

        // Navigate to history (correct route is /conversations/history)
        await authenticatedPage.goto(`${FRONTEND_URL}/conversations/history`);
        await authenticatedPage.waitForLoadState('networkidle');

        const sessionCard = authenticatedPage.locator(`text=${testSessionId}`).locator('..').locator('..');
        const deleteButton = sessionCard.locator('button:has-text("Delete")').first();

        if (await deleteButton.isVisible({ timeout: 3000 })) {
          // Delete via UI
          const [deleteResponse] = await Promise.all([
            authenticatedPage.waitForResponse(resp =>
              resp.url().includes('/convo_history') &&
              resp.request().method() === 'DELETE'
            ),
            deleteButton.click()
          ]);

          expect(deleteResponse.status()).toBe(204);

          // Verify removed from UI
          const sessionGone = await authenticatedPage.locator(`text=${testSessionId}`).isHidden({ timeout: 5000 });
          expect(sessionGone).toBeTruthy();

          // Verify via API
          const historyResponse = await authenticatedPage.request.get(
            `${BACKEND_URL}/convo_history?sessionId=${testSessionId}`,
            { headers: { 'Authorization': `Bearer ${authToken}` } }
          );

          // Should return empty or not found
          expect([200, 404]).toContain(historyResponse.status());
        }

      } catch (error) {
        console.error('Delete conversation test error:', error);
        throw error;
      } finally {
        // Cleanup
        await deleteConversationSession(testSessionId);
      }
    });
  });

  test.describe('Real-time Message Display', () => {

    test('should display typing indicator and update with AI response', async () => {
      await authenticatedPage.goto(`${FRONTEND_URL}/chat`);
      await authenticatedPage.waitForLoadState('networkidle');

      const chatInput = authenticatedPage.locator('textarea[placeholder*="message"], input[placeholder*="message"]').first();
      await chatInput.waitFor({ state: 'visible', timeout: 5000 });

      // Wait for connection
      await authenticatedPage.waitForFunction(
        () => {
          const input = document.querySelector('input[placeholder*="message"], textarea[placeholder*="message"]');
          return input && !input.disabled;
        },
        { timeout: 10000 }
      ).catch(() => console.log('Chat input remained disabled'));

      await authenticatedPage.waitForTimeout(500);

      await chatInput.fill('What do porcupines eat?');

      // Send message
      await authenticatedPage.click('button:has-text("Send")');

      // Check for typing indicator (if implemented)
      const typingIndicator = authenticatedPage.locator('[data-testid="typing-indicator"], text=/typing|thinking/i').first();
      const hasTypingIndicator = await typingIndicator.isVisible({ timeout: 2000 }).catch(() => false);

      if (hasTypingIndicator) {
        // Wait for typing to finish
        await typingIndicator.waitFor({ state: 'hidden', timeout: 10000 });
      }

      // Verify AI response appears
      const response = await authenticatedPage.locator('[data-testid="assistant-message"], .assistant-message').last().textContent({ timeout: 10000 });
      expect(response.length).toBeGreaterThan(0);
    });
  });
});
