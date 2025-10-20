# /validate-animal-config-fields

Performs comprehensive end-to-end testing of Animal Management configuration fields (Animal Name, Scientific Name, Temperature) with full visibility including admin authentication, DynamoDB validation, UI interaction testing, and error monitoring throughout the entire process.

## Context

This solution provides systematic field-level validation for the Animal Configuration interface, combining UI automation with database persistence verification. Every step is designed to be user-visible through screenshots, console outputs, and real-time validation feedback.

## Sequential Reasoning Approach

Use MCP Sequential Thinking to systematically validate animal configuration field modifications:

### Phase 1: Pre-Test Setup & System Health Validation
**Use Sequential Reasoning to:**
1. **System Health Assessment**: Verify frontend, backend, and database connectivity following ANY-PRE-TEST-ADVICE.md
2. **Baseline Capture**: Document initial system state and take reference screenshots
3. **Test Environment Preparation**: Ensure all required services are running and accessible
4. **Target Animal Selection**: Choose specific animal for testing (preferably with existing configuration)

**Key Questions for Sequential Analysis:**
- Are all system components (frontend, backend, DynamoDB) accessible and healthy?
- Which animal should be selected for comprehensive field testing?
- What are the current field values that will be modified during testing?
- Are there any existing error conditions that could affect testing?

### Phase 2: Authentication & Initial State Documentation
**Implementation Order (Follow Exactly):**

#### Step 1: Admin Authentication with Visual Confirmation
```javascript
// Navigate to login page and capture screenshot
await page.goto('http://localhost:3001/login');
await page.screenshot({ path: 'animal-config-fields-01-login.png', fullPage: true });

// Authenticate as admin with credentials from ANY-PRE-TEST-ADVICE.md
await page.fill('[data-testid="email-input"]', 'admin@cmz.org');
await page.fill('[data-testid="password-input"]', 'admin123');
await page.click('[data-testid="login-button"]');
await page.screenshot({ path: 'animal-config-fields-02-post-login.png', fullPage: true });
```

#### Step 2: Navigate to Animal Management and Capture Initial UI State
```javascript
// Navigate to Animal Management
await page.goto('http://localhost:3001/animals/config');
await page.screenshot({ path: 'animal-config-fields-03-animal-list.png', fullPage: true });

// Select target animal and open configuration
const targetAnimalId = 'bella_002'; // Bella the Bear
await page.click(`[data-animal-id="${targetAnimalId}"] .configure-button`);
await page.screenshot({ path: 'animal-config-fields-04-config-modal-initial.png', fullPage: true });
```

#### Step 3: Capture Initial DynamoDB State
```bash
# Query current animal configuration from DynamoDB
echo "🔍 INITIAL DYNAMODB STATE:"
aws dynamodb get-item \
  --table-name quest-dev-animal \
  --key '{"animalId":{"S":"bella_002"}}' \
  --region us-west-2 \
  --profile cmz \
  --output json > initial-animal-state.json

# Display key fields for comparison
echo "📋 Current Animal Name: $(jq -r '.Item.name.S // "null"' initial-animal-state.json)"
echo "📋 Current Species: $(jq -r '.Item.species.S // "null"' initial-animal-state.json)"
echo "📋 Current Temperature: $(jq -r '.Item.configuration.M.temperature.N // "null"' initial-animal-state.json)"
echo "📋 Last Modified: $(jq -r '.Item.modified.M.at.S // "null"' initial-animal-state.json)"
```

### Phase 3: Field-by-Field Testing with Immediate Validation
**Implementation Order (Test Each Field Individually):**

#### Step 1: Animal Name Field Testing
```javascript
// Locate and modify Animal Name field
const currentAnimalName = await page.inputValue('#animal-name-input');
console.log(`📝 Current Animal Name in UI: ${currentAnimalName}`);

const newAnimalName = `${currentAnimalName} - Updated ${new Date().toISOString()}`;
await page.fill('#animal-name-input', newAnimalName);
await page.screenshot({ path: 'animal-config-fields-05-name-modified.png', fullPage: true });

// Save changes and capture result
await page.click('.save-configuration-button');
await page.waitForSelector('.success-message, .error-message', { timeout: 10000 });
await page.screenshot({ path: 'animal-config-fields-06-name-saved.png', fullPage: true });
```

