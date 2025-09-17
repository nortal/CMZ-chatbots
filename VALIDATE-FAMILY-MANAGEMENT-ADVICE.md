# VALIDATE-FAMILY-MANAGEMENT-ADVICE.md

Best practices and lessons learned for validating Family Groups management functionality.

## Overview

The Family Groups management system involves complex interactions between:
- React frontend with modal components
- Flask backend with DynamoDB integration
- PynamoDB ORM for data persistence
- Multi-parent/student relationship management

## Key Implementation Insights

### Frontend Architecture

**Modal State Management**
```tsx
// Correct: Controlled modal with proper state
const [showAddFamily, setShowAddFamily] = useState(false);
const [isEditMode, setIsEditMode] = useState(false);

// Modal should handle its own internal state
const [familyName, setFamilyName] = useState('');
const [students, setStudents] = useState<Student[]>([...]);
const [parents, setParents] = useState<Parent[]>([...]);
```

**Dynamic Field Management**
- Use array state for parents/students with add/remove functionality
- Ensure at least one parent and one student remain
- Handle primary contact designation (only one at a time)

### Backend Implementation

**DynamoDB Model Structure**
```python
class FamilyModel(Model):
    familyId = UnicodeAttribute(hash_key=True)  # Generated UUID
    parents = ListAttribute(of=UnicodeAttribute)  # Array of parent data
    students = ListAttribute(of=UnicodeAttribute)  # Array of student data
    softDelete = BooleanAttribute(default=False)  # Soft delete flag
    created = Audit()  # Creation timestamp and user
    modified = Audit()  # Last modification timestamp and user
```

**Handler Pattern**
```python
# Correct implementation pattern
def family_list_get() -> Tuple[Any, int]:
    families = []
    for family in FamilyModel.scan():
        if not family.softDelete:  # Filter soft-deleted
            families.append(family.to_plain_dict())
    return families, 200
```

## Common Pitfalls and Solutions

### Issue 1: Modal Not Opening
**Problem**: Click handler not properly connected
**Solution**:
```tsx
// Ensure onClick is properly bound
<button onClick={() => setShowAddFamily(true)}>
  Add New Family
</button>

// Modal component must check isOpen prop
{showAddFamily && <AddFamilyModal ... />}
```

### Issue 2: DynamoDB Connection Errors
**Problem**: Table not found or credentials missing
**Solution**:
```bash
# Verify environment variables
export FAMILY_DYNAMO_TABLE_NAME=quest-dev-family
export AWS_PROFILE=cmz
export AWS_REGION=us-west-2
```

### Issue 3: Data Not Persisting
**Problem**: Frontend not calling backend properly
**Solution**:
```tsx
// Ensure proper API call structure
const response = await fetch('/api/family', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(familyData)
});
```

### Issue 4: Soft Delete Not Working
**Problem**: UI still shows deleted families
**Solution**:
```python
# Backend must filter soft-deleted records
if not family.softDelete:
    # Include in results

# Frontend should not display softDelete: true families
families.filter(f => !f.softDelete)
```

## Testing Strategy

### Phase 1: Unit Testing
```python
# Test DynamoDB model
def test_family_model_creation():
    family = FamilyModel(
        familyId="test_001",
        parents=["parent1"],
        students=["student1"]
    )
    assert family.familyId == "test_001"
```

### Phase 2: Integration Testing
```javascript
// Test API endpoints
describe('Family API', () => {
  test('POST /family creates record', async () => {
    const response = await createFamily(testData);
    expect(response.status).toBe(201);
    expect(response.data.familyId).toBeDefined();
  });
});
```

### Phase 3: E2E Testing with Playwright
```javascript
test('Add New Family flow', async ({ page }) => {
  await page.goto('/family-groups');
  await page.click('button:has-text("Add New Family")');
  await page.fill('input[name="familyName"]', 'Test Family');
  await page.click('button:has-text("Add Family")');
  await expect(page.locator('.success-message')).toBeVisible();
});
```

## DynamoDB Query Patterns

### List All Active Families
```python
families = FamilyModel.scan(
    filter_condition=FamilyModel.softDelete == False
)
```

### Get Specific Family
```python
try:
    family = FamilyModel.get(family_id)
    if family.softDelete:
        raise NotFound()
except DoesNotExist:
    return error_response(404)
```

### Update Family
```python
family = FamilyModel.get(family_id)
family.parents = updated_parents
family.modified = Audit(at=datetime.utcnow().isoformat())
family.save()
```

## Performance Optimization

### Frontend
- Implement pagination for large family lists
- Use React.memo for family card components
- Debounce search input

### Backend
- Use DynamoDB batch operations for bulk updates
- Implement caching for frequently accessed families
- Use projection expressions to limit data transfer

## Security Considerations

1. **Input Validation**
   - Sanitize all family data before storage
   - Validate email formats
   - Check phone number patterns

2. **Access Control**
   - Implement role-based access (admin, parent, student)
   - Parents can only edit their own family
   - Students have read-only access

3. **Data Privacy**
   - Never log sensitive information
   - Encrypt PII in transit and at rest
   - Implement audit logging for all changes

## Troubleshooting Guide

### Check Service Health
```bash
# Frontend
curl http://localhost:3001/health

# Backend
curl http://localhost:8080/health

# DynamoDB
aws dynamodb describe-table --table-name quest-dev-family
```

### View Logs
```bash
# Backend logs
docker logs cmz-openapi-api-dev

# Frontend logs
# Check browser console

# DynamoDB operations
aws dynamodb describe-table --table-name quest-dev-family
```

### Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| "Family not found" | Invalid familyId or soft deleted | Check DynamoDB for record |
| "Failed to create family" | DynamoDB write error | Check AWS credentials |
| "Modal is not defined" | Import error | Verify AddFamilyModal import |
| "Network error" | Backend not running | Start API server |

## Best Practices Summary

1. **Always use soft delete** - Never hard delete family records
2. **Maintain audit trails** - Track all changes with timestamps
3. **Handle edge cases** - Empty arrays, null values, etc.
4. **Validate on both ends** - Frontend and backend validation
5. **Test incrementally** - Unit → Integration → E2E
6. **Monitor performance** - Log slow queries and operations
7. **Document thoroughly** - Keep API docs in sync with implementation

## Related Documentation

- [OpenAPI Specification](backend/api/openapi_spec.yaml)
- [Family Model](backend/api/src/main/python/openapi_server/impl/utils/orm/models/family.py)
- [Family Handlers](backend/api/src/main/python/openapi_server/impl/family.py)
- [AddFamilyModal Component](frontend/src/components/AddFamilyModal.tsx)