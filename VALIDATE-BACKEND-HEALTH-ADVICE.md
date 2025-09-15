# Backend Health Validation Testing Advice

## Authentication & Service Credentials

### Standard Test Credentials
- **Email**: `test@cmz.org`
- **Password**: `testpass123`
- **Role**: Default user with basic access
- **JWT Token Expiry**: 1 hour (re-authenticate if tests run longer)

### Service Endpoints
- **Frontend**: `http://localhost:3000`
- **Backend API**: `http://localhost:8080`
- **Health Check**: `http://localhost:8080/health`
- **Authentication**: `http://localhost:8080/api/auth`

## Backend Service Management

### Service Start/Stop Commands
```bash
# Start backend (recommended method)
make run-api

# Stop backend
make stop-api

# Alternative: Docker commands
docker stop cmz-api-container
docker start cmz-api-container

# Alternative: Process management
pkill -f "python.*openapi_server"
ps aux | grep openapi_server  # Verify stopped
```

### Service Health Verification
```bash
# Quick health check
curl -f http://localhost:8080/health

# Detailed health status
curl -s http://localhost:8080/health | jq '.'

# Check if services are responding
curl -I http://localhost:3000  # Frontend
curl -I http://localhost:8080  # Backend
```

### Service Startup Time
- **Backend API**: Allow 5-10 seconds for full startup
- **Health Endpoint**: Available immediately after API server starts
- **DynamoDB Connection**: May take additional 2-3 seconds to establish
- **Frontend**: Usually ready in 1-2 seconds

## Expected Error Messages by Scenario

### Scenario 1: Healthy Backend + Valid Credentials
**Expected Outcome**: Successful login, redirect to dashboard
**Success Indicators**:
- URL changes to `/dashboard` or `/admin`
- "Dashboard" text visible
- No error messages displayed
- Browser console shows no errors

### Scenario 2: Healthy Backend + Invalid Credentials
**Expected Error Message**: "Invalid email or password. Please check your credentials and try again."
**Key Validation Points**:
- ❌ Should NOT contain: "service", "unavailable", "down", "temporarily"
- ✅ Should contain: "invalid", "email", "password", "credentials"
- Error should appear within 2-3 seconds
- Login form should remain accessible

### Scenario 3: Backend Down + Any Credentials
**Expected Error Message**: "Our service is temporarily unavailable. Please try again in a few minutes."
**Key Validation Points**:
- ❌ Should NOT contain: "invalid", "password", "credentials", "email"
- ✅ Should contain: "service", "temporarily unavailable", "try again"
- Error should appear within 5-8 seconds (timeout threshold)
- May show loading indicator before error

### Scenario 4: Degraded Services (if implemented)
**Expected Warning Message**: "Some features may be limited, but you can still log in."
**Key Validation Points**:
- Should appear as warning (yellow/orange), not error (red)
- Login functionality should still work
- Message should be informational, not blocking

## Service Health Response Formats

### Healthy Response
```json
{
  "status": "healthy",
  "timestamp": "2025-09-15T10:30:00.000Z",
  "services": {
    "dynamodb": "healthy",
    "auth": "healthy",
    "aws": "healthy"
  }
}
```

### Degraded Response
```json
{
  "status": "degraded",
  "timestamp": "2025-09-15T10:30:00.000Z",
  "services": {
    "dynamodb": "healthy",
    "auth": "unhealthy: JWT secret not configured",
    "aws": "healthy"
  }
}
```

### Unhealthy Response
```json
{
  "status": "unhealthy",
  "timestamp": "2025-09-15T10:30:00.000Z",
  "services": {
    "dynamodb": "unhealthy: Connection timeout",
    "auth": "unhealthy: Service not responding",
    "aws": "healthy"
  }
}
```

## Timing Considerations

### Response Time Expectations
- **Health Check API**: < 2 seconds under normal conditions
- **Frontend Health Validation**: < 5 seconds timeout
- **Login Attempt (Healthy)**: < 3 seconds
- **Login Attempt (Backend Down)**: 5-8 seconds (includes timeout)

### Test Timing Best Practices
- Allow 2-3 seconds after backend stop before testing
- Wait 5-10 seconds after backend start before testing
- Use explicit waits for error message appearance
- Account for network latency in CI/CD environments

## Browser-Specific Considerations

### Chrome/Chromium
- Fast JavaScript execution
- Reliable network timeout handling
- Good developer tools for debugging
- **Best for**: Primary testing and debugging

### Firefox
- May have slightly different timeout behavior
- Different JavaScript engine (SpiderMonkey)
- Good accessibility testing support
- **Best for**: Cross-browser compatibility validation

### Safari/WebKit
- More conservative timeout handling
- May show different network error messages
- Mobile Safari specific considerations
- **Best for**: Mobile and iOS compatibility testing

## Network Condition Testing

### Slow Network Simulation
```javascript
// Playwright method to simulate slow network
await page.route('**/*', route => {
  setTimeout(() => route.continue(), 2000); // 2s delay
});
```

### Network Timeout Testing
```javascript
// Simulate network timeout
await page.route('**/health', route => {
  // Don't respond, let it timeout
  // route.abort('timedout');
});
```

## Common Testing Issues & Solutions

### Issue 1: Backend Won't Stop
**Symptoms**: Service still responds after stop command
**Solutions**:
- Check for multiple instances: `ps aux | grep openapi_server`
- Force kill: `pkill -9 -f openapi_server`
- Check Docker containers: `docker ps | grep cmz`
- Restart Docker if needed: `docker restart`

