/**
 * E2E Test: Educator Family Management
 * Task T015: Create Playwright test for educator family management
 * Tests educator-specific family and student group management
 */

const { test, expect } = require('@playwright/test');

// Test data
const EDUCATOR_USER = {
  email: 'educator@cmz.org',
  password: 'testpass123'
};

const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:3001';

test.describe('👨‍🏫 Educator Family Management E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto(FRONTEND_URL);
  });

  test('T015.1: Educator can successfully login', async ({ page }) => {
    // Click login button
    await page.click('text=Login');

    // Fill in educator credentials
    await page.fill('input[type="email"]', EDUCATOR_USER.email);
    await page.fill('input[type="password"]', EDUCATOR_USER.password);

    // Submit login form
    await page.click('button[type="submit"]');

    // Wait for dashboard redirect
    await page.waitForURL('**/dashboard', { timeout: 10000 });

    // Verify educator role indicator
    await expect(page.locator('text=Educator Dashboard')).toBeVisible();

    // Verify educator-specific menu items
    await expect(page.locator('nav >> text=Families')).toBeVisible();
    await expect(page.locator('nav >> text=Students')).toBeVisible();
    await expect(page.locator('nav >> text=Programs')).toBeVisible();
  });

  test('T015.2: Educator can create a new family group', async ({ page }) => {
    await loginAsEducator(page);

    // Navigate to families page
    await page.click('nav >> text=Families');
    await page.waitForURL('**/families');

    // Click create family button
    await page.click('button:has-text("Create Family")');

    // Wait for create family dialog
    await page.waitForSelector('.create-family-dialog');

    // Fill family information
    await page.fill('input[name="familyName"]', 'The Johnson Family');

    // Add parent information
    await page.click('button:has-text("Add Parent")');
    await page.fill('input[name="parentName"]', 'Sarah Johnson');
    await page.fill('input[name="parentEmail"]', 'sarah.johnson@example.com');
    await page.fill('input[name="parentPhone"]', '+1234567890');

    // Add children information
    await page.click('button:has-text("Add Child")');
    await page.fill('input[name="childName1"]', 'Emma Johnson');
    await page.fill('input[name="childAge1"]', '10');
    await page.selectOption('select[name="childGrade1"]', '5');

    await page.click('button:has-text("Add Child")');
    await page.fill('input[name="childName2"]', 'Liam Johnson');
    await page.fill('input[name="childAge2"]', '8');
    await page.selectOption('select[name="childGrade2"]', '3');

    // Add notes
    await page.fill('textarea[name="familyNotes"]',
      'New family enrolled in wildlife education program');

    // Save family
    await page.click('button:has-text("Save Family")');

    // Verify success message
    await expect(page.locator('.success-message')).toContainText('Family created successfully');

    // Verify family appears in list
    await expect(page.locator('text=The Johnson Family')).toBeVisible();
  });

  test('T015.3: Educator can view family details', async ({ page }) => {
    await loginAsEducator(page);

    // Navigate to families page
    await page.goto(`${FRONTEND_URL}/families`);

    // Click on a family to view details
    await page.click('text=The Johnson Family');

    // Wait for family details page
    await page.waitForSelector('.family-details');

    // Verify family information is displayed
    await expect(page.locator('h2:has-text("The Johnson Family")')).toBeVisible();
    await expect(page.locator('text=Sarah Johnson')).toBeVisible();
    await expect(page.locator('text=Emma Johnson (Age: 10)')).toBeVisible();
    await expect(page.locator('text=Liam Johnson (Age: 8)')).toBeVisible();

    // Verify interaction history section
    await expect(page.locator('text=Interaction History')).toBeVisible();
    await expect(page.locator('.interaction-timeline')).toBeVisible();
  });

  test('T015.4: Educator can assign program to family', async ({ page }) => {
    await loginAsEducator(page);

    // Navigate to family details
    await page.goto(`${FRONTEND_URL}/families`);
    await page.click('text=The Johnson Family');

    // Click assign program button
    await page.click('button:has-text("Assign Program")');

    // Wait for program selection dialog
    await page.waitForSelector('.program-selection-dialog');

    // Select educational program
    await page.selectOption('select[name="programType"]', 'wildlife-conservation');

    // Set program schedule
    await page.selectOption('select[name="sessionFrequency"]', 'weekly');
    await page.fill('input[name="startDate"]', '2024-02-01');
    await page.fill('input[name="endDate"]', '2024-05-01');

    // Select preferred animals for interaction
    await page.check('input[value="lion"]');
    await page.check('input[value="elephant"]');
    await page.check('input[value="penguin"]');

    // Add program notes
    await page.fill('textarea[name="programNotes"]',
      'Family interested in conservation education');

    // Save program assignment
    await page.click('button:has-text("Assign Program")');

    // Verify success
    await expect(page.locator('.success-message')).toContainText('Program assigned');

    // Verify program appears in family details
    await expect(page.locator('text=Wildlife Conservation Program')).toBeVisible();
  });

  test('T015.5: Educator can track student progress', async ({ page }) => {
    await loginAsEducator(page);

    // Navigate to students page
    await page.click('nav >> text=Students');
    await page.waitForURL('**/students');

    // Click on a student
    await page.click('text=Emma Johnson');

    // Wait for student progress page
    await page.waitForSelector('.student-progress');

    // Verify progress metrics
    await expect(page.locator('text=Learning Progress')).toBeVisible();
    await expect(page.locator('[data-testid="sessions-completed"]')).toBeVisible();
    await expect(page.locator('[data-testid="badges-earned"]')).toBeVisible();
    await expect(page.locator('[data-testid="knowledge-score"]')).toBeVisible();

    // Verify interaction chart
    await expect(page.locator('.progress-chart')).toBeVisible();

    // Check recent activities
    await expect(page.locator('text=Recent Activities')).toBeVisible();
    await expect(page.locator('.activity-list')).toBeVisible();
  });

  test('T015.6: Educator can send messages to parents', async ({ page }) => {
    await loginAsEducator(page);

    // Navigate to family details
    await page.goto(`${FRONTEND_URL}/families`);
    await page.click('text=The Johnson Family');

    // Click message parent button
    await page.click('button:has-text("Message Parent")');

    // Wait for message dialog
    await page.waitForSelector('.message-dialog');

    // Select message type
    await page.selectOption('select[name="messageType"]', 'progress-update');

    // Compose message
    await page.fill('input[name="subject"]', 'Weekly Progress Update');
    await page.fill('textarea[name="messageBody"]',
      'Emma and Liam are doing great in the wildlife program! They showed excellent engagement with the lion ambassador this week.');

    // Attach progress report
    await page.check('input[name="attachProgressReport"]');

    // Send message
    await page.click('button:has-text("Send Message")');

    // Verify message sent
    await expect(page.locator('.success-message')).toContainText('Message sent');

    // Verify message appears in communication log
    await page.click('button[role="tab"]:has-text("Communications")');
    await expect(page.locator('text=Weekly Progress Update')).toBeVisible();
  });

  test('T015.7: Educator can generate family reports', async ({ page }) => {
    await loginAsEducator(page);

    // Navigate to families page
    await page.goto(`${FRONTEND_URL}/families`);

    // Click reports button
    await page.click('button:has-text("Generate Report")');

    // Wait for report dialog
    await page.waitForSelector('.report-dialog');

    // Select report type
    await page.selectOption('select[name="reportType"]', 'monthly-summary');

    // Select families to include
    await page.check('input[value="all-families"]');

    // Select date range
    const startDate = new Date();
    startDate.setMonth(startDate.getMonth() - 1);
    await page.fill('input[name="reportStartDate"]', startDate.toISOString().split('T')[0]);
    await page.fill('input[name="reportEndDate"]', new Date().toISOString().split('T')[0]);

    // Select metrics to include
    await page.check('input[name="includeAttendance"]');
    await page.check('input[name="includeProgress"]');
    await page.check('input[name="includeEngagement"]');

    // Generate report
    const [download] = await Promise.all([
      page.waitForEvent('download'),
      page.click('button:has-text("Generate")')
    ]);

    // Verify download
    expect(download).toBeTruthy();
    const fileName = download.suggestedFilename();
    expect(fileName).toContain('family-report');
  });

  test('T015.8: Educator can schedule group activities', async ({ page }) => {
    await loginAsEducator(page);

    // Navigate to programs page
    await page.click('nav >> text=Programs');
    await page.waitForURL('**/programs');

    // Click schedule activity
    await page.click('button:has-text("Schedule Activity")');

    // Wait for scheduling dialog
    await page.waitForSelector('.schedule-activity-dialog');

    // Fill activity details
    await page.fill('input[name="activityTitle"]', 'Virtual Safari Tour');
    await page.selectOption('select[name="activityType"]', 'group-session');

    // Set date and time
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    await page.fill('input[name="activityDate"]', tomorrow.toISOString().split('T')[0]);
    await page.fill('input[name="activityTime"]', '14:00');

    // Select participating families
    await page.check('input[value="johnson-family"]');
    await page.check('input[value="smith-family"]');

    // Select animal ambassadors
    await page.check('input[value="leo-lion"]');
    await page.check('input[value="ella-elephant"]');

    // Add activity description
    await page.fill('textarea[name="activityDescription"]',
      'Interactive virtual tour with animal ambassadors');

    // Save activity
    await page.click('button:has-text("Schedule Activity")');

    // Verify activity scheduled
    await expect(page.locator('.success-message')).toContainText('Activity scheduled');

    // Verify activity appears in calendar
    await expect(page.locator('text=Virtual Safari Tour')).toBeVisible();
  });

  test('T015.9: Educator can manage learning materials', async ({ page }) => {
    await loginAsEducator(page);

    // Navigate to resources
    await page.goto(`${FRONTEND_URL}/resources`);

    // Click add material button
    await page.click('button:has-text("Add Learning Material")');

    // Wait for material dialog
    await page.waitForSelector('.material-dialog');

    // Fill material information
    await page.fill('input[name="materialTitle"]', 'Lion Conservation Guide');
    await page.selectOption('select[name="materialType"]', 'pdf');
    await page.selectOption('select[name="ageGroup"]', '8-12');

    // Upload file (simulated)
    await page.setInputFiles('input[type="file"]', {
      name: 'lion-guide.pdf',
      mimeType: 'application/pdf',
      buffer: Buffer.from('PDF content here')
    });

    // Add tags
    await page.fill('input[name="tags"]', 'lions, conservation, habitat');

    // Set visibility
    await page.check('input[name="visibleToFamilies"]');

    // Save material
    await page.click('button:has-text("Save Material")');

    // Verify material added
    await expect(page.locator('.success-message')).toContainText('Material added');
    await expect(page.locator('text=Lion Conservation Guide')).toBeVisible();
  });

  test('T015.10: Educator role-based restrictions', async ({ page }) => {
    await loginAsEducator(page);

    // Verify cannot access admin features
    await page.goto(`${FRONTEND_URL}/system/ai-provider`);
    expect(page.url()).not.toContain('/system/ai-provider');

    // Verify cannot modify animal configurations
    await page.goto(`${FRONTEND_URL}/animals`);
    const configButtons = page.locator('button:has-text("Configure")');
    await expect(configButtons).toHaveCount(0);

    // Verify CAN manage families (educator permission)
    await page.goto(`${FRONTEND_URL}/families`);
    await expect(page.locator('button:has-text("Create Family")')).toBeVisible();

    // Verify CAN view student progress (educator permission)
    await page.goto(`${FRONTEND_URL}/students`);
    await expect(page.locator('.student-list')).toBeVisible();
  });
});

// Helper function to login as educator
async function loginAsEducator(page) {
  await page.goto(`${FRONTEND_URL}/login`);
  await page.fill('input[type="email"]', EDUCATOR_USER.email);
  await page.fill('input[type="password"]', EDUCATOR_USER.password);
  await page.click('button[type="submit"]');
  await page.waitForURL('**/dashboard', { timeout: 10000 });
}