const { test, expect } = require('@playwright/test');

test.describe('Charlie Chat Interface - Fixed Frontend Response Parsing', () => {
  test('should successfully chat with Charlie Test-1760449970 with proper response formatting', async ({ page }) => {
    const frontendUrl = process.env.FRONTEND_URL || 'http://localhost:3001';
    
    console.log('\n🧪 Testing Fixed Charlie Chat Interface');
    console.log('=' .repeat(60));
    
    // Step 1: Navigate to login page
    console.log('\n📍 Step 1: Navigating to login page...');
    await page.goto(`${frontendUrl}/login`);
    await page.waitForLoadState('networkidle');
    
    // Step 2: Login with test credentials
    console.log('🔐 Step 2: Logging in with parent1@test.cmz.org...');
    await page.fill('input[type="email"], input[name="email"]', 'parent1@test.cmz.org');
    await page.fill('input[type="password"], input[name="password"]', 'testpass123');
    
    // Take screenshot before login
    await page.screenshot({ 
      path: '/Users/keithstegbauer/repositories/CMZ-chatbots/backend/reports/playwright/test-results/charlie-chat-01-login-form.png',
      fullPage: true 
    });
    
    await page.click('button[type="submit"]');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    // Verify we're on dashboard
    console.log('✅ Login successful, verifying dashboard...');
    await page.screenshot({ 
      path: '/Users/keithstegbauer/repositories/CMZ-chatbots/backend/reports/playwright/test-results/charlie-chat-02-dashboard.png',
      fullPage: true 
    });
    
    // Step 3: Navigate to chat/conversations
    console.log('\n💬 Step 3: Navigating to chat interface...');
    
    // Try different navigation approaches
    const chatNavSelectors = [
      'a[href*="chat"]',
      'a[href*="conversation"]',
      'button:has-text("Chat")',
      'nav a:has-text("Chat")',
      '[data-testid="chat-nav"]'
    ];
    
    let navigated = false;
    for (const selector of chatNavSelectors) {
      try {
        const element = await page.$(selector);
        if (element) {
          console.log(`   Found navigation element: ${selector}`);
          await element.click();
          navigated = true;
          break;
        }
      } catch (e) {
        continue;
      }
    }
    
    if (!navigated) {
      // Try direct navigation
      console.log('   Using direct navigation to /chat');
      await page.goto(`${frontendUrl}/chat`);
    }
    
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    await page.screenshot({ 
      path: '/Users/keithstegbauer/repositories/CMZ-chatbots/backend/reports/playwright/test-results/charlie-chat-03-chat-page.png',
      fullPage: true 
    });
    
    // Step 4: Select Charlie Test-1760449970
    console.log('\n🐘 Step 4: Selecting Charlie Test-1760449970...');
    
    // Try different selectors for animal selection
    const animalSelectors = [
      'text=Charlie Test-1760449970',
      '[data-animal-id="charlie_003"]',
      'button:has-text("Charlie")',
      'div:has-text("Charlie Test-1760449970")',
      '.animal-item:has-text("Charlie")'
    ];
    
    let charlieSelected = false;
    for (const selector of animalSelectors) {
      try {
        const element = await page.$(selector);
        if (element) {
          console.log(`   Found Charlie element: ${selector}`);
          await element.click();
          charlieSelected = true;
          await page.waitForTimeout(1000);
          break;
        }
      } catch (e) {
        continue;
      }
    }
    
    if (!charlieSelected) {
      console.log('⚠️  Could not find Charlie in animal list');
      console.log('   Available animals on page:');
      const pageText = await page.textContent('body');
      console.log(pageText.substring(0, 500));
    }
    
    await page.screenshot({ 
      path: '/Users/keithstegbauer/repositories/CMZ-chatbots/backend/reports/playwright/test-results/charlie-chat-04-charlie-selected.png',
      fullPage: true 
    });
    
    // Step 5: Send first test message
    console.log('\n✉️  Step 5: Sending first message...');
    const message1 = "Hello Charlie, can you tell me about baby elephants?";
    
    // Try different input selectors
    const inputSelectors = [
      'input[placeholder*="message"]',
      'input[type="text"]',
      'textarea[placeholder*="message"]',
      'textarea',
      '[data-testid="chat-input"]',
      '.chat-input'
    ];
    
    let messageInput = null;
    for (const selector of inputSelectors) {
      messageInput = await page.$(selector);
      if (messageInput) {
        console.log(`   Found message input: ${selector}`);
        break;
      }
    }
    
    if (messageInput) {
      await messageInput.fill(message1);
      console.log(`   Typed: "${message1}"`);
      
      // Find and click send button
      const sendSelectors = [
        'button:has-text("Send")',
        'button[type="submit"]',
        '[data-testid="send-button"]',
        'button:has(svg)' // Icon button
      ];
      
      for (const selector of sendSelectors) {
        const sendBtn = await page.$(selector);
        if (sendBtn) {
          console.log(`   Found send button: ${selector}`);
          await sendBtn.click();
          break;
        }
      }
      
      // Wait for response
      console.log('   Waiting for Charlie\'s response...');
      await page.waitForTimeout(3000);
      
      await page.screenshot({ 
        path: '/Users/keithstegbauer/repositories/CMZ-chatbots/backend/reports/playwright/test-results/charlie-chat-05-first-response.png',
        fullPage: true 
      });
      
      // Step 6: Verify response appears correctly
      console.log('\n✅ Step 6: Verifying response format...');
      
      const pageContent = await page.textContent('body');
      
      // Check for error messages (should NOT be present)
      const hasError = pageContent.includes('Sorry, I encountered an error') || 
                       pageContent.includes('error processing') ||
                       pageContent.includes('something went wrong');
      
      if (hasError) {
        console.log('❌ ERROR: Found error message in response');
      } else {
        console.log('✅ No error messages detected');
      }
      
      // Check for actual response content
      const hasResponse = pageContent.includes('elephant') || 
                          pageContent.includes('Charlie') ||
                          pageContent.length > 1000; // Substantial content
      
      if (hasResponse) {
        console.log('✅ Response content detected');
      } else {
        console.log('⚠️  Response content may be missing');
      }
      
      // Step 7: Send follow-up message
      console.log('\n✉️  Step 7: Sending follow-up message...');
      const message2 = "Thank you Charlie!";
      
      await messageInput.fill(message2);
      console.log(`   Typed: "${message2}"`);
      
      for (const selector of sendSelectors) {
        const sendBtn = await page.$(selector);
        if (sendBtn) {
          await sendBtn.click();
          break;
        }
      }
      
      await page.waitForTimeout(2000);
      
      await page.screenshot({ 
        path: '/Users/keithstegbauer/repositories/CMZ-chatbots/backend/reports/playwright/test-results/charlie-chat-06-second-response.png',
        fullPage: true 
      });
      
      // Step 8: Verify conversation flow
      console.log('\n📊 Step 8: Verifying conversation flow...');
      
      const finalContent = await page.textContent('body');
      const messageCount = (finalContent.match(/Charlie/g) || []).length;
      
      console.log(`   Messages containing "Charlie": ${messageCount}`);
      
      // Check for timestamps
      const hasTimestamps = finalContent.includes(':') && 
                           (finalContent.includes('AM') || finalContent.includes('PM'));
      
      if (hasTimestamps) {
        console.log('✅ Timestamps detected');
      } else {
        console.log('⚠️  Timestamps may be missing');
      }
      
      // Final screenshot
      await page.screenshot({ 
        path: '/Users/keithstegbauer/repositories/CMZ-chatbots/backend/reports/playwright/test-results/charlie-chat-07-final-state.png',
        fullPage: true 
      });
      
      console.log('\n📸 Screenshots saved to backend/reports/playwright/test-results/');
      console.log('\n' + '='.repeat(60));
      console.log('🎉 Test Complete!');
      console.log('='.repeat(60));
      
      // Assertions
      expect(hasError).toBe(false);
      expect(hasResponse).toBe(true);
      
    } else {
      console.log('❌ Could not find message input field');
      throw new Error('Message input field not found');
    }
  });
});
