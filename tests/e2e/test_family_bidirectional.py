#!/usr/bin/env python3
"""
End-to-end tests for bidirectional family-user relationships
Tests create, read, update, delete operations and validates DynamoDB persistence
"""

import time
import json
import uuid
import pytest
from typing import Dict, Any, List
from playwright.sync_api import sync_playwright
import boto3
from botocore.exceptions import ClientError

# Configuration
API_BASE_URL = "http://localhost:8080"
FRONTEND_URL = "http://localhost:3001"
AWS_REGION = "us-west-2"
AWS_PROFILE = "cmz"

# DynamoDB table names
USER_TABLE = "quest-dev-user"
FAMILY_TABLE = "quest-dev-family"


class TestFamilyBidirectional:
    """Test suite for bidirectional family-user relationships"""

    @classmethod
    def setup_class(cls):
        """Set up test environment"""
        # Initialize DynamoDB client
        session = boto3.Session(profile_name=AWS_PROFILE)
        cls.dynamodb = session.resource('dynamodb', region_name=AWS_REGION)
        cls.user_table = cls.dynamodb.Table(USER_TABLE)
        cls.family_table = cls.dynamodb.Table(FAMILY_TABLE)

        # Test data
        cls.admin_user = {
            "userId": f"test_admin_{uuid.uuid4().hex[:8]}",
            "email": "admin@test.cmz.org",
            "displayName": "Test Admin",
            "role": "admin",
            "familyIds": set()
        }

        cls.parent_user = {
            "userId": f"test_parent_{uuid.uuid4().hex[:8]}",
            "email": "parent@test.cmz.org",
            "displayName": "Test Parent",
            "role": "parent",
            "familyIds": set()
        }

        cls.student_user = {
            "userId": f"test_student_{uuid.uuid4().hex[:8]}",
            "email": "student@test.cmz.org",
            "displayName": "Test Student",
            "role": "student",
            "familyIds": set()
        }

        cls.test_family = {
            "familyId": f"test_family_{uuid.uuid4().hex[:8]}",
            "familyName": "Test Family",
            "parentIds": set(),
            "studentIds": set(),
            "status": "active",
            "softDelete": False
        }

        # Create test users in DynamoDB
        cls._create_test_user(cls.admin_user)
        cls._create_test_user(cls.parent_user)
        cls._create_test_user(cls.student_user)

    @classmethod
    def teardown_class(cls):
        """Clean up test data"""
        # Delete test users
        for user_id in [cls.admin_user['userId'], cls.parent_user['userId'], cls.student_user['userId']]:
            try:
                cls.user_table.delete_item(Key={'userId': user_id})
            except:
                pass

        # Delete test family if created
        try:
            cls.family_table.delete_item(Key={'familyId': cls.test_family['familyId']})
        except:
            pass

    @classmethod
    def _create_test_user(cls, user_data: Dict[str, Any]):
        """Helper to create test user in DynamoDB"""
        try:
            cls.user_table.put_item(
                Item={
                    'userId': user_data['userId'],
                    'email': user_data['email'],
                    'displayName': user_data['displayName'],
                    'role': user_data['role'],
                    'familyIds': list(user_data.get('familyIds', [])),
                    'softDelete': False,
                    'created': {
                        'at': time.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                        'by': {'displayName': 'test_setup'}
                    }
                }
            )
            print(f"Created test user: {user_data['userId']}")
        except Exception as e:
            print(f"Error creating test user: {e}")

    def test_01_create_family_as_admin(self):
        """Test that admin can create a family with bidirectional references"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            # Navigate to API endpoint (simulating backend call)
            # In real test, would login first and use auth token
            response = page.request.post(
                f"{API_BASE_URL}/family",
                headers={
                    "Content-Type": "application/json",
                    "X-User-Id": self.admin_user['userId']  # Simulating authenticated user
                },
                data={
                    "familyName": "Johnson Test Family",
                    "parents": [
                        {
                            "email": "sarah.johnson@test.com",
                            "name": "Sarah Johnson",
                            "phone": "555-0101",
                            "isPrimary": True
                        },
                        {
                            "email": "mike.johnson@test.com",
                            "name": "Mike Johnson",
                            "phone": "555-0102"
                        }
                    ],
                    "students": [
                        {
                            "name": "Emma Johnson",
                            "age": "10",
                            "grade": "5th"
                        },
                        {
                            "name": "Liam Johnson",
                            "age": "8",
                            "grade": "3rd"
                        }
                    ],
                    "address": {
                        "street": "123 Test Lane",
                        "city": "Issaquah",
                        "state": "WA",
                        "zip": "98027"
                    },
                    "preferredPrograms": ["Junior Zookeeper", "Conservation Club"],
                    "status": "active"
                }
            )

            # Check response
            assert response.status == 201, f"Expected 201, got {response.status}"
            family_data = response.json()
            self.test_family['familyId'] = family_data['familyId']

            # Verify family in DynamoDB
            time.sleep(1)  # Allow for eventual consistency
            family = self.family_table.get_item(Key={'familyId': family_data['familyId']})
            assert 'Item' in family, "Family not found in DynamoDB"

            # Check bidirectional references
            family_item = family['Item']
            assert 'parentIds' in family_item, "parentIds not in family"
            assert 'studentIds' in family_item, "studentIds not in family"
            assert len(family_item['parentIds']) == 2, "Should have 2 parents"
            assert len(family_item['studentIds']) == 2, "Should have 2 students"

            # Verify parent users have family reference
            for parent_id in family_item['parentIds']:
                user = self.user_table.get_item(Key={'userId': parent_id})
                assert 'Item' in user, f"Parent {parent_id} not found"
                assert family_data['familyId'] in user['Item'].get('familyIds', []), \
                    f"Family ID not in parent's familyIds"

            # Verify student users have family reference
            for student_id in family_item['studentIds']:
                user = self.user_table.get_item(Key={'userId': student_id})
                assert 'Item' in user, f"Student {student_id} not found"
                assert family_data['familyId'] in user['Item'].get('familyIds', []), \
                    f"Family ID not in student's familyIds"

            browser.close()
            print("✅ Admin can create family with bidirectional references")

    def test_02_member_can_view_family(self):
        """Test that family members can view their family"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            # First, add parent to test family
            self._add_user_to_family(self.parent_user['userId'], self.test_family['familyId'], 'parent')

            # Parent tries to view family
            response = page.request.get(
                f"{API_BASE_URL}/family/{self.test_family['familyId']}",
                headers={
                    "X-User-Id": self.parent_user['userId']
                }
            )

            assert response.status == 200, f"Parent should be able to view family, got {response.status}"
            family_data = response.json()

            # Check response includes proper flags
            assert family_data['canView'] == True, "Parent should have view permission"
            assert family_data['canEdit'] == False, "Parent should NOT have edit permission"

            browser.close()
            print("✅ Family members can view their family")

    def test_03_non_member_cannot_view_family(self):
        """Test that non-members cannot view a family"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            # Create a non-member user
            non_member = {
                "userId": f"test_nonmember_{uuid.uuid4().hex[:8]}",
                "email": "nonmember@test.com",
                "displayName": "Non Member",
                "role": "parent",
                "familyIds": set()
            }
            self._create_test_user(non_member)

            # Non-member tries to view family
            response = page.request.get(
                f"{API_BASE_URL}/family/{self.test_family['familyId']}",
                headers={
                    "X-User-Id": non_member['userId']
                }
            )

            assert response.status == 403, f"Non-member should get 403, got {response.status}"

            # Cleanup
            self.user_table.delete_item(Key={'userId': non_member['userId']})

            browser.close()
            print("✅ Non-members cannot view family")

    def test_04_only_admin_can_edit_family(self):
        """Test that only admins can edit family details"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            # Parent tries to edit family (should fail)
            response = page.request.patch(
                f"{API_BASE_URL}/family/{self.test_family['familyId']}",
                headers={
                    "Content-Type": "application/json",
                    "X-User-Id": self.parent_user['userId']
                },
                data={
                    "familyName": "Updated Family Name"
                }
            )

            assert response.status == 403, f"Parent edit should fail with 403, got {response.status}"

            # Admin edits family (should succeed)
            response = page.request.patch(
                f"{API_BASE_URL}/family/{self.test_family['familyId']}",
                headers={
                    "Content-Type": "application/json",
                    "X-User-Id": self.admin_user['userId']
                },
                data={
                    "familyName": "Admin Updated Family"
                }
            )

            assert response.status == 200, f"Admin edit should succeed with 200, got {response.status}"

            # Verify update in DynamoDB
            time.sleep(1)
            family = self.family_table.get_item(Key={'familyId': self.test_family['familyId']})
            assert family['Item']['familyName'] == "Admin Updated Family", "Family name not updated"

            browser.close()
            print("✅ Only admins can edit families")

    def test_05_validate_bidirectional_consistency(self):
        """Validate that bidirectional references are consistent"""
        # Get family from DynamoDB
        family = self.family_table.get_item(Key={'familyId': self.test_family['familyId']})
        family_item = family['Item']

        all_user_ids = list(family_item.get('parentIds', [])) + list(family_item.get('studentIds', []))

        # Check each user has the family in their familyIds
        for user_id in all_user_ids:
            user = self.user_table.get_item(Key={'userId': user_id})
            if 'Item' in user:
                assert self.test_family['familyId'] in user['Item'].get('familyIds', []), \
                    f"User {user_id} missing family reference"

        # Check that users who claim this family are actually in the family
        scan_response = self.user_table.scan(
            FilterExpression="contains(familyIds, :fid)",
            ExpressionAttributeValues={':fid': self.test_family['familyId']}
        )

        for user_item in scan_response.get('Items', []):
            user_id = user_item['userId']
            assert user_id in all_user_ids, \
                f"User {user_id} claims family but not in family's user lists"

        print("✅ Bidirectional references are consistent")

    def test_06_delete_family_removes_references(self):
        """Test that deleting a family removes references from all users"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            # Get current family members before deletion
            family = self.family_table.get_item(Key={'familyId': self.test_family['familyId']})
            all_user_ids = list(family['Item'].get('parentIds', [])) + \
                          list(family['Item'].get('studentIds', []))

            # Admin deletes family
            response = page.request.delete(
                f"{API_BASE_URL}/family/{self.test_family['familyId']}",
                headers={
                    "X-User-Id": self.admin_user['userId']
                }
            )

            assert response.status == 200, f"Delete should succeed with 200, got {response.status}"

            # Verify soft delete in DynamoDB
            time.sleep(1)
            family = self.family_table.get_item(Key={'familyId': self.test_family['familyId']})
            assert family['Item']['softDelete'] == True, "Family not soft deleted"

            # Verify users no longer have family reference
            for user_id in all_user_ids:
                user = self.user_table.get_item(Key={'userId': user_id})
                if 'Item' in user:
                    assert self.test_family['familyId'] not in user['Item'].get('familyIds', []), \
                        f"User {user_id} still has deleted family reference"

            browser.close()
            print("✅ Deleting family removes all user references")

    def _add_user_to_family(self, user_id: str, family_id: str, role: str):
        """Helper to add user to family with bidirectional reference"""
        # Update family
        if role == 'parent':
            self.family_table.update_item(
                Key={'familyId': family_id},
                UpdateExpression='ADD parentIds :uid',
                ExpressionAttributeValues={':uid': {user_id}}
            )
        else:
            self.family_table.update_item(
                Key={'familyId': family_id},
                UpdateExpression='ADD studentIds :uid',
                ExpressionAttributeValues={':uid': {user_id}}
            )

        # Update user
        self.user_table.update_item(
            Key={'userId': user_id},
            UpdateExpression='ADD familyIds :fid',
            ExpressionAttributeValues={':fid': {family_id}}
        )


if __name__ == "__main__":
    # Run tests
    test_suite = TestFamilyBidirectional()
    test_suite.setup_class()

    try:
        print("\n🧪 Starting Family Bidirectional E2E Tests\n")
        test_suite.test_01_create_family_as_admin()
        test_suite.test_02_member_can_view_family()
        test_suite.test_03_non_member_cannot_view_family()
        test_suite.test_04_only_admin_can_edit_family()
        test_suite.test_05_validate_bidirectional_consistency()
        test_suite.test_06_delete_family_removes_references()
        print("\n✅ All tests passed!")
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
    finally:
        test_suite.teardown_class()
        print("\n🧹 Cleanup completed")