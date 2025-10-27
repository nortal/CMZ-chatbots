const { test, expect } = require('@playwright/test');
const { loginAsUser, authenticatedRequest } = require('../helpers/auth-helper');

test.describe('Animal Config Persistence Fixes', () => {
    test('should save and persist systemPrompt field', async ({ page }) => {
        console.log('🧪 Testing systemPrompt persistence fix...');

        const { token } = await loginAsUser(page, 'admin');

        // Get first animal
        const listResponse = await authenticatedRequest(page, 'GET', 'http://localhost:8080/animal_list', token);
        expect(listResponse.status()).toBe(200);
        const animals = await listResponse.json();
        const testAnimal = animals[0];
        const animalId = testAnimal.animalId;

        console.log(`📝 Testing with animal: ${testAnimal.name} (${animalId})`);

        // Get current config
        const getResponse = await authenticatedRequest(page, 'GET', `http://localhost:8080/animal_config?animalId=${animalId}`, token);
        expect(getResponse.status()).toBe(200);
        const originalConfig = await getResponse.json();
        const originalSystemPrompt = originalConfig.systemPrompt || '';

        // Update systemPrompt
        const testSystemPrompt = 'You are a friendly AI assistant representing ' + testAnimal.name + '. Test timestamp: ' + Date.now();
        console.log(`💾 Saving systemPrompt: ${testSystemPrompt.substring(0, 60)}...`);

        const saveResponse = await authenticatedRequest(
            page,
            'PATCH',
            `http://localhost:8080/animal_config?animalId=${animalId}`,
            token,
            { data: { systemPrompt: testSystemPrompt } }
        );
        expect(saveResponse.status()).toBe(200);

        // Verify the save by fetching again
        const verifyResponse = await authenticatedRequest(page, 'GET', `http://localhost:8080/animal_config?animalId=${animalId}`, token);
        expect(verifyResponse.status()).toBe(200);
        const updatedConfig = await verifyResponse.json();

        expect(updatedConfig.systemPrompt).toBe(testSystemPrompt);
        console.log('✅ systemPrompt saved and persisted successfully');

        // Restore original
        if (originalSystemPrompt !== testSystemPrompt) {
            await authenticatedRequest(
                page,
                'PATCH',
                `http://localhost:8080/animal_config?animalId=${animalId}`,
                token,
                { data: { systemPrompt: originalSystemPrompt } }
            );
            console.log('🔄 Original systemPrompt restored');
        }
    });

    test('should save and persist active status', async ({ page }) => {
        console.log('🧪 Testing active status persistence fix...');

        const { token } = await loginAsUser(page, 'admin');

        // Get first animal
        const listResponse = await authenticatedRequest(page, 'GET', 'http://localhost:8080/animal_list', token);
        expect(listResponse.status()).toBe(200);
        const animals = await listResponse.json();
        const testAnimal = animals[0];
        const animalId = testAnimal.animalId;

        console.log(`📝 Testing with animal: ${testAnimal.name} (${animalId})`);

        // Get current status
        const getResponse = await authenticatedRequest(page, 'GET', `http://localhost:8080/animal/${animalId}`, token);
        expect(getResponse.status()).toBe(200);
        const originalAnimal = await getResponse.json();
        const originalStatus = originalAnimal.status;

        // Toggle status to inactive then active
        const newStatus = originalStatus === 'active' ? 'inactive' : 'active';
        console.log(`💾 Changing status from ${originalStatus} to ${newStatus}`);

        const updateResponse = await authenticatedRequest(
            page,
            'PUT',
            `http://localhost:8080/animal/${animalId}`,
            token,
            { data: { status: newStatus } }
        );
        expect(updateResponse.status()).toBe(200);

        // Verify the status persisted
        const verifyResponse = await authenticatedRequest(page, 'GET', `http://localhost:8080/animal/${animalId}`, token);
        expect(verifyResponse.status()).toBe(200);
        const updatedAnimal = await verifyResponse.json();

        expect(updatedAnimal.status).toBe(newStatus);
        console.log(`✅ Status changed to ${newStatus} and persisted successfully`);

        // Restore original status
        if (originalStatus !== newStatus) {
            await authenticatedRequest(
                page,
                'PUT',
                `http://localhost:8080/animal/${animalId}`,
                token,
                { data: { status: originalStatus } }
            );
            console.log(`🔄 Original status ${originalStatus} restored`);
        }
    });
});
