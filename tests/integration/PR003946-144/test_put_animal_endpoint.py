"""
Test suite for PR003946-144: PUT /animal/{id} endpoint implementation

This test follows TDD principles - written before implementation to fail first,
then implementation will be created to make these tests pass.
"""

import pytest
import requests
import json
from datetime import datetime
from typing import Dict, Any


class TestPutAnimalEndpoint:
    """Test cases for PUT /animal/{id} endpoint"""

    BASE_URL = "http://localhost:8080"

    @pytest.fixture
    def auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for requests"""
        # TODO: Implement proper auth token generation
        return {
            "Content-Type": "application/json",
            "Authorization": "Bearer test-token"
        }

    @pytest.fixture
    def test_animal(self) -> Dict[str, Any]:
        """Create a test animal for update operations"""
        return {
            "id": "test-lion-001",
            "name": "Leo",
            "species": "Lion",
            "status": "active",
            "version": 1,
            "created": {"at": datetime.utcnow().isoformat() + "Z"},
            "modified": {"at": datetime.utcnow().isoformat() + "Z"}
        }

    def test_full_update_success(self, auth_headers, test_animal):
        """Test successful full update of an animal"""
        # Arrange
        animal_id = test_animal["id"]
        updated_animal = {
            **test_animal,
            "name": "Leo the Lion King",
            "description": "The mighty king of the savanna",
            "age": 5
        }

        # Act
        response = requests.put(
            f"{self.BASE_URL}/animal/{animal_id}",
            headers=auth_headers,
            json=updated_animal
        )

        # Assert
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

        result = response.json()
        assert result["name"] == "Leo the Lion King"
        assert result["description"] == "The mighty king of the savanna"
        assert result["age"] == 5
        assert result["version"] == 2  # Version should increment
        assert "modified" in result
        assert result["modified"]["at"] > test_animal["modified"]["at"]

    def test_partial_update_success(self, auth_headers, test_animal):
        """Test successful partial update (only changed fields)"""
        # Arrange
        animal_id = test_animal["id"]
        partial_update = {
            "id": animal_id,
            "name": "Leo the Brave",
            "version": 1
        }

        # Act
        response = requests.put(
            f"{self.BASE_URL}/animal/{animal_id}",
            headers=auth_headers,
            json=partial_update
        )

        # Assert
        assert response.status_code == 200

        result = response.json()
        assert result["name"] == "Leo the Brave"
        assert result["species"] == test_animal["species"]  # Unchanged
        assert result["status"] == test_animal["status"]  # Unchanged
        assert result["version"] == 2

    def test_id_mismatch_error(self, auth_headers, test_animal):
        """Test error when URL ID doesn't match body ID"""
        # Arrange
        url_id = "test-lion-001"
        mismatched_animal = {
            **test_animal,
            "id": "different-id"
        }

        # Act
        response = requests.put(
            f"{self.BASE_URL}/animal/{url_id}",
            headers=auth_headers,
            json=mismatched_animal
        )

        # Assert
        assert response.status_code == 400

        error = response.json()
        assert error["code"] == "id_mismatch"
        assert "does not match" in error["message"].lower()

    def test_not_found_error(self, auth_headers):
        """Test 404 error for non-existent animal"""
        # Arrange
        non_existent_id = "non-existent-animal"
        update_data = {
            "id": non_existent_id,
            "name": "Ghost Animal",
            "species": "Unknown",
            "status": "active",
            "version": 1
        }

        # Act
        response = requests.put(
            f"{self.BASE_URL}/animal/{non_existent_id}",
            headers=auth_headers,
            json=update_data
        )

        # Assert
        assert response.status_code == 404

        error = response.json()
        assert error["code"] == "not_found"
        assert "not found" in error["message"].lower()
        assert error["details"]["id"] == non_existent_id

    def test_validation_errors(self, auth_headers, test_animal):
        """Test validation errors for invalid data"""
        # Arrange
        animal_id = test_animal["id"]
        invalid_data = {
            "id": animal_id,
            "name": "L",  # Too short
            "species": "InvalidSpecies",  # Not in approved list
            "status": "invalid_status",  # Invalid enum value
            "version": 1
        }

        # Act
        response = requests.put(
            f"{self.BASE_URL}/animal/{animal_id}",
            headers=auth_headers,
            json=invalid_data
        )

        # Assert
        assert response.status_code == 400

        error = response.json()
        assert error["code"] == "validation_error"
        assert "validation" in error["message"].lower()

        # Check specific field errors
        details = error["details"]
        assert "name" in details
        assert "too short" in details["name"].lower()
        assert "species" in details
        assert "invalid" in details["species"].lower()
        assert "status" in details

    def test_version_conflict(self, auth_headers, test_animal):
        """Test 409 conflict when version doesn't match"""
        # Arrange
        animal_id = test_animal["id"]
        outdated_update = {
            **test_animal,
            "name": "Leo Updated",
            "version": 0  # Old version
        }

        # Act
        response = requests.put(
            f"{self.BASE_URL}/animal/{animal_id}",
            headers=auth_headers,
            json=outdated_update
        )

        # Assert
        assert response.status_code == 409

        error = response.json()
        assert error["code"] == "version_conflict"
        assert "conflict" in error["message"].lower()
        assert error["details"]["provided_version"] == 0
        assert "current_version" in error["details"]

    def test_unauthorized_access(self, test_animal):
        """Test 401 error without authentication"""
        # Arrange
        animal_id = test_animal["id"]
        update_data = {
            **test_animal,
            "name": "Unauthorized Update"
        }

        # Act
        response = requests.put(
            f"{self.BASE_URL}/animal/{animal_id}",
            headers={"Content-Type": "application/json"},  # No auth header
            json=update_data
        )

        # Assert
        assert response.status_code == 401

        error = response.json()
        assert error["code"] == "unauthorized"
        assert "authentication" in error["message"].lower()

    def test_audit_trail_creation(self, auth_headers, test_animal):
        """Test that audit trail is properly created"""
        # Arrange
        animal_id = test_animal["id"]
        update_data = {
            **test_animal,
            "name": "Leo with Audit",
            "status": "inactive"
        }

        # Act
        response = requests.put(
            f"{self.BASE_URL}/animal/{animal_id}",
            headers=auth_headers,
            json=update_data
        )

        # Assert
        assert response.status_code == 200

        result = response.json()
        assert "modified" in result
        assert "at" in result["modified"]
        assert "by" in result["modified"]

        # Check if changes are tracked (if included in response)
        if "changes" in result:
            changes = result["changes"]
            assert "name" in changes
            assert changes["name"]["old"] == test_animal["name"]
            assert changes["name"]["new"] == "Leo with Audit"
            assert "status" in changes
            assert changes["status"]["old"] == "active"
            assert changes["status"]["new"] == "inactive"

    def test_required_fields_missing(self, auth_headers):
        """Test error when required fields are missing"""
        # Arrange
        animal_id = "test-lion-001"
        incomplete_data = {
            "id": animal_id,
            "name": "Leo"
            # Missing species and status
        }

        # Act
        response = requests.put(
            f"{self.BASE_URL}/animal/{animal_id}",
            headers=auth_headers,
            json=incomplete_data
        )

        # Assert
        assert response.status_code == 400

        error = response.json()
        assert error["code"] == "validation_error"
        details = error["details"]
        assert "species" in details or "required" in error["message"].lower()
        assert "status" in details or "required" in error["message"].lower()

    def test_successful_update_persists_to_database(self, auth_headers, test_animal):
        """Test that successful update persists to database"""
        # Arrange
        animal_id = test_animal["id"]
        update_data = {
            **test_animal,
            "name": "Leo Persisted"
        }

        # Act - Update
        update_response = requests.put(
            f"{self.BASE_URL}/animal/{animal_id}",
            headers=auth_headers,
            json=update_data
        )

        assert update_response.status_code == 200

        # Act - Retrieve
        get_response = requests.get(
            f"{self.BASE_URL}/animal/{animal_id}",
            headers=auth_headers
        )

        # Assert
        assert get_response.status_code == 200
        retrieved = get_response.json()
        assert retrieved["name"] == "Leo Persisted"
        assert retrieved["version"] == 2


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])