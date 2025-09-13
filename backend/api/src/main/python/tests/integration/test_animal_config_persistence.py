"""
Integration tests for animal configuration endpoint and DynamoDB persistence.

This test suite validates that HTTP responses match actual DynamoDB persistence state,
addressing the issue where the frontend shows configuration changes disappearing.
"""

import pytest
import requests
import json
import boto3
import os
from datetime import datetime
from typing import Dict, Any, Optional


class TestAnimalConfigPersistence:
    """Integration tests for animal configuration persistence"""
    
    @classmethod
    def setup_class(cls):
        """Set up test environment"""
        cls.api_base_url = "http://localhost:8080"
        cls.test_animal_id = "test_cheetah_001"
        
        # DynamoDB configuration
        cls.animal_table_name = os.getenv("ANIMAL_DYNAMO_TABLE_NAME", "quest-dev-animal")
        cls.animal_pk_name = os.getenv("ANIMAL_DYNAMO_PK_NAME", "animalId")
        
        # Initialize DynamoDB client
        region = os.getenv("AWS_DEFAULT_REGION", "us-west-2")
        if os.getenv("DYNAMODB_ENDPOINT_URL"):
            cls.dynamodb = boto3.client('dynamodb', endpoint_url=os.getenv("DYNAMODB_ENDPOINT_URL"))
            cls.dynamodb_resource = boto3.resource('dynamodb', endpoint_url=os.getenv("DYNAMODB_ENDPOINT_URL"))
        else:
            cls.dynamodb = boto3.client('dynamodb', region_name=region)
            cls.dynamodb_resource = boto3.resource('dynamodb', region_name=region)
        
        cls.animal_table = cls.dynamodb_resource.Table(cls.animal_table_name)
    
    def setup_method(self):
        """Set up each test method"""
        # Clean up any existing test data
        self.cleanup_test_animal()
        
        # Create a test animal for configuration testing
        self.create_test_animal()
    
    def teardown_method(self):
        """Clean up after each test method"""
        self.cleanup_test_animal()
    
    def create_test_animal(self):
        """Create a test animal in DynamoDB for configuration testing"""
        test_animal_data = {
            'animalId': self.test_animal_id,
            'name': 'Test Cheetah',
            'species': 'Acinonyx jubatus',
            'personality': {
                'description': 'Energetic and educational, loves talking about speed and hunting techniques'
            },
            'active': True,
            'educational_focus': True,
            'age_appropriate': True,
            'created': {'at': datetime.utcnow().isoformat() + 'Z'},
            'modified': {'at': datetime.utcnow().isoformat() + 'Z'},
            'softDelete': False
        }
        
        try:
            # Use DynamoDB put_item to create the test animal
            self.animal_table.put_item(Item=test_animal_data)
            print(f"Created test animal: {self.test_animal_id}")
        except Exception as e:
            print(f"Error creating test animal: {e}")
            raise
    
    def cleanup_test_animal(self):
        """Remove test animal from DynamoDB"""
        try:
            self.animal_table.delete_item(
                Key={self.animal_pk_name: self.test_animal_id}
            )
            print(f"Cleaned up test animal: {self.test_animal_id}")
        except Exception as e:
            # Ignore errors if item doesn't exist
            print(f"Cleanup note: {e}")
    
    def get_animal_from_dynamodb(self) -> Optional[Dict[str, Any]]:
        """Retrieve animal directly from DynamoDB to verify persistence"""
        try:
            response = self.animal_table.get_item(
                Key={self.animal_pk_name: self.test_animal_id}
            )
            return response.get('Item')
        except Exception as e:
            print(f"Error retrieving animal from DynamoDB: {e}")
            return None
    
    def test_animal_config_get_endpoint(self):
        """Test GET /animal_config endpoint returns proper response"""
        # Test the GET endpoint
        response = requests.get(
            f"{self.api_base_url}/animal_config",
            params={"animalId": self.test_animal_id}
        )
        
        print(f"GET /animal_config response: {response.status_code}")
        print(f"Response body: {response.text}")
        
        # Verify response format
        assert response.status_code in [200, 404, 501], f"Unexpected status code: {response.status_code}"
        
        if response.status_code == 200:
            config_data = response.json()
            assert isinstance(config_data, dict), "Response should be a JSON object"
            print(f"Configuration data: {json.dumps(config_data, indent=2)}")
    
    def test_animal_config_patch_http_response(self):
        """Test PATCH /animal_config endpoint HTTP response"""
        # Prepare configuration update
        config_update = {
            "personality": "Updated: Energetic and educational, loves discussing speed and hunting techniques",
            "active": True,
            "educational_focus": True,
            "age_appropriate": True
        }
        
        # Test the PATCH endpoint
        response = requests.patch(
            f"{self.api_base_url}/animal_config",
            params={"animalId": self.test_animal_id},
            json=config_update,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"PATCH /animal_config HTTP status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        print(f"Response body: {response.text}")
        
        # Document the response for analysis
        assert response.status_code in [200, 201, 204, 400, 404, 501], f"Unexpected status code: {response.status_code}"
        
        # If successful, verify response format
        if response.status_code in [200, 201]:
            if response.text.strip():  # Only parse if there's content
                response_data = response.json()
                assert isinstance(response_data, dict), "Success response should be a JSON object"
                print(f"Update response data: {json.dumps(response_data, indent=2)}")
        
        return response.status_code, response.text
    
    def test_animal_config_patch_dynamodb_persistence(self):
        """Test that PATCH /animal_config actually persists changes to DynamoDB"""
        # Get initial state from DynamoDB
        initial_animal = self.get_animal_from_dynamodb()
        assert initial_animal is not None, "Test animal should exist in DynamoDB"
        initial_personality = initial_animal.get('personality', '')
        print(f"Initial personality: {initial_personality}")
        
        # Prepare configuration update with unique content
        timestamp = datetime.utcnow().isoformat()
        config_update = {
            "personality": f"UPDATED {timestamp}: Speed demon cheetah with educational focus",
            "active": True,
            "educational_focus": True,
            "age_appropriate": True
        }
        
        # Send PATCH request
        response = requests.patch(
            f"{self.api_base_url}/animal_config",
            params={"animalId": self.test_animal_id},
            json=config_update,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"PATCH response status: {response.status_code}")
        print(f"PATCH response body: {response.text}")
        
        # Get updated state from DynamoDB
        updated_animal = self.get_animal_from_dynamodb()
        assert updated_animal is not None, "Animal should still exist in DynamoDB after update"
        
        updated_personality = updated_animal.get('personality', '')
        print(f"Updated personality: {updated_personality}")
        
        # Verify persistence
        if response.status_code in [200, 201, 204]:
            # If API indicates success, DynamoDB should reflect the change
            assert updated_personality != initial_personality, \
                "Personality should have changed in DynamoDB when API indicates success"
            assert timestamp in updated_personality, \
                f"Updated personality should contain timestamp {timestamp}"
            print("✅ SUCCESS: HTTP response matches DynamoDB persistence")
        else:
            # If API indicates failure, DynamoDB should be unchanged
            assert updated_personality == initial_personality, \
                f"Personality should be unchanged in DynamoDB when API fails. Expected: {initial_personality}, Got: {updated_personality}"
            print(f"✅ CONSISTENT: HTTP error ({response.status_code}) matches unchanged DynamoDB state")
    
    def test_animal_config_patch_response_consistency(self):
        """Test that HTTP response content matches DynamoDB state"""
        # Prepare configuration update
        config_update = {
            "personality": "Response consistency test: Cheetah loves speed facts",
            "active": True,
            "educational_focus": False,  # Change this to test updates
            "age_appropriate": True
        }
        
        # Send PATCH request
        response = requests.patch(
            f"{self.api_base_url}/animal_config",
            params={"animalId": self.test_animal_id},
            json=config_update,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Response status: {response.status_code}")
        
        # Get actual DynamoDB state
        actual_animal = self.get_animal_from_dynamodb()
        assert actual_animal is not None, "Animal should exist in DynamoDB"
        
        if response.status_code in [200, 201]:
            # Parse response if successful
            if response.text.strip():
                response_data = response.json()
                
                # Compare critical fields between response and DynamoDB
                response_personality = response_data.get('personality', '')
                actual_personality = actual_animal.get('personality', '')
                
                response_educational = response_data.get('educational_focus', None)
                actual_educational = actual_animal.get('educational_focus', None)
                
                print(f"Response personality: {response_personality}")
                print(f"DynamoDB personality: {actual_personality}")
                print(f"Response educational_focus: {response_educational}")
                print(f"DynamoDB educational_focus: {actual_educational}")
                
                # Verify consistency
                assert response_personality == actual_personality, \
                    "Response personality should match DynamoDB personality"
                assert response_educational == actual_educational, \
                    "Response educational_focus should match DynamoDB educational_focus"
                
                print("✅ CONSISTENT: HTTP response data matches DynamoDB state")
    
    def test_multiple_config_updates_persistence(self):
        """Test multiple sequential configuration updates"""
        updates = [
            {"personality": "Update 1: Fast cheetah", "active": True},
            {"personality": "Update 2: Educational cheetah", "active": True},
            {"personality": "Update 3: Speed teaching cheetah", "active": False}
        ]
        
        for i, update in enumerate(updates, 1):
            print(f"\n--- Update {i} ---")
            
            # Send update
            response = requests.patch(
                f"{self.api_base_url}/animal_config",
                params={"animalId": self.test_animal_id},
                json=update,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Update {i} response: {response.status_code}")
            
            # Verify DynamoDB state
            current_animal = self.get_animal_from_dynamodb()
            assert current_animal is not None, f"Animal should exist after update {i}"
            
            current_personality = current_animal.get('personality', '')
            current_active = current_animal.get('active', None)
            
            print(f"DynamoDB personality: {current_personality}")
            print(f"DynamoDB active: {current_active}")
            
            if response.status_code in [200, 201, 204]:
                # Verify the update was persisted
                assert f"Update {i}" in current_personality, \
                    f"Update {i} personality should be reflected in DynamoDB"
                assert current_active == update["active"], \
                    f"Update {i} active status should be reflected in DynamoDB"
    
    def test_invalid_animal_id_handling(self):
        """Test behavior with non-existent animal ID"""
        invalid_id = "nonexistent_animal_123"
        
        # Test GET with invalid ID
        get_response = requests.get(
            f"{self.api_base_url}/animal_config",
            params={"animalId": invalid_id}
        )
        
        print(f"GET invalid ID response: {get_response.status_code}")
        print(f"GET invalid ID body: {get_response.text}")
        
        # Test PATCH with invalid ID
        patch_response = requests.patch(
            f"{self.api_base_url}/animal_config",
            params={"animalId": invalid_id},
            json={"personality": "Should not work"},
            headers={"Content-Type": "application/json"}
        )
        
        print(f"PATCH invalid ID response: {patch_response.status_code}")
        print(f"PATCH invalid ID body: {patch_response.text}")
        
        # Both should return 404 or appropriate error
        assert get_response.status_code in [404, 400, 501], "GET with invalid ID should return error"
        assert patch_response.status_code in [404, 400, 501], "PATCH with invalid ID should return error"


if __name__ == "__main__":
    # Run tests manually for debugging
    import sys
    
    test_instance = TestAnimalConfigPersistence()
    test_instance.setup_class()
    
    try:
        print("=== Setting up test ===")
        test_instance.setup_method()
        
        print("\n=== Testing GET endpoint ===")
        test_instance.test_animal_config_get_endpoint()
        
        print("\n=== Testing PATCH HTTP response ===")
        test_instance.test_animal_config_patch_http_response()
        
        print("\n=== Testing PATCH DynamoDB persistence ===")
        test_instance.test_animal_config_patch_dynamodb_persistence()
        
        print("\n=== Testing response consistency ===")
        test_instance.test_animal_config_patch_response_consistency()
        
        print("\n=== Testing multiple updates ===")
        test_instance.test_multiple_config_updates_persistence()
        
        print("\n=== Testing invalid ID handling ===")
        test_instance.test_invalid_animal_id_handling()
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n=== Cleaning up ===")
        test_instance.teardown_method()