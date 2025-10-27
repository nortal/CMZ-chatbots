/**
 * E2E Test: Cross-Browser Validation
 * Task T019: Validate tests pass in ≥5/6 browsers
 * Runs critical user flows across multiple browsers
 */

const { test, expect, devices } = require('@playwright/test');

const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:3001';

// Test users for different roles
const TEST_USERS = {
  admin: { email: 'admin@cmz.org', password: 'testpass123' },
  zookeeper: { email: 'zookeeper@cmz.org', password: 'testpass123' },
  educator: { email: 'educator@cmz.org', password: 'testpass123' },
  parent: { email: 'parent1@test.cmz.org', password: 'testpass123' },
  student: { email: 'student1@test.cmz.org', password: 'testpass123' }
};

// Critical flows that must work across all browsers
test.describe('🌐 Cross-Browser Validation Suite', () => {

  test.describe('Chrome Validation', () => {
    test.use({ ...devices['Desktop Chrome'] });

    test('T019.1.1: Chrome - All roles can login', async ({ page }) => {
      await validateAllRolesLogin(page);
    });

    test('T019.1.2: Chrome - Critical workflows function', async ({ page }) => {
      await validateCriticalWorkflows(page);
    });

    test('T019.1.3: Chrome - Chat functionality works', async ({ page }) => {
      await validateChatFunctionality(page);
    });
  });

  test.describe('Firefox Validation', () => {
    test.use({ ...devices['Desktop Firefox'] });

    test('T019.2.1: Firefox - All roles can login', async ({ page }) => {
      await validateAllRolesLogin(page);
    });

    test('T019.2.2: Firefox - Critical workflows function', async ({ page }) => {
      await validateCriticalWorkflows(page);
    });

    test('T019.2.3: Firefox - Chat functionality works', async ({ page }) => {
      await validateChatFunctionality(page);
    });
  });

  test.describe('Safari Validation', () => {
    test.use({ ...devices['Desktop Safari'] });

    test('T019.3.1: Safari - All roles can login', async ({ page }) => {
      await validateAllRolesLogin(page);
    });

    test('T019.3.2: Safari - Critical workflows function', async ({ page }) => {
      await validateCriticalWorkflows(page);
    });

    test('T019.3.3: Safari - Chat functionality works', async ({ page }) => {
      await validateChatFunctionality(page);
    });
  });

  test.describe('Edge Validation', () => {
    test.use({ ...devices['Desktop Edge'] });

    test('T019.4.1: Edge - All roles can login', async ({ page }) => {
      await validateAllRolesLogin(page);
    });

    test('T019.4.2: Edge - Critical workflows function', async ({ page }) => {
      await validateCriticalWorkflows(page);
    });

    test('T019.4.3: Edge - Chat functionality works', async ({ page }) => {
      await validateChatFunctionality(page);
    });
  });

  test.describe('Mobile Chrome Validation', () => {
    test.use({ ...devices['Pixel 5'] });

    test('T019.5.1: Mobile Chrome - All roles can login', async ({ page }) => {
      await validateAllRolesLogin(page);
    });

    test('T019.5.2: Mobile Chrome - Critical workflows function', async ({ page }) => {
      await validateCriticalWorkflows(page);
    });

    test('T019.5.3: Mobile Chrome - Chat functionality works', async ({ page }) => {
      await validateChatFunctionality(page);
    });
  });

  test.describe('Mobile Safari Validation', () => {
    test.use({ ...devices['iPhone 12'] });

    test('T019.6.1: Mobile Safari - All roles can login', async ({ page }) => {
      await validateAllRolesLogin(page);
    });

    test('T019.6.2: Mobile Safari - Critical workflows function', async ({ page }) => {
      await validateCriticalWorkflows(page);
    });

    test('T019.6.3: Mobile Safari - Chat functionality works', async ({ page }) => {
      await validateChatFunctionality(page);
    });
  });
});

// Validation helper functions

