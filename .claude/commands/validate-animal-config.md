# /validate-animal-config

Performs end-to-end validation of the Animal Management UI against DynamoDB data using Playwright automation and AWS DynamoDB queries.

## Command Requirements

### Playwright Automation
- Use Playwright MCP to navigate to the frontend (http://localhost:3001 or configured FRONTEND_URL)
- Login with admin/admin123 credentials
- Navigate to Animal Management -> Chatbot Personalities page
- Wait for data to load and capture any errors in console
- Take screenshot for visual validation
- Extract displayed animal data from the UI (names, IDs, status)
- Click the "Configure" button for one of the animals to test detailed view access

### Role-Based Authentication Testing
- **AUTHORIZED ROLES** (should succeed):
  - admin/admin123 (admin role) - full access expected
  - zookeeper credentials (zookeeper role) - full access expected
- **UNAUTHORIZED ROLES** (should fail with appropriate errors):
  - student credentials (student role) - should be denied access
  - member credentials (member role) - should be denied access
  - visitor credentials (visitor role) - should be denied access
  - No authentication (anonymous) - should be denied access
- **Test Process**:
  - Test each role by logging out and logging in with different credentials
  - Verify unauthorized roles cannot access Animal Management -> Chatbot Personalities
  - Confirm appropriate error messages for access denied scenarios
  - Document specific error responses for each unauthorized role

### DynamoDB Validation
- Query the CMZ animals table using AWS DynamoDB scan
- Extract animal records (animalId, name, status, chatbot config)
- Format data for comparison with UI display

### Data Comparison
- Compare UI displayed animals vs DynamoDB records
- Check for missing animals (in DB but not UI)
- Check for phantom animals (in UI but not DB)
- Validate key fields match (names, status, basic config)

### Test Results
- SUCCESS: UI data matches DynamoDB with no console errors
- FAILURE: Mismatched data, missing records, or console errors
- Report specific discrepancies and error details

## Implementation Workflow

1. **Pre-Test System Verification**
   - **MANDATORY**: Read `ANY-PRE-TEST-ADVICE.md` and follow all health checks
   - **MANDATORY**: Review `VALIDATE-ANIMAL-CONFIG.md` for lessons learned from previous runs
   - Verify frontend is running on correct port (3000 or 3001)
   - Verify backend API health endpoint responds
   - Verify AWS DynamoDB connectivity and table access
   - Only proceed if all systems are confirmed operational

2. **Frontend Setup - Admin Testing**
   - Navigate to FRONTEND_URL (determined from pre-test verification)
   - Login with admin/admin123
   - Navigate to Animal Management -> Chatbot Personalities
   - Wait for page load and data rendering

3. **UI Data Extraction and Configure Button Test**
   - Extract animal list from rendered page
   - Capture animal names, IDs, status indicators
   - Check for loading states or error messages
   - Take screenshot for documentation
   - Click "Configure" button for one of the animals
   - Verify configure page loads successfully for admin user
   - Take screenshot of configure page

4. **Role-Based Authentication Testing**
   - **Test Authorized Roles**:
     - Keep admin session (already tested)
     - Log out and test zookeeper credentials if available
   - **Test Unauthorized Roles**:
     - Log out and attempt login with student credentials
     - Verify Animal Management access is denied
     - Test member credentials - verify access denied
     - Test visitor credentials - verify access denied
     - Test anonymous access - verify login required
   - Document specific error messages for each role

5. **DynamoDB Query**
   - Use AWS profile 'cmz' and region 'us-west-2'
   - Scan animals table for all records
   - Extract relevant fields for comparison
   - Handle pagination if needed

6. **Validation Logic**
   - Compare count of animals (UI vs DB)
   - Match animals by ID/name
   - Validate status consistency
   - Report any discrepancies
   - Verify configure button functionality worked

7. **Error Handling**
   - Capture browser console errors
   - Handle network timeouts
   - Manage AWS credential issues
   - Provide clear failure diagnostics

7. **Post-Test Documentation Update**
   - **MANDATORY**: Update `VALIDATE-ANIMAL-CONFIG.md` with new findings
   - Document any mistakes made during this test run
   - Add lessons learned about port detection, authentication issues, etc.
   - Record any system setup issues encountered and their solutions
   - Update recommendations based on actual experience

## Expected Usage

```bash
/validate-animal-config
```

## Configuration

- **Frontend URL**: Uses FRONTEND_URL environment variable or defaults to http://localhost:3001
- **AWS Profile**: Uses 'cmz' profile with us-west-2 region
- **Timeout**: 30 seconds for page loads, 60 seconds for DynamoDB queries
- **Credentials**: admin/admin123 for frontend authentication

## Success Criteria

✅ **PASS**:
- UI displays all animals from DynamoDB for authorized users (admin/zookeeper)
- No missing or phantom records
- Key fields match between UI and DB
- No console errors during navigation
- Configure button works and loads animal configuration page
- **Role-based access control working**:
  - Admin and zookeeper users can access Animal Management
  - Student, member, visitor, and anonymous users are denied access
  - Appropriate error messages shown for unauthorized access attempts

❌ **FAIL**:
- Data mismatches between UI and DynamoDB
- Animals missing from UI that exist in DB
- Animals in UI that don't exist in DB
- Console errors during page load or navigation
- Configure button fails to load animal configuration
- **Role-based access control failures**:
  - Unauthorized users can access Animal Management
  - Missing or incorrect error messages for access denial
  - Admin or zookeeper users denied legitimate access

## Output Format

```
🔍 ANIMAL CONFIG VALIDATION RESULTS

📊 Database Query:
- Found X animals in DynamoDB
- Sample: [animal1, animal2, animal3...]

🌐 UI Validation - Admin Access:
- Displayed Y animals on page
- Sample: [ui_animal1, ui_animal2, ui_animal3...]
- Configure button test: SUCCESS/FAILED

🔐 Role-Based Access Control:
- ✅ ADMIN ACCESS: SUCCESS/FAILED
- ✅ ZOOKEEPER ACCESS: SUCCESS/FAILED (if tested)
- ❌ STUDENT ACCESS: DENIED/FAILED (should be denied)
- ❌ MEMBER ACCESS: DENIED/FAILED (should be denied)
- ❌ VISITOR ACCESS: DENIED/FAILED (should be denied)
- ❌ ANONYMOUS ACCESS: DENIED/FAILED (should be denied)

✅ MATCHES: [list of matching animals]
❌ MISSING FROM UI: [animals in DB but not UI]
⚠️ PHANTOM IN UI: [animals in UI but not DB]
🚨 CONSOLE ERRORS: [any browser errors]
🔧 CONFIGURE FUNCTIONALITY: [configure button test results]

RESULT: PASS/FAIL with specific details
```