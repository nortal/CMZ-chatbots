#!/usr/bin/env python3
"""
Fix DynamoDB data to use proper String Sets for ID fields
"""

import boto3

# Configure DynamoDB
dynamodb_client = boto3.client('dynamodb', region_name='us-west-2')

def fix_user_family_ids():
    """Convert familyIds from List to String Set in user table"""
    print("Fixing user familyIds to use String Sets...")

    # Scan all users
    response = dynamodb_client.scan(TableName='quest-dev-user')
    users = response['Items']

    for user in users:
        user_id = user['userId']['S']

        # Check if familyIds exists and is a list
        if 'familyIds' in user and 'L' in user['familyIds']:
            family_list = user['familyIds']['L']

            if family_list:
                # Convert to String Set
                family_set = list(set([item['S'] for item in family_list if 'S' in item]))

                if family_set:
                    # Update the item with String Set
                    dynamodb_client.update_item(
                        TableName='quest-dev-user',
                        Key={'userId': {'S': user_id}},
                        UpdateExpression='SET familyIds = :fids',
                        ExpressionAttributeValues={
                            ':fids': {'SS': family_set}
                        }
                    )
                    print(f"  ✓ Updated {user_id}: familyIds = {family_set}")
                else:
                    # Remove empty familyIds
                    dynamodb_client.update_item(
                        TableName='quest-dev-user',
                        Key={'userId': {'S': user_id}},
                        UpdateExpression='REMOVE familyIds'
                    )
                    print(f"  ✓ Removed empty familyIds for {user_id}")
            else:
                # Remove empty list
                dynamodb_client.update_item(
                    TableName='quest-dev-user',
                    Key={'userId': {'S': user_id}},
                    UpdateExpression='REMOVE familyIds'
                )
                print(f"  ✓ Removed empty familyIds for {user_id}")

def fix_family_ids():
    """Convert parentIds and studentIds from List to String Set in family table"""
    print("\nFixing family parentIds and studentIds to use String Sets...")

    # Scan all families
    response = dynamodb_client.scan(TableName='quest-dev-family')
    families = response['Items']

    for family in families:
        family_id = family['familyId']['S']
        updates = {}

        # Check parentIds
        if 'parentIds' in family and 'L' in family['parentIds']:
            parent_list = family['parentIds']['L']
            if parent_list:
                parent_set = list(set([item['S'] for item in parent_list if 'S' in item]))
                if parent_set:
                    updates['parentIds'] = {'SS': parent_set}

        # Check studentIds
        if 'studentIds' in family and 'L' in family['studentIds']:
            student_list = family['studentIds']['L']
            if student_list:
                student_set = list(set([item['S'] for item in student_list if 'S' in item]))
                if student_set:
                    updates['studentIds'] = {'SS': student_set}

        # Apply updates if any
        if updates:
            # Build update expression
            set_expressions = []
            expression_values = {}

            if 'parentIds' in updates:
                set_expressions.append('parentIds = :pids')
                expression_values[':pids'] = updates['parentIds']

            if 'studentIds' in updates:
                set_expressions.append('studentIds = :sids')
                expression_values[':sids'] = updates['studentIds']

            if set_expressions:
                dynamodb_client.update_item(
                    TableName='quest-dev-family',
                    Key={'familyId': {'S': family_id}},
                    UpdateExpression='SET ' + ', '.join(set_expressions),
                    ExpressionAttributeValues=expression_values
                )
                print(f"  ✓ Updated {family_id}:")
                if 'parentIds' in updates:
                    print(f"    parentIds = {updates['parentIds']['SS']}")
                if 'studentIds' in updates:
                    print(f"    studentIds = {updates['studentIds']['SS']}")

def verify_data():
    """Verify the data is correct"""
    print("\n=== Verification ===")

    # Check a user
    print("\nChecking user parent_test_001...")
    response = dynamodb_client.get_item(
        TableName='quest-dev-user',
        Key={'userId': {'S': 'parent_test_001'}}
    )
    if 'Item' in response and 'familyIds' in response['Item']:
        family_ids = response['Item']['familyIds']
        if 'SS' in family_ids:
            print(f"  ✓ familyIds is String Set: {family_ids['SS']}")
        else:
            print(f"  ✗ familyIds is not String Set: {family_ids}")

    # Check a family
    print("\nChecking family family_test_001...")
    response = dynamodb_client.get_item(
        TableName='quest-dev-family',
        Key={'familyId': {'S': 'family_test_001'}}
    )
    if 'Item' in response:
        family = response['Item']
        if 'parentIds' in family and 'SS' in family['parentIds']:
            print(f"  ✓ parentIds is String Set: {family['parentIds']['SS']}")
        if 'studentIds' in family and 'SS' in family['studentIds']:
            print(f"  ✓ studentIds is String Set: {family['studentIds']['SS']}")

def main():
    """Main function"""
    print("=== Fixing DynamoDB Data to Use String Sets ===")

    fix_user_family_ids()
    fix_family_ids()
    verify_data()

    print("\n=== Complete ===")

if __name__ == '__main__':
    main()