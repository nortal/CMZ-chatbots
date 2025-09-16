# validate-backend-health

Comprehensive validation of backend health checking functionality to distinguish between actual authentication failures and backend service unavailability, with user-friendly error message testing.

## Usage
```
/validate-backend-health [--service <name>] [--simulate <scenario>] [--quick] [--report-only]
```

## Overview

This command validates the complete backend health detection system, ensuring users receive appropriate error messages based on actual system status rather than generic authentication failures. The validation covers backend health endpoint functionality, error message accuracy, and graceful degradation scenarios.

**CRITICAL**: This validation MUST be performed using Playwright MCP with browser visibility enabled so users can observe the testing process in real-time. Visual feedback is essential for verifying correct error message display and user experience validation.

## Command Options

- `--service <name>`: Test specific service health (e.g., "dynamodb", "auth", "health")
- `--simulate <scenario>`: Simulate specific failure scenario (e.g., "backend-down", "db-failure", "auth-failure")
- `--quick`: Run minimal test set (core scenarios only)
- `--report-only`: Generate report from existing test data without re-running tests

## Implementation Process

### Phase 0: Environment Setup and Service Health Baseline
Before starting, read the files:
    ~/repositories/CMZ-chatbots/VALIDATE-BACKEND-HEALTH-ADVICE.md
    ~/repositories/CMZ-chatbots/VALIDATE-BACKEND-HEALTH-REPORT.md
    ~/repositories/CMZ-chatbots/ANY-PRE-TEST-ADVICE.md

1. **Initialize Playwright Browser**
   ```javascript
   // CRITICAL: Use Playwright MCP with visible browser
   await mcp__playwright__browser_navigate({ url: "http://localhost:3000" });

   // Ensure browser window is properly sized for visibility
   await mcp__playwright__browser_resize({ width: 1280, height: 720 });

   // Take initial screenshot for reference
   await mcp__playwright__browser_take_screenshot({
     filename: "backend-health-test-start.png",
     fullPage: false
   });
   ```

2. **Service Health Baseline Check**
   ```bash
   # Verify all required services are running
   curl -f http://localhost:3000 || exit 1  # Frontend
   curl -f http://localhost:8080 || exit 1  # Backend API
   curl -f http://localhost:8080/health || exit 1  # Health endpoint
   aws dynamodb list-tables --region us-west-2 || exit 1  # DynamoDB
   ```

3. **Health Endpoint Validation**
   ```bash
   # Test health endpoint directly
   curl -X GET http://localhost:8080/health \
     -H "Content-Type: application/json" \
     -w "\nStatus: %{http_code}\nTime: %{time_total}s\n" \
     > baseline-health-check.json

   # Validate response structure
   python3 -c "
   import json
   with open('baseline-health-check.json') as f:
       health = json.load(f)
   assert 'status' in health, 'Missing status field'
   assert 'services' in health, 'Missing services field'
   assert 'timestamp' in health, 'Missing timestamp field'
   print('✅ Health endpoint structure valid')
   "
   ```

### Phase 1: Backend Health Detection Validation

**Step 1: Healthy Backend State Verification**
```javascript
// Navigate to login page with healthy backend
await mcp__playwright__browser_navigate({ url: "http://localhost:3000/login" });
await mcp__playwright__browser_snapshot();

// Take screenshot of healthy login page
await mcp__playwright__browser_take_screenshot({
  filename: "healthy-backend-login.png"
});

// Test successful authentication with valid credentials
await mcp__playwright__browser_fill_form({
  fields: [
    { name: "Email", type: "textbox", ref: "[data-testid='email-input']", value: "test@cmz.org" },
    { name: "Password", type: "textbox", ref: "[data-testid='password-input']", value: "testpass123" }
  ]
});

await mcp__playwright__browser_click({
  element: "Login button",
  ref: "[data-testid='login-button']"
});

// Verify successful login (should redirect to dashboard)
await mcp__playwright__browser_wait_for({ text: "Dashboard" });
await mcp__playwright__browser_take_screenshot({
  filename: "successful-login-healthy-backend.png"
});

// Logout for next test
await mcp__playwright__browser_click({
  element: "Logout button",
  ref: "[data-testid='logout-button']"
});
```

