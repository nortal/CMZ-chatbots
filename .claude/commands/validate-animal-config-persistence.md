# Validate Animal Config Persistence

**Purpose**: Focused end-to-end validation of Animal Configuration data persistence, ensuring that changes made through the Animal Management UI correctly save to DynamoDB and can be retrieved accurately.

## Context
This prompt provides targeted validation for the Animal Config endpoint (`PATCH /animal_config`), testing the complete data flow from UI form submission through API processing to DynamoDB storage. Unlike full system validation, this focuses specifically on animal configuration updates including voice settings, guardrails, and personality traits.

**Problem Solved**: Detecting data loss, transformation errors, or persistence failures specific to animal configuration updates.

## Sequential Reasoning Approach

Use MCP Sequential Thinking to systematically validate the Animal Config persistence workflow:

### Phase 1: Pre-Test Setup & Baseline
**Use Sequential Reasoning to:**
1. **Service Verification**: Confirm backend API (port 8080) is operational
2. **Target Selection**: Identify specific animal ID for testing (e.g., leo_001)
3. **Baseline Capture**: Document current animal config state in DynamoDB
4. **Test Data Design**: Define comprehensive test updates (voice, guardrails, personality)
5. **Success Criteria**: Establish expected outcomes and validation rules

**Key Questions for Sequential Analysis:**
- Is the backend API responding on port 8080?
- What is the current configuration for the target animal?
- Which configuration fields need testing (required vs optional)?
- What data transformations are expected between UI and database?
- What are the validation rules for each field type?

### Phase 2: API Direct Testing
**Implementation Order (Follow Exactly):**

#### Step 1: Capture Current State
```bash
# Query current animal configuration
aws dynamodb get-item \
  --table-name quest-dev-animal \
  --key '{"animalId": {"S": "leo_001"}}' \
  --region us-west-2 \
  --output json > baseline-animal-config.json
```

#### Step 2: Prepare Test Payload
```json
{
  "voice": {
    "provider": "elevenlabs",
    "voiceId": "test_voice_${timestamp}",
    "modelId": "eleven_turbo_v2",
    "stability": 0.5,
    "similarityBoost": 0.75,
    "style": 0.0,
    "useSpeakerBoost": true
  },
  "guardrails": {
    "contentFilters": ["educational", "age-appropriate"],
    "responseMaxLength": 500,
    "topicRestrictions": ["violence", "inappropriate"],
    "safeMode": true
  },
  "personality": {
    "traits": ["friendly", "wise", "educational"],
    "backstory": "King of the savanna with wisdom to share",
    "interests": ["wildlife", "conservation", "leadership"],
    "communicationStyle": "warm and engaging"
  }
}
```

#### Step 3: Execute API Update
```bash
# Send PATCH request to update animal config
curl -X PATCH \
  -H "Content-Type: application/json" \
  -d @test-payload.json \
  "http://localhost:8080/animal_config?animalId=leo_001"
```

#### Step 4: Verify API Response
- Check HTTP status code (should be 200)
- Validate response body contains updated fields
- Verify audit fields (modified timestamp) are updated
- Confirm no unexpected field transformations

### Phase 3: DynamoDB Verification
**Verification Order (Systematic):**

#### Step 1: Query Updated State
```bash
# Get updated configuration from DynamoDB
aws dynamodb get-item \
  --table-name quest-dev-animal \
  --key '{"animalId": {"S": "leo_001"}}' \
  --region us-west-2 \
  --output json > updated-animal-config.json
```

#### Step 2: Field-by-Field Comparison
```python
def validate_persistence(baseline, updated, test_data):
    """
    Compare each field to ensure correct persistence
    """
    validations = {
        'voice': validate_voice_config(updated, test_data),
        'guardrails': validate_guardrails(updated, test_data),
        'personality': validate_personality(updated, test_data),
        'audit': validate_audit_fields(baseline, updated)
    }
    return validations
```

