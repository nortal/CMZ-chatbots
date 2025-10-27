/**
 * Critical Bug Validation: Data Loading Failures
 *
 * Tests for CRITICAL severity bugs:
 * 1. Assistant Management sub-elements non-functional
 * 2. Animal Details page shows "Failed to fetch" error
 * 3. Chat with Animals shows "Unable to load animals"
 * 4. Family Groups shows "Failed to load families"
 *
 * Session: Friday, October 24th, 2025 8:47 AM
 * Branch: 003-animal-assistant-mgmt
 */

const { test, expect } = require('@playwright/test');

const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:3001';
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8081';

// Test users with different roles
const TEST_USERS = {
  admin: {
    email: 'test@cmz.org',
    password: 'testpass123',
    role: 'admin'
  },
  parent: {
    email: 'parent1@test.cmz.org',
    password: 'testpass123',
    role: 'parent'
  }
};

/**
 * Helper: Login and navigate to authenticated state
 */
async function loginAs(page, userType) {
  const user = TEST_USERS[userType];

  await page.goto(FRONTEND_URL);
  await page.waitForLoadState('networkidle');

  // Check if already logged in (redirect to dashboard)
  if (page.url().includes('/dashboard')) {
    return 'already-logged-in';
  }

  // Fill login form
  await page.fill('input[type="email"]', user.email);
  await page.fill('input[type="password"]', user.password);

  // Submit and wait for successful navigation
  // Admin/Zookeeper -> /dashboard, Parent/Student/Visitor -> /animals
  const expectedPath = (user.role === 'admin' || user.role === 'zookeeper') ? /dashboard/ : /animals/;

  await Promise.all([
    page.waitForURL(expectedPath, { timeout: 15000 }),
    page.click('button[type="submit"]')
  ]);

  // Verify we're on the expected page
  expect(page.url()).toMatch(expectedPath);

  // Look for welcome message or user indicator (use first() to avoid multiple elements)
  await expect(page.locator('text=/Welcome|Dashboard|CMZ|Animal/').first()).toBeVisible({ timeout: 5000 });

  return 'login-successful';
}

