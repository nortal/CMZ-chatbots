# Animal Config Component Testing Advice

## CRITICAL: Visual Testing with Playwright MCP

**This validation MUST be performed using Playwright MCP with browser visibility enabled.** The browser window must remain visible throughout the entire testing process so users can:
- See exactly which UI elements are being tested
- Observe the actual user interactions being simulated
- Identify visual issues that automated tests might miss
- Build confidence that the test coverage is comprehensive
- Debug failures by seeing exactly where and how issues occur

### Playwright MCP Setup
```javascript
// ALWAYS start with browser initialization and visibility
await mcp__playwright__browser_navigate({ url: "http://localhost:3000" });
await mcp__playwright__browser_resize({ width: 1280, height: 720 });

// Take screenshots at every major step for documentation
await mcp__playwright__browser_take_screenshot({
  filename: "test-progress-{step}.png",
  fullPage: false
});

// Use snapshots for accessibility verification
const snapshot = await mcp__playwright__browser_snapshot();
```

## Authentication
- Use test@cmz.org / testpass123 for standard user
- Use admin@cmz.org / adminpass123 for admin operations
- JWT tokens expire after 1 hour, re-auth if tests run long
- **Visual Confirmation**: User should see successful login and dashboard redirect

## Valid Test Values by Component

### Voice Field
- Valid providers: "elevenlabs", "aws-polly", "azure"
- Valid voiceIds: Must match provider's voice list
- Stability: 0.0 to 1.0 (decimals)
- Note: "elevenlabs" requires additional nested settings
- **Visual Testing**: User should see dropdown options change when selecting different providers

### AI Model Field
- Valid models: "gpt-4", "gpt-3.5-turbo", "claude-2"
- Note: Model availability depends on API keys configured
- **Visual Testing**: Verify model descriptions appear on hover/selection

### Temperature/Top P
- Valid range: 0.0 to 1.0
- Precision: Up to 2 decimal places
- Default: 0.7 for temperature, 0.9 for top_p
- **Visual Testing**: Sliders should move smoothly, values should update in real-time

### Guardrails
- Structure: Array of objects with {id, name, enabled, rules}
- Maximum: 10 guardrails per animal
- Rules: JSON schema validation applied
- **Visual Testing**: User should see guardrails list update when adding/removing items

### Knowledge Base Entries
- File references only (no actual upload in testing)
- Support for multiple entries
- Each entry should have title, description, and reference
- **Visual Testing**: List should visually update when entries are added/deleted

### Boolean Fields (Active, Allow Personal Questions)
- Toggle switches should visually change state
- **Visual Testing**: User should see immediate visual feedback on toggle

### Text Fields (Animal Name, Species, System Prompt)
- Support Unicode characters: "Léo 獅子 🦁"
- Maximum lengths vary by field (check OpenAPI spec)
- **Visual Testing**: Character counters should update in real-time

## Timing Considerations with Visual Feedback
- Allow 2s after save for DynamoDB eventual consistency
- Dialog animations take ~300ms, wait before interacting
- List refresh may take up to 5s with many animals
- **Visual Indicators**: User should see loading spinners during async operations

## Visual Testing Best Practices

### Screenshot Documentation
```javascript
// Take screenshots at key moments
await mcp__playwright__browser_take_screenshot({
  filename: `${componentName}-before-change.png`,
  element: "Component under test",
  ref: `[data-testid="${componentId}"]`
});

// After making changes
await mcp__playwright__browser_take_screenshot({
  filename: `${componentName}-after-change.png`,
  element: "Component after modification",
  ref: `[data-testid="${componentId}"]`
});
```

### Accessibility Verification
```javascript
// Use snapshots to verify screen reader compatibility
const snapshot = await mcp__playwright__browser_snapshot();
// Verify all form fields have proper labels
// Check for ARIA attributes
// Ensure keyboard navigation works
```

### Network Monitoring
```javascript
// Monitor API calls during save operations
const requests = await mcp__playwright__browser_network_requests();
// User can see in browser DevTools that requests are being made
```

### Console Monitoring
```javascript
// Capture any errors or warnings
const messages = await mcp__playwright__browser_console_messages();
// Log these for debugging when tests fail
```

## Common Visual Issues to Watch For

### UI State Inconsistencies
- Fields not updating after save
- Loading states that never resolve
- Error messages that don't clear
- Success notifications that don't appear

### Layout Problems
- Overlapping elements when dialog opens
- Fields that are cut off or hidden
- Responsive issues at different screen sizes
- Scrolling problems in long forms

### Animation Issues
- Transitions that are too slow or too fast
- Elements that jump instead of animating smoothly
- Loading spinners that don't appear/disappear correctly

## Known Issues & Visual Workarounds

### Voice Field Validation
- **Issue**: Dropdown may not show all options initially
- **Visual Workaround**: Click dropdown twice to ensure all options load
- **User Should See**: Full list of voice providers after second click

### Large Personality Text
- **Issue**: Text area may not expand properly
- **Visual Workaround**: Click outside and back into field to trigger resize
- **User Should See**: Text area expand to accommodate content

### Concurrent Saves
- **Issue**: Multiple save buttons may appear active
- **Visual Workaround**: Wait for first save to complete (spinner stops)
- **User Should See**: Only one save operation at a time

## Debugging with Visual Feedback

### When Tests Fail
1. Check the screenshot at point of failure
2. Review browser console messages
3. Examine network requests in browser DevTools
4. Look for visual anomalies in the UI
5. Verify element selectors using browser inspector

### Visual Regression Detection
- Compare screenshots from previous runs
- Look for unexpected style changes
- Check for missing or new UI elements
- Verify color and contrast remain accessible

## Performance Monitoring with Visual Indicators

### Expected Visual Feedback Times
- Button click feedback: < 100ms
- Form validation messages: < 200ms
- Save operation spinner: appears within 100ms
- Success notification: appears within 2s of save
- Dialog open/close animation: ~300ms

### Visual Performance Issues
- Laggy animations (low FPS)
- Delayed visual feedback on interactions
- Flickering during updates
- Slow rendering of large lists

## Test Execution Checklist

### Before Each Test
- [ ] Browser window is visible and properly sized
- [ ] User is logged in (verify visually)
- [ ] Initial screenshot taken for reference
- [ ] Browser console is clear of errors

### During Each Test
- [ ] Each interaction is visually confirmed
- [ ] Screenshots taken at key points
- [ ] Loading states are visible when expected
- [ ] Success/error messages appear appropriately
- [ ] No visual glitches or anomalies

### After Each Test
- [ ] Final screenshot shows expected end state
- [ ] All dialogs properly closed
- [ ] No lingering loading states
- [ ] Browser console checked for errors
- [ ] Network requests completed successfully

## Reporting Visual Issues

When documenting failures, include:
1. Screenshot at point of failure
2. Expected visual state description
3. Actual visual state description
4. Browser console output
5. Network request status
6. Steps to reproduce with visual markers
7. Browser and OS information

## Integration with CI/CD

### Headless vs Headed Mode
- Development: Always use headed mode (visible browser)
- CI/CD: Can use headless with video recording
- Debugging: Must use headed mode to see issues

### Visual Regression Testing
- Store baseline screenshots in version control
- Compare new screenshots against baselines
- Flag visual differences for review
- Maintain screenshot history for comparison

## Conclusion

Visual testing with Playwright MCP is not just recommended—it's **required** for comprehensive validation of the Animal Config dialog. The ability to see tests execute in real-time provides invaluable insights that cannot be obtained through API testing alone. This approach ensures both functional correctness and visual quality, leading to a better user experience and more reliable application.