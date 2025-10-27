"""
Unit tests for Sandbox Assistant functionality

Tests sandbox creation, TTL expiry, and promotion logic for safely testing
assistant configurations before deploying to live environments.

T034, T035 - User Story 2: Test Assistant Changes Safely
"""

import pytest
import uuid
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock

from openapi_server.impl import sandbox
from openapi_server.impl.utils.dynamo import to_ddb, from_ddb


class TestSandboxCreation:
    """Test sandbox assistant creation and TTL handling"""

    @patch('openapi_server.impl.sandbox._table')
    def test_create_sandbox_assistant_success(self, mock_table):
        """Test successful sandbox assistant creation with TTL"""
        # Mock DynamoDB table operations
        mock_table.return_value.put_item.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        mock_table.return_value.get_item.return_value = {
            'Item': to_ddb({
                'sandboxId': 'test-sandbox-001',
                'assistantId': 'base-assistant-001',
                'name': 'Test Sandbox Assistant',
                'personalityId': 'test-personality-001',
                'guardrailId': 'test-guardrail-001',
                'status': 'draft',
                'ttl': int((datetime.now(timezone.utc) + timedelta(minutes=30)).timestamp()),
                'created': {'at': '2025-10-23T00:00:00Z', 'by': 'test@cmz.org'}
            })
        }

        # Create sandbox assistant request
        sandbox_request = {
            'assistantId': 'base-assistant-001',
            'name': 'Test Sandbox Assistant',
            'personalityId': 'test-personality-001',
            'guardrailId': 'test-guardrail-001',
            'description': 'Testing new personality configuration'
        }

        # Execute sandbox creation
        result, status_code = sandbox.create_sandbox_assistant(sandbox_request)

        # Verify successful creation
        assert status_code == 201
        assert 'sandboxId' in result
        assert result['name'] == sandbox_request['name']
        assert result['status'] == 'draft'
        assert 'ttl' in result
        assert 'created' in result

        # Verify TTL is set to approximately 30 minutes from now
        ttl_time = datetime.fromtimestamp(result['ttl'], tz=timezone.utc)
        expected_expiry = datetime.now(timezone.utc) + timedelta(minutes=30)
        time_diff = abs((ttl_time - expected_expiry).total_seconds())
        assert time_diff < 60  # Allow 1 minute tolerance

        # Verify DynamoDB put_item was called
        mock_table.return_value.put_item.assert_called_once()

    @patch('openapi_server.impl.sandbox._table')
    def test_create_sandbox_assistant_validation_error(self, mock_table):
        """Test sandbox creation with invalid input"""
        # Invalid request missing required fields
        invalid_request = {
            'description': 'Missing required fields'
        }

        # Execute sandbox creation
        result, status_code = sandbox.create_sandbox_assistant(invalid_request)

        # Verify validation error
        assert status_code == 400
        assert 'error' in result
        assert 'validation' in result['error'].lower() or 'required' in result['error'].lower()

        # Verify DynamoDB was not called
        mock_table.return_value.put_item.assert_not_called()

    @patch('openapi_server.impl.sandbox._table')
    def test_sandbox_ttl_calculation(self, mock_table):
        """Test TTL calculation for sandbox expiry"""
        # Mock DynamoDB operations
        mock_table.return_value.put_item.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}

        # Create sandbox with default TTL
        sandbox_request = {
            'assistantId': 'base-assistant-001',
            'name': 'TTL Test Assistant',
            'personalityId': 'test-personality-001',
            'guardrailId': 'test-guardrail-001'
        }

        # Record current time before creation
        start_time = datetime.now(timezone.utc)

        # Mock the get_item to return our created sandbox
        expected_sandbox = {
            'sandboxId': 'test-sandbox-ttl',
            'ttl': int((start_time + timedelta(minutes=30)).timestamp()),
            **sandbox_request,
            'status': 'draft',
            'created': {'at': start_time.isoformat(), 'by': 'test@cmz.org'}
        }
        mock_table.return_value.get_item.return_value = {'Item': to_ddb(expected_sandbox)}

        # Execute creation
        result, status_code = sandbox.create_sandbox_assistant(sandbox_request)

        # Verify TTL is correctly set
        assert status_code == 201
        ttl_timestamp = result['ttl']
        ttl_time = datetime.fromtimestamp(ttl_timestamp, tz=timezone.utc)

        # Verify TTL is approximately 30 minutes from creation
        expected_expiry = start_time + timedelta(minutes=30)
        time_diff = abs((ttl_time - expected_expiry).total_seconds())
        assert time_diff < 60  # Allow 1 minute tolerance

    @patch('openapi_server.impl.sandbox._table')
    def test_sandbox_expires_automatically(self, mock_table):
        """Test that expired sandboxes are handled correctly"""
        # Create an expired sandbox (TTL in the past)
        expired_ttl = int((datetime.now(timezone.utc) - timedelta(minutes=5)).timestamp())

        # Mock DynamoDB to return expired sandbox
        mock_table.return_value.get_item.return_value = {
            'Item': to_ddb({
                'sandboxId': 'expired-sandbox-001',
                'assistantId': 'base-assistant-001',
                'ttl': expired_ttl,
                'status': 'draft'
            })
        }

        # Try to retrieve expired sandbox
        result, status_code = sandbox.get_sandbox_assistant('expired-sandbox-001')

        # Verify expired sandbox returns not found or appropriate error
        assert status_code in [404, 410]  # Not found or Gone
        if status_code == 410:
            assert 'expired' in result.get('error', '').lower()


