# VALIDATE-FAMILY-MANAGEMENT-ADVICE.md

Comprehensive advice for validating Family Management with bidirectional references, RBAC, and visible testing.

## Core Architecture Understanding

### Bidirectional Reference Model
```
Traditional (OLD):                 Bidirectional (NEW):
Family stores names directly   →   Family stores user IDs
parents: ["John", "Jane"]      →   parentIds: ["user_123", "user_456"]
students: ["Jimmy"]            →   studentIds: ["user_789"]

User has no family info        →   User stores family associations
                               →   familyIds: ["family_abc", "family_def"]
```

**Why This Matters**:
- **Data Normalization**: Single source of truth for user data
- **Consistency**: Changes to user propagate automatically
- **Multi-Family Support**: Users can belong to multiple families
- **Performance**: ID lookups are O(1) operations

### Role-Based Access Control (RBAC)
```python
# Backend Permission Model
def can_edit_family(user, family):
    return user.role == 'admin'

def can_view_family(user, family):
    return user.role == 'admin' or user.userId in family.all_member_ids

# Frontend Permission Flags
family.canEdit = user.role === 'admin'
family.canView = user.role === 'admin' || user.familyIds.includes(family.familyId)
```

**Permission Matrix**:
| Operation | Admin | Family Member | Non-Member |
|-----------|-------|---------------|------------|
| Create | ✅ | ❌ | ❌ |
| View | ✅ | ✅ (own) | ❌ |
| Edit | ✅ | ❌ | ❌ |
| Delete | ✅ | ❌ | ❌ |

## Visible Testing Strategy

### Why Visible Testing is Critical
1. **User Confidence**: Stakeholders can see exactly what's being tested
2. **Debug Clarity**: Visual feedback when tests fail
3. **UI Validation**: Confirms visual elements (buttons, icons, colors)
4. **Real Browser**: Tests actual rendering, not just DOM structure
5. **Screenshot Evidence**: Documents test execution for reports

### Playwright MCP vs Native Playwright
```javascript
// ❌ Native Playwright (invisible by default)
await page.fill('#email', 'admin@cmz.org');
await page.click('button[type="submit"]');

// ✅ Playwright MCP (always visible)
await mcp__playwright__browser_type({
    element: "Email input",
    ref: "[data-testid='email-input']",
    text: "admin@cmz.org"
});
await mcp__playwright__browser_snapshot();  // Shows current state
```

### Key Testing Flows

#### 1. Admin Flow (Full Permissions)
```
Login → Dashboard → Family Groups → Manage Families
→ See "Add New Family" button (purple admin badge)
→ Create family with parents/students
→ Edit existing family
→ Delete test family
→ Verify all changes in DynamoDB
```

#### 2. Parent Flow (View-Only)
```
Login → Dashboard → Family Groups → Manage Families
→ NO "Add New Family" button (green parent badge)
→ See lock icons instead of edit/delete
→ Click "View Details" → Read-only modal
→ Cannot modify any fields
→ API returns 403 for edit attempts
```

#### 3. Non-Member Flow (No Access)
```
Login → Try to access family URL directly
→ Get 403 Forbidden
→ Redirected or shown error message
→ No family data exposed
```

## Common Issues and Solutions

### Issue: Test Users Not Working
**Symptom**: Login fails with "Invalid credentials"
**Root Cause**: Auth mode mismatch or missing test users

**Solution**:
```python
# Check auth mode in backend
print(f"AUTH_MODE: {os.environ.get('AUTH_MODE', 'mock')}")

# Ensure test users exist in mock auth
test_users = {
    "admin@cmz.org": {"password": "admin123", "role": "admin"},
    "parent1@test.cmz.org": {"password": "testpass123", "role": "parent"}
}
```

### Issue: Bidirectional References Not Updating
**Symptom**: Creating family doesn't update user's familyIds
**Root Cause**: Missing atomic operations

