#!/usr/bin/env python3
"""
Setup proper test data for bidirectional family-user references in DynamoDB
Creates users and families with correct ID-based references
"""

import boto3
import uuid
from datetime import datetime
from typing import Dict, List

# Configure DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
family_table = dynamodb.Table('quest-dev-family')
user_table = dynamodb.Table('quest-dev-user')

def create_audit_info(user_id: str, display_name: str) -> Dict:
    """Create audit information"""
    return {
        'at': datetime.utcnow().isoformat() + 'Z',
        'by': {
            'userId': user_id,
            'email': f"{user_id}@cmz.org",
            'displayName': display_name
        }
    }

def create_test_users() -> Dict[str, str]:
    """Create test users and return mapping of role to userId"""
    users = [
        {
            'userId': 'admin_test_001',
            'email': 'admin@cmz.org',
            'displayName': 'Test Admin',
            'role': 'admin',
            'familyIds': set(),  # Admins don't belong to families
            'password_hash': 'admin123',  # In production, this would be properly hashed
            'softDelete': False,
            'created': create_audit_info('system', 'System'),
            'modified': create_audit_info('system', 'System')
        },
        {
            'userId': 'parent_test_001',
            'email': 'parent1@test.cmz.org',
            'displayName': 'Test Parent One',
            'role': 'parent',
            'familyIds': set(['family_test_001']),  # Will be updated
            'phone': '555-0100',
            'isPrimaryContact': True,
            'isEmergencyContact': True,
            'password_hash': 'testpass123',
            'softDelete': False,
            'created': create_audit_info('system', 'System'),
            'modified': create_audit_info('system', 'System')
        },
        {
            'userId': 'parent_test_002',
            'email': 'parent2@test.cmz.org',
            'displayName': 'Test Parent Two',
            'role': 'parent',
            'familyIds': set(['family_test_001']),
            'phone': '555-0101',
            'isPrimaryContact': False,
            'isEmergencyContact': True,
            'password_hash': 'testpass123',
            'softDelete': False,
            'created': create_audit_info('system', 'System'),
            'modified': create_audit_info('system', 'System')
        },
        {
            'userId': 'student_test_001',
            'email': 'student1@test.cmz.org',
            'displayName': 'Test Student One',
            'role': 'student',
            'familyIds': set(['family_test_001']),
            'age': '10',
            'grade': '5th',
            'password_hash': 'testpass123',
            'softDelete': False,
            'created': create_audit_info('system', 'System'),
            'modified': create_audit_info('system', 'System')
        },
        {
            'userId': 'student_test_002',
            'email': 'student2@test.cmz.org',
            'displayName': 'Test Student Two',
            'role': 'student',
            'familyIds': set(['family_test_001']),
            'age': '8',
            'grade': '3rd',
            'password_hash': 'testpass123',
            'softDelete': False,
            'created': create_audit_info('system', 'System'),
            'modified': create_audit_info('system', 'System')
        }
    ]

    user_map = {}

    print("Creating test users...")
    for user in users:
        try:
            # Convert sets to lists for DynamoDB (DynamoDB stores as SS - String Set)
            if 'familyIds' in user and isinstance(user['familyIds'], set):
                user['familyIds'] = list(user['familyIds']) if user['familyIds'] else []

            user_table.put_item(Item=user)
            print(f"  ✓ Created user: {user['displayName']} ({user['userId']})")
            user_map[user['role']] = user['userId']
        except Exception as e:
            print(f"  ✗ Error creating user {user['email']}: {e}")

    return user_map

def create_test_families() -> None:
    """Create test families with bidirectional references"""
    families = [
        {
            'familyId': 'family_test_001',
            'familyName': 'Test Bidirectional Family',
            'parentIds': set(['parent_test_001', 'parent_test_002']),
            'studentIds': set(['student_test_001', 'student_test_002']),
            'status': 'active',
            'address': {
                'street': '123 Test Street',
                'city': 'Issaquah',
                'state': 'WA',
                'zipCode': '98027'
            },
            'preferredPrograms': ['Junior Zookeeper', 'Conservation Club'],
            'memberSince': '2024-01-15',
            'softDelete': False,
            'created': create_audit_info('system', 'System'),
            'modified': create_audit_info('system', 'System')
        },
        {
            'familyId': 'family_test_002',
            'familyName': 'Johnson Family',
            'parentIds': set(['parent_johnson_001']),
            'studentIds': set(['student_johnson_001', 'student_johnson_002']),
            'status': 'active',
            'preferredPrograms': ['Art & Animals', 'Science Club'],
            'memberSince': '2024-02-20',
            'softDelete': False,
            'created': create_audit_info('system', 'System'),
            'modified': create_audit_info('system', 'System')
        },
        {
            'familyId': 'family_test_003',
            'familyName': 'Rodriguez Family',
            'parentIds': set(['parent_rodriguez_001']),
            'studentIds': set(['student_rodriguez_001']),
            'status': 'active',
            'preferredPrograms': ['Tiny Tots', 'Music with Animals'],
            'memberSince': '2024-03-01',
            'softDelete': False,
            'created': create_audit_info('system', 'System'),
            'modified': create_audit_info('system', 'System')
        }
    ]

    print("\nCreating test families...")
    for family in families:
        try:
            # Convert sets to lists for DynamoDB
            if 'parentIds' in family and isinstance(family['parentIds'], set):
                family['parentIds'] = list(family['parentIds']) if family['parentIds'] else []
            if 'studentIds' in family and isinstance(family['studentIds'], set):
                family['studentIds'] = list(family['studentIds']) if family['studentIds'] else []

            family_table.put_item(Item=family)
            print(f"  ✓ Created family: {family['familyName']} ({family['familyId']})")
            print(f"    Parents: {family['parentIds']}")
            print(f"    Students: {family['studentIds']}")
        except Exception as e:
            print(f"  ✗ Error creating family {family['familyName']}: {e}")

