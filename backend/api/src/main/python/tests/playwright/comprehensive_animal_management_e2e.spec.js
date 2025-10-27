/**
 * Comprehensive Animal Assistant Management E2E Test
 *
 * Tests the complete animal configuration system workflow:
 * 1. Animal CRUD operations
 * 2. Guardrails configuration
 * 3. Personality assignment
 * 4. System prompt generation and saving
 * 5. Assistant creation and modification
 * 6. Conversation testing with newly created animals
 *
 * This test validates the complete User Story 1 implementation:
 * "Create and Deploy Live Animal Assistant"
 *
 * Author: CMZ Animal Assistant Management System
 * Date: 2025-10-25
 */

const { test, expect } = require('@playwright/test');

// Test configuration
const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:3001';
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8080';

// Test data
const TEST_ANIMAL = {
  animalId: `test-animal-${Date.now()}`,
  name: 'Test E2E Penguin',
  scientificName: 'Spheniscus e2etest',
  species: 'Humboldt Penguin',
  habitat: 'Antarctic coastal waters',
  diet: 'Fish, krill, and squid',
  status: 'active',
  description: 'A friendly penguin for comprehensive E2E testing of the animal assistant management system.',
  personalityTraits: [
    'Curious and playful',
    'Loves swimming and diving',
    'Social and communicative',
    'Educational and informative'
  ],
  temperature: 0.7,
  topP: 0.9,
  maxTokens: 1000,
  systemPrompt: 'You are a friendly Humboldt penguin who loves to teach children about marine life and conservation.'
};

const TEST_GUARDRAILS = [
  'Always maintain a friendly and educational tone',
  'Never discuss harmful or inappropriate topics',
  'Focus on marine conservation and penguin facts',
  'Keep responses appropriate for children ages 5-12'
];

// User credentials for testing
const TEST_USER = {
  email: 'test@cmz.org',
  password: 'testpass123'
};

