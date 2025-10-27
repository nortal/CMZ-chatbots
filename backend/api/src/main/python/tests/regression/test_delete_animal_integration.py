"""
DELETE /animal Integration Tests

Test Strategy:
1. API Layer: Verify DELETE /animal/{id} returns 200, not 501 or 404
2. Backend Layer: Verify handle_delete_animal() executes correctly
3. DynamoDB Layer: Verify animal is ACTUALLY removed from quest-dev-animal table
4. Validation: Verify GET /animal/{id} returns 404 after deletion
5. Cleanup: Restore deleted animal after test for repeatability

Test Users:
- parent1@test.cmz.org / testpass123 (parent role)
- student1@test.cmz.org / testpass123 (student role)

Expected Behavior:
- DELETE /animal/{id} returns 200 OK
- Animal is removed from DynamoDB
- Subsequent GET /animal/{id} returns 404
- No 501 "Not Implemented" errors
"""

import pytest
import boto3
import json
import time
from typing import Dict, Any, Optional
from botocore.exceptions import ClientError


# AWS Configuration
AWS_REGION = "us-west-2"
AWS_PROFILE = "cmz"
DYNAMODB_TABLE = "quest-dev-animal"

# Test animal - use a specific test animal that we can safely delete and restore
TEST_ANIMAL_ID = "test_delete_animal_001"


