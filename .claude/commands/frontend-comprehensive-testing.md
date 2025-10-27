# Frontend Comprehensive Testing Command

**Purpose**: Systematic UI component testing across all user roles with edge case validation and OpenAPI compliance

## Command Usage
```bash
/frontend-comprehensive-testing [--role role1,role2] [--components component1,component2] [--skip-backend-check]
```

## Integration with Feature Documentation Agent

**RECOMMENDED: Generate feature documentation BEFORE running comprehensive tests**

**Why Use Feature Documentation:**
- **Faster Testing**: Skip manual component discovery (save 30-60 minutes per feature)
- **Comprehensive Edge Cases**: Field docs already have 25+ edge cases documented
- **Consistent Testing**: All testers use same edge case definitions
- **Better Reporting**: Can compare actual vs. documented behavior
- **Documentation Validation**: Testing verifies documentation accuracy

**Recommended Workflow:**

**Step 1: Generate Feature Documentation** (if not exists)
```bash
/document-features animal-configuration

# Creates:
# - claudedocs/features/animal-configuration/frontend/components.md
# - claudedocs/features/animal-configuration/frontend/fields/*.md (with validation rules + edge cases)
# - claudedocs/features/animal-configuration/testing/test-scenarios.md
# - claudedocs/features/documentation-index.json (master reference)
```

**Step 2: Run Frontend Comprehensive Testing** (with documentation)
```bash
/frontend-comprehensive-testing animal-configuration

# Agent automatically:
# 1. Checks for claudedocs/features/documentation-index.json
# 2. Reads component inventory from docs (skip Phase 2 manual discovery)
# 3. Uses field docs for validation rules and edge cases (Phase 4)
# 4. References test scenarios as checklist (Phase 6)
# 5. Reports actual behavior differences back to documentation
```

**During Testing with Documentation:**
- **Phase 2 (Component Discovery)**: Read `documentation-index.json` instead of manual discovery
- **Phase 4 (Edge Case Testing)**: Use edge case lists from `fields/{field-name}.md`
- **Phase 6 (Reporting)**: Compare actual vs. documented behavior, report mismatches

**After Testing:**
- Update field docs with actual behavior (if differs from documented)
- Report documentation bugs if docs don't match implementation
- Suggest documentation improvements based on testing discoveries

**See:**
- `.claude/commands/document-features.md` - How to generate feature documentation
- `FEATURE-DOCUMENTATION-ADVICE.md` - Integration patterns with testing agent

## Agent Persona
You are a **Senior Frontend QA Engineer** with expertise in:
- Multi-role user journey testing (admin, zookeeper, parent, student, visitor)
- Comprehensive edge case testing for all input types
- OpenAPI specification validation and compliance
- Browser automation with Playwright
- Accessibility testing (WCAG 2.1 AA)
- Cross-browser compatibility validation

## CRITICAL DIRECTIVES

### 🚨 Backend Health Monitoring
**BEFORE starting ANY test execution:**
1. Verify backend is running and healthy
2. Check backend version matches expected version
3. Test authentication endpoint is working
4. If ANY "not implemented" error encountered → **STOP ALL TESTING**
5. If backend version mismatch detected → **STOP ALL TESTING**

### 📋 Component Inventory Maintenance
**MUST maintain complete component inventory:**
- Track ALL UI components in the project
- Map components to user roles (who can access what)
- Document component locations (routes, dialogs, panels)
- Track component states (enabled, disabled, loading, error)
- Update inventory as new components discovered

## 6-Phase Testing Methodology

### Phase 1: Backend Health Validation
**Objective**: Ensure backend is running current version before testing

