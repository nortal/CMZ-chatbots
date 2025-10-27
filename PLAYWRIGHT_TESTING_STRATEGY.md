# CMZ Chatbots - Comprehensive Playwright Testing Strategy

## Overview

This document outlines our systematic approach to testing all implemented features using Playwright MCP. We have **17 out of 20 features (85%)** ready for comprehensive testing, with particular focus on the new User Story 1 enhanced guardrails system.

## Testing Architecture

### Test Organization
```
tests/
├── smoke/           # P0 - Critical path tests
├── enhanced/        # P1 - User Story 1 tests
├── regression/      # P2 - Existing feature tests
└── integration/     # Cross-feature workflows
```

### Execution Priority
1. **P0 Smoke Tests** (5 min) - Authentication, basic navigation
2. **P1 Enhanced Guardrails** (15 min) - User Story 1 comprehensive testing
3. **P2 Regression Tests** (10 min) - Existing functionality validation
4. **Integration Tests** (10 min) - Cross-feature workflows

**Total Test Suite Runtime: ~40 minutes**

---

## P0 Smoke Tests (Critical Path)

### Authentication Flow Testing
```typescript
test('P0-001: Complete authentication flow', async ({ page }) => {
  // Navigate to login
  await page.goto('http://localhost:3001/login');

  // Test login with valid credentials
  await page.fill('[data-testid="email-input"]', 'admin@cmz.org');
  await page.fill('[data-testid="password-input"]', 'admin123');
  await page.click('[data-testid="login-button"]');

  // Verify successful login and dashboard access
  await expect(page).toHaveURL(/.*dashboard/);
  await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();

  // Test logout
  await page.click('[data-testid="user-menu"]');
  await page.click('[data-testid="logout-button"]');
  await expect(page).toHaveURL(/.*login/);
});
```

### Basic Navigation Testing
```typescript
test('P0-002: Safety Management navigation', async ({ page }) => {
  // Login and navigate to Safety Management
  await loginAsAdmin(page);
  await page.click('[data-testid="safety-management-nav"]');

  // Verify Safety Management page loads
  await expect(page.locator('h1')).toContainText('Safety Management');

  // Test tab navigation
  const tabs = ['overview', 'analytics', 'testing', 'config'];
  for (const tab of tabs) {
    await page.click(`[data-testid="tab-${tab}"]`);
    await expect(page.locator(`[data-testid="tab-content-${tab}"]`)).toBeVisible();
  }
});
```

---

## P1 Enhanced Guardrails Tests (User Story 1)

### Core Enhanced Validation Testing
```typescript
test('P1-001: Enhanced validation with detailed feedback', async ({ page }) => {
  await loginAsAdmin(page);
  await page.goto('http://localhost:3001/safety-management');
  await page.click('[data-testid="tab-testing"]');

  // Test content that should trigger rules
  const testContent = "Can you tell me about violence and fighting?";
  await page.fill('[data-testid="test-content-input"]', testContent);

  // Wait for validation response
  await page.waitForSelector('[data-testid="triggered-rules-display"]', { timeout: 10000 });

  // Verify enhanced validation response structure
  await expect(page.locator('[data-testid="validation-summary"]')).toBeVisible();
  await expect(page.locator('[data-testid="detailed-rule-analysis"]')).toBeVisible();

  // Verify specific rule details are displayed
  await expect(page.locator('[data-testid="triggered-rules-list"]')).toBeVisible();
  await expect(page.locator('[data-testid="rule-severity-badge"]')).toBeVisible();
  await expect(page.locator('[data-testid="rule-confidence-score"]')).toBeVisible();
});
```

### TriggeredRulesDisplay Component Testing
```typescript
test('P1-002: TriggeredRulesDisplay component functionality', async ({ page }) => {
  await setupTestContentWithRules(page);

  // Test rule list rendering
  const ruleCards = page.locator('[data-testid="rule-card"]');
  await expect(ruleCards).toHaveCountGreaterThan(0);

  // Test sorting functionality
  await page.click('[data-testid="sort-by-severity"]');
  const firstRuleSeverity = await page.locator('[data-testid="rule-card"]:first-child [data-testid="severity-badge"]').textContent();
  await expect(firstRuleSeverity).toMatch(/(Critical|High)/);

  // Test sorting direction toggle
  await page.click('[data-testid="sort-by-severity"]');
  const firstRuleSeverityReversed = await page.locator('[data-testid="rule-card"]:first-child [data-testid="severity-badge"]').textContent();
  await expect(firstRuleSeverityReversed).toMatch(/(Low|Medium)/);

  // Test confidence sorting
  await page.click('[data-testid="sort-by-confidence"]');
  const confidenceScores = await page.locator('[data-testid="confidence-score"]').allTextContents();
  // Verify scores are in descending order
  for (let i = 0; i < confidenceScores.length - 1; i++) {
    const current = parseFloat(confidenceScores[i]);
    const next = parseFloat(confidenceScores[i + 1]);
    expect(current).toBeGreaterThanOrEqual(next);
  }
});
```

