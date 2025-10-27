#!/usr/bin/env python3
"""
Migration script to convert existing family data to bidirectional references model.

Old model: Families store parent/student names as strings
New model: Families store parentIds/studentIds, Users store familyIds
"""

import boto3
import uuid
from datetime import datetime
from typing import Dict, List, Set

# Configure DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
family_table = dynamodb.Table('quest-dev-family')
user_table = dynamodb.Table('quest-dev-user')

def create_user_id(name: str, role: str) -> str:
    """Generate a consistent user ID from name and role"""
    # Create a deterministic ID based on name and role
    clean_name = name.lower().replace(' ', '_').replace('.', '_')
    return f"user_{role}_{clean_name}_{uuid.uuid4().hex[:8]}"

def get_or_create_user(name: str, role: str, family_id: str) -> str:
    """Get existing user or create new one"""
    # For this migration, we'll create new users for each parent/student
    # In production, you'd want to match existing users by email

    user_id = create_user_id(name, role)
    email = f"{name.lower().replace(' ', '.')}@migration.cmz.org"

    # Check if user exists (by email)
    response = user_table.scan(
        FilterExpression='email = :email',
        ExpressionAttributeValues={':email': email}
    )

    if response['Items']:
        # User exists, update with family ID
        existing_user = response['Items'][0]
        user_id = existing_user['userId']

        # Add family ID to user's familyIds
        family_ids = existing_user.get('familyIds', [])
        if family_id not in family_ids:
            family_ids.append(family_id)

        user_table.update_item(
            Key={'userId': user_id},
            UpdateExpression='SET familyIds = :fids, #r = :role',
            ExpressionAttributeNames={'#r': 'role'},
            ExpressionAttributeValues={
                ':fids': family_ids,
                ':role': role
            }
        )
    else:
        # Create new user with bidirectional reference
        user_item = {
            'userId': user_id,
            'email': email,
            'displayName': name,
            'role': role,
            'familyIds': [family_id],
            'created': {
                'at': datetime.utcnow().isoformat() + 'Z',
                'by': {
                    'userId': 'migration_script',
                    'displayName': 'Migration Script'
                }
            },
            'softDelete': False
        }

        # Add parent-specific fields
        if role == 'parent':
            user_item['phone'] = '555-0000'  # Default phone
            user_item['isPrimaryContact'] = False
            user_item['isEmergencyContact'] = False

        # Add student-specific fields
        if role == 'student':
            user_item['age'] = '10'  # Default age
            user_item['grade'] = '5th'  # Default grade

        user_table.put_item(Item=user_item)

    return user_id

def migrate_family(family: Dict) -> None:
    """Migrate a single family to bidirectional model"""
    family_id = family['familyId']
    print(f"\nMigrating family: {family_id}")

    # Extract current parents and students (strings)
    parents = family.get('parents', [])
    students = family.get('students', [])

    # Skip if already migrated (has parentIds/studentIds)
    if 'parentIds' in family and 'studentIds' in family:
        print(f"  ✓ Family {family_id} already migrated")
        return

    # Create/find users and get their IDs
    parent_ids = []
    student_ids = []

    # Process parents
    for parent_name in parents:
        if isinstance(parent_name, str) and parent_name.strip():
            user_id = get_or_create_user(parent_name, 'parent', family_id)
            parent_ids.append(user_id)
            print(f"  + Created/updated parent: {parent_name} -> {user_id}")

    # Process students
    for student_name in students:
        if isinstance(student_name, str) and student_name.strip():
            user_id = get_or_create_user(student_name, 'student', family_id)
            student_ids.append(user_id)
            print(f"  + Created/updated student: {student_name} -> {user_id}")

    # Update family with new structure
    update_expression = 'SET parentIds = :pids, studentIds = :sids'
    expression_values = {
        ':pids': parent_ids,
        ':sids': student_ids
    }

    # Add modified timestamp
    update_expression += ', modified = :mod'
    expression_values[':mod'] = {
        'at': datetime.utcnow().isoformat() + 'Z',
        'by': {
            'userId': 'migration_script',
            'displayName': 'Migration Script'
        }
    }

    # Keep original parents/students for rollback capability
    update_expression += ', parents_backup = :pb, students_backup = :sb'
    expression_values[':pb'] = parents
    expression_values[':sb'] = students

    family_table.update_item(
        Key={'familyId': family_id},
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_values
    )

    print(f"  ✓ Family {family_id} migrated successfully")

def add_test_users():
    """Add our test users for authentication"""
    test_users = [
        {
            'userId': 'user_admin_cmz_org',
            'email': 'admin@cmz.org',
            'displayName': 'Admin User',
            'role': 'admin',
            'familyIds': [],
            'password_hash': 'admin123',  # In production, this would be properly hashed
            'softDelete': False
        },
        {
            'userId': 'user_test_cmz_org',
            'email': 'test@cmz.org',
            'displayName': 'Test Admin',
            'role': 'admin',
            'familyIds': [],
            'password_hash': 'testpass123',
            'softDelete': False
        },
        {
            'userId': 'user_parent1_test_cmz_org',
            'email': 'parent1@test.cmz.org',
            'displayName': 'Test Parent One',
            'role': 'parent',
            'familyIds': [],
            'password_hash': 'testpass123',
            'softDelete': False
        }
    ]

    print("\n=== Adding Test Users ===")
    for user in test_users:
        try:
            # Check if user exists
            response = user_table.get_item(Key={'userId': user['userId']})
            if 'Item' in response:
                print(f"  ✓ User {user['email']} already exists")
            else:
                user_table.put_item(Item=user)
                print(f"  + Created test user: {user['email']}")
        except Exception as e:
            print(f"  ✗ Error creating user {user['email']}: {e}")

def main():
    """Main migration function"""
    print("=== DynamoDB Family-User Bidirectional Migration ===")
    print("Converting families from name-based to ID-based references...")

    # First, add test users
    add_test_users()

    # Scan all families
    print("\n=== Migrating Families ===")
    response = family_table.scan()
    families = response['Items']

    # Handle pagination
    while 'LastEvaluatedKey' in response:
        response = family_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        families.extend(response['Items'])

    print(f"Found {len(families)} families to migrate")

    # Migrate each family
    migrated_count = 0
    for family in families:
        # Skip soft-deleted families
        if family.get('softDelete', False):
            print(f"\n  ⊘ Skipping soft-deleted family: {family['familyId']}")
            continue

        try:
            migrate_family(family)
            migrated_count += 1
        except Exception as e:
            print(f"\n  ✗ Error migrating family {family.get('familyId', 'unknown')}: {e}")

    print(f"\n=== Migration Complete ===")
    print(f"Successfully migrated {migrated_count} families")

    # Verify migration
    print("\n=== Verification ===")

    # Check a sample family
    response = family_table.scan(Limit=1)
    if response['Items']:
        sample_family = response['Items'][0]
        print(f"\nSample family structure:")
        print(f"  Family ID: {sample_family.get('familyId')}")
        print(f"  Parent IDs: {sample_family.get('parentIds', [])}")
        print(f"  Student IDs: {sample_family.get('studentIds', [])}")

        # Check if users have familyIds
        if sample_family.get('parentIds'):
            parent_id = sample_family['parentIds'][0]
            parent = user_table.get_item(Key={'userId': parent_id})
            if 'Item' in parent:
                print(f"  Parent {parent_id} has familyIds: {parent['Item'].get('familyIds', [])}")

if __name__ == '__main__':
    main()