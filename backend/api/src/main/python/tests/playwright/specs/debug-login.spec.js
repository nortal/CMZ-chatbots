/**
 * Debug Login - Capture Console Errors
 */

const { test, expect } = require('@playwright/test');

const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:3001';

test('debug login with console capture', async ({ page }) => {
  // Capture all console messages
  const consoleMessages = [];
  page.on('console', msg => {
    consoleMessages.push({
      type: msg.type(),
      text: msg.text()
    });
    console.log(`[BROWSER ${msg.type()}]:`, msg.text());
  });

  // Capture network failures
  page.on('requestfailed', request => {
    console.log(`[NETWORK FAIL]: ${request.url()} - ${request.failure().errorText}`);
  });

  // Navigate to login page
  console.log('Navigating to frontend...');
  await page.goto(FRONTEND_URL);
  await page.waitForLoadState('networkidle');

  // Fill login form
  console.log('Filling login form...');
  await page.fill('input[type="email"]', 'test@cmz.org');
  await page.fill('input[type="password"]', 'testpass123');

  // Screenshot before login
  await page.screenshot({ path: 'reports/debug-before-login.png', fullPage: true });

  // Click login and wait
  console.log('Clicking login button...');
  await page.click('button[type="submit"]');

  // Wait for response
  await page.waitForTimeout(5000);

  // Screenshot after login attempt
  await page.screenshot({ path: 'reports/debug-after-login.png', fullPage: true });

  // Check for error message
  const errorMessage = await page.locator('text=Invalid email or password').first().textContent().catch(() => null);
  if (errorMessage) {
    console.log('[ERROR DETECTED]:', errorMessage);
  }

  // Print all console messages
  console.log('\n=== ALL CONSOLE MESSAGES ===');
  consoleMessages.forEach(msg => {
    console.log(`[${msg.type}]: ${msg.text}`);
  });
});
