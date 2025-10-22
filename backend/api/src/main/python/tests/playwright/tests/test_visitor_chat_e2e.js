/**
 * E2E Test: Visitor Chat with Animal
 * Task T017: Create Playwright test for visitor chat
 * Tests unauthenticated visitor interactions with animal chatbots
 */

const { test, expect } = require('@playwright/test');

const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:3001';

test.describe('🦒 Visitor Chat E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto(FRONTEND_URL);
  });

  test('T017.1: Visitor can access public homepage', async ({ page }) => {
    // Verify homepage loads
    await expect(page.locator('h1:has-text("Welcome to Cougar Mountain Zoo")')).toBeVisible();

    // Check for animal showcase
    await expect(page.locator('text=Meet Our Animal Ambassadors')).toBeVisible();

    // Verify animal cards are displayed
    const animalCards = page.locator('.animal-showcase-card');
    await expect(animalCards).toHaveCount({ min: 3 });

    // Check for chat invitation
    await expect(page.locator('text=Chat with an Animal')).toBeVisible();
  });

  test('T017.2: Visitor can browse available animals', async ({ page }) => {
    // Click explore animals
    await page.click('button:has-text("Explore Animals")');

    // Wait for animals gallery
    await page.waitForSelector('.animals-gallery');

    // Verify animals are displayed
    const animalTiles = page.locator('.animal-tile');
    await expect(animalTiles).toHaveCount({ min: 5 });

    // Check animal information displayed
    const firstAnimal = animalTiles.first();
    await expect(firstAnimal.locator('.animal-name')).toBeVisible();
    await expect(firstAnimal.locator('.animal-species')).toBeVisible();
    await expect(firstAnimal.locator('.animal-status')).toBeVisible();

    // Verify availability indicators
    await expect(page.locator('.status-available')).toBeVisible();
  });

  test('T017.3: Visitor can start chat with available animal', async ({ page }) => {
    // Click on an available animal
    await page.click('.animal-tile:has(.status-available):first-child button:has-text("Chat Now")');

    // Wait for chat interface
    await page.waitForSelector('.chat-interface');

    // Verify chat components
    await expect(page.locator('.chat-header')).toBeVisible();
    await expect(page.locator('.chat-messages')).toBeVisible();
    await expect(page.locator('.chat-input')).toBeVisible();

    // Check welcome message
    await expect(page.locator('.message.animal-message')).toBeVisible();
    const welcomeMessage = page.locator('.message.animal-message').first();
    await expect(welcomeMessage).toContainText(/Hello|Hi|Welcome/i);
  });

  test('T017.4: Visitor can send messages to animal', async ({ page }) => {
    // Start chat with animal
    await page.click('.animal-tile:has(.status-available):first-child button:has-text("Chat Now")');
    await page.waitForSelector('.chat-interface');

    // Type and send message
    await page.fill('.chat-input input', 'Hello! Tell me about yourself');
    await page.click('button:has-text("Send")');

    // Verify message appears in chat
    await expect(page.locator('.message.user-message:has-text("Hello! Tell me about yourself")')).toBeVisible();

    // Wait for animal response
    await page.waitForSelector('.message.animal-message:nth-child(2)', { timeout: 10000 });

    // Verify response received
    const response = page.locator('.message.animal-message').nth(1);
    await expect(response).toBeVisible();
    await expect(response).not.toBeEmpty();
  });

  test('T017.5: Visitor can ask educational questions', async ({ page }) => {
    // Start chat
    await page.click('.animal-tile:has-text("Lion"):first button:has-text("Chat Now")');
    await page.waitForSelector('.chat-interface');

    // Ask educational question
    await page.fill('.chat-input input', 'What do you eat?');
    await page.click('button:has-text("Send")');

    // Wait for response
    await page.waitForSelector('.message.animal-message:nth-child(2)', { timeout: 10000 });

    // Verify educational content in response
    const response = page.locator('.message.animal-message').nth(1);
    await expect(response).toContainText(/meat|carnivore|prey|hunt/i);

    // Ask follow-up question
    await page.fill('.chat-input input', 'How much do you eat per day?');
    await page.click('button:has-text("Send")');

    // Wait for follow-up response
    await page.waitForSelector('.message.animal-message:nth-child(4)', { timeout: 10000 });

    // Verify context maintained
    const followUp = page.locator('.message.animal-message').nth(2);
    await expect(followUp).toContainText(/pounds|kg|day/i);
  });

  test('T017.6: Visitor can use suggested questions', async ({ page }) => {
    // Start chat
    await page.click('.animal-tile:has(.status-available):first button:has-text("Chat Now")');
    await page.waitForSelector('.chat-interface');

    // Verify suggested questions appear
    await expect(page.locator('.suggested-questions')).toBeVisible();

    // Click a suggested question
    const suggestedQuestion = page.locator('.suggested-question').first();
    const questionText = await suggestedQuestion.textContent();
    await suggestedQuestion.click();

    // Verify question was sent
    await expect(page.locator(`.message.user-message:has-text("${questionText}")`)).toBeVisible();

    // Wait for response
    await page.waitForSelector('.message.animal-message:nth-child(2)', { timeout: 10000 });
  });

  test('T017.7: Visitor can end chat and rate experience', async ({ page }) => {
    // Start chat
    await page.click('.animal-tile:has(.status-available):first button:has-text("Chat Now")');
    await page.waitForSelector('.chat-interface');

    // Send a message
    await page.fill('.chat-input input', 'Thank you for chatting!');
    await page.click('button:has-text("Send")');

    // End chat
    await page.click('button:has-text("End Chat")');

    // Wait for rating dialog
    await page.waitForSelector('.rating-dialog');

    // Verify rating components
    await expect(page.locator('text=Rate Your Experience')).toBeVisible();
    await expect(page.locator('.star-rating')).toBeVisible();

    // Give rating
    await page.click('.star-rating .star:nth-child(4)'); // 4 stars

    // Add feedback
    await page.fill('textarea[name="feedback"]', 'Great educational experience!');

    // Submit rating
    await page.click('button:has-text("Submit")');

    // Verify thank you message
    await expect(page.locator('.thank-you-message')).toBeVisible();
  });

  test('T017.8: Visitor session persists during navigation', async ({ page }) => {
    // Start chat
    await page.click('.animal-tile:has(.status-available):first button:has-text("Chat Now")');
    await page.waitForSelector('.chat-interface');

    // Send message
    await page.fill('.chat-input input', 'Remember me!');
    await page.click('button:has-text("Send")');

    // Note session ID
    const sessionId = await page.evaluate(() => sessionStorage.getItem('chatSessionId'));
    expect(sessionId).toBeTruthy();

    // Navigate away
    await page.click('a:has-text("Home")');

    // Return to chat
    await page.click('.animal-tile:has(.status-available):first button:has-text("Resume Chat")');

    // Verify session restored
    await expect(page.locator('.message.user-message:has-text("Remember me!")')).toBeVisible();

    // Verify same session ID
    const restoredSessionId = await page.evaluate(() => sessionStorage.getItem('chatSessionId'));
    expect(restoredSessionId).toBe(sessionId);
  });

  test('T017.9: Visitor can learn fun facts', async ({ page }) => {
    // Start chat
    await page.click('.animal-tile:has(.status-available):first button:has-text("Chat Now")');
    await page.waitForSelector('.chat-interface');

    // Ask for fun fact
    await page.fill('.chat-input input', 'Tell me a fun fact!');
    await page.click('button:has-text("Send")');

    // Wait for response
    await page.waitForSelector('.message.animal-message:nth-child(2)', { timeout: 10000 });

    // Verify fun fact format
    const response = page.locator('.message.animal-message').nth(1);
    await expect(response).toContainText(/did you know|fun fact|interesting/i);

    // Verify fact includes educational content
    await expect(response).toMatch(/\d+|percent|only|unique|special/i);
  });

  test('T017.10: Visitor chat handles unavailable animals', async ({ page }) => {
    // Try to chat with unavailable animal
    const unavailableAnimal = page.locator('.animal-tile:has(.status-unavailable)').first();

    // Check if unavailable animals exist
    const count = await unavailableAnimal.count();
    if (count > 0) {
      // Verify chat button is disabled
      const chatButton = unavailableAnimal.locator('button:has-text("Chat")');
      await expect(chatButton).toBeDisabled();

      // Click on unavailable animal
      await unavailableAnimal.click();

      // Verify unavailable message
      await expect(page.locator('.unavailable-message')).toBeVisible();
      await expect(page.locator('.unavailable-message')).toContainText(/resting|offline|back soon/i);

      // Check for alternative suggestions
      await expect(page.locator('text=Try chatting with these animals')).toBeVisible();
    }
  });

  test('T017.11: Visitor can access educational resources', async ({ page }) => {
    // Start chat
    await page.click('.animal-tile:has(.status-available):first button:has-text("Chat Now")');
    await page.waitForSelector('.chat-interface');

    // Click learn more button
    await page.click('button:has-text("Learn More")');

    // Wait for resources panel
    await page.waitForSelector('.educational-resources');

    // Verify resources available
    await expect(page.locator('text=Educational Resources')).toBeVisible();
    await expect(page.locator('.resource-link')).toHaveCount({ min: 1 });

    // Check resource categories
    await expect(page.locator('text=About this Animal')).toBeVisible();
    await expect(page.locator('text=Conservation')).toBeVisible();
    await expect(page.locator('text=Fun Activities')).toBeVisible();
  });

  test('T017.12: Visitor experience is mobile-friendly', async ({ page, isMobile }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });

    // Verify mobile menu
    await expect(page.locator('.mobile-menu-button')).toBeVisible();

    // Open mobile menu
    await page.click('.mobile-menu-button');

    // Verify mobile navigation
    await expect(page.locator('.mobile-nav')).toBeVisible();

    // Navigate to animals
    await page.click('.mobile-nav >> text=Animals');

    // Verify responsive layout
    const animalCards = page.locator('.animal-tile');
    const firstCard = animalCards.first();
    const cardBox = await firstCard.boundingBox();

    // Cards should be full width on mobile
    expect(cardBox.width).toBeGreaterThan(300);

    // Start chat on mobile
    await page.click('.animal-tile:has(.status-available):first button');

    // Verify mobile chat interface
    await expect(page.locator('.chat-interface.mobile')).toBeVisible();

    // Verify input is accessible
    const input = page.locator('.chat-input input');
    await expect(input).toBeVisible();
    await input.click();
    await input.type('Mobile test');
  });
});

// No helper function needed as visitors don't login