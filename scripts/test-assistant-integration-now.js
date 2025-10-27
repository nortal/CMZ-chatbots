#!/usr/bin/env node
/**
 * Immediate Assistant Integration Test
 *
 * This script tests the specific issues identified in the screenshots:
 * 1. Charlie responding as puma instead of elephant
 * 2. PATCH operation failures in configuration
 * 3. System prompt not propagating to chat responses
 *
 * Run with: node scripts/test-assistant-integration-now.js
 */

const { chromium } = require('playwright');

async function testAssistantIntegration() {
  console.log('🧪 Starting Assistant Integration Test');
  console.log('📅 Timestamp:', new Date().toISOString());

  // Launch browser with console open
  const browser = await chromium.launch({
    headless: false,
    devtools: true,
    slowMo: 1500
  });

  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    // Setup comprehensive monitoring
    setupConsoleMonitoring(page);

    // Phase 1: Authentication
    console.log('\n🔐 Phase 1: Authentication');
    await authenticateUser(page);

    // Phase 2: Test Current Charlie Configuration
    console.log('\n🐘 Phase 2: Testing Current Charlie Configuration');
    await testCurrentCharlieChat(page);

    // Phase 3: Modify System Prompt
    console.log('\n✏️ Phase 3: Modifying System Prompt');
    await modifyCharliePrompt(page);

    // Phase 4: Test Updated Configuration
    console.log('\n🔄 Phase 4: Testing Updated Configuration');
    await testUpdatedCharlieChat(page);

    console.log('\n✅ Test completed successfully!');

  } catch (error) {
    console.error('\n❌ Test failed:', error.message);
    await page.screenshot({ path: 'test-results/error-screenshot.png', fullPage: true });
    throw error;
  } finally {
    // Keep browser open for manual inspection
    console.log('\n⏸️ Browser kept open for manual inspection');
    console.log('Press Ctrl+C to close when done reviewing');

    // Wait indefinitely until user closes
    await page.waitForTimeout(300000); // 5 minutes max
    await browser.close();
  }
}

function setupConsoleMonitoring(page) {
  console.log('🖥️ Setting up console monitoring...');

  // Monitor browser console
  page.on('console', msg => {
    const type = msg.type();
    const text = msg.text();

    if (type === 'error') {
      console.error(`🚨 [BROWSER ERROR]: ${text}`);
    } else if (type === 'warn') {
      console.warn(`⚠️ [BROWSER WARN]: ${text}`);
    } else if (text.includes('PATCH') || text.includes('POST')) {
      console.log(`📡 [BROWSER LOG]: ${text}`);
    }
  });

  // Monitor network requests
  page.on('request', request => {
    const method = request.method();
    const url = request.url();

    if (method === 'PATCH' || method === 'POST') {
      console.log(`🌐 ${method} Request: ${url}`);
    }
  });

  page.on('response', async response => {
    const status = response.status();
    const url = response.url();
    const method = response.request().method();

    if ((method === 'PATCH' || method === 'POST') && (url.includes('/animal') || url.includes('/convo'))) {
      if (status >= 400) {
        console.error(`❌ ${method} ${status}: ${url}`);
        try {
          const errorBody = await response.text();
          console.error(`Error Body: ${errorBody}`);
        } catch (e) {
          console.error('Could not read error response body');
        }
      } else {
        console.log(`✅ ${method} ${status}: ${url}`);
      }
    }
  });

  // Open developer console
  page.keyboard.press('F12');
}

async function authenticateUser(page) {
  await page.goto('http://localhost:3001');

  // Handle potential login page vs already logged in
  try {
    await page.fill('input[name="email"]', 'test@cmz.org', { timeout: 3000 });
    await page.fill('input[name="password"]', 'testpass123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard', { timeout: 10000 });
  } catch (error) {
    // Might already be logged in
    if (page.url().includes('dashboard')) {
      console.log('✅ Already authenticated');
    } else {
      throw error;
    }
  }

  await page.screenshot({ path: 'test-results/01-authenticated.png', fullPage: true });
  console.log('✅ Authentication completed');
}

async function testCurrentCharlieChat(page) {
  // Navigate to chat
  await page.click('text=Chat with Animals');
  await page.waitForTimeout(2000);

  // Find Charlie in the animal list
  await page.click('text=Charlie');
  await page.waitForTimeout(2000);

  // Send test message
  const testMessage = "Hello! What kind of animal are you?";
  await page.fill('input[name="message"], textarea[name="message"]', testMessage);
  await page.click('button:has-text("Send"), button[type="submit"]');

  // Wait for response
  await page.waitForSelector('.chat-message.assistant, .response-message', { timeout: 15000 });

  // Get response text
  const response = await page.locator('.chat-message.assistant, .response-message').last().textContent();

  console.log(`📤 Sent: ${testMessage}`);
  console.log(`📥 Response: ${response}`);

  // Check for the puma issue
  if (response.toLowerCase().includes('puma') || response.toLowerCase().includes('cougar')) {
    console.error('❌ BUG CONFIRMED: Charlie is responding as puma/cougar instead of elephant!');
  } else if (response.toLowerCase().includes('elephant')) {
    console.log('✅ Charlie correctly identifies as elephant');
  } else {
    console.warn('⚠️ Charlie response unclear about animal type');
  }

  await page.screenshot({ path: 'test-results/02-current-charlie-chat.png', fullPage: true });
}

