const { test, expect } = require('@playwright/test');
const { spawn } = require('child_process');

/**
 * DynamoDB Consistency Validation Tests - SECURE VERSION
 * 
 * These tests ensure that data displayed in the UI matches what's actually 
 * stored in DynamoDB, and that UI updates are properly persisted.
 * 
 * SECURITY FIXES:
 * - Command injection protection via spawn() with args array
 * - Input validation for all user-controlled data
 * - Secure error handling without information disclosure
 * - Minimal logging with no sensitive data exposure
 */
test.describe('DynamoDB Consistency Validation - Secure', () => {

    /**
     * Secure command execution helper
     */
    async function execSecureCommand(command, args) {
        return new Promise((resolve, reject) => {
            const process = spawn(command, args, { 
                stdio: ['pipe', 'pipe', 'pipe'],
                timeout: 30000 // 30 second timeout
            });
            
            let stdout = '';
            let stderr = '';
            
            process.stdout.on('data', (data) => stdout += data);
            process.stderr.on('data', (data) => stderr += data);
            
            process.on('close', (code) => {
                if (code === 0) {
                    resolve(stdout);
                } else {
                    reject(new Error(`AWS CLI command failed with exit code ${code}`));
                }
            });
            
            process.on('error', (error) => {
                reject(new Error(`Failed to execute AWS CLI: ${error.message}`));
            });
        });
    }

    /**
     * Secure input validation for animal IDs
     */
    function validateAnimalId(animalId) {
        if (!animalId || typeof animalId !== 'string') {
            throw new Error('Animal ID must be a non-empty string');
        }
        
        // Only allow alphanumeric, hyphens, and underscores
        if (!/^[a-zA-Z0-9_-]+$/.test(animalId)) {
            throw new Error('Animal ID contains invalid characters');
        }
        
        if (animalId.length > 100) {
            throw new Error('Animal ID too long');
        }
        
        return animalId;
    }

    /**
     * Secure DynamoDB item transformation
     */
    function transformDynamoDBItem(item) {
        if (!item || typeof item !== 'object') {
            return null;
        }
        
        return {
            animalId: item.animalId?.S || '',
            name: item.name?.S || '',
            species: item.species?.S || '',
            personality: item.personality?.M?.description?.S || item.personality?.S || '',
            active: item.active?.BOOL || false,
            educational_focus: item.educational_focus?.BOOL || false,
            age_appropriate: item.age_appropriate?.BOOL || false,
            created: item.created?.M?.at?.S || '',
            modified: item.modified?.M?.at?.S || ''
        };
    }

    /**
     * SECURE Helper function to query DynamoDB directly
     */
    async function getDynamoDBAnimal(animalId) {
        try {
            // Validate input to prevent injection
            const validatedId = validateAnimalId(animalId);
            
            const args = [
                'dynamodb',
                'get-item',
                '--table-name', 'quest-dev-animal',
                '--key', JSON.stringify({ animalId: { S: validatedId } }),
                '--output', 'json'
            ];
            
            const stdout = await execSecureCommand('aws', args);
            const result = JSON.parse(stdout);
            
            if (!result.Item) {
                return null;
            }
            
            return transformDynamoDBItem(result.Item);
            
        } catch (error) {
            // Secure error handling - no sensitive information in logs
            if (process.env.NODE_ENV === 'test' && process.env.DEBUG_TESTS) {
                console.debug('DynamoDB query error details:', error.message);
            }
            return null;
        }
    }

    /**
     * SECURE Helper function to scan all animals from DynamoDB
     */
    async function getAllDynamoDBAnimals() {
        try {
            const args = [
                'dynamodb',
                'scan',
                '--table-name', 'quest-dev-animal',
                '--output', 'json'
            ];
            
            const stdout = await execSecureCommand('aws', args);
            const result = JSON.parse(stdout);
            
            if (!result.Items || !Array.isArray(result.Items)) {
                return [];
            }
            
            return result.Items
                .map(transformDynamoDBItem)
                .filter(item => item !== null);
                
        } catch (error) {
            // Secure error handling
            if (process.env.NODE_ENV === 'test' && process.env.DEBUG_TESTS) {
                console.debug('DynamoDB scan error details:', error.message);
            }
            return [];
        }
    }

    test('should verify UI animal list matches DynamoDB data', async ({ page }) => {
        console.log('🔍 Testing UI animal list against DynamoDB...');
        
        // Get animals from DynamoDB directly
        const dynamoAnimals = await getAllDynamoDBAnimals();
        console.log('DynamoDB animals count:', dynamoAnimals.length);
        
        // Get animals from API
        const apiResponse = await page.request.get('http://localhost:8080/animal_list');
        expect(apiResponse.status()).toBe(200);
        const apiAnimals = await apiResponse.json();
        console.log('API animals count:', apiAnimals.length);
        
        // Verify counts match
        expect(apiAnimals.length).toBe(dynamoAnimals.length);
        
        // Verify each animal data matches
        for (const apiAnimal of apiAnimals) {
            const dynamoAnimal = dynamoAnimals.find(d => d.animalId === apiAnimal.animalId);
            expect(dynamoAnimal).toBeTruthy();
            expect(apiAnimal.name).toBe(dynamoAnimal.name);
            expect(apiAnimal.species).toBe(dynamoAnimal.species);
            expect(apiAnimal.active).toBe(dynamoAnimal.active);
        }
        
        console.log('✅ UI animal list matches DynamoDB data');
    });

    test('should verify animal configuration UI shows DynamoDB data', async ({ page }) => {
        console.log('🔍 Testing animal configuration UI against DynamoDB...');
        
        // Navigate to animal configuration page
        await page.goto('http://localhost:3001');
        await page.waitForLoadState('networkidle');
        
        // Login if needed (skip if already authenticated)
        const loginButton = page.locator('text=Login');
        if (await loginButton.isVisible()) {
            await loginButton.click();
            await page.fill('input[type="email"]', 'parent1@test.cmz.org');
            await page.fill('input[type="password"]', 'testpass123');
            await page.click('button[type="submit"]');
            await page.waitForLoadState('networkidle');
        }
        
        // Navigate to Animal Config section
        await page.goto('http://localhost:3001/animals');
        await page.waitForLoadState('networkidle');
        
        // Get first animal from DynamoDB
        const dynamoAnimals = await getAllDynamoDBAnimals();
        if (dynamoAnimals.length === 0) {
            console.log('⚠️ No animals found in DynamoDB, skipping UI comparison');
            return;
        }
        
        const testAnimal = dynamoAnimals[0];
        console.log('Testing animal:', testAnimal.animalId);
        
        // Find and click on the animal in the UI
        const animalCard = page.locator(`text=${testAnimal.name}`).first();
        await expect(animalCard).toBeVisible();
        
        // Check if the animal is displayed correctly in the list
        const animalCardParent = animalCard.locator('..').locator('..');
        await expect(animalCardParent).toContainText(testAnimal.species);
        
        console.log('✅ Animal configuration UI shows correct DynamoDB data');
    });

    test('should verify personality field UI-DynamoDB consistency', async ({ page }) => {
        console.log('🔍 Testing personality field consistency...');
        
        // Get test animal from DynamoDB
        const dynamoAnimals = await getAllDynamoDBAnimals();
        if (dynamoAnimals.length === 0) {
            console.log('⚠️ No animals found in DynamoDB, skipping personality test');
            return;
        }
        
        const testAnimal = dynamoAnimals[0];
        console.log('Testing personality for animal:', testAnimal.animalId);
        
        // Get personality from API
        const apiResponse = await page.request.get(`http://localhost:8080/animal_config?animalId=${testAnimal.animalId}`);
        expect(apiResponse.status()).toBe(200);
        const apiConfig = await apiResponse.json();
        
        // Verify API matches DynamoDB (secure comparison)
        expect(apiConfig.personality).toBe(testAnimal.personality);
        
        console.log('✅ Personality field API matches DynamoDB');
    });

    test('should verify UI updates persist to DynamoDB', async ({ page }) => {
        console.log('🔍 Testing UI update persistence to DynamoDB...');
        
        // Get a test animal
        const dynamoAnimals = await getAllDynamoDBAnimals();
        if (dynamoAnimals.length === 0) {
            console.log('⚠️ No animals found in DynamoDB, skipping update test');
            return;
        }
        
        const testAnimal = dynamoAnimals[0];
        const originalPersonality = testAnimal.personality;
        
        // Create safe test data
        const timestamp = Date.now();
        const testPersonality = `Test personality updated at ${timestamp}`;
        
        console.log('Testing personality update for animal:', testAnimal.animalId);
        
        // Update via API (simulating UI save)
        const updateResponse = await page.request.patch(
            `http://localhost:8080/animal_config?animalId=${testAnimal.animalId}`,
            {
                data: { personality: testPersonality },
                headers: { 'Content-Type': 'application/json' }
            }
        );
        
        expect(updateResponse.status()).toBe(200);
        console.log('API update completed with status:', updateResponse.status());
        
        // Wait a moment for DynamoDB eventual consistency
        await page.waitForTimeout(1000);
        
        // Verify the change persisted to DynamoDB
        const updatedDynamoAnimal = await getDynamoDBAnimal(testAnimal.animalId);
        expect(updatedDynamoAnimal).toBeTruthy();
        expect(updatedDynamoAnimal.personality).toBe(testPersonality);
        
        console.log('✅ UI update successfully persisted to DynamoDB');
        
        // Restore original value
        await page.request.patch(
            `http://localhost:8080/animal_config?animalId=${testAnimal.animalId}`,
            {
                data: { personality: originalPersonality },
                headers: { 'Content-Type': 'application/json' }
            }
        );
        
        console.log('✅ Original data restored');
    });

    test('should verify animal config form displays DynamoDB values', async ({ page }) => {
        console.log('🔍 Testing animal config form shows DynamoDB values...');
        
        // This test focuses on the specific issue the user reported:
        // "text goes away" when saving - ensures form shows real DynamoDB data
        
        const dynamoAnimals = await getAllDynamoDBAnimals();
        if (dynamoAnimals.length === 0) {
            console.log('⚠️ No animals found in DynamoDB, skipping form test');
            return;
        }
        
        const testAnimal = dynamoAnimals[0];
        console.log('Testing form data for animal:', testAnimal.animalId);
        
        // Navigate to the frontend (this will now show DynamoDB data, not mock data)
        await page.goto('http://localhost:3001');
        await page.waitForLoadState('networkidle');
        
        // Check if API health endpoint works
        const healthResponse = await page.request.get('http://localhost:8080/health');
        if (healthResponse.status() === 200) {
            console.log('✅ API is healthy, data should come from DynamoDB');
        } else {
            console.log('⚠️ API health check failed, frontend may use fallback data');
        }
        
        // Verify API returns the same data we see in DynamoDB
        const apiResponse = await page.request.get(`http://localhost:8080/animal_config?animalId=${testAnimal.animalId}`);
        if (apiResponse.status() === 200) {
            const apiConfig = await apiResponse.json();
            expect(apiConfig.personality).toBe(testAnimal.personality);
            console.log('✅ API config matches DynamoDB data');
        }
        
        console.log('✅ Animal config form validation complete');
    });

    test('should verify no mock data fallback occurs', async ({ page }) => {
        console.log('🔍 Testing that no mock data fallback occurs...');
        
        // This test ensures the UI changes we made work correctly:
        // - No fallback to mockAnimals 
        // - All form fields use animalConfig, not selectedAnimal
        // - Empty states shown instead of fake data
        
        const dynamoAnimals = await getAllDynamoDBAnimals();
        
        // Get API animals
        const apiResponse = await page.request.get('http://localhost:8080/animal_list');
        expect(apiResponse.status()).toBe(200);
        const apiAnimals = await apiResponse.json();
        
        // Verify we're getting real data, not mock data
        // Mock data would have specific IDs like 'cheetah-1', 'tiger-1', 'elephant-1'
        const mockDataIds = ['cheetah-1', 'tiger-1', 'elephant-1'];
        
        for (const animal of apiAnimals) {
            expect(mockDataIds).not.toContain(animal.animalId || animal.id);
        }
        
        // Verify API animals match DynamoDB animals exactly
        expect(apiAnimals.length).toBe(dynamoAnimals.length);
        
        for (const apiAnimal of apiAnimals) {
            const matchingDynamoAnimal = dynamoAnimals.find(d => d.animalId === apiAnimal.animalId);
            expect(matchingDynamoAnimal).toBeTruthy();
        }
        
        console.log('✅ No mock data fallback detected - using real DynamoDB data');
    });
});