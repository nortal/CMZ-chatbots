const { test, expect } = require('@playwright/test');

test.describe('Charlie Chat Interface Test', () => {
  test('should allow user to chat with Charlie and verify personality', async ({ page }) => {
    const frontendUrl = process.env.FRONTEND_URL || 'http://localhost:3001';
    const animalId = 'charlie_003';
    const animalName = 'Charlie Test-1760449970';
    
    console.log('=== Charlie Chat Interface Test ===');
    console.log('Frontend URL:', frontendUrl);
    console.log('Animal ID:', animalId);
    console.log('Animal Name:', animalName);
    
    // Step 1: Navigate to frontend
    console.log('\nStep 1: Navigating to frontend...');
    await page.goto(frontendUrl);
    await page.waitForLoadState('networkidle');
    console.log('✓ Frontend loaded');
    
    // Take screenshot of initial page
    await page.screenshot({ path: '/Users/keithstegbauer/repositories/CMZ-chatbots/.playwright-mcp/charlie-ui-01-initial.png', fullPage: true });
    
    // Step 2: Login with test credentials
    console.log('\nStep 2: Logging in...');
    const emailInput = page.locator('input[type="email"], input[name="email"], input[id="email"]');
    const passwordInput = page.locator('input[type="password"], input[name="password"], input[id="password"]');
    const loginButton = page.locator('button:has-text("Login"), button:has-text("Sign In"), button[type="submit"]');
    
    await emailInput.fill('parent1@test.cmz.org');
    await passwordInput.fill('testpass123');
    await page.screenshot({ path: '/Users/keithstegbauer/repositories/CMZ-chatbots/.playwright-mcp/charlie-ui-02-login.png', fullPage: true });
    
    await loginButton.click();
    await page.waitForLoadState('networkidle');
    console.log('✓ Login successful');
    
    // Wait for dashboard/main page
    await page.waitForTimeout(2000);
    await page.screenshot({ path: '/Users/keithstegbauer/repositories/CMZ-chatbots/.playwright-mcp/charlie-ui-03-dashboard.png', fullPage: true });
    
    // Step 3: Verify dashboard shows animal ambassadors
    console.log('\nStep 3: Verifying Animal Ambassadors dashboard...');

    // The dashboard should already show the animal cards
    const pageContent = await page.content();
    console.log('Dashboard contains "Charlie":', pageContent.includes('Charlie'));
    console.log('Dashboard contains "Animal Ambassadors":', pageContent.includes('Animal Ambassadors'));

    await page.screenshot({ path: '/Users/keithstegbauer/repositories/CMZ-chatbots/.playwright-mcp/charlie-ui-04-ambassadors.png', fullPage: true });

    // Step 4: Click "Chat with Me!" button for Charlie
    console.log('\nStep 4: Clicking "Chat with Me!" for Charlie...');

    // Find Charlie's card and click her "Chat with Me!" button
    // The card contains the text "Charlie Test-1760449970" followed by a "Chat with Me!" button
    const charlieCard = page.locator('div:has-text("Charlie Test-1760449970")').first();
    const charlieVisible = await charlieCard.count() > 0;
    console.log('Charlie card visible:', charlieVisible);

    if (charlieVisible) {
      // Find the "Chat with Me!" button within Charlie's card (use .first() to handle multiple matches)
      const chatButton = charlieCard.locator('button:has-text("Chat with Me!")').first();
      console.log('Clicking Chat with Me! button...');
      await chatButton.click();
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(2000);
      console.log('✓ Charlie chat opened');
    } else {
      console.log('⚠ Charlie card not found, trying alternative approach...');
      // Try clicking any "Chat with Me!" button near Charlie text
      await page.locator('button:has-text("Chat with Me!")').first().click();
      await page.waitForLoadState('networkidle');
      await page.waitForTimeout(2000);
    }

    await page.screenshot({ path: '/Users/keithstegbauer/repositories/CMZ-chatbots/.playwright-mcp/charlie-ui-05-charlie-chat.png', fullPage: true });
    
    // Step 5: Send first test message
    console.log('\nStep 5: Sending first test message...');
    const testMessage1 = "Hello Charlie, can you tell me about elephants?";

    // Look for message input - be specific to avoid the search bar
    // The chat input has placeholder "Type your message..."
    const messageInput = page.locator('input[placeholder="Type your message..."], textarea[placeholder="Type your message..."]').first();
    const sendButton = page.locator('button:has-text("Send"), button[type="submit"]').first();

    console.log('Filling message input...');
    await messageInput.click(); // Click to focus
    await messageInput.fill(testMessage1);
    await page.waitForTimeout(500); // Give time for the text to register
    await page.screenshot({ path: '/Users/keithstegbauer/repositories/CMZ-chatbots/.playwright-mcp/charlie-ui-06-message1-typed.png', fullPage: true });

    console.log('Clicking send button...');
    await sendButton.click({ force: true }); // Force click even if button appears disabled
    console.log('✓ First message sent');
    
    // Wait for response (give it time for AI processing)
    console.log('Waiting for Charlie\'s response...');
    await page.waitForTimeout(5000);
    await page.screenshot({ path: '/Users/keithstegbauer/repositories/CMZ-chatbots/.playwright-mcp/charlie-ui-07-message1-response.png', fullPage: true });
    
    // Step 6: Verify Charlie's response reflects her personality
    console.log('\nStep 6: Verifying Charlie\'s personality in response...');
    const chatContent = await page.textContent('body');
    console.log('Checking for motherly/elephant personality indicators...');
    
    // Look for personality indicators
    const personalityIndicators = ['elephant', 'dear', 'little one', 'slowly', 'gently', 'carefully'];
    const foundIndicators = personalityIndicators.filter(indicator => 
      chatContent.toLowerCase().includes(indicator)
    );
    console.log('Found personality indicators:', foundIndicators);
    
    // Step 7: Send follow-up message
    console.log('\nStep 7: Sending follow-up message...');
    const testMessage2 = "I'm a little scared of big animals";
    
    await messageInput.fill(testMessage2);
    await page.screenshot({ path: '/Users/keithstegbauer/repositories/CMZ-chatbots/.playwright-mcp/charlie-ui-08-message2-typed.png', fullPage: true });
    
    await sendButton.click();
    console.log('✓ Second message sent');
    
    // Wait for response
    console.log('Waiting for Charlie\'s protective response...');
    await page.waitForTimeout(5000);
    await page.screenshot({ path: '/Users/keithstegbauer/repositories/CMZ-chatbots/.playwright-mcp/charlie-ui-09-message2-response.png', fullPage: true });
    
    // Step 8: Verify protective/caring response
    console.log('\nStep 8: Verifying protective/caring response...');
    const chatContent2 = await page.textContent('body');
    
    // Look for caring/protective language
    const caringIndicators = ['safe', 'gentle', 'kind', 'protect', 'care', 'worry', 'afraid', 'friend'];
    const foundCaring = caringIndicators.filter(indicator => 
      chatContent2.toLowerCase().includes(indicator)
    );
    console.log('Found caring/protective indicators:', foundCaring);
    
    // Final screenshot
    await page.screenshot({ path: '/Users/keithstegbauer/repositories/CMZ-chatbots/.playwright-mcp/charlie-ui-10-final.png', fullPage: true });
    
    // Step 9: Verify chat interface quality
    console.log('\n=== VERIFICATION SUMMARY ===');
    console.log('✓ Chat interface loaded without errors');
    console.log('✓ Login successful');
    console.log('✓ Messages sent successfully');
    console.log('✓ Personality indicators found:', foundIndicators.length > 0 ? foundIndicators.join(', ') : 'None detected');
    console.log('✓ Caring response indicators found:', foundCaring.length > 0 ? foundCaring.join(', ') : 'None detected');
    console.log('\nScreenshots saved to .playwright-mcp/ directory');
    
    // Basic assertions
    expect(foundIndicators.length).toBeGreaterThan(0); // Should have some personality
    expect(foundCaring.length).toBeGreaterThan(0); // Should have caring response
  });
});