**Critical Checks**:
```javascript
// 1. Backend reachability
const healthCheck = await fetch(`${BACKEND_URL}/health`);
if (!healthCheck.ok) {
  STOP_ALL_TESTING("Backend not reachable");
}

// 2. Version verification
const versionCheck = await fetch(`${BACKEND_URL}/api/v1/version`);
const backendVersion = await versionCheck.json();
if (backendVersion !== EXPECTED_VERSION) {
  STOP_ALL_TESTING(`Backend version mismatch: ${backendVersion} != ${EXPECTED_VERSION}`);
}

// 3. Authentication endpoint test
const authTest = await fetch(`${BACKEND_URL}/api/v1/auth/login`, {
  method: 'POST',
  body: JSON.stringify({username: 'test@cmz.org', password: 'testpass123'})
});
if (authTest.status === 501 || authTest.status === 404) {
  STOP_ALL_TESTING("Authentication endpoint not implemented or broken");
}
```

**Stopping Criteria**:
- ❌ Backend not reachable → STOP
- ❌ Version mismatch → STOP
- ❌ "Not implemented" error → STOP
- ❌ 501 response → STOP
- ❌ 404 on known endpoint → STOP

### Phase 2: Component Discovery and Inventory
**Objective**: Build complete inventory of ALL UI components

**Discovery Process**:
```javascript
// For each role: admin, zookeeper, parent, student, visitor
for (const role of USER_ROLES) {
  // Login as role
  await loginAs(role);

  // Navigate through all accessible routes
  const routes = await discoverAccessibleRoutes(role);

  // For each route, discover components
  for (const route of routes) {
    await page.goto(route);

    // Discover all interactive elements
    const buttons = await page.locator('button').all();
    const inputs = await page.locator('input').all();
    const selects = await page.locator('select').all();
    const textareas = await page.locator('textarea').all();
    const dialogs = await page.locator('[role="dialog"]').all();

    // Record in component inventory
    componentInventory.add({
      role,
      route,
      componentType,
      locator,
      accessible: true
    });
  }
}
```

**Component Inventory Schema**:
```json
{
  "componentId": "animal-config-temperature-slider",
  "componentType": "slider",
  "accessibleRoles": ["admin", "zookeeper"],
  "route": "/admin/animals",
  "parentComponent": "animal-config-dialog",
  "locator": "input[name='temperature']",
  "openApiSpec": {
    "endpoint": "PATCH /animal_config",
    "field": "temperature",
    "type": "number",
    "minimum": 0.0,
    "maximum": 1.0,
    "required": false
  },
  "testStatus": "pending"
}
```

### Phase 3: OpenAPI Specification Validation
**Objective**: Validate all components have proper OpenAPI validation rules

**Validation Process**:
```javascript
// Read OpenAPI spec
const openApiSpec = await readOpenAPISpec('backend/api/openapi_spec.yaml');

// For each input component in inventory
for (const component of componentInventory.inputs) {
  // Find corresponding OpenAPI field
  const apiField = findOpenAPIField(openApiSpec, component);

  if (!apiField) {
    reportBug({
      severity: 'MEDIUM',
      component: component.componentId,
      issue: 'No OpenAPI specification found for input field',
      recommendation: 'Add validation rules to openapi_spec.yaml'
    });
    continue;
  }

  // Check validation rules exist
  const validationIssues = [];

  if (component.componentType === 'text' || component.componentType === 'textarea') {
    if (!apiField.minLength) {
      validationIssues.push('minLength not defined');
    }
    if (!apiField.maxLength) {
      validationIssues.push('maxLength not defined');
    }
    if (!apiField.pattern && requiresPattern(component)) {
      validationIssues.push('pattern (regex) not defined');
    }
  }

  if (component.componentType === 'number' || component.componentType === 'slider') {
    if (apiField.minimum === undefined) {
      validationIssues.push('minimum not defined');
    }
    if (apiField.maximum === undefined) {
      validationIssues.push('maximum not defined');
    }
  }

  if (validationIssues.length > 0) {
    reportBug({
      severity: 'HIGH',
      component: component.componentId,
      openApiField: apiField.path,
      issues: validationIssues,
      recommendation: 'Add missing validation constraints to OpenAPI spec'
    });
  }
}
```

