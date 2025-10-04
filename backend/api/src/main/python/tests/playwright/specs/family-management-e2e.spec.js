/**
 * Family Management End-to-End Tests
 *
 * Tests the complete family management flow:
 * 1. Frontend: UI interactions (family dialog, forms, navigation)
 * 2. Backend: API endpoints (POST /family, GET /family, PATCH /family, DELETE /family)
 * 3. Persistence: DynamoDB validation via AWS CLI
 */

const { test, expect } = require('@playwright/test');
const { spawn } = require('child_process');

const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:3001';
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8080';
const DYNAMODB_TABLE = 'quest-dev-family';

// Test admin user
const ADMIN_USER = {
  email: 'test@cmz.org',
  password: 'testpass123'
};

/**
 * Secure DynamoDB query helper
 */
async function queryDynamoDB(tableName, familyId) {
  return new Promise((resolve, reject) => {
    const args = [
      'dynamodb', 'get-item',
      '--table-name', tableName,
      '--key', JSON.stringify({ familyId: { S: familyId } }),
      '--profile', 'cmz',
      '--output', 'json'
    ];

    const process = spawn('aws', args, { stdio: ['pipe', 'pipe', 'pipe'] });

    let stdout = '';
    let stderr = '';

    process.stdout.on('data', (data) => stdout += data);
    process.stderr.on('data', (data) => stderr += data);

    process.on('close', (code) => {
      if (code === 0) {
        try {
          if (!stdout || stdout.trim() === '') {
            resolve(null); // Empty response means item not found
            return;
          }
          const result = JSON.parse(stdout);
          resolve(result.Item || null);
        } catch (e) {
          reject(new Error(`Failed to parse DynamoDB response. stdout: ${stdout.substring(0, 200)}, error: ${e.message}`));
        }
      } else {
        reject(new Error(`DynamoDB query failed (code ${code}): ${stderr}`));
      }
    });
  });
}

/**
 * Transform DynamoDB item to plain object
 */
function transformDynamoDBItem(item) {
  if (!item) return null;

  return {
    familyId: item.familyId?.S,
    familyName: item.familyName?.S,
    parentIds: item.parentIds?.L?.map(p => p.S) || [],
    studentIds: item.studentIds?.L?.map(s => s.S) || [],
    created: item.created?.S,
    modified: item.modified?.S
  };
}

/**
 * Delete DynamoDB item (cleanup)
 */
async function deleteDynamoDBItem(tableName, familyId) {
  return new Promise((resolve, reject) => {
    const args = [
      'dynamodb', 'delete-item',
      '--table-name', tableName,
      '--key', JSON.stringify({ familyId: { S: familyId } }),
      '--profile', 'cmz',
      '--output', 'json'
    ];

    const process = spawn('aws', args, { stdio: ['pipe', 'pipe', 'pipe'] });

    process.on('close', (code) => {
      if (code === 0) {
        resolve();
      } else {
        reject(new Error('DynamoDB delete failed'));
      }
    });
  });
}

