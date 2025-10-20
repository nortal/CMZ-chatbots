# Step 1 Validation Guide

## Purpose
Validate core login functionality before running comprehensive test suite. Catch fundamental authentication issues early to avoid wasting time on full tests when core functionality is broken.

## Success Criteria
- **Threshold**: 5/6+ browsers passing authentication
- **Core Requirements**: 
  - Authentication working (JWT tokens generated)
  - Proper redirects to dashboard
  - No CORS errors
  - Test users can login successfully

## Commands

### Quick Single User Test
```bash
FRONTEND_URL=http://localhost:3001 npx playwright test --config config/playwright.config.js --grep "should successfully validate login for Test Parent One" --reporter=line --workers=1
```

### Full Step 1 Validation (All 5 Test Users)
```bash
FRONTEND_URL=http://localhost:3001 npx playwright test --config config/playwright.config.js --grep "🔐 Login User Validation - STEP 1" --reporter=line --workers=1
```

### Infrastructure Validation Only
```bash
FRONTEND_URL=http://localhost:3001 npx playwright test --config config/playwright.config.js --grep "🔧 Login Infrastructure Validation" --reporter=line --workers=1
```

## Test Users Validated
1. **Test Parent One** - `parent1@test.cmz.org` / `testpass123`
2. **Test Student One** - `student1@test.cmz.org` / `testpass123`
3. **Test Student Two** - `student2@test.cmz.org` / `testpass123`
4. **Default Test User** - `test@cmz.org` / `testpass123`
5. **Hardcoded Test User** - `user_parent_001@cmz.org` / `testpass123`

## Common Issues and Solutions

### Issue: "do some magic!" Response
**Symptom**: API returns placeholder text instead of authentication
**Solution**: Connect generated controller to implementation
```python
# In auth_controller.py
from openapi_server.impl.auth import authenticate_user
# Call authenticate_user() instead of returning 'do some magic!'
```

### Issue: User Not Found
**Symptom**: "Invalid email or password" for all test users
**Solution**: Add test users to auth.py implementation
```python
# In openapi_server/impl/auth.py - authenticate_user()
test_users = {
    'parent1@test.cmz.org': {
        'password': 'testpass123',
        'user_id': 'user_test_parent_001',
        'role': 'parent',
        'user_type': 'parent'
    },
    # ... other test users
}
```

### Issue: CORS Errors
**Symptom**: Network requests blocked by CORS policy
**Solution**: Update CORS configuration in `__main__.py`
```python
CORS(app.app, origins=['http://localhost:3001', 'http://localhost:3000'], supports_credentials=True)
```

### Issue: Mobile Safari Button Click
**Symptom**: Footer intercepting login button clicks on Mobile Safari
**Status**: Known UI issue, does not affect authentication validation
**Impact**: Acceptable - 5/6 browsers still validates Step 1 success

## Validation Process

1. **Run Step 1 Validation**
2. **Check Results**:
   - ✅ 5/6+ browsers passing = Proceed to Step 2
   - ❌ <5/6 browsers passing = Fix issues before Step 2
3. **Common Success Indicators**:
   - `✅ Login successful - Current URL: http://localhost:3001/dashboard`
   - `🎯 Successfully redirected to /dashboard`
   - JWT token in API response
4. **Rebuild Backend** if auth changes made:
   ```bash
   cd /Users/keithstegbauer/repositories/CMZ-chatbots
   make build-api && make run-api
   ```

## Integration with Step 2

Once Step 1 passes (5/6+ browsers), proceed to full test suite:
```bash
# Step 2: Full test suite
FRONTEND_URL=http://localhost:3001 npx playwright test --config config/playwright.config.js --reporter=line
```

## Architecture Notes

- **Generated Code**: Controllers are auto-generated, must connect to `impl/` directory
- **Test Data**: Backend test users in `auth.py` must match Playwright expectations
- **CORS**: Frontend (3001) and Backend (8080) require proper CORS configuration
- **JWT**: Authentication returns proper JWT tokens for session management

## Last Updated
2025-09-12 - After successful CORS and authentication fixes