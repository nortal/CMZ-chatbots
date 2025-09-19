# Family-User Bidirectional Reference Design
**Date**: 2025-09-17
**Status**: Proposed Architecture

## Overview
Implement bidirectional references between Users and Families using IDs to enable efficient queries in both directions.

## Data Model Design

### Users Table
```python
{
  "userId": "user_abc123",  # Primary Key
  "email": "sarah.johnson@test.cmz.org",
  "name": "Sarah Johnson",
  "role": "parent",  # parent | student | admin
  "familyIds": ["family_xyz789", "family_def456"],  # Array of family IDs
  "phone": "555-0101",
  "isPrimaryContact": true,
  "isEmergencyContact": true,
  "created": {...},
  "modified": {...}
}
```

### Families Table
```python
{
  "familyId": "family_xyz789",  # Primary Key
  "familyName": "Johnson Family",
  "parentIds": ["user_abc123", "user_def456"],  # Array of parent user IDs
  "studentIds": ["user_ghi789", "user_jkl012"],  # Array of student user IDs
  "address": {...},
  "preferredPrograms": [...],
  "status": "active",
  "softDelete": false,
  "created": {...},
  "modified": {...}
}
```

## API Implementation Patterns

### Creating a New Family
```python
def create_family(body: Dict) -> Tuple[Dict, int]:
    # 1. Create/verify parent users
    parent_ids = []
    for parent_data in body['parents']:
        user = create_or_get_user(parent_data)
        parent_ids.append(user['userId'])

    # 2. Create/verify student users
    student_ids = []
    for student_data in body['students']:
        user = create_or_get_user(student_data)
        student_ids.append(user['userId'])

    # 3. Create family with user IDs
    family = {
        'familyId': generate_family_id(),
        'familyName': body['familyName'],
        'parentIds': parent_ids,
        'studentIds': student_ids,
        ...
    }
    save_family(family)

    # 4. Update users with family reference
    for user_id in parent_ids + student_ids:
        add_family_to_user(user_id, family['familyId'])

    return family, 201
```

### Fetching a Family with User Details
```python
def get_family_with_details(family_id: str) -> Dict:
    # 1. Get family record
    family = get_family_by_id(family_id)

    # 2. Batch fetch all referenced users
    user_ids = family['parentIds'] + family['studentIds']
    users = batch_get_users(user_ids)
    user_map = {u['userId']: u for u in users}

    # 3. Populate user details
    family['parents'] = [user_map[pid] for pid in family['parentIds']]
    family['students'] = [user_map[sid] for sid in family['studentIds']]

    return family
```

### Getting All Families for a User
```python
def get_user_families(user_id: str) -> List[Dict]:
    # 1. Get user record
    user = get_user_by_id(user_id)

    # 2. Batch fetch all referenced families
    families = batch_get_families(user['familyIds'])

    return families
```

## DynamoDB Implementation

### Primary Tables
```yaml
Users Table:
  - Partition Key: userId (String)
  - Attributes:
    - familyIds (List)
    - email (String)
    - name (String)
    - role (String)

Families Table:
  - Partition Key: familyId (String)
  - Attributes:
    - parentIds (List)
    - studentIds (List)
    - familyName (String)
```

### Global Secondary Indexes (GSI)
```yaml
Users Table GSI:
  - GSI Name: email-index
  - Partition Key: email
  - Purpose: Quick user lookup by email

Families Table GSI:
  - GSI Name: status-index
  - Partition Key: status
  - Purpose: Filter active/inactive families
```

## Consistency Management

### Adding a User to a Family
```python
def add_user_to_family(user_id: str, family_id: str, role: str):
    try:
        # Transaction to ensure consistency
        with dynamodb.transact_write() as transaction:
            # 1. Add user to family's parent/student list
            if role == 'parent':
                transaction.update_item(
                    Table='Families',
                    Key={'familyId': family_id},
                    UpdateExpression='ADD parentIds :uid',
                    ExpressionAttributeValues={':uid': {user_id}}
                )
            else:
                transaction.update_item(
                    Table='Families',
                    Key={'familyId': family_id},
                    UpdateExpression='ADD studentIds :uid',
                    ExpressionAttributeValues={':uid': {user_id}}
                )

            # 2. Add family to user's family list
            transaction.update_item(
                Table='Users',
                Key={'userId': user_id},
                UpdateExpression='ADD familyIds :fid',
                ExpressionAttributeValues={':fid': {family_id}}
            )

            transaction.commit()
    except TransactionCanceledException:
        # Handle consistency error
        pass
```

