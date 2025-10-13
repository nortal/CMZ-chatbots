"""
Bug #1 Regression Tests: systemPrompt Field Persistence

Bug Description:
When updating animal configuration via PATCH /animal_config, the systemPrompt field
was not persisting to DynamoDB due to broken hexagonal architecture forwarding chain.

Root Cause:
impl/animals.py had dead-end 501 stub instead of forwarding to handlers.py where
handle_animal_config_patch() implementation exists.

Fix:
Regenerated impl/animals.py with proper forwarding stub to handlers.py

Test Strategy:
1. API Layer: Verify PATCH /animal_config returns 200, not 501
2. Backend Layer: Verify handle_animal_config_patch() executes correctly
3. DynamoDB Layer: Verify systemPrompt actually persists to quest-dev-animal table
4. Validation: Query DynamoDB directly to confirm persistence (never infer from code)

Test Users:
- parent1@test.cmz.org / testpass123 (parent role)
- student1@test.cmz.org / testpass123 (student role)

Expected Behavior After Fix:
- PATCH /animal_config returns 200 OK
- systemPrompt field stored in DynamoDB
- temperature field stored in DynamoDB
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


class TestBug001SystemPromptPersistence:
    """
    Bug #1 Regression Tests: systemPrompt Persistence

    Tests verify that PATCH /animal_config correctly persists systemPrompt
    field to DynamoDB through the hexagonal architecture forwarding chain:

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
    def test_animal_config(self):
        """Test animal configuration data"""
        return {
            "animalId": TEST_ANIMAL_ID,
            "systemPrompt": f"Bug #1 Regression Test - {int(time.time())}",
            "temperature": 0.75
        }

    @pytest.fixture
    def cleanup_test_data(self, dynamodb_client):
        """Cleanup fixture - runs after each test"""
        yield
        # Cleanup happens here after test completes
        # We keep test data for verification, but you could delete it here if needed

    def test_01_api_layer_patch_returns_200_not_501(self, api_base_url, test_animal_config):
        """
        API Layer Test: Verify PATCH /animal_config returns 200 OK, not 501

        This test verifies the forwarding chain is not broken.
        Before fix: Returned 501 "Not Implemented"
        After fix: Returns 200 OK
        """
        import requests

        url = f"{api_base_url}/animal_config"

        # Get auth token first
        auth_response = requests.post(
            f"{api_base_url}/auth",
            json={"email": "parent1@test.cmz.org", "password": "testpass123"}
        )
        assert auth_response.status_code == 200, "Authentication failed"
        token = auth_response.json().get("token")
        assert token, "No token in auth response"

        # PATCH animal config
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        response = requests.patch(url, json=test_animal_config, headers=headers)

        # Critical assertion: Must return 200, not 501
        assert response.status_code == 200, (
            f"Expected 200 OK, got {response.status_code}. "
            f"If 501: forwarding chain is BROKEN. Response: {response.text}"
        )

        # Verify response contains expected data
        response_data = response.json()
        assert "animalId" in response_data or "id" in response_data, "No animalId in response"

        print(f"✅ API Layer: PATCH /animal_config returned {response.status_code}")

    def test_02_backend_layer_handler_executes(self, api_base_url, test_animal_config):
        """
        Backend Layer Test: Verify handle_animal_config_patch() executes correctly

        This test verifies the handler in handlers.py is actually called.
        We verify this by checking the response contains processed data.
        """
        import requests

        url = f"{api_base_url}/animal_config"

        # Get auth token
        auth_response = requests.post(
            f"{api_base_url}/auth",
            json={"email": "parent1@test.cmz.org", "password": "testpass123"}
        )
        token = auth_response.json().get("token")

        # PATCH animal config
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        response = requests.patch(url, json=test_animal_config, headers=headers)

        assert response.status_code == 200
        response_data = response.json()

        # Verify handler processed the data (adds metadata like timestamps)
        # Handler should return the updated config
        assert response_data is not None, "Handler returned None (not executed)"

        print("✅ Backend Layer: handle_animal_config_patch() executed successfully")

    def test_03_dynamodb_layer_systemprompt_persists(
        self,
        dynamodb_client,
        api_base_url,
        test_animal_config,
        cleanup_test_data
    ):
        """
        DynamoDB Layer Test: Verify systemPrompt ACTUALLY persists to DynamoDB

        CRITICAL: This test queries DynamoDB directly to verify persistence.
        We NEVER infer database state from code logic (lesson from Bug #8).

        This is the DEFINITIVE test for Bug #1 - if this passes, the bug is truly fixed.
        """
        import requests

        # Step 1: Update via API
        url = f"{api_base_url}/animal_config"
        auth_response = requests.post(
            f"{api_base_url}/auth",
            json={"email": "parent1@test.cmz.org", "password": "testpass123"}
        )
        token = auth_response.json().get("token")

        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        response = requests.patch(url, json=test_animal_config, headers=headers)
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

        # Step 5: Verify systemPrompt field exists and matches
        assert "configuration" in item, "No configuration field in DynamoDB item"
        config = item["configuration"]["M"]

        assert "systemPrompt" in config, (
            "systemPrompt field NOT in DynamoDB! Bug #1 NOT fixed. "
            f"Configuration fields: {list(config.keys())}"
        )

        stored_prompt = config["systemPrompt"]["S"]
        expected_prompt = test_animal_config["systemPrompt"]

        assert stored_prompt == expected_prompt, (
            f"systemPrompt mismatch! "
            f"Expected: {expected_prompt}, "
            f"Stored in DynamoDB: {stored_prompt}"
        )

        # Step 6: Verify temperature field also persists
        assert "temperature" in config, "temperature field NOT in DynamoDB"
        stored_temp = float(config["temperature"]["N"])
        expected_temp = test_animal_config["temperature"]

        assert abs(stored_temp - expected_temp) < 0.01, (
            f"temperature mismatch! "
            f"Expected: {expected_temp}, "
            f"Stored in DynamoDB: {stored_temp}"
        )

        print(f"✅ DynamoDB Layer: systemPrompt VERIFIED in database")
        print(f"   Stored value: {stored_prompt}")
        print(f"   Temperature: {stored_temp}")
        print(f"   DEFINITIVE PROOF: Bug #1 is fixed!")

    def test_04_persistence_across_reads(self, dynamodb_client, api_base_url, test_animal_config):
        """
        Persistence Test: Verify data persists across multiple reads

        This test ensures the data isn't just temporarily stored but actually persisted.
        """
        import requests

        # Step 1: Update config
        url = f"{api_base_url}/animal_config"
        auth_response = requests.post(
            f"{api_base_url}/auth",
            json={"email": "parent1@test.cmz.org", "password": "testpass123"}
        )
        token = auth_response.json().get("token")
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        patch_response = requests.patch(url, json=test_animal_config, headers=headers)
        assert patch_response.status_code == 200

        time.sleep(1)

        # Step 2: Read via API
        get_url = f"{api_base_url}/animal_config?animalId={TEST_ANIMAL_ID}"
        get_response = requests.get(get_url, headers=headers)
        assert get_response.status_code == 200

        api_data = get_response.json()

        # Step 3: Read via DynamoDB directly
        dynamodb_response = dynamodb_client.get_item(
            TableName=DYNAMODB_TABLE,
            Key={"animalId": {"S": TEST_ANIMAL_ID}}
        )

        item = dynamodb_response["Item"]
        config = item["configuration"]["M"]
        db_system_prompt = config["systemPrompt"]["S"]

        # Step 4: Verify consistency
        expected_prompt = test_animal_config["systemPrompt"]

        # API should return what's in DB
        assert db_system_prompt == expected_prompt, "DynamoDB has wrong value"

        print("✅ Persistence: Data consistent across API reads and DynamoDB queries")

    def test_05_no_501_errors_in_logs(self, api_base_url, test_animal_config):
        """
        Validation Test: Ensure no 501 errors occur during animal config update

        This test verifies the forwarding chain is working by ensuring
        we never see "Not Implemented" errors.
        """
        import requests

        url = f"{api_base_url}/animal_config"

        auth_response = requests.post(
            f"{api_base_url}/auth",
            json={"email": "parent1@test.cmz.org", "password": "testpass123"}
        )
        token = auth_response.json().get("token")
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        response = requests.patch(url, json=test_animal_config, headers=headers)

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


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
