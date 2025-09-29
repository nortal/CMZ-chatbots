# Complete ID Field Inventory - CMZ API

## Summary Statistics
- **Total ID Fields**: 18 unique types
- **Most Common**: `userId` (19), `animalId` (18), `familyId` (11)
- **Generic `id`**: Only 1 occurrence (in test endpoint response)

## All ID Fields by Domain

### 1. User-Related IDs
| Field | Count | Usage | Status |
|-------|-------|-------|--------|
| `userId` | 19 | User identifier in paths, queries, bodies | ✅ Good |
| `userDetailsId` | 1 | User details identifier | ✅ Good |
| `actorId` | 1 | Actor/user performing action | ✅ Good |

### 2. Animal-Related IDs
| Field | Count | Usage | Status |
|-------|-------|-------|--------|
| `animalId` | 18 | Animal identifier in bodies/responses | ✅ Good |
| `animalConfigId` | 2 | Animal configuration identifier | ✅ Good |
| `animalDetailId` | 1 | Animal detail identifier | ✅ Good |
| `id` (in `/animal/{id}`) | 3 | Path parameter | ❌ **NEEDS FIX** |

### 3. Family-Related IDs
| Field | Count | Usage | Status |
|-------|-------|-------|--------|
| `familyId` | 11 | Family identifier | ✅ Good |
| `parentIds` | - | Array of parent user IDs | ✅ Good |
| `studentIds` | - | Array of student user IDs | ✅ Good |

### 4. Conversation-Related IDs
| Field | Count | Usage | Status |
|-------|-------|-------|--------|
| `sessionId` | 9 | Conversation session identifier | ✅ Good |
| `convoTurnId` | 2 | Conversation turn identifier | ✅ Good |

### 5. Media/Content IDs
| Field | Count | Usage | Status |
|-------|-------|-------|--------|
| `mediaId` | 3 | Media content identifier | ✅ Good |
| `knowledgeId` | 3 | Knowledge base identifier | ✅ Good |

### 6. System/Technical IDs
| Field | Count | Usage | Status |
|-------|-------|-------|--------|
| `requestId` | 1 | Request tracking identifier | ✅ Good |
| `apiVersionUuid` | 2 | API version identifier | ✅ Good |
| `id` (test endpoint) | 1 | Generic ID in test response | ⚠️ Low priority |

## Path Parameters Analysis

### Current Path Parameters
```yaml
# PROBLEMATIC - Uses generic 'id'
/animal/{id}:           # ❌ Should be animalId

# GOOD - Use specific names
/family/{familyId}:     # ✅ Correct
/user/{userId}:         # ✅ Correct
/user_details/{userId}: # ✅ Correct
/conversations/sessions/{sessionId}: # ✅ Correct
```

## Request/Response Body IDs

### Animal Operations
```yaml
# Request bodies typically include:
animalId: string        # ✅ Specific name
animalConfigId: string  # ✅ Specific name
animalDetailId: string  # ✅ Specific name
```

### Family Operations
```yaml
# Request/Response includes:
familyId: string        # ✅ Specific name
parentIds: [string]     # ✅ Clear array of IDs
studentIds: [string]    # ✅ Clear array of IDs
```

### User Operations
```yaml
# Common fields:
userId: string          # ✅ Specific name
userDetailsId: string   # ✅ Specific name
actorId: string         # ✅ Clear purpose
```

### Conversation Operations
```yaml
# Session tracking:
sessionId: string       # ✅ Specific name
convoTurnId: string     # ✅ Specific name
userId: string          # ✅ References user
animalId: string        # ✅ References animal
```

## Consistency Analysis

### ✅ Good Practices Already in Place
1. **Specific Naming**: Most IDs use descriptive names (userId, animalId, etc.)
2. **Domain Grouping**: IDs clearly indicate their domain (animal, user, family)
3. **Array Naming**: Plural forms for arrays (parentIds, studentIds)
4. **Relationship Clarity**: Foreign keys are obvious (userId in conversations)

### ❌ Issues to Fix
1. **Generic Path Parameter**: `/animal/{id}` should be `/animal/{animalId}`
2. **Test Endpoint**: Response includes generic `id` field (low priority)

### ⚠️ Potential Improvements
1. **Naming Convention**: Consider if `convoTurnId` should be `conversationTurnId`
2. **UUID Fields**: `apiVersionUuid` could be `apiVersionId` for consistency
3. **Detail vs Details**: `animalDetailId` vs `userDetailsId` (singular vs plural)

## Cross-Reference Matrix

### Where IDs Reference Each Other
```
User System:
  userId → appears in:
    - Family (parentIds, studentIds arrays)
    - Conversation (userId field)
    - Animals (ownership/creator)
    - Media (uploader)
    - Knowledge (author)

Animal System:
  animalId → appears in:
    - Conversations (which animal)
    - Media (associated animal)
    - Knowledge (about which animal)
    - Analytics (animal metrics)

Family System:
  familyId → appears in:
    - Users (family membership)
    - Analytics (family metrics)
    - Conversations (family context)

Conversation System:
  sessionId → appears in:
    - Conversation turns
    - Analytics
    - Chat history
```

## Recommendations

### Priority 1: Critical Fixes
1. **Fix `/animal/{id}`** → `/animal/{animalId}`
   - Eliminates Connexion `id_` errors
   - Makes API consistent

### Priority 2: Minor Consistency
1. **Consider renaming**:
   - `convoTurnId` → `conversationTurnId`
   - `apiVersionUuid` → `apiVersionId`
   - Align `animalDetailId` vs `userDetailsId`

### Priority 3: Documentation
1. **Document ID relationships**
2. **Create ID naming guidelines**
3. **Add foreign key documentation**

## Impact Assessment

### If We Only Fix `/animal/{id}`:
- **Effort**: Low (1 endpoint, 3 operations)
- **Risk**: Low (isolated change)
- **Benefit**: High (eliminates major error source)

### If We Standardize All IDs:
- **Effort**: Medium (multiple endpoints)
- **Risk**: Medium (broader changes)
- **Benefit**: Medium (better consistency)

## Testing Requirements

### For Animal ID Fix:
```bash
# Before: These fail with id_ errors
curl -X GET http://localhost:8080/animal/test-1
curl -X PUT http://localhost:8080/animal/test-1
curl -X DELETE http://localhost:8080/animal/test-1

# After: Should work correctly
curl -X GET http://localhost:8080/animal/test-1
curl -X PUT http://localhost:8080/animal/test-1
curl -X DELETE http://localhost:8080/animal/test-1
```

### Regression Tests for Other IDs:
```bash
# These should continue working:
curl -X GET http://localhost:8080/family/family-1
curl -X GET http://localhost:8080/user/user-1
curl -X GET http://localhost:8080/conversations/sessions/session-1
```

## Conclusion

The CMZ API is actually in good shape regarding ID naming:
- **17 out of 18 ID types** use specific, descriptive names
- **Only 1 production issue**: `/animal/{id}` needs to become `/animal/{animalId}`
- The architecture shows good consistency and clear relationships
- Foreign key references are logical and traceable

The main action needed is fixing the animal endpoint's generic `id` parameter.