/**
 * Simplified Animal Config Save Button Debug Test
 *
 * Goes directly to the problem: Testing the Save Configuration button
 * with comprehensive browser console logging to identify where PATCH request fails.
 */

const { test, expect } = require('@playwright/test');

test.describe('Debug Save Button - Simplified', () => {
  let consoleMessages = [];
  let networkRequests = [];

  test.beforeEach(async ({ page }) => {
    // Capture ALL console messages with color coding
    page.on('console', msg => {
      const timestamp = new Date().toISOString();
      const text = msg.text();
      const logEntry = {
        timestamp,
        type: msg.type(),
        text,
        location: msg.location()
      };
      consoleMessages.push(logEntry);

      // Color-coded real-time output
      const prefix = text.includes('🔴') ? '🔴 RED (onClick)' :
                     text.includes('🟠') ? '🟠 ORANGE (handleSave)' :
                     text.includes('🟡') ? '🟡 YELLOW (updateConfig)' :
                     text.includes('🟢') ? '🟢 GREEN (API)' : '⚪';

      if (text.includes('🔴') || text.includes('🟠') || text.includes('🟡') || text.includes('🟢')) {
        console.log(`\n[${timestamp.split('T')[1]}] ${prefix}`);
        console.log(`   ${text}\n`);
      }
    });

    // Capture network requests, especially PATCH
    page.on('request', request => {
      networkRequests.push({
        timestamp: new Date().toISOString(),
        method: request.method(),
        url: request.url(),
        postData: request.postData()
      });

      if (request.method() === 'PATCH') {
        console.log(`\n🚨 PATCH REQUEST: ${request.url()}`);
        console.log(`   Body: ${request.postData()}\n`);
      }
    });

    // Capture errors
    page.on('pageerror', error => {
      console.log(`\n❌ PAGE ERROR: ${error.message}\n`);
    });
  });

  test('Debug Save button with browser console visible', async ({ page }) => {
    console.log('\n═══════════════════════════════════════════════════');
    console.log('  Animal Config Save Button Debug - Simple Test');
    console.log('═══════════════════════════════════════════════════\n');

    const frontendUrl = 'http://localhost:3000';

    // Step 1: Login
    console.log('Step 1: Logging in...');
    await page.goto(`${frontendUrl}/login`);
    await page.fill('input[type="email"]', 'test@cmz.org');
    await page.fill('input[type="password"]', 'testpass123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard', { timeout: 10000 });
    console.log('✅ Logged in\n');

    // Step 2: Go directly to Chatbot Personalities (animal config)
    console.log('Step 2: Navigating to Chatbot Personalities...');
    await page.goto(`${frontendUrl}/animals/config`);
    await page.waitForTimeout(3000);

    // Take a screenshot to see the page
    await page.screenshot({ path: '/tmp/animals-page.png' });
    console.log('📸 Screenshot: /tmp/animals-page.png');

    // Look for Charlie Test card
    console.log('   Looking for Charlie Test card...');
    const charlieCard = page.locator('text=Charlie Test-1760449970').first();
    const charlieExists = await charlieCard.count() > 0;
    console.log(`   Charlie card found: ${charlieExists}`);

    // Click the first Configure button (Charlie is first card)
    console.log('   Clicking first Configure button...');
    const configureButton = page.locator('button:has-text("Configure")').first();
    await configureButton.click();
    await page.waitForTimeout(2000);

    await page.screenshot({ path: '/tmp/config-dialog.png' });
    console.log('📸 Screenshot: /tmp/config-dialog.png');

    // The details modal should be open now - scroll down to see more chatbot configuration
    console.log('✅ Animal details modal opened\n');

    // Step 3: Scroll within the modal to see all configuration options
    console.log('Step 3: Looking for chatbot configuration fields...');

    // Scroll down in the modal to see all fields
    await page.mouse.wheel(0, 500);
    await page.waitForTimeout(1000);

    await page.screenshot({ path: '/tmp/scrolled-details.png' });
    console.log('📸 Screenshot after scroll: /tmp/scrolled-details.png');

    // Look for textareas or input fields that might contain systemPrompt
    const textareas = await page.locator('textarea').count();
    const inputs = await page.locator('input[type="text"]').count();
    console.log(`   Textareas found: ${textareas}`);
    console.log(`   Text inputs found: ${inputs}`);

    // Look for any Save button
    const saveButtons = page.locator('button').filter({ hasText: /save/i });
    const saveCount = await saveButtons.count();
    console.log(`   Save buttons found: ${saveCount}`);

    if (saveCount > 0) {
      console.log('   ✅ Found Save button!\n');

      // Step 4: Find and update a textarea (likely systemPrompt or personality)
      console.log('Step 4: Updating a textarea field...');

      if (textareas > 0) {
        const textarea = page.locator('textarea').first();
        const testContent = `DEBUG TEST ${Date.now()}: Testing PATCH request`;

        // Get the field name if possible
        const fieldName = await textarea.getAttribute('name').catch(() => 'unknown');
        console.log(`   Field name: ${fieldName}`);

        await textarea.clear();
        await textarea.fill(testContent);
        await page.waitForTimeout(500);

        const actualValue = await textarea.inputValue();
        console.log(`   ✅ Field updated: "${actualValue.substring(0, 50)}..."\n`);

        // Step 5: Click Save button
        console.log('Step 5: Clicking Save button...');
        console.log('🎯 MONITORING FOR DEBUG LOGS AND PATCH REQUEST...\n');
        console.log('══════════════════════════════════════════════════\n');

        // Clear logs to focus on Save action
        consoleMessages = [];
        networkRequests = [];

        // Click Save
        console.log('\n🖱️  CLICKING SAVE BUTTON NOW...\n');
        await saveButtons.first().click();

        // Monitor for 15 seconds
        for (let i = 0; i < 15; i++) {
          await page.waitForTimeout(1000);

          const patchRequest = networkRequests.find(req => req.method === 'PATCH');
          if (patchRequest) {
            console.log('\n✅ SUCCESS: PATCH REQUEST DETECTED!');
            console.log(`   URL: ${patchRequest.url}`);
            break;
          }

          if ((i + 1) % 5 === 0) {
            console.log(`   ${i + 1} seconds elapsed...`);
          }
        }

        // Analysis
        console.log('\n\n═══════════════════════════════════════════════════');
        console.log('  ANALYSIS');
        console.log('═══════════════════════════════════════════════════\n');

        const redLogs = consoleMessages.filter(msg => msg.text.includes('🔴'));
        const orangeLogs = consoleMessages.filter(msg => msg.text.includes('🟠'));
        const yellowLogs = consoleMessages.filter(msg => msg.text.includes('🟡'));
        const greenLogs = consoleMessages.filter(msg => msg.text.includes('🟢'));
        const patchRequests = networkRequests.filter(req => req.method === 'PATCH');

        console.log('Debug Log Count:');
        console.log(`  🔴 Button onClick: ${redLogs.length}`);
        console.log(`  🟠 handleSaveConfig: ${orangeLogs.length}`);
        console.log(`  🟡 updateConfig hook: ${yellowLogs.length}`);
        console.log(`  🟢 API function: ${greenLogs.length}`);
        console.log(`  📡 PATCH requests: ${patchRequests.length}\n`);

        console.log('Execution Flow:');
          if (redLogs.length === 0) {
            console.log('  ❌ Button onClick handler NOT executed');
            console.log('      → Button click event not firing');
            console.log('      → Check if button is actually clickable');
          } else {
            console.log('  ✅ Button onClick handler executed');
            if (orangeLogs.length === 0) {
              console.log('  ❌ handleSaveConfig NOT called');
              console.log('      → submitForm not working');
              console.log('      → Check form submission logic');
            } else {
              console.log('  ✅ handleSaveConfig called');
              if (yellowLogs.length === 0) {
                console.log('  ❌ updateConfig hook NOT invoked');
                console.log('      → Hook binding issue');
                console.log('      → Check useAnimals import');
              } else {
                console.log('  ✅ updateConfig hook invoked');
                if (greenLogs.length === 0) {
                  console.log('  ❌ updateAnimalConfig API NOT called');
                  console.log('      → API import issue');
                  console.log('      → Check api.ts import');
                } else {
                  console.log('  ✅ updateAnimalConfig API called');
                  if (patchRequests.length === 0) {
                    console.log('  ❌ PATCH request NOT sent');
                    console.log('      → fetch call failed');
                    console.log('      → Check network errors');
                  } else {
                    console.log('  ✅ PATCH request sent successfully!');
                  }
                }
              }
            }
          }

          // Show all debug logs
          if (redLogs.length + orangeLogs.length + yellowLogs.length + greenLogs.length > 0) {
            console.log('\nDetailed Debug Logs:');
            [...redLogs, ...orangeLogs, ...yellowLogs, ...greenLogs].forEach(log => {
              console.log(`  ${log.text}`);
            });
          } else {
            console.log('\n⚠️  NO DEBUG LOGS FOUND!');
            console.log('     Possible causes:');
            console.log('     - Frontend code not rebuilt with debug logs');
            console.log('     - Browser cache serving old code');
            console.log('     - Debug console.log statements removed');
          }

        console.log('\n═══════════════════════════════════════════════════\n');

        // Final screenshot
        await page.screenshot({ path: '/tmp/after-save-click.png' });
        console.log('📸 Final screenshot: /tmp/after-save-click.png\n');
      } else {
        console.log('❌ No textareas found to update\n');
      }
    } else {
      console.log('❌ No Save button found\n');
      await page.screenshot({ path: '/tmp/no-save-button.png' });
    }
  });
});
