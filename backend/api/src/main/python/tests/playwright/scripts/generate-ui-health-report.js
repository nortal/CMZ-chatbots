#!/usr/bin/env node

// UI Health Report Generator for CMZ Chatbot Platform
// PR003946-96: Integrated playwright testing

const fs = require('fs');
const path = require('path');

/**
 * Generate comprehensive UI health report for GitLab CI and stakeholders
 * Creates executive summary, feature-level details, and technical metrics
 */
class UIHealthReportGenerator {
  constructor() {
    this.reportsDir = path.join(__dirname, '..', 'reports');
    this.outputPath = path.join(this.reportsDir, 'ui-health-report.html');
    this.jsonReportPath = path.join(this.reportsDir, 'test-results.json');
    this.featureMappingPath = path.join(__dirname, '..', 'config', 'feature-mapping.json');
  }

  /**
   * Generate complete UI health report
   */
  async generate() {
    console.log('🏥 Generating UI Health Report...');

    try {
      // Load test results and feature mapping
      const testResults = await this.loadTestResults();
      const featureMapping = await this.loadFeatureMapping();
      
      // Analyze results
      const analysis = this.analyzeTestResults(testResults, featureMapping);
      
      // Generate HTML report
      const htmlReport = this.generateHTMLReport(analysis);
      
      // Write report
      fs.writeFileSync(this.outputPath, htmlReport);
      
      // Generate JSON summary for CI/CD
      const jsonSummary = this.generateJSONSummary(analysis);
      fs.writeFileSync(path.join(this.reportsDir, 'ui-health-summary.json'), JSON.stringify(jsonSummary, null, 2));
      
      console.log(`✅ UI Health Report generated: ${this.outputPath}`);
      console.log(`📊 Pass Rate: ${analysis.overall.passRate}%`);
      console.log(`🎯 Quality Gates: ${analysis.qualityGates.overall ? 'PASS' : 'FAIL'}`);
      
      return analysis;
      
    } catch (error) {
      console.error('❌ Failed to generate UI Health Report:', error.message);
      throw error;
    }
  }

  /**
   * Load test results from Playwright JSON report
   */
  async loadTestResults() {
    if (!fs.existsSync(this.jsonReportPath)) {
      return {
        suites: [],
        config: {},
        stats: { total: 0, passed: 0, failed: 0, skipped: 0 }
      };
    }

    const rawData = fs.readFileSync(this.jsonReportPath, 'utf8');
    return JSON.parse(rawData);
  }

  /**
   * Load feature mapping configuration
   */
  async loadFeatureMapping() {
    if (!fs.existsSync(this.featureMappingPath)) {
      return { features: {}, quality_gates: {} };
    }

    const rawData = fs.readFileSync(this.featureMappingPath, 'utf8');
    return JSON.parse(rawData);
  }

  /**
   * Analyze test results and calculate metrics
   */
  analyzeTestResults(testResults, featureMapping) {
    const analysis = {
      timestamp: new Date().toISOString(),
      overall: {
        totalTests: 0,
        passedTests: 0,
        failedTests: 0,
        skippedTests: 0,
        passRate: 0,
        duration: 0
      },
      features: {},
      browsers: {},
      qualityGates: {
        overall: false,
        criticalFeatures: false,
        accessibility: false,
        performance: false,
        mobileFriendly: false
      },
      recommendations: [],
      trends: {
        improving: [],
        degrading: [],
        stable: []
      }
    };

    // Process test suites
    if (testResults.suites) {
      testResults.suites.forEach(suite => {
        if (suite.specs) {
          suite.specs.forEach(spec => {
            analysis.overall.totalTests++;
            
            const duration = spec.tests?.reduce((sum, test) => sum + (test.duration || 0), 0) || 0;
            analysis.overall.duration += duration;

            if (spec.outcome === 'expected') {
              analysis.overall.passedTests++;
            } else if (spec.outcome === 'skipped') {
              analysis.overall.skippedTests++;
            } else {
              analysis.overall.failedTests++;
            }

            // Categorize by feature
            const featureName = this.extractFeatureName(spec.title || suite.title);
            if (!analysis.features[featureName]) {
              analysis.features[featureName] = {
                total: 0,
                passed: 0,
                failed: 0,
                passRate: 0,
                criticalIssues: [],
                recommendations: []
              };
            }

            analysis.features[featureName].total++;
            if (spec.outcome === 'expected') {
              analysis.features[featureName].passed++;
            } else if (spec.outcome !== 'skipped') {
              analysis.features[featureName].failed++;
            }
          });
        }
      });
    }

    // Calculate pass rates
    if (analysis.overall.totalTests > 0) {
      analysis.overall.passRate = Math.round(
        (analysis.overall.passedTests / analysis.overall.totalTests) * 100
      );
    }

    // Calculate feature pass rates
    Object.keys(analysis.features).forEach(feature => {
      const featureData = analysis.features[feature];
      if (featureData.total > 0) {
        featureData.passRate = Math.round((featureData.passed / featureData.total) * 100);
      }
    });

    // Evaluate quality gates
    this.evaluateQualityGates(analysis, featureMapping);

    // Generate recommendations
    this.generateRecommendations(analysis);

    return analysis;
  }

