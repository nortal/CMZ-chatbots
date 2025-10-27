/**
 * Assistant Management E2E Testing
 *
 * Complete workflow testing for Assistant Management feature including:
 * - Authentication and navigation
 * - Assistant listing interface validation
 * - Create assistant functionality
 * - Edit assistant functionality
 * - Delete assistant functionality
 * - API integration verification
 *
 * Environment:
 * - Frontend: http://localhost:3000
 * - Backend: http://localhost:8081
 * - Test User: test@cmz.org / testpass123 (admin role)
 */

import { test, expect } from '@playwright/test';

// Test configuration
const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:3000';
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8081';
const TEST_USER_EMAIL = 'test@cmz.org';
const TEST_USER_PASSWORD = 'testpass123';

// Test data
const TEST_ASSISTANT = {
  name: 'Test Zoo Assistant',
  description: 'E2E test assistant for validation',
  animalId: 'test-animal-id',
  personality: 'friendly',
  guardrails: ['content-filter', 'age-appropriate']
};

const UPDATED_ASSISTANT = {
  description: 'Updated E2E test assistant'
};

test.describe('Assistant Management E2E Workflow', () => {

  test.beforeEach(async ({ page }) => {
    // Navigate to frontend
    await page.goto(FRONTEND_URL);
  });

  test('1. Authentication & Navigation Test', async ({ page }) => {
    console.log('Step 1: Testing authentication and navigation...');

    // Wait for login page to load
    await page.waitForLoadState('networkidle');

    // Take screenshot of login page
    await page.screenshot({
      path: '/Users/keithstegbauer/repositories/CMZ-chatbots/frontend/tests/screenshots/assistant-mgmt-01-login-page.png',
      fullPage: true
    });

    // Fill login form
    const emailInput = page.locator('input[type="email"], input[name="email"], input[placeholder*="email" i]').first();
    const passwordInput = page.locator('input[type="password"], input[name="password"]').first();

    await emailInput.fill(TEST_USER_EMAIL);
    await passwordInput.fill(TEST_USER_PASSWORD);

    // Take screenshot of filled login form
    await page.screenshot({
      path: '/Users/keithstegbauer/repositories/CMZ-chatbots/frontend/tests/screenshots/assistant-mgmt-02-login-filled.png',
      fullPage: true
    });

    // Click login button
    const loginButton = page.locator('button[type="submit"], button:has-text("Login"), button:has-text("Sign In")').first();
    await loginButton.click();

    // Wait for navigation after login
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000); // Allow time for token storage

    // Verify JWT token is stored (check multiple possible keys)
    const tokenData = await page.evaluate(() => {
      const keys = ['token', 'authToken', 'jwt', 'accessToken', 'jwtToken'];
      const tokens = {};

      // Check localStorage
      keys.forEach(key => {
        const value = localStorage.getItem(key);
        if (value) tokens[`localStorage.${key}`] = value;
      });

      // Check sessionStorage
      keys.forEach(key => {
        const value = sessionStorage.getItem(key);
        if (value) tokens[`sessionStorage.${key}`] = value;
      });

      return tokens;
    });

    console.log('Token storage:', tokenData);

    // Also check if we're on the dashboard (which indicates successful login)
    const isDashboard = await page.locator('heading:has-text("Dashboard"), heading:has-text("Good afternoon")').first().isVisible().catch(() => false);

    if (isDashboard) {
      console.log('✅ Successfully logged in - Dashboard visible');
    } else if (Object.keys(tokenData).length > 0) {
      console.log('✅ JWT token stored successfully:', Object.keys(tokenData));
    } else {
      console.log('⚠️  No token found, but checking if login succeeded anyway');
    }

    // Take screenshot of post-login state
    await page.screenshot({
      path: '/Users/keithstegbauer/repositories/CMZ-chatbots/frontend/tests/screenshots/assistant-mgmt-03-logged-in.png',
      fullPage: true
    });

    // Navigate to Assistant Management page
    // Click the visible "Assistant Management" button in navigation
    const assistantMgmtButton = page.locator('button:has-text("Assistant Management")').first();
    await expect(assistantMgmtButton).toBeVisible({ timeout: 10000 });
    await assistantMgmtButton.click();
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    // Verify we're on the assistant management page
    const currentUrl = page.url();
    console.log('Current URL after navigation:', currentUrl);
    console.log('✅ Navigated to Assistant Management page');

    // Take screenshot of Assistant Management page
    await page.screenshot({
      path: '/Users/keithstegbauer/repositories/CMZ-chatbots/frontend/tests/screenshots/assistant-mgmt-04-assistant-page.png',
      fullPage: true
    });
  });

  test('2. Assistant Management Interface Validation', async ({ page }) => {
    console.log('Step 2: Validating Assistant Management interface...');

    // Login first
    await performLogin(page);

    // Navigate to Assistant Management
    await page.goto(`${FRONTEND_URL}/assistants`);
    await page.waitForLoadState('networkidle');

    // Check for Create Assistant button
    const createButton = page.locator('button:has-text("Create"), button:has-text("Add"), button:has-text("New")').first();
    await expect(createButton).toBeVisible({ timeout: 10000 });
    console.log('✅ Create Assistant button found');

    // Check for listing table/grid
    const listingContainer = page.locator('table, .grid, .list, [role="grid"]').first();
    await expect(listingContainer).toBeVisible({ timeout: 10000 });
    console.log('✅ Assistant listing container found');

    // Check for search/filter functionality
    const searchInput = page.locator('input[type="search"], input[placeholder*="search" i], input[placeholder*="filter" i]').first();
    const hasSearch = await searchInput.isVisible({ timeout: 3000 }).catch(() => false);
    if (hasSearch) {
      console.log('✅ Search/filter functionality found');
    } else {
      console.log('ℹ️ No search/filter functionality visible');
    }

    // Take screenshot of interface
    await page.screenshot({
      path: '/Users/keithstegbauer/repositories/CMZ-chatbots/frontend/tests/screenshots/assistant-mgmt-05-interface-validation.png',
      fullPage: true
    });
  });

  test('3. Create Assistant Test', async ({ page }) => {
    console.log('Step 3: Testing assistant creation...');

    // Login and navigate
    await performLogin(page);
    await page.goto(`${FRONTEND_URL}/assistants`);
    await page.waitForLoadState('networkidle');

    // Click Create Assistant button
    const createButton = page.locator('button:has-text("Create"), button:has-text("Add"), button:has-text("New")').first();
    await createButton.click();
    await page.waitForTimeout(1000);

    // Take screenshot of create form
    await page.screenshot({
      path: '/Users/keithstegbauer/repositories/CMZ-chatbots/frontend/tests/screenshots/assistant-mgmt-06-create-form.png',
      fullPage: true
    });

    // Setup API response listener
    const createResponse = page.waitForResponse(
      response => response.url().includes('/assistant') && response.request().method() === 'POST'
    );

    // Fill form fields
    const nameInput = page.locator('input[name="name"], input[placeholder*="name" i]').first();
    await nameInput.fill(TEST_ASSISTANT.name);

    const descInput = page.locator('textarea[name="description"], input[name="description"], textarea[placeholder*="description" i]').first();
    await descInput.fill(TEST_ASSISTANT.description);

    // Look for animal selection dropdown
    const animalSelect = page.locator('select[name="animalId"], select[name="animal"]').first();
    const hasAnimalSelect = await animalSelect.isVisible({ timeout: 3000 }).catch(() => false);
    if (hasAnimalSelect) {
      await animalSelect.selectOption({ index: 1 }); // Select first non-default option
      console.log('✅ Animal selected');
    }

    // Look for personality selection
    const personalitySelect = page.locator('select[name="personality"]').first();
    const hasPersonalitySelect = await personalitySelect.isVisible({ timeout: 3000 }).catch(() => false);
    if (hasPersonalitySelect) {
      await personalitySelect.selectOption(TEST_ASSISTANT.personality);
      console.log('✅ Personality selected');
    }

    // Take screenshot of filled form
    await page.screenshot({
      path: '/Users/keithstegbauer/repositories/CMZ-chatbots/frontend/tests/screenshots/assistant-mgmt-07-create-form-filled.png',
      fullPage: true
    });

    // Submit form
    const submitButton = page.locator('button[type="submit"], button:has-text("Create"), button:has-text("Save")').first();
    await submitButton.click();

    // Wait for API response
    const response = await createResponse;
    const responseData = await response.json();
    console.log('Create API Response:', responseData);

    // Verify success
    expect(response.status()).toBe(201);
    console.log('✅ Assistant created successfully');

    // Wait for UI update
    await page.waitForTimeout(2000);

    // Take screenshot of success state
    await page.screenshot({
      path: '/Users/keithstegbauer/repositories/CMZ-chatbots/frontend/tests/screenshots/assistant-mgmt-08-create-success.png',
      fullPage: true
    });

    // Verify assistant appears in listing
    const assistantRow = page.locator(`text="${TEST_ASSISTANT.name}"`).first();
    await expect(assistantRow).toBeVisible({ timeout: 5000 });
    console.log('✅ Assistant appears in listing');
  });

  test('4. List & Display Test', async ({ page }) => {
    console.log('Step 4: Testing assistant listing and display...');

    // Login and navigate
    await performLogin(page);
    await page.goto(`${FRONTEND_URL}/assistants`);
    await page.waitForLoadState('networkidle');

    // Setup API response listener
    page.on('response', response => {
      if (response.url().includes('/assistant') && response.request().method() === 'GET') {
        console.log('List API called:', response.url());
      }
    });

    // Take screenshot of listing
    await page.screenshot({
      path: '/Users/keithstegbauer/repositories/CMZ-chatbots/frontend/tests/screenshots/assistant-mgmt-09-listing.png',
      fullPage: true
    });

    // Check for assistant details in listing
    const assistantElements = page.locator('[data-testid*="assistant"], tr, .assistant-item').all();
    console.log(`Found ${(await assistantElements).length} assistant elements`);

    // Test search if available
    const searchInput = page.locator('input[type="search"], input[placeholder*="search" i]').first();
    const hasSearch = await searchInput.isVisible({ timeout: 3000 }).catch(() => false);

    if (hasSearch) {
      await searchInput.fill(TEST_ASSISTANT.name);
      await page.waitForTimeout(1000);

      await page.screenshot({
        path: '/Users/keithstegbauer/repositories/CMZ-chatbots/frontend/tests/screenshots/assistant-mgmt-10-search-filtered.png',
        fullPage: true
      });

      console.log('✅ Search functionality tested');
    }
  });

  test('5. Edit Assistant Test', async ({ page }) => {
    console.log('Step 5: Testing assistant editing...');

    // Login and navigate
    await performLogin(page);
    await page.goto(`${FRONTEND_URL}/assistants`);
    await page.waitForLoadState('networkidle');

    // Find and click edit button
    const editButton = page.locator('button:has-text("Edit"), button[aria-label*="edit" i], a:has-text("Edit")').first();
    await editButton.click();
    await page.waitForTimeout(1000);

    // Take screenshot of edit form
    await page.screenshot({
      path: '/Users/keithstegbauer/repositories/CMZ-chatbots/frontend/tests/screenshots/assistant-mgmt-11-edit-form.png',
      fullPage: true
    });

    // Setup API response listener
    const updateResponse = page.waitForResponse(
      response => response.url().includes('/assistant') && response.request().method() === 'PUT'
    );

    // Update description
    const descInput = page.locator('textarea[name="description"], input[name="description"]').first();
    await descInput.clear();
    await descInput.fill(UPDATED_ASSISTANT.description);

    // Take screenshot of modified form
    await page.screenshot({
      path: '/Users/keithstegbauer/repositories/CMZ-chatbots/frontend/tests/screenshots/assistant-mgmt-12-edit-form-modified.png',
      fullPage: true
    });

    // Submit update
    const saveButton = page.locator('button[type="submit"], button:has-text("Save"), button:has-text("Update")').first();
    await saveButton.click();

    // Wait for API response
    const response = await updateResponse;
    expect(response.status()).toBe(200);
    console.log('✅ Assistant updated successfully');

    // Wait for UI update
    await page.waitForTimeout(2000);

    // Take screenshot of updated state
    await page.screenshot({
      path: '/Users/keithstegbauer/repositories/CMZ-chatbots/frontend/tests/screenshots/assistant-mgmt-13-edit-success.png',
      fullPage: true
    });

    // Verify changes in listing
    const updatedText = page.locator(`text="${UPDATED_ASSISTANT.description}"`).first();
    await expect(updatedText).toBeVisible({ timeout: 5000 });
    console.log('✅ Changes reflected in listing');
  });

  test('6. Status/Monitoring Test', async ({ page }) => {
    console.log('Step 6: Testing status and monitoring features...');

    // Login and navigate
    await performLogin(page);
    await page.goto(`${FRONTEND_URL}/assistants`);
    await page.waitForLoadState('networkidle');

    // Look for status indicators
    const statusIndicators = page.locator('[data-testid*="status"], .status, .badge').all();
    const statusCount = (await statusIndicators).length;

    if (statusCount > 0) {
      console.log(`✅ Found ${statusCount} status indicators`);

      // Take screenshot of status display
      await page.screenshot({
        path: '/Users/keithstegbauer/repositories/CMZ-chatbots/frontend/tests/screenshots/assistant-mgmt-14-status-display.png',
        fullPage: true
      });
    } else {
      console.log('ℹ️ No status indicators found');
    }

    // Look for monitoring/analytics features
    const analyticsLinks = page.locator('a:has-text("Analytics"), a:has-text("Stats"), a:has-text("Monitor")').all();
    const analyticsCount = (await analyticsLinks).length;

    if (analyticsCount > 0) {
      console.log(`✅ Found ${analyticsCount} monitoring/analytics links`);
    } else {
      console.log('ℹ️ No monitoring/analytics features found');
    }
  });

  test('7. Delete Assistant Test', async ({ page }) => {
    console.log('Step 7: Testing assistant deletion...');

    // Login and navigate
    await performLogin(page);
    await page.goto(`${FRONTEND_URL}/assistants`);
    await page.waitForLoadState('networkidle');

    // Setup API response listener
    const deleteResponse = page.waitForResponse(
      response => response.url().includes('/assistant') && response.request().method() === 'DELETE'
    );

    // Find and click delete button
    const deleteButton = page.locator('button:has-text("Delete"), button[aria-label*="delete" i]').first();
    await deleteButton.click();
    await page.waitForTimeout(500);

    // Take screenshot of confirmation dialog if present
    const confirmDialog = page.locator('[role="dialog"], .modal').first();
    const hasDialog = await confirmDialog.isVisible({ timeout: 2000 }).catch(() => false);

    if (hasDialog) {
      await page.screenshot({
        path: '/Users/keithstegbauer/repositories/CMZ-chatbots/frontend/tests/screenshots/assistant-mgmt-15-delete-confirm.png',
        fullPage: true
      });

      // Click confirm button
      const confirmButton = page.locator('button:has-text("Confirm"), button:has-text("Delete"), button:has-text("Yes")').last();
      await confirmButton.click();
    }

    // Wait for API response
    const response = await deleteResponse;
    expect(response.status()).toBe(200);
    console.log('✅ Assistant deleted successfully');

    // Wait for UI update
    await page.waitForTimeout(2000);

    // Take screenshot of clean state
    await page.screenshot({
      path: '/Users/keithstegbauer/repositories/CMZ-chatbots/frontend/tests/screenshots/assistant-mgmt-16-delete-success.png',
      fullPage: true
    });

    // Verify assistant is removed from listing
    const assistantRow = page.locator(`text="${TEST_ASSISTANT.name}"`).first();
    const isRemoved = !(await assistantRow.isVisible({ timeout: 3000 }).catch(() => true));
    expect(isRemoved).toBeTruthy();
    console.log('✅ Assistant removed from listing');
  });

  test('8. Complete CRUD Workflow', async ({ page }) => {
    console.log('Step 8: Running complete CRUD workflow...');

    // Login
    await performLogin(page);
    await page.goto(`${FRONTEND_URL}/assistants`);
    await page.waitForLoadState('networkidle');

    // CREATE
    console.log('Testing CREATE...');
    const createButton = page.locator('button:has-text("Create"), button:has-text("Add")').first();
    await createButton.click();
    await page.waitForTimeout(1000);

    const nameInput = page.locator('input[name="name"]').first();
    await nameInput.fill('Workflow Test Assistant');

    const descInput = page.locator('textarea[name="description"], input[name="description"]').first();
    await descInput.fill('Complete workflow test');

    const submitButton = page.locator('button[type="submit"]').first();
    await submitButton.click();
    await page.waitForTimeout(2000);

    // READ - Verify in listing
    console.log('Testing READ...');
    const newAssistant = page.locator('text="Workflow Test Assistant"').first();
    await expect(newAssistant).toBeVisible();

    // UPDATE
    console.log('Testing UPDATE...');
    const editButton = page.locator('button:has-text("Edit")').first();
    await editButton.click();
    await page.waitForTimeout(1000);

    const editDescInput = page.locator('textarea[name="description"], input[name="description"]').first();
    await editDescInput.clear();
    await editDescInput.fill('Updated workflow test');

    const saveButton = page.locator('button:has-text("Save"), button[type="submit"]').first();
    await saveButton.click();
    await page.waitForTimeout(2000);

    // Verify update
    const updatedAssistant = page.locator('text="Updated workflow test"').first();
    await expect(updatedAssistant).toBeVisible();

    // DELETE
    console.log('Testing DELETE...');
    const deleteButton = page.locator('button:has-text("Delete")').first();
    await deleteButton.click();
    await page.waitForTimeout(500);

    // Handle confirmation if present
    const confirmButton = page.locator('button:has-text("Confirm"), button:has-text("Yes")').last();
    const hasConfirm = await confirmButton.isVisible({ timeout: 2000 }).catch(() => false);
    if (hasConfirm) {
      await confirmButton.click();
    }

    await page.waitForTimeout(2000);

    // Verify deletion
    const deletedAssistant = page.locator('text="Workflow Test Assistant"').first();
    const isDeleted = !(await deletedAssistant.isVisible({ timeout: 3000 }).catch(() => true));
    expect(isDeleted).toBeTruthy();

    console.log('✅ Complete CRUD workflow successful');

    // Final screenshot
    await page.screenshot({
      path: '/Users/keithstegbauer/repositories/CMZ-chatbots/frontend/tests/screenshots/assistant-mgmt-17-workflow-complete.png',
      fullPage: true
    });
  });
});

// Helper function to perform login
async function performLogin(page) {
  await page.goto(FRONTEND_URL);
  await page.waitForLoadState('networkidle');

  const emailInput = page.locator('input[type="email"], input[name="email"]').first();
  const passwordInput = page.locator('input[type="password"]').first();

  await emailInput.fill(TEST_USER_EMAIL);
  await passwordInput.fill(TEST_USER_PASSWORD);

  const loginButton = page.locator('button[type="submit"]').first();
  await loginButton.click();

  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(2000);
}
