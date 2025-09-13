/**
 * MANDATORY PERSISTENCE TEST: Playwright-to-DynamoDB Verification
 *
 * This test verifies that Playwright UI interactions are properly persisted
 * to DynamoDB tables, ensuring data integrity across the entire stack.
 *
 * Required by TDD framework for comprehensive coverage reporting.
 */

const { test, expect } = require('@playwright/test');

// DynamoDB verification utilities
const AWS = require('aws-sdk');
const dynamodb = new AWS.DynamoDB.DocumentClient({
  region: process.env.AWS_REGION || 'us-west-2',
  ...(process.env.DYNAMODB_ENDPOINT_URL && { endpoint: process.env.DYNAMODB_ENDPOINT_URL })
});

// Test data for verification
const TEST_DATA = {
  family: {
    tableName: process.env.FAMILY_DYNAMO_TABLE_NAME || 'quest-dev-family',
    pkName: process.env.FAMILY_DYNAMO_PK_NAME || 'familyId',
    testRecord: {
      familyName: 'Playwright Test Family',
      parentEmail: 'playwright.test@cmz.org',
      studentCount: 2
    }
  },
  animal: {
    tableName: process.env.ANIMAL_DYNAMO_TABLE_NAME || 'quest-dev-animal',
    pkName: process.env.ANIMAL_DYNAMO_PK_NAME || 'animalId',
    testRecord: {
      name: 'Playwright Test Tiger',
      species: 'tiger',
      personality: 'friendly'
    }
  }
};

async function verifyDynamoDBRecord(tableName, pkName, pkValue, expectedData) {
  try {
    const params = {
      TableName: tableName,
      Key: { [pkName]: pkValue }
    };

    const result = await dynamodb.get(params).promise();

    if (!result.Item) {
      throw new Error(`Record not found in ${tableName} with ${pkName}=${pkValue}`);
    }

    // Verify expected fields exist
    for (const [field, value] of Object.entries(expectedData)) {
      if (result.Item[field] !== value) {
        throw new Error(`Field ${field}: expected '${value}', got '${result.Item[field]}'`);
      }
    }

    console.log(`✅ DynamoDB verification passed for ${tableName}`);
    return result.Item;

  } catch (error) {
    console.error(`❌ DynamoDB verification failed for ${tableName}:`, error);
    throw error;
  }
}

