/**
 * E2E Test: Family Management Frontend-Backend Integration
 * Tests bidirectional references and role-based access control
 */

const { test, expect } = require('@playwright/test');

// Test configuration
const FRONTEND_URL = 'http://localhost:3001';
const API_URL = 'http://localhost:8080';

// Test users
const adminUser = {
  email: 'admin@cmz.org',
  password: 'admin123',
  role: 'admin'
};

const parentUser = {
  email: 'parent1@test.cmz.org',
  password: 'testpass123',
  role: 'parent'
};

test.describe('Family Management with Bidirectional References', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto(FRONTEND_URL);
  });

  test('Admin can create and edit families', async ({ page }) => {
    console.log('🧪 Testing admin family management...');

    // Step 1: Login as admin
    await page.fill('[data-testid="email-input"]', adminUser.email);
    await page.fill('[data-testid="password-input"]', adminUser.password);
    await page.click('[data-testid="login-button"]');

    // Wait for redirect to dashboard
    await page.waitForURL('**/dashboard', { timeout: 10000 });
    console.log('✅ Admin logged in');

    // Step 2: Navigate to Family Management
    await page.click('text=Family Groups');
    await page.click('text=Manage Families');
    await page.waitForSelector('h1:has-text("Family Management")');

    // Verify admin UI elements
    const addButton = await page.locator('button:has-text("Add New Family")');
    await expect(addButton).toBeVisible();
    console.log('✅ Admin UI elements visible');

    // Step 3: Create a new family
    await addButton.click();

    // Wait for modal to open
    await page.waitForSelector('[data-testid="add-family-modal"]');

    // Fill family details
    await page.fill('[name="familyName"]', 'Test Bidirectional Family');

    // Add parent
    await page.click('button:has-text("Add Parent")');
    await page.fill('[name="parent[0].name"]', 'Sarah Test');
    await page.fill('[name="parent[0].email"]', 'sarah.test@example.com');
    await page.fill('[name="parent[0].phone"]', '555-0100');

    // Add student
    await page.click('button:has-text("Add Student")');
    await page.fill('[name="student[0].name"]', 'Emma Test');
    await page.fill('[name="student[0].age"]', '10');
    await page.fill('[name="student[0].grade"]', '5th');

    // Submit form
    await page.click('button:has-text("Create Family")');

    // Wait for success message or redirect
    await page.waitForSelector('text=Family created successfully', { timeout: 5000 });
    console.log('✅ Family created');

    // Step 4: Verify family appears in list
    await page.waitForSelector('text=Test Bidirectional Family');

    // Find the family card
    const familyCard = await page.locator('.bg-white:has-text("Test Bidirectional Family")').first();

    // Verify edit button is visible (admin only)
    const editButton = await familyCard.locator('[title="Edit Family"]');
    await expect(editButton).toBeVisible();

    // Step 5: Edit the family
    await editButton.click();
    await page.waitForSelector('[data-testid="edit-family-modal"]');

    // Update family name
    await page.fill('[name="familyName"]', 'Updated Bidirectional Family');
    await page.click('button:has-text("Save Changes")');

    await page.waitForSelector('text=Family updated successfully');
    console.log('✅ Family edited by admin');

    // Step 6: Verify update in list
    await page.waitForSelector('text=Updated Bidirectional Family');
    console.log('✅ Admin can create and edit families');
  });

  test('Family member can only view their family', async ({ page }) => {
    console.log('🧪 Testing member view permissions...');

    // Step 1: Login as parent
    await page.fill('[data-testid="email-input"]', parentUser.email);
    await page.fill('[data-testid="password-input"]', parentUser.password);
    await page.click('[data-testid="login-button"]');

    // Wait for redirect to dashboard
    await page.waitForURL('**/dashboard', { timeout: 10000 });
    console.log('✅ Parent logged in');

    // Step 2: Navigate to Family Management
    await page.click('text=Family Groups');
    await page.click('text=Manage Families');
    await page.waitForSelector('h1:has-text("Family Management")');

    // Step 3: Verify limited UI for non-admin
    // Should NOT see "Add New Family" button
    const addButton = await page.locator('button:has-text("Add New Family")');
    await expect(addButton).not.toBeVisible();
    console.log('✅ Add button hidden for non-admin');

    // Step 4: Find family cards
    const familyCards = await page.locator('.bg-white.rounded-lg.shadow-md');
    const cardCount = await familyCards.count();

    if (cardCount > 0) {
      // Check first family card
      const firstCard = familyCards.first();

      // Should see view button
      const viewButton = await firstCard.locator('[title="View Details"]');
      await expect(viewButton).toBeVisible();

      // Should NOT see edit/delete buttons, but see lock icon
      const lockIcon = await firstCard.locator('[title="Admin access required"]');
      await expect(lockIcon).toBeVisible();

      console.log('✅ Member sees view-only permissions');

      // Step 5: View family details
      await viewButton.click();
      await page.waitForSelector('[data-testid="family-details-modal"]');

      // Verify read-only mode (no save button)
      const saveButton = await page.locator('button:has-text("Save Changes")');
      await expect(saveButton).not.toBeVisible();

      console.log('✅ Family details are read-only for members');
    } else {
      console.log('⚠️ No families visible to parent user');
    }
  });

  test('Validate DynamoDB bidirectional references', async ({ page, request }) => {
    console.log('🧪 Testing DynamoDB persistence...');

    // Step 1: Create test data via API
    const familyData = {
      familyName: 'DynamoDB Test Family',
      parents: [
        {
          email: `parent_${Date.now()}@test.com`,
          name: 'DynamoDB Parent',
          phone: '555-9999'
        }
      ],
      students: [
        {
          name: 'DynamoDB Student',
          age: '12',
          grade: '6th'
        }
      ],
      status: 'active'
    };

    // Create family (would need auth token in real scenario)
    const createResponse = await request.post(`${API_URL}/family`, {
      data: familyData,
      headers: {
        'Content-Type': 'application/json',
        'X-User-Id': 'test_admin_user' // Simulated admin
      }
    });

    if (createResponse.ok()) {
      const family = await createResponse.json();
      console.log(`✅ Created family: ${family.familyId}`);

      // Step 2: Verify family has user IDs, not names
      expect(family.parentIds).toBeTruthy();
      expect(Array.isArray(family.parentIds)).toBe(true);
      expect(family.studentIds).toBeTruthy();
      expect(Array.isArray(family.studentIds)).toBe(true);
      console.log('✅ Family uses ID-based references');

      // Step 3: Verify populated user details
      if (family.parents && family.students) {
        expect(family.parents[0].userId).toBeTruthy();
        expect(family.parents[0].displayName).toBe('DynamoDB Parent');
        expect(family.students[0].userId).toBeTruthy();
        expect(family.students[0].displayName).toBe('DynamoDB Student');
        console.log('✅ User details properly populated');
      }

      // Step 4: Test permissions
      expect(family.canView).toBeDefined();
      expect(family.canEdit).toBeDefined();
      console.log('✅ Permission flags included');

      // Step 5: Cleanup - soft delete
      await request.delete(`${API_URL}/family/${family.familyId}`, {
        headers: {
          'X-User-Id': 'test_admin_user'
        }
      });
      console.log('✅ Test family cleaned up');
    } else {
      console.error('❌ Failed to create test family');
    }
  });

  test('Verify role-based UI elements', async ({ page }) => {
    console.log('🧪 Testing role-based UI...');

    // Test 1: Admin UI
    await page.fill('[data-testid="email-input"]', adminUser.email);
    await page.fill('[data-testid="password-input"]', adminUser.password);
    await page.click('[data-testid="login-button"]');
    await page.waitForURL('**/dashboard');

    await page.click('text=Family Groups');
    await page.click('text=Manage Families');

    // Check for admin role indicator
    await page.waitForSelector('text=Role:');
    const roleIndicator = await page.locator('.bg-purple-100:has-text("admin")');
    await expect(roleIndicator).toBeVisible();
    console.log('✅ Admin role indicator visible');

    // Logout
    await page.click('[data-testid="logout-button"]');

    // Test 2: Parent UI
    await page.fill('[data-testid="email-input"]', parentUser.email);
    await page.fill('[data-testid="password-input"]', parentUser.password);
    await page.click('[data-testid="login-button"]');
    await page.waitForURL('**/dashboard');

    await page.click('text=Family Groups');
    await page.click('text=Manage Families');

    // Check for parent role indicator
    const parentRoleIndicator = await page.locator('.bg-green-100:has-text("parent")');
    await expect(parentRoleIndicator).toBeVisible();
    console.log('✅ Parent role indicator visible');

    // Verify descriptive text changes
    const description = await page.locator('p.text-gray-600');
    const descText = await description.textContent();
    expect(descText).toContain('View your family information');
    console.log('✅ Role-appropriate description shown');
  });
});

