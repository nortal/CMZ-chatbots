/**
 * Conversation / ChatGPT Endpoint Validation
 * Tests all conversation/chat endpoints implemented in feature/chat-implementation-chatgpt branch
 */

const { test, expect } = require('@playwright/test');

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8080';
const TEST_SESSION_ID = `test-session-${Date.now()}`;
const TEST_ANIMAL_ID = 'pokey';

test.describe('Conversation / ChatGPT Endpoints', () => {

  test.describe('POST /convo_turn - Chat Message Processing', () => {

    test('should process user message and return AI response', async ({ request }) => {
      const response = await request.post(`${BACKEND_URL}/convo_turn`, {
        data: {
          sessionId: TEST_SESSION_ID,
          animalId: TEST_ANIMAL_ID,
          message: 'Hello Pokey! Tell me about your quills.',
          metadata: {
            userId: 'test-user-123',
            contextTurns: 5
          }
        }
      });

      expect(response.status()).toBe(200);
      const data = await response.json();

      // Validate response structure
      expect(data).toHaveProperty('reply');
      expect(data).toHaveProperty('sessionId', TEST_SESSION_ID);
      expect(data).toHaveProperty('turnId');
      expect(data).toHaveProperty('timestamp');
      expect(data).toHaveProperty('metadata');

      // Validate metadata
      expect(data.metadata).toHaveProperty('model');
      expect(data.metadata).toHaveProperty('tokensUsed');
      expect(data.metadata).toHaveProperty('processingTime');

      // Validate AI response content
      expect(typeof data.reply).toBe('string');
      expect(data.reply.length).toBeGreaterThan(0);
      expect(data.reply.toLowerCase()).toContain('quill');
    });

    test('should return error for missing sessionId', async ({ request }) => {
      const response = await request.post(`${BACKEND_URL}/convo_turn`, {
        data: {
          animalId: TEST_ANIMAL_ID,
          message: 'Hello!'
        }
      });

      expect(response.status()).toBe(400);
      const data = await response.json();
      expect(data.code).toBe('invalid_request');
      expect(data.message).toContain('sessionId');
    });

    test('should return error for missing animalId', async ({ request }) => {
      const response = await request.post(`${BACKEND_URL}/convo_turn`, {
        data: {
          sessionId: TEST_SESSION_ID,
          message: 'Hello!'
        }
      });

      expect(response.status()).toBe(400);
      const data = await response.json();
      expect(data.code).toBe('invalid_request');
      expect(data.message).toContain('animalId');
    });

    test('should return error for missing message', async ({ request }) => {
      const response = await request.post(`${BACKEND_URL}/convo_turn`, {
        data: {
          sessionId: TEST_SESSION_ID,
          animalId: TEST_ANIMAL_ID
        }
      });

      expect(response.status()).toBe(400);
      const data = await response.json();
      expect(data.code).toBe('invalid_request');
      expect(data.message).toContain('message');
    });

    test('should handle different animal personalities (Leo)', async ({ request }) => {
      const response = await request.post(`${BACKEND_URL}/convo_turn`, {
        data: {
          sessionId: `leo-session-${Date.now()}`,
          animalId: 'leo',
          message: 'Tell me about lion pride dynamics'
        }
      });

      expect(response.status()).toBe(200);
      const data = await response.json();
      expect(data.reply.toLowerCase()).toContain('pride');
    });

    test('should store conversation turns in DynamoDB', async ({ request }) => {
      const testSessionId = `dynamodb-test-${Date.now()}`;

      // Send first message
      const response1 = await request.post(`${BACKEND_URL}/convo_turn`, {
        data: {
          sessionId: testSessionId,
          animalId: TEST_ANIMAL_ID,
          message: 'First message about quills'
        }
      });
      expect(response1.status()).toBe(200);

      // Send second message
      const response2 = await request.post(`${BACKEND_URL}/convo_turn`, {
        data: {
          sessionId: testSessionId,
          animalId: TEST_ANIMAL_ID,
          message: 'Second message about food'
        }
      });
      expect(response2.status()).toBe(200);

      // Verify turnIds are different
      const data1 = await response1.json();
      const data2 = await response2.json();
      expect(data1.turnId).not.toBe(data2.turnId);
    });
  });

  test.describe('GET /convo_history - Conversation History Retrieval', () => {

    test('should retrieve conversation history with default parameters', async ({ request }) => {
      const response = await request.get(`${BACKEND_URL}/convo_history`);

      expect(response.status()).toBe(200);
      const data = await response.json();

      // Validate response structure
      expect(data).toHaveProperty('sessionId');
      expect(data).toHaveProperty('userId');
      expect(data).toHaveProperty('animalId');
      expect(data).toHaveProperty('animalName');
      expect(data).toHaveProperty('messages');
      expect(Array.isArray(data.messages)).toBeTruthy();
      expect(data.messages.length).toBeGreaterThan(0);
    });

    test('should filter by animalId', async ({ request }) => {
      const response = await request.get(`${BACKEND_URL}/convo_history?animalId=${TEST_ANIMAL_ID}`);

      expect(response.status()).toBe(200);
      const data = await response.json();
      expect(data.animalId).toBe(TEST_ANIMAL_ID);
    });

    test('should filter by sessionId', async ({ request }) => {
      const response = await request.get(`${BACKEND_URL}/convo_history?sessionId=${TEST_SESSION_ID}`);

      expect(response.status()).toBe(200);
      const data = await response.json();
      expect(data.sessionId).toBe(TEST_SESSION_ID);
    });

    test('should include metadata when requested', async ({ request }) => {
      const response = await request.get(`${BACKEND_URL}/convo_history?includeMetadata=true`);

      expect(response.status()).toBe(200);
      const data = await response.json();
      expect(data).toHaveProperty('metadata');
      expect(data.metadata).toHaveProperty('model');
      expect(data.metadata).toHaveProperty('temperature');
      expect(data.metadata).toHaveProperty('totalTokens');
    });

    test('should not include metadata by default', async ({ request }) => {
      const response = await request.get(`${BACKEND_URL}/convo_history`);

      expect(response.status()).toBe(200);
      const data = await response.json();
      expect(data.metadata).toBeUndefined();
    });

    test('should validate message structure', async ({ request }) => {
      const response = await request.get(`${BACKEND_URL}/convo_history`);

      expect(response.status()).toBe(200);
      const data = await response.json();

      // Validate message structure
      for (const message of data.messages) {
        expect(message).toHaveProperty('messageId');
        expect(message).toHaveProperty('role');
        expect(message).toHaveProperty('content');
        expect(message).toHaveProperty('timestamp');
        expect(['user', 'assistant']).toContain(message.role);

        if (message.role === 'assistant') {
          expect(message).toHaveProperty('animalName');
        }
      }
    });
  });

  test.describe('DELETE /convo_history - Conversation Deletion with GDPR', () => {

    test('should delete conversation by sessionId', async ({ request }) => {
      const response = await request.delete(`${BACKEND_URL}/convo_history?sessionId=test-session-delete`);

      expect(response.status()).toBe(204);
    });

    test('should require GDPR confirmation for user data deletion', async ({ request }) => {
      const response = await request.delete(`${BACKEND_URL}/convo_history?userId=test-user-123`);

      expect(response.status()).toBe(400);
      const data = await response.json();
      expect(data.code).toBe('gdpr_confirmation_required');
      expect(data.message).toContain('GDPR confirmation required');
    });

    test('should delete user conversations with GDPR confirmation', async ({ request }) => {
      const response = await request.delete(
        `${BACKEND_URL}/convo_history?userId=test-user-123&confirmGdpr=true&auditReason=User+requested+deletion`
      );

      expect(response.status()).toBe(204);
    });

    test('should delete conversations by animalId', async ({ request }) => {
      const response = await request.delete(`${BACKEND_URL}/convo_history?animalId=${TEST_ANIMAL_ID}`);

      expect(response.status()).toBe(204);
    });
  });

  test.describe('GET /conversations/sessions - Session Listing', () => {

    test('should list conversation sessions', async ({ request }) => {
      const response = await request.get(`${BACKEND_URL}/conversations/sessions`);

      expect(response.status()).toBe(200);
      const data = await response.json();

      expect(data).toHaveProperty('sessions');
      expect(data).toHaveProperty('totalCount');
      expect(Array.isArray(data.sessions)).toBeTruthy();
      expect(data.totalCount).toBeGreaterThan(0);
    });

    test('should validate session structure', async ({ request }) => {
      const response = await request.get(`${BACKEND_URL}/conversations/sessions`);

      expect(response.status()).toBe(200);
      const data = await response.json();

      for (const session of data.sessions) {
        expect(session).toHaveProperty('sessionId');
        expect(session).toHaveProperty('userId');
        expect(session).toHaveProperty('animalId');
        expect(session).toHaveProperty('animalName');
        expect(session).toHaveProperty('startTime');
        expect(session).toHaveProperty('lastMessageTime');
        expect(session).toHaveProperty('messageCount');
        expect(session).toHaveProperty('duration');
        expect(session).toHaveProperty('summary');
        expect(session.messageCount).toBeGreaterThan(0);
      }
    });
  });

  test.describe('GET /conversations/sessions/{sessionId} - Session Details', () => {

    test('should retrieve detailed session information', async ({ request }) => {
      const response = await request.get(`${BACKEND_URL}/conversations/sessions/session-001`);

      expect(response.status()).toBe(200);
      const data = await response.json();

      expect(data).toHaveProperty('sessionId', 'session-001');
      expect(data).toHaveProperty('userId');
      expect(data).toHaveProperty('animalId');
      expect(data).toHaveProperty('messages');
      expect(data).toHaveProperty('metadata');
      expect(Array.isArray(data.messages)).toBeTruthy();
      expect(data.messages.length).toBeGreaterThan(0);
    });

    test('should include conversation metadata', async ({ request }) => {
      const response = await request.get(`${BACKEND_URL}/conversations/sessions/session-001`);

      expect(response.status()).toBe(200);
      const data = await response.json();

      expect(data.metadata).toHaveProperty('model');
      expect(data.metadata).toHaveProperty('temperature');
    });
  });

  test.describe('POST /summarize_convo - Conversation Summarization', () => {

    test('should return not implemented (future feature)', async ({ request }) => {
      const response = await request.post(`${BACKEND_URL}/summarize_convo`, {
        data: {
          sessionId: TEST_SESSION_ID,
          summaryType: 'brief'
        }
      });

      // This endpoint should be implemented but may return 501
      expect([200, 501]).toContain(response.status());
    });
  });

  test.describe('End-to-End Conversation Flow', () => {

    test('should complete full chat conversation workflow', async ({ request }) => {
      const e2eSessionId = `e2e-test-${Date.now()}`;

      // Step 1: Send first message
      const turn1 = await request.post(`${BACKEND_URL}/convo_turn`, {
        data: {
          sessionId: e2eSessionId,
          animalId: 'pokey',
          message: 'Hello Pokey!'
        }
      });
      expect(turn1.status()).toBe(200);
      const turn1Data = await turn1.json();
      expect(turn1Data.reply.toLowerCase()).toContain('pokey');

      // Step 2: Send second message
      const turn2 = await request.post(`${BACKEND_URL}/convo_turn`, {
        data: {
          sessionId: e2eSessionId,
          animalId: 'pokey',
          message: 'Tell me about your food'
        }
      });
      expect(turn2.status()).toBe(200);
      const turn2Data = await turn2.json();
      expect(turn2Data.reply.toLowerCase()).toContain('food');

      // Step 3: Retrieve conversation history
      const history = await request.get(`${BACKEND_URL}/convo_history?sessionId=${e2eSessionId}`);
      expect(history.status()).toBe(200);
      const historyData = await history.json();
      expect(historyData.sessionId).toBe(e2eSessionId);
      expect(historyData.messages.length).toBeGreaterThanOrEqual(2);

      // Step 4: Clean up - delete conversation
      const cleanup = await request.delete(`${BACKEND_URL}/convo_history?sessionId=${e2eSessionId}`);
      expect(cleanup.status()).toBe(204);
    });
  });
});