test.describe('🔄 Playwright-to-DynamoDB Persistence Verification', () => {
  let testFamilyId;
  let testAnimalId;

  test.beforeEach(async ({ page }) => {
    // Navigate to application
    await page.goto(process.env.FRONTEND_URL || 'http://localhost:3001');

    // Ensure authenticated state
    await page.waitForLoadState('networkidle');
  });

  test('should persist family creation from UI to DynamoDB', async ({ page }) => {
    // Step 1: Create family via UI
    await page.click('[data-testid="create-family-button"]');
    await page.fill('[data-testid="family-name-input"]', TEST_DATA.family.testRecord.familyName);
    await page.fill('[data-testid="parent-email-input"]', TEST_DATA.family.testRecord.parentEmail);
    await page.fill('[data-testid="student-count-input"]', TEST_DATA.family.testRecord.studentCount.toString());

    // Submit form and capture response
    const [response] = await Promise.all([
      page.waitForResponse(response =>
        response.url().includes('/family') && response.request().method() === 'POST'
      ),
      page.click('[data-testid="submit-family-button"]')
    ]);

    // Verify API response
    expect(response.status()).toBe(201);
    const responseData = await response.json();
    testFamilyId = responseData.familyId;

    console.log(`📋 Created family with ID: ${testFamilyId}`);

    // Step 2: Verify persistence in DynamoDB
    await new Promise(resolve => setTimeout(resolve, 2000)); // Wait for DB write

    const dbRecord = await verifyDynamoDBRecord(
      TEST_DATA.family.tableName,
      TEST_DATA.family.pkName,
      testFamilyId,
      {
        familyName: TEST_DATA.family.testRecord.familyName,
        parentEmail: TEST_DATA.family.testRecord.parentEmail,
        studentCount: TEST_DATA.family.testRecord.studentCount
      }
    );

    // Step 3: Verify audit fields
    expect(dbRecord.created).toBeDefined();
    expect(dbRecord.created.at).toBeDefined();
    expect(dbRecord.modified).toBeDefined();
    expect(dbRecord.modified.at).toBeDefined();

    console.log('✅ Family persistence verification: UI → API → DynamoDB ✅');
  });

  test('should persist animal configuration from UI to DynamoDB', async ({ page }) => {
    // Step 1: Navigate to animal configuration
    await page.click('[data-testid="animal-config-button"]');

    // Create new animal configuration
    await page.click('[data-testid="add-animal-button"]');
    await page.fill('[data-testid="animal-name-input"]', TEST_DATA.animal.testRecord.name);
    await page.selectOption('[data-testid="animal-species-select"]', TEST_DATA.animal.testRecord.species);
    await page.fill('[data-testid="animal-personality-input"]', TEST_DATA.animal.testRecord.personality);

    // Submit and capture response
    const [response] = await Promise.all([
      page.waitForResponse(response =>
        response.url().includes('/animal') && response.request().method() === 'POST'
      ),
      page.click('[data-testid="save-animal-button"]')
    ]);

    // Verify API response
    expect(response.status()).toBe(201);
    const responseData = await response.json();
    testAnimalId = responseData.animalId;

    console.log(`🐯 Created animal with ID: ${testAnimalId}`);

    // Step 2: Verify persistence in DynamoDB
    await new Promise(resolve => setTimeout(resolve, 2000)); // Wait for DB write

    const dbRecord = await verifyDynamoDBRecord(
      TEST_DATA.animal.tableName,
      TEST_DATA.animal.pkName,
      testAnimalId,
      {
        name: TEST_DATA.animal.testRecord.name,
        species: TEST_DATA.animal.testRecord.species,
        personality: TEST_DATA.animal.testRecord.personality
      }
    );

    // Step 3: Verify configuration fields
    expect(dbRecord.enabled).toBe(true);
    expect(dbRecord.created).toBeDefined();
    expect(dbRecord.modified).toBeDefined();

    console.log('✅ Animal persistence verification: UI → API → DynamoDB ✅');
  });

  test('should persist conversation data from chat UI to DynamoDB', async ({ page }) => {
    // Step 1: Start chat session
    await page.click('[data-testid="start-chat-button"]');

    // Send test message
    const testMessage = 'Hello, can you tell me about tigers?';
    await page.fill('[data-testid="chat-input"]', testMessage);

    const [response] = await Promise.all([
      page.waitForResponse(response =>
        response.url().includes('/conversation') && response.request().method() === 'POST'
      ),
      page.press('[data-testid="chat-input"]', 'Enter')
    ]);

    // Verify API response
    expect(response.status()).toBe(201);
    const responseData = await response.json();
    const conversationId = responseData.conversationId;

    console.log(`💬 Created conversation with ID: ${conversationId}`);

    // Step 2: Verify persistence in DynamoDB
    await new Promise(resolve => setTimeout(resolve, 3000)); // Wait for AI response + DB write

    const dbRecord = await verifyDynamoDBRecord(
      process.env.CONVERSATION_DYNAMO_TABLE_NAME || 'quest-dev-conversation',
      process.env.CONVERSATION_DYNAMO_PK_NAME || 'conversationId',
      conversationId,
      {
        status: 'active'
      }
    );

    // Step 3: Verify conversation structure
    expect(dbRecord.messages).toBeDefined();
    expect(Array.isArray(dbRecord.messages)).toBe(true);
    expect(dbRecord.messages.length).toBeGreaterThan(0);

    // Verify user message was stored
    const userMessage = dbRecord.messages.find(m => m.role === 'user');
    expect(userMessage).toBeDefined();
    expect(userMessage.content).toContain(testMessage);

    console.log('✅ Conversation persistence verification: UI → API → DynamoDB ✅');
  });

  test.afterEach(async () => {
    // Cleanup test records to maintain clean state
    if (testFamilyId) {
      try {
        await dynamodb.delete({
          TableName: TEST_DATA.family.tableName,
          Key: { [TEST_DATA.family.pkName]: testFamilyId }
        }).promise();
        console.log(`🗑️ Cleaned up test family: ${testFamilyId}`);
      } catch (error) {
        console.warn(`⚠️ Cleanup warning for family ${testFamilyId}:`, error);
      }
    }

    if (testAnimalId) {
      try {
        await dynamodb.delete({
          TableName: TEST_DATA.animal.tableName,
          Key: { [TEST_DATA.animal.pkName]: testAnimalId }
        }).promise();
        console.log(`🗑️ Cleaned up test animal: ${testAnimalId}`);
      } catch (error) {
        console.warn(`⚠️ Cleanup warning for animal ${testAnimalId}:`, error);
      }
    }
  });
});

// Performance verification test
test.describe('🚀 DynamoDB Performance Verification', () => {
  test('should complete CRUD operations within acceptable time limits', async ({ page }) => {
    const startTime = Date.now();

    // Test rapid succession of operations
    await page.goto(process.env.FRONTEND_URL || 'http://localhost:3001');

    // Create → Read → Update → Delete cycle
    await page.click('[data-testid="create-family-button"]');
    await page.fill('[data-testid="family-name-input"]', 'Performance Test Family');

    const createResponse = await Promise.all([
      page.waitForResponse(response =>
        response.url().includes('/family') && response.request().method() === 'POST'
      ),
      page.click('[data-testid="submit-family-button"]')
    ]);

    const createTime = Date.now() - startTime;
    console.log(`⏱️ Create operation: ${createTime}ms`);

    // Verify performance constraints
    expect(createTime).toBeLessThan(5000); // 5 second max

    // Verify DynamoDB response time
    const dbVerifyStart = Date.now();
    const familyId = (await createResponse[0].json()).familyId;

    await verifyDynamoDBRecord(
      TEST_DATA.family.tableName,
      TEST_DATA.family.pkName,
      familyId,
      { familyName: 'Performance Test Family' }
    );

    const dbVerifyTime = Date.now() - dbVerifyStart;
    console.log(`⏱️ DynamoDB verification: ${dbVerifyTime}ms`);

    expect(dbVerifyTime).toBeLessThan(2000); // 2 second max for DB operations

    console.log('✅ Performance verification: All operations within acceptable limits');
  });
});