**Solution**:
```python
# Must update BOTH directions atomically
def add_user_to_family(user_id, family_id):
    with transaction():
        # Update family
        family = Family.get(family_id)
        family.parentIds.add(user_id)
        family.save()

        # Update user
        user = User.get(user_id)
        user.familyIds.add(family_id)
        user.save()
```

### Issue: Permissions Not Enforced in UI
**Symptom**: Non-admins see edit buttons
**Root Cause**: Frontend not checking permissions

**Solution**:
```typescript
// Component must check permissions
{family.canEdit ? (
    <EditButton onClick={handleEdit} />
) : (
    <LockIcon title="Admin access required" />
)}
```

### Issue: User Names Not Displaying
**Symptom**: UI shows user IDs instead of names
**Root Cause**: Missing user population step

**Solution**:
```typescript
// Batch fetch users after getting family
const family = await getFamily(familyId);
const allUserIds = [...family.parentIds, ...family.studentIds];
const users = await batchGetUsers(allUserIds);

// Map IDs to user objects
family.parents = family.parentIds.map(id => users[id]);
family.students = family.studentIds.map(id => users[id]);
```

## Testing Best Practices

### 1. Data Isolation
```bash
# Use test-specific IDs
FAMILY_TEST_PREFIX="family_test_"
USER_TEST_PREFIX="user_test_"

# Cleanup after tests
aws dynamodb update-item \
    --table-name quest-dev-family \
    --key '{"familyId":{"S":"family_test_001"}}' \
    --update-expression "SET softDelete = :true" \
    --expression-attribute-values '{":true":{"BOOL":true}}'
```

### 2. Progressive Testing
```bash
# Step 1: Basic connectivity
curl http://localhost:8080/health

# Step 2: Auth verification
curl -X POST http://localhost:8080/auth/login \
    -d '{"email":"admin@cmz.org","password":"admin123"}'

# Step 3: CRUD operations
curl -X POST http://localhost:8080/family ...

# Step 4: Permission validation
curl -X PATCH http://localhost:8080/family/123 \
    -H "X-User-Id: non_admin" \
    # Should get 403

# Step 5: UI validation with Playwright MCP
```

### 3. Visual Evidence Collection
```javascript
// Take snapshots at key moments
await browser.snapshot();  // Before action
await browser.click({...});
await browser.wait_for({...});
await browser.snapshot();  // After action

// Screenshot specific states
await browser.take_screenshot({
    filename: "admin-family-list.png",
    fullPage: true
});
```

### 4. DynamoDB Verification
```bash
# Verify bidirectional references
echo "🔍 Checking family→user references..."
FAMILY=$(aws dynamodb get-item \
    --table-name quest-dev-family \
    --key '{"familyId":{"S":"family_123"}}' \
    --query 'Item.parentIds.SS')

echo "🔍 Checking user→family references..."
USER=$(aws dynamodb get-item \
    --table-name quest-dev-user \
    --key '{"userId":{"S":"user_456"}}' \
    --query 'Item.familyIds.SS')

# Verify consistency
if [[ $FAMILY == *"user_456"* ]] && [[ $USER == *"family_123"* ]]; then
    echo "✅ Bidirectional references consistent"
else
    echo "❌ Reference mismatch detected"
fi
```

## Performance Optimization

### Batch Operations
```typescript
// ❌ Bad: N+1 queries
for (const userId of family.parentIds) {
    const user = await getUser(userId);
    family.parents.push(user);
}

// ✅ Good: Single batch query
const users = await batchGetUsers(family.parentIds);
family.parents = users;
```

### Caching Strategy
```typescript
// Cache user lookups per session
const userCache = new Map();

async function getUserWithCache(userId) {
    if (!userCache.has(userId)) {
        userCache.set(userId, await getUser(userId));
    }
    return userCache.get(userId);
}
```

## Security Considerations