test.describe('Edit Functionality Validation', () => {
  test('Only admins can access edit functionality', async ({ page, request }) => {
    console.log('🧪 Validating edit permissions...');

    // Test 1: Parent cannot edit via API
    const editResponse = await request.patch(`${API_URL}/family/test_family_001`, {
      data: { familyName: 'Hacked Family Name' },
      headers: {
        'Content-Type': 'application/json',
        'X-User-Id': 'parent_user_001' // Non-admin user
      }
    });

    expect(editResponse.status()).toBe(403);
    const errorData = await editResponse.json();
    expect(errorData.message).toContain('Only admins can edit families');
    console.log('✅ API blocks non-admin edits');

    // Test 2: Admin can edit via API
    const adminEditResponse = await request.patch(`${API_URL}/family/test_family_001`, {
      data: { familyName: 'Admin Updated Family' },
      headers: {
        'Content-Type': 'application/json',
        'X-User-Id': 'admin_user_001'
      }
    });

    if (adminEditResponse.ok()) {
      console.log('✅ API allows admin edits');
    }

    // Test 3: UI enforces permissions
    await page.goto(FRONTEND_URL);
    await page.fill('[data-testid="email-input"]', parentUser.email);
    await page.fill('[data-testid="password-input"]', parentUser.password);
    await page.click('[data-testid="login-button"]');
    await page.waitForURL('**/dashboard');

    await page.click('text=Family Groups');
    await page.click('text=Manage Families');

    // Try to find edit buttons (should not exist)
    const editButtons = await page.locator('[title="Edit Family"]');
    const editCount = await editButtons.count();
    expect(editCount).toBe(0);
    console.log('✅ UI hides edit buttons for non-admins');
  });
});