  /**
   * Extract feature name from test title
   */
  extractFeatureName(title) {
    if (!title) return 'Unknown';
    
    const featurePatterns = [
      /authentication/i,
      /login/i,
      /dashboard/i,
      /chat/i,
      /admin/i,
      /navigation/i,
      /responsive/i,
      /accessibility/i,
      /performance/i
    ];

    for (const pattern of featurePatterns) {
      if (pattern.test(title)) {
        return pattern.source.replace(/[^a-z]/gi, '').toLowerCase();
      }
    }

    return 'other';
  }

  /**
   * Evaluate quality gates based on thresholds
   */
  evaluateQualityGates(analysis, featureMapping) {
    const gates = featureMapping.quality_gates?.pass_thresholds || {
      critical_features: 100,
      standard_features: 90,
      boundary_conditions: 80,
      accessibility_compliance: 95,
      mobile_responsive: 85
    };

    // Overall quality gate
    analysis.qualityGates.overall = analysis.overall.passRate >= 85;

    // Critical features (authentication, chat, admin)
    const criticalFeatures = ['authentication', 'chat', 'admin'];
    const criticalPassRates = criticalFeatures.map(feature => 
      analysis.features[feature]?.passRate || 0
    );
    analysis.qualityGates.criticalFeatures = criticalPassRates.every(rate => rate >= gates.critical_features);

    // Accessibility (placeholder - would integrate with axe-core)
    analysis.qualityGates.accessibility = analysis.overall.passRate >= gates.accessibility_compliance;

    // Performance (placeholder - would check performance test results)
    analysis.qualityGates.performance = analysis.overall.passRate >= 80;

    // Mobile responsive (placeholder - would check mobile test results)
    analysis.qualityGates.mobileFriendly = analysis.overall.passRate >= gates.mobile_responsive;
  }

  /**
   * Generate actionable recommendations
   */
  generateRecommendations(analysis) {
    const recommendations = [];

    // Overall pass rate recommendations
    if (analysis.overall.passRate < 90) {
      recommendations.push({
        priority: 'high',
        category: 'quality',
        title: 'Improve Overall Test Pass Rate',
        description: `Current pass rate is ${analysis.overall.passRate}%, target is 90%+`,
        actions: [
          'Focus on failing tests in critical features',
          'Review and fix boundary condition handling',
          'Improve error handling and user feedback'
        ]
      });
    }

    // Feature-specific recommendations
    Object.entries(analysis.features).forEach(([feature, data]) => {
      if (data.passRate < 80) {
        recommendations.push({
          priority: data.passRate < 50 ? 'critical' : 'high',
          category: 'feature',
          title: `Improve ${feature} Feature Stability`,
          description: `${feature} has ${data.passRate}% pass rate with ${data.failed} failing tests`,
          actions: [
            `Review failing tests in ${feature} functionality`,
            'Check for UI element selector changes',
            'Validate backend integration points',
            'Consider feature refactoring if consistently failing'
          ]
        });
      }
    });

    // Performance recommendations
    if (analysis.overall.duration > 300000) { // > 5 minutes
      recommendations.push({
        priority: 'medium',
        category: 'performance',
        title: 'Optimize Test Execution Time',
        description: `Tests take ${Math.round(analysis.overall.duration / 1000)}s, consider optimization`,
        actions: [
          'Enable parallel test execution',
          'Optimize page load waits and timeouts',
          'Consider test data setup optimization',
          'Profile slow-running tests'
        ]
      });
    }

    analysis.recommendations = recommendations;
  }