### JWT Token Validation
```python
# Backend must validate role claim
def validate_admin(token):
    payload = jwt.decode(token)
    if payload.get('role') != 'admin':
        raise Forbidden("Admin access required")
```

### Input Validation
```python
# Validate parent/student data
def validate_family_input(data):
    # Check email formats
    for parent in data.get('parents', []):
        if not is_valid_email(parent['email']):
            raise ValidationError("Invalid email")

    # Validate age ranges
    for student in data.get('students', []):
        age = int(student.get('age', 0))
        if age < 5 or age > 18:
            raise ValidationError("Age must be 5-18")
```

## Debugging Techniques

### Console Logging
```javascript
// Frontend debugging
console.log('Current user role:', currentUser.role);
console.log('Family permissions:', { canView, canEdit });
console.log('API response:', response);
```

### Backend Logging
```python
# Add debug logging
import logging
logger = logging.getLogger(__name__)

def create_family(data, user_id):
    logger.info(f"Creating family for user {user_id}")
    logger.debug(f"Family data: {data}")
    # ... implementation
    logger.info(f"Created family {family_id}")
```

### Browser DevTools
1. **Network Tab**: Monitor API calls and responses
2. **Console**: Check for JavaScript errors
3. **Application Tab**: Inspect localStorage for tokens
4. **React DevTools**: Examine component state and props

## Rollback Procedures

### Data Rollback
```bash
# Restore family to previous state
aws dynamodb put-item \
    --table-name quest-dev-family \
    --item file://backup/family_123.json

# Remove test data
aws dynamodb delete-item \
    --table-name quest-dev-family \
    --key '{"familyId":{"S":"family_test_001"}}'
```

### Code Rollback
```bash
# If implementation breaks
git stash  # Save current changes
git checkout main
git pull origin main
git checkout -b bugfix/family-management-fix
# Apply specific fixes only
```

## Success Metrics

### Functional Metrics
- ✅ 100% of permission rules enforced
- ✅ 0 unauthorized data access incidents
- ✅ 100% bidirectional reference consistency
- ✅ All CRUD operations working for admins

### Performance Metrics
- ✅ Family list loads < 2 seconds
- ✅ User batch fetch < 500ms
- ✅ Permission check < 100ms overhead
- ✅ DynamoDB operations < 200ms

### User Experience Metrics
- ✅ Clear role indicators (badges)
- ✅ Intuitive permission feedback (lock icons)
- ✅ Appropriate error messages
- ✅ Smooth UI transitions

## Reporting Template

```markdown
## Family Management Validation Report
**Date**: [DATE]
**Tester**: [NAME]
**Environment**: [DEV/STAGING/PROD]

### Test Coverage
- [ ] Admin full CRUD flow
- [ ] Parent view-only flow
- [ ] Non-member restriction flow
- [ ] Bidirectional reference validation
- [ ] DynamoDB persistence check
- [ ] API permission enforcement
- [ ] UI permission display

### Results
| Test Case | Result | Notes |
|-----------|--------|-------|
| Admin creates family | PASS/FAIL | |
| Parent views family | PASS/FAIL | |
| Non-admin edit blocked | PASS/FAIL | |
| Bidirectional refs | PASS/FAIL | |

### Issues Found
1. [Issue description and severity]
2. [Steps to reproduce]
3. [Suggested fix]

### Screenshots
- Admin view: [link]
- Parent view: [link]
- Error states: [link]

### Recommendations
[Next steps and improvements]
```

## Key Takeaways

1. **Always test visibly** - Use Playwright MCP for browser visibility
2. **Verify both directions** - Check family→user AND user→family references
3. **Test all roles** - Admin, parent, student, non-member
4. **Validate at all layers** - UI, API, and database
5. **Document with screenshots** - Visual evidence of test execution
6. **Clean up test data** - Use soft delete for test families
7. **Monitor performance** - Track response times for optimization