/**
 * End-to-end tests for Sandbox Testing Workflow
 *
 * Tests the complete user journey for safely testing assistant changes
 * through sandbox creation, testing, and promotion to live environment.
 *
 * T038 - User Story 2: Test Assistant Changes Safely
 */

const { test, expect } = require('@playwright/test');

// Test configuration
const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:3001';
const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8080';

// Test data
const TEST_USERS = {
  admin: { email: 'test@cmz.org', password: 'testpass123' },
  zookeeper: { email: 'parent1@test.cmz.org', password: 'testpass123' }
};

const TEST_SANDBOX_DATA = {
  name: 'E2E Test Sandbox Assistant',
  description: 'Testing new personality configuration for Bella the Bear',
  personalityId: 'friendly-educational',
  guardrailId: 'family-friendly-strict'
};

test.describe('🧪 Sandbox Testing Workflow E2E', () => {

  test.beforeEach(async ({ page }) => {
    // Navigate to application
    await page.goto(FRONTEND_URL);
    await page.waitForLoadState('networkidle');
  });

  test('🎯 Complete sandbox testing workflow - Admin User', async ({ page }) => {
    // Step 1: Login as admin user
    await test.step('Login as admin', async () => {
      await page.fill('[data-testid="email-input"]', TEST_USERS.admin.email);
      await page.fill('[data-testid="password-input"]', TEST_USERS.admin.password);
      await page.click('[data-testid="login-button"]');

      // Verify successful login and dashboard access
      await expect(page).toHaveURL(/.*dashboard/);
      await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();
    });

    // Step 2: Navigate to Assistant Management
    await test.step('Navigate to Assistant Management', async () => {
      await page.click('[data-testid="nav-assistant-management"]');
      await expect(page).toHaveURL(/.*assistant-management/);
      await expect(page.locator('h1')).toContainText('Assistant Management');
    });

    // Step 3: Select base assistant for sandbox testing
    let baseAssistantId;
    await test.step('Select base assistant', async () => {
      // Wait for assistant list to load
      await page.waitForSelector('[data-testid="assistant-list"]');

      // Select first available assistant (should be Bella the Bear)
      const firstAssistant = page.locator('[data-testid="assistant-card"]').first();
      await expect(firstAssistant).toBeVisible();

      // Extract assistant ID for later use
      baseAssistantId = await firstAssistant.getAttribute('data-assistant-id');
      expect(baseAssistantId).toBeTruthy();

      // Click "Test Changes" button
      await firstAssistant.locator('[data-testid="test-changes-button"]').click();
    });

    // Step 4: Create sandbox assistant
    let sandboxId;
    await test.step('Create sandbox assistant', async () => {
      // Verify sandbox creation dialog appears
      await expect(page.locator('[data-testid="sandbox-creation-dialog"]')).toBeVisible();

      // Fill in sandbox details
      await page.fill('[data-testid="sandbox-name-input"]', TEST_SANDBOX_DATA.name);
      await page.fill('[data-testid="sandbox-description-input"]', TEST_SANDBOX_DATA.description);

      // Select different personality for testing
      await page.selectOption('[data-testid="personality-select"]', TEST_SANDBOX_DATA.personalityId);

      // Select different guardrail for testing
      await page.selectOption('[data-testid="guardrail-select"]', TEST_SANDBOX_DATA.guardrailId);

      // Create sandbox
      await page.click('[data-testid="create-sandbox-button"]');

      // Verify sandbox creation success
      await expect(page.locator('[data-testid="sandbox-created-success"]')).toBeVisible();

      // Extract sandbox ID from success message
      const successText = await page.locator('[data-testid="sandbox-id-display"]').textContent();
      sandboxId = successText.match(/sandbox-[\w-]+/)[0];
      expect(sandboxId).toBeTruthy();

      // Verify TTL display (should show ~30 minutes)
      const ttlDisplay = page.locator('[data-testid="sandbox-ttl-display"]');
      await expect(ttlDisplay).toBeVisible();
      await expect(ttlDisplay).toContainText('29'); // Should show ~29-30 minutes
    });

    // Step 5: Test sandbox assistant functionality
    await test.step('Test sandbox assistant', async () => {
      // Navigate to sandbox testing interface
      await page.click('[data-testid="test-sandbox-button"]');
      await expect(page).toHaveURL(new RegExp(`.*sandbox/${sandboxId}/test`));

      // Verify sandbox testing interface loads
      await expect(page.locator('[data-testid="sandbox-chat-interface"]')).toBeVisible();
      await expect(page.locator('[data-testid="sandbox-info-panel"]')).toBeVisible();

      // Verify sandbox info displays correctly
      await expect(page.locator('[data-testid="sandbox-name-display"]')).toContainText(TEST_SANDBOX_DATA.name);
      await expect(page.locator('[data-testid="sandbox-status"]')).toContainText('Draft');

      // Test sandbox chat functionality
      const testMessage = 'Hello! Can you tell me about yourself?';
      await page.fill('[data-testid="chat-input"]', testMessage);
      await page.click('[data-testid="send-message-button"]');

      // Verify chat response
      await expect(page.locator('[data-testid="chat-messages"]')).toContainText(testMessage);

      // Wait for AI response (may take a few seconds)
      await page.waitForSelector('[data-testid="ai-response"]', { timeout: 10000 });
      const aiResponse = page.locator('[data-testid="ai-response"]').last();
      await expect(aiResponse).toBeVisible();
      await expect(aiResponse).not.toBeEmpty();

      // Verify sandbox-specific response (should mention testing mode)
      const responseText = await aiResponse.textContent();
      expect(responseText.toLowerCase()).toMatch(/(test|sandbox|testing)/);
    });

    // Step 6: Mark sandbox as tested
    await test.step('Mark sandbox as tested', async () => {
      // Click "Mark as Tested" button
      await page.click('[data-testid="mark-tested-button"]');

      // Verify status change
      await expect(page.locator('[data-testid="sandbox-status"]')).toContainText('Tested');

      // Verify promotion becomes available
      await expect(page.locator('[data-testid="promote-sandbox-button"]')).toBeEnabled();
    });

    // Step 7: Promote sandbox to live
    await test.step('Promote sandbox to live', async () => {
      // Click promote button
      await page.click('[data-testid="promote-sandbox-button"]');

      // Verify confirmation dialog
      await expect(page.locator('[data-testid="promotion-confirmation-dialog"]')).toBeVisible();
      await expect(page.locator('[data-testid="promotion-warning"]')).toContainText('replace the live assistant');

      // Confirm promotion
      await page.click('[data-testid="confirm-promotion-button"]');

      // Verify promotion success
      await expect(page.locator('[data-testid="promotion-success"]')).toBeVisible();
      await expect(page.locator('[data-testid="promotion-success"]')).toContainText('successfully promoted');

      // Verify redirect back to assistant management
      await expect(page).toHaveURL(/.*assistant-management/);
    });

    // Step 8: Verify live assistant updated
    await test.step('Verify live assistant updated', async () => {
      // Find the updated assistant in the list
      const updatedAssistant = page.locator(`[data-assistant-id="${baseAssistantId}"]`);
      await expect(updatedAssistant).toBeVisible();

      // Verify assistant shows updated configuration
      await expect(updatedAssistant.locator('[data-testid="assistant-personality"]')).toContainText(TEST_SANDBOX_DATA.personalityId);
      await expect(updatedAssistant.locator('[data-testid="assistant-guardrail"]')).toContainText(TEST_SANDBOX_DATA.guardrailId);

      // Verify "Last Updated" timestamp is recent
      const lastUpdated = updatedAssistant.locator('[data-testid="last-updated"]');
      await expect(lastUpdated).toBeVisible();
      const updateTime = await lastUpdated.textContent();
      expect(updateTime).toMatch(/(just now|minute ago|seconds ago)/);
    });

    // Step 9: Verify sandbox cleanup
    await test.step('Verify sandbox cleanup', async () => {
      // Navigate to sandbox management (if available)
      const sandboxNavExists = await page.locator('[data-testid="nav-sandbox-management"]').count();
      if (sandboxNavExists > 0) {
        await page.click('[data-testid="nav-sandbox-management"]');

        // Verify promoted sandbox is no longer listed
        const sandboxList = page.locator('[data-testid="sandbox-list"]');
        if (await sandboxList.count() > 0) {
          await expect(sandboxList.locator(`[data-sandbox-id="${sandboxId}"]`)).not.toBeVisible();
        }
      }
    });
  });

  test('🔒 Sandbox testing workflow - Zookeeper User (Limited Permissions)', async ({ page }) => {
    // Test that zookeepers can create and test sandboxes but not promote

    // Step 1: Login as zookeeper
    await test.step('Login as zookeeper', async () => {
      await page.fill('[data-testid="email-input"]', TEST_USERS.zookeeper.email);
      await page.fill('[data-testid="password-input"]', TEST_USERS.zookeeper.password);
      await page.click('[data-testid="login-button"]');

      await expect(page).toHaveURL(/.*dashboard/);
    });

    // Step 2: Navigate to Assistant Management
    await test.step('Navigate to Assistant Management', async () => {
      await page.click('[data-testid="nav-assistant-management"]');
      await expect(page).toHaveURL(/.*assistant-management/);
    });

    // Step 3: Create sandbox (should work)
    let sandboxId;
    await test.step('Create sandbox as zookeeper', async () => {
      const firstAssistant = page.locator('[data-testid="assistant-card"]').first();
      await firstAssistant.locator('[data-testid="test-changes-button"]').click();

      await page.fill('[data-testid="sandbox-name-input"]', 'Zookeeper Test Sandbox');
      await page.fill('[data-testid="sandbox-description-input"]', 'Testing as zookeeper role');
      await page.selectOption('[data-testid="personality-select"]', 'playful-energetic');

      await page.click('[data-testid="create-sandbox-button"]');

      await expect(page.locator('[data-testid="sandbox-created-success"]')).toBeVisible();

      const successText = await page.locator('[data-testid="sandbox-id-display"]').textContent();
      sandboxId = successText.match(/sandbox-[\w-]+/)[0];
    });

    // Step 4: Test sandbox functionality
    await test.step('Test sandbox functionality', async () => {
      await page.click('[data-testid="test-sandbox-button"]');

      // Test basic chat functionality
      await page.fill('[data-testid="chat-input"]', 'Tell me about your habitat');
      await page.click('[data-testid="send-message-button"]');

      await page.waitForSelector('[data-testid="ai-response"]', { timeout: 10000 });
      await expect(page.locator('[data-testid="ai-response"]').last()).toBeVisible();
    });

    // Step 5: Mark as tested but verify promotion restrictions
    await test.step('Verify promotion restrictions for zookeeper', async () => {
      await page.click('[data-testid="mark-tested-button"]');
      await expect(page.locator('[data-testid="sandbox-status"]')).toContainText('Tested');

      // Verify zookeeper cannot promote (button should be disabled or missing)
      const promoteButton = page.locator('[data-testid="promote-sandbox-button"]');
      const buttonExists = await promoteButton.count();

      if (buttonExists > 0) {
        // Button exists but should be disabled
        await expect(promoteButton).toBeDisabled();

        // Verify tooltip explains permission requirement
        await promoteButton.hover();
        await expect(page.locator('[data-testid="permission-tooltip"]')).toContainText('admin');
      } else {
        // Button should not exist for non-admin users
        await expect(promoteButton).not.toBeVisible();
      }
    });
  });

  test('⏰ Sandbox TTL expiration handling', async ({ page }) => {
    // Test sandbox expiration behavior (simulated)

    await test.step('Login and create sandbox', async () => {
      await page.fill('[data-testid="email-input"]', TEST_USERS.admin.email);
      await page.fill('[data-testid="password-input"]', TEST_USERS.admin.password);
      await page.click('[data-testid="login-button"]');

      await page.click('[data-testid="nav-assistant-management"]');

      const firstAssistant = page.locator('[data-testid="assistant-card"]').first();
      await firstAssistant.locator('[data-testid="test-changes-button"]').click();

      await page.fill('[data-testid="sandbox-name-input"]', 'TTL Test Sandbox');
      await page.click('[data-testid="create-sandbox-button"]');

      await expect(page.locator('[data-testid="sandbox-created-success"]')).toBeVisible();
    });

    // Note: Full TTL testing requires backend manipulation or time acceleration
    // This test focuses on UI behavior for TTL display and warnings

    await test.step('Verify TTL display and warnings', async () => {
      // Verify initial TTL display
      const ttlDisplay = page.locator('[data-testid="sandbox-ttl-display"]');
      await expect(ttlDisplay).toBeVisible();

      // Verify countdown format (should show minutes:seconds or similar)
      const ttlText = await ttlDisplay.textContent();
      expect(ttlText).toMatch(/\d+.*minute/i);

      // Check for expiration warning styles when TTL gets low
      // (This would require backend manipulation for full testing)
      const ttlContainer = page.locator('[data-testid="sandbox-ttl-container"]');
      await expect(ttlContainer).toBeVisible();
    });
  });

  test('🔄 Multiple sandbox management', async ({ page }) => {
    // Test handling multiple sandboxes for different assistants

    await test.step('Login as admin', async () => {
      await page.fill('[data-testid="email-input"]', TEST_USERS.admin.email);
      await page.fill('[data-testid="password-input"]', TEST_USERS.admin.password);
      await page.click('[data-testid="login-button"]');

      await page.click('[data-testid="nav-assistant-management"]');
    });

    await test.step('Create multiple sandboxes', async () => {
      // Get list of available assistants
      await page.waitForSelector('[data-testid="assistant-list"]');
      const assistantCount = await page.locator('[data-testid="assistant-card"]').count();

      // Create sandboxes for first two assistants (if available)
      const maxSandboxes = Math.min(2, assistantCount);

      for (let i = 0; i < maxSandboxes; i++) {
        const assistant = page.locator('[data-testid="assistant-card"]').nth(i);
        await assistant.locator('[data-testid="test-changes-button"]').click();

        await page.fill('[data-testid="sandbox-name-input"]', `Multi-Test Sandbox ${i + 1}`);
        await page.fill('[data-testid="sandbox-description-input"]', `Testing assistant ${i + 1}`);

        await page.click('[data-testid="create-sandbox-button"]');
        await expect(page.locator('[data-testid="sandbox-created-success"]')).toBeVisible();

        // Close the success dialog
        await page.click('[data-testid="close-success-dialog"]');
      }
    });

    await test.step('Verify sandbox isolation', async () => {
      // Navigate to sandbox management if available
      const sandboxNavExists = await page.locator('[data-testid="nav-sandbox-management"]').count();
      if (sandboxNavExists > 0) {
        await page.click('[data-testid="nav-sandbox-management"]');

        // Verify multiple sandboxes are listed
        const sandboxCards = page.locator('[data-testid="sandbox-card"]');
        const sandboxCount = await sandboxCards.count();
        expect(sandboxCount).toBeGreaterThanOrEqual(1);

        // Verify each sandbox shows correct information
        for (let i = 0; i < Math.min(2, sandboxCount); i++) {
          const sandboxCard = sandboxCards.nth(i);
          await expect(sandboxCard.locator('[data-testid="sandbox-name"]')).toContainText('Multi-Test Sandbox');
          await expect(sandboxCard.locator('[data-testid="sandbox-status"]')).toContainText('Draft');
          await expect(sandboxCard.locator('[data-testid="sandbox-ttl"]')).toBeVisible();
        }
      }
    });
  });

  test('🚨 Error handling and validation', async ({ page }) => {
    // Test error scenarios and validation

    await test.step('Login and navigate to assistant management', async () => {
      await page.fill('[data-testid="email-input"]', TEST_USERS.admin.email);
      await page.fill('[data-testid="password-input"]', TEST_USERS.admin.password);
      await page.click('[data-testid="login-button"]');

      await page.click('[data-testid="nav-assistant-management"]');
    });

    await test.step('Test sandbox creation validation', async () => {
      const firstAssistant = page.locator('[data-testid="assistant-card"]').first();
      await firstAssistant.locator('[data-testid="test-changes-button"]').click();

      // Try to create sandbox without required fields
      await page.click('[data-testid="create-sandbox-button"]');

      // Verify validation errors
      await expect(page.locator('[data-testid="name-validation-error"]')).toBeVisible();
      await expect(page.locator('[data-testid="name-validation-error"]')).toContainText('required');
    });

    await test.step('Test backend error handling', async () => {
      // Fill valid data
      await page.fill('[data-testid="sandbox-name-input"]', 'Error Test Sandbox');
      await page.selectOption('[data-testid="personality-select"]', 'friendly-educational');

      // Mock backend error by intercepting API call
      await page.route(`${API_BASE_URL}/sandbox`, async route => {
        await route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({
            error: 'Internal server error',
            code: 'server_error'
          })
        });
      });

      await page.click('[data-testid="create-sandbox-button"]');

      // Verify error message display
      await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
      await expect(page.locator('[data-testid="error-message"]')).toContainText('server error');
    });
  });

  test('📱 Responsive design validation', async ({ page }) => {
    // Test sandbox workflow on different screen sizes

    await test.step('Test mobile layout', async () => {
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 667 });

      await page.fill('[data-testid="email-input"]', TEST_USERS.admin.email);
      await page.fill('[data-testid="password-input"]', TEST_USERS.admin.password);
      await page.click('[data-testid="login-button"]');

      // Verify mobile navigation works
      await page.click('[data-testid="mobile-menu-button"]');
      await page.click('[data-testid="nav-assistant-management"]');

      // Verify assistant cards adapt to mobile layout
      const assistantCard = page.locator('[data-testid="assistant-card"]').first();
      await expect(assistantCard).toBeVisible();

      // Verify sandbox creation dialog is responsive
      await assistantCard.locator('[data-testid="test-changes-button"]').click();
      await expect(page.locator('[data-testid="sandbox-creation-dialog"]')).toBeVisible();

      // Verify form elements are properly sized for mobile
      const nameInput = page.locator('[data-testid="sandbox-name-input"]');
      await expect(nameInput).toBeVisible();

      const inputBox = await nameInput.boundingBox();
      expect(inputBox.width).toBeLessThan(350); // Should fit mobile screen
    });

    await test.step('Test tablet layout', async () => {
      // Set tablet viewport
      await page.setViewportSize({ width: 768, height: 1024 });

      // Verify layout adapts appropriately
      const assistantList = page.locator('[data-testid="assistant-list"]');
      await expect(assistantList).toBeVisible();

      // Verify sandbox creation dialog scales properly
      const dialog = page.locator('[data-testid="sandbox-creation-dialog"]');
      const dialogBox = await dialog.boundingBox();
      expect(dialogBox.width).toBeGreaterThan(400);
      expect(dialogBox.width).toBeLessThan(750);
    });
  });

});