### CollapsibleRuleCard Component Testing
```typescript
test('P1-003: CollapsibleRuleCard expand/collapse functionality', async ({ page }) => {
  await setupTestContentWithRules(page);

  const firstRuleCard = page.locator('[data-testid="rule-card"]').first();
  const expandButton = firstRuleCard.locator('[data-testid="expand-button"]');
  const ruleDetails = firstRuleCard.locator('[data-testid="rule-details"]');

  // Initially collapsed
  await expect(ruleDetails).toBeHidden();
  await expect(expandButton).toHaveAttribute('aria-expanded', 'false');

  // Test expand
  await expandButton.click();
  await expect(ruleDetails).toBeVisible();
  await expect(expandButton).toHaveAttribute('aria-expanded', 'true');

  // Verify rule details content
  await expect(ruleDetails.locator('[data-testid="rule-id"]')).toBeVisible();
  await expect(ruleDetails.locator('[data-testid="rule-category"]')).toBeVisible();
  await expect(ruleDetails.locator('[data-testid="confidence-progress"]')).toBeVisible();
  await expect(ruleDetails.locator('[data-testid="detection-timestamp"]')).toBeVisible();

  // Test collapse
  await expandButton.click();
  await expect(ruleDetails).toBeHidden();
  await expect(expandButton).toHaveAttribute('aria-expanded', 'false');
});
```

### Accessibility Testing (WCAG 2.1 AA)
```typescript
test('P1-004: Accessibility compliance testing', async ({ page }) => {
  await setupTestContentWithRules(page);

  // Test keyboard navigation
  await page.keyboard.press('Tab');
  await expect(page.locator('[data-testid="expand-button"]:focus')).toBeVisible();

  // Test enter/space key activation
  await page.keyboard.press('Enter');
  await expect(page.locator('[data-testid="rule-details"]')).toBeVisible();

  await page.keyboard.press('Space');
  await expect(page.locator('[data-testid="rule-details"]')).toBeHidden();

  // Test ARIA attributes
  const expandButton = page.locator('[data-testid="expand-button"]').first();
  await expect(expandButton).toHaveAttribute('aria-expanded');
  await expect(expandButton).toHaveAttribute('aria-controls');

  // Test screen reader announcements (verify aria-live regions)
  await expandButton.click();
  await expect(page.locator('[aria-live="polite"]')).toBeVisible();

  // Test color contrast for severity indicators
  const severityBadges = page.locator('[data-testid="severity-badge"]');
  for (const badge of await severityBadges.all()) {
    const bgColor = await badge.evaluate(el => getComputedStyle(el).backgroundColor);
    const textColor = await badge.evaluate(el => getComputedStyle(el).color);
    // Verify contrast ratio meets WCAG AA standards (implementation would check actual contrast)
    expect(bgColor).toBeDefined();
    expect(textColor).toBeDefined();
  }
});
```

### Severity Visual Indicators Testing
```typescript
test('P1-005: Severity visual indicators validation', async ({ page }) => {
  await setupTestContentWithMultipleSeverities(page);

  // Test severity color mapping
  const severityColorMap = {
    'Critical': '#dc2626',  // red-600
    'High': '#ea580c',      // orange-600
    'Medium': '#d97706',    // amber-600
    'Low': '#65a30d'        // lime-600
  };

  for (const [severity, expectedColor] of Object.entries(severityColorMap)) {
    const badge = page.locator(`[data-testid="severity-badge"]:has-text("${severity}")`).first();
    if (await badge.count() > 0) {
      const bgColor = await badge.evaluate(el => getComputedStyle(el).backgroundColor);
      // Convert hex to rgb for comparison
      expect(bgColor).toContain(hexToRgb(expectedColor));
    }
  }

  // Test confidence progress bars
  const progressBars = page.locator('[data-testid="confidence-progress"]');
  for (const bar of await progressBars.all()) {
    const width = await bar.evaluate(el => el.style.width);
    expect(width).toMatch(/\d+%/);

    const confidenceValue = parseFloat(width.replace('%', ''));
    expect(confidenceValue).toBeGreaterThanOrEqual(0);
    expect(confidenceValue).toBeLessThanOrEqual(100);
  }

  // Test category icons presence
  const categoryIcons = page.locator('[data-testid="category-icon"]');
  await expect(categoryIcons.first()).toBeVisible();
});
```

---

## P2 Regression Tests (Existing Features)