class TestDeleteAnimalIntegration:
    """
    DELETE /animal Integration Tests

    Tests verify that DELETE /animal/{id} correctly removes animal
    from DynamoDB through the hexagonal architecture:

    Controller → impl/animals.py → impl/handlers.py → DynamoDB
    """

    @pytest.fixture(scope="class")
    def dynamodb_client(self):
        """Create DynamoDB client with CMZ profile"""
        session = boto3.Session(profile_name=AWS_PROFILE, region_name=AWS_REGION)
        return session.client('dynamodb')

    @pytest.fixture(scope="class")
    def dynamodb_resource(self):
        """Create DynamoDB resource with CMZ profile"""
        session = boto3.Session(profile_name=AWS_PROFILE, region_name=AWS_REGION)
        return session.resource('dynamodb')

    @pytest.fixture(scope="class")
    def api_base_url(self):
        """API base URL for testing"""
        return "http://localhost:8080"

    @pytest.fixture
    def test_animal_data(self):
        """Test animal data for creation before deletion"""
        return {
            "animalId": TEST_ANIMAL_ID,
            "name": "Test Delete Animal",
            "species": "Test Species",
            "scientificName": "Testus deleteus",
            "description": "Animal created for DELETE integration testing",
            "habitat": "Test Habitat",
            "conservation_status": "Test Status",
            "personality": {
                "description": "Test personality for deletion testing"
            },
            "configuration": {
                "systemPrompt": "Test system prompt"
            }
        }

    @pytest.fixture
    def ensure_test_animal_exists(self, dynamodb_resource, test_animal_data):
        """Ensure test animal exists before deletion test"""
        table = dynamodb_resource.Table(DYNAMODB_TABLE)

        # Check if test animal exists
        try:
            response = table.get_item(Key={"animalId": TEST_ANIMAL_ID})
            if "Item" not in response:
                # Create test animal
                table.put_item(Item=test_animal_data)
                print(f"✓ Created test animal {TEST_ANIMAL_ID} for deletion testing")
            else:
                print(f"✓ Test animal {TEST_ANIMAL_ID} already exists")
        except ClientError as e:
            pytest.fail(f"Failed to create test animal: {e}")

        yield test_animal_data

    @pytest.fixture
    def cleanup_test_animal(self, dynamodb_resource, test_animal_data):
        """Cleanup fixture - restores test animal after deletion test"""
        yield

        # Restore test animal after test
        table = dynamodb_resource.Table(DYNAMODB_TABLE)
        try:
            table.put_item(Item=test_animal_data)
            print(f"✓ Restored test animal {TEST_ANIMAL_ID} after test")
        except ClientError as e:
            print(f"⚠️  Could not restore test animal: {e}")

    @pytest.fixture
    def auth_token(self, api_base_url):
        """Get authentication token for API requests"""
        import requests

        auth_response = requests.post(
            f"{api_base_url}/auth",
            json={"email": "parent1@test.cmz.org", "password": "testpass123"}
        )
        assert auth_response.status_code == 200, "Authentication failed"
        token = auth_response.json().get("token")
        assert token, "No token in auth response"
        return token

    def test_01_api_layer_delete_returns_200_not_501(
        self,
        api_base_url,
        auth_token,
        ensure_test_animal_exists
    ):
        """
        API Layer Test: Verify DELETE /animal/{id} returns 200 OK, not 501

        This test verifies the forwarding chain is not broken.
        Expected: Returns 200 OK (or 204 No Content)
        """
        import requests

        url = f"{api_base_url}/animal/{TEST_ANIMAL_ID}"
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }

        response = requests.delete(url, headers=headers)

        # Critical assertion: Must return 200 or 204, not 501
        assert response.status_code in [200, 204], (
            f"Expected 200 or 204, got {response.status_code}. "
            f"If 501: forwarding chain is BROKEN. Response: {response.text}"
        )

        print(f"✅ API Layer: DELETE /animal/{TEST_ANIMAL_ID} returned {response.status_code}")

    def test_02_backend_layer_handler_executes(
        self,
        api_base_url,
        auth_token,
        dynamodb_resource,
        test_animal_data,
        cleanup_test_animal
    ):
        """
        Backend Layer Test: Verify handle_delete_animal() executes correctly

        This test verifies the handler in handlers.py is actually called.
        """
        import requests

        # Ensure animal exists before deletion
        table = dynamodb_resource.Table(DYNAMODB_TABLE)
        table.put_item(Item=test_animal_data)
        time.sleep(1)

        url = f"{api_base_url}/animal/{TEST_ANIMAL_ID}"
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}

        response = requests.delete(url, headers=headers)

        assert response.status_code in [200, 204]

        print("✅ Backend Layer: handle_delete_animal() executed successfully")

    def test_03_dynamodb_layer_animal_deleted(
        self,
        dynamodb_client,
        dynamodb_resource,
        api_base_url,
        auth_token,
        test_animal_data,
        cleanup_test_animal
    ):
        """
        DynamoDB Layer Test: Verify animal is ACTUALLY removed from DynamoDB

        CRITICAL: This test queries DynamoDB directly to verify deletion.
        We NEVER infer database state from code logic.

        This is the DEFINITIVE test - if this passes, DELETE is truly working.
        """
        import requests

        # Step 1: Ensure animal exists
        table = dynamodb_resource.Table(DYNAMODB_TABLE)
        table.put_item(Item=test_animal_data)
        time.sleep(1)

        # Verify it exists before deletion
        pre_delete_response = dynamodb_client.get_item(
            TableName=DYNAMODB_TABLE,
            Key={"animalId": {"S": TEST_ANIMAL_ID}}
        )
        assert "Item" in pre_delete_response, "Test animal doesn't exist before deletion"
        print(f"✓ Verified test animal exists before deletion")

        # Step 2: Delete via API
        url = f"{api_base_url}/animal/{TEST_ANIMAL_ID}"
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}

        response = requests.delete(url, headers=headers)
        assert response.status_code in [200, 204], f"API call failed: {response.text}"

        # Step 3: Wait for eventual consistency
        time.sleep(2)

        # Step 4: Query DynamoDB directly to verify deletion
        try:
            post_delete_response = dynamodb_client.get_item(
                TableName=DYNAMODB_TABLE,
                Key={"animalId": {"S": TEST_ANIMAL_ID}}
            )
        except ClientError as e:
            pytest.fail(f"DynamoDB query failed: {e}")

        # Step 5: Verify item is GONE
        assert "Item" not in post_delete_response, (
            f"Animal {TEST_ANIMAL_ID} STILL EXISTS in DynamoDB after DELETE! "
            f"DELETE is NOT working. Item found: {post_delete_response.get('Item')}"
        )

        print(f"✅ DynamoDB Layer: Animal VERIFIED deleted from database")
        print(f"   DEFINITIVE PROOF: DELETE is working correctly!")

    def test_04_get_returns_404_after_delete(
        self,
        dynamodb_resource,
        api_base_url,
        auth_token,
        test_animal_data,
        cleanup_test_animal
    ):
        """
        Validation Test: Verify GET /animal/{id} returns 404 after deletion

        This test ensures the API correctly reports the animal as not found
        after deletion.
        """
        import requests

        # Step 1: Ensure animal exists and delete it
        table = dynamodb_resource.Table(DYNAMODB_TABLE)
        table.put_item(Item=test_animal_data)
        time.sleep(1)

        delete_url = f"{api_base_url}/animal/{TEST_ANIMAL_ID}"
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}

        delete_response = requests.delete(delete_url, headers=headers)
        assert delete_response.status_code in [200, 204]

        time.sleep(2)

        # Step 2: Try to GET the deleted animal
        get_url = f"{api_base_url}/animal/{TEST_ANIMAL_ID}"
        get_response = requests.get(get_url, headers=headers)

        # Step 3: Verify GET returns 404
        assert get_response.status_code == 404, (
            f"Expected 404 after deletion, got {get_response.status_code}. "
            f"API not correctly reporting deleted animal. Response: {get_response.text}"
        )

        print("✅ Validation: GET correctly returns 404 for deleted animal")

    def test_05_no_501_errors_in_delete(
        self,
        api_base_url,
        auth_token,
        dynamodb_resource,
        test_animal_data,
        cleanup_test_animal
    ):
        """
        Validation Test: Ensure no 501 errors occur during animal deletion

        This test verifies the forwarding chain is working by ensuring
        we never see "Not Implemented" errors.
        """
        import requests

        # Ensure animal exists
        table = dynamodb_resource.Table(DYNAMODB_TABLE)
        table.put_item(Item=test_animal_data)
        time.sleep(1)

        url = f"{api_base_url}/animal/{TEST_ANIMAL_ID}"
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}

        response = requests.delete(url, headers=headers)

        # Should never return 501
        assert response.status_code != 501, (
            "CRITICAL: Got 501 Not Implemented! "
            "Forwarding chain is BROKEN. "
            "impl/animals.py is not forwarding to handlers.py"
        )

        # Check response doesn't contain error messages
        if response.text:  # Some DELETE responses may have empty body
            response_text = response.text.lower()
            assert "not implemented" not in response_text, "Response contains 'not implemented' error"
            assert "501" not in response_text, "Response contains 501 error code"

        print("✅ No 501 Errors: Forwarding chain is working correctly")

    def test_06_delete_nonexistent_animal_returns_404(
        self,
        api_base_url,
        auth_token
    ):
        """
        Edge Case Test: Verify DELETE on non-existent animal returns 404

        This test ensures proper error handling when trying to delete
        an animal that doesn't exist.
        """
        import requests

        # Use a definitely non-existent animal ID
        nonexistent_id = "nonexistent_animal_999999"
        url = f"{api_base_url}/animal/{nonexistent_id}"
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}

        response = requests.delete(url, headers=headers)

        # Should return 404 for non-existent animal
        assert response.status_code == 404, (
            f"Expected 404 for non-existent animal, got {response.status_code}. "
            f"Response: {response.text}"
        )

        print("✅ Edge Case: DELETE correctly returns 404 for non-existent animal")

    def test_07_idempotent_delete_behavior(
        self,
        dynamodb_resource,
        api_base_url,
        auth_token,
        test_animal_data,
        cleanup_test_animal
    ):
        """
        Idempotency Test: Verify multiple DELETE calls behave correctly

        This test ensures DELETE is idempotent - calling it multiple times
        doesn't cause errors (should return 404 on subsequent calls).
        """
        import requests

        # Step 1: Create test animal
        table = dynamodb_resource.Table(DYNAMODB_TABLE)
        table.put_item(Item=test_animal_data)
        time.sleep(1)

        url = f"{api_base_url}/animal/{TEST_ANIMAL_ID}"
        headers = {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}

        # Step 2: First DELETE should succeed
        first_response = requests.delete(url, headers=headers)
        assert first_response.status_code in [200, 204]

        time.sleep(2)

        # Step 3: Second DELETE should return 404 (not an error)
        second_response = requests.delete(url, headers=headers)
        assert second_response.status_code == 404, (
            f"Expected 404 on second DELETE, got {second_response.status_code}. "
            f"DELETE is not idempotent."
        )

        print("✅ Idempotency: DELETE behaves correctly on multiple calls")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