**Bug Report Categories**:
- **CRITICAL**: No OpenAPI spec exists for input field
- **HIGH**: Missing validation constraints (min/max, length, pattern)
- **MEDIUM**: Validation constraints present but insufficient
- **LOW**: Optional validation enhancements

### Phase 4: Text Input Edge Case Testing
**Objective**: Test ALL text inputs with comprehensive edge cases

**Edge Case Test Matrix**:
```javascript
const TEXT_EDGE_CASES = {
  empty: '',
  singleChar: 'A',
  twoChars: 'Ab',
  exactMinLength: generateString(minLength),
  exactMaxLength: generateString(maxLength),
  exceedMaxLength: generateString(maxLength + 1),

  // Large content
  loremIpsum: LOREM_IPSUM_PARAGRAPH, // ~500 chars
  veryLargeBlock: LOREM_IPSUM_5_PARAGRAPHS, // ~2500 chars

  // Special characters
  specialChars: '!@#$%^&*()_+-={}[]|\\:";\'<>?,./',
  htmlTags: '<script>alert("xss")</script>',
  sqlInjection: '\'; DROP TABLE users; --',
  unicodeEmojis: '🦁🐯🐻🦅🐍',

  // Foreign languages
  chinese: '这是一个测试描述',
  arabic: 'هذا وصف اختباري',
  russian: 'Это тестовое описание',
  japanese: 'これはテストの説明です',
  hebrew: 'זהו תיאור מבחן',

  // Whitespace variations
  leadingWhitespace: '   Leading spaces',
  trailingWhitespace: 'Trailing spaces   ',
  multipleSpaces: 'Multiple    spaces    between',
  tabs: 'Text\twith\ttabs',
  newlines: 'Text\nwith\nnewlines',
  mixedWhitespace: '  \t \n  Mixed  \t \n  ',

  // Boundary cases
  allSpaces: '     ',
  allNewlines: '\n\n\n\n',
  singleNewline: '\n',

  // Common issues
  duplicateContent: 'Same Same Same Same',
  allUppercase: 'ALL UPPERCASE TEXT',
  allLowercase: 'all lowercase text',
  mixedCase: 'MiXeD CaSe TeXt'
};

// Test each text input with all edge cases
for (const component of componentInventory.textInputs) {
  await loginAsRole(component.accessibleRoles[0]);
  await navigateToComponent(component);

  for (const [caseName, testValue] of Object.entries(TEXT_EDGE_CASES)) {
    // Apply test value
    await component.fill(testValue);

    // Attempt to save/submit
    const result = await component.submit();

    // Validate behavior
    if (shouldAccept(testValue, component.openApiSpec)) {
      expect(result.success).toBe(true);
      expect(result.error).toBeUndefined();

      // Verify persistence
      const persisted = await verifyDynamoDBValue(component, testValue);
      expect(persisted).toBe(true);
    } else {
      expect(result.success).toBe(false);
      expect(result.error).toBeDefined();
      expect(result.error).toContain('validation');
    }

    // Record result
    testResults.record({
      component: component.componentId,
      testCase: caseName,
      input: testValue,
      expected: shouldAccept(testValue, component.openApiSpec),
      actual: result.success,
      passed: result.success === shouldAccept(testValue, component.openApiSpec)
    });
  }
}
```

### Phase 5: Control and Button Testing
**Objective**: Test ALL controls and buttons for expected behavior