test.describe('CRITICAL: Data Loading Failures', () => {

  test.describe('Bug #1: Assistant Management Sub-Elements Non-Functional', () => {

    test('should load Active Assistants section without errors', async ({ page }) => {
      // Given: Admin user is logged in
      await loginAs(page, 'admin');

      // When: Navigate to Assistant Management
      await page.goto(`${FRONTEND_URL}/assistants`);
      await page.waitForLoadState('networkidle');

      // Then: Active Assistants section should be visible and functional
      const activeAssistantsSection = page.locator('[data-testid="active-assistants"], :has-text("Active Assistants")');
      await expect(activeAssistantsSection).toBeVisible({ timeout: 5000 });

      // And: Should NOT show error messages
      await expect(page.locator('text=/failed to fetch|error loading|unable to load/i')).not.toBeVisible();

      // And: Should display assistant list or empty state
      const hasAssistants = await page.locator('[data-testid="assistant-list"] > *').count() > 0;
      const hasEmptyState = await page.locator('text=/no assistants|no active/i').isVisible();
      expect(hasAssistants || hasEmptyState).toBeTruthy();
    });

    test('should open Create Assistant dialog successfully', async ({ page }) => {
      // Given: Admin user is logged in and on Assistant Management page
      await loginAs(page, 'admin');
      await page.goto(`${FRONTEND_URL}/assistants`);
      await page.waitForLoadState('networkidle');

      // When: Click "Create Assistant" button
      const createButton = page.locator('button:has-text("Create Assistant"), button:has-text("Add Assistant")').first();
      await expect(createButton).toBeVisible({ timeout: 5000 });
      await createButton.click();

      // Then: Create Assistant dialog should open
      const dialog = page.locator('[role="dialog"], [data-testid="create-assistant-dialog"]');
      await expect(dialog).toBeVisible({ timeout: 5000 });

      // And: Dialog should have required form fields
      await expect(page.locator('input[name="name"], input[placeholder*="name" i]')).toBeVisible();

      // And: Should NOT show error messages in dialog
      await expect(dialog.locator('text=/failed to fetch|error loading/i')).not.toBeVisible();
    });

    test('should load Personality Templates section without errors', async ({ page }) => {
      // Given: Admin user is logged in
      await loginAs(page, 'admin');

      // When: Navigate to Personality Templates (may be subsection of Assistant Management)
      await page.goto(`${FRONTEND_URL}/assistants/personalities`);
      await page.waitForLoadState('networkidle');

      // Then: Personality Templates section should be visible
      const templatesSection = page.locator('[data-testid="personality-templates"], :has-text("Personality Templates")');
      await expect(templatesSection).toBeVisible({ timeout: 5000 });

      // And: Should NOT show error messages
      await expect(page.locator('text=/failed to fetch|error loading|unable to load/i')).not.toBeVisible();

      // And: Should display templates list or empty state
      const hasTemplates = await page.locator('[data-testid="template-list"] > *').count() > 0;
      const hasEmptyState = await page.locator('text=/no templates|no personalities/i').isVisible();
      expect(hasTemplates || hasEmptyState).toBeTruthy();
    });
  });

  test.describe('Bug #2: Animal Details Page Shows "Failed to Fetch" Error', () => {

    test('should load Animal Details page without "Failed to fetch" error', async ({ page }) => {
      // Given: Admin user is logged in
      await loginAs(page, 'admin');

      // When: Navigate to Animal Details page
      await page.goto(`${FRONTEND_URL}/animals`);
      await page.waitForLoadState('networkidle');

      // Then: Page should load successfully
      await expect(page.locator('h1, h2').filter({ hasText: /animal/i })).toBeVisible({ timeout: 5000 });

      // And: Should NOT show "Failed to fetch" error
      await expect(page.locator('text=/failed to fetch/i')).not.toBeVisible();

      // And: Should display animal list or loading indicator
      const hasAnimals = await page.locator('[data-testid="animal-list"], [data-testid="animal-card"]').count() > 0;
      const isLoading = await page.locator('text=/loading|please wait/i').isVisible();
      const hasEmptyState = await page.locator('text=/no animals/i').isVisible();

      expect(hasAnimals || isLoading || hasEmptyState).toBeTruthy();
    });

    test('should fetch animals from backend API successfully', async ({ page }) => {
      // Given: Admin user is logged in
      const token = await loginAs(page, 'admin');

      // When: Navigate to Animal Details and capture backend request
      const [animalResponse] = await Promise.all([
        page.waitForResponse(resp => resp.url().includes('/animal') && resp.request().method() === 'GET', { timeout: 10000 }),
        page.goto(`${FRONTEND_URL}/animals`)
      ]);

      // Then: Backend should respond successfully
      expect(animalResponse.status()).toBe(200);

      // And: Response should contain valid animal data
      const animals = await animalResponse.json();
      expect(Array.isArray(animals)).toBeTruthy();

      // And: UI should display the fetched animals
      await page.waitForLoadState('networkidle');

      if (animals.length > 0) {
        const firstAnimal = animals[0];
        if (firstAnimal.name) {
          await expect(page.locator(`text=${firstAnimal.name}`)).toBeVisible({ timeout: 5000 });
        }
      }
    });

    test('should handle backend unavailability gracefully', async ({ page }) => {
      // Given: Admin user is logged in
      await loginAs(page, 'admin');

      // When: Navigate to Animal Details with backend intercepted to fail
      await page.route('**/animal*', route => route.abort());
      await page.goto(`${FRONTEND_URL}/animals`);
      await page.waitForLoadState('networkidle');

      // Then: Should show user-friendly error message (not technical "Failed to fetch")
      const errorMessage = page.locator('text=/unable to load|service unavailable|try again/i');
      await expect(errorMessage).toBeVisible({ timeout: 5000 });

      // And: Should NOT show raw technical errors
      await expect(page.locator('text=/failed to fetch|network error|500/i')).not.toBeVisible();
    });
  });

  test.describe('Bug #3: Chat with Animals Shows "Unable to Load Animals"', () => {

    test('should load Chat with Animals page without errors', async ({ page }) => {
      // Given: Parent user is logged in (students/parents use chat)
      await loginAs(page, 'parent');

      // When: Navigate to Chat page
      await page.goto(`${FRONTEND_URL}/chat`);
      await page.waitForLoadState('networkidle');

      // Then: Should NOT show "Unable to load animals" error
      await expect(page.locator('text=/unable to load animals/i')).not.toBeVisible();

      // And: Should display animal selection or chat interface
      const hasAnimalSelector = await page.locator('[data-testid="animal-selector"], select[name="animal"]').isVisible();
      const hasChatInterface = await page.locator('[data-testid="chat-interface"], [data-testid="message-input"]').isVisible();

      expect(hasAnimalSelector || hasChatInterface).toBeTruthy();
    });

    test('should fetch available animals for chat successfully', async ({ page }) => {
      // Given: Parent user is logged in
      await loginAs(page, 'parent');

      // When: Navigate to Chat and capture animal fetch request
      const [animalResponse] = await Promise.all([
        page.waitForResponse(resp => resp.url().includes('/animal') && resp.request().method() === 'GET', { timeout: 10000 }),
        page.goto(`${FRONTEND_URL}/chat`)
      ]);

      // Then: Should receive valid animal list
      expect(animalResponse.status()).toBe(200);
      const animals = await animalResponse.json();
      expect(Array.isArray(animals)).toBeTruthy();

      // And: Animals should be displayed in selector
      await page.waitForLoadState('networkidle');

      if (animals.length > 0) {
        const animalSelector = page.locator('[data-testid="animal-selector"], select[name="animal"]');
        await expect(animalSelector).toBeVisible({ timeout: 5000 });
      }
    });

    test('should allow selecting an animal for chat', async ({ page }) => {
      // Given: Parent user is logged in on Chat page
      await loginAs(page, 'parent');
      await page.goto(`${FRONTEND_URL}/chat`);
      await page.waitForLoadState('networkidle');

      // When: Select an animal from the list
      const animalSelector = page.locator('[data-testid="animal-selector"], button:has-text("Select Animal")').first();
      await animalSelector.click();

      // Then: Animal list should be displayed
      const animalList = page.locator('[data-testid="animal-list"], [role="listbox"]');
      await expect(animalList).toBeVisible({ timeout: 5000 });

      // And: Clicking an animal should start chat session
      const firstAnimal = page.locator('[data-testid="animal-option"], [role="option"]').first();
      await firstAnimal.click();

      // And: Chat interface should be ready
      const messageInput = page.locator('[data-testid="message-input"], input[placeholder*="message" i]');
      await expect(messageInput).toBeVisible({ timeout: 5000 });
    });
  });

  test.describe('Bug #4: Family Groups Shows "Failed to Load Families"', () => {

    test('should load Family Groups page without "Failed to load" error', async ({ page }) => {
      // Given: Admin user is logged in
      await loginAs(page, 'admin');

      // When: Navigate to Family Groups page
      await page.goto(`${FRONTEND_URL}/families`);
      await page.waitForLoadState('networkidle');

      // Then: Should NOT show "Failed to load families" error
      await expect(page.locator('text=/failed to load families/i')).not.toBeVisible();

      // And: Should display family list or empty state
      const hasFamilies = await page.locator('[data-testid="family-list"], [data-testid="family-card"]').count() > 0;
      const hasEmptyState = await page.locator('text=/no families|add your first/i').isVisible();

      expect(hasFamilies || hasEmptyState).toBeTruthy();
    });

    test('should fetch families from backend successfully', async ({ page }) => {
      // Given: Admin user is logged in
      const token = await loginAs(page, 'admin');

      // When: Navigate to Family Groups and capture backend request
      const [familyResponse] = await Promise.all([
        page.waitForResponse(resp => resp.url().includes('/family') && resp.request().method() === 'GET', { timeout: 10000 }),
        page.goto(`${FRONTEND_URL}/families`)
      ]);

      // Then: Backend should respond successfully
      expect(familyResponse.status()).toBe(200);

      // And: Response should contain valid family data
      const families = await familyResponse.json();
      expect(Array.isArray(families)).toBeTruthy();

      // And: UI should display the fetched families
      await page.waitForLoadState('networkidle');

      if (families.length > 0) {
        const firstFamily = families[0];
        if (firstFamily.familyName) {
          await expect(page.locator(`text=${firstFamily.familyName}`)).toBeVisible({ timeout: 5000 });
        }
      }
    });

    test('should NOT fall back to demo data when DynamoDB is available', async ({ page }) => {
      // Given: Admin user is logged in
      await loginAs(page, 'admin');

      // When: Navigate to Family Groups
      await page.goto(`${FRONTEND_URL}/families`);
      await page.waitForLoadState('networkidle');

      // Then: Should NOT show "using demo data" message
      await expect(page.locator('text=/using demo data|demo mode/i')).not.toBeVisible();

      // And: Should display real data from DynamoDB
      const realDataIndicator = page.locator('[data-testid="family-list"]');
      await expect(realDataIndicator).toBeVisible({ timeout: 5000 });
    });

    test('should handle empty family list gracefully', async ({ page }) => {
      // Given: Admin user is logged in
      await loginAs(page, 'admin');

      // When: Navigate to Family Groups with no families in database
      // (Intercept to return empty array)
      await page.route('**/family*', route => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([])
        });
      });

      await page.goto(`${FRONTEND_URL}/families`);
      await page.waitForLoadState('networkidle');

      // Then: Should show appropriate empty state
      const emptyState = page.locator('text=/no families|add your first family/i');
      await expect(emptyState).toBeVisible({ timeout: 5000 });

      // And: Should NOT show error message
      await expect(page.locator('text=/failed to load|error/i')).not.toBeVisible();
    });
  });

  test.describe('Cross-Cutting: Backend Health Check', () => {

    test('should verify backend is healthy before testing data loads', async ({ page }) => {
      // Given: Backend service should be running
      const healthResponse = await page.request.get(`${BACKEND_URL}/health`).catch(() => null);

      // Then: Backend should respond to health check
      if (healthResponse) {
        expect(healthResponse.status()).toBe(200);
      } else {
        // If no health endpoint, check root endpoint
        const rootResponse = await page.request.get(BACKEND_URL);
        expect(rootResponse.status()).toBeLessThan(500);
      }
    });

    test('should verify all critical endpoints are available', async ({ page }) => {
      // Given: Admin user token
      const token = await loginAs(page, 'admin');

      // When: Check each critical endpoint
      const endpoints = [
        { path: '/animal', name: 'Animals' },
        { path: '/family', name: 'Families' },
        { path: '/user', name: 'Users' }
      ];

      for (const endpoint of endpoints) {
        // Then: Each endpoint should be accessible
        const response = await page.request.get(`${BACKEND_URL}${endpoint.path}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });

        expect(response.status(), `${endpoint.name} endpoint should be available`).toBeLessThan(500);
      }
    });
  });
});
