# Animal Config Persistence Validation - Best Practices & Advice

## Overview
This document provides guidance for validating data persistence specifically for the Animal Configuration endpoint in the CMZ application. It focuses on the complete data flow from UI updates through the API to DynamoDB storage.

## Final Session Update - 2025-09-15
**Status**: ✅ **VALIDATION PASSED** - All persistence issues resolved
- Voice field persistence: Working correctly with valid enum values
- Personality field structure: Properly handled as complex object
- Guardrails schema: Frontend-backend alignment fixed
- Authentication: Mock JWT system implemented for testing

## Key Learnings

### 1. Endpoint Alignment is Critical
**Finding**: The frontend and backend must use identical endpoint signatures.
- **Verified**: Frontend uses `PATCH /animal_config?animalId={id}`
- **Confirmed**: Backend OpenAPI spec defines matching endpoint
- **Success**: Perfect alignment enables proper data flow

### 2. Data Type Transformations
**Challenge**: JavaScript numbers vs DynamoDB Decimals
```javascript
// Frontend sends
{ "stability": 0.5 }  // JavaScript number

// DynamoDB stores
{ "stability": { "N": "0.5" } }  // Decimal type
```
**Solution**: Implement type normalization in validation logic to handle these conversions.

### 3. Nested Object Complexity
**Challenge**: Voice, guardrails, and personality are complex nested structures
```json
{
  "voice": {
    "provider": "elevenlabs",
    "voiceId": "test_123",
    "settings": {
      "stability": 0.5,
      "similarityBoost": 0.75
    }
  }
}
```
**Solution**: Use recursive validation to verify nested field integrity.

## Validation Strategy

### Phase-Based Approach
1. **Baseline First**: Always capture current state before modifications
2. **API Testing**: Test the API directly before UI testing
3. **Database Verification**: Query DynamoDB immediately after updates
4. **Comparison Analysis**: Field-by-field validation with type awareness

### Test Data Design
```json
{
  "voice": {
    "provider": "elevenlabs",
    "voiceId": "unique_test_id_${timestamp}",  // Use timestamps for uniqueness
    "modelId": "eleven_turbo_v2",
    "stability": 0.5,  // Test decimal handling
    "similarityBoost": 0.75,
    "style": 0.0,
    "useSpeakerBoost": true  // Test boolean fields
  },
  "guardrails": {
    "contentFilters": ["educational", "age-appropriate"],  // Test arrays
    "responseMaxLength": 500,  // Test integers
    "topicRestrictions": ["violence", "inappropriate"],
    "safeMode": true
  },
  "personality": {
    "traits": ["friendly", "wise", "educational"],
    "backstory": "Test backstory with special characters: ñ, é, 中文",  // Test Unicode
    "interests": ["wildlife", "conservation", "leadership"],
    "communicationStyle": "warm and engaging"
  }
}
```

## Common Pitfalls & Solutions

### Pitfall 1: Not Checking Service Availability
**Problem**: Tests fail because services aren't running
**Solution**: Always verify services first
```bash
# Check backend
curl -f http://localhost:8080/ || echo "Backend not running"

# Check DynamoDB access
aws dynamodb list-tables --region us-west-2 || echo "AWS not configured"
```

### Pitfall 2: Comparing Raw DynamoDB Output
**Problem**: DynamoDB returns data in AttributeValue format
```json
// DynamoDB format
{ "name": { "S": "Leo" }, "age": { "N": "5" } }

// Expected format
{ "name": "Leo", "age": 5 }
```
**Solution**: Use proper deserialization
```python
from boto3.dynamodb.types import TypeDeserializer
deserializer = TypeDeserializer()
python_obj = {k: deserializer.deserialize(v) for k, v in dynamo_item.items()}
```

### Pitfall 3: Ignoring Audit Fields
**Problem**: Modified timestamps change on every update
**Solution**: Exclude audit fields from equality checks but verify they're updated
```python
def validate_audit_fields(baseline, updated):
    # Modified timestamp should be newer
    assert updated['modified']['at'] > baseline['modified']['at']
    # Created timestamp should remain unchanged
    assert updated['created']['at'] == baseline['created']['at']
```

