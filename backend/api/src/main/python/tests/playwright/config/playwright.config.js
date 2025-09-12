// @ts-check
const { defineConfig, devices } = require('@playwright/test');

/**
 * Playwright Configuration for CMZ Chatbot UI Testing
 * PR003946-96: Integrated playwright testing
 * 
 * @see https://playwright.dev/docs/test-configuration
 */
module.exports = defineConfig({
  // Test directory
  testDir: '../specs',
  
  // Run tests in files in parallel
  fullyParallel: true,
  
  // Fail the build on CI if you accidentally left test.only in the source code
  forbidOnly: !!process.env.CI,
  
  // Retry on CI only
  retries: process.env.CI ? 2 : 0,
  
  // Opt out of parallel tests on CI for more stability
  workers: process.env.CI ? 1 : undefined,
  
  // Reporter configuration for GitLab CI integration
  reporter: [
    // HTML report for detailed analysis
    ['html', { 
      outputFolder: '../reports/html-report',
      open: 'never'
    }],
    
    // JUnit XML for GitLab CI integration
    ['junit', { 
      outputFile: '../reports/junit-results.xml' 
    }],
    
    // JSON report for custom processing
    ['json', { 
      outputFile: '../reports/test-results.json' 
    }],
    
    // Line reporter for console output
    ['line']
  ],
  
  // Global test configuration
  use: {
    // Base URL for the application under test
    baseURL: process.env.FRONTEND_URL || 'http://localhost:3000',
    
    // Collect trace on first retry of each test failure
    trace: 'on-first-retry',
    
    // Capture screenshot on failure
    screenshot: 'only-on-failure',
    
    // Record video on failure
    video: 'retain-on-failure',
    
    // Global timeout for actions
    actionTimeout: 10 * 1000, // 10 seconds
    
    // Global timeout for navigation
    navigationTimeout: 30 * 1000, // 30 seconds
    
    // Backend API base URL for integration testing
    extraHTTPHeaders: {
      'X-Test-Mode': 'playwright',
    },
  },

  // Test timeout
  timeout: 30 * 1000, // 30 seconds per test
  
  // Expect timeout for assertions
  expect: {
    timeout: 5 * 1000, // 5 seconds for expect assertions
  },

  // Configure projects for major browsers
  projects: [
    // Desktop Browsers
    {
      name: 'chromium',
      use: { 
        ...devices['Desktop Chrome'],
        // Enable Chrome DevTools Protocol for accessibility testing
        launchOptions: {
          args: ['--enable-features=VaapiVideoDecoder']
        }
      },
    },

    {
      name: 'firefox',
      use: { 
        ...devices['Desktop Firefox'] 
      },
    },

    {
      name: 'webkit',
      use: { 
        ...devices['Desktop Safari'] 
      },
    },

    // Mobile Browsers for responsive testing
    {
      name: 'Mobile Chrome',
      use: { 
        ...devices['Pixel 5'] 
      },
    },
    
    {
      name: 'Mobile Safari',
      use: { 
        ...devices['iPhone 12'] 
      },
    },

    // High-resolution desktop for visual testing
    {
      name: 'Desktop High DPI',
      use: {
        ...devices['Desktop Chrome HiDPI'],
        viewport: { width: 1920, height: 1080 }
      },
    },
  ],

  // Configure local dev server for testing
  webServer: [
    // Backend server with file persistence mode
    {
      command: 'PERSISTENCE_MODE=file python -m flask run --host=0.0.0.0 --port=8080',
      port: 8080,
      cwd: '../../../',
      reuseExistingServer: !process.env.CI,
      env: {
        'PERSISTENCE_MODE': 'file',
        'FLASK_APP': 'openapi_server',
        'FLASK_ENV': 'development'
      },
      timeout: 120 * 1000, // 2 minutes to start
    },
    
    // Frontend server (if needed)
    ...(process.env.FRONTEND_COMMAND ? [{
      command: process.env.FRONTEND_COMMAND,
      port: 3000,
      reuseExistingServer: !process.env.CI,
      timeout: 120 * 1000, // 2 minutes to start
    }] : []),
  ],

  // Test output directory
  outputDir: '../reports/test-results',
  
  // Global setup and teardown
  globalSetup: require.resolve('../fixtures/global-setup.js'),
  globalTeardown: require.resolve('../fixtures/global-teardown.js'),
});