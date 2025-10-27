/**
 * DEBUG TEST: SystemPrompt Propagation Tracing
 *
 * Purpose: Trace exactly where systemPrompt data is lost in the update flow
 *
 * Test Flow:
 * 1. Quick authentication
 * 2. Navigate to Animal Management
 * 3. Update ONLY systemPrompt field with test content
 * 4. Monitor API logs for debug output
 *
 * Success Criteria:
 * - PATCH operation succeeds (HTTP 200)
 * - Debug output appears in API logs
 * - Can identify if systemPrompt reaches service layer
 */

const { test, expect } = require('@playwright/test');

test.describe('SystemPrompt Propagation Debug', () => {
  test('should trace systemPrompt data flow from UI to service layer', async ({ page }) => {
    const frontendUrl = process.env.FRONTEND_URL || 'http://localhost:3001';
    const testTimestamp = Date.now();
    const testContent = `DEBUG TEST ${testTimestamp}: You are Charlie the elephant. This is a systemPrompt test.`;

    console.log('\n🔍 Starting SystemPrompt Propagation Debug Test');
    console.log(`📝 Test Content: ${testContent}`);

    // ============================================================================
    // PHASE 1: Quick Authentication
    // ============================================================================
    console.log('\n📋 Phase 1: Quick Authentication');

    await page.goto(frontendUrl);
    await page.waitForLoadState('networkidle');

    // Login
    await page.fill('input[type="email"]', 'test@cmz.org');
    await page.fill('input[type="password"]', 'testpass123');
    await page.click('button[type="submit"]');

    // Wait for dashboard
    await page.waitForURL('**/dashboard', { timeout: 10000 });
    console.log('✅ Authentication successful');

    // ============================================================================
    // PHASE 2: Navigate to Animal Management
    // ============================================================================
    console.log('\n📋 Phase 2: Navigate to Animal Management');

    await page.click('text=Animal Management');
    await page.waitForLoadState('networkidle');

    // Wait for Chatbot Personalities tab
    const chatbotTab = page.locator('button:has-text("Chatbot Personalities")');
    await chatbotTab.waitFor({ state: 'visible', timeout: 10000 });
    await chatbotTab.click();
    await page.waitForLoadState('networkidle');
    console.log('✅ Navigated to Chatbot Personalities');

    // ============================================================================
    // PHASE 3: Open Configuration for Charlie Test
    // ============================================================================
    console.log('\n📋 Phase 3: Open Configuration Dialog');

    // Find Charlie Test row and click Configure
    const configureButton = page.locator('button:has-text("Configure")').first();
    await configureButton.waitFor({ state: 'visible', timeout: 10000 });

    // Setup network monitoring BEFORE clicking Configure
    const patchRequestPromise = page.waitForRequest(
      request => request.url().includes('/animal/') && request.method() === 'PATCH',
      { timeout: 30000 }
    );

    const patchResponsePromise = page.waitForResponse(
      response => response.url().includes('/animal/') && response.request().method() === 'PATCH',
      { timeout: 30000 }
    );

    await configureButton.click();

    // Wait for dialog to open
    const dialog = page.locator('[role="dialog"]');
    await dialog.waitFor({ state: 'visible', timeout: 10000 });
    console.log('✅ Configuration dialog opened');

    // ============================================================================
    // PHASE 4: Navigate to System Prompt Tab
    // ============================================================================
    console.log('\n📋 Phase 4: Navigate to System Prompt Tab');

    const systemPromptTab = dialog.locator('button:has-text("System Prompt")');
    await systemPromptTab.waitFor({ state: 'visible', timeout: 5000 });
    await systemPromptTab.click();
    await page.waitForTimeout(1000); // Wait for tab content to load
    console.log('✅ System Prompt tab opened');

    // ============================================================================
    // PHASE 5: Update SystemPrompt Field
    // ============================================================================
    console.log('\n📋 Phase 5: Update SystemPrompt Field');

    // Find the textarea for systemPrompt
    const systemPromptTextarea = dialog.locator('textarea').first();
    await systemPromptTextarea.waitFor({ state: 'visible', timeout: 5000 });

    // Clear existing content and enter test content
    await systemPromptTextarea.fill('');
    await systemPromptTextarea.fill(testContent);
    await page.waitForTimeout(500); // Let value settle

    // Verify the value was set
    const enteredValue = await systemPromptTextarea.inputValue();
    console.log(`📝 Entered value length: ${enteredValue.length} characters`);
    console.log(`📝 First 50 chars: ${enteredValue.substring(0, 50)}...`);

    expect(enteredValue).toBe(testContent);
    console.log('✅ SystemPrompt field updated with test content');

    // ============================================================================
    // PHASE 6: Save Configuration and Monitor Network
    // ============================================================================
    console.log('\n📋 Phase 6: Save Configuration');

    // Click Save Configuration button
    const saveButton = dialog.locator('button:has-text("Save Configuration")');
    await saveButton.waitFor({ state: 'visible', timeout: 5000 });
    await saveButton.click();

    console.log('🔄 Waiting for PATCH request...');

    try {
      // Wait for PATCH request
      const patchRequest = await patchRequestPromise;
      const requestBody = patchRequest.postDataJSON();

      console.log('\n📤 PATCH Request Captured:');
      console.log(`   URL: ${patchRequest.url()}`);
      console.log(`   Method: ${patchRequest.method()}`);
      console.log(`   Body keys: ${Object.keys(requestBody || {}).join(', ')}`);

      // Check if systemPrompt is in the request
      if (requestBody && 'systemPrompt' in requestBody) {
        console.log(`   ✅ systemPrompt PRESENT in request`);
        console.log(`   📝 systemPrompt value: ${requestBody.systemPrompt.substring(0, 80)}...`);
      } else {
        console.log(`   ❌ systemPrompt NOT FOUND in request`);
        console.log(`   📋 Full request body:`, JSON.stringify(requestBody, null, 2));
      }

      // Wait for response
      const patchResponse = await patchResponsePromise;
      const responseStatus = patchResponse.status();

      console.log('\n📥 PATCH Response:');
      console.log(`   Status: ${responseStatus}`);

      if (responseStatus === 200) {
        console.log('   ✅ PATCH succeeded');

        try {
          const responseBody = await patchResponse.json();
          console.log(`   Response body keys: ${Object.keys(responseBody || {}).join(', ')}`);

          if (responseBody && 'systemPrompt' in responseBody) {
            console.log(`   ✅ systemPrompt in response`);
            console.log(`   📝 Response systemPrompt: ${responseBody.systemPrompt.substring(0, 80)}...`);
          } else {
            console.log(`   ⚠️ systemPrompt not in response`);
          }
        } catch (e) {
          console.log(`   ⚠️ Could not parse response body: ${e.message}`);
        }
      } else {
        console.log(`   ❌ PATCH failed with status ${responseStatus}`);
      }

      // Check for browser console errors
      const consoleErrors = [];
      page.on('console', msg => {
        if (msg.type() === 'error') {
          consoleErrors.push(msg.text());
        }
      });

      await page.waitForTimeout(2000); // Wait for any console errors

      if (consoleErrors.length > 0) {
        console.log('\n⚠️ Browser Console Errors:');
        consoleErrors.forEach(err => console.log(`   ${err}`));
      } else {
        console.log('\n✅ No browser console errors');
      }

    } catch (error) {
      console.error(`\n❌ Error during network monitoring: ${error.message}`);
      throw error;
    }

    // ============================================================================
    // PHASE 7: Analysis Summary
    // ============================================================================
    console.log('\n' + '='.repeat(80));
    console.log('📊 SYSTEMPROMPT PROPAGATION ANALYSIS');
    console.log('='.repeat(80));
    console.log('\nNow check API logs for debug output:');
    console.log('  docker logs cmz-api-dev | grep -A5 "DEBUG update_animal_configuration"');
    console.log('\nExpected debug output:');
    console.log('  DEBUG update_animal_configuration: animal_id=charlie_003');
    console.log('  DEBUG update_animal_configuration: config_data keys=[...]');
    console.log('  DEBUG update_animal_configuration: systemPrompt=[value or NOT_FOUND]');
    console.log('\n' + '='.repeat(80));

    // Keep browser open for manual inspection
    await page.waitForTimeout(5000);
  });
});