### Issue 2: Health Endpoint Returns 404
**Symptoms**: `curl http://localhost:8080/health` returns 404
**Solutions**:
- Verify endpoint implementation in backend code
- Check route registration in Flask app
- Confirm backend is running on correct port
- Check for OpenAPI spec health endpoint definition

### Issue 3: Error Messages Not Displaying
**Symptoms**: Login attempts show no error messages
**Solutions**:
- Check browser console for JavaScript errors
- Verify error handling in frontend code
- Confirm error message selectors in tests
- Check CSS display properties (not hidden)

### Issue 4: Inconsistent Test Results
**Symptoms**: Same test gives different results on different runs
**Solutions**:
- Add longer waits between service state changes
- Verify complete service shutdown before testing
- Check for race conditions in async operations
- Use deterministic test data

### Issue 5: Performance Issues
**Symptoms**: Health checks take > 5 seconds
**Solutions**:
- Check DynamoDB connection configuration
- Verify AWS credentials and region settings
- Monitor network latency to AWS services
- Consider implementing connection pooling

## DynamoDB Health Validation

### Connection Testing
```bash
# Test DynamoDB connectivity
aws dynamodb list-tables --region us-west-2

# Test specific table access
aws dynamodb describe-table --table-name quest-dev-user --region us-west-2

# Quick item count (health indicator)
aws dynamodb scan --table-name quest-dev-user --select COUNT --region us-west-2
```

### Common DynamoDB Issues
- **Credentials**: Ensure AWS_PROFILE=cmz is set
- **Region**: Confirm us-west-2 region
- **Network**: Check internet connectivity for AWS access
- **Permissions**: Verify IAM permissions for DynamoDB access

## Frontend Error Handling Implementation

### Required Frontend Components
```javascript
// Health check integration in login flow
async function validateBackendHealth() {
  // Implementation should exist in frontend
  // Should return true/false for backend status
}

// Error message display system
function showError(message) {
  // Should display user-friendly error messages
  // Should be accessible and visible
}

// Loading state management
function showLoading() {
  // Should indicate when health check is in progress
}
```

### Error Message Accessibility
- Use proper ARIA labels for error messages
- Ensure sufficient color contrast
- Screen reader compatibility
- Keyboard navigation support

## Performance Benchmarking

### Acceptable Performance Thresholds
- **Health Check Response**: < 2 seconds (average), < 5 seconds (maximum)
- **Frontend Timeout**: 5 seconds for health validation
- **Error Message Display**: < 1 second after backend response
- **Service Recovery**: < 10 seconds to detect backend restoration

### Performance Testing Commands
```bash
# Multiple health check timing
for i in {1..10}; do
  time curl -s http://localhost:8080/health > /dev/null
done

# Average response time calculation
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8080/health
```

## Security Considerations

### Health Endpoint Security
- Should NOT expose sensitive configuration
- Should NOT reveal internal service details
- Should provide minimal information for status only
- Consider rate limiting for health endpoint

### Error Message Security
- Avoid exposing internal error details to users
- Don't reveal system architecture in error messages
- Log detailed errors server-side, show generic messages to users
- Prevent information disclosure through error timing

## Debugging Tools & Techniques

### Browser Developer Tools
- **Network Tab**: Monitor health check requests/responses
- **Console**: Check for JavaScript errors and logs
- **Application Tab**: Verify localStorage/sessionStorage state
- **Elements Tab**: Inspect error message DOM elements

### Backend Debugging
```bash
# Enable debug mode
DEBUG=1 make run-api

# Check backend logs
make logs-api

# Test health endpoint directly
curl -v http://localhost:8080/health
```

### Playwright Debugging
- Use `--headed` flag to see browser actions
- Add `page.pause()` for interactive debugging
- Enable verbose logging for network requests
- Take screenshots at key points for visual verification

## Continuous Integration Considerations

### CI Environment Setup
- Ensure Docker/services available in CI
- Account for slower CI network/performance
- Use appropriate timeouts for CI environment
- Mock external dependencies if needed

### CI-Specific Timing
- Increase timeout values by 2-3x for CI
- Add extra wait time after service state changes
- Use retry logic for flaky network conditions
- Implement proper cleanup between tests

## Recovery Testing Best Practices

### Service Recovery Validation
1. Stop backend service completely
2. Verify error messages display correctly
3. Start backend service
4. Wait for health check to pass
5. Verify login works normally again
6. Confirm no residual error states

### State Cleanup
- Clear browser cache between tests
- Reset any localStorage/sessionStorage
- Ensure no stale error messages persist
- Verify service state indicators reset

## Integration with Other Tests

### Test Dependencies
- **Animal Config Validation**: Requires healthy backend
- **Data Persistence Tests**: Needs backend health detection
- **Authentication Tests**: Should integrate with health checking

### Test Order Optimization
1. Run health validation first (establishes baseline)
2. Use health results for subsequent test routing
3. Skip complex tests if basic health fails
4. Report health status in all test summaries

---

## Quick Reference Commands

```bash
# Service Management
make run-api          # Start backend
make stop-api         # Stop backend
make logs-api         # View backend logs

# Health Verification
curl -f http://localhost:8080/health    # Quick health check
curl -s http://localhost:8080/health | jq '.status'  # Status only

# Performance Testing
time curl -s http://localhost:8080/health > /dev/null

# Service Process Check
ps aux | grep openapi_server
docker ps | grep cmz

# DynamoDB Connectivity
aws dynamodb list-tables --region us-west-2
```

## Success Patterns
✅ Clear error message differentiation between auth and service failures
✅ Consistent timing and behavior across browsers
✅ Graceful degradation when possible
✅ Fast health check responses (< 2 seconds)
✅ User-friendly language appropriate for zoo visitors
✅ Visual confirmation through Playwright browser testing