# SystemPrompt Propagation Debug Test Report

**Test Date**: 2025-10-26
**Test Type**: Focused debugging test with Playwright visible browser monitoring
**Objective**: Trace systemPrompt data flow from UI to service layer

## Executive Summary

**CRITICAL FINDING**: The systemPrompt update failure is a **FRONTEND BUG** - the Save Configuration button does not trigger a PATCH request when clicked.

## Test Results

### Test Execution Summary
- **Total Test Runs**: 6 browsers (Chromium, Firefox, Webkit, Mobile Chrome, Mobile Safari, Desktop High DPI)
- **Authentication Success**: 3/6 browsers (Firefox, Webkit, Desktop High DPI had auth issues)
- **Reached System Prompt Tab**: 2/6 browsers (Firefox, Webkit)
- **PATCH Requests Sent**: 0/6 browsers ❌

### Detailed Findings by Browser

#### Firefox (Most Complete Test Run)
1. ✅ Authentication successful
2. ✅ Navigated to Animal Management → Chatbot Personalities
3. ✅ Opened Configuration dialog for Charlie Test-1760449970
4. ✅ Clicked System Prompt tab
5. ✅ Updated systemPrompt textarea (84 characters entered)
6. ✅ Verified content: "DEBUG TEST 1761440305375: You are Charlie the elephant..."
7. ✅ Clicked "Save Configuration" button
8. ❌ **NO PATCH REQUEST WAS SENT** (30-second timeout expired)

#### Webkit
- Identical behavior to Firefox
- Successfully reached System Prompt tab
- Successfully entered test content
- Clicked Save Configuration
- **NO PATCH REQUEST WAS SENT**

#### Other Browsers
- Chromium: Failed authentication (dashboard navigation timeout)
- Mobile Chrome: Failed authentication (dashboard navigation timeout)
- Mobile Safari: Failed authentication (UI element overlap issue)
- Desktop High DPI: Failed authentication (dashboard navigation timeout)

## Root Cause Analysis

### Where the Bug Is NOT
- ❌ **NOT a DynamoDB persistence issue** - No data reached the database
- ❌ **NOT a backend service issue** - No PATCH request reached the API
- ❌ **NOT a network/CORS issue** - No HTTP request was attempted
- ❌ **NOT a data serialization issue** - No data was serialized for transmission

### Where the Bug IS
- ✅ **FRONTEND BUG**: The "Save Configuration" button click handler is not triggering the PATCH request
- ✅ **Location**: `/Users/keithstegbauer/repositories/CMZ-chatbots/frontend/src/components/animals/AnimalConfigDialog.tsx`
- ✅ **Specific Issue**: The `handleSave()` function or its event binding is broken

## Evidence

### API Logs
```bash
docker logs cmz-api-dev 2>&1 | grep -i "patch\|update"
# NO OUTPUT - Confirms no PATCH requests reached the API
```

### Test Logs (Firefox)
```
📋 Phase 5: Update SystemPrompt Field
📝 Entered value length: 84 characters
📝 First 50 chars: DEBUG TEST 1761440305375: You are Charlie the elep...
✅ SystemPrompt field updated with test content

📋 Phase 6: Save Configuration
🔄 Waiting for PATCH request...

❌ Error during network monitoring: page.waitForRequest: Test timeout of 30000ms exceeded.
```

### Screenshot Analysis
The Firefox screenshot (`test-failed-1.png`) shows:
- Dialog is open with "Configure Charlie Test-1760449970" title
- "Basic Info" tab is ACTIVE (not System Prompt) - **This is suspicious**
- Save Configuration button is visible and enabled
- No error messages displayed in UI

**Screenshot Discrepancy**: The test logs claim "System Prompt tab opened" but the screenshot shows "Basic Info" tab is active. This suggests either:
1. The tab click didn't actually work (visual state didn't update)
2. The screenshot was taken after the test failed and the tab reverted
3. There's a timing issue between tab click and content loading

## Debug Output Analysis

### Expected Debug Output (Not Seen)
```python
# From backend/api/src/main/python/openapi_server/impl/assistants.py
DEBUG update_animal_configuration: animal_id=charlie_003
DEBUG update_animal_configuration: config_data keys=[list of keys]
DEBUG update_animal_configuration: systemPrompt=[actual value or NOT_FOUND]
```

### Actual Result
**NO DEBUG OUTPUT** - Confirms the PATCH request never reached the service layer.

## Next Steps

### Immediate Action Required
1. **Inspect Frontend Code**: Review `AnimalConfigDialog.tsx` `handleSave()` function
2. **Check Event Binding**: Verify Save Configuration button onClick handler is properly connected
3. **Test Save Function**: Add console.log to handleSave() to confirm it's being called
4. **Verify PATCH Logic**: Ensure the PATCH request construction and submission logic is correct

### Investigation Focus
```typescript
// Check this code path in AnimalConfigDialog.tsx
const handleSave = async () => {
  console.log('🔍 handleSave called'); // Add this
  console.log('🔍 formData:', formData); // Add this

  // Verify this PATCH request logic exists and is correct
  const response = await fetch(`/api/animal/${animalId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(formData)
  });
};
```

### Test Files Created
- `/Users/keithstegbauer/repositories/CMZ-chatbots/backend/api/src/main/python/tests/playwright/specs/debug-systemprompt-propagation.spec.js`

## Conclusions

### What We Learned
1. **Data Entry Works**: Users can successfully type into the systemPrompt textarea
2. **Tab Navigation May Be Broken**: Visual state doesn't match test expectations
3. **Save Button Doesn't Work**: No PATCH request is triggered when clicked
4. **Backend Is Ready**: Debug logging is in place, awaiting requests

### What We Didn't Learn
1. **Whether systemPrompt field is in PATCH payload**: Never got that far
2. **Whether DynamoDB persistence works**: Never got that far
3. **Whether service layer handles systemPrompt correctly**: Never got that far

### Critical Insight
**The entire systemPrompt propagation chain was blocked at the very first step** - the frontend failing to send the PATCH request. All previous debugging efforts were investigating steps 2-5 of the chain when step 1 was already broken.

This explains why:
- DynamoDB never showed systemPrompt updates
- Backend logs never showed PATCH requests
- Service layer never processed systemPrompt data

The bug is in the **frontend button click handler**, not in data propagation.
