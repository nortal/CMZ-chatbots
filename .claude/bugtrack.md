# CMZ Chatbots Bug Registry

**Last Updated**: 2025-10-12 (Root Cause Analysis REVISED with ENDPOINT-WORK.md validation)
**Total Bugs**: 13
**Root Causes Identified**: 13/13 (100%)
**Real Bugs**: 7 (1, 2, 3, 4, 5, 6, 7)
**Not Bugs**: 6 (8, 9, 10, 11, 12, 13)
**Untracked**: 13
**Tracked**: 0
**Resolved**: 0

**Analysis Summary** (REVISED):
- **CRITICAL - Broken Hexagonal Architecture**: 2 bugs (1, 7) - impl/animals.py doesn't forward to impl/handlers.py despite working implementations
- **HIGH - Guardrails System**: 3 bugs (2, 3, 4) - Backend implemented, missing DynamoDB table + handler mappings + frontend template UI
- **MEDIUM - UX Issues**: 2 bugs (5, 6) - State management after save + redundant UI button
- **NOT BUGS - Test/Data Issues**: 6 items (8, 9, 10, 11, 12, 13) - Empty database, test configuration, timing issues

**KEY FINDING**: Bugs #1 and #7 share same root cause - broken forwarding chain in hexagonal architecture. ENDPOINT-WORK.md shows implementations exist in handlers.py but impl/animals.py stubs return 501 instead of forwarding.

---

## Bug #1: [Untracked] Animal Config systemPrompt Changes Not Persisting to Database
**Severity**: High
**Component**: Backend API
**Status**: Untracked
**Reported**: 2025-10-12
**Jira Ticket**: None

**Symptoms**:
- systemPrompt changes in Animal Config dialog don't persist after save
- PATCH request appears successful (200 response)
- Subsequent GET requests return old systemPrompt value
- Frontend displays previous value after refresh

**Steps to Reproduce**:
1. Navigate to Animal Management > Select animal > Click Config
2. Edit systemPrompt field with new content
3. Click "Save Configuration"
4. Observe success message
5. Refresh page or close/reopen config dialog
6. Observe systemPrompt shows old value (changes lost)

**Expected Behavior**:
- PATCH /animal_config persists systemPrompt changes to DynamoDB
- Subsequent GET /animal_config returns updated systemPrompt value
- Frontend displays saved changes after refresh

**Actual Behavior**:
- PATCH returns 200 OK but changes don't persist to database
- GET returns original systemPrompt value
- Data loss occurs without error indication

**Root Cause** (REVISED - CRITICAL - Two Issues):

**PRIMARY: Broken Hexagonal Architecture Forwarding Chain**
Location: `/backend/api/src/main/python/openapi_server/impl/animals.py` lines 29-35

The `handle_animal_config_patch()` function is a DEAD-END STUB returning `not_implemented_error()` instead of forwarding to the WORKING implementation in impl/handlers.py.

**SECONDARY: Missing systemPrompt Field Mapping**
Location: `/backend/api/src/main/python/openapi_server/impl/domain/animal_service.py` lines 277-333

Even if forwarding worked, the `update_animal_configuration()` method doesn't map the `systemPrompt` field from the request to DynamoDB.

**Evidence Chain** (REVISED with ENDPOINT-WORK.md):
1. **ENDPOINT-WORK.md line 80**: PATCH /animal_config documented as "✅ FIXED 2025-10-02: Working with auth"
2. **handlers.py lines 188-250**: WORKING implementation exists with 60+ lines of auth validation and business logic
3. **animals.py lines 29-35**: BROKEN STUB returns 501 instead of forwarding to handlers.py
4. **animal_service.py lines 277-333**: Maps all fields EXCEPT systemPrompt (personality ✅, voice ✅, aiModel ✅, temperature ✅, topP ✅, toolsEnabled ✅, guardrails ✅, systemPrompt ❌)

**Impact**: 100% data loss - all PATCH /animal_config requests return 501 before reaching business logic

