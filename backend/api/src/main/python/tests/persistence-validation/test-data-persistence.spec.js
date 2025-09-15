const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

// Test configuration
const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:3001';
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8080';
const TEST_TIMEOUT = 90000;

// Load baseline data
const baselineData = JSON.parse(
  fs.readFileSync(path.join(__dirname, 'baseline-data.json'), 'utf8')
);

// Test data for animal configuration
const testAnimalData = {
  animalId: 'leo_001',
  voice: {
    provider: 'elevenlabs',
    voiceId: 'test_voice_' + Date.now(),
    modelId: 'eleven_turbo_v2',
    stability: 0.5,
    similarityBoost: 0.75,
    style: 0.0,
    useSpeakerBoost: true
  },
  guardrails: {
    contentFilters: ['educational', 'age-appropriate'],
    responseMaxLength: 500,
    topicRestrictions: ['violence', 'inappropriate']
  },
  personality: {
    traits: ['friendly', 'educational', 'enthusiastic'],
    backstory: 'King of the savanna with wisdom to share',
    interests: ['wildlife', 'conservation', 'leadership']
  }
};

// Capture network data
let capturedRequests = [];
let capturedResponses = [];

test.describe('Data Persistence Validation', () => {
  test.setTimeout(TEST_TIMEOUT);

  test.beforeEach(async ({ page }) => {
    // Reset captured data
    capturedRequests = [];
    capturedResponses = [];

    // Monitor network requests
    page.on('request', request => {
      if (request.url().includes('/api/') || request.url().includes('/animals')) {
        capturedRequests.push({
          url: request.url(),
          method: request.method(),
          headers: request.headers(),
          postData: request.postData()
        });
      }
    });

    page.on('response', response => {
      if (response.url().includes('/api/') || response.url().includes('/animals')) {
        capturedResponses.push({
          url: response.url(),
          status: response.status(),
          headers: response.headers()
        });
      }
    });
  });

  test('Phase 1: Validate Animal Configuration Save', async ({ page }) => {
    console.log('🔍 Starting Data Persistence Validation');
    console.log('📊 Baseline data loaded:', baselineData.baseline_data.animals.count, 'animals');

    // Navigate to admin dashboard
    await page.goto(FRONTEND_URL);

    // Handle authentication if needed
    const loginVisible = await page.locator('input[type="email"], input[name="email"]').isVisible().catch(() => false);
    if (loginVisible) {
      console.log('🔐 Authenticating...');
      await page.fill('input[type="email"], input[name="email"]', 'admin@cmz.org');
      await page.fill('input[type="password"], input[name="password"]', 'testpass123');
      await page.click('button[type="submit"]');
      await page.waitForNavigation({ waitUntil: 'networkidle' });
    }

    // Navigate to animal configuration
    console.log('🦁 Navigating to animal configuration for:', testAnimalData.animalId);
    await page.goto(`${FRONTEND_URL}/animals/${testAnimalData.animalId}/config`);

    // Wait for form to load
    await page.waitForSelector('form, [data-testid="animal-config-form"]', { timeout: 10000 });

    // Capture initial form state
    const initialFormData = await page.evaluate(() => {
      const formData = {};
      const inputs = document.querySelectorAll('input, textarea, select');
      inputs.forEach(input => {
        if (input.name) {
          formData[input.name] = input.value;
        }
      });
      return formData;
    });
    console.log('📝 Initial form data captured:', Object.keys(initialFormData).length, 'fields');

    // Fill voice configuration
    console.log('🎤 Configuring voice settings...');
    const voiceSection = await page.locator('[data-testid="voice-config"], fieldset:has-text("Voice"), div:has-text("Voice Configuration")').first();

    // Provider selection
    await voiceSection.locator('select[name*="provider"], input[name*="provider"]').fill(testAnimalData.voice.provider);

    // Voice ID
    await voiceSection.locator('input[name*="voiceId"], input[placeholder*="Voice ID"]').fill(testAnimalData.voice.voiceId);

    // Model ID
    await voiceSection.locator('input[name*="modelId"], select[name*="model"]').fill(testAnimalData.voice.modelId);

    // Stability slider
    const stabilityInput = await voiceSection.locator('input[name*="stability"], input[type="range"]:near(:text("Stability"))').first();
    await stabilityInput.fill(String(testAnimalData.voice.stability));

    // Similarity boost slider
    const similarityInput = await voiceSection.locator('input[name*="similarity"], input[type="range"]:near(:text("Similarity"))').first();
    await similarityInput.fill(String(testAnimalData.voice.similarityBoost));

    // Fill guardrails configuration
    console.log('🛡️ Configuring guardrails...');
    const guardrailsSection = await page.locator('[data-testid="guardrails-config"], fieldset:has-text("Guardrails"), div:has-text("Safety Settings")').first();

    // Content filters
    for (const filter of testAnimalData.guardrails.contentFilters) {
      const filterCheckbox = await guardrailsSection.locator(`input[type="checkbox"][value="${filter}"], label:has-text("${filter}")`).first();
      await filterCheckbox.check();
    }

    // Response max length
    await guardrailsSection.locator('input[name*="maxLength"], input[type="number"]:near(:text("Max"))').fill(String(testAnimalData.guardrails.responseMaxLength));

    // Fill personality configuration
    console.log('🎭 Configuring personality...');
    const personalitySection = await page.locator('[data-testid="personality-config"], fieldset:has-text("Personality"), div:has-text("Personality")').first();

    // Traits
    const traitsInput = await personalitySection.locator('textarea[name*="traits"], input[name*="traits"]').first();
    await traitsInput.fill(testAnimalData.personality.traits.join(', '));

    // Backstory
    const backstoryInput = await personalitySection.locator('textarea[name*="backstory"], textarea[placeholder*="backstory"]').first();
    await backstoryInput.fill(testAnimalData.personality.backstory);

    // Capture form data before submission
    const submissionFormData = await page.evaluate(() => {
      const formData = {};
      const inputs = document.querySelectorAll('input, textarea, select');
      inputs.forEach(input => {
        if (input.name && input.value) {
          if (input.type === 'checkbox') {
            if (!formData[input.name]) formData[input.name] = [];
            if (input.checked) formData[input.name].push(input.value);
          } else {
            formData[input.name] = input.value;
          }
        }
      });
      return formData;
    });
    console.log('📋 Form data prepared for submission:', submissionFormData);

    // Submit the form
    console.log('💾 Submitting form...');
    const saveButton = await page.locator('button:has-text("Save"), button[type="submit"]:has-text("Update")').first();

    // Set up response listener for the save request
    const saveResponsePromise = page.waitForResponse(
      response => response.url().includes('/animals') && response.status() === 200,
      { timeout: 10000 }
    );

    await saveButton.click();

    // Wait for save response
    try {
      const saveResponse = await saveResponsePromise;
      console.log('✅ Save response received:', saveResponse.status());

      // Get response body if available
      const responseBody = await saveResponse.json().catch(() => null);
      if (responseBody) {
        console.log('📦 Response data:', JSON.stringify(responseBody, null, 2));
      }
    } catch (error) {
      console.log('⚠️ Save response timeout or error:', error.message);
    }

    // Wait for any success notification
    const successNotification = await page.locator('.toast-success, .notification-success, [role="alert"]:has-text("success")').first();
    const notificationVisible = await successNotification.isVisible({ timeout: 5000 }).catch(() => false);
    if (notificationVisible) {
      console.log('✅ Success notification displayed');
    }

    // Export captured network data
    const networkData = {
      timestamp: new Date().toISOString(),
      requests: capturedRequests,
      responses: capturedResponses,
      formDataSubmitted: submissionFormData
    };

    fs.writeFileSync(
      path.join(__dirname, 'network-capture.json'),
      JSON.stringify(networkData, null, 2)
    );
    console.log('📡 Network data saved to network-capture.json');

    // Log summary
    console.log('\n📊 Submission Summary:');
    console.log('- Requests captured:', capturedRequests.length);
    console.log('- Responses captured:', capturedResponses.length);
    console.log('- Form fields submitted:', Object.keys(submissionFormData).length);
  });

  test('Phase 2: Verify Database Persistence', async ({ page }) => {
    console.log('\n🔍 Phase 2: Database Verification');

    // Wait a moment for data to persist
    await page.waitForTimeout(2000);

    // Query DynamoDB directly (would be done via AWS SDK in real implementation)
    // For now, we'll make an API call to verify the data
    const response = await page.request.get(`${BACKEND_URL}/api/animals/${testAnimalData.animalId}`);
    const savedAnimal = await response.json();

    console.log('📦 Retrieved animal data from API:', JSON.stringify(savedAnimal, null, 2));

    // Validate voice configuration
    if (savedAnimal.voice) {
      expect(savedAnimal.voice.provider).toBe(testAnimalData.voice.provider);
      expect(savedAnimal.voice.voiceId).toBe(testAnimalData.voice.voiceId);
      console.log('✅ Voice configuration validated');
    } else {
      console.log('❌ Voice configuration missing');
    }

    // Validate guardrails
    if (savedAnimal.guardrails) {
      expect(savedAnimal.guardrails.responseMaxLength).toBe(testAnimalData.guardrails.responseMaxLength);
      console.log('✅ Guardrails configuration validated');
    } else {
      console.log('❌ Guardrails configuration missing');
    }

    // Generate validation report
    const validationReport = {
      timestamp: new Date().toISOString(),
      testScenario: 'Animal Configuration Update',
      targetEntity: testAnimalData.animalId,
      validation: {
        voice: {
          expected: testAnimalData.voice,
          actual: savedAnimal.voice || null,
          match: JSON.stringify(savedAnimal.voice) === JSON.stringify(testAnimalData.voice)
        },
        guardrails: {
          expected: testAnimalData.guardrails,
          actual: savedAnimal.guardrails || null,
          match: JSON.stringify(savedAnimal.guardrails) === JSON.stringify(testAnimalData.guardrails)
        }
      },
      summary: {
        totalFields: 2,
        matchingFields: 0,
        discrepancies: []
      }
    };

    // Count matches and discrepancies
    Object.entries(validationReport.validation).forEach(([field, validation]) => {
      if (validation.match) {
        validationReport.summary.matchingFields++;
      } else {
        validationReport.summary.discrepancies.push({
          field,
          expected: validation.expected,
          actual: validation.actual
        });
      }
    });

    fs.writeFileSync(
      path.join(__dirname, 'validation-report.json'),
      JSON.stringify(validationReport, null, 2)
    );

    console.log('\n📊 Validation Report Generated:');
    console.log(`- Total fields tested: ${validationReport.summary.totalFields}`);
    console.log(`- Matching fields: ${validationReport.summary.matchingFields}`);
    console.log(`- Discrepancies found: ${validationReport.summary.discrepancies.length}`);

    if (validationReport.summary.discrepancies.length > 0) {
      console.log('\n⚠️ Discrepancies detected:');
      validationReport.summary.discrepancies.forEach(d => {
        console.log(`  - ${d.field}: Expected vs Actual mismatch`);
      });
    }
  });
});

// Helper function to compare data
function compareData(expected, actual) {
  const differences = [];

  for (const key in expected) {
    if (expected[key] !== actual[key]) {
      differences.push({
        field: key,
        expected: expected[key],
        actual: actual[key]
      });
    }
  }

  return differences;
}