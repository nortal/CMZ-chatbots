// Global setup for Playwright tests
// PR003946-96: Integrated playwright testing

const fs = require('fs');
const path = require('path');

/**
 * Global setup runs once before all tests
 * Sets up backend in file persistence mode and prepares test environment
 */
async function globalSetup() {
  console.log('🚀 Setting up Playwright test environment...');
  
  // Ensure we're in file persistence mode for isolated testing
  process.env.PERSISTENCE_MODE = 'file';
  
  // Create test reports directory
  const reportsDir = path.join(__dirname, '..', 'reports');
  if (!fs.existsSync(reportsDir)) {
    fs.mkdirSync(reportsDir, { recursive: true });
  }
  
  // Create screenshots directory
  const screenshotsDir = path.join(reportsDir, 'screenshots');
  if (!fs.existsSync(screenshotsDir)) {
    fs.mkdirSync(screenshotsDir, { recursive: true });
  }
  
  // Create videos directory
  const videosDir = path.join(reportsDir, 'videos');
  if (!fs.existsSync(videosDir)) {
    fs.mkdirSync(videosDir, { recursive: true });
  }
  
  try {
    // Verify backend API is accessible
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8080';
    console.log(`📡 Checking backend availability at ${backendUrl}`);
    
    // Wait for backend to be ready (this will be handled by webServer config)
    console.log('⏳ Backend will be started by webServer configuration...');
    
    // Initialize test data
    await initializeTestData();
    
    console.log('✅ Global setup completed successfully');
    
  } catch (error) {
    console.error('❌ Global setup failed:', error.message);
    throw error;
  }
}

/**
 * Initialize test data for consistent test execution
 */
async function initializeTestData() {
  console.log('📊 Initializing test data...');
  
  // Test data will be automatically loaded by file persistence mode
  // from openapi_server/impl/utils/orm/test_data.json
  
  const testDataPath = path.join(__dirname, '..', '..', '..', 'openapi_server', 'impl', 'utils', 'orm', 'test_data.json');
  
  if (fs.existsSync(testDataPath)) {
    console.log('✅ Test data file found at:', testDataPath);
  } else {
    console.warn('⚠️  Test data file not found at:', testDataPath);
  }
  
  // Create test environment metadata
  const testMetadata = {
    test_run_id: `playwright_${Date.now()}`,
    started_at: new Date().toISOString(),
    persistence_mode: 'file',
    backend_url: process.env.BACKEND_URL || 'http://localhost:8080',
    frontend_url: process.env.FRONTEND_URL || 'http://localhost:3000'
  };
  
  const metadataPath = path.join(__dirname, '..', 'reports', 'test-metadata.json');
  fs.writeFileSync(metadataPath, JSON.stringify(testMetadata, null, 2));
  
  console.log('📝 Test metadata created:', metadataPath);
}

module.exports = globalSetup;