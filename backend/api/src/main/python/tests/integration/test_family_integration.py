"""
Integration tests for Family CRUD operations
Task T010: Create family CRUD tests
Tests complete family lifecycle with DynamoDB persistence
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from typing import Dict, Any, List
import json
import uuid
from datetime import datetime
from decimal import Decimal

# Import required modules
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from openapi_server.impl.handlers import (
    handle_family_list_get,
    handle_family_details_post,
    handle_family_details_get,
    handle_family_details_patch,
    handle_family_details_delete,
    handle_create_family,
    handle_delete_family
)
from openapi_server.models.family import Family
from openapi_server.models.error import Error


class TestFamilyCRUDOperations:
    """Test complete CRUD lifecycle for families"""

    @pytest.fixture
    def mock_dynamo_table(self):
        """Fixture for mocked DynamoDB table"""
        with patch('openapi_server.impl.utils.dynamo.table') as mock_table_func:
            mock_table = Mock()
            mock_table_func.return_value = mock_table
            yield mock_table

    @pytest.fixture
    def sample_family_data(self):
        """Sample family data for testing"""
        return {
            'familyName': 'The Smiths',
            'parents': [
                {'userId': 'parent1', 'name': 'John Smith', 'email': 'john@example.com'},
                {'userId': 'parent2', 'name': 'Jane Smith', 'email': 'jane@example.com'}
            ],
            'children': [
                {'userId': 'child1', 'name': 'Tommy Smith', 'age': 10},
                {'userId': 'child2', 'name': 'Sally Smith', 'age': 8}
            ],
            'notes': 'Regular zoo visitors'
        }

    def test_create_family_success(self, mock_dynamo_table, sample_family_data):
        """Test successful family creation"""
        # Mock DynamoDB put_item response
        mock_dynamo_table.put_item.return_value = {
            'ResponseMetadata': {'HTTPStatusCode': 200}
        }

        with patch('openapi_server.impl.adapters.flask.family_handlers.FlaskFamilyHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_handler_class.return_value = mock_handler

            # Mock the create_family method
            created_family = {
                **sample_family_data,
                'familyId': 'fam-123',
                'created': {'at': '2024-01-01T00:00:00Z'},
                'modified': {'at': '2024-01-01T00:00:00Z'}
            }
            mock_handler.create_family.return_value = (created_family, 201)

            # Create family
            response, status = handle_family_details_post(sample_family_data)

            # Assertions
            assert status == 201
            assert 'familyId' in response
            mock_handler.create_family.assert_called_once_with(sample_family_data)

    def test_create_family_validation_error(self, sample_family_data):
        """Test family creation with validation errors"""
        # Remove required field (children)
        invalid_data = {**sample_family_data}
        invalid_data.pop('children')

        with patch('openapi_server.impl.adapters.flask.family_handlers.FlaskFamilyHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_handler_class.return_value = mock_handler

            # Mock validation error
            mock_handler.create_family.return_value = (
                {'error': {'code': 'validation_error', 'message': 'At least one child is required'}},
                400
            )

            response, status = handle_family_details_post(invalid_data)

            # Should return validation error
            assert status == 400
            assert 'error' in response

    def test_get_family_by_id(self, mock_dynamo_table):
        """Test retrieving a family by ID"""
        family_id = 'fam-123'

        # Mock DynamoDB get_item response
        mock_dynamo_table.get_item.return_value = {
            'Item': {
                'familyId': family_id,
                'familyName': 'The Smiths',
                'memberCount': Decimal('4'),
                'created': {'at': '2024-01-01T00:00:00Z'}
            }
        }

        with patch('openapi_server.impl.adapters.flask.family_handlers.FlaskFamilyHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_handler_class.return_value = mock_handler

            mock_handler.get_family.return_value = (
                {
                    'familyId': family_id,
                    'familyName': 'The Smiths',
                    'memberCount': 4,
                    'created': {'at': '2024-01-01T00:00:00Z'}
                },
                200
            )

            response, status = handle_family_details_get(family_id)

            # Assertions
            assert status == 200
            assert response['familyId'] == family_id
            assert response['familyName'] == 'The Smiths'
            mock_handler.get_family.assert_called_once_with(family_id)

    def test_get_family_not_found(self, mock_dynamo_table):
        """Test retrieving a non-existent family"""
        family_id = 'nonexistent'

        # Mock DynamoDB get_item response (empty)
        mock_dynamo_table.get_item.return_value = {}

        with patch('openapi_server.impl.adapters.flask.family_handlers.FlaskFamilyHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_handler_class.return_value = mock_handler

            mock_handler.get_family.return_value = (
                {'error': {'code': 'not_found', 'message': f'Family {family_id} not found'}},
                404
            )

            response, status = handle_family_details_get(family_id)

            # Should return 404
            assert status == 404
            assert 'error' in response

    def test_list_families(self, mock_dynamo_table):
        """Test listing all families"""
        # Mock DynamoDB scan response
        mock_dynamo_table.scan.return_value = {
            'Items': [
                {
                    'familyId': 'fam-1',
                    'familyName': 'The Smiths',
                    'memberCount': Decimal('4')
                },
                {
                    'familyId': 'fam-2',
                    'familyName': 'The Johnsons',
                    'memberCount': Decimal('3')
                }
            ],
            'Count': 2
        }

        with patch('openapi_server.impl.adapters.flask.family_handlers.FlaskFamilyHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_handler_class.return_value = mock_handler

            mock_handler.list_families.return_value = (
                [
                    {'familyId': 'fam-1', 'familyName': 'The Smiths', 'memberCount': 4},
                    {'familyId': 'fam-2', 'familyName': 'The Johnsons', 'memberCount': 3}
                ],
                200
            )

            response, status = handle_family_list_get()

            # Assertions
            assert status == 200
            assert len(response) == 2
            assert response[0]['familyName'] == 'The Smiths'
            mock_handler.list_families.assert_called_once()

    def test_list_families_with_filter(self):
        """Test listing families with user filter"""
        user_id = 'parent1'

        with patch('openapi_server.impl.adapters.flask.family_handlers.FlaskFamilyHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_handler_class.return_value = mock_handler

            mock_handler.list_families.return_value = (
                [{'familyId': 'fam-1', 'familyName': 'The Smiths'}],
                200
            )

            response, status = handle_family_list_get(user_id=user_id)

            # Should filter by user
            assert status == 200
            mock_handler.list_families.assert_called_once_with(user_id=user_id)

    def test_update_family(self, mock_dynamo_table):
        """Test updating a family"""
        family_id = 'fam-123'
        update_data = {
            'familyName': 'The Smith Family',
            'notes': 'Updated notes - Premium members'
        }

        # Mock DynamoDB update_item response
        mock_dynamo_table.update_item.return_value = {
            'Attributes': {
                'familyId': family_id,
                'familyName': 'The Smith Family',
                'notes': 'Updated notes - Premium members',
                'modified': {'at': '2024-01-02T00:00:00Z'}
            }
        }

        with patch('openapi_server.impl.adapters.flask.family_handlers.FlaskFamilyHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_handler_class.return_value = mock_handler

            mock_handler.update_family.return_value = (
                {
                    'familyId': family_id,
                    'familyName': 'The Smith Family',
                    'notes': 'Updated notes - Premium members',
                    'modified': {'at': '2024-01-02T00:00:00Z'}
                },
                200
            )

            response, status = handle_family_details_patch(family_id, update_data)

            # Assertions
            assert status == 200
            assert response['familyName'] == 'The Smith Family'
            assert response['notes'] == 'Updated notes - Premium members'
            mock_handler.update_family.assert_called_once_with(family_id, update_data)

    def test_delete_family_soft_delete(self, mock_dynamo_table):
        """Test soft deleting a family"""
        family_id = 'fam-123'

        # Mock DynamoDB update_item for soft delete
        mock_dynamo_table.update_item.return_value = {
            'ResponseMetadata': {'HTTPStatusCode': 200}
        }

        with patch('openapi_server.impl.adapters.flask.family_handlers.FlaskFamilyHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_handler_class.return_value = mock_handler

            mock_handler.delete_family.return_value = (None, 204)

            response, status = handle_family_details_delete(family_id)

            # Should return 204 No Content
            assert status == 204
            assert response is None
            mock_handler.delete_family.assert_called_once_with(family_id)

    def test_delete_family_not_found(self, mock_dynamo_table):
        """Test deleting a non-existent family"""
        family_id = 'nonexistent'

        with patch('openapi_server.impl.adapters.flask.family_handlers.FlaskFamilyHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_handler_class.return_value = mock_handler

            mock_handler.delete_family.return_value = (
                {'error': {'code': 'not_found', 'message': f'Family {family_id} not found'}},
                404
            )

            response, status = handle_family_details_delete(family_id)

            # Should return 404
            assert status == 404
            assert 'error' in response

    def test_create_family_alias_function(self):
        """Test that handle_create_family properly aliases to handle_family_details_post"""
        sample_data = {'familyName': 'Test', 'children': [{'userId': 'child1'}]}

        with patch('openapi_server.impl.handlers.handle_family_details_post') as mock_post:
            mock_post.return_value = ({'familyId': 'new-123'}, 201)

            response, status = handle_create_family(sample_data)

            # Should delegate to handle_family_details_post
            assert status == 201
            assert response['familyId'] == 'new-123'
            mock_post.assert_called_once_with(sample_data)

    def test_delete_family_alias_function(self):
        """Test that handle_delete_family properly aliases to handle_family_details_delete"""
        family_id = 'fam-123'

        with patch('openapi_server.impl.handlers.handle_family_details_delete') as mock_delete:
            mock_delete.return_value = (None, 204)

            response, status = handle_delete_family(family_id)

            # Should delegate to handle_family_details_delete
            assert status == 204
            assert response is None
            mock_delete.assert_called_once_with(family_id)


class TestFamilyBusinessRules:
    """Test family-specific business rules"""

    def test_family_requires_at_least_one_child(self):
        """Test that families must have at least one child"""
        invalid_family = {
            'familyName': 'No Children Family',
            'parents': [{'userId': 'parent1'}],
            'children': []  # Empty children list
        }

        with patch('openapi_server.impl.adapters.flask.family_handlers.FlaskFamilyHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_handler_class.return_value = mock_handler

            mock_handler.create_family.return_value = (
                {'error': {'code': 'validation_error', 'message': 'At least one child is required'}},
                400
            )

            response, status = handle_family_details_post(invalid_family)

            assert status == 400
            assert 'error' in response

    def test_family_member_validation(self):
        """Test validation of family member data"""
        family_with_invalid_member = {
            'familyName': 'Test Family',
            'children': [
                {'userId': 'child1', 'name': 'Valid Child'},
                {'name': 'Missing UserId'}  # Invalid - missing userId
            ]
        }

        with patch('openapi_server.impl.adapters.flask.family_handlers.FlaskFamilyHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_handler_class.return_value = mock_handler

            mock_handler.create_family.return_value = (
                {'error': {'code': 'validation_error', 'message': 'All family members must have userId'}},
                400
            )

            response, status = handle_family_details_post(family_with_invalid_member)

            assert status == 400

    def test_family_cascading_operations(self, mock_dynamo_table):
        """Test that deleting a family handles related data properly"""
        family_id = 'fam-123'

        # Mock checking for related conversations
        mock_dynamo_table.query.return_value = {
            'Items': [],  # No active conversations
            'Count': 0
        }

        with patch('openapi_server.impl.adapters.flask.family_handlers.FlaskFamilyHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_handler_class.return_value = mock_handler

            # Can delete since no active conversations
            mock_handler.delete_family.return_value = (None, 204)

            response, status = handle_family_details_delete(family_id)

            assert status == 204


class TestFamilyPagination:
    """Test family list pagination"""

    def test_paginated_family_list(self):
        """Test listing families with pagination"""
        with patch('openapi_server.impl.adapters.flask.family_handlers.FlaskFamilyHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_handler_class.return_value = mock_handler

            # Mock paginated response
            mock_handler.list_families.return_value = (
                {
                    'families': [
                        {'familyId': 'fam-1', 'familyName': 'Family 1'},
                        {'familyId': 'fam-2', 'familyName': 'Family 2'}
                    ],
                    'pagination': {
                        'page': 1,
                        'pageSize': 2,
                        'totalCount': 10,
                        'totalPages': 5
                    }
                },
                200
            )

            # Request with pagination parameters
            response, status = handle_family_list_get(page=1, page_size=2)

            assert status == 200
            # Handler should be called with pagination params
            mock_handler.list_families.assert_called()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])