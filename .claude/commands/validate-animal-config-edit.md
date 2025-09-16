# /validate-animal-config-edit

Performs end-to-end validation of the Animal Configuration Edit functionality using Playwright automation, focusing on the detailed configuration and editing workflow for animal chatbot personalities.

## Command Requirements

### Prerequisite Setup
- **MANDATORY**: Run `/validate-animal-config` first to ensure basic animal listing works
- **MANDATORY**: Read `ANY-PRE-TEST-ADVICE.md` for system health checks
- **MANDATORY**: Review `VALIDATE-ANIMAL-CONFIG-EDIT.md` for lessons learned from previous edit validation runs
- **MANDATORY**: Ensure at least one animal exists in the system for editing
- **MANDATORY**: Verify admin authentication is working.  If there is an account logged in at the start,  log out and re-authenitcate

### Playwright Automation - Edit Flow
- Use Playwright MCP to navigate to Animal Management -> Chatbot Personalities
- Login as admin/admin123 (or maintain existing admin session)
- Select one animal from the list (preferably with existing configuration)
- Click the "Configure" button for the selected animal
- Navigate through the animal configuration/editing interface
- Test key editing functionality:
  - Personality settings modification
  - Chatbot behavior configuration
  - Status updates
  - Save/update operations
- Verify changes persist after save
- Return to main animal list and confirm changes are reflected

### Configuration Testing Areas
- **Personality Configuration**:
  - Test personality trait modifications
  - Verify personality description updates
  - Check behavior pattern settings
- **Chatbot Settings**:
  - Response style configuration
  - Knowledge base integration settings
  - Conversation flow preferences
- **Status and Metadata**:
  - Active/inactive status toggles
  - Species information editing
  - Display name modifications
- **Validation Rules**:
  - Test required field validation
  - Check input format requirements
  - Verify error handling for invalid inputs

### Backend API Testing by Role
- **AUTHORIZED BACKEND ACCESS** (should succeed):
  - Admin users: All animal configuration API calls should work
  - Zookeeper users: All animal configuration API calls should work
- **UNAUTHORIZED BACKEND ACCESS** (should fail with 401/403):
  - Student users: Configuration API calls should be rejected
  - Member users: Configuration API calls should be rejected
  - Visitor users: Configuration API calls should be rejected
  - Anonymous users: Configuration API calls should be rejected
- **API Endpoints to Test**:
  - GET /animal_config?animalId=X (fetch configuration)
  - PATCH /animal_config/X (update configuration)
  - PUT /animal/X (update animal details)
  - Verify appropriate HTTP status codes for each role

### Data Persistence Validation
- **Save Operation Testing**:
  - Modify animal configuration
  - Save changes
  - Refresh page/navigate away and return
  - Verify all changes persisted correctly
- **DynamoDB Verification**:
  - Query animal record before changes
  - Apply modifications through UI
  - Query animal record after changes
  - Compare timestamps and modified fields
- **Audit Trail Verification**:
  - Check modification timestamps
  - Verify user attribution for changes
  - Validate audit log entries if available

## Implementation Workflow

1. **Pre-Test Validation**
   - Run basic animal listing validation first
   - Verify admin access to Animal Management
   - Identify target animal for editing (preferably one with existing config)
   - Take baseline screenshot of animal list

2. **Navigate to Edit Mode**
   - Click "Configure" button for selected animal
   - Wait for configuration page to load completely
   - Capture any console errors during navigation
   - Take screenshot of configuration interface

3. **Configuration Interface Testing**
   - **Field Identification**:
     - Identify all editable fields
     - Document field types and validation rules
     - Test field accessibility and functionality
   - **Modification Testing**:
     - Make test modifications to various fields
     - Test different input types and formats
     - Verify real-time validation feedback
   - **Save Operation**:
     - Attempt to save valid changes
     - Test save with invalid data (should fail gracefully)
     - Verify success/error message display

4. **Persistence Verification**
   - **UI Persistence**:
     - Save changes and remain on page
     - Refresh browser and verify changes persist
     - Navigate away and return to verify persistence
   - **Database Persistence**:
     - Query DynamoDB before changes
     - Apply changes through UI
     - Query DynamoDB after changes
     - Compare database records for accuracy

5. **Integration Testing**
   - Return to main animal listing
   - Verify changes are reflected in the list view
   - Check that modified timestamp is updated
   - Confirm status changes are visible in main list

6. **Backend API Role-Based Testing**
   - **Authorized API Testing** (admin/zookeeper):
     - Test GET /animal_config?animalId=X with valid tokens
     - Test PATCH /animal_config/X with configuration updates
     - Test PUT /animal/X with animal detail updates
     - Verify all calls return 200/201 status codes
   - **Unauthorized API Testing** (student/member/visitor/anonymous):
     - Attempt same API calls with different role tokens
     - Verify calls return 401 Unauthorized or 403 Forbidden
     - Confirm error messages are appropriate
     - Test with no authentication token (anonymous)

7. **Error Handling Testing**
   - Test with invalid input data
   - Test with missing required fields
   - Test network interruption scenarios (if possible)
   - Verify appropriate error messages and recovery

8. **Role-Based Edit Access Testing**
   - **Authorized Users** (admin/zookeeper):
     - Should have full edit capabilities
     - All configuration options should be accessible
   - **Unauthorized Users** (student/member/visitor):
     - Should not be able to access edit mode
     - Configure buttons should be hidden or disabled