test.describe('Family Management E2E Flow', () => {

  let authenticatedPage;
  let authToken;

  // Login before all tests
  test.beforeAll(async ({ browser }) => {
    const context = await browser.newContext();
    authenticatedPage = await context.newPage();

    // Login as admin
    await authenticatedPage.goto(FRONTEND_URL);
    await authenticatedPage.waitForLoadState('networkidle');

    await authenticatedPage.waitForSelector('input[type="email"]');

    await authenticatedPage.fill('input[type="email"]', ADMIN_USER.email);
    await authenticatedPage.fill('input[type="password"]', ADMIN_USER.password);

    const [response] = await Promise.all([
      authenticatedPage.waitForResponse(resp => resp.url().includes('/auth')),
      authenticatedPage.click('button[type="submit"]')
    ]);

    const authData = await response.json();
    authToken = authData.token;

    // Wait for dashboard
    await authenticatedPage.waitForURL(/dashboard|member|admin/, { timeout: 10000 });
  });

  test.describe('Create Family Flow (UI → Backend → DynamoDB)', () => {

    test('should create family through complete stack', async () => {
      const testFamilyName = `E2E Test Family ${Date.now()}`;
      let createdFamilyId;

      try {
        // 1. FRONTEND: Navigate to Family Management
        await authenticatedPage.goto(`${FRONTEND_URL}/families/manage`);
        await authenticatedPage.waitForLoadState('networkidle');

        // Click "Add New Family" button
        const addFamilyButton = authenticatedPage.locator('button:has-text("Add New Family"), button:has-text("Add Family")').first();
        await addFamilyButton.click();

        // Wait for family dialog/form
        await authenticatedPage.waitForSelector('[data-testid="family-dialog"], [role="dialog"]', { timeout: 5000 });

        // 2. FRONTEND: Fill family form - Note: Form requires at least one parent
        await authenticatedPage.fill('input[placeholder="Enter family name"]', testFamilyName);

        // Click Add Parent button to add a parent (required by form validation)
        await authenticatedPage.click('button:has-text("Add Parent")');

        // Wait for parent form fields to appear and fill them
        await authenticatedPage.waitForTimeout(500); // Wait for form to expand

        // Fill parent email (first input after clicking Add Parent)
        const parentEmailInput = authenticatedPage.locator('input[type="email"]').first();
        if (await parentEmailInput.isVisible()) {
          await parentEmailInput.fill('testparent@cmz.org');
        }

        // Add address
        await authenticatedPage.fill('input[placeholder="123 Main Street"]', '123 Zoo Lane');
        const cityInput = authenticatedPage.locator('label:has-text("City")').locator('..').locator('input');
        await cityInput.fill('Seattle');
        const stateInput = authenticatedPage.locator('label:has-text("State")').locator('..').locator('input');
        await stateInput.fill('WA');
        await authenticatedPage.fill('input[placeholder="12345"]', '98101');

        // 3. FRONTEND: Submit form and capture backend request
        const [createResponse] = await Promise.all([
          authenticatedPage.waitForResponse(resp => resp.url().includes('/family') && resp.request().method() === 'POST'),
          authenticatedPage.click('button:has-text("Add Family")')
        ]);

        // 4. BACKEND: Validate create response
        expect(createResponse.status()).toBe(201);
        const createdFamily = await createResponse.json();

        expect(createdFamily).toHaveProperty('familyId');
        expect(createdFamily.familyName).toBe(testFamilyName);
        createdFamilyId = createdFamily.familyId;

        // 5. FRONTEND: Verify family appears in list
        await authenticatedPage.waitForSelector(`text=${testFamilyName}`, { timeout: 5000 });

        // 6. BACKEND: Verify via GET /family
        const listResponse = await authenticatedPage.request.get(`${BACKEND_URL}/family`, {
          headers: { 'Authorization': `Bearer ${authToken}` }
        });
        expect(listResponse.status()).toBe(200);

        const families = await listResponse.json();
        const foundFamily = families.find(f => f.familyId === createdFamilyId);
        expect(foundFamily).toBeDefined();
        expect(foundFamily.familyName).toBe(testFamilyName);

        // 7. PERSISTENCE: Verify in DynamoDB
        const dbItem = await queryDynamoDB(DYNAMODB_TABLE, createdFamilyId);
        expect(dbItem).not.toBeNull();

        const dbFamily = transformDynamoDBItem(dbItem);
        expect(dbFamily.familyId).toBe(createdFamilyId);
        expect(dbFamily.familyName).toBe(testFamilyName);
        expect(dbFamily.parentIds).toContain('user_parent_001');
        expect(dbFamily.studentIds).toContain('user_student_001');

      } finally {
        // Cleanup: Delete test family from DynamoDB
        if (createdFamilyId) {
          await deleteDynamoDBItem(DYNAMODB_TABLE, createdFamilyId);
        }
      }
    });
  });

  test.describe('Read Family Flow (UI → Backend → DynamoDB)', () => {

    test('should display families from DynamoDB in UI', async () => {
      // 1. BACKEND: Get families from API
      const apiResponse = await authenticatedPage.request.get(`${BACKEND_URL}/family`, {
        headers: { 'Authorization': `Bearer ${authToken}` }
      });
      expect(apiResponse.status()).toBe(200);

      const apiFamilies = await apiResponse.json();
      expect(apiFamilies.length).toBeGreaterThan(0);

      const testFamily = apiFamilies[0];

      // 2. PERSISTENCE: Verify same family exists in DynamoDB
      const dbItem = await queryDynamoDB(DYNAMODB_TABLE, testFamily.familyId);
      expect(dbItem).not.toBeNull();

      const dbFamily = transformDynamoDBItem(dbItem);
      expect(dbFamily.familyName).toBe(testFamily.familyName);

      // 3. FRONTEND: Navigate to family management
      await authenticatedPage.goto(`${FRONTEND_URL}/families/manage`);
      await authenticatedPage.waitForLoadState('networkidle');

      // 4. FRONTEND: Verify family displayed in UI
      await authenticatedPage.waitForSelector(`text=${testFamily.familyName}`, { timeout: 5000 });

      // 5. FRONTEND: Verify student/parent counts match DynamoDB
      const familyCard = authenticatedPage.locator(`text=${testFamily.familyName}`).locator('..').locator('..');

      if (dbFamily.studentIds.length > 0 || dbFamily.parentIds.length > 0) {
        const countsText = await familyCard.textContent();

        if (dbFamily.studentIds.length > 0) {
          expect(countsText).toContain(`${dbFamily.studentIds.length} student`);
        }

        if (dbFamily.parentIds.length > 0) {
          expect(countsText).toContain(`${dbFamily.parentIds.length} parent`);
        }
      }
    });
  });

  test.describe('Update Family Flow (UI → Backend → DynamoDB)', () => {

    test('should update family name through complete stack', async () => {
      // First, create a test family
      const originalName = `E2E Update Test ${Date.now()}`;
      const updatedName = `${originalName} - UPDATED`;
      let testFamilyId;

      try {
        // Create family via API
        const createResponse = await authenticatedPage.request.post(`${BACKEND_URL}/family`, {
          headers: {
            'Authorization': `Bearer ${authToken}`,
            'Content-Type': 'application/json'
          },
          data: {
            familyName: originalName,
            parents: ['user_parent_001'],
            students: ['user_student_001'],
            address: {
              street: '123 Test St',
              city: 'Seattle',
              state: 'WA',
              zipCode: '98101'
            }
          }
        });

        expect(createResponse.status()).toBe(201);
        const createdFamily = await createResponse.json();
        testFamilyId = createdFamily.familyId;

        // 1. FRONTEND: Navigate and find family
        await authenticatedPage.goto(`${FRONTEND_URL}/families/manage`);
        await authenticatedPage.waitForLoadState('networkidle');
        await authenticatedPage.waitForSelector(`text=${originalName}`);

        // Click edit button for this family
        const familyCard = authenticatedPage.locator(`text=${originalName}`).locator('..').locator('..');
        const editButton = familyCard.getByRole('button', { name: 'Edit Family' });
        await editButton.click();

        // Wait for edit dialog
        await authenticatedPage.waitForSelector('[data-testid="family-dialog"], [role="dialog"]');

        // 2. FRONTEND: Update family name
        const nameField = authenticatedPage.locator('input[placeholder="Enter family name"]');
        await nameField.clear();
        await nameField.fill(updatedName);

        // 3. FRONTEND: Save changes and capture backend request
        const [updateResponse] = await Promise.all([
          authenticatedPage.waitForResponse(resp =>
            resp.url().includes(`/family/${testFamilyId}`) &&
            (resp.request().method() === 'PATCH' || resp.request().method() === 'PUT')
          ),
          authenticatedPage.click('button:has-text("Save")')
        ]);

        // 4. BACKEND: Validate update response
        expect(updateResponse.status()).toBe(200);
        const updatedFamily = await updateResponse.json();
        expect(updatedFamily.familyName).toBe(updatedName);

        // 5. FRONTEND: Verify updated name in UI
        await authenticatedPage.waitForSelector(`text=${updatedName}`, { timeout: 5000 });

        // 6. BACKEND: Verify via GET /family/{familyId}
        const getResponse = await authenticatedPage.request.get(`${BACKEND_URL}/family/${testFamilyId}`, {
          headers: { 'Authorization': `Bearer ${authToken}` }
        });
        expect(getResponse.status()).toBe(200);

        const fetchedFamily = await getResponse.json();
        expect(fetchedFamily.familyName).toBe(updatedName);

        // 7. PERSISTENCE: Verify in DynamoDB
        const dbItem = await queryDynamoDB(DYNAMODB_TABLE, testFamilyId);
        const dbFamily = transformDynamoDBItem(dbItem);
        expect(dbFamily.familyName).toBe(updatedName);

      } finally {
        // Cleanup
        if (testFamilyId) {
          await deleteDynamoDBItem(DYNAMODB_TABLE, testFamilyId);
        }
      }
    });
  });

  test.describe('Delete Family Flow (UI → Backend → DynamoDB)', () => {

    test('should delete family through complete stack', async () => {
      const testFamilyName = `E2E Delete Test ${Date.now()}`;
      let testFamilyId;

      try {
        // 1. Create test family via API
        const createResponse = await authenticatedPage.request.post(`${BACKEND_URL}/family`, {
          headers: {
            'Authorization': `Bearer ${authToken}`,
            'Content-Type': 'application/json'
          },
          data: {
            familyName: testFamilyName,
            parents: ['user_parent_001'],
            students: ['user_student_001'],
            address: {
              street: '123 Delete St',
              city: 'Seattle',
              state: 'WA',
              zipCode: '98101'
            }
          }
        });

        const createdFamily = await createResponse.json();
        testFamilyId = createdFamily.familyId;

        // 2. FRONTEND: Navigate to family management
        await authenticatedPage.goto(`${FRONTEND_URL}/families/manage`);
        await authenticatedPage.waitForLoadState('networkidle');
        await authenticatedPage.waitForSelector(`text=${testFamilyName}`);

        // 3. FRONTEND: Click delete button
        const familyCard = authenticatedPage.locator(`text=${testFamilyName}`).locator('..').locator('..');
        const deleteButton = familyCard.getByRole('button', { name: 'Delete Family' });
        await deleteButton.click();

        // Confirm deletion if confirmation dialog appears
        const confirmButton = authenticatedPage.locator('button:has-text("Confirm"), button:has-text("Yes")').first();
        if (await confirmButton.isVisible({ timeout: 2000 })) {
          const [deleteResponse] = await Promise.all([
            authenticatedPage.waitForResponse(resp =>
              resp.url().includes(`/family/${testFamilyId}`) &&
              resp.request().method() === 'DELETE'
            ),
            confirmButton.click()
          ]);

          // 4. BACKEND: Validate delete response
          expect(deleteResponse.status()).toBe(204);

          // 5. FRONTEND: Verify family removed from UI
          const familyGone = await authenticatedPage.locator(`text=${testFamilyName}`).isHidden({ timeout: 5000 });
          expect(familyGone).toBeTruthy();

          // 6. BACKEND: Verify via GET /family
          const listResponse = await authenticatedPage.request.get(`${BACKEND_URL}/family`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
          });
          const families = await listResponse.json();
          const deletedFamily = families.find(f => f.familyId === testFamilyId);
          expect(deletedFamily).toBeUndefined();

          // 7. PERSISTENCE: Verify removed from DynamoDB
          const dbItem = await queryDynamoDB(DYNAMODB_TABLE, testFamilyId);
          expect(dbItem).toBeNull();

          testFamilyId = null; // Don't try to cleanup again
        }

      } finally {
        // Cleanup if delete didn't work
        if (testFamilyId) {
          await deleteDynamoDBItem(DYNAMODB_TABLE, testFamilyId);
        }
      }
    });
  });

  test.describe('User Population Flow (Backend → DynamoDB)', () => {

    test('should display parent and student counts from family data', async () => {
      // 1. BACKEND: Get families
      const response = await authenticatedPage.request.get(`${BACKEND_URL}/family`, {
        headers: { 'Authorization': `Bearer ${authToken}` }
      });

      const families = await response.json();
      const familyWithMembers = families.find(f =>
        f.parentIds && f.parentIds.length > 0 &&
        f.studentIds && f.studentIds.length > 0
      );

      if (familyWithMembers) {
        // 2. Verify family has parentIds and studentIds arrays
        expect(familyWithMembers).toHaveProperty('parentIds');
        expect(Array.isArray(familyWithMembers.parentIds)).toBeTruthy();
        expect(familyWithMembers.parentIds.length).toBeGreaterThan(0);

        expect(familyWithMembers).toHaveProperty('studentIds');
        expect(Array.isArray(familyWithMembers.studentIds)).toBeTruthy();
        expect(familyWithMembers.studentIds.length).toBeGreaterThan(0);

        // 3. FRONTEND: Verify counts displayed correctly
        await authenticatedPage.goto(`${FRONTEND_URL}/families/manage`);
        await authenticatedPage.waitForLoadState('networkidle');

        const familyCard = authenticatedPage.locator(`text=${familyWithMembers.familyName}`).locator('..').locator('..');
        const cardText = await familyCard.textContent();

        expect(cardText).toContain(`${familyWithMembers.studentIds.length} student`);
        expect(cardText).toContain(`${familyWithMembers.parentIds.length} parent`);
      }
    });
  });
});
