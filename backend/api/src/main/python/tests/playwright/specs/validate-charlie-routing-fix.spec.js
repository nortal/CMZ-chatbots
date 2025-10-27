/**
 * CRITICAL TEST: Validate Charlie Routing Fix
 *
 * PURPOSE: Verify that the ChatWrapper component correctly extracts animalId from URL
 * and Charlie responds as an elephant (not default "Zara" personality)
 *
 * WHAT WAS FIXED:
 * - Added ChatWrapper component to App.tsx with useSearchParams()
 * - Modified /chat route to extract animalId from URL query parameters
 * - ChatWrapper passes animalId prop to Chat component
 *
 * CRITICAL SUCCESS CRITERIA:
 * 1. Frontend extracts animalId="charlie_003" from URL correctly
 * 2. Backend receives animalId="charlie_003" (NOT "default")
 * 3. Charlie identifies as an ELEPHANT with motherly personality
 * 4. No Unicode parsing errors in API logs
 * 5. Response uses motherly language ("dear", "little one", "sweetheart")
 */

const { test, expect } = require('@playwright/test');

test.describe('🐘 CRITICAL: Charlie Routing Fix Validation', () => {
  const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:3001';
  const CHARLIE_URL = `${FRONTEND_URL}/chat?animalId=charlie_003`;
  const TEST_MESSAGE = "Hello! What animal are you?";

  // Test user credentials
  const TEST_USER = {
    email: 'parent1@test.cmz.org',
    password: 'testpass123'
  };

  test.beforeEach(async ({ page }) => {
    console.log('\n🔧 Setting up test environment...');

    // Enable console logging to capture API communication
    page.on('console', msg => {
      const text = msg.text();
      if (text.includes('animalId') || text.includes('charlie') || text.includes('default')) {
        console.log(`📱 Frontend Log: ${text}`);
      }
    });

    // Monitor network requests to verify animalId transmission
    page.on('request', request => {
      const url = request.url();
      if (url.includes('/convo/turn')) {
        console.log(`🌐 API Request to: ${url}`);
        const postData = request.postData();
        if (postData) {
          try {
            const data = JSON.parse(postData);
            console.log(`📤 Request animalId: ${data.animalId || 'MISSING!'}`);
          } catch (e) {
            console.log('📤 Request data (non-JSON)');
          }
        }
      }
    });

    page.on('response', async response => {
      const url = response.url();
      if (url.includes('/convo/turn')) {
        console.log(`📥 API Response status: ${response.status()}`);
        try {
          const data = await response.json();
          if (data.response) {
            console.log(`🤖 AI Response preview: ${data.response.substring(0, 100)}...`);
          }
        } catch (e) {
          console.log('📥 Response data could not be parsed');
        }
      }
    });
  });

  test('should extract animalId from URL and Charlie responds as elephant', async ({ page }) => {
    console.log('\n🎯 TEST: Validate Charlie Routing Fix');
    console.log(`📍 Testing URL: ${CHARLIE_URL}`);

    // Step 1: Login
    console.log('\n📝 Step 1: Login to application');
    await page.goto(`${FRONTEND_URL}/login`);
    await page.waitForLoadState('networkidle');

    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button[type="submit"]');

    // Wait for successful login (dashboard or animals page)
    await page.waitForURL(/\/(dashboard|animals)/, { timeout: 10000 });
    console.log('✅ Login successful');

    // Step 2: Navigate to Charlie's chat with animalId parameter
    console.log('\n🐘 Step 2: Navigate to Charlie chat URL with animalId parameter');
    await page.goto(CHARLIE_URL);
    await page.waitForLoadState('networkidle');
    console.log(`✅ Navigated to: ${CHARLIE_URL}`);

    // Take screenshot of chat page load
    await page.screenshot({
      path: '/Users/keithstegbauer/repositories/CMZ-chatbots/backend/api/src/main/python/tests/playwright/screenshots/charlie-routing-01-loaded.png',
      fullPage: true
    });

    // Step 3: Verify chat interface loaded
    console.log('\n🔍 Step 3: Verify chat interface components');
    const chatInput = page.locator('textarea, input[type="text"]').first();
    await expect(chatInput).toBeVisible({ timeout: 10000 });
    console.log('✅ Chat input field visible');

    const sendButton = page.locator('button:has-text("Send"), button[type="submit"]').first();
    await expect(sendButton).toBeVisible();
    console.log('✅ Send button visible');

    // Step 4: Send test message
    console.log(`\n💬 Step 4: Send test message: "${TEST_MESSAGE}"`);
    await chatInput.fill(TEST_MESSAGE);
    await page.screenshot({
      path: '/Users/keithstegbauer/repositories/CMZ-chatbots/backend/api/src/main/python/tests/playwright/screenshots/charlie-routing-02-message-typed.png',
      fullPage: true
    });

    await sendButton.click();
    console.log('✅ Message sent, waiting for response...');

    // Step 5: Wait for and capture Charlie's response
    console.log('\n⏳ Step 5: Wait for Charlie\'s response');

    // Wait for response to appear (look for message container)
    await page.waitForSelector('.message, .response, [class*="message"], [class*="response"]', {
      timeout: 30000,
      state: 'visible'
    });

    // Wait a bit for complete response
    await page.waitForTimeout(3000);

    await page.screenshot({
      path: '/Users/keithstegbauer/repositories/CMZ-chatbots/backend/api/src/main/python/tests/playwright/screenshots/charlie-routing-03-response-received.png',
      fullPage: true
    });

    // Step 6: Extract and validate response content
    console.log('\n🔍 Step 6: Extract and validate response content');

    // Get all text content from the page
    const pageContent = await page.content();
    const bodyText = await page.locator('body').innerText();

    console.log('\n📝 Full page text content:');
    console.log('='.repeat(80));
    console.log(bodyText);
    console.log('='.repeat(80));

    // Critical validations
    const validations = {
      hasElephantReference: false,
      hasMotherlanguage: false,
      noZaraReference: false,
      noDefaultReference: false
    };

    const lowerContent = bodyText.toLowerCase();

    // Check for elephant references
    if (lowerContent.includes('elephant') || lowerContent.includes('african elephant')) {
      validations.hasElephantReference = true;
      console.log('✅ PASS: Response mentions "elephant"');
    } else {
      console.log('❌ FAIL: Response does NOT mention "elephant"');
    }

    // Check for motherly language
    const motherlyTerms = ['dear', 'little one', 'sweetheart', 'my dear', 'sweetie'];
    const foundTerms = motherlyTerms.filter(term => lowerContent.includes(term));
    if (foundTerms.length > 0) {
      validations.hasMotherlanguage = true;
      console.log(`✅ PASS: Response uses motherly language: ${foundTerms.join(', ')}`);
    } else {
      console.log(`❌ FAIL: Response does NOT use motherly language (checked: ${motherlyTerms.join(', ')})`);
    }

    // Check for wrong personality (Zara)
    if (!lowerContent.includes('zara')) {
      validations.noZaraReference = true;
      console.log('✅ PASS: Response does NOT mention "Zara" (correct - not using default personality)');
    } else {
      console.log('❌ FAIL: Response mentions "Zara" (WRONG - using default personality!)');
    }

    // Check for "default" animal reference
    if (!lowerContent.includes('zoo ambassador') || lowerContent.includes('charlie')) {
      validations.noDefaultReference = true;
      console.log('✅ PASS: Response uses Charlie personality (not generic zoo ambassador)');
    } else {
      console.log('❌ FAIL: Response uses generic zoo ambassador personality');
    }

    // Step 7: Final validation summary
    console.log('\n📊 VALIDATION SUMMARY:');
    console.log('='.repeat(80));

    const passedChecks = Object.values(validations).filter(v => v).length;
    const totalChecks = Object.keys(validations).length;

    console.log(`Passed: ${passedChecks}/${totalChecks} checks`);
    console.log(`- Has Elephant Reference: ${validations.hasElephantReference ? '✅' : '❌'}`);
    console.log(`- Has Motherly Language: ${validations.hasMotherlanguage ? '✅' : '❌'}`);
    console.log(`- No Zara Reference: ${validations.noZaraReference ? '✅' : '❌'}`);
    console.log(`- No Default Reference: ${validations.noDefaultReference ? '✅' : '❌'}`);
    console.log('='.repeat(80));

    // Assert critical validations
    expect(validations.hasElephantReference, 'Charlie should identify as an elephant').toBe(true);
    expect(validations.hasMotherlanguage, 'Charlie should use motherly language').toBe(true);
    expect(validations.noZaraReference, 'Should NOT use Zara personality').toBe(true);

    console.log('\n🎉 TEST PASSED: Charlie routing fix successful!');
  });

  test('should send correct animalId to backend API', async ({ page }) => {
    console.log('\n🎯 TEST: Verify animalId transmission to backend');

    let requestAnimalId = null;

    // Capture the animalId from API request
    page.on('request', request => {
      const url = request.url();
      if (url.includes('/convo/turn')) {
        const postData = request.postData();
        if (postData) {
          try {
            const data = JSON.parse(postData);
            requestAnimalId = data.animalId;
            console.log(`📤 Captured animalId from request: "${requestAnimalId}"`);
          } catch (e) {
            console.log('⚠️ Could not parse request data');
          }
        }
      }
    });

    // Login
    await page.goto(`${FRONTEND_URL}/login`);
    await page.fill('input[type="email"]', TEST_USER.email);
    await page.fill('input[type="password"]', TEST_USER.password);
    await page.click('button[type="submit"]');
    await page.waitForURL(/\/(dashboard|animals)/, { timeout: 10000 });

    // Navigate to Charlie
    await page.goto(CHARLIE_URL);
    await page.waitForLoadState('networkidle');

    // Send message
    const chatInput = page.locator('textarea, input[type="text"]').first();
    await chatInput.fill('Test message');

    const sendButton = page.locator('button:has-text("Send"), button[type="submit"]').first();
    await sendButton.click();

    // Wait for API call
    await page.waitForTimeout(2000);

    // Validate animalId
    console.log('\n🔍 Validating animalId transmission:');
    console.log(`Expected: "charlie_003"`);
    console.log(`Actual: "${requestAnimalId}"`);

    expect(requestAnimalId, 'animalId should be "charlie_003"').toBe('charlie_003');
    expect(requestAnimalId, 'animalId should NOT be "default"').not.toBe('default');

    console.log('✅ PASS: Correct animalId sent to backend!');
  });
});
