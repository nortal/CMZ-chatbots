/**
 * Debug Animal Config Save Button - Console and Network Analysis
 *
 * This test captures ALL browser console messages and network activity
 * to debug why the Save Configuration button is not sending PATCH requests.
 *
 * Debug Logging Colors:
 * 🔴 RED - Button onClick handler (AnimalConfig.tsx lines 807-823)
 * 🟠 ORANGE - handleSaveConfig function (AnimalConfig.tsx lines 96-123)
 * 🟡 YELLOW - updateConfig hook (useAnimals.ts lines 85-105)
 * 🟢 GREEN - updateAnimalConfig API (api.ts lines 198-217)
 */

const { test, expect } = require('@playwright/test');

test.describe('Debug Animal Config Save Button', () => {
  let consoleMessages = [];
  let networkRequests = [];

  test.beforeEach(async ({ page }) => {
    // Capture ALL console messages
    page.on('console', msg => {
      const timestamp = new Date().toISOString();
      const logEntry = {
        timestamp,
        type: msg.type(),
        text: msg.text(),
        location: msg.location()
      };
      consoleMessages.push(logEntry);

      // Real-time console output with color coding
      const prefix = msg.text().includes('🔴') ? '🔴 RED' :
                     msg.text().includes('🟠') ? '🟠 ORANGE' :
                     msg.text().includes('🟡') ? '🟡 YELLOW' :
                     msg.text().includes('🟢') ? '🟢 GREEN' : '⚪';

      console.log(`[${timestamp}] ${prefix} [${msg.type()}] ${msg.text()}`);
    });

    // Capture ALL network requests
    page.on('request', request => {
      const requestInfo = {
        timestamp: new Date().toISOString(),
        method: request.method(),
        url: request.url(),
        headers: request.headers(),
        postData: request.postData()
      };
      networkRequests.push(requestInfo);

      // Highlight PATCH requests
      if (request.method() === 'PATCH') {
        console.log(`\n🚨 PATCH REQUEST DETECTED: ${request.url()}`);
        console.log(`   Headers: ${JSON.stringify(request.headers(), null, 2)}`);
        console.log(`   Body: ${request.postData()}\n`);
      }
    });

    // Capture network responses
    page.on('response', response => {
      if (response.request().method() === 'PATCH') {
        console.log(`\n✅ PATCH RESPONSE: ${response.status()} ${response.url()}\n`);
      }
    });

    // Capture page errors
    page.on('pageerror', error => {
      console.log(`\n❌ PAGE ERROR: ${error.message}\n`);
      consoleMessages.push({
        timestamp: new Date().toISOString(),
        type: 'error',
        text: error.message,
        stack: error.stack
      });
    });
  });

  test('Debug Save Configuration button with comprehensive logging', async ({ page }) => {
    const frontendUrl = process.env.FRONTEND_URL || 'http://localhost:3000';

    console.log('\n╔════════════════════════════════════════════════════════════════╗');
    console.log('║  Animal Config Save Button Debug Test - Started               ║');
    console.log('╚════════════════════════════════════════════════════════════════╝\n');

    // Step 1: Navigate to frontend
    console.log('📍 Step 1: Navigating to frontend...');
    await page.goto(frontendUrl, { waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);

    // Step 2: Login
    console.log('📍 Step 2: Logging in as test@cmz.org...');
    await page.fill('input[type="email"]', 'test@cmz.org');
    await page.fill('input[type="password"]', 'testpass123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard', { timeout: 10000 });
    console.log('✅ Login successful, on dashboard\n');

    // Step 3: Navigate to Animal Management
    console.log('📍 Step 3: Navigating to Animal Management...');
    await page.click('text=Animal Management');
    await page.waitForTimeout(1000);
    await page.click('text=Chatbot Personalities');
    await page.waitForTimeout(3000);

    // Take screenshot to see what's on the page
    await page.screenshot({ path: '/tmp/chatbot-personalities-page.png' });
    console.log('📸 Screenshot saved to /tmp/chatbot-personalities-page.png');

    // Check if there's any error message
    const pageContent = await page.content();
    if (pageContent.includes('Error') || pageContent.includes('error')) {
      console.log('⚠️  Page contains error text');
    }

    console.log('✅ On Chatbot Personalities page\n');

    // Step 4: Find and click first animal in the list
    console.log('📍 Step 4: Finding first animal in list...');

    // Wait for table to load
    await page.waitForSelector('table tbody tr', { timeout: 10000 });

    // Get all visible animal names
    const animalNames = await page.$$eval('table tbody tr td:first-child', cells =>
      cells.map(cell => cell.textContent.trim())
    );
    console.log(`   Found ${animalNames.length} animals:`, animalNames.slice(0, 5));

    // Click the first animal row
    const firstAnimalRow = page.locator('table tbody tr').first();
    await expect(firstAnimalRow).toBeVisible({ timeout: 5000 });
    await firstAnimalRow.click();
    await page.waitForTimeout(1000);

    const selectedAnimal = animalNames[0] || 'Unknown';
    console.log(`✅ Selected first animal: ${selectedAnimal}\n`);

    // Step 5: Click Configure button
    console.log('📍 Step 5: Clicking Configure button...');
    const configureButton = page.locator('button:has-text("Configure")');
    await expect(configureButton).toBeVisible({ timeout: 5000 });
    await configureButton.click();
    await page.waitForTimeout(2000);
    console.log('✅ Configure dialog opened\n');

    // Step 6: Navigate to System Prompt tab
    console.log('📍 Step 6: Clicking System Prompt tab...');
    const systemPromptTab = page.locator('button[role="tab"]:has-text("System Prompt")');
    await expect(systemPromptTab).toBeVisible({ timeout: 5000 });
    await systemPromptTab.click();
    await page.waitForTimeout(1000);
    console.log('✅ On System Prompt tab\n');

    // Step 7: Update systemPrompt field
    console.log('📍 Step 7: Updating systemPrompt field...');
    const testContent = `DEBUG TEST ${Date.now()}: Testing PATCH request generation`;
    console.log(`   Content: "${testContent}"`);

    const textarea = page.locator('textarea[name="systemPrompt"]');
    await expect(textarea).toBeVisible({ timeout: 5000 });
    await textarea.clear();
    await textarea.fill(testContent);
    await page.waitForTimeout(1000);

    // Verify the content was entered
    const actualValue = await textarea.inputValue();
    console.log(`   Verified content: "${actualValue}"`);
    expect(actualValue).toBe(testContent);
    console.log('✅ systemPrompt field updated\n');

    // Step 8: Click Save Configuration button
    console.log('📍 Step 8: Clicking Save Configuration button...');
    console.log('⏱️  Starting 30-second monitoring period for PATCH request...\n');

    const saveButton = page.locator('button:has-text("Save Configuration")');
    await expect(saveButton).toBeVisible({ timeout: 5000 });

    // Clear previous network requests to focus on Save action
    networkRequests = [];
    consoleMessages = [];

    // Click Save button
    console.log('🖱️  CLICKING SAVE BUTTON NOW...\n');
    await saveButton.click();

    // Wait and monitor for 30 seconds
    console.log('📊 Console Messages (Real-time):');
    console.log('─────────────────────────────────────────────────────────────\n');

    for (let i = 0; i < 30; i++) {
      await page.waitForTimeout(1000);

      // Check if PATCH request was sent
      const patchRequest = networkRequests.find(req => req.method === 'PATCH');
      if (patchRequest) {
        console.log('\n✅ PATCH REQUEST FOUND!');
        console.log(`   URL: ${patchRequest.url}`);
        console.log(`   Time: ${patchRequest.timestamp}`);
        break;
      }

      if ((i + 1) % 5 === 0) {
        console.log(`\n⏱️  ${i + 1} seconds elapsed, no PATCH request yet...`);
      }
    }

    // Step 9: Analysis
    console.log('\n\n╔════════════════════════════════════════════════════════════════╗');
    console.log('║  ANALYSIS RESULTS                                              ║');
    console.log('╚════════════════════════════════════════════════════════════════╝\n');

    // Analyze console messages by color
    const redLogs = consoleMessages.filter(msg => msg.text.includes('🔴'));
    const orangeLogs = consoleMessages.filter(msg => msg.text.includes('🟠'));
    const yellowLogs = consoleMessages.filter(msg => msg.text.includes('🟡'));
    const greenLogs = consoleMessages.filter(msg => msg.text.includes('🟢'));
    const errorLogs = consoleMessages.filter(msg => msg.type === 'error');

    console.log('📊 Debug Log Summary:');
    console.log(`   🔴 RED logs (Button onClick): ${redLogs.length}`);
    console.log(`   🟠 ORANGE logs (handleSaveConfig): ${orangeLogs.length}`);
    console.log(`   🟡 YELLOW logs (updateConfig hook): ${yellowLogs.length}`);
    console.log(`   🟢 GREEN logs (API function): ${greenLogs.length}`);
    console.log(`   ❌ Error logs: ${errorLogs.length}\n`);

    // Show first log of each color to see execution flow
    console.log('🔍 Execution Flow Analysis:\n');

    if (redLogs.length > 0) {
      console.log('✅ 🔴 Button onClick handler EXECUTED');
      console.log(`   First log: ${redLogs[0].text}\n`);
    } else {
      console.log('❌ 🔴 Button onClick handler NOT executed\n');
    }

    if (orangeLogs.length > 0) {
      console.log('✅ 🟠 handleSaveConfig function EXECUTED');
      console.log(`   First log: ${orangeLogs[0].text}\n`);
    } else {
      console.log('❌ 🟠 handleSaveConfig function NOT executed\n');
    }

    if (yellowLogs.length > 0) {
      console.log('✅ 🟡 updateConfig hook EXECUTED');
      console.log(`   First log: ${yellowLogs[0].text}\n`);
    } else {
      console.log('❌ 🟡 updateConfig hook NOT executed\n');
    }

    if (greenLogs.length > 0) {
      console.log('✅ 🟢 updateAnimalConfig API function EXECUTED');
      console.log(`   First log: ${greenLogs[0].text}\n`);
    } else {
      console.log('❌ 🟢 updateAnimalConfig API function NOT executed\n');
    }

    // Network activity summary
    console.log('🌐 Network Activity:');
    const patchRequests = networkRequests.filter(req => req.method === 'PATCH');
    const getRequests = networkRequests.filter(req => req.method === 'GET');
    const postRequests = networkRequests.filter(req => req.method === 'POST');

    console.log(`   PATCH requests: ${patchRequests.length}`);
    console.log(`   GET requests: ${getRequests.length}`);
    console.log(`   POST requests: ${postRequests.length}`);
    console.log(`   Total requests: ${networkRequests.length}\n`);

    // Show all network requests
    if (networkRequests.length > 0) {
      console.log('📋 All Network Requests:\n');
      networkRequests.forEach((req, idx) => {
        console.log(`   ${idx + 1}. ${req.method} ${req.url}`);
      });
      console.log('');
    }

    // Show errors if any
    if (errorLogs.length > 0) {
      console.log('❌ Errors Found:\n');
      errorLogs.forEach((err, idx) => {
        console.log(`   ${idx + 1}. ${err.text}`);
        if (err.stack) {
          console.log(`      Stack: ${err.stack}`);
        }
      });
      console.log('');
    }

    // Diagnosis
    console.log('🔬 DIAGNOSIS:');
    if (greenLogs.length === 0 && yellowLogs.length === 0 && orangeLogs.length === 0 && redLogs.length === 0) {
      console.log('   ⚠️  NO debug logs found - possible issues:');
      console.log('      1. Debug logging not properly deployed');
      console.log('      2. Frontend bundle not rebuilt');
      console.log('      3. Browser cache preventing new code execution');
    } else if (redLogs.length > 0 && orangeLogs.length === 0) {
      console.log('   ⚠️  Button clicked but handleSaveConfig not called');
      console.log('      - Check submitForm implementation');
      console.log('      - Check if handleSubmit prevents default form behavior');
    } else if (orangeLogs.length > 0 && yellowLogs.length === 0) {
      console.log('   ⚠️  handleSaveConfig called but updateConfig hook not invoked');
      console.log('      - Check updateConfig hook binding');
      console.log('      - Check if updateConfig is undefined or null');
    } else if (yellowLogs.length > 0 && greenLogs.length === 0) {
      console.log('   ⚠️  updateConfig hook called but API function not invoked');
      console.log('      - Check API import in useAnimals.ts');
      console.log('      - Check if updateAnimalConfig is properly imported');
    } else if (greenLogs.length > 0 && patchRequests.length === 0) {
      console.log('   ⚠️  API function called but PATCH request not sent');
      console.log('      - Check fetch implementation');
      console.log('      - Check if request is being cancelled');
      console.log('      - Check network errors or CORS issues');
    }

    console.log('\n╔════════════════════════════════════════════════════════════════╗');
    console.log('║  Test Complete - Check logs above for detailed analysis       ║');
    console.log('╚════════════════════════════════════════════════════════════════╝\n');

    // Save detailed logs to file
    const fs = require('fs');
    const logData = {
      timestamp: new Date().toISOString(),
      consoleMessages,
      networkRequests,
      summary: {
        redLogs: redLogs.length,
        orangeLogs: orangeLogs.length,
        yellowLogs: yellowLogs.length,
        greenLogs: greenLogs.length,
        errorLogs: errorLogs.length,
        patchRequests: patchRequests.length,
        totalRequests: networkRequests.length
      }
    };

    fs.writeFileSync(
      '/Users/keithstegbauer/repositories/CMZ-chatbots/backend/api/src/main/python/tests/playwright/debug-save-button-logs.json',
      JSON.stringify(logData, null, 2)
    );

    console.log('📄 Detailed logs saved to: debug-save-button-logs.json\n');
  });
});