**Immediate DynamoDB Validation:**
```bash
echo "🔍 VALIDATING ANIMAL NAME CHANGE IN DYNAMODB:"
aws dynamodb get-item \
  --table-name quest-dev-animal \
  --key '{"animalId":{"S":"bella_002"}}' \
  --region us-west-2 \
  --profile cmz \
  --query 'Item.{Name:name.S,Modified:modified.M.at.S}' \
  --output table

echo "✅ Animal Name change validation complete"
```

#### Step 2: Scientific Name (Species) Field Testing
```javascript
// Test Species field modification
const currentSpecies = await page.inputValue('#animal-species-input');
console.log(`📝 Current Species in UI: ${currentSpecies}`);

const newSpecies = currentSpecies.includes('Updated') ?
  currentSpecies.replace(/ - Updated.*/, '') :
  `${currentSpecies} - Updated ${new Date().toISOString()}`;

await page.fill('#animal-species-input', newSpecies);
await page.screenshot({ path: 'animal-config-fields-07-species-modified.png', fullPage: true });

// Save and capture
await page.click('.save-configuration-button');
await page.waitForSelector('.success-message, .error-message', { timeout: 10000 });
await page.screenshot({ path: 'animal-config-fields-08-species-saved.png', fullPage: true });
```

**Immediate DynamoDB Validation:**
```bash
echo "🔍 VALIDATING SPECIES CHANGE IN DYNAMODB:"
aws dynamodb get-item \
  --table-name quest-dev-animal \
  --key '{"animalId":{"S":"bella_002"}}' \
  --region us-west-2 \
  --profile cmz \
  --query 'Item.{Species:species.S,Modified:modified.M.at.S}' \
  --output table

echo "✅ Species change validation complete"
```

#### Step 3: Temperature Control Testing
```javascript
// Navigate to Settings tab for Temperature control
await page.click('#settings-tab');
await page.screenshot({ path: 'animal-config-fields-09-settings-tab.png', fullPage: true });

// Get current temperature value
const currentTemp = await page.inputValue('#temperature-slider, #temperature-input');
console.log(`🌡️ Current Temperature in UI: ${currentTemp}`);

// Modify temperature (ensure it's a multiple of 0.1 as per schema requirements)
const newTemp = currentTemp === '0.5' ? '0.7' : '0.5';
await page.fill('#temperature-input', newTemp);
// Or use slider if available
// await page.setInputFiles('#temperature-slider', newTemp);
await page.screenshot({ path: 'animal-config-fields-10-temperature-modified.png', fullPage: true });

// Save and capture
await page.click('.save-configuration-button');
await page.waitForSelector('.success-message, .error-message', { timeout: 10000 });
await page.screenshot({ path: 'animal-config-fields-11-temperature-saved.png', fullPage: true });
```

**Immediate DynamoDB Validation:**
```bash
echo "🔍 VALIDATING TEMPERATURE CHANGE IN DYNAMODB:"
aws dynamodb get-item \
  --table-name quest-dev-animal \
  --key '{"animalId":{"S":"bella_002"}}' \
  --region us-west-2 \
  --profile cmz \
  --query 'Item.{Temperature:configuration.M.temperature.N,Modified:modified.M.at.S}' \
  --output table

echo "🌡️ Temperature change validation complete"
```

### Phase 4: Error Monitoring & Final Validation
**Implementation Order (Monitor Throughout Process):**

#### Step 1: Console Error Monitoring
```javascript
// Monitor browser console for errors throughout the process
page.on('console', msg => {
  if (msg.type() === 'error') {
    console.log(`🚨 Browser Console Error: ${msg.text()}`);
  }
});

// Check for UI error messages
const errorMessages = await page.$$('.error-message, .alert-danger, [class*="error"]');
if (errorMessages.length > 0) {
  console.log(`⚠️ Found ${errorMessages.length} error message(s) in UI`);
  await page.screenshot({ path: 'animal-config-fields-errors-detected.png', fullPage: true });
}
```

