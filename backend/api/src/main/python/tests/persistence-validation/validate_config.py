import json
import sys
from decimal import Decimal

def deserialize_dynamodb_item(item):
    """Convert DynamoDB format to Python dict"""
    result = {}
    for key, value in item.items():
        if 'S' in value:
            result[key] = value['S']
        elif 'N' in value:
            result[key] = float(value['N']) if '.' in value['N'] else int(value['N'])
        elif 'BOOL' in value:
            result[key] = value['BOOL']
        elif 'M' in value:
            result[key] = deserialize_dynamodb_item(value['M'])
        elif 'L' in value:
            result[key] = [deserialize_dynamodb_item({'item': v})['item'] if 'M' in v else v for v in value['L']]
        elif 'SS' in value:
            result[key] = value['SS']
        elif 'NULL' in value:
            result[key] = None
    return result

def validate_field(updated_data, test_data, field_path):
    """Validate a specific field was persisted correctly"""
    # Navigate to the field in both datasets
    updated_value = updated_data
    test_value = test_data

    for part in field_path.split('.'):
        if updated_value is None:
            return False, f"Field {field_path} not found in updated data"
        updated_value = updated_value.get(part)
        test_value = test_value.get(part)

    # Compare values (with type flexibility for numbers)
    if isinstance(test_value, (int, float)) and isinstance(updated_value, (int, float)):
        if abs(float(test_value) - float(updated_value)) < 0.0001:
            return True, f"✓ {field_path}: {updated_value}"
    elif test_value == updated_value:
        return True, f"✓ {field_path}: {updated_value}"
    else:
        return False, f"✗ {field_path}: expected {test_value}, got {updated_value}"

# Load data
with open('baseline-animal-config.json') as f:
    baseline = json.load(f)

with open('updated-animal-config.json') as f:
    updated = json.load(f)

with open('test-payload.json') as f:
    test_data = json.load(f)

# Deserialize DynamoDB items
baseline_data = deserialize_dynamodb_item(baseline.get('Item', {}))
updated_data = deserialize_dynamodb_item(updated.get('Item', {}))

print("Validation Results:")
print("-" * 40)

# Validate core configuration fields
core_fields = [
    'voice',
    'personality'
]

core_passed = 0
core_failed = 0

print("\nCore Configuration:")
for field in core_fields:
    passed, message = validate_field(updated_data, test_data, field)
    print(f"  {message}")
    if passed:
        core_passed += 1
    else:
        core_failed += 1

# Skip guardrails validation since we're not updating them
guardrails_passed = 0
guardrails_failed = 0

# Check audit fields
print("\nAudit Fields:")
if 'modified' in updated_data:
    if baseline_data.get('modified', {}).get('at') != updated_data['modified'].get('at'):
        print(f"  ✓ Modified timestamp updated")
    else:
        print(f"  ✗ Modified timestamp not updated")

# Summary
print("\n" + "=" * 40)
print("VALIDATION SUMMARY")
print("=" * 40)

total_passed = core_passed + guardrails_passed
total_failed = core_failed + guardrails_failed
success_rate = (total_passed / (total_passed + total_failed) * 100) if (total_passed + total_failed) > 0 else 0

print(f"Core Fields: {core_passed}/{core_passed + core_failed} passed")
print(f"Overall Success Rate: {success_rate:.1f}%")

if total_failed == 0:
    print(f"\n✓ All validations PASSED")
    sys.exit(0)
else:
    print(f"\n✗ {total_failed} validation(s) FAILED")
    sys.exit(1)
