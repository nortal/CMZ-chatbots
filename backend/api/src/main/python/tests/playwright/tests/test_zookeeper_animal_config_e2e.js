/**
 * E2E Test: Zookeeper Animal Configuration
 * Task T014: Create Playwright test for zookeeper animal config
 * Tests zookeeper-specific animal management and configuration
 */

const { test, expect } = require('@playwright/test');

// Test data
const ZOOKEEPER_USER = {
  email: 'zookeeper@cmz.org',
  password: 'testpass123'
};

const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:3001';

test.describe('🦁 Zookeeper Animal Config E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto(FRONTEND_URL);
  });

  test('T014.1: Zookeeper can successfully login', async ({ page }) => {
    // Click login button
    await page.click('text=Login');

    // Fill in zookeeper credentials
    await page.fill('input[type="email"]', ZOOKEEPER_USER.email);
    await page.fill('input[type="password"]', ZOOKEEPER_USER.password);

    // Submit login form
    await page.click('button[type="submit"]');

    // Wait for dashboard redirect
    await page.waitForURL('**/dashboard', { timeout: 10000 });

    // Verify zookeeper role indicator
    await expect(page.locator('text=Zookeeper Dashboard')).toBeVisible();
  });

  test('T014.2: Zookeeper can view animal list', async ({ page }) => {
    await loginAsZookeeper(page);

    // Navigate to animals page
    await page.click('nav >> text=Animals');
    await page.waitForURL('**/animals');

    // Verify animal list is visible
    await expect(page.locator('.animal-list')).toBeVisible();

    // Check for expected columns
    const headers = ['Name', 'Species', 'Habitat', 'Status', 'Actions'];
    for (const header of headers) {
      await expect(page.locator(`th:has-text("${header}")`)).toBeVisible();
    }

    // Verify at least one animal is listed
    const animalRows = page.locator('tbody tr');
    await expect(animalRows).toHaveCount({ min: 1 });
  });

  test('T014.3: Zookeeper can configure animal personality', async ({ page }) => {
    await loginAsZookeeper(page);

    // Navigate to animals page
    await page.goto(`${FRONTEND_URL}/animals`);

    // Click configure on first animal
    await page.click('button:has-text("Configure"):first');

    // Wait for configuration dialog
    await page.waitForSelector('.animal-config-dialog');

    // Verify personality configuration fields
    await expect(page.locator('label:has-text("Personality Type")')).toBeVisible();
    await expect(page.locator('select[name="personalityType"]')).toBeVisible();

    // Check AI parameter fields
    await expect(page.locator('label:has-text("Temperature")')).toBeVisible();
    await expect(page.locator('input[name="temperature"]')).toBeVisible();

    await expect(page.locator('label:has-text("Max Tokens")')).toBeVisible();
    await expect(page.locator('input[name="maxTokens"]')).toBeVisible();

    // Verify system prompt field
    await expect(page.locator('label:has-text("System Prompt")')).toBeVisible();
    await expect(page.locator('textarea[name="systemPrompt"]')).toBeVisible();
  });

  test('T014.4: Zookeeper can update animal AI parameters', async ({ page }) => {
    await loginAsZookeeper(page);

    // Navigate to animal configuration
    await page.goto(`${FRONTEND_URL}/animals`);
    await page.click('button:has-text("Configure"):first');

    // Wait for dialog to load
    await page.waitForSelector('.animal-config-dialog');

    // Update AI parameters
    await page.selectOption('select[name="personalityType"]', 'playful');

    // Clear and set temperature
    await page.fill('input[name="temperature"]', '');
    await page.fill('input[name="temperature"]', '0.8');

    // Clear and set max tokens
    await page.fill('input[name="maxTokens"]', '');
    await page.fill('input[name="maxTokens"]', '150');

    // Update system prompt
    await page.fill('textarea[name="systemPrompt"]',
      'You are a playful animal ambassador. Be friendly and educational.');

    // Save configuration
    await page.click('button:has-text("Save Configuration")');

    // Verify success message
    await expect(page.locator('.success-message')).toContainText('Configuration saved');

    // Verify changes persist (reopen dialog)
    await page.click('button:has-text("Configure"):first');
    await page.waitForSelector('.animal-config-dialog');

    // Check values were saved
    const temperature = await page.inputValue('input[name="temperature"]');
    expect(parseFloat(temperature)).toBe(0.8);

    const maxTokens = await page.inputValue('input[name="maxTokens"]');
    expect(parseInt(maxTokens)).toBe(150);
  });

  test('T014.5: Zookeeper can manage animal knowledge base', async ({ page }) => {
    await loginAsZookeeper(page);

    // Navigate to animal configuration
    await page.goto(`${FRONTEND_URL}/animals`);
    await page.click('button:has-text("Configure"):first');

    // Switch to Knowledge tab
    await page.click('button[role="tab"]:has-text("Knowledge Base")');

    // Verify knowledge base interface
    await expect(page.locator('text=Knowledge Entries')).toBeVisible();
    await expect(page.locator('button:has-text("Add Entry")')).toBeVisible();

    // Add new knowledge entry
    await page.click('button:has-text("Add Entry")');

    // Fill knowledge entry form
    await page.fill('input[name="knowledgeTitle"]', 'Diet Information');
    await page.fill('textarea[name="knowledgeContent"]',
      'This animal primarily eats leaves, fruits, and vegetables.');

    // Save knowledge entry
    await page.click('button:has-text("Save Entry")');

    // Verify entry was added
    await expect(page.locator('text=Diet Information')).toBeVisible();
  });

  test('T014.6: Zookeeper can set animal availability schedule', async ({ page }) => {
    await loginAsZookeeper(page);

    // Navigate to animal configuration
    await page.goto(`${FRONTEND_URL}/animals`);
    await page.click('button:has-text("Configure"):first');

    // Switch to Schedule tab
    await page.click('button[role="tab"]:has-text("Schedule")');

    // Verify schedule interface
    await expect(page.locator('text=Availability Schedule')).toBeVisible();

    // Set availability
    await page.check('input[name="monday"]');
    await page.check('input[name="tuesday"]');
    await page.check('input[name="wednesday"]');

    // Set time slots
    await page.fill('input[name="startTime"]', '09:00');
    await page.fill('input[name="endTime"]', '17:00');

    // Save schedule
    await page.click('button:has-text("Save Schedule")');

    // Verify success
    await expect(page.locator('.success-message')).toContainText('Schedule updated');
  });

  test('T014.7: Zookeeper can view animal interaction analytics', async ({ page }) => {
    await loginAsZookeeper(page);

    // Navigate to animal analytics
    await page.goto(`${FRONTEND_URL}/animals`);
    await page.click('button:has-text("Analytics"):first');

    // Wait for analytics page
    await page.waitForURL('**/analytics');

    // Verify analytics components
    await expect(page.locator('text=Interaction Statistics')).toBeVisible();
    await expect(page.locator('[data-testid="total-interactions"]')).toBeVisible();
    await expect(page.locator('[data-testid="avg-session-duration"]')).toBeVisible();
    await expect(page.locator('[data-testid="satisfaction-score"]')).toBeVisible();

    // Verify charts are rendered
    await expect(page.locator('.interactions-chart')).toBeVisible();
    await expect(page.locator('.sentiment-chart')).toBeVisible();
  });

  test('T014.8: Zookeeper can manage animal health status', async ({ page }) => {
    await loginAsZookeeper(page);

    // Navigate to animals page
    await page.goto(`${FRONTEND_URL}/animals`);

    // Click on animal status
    await page.click('button:has-text("Update Status"):first');

    // Wait for status dialog
    await page.waitForSelector('.status-dialog');

    // Update health status
    await page.selectOption('select[name="healthStatus"]', 'healthy');

    // Add health notes
    await page.fill('textarea[name="healthNotes"]',
      'Regular checkup completed. All vitals normal.');

    // Set next checkup date
    const nextWeek = new Date();
    nextWeek.setDate(nextWeek.getDate() + 7);
    const dateStr = nextWeek.toISOString().split('T')[0];
    await page.fill('input[type="date"]', dateStr);

    // Save status update
    await page.click('button:has-text("Save Status")');

    // Verify status was updated
    await expect(page.locator('.status-indicator.healthy')).toBeVisible();
  });

  test('T014.9: Zookeeper role-based restrictions', async ({ page }) => {
    await loginAsZookeeper(page);

    // Verify cannot access admin-only features
    await page.goto(`${FRONTEND_URL}/system/ai-provider`);

    // Should redirect or show access denied
    const url = page.url();
    expect(url).not.toContain('/system/ai-provider');

    // Verify cannot delete users
    await page.goto(`${FRONTEND_URL}/users`);

    // Delete buttons should not be visible for zookeeper
    const deleteButtons = page.locator('button:has-text("Delete User")');
    await expect(deleteButtons).toHaveCount(0);

    // Verify CAN manage animals (zookeeper permission)
    await page.goto(`${FRONTEND_URL}/animals`);
    await expect(page.locator('button:has-text("Configure")')).toBeVisible();
  });

  test('T014.10: Zookeeper can export animal data', async ({ page }) => {
    await loginAsZookeeper(page);

    // Navigate to animals page
    await page.goto(`${FRONTEND_URL}/animals`);

    // Click export button
    await page.click('button:has-text("Export Data")');

    // Select export format
    await page.selectOption('select[name="exportFormat"]', 'csv');

    // Select data to export
    await page.check('input[name="includeConfig"]');
    await page.check('input[name="includeAnalytics"]');
    await page.check('input[name="includeSchedule"]');

    // Trigger download
    const [download] = await Promise.all([
      page.waitForEvent('download'),
      page.click('button:has-text("Download")')
    ]);

    // Verify download started
    expect(download).toBeTruthy();
    const fileName = download.suggestedFilename();
    expect(fileName).toContain('animal');
    expect(fileName).toEndWith('.csv');
  });
});

// Helper function to login as zookeeper
async function loginAsZookeeper(page) {
  await page.goto(`${FRONTEND_URL}/login`);
  await page.fill('input[type="email"]', ZOOKEEPER_USER.email);
  await page.fill('input[type="password"]', ZOOKEEPER_USER.password);
  await page.click('button[type="submit"]');
  await page.waitForURL('**/dashboard', { timeout: 10000 });
}