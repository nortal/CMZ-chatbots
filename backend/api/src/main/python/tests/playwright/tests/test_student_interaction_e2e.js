/**
 * E2E Test: Student Educational Interaction
 * Task T018: Create Playwright test for student interaction
 * Tests student-specific educational features and gamified learning
 */

const { test, expect } = require('@playwright/test');

// Test data
const STUDENT_USER = {
  email: 'student1@test.cmz.org',
  password: 'testpass123'
};

const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:3001';

test.describe('🎓 Student Interaction E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto(FRONTEND_URL);
  });

  test('T018.1: Student can successfully login', async ({ page }) => {
    // Click login button
    await page.click('text=Login');

    // Fill in student credentials
    await page.fill('input[type="email"]', STUDENT_USER.email);
    await page.fill('input[type="password"]', STUDENT_USER.password);

    // Submit login form
    await page.click('button[type="submit"]');

    // Wait for dashboard redirect
    await page.waitForURL('**/dashboard', { timeout: 10000 });

    // Verify student role indicator
    await expect(page.locator('text=Student Dashboard')).toBeVisible();

    // Verify student-specific features
    await expect(page.locator('nav >> text=Learn')).toBeVisible();
    await expect(page.locator('nav >> text=Animals')).toBeVisible();
    await expect(page.locator('nav >> text=Achievements')).toBeVisible();
    await expect(page.locator('nav >> text=My Progress')).toBeVisible();
  });

  test('T018.2: Student can view learning dashboard', async ({ page }) => {
    await loginAsStudent(page);

    // Navigate to learn page
    await page.click('nav >> text=Learn');
    await page.waitForURL('**/learn');

    // Verify learning modules
    await expect(page.locator('text=Today\'s Lessons')).toBeVisible();
    await expect(page.locator('.lesson-card')).toHaveCount({ min: 1 });

    // Check for progress indicators
    await expect(page.locator('[data-testid="lessons-completed"]')).toBeVisible();
    await expect(page.locator('[data-testid="points-earned"]')).toBeVisible();
    await expect(page.locator('[data-testid="current-streak"]')).toBeVisible();

    // Verify recommended animals
    await expect(page.locator('text=Recommended Animals to Meet')).toBeVisible();
    await expect(page.locator('.recommended-animal')).toHaveCount({ min: 2 });
  });

  test('T018.3: Student can start educational chat', async ({ page }) => {
    await loginAsStudent(page);

    // Navigate to animals
    await page.goto(`${FRONTEND_URL}/animals`);

    // Start chat with educational focus
    await page.click('.animal-card:first button:has-text("Learn About Me")');

    // Wait for educational chat interface
    await page.waitForSelector('.educational-chat');

    // Verify educational elements
    await expect(page.locator('.learning-objectives')).toBeVisible();
    await expect(page.locator('.knowledge-tracker')).toBeVisible();
    await expect(page.locator('.hint-button')).toBeVisible();

    // Check for age-appropriate greeting
    const greeting = page.locator('.message.animal-message').first();
    await expect(greeting).toContainText(/Hi|Hello|Hey there/i);
  });

  test('T018.4: Student can complete learning objectives', async ({ page }) => {
    await loginAsStudent(page);

    // Start educational chat
    await page.goto(`${FRONTEND_URL}/animals`);
    await page.click('.animal-card:first button:has-text("Learn About Me")');
    await page.waitForSelector('.educational-chat');

    // View learning objectives
    await page.click('.learning-objectives-toggle');
    await expect(page.locator('.objective-list')).toBeVisible();

    // Complete first objective (e.g., learn about habitat)
    await page.fill('.chat-input input', 'Where do you live?');
    await page.click('button:has-text("Send")');

    // Wait for response
    await page.waitForSelector('.message.animal-message:nth-child(2)', { timeout: 10000 });

    // Verify objective marked complete
    await expect(page.locator('.objective-complete:first')).toBeVisible();

    // Check points earned notification
    await expect(page.locator('.points-notification')).toBeVisible();
    await expect(page.locator('.points-notification')).toContainText('+10 points');
  });

  test('T018.5: Student can play educational quiz', async ({ page }) => {
    await loginAsStudent(page);

    // Start chat and trigger quiz
    await page.goto(`${FRONTEND_URL}/animals`);
    await page.click('.animal-card:first button:has-text("Learn About Me")');
    await page.waitForSelector('.educational-chat');

    // Request quiz
    await page.fill('.chat-input input', 'Can we play a quiz?');
    await page.click('button:has-text("Send")');

    // Wait for quiz to start
    await page.waitForSelector('.quiz-container', { timeout: 10000 });

    // Verify quiz interface
    await expect(page.locator('.quiz-question')).toBeVisible();
    await expect(page.locator('.quiz-options')).toBeVisible();
    await expect(page.locator('.quiz-progress')).toBeVisible();

    // Answer question
    await page.click('.quiz-option:first');

    // Verify feedback
    await expect(page.locator('.quiz-feedback')).toBeVisible();

    // Check for next question or completion
    await page.waitForSelector('.quiz-question:nth-child(2), .quiz-complete', { timeout: 5000 });
  });

  test('T018.6: Student can earn badges', async ({ page }) => {
    await loginAsStudent(page);

    // Navigate to achievements
    await page.click('nav >> text=Achievements');
    await page.waitForURL('**/achievements');

    // Verify badge display
    await expect(page.locator('text=My Badges')).toBeVisible();
    await expect(page.locator('.badge-grid')).toBeVisible();

    // Check for earned badges
    const earnedBadges = page.locator('.badge.earned');
    const earnedCount = await earnedBadges.count();

    // Check for locked badges
    const lockedBadges = page.locator('.badge.locked');
    await expect(lockedBadges).toHaveCount({ min: 1 });

    // View badge details
    if (earnedCount > 0) {
      await earnedBadges.first().click();
      await page.waitForSelector('.badge-details-dialog');

      // Verify badge information
      await expect(page.locator('.badge-name')).toBeVisible();
      await expect(page.locator('.badge-description')).toBeVisible();
      await expect(page.locator('.badge-earned-date')).toBeVisible();
    }

    // Check progress towards next badge
    await expect(page.locator('.next-badge-progress')).toBeVisible();
  });

  test('T018.7: Student can track learning streaks', async ({ page }) => {
    await loginAsStudent(page);

    // Navigate to progress page
    await page.click('nav >> text=My Progress');
    await page.waitForURL('**/progress');

    // Verify streak display
    await expect(page.locator('.streak-counter')).toBeVisible();
    await expect(page.locator('.streak-calendar')).toBeVisible();

    // Check streak details
    const currentStreak = page.locator('[data-testid="current-streak-days"]');
    await expect(currentStreak).toBeVisible();

    const bestStreak = page.locator('[data-testid="best-streak-days"]');
    await expect(bestStreak).toBeVisible();

    // Verify calendar marks
    const activeDays = page.locator('.calendar-day.active');
    await expect(activeDays).toHaveCount({ min: 1 });
  });

  test('T018.8: Student can access age-appropriate content', async ({ page }) => {
    await loginAsStudent(page);

    // Start chat
    await page.goto(`${FRONTEND_URL}/animals`);
    await page.click('.animal-card:has-text("Lion") button:has-text("Learn About Me")');
    await page.waitForSelector('.educational-chat');

    // Ask potentially sensitive question
    await page.fill('.chat-input input', 'How do you hunt?');
    await page.click('button:has-text("Send")');

    // Wait for response
    await page.waitForSelector('.message.animal-message:nth-child(2)', { timeout: 10000 });

    // Verify response is age-appropriate (no graphic content)
    const response = page.locator('.message.animal-message').nth(1);
    const responseText = await response.textContent();

    // Should not contain graphic terms
    expect(responseText).not.toMatch(/blood|kill|death|violent/i);

    // Should contain educational content
    expect(responseText).toMatch(/food|eat|nature|survive/i);
  });

  test('T018.9: Student can view learning history', async ({ page }) => {
    await loginAsStudent(page);

    // Navigate to progress page
    await page.goto(`${FRONTEND_URL}/progress`);

    // Click learning history tab
    await page.click('button[role="tab"]:has-text("Learning History")');

    // Verify history display
    await expect(page.locator('.learning-history-timeline')).toBeVisible();

    // Check for past sessions
    const historyEntries = page.locator('.history-entry');
    await expect(historyEntries.first()).toBeVisible();

    // View session details
    await historyEntries.first().click();
    await page.waitForSelector('.session-details-dialog');

    // Verify session information
    await expect(page.locator('.session-date')).toBeVisible();
    await expect(page.locator('.session-animal')).toBeVisible();
    await expect(page.locator('.session-duration')).toBeVisible();
    await expect(page.locator('.session-points')).toBeVisible();
    await expect(page.locator('.session-objectives')).toBeVisible();
  });

  test('T018.10: Student can participate in group challenges', async ({ page }) => {
    await loginAsStudent(page);

    // Navigate to challenges
    await page.goto(`${FRONTEND_URL}/challenges`);

    // Verify challenges display
    await expect(page.locator('text=Current Challenges')).toBeVisible();
    await expect(page.locator('.challenge-card')).toHaveCount({ min: 1 });

    // Join a challenge
    const activeChallenge = page.locator('.challenge-card:has(.status-active)').first();
    await activeChallenge.click('button:has-text("Join Challenge")');

    // Verify joined
    await expect(page.locator('.success-message')).toContainText('Joined challenge');

    // Check challenge details
    await expect(page.locator('.challenge-leaderboard')).toBeVisible();
    await expect(page.locator('.my-challenge-progress')).toBeVisible();
    await expect(page.locator('.challenge-deadline')).toBeVisible();
  });

  test('T018.11: Student can use hints during learning', async ({ page }) => {
    await loginAsStudent(page);

    // Start educational chat
    await page.goto(`${FRONTEND_URL}/animals`);
    await page.click('.animal-card:first button:has-text("Learn About Me")');
    await page.waitForSelector('.educational-chat');

    // Ask a challenging question
    await page.fill('.chat-input input', 'What is your scientific name?');
    await page.click('button:has-text("Send")');

    // Use hint button
    await page.click('button:has-text("Get Hint")');

    // Verify hint appears
    await page.waitForSelector('.hint-bubble');
    await expect(page.locator('.hint-bubble')).toBeVisible();
    await expect(page.locator('.hint-bubble')).toContainText(/Latin|scientific|genus|species/i);

    // Verify hint doesn't give full answer
    const hintText = await page.locator('.hint-bubble').textContent();
    expect(hintText.length).toBeLessThan(100); // Hints should be brief
  });

  test('T018.12: Student learning preferences are saved', async ({ page }) => {
    await loginAsStudent(page);

    // Navigate to settings
    await page.goto(`${FRONTEND_URL}/settings`);

    // Click learning preferences
    await page.click('button[role="tab"]:has-text("Learning Preferences")');

    // Set preferences
    await page.selectOption('select[name="difficultyLevel"]', 'intermediate');
    await page.check('input[name="enableQuizzes"]');
    await page.check('input[name="showHints"]');
    await page.uncheck('input[name="enableSound"]');

    // Select favorite topics
    await page.check('input[value="habitats"]');
    await page.check('input[value="diet"]');
    await page.check('input[value="conservation"]');

    // Save preferences
    await page.click('button:has-text("Save Preferences")');

    // Verify saved
    await expect(page.locator('.success-message')).toContainText('Preferences saved');

    // Reload and verify persistence
    await page.reload();
    await page.click('button[role="tab"]:has-text("Learning Preferences")');

    // Check that difficulty is still set
    const difficulty = await page.inputValue('select[name="difficultyLevel"]');
    expect(difficulty).toBe('intermediate');

    // Check that enableQuizzes is still checked
    const quizCheckbox = page.locator('input[name="enableQuizzes"]');
    await expect(quizCheckbox).toBeChecked();
  });

  test('T018.13: Student role-based restrictions', async ({ page }) => {
    await loginAsStudent(page);

    // Verify cannot access admin features
    await page.goto(`${FRONTEND_URL}/system/ai-provider`);
    expect(page.url()).not.toContain('/system/ai-provider');

    // Verify cannot manage families
    await page.goto(`${FRONTEND_URL}/families`);
    const createButtons = page.locator('button:has-text("Create")');
    await expect(createButtons).toHaveCount(0);

    // Verify cannot configure animals
    await page.goto(`${FRONTEND_URL}/animals`);
    const configButtons = page.locator('button:has-text("Configure")');
    await expect(configButtons).toHaveCount(0);

    // Verify CAN access learning features
    await page.goto(`${FRONTEND_URL}/learn`);
    await expect(page.locator('.lesson-card')).toBeVisible();

    // Verify CAN chat with animals
    await page.goto(`${FRONTEND_URL}/animals`);
    await expect(page.locator('button:has-text("Learn About Me")')).toBeVisible();
  });
});

// Helper function to login as student
async function loginAsStudent(page) {
  await page.goto(`${FRONTEND_URL}/login`);
  await page.fill('input[type="email"]', STUDENT_USER.email);
  await page.fill('input[type="password"]', STUDENT_USER.password);
  await page.click('button[type="submit"]');
  await page.waitForURL('**/dashboard', { timeout: 10000 });
}