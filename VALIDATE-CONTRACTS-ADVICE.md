# Contract Validation - Best Practices and Troubleshooting

## Purpose

This document provides guidance for using `/validate-contracts` to ensure UI-API-OpenAPI alignment and prevent runtime contract violations.

## When to Use Contract Validation

### Critical Moments
- **Before deploying to production** - Catch contract breaks before users experience them
- **After OpenAPI spec changes** - Verify UI and API still compatible
- **After UI refactoring** - Ensure API calls haven't changed incorrectly
- **After API implementation changes** - Verify OpenAPI contract still honored
- **In CI/CD pipeline** - Automated validation on every PR

### Development Workflow Integration
1. **Local Development**: Run before creating PR
2. **Code Review**: Reviewers check contract report
3. **Pre-merge**: CI/CD runs validation automatically
4. **Post-deployment**: Smoke test with contract validation

## Common Contract Violations

### 1. Field Name Mismatches

**Problem**: UI, API, and OpenAPI use different field names

**Example**:
```javascript
// OpenAPI spec
{
  "animalConfigId": { "type": "string" }
}

// UI code (WRONG)
fetch('/animal_config')
  .then(r => r.json())
  .then(data => {
    console.log(data.configId)  // ❌ Field doesn't exist
  })

// UI code (CORRECT)
fetch('/animal_config')
  .then(r => r.json())
  .then(data => {
    console.log(data.animalConfigId)  // ✅ Matches OpenAPI
  })
```

**Prevention**:
- Always reference OpenAPI spec when writing UI code
- Use TypeScript with generated types from OpenAPI
- Run contract validation before committing

### 2. Parameter Location Errors

**Problem**: UI sends parameters in wrong location (query vs body vs path)

**Example**:
```javascript
// OpenAPI spec: animalId is QUERY parameter
// GET /animal_config?animalId={value}

// UI code (WRONG)
fetch('/animal_config', {
  method: 'GET',
  body: JSON.stringify({ animalId: 'charlie_003' })  // ❌ Query param in body
})

// UI code (CORRECT)
fetch('/animal_config?animalId=charlie_003')  // ✅ Query param in URL
```

**Detection**: Contract validator checks parameter location matches OpenAPI spec

**Fix**: Read OpenAPI spec `parameters[].in` field to determine location

### 3. Required Field Omissions

**Problem**: UI doesn't send fields marked as required in OpenAPI

**Example**:
```yaml
# OpenAPI spec
requestBody:
  required: true
  content:
    application/json:
      schema:
        required: [familyName, parentIds, studentIds]
        properties:
          familyName: {type: string}
          parentIds: {type: array, minItems: 1}
          studentIds: {type: array, minItems: 1}  # REQUIRED and non-empty
```

```javascript
// UI code (WRONG)
fetch('/family', {
  method: 'POST',
  body: JSON.stringify({
    familyName: "Test Family",
    parentIds: ["parent1"],
    studentIds: []  // ❌ Empty array but OpenAPI requires minItems: 1
  })
})

// Result: 400 Bad Request "studentIds should be non-empty"
```

**Prevention**:
- Check `required` fields and `minItems` constraints in OpenAPI
- Validate in UI before sending request
- Show validation errors to user

### 4. Type Mismatches

**Problem**: UI sends wrong data type (string vs number, etc.)

**Example**:
```javascript
// OpenAPI spec: temperature is number (0.0 to 1.0)

// UI code (WRONG)
fetch('/animal_config', {
  method: 'PATCH',
  body: JSON.stringify({
    temperature: "0.7"  // ❌ String, should be number
  })
})

// UI code (CORRECT)
fetch('/animal_config', {
  method: 'PATCH',
  body: JSON.stringify({
    temperature: 0.7  // ✅ Number
  })
})
```

**Prevention**:
- Use TypeScript to catch type errors at compile time
- Validate types before JSON.stringify()
- Check OpenAPI `type` field for each parameter

### 5. Response Structure Assumptions

**Problem**: UI expects different response structure than API returns

**Example**:
```javascript
// OpenAPI spec returns: {familyId: string, familyName: string, ...}

// UI code (WRONG)
fetch('/family/123')
  .then(r => r.json())
  .then(data => {
    console.log(data.family.familyId)  // ❌ Assumes nested structure
  })

// UI code (CORRECT)
fetch('/family/123')
  .then(r => r.json())
  .then(family => {
    console.log(family.familyId)  // ✅ Matches OpenAPI flat structure
  })
```

