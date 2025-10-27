/**
 * Playwright Configuration for Assistant Management E2E Testing
 *
 * Configured for visible browser testing with comprehensive screenshot capture
 */

import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',

  // Test execution settings
  fullyParallel: false, // Run tests sequentially for CRUD workflow
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: 1, // Single worker for sequential execution

  // Reporter configuration
  reporter: [
    ['html', { outputFolder: 'tests/reports/html' }],
    ['json', { outputFile: 'tests/reports/results.json' }],
    ['list']
  ],

  // Screenshot and video settings
  use: {
    // Base URL for navigation
    baseURL: process.env.FRONTEND_URL || 'http://localhost:3000',

    // Browser context options
    trace: 'on-first-retry',
    screenshot: 'on',
    video: 'retain-on-failure',

    // Viewport
    viewport: { width: 1280, height: 720 },

    // Timeouts
    actionTimeout: 10000,
    navigationTimeout: 30000,
  },

  // Test timeout
  timeout: 60000,

  // Projects for different browsers
  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        headless: false, // VISIBLE BROWSER MODE
        slowMo: 500, // Slow down by 500ms for visibility
      },
    },
  ],

  // Web server configuration (if needed)
  webServer: process.env.CI ? undefined : {
    command: 'npm start',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
  },
});