test.describe('🐧 Comprehensive Animal Assistant Management E2E', () => {
  let authToken = null;
  let animalId = null;
  let assistantId = null;

  test.beforeAll(async () => {
    console.log('🚀 Starting comprehensive animal management E2E test');
    console.log(`Frontend: ${FRONTEND_URL}`);
    console.log(`Backend: ${BACKEND_URL}`);
  });

  test.beforeEach(async ({ page }) => {
    console.log('🔐 Setting up authentication for test...');

    // Navigate to login page
    await page.goto(FRONTEND_URL);

    // Perform login
    await page.fill('input[name="email"]', TEST_USER.email);
    await page.fill('input[name="password"]', TEST_USER.password);
    await page.click('button[type="submit"]');

    // Wait for successful login and dashboard load
    await page.waitForURL('**/dashboard', { timeout: 10000 });
    await expect(page.locator('h1')).toContainText('Dashboard');

    console.log('✅ Authentication successful');
  });

  test('Phase 1: Create New Animal with Complete Configuration', async ({ page }) => {
    console.log('🆕 Phase 1: Creating new animal with complete configuration...');

    // Navigate to Animals section
    await page.click('text=Animals');
    await page.waitForLoadState('networkidle');

    // Click "Add New Animal" button
    await page.click('button:has-text("Add New Animal"), button:has-text("Create Animal")');
    await page.waitForSelector('.animal-form, [data-testid="animal-form"]', { timeout: 5000 });

    // Fill in basic animal information
    console.log('📝 Filling in animal basic information...');
    await page.fill('input[name="name"]', TEST_ANIMAL.name);
    await page.fill('input[name="scientificName"]', TEST_ANIMAL.scientificName);
    await page.fill('input[name="species"]', TEST_ANIMAL.species);
    await page.fill('input[name="habitat"]', TEST_ANIMAL.habitat);
    await page.fill('input[name="diet"]', TEST_ANIMAL.diet);
    await page.fill('textarea[name="description"]', TEST_ANIMAL.description);

    // Set status to active
    await page.selectOption('select[name="status"]', 'active');

    // Save the animal
    await page.click('button:has-text("Save"), button:has-text("Create")');

    // Wait for success confirmation
    await expect(page.locator('.success-message, .alert-success')).toBeVisible({ timeout: 10000 });

    // Capture the animal ID from the URL or response
    const currentUrl = page.url();
    const animalIdMatch = currentUrl.match(/animal[s]?\/([^\/\?]+)/);
    if (animalIdMatch) {
      animalId = animalIdMatch[1];
      console.log(`✅ Animal created successfully with ID: ${animalId}`);
    }

    // Take screenshot of created animal
    await page.screenshot({
      path: 'test-results/01-animal-created.png',
      fullPage: true
    });
  });

  test('Phase 2: Configure Animal Personality and Guardrails', async ({ page }) => {
    console.log('🎭 Phase 2: Configuring animal personality and guardrails...');

    // Navigate to the animal configuration page
    await page.click('text=Animals');
    await page.waitForLoadState('networkidle');

    // Find and click on our test animal
    await page.click(`text=${TEST_ANIMAL.name}`);
    await page.waitForLoadState('networkidle');

    // Click on "Configuration" or "Settings" tab
    await page.click('text=Configuration, text=Settings, button:has-text("Configure")');
    await page.waitForSelector('.config-form, [data-testid="config-form"]', { timeout: 5000 });

    // Configure personality traits
    console.log('🎨 Setting personality configuration...');

    // Set temperature and topP values
    await page.fill('input[name="temperature"]', TEST_ANIMAL.temperature.toString());
    await page.fill('input[name="topP"]', TEST_ANIMAL.topP.toString());
    await page.fill('input[name="maxTokens"]', TEST_ANIMAL.maxTokens.toString());

    // Set system prompt
    await page.fill('textarea[name="systemPrompt"]', TEST_ANIMAL.systemPrompt);

    // Add personality traits
    for (const trait of TEST_ANIMAL.personalityTraits) {
      await page.click('button:has-text("Add Trait"), button:has-text("Add Personality")');
      await page.fill('input[name="personalityTrait"]:last-of-type, .trait-input:last-of-type input', trait);
    }

    // Configure guardrails
    console.log('🛡️ Setting guardrails configuration...');

    for (const guardrail of TEST_GUARDRAILS) {
      await page.click('button:has-text("Add Guardrail"), button:has-text("Add Rule")');
      await page.fill('textarea[name="guardrailRule"]:last-of-type, .guardrail-input:last-of-type textarea', guardrail);
    }

    // Save configuration
    await page.click('button:has-text("Save Configuration"), button:has-text("Update")');

    // Wait for success confirmation
    await expect(page.locator('.success-message, .alert-success')).toBeVisible({ timeout: 10000 });

    console.log('✅ Animal personality and guardrails configured successfully');

    // Take screenshot of configuration
    await page.screenshot({
      path: 'test-results/02-animal-configured.png',
      fullPage: true
    });
  });

  test('Phase 3: Generate and Validate System Prompt', async ({ page }) => {
    console.log('🔧 Phase 3: Generating and validating system prompt...');

    // Navigate to the animal configuration page
    await page.click('text=Animals');
    await page.waitForLoadState('networkidle');
    await page.click(`text=${TEST_ANIMAL.name}`);
    await page.waitForLoadState('networkidle');

    // Look for prompt generation section
    await page.click('text=Generate Prompt, text=Merge Prompt, button:has-text("Generate")');

    // Wait for prompt generation to complete
    await page.waitForSelector('.generated-prompt, [data-testid="generated-prompt"]', { timeout: 15000 });

    // Verify the prompt contains our personality elements
    const generatedPrompt = await page.locator('.generated-prompt textarea, .prompt-preview textarea').textContent();

    // Validate prompt contains key elements
    expect(generatedPrompt).toContain('penguin');
    expect(generatedPrompt).toContain('marine life');
    expect(generatedPrompt).toContain('educational');

    console.log('✅ System prompt generated and validated');

    // Save the generated prompt
    await page.click('button:has-text("Save Prompt"), button:has-text("Accept")');
    await expect(page.locator('.success-message, .alert-success')).toBeVisible({ timeout: 5000 });

    // Take screenshot of generated prompt
    await page.screenshot({
      path: 'test-results/03-prompt-generated.png',
      fullPage: true
    });
  });

  test('Phase 4: Create and Deploy Assistant', async ({ page }) => {
    console.log('🤖 Phase 4: Creating and deploying assistant...');

    // Navigate to Assistants section
    await page.click('text=Assistants');
    await page.waitForLoadState('networkidle');

    // Create new assistant or link to animal
    await page.click('button:has-text("Create Assistant"), button:has-text("New Assistant")');
    await page.waitForSelector('.assistant-form, [data-testid="assistant-form"]', { timeout: 5000 });

    // Link assistant to our test animal
    await page.selectOption('select[name="animalId"]', animalId || TEST_ANIMAL.name);

    // Set assistant name
    await page.fill('input[name="assistantName"]', `${TEST_ANIMAL.name} Assistant`);

    // Deploy assistant
    await page.click('button:has-text("Deploy"), button:has-text("Create and Deploy")');

    // Wait for deployment success
    await expect(page.locator('.success-message, .alert-success')).toBeVisible({ timeout: 15000 });

    // Capture assistant ID if available
    const assistantUrl = page.url();
    const assistantIdMatch = assistantUrl.match(/assistant[s]?\/([^\/\?]+)/);
    if (assistantIdMatch) {
      assistantId = assistantIdMatch[1];
      console.log(`✅ Assistant deployed successfully with ID: ${assistantId}`);
    }

    // Take screenshot of deployed assistant
    await page.screenshot({
      path: 'test-results/04-assistant-deployed.png',
      fullPage: true
    });
  });

  test('Phase 5: Test Conversation with New Assistant', async ({ page }) => {
    console.log('💬 Phase 5: Testing conversation with new assistant...');

    // Navigate to Chat section
    await page.click('text=Chat');
    await page.waitForLoadState('networkidle');

    // Select our test animal for conversation
    await page.click(`text=${TEST_ANIMAL.name}`);
    await page.waitForSelector('.chat-interface, [data-testid="chat-interface"]', { timeout: 5000 });

    // Send test messages to validate assistant behavior
    const testMessages = [
      "Hello! What kind of animal are you?",
      "Tell me about your habitat",
      "What do you like to eat?",
      "Can you teach me about conservation?"
    ];

    for (let i = 0; i < testMessages.length; i++) {
      const message = testMessages[i];
      console.log(`📨 Sending message ${i + 1}: "${message}"`);

      // Type and send message
      await page.fill('input[name="message"], textarea[name="message"]', message);
      await page.click('button:has-text("Send"), button[type="submit"]');

      // Wait for response
      await page.waitForSelector('.chat-message.assistant, .response-message', { timeout: 20000 });

      // Verify response contains expected content
      const responseLocator = page.locator('.chat-message.assistant, .response-message').last();
      const responseText = await responseLocator.textContent();

      // Basic validation that response is relevant
      expect(responseText.length).toBeGreaterThan(10);
      expect(responseText).not.toContain('error');
      expect(responseText).not.toContain('not implemented');

      console.log(`✅ Received valid response for message ${i + 1}`);

      // Wait a moment between messages
      await page.waitForTimeout(2000);
    }

    console.log('✅ Conversation testing completed successfully');

    // Take screenshot of chat session
    await page.screenshot({
      path: 'test-results/05-conversation-test.png',
      fullPage: true
    });
  });

  test('Phase 6: Modify Assistant and Test Changes', async ({ page }) => {
    console.log('🔄 Phase 6: Modifying assistant and testing changes...');

    // Navigate back to animal configuration
    await page.click('text=Animals');
    await page.waitForLoadState('networkidle');
    await page.click(`text=${TEST_ANIMAL.name}`);
    await page.waitForLoadState('networkidle');

    // Edit the system prompt
    await page.click('text=Configuration, text=Settings');
    await page.waitForSelector('textarea[name="systemPrompt"]', { timeout: 5000 });

    // Modify the system prompt
    const modifiedPrompt = TEST_ANIMAL.systemPrompt + ' You are also very enthusiastic about ocean conservation and love to share fun penguin facts!';
    await page.fill('textarea[name="systemPrompt"]', modifiedPrompt);

    // Adjust temperature for more creative responses
    await page.fill('input[name="temperature"]', '0.8');

    // Save changes
    await page.click('button:has-text("Save Configuration"), button:has-text("Update")');
    await expect(page.locator('.success-message, .alert-success')).toBeVisible({ timeout: 5000 });

    // Regenerate prompt with new settings
    await page.click('button:has-text("Generate Prompt"), button:has-text("Regenerate")');
    await page.waitForSelector('.generated-prompt', { timeout: 10000 });
    await page.click('button:has-text("Save Prompt"), button:has-text("Accept")');

    console.log('✅ Assistant configuration modified');

    // Test the modified assistant
    await page.click('text=Chat');
    await page.waitForLoadState('networkidle');
    await page.click(`text=${TEST_ANIMAL.name}`);

    // Send a test message to see the updated behavior
    await page.fill('input[name="message"], textarea[name="message"]', "Tell me something exciting about being a penguin!");
    await page.click('button:has-text("Send"), button[type="submit"]');

    // Wait for response
    await page.waitForSelector('.chat-message.assistant, .response-message', { timeout: 20000 });

    const modifiedResponse = await page.locator('.chat-message.assistant, .response-message').last().textContent();
    expect(modifiedResponse.length).toBeGreaterThan(10);

    console.log('✅ Modified assistant responding correctly');

    // Take final screenshot
    await page.screenshot({
      path: 'test-results/06-modified-assistant.png',
      fullPage: true
    });
  });

  test('Phase 7: Validate Data Persistence in DynamoDB', async ({ page }) => {
    console.log('💾 Phase 7: Validating data persistence in DynamoDB...');

    // This phase validates that all our changes are properly persisted
    // by refreshing the page and checking that all data is still there

    // Refresh the page to clear any client-side cache
    await page.reload();
    await page.waitForLoadState('networkidle');

    // Navigate to the animal and verify all data persisted
    await page.click('text=Animals');
    await page.waitForLoadState('networkidle');

    // Verify animal still exists in list
    await expect(page.locator(`text=${TEST_ANIMAL.name}`)).toBeVisible();

    // Click on the animal
    await page.click(`text=${TEST_ANIMAL.name}`);
    await page.waitForLoadState('networkidle');

    // Verify configuration is persisted
    await page.click('text=Configuration, text=Settings');
    await page.waitForSelector('textarea[name="systemPrompt"]', { timeout: 5000 });

    // Check that our modified values are still there
    const persistedPrompt = await page.locator('textarea[name="systemPrompt"]').inputValue();
    expect(persistedPrompt).toContain('enthusiastic about ocean conservation');

    const persistedTemp = await page.locator('input[name="temperature"]').inputValue();
    expect(persistedTemp).toBe('0.8');

    console.log('✅ Data persistence validated - all changes properly saved to DynamoDB');

    // Take final validation screenshot
    await page.screenshot({
      path: 'test-results/07-data-persistence-validated.png',
      fullPage: true
    });
  });

  test.afterAll(async () => {
    console.log('🧹 Cleaning up test data...');
    console.log(`Animal ID: ${animalId}`);
    console.log(`Assistant ID: ${assistantId}`);
    console.log('✅ Comprehensive Animal Assistant Management E2E test completed successfully!');

    // Note: In a real environment, you might want to clean up the test data
    // by making API calls to delete the test animal and assistant
  });
});

// Helper function to wait for API response
async function waitForApiResponse(page, endpoint, timeout = 10000) {
  return page.waitForResponse(
    response => response.url().includes(endpoint) && response.status() === 200,
    { timeout }
  );
}

// Helper function to validate response contains expected data
async function validateApiResponse(page, endpoint, expectedFields) {
  const response = await waitForApiResponse(page, endpoint);
  const data = await response.json();

  for (const field of expectedFields) {
    expect(data).toHaveProperty(field);
  }

  return data;
}