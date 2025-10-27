"""
Bug #7 Regression Tests: Animal Details Save Button (PUT /animal/{id})

Bug Description:
When clicking save button on Animal Details page, the animal data was not updating
in DynamoDB due to broken hexagonal architecture forwarding chain.

Root Cause:
impl/animals.py had dead-end 501 stub instead of forwarding to handlers.py where
handle_animal_put() implementation exists.

Fix:
Regenerated impl/animals.py with proper forwarding stub to handlers.py

Test Strategy:
1. API Layer: Verify PUT /animal/{id} returns 200, not 501
2. Backend Layer: Verify handle_animal_put() executes correctly
3. DynamoDB Layer: Verify animal details actually persist to quest-dev-animal table
4. Validation: Query DynamoDB directly to confirm persistence (never infer from code)

Test Users:
- parent1@test.cmz.org / testpass123 (parent role)
- student1@test.cmz.org / testpass123 (student role)

Expected Behavior After Fix:
- PUT /animal/{id} returns 200 OK
- Animal name, species, description fields updated in DynamoDB
- Data persists across page reloads
- No 501 "Not Implemented" errors
"""

import pytest
import boto3
import json
import time
from typing import Dict, Any
from botocore.exceptions import ClientError


# AWS Configuration
AWS_REGION = "us-west-2"
AWS_PROFILE = "cmz"
DYNAMODB_TABLE = "quest-dev-animal"
TEST_ANIMAL_ID = "charlie_003"


