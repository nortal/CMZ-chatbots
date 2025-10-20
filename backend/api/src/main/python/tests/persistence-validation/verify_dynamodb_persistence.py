#!/usr/bin/env python3
"""
DynamoDB Data Persistence Verification Script
Validates that UI form submissions correctly persist to DynamoDB
"""

import json
import boto3
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
from decimal import Decimal

# AWS Configuration
AWS_REGION = 'us-west-2'
DYNAMODB_TABLE_PREFIX = 'quest-dev-'

# Initialize DynamoDB client
dynamodb = boto3.client('dynamodb', region_name=AWS_REGION)

def decimal_to_native(obj):
    """Convert DynamoDB Decimal types to native Python types"""
    if isinstance(obj, Decimal):
        return float(obj) if obj % 1 else int(obj)
    elif isinstance(obj, dict):
        return {k: decimal_to_native(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [decimal_to_native(item) for item in obj]
    return obj

def from_dynamodb_format(item: Dict) -> Dict:
    """Convert DynamoDB format to standard Python dict"""
    result = {}
    for key, value in item.items():
        if 'S' in value:
            result[key] = value['S']
        elif 'N' in value:
            result[key] = float(value['N']) if '.' in value['N'] else int(value['N'])
        elif 'BOOL' in value:
            result[key] = value['BOOL']
        elif 'M' in value:
            result[key] = from_dynamodb_format(value['M'])
        elif 'L' in value:
            result[key] = [from_dynamodb_format({'item': v})['item'] if 'M' in v else v for v in value['L']]
        elif 'SS' in value:
            result[key] = value['SS']
        elif 'NULL' in value:
            result[key] = None
    return result

def query_animal_config(animal_id: str) -> Optional[Dict]:
    """Query DynamoDB for specific animal configuration"""
    try:
        response = dynamodb.get_item(
            TableName=f'{DYNAMODB_TABLE_PREFIX}animal',
            Key={'animalId': {'S': animal_id}}
        )

        if 'Item' in response:
            return from_dynamodb_format(response['Item'])
        return None
    except Exception as e:
        print(f"Error querying DynamoDB: {e}")
        return None

def compare_data_fields(expected: Any, actual: Any, path: str = "") -> List[Dict]:
    """Recursively compare expected and actual data fields"""
    discrepancies = []

    if expected is None and actual is None:
        return []

    if type(expected) != type(actual):
        discrepancies.append({
            'path': path,
            'type': 'type_mismatch',
            'expected_type': type(expected).__name__,
            'actual_type': type(actual).__name__,
            'expected_value': expected,
            'actual_value': actual
        })
        return discrepancies

    if isinstance(expected, dict):
        all_keys = set(expected.keys()) | set(actual.keys() if actual else {})
        for key in all_keys:
            new_path = f"{path}.{key}" if path else key
            exp_val = expected.get(key)
            act_val = actual.get(key) if actual else None

            if key not in expected:
                discrepancies.append({
                    'path': new_path,
                    'type': 'unexpected_field',
                    'actual_value': act_val
                })
            elif actual is None or key not in actual:
                discrepancies.append({
                    'path': new_path,
                    'type': 'missing_field',
                    'expected_value': exp_val
                })
            else:
                discrepancies.extend(compare_data_fields(exp_val, act_val, new_path))

    elif isinstance(expected, list):
        if actual is None:
            discrepancies.append({
                'path': path,
                'type': 'missing_list',
                'expected_value': expected
            })
        elif len(expected) != len(actual):
            discrepancies.append({
                'path': path,
                'type': 'list_length_mismatch',
                'expected_length': len(expected),
                'actual_length': len(actual)
            })
        else:
            for i, (exp_item, act_item) in enumerate(zip(expected, actual)):
                discrepancies.extend(compare_data_fields(exp_item, act_item, f"{path}[{i}]"))

    elif expected != actual:
        discrepancies.append({
            'path': path,
            'type': 'value_mismatch',
            'expected_value': expected,
            'actual_value': actual
        })

    return discrepancies

def load_test_data() -> Dict:
    """Load test data from baseline file"""
    try:
        with open('baseline-data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Warning: baseline-data.json not found")
        return {}

def load_network_capture() -> Dict:
    """Load captured network data from Playwright test"""
    try:
        with open('network-capture.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Warning: network-capture.json not found")
        return {}

def generate_validation_report(test_data: Dict, db_data: Dict, network_data: Dict) -> Dict:
    """Generate comprehensive validation report"""

    # Expected data from test scenario
    expected_updates = test_data.get('test_scenarios', {}).get('animal_config_update', {}).get('test_data', {})

    # Compare expected vs actual
    discrepancies = []

    # Check voice configuration
    if 'voice' in expected_updates:
        actual_voice = db_data.get('voice', {})
        voice_discrepancies = compare_data_fields(expected_updates['voice'], actual_voice, 'voice')
        discrepancies.extend(voice_discrepancies)

    # Check guardrails configuration
    if 'guardrails' in expected_updates:
        actual_guardrails = db_data.get('guardrails', {})
        guardrails_discrepancies = compare_data_fields(expected_updates['guardrails'], actual_guardrails, 'guardrails')
        discrepancies.extend(guardrails_discrepancies)

    # Analyze audit fields
    audit_fields = {
        'modified': db_data.get('modified'),
        'created': db_data.get('created'),
        'updatedBy': db_data.get('updatedBy')
    }

    # Calculate success metrics
    total_expected_fields = count_fields(expected_updates)
    total_actual_fields = count_fields(db_data)
    discrepancy_count = len(discrepancies)
    success_rate = ((total_expected_fields - discrepancy_count) / total_expected_fields * 100) if total_expected_fields > 0 else 0

    report = {
        'timestamp': datetime.now().isoformat(),
        'test_scenario': 'Animal Configuration Data Persistence',
        'entity_tested': test_data.get('test_scenarios', {}).get('animal_config_update', {}).get('target_id'),
        'validation_results': {
            'total_expected_fields': total_expected_fields,
            'total_actual_fields': total_actual_fields,
            'discrepancy_count': discrepancy_count,
            'success_rate': f"{success_rate:.2f}%",
            'data_integrity': 'PASS' if discrepancy_count == 0 else 'FAIL'
        },
        'discrepancies': discrepancies,
        'audit_trail': audit_fields,
        'network_analysis': {
            'requests_captured': len(network_data.get('requests', [])),
            'responses_captured': len(network_data.get('responses', [])),
            'form_fields_submitted': len(network_data.get('formDataSubmitted', {}))
        },
        'recommendations': []
    }

    # Add recommendations based on findings
    if discrepancy_count > 0:
        report['recommendations'].append("Review data transformation logic in API layer")
        report['recommendations'].append("Verify form field to database field mapping")

        # Check for specific issues
        for disc in discrepancies:
            if disc['type'] == 'missing_field':
                report['recommendations'].append(f"Ensure field '{disc['path']}' is being saved to database")
            elif disc['type'] == 'type_mismatch':
                report['recommendations'].append(f"Fix type conversion for field '{disc['path']}'")

    return report

def count_fields(obj: Any, depth: int = 0) -> int:
    """Recursively count fields in nested structure"""
    if depth > 10:  # Prevent infinite recursion
        return 0

    count = 0
    if isinstance(obj, dict):
        for value in obj.values():
            count += 1 + count_fields(value, depth + 1)
    elif isinstance(obj, list):
        count += len(obj)
        for item in obj:
            count += count_fields(item, depth + 1)
    else:
        count += 1
    return count

def main():
    """Main validation workflow"""
    print("=" * 60)
    print("DynamoDB Data Persistence Validation")
    print("=" * 60)

    # Load test data
    print("\n1. Loading test data...")
    test_data = load_test_data()
    network_data = load_network_capture()

    # Get target animal ID
    animal_id = test_data.get('test_scenarios', {}).get('animal_config_update', {}).get('target_id', 'leo_001')
    print(f"   Target entity: {animal_id}")

    # Query current database state
    print("\n2. Querying DynamoDB...")
    db_data = query_animal_config(animal_id)

    if db_data:
        print(f"   ✅ Retrieved animal data from DynamoDB")
        print(f"   Fields present: {', '.join(db_data.keys())}")
    else:
        print(f"   ❌ No data found for animal ID: {animal_id}")
        sys.exit(1)

    # Generate validation report
    print("\n3. Analyzing data consistency...")
    report = generate_validation_report(test_data, db_data, network_data)

    # Save report
    with open('validation-report-final.json', 'w') as f:
        json.dump(report, f, indent=2, default=str)
    print("   Report saved to validation-report-final.json")

    # Print summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Entity Tested: {report['entity_tested']}")
    print(f"Data Integrity: {report['validation_results']['data_integrity']}")
    print(f"Success Rate: {report['validation_results']['success_rate']}")
    print(f"Discrepancies Found: {report['validation_results']['discrepancy_count']}")

    if report['discrepancies']:
        print("\nDiscrepancy Details:")
        for disc in report['discrepancies'][:5]:  # Show first 5 discrepancies
            print(f"  - {disc['path']}: {disc['type']}")
            if 'expected_value' in disc:
                print(f"    Expected: {disc['expected_value']}")
            if 'actual_value' in disc:
                print(f"    Actual: {disc['actual_value']}")

    if report['recommendations']:
        print("\nRecommendations:")
        for rec in report['recommendations']:
            print(f"  • {rec}")

    print("\n" + "=" * 60)

    # Exit with appropriate code
    sys.exit(0 if report['validation_results']['data_integrity'] == 'PASS' else 1)

if __name__ == "__main__":
    main()