## Edge Cases and Incompatibilities

Even with perfect static contract validation, these runtime issues may occur:

### 1. JavaScript Type Coercion

**Issue**: JavaScript automatically coerces types

```javascript
// UI sends
{temperature: "0.7"}  // String

// JavaScript coerces to
{temperature: 0.7}  // Number

// Problem: Works in JavaScript, fails in strict validation
```

**Mitigation**: Use TypeScript strict mode to prevent implicit coercion

### 2. Null vs Undefined vs Empty String

**Issue**: Different "emptiness" semantics

```javascript
// JavaScript treats these differently:
{ field: null }       // Explicitly null
{ field: undefined }  // Undefined
{ field: "" }         // Empty string
{ }                   // Field missing

// Python backend:
body.get('field')  # Returns None if missing
body.get('field', default)  # Returns default if missing/None
```

**Mitigation**: Document null handling conventions in OpenAPI using `nullable: true`

### 3. Array Ordering

**Issue**: Order not guaranteed unless specified

```javascript
// UI expects specific order
families.forEach((family, index) => {
  // Assumes families[0] is most recent
})

// API returns unordered
# Unless OpenAPI specifies sorting, order is undefined
```

**Mitigation**: Explicitly document sorting in OpenAPI `description` field

### 4. Date/Time Formats

**Issue**: Different date interpretations

```javascript
// API returns ISO string
{created: "2025-10-10T12:34:56Z"}

// UI parses as Date
new Date("2025-10-10T12:34:56Z")  // Timezone dependent!

// Problem: Timezone conversion may differ
```

**Mitigation**: Always use ISO 8601 with explicit timezone (Z or +00:00)

### 5. Floating Point Precision

**Issue**: Rounding differences between languages

```javascript
// JavaScript
0.1 + 0.2 === 0.3  // false (0.30000000000000004)

// Python
0.1 + 0.2 == 0.3  // True

// Problem: Comparison failures in tests
```

**Mitigation**: Use epsilon comparison for floats, or use integers (cents instead of dollars)

### 6. Case Sensitivity

**Issue**: Email/username comparisons

```javascript
// UI sends
{email: "Test@CMZ.org"}

// API stores
{email: "test@cmz.org"}  // Normalized to lowercase

// Problem: Case-sensitive comparison fails
```

**Mitigation**: Document case normalization rules in OpenAPI

### 7. Whitespace Handling

**Issue**: Trimming behavior differs

```javascript
// UI sends
{familyName: "  Test Family  "}

// API trims or doesn't trim?
{familyName: "Test Family"}  // Trimmed?

// Problem: Inconsistent whitespace handling
```

**Mitigation**: Document trimming behavior in OpenAPI `description`

### 8. Unicode and Emoji

**Issue**: Encoding differences

```javascript
// UI allows emoji
{name: "Charlie 🐻"}

// Database/API handles Unicode?
# May fail if not UTF-8 throughout

// Problem: Encoding errors or data loss
```

**Mitigation**: Test with Unicode/emoji, document encoding requirements

### 9. File Upload Handling

**Issue**: Binary data encoding

```javascript
// UI uploads file
const formData = new FormData()
formData.append('file', fileBlob)

// OpenAPI spec may not detail multipart/form-data correctly
```

**Mitigation**: Explicitly test file upload endpoints, document in OpenAPI

### 10. Concurrent Modifications

**Issue**: Race conditions with PATCH

```javascript
// User A reads config
{temperature: 0.5}

// User B updates temperature
{temperature: 0.7}

// User A updates voice
{voice: "echo"}  // Overwrites temperature to 0.5?

// Problem: Last-write-wins without optimistic locking
```

**Mitigation**: Use ETags or version fields for optimistic locking

## Handler Validation Best Practices

### Validate Required Fields

**Always check required fields before using them:**