**Step 2: Authentication Failure vs Backend Down Differentiation**
```javascript
// Test 1: Valid backend, invalid credentials
await mcp__playwright__browser_navigate({ url: "http://localhost:3000/login" });

await mcp__playwright__browser_fill_form({
  fields: [
    { name: "Email", type: "textbox", ref: "[data-testid='email-input']", value: "test@cmz.org" },
    { name: "Password", type: "textbox", ref: "[data-testid='password-input']", value: "wrongpassword" }
  ]
});

await mcp__playwright__browser_click({
  element: "Login button",
  ref: "[data-testid='login-button']"
});

// Verify authentication failure message (NOT service unavailable)
await mcp__playwright__browser_wait_for({ text: "Invalid email or password" });
await mcp__playwright__browser_take_screenshot({
  filename: "auth-failure-valid-backend.png"
});

// Verify specific error message content
const snapshot1 = await mcp__playwright__browser_snapshot();
const errorMessage1 = extractErrorMessage(snapshot1);
assert(
  errorMessage1.includes("Invalid email or password") &&
  !errorMessage1.includes("service is temporarily unavailable"),
  'Should show auth failure, not service unavailable'
);
```

**Step 3: Backend Down Scenario Simulation**
```bash
# Stop backend API server to simulate service down
make stop-api || docker stop cmz-api-container || pkill -f "python.*openapi_server"

# Verify backend is actually down
curl -f http://localhost:8080/health && exit 1 || echo "✅ Backend confirmed down"

# Wait for service to be fully stopped
sleep 3
```

```javascript
// Test login attempt with backend down
await mcp__playwright__browser_navigate({ url: "http://localhost:3000/login" });

await mcp__playwright__browser_fill_form({
  fields: [
    { name: "Email", type: "textbox", ref: "[data-testid='email-input']", value: "test@cmz.org" },
    { name: "Password", type: "textbox", ref: "[data-testid='password-input']", value: "testpass123" }
  ]
});

await mcp__playwright__browser_click({
  element: "Login button",
  ref: "[data-testid='login-button']"
});

// Verify service unavailable message (NOT auth failure)
await mcp__playwright__browser_wait_for({ text: "service is temporarily unavailable" });
await mcp__playwright__browser_take_screenshot({
  filename: "service-unavailable-backend-down.png"
});

// Verify specific error message content
const snapshot2 = await mcp__playwright__browser_snapshot();
const errorMessage2 = extractErrorMessage(snapshot2);
assert(
  errorMessage2.includes("service is temporarily unavailable") &&
  !errorMessage2.includes("Invalid email or password"),
  'Should show service unavailable, not auth failure'
);
```

**Step 4: Backend Recovery Validation**
```bash
# Restart backend API server
make run-api &

# Wait for service to be fully started
sleep 10

# Verify backend is healthy again
curl -f http://localhost:8080/health || exit 1
echo "✅ Backend confirmed healthy after restart"
```

```javascript
// Test login works again after backend recovery
await mcp__playwright__browser_navigate({ url: "http://localhost:3000/login" });

await mcp__playwright__browser_fill_form({
  fields: [
    { name: "Email", type: "textbox", ref: "[data-testid='email-input']", value: "test@cmz.org" },
    { name: "Password", type: "textbox", ref: "[data-testid='password-input']", value: "testpass123" }
  ]
});

await mcp__playwright__browser_click({
  element: "Login button",
  ref: "[data-testid='login-button']"
});

// Verify successful login after recovery
await mcp__playwright__browser_wait_for({ text: "Dashboard" });
await mcp__playwright__browser_take_screenshot({
  filename: "successful-login-after-recovery.png"
});
```

### Phase 2: Service-Specific Health Validation

**DynamoDB Connectivity Testing**
```bash
# Test DynamoDB health endpoint specifically
curl -X GET http://localhost:8080/health \
  -H "Content-Type: application/json" | \
  jq '.services.dynamodb' > dynamodb-health.json

# Verify DynamoDB service status
python3 -c "
import json
with open('dynamodb-health.json') as f:
    status = json.load(f)
assert status == 'healthy', f'DynamoDB not healthy: {status}'
print('✅ DynamoDB connectivity confirmed')
"
```

**Authentication Service Testing**
```bash
# Test authentication service health
curl -X POST http://localhost:8080/api/auth/test \
  -H "Content-Type: application/json" \
  -d '{"test": "health_check"}' \
  -w "\nStatus: %{http_code}\n" > auth-health-test.json

# Verify auth service responds correctly
grep -q "200" auth-health-test.json && echo "✅ Auth service healthy"
```

