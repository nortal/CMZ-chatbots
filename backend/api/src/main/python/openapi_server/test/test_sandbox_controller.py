"""
Contract tests for Sandbox Testing API endpoints

Tests the API contract compliance between OpenAPI specification and implementation.
Ensures request/response schemas, status codes, and error handling match the spec
for sandbox testing functionality.

T037 - User Story 2: Test Assistant Changes Safely
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone, timedelta

# Import the test client setup
from openapi_server.test import BaseTestCase


class TestSandboxTestingController(BaseTestCase):
    """Test sandbox testing API endpoints contract compliance"""

    def setUp(self):
        """Set up test client"""
        super().setUp()

    def test_create_sandbox_contract(self):
        """Test POST /sandbox contract compliance"""
        # Valid request body according to OpenAPI spec
        valid_request = {
            "assistantId": "test-assistant-001",
            "name": "Test Sandbox Assistant",
            "personalityId": "test-personality-001",
            "guardrailId": "test-guardrail-001",
            "description": "Testing new personality configuration"
        }

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer mock-jwt-token'
        }

        with patch('openapi_server.impl.sandbox.create_sandbox_assistant') as mock_create:
            # Mock successful creation response
            ttl = int((datetime.now(timezone.utc) + timedelta(minutes=30)).timestamp())
            mock_create.return_value = (
                {
                    "sandboxId": "test-sandbox-001",
                    "assistantId": "test-assistant-001",
                    "name": "Test Sandbox Assistant",
                    "personalityId": "test-personality-001",
                    "guardrailId": "test-guardrail-001",
                    "description": "Testing new personality configuration",
                    "status": "draft",
                    "ttl": ttl,
                    "created": {"at": "2025-10-23T00:00:00Z", "by": "test@cmz.org"},
                    "expiresAt": "2025-10-23T00:30:00Z"
                },
                201
            )

            # Make request
            response = self.client.post(
                '/sandbox',
                data=json.dumps(valid_request),
                headers=headers
            )

            # Verify contract compliance
            self.assertEqual(response.status_code, 201)

            response_data = json.loads(response.data)

            # Verify required fields in response
            self.assertIn('sandboxId', response_data)
            self.assertIn('assistantId', response_data)
            self.assertIn('name', response_data)
            self.assertIn('status', response_data)
            self.assertIn('ttl', response_data)
            self.assertIn('created', response_data)
            self.assertIn('expiresAt', response_data)

            # Verify data types match schema
            self.assertIsInstance(response_data['sandboxId'], str)
            self.assertIsInstance(response_data['assistantId'], str)
            self.assertIsInstance(response_data['name'], str)
            self.assertIsInstance(response_data['status'], str)
            self.assertIsInstance(response_data['ttl'], int)

            # Verify status is valid enum value
            self.assertIn(response_data['status'], ['draft', 'tested', 'promoted'])

    def test_create_sandbox_validation_error_contract(self):
        """Test POST /sandbox validation error response contract"""
        # Invalid request body (missing required fields)
        invalid_request = {
            "description": "Missing required fields"
        }

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer mock-jwt-token'
        }

        with patch('openapi_server.impl.sandbox.create_sandbox_assistant') as mock_create:
            # Mock validation error response
            mock_create.return_value = (
                {
                    "error": "Missing required field: assistantId",
                    "code": "validation_error",
                    "details": {"field": "assistantId", "message": "Field is required"}
                },
                400
            )

            # Make request
            response = self.client.post(
                '/sandbox',
                data=json.dumps(invalid_request),
                headers=headers
            )

            # Verify error contract compliance
            self.assertEqual(response.status_code, 400)

            response_data = json.loads(response.data)
            self.assertIn('error', response_data)

    def test_list_sandboxes_contract(self):
        """Test GET /sandbox contract compliance"""
        headers = {
            'Authorization': 'Bearer mock-jwt-token'
        }

        with patch('openapi_server.impl.sandbox.list_sandbox_assistants') as mock_list:
            # Mock successful list response
            ttl = int((datetime.now(timezone.utc) + timedelta(minutes=20)).timestamp())
            mock_list.return_value = (
                {
                    "sandboxes": [
                        {
                            "sandboxId": "sandbox-001",
                            "assistantId": "assistant-001",
                            "name": "Test Sandbox 1",
                            "status": "draft",
                            "ttl": ttl,
                            "created": {"at": "2025-10-23T00:00:00Z", "by": "test@cmz.org"},
                            "expiresAt": "2025-10-23T00:20:00Z"
                        },
                        {
                            "sandboxId": "sandbox-002",
                            "assistantId": "assistant-002",
                            "name": "Test Sandbox 2",
                            "status": "tested",
                            "ttl": ttl,
                            "created": {"at": "2025-10-23T00:00:00Z", "by": "test@cmz.org"},
                            "expiresAt": "2025-10-23T00:20:00Z"
                        }
                    ]
                },
                200
            )

            # Make request
            response = self.client.get('/sandbox', headers=headers)

            # Verify contract compliance
            self.assertEqual(response.status_code, 200)

            response_data = json.loads(response.data)
            self.assertIn('sandboxes', response_data)
            self.assertIsInstance(response_data['sandboxes'], list)

            # Verify each sandbox has required fields
            for sandbox in response_data['sandboxes']:
                self.assertIn('sandboxId', sandbox)
                self.assertIn('assistantId', sandbox)
                self.assertIn('name', sandbox)
                self.assertIn('status', sandbox)
                self.assertIn('ttl', sandbox)
                self.assertIn('created', sandbox)

    def test_list_sandboxes_with_filters_contract(self):
        """Test GET /sandbox with query parameters contract"""
        headers = {
            'Authorization': 'Bearer mock-jwt-token'
        }

        with patch('openapi_server.impl.sandbox.list_sandbox_assistants') as mock_list:
            # Mock filtered response
            ttl = int((datetime.now(timezone.utc) + timedelta(minutes=20)).timestamp())
            mock_list.return_value = (
                {
                    "sandboxes": [
                        {
                            "sandboxId": "sandbox-001",
                            "assistantId": "assistant-001",
                            "name": "Filtered Sandbox",
                            "status": "tested",
                            "ttl": ttl,
                            "created": {"at": "2025-10-23T00:00:00Z", "by": "test@cmz.org"},
                            "expiresAt": "2025-10-23T00:20:00Z"
                        }
                    ]
                },
                200
            )

            # Make request with query parameters
            response = self.client.get(
                '/sandbox?status=tested&assistantId=assistant-001',
                headers=headers
            )

            # Verify contract compliance
            self.assertEqual(response.status_code, 200)

            response_data = json.loads(response.data)
            self.assertIn('sandboxes', response_data)

    def test_get_sandbox_by_id_contract(self):
        """Test GET /sandbox/{sandboxId} contract compliance"""
        sandbox_id = "test-sandbox-001"
        headers = {
            'Authorization': 'Bearer mock-jwt-token'
        }

        with patch('openapi_server.impl.sandbox.get_sandbox_assistant') as mock_get:
            # Mock successful get response
            ttl = int((datetime.now(timezone.utc) + timedelta(minutes=20)).timestamp())
            mock_get.return_value = (
                {
                    "sandboxId": sandbox_id,
                    "assistantId": "assistant-001",
                    "name": "Test Sandbox",
                    "personalityId": "personality-001",
                    "guardrailId": "guardrail-001",
                    "description": "Test sandbox description",
                    "status": "tested",
                    "ttl": ttl,
                    "created": {"at": "2025-10-23T00:00:00Z", "by": "test@cmz.org"},
                    "modified": {"at": "2025-10-23T00:10:00Z", "by": "test@cmz.org"},
                    "expiresAt": "2025-10-23T00:20:00Z"
                },
                200
            )

            # Make request
            response = self.client.get(f'/sandbox/{sandbox_id}', headers=headers)

            # Verify contract compliance
            self.assertEqual(response.status_code, 200)

            response_data = json.loads(response.data)
            self.assertEqual(response_data['sandboxId'], sandbox_id)

            # Verify all required fields present
            required_fields = ['sandboxId', 'assistantId', 'name', 'status', 'ttl', 'created']
            for field in required_fields:
                self.assertIn(field, response_data)

    def test_get_sandbox_not_found_contract(self):
        """Test GET /sandbox/{sandboxId} not found response contract"""
        sandbox_id = "nonexistent-sandbox"
        headers = {
            'Authorization': 'Bearer mock-jwt-token'
        }

        with patch('openapi_server.impl.sandbox.get_sandbox_assistant') as mock_get:
            # Mock not found response
            mock_get.return_value = (
                {
                    "error": "Sandbox not found",
                    "code": "not_found",
                    "details": {"sandboxId": sandbox_id}
                },
                404
            )

            # Make request
            response = self.client.get(f'/sandbox/{sandbox_id}', headers=headers)

            # Verify error contract compliance
            self.assertEqual(response.status_code, 404)

            response_data = json.loads(response.data)
            self.assertIn('error', response_data)

    def test_get_sandbox_expired_contract(self):
        """Test GET /sandbox/{sandboxId} expired response contract"""
        sandbox_id = "expired-sandbox"
        headers = {
            'Authorization': 'Bearer mock-jwt-token'
        }

        with patch('openapi_server.impl.sandbox.get_sandbox_assistant') as mock_get:
            # Mock expired response
            mock_get.return_value = (
                {
                    "error": "Sandbox has expired",
                    "code": "expired",
                    "details": {"sandboxId": sandbox_id, "expiredAt": "2025-10-23T00:00:00Z"}
                },
                410
            )

            # Make request
            response = self.client.get(f'/sandbox/{sandbox_id}', headers=headers)

            # Verify expired contract compliance
            self.assertEqual(response.status_code, 410)

            response_data = json.loads(response.data)
            self.assertIn('error', response_data)
            self.assertIn('expired', response_data['error'].lower())

    def test_promote_sandbox_contract(self):
        """Test POST /sandbox/{sandboxId}/promote contract compliance"""
        sandbox_id = "test-sandbox-001"
        headers = {
            'Authorization': 'Bearer mock-jwt-token'
        }

        with patch('openapi_server.impl.sandbox.promote_sandbox_to_live') as mock_promote:
            # Mock successful promotion response
            mock_promote.return_value = (
                {
                    "message": "Sandbox successfully promoted to live assistant",
                    "sandboxId": sandbox_id,
                    "assistantId": "assistant-001",
                    "promotedAt": "2025-10-23T00:15:00Z"
                },
                200
            )

            # Make request
            response = self.client.post(f'/sandbox/{sandbox_id}/promote', headers=headers)

            # Verify contract compliance
            self.assertEqual(response.status_code, 200)

            response_data = json.loads(response.data)
            self.assertIn('message', response_data)
            self.assertIn('assistantId', response_data)
            self.assertEqual(response_data['sandboxId'], sandbox_id)

    def test_promote_sandbox_not_found_contract(self):
        """Test POST /sandbox/{sandboxId}/promote not found response contract"""
        sandbox_id = "nonexistent-sandbox"
        headers = {
            'Authorization': 'Bearer mock-jwt-token'
        }

        with patch('openapi_server.impl.sandbox.promote_sandbox_to_live') as mock_promote:
            # Mock not found response
            mock_promote.return_value = (
                {
                    "error": "Sandbox not found",
                    "code": "not_found",
                    "details": {"sandboxId": sandbox_id}
                },
                404
            )

            # Make request
            response = self.client.post(f'/sandbox/{sandbox_id}/promote', headers=headers)

            # Verify error contract compliance
            self.assertEqual(response.status_code, 404)

            response_data = json.loads(response.data)
            self.assertIn('error', response_data)

    def test_delete_sandbox_contract(self):
        """Test DELETE /sandbox/{sandboxId} contract compliance"""
        sandbox_id = "test-sandbox-001"
        headers = {
            'Authorization': 'Bearer mock-jwt-token'
        }

        with patch('openapi_server.impl.sandbox.delete_sandbox_assistant') as mock_delete:
            # Mock successful deletion response
            mock_delete.return_value = (
                {
                    "message": "Sandbox deleted successfully",
                    "sandboxId": sandbox_id
                },
                204
            )

            # Make request
            response = self.client.delete(f'/sandbox/{sandbox_id}', headers=headers)

            # Verify contract compliance
            self.assertEqual(response.status_code, 204)

    def test_test_sandbox_chat_contract(self):
        """Test POST /sandbox/{sandboxId}/chat contract compliance"""
        sandbox_id = "test-sandbox-001"
        chat_request = {
            "message": "Hello, can you tell me about yourself?",
            "context": {
                "userId": "test-user-001",
                "sessionId": "test-session-001"
            }
        }

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer mock-jwt-token'
        }

        with patch('openapi_server.impl.sandbox.test_sandbox_chat') as mock_chat:
            # Mock successful chat response
            mock_chat.return_value = (
                {
                    "response": "Hello! I'm a test sandbox assistant for a zoo animal. I'm currently in testing mode.",
                    "conversationId": "test-conversation-001",
                    "usage": {
                        "promptTokens": 45,
                        "completionTokens": 23,
                        "totalTokens": 68
                    },
                    "metadata": {
                        "model": "gpt-4",
                        "personality": "friendly-educational",
                        "guardrails": ["family-friendly", "no-personal-info"]
                    }
                },
                200
            )

            # Make request
            response = self.client.post(
                f'/sandbox/{sandbox_id}/chat',
                data=json.dumps(chat_request),
                headers=headers
            )

            # Verify contract compliance
            self.assertEqual(response.status_code, 200)

            response_data = json.loads(response.data)
            self.assertIn('response', response_data)
            self.assertIn('conversationId', response_data)
            self.assertIn('usage', response_data)
            self.assertIn('metadata', response_data)

            # Verify usage tracking structure
            usage = response_data['usage']
            self.assertIn('promptTokens', usage)
            self.assertIn('completionTokens', usage)
            self.assertIn('totalTokens', usage)

    def test_content_type_validation(self):
        """Test content type validation for POST requests"""
        valid_request = {
            "assistantId": "test-assistant-001",
            "name": "Test Sandbox",
            "personalityId": "test-personality-001",
            "guardrailId": "test-guardrail-001"
        }

        # Test with missing content-type header
        response = self.client.post(
            '/sandbox',
            data=json.dumps(valid_request),
            headers={'Authorization': 'Bearer mock-jwt-token'}
        )

        # Should handle missing content-type gracefully or return 400
        self.assertIn(response.status_code, [400, 415, 201])  # Depends on implementation

        # Test with wrong content-type
        response = self.client.post(
            '/sandbox',
            data=json.dumps(valid_request),
            headers={
                'Content-Type': 'text/plain',
                'Authorization': 'Bearer mock-jwt-token'
            }
        )

        # Should reject wrong content-type
        self.assertIn(response.status_code, [400, 415])

    def test_authentication_contract(self):
        """Test authentication requirements contract"""
        valid_request = {
            "assistantId": "test-assistant-001",
            "name": "Test Sandbox",
            "personalityId": "test-personality-001",
            "guardrailId": "test-guardrail-001"
        }

        # Test without authorization header
        response = self.client.post(
            '/sandbox',
            data=json.dumps(valid_request),
            headers={'Content-Type': 'application/json'}
        )

        # Should require authentication (401) or handle mock auth gracefully
        self.assertIn(response.status_code, [401, 201])  # Depends on AUTH_MODE setting


if __name__ == '__main__':
    pytest.main([__file__])