### Removing a User from a Family
```python
def remove_user_from_family(user_id: str, family_id: str):
    # Similar transaction pattern for removal
    # Must update both tables atomically
    pass
```

## API Endpoints

### Family Endpoints
```yaml
GET /family/{familyId}:
  - Returns family with populated user details
  - Performs batch lookup of all referenced users

POST /family:
  - Creates new family
  - Creates/updates user records
  - Establishes bidirectional references

PATCH /family/{familyId}:
  - Updates family details
  - Manages user reference changes
  - Maintains consistency

DELETE /family/{familyId}:
  - Soft deletes family
  - Optionally removes family references from users
```

### User Endpoints
```yaml
GET /user/{userId}:
  - Returns user with family IDs
  - Can optionally populate family details

GET /user/{userId}/families:
  - Returns all families for a user
  - Efficient lookup via familyIds array

POST /user/{userId}/family/{familyId}:
  - Adds user to family
  - Updates both tables

DELETE /user/{userId}/family/{familyId}:
  - Removes user from family
  - Updates both tables
```

## Query Patterns

### Efficient Queries Enabled
1. **Get all families for a user**: O(1) lookup via user.familyIds
2. **Get all users in a family**: O(1) lookup via family.parentIds + studentIds
3. **Check if user belongs to family**: O(n) where n = user.familyIds.length
4. **Get all students of a parent**: Requires family lookups but efficient with batch operations

### Example Query Flows

**"Show me all my children"** (Parent perspective):
```python
1. Get parent user by ID
2. Batch get all families via familyIds
3. Extract all unique studentIds from families
4. Batch get student users
5. Filter students that share families with parent
```

**"Show me all families in a program"**:
```python
1. Query families by program (using GSI if frequent)
2. Batch populate user details for display
```

## Migration Strategy

### From Current Model to Bidirectional
```python
def migrate_existing_data():
    # 1. Scan all families
    families = scan_all_families()

    for family in families:
        # 2. For each parent/student name, create/find user
        parent_ids = []
        for parent_name in family.get('parents', []):
            user = find_or_create_user_by_name(parent_name, role='parent')
            parent_ids.append(user['userId'])
            # Add family reference to user
            add_family_to_user(user['userId'], family['familyId'])

        student_ids = []
        for student_name in family.get('students', []):
            user = find_or_create_user_by_name(student_name, role='student')
            student_ids.append(user['userId'])
            # Add family reference to user
            add_family_to_user(user['userId'], family['familyId'])

        # 3. Update family with IDs instead of names
        update_family(family['familyId'], {
            'parentIds': parent_ids,
            'studentIds': student_ids
        })
```

## Benefits

1. **Performance**: Eliminates N+1 query problems with batch operations
2. **Flexibility**: Can query from either direction efficiently
3. **Consistency**: Atomic updates maintain referential integrity
4. **Scalability**: Works well with DynamoDB's architecture
5. **Feature Enablement**: Supports complex features like:
   - Family switching for users in multiple families
   - Sibling relationships
   - Guardian permissions
   - Family group messaging

## Implementation Checklist

- [ ] Update User model to include familyIds array
- [ ] Update Family model to use parentIds/studentIds instead of names
- [ ] Implement create_or_get_user utility function
- [ ] Add DynamoDB transactions for consistency
- [ ] Create batch_get_users and batch_get_families functions
- [ ] Update all family CRUD operations
- [ ] Add user-family relationship endpoints
- [ ] Migrate existing data
- [ ] Update frontend to handle ID-based relationships
- [ ] Add integration tests for bidirectional operations
- [ ] Document API changes in OpenAPI spec