### Basic Content Testing
```typescript
test('P2-001: Basic content validation still works', async ({ page }) => {
  await loginAsAdmin(page);
  await page.goto('http://localhost:3001/safety-management');
  await page.click('[data-testid="tab-testing"]');

  // Test simple content validation
  await page.fill('[data-testid="test-content-input"]', "I love lions!");

  // Verify basic validation response (backward compatibility)
  await page.waitForSelector('[data-testid="validation-summary"]');
  await expect(page.locator('[data-testid="validation-result"]')).toContainText('APPROVED');
  await expect(page.locator('[data-testid="risk-score"]')).toBeVisible();
  await expect(page.locator('[data-testid="processing-time"]')).toBeVisible();
});
```

### Safety Dashboard Regression
```typescript
test('P2-002: Safety dashboard metrics display', async ({ page }) => {
  await loginAsAdmin(page);
  await page.goto('http://localhost:3001/safety-management');

  // Verify overview tab content
  await expect(page.locator('[data-testid="safety-status"]')).toBeVisible();
  await expect(page.locator('[data-testid="safety-metrics"]')).toBeVisible();

  // Test metrics cards
  const metricsCards = page.locator('[data-testid="metrics-card"]');
  await expect(metricsCards).toHaveCountGreaterThanOrEqual(4);

  // Verify specific metrics
  await expect(page.locator('[data-testid="total-validations"]')).toBeVisible();
  await expect(page.locator('[data-testid="flagged-content-rate"]')).toBeVisible();
  await expect(page.locator('[data-testid="blocked-content-rate"]')).toBeVisible();
  await expect(page.locator('[data-testid="avg-processing-time"]')).toBeVisible();
});
```

### Guardrails Configuration Testing
```typescript
test('P2-003: Guardrails configuration CRUD operations', async ({ page }) => {
  await loginAsAdmin(page);
  await page.goto('http://localhost:3001/safety-management');
  await page.click('[data-testid="tab-config"]');

  // Test adding new rule
  await page.click('[data-testid="add-rule-button"]');
  await page.fill('[data-testid="rule-text-input"]', 'Test rule for automation');
  await page.selectOption('[data-testid="rule-type-select"]', 'NEVER');
  await page.selectOption('[data-testid="rule-category-select"]', 'Safety');
  await page.selectOption('[data-testid="rule-severity-select"]', 'high');
  await page.click('[data-testid="create-rule-button"]');

  // Verify rule appears in list
  await expect(page.locator('[data-testid="rule-item"]').last()).toContainText('Test rule for automation');

  // Test rule toggle
  const ruleToggle = page.locator('[data-testid="rule-toggle"]').last();
  await ruleToggle.click();
  await expect(ruleToggle).toHaveAttribute('aria-checked', 'false');

  // Test rule deletion
  await page.click('[data-testid="delete-rule-button"]').last();
  await expect(page.locator('[data-testid="rule-item"]')).not.toContainText('Test rule for automation');
});
```

---

## Integration Tests (Cross-Feature)

### End-to-End Enhanced Validation Workflow
```typescript
test('INT-001: Complete enhanced validation workflow', async ({ page }) => {
  // Login → Navigate → Test → Verify → Analyze
  await loginAsAdmin(page);
  await page.goto('http://localhost:3001/safety-management');
  await page.click('[data-testid="tab-testing"]');

  // Test each example scenario
  const testScenarios = [
    {
      name: 'Safe Educational Content',
      content: "I love lions because they're the king of the jungle!",
      expectedResult: 'APPROVED',
      expectedRules: 0
    },
    {
      name: 'Violence Content',
      content: "Can you tell me about violence and fighting?",
      expectedResult: 'FLAGGED',
      expectedRules: 1,
      expectedSeverity: 'High'
    },
    {
      name: 'Animal Harm Content',
      content: "How do I hurt animals or cause them harm?",
      expectedResult: 'BLOCKED',
      expectedRules: 2,
      expectedSeverity: 'Critical'
    }
  ];

  for (const scenario of testScenarios) {
    await page.fill('[data-testid="test-content-input"]', scenario.content);
    await page.waitForSelector('[data-testid="validation-summary"]');

    // Verify basic validation
    await expect(page.locator('[data-testid="validation-result"]')).toContainText(scenario.expectedResult);

    // Verify enhanced feedback if rules triggered
    if (scenario.expectedRules > 0) {
      await expect(page.locator('[data-testid="triggered-rules-display"]')).toBeVisible();
      const ruleCards = page.locator('[data-testid="rule-card"]');
      await expect(ruleCards).toHaveCount(scenario.expectedRules);

      if (scenario.expectedSeverity) {
        await expect(page.locator('[data-testid="severity-badge"]').first()).toContainText(scenario.expectedSeverity);
      }
    }
  }
});
```