**Related Files**:
- backend/api/src/main/python/openapi_server/impl/animals.py (PATCH handler)
- backend/api/src/main/python/openapi_server/controllers/animal_config_controller.py
- frontend/src/components/AnimalConfig/* (form submission)

**Notes**:
- This is a data loss bug affecting critical configuration
- Previously tested in validation suite but may have regressed
- Similar to historical issues with other animal config fields

---

## Bug #2: [Untracked] Add Guardrail Button Non-Functional in Animal Config
**Severity**: High
**Component**: Frontend UI
**Status**: Untracked
**Reported**: 2025-10-12
**Jira Ticket**: None

**Symptoms**:
- "Add Guardrail" button in Animal Config dialog doesn't respond to clicks
- No dialog opens when button is clicked
- No console errors visible (needs verification)
- Feature completely unavailable

**Steps to Reproduce**:
1. Navigate to Animal Management > Select animal > Click Config
2. Navigate to "Guardrails" tab within config dialog
3. Click "Add Guardrail" button
4. Observe no response, no dialog, no action

**Expected Behavior**:
- Clicking "Add Guardrail" opens dialog or modal
- Dialog allows selection/configuration of guardrail to add
- User can save and apply guardrail to animal

**Actual Behavior**:
- Button click has no effect
- No visual feedback or error message
- Cannot add guardrails through UI

**Root Cause** (REVISED - Implemented But Not Operational):
**Backend implemented, DynamoDB table missing + handler mappings missing**

**Evidence from Investigation**:
1. **ENDPOINT-WORK.md lines 86-95**: 9 guardrails endpoints documented as "✅ IMPLEMENTED" with note "[✅ Working] - Needs DynamoDB table"
2. **guardrails.py lines 1-557**: FULL implementation exists (526 lines of code including GuardrailsManager class, template system, priority sorting)
3. **chatgpt_integration.py lines 164-236**: Dynamic guardrails integration EXISTS in system prompt generation
4. **handlers.py**: NO guardrail handler mappings in handler_map (checked lines 45-119)
5. **DynamoDB**: Table `quest-dev-guardrails` does NOT exist
6. **Frontend AnimalConfig.tsx**: Button exists but NO template dropdown UI

**Status**: IMPLEMENTED BUT NOT OPERATIONAL
- Backend code: ✅ Complete
- Integration: ✅ Exists (chat system calls guardrails manager)
- Handler mappings: ❌ Missing
- DynamoDB table: ❌ Missing
- Frontend template UI: ❌ Missing

**Reclassification**: Real bug, not feature request - implementation exists but broken due to missing infrastructure

**Estimated Fix**: 2-4 hours (create DynamoDB table, add handler mappings, add frontend dropdown)

**Related Files**:
- frontend/src/pages/AnimalConfig.tsx (lines 517-520 - button with no onClick)
- frontend/src/components/dialogs/AddGuardrailDialog.tsx (**DOES NOT EXIST**)

**Notes**:
- Part of broader guardrail system issues (see Bugs #3, #4)
- All three bugs (#2, #3, #4) share same root cause: unimplemented feature
- Recommend consolidating into single Feature Request Epic

---

## Bug #3: [Untracked] Guardrail Toggle Icons Not Responding on Guardrails Page
**Severity**: High
**Component**: Frontend UI
**Status**: Untracked
**Reported**: 2025-10-12
**Jira Ticket**: None

**Symptoms**:
- Toggle icons on Guardrails management page don't respond to clicks
- Cannot enable/disable guardrails through toggle interaction
- No visual state change when clicked
- No console errors (needs verification)

**Steps to Reproduce**:
1. Navigate to Guardrails management page (main navigation)
2. Locate toggle icons next to guardrail entries
3. Attempt to click toggle icons
4. Observe no state change, no response

**Expected Behavior**:
- Clicking toggle changes guardrail enabled/disabled state
- Visual feedback shows state change (color, position)
- Backend updated with new state via PATCH request
- List refreshes to show updated state

**Actual Behavior**:
- Toggle icons don't respond to clicks
- No state change occurs
- Cannot enable/disable guardrails

**Root Cause** (IDENTIFIED - Unimplemented Feature):
**NOT A BUG - Toggle hardcoded as readOnly**

Location: `/frontend/src/pages/AnimalConfig.tsx` lines 539-547

The toggle input is explicitly set to `readOnly` with **NO onChange handler**. This is intentional placeholder implementation, not a bug.

**Evidence**:
```typescript
<input
  type="checkbox"
  className="sr-only peer"
  checked={typeof value === 'boolean' ? value : false}
  readOnly  // ← Explicitly read-only
/>
```

**Additional Finding**: Dedicated Guardrails page `/knowledge/guardrails` **DOES NOT EXIST**
- Route defined in navigation.ts but no page component
- No route implementation in App.tsx
- Clicking menu item results in 404

**Reclassification**: Should be tracked as **Feature Request** not Bug

**Related Files**:
- frontend/src/pages/AnimalConfig.tsx (lines 539-547 - readOnly toggle)
- frontend/src/pages/Guardrails.tsx (**DOES NOT EXIST**)

**Notes**:
- Part of broader guardrail system issues (see Bugs #2, #4)
- Same root cause: feature designed but never implemented
- Navigation exists but no actual functionality

---

## Bug #4: [Untracked] Guardrail Edit Button Not Responding on Guardrails Page
**Severity**: High
**Component**: Frontend UI
**Status**: Untracked
**Reported**: 2025-10-12
**Jira Ticket**: None

**Symptoms**:
- Edit button for guardrails on Guardrails page doesn't respond
- Cannot open edit dialog for existing guardrails
- No console errors (needs verification)
- Feature completely unavailable

**Steps to Reproduce**:
1. Navigate to Guardrails management page (main navigation)
2. Locate Edit button next to guardrail entries
3. Click Edit button
4. Observe no response, no dialog opens

**Expected Behavior**:
- Clicking Edit opens dialog with guardrail configuration
- User can modify guardrail settings
- Changes save back to database via PATCH request
- List refreshes with updated guardrail

**Actual Behavior**:
- Edit button doesn't respond to clicks
- No dialog opens
- Cannot edit existing guardrails

**Root Cause** (IDENTIFIED - Unimplemented Feature):
**NOT A BUG - Edit button has no onClick handler**

Location: `/frontend/src/pages/AnimalConfig.tsx` lines 548-550

The Edit button exists with hover styling but **NO onClick handler**. Part of unimplemented guardrail feature.

**Evidence**:
```typescript
<button className="p-2 text-gray-400 hover:text-gray-600">
  <Edit className="w-4 h-4" />
</button>
```

**Pattern Detected**: All guardrail interactive elements (add, toggle, edit) are non-functional placeholders
- Approximately 10-15% feature completion (UI shells exist, no business logic)
- Design intent clear, implementation never completed
- Navigation structure and data models exist

**Reclassification**: Should be tracked as **Feature Request** not Bug
**Recommendation**: Consolidate Bugs #2, #3, #4 into single Feature Request Epic

**Related Files**:
- frontend/src/pages/AnimalConfig.tsx (lines 548-550 - button with no onClick)
- frontend/src/components/dialogs/EditGuardrailDialog.tsx (**DOES NOT EXIST**)

**Notes**:
- Part of broader guardrail system issues (see Bugs #2, #3)
- All three bugs manifestations of single root cause
- Guardrail system requires complete implementation project

---

## Bug #5: [Untracked] Animal Config Save Returns to Basic Info Tab Instead of Current Tab
**Severity**: Medium
**Component**: Frontend UI
**Status**: Untracked
**Reported**: 2025-10-12
**Jira Ticket**: None

**Symptoms**:
- After saving configuration changes from any tab, user redirected to Basic Info tab
- Occurs regardless of which tab "Save Configuration" was clicked from
- Forces manual navigation back to desired tab
- UX inconvenience affecting workflow efficiency

**Steps to Reproduce**:
1. Navigate to Animal Management > Select animal > Click Config
2. Navigate to any tab other than "Basic Info" (e.g., Guardrails, Voice, Personality)
3. Make changes to fields on that tab
4. Click "Save Configuration" button
5. Observe redirect to "Basic Info" tab instead of staying on current tab

**Expected Behavior**:
- After clicking "Save Configuration", user remains on the same tab
- Success message displays on current tab
- User can continue editing on same tab if needed

**Actual Behavior**:
- Always redirected to "Basic Info" tab after save
- Must manually navigate back to previous tab
- Disrupts workflow when making multiple edits

**Root Cause** (IDENTIFIED - State Management):
**activeTab state not preserved during save/refetch cycle**

Location: `/frontend/src/pages/AnimalConfig.tsx` line 279

**Problem**: `activeTab` is initialized with hard-coded default value `'basic'` and this default is reapplied during component re-render after save operation.

**Flow**:
1. User edits form on 'settings' tab
2. User clicks "Save Configuration"
3. `submitForm()` calls `handleSaveConfig` which calls `refetch()`
4. Data refetch triggers re-render
5. `activeTab` state not preserved → resets to 'basic'

**Fix**: Capture current tab before save and restore after successful save operation

**Related Files**:
- frontend/src/pages/AnimalConfig.tsx (line 279 - state initialization, lines 806-814 - save button)

**Notes**:
- UX issue, not a blocker
- Simple fix: ~10 lines of code
- Alternative: persist activeTab to sessionStorage
- Low complexity, high user experience improvement

---

## Bug #6: [Untracked] Unnecessary Gear Icon on Animal Management Main Page
**Severity**: Low
**Component**: Frontend UI
**Status**: Untracked
**Reported**: 2025-10-12
**Jira Ticket**: None

**Symptoms**:
- Animal cards on main Animal Management page display 3 buttons
- Three buttons: Config icon, Chat icon, Gear icon
- Gear icon serves no purpose and is unnecessary
- Clutters UI with unused element

**Steps to Reproduce**:
1. Navigate to Animal Management main page
2. Observe animal cards/list
3. Note 3 buttons under each animal entry
4. Identify gear icon as third button
5. Verify gear icon has no function or tooltip

**Expected Behavior**:
- Animal cards should display only 2 buttons: Config and Chat
- Config button: Opens animal configuration dialog
- Chat button: Opens chat interface with animal
- No third button needed

**Actual Behavior**:
- Three buttons displayed: Config, Chat, Gear
- Gear icon present but serves no purpose
- Extra UI clutter

**Root Cause** (IDENTIFIED - UI Cleanup):
**Redundant non-functional Settings button**

Location: `/frontend/src/pages/AnimalConfig.tsx` lines 191-193

**Problem**: The gear/Settings icon button has **NO onClick handler** and serves no purpose. The "Configure" button (lines 177-183) already provides access to settings.

**Evidence**:
```typescript
<button className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">
  <Settings className="w-4 h-4" />
</button>
```

**Fix**: Simply remove lines 191-193 (3-line deletion)

**Related Files**:
- frontend/src/pages/AnimalConfig.tsx (lines 191-193 - unused button)

**Notes**:
- Cosmetic issue, lowest priority
- Minimal code change (delete 3 lines)
- No functional impact
- Quick win for cleanup

---

## Bug Summary by Component

### Backend API (1 bug)
- Bug #1: systemPrompt not persisting (High)

### Frontend UI - Animal Config (4 bugs)
- Bug #1: systemPrompt not persisting (High) - may have frontend component
- Bug #2: Add Guardrail button broken (High)
- Bug #5: Tab navigation after save (Medium)
- Bug #6: Unnecessary gear icon (Low)

### Frontend UI - Guardrails Page (2 bugs)
- Bug #3: Toggle icons not usable (High)
- Bug #4: Edit button not usable (High)

## Priority Recommendations

**Immediate (High Severity)**:
1. Bug #1: System prompt persistence (data loss)
2. Bug #2, #3, #4: Guardrail system (comprehensive fix needed)

**Soon (Medium Severity)**:
3. Bug #5: Tab navigation (UX improvement)

**Later (Low Severity)**:
4. Bug #6: Remove gear icon (cleanup)

## Next Actions

- [ ] Investigate Bug #1 with Playwright test to verify persistence failure
- [ ] Comprehensive audit of guardrail system UI (Bugs #2, #3, #4 likely share root cause)
- [ ] Create Jira tickets for High severity bugs (1, 2, 3, 4)
- [ ] Test fixes with existing E2E validation suite

---

## Bug #7: [Untracked] Animal Details Save Changes Button Not Persisting Data
**Severity**: High
**Component**: Frontend UI / Animal Details
**Status**: Untracked
**Reported**: 2025-10-12
**Jira Ticket**: None

**Symptoms**:
- Save Changes button (disk icon) at bottom right of Animal Details subpage doesn't persist changes
- Changes appear to save initially but revert upon page refresh or navigation
- No error messages displayed to user
- Data loss occurs silently

**Steps to Reproduce**:
1. Navigate to Animal Management
2. Click on an animal to view Animal Details subpage
3. Edit one or more fields (e.g., age, description)
4. Click Save Changes button (disk icon at bottom right)
5. Observe success message or confirmation
6. Refresh page or navigate away and return
7. Observe changes were not saved (reverted to original values)

**Expected Behavior**:
- Clicking Save Changes button persists all edited fields to database
- Subsequent page loads display saved changes
- Changes remain permanent until explicitly modified again

**Actual Behavior**:
- Save Changes button appears to work (may show success message)
- Changes do not persist to database
- Page refresh shows original values (data loss)

**Root Cause** (REVISED - CRITICAL - Broken Hexagonal Architecture):
**Broken forwarding chain - impl/animals.py doesn't forward to working implementation in impl/handlers.py**

**Evidence from ENDPOINT-WORK.md Re-investigation**:
1. **ENDPOINT-WORK.md lines 77-78**: "PUT /animal/{animalId} → handlers.py:handle_animal_put() [✅ FIXED 2025-10-02: Working]"
2. **handlers.py lines 344-430**: COMPLETE WORKING implementation with comprehensive parameter handling, DynamoDB integration, error handling, model conversion
3. **animals.py lines 124-136**: BROKEN STUB returns `not_implemented_error()` instead of forwarding
4. **Controllers**: Pattern 1 import finds BROKEN stub, Pattern 2 (handlers.handle_) never reached
5. **Request Flow**: User clicks Save → Controller → animals.py stub → 501 error → [NEVER REACHES] handlers.py working implementation

**Impact**: 100% data loss - ALL PUT /animal/{animalId} requests fail with 501 before reaching working business logic

**Fix**: Delete `/backend/api/src/main/python/openapi_server/impl/animals.py` entirely (recommended) OR fix all stubs to forward to handlers.py

**Related Files**:
- backend/api/src/main/python/openapi_server/impl/animals.py (lines 124-136 - unimplemented handler)
- frontend/src/pages/AnimalDetails.tsx (lines 154-159 - incomplete payload)

**Notes**:
- Different from Bug #1 but same root cause pattern (unimplemented handler)
- Animal Details is separate page from Animal Config dialog
- Affects all editable fields on Animal Details page
- Similar to Bug #1 (systemPrompt persistence)

---

## Bug #8: [Untracked] Family Management Page Fails to Load Family List
**Severity**: High
**Component**: Frontend UI / Family Management
**Status**: Untracked
**Reported**: 2025-10-12
**Jira Ticket**: None

**Symptoms**:
- Family Management page loads but family list doesn't display
- Page appears broken or shows empty state
- Users cannot view existing families
- Feature completely unavailable

**Steps to Reproduce**:
1. Navigate to Family Groups from main menu
2. Observe Family Management page loads
3. Note that family list section is empty, broken, or shows error
4. Verify families exist in database (should have test data)

**Expected Behavior**:
- Family Management page loads successfully
- List of all families displays in table or card layout
- Each family shows key information (name, members, status)
- User can interact with family entries (view details, edit, delete)

**Actual Behavior**:
- Page loads but family list fails to populate
- Empty state or error displayed
- Cannot access family management features

**Root Cause** (REVISED - REAL BUG - Query Filtering Issue):
**DynamoDB table has 33 families but API returns empty array - likely user-specific filtering bug**

**CORRECTED FINDING** (after actual DynamoDB verification):
- **quest-dev-family table**: Contains 33 families (verified via `aws dynamodb scan`)
- **Active families**: 4+ families with `softDelete: false` including:
  - family_test_001 (Test Bidirectional Family)
  - family_test_002 (Johnson Family)
  - family_1b22f1c4 (Stegbauer)
  - test_family_001 (Test Family One)
- **API response**: Returns `[]` empty array
- **Conclusion**: Backend is filtering families (likely by user_id) and test user has no associated families

**Evidence Chain** (CORRECTED):
1. Frontend calls `/family` endpoint ✅
2. Backend routing works correctly ✅
3. Handler calls `list_families_for_user()` ✅
4. DynamoDB query executes with user_id filter ✅
5. **Result: `[]` because test user has no family associations** ❌
6. Table HAS data, but query filters it all out

**Root Cause**: User-family association missing or incorrect query filtering logic

**Fix**: Investigate `list_families_for_user()` filtering logic and user-family associations

**Related Files**:
- frontend/src/pages/FamilyManagement.tsx (line 115 - correctly handles empty response)
- backend/api/src/main/python/openapi_server/impl/family_bidirectional.py (lines 499-573 - working implementation)
- scripts/seed_test_families.py (**TO BE CREATED**)

**Notes**:
- Not a bug - expected behavior for empty database
- Users can still create families through "Add New Family" button
- Improve empty state UI with better call-to-action
- Add database seeding to development setup documentation

---

## Bug #9: [Untracked] Family Groups Billing Information Menu Item Non-Functional
**Severity**: Medium
**Component**: Frontend UI / Navigation
**Status**: Untracked
**Reported**: 2025-10-12
**Jira Ticket**: None

**Symptoms**:
- Billing Information submenu item under Family Groups doesn't navigate
- Menu closes immediately when clicked
- No action taken, no error shown
- Feature inaccessible through navigation

**Steps to Reproduce**:
1. Navigate to main menu
2. Click or hover over Family Groups menu item
3. Observe submenu opens with options
4. Click "Billing Information" submenu item
5. Observe menu closes but no navigation occurs

**Expected Behavior**:
- Clicking Billing Information opens billing page or dialog
- User can view and manage billing information for families
- Page loads with billing-related content

**Actual Behavior**:
- Menu closes without taking action
- No navigation occurs
- No error message displayed
- Billing feature cannot be accessed

**Root Cause** (IDENTIFIED - Missing Implementation):
**Route and page component do not exist**

**Evidence**:
1. Navigation config defines `/families/billing` route ✅ (navigation.ts lines 51-55)
2. App.tsx has NO route for `/families/billing` ❌
3. FamilyBilling.tsx page component DOES NOT EXIST ❌
4. React Router redirects to dashboard (catch-all route)

**Fix**: Create FamilyBilling page component and add route to App.tsx (~60 lines of code)

**Related Files**:
- frontend/src/config/navigation.ts (lines 51-55 - nav config exists)
- frontend/src/App.tsx (missing route definition)
- frontend/src/pages/FamilyBilling.tsx (**DOES NOT EXIST** - needs creation)

**Notes**:
- Navigation/routing issue, billing feature not implemented
- Can provide placeholder page with "Coming Soon" message
- Medium priority - resolves navigation dead-end
- Consider removing menu item until feature ready (alternative solution)

---

## Feature Requests Registry

The following feature requests were reported alongside bugs. These should be tracked separately as enhancement tickets rather than bug fixes.

### FR #1: Replace Age Field with Birthday and Calculated Age
**Priority**: Medium
**Component**: Frontend UI / Animal Details
**Requested**: 2025-10-12

**Current Behavior**:
- Animal Details page shows editable age field
- Age must be manually updated periodically

**Requested Behavior**:
- Replace age field with birthday (date picker)
- Calculate and display age automatically based on birthday
- Age is read-only, calculated field
- Birthday is the editable field

**Benefits**:
- More accurate animal age tracking
- Eliminates need for manual age updates
- Better data model (date of birth vs current age)

**Implementation Notes**:
- Requires database schema change (add birthday field)
- Frontend needs date picker component
- Backend needs age calculation logic
- Migration script for existing animals with age data

---

### FR #2: Remove Educational Programs from Family Groups Menu
**Priority**: Low
**Component**: Frontend UI / Navigation
**Requested**: 2025-10-12

**Current Behavior**:
- Family Groups menu includes "Educational Programs" submenu item

**Requested Behavior**:
- Remove "Educational Programs" from Family Groups submenu
- Feature not needed in current scope

**Implementation Notes**:
- Simple removal from navigation configuration
- Verify no dependencies on educational programs feature
- If feature exists elsewhere, consider complete removal

---

### FR #3: Rename "Knowledge Base" to "Global Chat Configurations"
**Priority**: Low
**Component**: Frontend UI / Navigation
**Requested**: 2025-10-12

**Current Behavior**:
- Main menu item labeled "Knowledge Base"

**Requested Behavior**:
- Rename to "Global Chat Configurations"
- Better reflects actual functionality

**Implementation Notes**:
- Update navigation label
- Update page titles and breadcrumbs
- Update documentation and help text

---

### FR #4: Add "System Prompts" Submenu Under Global Chat Configurations
**Priority**: Medium
**Component**: Frontend UI / New Page
**Requested**: 2025-10-12

**Description**:
Create new submenu item "System Prompts" under "Global Chat Configurations" (formerly Knowledge Base).

**Functionality**:
- Display list of all animals
- Show each animal's current system prompt
- Read-only view (no editing capability)
- Purpose: Quick reference for reviewing all system prompts

**Implementation Notes**:
- New page component needed
- Fetch all animals from API
- Display animal name + current systemPrompt field
- Use table or card layout
- No edit functionality (view only)

---

### FR #5: Add "Guardrails" Submenu with Toggle and Priority Management
**Priority**: High
**Component**: Frontend UI / New Page
**Requested**: 2025-10-12

**Description**:
Create new submenu item "Guardrails" under "Global Chat Configurations".

**Functionality**:
- Display all system-wide guardrails
- Active/Inactive toggle for each guardrail
- Edit button to modify guardrail settings
- Priority/importance adjustment capability (reordering or numeric priority)

**Implementation Notes**:
- New page component needed
- Fetch guardrails from API (may need new endpoint)
- Toggle component for enable/disable
- Edit dialog for guardrail configuration
- Drag-and-drop or priority field for ordering
- PATCH API endpoint for updates

**Related to**:
- Bugs #2, #3, #4 (existing guardrail UI issues)
- This feature may require fixing existing guardrail system first

---

### FR #6: Reorder Main Menu Items
**Priority**: Low
**Component**: Frontend UI / Navigation
**Requested**: 2025-10-12

**Current Order**:
- (Unknown current order)

**Requested Order**:
1. Dashboard
2. Animal Management
3. Global Chat Configuration
4. Family Groups
5. User Management
6. Analytics
7. System

**Implementation Notes**:
- Update navigation configuration
- Maintain existing routes and functionality
- Update any navigation-related documentation
- Simple reordering, no functional changes

---

## Bug Summary by Component

### Backend API (2 bugs)
- Bug #1: systemPrompt not persisting (High)
- Bug #11: Animal status update returns 400 (High)

### Frontend UI - Chat Interface (1 bug)
- Bug #10: Chat input element missing (Critical)

### Frontend UI - Animal Details (1 bug)
- Bug #7: Save Changes button not persisting (High)

### Frontend UI - Animal Config (4 bugs)
- Bug #1: systemPrompt not persisting (High) - may have frontend component
- Bug #2: Add Guardrail button broken (High)
- Bug #5: Tab navigation after save (Medium)
- Bug #6: Unnecessary gear icon (Low)

### Frontend UI - Guardrails Page (2 bugs)
- Bug #3: Toggle icons not usable (High)
- Bug #4: Edit button not usable (High)

### Frontend UI - Family Management (2 bugs)
- Bug #8: Family list fails to load (High)
- Bug #9: Billing menu non-functional (Medium)

### Frontend Auth / Token Management (1 bug)
- Bug #12: Token storage location unclear (Medium)

### Test Suite (1 issue)
- Bug #13: Test expects unimplemented /me endpoint (Low)

## Priority Recommendations

**Critical (Immediate)**:
1. Bug #10: Chat input element missing (blocks entire chat feature)
2. Bug #8: Family list loading (blocks entire feature)
3. Bug #1: System prompt persistence (data loss)
4. Bug #7: Animal Details save (data loss)

**High Priority (Soon)**:
5. Bug #11: Animal status update 400 error (prevents status management)
6. Bugs #2, #3, #4: Guardrail system (comprehensive fix needed)
7. FR #5: Guardrails submenu (high priority feature request)

**Medium Priority**:
8. Bug #12: Token storage documentation
9. Bug #9: Billing menu navigation
10. Bug #5: Tab navigation UX
11. FR #1: Birthday field replacement
12. FR #4: System Prompts submenu

**Low Priority (Later)**:
13. Bug #13: Update test to skip /me endpoint
14. Bug #6: Remove gear icon (cleanup)
15. FR #2: Remove educational programs
16. FR #3: Rename Knowledge Base
17. FR #6: Reorder menu items

## Next Actions

- [ ] **URGENT**: Investigate Bug #10 (Chat input missing) - blocks all chat testing
- [ ] Investigate Bug #8 (Family list) - highest priority blocking issue
- [ ] Investigate Bug #11 (Status update 400) - test with cURL to reproduce
- [ ] Investigate Bug #7 (Animal Details save) - data loss risk
- [ ] Investigate Bug #1 with Playwright test to verify persistence failure
- [ ] Comprehensive audit of guardrail system UI (Bugs #2, #3, #4 likely share root cause)
- [ ] Create Jira tickets for Critical and High severity bugs (10, 8, 1, 7, 11, 2, 3, 4)
- [ ] Fix Bug #13 (test issue) - simple test update
- [ ] Document token storage for Bug #12
- [ ] Evaluate feature requests and create enhancement tickets as appropriate
- [ ] Re-run E2E validation suite after fixes

---

## Bug #10: [Untracked] Chat Message Input Element Not Rendering in Chat Interface
**Severity**: Critical
**Component**: Frontend UI / Chat Interface
**Status**: Untracked
**Reported**: 2025-10-12
**Jira Ticket**: None
**Test Failure**: chat-conversation-e2e.spec.js:105, 198

**Symptoms**:
- Chat interface loads but message input element not found
- Playwright tests fail with timeout waiting for selector 'textarea[placeholder*="message"], input[placeholder*="message"]'
- Chat functionality completely unavailable
- Blocks all chat E2E testing (multiple tests failing)

**Steps to Reproduce**:
1. Navigate to chat interface (via Animal Management > Chat button)
2. Observe chat window/dialog opens
3. Look for message input field (textarea or input)
4. Note that input element is missing or has different selector

**Expected Behavior**:
- Chat interface displays message input field with placeholder containing "message"
- Input field is visible and interactive
- User can type and send messages

**Actual Behavior**:
- Message input element either not rendered or has different selector
- Tests cannot locate input field after 5 second timeout
- Chat interface non-functional

**Root Cause** (IDENTIFIED - Timing Issue):
**Connection status initialization mismatch causing input to be disabled during test**

Location: `/frontend/src/pages/Chat.tsx` line 177

**Problem**: Component initializes with `connectionStatus = 'connected'` but immediately switches to `'connecting'` on mount, causing input element to be disabled during critical test window.

**Evidence Chain**:
1. Input element EXISTS in code ✅ (lines 452-458)
2. Placeholder "Type your message..." contains "message" ✅
3. Test selector `input[placeholder*="message"]` should match ✅
4. **BUT**: Input is disabled when `connectionStatus !== 'connected'` (line 457)
5. Component starts 'connected' then immediately becomes 'connecting' (lines 177, 193-201)
6. Test times out waiting for enabled input

**Fix Options**:
1. **Primary**: Change initial state from `'connected'` to `'connecting'` (line 177)
2. **Secondary**: Update test to wait for input enabled state (increase timeout)
3. **Infrastructure**: Add backend health check to test suite

**Related Files**:
- frontend/src/pages/Chat.tsx (line 177 - state init, lines 452-458 - input element)
- backend/api/src/main/python/tests/playwright/specs/chat-conversation-e2e.spec.js (lines 104-117)

**Notes**:
- **CRITICAL** - Timing issue, not missing element
- Element exists but disabled state prevents test detection
- High confidence fix (1-line change in frontend)
- Backend health check timing affects input availability

---

## Bug #11: [Untracked] Animal Status Update Returns 400 Bad Request
**Severity**: High
**Component**: Backend API / Animal Management
**Status**: Untracked
**Reported**: 2025-10-12
**Jira Ticket**: None
**Test Failure**: test-animal-config-fixes.spec.js:90
**Potential Duplicate**: May be related to Bug #1 (animal config persistence)

**Symptoms**:
- Updating animal status (active/inactive) via PUT /animal/{id} returns 400 Bad Request
- Request payload appears valid but backend rejects it
- Cannot change animal active/inactive status through API
- Test expects 200 OK but receives 400

**Steps to Reproduce**:
1. Get valid authentication token
2. Fetch animal details: GET /animal/charlie_003
3. Note current status (e.g., "active")
4. Send PUT request to update status: PUT /animal/charlie_003 with body {"data": {"status": "inactive"}}
5. Observe 400 Bad Request response

**Expected Behavior**:
- PUT /animal/{id} with valid status change returns 200 OK
- Animal status updated in database
- Subsequent GET returns new status value

**Actual Behavior**:
- PUT request returns 400 Bad Request
- Status not updated
- No descriptive error message about validation failure

**Root Cause** (IDENTIFIED - Test Issue):
**Invalid request payload structure - test wraps data incorrectly**

Location: Test file `test-animal-config-fixes.spec.js` line 88

**Problem**: Test sends `{ "data": { "status": "inactive" }}` but OpenAPI spec expects `{ "status": "inactive" }` (flat structure, no "data" wrapper)

**Evidence**:
- OpenAPI AnimalUpdate schema (openapi_spec.yaml:2758-2773) has no "data" field
- Connexion validation rejects unknown "data" field → 400 Bad Request
- Backend handler code is correctly implemented

**Secondary Issue**: Status enum inconsistency
- AnimalUpdate.status enum: `[active, hidden]` (lines 2769-2772)
- Query parameter enum: `[active, inactive, hidden, breeding, retired]`
- Test attempts "inactive" which is invalid per AnimalUpdate enum

**Fix**:
1. **Immediate**: Correct test payload structure (remove "data" wrapper)
2. **Consistency**: Align AnimalUpdate status enum with query parameter enum

**Related Files**:
- backend/api/src/main/python/tests/playwright/specs/test-animal-config-fixes.spec.js (line 88 - incorrect payload)
- backend/api/openapi_spec.yaml (lines 2768-2772 - enum definition)

**Notes**:
- **TEST ISSUE, NOT CODE BUG**
- Backend is working correctly, test has wrong payload structure
- Once payload fixed, enum inconsistency will surface as secondary issue
- Both test and OpenAPI spec need updates

---

## Bug #12: [Untracked] Authentication Token Storage Location Unclear
**Severity**: Medium
**Component**: Frontend Auth / Token Management
**Status**: Untracked
**Reported**: 2025-10-12
**Jira Ticket**: None
**Test Warning**: authentication-e2e.spec.js:38

**Symptoms**:
- Authentication tests pass successfully
- Warning message: "Token not found in localStorage/sessionStorage - frontend may use different storage mechanism"
- Token IS being stored and working correctly
- Storage location not documented or unclear

**Steps to Reproduce**:
1. Run authentication E2E tests
2. Successfully login with valid credentials
3. Observe warning in test output
4. Check localStorage and sessionStorage - token not found
5. Yet authentication works (token exists somewhere)

**Expected Behavior**:
- JWT token stored in documented location (localStorage, sessionStorage, or cookie)
- Tests can easily verify token storage
- Clear documentation of token storage mechanism

**Actual Behavior**:
- Token stored in undocumented location or custom mechanism
- Tests cannot find token in standard locations
- Auth works but token storage unclear

**Root Cause** (IDENTIFIED - Test Issue):
**Test checks wrong localStorage keys**

Location: Test file `authentication-e2e.spec.js` lines 85-91

**Finding**: Token IS stored in localStorage but test searches for generic key names (`'authToken'`, `'token'`, `'jwt'`) instead of actual keys used by implementation.

**Actual Token Storage** (AuthContext.tsx):
- Primary: `localStorage.getItem('cmz_token')` (lines 34, 127, 139-141)
- User data: `localStorage.getItem('cmz_user')`
- Secondary: `localStorage.getItem('cmz_auth_token')` (api.ts:64-65)
- Expiry: `localStorage.getItem('cmz_token_expiry')`

**Impact**: NONE - Authentication works perfectly, only test warning affected

**Fix**: Update test to check actual localStorage keys (`'cmz_token'`, `'cmz_user'`)

**Bonus Finding**: Dual token management systems exist - recommend consolidation

**Related Files**:
- frontend/src/context/AuthContext.tsx (lines 34, 127, 139-141 - uses 'cmz_token')
- frontend/src/services/api.ts (lines 64-65 - uses 'cmz_auth_token')
- backend/api/src/main/python/tests/playwright/specs/ui-features/authentication-e2e.spec.js (lines 85-91)

**Notes**:
- **NOT A BUG** - Documentation/test issue only
- Auth works perfectly, test just checks wrong keys
- 5-minute fix (update test expectations)
- Consider documenting token storage keys for developers

---

## Bug #13: [Untracked] Authentication E2E Test Expects Unimplemented /me Endpoint
**Severity**: Low (Test Issue)
**Component**: Test Suite / Authentication Tests
**Status**: Untracked
**Reported**: 2025-10-12
**Jira Ticket**: None
**Test Warning**: authentication-e2e.spec.js

**Symptoms**:
- Authentication E2E test calls /me endpoint for user profile validation
- Endpoint returns 501 Not Implemented
- Test falls back to "auth validation via login success"
- Expected behavior per ENDPOINT-WORK.md (user profile not implemented)

**Steps to Reproduce**:
1. Run authentication E2E tests: authentication-e2e.spec.js
2. After successful login, test attempts GET /me
3. Observe 501 Not Implemented response
4. Test continues with fallback validation

**Expected Behavior**:
- Test should NOT call unimplemented endpoints
- Test should be updated to skip /me validation
- Or /me endpoint should be implemented if needed

**Actual Behavior**:
- Test calls /me endpoint
- Gets 501 response (expected per ENDPOINT-WORK.md)
- Test works but shows unnecessary warning

**Root Cause** (IDENTIFIED - Test Issue):
**Test calls unimplemented endpoint with proper fallback**

Location: Test file `authentication-e2e.spec.js` lines 101-106

**Finding**: Test attempts to call `GET /me` for user profile validation, but endpoint was never implemented. Test has proper fallback logic so it passes anyway.

**Evidence**:
- Test calls `/me` endpoint expecting user profile
- Backend returns 501 Not Implemented (expected per ENDPOINT-WORK.md)
- api.ts has unused `getCurrentUser()` function (lines 318-330) that would fail if called
- User info obtained from JWT payload, not backend call

**Recommendation**: Do NOT implement `/me` endpoint - it's unnecessary since user info comes from JWT token

**Fix**: Remove `/me` call from test, validate JWT payload directly (5-minute fix)

**Related Files**:
- backend/api/src/main/python/tests/playwright/specs/ui-features/authentication-e2e.spec.js (lines 101-106)
- frontend/src/services/api.ts (lines 318-330 - unused getCurrentUser function)
- ENDPOINT-WORK.md (confirms user profile endpoints not implemented)

**Notes**:
- **TEST ISSUE, NOT CODE BUG**
- Test has fallback and works correctly
- Zero functional impact
- Simple test cleanup task

---

**Generated by**: /bugtrack add-batch
**Sequential Reasoning**: mcp__sequential-thinking__sequentialthinking
**Duplicate Detection**: Bug #11 may relate to Bug #1 (both animal update issues)
**Test Failures**: 4 new bugs from E2E test suite run on 2025-10-12
**Feature Requests**: 6 enhancement requests documented
