// Global teardown for Playwright tests
// PR003946-96: Integrated playwright testing

const fs = require('fs');
const path = require('path');

/**
 * Global teardown runs once after all tests complete
 * Cleans up test environment and generates final reports
 */
async function globalTeardown() {
  console.log('🧹 Running Playwright test cleanup...');
  
  try {
    // Update test metadata with completion info
    await updateTestMetadata();
    
    // Generate test summary report
    await generateTestSummary();
    
    // Clean up temporary files (optional - keep for debugging)
    // await cleanupTempFiles();
    
    console.log('✅ Global teardown completed successfully');
    
  } catch (error) {
    console.error('❌ Global teardown failed:', error.message);
    // Don't throw error to avoid masking test failures
  }
}

/**
 * Update test metadata with completion information
 */
async function updateTestMetadata() {
  const metadataPath = path.join(__dirname, '..', 'reports', 'test-metadata.json');
  
  if (fs.existsSync(metadataPath)) {
    const metadata = JSON.parse(fs.readFileSync(metadataPath, 'utf8'));
    
    metadata.completed_at = new Date().toISOString();
    metadata.duration_ms = new Date().getTime() - new Date(metadata.started_at).getTime();
    
    fs.writeFileSync(metadataPath, JSON.stringify(metadata, null, 2));
    console.log('📝 Test metadata updated with completion info');
  }
}

/**
 * Generate test summary report for GitLab CI integration
 */
async function generateTestSummary() {
  console.log('📊 Generating test summary report...');
  
  const reportsDir = path.join(__dirname, '..', 'reports');
  const testResultsPath = path.join(reportsDir, 'test-results.json');
  const summaryPath = path.join(reportsDir, 'test-summary.json');
  
  try {
    if (fs.existsSync(testResultsPath)) {
      const testResults = JSON.parse(fs.readFileSync(testResultsPath, 'utf8'));
      
      // Generate summary statistics
      const summary = {
        timestamp: new Date().toISOString(),
        total_tests: 0,
        passed_tests: 0,
        failed_tests: 0,
        skipped_tests: 0,
        duration_ms: 0,
        pass_rate: 0,
        browser_results: {},
        feature_results: {},
        quality_gates: {
          overall_pass: false,
          critical_features_pass: false,
          accessibility_pass: false,
          performance_pass: false
        }
      };
      
      // Process test results
      if (testResults.suites) {
        testResults.suites.forEach(suite => {
          if (suite.specs) {
            suite.specs.forEach(spec => {
              summary.total_tests += 1;
              summary.duration_ms += spec.duration || 0;
              
              if (spec.outcome === 'expected') {
                summary.passed_tests += 1;
              } else if (spec.outcome === 'skipped') {
                summary.skipped_tests += 1;
              } else {
                summary.failed_tests += 1;
              }
            });
          }
        });
      }
      
      // Calculate pass rate
      if (summary.total_tests > 0) {
        summary.pass_rate = Math.round((summary.passed_tests / summary.total_tests) * 100);
      }
      
      // Determine quality gates
      summary.quality_gates.overall_pass = summary.pass_rate >= 80;
      summary.quality_gates.critical_features_pass = summary.pass_rate >= 90;
      summary.quality_gates.accessibility_pass = true; // TODO: Implement accessibility checks
      summary.quality_gates.performance_pass = true; // TODO: Implement performance checks
      
      fs.writeFileSync(summaryPath, JSON.stringify(summary, null, 2));
      
      console.log(`📈 Test Summary:`);
      console.log(`   Total: ${summary.total_tests}`);
      console.log(`   Passed: ${summary.passed_tests}`);
      console.log(`   Failed: ${summary.failed_tests}`);
      console.log(`   Pass Rate: ${summary.pass_rate}%`);
      console.log(`   Duration: ${Math.round(summary.duration_ms / 1000)}s`);
      console.log(`   Quality Gates: ${summary.quality_gates.overall_pass ? '✅ PASS' : '❌ FAIL'}`);
      
    } else {
      console.warn('⚠️  Test results file not found, skipping summary generation');
    }
    
  } catch (error) {
    console.error('❌ Failed to generate test summary:', error.message);
  }
}

module.exports = globalTeardown;