### Phase 3: Degraded Service Scenarios

**Step 1: Partial Service Degradation Simulation**
```bash
# Simulate DynamoDB connectivity issues (mock/stub)
# This would require implementation-specific mocking
echo "Simulating partial service degradation..."

# Test health endpoint with degraded services
curl -X GET http://localhost:8080/health \
  -H "Content-Type: application/json" > degraded-health-check.json

# Verify degraded status handling
python3 -c "
import json
with open('degraded-health-check.json') as f:
    health = json.load(f)
if health.get('status') == 'degraded':
    print('✅ Degraded status detected correctly')
else:
    print('ℹ️ Degraded scenario not currently implemented')
"
```

**Step 2: Graceful Degradation Testing**
```javascript
// Test login with degraded services (if implemented)
await mcp__playwright__browser_navigate({ url: "http://localhost:3000/login" });

// Check for degraded service warning messages
const snapshot3 = await mcp__playwright__browser_snapshot();
const warningMessage = extractWarningMessage(snapshot3);

if (warningMessage.includes("Some features may be limited")) {
  await mcp__playwright__browser_take_screenshot({
    filename: "graceful-degradation-warning.png"
  });
  console.log('✅ Graceful degradation warning displayed');
} else {
  console.log('ℹ️ Graceful degradation not currently implemented');
}
```

### Phase 4: Performance and Reliability Testing

**Step 1: Health Check Performance Validation**
```bash
# Test health endpoint response times
for i in {1..10}; do
  curl -X GET http://localhost:8080/health \
    -H "Content-Type: application/json" \
    -w "%{time_total}\n" \
    -o /dev/null -s
done > health-response-times.txt

# Analyze performance
python3 -c "
import statistics
with open('health-response-times.txt') as f:
    times = [float(line.strip()) for line in f]
avg_time = statistics.mean(times)
max_time = max(times)
print(f'Average response time: {avg_time:.3f}s')
print(f'Maximum response time: {max_time:.3f}s')
assert max_time < 2.0, f'Health check too slow: {max_time}s > 2.0s'
print('✅ Health check performance acceptable')
"
```

**Step 2: Error Message Consistency Testing**
```javascript
// Test error message consistency across multiple attempts
const errorMessages = [];

for (let i = 0; i < 3; i++) {
  // Stop backend
  await stopBackendService();

  await mcp__playwright__browser_navigate({ url: "http://localhost:3000/login" });
  await mcp__playwright__browser_fill_form({
    fields: [
      { name: "Email", type: "textbox", ref: "[data-testid='email-input']", value: "test@cmz.org" },
      { name: "Password", type: "textbox", ref: "[data-testid='password-input']", value: "testpass123" }
    ]
  });

  await mcp__playwright__browser_click({
    element: "Login button",
    ref: "[data-testid='login-button']"
  });

  const snapshot = await mcp__playwright__browser_snapshot();
  const errorMessage = extractErrorMessage(snapshot);
  errorMessages.push(errorMessage);

  // Restart backend for next iteration
  await startBackendService();
  await new Promise(resolve => setTimeout(resolve, 5000)); // Wait for startup
}

// Verify consistency
const uniqueMessages = [...new Set(errorMessages)];
assert(uniqueMessages.length === 1, 'Error messages should be consistent');
console.log('✅ Error message consistency validated');
```

### Phase 5: Cross-Browser Compatibility Testing

**Step 1: Multi-Browser Error Message Validation**
```javascript
// Test in different browsers (if Playwright supports multiple)
const browsers = ['chromium', 'firefox', 'webkit'];

for (const browserType of browsers) {
  console.log(`Testing in ${browserType}...`);

  // Stop backend for this test
  await stopBackendService();

  // Navigate and test in specific browser
  await mcp__playwright__browser_navigate({ url: "http://localhost:3000/login" });

  await mcp__playwright__browser_fill_form({
    fields: [
      { name: "Email", type: "textbox", ref: "[data-testid='email-input']", value: "test@cmz.org" },
      { name: "Password", type: "textbox", ref: "[data-testid='password-input']", value: "testpass123" }
    ]
  });

  await mcp__playwright__browser_click({
    element: "Login button",
    ref: "[data-testid='login-button']"
  });

  await mcp__playwright__browser_wait_for({ text: "service is temporarily unavailable" });
  await mcp__playwright__browser_take_screenshot({
    filename: `service-unavailable-${browserType}.png`
  });

  // Restart backend for next browser
  await startBackendService();
  await new Promise(resolve => setTimeout(resolve, 5000));
}
```