async function modifyCharliePrompt(page) {
  // Navigate to Animal Configuration
  await page.click('text=Animal Management');
  await page.waitForTimeout(1000);
  await page.click('text=Chatbot Personalities');
  await page.waitForTimeout(2000);

  // Find Charlie
  await page.click('text=Charlie Test-1760449970');
  await page.waitForTimeout(2000);

  // Click Configure
  await page.click('button:has-text("Configure")');
  await page.waitForTimeout(2000);

  await page.screenshot({ path: 'test-results/03a-config-dialog-opened.png', fullPage: true });

  // Get current prompt
  const currentPrompt = await page.locator('textarea[name="systemPrompt"]').inputValue();
  console.log('📄 Current system prompt:', currentPrompt.substring(0, 100) + '...');

  // Create new test prompt
  const newPrompt = `You are Charlie, a wise African elephant at Cougar Mountain Zoo.
You ALWAYS mention your large ears and trumpet sound when introducing yourself.
You are passionate about conservation and ALWAYS end responses with 'Remember to protect our wildlife!'
CRITICAL: You are an ELEPHANT, never a puma or cougar.`;

  // Update the prompt
  await page.locator('textarea[name="systemPrompt"]').clear();
  await page.locator('textarea[name="systemPrompt"]').fill(newPrompt);

  console.log('✏️ Updated system prompt with test content');

  // Save and monitor for PATCH errors
  let patchSuccess = false;

  page.on('response', async response => {
    if (response.request().method() === 'PATCH' && response.url().includes('/animal')) {
      if (response.status() < 400) {
        patchSuccess = true;
        console.log('✅ PATCH operation successful');
      } else {
        console.error(`❌ PATCH failed with status ${response.status()}`);
      }
    }
  });

  await page.click('button:has-text("Save Configuration")');
  await page.waitForTimeout(3000);

  await page.screenshot({ path: 'test-results/03b-config-saved.png', fullPage: true });

  if (!patchSuccess) {
    console.error('❌ PATCH operation may have failed - check browser console');
  }
}

async function testUpdatedCharlieChat(page) {
  // Navigate back to chat
  await page.click('text=Chat with Animals');
  await page.waitForTimeout(2000);

  // Select Charlie again
  await page.click('text=Charlie');
  await page.waitForTimeout(2000);

  // Send the same test message
  const testMessage = "Hello! What kind of animal are you?";
  await page.fill('input[name="message"], textarea[name="message"]', testMessage);
  await page.click('button:has-text("Send"), button[type="submit"]');

  // Wait for response
  await page.waitForSelector('.chat-message.assistant, .response-message', { timeout: 15000 });

  // Get response text
  const response = await page.locator('.chat-message.assistant, .response-message').last().textContent();

  console.log(`📤 Sent: ${testMessage}`);
  console.log(`📥 Updated Response: ${response}`);

  // Validate updated prompt is working
  const checks = {
    elephant: response.toLowerCase().includes('elephant'),
    largeEars: response.toLowerCase().includes('large ears') || response.toLowerCase().includes('big ears'),
    trumpet: response.toLowerCase().includes('trumpet'),
    wildlife: response.includes('Remember to protect our wildlife!'),
    notPuma: !response.toLowerCase().includes('puma') && !response.toLowerCase().includes('cougar')
  };

  console.log('\n🧪 Validation Results:');
  console.log(`🐘 Identifies as elephant: ${checks.elephant ? '✅' : '❌'}`);
  console.log(`👂 Mentions large ears: ${checks.largeEars ? '✅' : '❌'}`);
  console.log(`🎺 Mentions trumpet: ${checks.trumpet ? '✅' : '❌'}`);
  console.log(`🌿 Ends with wildlife message: ${checks.wildlife ? '✅' : '❌'}`);
  console.log(`🚫 Not puma/cougar: ${checks.notPuma ? '✅' : '❌'}`);

  const passedChecks = Object.values(checks).filter(Boolean).length;
  console.log(`\n📊 Overall Score: ${passedChecks}/5 checks passed`);

  if (passedChecks >= 4) {
    console.log('🎉 System prompt update successful!');
  } else {
    console.error('❌ System prompt update may not be working correctly');
  }

  await page.screenshot({ path: 'test-results/04-updated-charlie-chat.png', fullPage: true });
}

// Run the test
testAssistantIntegration().catch(console.error);