#### Step 3: Type Validation
- Verify DynamoDB type conversions (Decimal, String, Map, List)
- Check nested object structure preservation
- Validate array/list handling
- Confirm boolean field accuracy

#### Step 4: Business Rule Validation
- Ensure required fields are present
- Validate field constraints (max lengths, allowed values)
- Check default value application
- Verify soft delete handling

### Phase 4: UI Integration Testing with Visual Feedback
**Browser Automation with Playwright MCP (Visible to User):**

#### Step 1: Initialize Browser with Visible Window
```javascript
// Launch browser in non-headless mode so user can see interactions
const browser = await playwright.chromium.launch({
  headless: false,  // Show browser window
  slowMo: 500,      // Slow down actions for visibility
  devtools: true    // Open DevTools for debugging
});

// Set viewport for consistent display
await page.setViewportSize({ width: 1280, height: 720 });
```

#### Step 2: Navigate and Take Screenshot
```javascript
// Navigate to Animal Config page
console.log('🔍 Navigating to Animal Configuration page...');
await page.goto(`${FRONTEND_URL}/animals/leo_001/config`);

// Take screenshot of initial state
await page.screenshot({
  path: 'animal-config-initial.png',
  fullPage: true
});
console.log('📸 Screenshot saved: animal-config-initial.png');

// Highlight the form area
await page.evaluate(() => {
  const form = document.querySelector('form');
  if (form) {
    form.style.border = '3px solid #00ff00';
    form.style.boxShadow = '0 0 20px rgba(0,255,0,0.5)';
  }
});
```

#### Step 3: Fill Form with Visual Feedback
```javascript
// Voice Configuration with visual highlighting
console.log('🎤 Configuring voice settings...');
const voiceSelect = await page.locator('select[name="voice"]');
await voiceSelect.highlight();  // Visual highlight
await voiceSelect.selectOption('nova');
await page.waitForTimeout(1000);  // Pause for visibility

// Take screenshot after voice selection
await page.screenshot({
  path: 'animal-config-voice-selected.png',
  clip: { x: 0, y: 0, width: 1280, height: 400 }
});

// Personality Configuration with typing animation
console.log('🎭 Updating personality...');
const personalityField = await page.locator('textarea[name="personality"]');
await personalityField.highlight();
await personalityField.clear();
await personalityField.type('Majestic king of the savanna with wisdom to share', {
  delay: 50  // Type slowly for visibility
});

// Guardrails Configuration with visual feedback
console.log('🛡️ Setting guardrails...');
const guardrailsSection = await page.locator('[data-testid="guardrails-section"]');
await page.evaluate(() => {
  const section = document.querySelector('[data-testid="guardrails-section"]');
  if (section) {
    section.scrollIntoView({ behavior: 'smooth', block: 'center' });
    section.style.backgroundColor = '#ffff0030';
  }
});

// Take screenshot of filled form
await page.screenshot({
  path: 'animal-config-filled.png',
  fullPage: true
});
console.log('📸 Screenshot saved: animal-config-filled.png');
```

#### Step 4: Submit with Network Monitoring
```javascript
// Set up network monitoring with visual indicators
console.log('📡 Monitoring network requests...');
page.on('request', request => {
  if (request.url().includes('/animal_config')) {
    console.log(`🔹 REQUEST: ${request.method()} ${request.url()}`);
    console.log(`🔹 Payload: ${request.postData()}`);
  }
});

page.on('response', response => {
  if (response.url().includes('/animal_config')) {
    console.log(`🔸 RESPONSE: ${response.status()} ${response.url()}`);
  }
});

// Click save button with visual feedback
console.log('💾 Clicking Save button...');
const saveButton = await page.locator('button:has-text("Save")');
await saveButton.highlight();
await page.waitForTimeout(1000);  // Pause before click

// Capture the save action
const [response] = await Promise.all([
  page.waitForResponse(resp => resp.url().includes('/animal_config')),
  saveButton.click()
]);

// Show success/error state
if (response.status() === 200) {
  console.log('✅ Save successful!');
  // Take screenshot of success state
  await page.screenshot({
    path: 'animal-config-success.png',
    fullPage: true
  });
} else {
  console.log(`❌ Save failed with status: ${response.status()}`);
  // Take screenshot of error state
  await page.screenshot({
    path: 'animal-config-error.png',
    fullPage: true
  });
}
```

