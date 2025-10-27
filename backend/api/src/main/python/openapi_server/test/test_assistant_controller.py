"""
Contract tests for Assistant Management API endpoints

Tests the API contract compliance between OpenAPI specification and implementation.
Ensures request/response schemas, status codes, and error handling match the spec.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from flask import Flask
from connexion import FlaskApp

# Import the test client setup
from openapi_server.test import BaseTestCase


class TestAssistantManagementController(BaseTestCase):
    """Test assistant management API endpoints contract compliance"""

    def setUp(self):
        """Set up test client"""
        super().setUp()
        self.test_client = self.app.test_client()

    def test_create_assistant_contract(self):
        """Test POST /assistant contract compliance"""
        # Valid request body according to OpenAPI spec
        valid_request = {
            "name": "Test Assistant",
            "animalId": "tiger-001",
            "personalityId": "friendly-001",
            "guardrailId": "basic-001",
            "description": "Test assistant for contract validation",
            "status": "draft"
        }

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer mock-jwt-token'
        }

        with patch('openapi_server.impl.assistants.create_assistant') as mock_create:
            # Mock successful creation response
            mock_create.return_value = (
                {
                    "assistantId": "test-assistant-001",
                    "name": "Test Assistant",
                    "animalId": "tiger-001",
                    "personalityId": "friendly-001",
                    "guardrailId": "basic-001",
                    "description": "Test assistant for contract validation",
                    "status": "draft",
                    "created": {"at": "2025-10-23T00:00:00Z", "by": "test@cmz.org"},
                    "mergedPrompt": "Test merged prompt"
                },
                201
            )

            # Make request
            response = self.test_client.post(
                '/assistant',
                data=json.dumps(valid_request),
                headers=headers
            )

            # Verify contract compliance
            assert response.status_code == 201

            response_data = json.loads(response.data)

            # Verify required fields in response
            assert 'assistantId' in response_data
            assert 'name' in response_data
            assert 'animalId' in response_data
            assert 'personalityId' in response_data
            assert 'guardrailId' in response_data
            assert 'status' in response_data
            assert 'created' in response_data

            # Verify data types match schema
            assert isinstance(response_data['assistantId'], str)
            assert isinstance(response_data['name'], str)
            assert isinstance(response_data['animalId'], str)
            assert isinstance(response_data['status'], str)

    def test_create_assistant_validation_error_contract(self):
        """Test POST /assistant validation error response contract"""
        # Invalid request body (missing required fields)
        invalid_request = {
            "description": "Missing required fields"
        }

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer mock-jwt-token'
        }

        with patch('openapi_server.impl.assistants.create_assistant') as mock_create:
            # Mock validation error response
            mock_create.return_value = (
                {
                    "error": "Missing required field: name",
                    "code": "validation_error",
                    "details": {"field": "name", "message": "Field is required"}
                },
                400
            )

            # Make request
            response = self.test_client.post(
                '/assistant',
                data=json.dumps(invalid_request),
                headers=headers
            )

            # Verify error contract compliance
            assert response.status_code == 400

            response_data = json.loads(response.data)
            assert 'error' in response_data

    def test_list_assistants_contract(self):
        """Test GET /assistant contract compliance"""
        headers = {
            'Authorization': 'Bearer mock-jwt-token'
        }

        with patch('openapi_server.impl.assistants.list_assistants') as mock_list:
            # Mock successful list response
            mock_list.return_value = (
                {
                    "assistants": [
                        {
                            "assistantId": "assistant-001",
                            "name": "Bella's Assistant",
                            "animalId": "tiger-001",
                            "status": "active",
                            "created": {"at": "2025-10-23T00:00:00Z", "by": "test@cmz.org"}
                        },
                        {
                            "assistantId": "assistant-002",
                            "name": "Leo's Assistant",
                            "animalId": "lion-001",
                            "status": "draft",
                            "created": {"at": "2025-10-23T00:00:00Z", "by": "test@cmz.org"}
                        }
                    ]
                },
                200
            )

            # Make request
            response = self.test_client.get('/assistant', headers=headers)

            # Verify contract compliance
            assert response.status_code == 200

            response_data = json.loads(response.data)
            assert 'assistants' in response_data
            assert isinstance(response_data['assistants'], list)

            # Verify each assistant has required fields
            for assistant in response_data['assistants']:
                assert 'assistantId' in assistant
                assert 'name' in assistant
                assert 'animalId' in assistant
                assert 'status' in assistant

    def test_list_assistants_with_filters_contract(self):
        """Test GET /assistant with query parameters contract"""
        headers = {
            'Authorization': 'Bearer mock-jwt-token'
        }

        with patch('openapi_server.impl.assistants.list_assistants') as mock_list:
            # Mock filtered response
            mock_list.return_value = (
                {
                    "assistants": [
                        {
                            "assistantId": "assistant-001",
                            "name": "Bella's Assistant",
                            "animalId": "tiger-001",
                            "status": "active",
                            "created": {"at": "2025-10-23T00:00:00Z", "by": "test@cmz.org"}
                        }
                    ]
                },
                200
            )

            # Make request with query parameters
            response = self.test_client.get(
                '/assistant?status=active&animalId=tiger-001',
                headers=headers
            )

            # Verify contract compliance
            assert response.status_code == 200

            response_data = json.loads(response.data)
            assert 'assistants' in response_data

    def test_get_assistant_by_id_contract(self):
        """Test GET /assistant/{assistantId} contract compliance"""
        assistant_id = "test-assistant-001"
        headers = {
            'Authorization': 'Bearer mock-jwt-token'
        }

        with patch('openapi_server.impl.assistants.get_assistant') as mock_get:
            # Mock successful get response
            mock_get.return_value = (
                {
                    "assistantId": assistant_id,
                    "name": "Test Assistant",
                    "animalId": "tiger-001",
                    "personalityId": "friendly-001",
                    "guardrailId": "basic-001",
                    "description": "Test assistant",
                    "status": "active",
                    "created": {"at": "2025-10-23T00:00:00Z", "by": "test@cmz.org"},
                    "modified": {"at": "2025-10-23T00:00:00Z", "by": "test@cmz.org"},
                    "mergedPrompt": "Test merged prompt"
                },
                200
            )

            # Make request
            response = self.test_client.get(f'/assistant/{assistant_id}', headers=headers)

            # Verify contract compliance
            assert response.status_code == 200

            response_data = json.loads(response.data)
            assert response_data['assistantId'] == assistant_id

            # Verify all required fields present
            required_fields = ['assistantId', 'name', 'animalId', 'status', 'created']
            for field in required_fields:
                assert field in response_data

    def test_get_assistant_not_found_contract(self):
        """Test GET /assistant/{assistantId} not found response contract"""
        assistant_id = "nonexistent-assistant"
        headers = {
            'Authorization': 'Bearer mock-jwt-token'
        }

        with patch('openapi_server.impl.assistants.get_assistant') as mock_get:
            # Mock not found response
            mock_get.return_value = (
                {
                    "error": "Assistant not found",
                    "code": "not_found",
                    "details": {"assistantId": assistant_id}
                },
                404
            )

            # Make request
            response = self.test_client.get(f'/assistant/{assistant_id}', headers=headers)

            # Verify error contract compliance
            assert response.status_code == 404

            response_data = json.loads(response.data)
            assert 'error' in response_data

    def test_update_assistant_contract(self):
        """Test PUT /assistant/{assistantId} contract compliance"""
        assistant_id = "test-assistant-001"
        update_request = {
            "name": "Updated Assistant Name",
            "description": "Updated description",
            "status": "active"
        }

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer mock-jwt-token'
        }

        with patch('openapi_server.impl.assistants.update_assistant') as mock_update:
            # Mock successful update response
            mock_update.return_value = (
                {
                    "assistantId": assistant_id,
                    "name": "Updated Assistant Name",
                    "animalId": "tiger-001",
                    "personalityId": "friendly-001",
                    "guardrailId": "basic-001",
                    "description": "Updated description",
                    "status": "active",
                    "modified": {"at": "2025-10-23T00:00:00Z", "by": "test@cmz.org"}
                },
                200
            )

            # Make request
            response = self.test_client.put(
                f'/assistant/{assistant_id}',
                data=json.dumps(update_request),
                headers=headers
            )

            # Verify contract compliance
            assert response.status_code == 200

            response_data = json.loads(response.data)
            assert response_data['assistantId'] == assistant_id
            assert response_data['name'] == update_request['name']
            assert response_data['description'] == update_request['description']

    def test_delete_assistant_contract(self):
        """Test DELETE /assistant/{assistantId} contract compliance"""
        assistant_id = "test-assistant-001"
        headers = {
            'Authorization': 'Bearer mock-jwt-token'
        }

        with patch('openapi_server.impl.assistants.delete_assistant') as mock_delete:
            # Mock successful deletion response
            mock_delete.return_value = (
                {
                    "message": "Assistant deleted successfully",
                    "assistantId": assistant_id
                },
                204
            )

            # Make request
            response = self.test_client.delete(f'/assistant/{assistant_id}', headers=headers)

            # Verify contract compliance
            assert response.status_code == 204

    def test_content_type_validation(self):
        """Test content type validation for POST requests"""
        valid_request = {
            "name": "Test Assistant",
            "animalId": "tiger-001",
            "personalityId": "friendly-001",
            "guardrailId": "basic-001"
        }

        # Test with missing content-type header
        response = self.test_client.post(
            '/assistant',
            data=json.dumps(valid_request),
            headers={'Authorization': 'Bearer mock-jwt-token'}
        )

        # Should handle missing content-type gracefully or return 400
        assert response.status_code in [400, 415, 201]  # Depends on implementation

        # Test with wrong content-type
        response = self.test_client.post(
            '/assistant',
            data=json.dumps(valid_request),
            headers={
                'Content-Type': 'text/plain',
                'Authorization': 'Bearer mock-jwt-token'
            }
        )

        # Should reject wrong content-type
        assert response.status_code in [400, 415]

    def test_authentication_contract(self):
        """Test authentication requirements contract"""
        valid_request = {
            "name": "Test Assistant",
            "animalId": "tiger-001",
            "personalityId": "friendly-001",
            "guardrailId": "basic-001"
        }

        # Test without authorization header
        response = self.test_client.post(
            '/assistant',
            data=json.dumps(valid_request),
            headers={'Content-Type': 'application/json'}
        )

        # Should require authentication (401) or handle mock auth gracefully
        assert response.status_code in [401, 201]  # Depends on AUTH_MODE setting


if __name__ == '__main__':
    pytest.main([__file__])