```python
# ❌ BAD: Assumes field exists
def handle_family_post(body):
    family_name = body['familyName']  # May raise KeyError
    parent_ids = body['parentIds']    # May raise KeyError

# ✅ GOOD: Validates required fields
def handle_family_post(body):
    family_name = body.get('familyName')
    if not family_name:
        error = Error(
            code="validation_error",
            message="familyName is required",
            details={"field": "familyName"}
        )
        return error.to_dict(), 400

    parent_ids = body.get('parentIds')
    if not parent_ids:
        error = Error(
            code="validation_error",
            message="parentIds is required",
            details={"field": "parentIds"}
        )
        return error.to_dict(), 400
```

### Validate Types

**Check data types match OpenAPI spec:**

```python
# ❌ BAD: No type validation
def handle_config_patch(body):
    temperature = body.get('temperature', 0.5)
    # Could be string "0.5" from malformed request

# ✅ GOOD: Validates type
def handle_config_patch(body):
    temperature = body.get('temperature')
    if temperature is not None and not isinstance(temperature, (int, float)):
        error = Error(
            code="validation_error",
            message="temperature must be a number",
            details={"field": "temperature", "received_type": str(type(temperature))}
        )
        return error.to_dict(), 400
```

### Build Responses Matching OpenAPI

**Use exact field names from OpenAPI schema:**

```python
# ❌ BAD: Different field names than OpenAPI
def handle_get_family(family_id):
    family = get_from_db(family_id)
    return {
        'id': family.id,           # OpenAPI says familyId
        'name': family.name,       # OpenAPI says familyName
    }, 200

# ✅ GOOD: Matches OpenAPI schema exactly
def handle_get_family(family_id):
    family = get_from_db(family_id)
    return {
        'familyId': family.id,      # Matches OpenAPI
        'familyName': family.name,  # Matches OpenAPI
        'parentIds': family.parents # Matches OpenAPI
    }, 200
```

### Use Error Model Consistently

**Always use OpenAPI Error model for failures:**

```python
from openapi_server.models.error import Error

# ❌ BAD: Inconsistent error format
def handle_operation():
    return {"error": "Something went wrong"}, 500

# ✅ GOOD: Uses Error model from OpenAPI
def handle_operation():
    error = Error(
        code="internal_error",
        message="Operation failed",
        details={"reason": "Database connection lost"}
    )
    return error.to_dict(), 500
```

## Teams Notification

Contract validation automatically sends results to Teams using Adaptive Card format. Ensure `TEAMS_WEBHOOK_URL` environment variable is set.

**Notification includes:**
- Total endpoints validated
- Alignment statistics (aligned, partial, misaligned)
- Handler validation issues
- Critical mismatches requiring immediate attention
- Actionable recommendations

See `TEAMS-WEBHOOK-ADVICE.md` for webhook configuration and troubleshooting.

## Best Practices

### For UI Development

1. **Generate TypeScript Types from OpenAPI**
   ```bash
   # Use openapi-typescript to generate types
   npx openapi-typescript backend/api/openapi_spec.yaml -o src/api/types.ts
   ```

2. **Create API Client Wrapper**
   ```typescript
   // src/api/client.ts
   import { paths } from './types'

   type PostFamilyRequest = paths['/family']['post']['requestBody']['content']['application/json']
   type PostFamilyResponse = paths['/family']['post']['responses']['201']['content']['application/json']

   export async function createFamily(data: PostFamilyRequest): Promise<PostFamilyResponse> {
     const response = await fetch('/family', {
       method: 'POST',
       headers: { 'Content-Type': 'application/json' },
       body: JSON.stringify(data)
     })
     if (!response.ok) throw new Error('Failed to create family')
     return response.json()
   }
   ```

3. **Validate Before Sending**
   ```typescript
   // Validate required fields before API call
   function validateFamilyData(data: PostFamilyRequest): string[] {
     const errors = []
     if (!data.familyName) errors.push('Family name is required')
     if (!data.parentIds || data.parentIds.length === 0) errors.push('At least one parent required')
     if (!data.studentIds || data.studentIds.length === 0) errors.push('At least one student required')
     return errors
   }
   ```

### For API Development

1. **Use OpenAPI Validation Decorators**
   ```python
   from connexion import request
   from openapi_server.models.family import Family

   @validate_request_body(Family)
   def handle_family_post(body: Family):
       # Body is already validated against OpenAPI schema
       return create_family(body), 201
   ```