#### Step 5: Display Visual Results
```javascript
// Create HTML report with screenshots
const reportHTML = `
<!DOCTYPE html>
<html>
<head>
  <title>Animal Config Validation Report</title>
  <style>
    body { font-family: Arial, sans-serif; padding: 20px; }
    .screenshot {
      border: 1px solid #ccc;
      margin: 20px 0;
      box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .screenshot img { width: 100%; max-width: 800px; }
    .success { color: green; font-weight: bold; }
    .error { color: red; font-weight: bold; }
  </style>
</head>
<body>
  <h1>Animal Config Persistence Validation</h1>
  <h2>Visual Test Results</h2>

  <div class="screenshot">
    <h3>1. Initial Page Load</h3>
    <img src="animal-config-initial.png" alt="Initial state">
  </div>

  <div class="screenshot">
    <h3>2. Form Filled</h3>
    <img src="animal-config-filled.png" alt="Filled form">
  </div>

  <div class="screenshot">
    <h3>3. Final Result</h3>
    <img src="${response.status() === 200 ? 'animal-config-success.png' : 'animal-config-error.png'}"
         alt="Final result">
    <p class="${response.status() === 200 ? 'success' : 'error'}">
      Status: ${response.status()}
    </p>
  </div>
</body>
</html>
`;

// Save and open report
await fs.writeFile('validation-report.html', reportHTML);
console.log('📊 Opening visual report...');
await page.goto(`file://${process.cwd()}/validation-report.html`);
```

### Phase 5: Comprehensive Report Generation
**Analysis Framework:**

#### Step 1: Data Integrity Report
```yaml
persistence_validation:
  test_id: "animal_config_${timestamp}"
  target_animal: "leo_001"

  field_validation:
    voice:
      fields_tested: 7
      fields_persisted: 7
      success_rate: 100%

    guardrails:
      fields_tested: 4
      fields_persisted: 4
      success_rate: 100%

    personality:
      fields_tested: 4
      fields_persisted: 4
      success_rate: 100%

  data_transformations:
    - field: "voice.stability"
      ui_type: "number"
      db_type: "Decimal"
      transformation: "correct"

  discrepancies: []

  overall_status: "PASS"
```

#### Step 2: Performance Metrics
- API response time
- Database write latency
- End-to-end save duration
- Data size analysis

#### Step 3: Recommendations
- Identify any data handling improvements
- Suggest validation enhancements
- Document edge cases for future testing

## Implementation Details

### Visual Browser Automation with Playwright MCP

#### Browser Visibility Configuration
```yaml
playwright_settings:
  headless: false            # Show browser window to user
  slowMo: 500               # Milliseconds between actions for visibility
  devtools: true            # Open DevTools for debugging
  viewport:
    width: 1280
    height: 720
  recordVideo:
    dir: './test-videos'    # Record session for review
    size:
      width: 1280
      height: 720
```

#### Real-Time Visual Feedback Methods
```javascript
// 1. Highlight Elements Before Interaction
await element.highlight();                    // Built-in Playwright highlight
await element.scrollIntoViewIfNeeded();      // Ensure visible
await page.waitForTimeout(500);              // Pause for user to see

// 2. Add Visual Markers
await page.evaluate((selector) => {
  const el = document.querySelector(selector);
  el.style.border = '3px solid red';
  el.style.backgroundColor = 'yellow';
  el.style.transition = 'all 0.3s ease';
}, selector);

// 3. Console Logging with Emojis for Clarity
console.log('🎯 Targeting element:', selector);
console.log('✏️ Entering text:', value);
console.log('🖱️ Clicking button:', buttonText);

// 4. Take Progressive Screenshots
await page.screenshot({ path: `step-${stepNumber}.png` });

// 5. Show Toast Notifications in Page
await page.evaluate((message) => {
  const toast = document.createElement('div');
  toast.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: #4CAF50;
    color: white;
    padding: 16px;
    border-radius: 4px;
    z-index: 10000;
    font-family: Arial;
    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
  `;
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 3000);
}, 'Test automation in progress...');
```

#### Interactive Debugging Features
```javascript
// Pause for user inspection
await page.pause();  // Opens Playwright Inspector

// Wait for user confirmation
await page.evaluate(() => {
  return new Promise(resolve => {
    if (confirm('Continue with test?')) {
      resolve();
    }
  });
});

// Step-by-step mode with user control
const stepMode = true;
if (stepMode) {
  console.log('Press Enter to continue...');
  await page.keyboard.press('Enter');
}
```

### Test Scenarios
```yaml
standard_update:
  description: "Update all configuration fields"
  fields: ["voice", "guardrails", "personality"]

partial_update:
  description: "Update single field only"
  fields: ["voice"]

edge_cases:
  empty_values:
    description: "Test with empty/null values"

  special_characters:
    description: "Unicode and special characters in text fields"

  large_payloads:
    description: "Maximum size configurations"

  concurrent_updates:
    description: "Simultaneous update attempts"
```

### Validation Script
```bash
#!/bin/bash
# validate-animal-config-persistence.sh

ANIMAL_ID="${1:-leo_001}"
BACKEND_URL="${BACKEND_URL:-http://localhost:8080}"

echo "🔍 Validating Animal Config Persistence for: $ANIMAL_ID"

# Step 1: Capture baseline
echo "📊 Capturing baseline configuration..."
aws dynamodb get-item \
  --table-name quest-dev-animal \
  --key "{\"animalId\": {\"S\": \"$ANIMAL_ID\"}}" \
  --region us-west-2 > baseline.json

# Step 2: Update via API
echo "🔄 Updating configuration via API..."
curl -X PATCH \
  -H "Content-Type: application/json" \
  -d @test-payload.json \
  "$BACKEND_URL/animal_config?animalId=$ANIMAL_ID" > api-response.json

# Step 3: Verify in DynamoDB
echo "✅ Verifying persistence in DynamoDB..."
aws dynamodb get-item \
  --table-name quest-dev-animal \
  --key "{\"animalId\": {\"S\": \"$ANIMAL_ID\"}}" \
  --region us-west-2 > updated.json

# Step 4: Compare and report
echo "📈 Generating validation report..."
python3 validate_animal_config.py baseline.json updated.json test-payload.json
```

## Integration Points

### CMZ Project Structure
- **Backend API**: `/animal_config` endpoint in `openapi_spec.yaml`
- **Implementation**: `backend/api/src/main/python/openapi_server/impl/animals.py`
- **DynamoDB Table**: `quest-dev-animal`
- **Frontend**: `frontend/src/pages/AnimalConfig.tsx`

### Existing Infrastructure
- Uses established DynamoDB utilities in `impl/utils/dynamo.py`
- Follows CMZ error handling patterns
- Integrates with audit trail system
- Respects soft delete mechanisms

## Quality Gates

### Pre-Validation Checklist
- [ ] Backend API is running on port 8080
- [ ] AWS credentials are configured
- [ ] Target animal exists in DynamoDB
- [ ] Test payload is valid JSON
- [ ] Python validation script is available

### Success Criteria
- [ ] All test fields persist correctly to DynamoDB
- [ ] Data types are properly converted
- [ ] Nested objects maintain structure
- [ ] Audit fields are updated appropriately
- [ ] API returns success status
- [ ] No data loss or corruption

### Failure Indicators
- HTTP status codes other than 200
- Missing fields in database after update
- Type conversion errors
- Validation constraint violations
- Timeout or connection errors

## Error Handling

### Common Issues
1. **API Not Responding**: Check if backend is running with `make run-api`
2. **DynamoDB Access**: Verify AWS credentials and region
3. **Data Type Mismatches**: Review field type definitions
4. **Validation Failures**: Check field constraints in OpenAPI spec

### Troubleshooting Steps
```bash
# Check API health
curl http://localhost:8080/

# Verify DynamoDB access
aws dynamodb list-tables --region us-west-2

# Test animal exists
aws dynamodb get-item \
  --table-name quest-dev-animal \
  --key '{"animalId": {"S": "leo_001"}}' \
  --region us-west-2
```

## Playwright MCP Integration for Visible UI Testing

### Using Playwright MCP Commands
When implementing this validation with Claude Code, use the Playwright MCP server for browser automation:

```javascript
// Initialize browser with visibility
mcp_playwright_browser_navigate({ url: 'http://localhost:3001' });

// Take screenshot to show current state
mcp_playwright_browser_take_screenshot({
  filename: 'animal-config-initial.png',
  fullPage: true
});

// Get page snapshot for element selection
const snapshot = mcp_playwright_browser_snapshot();

// Click on animal to configure
mcp_playwright_browser_click({
  element: 'Leo the Lion configuration button',
  ref: snapshot.elements.find(e => e.text.includes('Leo'))
});

// Fill in voice configuration
mcp_playwright_browser_type({
  element: 'Voice selection dropdown',
  ref: 'select[name="voice"]',
  text: 'nova'
});

// Type personality with slow typing for visibility
mcp_playwright_browser_type({
  element: 'Personality text area',
  ref: 'textarea[name="personality"]',
  text: 'Majestic king of the savanna',
  slowly: true  // Types one character at a time
});

// Submit form
mcp_playwright_browser_click({
  element: 'Save configuration button',
  ref: 'button[type="submit"]'
});

// Capture final state
mcp_playwright_browser_take_screenshot({
  filename: 'animal-config-saved.png',
  fullPage: true
});
```

### Visual Validation Flow
1. **Browser Launch**: Non-headless mode shows browser window
2. **Navigation**: User sees page loading
3. **Form Interaction**: Each field update is visible
4. **Network Activity**: Console shows API calls
5. **Screenshots**: Captured at each major step
6. **Results**: Visual report opens automatically

### Console Output During Execution
```
🚀 Starting Animal Config Validation
📱 Opening browser window (visible mode)
🔍 Navigating to http://localhost:3001/animals/leo_001/config
📸 Screenshot: animal-config-initial.png
🎤 Setting voice to: nova
✏️ Updating personality field
🛡️ Configuring guardrails
📸 Screenshot: animal-config-filled.png
💾 Saving configuration...
📡 API Request: PATCH /animal_config?animalId=leo_001
✅ Response: 200 OK
📸 Screenshot: animal-config-success.png
📊 Opening visual report in browser
```

## Usage Examples

### Quick Validation
```bash
# Default test with leo_001
./validate-animal-config-persistence.sh

# Test specific animal
./validate-animal-config-persistence.sh maya_003

# Custom backend URL
BACKEND_URL=http://localhost:9000 ./validate-animal-config-persistence.sh
```

### Comprehensive Testing
```bash
# Run all test scenarios
for scenario in standard partial edge_cases; do
  ./validate-animal-config-persistence.sh --scenario $scenario
done
```

### CI/CD Integration
```yaml
test:
  stage: integration
  script:
    - make run-api &
    - sleep 5
    - ./validate-animal-config-persistence.sh
    - cat validation-report.json
```

## References
- `VALIDATE-ANIMAL-CONFIG-PERSISTENCE-ADVICE.md` - Best practices and lessons learned
- `backend/api/openapi_spec.yaml` - API specification
- `frontend/src/services/api.ts` - Frontend API integration
- `impl/animals.py` - Backend implementation