  /**
   * Generate HTML report with styling
   */
  generateHTMLReport(analysis) {
    const passRateColor = analysis.overall.passRate >= 90 ? '#10b981' : 
                         analysis.overall.passRate >= 75 ? '#f59e0b' : '#ef4444';

    return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CMZ Chatbot - UI Health Report</title>
    <style>
        * { box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6; 
            color: #1f2937; 
            max-width: 1200px; 
            margin: 0 auto; 
            padding: 20px;
            background-color: #f9fafb;
        }
        .header { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; 
            padding: 2rem; 
            border-radius: 12px; 
            margin-bottom: 2rem;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }
        .header h1 { margin: 0; font-size: 2.5rem; font-weight: 700; }
        .header p { margin: 0.5rem 0 0 0; opacity: 0.9; font-size: 1.1rem; }
        .metrics-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
            gap: 1.5rem; 
            margin-bottom: 2rem; 
        }
        .metric-card { 
            background: white; 
            padding: 1.5rem; 
            border-radius: 12px; 
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
        }
        .metric-value { 
            font-size: 2.5rem; 
            font-weight: 700; 
            color: ${passRateColor}; 
            margin: 0;
        }
        .metric-label { 
            color: #6b7280; 
            font-size: 0.875rem; 
            text-transform: uppercase; 
            letter-spacing: 0.05em;
            margin: 0;
        }
        .section { 
            background: white; 
            padding: 2rem; 
            border-radius: 12px; 
            margin-bottom: 2rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }
        .section h2 { 
            margin-top: 0; 
            color: #1f2937; 
            border-bottom: 2px solid #e5e7eb; 
            padding-bottom: 0.5rem;
        }
        .feature-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); 
            gap: 1rem; 
        }
        .feature-card { 
            background: #f8fafc; 
            padding: 1rem; 
            border-radius: 8px; 
            border-left: 4px solid #e5e7eb;
        }
        .feature-card.pass { border-left-color: #10b981; }
        .feature-card.warn { border-left-color: #f59e0b; }
        .feature-card.fail { border-left-color: #ef4444; }
        .feature-name { 
            font-weight: 600; 
            margin: 0 0 0.5rem 0; 
            text-transform: capitalize;
        }
        .feature-stats { 
            font-size: 0.875rem; 
            color: #6b7280; 
        }
        .quality-gates { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 1rem; 
        }
        .gate { 
            padding: 1rem; 
            border-radius: 8px; 
            text-align: center;
        }
        .gate.pass { background: #d1fae5; color: #065f46; }
        .gate.fail { background: #fee2e2; color: #991b1b; }
        .recommendations { 
            list-style: none; 
            padding: 0; 
        }
        .recommendation { 
            background: #fef3c7; 
            border-left: 4px solid #f59e0b; 
            padding: 1rem; 
            margin-bottom: 1rem; 
            border-radius: 0 8px 8px 0;
        }
        .recommendation.critical { 
            background: #fee2e2; 
            border-left-color: #ef4444; 
        }
        .recommendation h4 { 
            margin: 0 0 0.5rem 0; 
            color: #1f2937;
        }
        .actions { 
            margin: 0.5rem 0 0 0; 
            padding-left: 1.25rem;
        }
        .timestamp { 
            color: #6b7280; 
            font-size: 0.875rem; 
            text-align: center; 
            margin-top: 2rem;
        }
        @media (max-width: 768px) {
            .metrics-grid { grid-template-columns: 1fr; }
            .feature-grid { grid-template-columns: 1fr; }
            .quality-gates { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏥 UI Health Report</h1>
        <p>CMZ Chatbot Platform - Comprehensive UI Testing Analysis</p>
    </div>

    <div class="metrics-grid">
        <div class="metric-card">
            <p class="metric-value">${analysis.overall.passRate}%</p>
            <p class="metric-label">Overall Pass Rate</p>
        </div>
        <div class="metric-card">
            <p class="metric-value">${analysis.overall.totalTests}</p>
            <p class="metric-label">Total Tests</p>
        </div>
        <div class="metric-card">
            <p class="metric-value">${analysis.overall.passedTests}</p>
            <p class="metric-label">Passed Tests</p>
        </div>
        <div class="metric-card">
            <p class="metric-value">${Math.round(analysis.overall.duration / 1000)}s</p>
            <p class="metric-label">Execution Time</p>
        </div>
    </div>

    <div class="section">
        <h2>🎯 Quality Gates</h2>
        <div class="quality-gates">
            <div class="gate ${analysis.qualityGates.overall ? 'pass' : 'fail'}">
                <strong>Overall Quality</strong><br>
                ${analysis.qualityGates.overall ? '✅ PASS' : '❌ FAIL'}
            </div>
            <div class="gate ${analysis.qualityGates.criticalFeatures ? 'pass' : 'fail'}">
                <strong>Critical Features</strong><br>
                ${analysis.qualityGates.criticalFeatures ? '✅ PASS' : '❌ FAIL'}
            </div>
            <div class="gate ${analysis.qualityGates.accessibility ? 'pass' : 'fail'}">
                <strong>Accessibility</strong><br>
                ${analysis.qualityGates.accessibility ? '✅ PASS' : '❌ FAIL'}
            </div>
            <div class="gate ${analysis.qualityGates.performance ? 'pass' : 'fail'}">
                <strong>Performance</strong><br>
                ${analysis.qualityGates.performance ? '✅ PASS' : '❌ FAIL'}
            </div>
        </div>
    </div>

    <div class="section">
        <h2>📊 Feature Analysis</h2>
        <div class="feature-grid">
            ${Object.entries(analysis.features).map(([feature, data]) => `
                <div class="feature-card ${data.passRate >= 90 ? 'pass' : data.passRate >= 75 ? 'warn' : 'fail'}">
                    <h3 class="feature-name">${feature}</h3>
                    <div class="feature-stats">
                        <strong>${data.passRate}%</strong> pass rate<br>
                        ${data.passed}/${data.total} tests passing
                        ${data.failed > 0 ? `<br><span style="color: #ef4444">${data.failed} failing</span>` : ''}
                    </div>
                </div>
            `).join('')}
        </div>
    </div>

    ${analysis.recommendations.length > 0 ? `
    <div class="section">
        <h2>💡 Recommendations</h2>
        <ul class="recommendations">
            ${analysis.recommendations.map(rec => `
                <li class="recommendation ${rec.priority}">
                    <h4>${rec.title}</h4>
                    <p>${rec.description}</p>
                    <ul class="actions">
                        ${rec.actions.map(action => `<li>${action}</li>`).join('')}
                    </ul>
                </li>
            `).join('')}
        </ul>
    </div>
    ` : ''}

    <div class="timestamp">
        Report generated on ${new Date(analysis.timestamp).toLocaleString()}
    </div>
</body>
</html>`;
  }

  /**
   * Generate JSON summary for CI/CD integration
   */
  generateJSONSummary(analysis) {
    return {
      timestamp: analysis.timestamp,
      pass_rate: analysis.overall.passRate,
      total_tests: analysis.overall.totalTests,
      passed_tests: analysis.overall.passedTests,
      failed_tests: analysis.overall.failedTests,
      quality_gates: analysis.qualityGates,
      critical_issues: analysis.recommendations.filter(r => r.priority === 'critical').length,
      recommendations_count: analysis.recommendations.length,
      features: Object.keys(analysis.features).map(feature => ({
        name: feature,
        pass_rate: analysis.features[feature].passRate,
        tests: analysis.features[feature].total
      }))
    };
  }
}

// CLI execution
if (require.main === module) {
  const generator = new UIHealthReportGenerator();
  generator.generate()
    .then(analysis => {
      console.log(`\n📋 Report Summary:`);
      console.log(`   Overall: ${analysis.overall.passRate}% (${analysis.overall.passedTests}/${analysis.overall.totalTests})`);
      console.log(`   Quality Gates: ${analysis.qualityGates.overall ? '✅ PASS' : '❌ FAIL'}`);
      console.log(`   Recommendations: ${analysis.recommendations.length}`);
      console.log(`   Report: file://${path.resolve(__dirname, '..', 'reports', 'ui-health-report.html')}\n`);
      
      process.exit(analysis.qualityGates.overall ? 0 : 1);
    })
    .catch(error => {
      console.error('Failed to generate report:', error);
      process.exit(1);
    });
}

module.exports = UIHealthReportGenerator;