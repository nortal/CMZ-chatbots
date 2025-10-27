/**
 * High Severity Bug Validation: Dialog Functionality Issues
 *
 * Tests for HIGH severity bugs:
 * 5. Create Sandbox Assistant dialog cancel button doesn't work
 * 6. Guardrails disappear after closing creation dialog and returning to page
 * 7. Chat History shows "no sessions found" and "not authenticated" for admin users
 *
 * Session: Friday, October 24th, 2025 8:47 AM
 * Branch: 003-animal-assistant-mgmt
 */

const { test, expect } = require('@playwright/test');

const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:3001';
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8081';

// Test users
const ADMIN_USER = {
  email: 'test@cmz.org',
  password: 'testpass123',
  role: 'admin'
};

/**
 * Helper: Login as admin
 */
async function loginAsAdmin(page) {
  await page.goto(FRONTEND_URL);
  await page.waitForLoadState('networkidle');

  // Check if already logged in (redirect to dashboard)
  if (page.url().includes('/dashboard')) {
    return 'already-logged-in';
  }

  // Fill login form
  await page.fill('input[type="email"]', ADMIN_USER.email);
  await page.fill('input[type="password"]', ADMIN_USER.password);

  // Submit and wait for successful navigation
  // Admin/Zookeeper -> /dashboard, Parent/Student/Visitor -> /animals
  const expectedPath = (ADMIN_USER.role === 'admin' || ADMIN_USER.role === 'zookeeper') ? /dashboard/ : /animals/;

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

test.describe('HIGH SEVERITY: Dialog Functionality Issues', () => {

  test.describe('Bug #5: Create Sandbox Assistant Dialog Cancel Button', () => {

    test('should close Create Sandbox Assistant dialog when Cancel is clicked', async ({ page }) => {
      // Given: Admin user is logged in and on Sandbox/Assistant page
      await loginAsAdmin(page);
      await page.goto(`${FRONTEND_URL}/assistants/sandbox`);
      await page.waitForLoadState('networkidle');

      // When: Open Create Sandbox Assistant dialog
      const createButton = page.locator('button:has-text("Create Sandbox"), button:has-text("New Sandbox")').first();
      await createButton.click();

      // Then: Dialog should be visible
      const dialog = page.locator('[role="dialog"], [data-testid="sandbox-dialog"]');
      await expect(dialog).toBeVisible({ timeout: 5000 });

      // When: Click Cancel button
      const cancelButton = dialog.locator('button:has-text("Cancel")');
      await expect(cancelButton).toBeVisible();
      await expect(cancelButton).toBeEnabled();
      await cancelButton.click();

      // Then: Dialog should close
      await expect(dialog).not.toBeVisible({ timeout: 3000 });

      // And: Should return to sandbox list page
      await expect(page.locator('button:has-text("Create Sandbox"), button:has-text("New Sandbox")')).toBeVisible();
    });

    test('should NOT submit form data when Cancel is clicked', async ({ page }) => {
      // Given: Admin user is logged in and dialog is open
      await loginAsAdmin(page);
      await page.goto(`${FRONTEND_URL}/assistants/sandbox`);
      await page.waitForLoadState('networkidle');

      const createButton = page.locator('button:has-text("Create Sandbox"), button:has-text("New Sandbox")').first();
      await createButton.click();

      const dialog = page.locator('[role="dialog"], [data-testid="sandbox-dialog"]');
      await expect(dialog).toBeVisible({ timeout: 5000 });

      // When: Fill form with test data
      const nameInput = dialog.locator('input[name="name"], input[placeholder*="name" i]').first();
      await nameInput.fill('Test Sandbox Assistant');

      // And: Setup request interceptor to detect POST requests
      let requestMade = false;
      page.on('request', request => {
        if (request.url().includes('/sandbox') && request.method() === 'POST') {
          requestMade = true;
        }
      });

      // And: Click Cancel
      const cancelButton = dialog.locator('button:has-text("Cancel")');
      await cancelButton.click();
      await page.waitForTimeout(1000); // Give time for any accidental request

      // Then: Should NOT have made POST request
      expect(requestMade).toBe(false);

      // And: Dialog should be closed
      await expect(dialog).not.toBeVisible();
    });

    test('should clear form data after canceling and reopening dialog', async ({ page }) => {
      // Given: Admin user is logged in
      await loginAsAdmin(page);
      await page.goto(`${FRONTEND_URL}/assistants/sandbox`);
      await page.waitForLoadState('networkidle');

      // When: Open dialog and fill form
      const createButton = page.locator('button:has-text("Create Sandbox"), button:has-text("New Sandbox")').first();
      await createButton.click();

      const dialog = page.locator('[role="dialog"], [data-testid="sandbox-dialog"]');
      await expect(dialog).toBeVisible({ timeout: 5000 });

      const nameInput = dialog.locator('input[name="name"], input[placeholder*="name" i]').first();
      await nameInput.fill('Test Data To Be Cleared');

      // And: Cancel dialog
      await dialog.locator('button:has-text("Cancel")').click();
      await expect(dialog).not.toBeVisible();

      // And: Reopen dialog
      await createButton.click();
      await expect(dialog).toBeVisible({ timeout: 5000 });

      // Then: Form should be empty
      const clearedInput = dialog.locator('input[name="name"], input[placeholder*="name" i]').first();
      const value = await clearedInput.inputValue();
      expect(value).toBe('');
    });

    test('should handle Escape key to close dialog', async ({ page }) => {
      // Given: Admin user with open Create Sandbox dialog
      await loginAsAdmin(page);
      await page.goto(`${FRONTEND_URL}/assistants/sandbox`);
      await page.waitForLoadState('networkidle');

      const createButton = page.locator('button:has-text("Create Sandbox"), button:has-text("New Sandbox")').first();
      await createButton.click();

      const dialog = page.locator('[role="dialog"], [data-testid="sandbox-dialog"]');
      await expect(dialog).toBeVisible({ timeout: 5000 });

      // When: Press Escape key
      await page.keyboard.press('Escape');

      // Then: Dialog should close
      await expect(dialog).not.toBeVisible({ timeout: 3000 });
    });
  });

  test.describe('Bug #6: Guardrails Disappear After Closing Creation Dialog', () => {

    test('should persist existing guardrails after opening and closing creation dialog', async ({ page }) => {
      // Given: Admin user is logged in and on Guardrails page
      await loginAsAdmin(page);
      await page.goto(`${FRONTEND_URL}/safety/guardrails`);
      await page.waitForLoadState('networkidle');

      // And: Capture existing guardrails count before opening dialog
      const guardrailListBefore = page.locator('[data-testid="guardrail-list"], [data-testid="guardrail-item"]');
      const countBefore = await guardrailListBefore.count();

      // When: Open Create Guardrail dialog
      const createButton = page.locator('button:has-text("Create Guardrail"), button:has-text("Add Guardrail")').first();
      await createButton.click();

      const dialog = page.locator('[role="dialog"], [data-testid="guardrail-dialog"]');
      await expect(dialog).toBeVisible({ timeout: 5000 });

      // And: Close dialog without creating
      const cancelButton = dialog.locator('button:has-text("Cancel"), button:has-text("Close")').first();
      await cancelButton.click();
      await expect(dialog).not.toBeVisible({ timeout: 3000 });

      // Then: Guardrails should still be displayed
      await page.waitForLoadState('networkidle');
      const guardrailListAfter = page.locator('[data-testid="guardrail-list"], [data-testid="guardrail-item"]');
      const countAfter = await guardrailListAfter.count();

      expect(countAfter).toBe(countBefore);

      // And: Should NOT show empty state if guardrails existed before
      if (countBefore > 0) {
        await expect(page.locator('text=/no guardrails|no rules/i')).not.toBeVisible();
      }
    });

    test('should maintain guardrails visibility after page navigation and return', async ({ page }) => {
      // Given: Admin user is on Guardrails page with existing guardrails
      await loginAsAdmin(page);
      await page.goto(`${FRONTEND_URL}/safety/guardrails`);
      await page.waitForLoadState('networkidle');

      // Capture existing guardrails
      const guardrailList = page.locator('[data-testid="guardrail-list"], [data-testid="guardrail-item"]');
      const initialCount = await guardrailList.count();

      // When: Navigate away
      await page.goto(`${FRONTEND_URL}/dashboard`);
      await page.waitForLoadState('networkidle');

      // And: Return to Guardrails page
      await page.goto(`${FRONTEND_URL}/safety/guardrails`);
      await page.waitForLoadState('networkidle');

      // Then: Guardrails should still be visible
      const finalCount = await guardrailList.count();
      expect(finalCount).toBe(initialCount);
    });

    test('should refresh guardrails list after dialog interactions', async ({ page }) => {
      // Given: Admin user on Guardrails page
      await loginAsAdmin(page);
      await page.goto(`${FRONTEND_URL}/safety/guardrails`);
      await page.waitForLoadState('networkidle');

      // When: Open and close dialog multiple times
      const createButton = page.locator('button:has-text("Create Guardrail"), button:has-text("Add Guardrail")').first();
      const dialog = page.locator('[role="dialog"], [data-testid="guardrail-dialog"]');

      for (let i = 0; i < 3; i++) {
        await createButton.click();
        await expect(dialog).toBeVisible({ timeout: 3000 });

        const cancelButton = dialog.locator('button:has-text("Cancel"), button:has-text("Close")').first();
        await cancelButton.click();
        await expect(dialog).not.toBeVisible({ timeout: 3000 });
      }

      // Then: Guardrails should still be displayed and not duplicated
      await page.waitForLoadState('networkidle');
      const guardrailItems = page.locator('[data-testid="guardrail-item"]');
      const count = await guardrailItems.count();

      // Verify no duplicate rendering
      if (count > 0) {
        const firstGuardrail = await guardrailItems.first().textContent();
        const duplicates = await guardrailItems.filter({ hasText: firstGuardrail }).count();
        expect(duplicates).toBe(1); // Should only appear once
      }
    });
  });

  test.describe('Bug #7: Chat History Authentication Issues', () => {

    test('should NOT show "not authenticated" error for logged-in admin users', async ({ page }) => {
      // Given: Admin user is logged in
      const token = await loginAsAdmin(page);

      // When: Navigate to Chat History page
      await page.goto(`${FRONTEND_URL}/chat/history`);
      await page.waitForLoadState('networkidle');

      // Then: Should NOT show "not authenticated" error
      await expect(page.locator('text=/not authenticated|please log in/i')).not.toBeVisible();

      // And: Page should be accessible
      await expect(page.locator('h1, h2').filter({ hasText: /chat history|conversation history/i })).toBeVisible({ timeout: 5000 });
    });

    test('should fetch chat history successfully for admin users', async ({ page }) => {
      // Given: Admin user is logged in
      const token = await loginAsAdmin(page);

      // When: Navigate to Chat History and capture backend request
      const [historyResponse] = await Promise.all([
        page.waitForResponse(resp =>
          resp.url().includes('/conversation') || resp.url().includes('/chat/history'),
          { timeout: 10000 }
        ),
        page.goto(`${FRONTEND_URL}/chat/history`)
      ]);

      // Then: Should receive successful response
      expect(historyResponse.status()).toBe(200);

      // And: Should include auth token in request
      const requestHeaders = historyResponse.request().headers();
      expect(requestHeaders.authorization || requestHeaders.Authorization).toBeTruthy();
    });

    test('should display chat sessions when they exist', async ({ page }) => {
      // Given: Admin user with existing chat sessions
      const token = await loginAsAdmin(page);

      // When: Navigate to Chat History
      await page.goto(`${FRONTEND_URL}/chat/history`);
      await page.waitForLoadState('networkidle');

      // Then: Should either show sessions or appropriate empty state
      const hasSessions = await page.locator('[data-testid="chat-session"], [data-testid="conversation-item"]').count() > 0;
      const hasEmptyState = await page.locator('text=/no sessions found|no conversations yet/i').isVisible();

      expect(hasSessions || hasEmptyState).toBeTruthy();

      // And: Should NOT show "not authenticated" if authenticated
      await expect(page.locator('text=/not authenticated/i')).not.toBeVisible();
    });

    test('should handle empty chat history gracefully', async ({ page }) => {
      // Given: Admin user with no chat sessions
      const token = await loginAsAdmin(page);

      // Mock empty response
      await page.route('**/conversation*', route => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([])
        });
      });

      // When: Navigate to Chat History
      await page.goto(`${FRONTEND_URL}/chat/history`);
      await page.waitForLoadState('networkidle');

      // Then: Should show appropriate empty state
      const emptyState = page.locator('text=/no sessions found|no conversations yet|start chatting/i');
      await expect(emptyState).toBeVisible({ timeout: 5000 });

      // And: Should NOT show authentication error
      await expect(page.locator('text=/not authenticated|unauthorized/i')).not.toBeVisible();

      // And: Should NOT show generic error message
      await expect(page.locator('text=/error loading|failed to fetch/i')).not.toBeVisible();
    });

    test('should persist authentication across chat history requests', async ({ page }) => {
      // Given: Admin user is logged in
      const token = await loginAsAdmin(page);

      // When: Navigate to Chat History
      await page.goto(`${FRONTEND_URL}/chat/history`);
      await page.waitForLoadState('networkidle');

      // And: Refresh the page
      await page.reload();
      await page.waitForLoadState('networkidle');

      // Then: Should still be authenticated and not show error
      await expect(page.locator('text=/not authenticated/i')).not.toBeVisible();

      // And: Should still display chat history or empty state
      const isAuthenticated = await page.locator('[data-testid="chat-history"], h1').isVisible();
      expect(isAuthenticated).toBeTruthy();
    });

    test('should display correct session metadata in chat history', async ({ page }) => {
      // Given: Admin user with chat sessions
      const token = await loginAsAdmin(page);

      // When: Navigate to Chat History
      await page.goto(`${FRONTEND_URL}/chat/history`);
      await page.waitForLoadState('networkidle');

      // Then: Each session should display required metadata
      const sessions = page.locator('[data-testid="chat-session"], [data-testid="conversation-item"]');
      const count = await sessions.count();

      if (count > 0) {
        // First session should have timestamp and animal info
        const firstSession = sessions.first();

        // Should show timestamp
        const hasTimestamp = await firstSession.locator('text=/ago|AM|PM|\\d{1,2}:\\d{2}/').isVisible() ||
                            await firstSession.locator('[data-testid="session-time"]').isVisible();
        expect(hasTimestamp).toBeTruthy();

        // Should show animal name or identifier
        const hasAnimal = await firstSession.locator('[data-testid="animal-name"]').isVisible() ||
                         await firstSession.textContent().then(text => text.length > 0);
        expect(hasAnimal).toBeTruthy();
      }
    });
  });
});