**Control Testing**:
```javascript
// Toggle Controls (checkboxes, switches)
for (const toggle of componentInventory.toggles) {
  await navigateToComponent(toggle);

  // Test both states
  for (const state of [true, false]) {
    await toggle.click();
    expect(await toggle.isChecked()).toBe(state);

    // Verify state persists after save
    await saveChanges();
    await reloadPage();
    expect(await toggle.isChecked()).toBe(state);
  }
}

// Slider Controls
for (const slider of componentInventory.sliders) {
  await navigateToComponent(slider);

  const min = slider.openApiSpec.minimum;
  const max = slider.openApiSpec.maximum;

  // Test boundary values
  for (const value of [min, max, (min + max) / 2]) {
    await slider.fill(value.toString());
    expect(await slider.inputValue()).toBe(value.toString());

    // Verify persistence
    await saveChanges();
    const persisted = await verifyDynamoDBValue(slider, value);
    expect(persisted).toBe(true);
  }

  // Test out-of-range values
  await slider.fill((min - 1).toString());
  const result = await saveChanges();
  expect(result.error).toBeDefined();
}

// Select/Dropdown Controls
for (const select of componentInventory.selects) {
  await navigateToComponent(select);

  // Get all options
  const options = await select.locator('option').all();

  // Test each option
  for (const option of options) {
    const value = await option.getAttribute('value');
    await select.selectOption(value);
    expect(await select.inputValue()).toBe(value);

    // Verify persistence
    await saveChanges();
    const persisted = await verifyDynamoDBValue(select, value);
    expect(persisted).toBe(true);
  }
}

// Button Testing
for (const button of componentInventory.buttons) {
  await navigateToComponent(button);

  // Check enabled state
  const enabled = await button.isEnabled();

  if (enabled) {
    // Click button
    await button.click();

    // Verify expected behavior
    if (button.expectedBehavior === 'dialog') {
      expect(await page.locator('[role="dialog"]').isVisible()).toBe(true);
    } else if (button.expectedBehavior === 'navigation') {
      expect(page.url()).toContain(button.expectedRoute);
    } else if (button.expectedBehavior === 'save') {
      expect(await page.locator('.success-message').isVisible()).toBe(true);
    }

    // Check for errors
    const errorVisible = await page.locator('.error-message').isVisible();
    if (errorVisible) {
      const errorText = await page.locator('.error-message').textContent();
      if (errorText.includes('not implemented')) {
        STOP_ALL_TESTING('Button triggered "not implemented" error');
      }
    }
  }
}
```

### Phase 6: Multi-Role Testing and Reporting
**Objective**: Verify role-based access control and generate comprehensive report

**Role-Based Testing**:
```javascript
const ROLE_TEST_MATRIX = {
  admin: {
    shouldAccess: ['dashboard', 'animals', 'families', 'users', 'analytics', 'settings'],
    shouldNotAccess: []
  },
  zookeeper: {
    shouldAccess: ['dashboard', 'animals'],
    shouldNotAccess: ['families', 'users', 'analytics']
  },
  parent: {
    shouldAccess: ['dashboard', 'chat', 'family-management'],
    shouldNotAccess: ['animals', 'users', 'analytics']
  },
  student: {
    shouldAccess: ['dashboard', 'chat'],
    shouldNotAccess: ['animals', 'families', 'users', 'analytics', 'settings']
  },
  visitor: {
    shouldAccess: ['home', 'chat-limited'],
    shouldNotAccess: ['dashboard', 'animals', 'families', 'users']
  }
};

// Test role-based access
for (const [role, access] of Object.entries(ROLE_TEST_MATRIX)) {
  await loginAsRole(role);

  // Verify allowed access
  for (const route of access.shouldAccess) {
    await page.goto(`${FRONTEND_URL}/${route}`);
    expect(page.url()).toContain(route);
    expect(await page.locator('.error').isVisible()).toBe(false);
  }

  // Verify denied access
  for (const route of access.shouldNotAccess) {
    await page.goto(`${FRONTEND_URL}/${route}`);
    expect(page.url()).not.toContain(route); // Should redirect
    // OR
    expect(await page.locator('.unauthorized').isVisible()).toBe(true);
  }
}
```

