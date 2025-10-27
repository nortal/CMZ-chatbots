/**
 * E2E Test: Parent Viewing Children's Activity
 * Task T016: Create Playwright test for parent viewing activity
 * Tests parent-specific features for monitoring children's interactions
 */

const { test, expect } = require('@playwright/test');

// Test data
const PARENT_USER = {
  email: 'parent1@test.cmz.org',
  password: 'testpass123'
};

const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:3001';

test.describe('👨‍👩‍👦 Parent Activity Viewing E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto(FRONTEND_URL);
  });

  test('T016.1: Parent can successfully login', async ({ page }) => {
    // Click login button
    await page.click('text=Login');

    // Fill in parent credentials
    await page.fill('input[type="email"]', PARENT_USER.email);
    await page.fill('input[type="password"]', PARENT_USER.password);

    // Submit login form
    await page.click('button[type="submit"]');

    // Wait for dashboard redirect
    await page.waitForURL('**/dashboard', { timeout: 10000 });

    // Verify parent role indicator
    await expect(page.locator('text=Parent Dashboard')).toBeVisible();

    // Verify parent-specific menu items
    await expect(page.locator('nav >> text=My Children')).toBeVisible();
    await expect(page.locator('nav >> text=Activity')).toBeVisible();
    await expect(page.locator('nav >> text=Progress')).toBeVisible();
  });

  test('T016.2: Parent can view children list', async ({ page }) => {
    await loginAsParent(page);

    // Navigate to children page
    await page.click('nav >> text=My Children');
    await page.waitForURL('**/children');

    // Verify children are listed
    await expect(page.locator('.children-list')).toBeVisible();

    // Check for child cards
    const childCards = page.locator('.child-card');
    await expect(childCards).toHaveCount({ min: 1 });

    // Verify child information displayed
    await expect(page.locator('text=Emma Johnson')).toBeVisible();
    await expect(page.locator('text=Age: 10')).toBeVisible();
    await expect(page.locator('text=Grade: 5')).toBeVisible();
  });

  test('T016.3: Parent can view child activity timeline', async ({ page }) => {
    await loginAsParent(page);

    // Navigate to activity page
    await page.click('nav >> text=Activity');
    await page.waitForURL('**/activity');

    // Verify activity timeline is visible
    await expect(page.locator('.activity-timeline')).toBeVisible();

    // Check for recent activities
    await expect(page.locator('text=Recent Interactions')).toBeVisible();

    // Verify activity entries
    const activityEntries = page.locator('.activity-entry');
    await expect(activityEntries.first()).toBeVisible();

    // Check activity details
    const firstActivity = activityEntries.first();
    await expect(firstActivity.locator('.activity-date')).toBeVisible();
    await expect(firstActivity.locator('.activity-animal')).toBeVisible();
    await expect(firstActivity.locator('.activity-duration')).toBeVisible();
  });

  test('T016.4: Parent can view conversation transcripts', async ({ page }) => {
    await loginAsParent(page);

    // Navigate to activity page
    await page.goto(`${FRONTEND_URL}/activity`);

    // Click on a specific interaction
    await page.click('.activity-entry:first-child button:has-text("View Details")');

    // Wait for transcript dialog
    await page.waitForSelector('.transcript-dialog');

    // Verify transcript is displayed
    await expect(page.locator('text=Conversation Transcript')).toBeVisible();
    await expect(page.locator('.message-list')).toBeVisible();

    // Check for messages
    const messages = page.locator('.message');
    await expect(messages).toHaveCount({ min: 1 });

    // Verify message structure
    const firstMessage = messages.first();
    await expect(firstMessage.locator('.message-sender')).toBeVisible();
    await expect(firstMessage.locator('.message-content')).toBeVisible();
    await expect(firstMessage.locator('.message-time')).toBeVisible();
  });

  test('T016.5: Parent can view learning progress', async ({ page }) => {
    await loginAsParent(page);

    // Navigate to progress page
    await page.click('nav >> text=Progress');
    await page.waitForURL('**/progress');

    // Verify progress dashboard
    await expect(page.locator('text=Learning Progress')).toBeVisible();

    // Check for progress metrics
    await expect(page.locator('[data-testid="total-sessions"]')).toBeVisible();
    await expect(page.locator('[data-testid="badges-earned"]')).toBeVisible();
    await expect(page.locator('[data-testid="knowledge-points"]')).toBeVisible();
    await expect(page.locator('[data-testid="favorite-animal"]')).toBeVisible();

    // Verify progress chart
    await expect(page.locator('.progress-chart')).toBeVisible();

    // Check for achievement badges
    await expect(page.locator('text=Achievements')).toBeVisible();
    await expect(page.locator('.badge-container')).toBeVisible();
  });

  test('T016.6: Parent can set interaction limits', async ({ page }) => {
    await loginAsParent(page);

    // Navigate to settings
    await page.goto(`${FRONTEND_URL}/settings`);

    // Click parental controls
    await page.click('button:has-text("Parental Controls")');

    // Wait for controls dialog
    await page.waitForSelector('.parental-controls-dialog');

    // Set daily time limit
    await page.fill('input[name="dailyTimeLimit"]', '60');

    // Set allowed hours
    await page.fill('input[name="allowedStartTime"]', '09:00');
    await page.fill('input[name="allowedEndTime"]', '20:00');

    // Set content restrictions
    await page.selectOption('select[name="contentLevel"]', 'age-appropriate');

    // Enable notifications
    await page.check('input[name="notifyOnNewSession"]');
    await page.check('input[name="weeklyProgressReport"]');

    // Save settings
    await page.click('button:has-text("Save Controls")');

    // Verify settings saved
    await expect(page.locator('.success-message')).toContainText('Parental controls updated');
  });

  test('T016.7: Parent can view favorite animals', async ({ page }) => {
    await loginAsParent(page);

    // Navigate to child profile
    await page.goto(`${FRONTEND_URL}/children`);
    await page.click('text=Emma Johnson');

    // Check favorite animals section
    await expect(page.locator('text=Favorite Animals')).toBeVisible();

    // Verify favorite animals list
    await expect(page.locator('.favorite-animals')).toBeVisible();

    // Check interaction stats for favorites
    const favoriteCard = page.locator('.favorite-animal-card').first();
    await expect(favoriteCard.locator('.animal-name')).toBeVisible();
    await expect(favoriteCard.locator('.interaction-count')).toBeVisible();
    await expect(favoriteCard.locator('.last-interaction')).toBeVisible();
  });

  test('T016.8: Parent can download activity reports', async ({ page }) => {
    await loginAsParent(page);

    // Navigate to activity page
    await page.goto(`${FRONTEND_URL}/activity`);

    // Click download report
    await page.click('button:has-text("Download Report")');

    // Wait for report dialog
    await page.waitForSelector('.report-options-dialog');

    // Select report period
    await page.selectOption('select[name="reportPeriod"]', 'last-month');

    // Select report format
    await page.selectOption('select[name="reportFormat"]', 'pdf');

    // Select content to include
    await page.check('input[name="includeTranscripts"]');
    await page.check('input[name="includeProgress"]');
    await page.check('input[name="includeAchievements"]');

    // Download report
    const [download] = await Promise.all([
      page.waitForEvent('download'),
      page.click('button:has-text("Download")')
    ]);

    // Verify download
    expect(download).toBeTruthy();
    const fileName = download.suggestedFilename();
    expect(fileName).toContain('activity-report');
    expect(fileName).toEndWith('.pdf');
  });

  test('T016.9: Parent can communicate with educator', async ({ page }) => {
    await loginAsParent(page);

    // Navigate to messages
    await page.goto(`${FRONTEND_URL}/messages`);

    // Click compose message
    await page.click('button:has-text("New Message")');

    // Wait for message dialog
    await page.waitForSelector('.compose-message-dialog');

    // Select recipient (educator)
    await page.selectOption('select[name="recipient"]', 'educator');

    // Fill message details
    await page.fill('input[name="subject"]', 'Question about wildlife program');
    await page.fill('textarea[name="message"]',
      'Hi, I wanted to ask about the upcoming virtual safari tour. Will Emma be able to participate?');

    // Send message
    await page.click('button:has-text("Send")');

    // Verify message sent
    await expect(page.locator('.success-message')).toContainText('Message sent');

    // Verify message appears in sent items
    await page.click('button[role="tab"]:has-text("Sent")');
    await expect(page.locator('text=Question about wildlife program')).toBeVisible();
  });

  test('T016.10: Parent can manage notification preferences', async ({ page }) => {
    await loginAsParent(page);

    // Navigate to settings
    await page.goto(`${FRONTEND_URL}/settings`);

    // Click notifications tab
    await page.click('button[role="tab"]:has-text("Notifications")');

    // Configure notification preferences
    await page.check('input[name="emailNewSession"]');
    await page.check('input[name="emailWeeklyReport"]');
    await page.uncheck('input[name="emailDailyDigest"]');

    // Set notification frequency
    await page.selectOption('select[name="reportFrequency"]', 'weekly');

    // Configure alert thresholds
    await page.fill('input[name="sessionLengthAlert"]', '90');

    // Enable push notifications
    await page.check('input[name="enablePushNotifications"]');

    // Save preferences
    await page.click('button:has-text("Save Preferences")');

    // Verify preferences saved
    await expect(page.locator('.success-message')).toContainText('Notification preferences updated');

    // Verify settings persist (reload page)
    await page.reload();
    await page.click('button[role="tab"]:has-text("Notifications")');

    // Check that emailWeeklyReport is still checked
    const weeklyReportCheckbox = page.locator('input[name="emailWeeklyReport"]');
    await expect(weeklyReportCheckbox).toBeChecked();
  });

  test('T016.11: Parent role-based restrictions', async ({ page }) => {
    await loginAsParent(page);

    // Verify cannot access admin features
    await page.goto(`${FRONTEND_URL}/system/ai-provider`);
    expect(page.url()).not.toContain('/system/ai-provider');

    // Verify cannot manage other families
    await page.goto(`${FRONTEND_URL}/families`);
    const createFamilyButtons = page.locator('button:has-text("Create Family")');
    await expect(createFamilyButtons).toHaveCount(0);

    // Verify cannot configure animals
    await page.goto(`${FRONTEND_URL}/animals`);
    const configureButtons = page.locator('button:has-text("Configure")');
    await expect(configureButtons).toHaveCount(0);

    // Verify CAN view own children (parent permission)
    await page.goto(`${FRONTEND_URL}/children`);
    await expect(page.locator('.children-list')).toBeVisible();

    // Verify CAN view activity (parent permission)
    await page.goto(`${FRONTEND_URL}/activity`);
    await expect(page.locator('.activity-timeline')).toBeVisible();
  });
});

// Helper function to login as parent
async function loginAsParent(page) {
  await page.goto(`${FRONTEND_URL}/login`);
  await page.fill('input[type="email"]', PARENT_USER.email);
  await page.fill('input[type="password"]', PARENT_USER.password);
  await page.click('button[type="submit"]');
  await page.waitForURL('**/dashboard', { timeout: 10000 });
}