8. **Post-Test Documentation Update**
   - **MANDATORY**: Update `VALIDATE-ANIMAL-CONFIG-EDIT.md` with new findings
   - Document any mistakes made during this edit validation test run
   - Add lessons learned about configuration interface issues, save failures, etc.
   - Record any edit workflow problems encountered and their solutions
   - Update recommendations based on actual edit testing experience
   - Document specific field validation issues or data persistence problems
   - Record browser compatibility issues with configuration interface

## Expected Usage

```bash
/validate-animal-config-edit
```

## Configuration

- **Frontend URL**: Uses FRONTEND_URL environment variable or defaults to http://localhost:3001
- **AWS Profile**: Uses 'cmz' profile with us-west-2 region
- **Test Animal**: Automatically selects first available animal or uses specified animalId
- **Timeout**: 45 seconds for page loads, 90 seconds for save operations
- **Credentials**: admin/admin123 for frontend authentication

## Success Criteria

✅ **PASS - Configuration Interface**:
- Configure button successfully opens animal configuration page
- All configuration fields are accessible and functional
- Form validation works appropriately for different input types
- Save operation completes successfully with valid data
- Error handling works correctly for invalid inputs

✅ **PASS - Data Persistence**:
- Changes made through UI are saved to DynamoDB
- Modified timestamps are updated correctly
- Changes persist after browser refresh
- Changes are reflected in main animal listing
- Database queries show accurate updated data

✅ **PASS - User Experience**:
- No console errors during edit workflow
- Appropriate success/error messages displayed
- Navigation between edit and list views works smoothly
- Form fields are properly labeled and intuitive

✅ **PASS - Security & Access Control**:
- Only authorized users (admin/zookeeper) can edit configurations
- Unauthorized users cannot access edit functionality
- Data validation prevents malicious input
- Audit trails are maintained for changes
- **Backend API access control working**:
  - Admin and zookeeper API calls succeed (200/201 responses)
  - Student, member, visitor, anonymous API calls fail (401/403 responses)
  - Appropriate error messages for unauthorized API access

❌ **FAIL - Interface Issues**:
- Configure button doesn't work or leads to error page
- Configuration fields are inaccessible or non-functional
- Form validation is missing or incorrect
- Save operation fails with valid data
- Poor error handling for invalid inputs

❌ **FAIL - Data Issues**:
- Changes are not saved to database
- Data inconsistencies between UI and database
- Timestamps not updated correctly
- Changes don't persist after refresh
- Audit trail issues or missing change tracking

❌ **FAIL - Security Issues**:
- Unauthorized users can access edit functionality
- Data validation failures allow malicious input
- Missing access controls for sensitive configuration options
- **Backend API security failures**:
  - Unauthorized users can make successful API calls
  - Missing or incorrect HTTP status codes for access denial
  - Admin/zookeeper users unable to make legitimate API calls

## Output Format

```
🔧 ANIMAL CONFIG EDIT VALIDATION RESULTS

🎯 Target Animal:
- Animal ID: [animal_id]
- Name: [animal_name]
- Species: [species]
- Initial Status: [status]

🖥️ Configuration Interface:
- Configure button: SUCCESS/FAILED
- Page load: SUCCESS/FAILED
- Form accessibility: SUCCESS/FAILED
- Field validation: SUCCESS/FAILED

✏️ Edit Operations Tested:
- Personality settings: MODIFIED/FAILED
- Chatbot behavior: MODIFIED/FAILED
- Status changes: MODIFIED/FAILED
- Save operation: SUCCESS/FAILED

💾 Data Persistence:
- UI persistence (refresh): SUCCESS/FAILED
- Database persistence: SUCCESS/FAILED
- Audit timestamps: SUCCESS/FAILED
- List view updates: SUCCESS/FAILED

🔐 Access Control:
- Admin edit access: SUCCESS/FAILED
- Unauthorized access prevention: SUCCESS/FAILED
- Security validation: SUCCESS/FAILED

🔗 Backend API Testing:
- Admin API calls (GET/PATCH/PUT): SUCCESS/FAILED
- Zookeeper API calls: SUCCESS/FAILED (if tested)
- Student API rejection (401/403): SUCCESS/FAILED
- Member API rejection (401/403): SUCCESS/FAILED
- Visitor API rejection (401/403): SUCCESS/FAILED
- Anonymous API rejection (401/403): SUCCESS/FAILED

📊 Database Verification:
- Pre-modification state: [timestamp, key fields]
- Post-modification state: [timestamp, key fields]
- Change accuracy: SUCCESS/FAILED

🚨 Issues Found:
- Console errors: [list any errors]
- Validation failures: [list any issues]
- Data inconsistencies: [list any problems]

RESULT: PASS/FAIL with specific details and recommendations
```

## Integration with Main Validation

This command is designed to be run after `/validate-animal-config` to provide comprehensive end-to-end testing:

1. **First**: Run `/validate-animal-config` to validate basic listing and access
2. **Then**: Run `/validate-animal-config-edit` to validate detailed edit functionality
3. **Optional**: Run both commands in sequence for complete system validation

The edit validation builds upon the basic validation to ensure the full animal management workflow functions correctly for authorized users while maintaining appropriate security controls.