**Report Generation**:
```json
{
  "frontend_comprehensive_test_report": {
    "timestamp": "ISO-8601",
    "backend_health": {
      "status": "healthy|unhealthy",
      "version": "1.2.3",
      "versionMatch": true,
      "authenticationWorking": true
    },
    "component_inventory": {
      "totalComponents": 150,
      "byType": {
        "button": 45,
        "textInput": 30,
        "textarea": 8,
        "select": 12,
        "checkbox": 20,
        "slider": 10,
        "dialog": 15,
        "other": 10
      },
      "byRole": {
        "admin": 120,
        "zookeeper": 50,
        "parent": 40,
        "student": 30,
        "visitor": 10
      }
    },
    "openapi_validation": {
      "totalFieldsChecked": 80,
      "bugsFound": [
        {
          "severity": "HIGH",
          "component": "animal-description",
          "field": "description",
          "issue": "maxLength not defined",
          "openApiPath": "/animal.description"
        }
      ]
    },
    "edge_case_testing": {
      "textInputsTested": 30,
      "edgeCasesPerInput": 25,
      "totalTests": 750,
      "passed": 720,
      "failed": 30,
      "failureReasons": {
        "validation_too_loose": 15,
        "validation_too_strict": 10,
        "unicode_not_supported": 5
      }
    },
    "control_testing": {
      "togglesTested": 20,
      "slidersTested": 10,
      "selectsTested": 12,
      "buttonsTested": 45,
      "allWorking": true,
      "issues": []
    },
    "role_based_access": {
      "rolesTested": 5,
      "accessTestsPassed": 48,
      "accessTestsFailed": 2,
      "unauthorizedAccessAttempts": 0
    },
    "cross_browser_results": {
      "chromium": "100% pass",
      "firefox": "98% pass",
      "webkit": "95% pass"
    },
    "accessibility_audit": {
      "wcag_aa_compliance": "92%",
      "issues": [
        {
          "severity": "MEDIUM",
          "component": "animal-config-dialog",
          "issue": "Missing aria-label on close button"
        }
      ]
    },
    "recommendations": [
      "Add maxLength validation to animal description field",
      "Improve Unicode character support in text inputs",
      "Add aria-labels to dialog close buttons for accessibility"
    ]
  }
}
```

## Component Test Specifications

### Text Input Testing Template
```javascript
async function testTextInput(component, openApiSpec) {
  const tests = {
    // Basic validation
    'empty': { value: '', shouldAccept: !openApiSpec.required },
    'valid_short': { value: 'Test', shouldAccept: true },
    'valid_long': { value: 'A'.repeat(openApiSpec.maxLength || 100), shouldAccept: true },
    'too_long': { value: 'A'.repeat((openApiSpec.maxLength || 100) + 1), shouldAccept: false },

    // Edge cases
    'lorem_ipsum': { value: LOREM_IPSUM, shouldAccept: true },
    'single_char': { value: 'A', shouldAccept: openApiSpec.minLength <= 1 },
    'unicode_emoji': { value: '🦁 Lion', shouldAccept: true },
    'chinese': { value: '这是测试', shouldAccept: true },
    'arabic': { value: 'مرحبا', shouldAccept: true },

    // Security
    'html_tags': { value: '<script>alert(1)</script>', shouldAccept: false },
    'sql_injection': { value: "'; DROP TABLE--", shouldAccept: false },

    // Whitespace
    'leading_spaces': { value: '   Test', shouldAccept: true },
    'trailing_spaces': { value: 'Test   ', shouldAccept: true },
    'only_spaces': { value: '     ', shouldAccept: false },
    'newlines': { value: 'Line1\nLine2', shouldAccept: true }
  };

  for (const [name, test] of Object.entries(tests)) {
    await component.fill(test.value);
    const result = await component.submit();

    expect(result.success).toBe(test.shouldAccept);

    if (test.shouldAccept) {
      // Verify DynamoDB persistence
      const persisted = await verifyDynamoDB(component, test.value);
      expect(persisted).toBe(true);
    }
  }
}
```

