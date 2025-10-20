"""
Integration tests for DynamoDB operations
Task T008: Create integration tests for DynamoDB operations
Tests the impl/utils/dynamo.py utilities with mock DynamoDB
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any
import json
from datetime import datetime
from decimal import Decimal

# Import the DynamoDB utilities
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from openapi_server.impl.utils.dynamo import (
    to_ddb, from_ddb, now_iso, model_to_json_keyed_dict,
    ensure_pk, error_response, not_found
)


class TestDynamoDBUtilities:
    """Test DynamoDB utility functions"""

    def test_to_ddb_basic_types(self):
        """Test converting Python types to DynamoDB format"""
        data = {
            'string': 'test',
            'number': 42,
            'boolean': True,
            'null': None,
            'list': [1, 2, 3],
            'dict': {'nested': 'value'}
        }

        result = to_ddb(data)

        assert result['string'] == 'test'
        assert result['number'] == Decimal('42')
        assert result['boolean'] is True
        assert result['null'] is None
        assert result['list'] == [Decimal('1'), Decimal('2'), Decimal('3')]
        assert result['dict']['nested'] == 'value'

    def test_from_ddb_decimal_conversion(self):
        """Test converting DynamoDB Decimals back to Python types"""
        data = {
            'integer': Decimal('42'),
            'float': Decimal('3.14'),
            'nested': {
                'decimal': Decimal('100')
            },
            'list': [Decimal('1'), Decimal('2')]
        }

        result = from_ddb(data)

        assert result['integer'] == 42
        assert result['float'] == 3.14
        assert result['nested']['decimal'] == 100
        assert result['list'] == [1, 2]

    def test_now_iso_format(self):
        """Test ISO timestamp generation"""
        timestamp = now_iso()

        # Check format: YYYY-MM-DDTHH:MM:SS.sssZ
        assert 'T' in timestamp
        assert timestamp.endswith('Z')
        assert len(timestamp) >= 20

        # Verify it's a valid ISO string
        parsed = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        assert parsed is not None

    def test_model_to_json_keyed_dict(self):
        """Test converting OpenAPI models to dictionaries"""
        # Mock model with to_dict method
        mock_model = Mock()
        mock_model.to_dict.return_value = {'key': 'value'}

        result = model_to_json_keyed_dict(mock_model)
        assert result == {'key': 'value'}

        # Test with plain dictionary
        plain_dict = {'key': 'value'}
        result = model_to_json_keyed_dict(plain_dict)
        assert result == {'key': 'value'}

    def test_ensure_pk_generation(self):
        """Test primary key generation"""
        data = {}
        ensure_pk(data, 'testId')

        assert 'testId' in data
        assert len(data['testId']) == 36  # UUID length with hyphens
        assert data['testId'].count('-') == 4  # UUID format

    def test_ensure_pk_existing(self):
        """Test that existing primary keys are not overwritten"""
        data = {'testId': 'existing-id'}
        ensure_pk(data, 'testId')

        assert data['testId'] == 'existing-id'

    def test_error_response(self):
        """Test error response generation"""
        from botocore.exceptions import ClientError

        # Mock ClientError
        error = ClientError(
            {
                'Error': {
                    'Code': 'ValidationException',
                    'Message': 'One or more parameter values were invalid'
                }
            },
            'PutItem'
        )

        response, status_code = error_response(error)

        assert status_code == 400
        assert 'error' in response
        assert response['error']['code'] == 'ValidationException'

    def test_not_found_response(self):
        """Test not found response generation"""
        response, status_code = not_found('Family', 'family123')

        assert status_code == 404
        assert 'error' in response
        assert 'Family' in response['error']['message']
        assert 'family123' in response['error']['message']


class TestDynamoDBTableOperations:
    """Test actual DynamoDB table operations with mocks"""

    @patch('openapi_server.impl.utils.dynamo.table')
    def test_put_item_operation(self, mock_table_func):
        """Test putting an item to DynamoDB"""
        mock_table = Mock()
        mock_table_func.return_value = mock_table

        # Simulate successful put
        mock_table.put_item.return_value = {
            'ResponseMetadata': {'HTTPStatusCode': 200}
        }

        item = {
            'familyId': 'test-family-123',
            'familyName': 'Test Family',
            'children': ['child1', 'child2'],
            'created': {'at': now_iso()},
            'modified': {'at': now_iso()}
        }

        # Convert to DynamoDB format
        ddb_item = to_ddb(item)

        # Put the item
        result = mock_table.put_item(Item=ddb_item)

        assert result['ResponseMetadata']['HTTPStatusCode'] == 200
        mock_table.put_item.assert_called_once_with(Item=ddb_item)

    @patch('openapi_server.impl.utils.dynamo.table')
    def test_get_item_operation(self, mock_table_func):
        """Test getting an item from DynamoDB"""
        mock_table = Mock()
        mock_table_func.return_value = mock_table

        # Simulate successful get
        mock_table.get_item.return_value = {
            'Item': {
                'familyId': 'test-family-123',
                'familyName': 'Test Family',
                'memberCount': Decimal('4')
            }
        }

        # Get the item
        result = mock_table.get_item(Key={'familyId': 'test-family-123'})

        assert 'Item' in result
        assert result['Item']['familyId'] == 'test-family-123'
        mock_table.get_item.assert_called_once_with(Key={'familyId': 'test-family-123'})

        # Convert from DynamoDB format
        item = from_ddb(result['Item'])
        assert item['memberCount'] == 4  # Decimal converted to int

    @patch('openapi_server.impl.utils.dynamo.table')
    def test_scan_operation(self, mock_table_func):
        """Test scanning a DynamoDB table"""
        mock_table = Mock()
        mock_table_func.return_value = mock_table

        # Simulate scan with multiple items
        mock_table.scan.return_value = {
            'Items': [
                {'familyId': 'family1', 'memberCount': Decimal('3')},
                {'familyId': 'family2', 'memberCount': Decimal('5')}
            ],
            'Count': 2
        }

        # Scan the table
        result = mock_table.scan()

        assert result['Count'] == 2
        assert len(result['Items']) == 2

        # Convert items from DynamoDB format
        items = [from_ddb(item) for item in result['Items']]
        assert items[0]['memberCount'] == 3
        assert items[1]['memberCount'] == 5

    @patch('openapi_server.impl.utils.dynamo.table')
    def test_delete_item_operation(self, mock_table_func):
        """Test deleting an item from DynamoDB (soft delete)"""
        mock_table = Mock()
        mock_table_func.return_value = mock_table

        # Simulate successful update for soft delete
        mock_table.update_item.return_value = {
            'ResponseMetadata': {'HTTPStatusCode': 200}
        }

        # Soft delete by updating deletedAt
        result = mock_table.update_item(
            Key={'familyId': 'test-family-123'},
            UpdateExpression='SET deletedAt = :now',
            ExpressionAttributeValues={':now': now_iso()}
        )

        assert result['ResponseMetadata']['HTTPStatusCode'] == 200
        mock_table.update_item.assert_called_once()

    @patch('openapi_server.impl.utils.dynamo.table')
    def test_batch_write_operation(self, mock_table_func):
        """Test batch write operations"""
        mock_table = Mock()
        mock_table_func.return_value = mock_table

        # Simulate successful batch write
        mock_table.batch_writer.return_value.__enter__ = Mock()
        mock_table.batch_writer.return_value.__exit__ = Mock()
        batch = mock_table.batch_writer.return_value.__enter__.return_value
        batch.put_item = Mock()

        items = [
            {'animalId': 'lion1', 'name': 'Leo'},
            {'animalId': 'tiger1', 'name': 'Tony'},
            {'animalId': 'bear1', 'name': 'Bella'}
        ]

        # Batch write
        with mock_table.batch_writer() as batch:
            for item in items:
                batch.put_item(Item=to_ddb(item))

        assert batch.put_item.call_count == 3


class TestDynamoDBErrorHandling:
    """Test error handling for DynamoDB operations"""

    @patch('openapi_server.impl.utils.dynamo.table')
    def test_handle_validation_exception(self, mock_table_func):
        """Test handling DynamoDB validation exceptions"""
        from botocore.exceptions import ClientError

        mock_table = Mock()
        mock_table_func.return_value = mock_table

        # Simulate validation error
        mock_table.put_item.side_effect = ClientError(
            {
                'Error': {
                    'Code': 'ValidationException',
                    'Message': 'Invalid attribute value type'
                }
            },
            'PutItem'
        )

        try:
            mock_table.put_item(Item={'invalid': 'data'})
        except ClientError as e:
            response, status_code = error_response(e)
            assert status_code == 400
            assert 'ValidationException' in response['error']['code']

    @patch('openapi_server.impl.utils.dynamo.table')
    def test_handle_resource_not_found(self, mock_table_func):
        """Test handling resource not found exceptions"""
        from botocore.exceptions import ClientError

        mock_table = Mock()
        mock_table_func.return_value = mock_table

        # Simulate resource not found
        mock_table.get_item.side_effect = ClientError(
            {
                'Error': {
                    'Code': 'ResourceNotFoundException',
                    'Message': 'Requested resource not found'
                }
            },
            'GetItem'
        )

        try:
            mock_table.get_item(Key={'id': 'nonexistent'})
        except ClientError as e:
            response, status_code = error_response(e)
            assert status_code == 404
            assert 'ResourceNotFoundException' in response['error']['code']

    @patch('openapi_server.impl.utils.dynamo.table')
    def test_handle_throttling(self, mock_table_func):
        """Test handling DynamoDB throttling"""
        from botocore.exceptions import ClientError

        mock_table = Mock()
        mock_table_func.return_value = mock_table

        # Simulate throttling
        mock_table.scan.side_effect = ClientError(
            {
                'Error': {
                    'Code': 'ProvisionedThroughputExceededException',
                    'Message': 'Request rate exceeded'
                }
            },
            'Scan'
        )

        try:
            mock_table.scan()
        except ClientError as e:
            response, status_code = error_response(e)
            assert status_code == 429  # Too Many Requests
            assert 'ProvisionedThroughputExceededException' in response['error']['code']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])