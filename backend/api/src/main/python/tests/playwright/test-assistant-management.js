/**
 * E2E Test: Assistant Management Complete Workflow
 *
 * Tests the complete CRUD workflow for Assistant Management including:
 * - Login and authentication
 * - Assistant listing and interface validation
 * - Create assistant workflow
 * - Edit assistant workflow
 * - Status monitoring
 * - Delete assistant workflow
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const FRONTEND_URL = 'http://localhost:3000';
const BACKEND_URL = 'http://localhost:8081';
const SCREENSHOTS_DIR = './screenshots/assistant-management';
const TEST_USER = {
  email: 'test@cmz.org',
  password: 'testpass123'
};

// Ensure screenshots directory exists
if (!fs.existsSync(SCREENSHOTS_DIR)) {
  fs.mkdirSync(SCREENSHOTS_DIR, { recursive: true });
}

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function takeScreenshot(page, name) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const filename = path.join(SCREENSHOTS_DIR, `${timestamp}_${name}.png`);
  await page.screenshot({ path: filename, fullPage: true });
  console.log(`📸 Screenshot saved: ${filename}`);
  return filename;
}

async function runTests() {
  console.log('🚀 Starting Assistant Management E2E Tests\n');

  const browser = await chromium.launch({
    headless: false,
    slowMo: 500 // Slow down for visibility
  });

  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    recordVideo: {
      dir: SCREENSHOTS_DIR,
      size: { width: 1920, height: 1080 }
    }
  });

  const page = await context.newPage();

  const testResults = {
    passed: [],
    failed: [],
    screenshots: []
  };

  try {
    // ==========================================
    // STEP 1: LOGIN AND AUTHENTICATION
    // ==========================================
    console.log('\n📝 STEP 1: Login and Authentication');
    console.log('=' .repeat(60));

    await page.goto(FRONTEND_URL);
    await sleep(1000);

    // Take initial screenshot
    testResults.screenshots.push(await takeScreenshot(page, 'step1_initial_page'));

    // Fill login form
    console.log('Filling login credentials...');
    await page.fill('input[type="email"], input[name="email"], input[placeholder*="email" i]', TEST_USER.email);
    await page.fill('input[type="password"], input[name="password"]', TEST_USER.password);

    testResults.screenshots.push(await takeScreenshot(page, 'step1_credentials_filled'));

    // Submit login
    console.log('Submitting login form...');
    await page.click('button[type="submit"], button:has-text("Sign In"), button:has-text("Login")');

    // Wait for navigation
    await page.waitForLoadState('networkidle', { timeout: 10000 });
    await sleep(2000);

    testResults.screenshots.push(await takeScreenshot(page, 'step1_after_login'));

    // Check if we're logged in (dashboard should be visible)
    const dashboardVisible = await page.isVisible('text=Dashboard, text=Assistant Management, text=Welcome').catch(() => false);

    if (dashboardVisible) {
      console.log('✅ Login successful - Dashboard visible');
      testResults.passed.push('Login and Authentication');
    } else {
      console.log('❌ Login may have failed - Dashboard not clearly visible');
      testResults.failed.push('Login and Authentication');
    }

    // ==========================================
    // STEP 2: NAVIGATE TO ASSISTANT MANAGEMENT
    // ==========================================
    console.log('\n📝 STEP 2: Navigate to Assistant Management Page');
    console.log('=' .repeat(60));

    // Try to navigate via URL directly
    console.log('Navigating to /assistants...');
    await page.goto(`${FRONTEND_URL}/assistants`);
    await page.waitForLoadState('networkidle', { timeout: 10000 });
    await sleep(2000);

    testResults.screenshots.push(await takeScreenshot(page, 'step2_assistant_management_page'));

    // Check for key interface elements
    const headerVisible = await page.isVisible('h1:has-text("Assistant Management")').catch(() => false);
    const createButtonVisible = await page.isVisible('button:has-text("Create")').catch(() => false);

    console.log(`Header visible: ${headerVisible}`);
    console.log(`Create button visible: ${createButtonVisible}`);

    if (headerVisible) {
      console.log('✅ Assistant Management page loaded');
      testResults.passed.push('Navigate to Assistant Management');

      // Check for statistics cards
      const statsVisible = await page.isVisible('text=Total Assistants, text=Active').catch(() => false);
      if (statsVisible) {
        console.log('✅ Statistics cards visible');
        testResults.passed.push('Statistics Display');
      }

      // Check for search functionality
      const searchVisible = await page.isVisible('input[placeholder*="Search" i]').catch(() => false);
      if (searchVisible) {
        console.log('✅ Search functionality visible');
        testResults.passed.push('Search Functionality');
      }
    } else {
      console.log('❌ Assistant Management page may not have loaded correctly');
      testResults.failed.push('Navigate to Assistant Management');
    }

    // ==========================================
    // STEP 3: CREATE ASSISTANT
    // ==========================================
    console.log('\n📝 STEP 3: Create Assistant Workflow');
    console.log('=' .repeat(60));

    // Click Create New Assistant button
    const createButton = await page.locator('button:has-text("Create New Assistant"), button:has-text("Create Assistant")').first();

    if (await createButton.isVisible().catch(() => false)) {
      console.log('Clicking Create New Assistant button...');
      await createButton.click();
      await sleep(2000);

      testResults.screenshots.push(await takeScreenshot(page, 'step3_create_dialog_opened'));

      // Check if dialog/form is visible
      const dialogVisible = await page.isVisible('[role="dialog"], .dialog, .modal').catch(() => false);
      const formVisible = await page.isVisible('form').catch(() => false);

      if (dialogVisible || formVisible) {
        console.log('✅ Create Assistant dialog/form opened');
        testResults.passed.push('Open Create Dialog');

        // Try to fill the form
        console.log('Attempting to fill assistant creation form...');

        // Select animal (first available option)
        try {
          const animalSelect = await page.locator('select, [role="combobox"]').filter({ hasText: /Animal|Select an animal/i }).first();
          if (await animalSelect.isVisible().catch(() => false)) {
            await animalSelect.click();
            await sleep(500);

            // Try to select first option
            const firstOption = await page.locator('[role="option"], option').first();
            if (await firstOption.isVisible().catch(() => false)) {
              await firstOption.click();
              console.log('✅ Animal selected');
            }
          }
        } catch (e) {
          console.log(`⚠️  Could not select animal: ${e.message}`);
        }

        await sleep(1000);
        testResults.screenshots.push(await takeScreenshot(page, 'step3_animal_selected'));

        // Select personality
        try {
          const personalitySelect = await page.locator('select, [role="combobox"]').filter({ hasText: /Personality/i }).first();
          if (await personalitySelect.isVisible().catch(() => false)) {
            await personalitySelect.click();
            await sleep(500);

            const firstOption = await page.locator('[role="option"], option').nth(1); // Get second option to skip placeholder
            if (await firstOption.isVisible().catch(() => false)) {
              await firstOption.click();
              console.log('✅ Personality selected');
            }
          }
        } catch (e) {
          console.log(`⚠️  Could not select personality: ${e.message}`);
        }

        await sleep(1000);
        testResults.screenshots.push(await takeScreenshot(page, 'step3_personality_selected'));

        // Select guardrail
        try {
          const guardrailSelect = await page.locator('select, [role="combobox"]').filter({ hasText: /Guardrail|Safety/i }).first();
          if (await guardrailSelect.isVisible().catch(() => false)) {
            await guardrailSelect.click();
            await sleep(500);

            const firstOption = await page.locator('[role="option"], option').nth(1);
            if (await firstOption.isVisible().catch(() => false)) {
              await firstOption.click();
              console.log('✅ Guardrail selected');
            }
          }
        } catch (e) {
          console.log(`⚠️  Could not select guardrail: ${e.message}`);
        }

        await sleep(1000);
        testResults.screenshots.push(await takeScreenshot(page, 'step3_form_filled'));

        // Try to submit the form
        console.log('Attempting to submit form...');
        const submitButton = await page.locator('button[type="submit"], button:has-text("Create Assistant")').first();

        if (await submitButton.isVisible().catch(() => false)) {
          const isDisabled = await submitButton.isDisabled().catch(() => true);

          if (!isDisabled) {
            await submitButton.click();
            console.log('✅ Form submitted');
            await sleep(3000); // Wait for creation

            testResults.screenshots.push(await takeScreenshot(page, 'step3_after_submission'));
            testResults.passed.push('Create Assistant Form Submission');
          } else {
            console.log('⚠️  Submit button is disabled (validation may be failing)');
            testResults.failed.push('Create Assistant - Button Disabled');
          }
        } else {
          console.log('❌ Submit button not found');
          testResults.failed.push('Create Assistant - No Submit Button');
        }
      } else {
        console.log('❌ Create dialog/form did not open');
        testResults.failed.push('Open Create Dialog');
      }
    } else {
      console.log('⚠️  Create button not available (may be no available animals)');
      testResults.failed.push('Create Button Availability');
    }

    // ==========================================
    // STEP 4: VERIFY ASSISTANT IN LIST
    // ==========================================
    console.log('\n📝 STEP 4: Verify Assistant Appears in List');
    console.log('=' .repeat(60));

    // Refresh the page to see updated list
    await page.reload();
    await page.waitForLoadState('networkidle', { timeout: 10000 });
    await sleep(2000);

    testResults.screenshots.push(await takeScreenshot(page, 'step4_assistant_list'));

    // Check if table has rows
    const tableRows = await page.locator('table tbody tr').count().catch(() => 0);
    console.log(`Found ${tableRows} assistant(s) in table`);

    if (tableRows > 0) {
      console.log('✅ Assistants visible in list');
      testResults.passed.push('Assistant List Display');
    } else {
      console.log('⚠️  No assistants visible in list');
      testResults.failed.push('Assistant List Display');
    }

    // ==========================================
    // STEP 5: EDIT ASSISTANT (if available)
    // ==========================================
    console.log('\n📝 STEP 5: Edit Assistant Workflow');
    console.log('=' .repeat(60));

    if (tableRows > 0) {
      const editButton = await page.locator('button:has-text("Edit")').first();

      if (await editButton.isVisible().catch(() => false)) {
        console.log('Clicking Edit button...');
        await editButton.click();
        await sleep(2000);

        testResults.screenshots.push(await takeScreenshot(page, 'step5_edit_dialog_opened'));

        const dialogVisible = await page.isVisible('[role="dialog"], .dialog').catch(() => false);

        if (dialogVisible) {
          console.log('✅ Edit dialog opened');
          testResults.passed.push('Open Edit Dialog');

          // Try to change status
          try {
            const statusSelect = await page.locator('select, [role="combobox"]').filter({ hasText: /Status/i }).first();
            if (await statusSelect.isVisible().catch(() => false)) {
              await statusSelect.click();
              await sleep(500);

              const inactiveOption = await page.locator('[role="option"]:has-text("Inactive"), option:has-text("Inactive")').first();
              if (await inactiveOption.isVisible().catch(() => false)) {
                await inactiveOption.click();
                console.log('✅ Status changed to Inactive');
              }
            }
          } catch (e) {
            console.log(`⚠️  Could not change status: ${e.message}`);
          }

          await sleep(1000);
          testResults.screenshots.push(await takeScreenshot(page, 'step5_status_changed'));

          // Submit edit
          const updateButton = await page.locator('button:has-text("Update")').first();
          if (await updateButton.isVisible().catch(() => false)) {
            await updateButton.click();
            console.log('✅ Edit form submitted');
            await sleep(3000);

            testResults.screenshots.push(await takeScreenshot(page, 'step5_after_update'));
            testResults.passed.push('Edit Assistant Submission');
          }
        } else {
          console.log('❌ Edit dialog did not open');
          testResults.failed.push('Open Edit Dialog');
        }
      } else {
        console.log('⚠️  Edit button not found');
        testResults.failed.push('Edit Button Availability');
      }
    }

    // ==========================================
    // STEP 6: STATUS MONITORING
    // ==========================================
    console.log('\n📝 STEP 6: Status Monitoring');
    console.log('=' .repeat(60));

    // Check for status badges
    const statusBadges = await page.locator('[class*="badge"], .badge').count().catch(() => 0);
    console.log(`Found ${statusBadges} status badge(s)`);

    if (statusBadges > 0) {
      console.log('✅ Status indicators visible');
      testResults.passed.push('Status Monitoring');
    }

    // ==========================================
    // STEP 7: DELETE ASSISTANT (if available)
    // ==========================================
    console.log('\n📝 STEP 7: Delete Assistant Workflow');
    console.log('=' .repeat(60));

    // Reload to see current state
    await page.reload();
    await page.waitForLoadState('networkidle', { timeout: 10000 });
    await sleep(2000);

    const currentRows = await page.locator('table tbody tr').count().catch(() => 0);

    if (currentRows > 0) {
      const deleteButton = await page.locator('button:has-text("Delete")').first();

      if (await deleteButton.isVisible().catch(() => false)) {
        console.log('Clicking Delete button...');

        // Listen for confirm dialog
        page.once('dialog', dialog => {
          console.log(`Confirm dialog appeared: ${dialog.message()}`);
          dialog.accept();
        });

        await deleteButton.click();
        await sleep(3000);

        testResults.screenshots.push(await takeScreenshot(page, 'step7_after_delete'));

        // Check if row count decreased
        const afterDeleteRows = await page.locator('table tbody tr').count().catch(() => 0);

        if (afterDeleteRows < currentRows) {
          console.log('✅ Assistant deleted successfully');
          testResults.passed.push('Delete Assistant');
        } else {
          console.log('⚠️  Assistant may not have been deleted');
          testResults.failed.push('Delete Assistant');
        }
      } else {
        console.log('⚠️  Delete button not found');
        testResults.failed.push('Delete Button Availability');
      }
    }

  } catch (error) {
    console.error('❌ Test execution error:', error);
    testResults.failed.push(`Test Error: ${error.message}`);
    testResults.screenshots.push(await takeScreenshot(page, 'error_state'));
  }

  // ==========================================
  // FINAL RESULTS
  // ==========================================
  console.log('\n\n' + '='.repeat(60));
  console.log('📊 TEST RESULTS SUMMARY');
  console.log('='.repeat(60));

  console.log(`\n✅ PASSED (${testResults.passed.length}):`);
  testResults.passed.forEach(test => console.log(`   - ${test}`));

  if (testResults.failed.length > 0) {
    console.log(`\n❌ FAILED (${testResults.failed.length}):`);
    testResults.failed.forEach(test => console.log(`   - ${test}`));
  }

  console.log(`\n📸 Screenshots saved: ${testResults.screenshots.length}`);
  console.log(`📁 Location: ${SCREENSHOTS_DIR}/`);

  const successRate = (testResults.passed.length / (testResults.passed.length + testResults.failed.length) * 100).toFixed(1);
  console.log(`\n📈 Success Rate: ${successRate}%`);

  console.log('\n' + '='.repeat(60));

  // Keep browser open for 10 seconds for review
  console.log('\n⏳ Keeping browser open for 10 seconds for review...\n');
  await sleep(10000);

  await context.close();
  await browser.close();

  console.log('✅ Test execution completed\n');
}

// Run the tests
runTests().catch(console.error);