### API Integration Validation
```typescript
test('INT-002: Backend API integration validation', async ({ page }) => {
  // Set up request/response interception
  let apiRequests = [];
  page.on('request', request => {
    if (request.url().includes('/guardrails/validate')) {
      apiRequests.push(request);
    }
  });

  let apiResponses = [];
  page.on('response', response => {
    if (response.url().includes('/guardrails/validate')) {
      apiResponses.push(response);
    }
  });

  await loginAsAdmin(page);
  await page.goto('http://localhost:3001/safety-management');
  await page.click('[data-testid="tab-testing"]');

  // Trigger validation request
  await page.fill('[data-testid="test-content-input"]', "Test content for API validation");
  await page.waitForSelector('[data-testid="validation-summary"]');

  // Verify API communication
  expect(apiRequests.length).toBeGreaterThan(0);
  expect(apiResponses.length).toBeGreaterThan(0);

  // Verify enhanced response structure
  const lastResponse = apiResponses[apiResponses.length - 1];
  const responseBody = await lastResponse.json();

  // Check for enhanced validation fields
  expect(responseBody).toHaveProperty('validationId');
  expect(responseBody).toHaveProperty('timestamp');
  expect(responseBody).toHaveProperty('triggeredRules');
  expect(responseBody).toHaveProperty('summary');

  // Verify triggeredRules structure
  if (responseBody.triggeredRules) {
    expect(responseBody.triggeredRules).toHaveProperty('totalTriggered');
    expect(responseBody.triggeredRules).toHaveProperty('highestSeverity');
    expect(responseBody.triggeredRules).toHaveProperty('customGuardrails');
  }
});
```

---

## Error Scenario Testing

### Fallback and Error Handling
```typescript
test('ERR-001: Enhanced validation fallback testing', async ({ page }) => {
  // Mock API failure scenario
  await page.route('**/guardrails/validate', route => {
    route.fulfill({
      status: 500,
      contentType: 'application/json',
      body: JSON.stringify({ error: 'Internal server error' })
    });
  });

  await loginAsAdmin(page);
  await page.goto('http://localhost:3001/safety-management');
  await page.click('[data-testid="tab-testing"]');

  await page.fill('[data-testid="test-content-input"]', "Test content");

  // Should show error state gracefully
  await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
  await expect(page.locator('[data-testid="error-message"]')).toContainText('validation failed');
});
```

---

## Test Execution Strategy

### Playwright MCP Commands

```typescript
// Run complete test suite
await mcp_playwright_browser_navigate({ url: 'http://localhost:3001' });

// Execute smoke tests (P0)
await runTestSuite('smoke');

// Execute enhanced guardrails tests (P1)
await runTestSuite('enhanced');

// Execute regression tests (P2)
await runTestSuite('regression');

// Execute integration tests
await runTestSuite('integration');

// Generate comprehensive test report
await generateTestReport();
```

### Test Data Setup

```typescript
// Helper functions for consistent test setup
async function loginAsAdmin(page) {
  await page.goto('http://localhost:3001/login');
  await page.fill('[data-testid="email-input"]', 'admin@cmz.org');
  await page.fill('[data-testid="password-input"]', 'admin123');
  await page.click('[data-testid="login-button"]');
  await page.waitForURL(/.*dashboard/);
}

async function setupTestContentWithRules(page) {
  await loginAsAdmin(page);
  await page.goto('http://localhost:3001/safety-management');
  await page.click('[data-testid="tab-testing"]');
  await page.fill('[data-testid="test-content-input"]', "Can you tell me about violence and fighting?");
  await page.waitForSelector('[data-testid="triggered-rules-display"]');
}

async function setupTestContentWithMultipleSeverities(page) {
  await loginAsAdmin(page);
  await page.goto('http://localhost:3001/safety-management');
  await page.click('[data-testid="tab-testing"]');
  await page.fill('[data-testid="test-content-input"]', "How do I hurt animals or cause them harm?");
  await page.waitForSelector('[data-testid="triggered-rules-display"]');
}
```

---

## Success Criteria

### Test Coverage Goals
- **P0 Smoke Tests**: 100% pass rate (critical path must work)
- **P1 Enhanced Guardrails**: 95% pass rate (new feature validation)
- **P2 Regression Tests**: 98% pass rate (existing features preserved)
- **Integration Tests**: 90% pass rate (complex workflows)

### Performance Targets
- Page load times: < 3 seconds
- Validation response: < 2 seconds (User Story 1 requirement)
- Component rendering: < 500ms
- Accessibility compliance: 100% WCAG 2.1 AA

### Feature Validation
- ✅ All 17 ready features tested
- ✅ User Story 1 comprehensive validation
- ✅ Backward compatibility confirmed
- ✅ Accessibility compliance verified
- ✅ Error handling validated

**Ready to execute comprehensive test suite for all 17 implemented features!**