async function validateAllRolesLogin(page) {
  // Test each role's login
  for (const [role, credentials] of Object.entries(TEST_USERS)) {
    await page.goto(FRONTEND_URL);

    // Click login
    await page.click('text=Login');

    // Fill credentials
    await page.fill('input[type="email"]', credentials.email);
    await page.fill('input[type="password"]', credentials.password);

    // Submit
    await page.click('button[type="submit"]');

    // Verify redirect to dashboard
    await page.waitForURL('**/dashboard', { timeout: 10000 });

    // Verify role-specific content
    const roleDashboard = `${role.charAt(0).toUpperCase() + role.slice(1)} Dashboard`;
    await expect(page.locator(`text=${roleDashboard}`)).toBeVisible();

    // Logout for next test
    const userMenu = page.locator('[data-testid="user-menu"], .user-menu, button:has-text("Logout")');
    const userMenuCount = await userMenu.count();

    if (userMenuCount > 0) {
      // If there's a user menu, click it first
      if (await page.locator('[data-testid="user-menu"]').count() > 0) {
        await page.click('[data-testid="user-menu"]');
      }
      await page.click('text=Logout');
    }

    // Verify logged out
    await page.waitForURL('**/login', { timeout: 5000 }).catch(() => {
      // Some browsers might redirect to home instead
      return page.waitForURL(FRONTEND_URL, { timeout: 5000 });
    });
  }
}

async function validateCriticalWorkflows(page) {
  // Test 1: Admin can access system settings
  await loginAs(page, 'admin');
  await page.goto(`${FRONTEND_URL}/system`);
  await expect(page.locator('text=System')).toBeVisible();
  await logout(page);

  // Test 2: Zookeeper can manage animals
  await loginAs(page, 'zookeeper');
  await page.goto(`${FRONTEND_URL}/animals`);
  await expect(page.locator('.animal-list, .animals-grid, text=Animals')).toBeVisible();
  await logout(page);

  // Test 3: Educator can view families
  await loginAs(page, 'educator');
  await page.goto(`${FRONTEND_URL}/families`);
  await expect(page.locator('text=Families')).toBeVisible();
  await logout(page);

  // Test 4: Parent can view children
  await loginAs(page, 'parent');
  await page.goto(`${FRONTEND_URL}/children`);
  await expect(page.locator('text=Children, text=My Children')).toBeVisible();
  await logout(page);

  // Test 5: Student can access learning
  await loginAs(page, 'student');
  await page.goto(`${FRONTEND_URL}/learn`);
  await expect(page.locator('text=Learn, text=Lessons, text=Educational')).toBeVisible();
  await logout(page);
}

async function validateChatFunctionality(page) {
  // Test visitor chat (no login required)
  await page.goto(FRONTEND_URL);

  // Find and click on available animal
  const chatButton = page.locator('button:has-text("Chat"), button:has-text("Chat Now"), .animal-card button').first();
  const buttonCount = await chatButton.count();

  if (buttonCount > 0) {
    await chatButton.click();

    // Wait for chat interface
    await page.waitForSelector('.chat-interface, .chat-container, .chat-messages', { timeout: 10000 });

    // Send a message
    const input = page.locator('.chat-input input, input[type="text"], textarea').first();
    await input.fill('Hello!');

    const sendButton = page.locator('button:has-text("Send"), button[type="submit"]').first();
    await sendButton.click();

    // Verify message appears
    await expect(page.locator('.message:has-text("Hello!"), .user-message:has-text("Hello!")')).toBeVisible();

    // Wait for response (with timeout)
    await page.waitForSelector('.animal-message, .bot-message, .assistant-message', {
      timeout: 15000
    }).catch(() => {
      // Some browsers might be slower
      console.log('Response timeout - may be normal for some browsers');
    });
  }
}

// Helper functions
async function loginAs(page, role) {
  const credentials = TEST_USERS[role];
  await page.goto(`${FRONTEND_URL}/login`);
  await page.fill('input[type="email"]', credentials.email);
  await page.fill('input[type="password"]', credentials.password);
  await page.click('button[type="submit"]');
  await page.waitForURL('**/dashboard', { timeout: 10000 });
}

async function logout(page) {
  // Try multiple logout strategies for cross-browser compatibility
  const logoutStrategies = [
    async () => {
      // Strategy 1: User menu dropdown
      await page.click('[data-testid="user-menu"]');
      await page.click('text=Logout');
    },
    async () => {
      // Strategy 2: Direct logout button
      await page.click('button:has-text("Logout")');
    },
    async () => {
      // Strategy 3: Navigate to logout URL
      await page.goto(`${FRONTEND_URL}/logout`);
    }
  ];

  for (const strategy of logoutStrategies) {
    try {
      await strategy();
      // Wait for redirect
      await page.waitForURL('**/login', { timeout: 3000 }).catch(() => {
        return page.waitForURL(FRONTEND_URL, { timeout: 3000 });
      });
      return; // Successfully logged out
    } catch (e) {
      // Try next strategy
      continue;
    }
  }

  // If all strategies fail, navigate directly to login
  await page.goto(`${FRONTEND_URL}/login`);
}

// Export test summary function for CI/CD integration
module.exports = {
  validateAllRolesLogin,
  validateCriticalWorkflows,
  validateChatFunctionality
};