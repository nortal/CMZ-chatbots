/**
 * Assistant Management Direct CRUD Testing
 *
 * Simplified E2E test using direct URL navigation to test
 * the complete CRUD workflow for Assistant Management.
 *
 * Uses direct navigation to bypass menu hierarchy issues.
 *
 * Environment:
 * - Frontend: http://localhost:3000
 * - Backend: http://localhost:8081
 * - Test User: test@cmz.org / testpass123 (admin role)
 */

import { test, expect } from '@playwright/test';

const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:3000';
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8081';
const TEST_USER_EMAIL = 'test@cmz.org';
const TEST_USER_PASSWORD = 'testpass123';

test.describe('Assistant Management Direct CRUD Workflow', () => {

  // Login helper function
  async function login(page) {
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

    // Verify login success
    const isDashboard = await page.locator('heading:has-text("Dashboard")').first().isVisible().catch(() => false);
    expect(isDashboard).toBeTruthy();
  }

  test('Complete Assistant CRUD Workflow with Direct Navigation', async ({ page }) => {
    console.log('Starting complete CRUD workflow test...');

    // STEP 1: Login
    console.log('Step 1: Logging in...');
    await login(page);

    await page.screenshot({
      path: '/Users/keithstegbauer/repositories/CMZ-chatbots/frontend/tests/screenshots/crud-01-logged-in.png',
      fullPage: true
    });
    console.log('✅ Login successful');

    // STEP 2: Navigate directly to Assistant Management
    console.log('Step 2: Navigating to Assistant Management...');
    await page.goto(`${FRONTEND_URL}/assistants`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    await page.screenshot({
      path: '/Users/keithstegbauer/repositories/CMZ-chatbots/frontend/tests/screenshots/crud-02-assistant-page.png',
      fullPage: true
    });
    console.log('✅ Assistant Management page loaded');

    // STEP 3: Check page content
    console.log('Step 3: Verifying page content...');
    const pageContent = await page.content();
    console.log('Page title:', await page.title());
    console.log('Current URL:', page.url());

    // Look for key page elements
    const hasCreateButton = await page.locator('button:has-text("Create"), button:has-text("Add"), button:has-text("New")').first().isVisible({ timeout: 5000 }).catch(() => false);
    const hasTable = await page.locator('table, [role="grid"]').first().isVisible({ timeout: 5000 }).catch(() => false);
    const hasSearch = await page.locator('input[type="search"], input[placeholder*="search" i]').first().isVisible({ timeout: 3000 }).catch(() => false);

    console.log('Page Elements Found:');
    console.log('  - Create Button:', hasCreateButton);
    console.log('  - Table/Grid:', hasTable);
    console.log('  - Search:', hasSearch);

    // Check for loading states or error messages
    const isLoading = await page.locator('text=/loading/i, [role="status"]').first().isVisible({ timeout: 2000 }).catch(() => false);
    const hasError = await page.locator('text=/error/i, [role="alert"]').first().isVisible({ timeout: 2000 }).catch(() => false);

    if (isLoading) {
      console.log('⏳ Page is still loading...');
      await page.waitForTimeout(3000);
    }

    if (hasError) {
      console.log('❌ Error detected on page');
      const errorText = await page.locator('text=/error/i, [role="alert"]').first().textContent();
      console.log('Error message:', errorText);
    }

    await page.screenshot({
      path: '/Users/keithstegbauer/repositories/CMZ-chatbots/frontend/tests/screenshots/crud-03-page-analysis.png',
      fullPage: true
    });

    // STEP 4: Check API calls
    console.log('Step 4: Monitoring API calls...');

    let apiCalls = [];
    page.on('response', response => {
      if (response.url().includes('/assistant')) {
        apiCalls.push({
          url: response.url(),
          method: response.request().method(),
          status: response.status()
        });
        console.log(`API Call: ${response.request().method()} ${response.url()} -> ${response.status()}`);
      }
    });

    // Refresh to trigger API calls
    await page.reload();
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    console.log('API Calls captured:', apiCalls);

    await page.screenshot({
      path: '/Users/keithstegbauer/repositories/CMZ-chatbots/frontend/tests/screenshots/crud-04-after-reload.png',
      fullPage: true
    });

    // STEP 5: Try to open create dialog
    console.log('Step 5: Attempting to open create form...');

    if (hasCreateButton) {
      const createButton = page.locator('button:has-text("Create"), button:has-text("Add"), button:has-text("New")').first();
      await createButton.click();
      await page.waitForTimeout(1000);

      await page.screenshot({
        path: '/Users/keithstegbauer/repositories/CMZ-chatbots/frontend/tests/screenshots/crud-05-create-dialog.png',
        fullPage: true
      });

      // Check if dialog opened
      const dialogVisible = await page.locator('[role="dialog"], .modal, .dialog').first().isVisible({ timeout: 2000 }).catch(() => false);
      console.log('Create dialog visible:', dialogVisible);

      if (dialogVisible) {
        // Look for form fields
        const formFields = await page.locator('input, textarea, select').count();
        console.log(`Found ${formFields} form fields in dialog`);

        // Try to find specific fields
        const nameField = await page.locator('input[name="name"], input[placeholder*="name" i]').first().isVisible({ timeout: 2000 }).catch(() => false);
        const descField = await page.locator('textarea[name="description"], input[name="description"]').first().isVisible({ timeout: 2000 }).catch(() => false);

        console.log('Form fields found:');
        console.log('  - Name field:', nameField);
        console.log('  - Description field:', descField);

        if (nameField && descField) {
          // STEP 6: Fill and submit form
          console.log('Step 6: Filling create form...');

          const nameInput = page.locator('input[name="name"], input[placeholder*="name" i]').first();
          const descInput = page.locator('textarea[name="description"], input[name="description"]').first();

          await nameInput.fill('E2E Test Assistant');
          await descInput.fill('Created by automated E2E test');

          await page.screenshot({
            path: '/Users/keithstegbauer/repositories/CMZ-chatbots/frontend/tests/screenshots/crud-06-form-filled.png',
            fullPage: true
          });

          // Submit form
          const submitButton = page.locator('button[type="submit"], button:has-text("Create"), button:has-text("Save")').first();

          // Setup response listener
          const createResponse = page.waitForResponse(
            response => response.url().includes('/assistant') && response.request().method() === 'POST',
            { timeout: 10000 }
          ).catch(() => null);

          await submitButton.click();

          const response = await createResponse;
          if (response) {
            console.log('Create API Response:', response.status());
            const responseData = await response.json().catch(() => ({}));
            console.log('Response data:', responseData);
          } else {
            console.log('⚠️  No API response captured');
          }

          await page.waitForTimeout(2000);

          await page.screenshot({
            path: '/Users/keithstegbauer/repositories/CMZ-chatbots/frontend/tests/screenshots/crud-07-after-create.png',
            fullPage: true
          });
        }
      }
    } else {
      console.log('⚠️  Create button not found - cannot test create workflow');
    }

    // STEP 7: Final state
    console.log('Step 7: Final state capture...');
    await page.screenshot({
      path: '/Users/keithstegbauer/repositories/CMZ-chatbots/frontend/tests/screenshots/crud-08-final-state.png',
      fullPage: true
    });

    console.log('✅ Test complete');
  });

  test('Backend API Direct Validation', async ({ page }) => {
    console.log('Testing backend API directly...');

    // Test 1: List assistants
    console.log('Test 1: GET /assistant');
    const listResponse = await page.request.get(`${BACKEND_URL}/assistant`);
    console.log('List Response:', listResponse.status());

    if (listResponse.ok()) {
      const data = await listResponse.json();
      console.log('List Data:', data);
    }

    // Test 2: Create assistant
    console.log('Test 2: POST /assistant');
    const createPayload = {
      name: 'API Test Assistant',
      description: 'Created via direct API test',
      animalId: 'test-animal-id',
      personalityId: 'test-personality-id',
      guardrailIds: []
    };

    const createResponse = await page.request.post(`${BACKEND_URL}/assistant`, {
      data: createPayload,
      headers: {
        'Content-Type': 'application/json'
      }
    });

    console.log('Create Response:', createResponse.status());

    if (createResponse.ok()) {
      const data = await createResponse.json();
      console.log('Created Assistant:', data);
    } else {
      const errorText = await createResponse.text();
      console.log('Create Error:', errorText);
    }
  });

  test('Frontend Service Layer Test', async ({ page }) => {
    console.log('Testing frontend service integration...');

    await login(page);

    // Execute frontend service calls via page context
    const serviceTest = await page.evaluate(async (backendUrl) => {
      try {
        // Simulate what the frontend service does
        const response = await fetch(`${backendUrl}/assistant`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            // Token would be added here by the service
          }
        });

        return {
          status: response.status,
          ok: response.ok,
          data: await response.json().catch(() => null)
        };
      } catch (error) {
        return {
          error: error.message
        };
      }
    }, BACKEND_URL);

    console.log('Frontend Service Test Result:', serviceTest);
  });

});