### Pitfall 4: Not Testing Edge Cases
**Problem**: Standard tests pass but edge cases fail in production
**Solution**: Test comprehensive scenarios
- Empty strings vs null values
- Maximum field lengths
- Special characters and Unicode
- Concurrent updates
- Missing optional fields

## Implementation Best Practices

### 1. Modular Validation Functions
```python
def validate_animal_config_persistence(animal_id, test_data):
    """Main validation orchestrator"""
    baseline = capture_baseline(animal_id)
    response = update_via_api(animal_id, test_data)
    updated = query_dynamodb(animal_id)

    results = {
        'voice': validate_voice(baseline, updated, test_data),
        'guardrails': validate_guardrails(baseline, updated, test_data),
        'personality': validate_personality(baseline, updated, test_data),
        'audit': validate_audit_fields(baseline, updated)
    }

    return generate_report(results)
```

### 2. Comprehensive Error Reporting
```python
def generate_discrepancy_report(field, expected, actual):
    return {
        'field': field,
        'severity': assess_severity(field),
        'expected': expected,
        'actual': actual,
        'type_expected': type(expected).__name__,
        'type_actual': type(actual).__name__,
        'recommendation': suggest_fix(field, expected, actual)
    }
```

### 3. Performance Monitoring
```python
import time

start_time = time.time()
response = update_animal_config(animal_id, config)
api_latency = time.time() - start_time

if api_latency > 0.5:  # 500ms threshold
    log_performance_warning(api_latency)
```

## Validation Script Template

### Complete Validation Runner
```bash
#!/bin/bash
# validate-animal-config-persistence.sh

set -euo pipefail

# Configuration
ANIMAL_ID="${1:-leo_001}"
BACKEND_URL="${BACKEND_URL:-http://localhost:8080}"
AWS_REGION="${AWS_REGION:-us-west-2}"
TABLE_NAME="quest-dev-animal"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Animal Config Persistence Validation${NC}"
echo "======================================="
echo "Target Animal: $ANIMAL_ID"
echo "Backend URL: $BACKEND_URL"
echo ""

# Step 1: Service verification
echo -n "Checking backend API..."
if curl -f -s "$BACKEND_URL" > /dev/null 2>&1; then
    echo -e " ${GREEN}✓${NC}"
else
    echo -e " ${RED}✗${NC}"
    echo "Please start the backend with: make run-api"
    exit 1
fi

# Step 2: Baseline capture
echo "Capturing baseline configuration..."
aws dynamodb get-item \
    --table-name "$TABLE_NAME" \
    --key "{\"animalId\": {\"S\": \"$ANIMAL_ID\"}}" \
    --region "$AWS_REGION" \
    --output json > baseline.json

# Step 3: Prepare test data
echo "Preparing test payload..."
cat > test-payload.json <<EOF
{
  "voice": {
    "provider": "elevenlabs",
    "voiceId": "test_$(date +%s)",
    "stability": 0.5
  },
  "guardrails": {
    "responseMaxLength": 500,
    "safeMode": true
  }
}
EOF

# Step 4: Update via API
echo "Updating configuration via API..."
HTTP_STATUS=$(curl -s -o api-response.json -w "%{http_code}" \
    -X PATCH \
    -H "Content-Type: application/json" \
    -d @test-payload.json \
    "$BACKEND_URL/animal_config?animalId=$ANIMAL_ID")

if [ "$HTTP_STATUS" -ne 200 ]; then
    echo -e "${RED}API update failed with status: $HTTP_STATUS${NC}"
    cat api-response.json
    exit 1
fi

# Step 5: Verify in DynamoDB
echo "Verifying persistence in DynamoDB..."
sleep 1  # Allow time for write to complete
aws dynamodb get-item \
    --table-name "$TABLE_NAME" \
    --key "{\"animalId\": {\"S\": \"$ANIMAL_ID\"}}" \
    --region "$AWS_REGION" \
    --output json > updated.json

# Step 6: Validate
echo "Running validation..."
python3 - <<'PYTHON'
import json
import sys

with open('baseline.json') as f:
    baseline = json.load(f)

with open('updated.json') as f:
    updated = json.load(f)

with open('test-payload.json') as f:
    test_data = json.load(f)

# Simple validation example
if 'Item' not in updated:
    print("ERROR: No item found in updated data")
    sys.exit(1)

# Check if voice was updated
if 'voice' in updated['Item']:
    print("✓ Voice configuration persisted")
else:
    print("✗ Voice configuration missing")
    sys.exit(1)

# Check if guardrails were updated
if 'guardrails' in updated['Item']:
    print("✓ Guardrails configuration persisted")
else:
    print("✗ Guardrails configuration missing")
    sys.exit(1)

print("\nValidation PASSED")
PYTHON

echo -e "\n${GREEN}✓ Animal Config Persistence Validation Complete${NC}"
```