2. **Return Exact OpenAPI Schema**
   ```python
   # Don't add extra fields unless documented in OpenAPI
   def handle_get_family(family_id: str):
       family = get_family_from_db(family_id)

       # Return ONLY fields defined in OpenAPI
       return {
           'familyId': family.id,
           'familyName': family.name,
           'parentIds': family.parent_ids,
           'studentIds': family.student_ids
       }, 200
   ```

3. **Use Consistent Error Format**
   ```python
   from openapi_server.models.error import Error

   # Always use Error model for failures
   error = Error(
       code="validation_error",
       message="Invalid family data",
       details={"field": "studentIds", "issue": "cannot be empty"}
   )
   return error.to_dict(), 400
   ```

### For OpenAPI Spec Maintenance

1. **Document All Fields**
   ```yaml
   # Add descriptions for clarity
   properties:
     temperature:
       type: number
       format: float
       minimum: 0.0
       maximum: 1.0
       description: "AI model temperature (0=deterministic, 1=creative)"
   ```

2. **Use Examples**
   ```yaml
   # Provide examples for complex objects
   Family:
     example:
       familyId: "family_abc123"
       familyName: "Smith Family"
       parentIds: ["user_parent_001"]
       studentIds: ["user_student_001", "user_student_002"]
   ```

3. **Version Breaking Changes**
   ```yaml
   # When breaking contract, version the API
   /v2/family:  # New version
     post:
       # New contract with breaking changes
   ```

## Troubleshooting

### Contract Validation Reports High-Severity Mismatch

1. **Identify Source of Truth**: OpenAPI is always authoritative
2. **Check Recent Changes**: Did OpenAPI spec change? Did UI refactor?
3. **Fix UI First**: Easier to fix UI than change API contract
4. **Test Fix**: Re-run validation after fix
5. **Add Regression Test**: Create test for this contract

### UI Calls Work Locally But Fail in Production

1. **Check Environment Variables**: Different API URLs?
2. **Verify CORS**: Production CORS config different?
3. **Check Authentication**: Production JWT secret different?
4. **Inspect Network Tab**: See actual request/response in browser
5. **Run Contract Validation**: Against production OpenAPI spec

### API Returns 400 But Contract Looks Correct

1. **Check Required Fields**: All required fields present?
2. **Verify Types**: Numbers not strings, arrays not objects?
3. **Check Array Constraints**: minItems, maxItems satisfied?
4. **Validate Enums**: Value in allowed enum values?
5. **Inspect Validation Error Details**: Error.details shows which field failed

## Integration with CI/CD

### GitHub Actions Example

```yaml
# .github/workflows/contract-validation.yml
name: Contract Validation

on:
  pull_request:
    paths:
      - 'backend/api/openapi_spec.yaml'
      - 'frontend/src/**'
      - 'backend/api/src/main/python/openapi_server/impl/**'

jobs:
  validate-contracts:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run Contract Validation
        run: |
          python3 scripts/validate_contracts.py \
            --openapi backend/api/openapi_spec.yaml \
            --ui frontend/src \
            --api backend/api/src/main/python/openapi_server/impl \
            --output contract_report.md

      - name: Check for Mismatches
        run: |
          if grep -q "❌ Misaligned" contract_report.md; then
            echo "Contract validation failed!"
            cat contract_report.md
            exit 1
          fi

      - name: Upload Report
        uses: actions/upload-artifact@v3
        with:
          name: contract-validation-report
          path: contract_report.md
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Run contract validation before allowing commit
python3 scripts/validate_contracts.py \
  --openapi backend/api/openapi_spec.yaml \
  --ui frontend/src \
  --api backend/api/src/main/python/openapi_server/impl \
  --output /tmp/contract_report.md

if grep -q "❌ Misaligned" /tmp/contract_report.md; then
  echo "❌ Contract validation failed! Fix mismatches before committing."
  cat /tmp/contract_report.md
  exit 1
fi

echo "✅ Contract validation passed"
```

## Summary

Contract validation prevents runtime failures by ensuring UI, API, and OpenAPI spec stay aligned. Use it:
- **Before every deployment**
- **In CI/CD pipelines**
- **After any contract changes**

Even with perfect validation, be aware of runtime edge cases like type coercion, null handling, and timezone differences. Document these conventions clearly in your OpenAPI spec and test them explicitly.