class TestSandboxPromotion:
    """Test sandbox promotion logic"""

    @patch('openapi_server.impl.sandbox._table')
    @patch('openapi_server.impl.assistants._table')
    def test_promote_sandbox_to_live_success(self, mock_assistant_table, mock_sandbox_table):
        """Test successful promotion of sandbox to live assistant"""
        # Mock sandbox data
        sandbox_data = {
            'sandboxId': 'test-sandbox-001',
            'assistantId': 'base-assistant-001',
            'name': 'Promoted Assistant',
            'personalityId': 'new-personality-001',
            'guardrailId': 'new-guardrail-001',
            'status': 'tested',
            'ttl': int((datetime.now(timezone.utc) + timedelta(minutes=20)).timestamp())
        }

        # Mock existing live assistant
        live_assistant_data = {
            'assistantId': 'base-assistant-001',
            'name': 'Original Assistant',
            'personalityId': 'old-personality-001',
            'guardrailId': 'old-guardrail-001',
            'status': 'active'
        }

        # Mock DynamoDB responses
        mock_sandbox_table.return_value.get_item.return_value = {'Item': to_ddb(sandbox_data)}
        mock_assistant_table.return_value.get_item.return_value = {'Item': to_ddb(live_assistant_data)}
        mock_assistant_table.return_value.update_item.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        mock_sandbox_table.return_value.delete_item.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}

        # Execute promotion
        result, status_code = sandbox.promote_sandbox_to_live('test-sandbox-001')

        # Verify successful promotion
        assert status_code == 200
        assert 'message' in result
        assert 'promoted' in result['message'].lower()
        assert result['assistantId'] == 'base-assistant-001'

        # Verify assistant was updated
        mock_assistant_table.return_value.update_item.assert_called_once()

        # Verify sandbox was deleted
        mock_sandbox_table.return_value.delete_item.assert_called_once()

    @patch('openapi_server.impl.sandbox._table')
    def test_promote_nonexistent_sandbox_error(self, mock_sandbox_table):
        """Test promotion of non-existent sandbox"""
        # Mock sandbox not found
        mock_sandbox_table.return_value.get_item.return_value = {}

        # Execute promotion
        result, status_code = sandbox.promote_sandbox_to_live('nonexistent-sandbox')

        # Verify not found error
        assert status_code == 404
        assert 'error' in result
        assert 'not found' in result['error'].lower()

    @patch('openapi_server.impl.sandbox._table')
    def test_promote_expired_sandbox_error(self, mock_sandbox_table):
        """Test promotion of expired sandbox"""
        # Mock expired sandbox
        expired_sandbox = {
            'sandboxId': 'expired-sandbox-001',
            'assistantId': 'base-assistant-001',
            'ttl': int((datetime.now(timezone.utc) - timedelta(minutes=5)).timestamp()),
            'status': 'draft'
        }

        mock_sandbox_table.return_value.get_item.return_value = {'Item': to_ddb(expired_sandbox)}

        # Execute promotion
        result, status_code = sandbox.promote_sandbox_to_live('expired-sandbox-001')

        # Verify expired error
        assert status_code == 410  # Gone
        assert 'error' in result
        assert 'expired' in result['error'].lower()


class TestSandboxCleanup:
    """Test automatic sandbox cleanup functionality"""

    @patch('openapi_server.impl.sandbox._table')
    def test_cleanup_expired_sandboxes(self, mock_table):
        """Test cleanup of expired sandbox entries"""
        # Mock scan to return expired sandboxes
        current_time = datetime.now(timezone.utc)
        expired_time = int((current_time - timedelta(minutes=5)).timestamp())
        valid_time = int((current_time + timedelta(minutes=25)).timestamp())

        mock_scan_response = {
            'Items': [
                to_ddb({
                    'sandboxId': 'expired-1',
                    'ttl': expired_time,
                    'status': 'draft'
                }),
                to_ddb({
                    'sandboxId': 'expired-2',
                    'ttl': expired_time,
                    'status': 'tested'
                }),
                to_ddb({
                    'sandboxId': 'valid-1',
                    'ttl': valid_time,
                    'status': 'draft'
                })
            ]
        }

        mock_table.return_value.scan.return_value = mock_scan_response
        mock_table.return_value.delete_item.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}

        # Execute cleanup
        result = sandbox.cleanup_expired_sandboxes()

        # Verify cleanup results
        assert 'cleaned_count' in result
        assert result['cleaned_count'] == 2  # Two expired sandboxes

        # Verify delete_item was called twice (for expired sandboxes only)
        assert mock_table.return_value.delete_item.call_count == 2

    @patch('openapi_server.impl.sandbox._table')
    def test_cleanup_no_expired_sandboxes(self, mock_table):
        """Test cleanup when no sandboxes are expired"""
        # Mock scan to return only valid sandboxes
        valid_time = int((datetime.now(timezone.utc) + timedelta(minutes=25)).timestamp())

        mock_scan_response = {
            'Items': [
                to_ddb({
                    'sandboxId': 'valid-1',
                    'ttl': valid_time,
                    'status': 'draft'
                }),
                to_ddb({
                    'sandboxId': 'valid-2',
                    'ttl': valid_time,
                    'status': 'tested'
                })
            ]
        }

        mock_table.return_value.scan.return_value = mock_scan_response

        # Execute cleanup
        result = sandbox.cleanup_expired_sandboxes()

        # Verify no cleanup needed
        assert result['cleaned_count'] == 0

        # Verify delete_item was not called
        mock_table.return_value.delete_item.assert_not_called()


if __name__ == '__main__':
    pytest.main([__file__])