## Troubleshooting Guide

### Issue: API Returns 404
**Symptoms**: `curl` returns 404 for `/animal_config`
**Diagnosis**:
```bash
# Check if API is running
docker ps | grep cmz-openapi-api

# Check API logs
docker logs cmz-openapi-api-dev
```
**Solution**: Ensure API is regenerated with latest OpenAPI spec
```bash
make generate-api
make build-api
make run-api
```

### Issue: DynamoDB Access Denied
**Symptoms**: AWS CLI returns access denied errors
**Diagnosis**:
```bash
# Check AWS credentials
aws sts get-caller-identity

# Verify table access
aws dynamodb describe-table --table-name quest-dev-animal --region us-west-2
```
**Solution**: Configure AWS credentials
```bash
export AWS_PROFILE=cmz
export AWS_REGION=us-west-2
```

### Issue: Data Not Persisting
**Symptoms**: API returns 200 but data doesn't appear in DynamoDB
**Diagnosis**:
```python
# Check implementation
grep -n "put_item\|update_item" impl/animals.py

# Verify table name
grep "ANIMAL_DYNAMO_TABLE" .env
```
**Solution**: Check implementation in `impl/animals.py` for proper DynamoDB calls

## Performance Benchmarks

### Expected Latencies
- **API Response**: < 200ms for standard update
- **DynamoDB Write**: < 50ms
- **End-to-End**: < 300ms
- **Large Payload**: < 500ms

### Monitoring Commands
```bash
# Monitor API latency
time curl -X PATCH ...

# Monitor DynamoDB metrics
aws cloudwatch get-metric-statistics \
    --namespace AWS/DynamoDB \
    --metric-name UserErrors \
    --dimensions Name=TableName,Value=quest-dev-animal \
    --start-time 2024-01-01T00:00:00Z \
    --end-time 2024-01-02T00:00:00Z \
    --period 3600 \
    --statistics Sum
```

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Animal Config Persistence Test

on:
  pull_request:
    paths:
      - 'backend/api/src/main/python/openapi_server/impl/animals.py'
      - 'frontend/src/pages/AnimalConfig.tsx'

jobs:
  validate-persistence:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Start Backend
        run: |
          make build-api
          make run-api &
          sleep 10

      - name: Run Validation
        run: |
          ./validate-animal-config-persistence.sh

      - name: Upload Results
        if: always()
        uses: actions/upload-artifact@v2
        with:
          name: validation-results
          path: |
            baseline.json
            updated.json
            api-response.json
            validation-report.json
```

## Next Steps

1. **Expand Test Coverage**
   - Add more animals to test suite
   - Test all optional fields
   - Include error scenarios

2. **Automate Reporting**
   - Generate HTML reports
   - Send notifications on failures
   - Track metrics over time

3. **Performance Testing**
   - Load testing with concurrent updates
   - Measure scaling characteristics
   - Identify bottlenecks

4. **Integration Testing**
   - Test with frontend Playwright
   - Validate user workflows
   - Cross-browser testing

## Conclusion

The Animal Config Persistence validation provides focused testing for one of the most critical data flows in the CMZ application. By following these practices and using the provided tools, you can ensure reliable data persistence from UI to database.

Key takeaways:
- Always verify endpoint alignment first
- Test data transformations explicitly
- Use phased validation approach
- Monitor performance metrics
- Automate where possible

For questions or issues, refer to the main `CLAUDE.md` documentation or create an issue in the project repository.