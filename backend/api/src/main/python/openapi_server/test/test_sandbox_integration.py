"""
Integration tests for Sandbox Assistant expiration and cleanup

Tests the integration between sandbox creation, TTL management, and automatic
cleanup processes to ensure sandbox assistants properly expire and are cleaned up.

T036 - User Story 2: Test Assistant Changes Safely
"""

import pytest
import time
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock

from openapi_server.impl import sandbox, assistants
from openapi_server.impl.utils.dynamo import to_ddb, from_ddb, now_iso


class TestSandboxExpirationIntegration:
    """Test integration of sandbox expiration with assistant management"""

    @patch('openapi_server.impl.sandbox._table')
    @patch('openapi_server.impl.assistants._table')
    def test_sandbox_expiry_integration_workflow(self, mock_assistant_table, mock_sandbox_table):
        """Test complete sandbox workflow from creation to expiry"""
        # Mock base assistant
        base_assistant = {
            'assistantId': 'integration-assistant-001',
            'name': 'Base Integration Assistant',
            'animalId': 'tiger-001',
            'personalityId': 'original-personality',
            'guardrailId': 'original-guardrail',
            'status': 'active'
        }

        # Mock DynamoDB responses for base assistant
        mock_assistant_table.return_value.get_item.return_value = {'Item': to_ddb(base_assistant)}

        # Step 1: Create sandbox assistant
        sandbox_request = {
            'assistantId': 'integration-assistant-001',
            'name': 'Integration Test Sandbox',
            'personalityId': 'new-personality-001',
            'guardrailId': 'new-guardrail-001',
            'description': 'Testing integration workflow'
        }

        # Mock sandbox creation
        created_sandbox = {
            'sandboxId': 'integration-sandbox-001',
            'ttl': int((datetime.now(timezone.utc) + timedelta(minutes=30)).timestamp()),
            'status': 'draft',
            'created': {'at': now_iso(), 'by': 'integration@test.cmz.org'},
            **sandbox_request
        }

        mock_sandbox_table.return_value.put_item.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        mock_sandbox_table.return_value.get_item.return_value = {'Item': to_ddb(created_sandbox)}

        # Execute sandbox creation
        sandbox_result, sandbox_status = sandbox.create_sandbox_assistant(sandbox_request)

        # Verify sandbox creation
        assert sandbox_status == 201
        assert 'sandboxId' in sandbox_result
        assert sandbox_result['status'] == 'draft'

        # Step 2: Simulate sandbox usage and testing
        # Update sandbox status to 'tested'
        tested_sandbox = {**created_sandbox, 'status': 'tested'}
        mock_sandbox_table.return_value.get_item.return_value = {'Item': to_ddb(tested_sandbox)}

        # Step 3: Test promotion workflow
        mock_assistant_table.return_value.update_item.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        mock_sandbox_table.return_value.delete_item.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}

        promote_result, promote_status = sandbox.promote_sandbox_to_live('integration-sandbox-001')

        # Verify promotion
        assert promote_status == 200
        assert 'promoted' in promote_result['message'].lower()

        # Verify assistant was updated and sandbox was deleted
        mock_assistant_table.return_value.update_item.assert_called_once()
        mock_sandbox_table.return_value.delete_item.assert_called_once()

    @patch('openapi_server.impl.sandbox._table')
    def test_sandbox_cleanup_integration_with_multiple_sandboxes(self, mock_table):
        """Test integration of cleanup with multiple sandboxes in different states"""
        current_time = datetime.now(timezone.utc)

        # Create mix of expired and valid sandboxes
        sandboxes = [
            # Expired sandboxes
            {
                'sandboxId': 'expired-integration-1',
                'assistantId': 'assistant-001',
                'ttl': int((current_time - timedelta(minutes=10)).timestamp()),
                'status': 'draft'
            },
            {
                'sandboxId': 'expired-integration-2',
                'assistantId': 'assistant-002',
                'ttl': int((current_time - timedelta(hours=2)).timestamp()),
                'status': 'tested'
            },
            # Valid sandboxes
            {
                'sandboxId': 'valid-integration-1',
                'assistantId': 'assistant-003',
                'ttl': int((current_time + timedelta(minutes=20)).timestamp()),
                'status': 'draft'
            },
            {
                'sandboxId': 'valid-integration-2',
                'assistantId': 'assistant-004',
                'ttl': int((current_time + timedelta(minutes=15)).timestamp()),
                'status': 'tested'
            }
        ]

        # Mock scan response
        mock_table.return_value.scan.return_value = {
            'Items': [to_ddb(sb) for sb in sandboxes]
        }
        mock_table.return_value.delete_item.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}

        # Execute cleanup
        cleanup_result = sandbox.cleanup_expired_sandboxes()

        # Verify cleanup results
        assert cleanup_result['cleaned_count'] == 2  # Two expired sandboxes
        assert mock_table.return_value.delete_item.call_count == 2

        # Verify only expired sandboxes were deleted
        delete_calls = mock_table.return_value.delete_item.call_args_list
        deleted_sandbox_ids = [call[1]['Key']['sandboxId'] for call in delete_calls]
        assert 'expired-integration-1' in deleted_sandbox_ids
        assert 'expired-integration-2' in deleted_sandbox_ids
        assert 'valid-integration-1' not in deleted_sandbox_ids
        assert 'valid-integration-2' not in deleted_sandbox_ids

    @patch('openapi_server.impl.sandbox._table')
    def test_sandbox_listing_with_expired_filtering(self, mock_table):
        """Test that listing sandboxes properly filters out expired entries"""
        current_time = datetime.now(timezone.utc)

        # Create mix of expired and valid sandboxes
        sandboxes = [
            {
                'sandboxId': 'expired-list-1',
                'assistantId': 'assistant-001',
                'ttl': int((current_time - timedelta(minutes=5)).timestamp()),
                'status': 'draft',
                'name': 'Expired Sandbox 1'
            },
            {
                'sandboxId': 'valid-list-1',
                'assistantId': 'assistant-002',
                'ttl': int((current_time + timedelta(minutes=25)).timestamp()),
                'status': 'draft',
                'name': 'Valid Sandbox 1'
            },
            {
                'sandboxId': 'valid-list-2',
                'assistantId': 'assistant-003',
                'ttl': int((current_time + timedelta(minutes=15)).timestamp()),
                'status': 'tested',
                'name': 'Valid Sandbox 2'
            }
        ]

        # Mock scan response
        mock_table.return_value.scan.return_value = {
            'Items': [to_ddb(sb) for sb in sandboxes]
        }

        # Execute listing
        list_result, list_status = sandbox.list_sandbox_assistants()

        # Verify listing results
        assert list_status == 200
        assert 'sandboxes' in list_result

        # Verify only valid sandboxes are returned
        returned_sandboxes = list_result['sandboxes']
        assert len(returned_sandboxes) == 2  # Only non-expired sandboxes

        returned_ids = [sb['sandboxId'] for sb in returned_sandboxes]
        assert 'valid-list-1' in returned_ids
        assert 'valid-list-2' in returned_ids
        assert 'expired-list-1' not in returned_ids

    @patch('openapi_server.impl.sandbox._table')
    @patch('openapi_server.impl.assistants._table')
    def test_sandbox_assistant_relationship_integration(self, mock_assistant_table, mock_sandbox_table):
        """Test integration between sandbox and base assistant relationships"""
        # Mock base assistant
        base_assistant = {
            'assistantId': 'relationship-assistant-001',
            'name': 'Relationship Test Assistant',
            'animalId': 'elephant-001',
            'personalityId': 'current-personality',
            'guardrailId': 'current-guardrail',
            'status': 'active'
        }

        mock_assistant_table.return_value.get_item.return_value = {'Item': to_ddb(base_assistant)}

        # Create multiple sandboxes for the same base assistant
        sandbox_requests = [
            {
                'assistantId': 'relationship-assistant-001',
                'name': 'Personality Test 1',
                'personalityId': 'test-personality-1',
                'guardrailId': 'current-guardrail'
            },
            {
                'assistantId': 'relationship-assistant-001',
                'name': 'Personality Test 2',
                'personalityId': 'test-personality-2',
                'guardrailId': 'current-guardrail'
            }
        ]

        created_sandboxes = []
        for i, request in enumerate(sandbox_requests):
            sandbox_id = f'relationship-sandbox-{i+1:03d}'
            created_sandbox = {
                'sandboxId': sandbox_id,
                'ttl': int((datetime.now(timezone.utc) + timedelta(minutes=30)).timestamp()),
                'status': 'draft',
                'created': {'at': now_iso(), 'by': 'relationship@test.cmz.org'},
                **request
            }
            created_sandboxes.append(created_sandbox)

        # Mock sandbox creation responses
        mock_sandbox_table.return_value.put_item.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}

        # Create sandboxes
        for i, (request, created) in enumerate(zip(sandbox_requests, created_sandboxes)):
            mock_sandbox_table.return_value.get_item.return_value = {'Item': to_ddb(created)}
            result, status = sandbox.create_sandbox_assistant(request)
            assert status == 201
            assert result['assistantId'] == 'relationship-assistant-001'

        # Mock listing sandboxes for specific assistant
        mock_sandbox_table.return_value.scan.return_value = {
            'Items': [to_ddb(sb) for sb in created_sandboxes]
        }

        # Test listing sandboxes by assistant ID
        list_result, list_status = sandbox.list_sandbox_assistants(assistant_id='relationship-assistant-001')

        # Verify relationship integrity
        assert list_status == 200
        returned_sandboxes = list_result['sandboxes']
        assert len(returned_sandboxes) == 2

        # Verify all returned sandboxes belong to the same base assistant
        for returned_sandbox in returned_sandboxes:
            assert returned_sandbox['assistantId'] == 'relationship-assistant-001'

    @patch('openapi_server.impl.sandbox._table')
    def test_sandbox_concurrent_access_integration(self, mock_table):
        """Test sandbox behavior under concurrent access scenarios"""
        # Simulate concurrent promotion attempts on same sandbox
        sandbox_data = {
            'sandboxId': 'concurrent-sandbox-001',
            'assistantId': 'concurrent-assistant-001',
            'personalityId': 'new-personality',
            'guardrailId': 'new-guardrail',
            'status': 'tested',
            'ttl': int((datetime.now(timezone.utc) + timedelta(minutes=20)).timestamp())
        }

        # First promotion attempt succeeds
        mock_table.return_value.get_item.return_value = {'Item': to_ddb(sandbox_data)}
        mock_table.return_value.delete_item.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}

        # Second promotion attempt should fail (sandbox already deleted)
        def side_effect_get_item(*args, **kwargs):
            # First call returns sandbox, second call returns empty (deleted)
            if mock_table.return_value.get_item.call_count <= 1:
                return {'Item': to_ddb(sandbox_data)}
            else:
                return {}

        mock_table.return_value.get_item.side_effect = side_effect_get_item

        # First promotion
        result1, status1 = sandbox.promote_sandbox_to_live('concurrent-sandbox-001')
        assert status1 == 200

        # Second promotion (should fail)
        result2, status2 = sandbox.promote_sandbox_to_live('concurrent-sandbox-001')
        assert status2 == 404
        assert 'not found' in result2['error'].lower()


if __name__ == '__main__':
    pytest.main([__file__])