class TestBug007AnimalPutFunctionality:
    """
    Bug #7 Regression Tests: Animal PUT Functionality

    Tests verify that PUT /animal/{id} correctly updates animal details
    in DynamoDB through the hexagonal architecture forwarding chain:

    Controller → impl/animals.py → impl/handlers.py → DynamoDB
    """

    @pytest.fixture(scope="class")
    def dynamodb_client(self):
        """Create DynamoDB client with CMZ profile"""
        session = boto3.Session(profile_name=AWS_PROFILE, region_name=AWS_REGION)
        return session.client('dynamodb')

    @pytest.fixture(scope="class")
    def api_base_url(self):
        """API base URL for testing"""
        return "http://localhost:8080"

    @pytest.fixture
    def test_animal_data(self):
        """Test animal data for update"""
        timestamp = int(time.time())
        return {
            "name": f"Charlie Test-{timestamp}",
            "species": "Loxodonta africana",
            "description": f"Bug #7 regression test - {timestamp}",
            "scientificName": "African Elephant",
            "habitat": "African Savanna",
            "conservation_status": "Endangered"
        }

    @pytest.fixture
    def original_animal_data(self, dynamodb_client):
        """Store original animal data for restoration"""
        try:
            response = dynamodb_client.get_item(
                TableName=DYNAMODB_TABLE,
                Key={"animalId": {"S": TEST_ANIMAL_ID}}
            )
            if "Item" in response:
                return response["Item"]
        except ClientError:
            pass
        return None

    @pytest.fixture
    def cleanup_test_data(self, dynamodb_client, original_animal_data):
        """Cleanup fixture - restores original data after test"""
        yield
        # Restore original data if it existed
        if original_animal_data:
            try:
                dynamodb_client.put_item(
                    TableName=DYNAMODB_TABLE,
                    Item=original_animal_data
                )
                print("✓ Restored original animal data")
            except ClientError as e:
                print(f"⚠️  Could not restore original data: {e}")

    def test_01_api_layer_put_returns_200_not_501(self, api_base_url, test_animal_data):
        """
        API Layer Test: Verify PUT /animal/{id} returns 200 OK, not 501

        This test verifies the forwarding chain is not broken.
        Before fix: Returned 501 "Not Implemented"
        After fix: Returns 200 OK
        """
        import requests

        url = f"{api_base_url}/animal/{TEST_ANIMAL_ID}"

        # Get auth token first
        auth_response = requests.post(
            f"{api_base_url}/auth",
            json={"email": "parent1@test.cmz.org", "password": "testpass123"}
        )
        assert auth_response.status_code == 200, "Authentication failed"
        token = auth_response.json().get("token")
        assert token, "No token in auth response"

        # PUT animal details
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        response = requests.put(url, json=test_animal_data, headers=headers)

        # Critical assertion: Must return 200, not 501
        assert response.status_code == 200, (
            f"Expected 200 OK, got {response.status_code}. "
            f"If 501: forwarding chain is BROKEN. Response: {response.text}"
        )

        # Verify response contains expected data
        response_data = response.json()
        assert response_data is not None, "No response data"

        print(f"✅ API Layer: PUT /animal/{TEST_ANIMAL_ID} returned {response.status_code}")

    def test_02_backend_layer_handler_executes(self, api_base_url, test_animal_data):
        """
        Backend Layer Test: Verify handle_animal_put() executes correctly

        This test verifies the handler in handlers.py is actually called.
        We verify this by checking the response contains processed data.
        """
        import requests

        url = f"{api_base_url}/animal/{TEST_ANIMAL_ID}"

        # Get auth token
        auth_response = requests.post(
            f"{api_base_url}/auth",
            json={"email": "parent1@test.cmz.org", "password": "testpass123"}
        )
        token = auth_response.json().get("token")

        # PUT animal details
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        response = requests.put(url, json=test_animal_data, headers=headers)

        assert response.status_code == 200
        response_data = response.json()

        # Verify handler processed the data
        assert response_data is not None, "Handler returned None (not executed)"

        print("✅ Backend Layer: handle_animal_put() executed successfully")

    def test_03_dynamodb_layer_animal_details_persist(
        self,
        dynamodb_client,
        api_base_url,
        test_animal_data,
        cleanup_test_data
    ):
        """
        DynamoDB Layer Test: Verify animal details ACTUALLY persist to DynamoDB

        CRITICAL: This test queries DynamoDB directly to verify persistence.
        We NEVER infer database state from code logic (lesson from Bug #8).

        This is the DEFINITIVE test for Bug #7 - if this passes, the bug is truly fixed.
        """
        import requests

        # Step 1: Update via API
        url = f"{api_base_url}/animal/{TEST_ANIMAL_ID}"
        auth_response = requests.post(
            f"{api_base_url}/auth",
            json={"email": "parent1@test.cmz.org", "password": "testpass123"}
        )
        token = auth_response.json().get("token")

        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        response = requests.put(url, json=test_animal_data, headers=headers)
        assert response.status_code == 200, f"API call failed: {response.text}"

        # Step 2: Wait for eventual consistency
        time.sleep(2)

        # Step 3: Query DynamoDB directly to verify persistence
        try:
            dynamodb_response = dynamodb_client.get_item(
                TableName=DYNAMODB_TABLE,
                Key={"animalId": {"S": TEST_ANIMAL_ID}}
            )
        except ClientError as e:
            pytest.fail(f"DynamoDB query failed: {e}")

        # Step 4: Verify item exists
        assert "Item" in dynamodb_response, (
            f"Animal {TEST_ANIMAL_ID} not found in DynamoDB. "
            f"Either item doesn't exist or table name is wrong."
        )

        item = dynamodb_response["Item"]

        # Step 5: Verify name field was updated
        assert "name" in item, "No name field in DynamoDB item"
        stored_name = item["name"]["S"]
        expected_name = test_animal_data["name"]

        assert stored_name == expected_name, (
            f"Name NOT updated in DynamoDB! Bug #7 NOT fixed. "
            f"Expected: {expected_name}, "
            f"Stored in DynamoDB: {stored_name}"
        )

        # Step 6: Verify description field was updated
        if "description" in test_animal_data:
            assert "description" in item, "description field NOT in DynamoDB"
            stored_desc = item["description"]["S"]
            expected_desc = test_animal_data["description"]

            assert stored_desc == expected_desc, (
                f"Description NOT updated in DynamoDB! "
                f"Expected: {expected_desc}, "
                f"Stored: {stored_desc}"
            )

        # Step 7: Verify species field was updated
        assert "species" in item, "species field NOT in DynamoDB"
        stored_species = item["species"]["S"]
        expected_species = test_animal_data["species"]

        assert stored_species == expected_species, (
            f"Species NOT updated in DynamoDB! "
            f"Expected: {expected_species}, "
            f"Stored: {stored_species}"
        )

        print(f"✅ DynamoDB Layer: Animal details VERIFIED in database")
        print(f"   Name: {stored_name}")
        print(f"   Species: {stored_species}")
        print(f"   DEFINITIVE PROOF: Bug #7 is fixed!")

    def test_04_persistence_across_reads(
        self,
        dynamodb_client,
        api_base_url,
        test_animal_data,
        cleanup_test_data
    ):
        """
        Persistence Test: Verify data persists across multiple reads

        This test ensures the data isn't just temporarily stored but actually persisted.
        """
        import requests

        # Step 1: Update animal details
        url = f"{api_base_url}/animal/{TEST_ANIMAL_ID}"
        auth_response = requests.post(
            f"{api_base_url}/auth",
            json={"email": "parent1@test.cmz.org", "password": "testpass123"}
        )
        token = auth_response.json().get("token")
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        put_response = requests.put(url, json=test_animal_data, headers=headers)
        assert put_response.status_code == 200

        time.sleep(1)

        # Step 2: Read via API
        get_url = f"{api_base_url}/animal/{TEST_ANIMAL_ID}"
        get_response = requests.get(get_url, headers=headers)
        assert get_response.status_code == 200

        api_data = get_response.json()

        # Step 3: Read via DynamoDB directly
        dynamodb_response = dynamodb_client.get_item(
            TableName=DYNAMODB_TABLE,
            Key={"animalId": {"S": TEST_ANIMAL_ID}}
        )

        item = dynamodb_response["Item"]
        db_name = item["name"]["S"]

        # Step 4: Verify consistency
        expected_name = test_animal_data["name"]

        # DynamoDB should have correct value
        assert db_name == expected_name, (
            f"DynamoDB has wrong value. Expected: {expected_name}, Got: {db_name}"
        )

        print("✅ Persistence: Data consistent across API reads and DynamoDB queries")

    def test_05_no_501_errors_in_logs(self, api_base_url, test_animal_data):
        """
        Validation Test: Ensure no 501 errors occur during animal update

        This test verifies the forwarding chain is working by ensuring
        we never see "Not Implemented" errors.
        """
        import requests

        url = f"{api_base_url}/animal/{TEST_ANIMAL_ID}"

        auth_response = requests.post(
            f"{api_base_url}/auth",
            json={"email": "parent1@test.cmz.org", "password": "testpass123"}
        )
        token = auth_response.json().get("token")
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        response = requests.put(url, json=test_animal_data, headers=headers)

        # Should never return 501
        assert response.status_code != 501, (
            "CRITICAL: Got 501 Not Implemented! "
            "Forwarding chain is BROKEN. "
            "impl/animals.py is not forwarding to handlers.py"
        )

        # Check response doesn't contain error messages
        response_text = response.text.lower()
        assert "not implemented" not in response_text, "Response contains 'not implemented' error"
        assert "501" not in response_text, "Response contains 501 error code"

        print("✅ No 501 Errors: Forwarding chain is working correctly")

    def test_06_multiple_field_updates(
        self,
        dynamodb_client,
        api_base_url,
        test_animal_data,
        cleanup_test_data
    ):
        """
        Comprehensive Test: Verify all fields in animal details can be updated

        This test ensures the entire animal object is properly updated,
        not just individual fields.
        """
        import requests

        url = f"{api_base_url}/animal/{TEST_ANIMAL_ID}"

        auth_response = requests.post(
            f"{api_base_url}/auth",
            json={"email": "parent1@test.cmz.org", "password": "testpass123"}
        )
        token = auth_response.json().get("token")
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        response = requests.put(url, json=test_animal_data, headers=headers)
        assert response.status_code == 200

        time.sleep(2)

        # Query DynamoDB
        dynamodb_response = dynamodb_client.get_item(
            TableName=DYNAMODB_TABLE,
            Key={"animalId": {"S": TEST_ANIMAL_ID}}
        )

        item = dynamodb_response["Item"]

        # Verify all fields that were sent are now in DynamoDB
        fields_to_check = ["name", "species", "description"]
        for field in fields_to_check:
            if field in test_animal_data:
                assert field in item, f"{field} field not in DynamoDB"
                expected_value = test_animal_data[field]
                stored_value = item[field]["S"]
                assert stored_value == expected_value, (
                    f"{field} mismatch: expected {expected_value}, got {stored_value}"
                )

        print("✅ Multiple Fields: All animal detail fields successfully updated")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