#### Step 2: Network Request Monitoring
```javascript
// Monitor network requests for API failures
page.on('response', response => {
  if (response.url().includes('/animal') && response.status() >= 400) {
    console.log(`🚨 API Error: ${response.status()} on ${response.url()}`);
  }
});
```

#### Step 3: Final State Validation and Cleanup
```bash
echo "🔍 FINAL DYNAMODB STATE COMPARISON:"
aws dynamodb get-item \
  --table-name quest-dev-animal \
  --key '{"animalId":{"S":"bella_002"}}' \
  --region us-west-2 \
  --profile cmz \
  --output json > final-animal-state.json

echo "📊 CHANGE SUMMARY:"
echo "Original Name: $(jq -r '.Item.name.S // "null"' initial-animal-state.json)"
echo "Final Name: $(jq -r '.Item.name.S // "null"' final-animal-state.json)"
echo ""
echo "Original Species: $(jq -r '.Item.species.S // "null"' initial-animal-state.json)"
echo "Final Species: $(jq -r '.Item.species.S // "null"' final-animal-state.json)"
echo ""
echo "Original Temperature: $(jq -r '.Item.configuration.M.temperature.N // "null"' initial-animal-state.json)"
echo "Final Temperature: $(jq -r '.Item.configuration.M.temperature.N // "null"' final-animal-state.json)"
echo ""
echo "Modification Timestamps:"
echo "Initial: $(jq -r '.Item.modified.M.at.S // "null"' initial-animal-state.json)"
echo "Final: $(jq -r '.Item.modified.M.at.S // "null"' final-animal-state.json)"
```

#### Step 4: Proper Logout Process
```javascript
// Close configuration modal
await page.click('.modal-close, .cancel-button');
await page.screenshot({ path: 'animal-config-fields-12-modal-closed.png', fullPage: true });

// Navigate to logout
await page.click('.user-menu, .profile-dropdown');
await page.click('.logout-button, [href="/logout"]');
await page.screenshot({ path: 'animal-config-fields-13-logged-out.png', fullPage: true });

// Verify logout successful
await page.waitForSelector('.login-form, [data-testid="login-button"]', { timeout: 5000 });
console.log('✅ Successfully logged out of the application');
```

## Implementation Details

### Required Prerequisites
1. **System Health**: Follow ALL steps in `ANY-PRE-TEST-ADVICE.md` for system verification
2. **Persistence Knowledge**: Reference `VALIDATE-ANIMAL-CONFIG-PERSISTENCE-ADVICE.md` for data validation patterns
3. **MCP Tools**: Playwright MCP for browser automation, AWS CLI for DynamoDB access
4. **Environment**: Frontend on localhost:3001, Backend API on localhost:8080

### Test Data Management
- **Target Animal**: Use `bella_002` (Bella the Bear) with existing configuration
- **Fallback Animals**: `leo_001`, `charlie_003` if primary target unavailable
- **Field Values**: Generate timestamped values to ensure uniqueness
- **Temperature Values**: Use schema-compliant values (multiples of 0.1)

### Visual Documentation Requirements
- **Screenshot Naming**: `animal-config-fields-XX-description.png`
- **Full Page Captures**: Include complete browser window for context
- **Error Documentation**: Capture any error states or unexpected behaviors
- **State Comparison**: Visual confirmation of before/after states

## Integration Points

### CMZ Project Standards
- **Authentication**: Use established admin credentials (admin@cmz.org/admin123)
- **Database Integration**: AWS DynamoDB with profile `cmz` in us-west-2 region
- **API Endpoints**: Leverage existing animal configuration endpoints
- **Error Handling**: Follow CMZ error reporting and recovery patterns

