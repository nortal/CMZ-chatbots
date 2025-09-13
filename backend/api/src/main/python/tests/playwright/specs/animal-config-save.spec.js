const { test, expect } = require('@playwright/test');

test.describe('Animal Configuration Save Test', () => {
    test('should save animal configuration data and persist on reload - Bella the Bear', async ({ page }) => {
        // Navigate to the application
        await page.goto('http://localhost:3001');
        
        // Wait for the page to load
        await page.waitForLoadState('networkidle');
        
        // Login as admin to access animal configuration
        await page.click('text=Login', { timeout: 10000 });
        await page.fill('input[type="email"]', 'admin@cmz.org');
        await page.fill('input[type="password"]', 'admin123');
        await page.click('button[type="submit"]');
        
        // Wait for login to complete
        await page.waitForLoadState('networkidle');
        
        // Navigate to animal configuration section
        // This may vary based on the UI - adjust selectors as needed
        await page.click('text=Animals', { timeout: 10000 });
        
        // Look for Bella the Bear or create/select an animal
        const bellaSelector = 'text=Bella the Bear';
        const bellaExists = await page.isVisible(bellaSelector);
        
        if (bellaExists) {
            await page.click(bellaSelector);
        } else {
            // If Bella doesn't exist in UI, look for any animal to test with
            await page.click('[data-testid="animal-item"]:first-child', { timeout: 10000 });
        }
        
        // Navigate to animal configuration tab
        await page.click('text=Configuration', { timeout: 10000 });
        
        // Wait for the configuration form to load
        await page.waitForSelector('[data-testid="animal-config-form"]', { timeout: 10000 });
        
        // Find the basic info tab or personality field
        const personalityField = page.locator('textarea[name="personality"], input[name="personality"], [data-testid="personality-field"]');
        
        // Clear existing content and enter test data
        const testPersonality = 'playful,gentle,storyteller,test-data-' + Date.now();
        
        if (await personalityField.isVisible()) {
            await personalityField.clear();
            await personalityField.fill(testPersonality);
            
            // Save the configuration
            await page.click('button:has-text("Save")', { timeout: 5000 });
            
            // Wait for save to complete (look for success message or network idle)
            await page.waitForLoadState('networkidle');
            
            // Verify the data was saved by checking if it's still there
            const savedValue = await personalityField.inputValue();
            expect(savedValue).toBe(testPersonality);
            
            // Reload the page to verify persistence
            await page.reload();
            await page.waitForLoadState('networkidle');
            
            // Navigate back to the same animal configuration
            if (bellaExists) {
                await page.click('text=Bella the Bear');
            } else {
                await page.click('[data-testid="animal-item"]:first-child', { timeout: 10000 });
            }
            
            await page.click('text=Configuration', { timeout: 10000 });
            await page.waitForSelector('[data-testid="animal-config-form"]', { timeout: 10000 });
            
            // Verify the data persisted after reload
            const persistedValue = await personalityField.inputValue();
            expect(persistedValue).toBe(testPersonality);
            
        } else {
            // If we can't find the personality field, fail with helpful info
            const pageContent = await page.content();
            console.log('Available form fields:', await page.locator('input, textarea, select').count());
            throw new Error('Could not find personality field in animal configuration form');
        }
    });
    
    test('should handle animal configuration API endpoints correctly', async ({ page }) => {
        // Test the API endpoints directly
        const response = await page.request.get('http://localhost:8080/animal_list');
        expect(response.status()).toBe(200);
        
        const animals = await response.json();
        console.log('Available animals:', animals);
        
        if (animals.length > 0) {
            const animalId = animals[0].animalId;
            
            // Test getting animal config
            const configResponse = await page.request.get(`http://localhost:8080/animal_config?animalId=${animalId}`);
            expect(configResponse.status()).toBe(200);
            
            const config = await configResponse.json();
            console.log('Animal config:', config);
            
            // Test saving animal config
            const updateData = {
                personality: 'test-personality-' + Date.now(),
                chatbotConfig: {
                    enabled: true,
                    model: 'claude-3-sonnet',
                    temperature: 0.7,
                    maxTokens: 500
                }
            };
            
            const saveResponse = await page.request.patch(`http://localhost:8080/animal_config?animalId=${animalId}`, {
                data: updateData
            });
            
            expect(saveResponse.status()).toBe(200);
            
            // Verify the update persisted
            const verifyResponse = await page.request.get(`http://localhost:8080/animal_config?animalId=${animalId}`);
            expect(verifyResponse.status()).toBe(200);
            
            const updatedConfig = await verifyResponse.json();
            expect(updatedConfig.personality).toBe(updateData.personality);
        }
    });
});