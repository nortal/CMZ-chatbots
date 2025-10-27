/**
 * E2E Test: Admin Role Login and Dashboard
 * Task T013: Create Playwright test for admin role login and dashboard
 * Tests admin-specific functionality and metrics visibility
 */

const { test, expect } = require('@playwright/test');

// Test data
const ADMIN_USER = {
  email: 'admin@cmz.org',
  password: 'testpass123'
};

const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:3001';

test.describe('🔐 Admin Dashboard E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto(FRONTEND_URL);
  });

  test('T013.1: Admin can successfully login', async ({ page }) => {
    // Click login button
    await page.click('text=Login');

    // Fill in admin credentials
    await page.fill('input[type="email"]', ADMIN_USER.email);
    await page.fill('input[type="password"]', ADMIN_USER.password);

    // Submit login form
    await page.click('button[type="submit"]');

    // Wait for dashboard redirect
    await page.waitForURL('**/dashboard', { timeout: 10000 });

    // Verify admin role indicator
    await expect(page.locator('text=Admin Dashboard')).toBeVisible();

    // Check for JWT token in localStorage
    const token = await page.evaluate(() => localStorage.getItem('token'));
    expect(token).toBeTruthy();
  });

  test('T013.2: Admin dashboard displays correct metrics', async ({ page }) => {
    // Login as admin first
    await loginAsAdmin(page);

    // Wait for dashboard to load
    await page.waitForSelector('.dashboard-metrics', { timeout: 10000 });

    // Verify 3 key metrics are displayed
    const totalUsers = page.locator('[data-testid="metric-total-users"]');
    const totalAnimals = page.locator('[data-testid="metric-total-animals"]');
    const activeConversations = page.locator('[data-testid="metric-active-conversations"]');

    await expect(totalUsers).toBeVisible();
    await expect(totalAnimals).toBeVisible();
    await expect(activeConversations).toBeVisible();

    // Verify metrics have values
    const usersCount = await totalUsers.textContent();
    expect(parseInt(usersCount)).toBeGreaterThanOrEqual(0);

    const animalsCount = await totalAnimals.textContent();
    expect(parseInt(animalsCount)).toBeGreaterThanOrEqual(0);

    const conversationsCount = await activeConversations.textContent();
    expect(parseInt(conversationsCount)).toBeGreaterThanOrEqual(0);
  });

  test('T013.3: Admin can access all menu sections', async ({ page }) => {
    await loginAsAdmin(page);

    // Check for admin-only menu items
    const menuItems = [
      'Dashboard',
      'Users',
      'Families',
      'Animals',
      'Animal Management',
      'System',
      'AI Provider Settings'
    ];

    for (const item of menuItems) {
      const menuLink = page.locator(`nav >> text=${item}`);
      await expect(menuLink).toBeVisible();
    }

    // Test navigation to AI Provider Settings (admin-only)
    await page.click('text=System');
    await page.click('text=AI Provider Settings');
    await page.waitForURL('**/system/ai-provider');

    // Verify AI Provider Settings page loaded
    await expect(page.locator('text=ChatGPT Configuration')).toBeVisible();
  });

  test('T013.4: Admin can manage users', async ({ page }) => {
    await loginAsAdmin(page);

    // Navigate to users page
    await page.click('nav >> text=Users');
    await page.waitForURL('**/users');

    // Verify user list is visible
    await expect(page.locator('.user-list')).toBeVisible();

    // Check for user management actions
    await expect(page.locator('button:has-text("Add User")')).toBeVisible();

    // Verify user table has expected columns
    const headers = ['Name', 'Email', 'Role', 'Status', 'Actions'];
    for (const header of headers) {
      await expect(page.locator(`th:has-text("${header}")`)).toBeVisible();
    }
  });

  test('T013.5: Admin can view system configuration', async ({ page }) => {
    await loginAsAdmin(page);

    // Navigate to system configuration
    await page.click('nav >> text=System');
    await page.waitForSelector('.system-menu');

    // Check system menu options
    const systemOptions = [
      'AI Provider Settings',
      'System Health',
      'Configuration'
    ];

    for (const option of systemOptions) {
      await expect(page.locator(`.system-menu >> text=${option}`)).toBeVisible();
    }

    // Test system health check
    await page.click('text=System Health');
    await page.waitForURL('**/system/health');

    // Verify health status indicators
    await expect(page.locator('[data-testid="health-status"]')).toBeVisible();
  });

  test('T013.6: Admin can configure AI provider', async ({ page }) => {
    await loginAsAdmin(page);

    // Navigate to AI Provider Settings
    await page.goto(`${FRONTEND_URL}/system/ai-provider`);

    // Verify configuration form elements
    await expect(page.locator('select[name="provider"]')).toBeVisible();
    await expect(page.locator('input[name="apiKey"]')).toBeVisible();
    await expect(page.locator('input[name="monthlyBudget"]')).toBeVisible();

    // Check for GPT management section
    await expect(page.locator('text=GPT Instances')).toBeVisible();
    await expect(page.locator('button:has-text("Create GPT")')).toBeVisible();

    // Verify current spend display
    await expect(page.locator('[data-testid="current-spend"]')).toBeVisible();
  });

  test('T013.7: Admin logout functionality', async ({ page }) => {
    await loginAsAdmin(page);

    // Find and click logout button
    await page.click('[data-testid="user-menu"]');
    await page.click('text=Logout');

    // Verify redirect to login page
    await page.waitForURL('**/login');

    // Verify token is removed
    const token = await page.evaluate(() => localStorage.getItem('token'));
    expect(token).toBeFalsy();

    // Verify can't access protected routes
    await page.goto(`${FRONTEND_URL}/dashboard`);
    await page.waitForURL('**/login');
  });

  test('T013.8: Admin role-based access control', async ({ page }) => {
    await loginAsAdmin(page);

    // Try to access admin-only features
    await page.goto(`${FRONTEND_URL}/system/ai-provider`);

    // Should have access - page loads without redirect
    await expect(page).toHaveURL(/.*system\/ai-provider/);

    // Verify admin-specific actions are available
    const adminActions = page.locator('.admin-actions');
    await expect(adminActions).toBeVisible();
  });
});

// Helper function to login as admin
async function loginAsAdmin(page) {
  await page.goto(`${FRONTEND_URL}/login`);
  await page.fill('input[type="email"]', ADMIN_USER.email);
  await page.fill('input[type="password"]', ADMIN_USER.password);
  await page.click('button[type="submit"]');
  await page.waitForURL('**/dashboard', { timeout: 10000 });
}