### Phase 6: Network Condition Testing

**Step 1: Slow Network Simulation**
```javascript
// Simulate slow network conditions (if supported)
await mcp__playwright__browser_evaluate({
  function: `() => {
    // Simulate slow network by adding delays to fetch requests
    const originalFetch = window.fetch;
    window.fetch = function(...args) {
      return new Promise(resolve => {
        setTimeout(() => resolve(originalFetch.apply(this, args)), 3000);
      });
    };
  }`
});

// Test login with slow network
await mcp__playwright__browser_navigate({ url: "http://localhost:3000/login" });

await mcp__playwright__browser_fill_form({
  fields: [
    { name: "Email", type: "textbox", ref: "[data-testid='email-input']", value: "test@cmz.org" },
    { name: "Password", type: "textbox", ref: "[data-testid='password-input']", value: "testpass123" }
  ]
});

await mcp__playwright__browser_click({
  element: "Login button",
  ref: "[data-testid='login-button']"
});

// Verify loading state or timeout handling
await mcp__playwright__browser_take_screenshot({
  filename: "slow-network-login-attempt.png"
});
```

### Phase 7: Reporting and Analysis

**Update Test Reports**

**VALIDATE-BACKEND-HEALTH-REPORT.md**:
```markdown
# Backend Health Validation Report
Generated: [timestamp]

## 🎯 PRIMARY VALIDATION RESULTS

### Backend Health Detection
| Test Scenario | Expected Message | Actual Message | Status |
|---------------|------------------|----------------|---------|
| Healthy Backend + Valid Creds | Dashboard redirect | [actual] | ✅/❌ |
| Healthy Backend + Invalid Creds | "Invalid email or password" | [actual] | ✅/❌ |
| Backend Down + Valid Creds | "service is temporarily unavailable" | [actual] | ✅/❌ |
| Backend Down + Invalid Creds | "service is temporarily unavailable" | [actual] | ✅/❌ |
| Backend Recovery | Dashboard redirect | [actual] | ✅/❌ |

### Service Health Endpoint
| Service | Status | Response Time | Details |
|---------|--------|---------------|---------|
| Overall Health | ✅/❌ | [time]ms | [details] |
| DynamoDB | ✅/❌ | [time]ms | [connection status] |
| Authentication | ✅/❌ | [time]ms | [jwt validation] |
| AWS Services | ✅/❌ | [time]ms | [service status] |

### Performance Metrics
- Health Check Average Response: [time]ms
- Health Check Maximum Response: [time]ms
- Frontend Timeout Threshold: 5000ms
- Performance Status: ✅ ACCEPTABLE / ❌ TOO SLOW

### Error Message Validation
**Consistency Check**: ✅ CONSISTENT / ❌ INCONSISTENT
**Message Clarity**: ✅ USER-FRIENDLY / ❌ TECHNICAL
**Cross-Browser**: ✅ CONSISTENT / ❌ VARIES

### 🔍 Root Cause Analysis (if failures detected)

**If Backend Health Detection FAILED**:

**Data Flow Analysis**:
- Frontend → Health Check: [SUCCESS/FAIL - details]
- Health Check → Services: [SUCCESS/FAIL - details]
- Error Message Display: [SUCCESS/FAIL - details]
- User Experience: [SUCCESS/FAIL - details]

**Network Requests Analysis**:
- Health Check Call: [URL, Method, Status, Response Time]
- Login API Call: [URL, Method, Status, Payload]
- Error Messages: [Browser console errors]

**Identified Issues**:
1. [Issue description with exact failure point]
2. [Reproduction steps]
3. [Suggested fix]

### 🎯 WORKING STATUS SUMMARY

**BACKEND HEALTH DETECTION WORKING CORRECTLY**:
- ✅ Health endpoint functional
- ✅ Service status detection accurate
- ✅ Error messages user-friendly and appropriate
- ✅ Performance within acceptable limits
**Result**: Backend health validation is functional ✅

**OR**

**BACKEND HEALTH DETECTION NOT WORKING**:
- ❌ [specific issue - e.g., "always shows auth failure"]
- ❌ [specific issue - e.g., "health endpoint not responding"]
**Result**: Backend health validation is broken ❌
**Impact**: Users cannot distinguish between login errors and service issues
**Fix Required**: Yes, before production use

## Test Execution Metrics
- Total Test Duration: [duration]
- Health Check Tests: [count passed/failed]
- Error Message Tests: [count passed/failed]
- Browser Compatibility: [browsers tested]
- Performance Tests: [response time analysis]
```