def create_additional_family_users():
    """Create users for the other test families"""
    additional_users = [
        # Johnson Family
        {
            'userId': 'parent_johnson_001',
            'email': 'sarah.johnson@email.com',
            'displayName': 'Sarah Johnson',
            'role': 'parent',
            'familyIds': ['family_test_002'],
            'phone': '555-0200',
            'isPrimaryContact': True,
            'softDelete': False,
            'created': create_audit_info('system', 'System')
        },
        {
            'userId': 'student_johnson_001',
            'email': 'emma.johnson@email.com',
            'displayName': 'Emma Johnson',
            'role': 'student',
            'familyIds': ['family_test_002'],
            'age': '8',
            'grade': '3rd',
            'softDelete': False,
            'created': create_audit_info('system', 'System')
        },
        {
            'userId': 'student_johnson_002',
            'email': 'liam.johnson@email.com',
            'displayName': 'Liam Johnson',
            'role': 'student',
            'familyIds': ['family_test_002'],
            'age': '10',
            'grade': '5th',
            'softDelete': False,
            'created': create_audit_info('system', 'System')
        },
        # Rodriguez Family
        {
            'userId': 'parent_rodriguez_001',
            'email': 'maria.rodriguez@email.com',
            'displayName': 'Maria Rodriguez',
            'role': 'parent',
            'familyIds': ['family_test_003'],
            'phone': '555-0300',
            'isPrimaryContact': True,
            'softDelete': False,
            'created': create_audit_info('system', 'System')
        },
        {
            'userId': 'student_rodriguez_001',
            'email': 'sofia.rodriguez@email.com',
            'displayName': 'Sofia Rodriguez',
            'role': 'student',
            'familyIds': ['family_test_003'],
            'age': '6',
            'grade': '1st',
            'softDelete': False,
            'created': create_audit_info('system', 'System')
        }
    ]

    print("\nCreating additional family users...")
    for user in additional_users:
        try:
            user_table.put_item(Item=user)
            print(f"  ✓ Created user: {user['displayName']} ({user['userId']})")
        except Exception as e:
            print(f"  ✗ Error creating user {user['email']}: {e}")

def verify_bidirectional_references():
    """Verify that bidirectional references are working"""
    print("\n=== Verifying Bidirectional References ===")

    # Check family references
    print("\nChecking family_test_001...")
    try:
        family = family_table.get_item(Key={'familyId': 'family_test_001'})['Item']
        print(f"  Family Name: {family.get('familyName')}")
        print(f"  Parent IDs: {family.get('parentIds', [])}")
        print(f"  Student IDs: {family.get('studentIds', [])}")

        # Check that parents exist and have family reference
        for parent_id in family.get('parentIds', []):
            try:
                parent = user_table.get_item(Key={'userId': parent_id})['Item']
                print(f"  ✓ Parent {parent['displayName']} has familyIds: {parent.get('familyIds', [])}")
            except:
                print(f"  ✗ Parent {parent_id} not found")

        # Check that students exist and have family reference
        for student_id in family.get('studentIds', []):
            try:
                student = user_table.get_item(Key={'userId': student_id})['Item']
                print(f"  ✓ Student {student['displayName']} has familyIds: {student.get('familyIds', [])}")
            except:
                print(f"  ✗ Student {student_id} not found")

    except Exception as e:
        print(f"  ✗ Error checking family: {e}")

    # Verify admin user
    print("\nChecking admin user...")
    try:
        admin = user_table.get_item(Key={'userId': 'admin_test_001'})['Item']
        print(f"  ✓ Admin {admin['displayName']} exists")
        print(f"    Role: {admin.get('role')}")
        print(f"    Family IDs: {admin.get('familyIds', [])} (should be empty)")
    except Exception as e:
        print(f"  ✗ Error checking admin: {e}")

def main():
    """Main function to set up all test data"""
    print("=== Setting Up Bidirectional Test Data for DynamoDB ===")

    # Create users first
    user_map = create_test_users()

    # Create additional users for other families
    create_additional_family_users()

    # Create families with references to users
    create_test_families()

    # Verify everything is connected properly
    verify_bidirectional_references()

    print("\n=== Setup Complete ===")
    print("Test credentials:")
    print("  Admin: admin@cmz.org / admin123")
    print("  Parent: parent1@test.cmz.org / testpass123")
    print("  Student: student1@test.cmz.org / testpass123")

if __name__ == '__main__':
    main()