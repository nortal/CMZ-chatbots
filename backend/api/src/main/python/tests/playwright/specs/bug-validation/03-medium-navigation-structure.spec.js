/**
 * Medium Severity Bug Validation: Navigation and Structure Issues
 *
 * Tests for MEDIUM severity bugs:
 * 8. Guardrails are in System/Safety Management instead of Animal Management
 * 9. User roles include "Visitor" (should be removed), "Educator" (should be "Parent"), "Member" (should be "Student")
 * 10. Department field enabled for all roles instead of only Administrator/Zookeeper
 *
 * Session: Friday, October 24th, 2025 8:47 AM
 * Branch: 003-animal-assistant-mgmt
 */

const { test, expect } = require('@playwright/test');

const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:3001';
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8081';

// Test users for different role scenarios
const TEST_USERS = {
  admin: {
    email: 'test@cmz.org',
    password: 'testpass123',
    role: 'admin'
  },
  parent: {
    email: 'parent1@test.cmz.org',
    password: 'testpass123',
    role: 'parent'
  },
  student: {
    email: 'student1@test.cmz.org',
    password: 'testpass123',
    role: 'student'
  }
};

/**
 * Helper: Login as specific user type
 */
async function loginAs(page, userType) {
  const user = TEST_USERS[userType];

  await page.goto(FRONTEND_URL);
  await page.waitForLoadState('networkidle');

  // Check if already logged in (redirect to dashboard)
  if (page.url().includes('/dashboard')) {
    return 'already-logged-in';
  }

  // Fill login form
  await page.fill('input[type="email"]', user.email);
  await page.fill('input[type="password"]', user.password);

  // Submit and wait for successful navigation
  // Admin/Zookeeper -> /dashboard, Parent/Student/Visitor -> /animals
  const expectedPath = (user.role === 'admin' || user.role === 'zookeeper') ? /dashboard/ : /animals/;

  await Promise.all([
    page.waitForURL(expectedPath, { timeout: 15000 }),
    page.click('button[type="submit"]')
  ]);

  // Verify we're on the expected page
  expect(page.url()).toMatch(expectedPath);

  // Look for welcome message or user indicator (use first() to avoid multiple elements)
  await expect(page.locator('text=/Welcome|Dashboard|CMZ|Animal/').first()).toBeVisible({ timeout: 5000 });

  return 'login-successful';
}