### MCP Server Usage
- **Playwright MCP**: Primary tool for browser automation and screenshot capture
- **Sequential Thinking MCP**: For systematic analysis and decision-making throughout testing
- **Native Tools**: AWS CLI for DynamoDB queries, Bash for orchestration

## Quality Gates

### Mandatory Validation Before Completion
- [ ] All three fields (Animal Name, Scientific Name, Temperature) successfully modified
- [ ] Each field change verified in DynamoDB with updated timestamps
- [ ] No browser console errors detected during the testing process
- [ ] UI displays updated values correctly after each modification
- [ ] All screenshots captured showing visual progression
- [ ] Proper logout process completed successfully
- [ ] Initial and final DynamoDB states documented with comparison

### Error Handling Requirements
- [ ] Browser console monitoring active throughout process
- [ ] Network request error detection implemented
- [ ] UI error message detection and documentation
- [ ] Recovery procedures defined for common failure scenarios
- [ ] Graceful handling of authentication failures
- [ ] DynamoDB access error handling with clear error messages

## Success Criteria

**✅ COMPLETE SUCCESS**: All field modifications successful with DynamoDB persistence
- Animal Name field updated and persisted
- Scientific Name field updated and persisted
- Temperature control updated and persisted
- No errors detected in browser console or UI
- All changes visible in screenshots and database queries
- Clean logout process completed

**⚠️ PARTIAL SUCCESS**: Some fields updated successfully, others failed
- Document which fields succeeded/failed and why
- Provide error analysis and recommended fixes
- Include screenshots of error states

**❌ VALIDATION FAILURE**: Unable to complete field testing
- Authentication failures preventing access to configuration interface
- Database connectivity issues preventing validation
- Critical UI errors preventing field modification
- System health issues requiring resolution per ANY-PRE-TEST-ADVICE.md

## Output Format

```
🔧 ANIMAL CONFIG FIELDS VALIDATION RESULTS

🎯 Target Animal Tested:
- Animal ID: bella_002
- Name: [Initial] → [Final]
- Species: [Initial] → [Final]
- Temperature: [Initial] → [Final]

✅ Field Modification Results:
- Animal Name: SUCCESS/FAILED - [Details]
- Scientific Name: SUCCESS/FAILED - [Details]
- Temperature Control: SUCCESS/FAILED - [Details]

💾 Database Persistence Validation:
- Initial Modified Timestamp: [timestamp]
- Final Modified Timestamp: [timestamp]
- All Changes Persisted: YES/NO

🖥️ UI Interaction Results:
- Authentication: SUCCESS/FAILED
- Configuration Modal Access: SUCCESS/FAILED
- Field Modifications: [Count] successful, [Count] failed
- Error Messages Displayed: YES/NO - [Details if any]
- Logout Process: SUCCESS/FAILED

📊 Visual Documentation:
- Screenshots Captured: [Count] files
- Error States Documented: [Count] issues
- State Comparisons: Initial vs Final states captured

RESULT: PASS/FAIL with specific field-level details and recommendations
```

## Error Recovery Procedures

### Authentication Issues
1. Verify backend API is running on localhost:8080
2. Check admin credentials in ANY-PRE-TEST-ADVICE.md
3. Clear browser cache and retry authentication
4. Verify no existing active sessions blocking login

### Database Access Issues
1. Verify AWS profile `cmz` is configured correctly
2. Test DynamoDB connectivity: `aws dynamodb list-tables --profile cmz`
3. Check table permissions and region settings
4. Validate animal ID exists in quest-dev-animal table

### UI Field Access Issues
1. Verify configuration modal opens correctly
2. Check for JavaScript errors in browser console
3. Validate field selectors and element IDs
4. Ensure proper tab navigation if fields are on different tabs

## References
- `VALIDATE-ANIMAL-CONFIG-FIELDS-ADVICE.md` - Comprehensive testing best practices
- `ANY-PRE-TEST-ADVICE.md` - System health validation requirements
- `VALIDATE-ANIMAL-CONFIG-PERSISTENCE-ADVICE.md` - Data persistence validation patterns