### Slider/Number Input Testing Template
```javascript
async function testSliderInput(component, openApiSpec) {
  const min = openApiSpec.minimum;
  const max = openApiSpec.maximum;

  const tests = {
    'at_minimum': { value: min, shouldAccept: true },
    'at_maximum': { value: max, shouldAccept: true },
    'at_midpoint': { value: (min + max) / 2, shouldAccept: true },
    'below_minimum': { value: min - 0.1, shouldAccept: false },
    'above_maximum': { value: max + 0.1, shouldAccept: false },
    'zero': { value: 0, shouldAccept: min <= 0 && max >= 0 },
    'negative': { value: -1, shouldAccept: min < 0 },
    'decimal': { value: min + 0.5, shouldAccept: true }
  };

  for (const [name, test] of Object.entries(tests)) {
    await component.fill(test.value.toString());
    const result = await component.submit();

    expect(result.success).toBe(test.shouldAccept);

    if (test.shouldAccept) {
      const persisted = await verifyDynamoDB(component, test.value);
      expect(persisted).toBe(true);
    }
  }
}
```

## Error Handling and Stop Conditions

### Immediate Stop Conditions
```javascript
const STOP_CONDITIONS = {
  'not_implemented': /not implemented/i,
  'backend_down': /ECONNREFUSED|ETIMEDOUT|network error/i,
  'version_mismatch': (actual, expected) => actual !== expected,
  'auth_broken': (status) => status === 501 || status === 404,
  'handler_missing': /do some magic/i
};

function checkStopConditions(response, expectedVersion) {
  // Check response text for "not implemented"
  if (STOP_CONDITIONS.not_implemented.test(response.text)) {
    stopAllTesting({
      reason: 'NOT_IMPLEMENTED_ERROR',
      details: response.text,
      recommendation: 'Check if OpenAPI regeneration broke handlers'
    });
  }

  // Check backend version
  if (response.version && STOP_CONDITIONS.version_mismatch(response.version, expectedVersion)) {
    stopAllTesting({
      reason: 'VERSION_MISMATCH',
      expected: expectedVersion,
      actual: response.version,
      recommendation: 'Rebuild and restart backend'
    });
  }

  // Check for broken authentication
  if (STOP_CONDITIONS.auth_broken(response.status)) {
    stopAllTesting({
      reason: 'AUTHENTICATION_BROKEN',
      status: response.status,
      recommendation: 'Check auth handler in impl/auth.py'
    });
  }
}
```

## Usage Examples

### Full Frontend Testing Suite
```bash
/frontend-comprehensive-testing
# Runs complete test suite across all roles and components
```

### Specific Role Testing
```bash
/frontend-comprehensive-testing --role admin,parent
# Tests only admin and parent roles
```

### Specific Component Testing
```bash
/frontend-comprehensive-testing --components animal-config,family-dialog
# Tests only specified components
```

### Skip Backend Health Check (Use with Caution)
```bash
/frontend-comprehensive-testing --skip-backend-check
# Skips backend validation (NOT RECOMMENDED except for offline UI testing)
```

## Success Criteria

**Overall Success**:
- ≥98% of components working correctly
- Zero "not implemented" errors encountered
- Backend version matches expected version
- All text inputs accept valid edge cases
- All text inputs reject invalid inputs
- All controls function correctly
- Role-based access properly enforced

**OpenAPI Validation**:
- 100% of input fields have corresponding OpenAPI spec
- ≥90% of fields have complete validation constraints
- All validation constraint gaps reported as bugs

**Edge Case Testing**:
- All text inputs tested with ≥20 edge cases
- Unicode support validated
- Security inputs (XSS, SQL injection) properly rejected
- Whitespace handling correct

**Cross-Browser**:
- ≥95% pass rate on Chromium, Firefox, WebKit
- Critical user journeys work on all browsers

## Integration

**With Test Orchestrator**:
```python
# Test Orchestrator delegates to Frontend Comprehensive Testing
Task(
    subagent_type="general-purpose",
    description="Frontend comprehensive testing",
    prompt="""Frontend QA Engineer - test ALL UI components systematically.

    See .claude/commands/frontend-comprehensive-testing.md for methodology.
    """
)
```

**With Test Generation**:
- Frontend testing identifies missing test cases
- Test generation creates additional edge case tests
- Continuous improvement loop

**With Teams Reporting**:
- Detailed test results sent to Teams
- OpenAPI validation bugs reported
- Recommendations for improvements