test.describe('MEDIUM SEVERITY: Navigation and Structure Issues', () => {

  test.describe('Bug #8: Guardrails Location in Navigation', () => {

    test('should find Guardrails under Animal Management section, not System/Safety', async ({ page }) => {
      // Given: Admin user is logged in
      await loginAs(page, 'admin');
      await page.goto(`${FRONTEND_URL}/dashboard`);
      await page.waitForLoadState('networkidle');

      // When: Look for Animal Management navigation section
      const animalManagementSection = page.locator('nav, [role="navigation"]').locator('text=/animal management/i').first();

      // Then: Animal Management section should exist
      await expect(animalManagementSection).toBeVisible({ timeout: 5000 });

      // And: Guardrails should be under Animal Management
      const animalNavParent = animalManagementSection.locator('..');
      const guardrailsLink = animalNavParent.locator('a:has-text("Guardrails"), a:has-text("Safety Rules")');

      await expect(guardrailsLink).toBeVisible({ timeout: 5000 });
    });

    test('should NOT find Guardrails under System or Safety Management section', async ({ page }) => {
      // Given: Admin user is logged in
      await loginAs(page, 'admin');
      await page.goto(`${FRONTEND_URL}/dashboard`);
      await page.waitForLoadState('networkidle');

      // When: Look for System or Safety Management sections
      const systemSection = page.locator('nav, [role="navigation"]').locator('text=/^system$/i, text=/system management/i').first();
      const safetySection = page.locator('nav, [role="navigation"]').locator('text=/^safety$/i, text=/safety management/i').first();

      // Then: If these sections exist, Guardrails should NOT be under them
      if (await systemSection.isVisible({ timeout: 1000 })) {
        const systemParent = systemSection.locator('..');
        const guardrailsInSystem = systemParent.locator('a:has-text("Guardrails")');
        await expect(guardrailsInSystem).not.toBeVisible();
      }

      if (await safetySection.isVisible({ timeout: 1000 })) {
        const safetyParent = safetySection.locator('..');
        const guardrailsInSafety = safetyParent.locator('a:has-text("Guardrails")');
        await expect(guardrailsInSafety).not.toBeVisible();
      }
    });

    test('should navigate to Guardrails from Animal Management menu', async ({ page }) => {
      // Given: Admin user is logged in
      await loginAs(page, 'admin');
      await page.goto(`${FRONTEND_URL}/dashboard`);
      await page.waitForLoadState('networkidle');

      // When: Click Guardrails link under Animal Management
      const guardrailsLink = page.locator('nav a:has-text("Guardrails"), nav a:has-text("Safety Rules")').first();
      await guardrailsLink.click();

      // Then: Should navigate to Guardrails page
      await page.waitForURL(/guardrail|safety/i, { timeout: 5000 });

      // And: Page should display Guardrails content
      await expect(page.locator('h1, h2').filter({ hasText: /guardrail|safety rule/i })).toBeVisible({ timeout: 5000 });
    });

    test('should have consistent breadcrumb navigation showing Animal Management > Guardrails', async ({ page }) => {
      // Given: Admin user navigates to Guardrails page
      await loginAs(page, 'admin');
      await page.goto(`${FRONTEND_URL}/animals/guardrails`);
      await page.waitForLoadState('networkidle');

      // Then: Breadcrumb should show correct hierarchy
      const breadcrumb = page.locator('[data-testid="breadcrumb"], nav[aria-label="breadcrumb"]');

      if (await breadcrumb.isVisible({ timeout: 2000 })) {
        const breadcrumbText = await breadcrumb.textContent();
        expect(breadcrumbText).toMatch(/animal.*guardrail/i);
      }
    });
  });

  test.describe('Bug #9: User Role Naming Corrections', () => {

    test('should NOT have "Visitor" as available user role', async ({ page }) => {
      // Given: Admin user is logged in and on User Management page
      await loginAs(page, 'admin');
      await page.goto(`${FRONTEND_URL}/users`);
      await page.waitForLoadState('networkidle');

      // When: Open create/edit user dialog
      const createUserButton = page.locator('button:has-text("Create User"), button:has-text("Add User")').first();
      await createUserButton.click();

      const dialog = page.locator('[role="dialog"], [data-testid="user-dialog"]');
      await expect(dialog).toBeVisible({ timeout: 5000 });

      // Then: Role dropdown should NOT include "Visitor"
      const roleSelect = dialog.locator('select[name="role"], [data-testid="role-select"]');
      await roleSelect.click();

      // Get all option values
      const options = await roleSelect.locator('option').allTextContents();
      const hasVisitor = options.some(opt => opt.toLowerCase().includes('visitor'));

      expect(hasVisitor).toBe(false);
    });

    test('should have "Parent" role instead of "Educator"', async ({ page }) => {
      // Given: Admin user is on User Management page with create dialog open
      await loginAs(page, 'admin');
      await page.goto(`${FRONTEND_URL}/users`);
      await page.waitForLoadState('networkidle');

      const createUserButton = page.locator('button:has-text("Create User"), button:has-text("Add User")').first();
      await createUserButton.click();

      const dialog = page.locator('[role="dialog"], [data-testid="user-dialog"]');
      await expect(dialog).toBeVisible({ timeout: 5000 });

      // When: Check role options
      const roleSelect = dialog.locator('select[name="role"], [data-testid="role-select"]');
      await roleSelect.click();

      const options = await roleSelect.locator('option').allTextContents();

      // Then: Should have "Parent" option
      const hasParent = options.some(opt => opt.toLowerCase().includes('parent'));
      expect(hasParent).toBe(true);

      // And: Should NOT have "Educator" option
      const hasEducator = options.some(opt => opt.toLowerCase().includes('educator'));
      expect(hasEducator).toBe(false);
    });

    test('should have "Student" role instead of "Member"', async ({ page }) => {
      // Given: Admin user is on User Management page with create dialog open
      await loginAs(page, 'admin');
      await page.goto(`${FRONTEND_URL}/users`);
      await page.waitForLoadState('networkidle');

      const createUserButton = page.locator('button:has-text("Create User"), button:has-text("Add User")').first();
      await createUserButton.click();

      const dialog = page.locator('[role="dialog"], [data-testid="user-dialog"]');
      await expect(dialog).toBeVisible({ timeout: 5000 });

      // When: Check role options
      const roleSelect = dialog.locator('select[name="role"], [data-testid="role-select"]');
      await roleSelect.click();

      const options = await roleSelect.locator('option').allTextContents();

      // Then: Should have "Student" option
      const hasStudent = options.some(opt => opt.toLowerCase().includes('student'));
      expect(hasStudent).toBe(true);

      // And: Should NOT have "Member" option
      const hasMember = options.some(opt => opt.toLowerCase().includes('member'));
      expect(hasMember).toBe(false);
    });

    test('should have correct standard roles: Admin, Zookeeper, Parent, Student', async ({ page }) => {
      // Given: Admin user with create user dialog open
      await loginAs(page, 'admin');
      await page.goto(`${FRONTEND_URL}/users`);
      await page.waitForLoadState('networkidle');

      const createUserButton = page.locator('button:has-text("Create User"), button:has-text("Add User")').first();
      await createUserButton.click();

      const dialog = page.locator('[role="dialog"], [data-testid="user-dialog"]');
      await expect(dialog).toBeVisible({ timeout: 5000 });

      // When: Get all role options
      const roleSelect = dialog.locator('select[name="role"], [data-testid="role-select"]');
      await roleSelect.click();

      const options = await roleSelect.locator('option').allTextContents();
      const optionsLower = options.map(opt => opt.toLowerCase());

      // Then: Should have exactly these 4 roles
      const expectedRoles = ['admin', 'zookeeper', 'parent', 'student'];

      for (const role of expectedRoles) {
        const hasRole = optionsLower.some(opt => opt.includes(role));
        expect(hasRole, `Should have ${role} role`).toBe(true);
      }

      // And: Should NOT have incorrect roles
      const incorrectRoles = ['visitor', 'educator', 'member'];

      for (const role of incorrectRoles) {
        const hasRole = optionsLower.some(opt => opt.includes(role));
        expect(hasRole, `Should NOT have ${role} role`).toBe(false);
      }
    });

    test('should display correct role labels in user list', async ({ page }) => {
      // Given: Admin user viewing user list
      await loginAs(page, 'admin');
      await page.goto(`${FRONTEND_URL}/users`);
      await page.waitForLoadState('networkidle');

      // When: Check displayed user roles
      const userRows = page.locator('[data-testid="user-row"], [data-testid="user-item"]');
      const count = await userRows.count();

      if (count > 0) {
        // Then: Should show correct role names
        const pageText = await page.locator('[data-testid="user-list"]').textContent();

        // Should NOT contain incorrect role names
        expect(pageText).not.toContain('Visitor');
        expect(pageText).not.toContain('Educator');
        expect(pageText).not.toContain('Member');

        // If roles are visible, they should be correct
        if (pageText.toLowerCase().includes('role')) {
          const validRoles = /admin|zookeeper|parent|student/i;
          expect(pageText).toMatch(validRoles);
        }
      }
    });
  });

  test.describe('Bug #10: Department Field Access Control', () => {

    test('should enable Department field for Administrator role', async ({ page }) => {
      // Given: Admin user creating a new admin user
      await loginAs(page, 'admin');
      await page.goto(`${FRONTEND_URL}/users`);
      await page.waitForLoadState('networkidle');

      const createUserButton = page.locator('button:has-text("Create User"), button:has-text("Add User")').first();
      await createUserButton.click();

      const dialog = page.locator('[role="dialog"], [data-testid="user-dialog"]');
      await expect(dialog).toBeVisible({ timeout: 5000 });

      // When: Select Administrator role
      const roleSelect = dialog.locator('select[name="role"], [data-testid="role-select"]');
      await roleSelect.selectOption('admin');

      // Then: Department field should be enabled
      const departmentField = dialog.locator('input[name="department"], select[name="department"]');
      await expect(departmentField).toBeEnabled({ timeout: 3000 });
    });

    test('should enable Department field for Zookeeper role', async ({ page }) => {
      // Given: Admin user creating a zookeeper user
      await loginAs(page, 'admin');
      await page.goto(`${FRONTEND_URL}/users`);
      await page.waitForLoadState('networkidle');

      const createUserButton = page.locator('button:has-text("Create User"), button:has-text("Add User")').first();
      await createUserButton.click();

      const dialog = page.locator('[role="dialog"], [data-testid="user-dialog"]');
      await expect(dialog).toBeVisible({ timeout: 5000 });

      // When: Select Zookeeper role
      const roleSelect = dialog.locator('select[name="role"], [data-testid="role-select"]');
      await roleSelect.selectOption('zookeeper');

      // Then: Department field should be enabled
      const departmentField = dialog.locator('input[name="department"], select[name="department"]');
      await expect(departmentField).toBeEnabled({ timeout: 3000 });
    });

    test('should disable Department field for Parent role', async ({ page }) => {
      // Given: Admin user creating a parent user
      await loginAs(page, 'admin');
      await page.goto(`${FRONTEND_URL}/users`);
      await page.waitForLoadState('networkidle');

      const createUserButton = page.locator('button:has-text("Create User"), button:has-text("Add User")').first();
      await createUserButton.click();

      const dialog = page.locator('[role="dialog"], [data-testid="user-dialog"]');
      await expect(dialog).toBeVisible({ timeout: 5000 });

      // When: Select Parent role
      const roleSelect = dialog.locator('select[name="role"], [data-testid="role-select"]');
      await roleSelect.selectOption('parent');

      // Then: Department field should be disabled or hidden
      const departmentField = dialog.locator('input[name="department"], select[name="department"]');

      const isDisabled = await departmentField.isDisabled().catch(() => true);
      const isHidden = await departmentField.isHidden().catch(() => true);

      expect(isDisabled || isHidden).toBe(true);
    });

    test('should disable Department field for Student role', async ({ page }) => {
      // Given: Admin user creating a student user
      await loginAs(page, 'admin');
      await page.goto(`${FRONTEND_URL}/users`);
      await page.waitForLoadState('networkidle');

      const createUserButton = page.locator('button:has-text("Create User"), button:has-text("Add User")').first();
      await createUserButton.click();

      const dialog = page.locator('[role="dialog"], [data-testid="user-dialog"]');
      await expect(dialog).toBeVisible({ timeout: 5000 });

      // When: Select Student role
      const roleSelect = dialog.locator('select[name="role"], [data-testid="role-select"]');
      await roleSelect.selectOption('student');

      // Then: Department field should be disabled or hidden
      const departmentField = dialog.locator('input[name="department"], select[name="department"]');

      const isDisabled = await departmentField.isDisabled().catch(() => true);
      const isHidden = await departmentField.isHidden().catch(() => true);

      expect(isDisabled || isHidden).toBe(true);
    });

    test('should dynamically update Department field when role changes', async ({ page }) => {
      // Given: Admin user with create user dialog open
      await loginAs(page, 'admin');
      await page.goto(`${FRONTEND_URL}/users`);
      await page.waitForLoadState('networkidle');

      const createUserButton = page.locator('button:has-text("Create User"), button:has-text("Add User")').first();
      await createUserButton.click();

      const dialog = page.locator('[role="dialog"], [data-testid="user-dialog"]');
      await expect(dialog).toBeVisible({ timeout: 5000 });

      const roleSelect = dialog.locator('select[name="role"], [data-testid="role-select"]');
      const departmentField = dialog.locator('input[name="department"], select[name="department"]');

      // When: Switch from Admin to Parent
      await roleSelect.selectOption('admin');
      await page.waitForTimeout(500); // Allow reactive update

      // Then: Department should be enabled for Admin
      await expect(departmentField).toBeEnabled();

      // When: Switch to Parent role
      await roleSelect.selectOption('parent');
      await page.waitForTimeout(500);

      // Then: Department should be disabled for Parent
      const isDisabled = await departmentField.isDisabled().catch(() => true);
      const isHidden = await departmentField.isHidden().catch(() => true);
      expect(isDisabled || isHidden).toBe(true);

      // When: Switch back to Zookeeper
      await roleSelect.selectOption('zookeeper');
      await page.waitForTimeout(500);

      // Then: Department should be enabled again
      await expect(departmentField).toBeEnabled();
    });
  });

  test.describe('Bug #11: Roles and Permissions Subsection', () => {

    test('should NOT have "Roles and Permissions" subsection in User Management', async ({ page }) => {
      // Given: Admin user is logged in
      await loginAs(page, 'admin');

      // When: Navigate to User Management
      await page.goto(`${FRONTEND_URL}/users`);
      await page.waitForLoadState('networkidle');

      // Then: Should NOT find "Roles and Permissions" subsection
      const rolesPermissionsSection = page.locator('text=/^roles and permissions$/i, [data-testid="roles-permissions"]');
      await expect(rolesPermissionsSection).not.toBeVisible();

      // And: Navigation should not have separate Roles and Permissions link
      const navLinks = page.locator('nav a, [role="navigation"] a');
      const linkTexts = await navLinks.allTextContents();
      const hasRolesPermissions = linkTexts.some(text =>
        text.toLowerCase().includes('roles and permissions')
      );

      expect(hasRolesPermissions).toBe(false);
    });

    test('should have role selection integrated into user form, not separate section', async ({ page }) => {
      // Given: Admin user creating a new user
      await loginAs(page, 'admin');
      await page.goto(`${FRONTEND_URL}/users`);
      await page.waitForLoadState('networkidle');

      const createUserButton = page.locator('button:has-text("Create User"), button:has-text("Add User")').first();
      await createUserButton.click();

      const dialog = page.locator('[role="dialog"], [data-testid="user-dialog"]');
      await expect(dialog).toBeVisible({ timeout: 5000 });

      // Then: Role field should be part of user form
      const roleField = dialog.locator('select[name="role"], [data-testid="role-select"]');
      await expect(roleField).toBeVisible();

      // And: Should be within the user creation form
      const formParent = roleField.locator('..').locator('..');
      const hasOtherFields = await formParent.locator('input[name="email"], input[name="name"]').count() > 0;
      expect(hasOtherFields).toBe(true);
    });
  });
});