## Success Criteria

### 🎯 PRIMARY GOALS: Backend Health Detection
- ✅ **Health endpoint** responds correctly for all service states
- ✅ **Error message differentiation** between auth failures and service unavailability
- ✅ **Service recovery detection** when backend comes back online
- ✅ **Performance requirements** met (< 2s health check response)
- ✅ **Cross-browser compatibility** for error message display
- ✅ **User-friendly messaging** appropriate for zoo visitors

**CRITICAL SUCCESS INDICATOR**: If users see "service temporarily unavailable" when backend is down and "invalid credentials" when backend is up but credentials are wrong, the system is working correctly.

### Quality Metrics
- Health endpoint has complete service dependency validation
- Every failure includes exact reproduction steps and root cause analysis
- Error messages are consistent across browsers and attempts
- Performance benchmarks are within acceptable ranges
- User experience is appropriate for non-technical zoo visitors

### Deliverables
1. `VALIDATE-BACKEND-HEALTH-REPORT.md` - Comprehensive test results
2. `VALIDATE-BACKEND-HEALTH-ADVICE.md` - Testing guidance and troubleshooting
3. All health check validations documented with screenshots
4. Performance benchmarks and cross-browser compatibility results

## Implementation Notes

### Sequential Reasoning Integration
Use MCP Sequential Thinking to:
- Plan optimal test sequence for service state transitions
- Predict likely failure patterns in health detection
- Generate hypotheses about error message display issues
- Design targeted scenarios for edge case testing

### Tool Usage
- **Playwright MCP (PRIMARY - REQUIRED)**: Browser automation with VISUAL feedback
  - MUST use for ALL user interaction testing
  - Browser window MUST be visible throughout testing
  - Take screenshots at key validation points
  - Use browser_snapshot for error message extraction
- **Bash**: Service control (start/stop backend), API testing with curl
- **Read/Write**: Maintain test reports and documentation

**CRITICAL IMPLEMENTATION NOTE**:
The entire test MUST be performed through Playwright MCP with visible browser. This ensures:
1. User confidence in error message accuracy
2. Visual verification of user experience
3. Real-world testing of frontend-backend integration
4. Debugging capability when tests fail

### Error Handling
- Capture screenshots on all error scenarios
- Log full network request/response details
- Document browser console errors
- Save service status at time of failure

### Helper Functions
```javascript
function extractErrorMessage(snapshot) {
  // Extract error message text from accessibility snapshot
  // Look for error containers, alert divs, etc.
}

function extractWarningMessage(snapshot) {
  // Extract warning message text for degraded services
}

async function stopBackendService() {
  // Implement backend service stopping
  // Platform-specific (Docker, process kill, etc.)
}

async function startBackendService() {
  // Implement backend service starting
  // Wait for health check to pass
}
```

## Example Execution

```bash
# Full backend health validation
/validate-backend-health

# Test specific service health
/validate-backend-health --service dynamodb

# Simulate specific failure scenario
/validate-backend-health --simulate backend-down

# Quick validation (core scenarios only)
/validate-backend-health --quick

# Generate report only
/validate-backend-health --report-only
```

**Recommended Usage**: Start with the basic command to get complete backend health validation. The test will provide clear WORKING/NOT WORKING status for the health detection system.

## Troubleshooting

### Common Issues

1. **Backend won't stop/start**: Check Docker containers, process management
2. **Health endpoint not found**: Verify backend API is running on correct port
3. **Error messages not displaying**: Check frontend error handling implementation
4. **Performance issues**: Monitor network latency, service response times
5. **Browser compatibility**: Test across Chrome, Firefox, Safari

### Debug Mode
Add `--debug` flag for verbose output including:
- Each health check request/response
- Service status details
- Error message extraction details
- Timing for each test operation

## Related Commands
- `/validate-full-animal-config` - Component validation with health dependencies
- `/validate-data-persistence` - Data flow validation requiring healthy backend
- `/systematic-cmz-infrastructure-hardening` - Infrastructure reliability including health monitoring