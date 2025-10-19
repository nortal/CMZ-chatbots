"""
Unit tests for family.py functions to enable TDD workflow.
PR003946-94: Comprehensive function-level unit tests

Tests all family CRUD operations, member validation, parent-student relationships,
and business logic for the family module.

FIXED: Updated to handle tuple return types (response, status_code) from API handlers
"""
import pytest
from unittest.mock import patch, MagicMock

from openapi_server.impl.family import (
    handle_list_families, handle_get_family, handle_create_family,
    handle_update_family, handle_delete_family
)


class TestHandleListFamilies:
    """Test handle_list_families function."""

    @patch('openapi_server.impl.family.handle_family_list_get')
    def test_handle_list_families_success(self, mock_list_get):
        """Test successful family listing."""
        mock_families = [
            {'familyId': 'family1', 'familyName': 'Family One'},
            {'familyId': 'family2', 'familyName': 'Family Two'}
        ]
        mock_list_get.return_value = (mock_families, 200)

        result, status = handle_list_families()

        assert len(result) == 2
        assert result[0]['familyId'] == 'family1'
        assert result[1]['familyId'] == 'family2'
        assert status == 200
        mock_list_get.assert_called_once()

    @patch('openapi_server.impl.family.handle_family_list_get')
    def test_handle_list_families_empty(self, mock_list_get):
        """Test family listing when no families exist."""
        mock_list_get.return_value = ([], 200)

        result, status = handle_list_families()

        assert result == []
        assert status == 200
        mock_list_get.assert_called_once()


class TestHandleGetFamily:
    """Test handle_get_family function."""

    @patch('openapi_server.impl.family.handle_family_get')
    def test_handle_get_family_success(self, mock_get):
        """Test successful family retrieval."""
        mock_family = {
            'familyId': 'test_family',
            'familyName': 'Test Family',
            'parents': ['parent1'],
            'students': ['student1', 'student2']
        }
        mock_get.return_value = (mock_family, 200)

        result, status = handle_get_family('test_family')

        assert result == mock_family
        assert status == 200
        mock_get.assert_called_once_with('test_family')

    @patch('openapi_server.impl.family.handle_family_get')
    def test_handle_get_family_not_found(self, mock_get):
        """Test get family when family doesn't exist."""
        error_response = {'error': 'Family not found', 'code': 'NOT_FOUND'}
        mock_get.return_value = (error_response, 404)

        result, status = handle_get_family('nonexistent_family')

        assert status == 404
        assert 'error' in result
        mock_get.assert_called_once_with('nonexistent_family')


class TestHandleCreateFamily:
    """Test handle_create_family function with member validation."""

    @patch('openapi_server.impl.family.handle_family_post')
    def test_handle_create_family_success(self, mock_post):
        """Test successful family creation."""
        family_data = {
            'familyName': 'New Family',
            'parents': ['parent1'],
            'students': ['student1', 'student2']
        }

        created_family = {**family_data, 'familyId': 'generated_id'}
        mock_post.return_value = (created_family, 201)

        result, status = handle_create_family(family_data)

        assert status == 201
        assert result['familyId'] == 'generated_id'
        assert result['familyName'] == 'New Family'
        mock_post.assert_called_once_with(family_data)

    @patch('openapi_server.impl.family.handle_family_post')
    def test_handle_create_family_validation_error(self, mock_post):
        """Test family creation fails with validation error."""
        family_data = {
            'familyName': 'Invalid Family',
            'parents': ['nonexistent_parent']
        }

        error_response = {
            'error': 'Invalid family members',
            'code': 'VALIDATION_ERROR',
            'field_errors': {'parents': ['Parent does not exist']}
        }
        mock_post.return_value = (error_response, 400)

        result, status = handle_create_family(family_data)

        assert status == 400
        assert 'error' in result
        assert result['error'] == 'Invalid family members'

    @patch('openapi_server.impl.family.handle_family_post')
    def test_handle_create_family_minimal_data(self, mock_post):
        """Test family creation with minimal required data."""
        family_data = {'familyName': 'Minimal Family'}

        created_family = {**family_data, 'familyId': 'minimal_id'}
        mock_post.return_value = (created_family, 201)

        result, status = handle_create_family(family_data)

        assert status == 201
        assert result['familyName'] == 'Minimal Family'


class TestHandleUpdateFamily:
    """Test handle_update_family function."""

    @patch('openapi_server.impl.family.handle_family_put')
    def test_handle_update_family_success(self, mock_put):
        """Test successful family update."""
        update_data = {
            'familyName': 'Updated Family Name',
            'students': ['student1', 'student2', 'student3']
        }

        updated_family = {
            'familyId': 'test_family',
            'familyName': 'Updated Family Name',
            'students': ['student1', 'student2', 'student3']
        }
        mock_put.return_value = (updated_family, 200)

        result, status = handle_update_family('test_family', update_data)

        assert status == 200
        assert result['familyName'] == 'Updated Family Name'
        assert len(result['students']) == 3
        mock_put.assert_called_once_with('test_family', update_data)

    @patch('openapi_server.impl.family.handle_family_put')
    def test_handle_update_family_validation_error(self, mock_put):
        """Test family update fails with validation error."""
        update_data = {'students': ['nonexistent']}

        error_response = {
            'error': 'Invalid student reference',
            'code': 'VALIDATION_ERROR',
            'field_errors': {'students': ['Student does not exist']}
        }
        mock_put.return_value = (error_response, 400)

        result, status = handle_update_family('test_family', update_data)

        assert status == 400
        assert 'error' in result


class TestHandleDeleteFamily:
    """Test handle_delete_family function with soft delete semantics."""

    @patch('openapi_server.impl.family.handle_family_delete')
    def test_handle_delete_family_success(self, mock_delete):
        """Test successful family deletion (soft delete)."""
        mock_delete.return_value = (None, 204)

        result, status = handle_delete_family('test_family')

        assert status == 204
        assert result is None
        mock_delete.assert_called_once_with('test_family')

    @patch('openapi_server.impl.family.handle_family_delete')
    def test_handle_delete_family_not_found(self, mock_delete):
        """Test family deletion when family doesn't exist."""
        error_response = {'error': 'Family not found'}
        mock_delete.return_value = (error_response, 404)

        result, status = handle_delete_family('nonexistent')

        assert status == 404
        assert 'error' in result


class TestValidateFamilyMembers:
    """Test family member validation."""

    @patch('openapi_server.impl.family._get_existing_user_ids')
    def test_validate_family_members_success(self, mock_get_users):
        """Test validation passes with valid members."""
        mock_get_users.return_value = ['parent1', 'student1', 'student2']

        from openapi_server.impl.family import _validate_family_members

        family_data = {
            'parents': ['parent1'],
            'students': ['student1', 'student2']
        }

        # Should not raise any exception
        _validate_family_members(family_data)

    @patch('openapi_server.impl.family._get_existing_user_ids')
    def test_validate_family_members_invalid_parent(self, mock_get_users):
        """Test validation fails with invalid parent."""
        mock_get_users.return_value = ['student1', 'student2']

        from openapi_server.impl.family import _validate_family_members
        from openapi_server.impl.error_handler import ValidationError

        family_data = {
            'parents': ['invalid_parent'],
            'students': ['student1', 'student2']
        }

        with pytest.raises(ValidationError):
            _validate_family_members(family_data)

    @patch('openapi_server.impl.family._get_existing_user_ids')
    def test_validate_family_members_invalid_student(self, mock_get_users):
        """Test validation fails with invalid student."""
        mock_get_users.return_value = ['parent1']

        from openapi_server.impl.family import _validate_family_members
        from openapi_server.impl.error_handler import ValidationError

        family_data = {
            'parents': ['parent1'],
            'students': ['invalid_student']
        }

        with pytest.raises(ValidationError):
            _validate_family_members(family_data)


class TestGetExistingUserIds:
    """Test get existing user IDs function."""

    @patch('openapi_server.impl.family._user_store')
    def test_get_existing_user_ids_success(self, mock_user_store):
        """Test retrieving existing user IDs."""
        mock_users = [
            {'userId': 'user1'},
            {'userId': 'user2'},
            {'userId': 'user3'}
        ]
        mock_user_store.return_value.list.return_value = mock_users

        from openapi_server.impl.family import _get_existing_user_ids

        result = _get_existing_user_ids(['user1', 'user2', 'user4'])

        assert 'user1' in result
        assert 'user2' in result
        assert 'user4' not in result

    @patch('openapi_server.impl.family._user_store')
    def test_get_existing_user_ids_empty(self, mock_user_store):
        """Test when no users exist."""
        mock_user_store.return_value.list.return_value = []

        from openapi_server.impl.family import _get_existing_user_ids

        result = _get_existing_user_ids(['user1', 'user2'])

        assert len(result) == 0


class TestFamilyFunctionIntegration:
    """Test integration between family functions."""

    @patch('openapi_server.impl.family.handle_family_post')
    @patch('openapi_server.impl.family.handle_family_get')
    def test_create_then_get_family(self, mock_get, mock_post):
        """Test creating a family then retrieving it."""
        family_data = {'familyName': 'Integration Test Family'}

        created_family = {
            'familyId': 'test_id',
            'familyName': 'Integration Test Family'
        }
        mock_post.return_value = (created_family, 201)

        # Create family
        create_result, create_status = handle_create_family(family_data)
        assert create_status == 201

        # Get the created family
        mock_get.return_value = (created_family, 200)
        get_result, get_status = handle_get_family('test_id')

        assert get_status == 200
        assert get_result['familyId'] == 'test_id'
        assert get_result['familyName'] == 'Integration Test Family'

    @patch('openapi_server.impl.family.handle_family_post')
    @patch('openapi_server.impl.family.handle_family_put')
    def test_create_update_family_workflow(self, mock_put, mock_post):
        """Test complete family creation and update workflow."""
        # Create family
        create_data = {'familyName': 'Original Name'}
        created = {'familyId': 'family123', 'familyName': 'Original Name'}
        mock_post.return_value = (created, 201)

        result1, status1 = handle_create_family(create_data)
        assert status1 == 201

        # Update family
        update_data = {'familyName': 'Updated Name'}
        updated = {'familyId': 'family123', 'familyName': 'Updated Name'}
        mock_put.return_value = (updated, 200)

        result2, status2 = handle_update_family('family123', update_data)
        assert status2 == 200
        assert result2['familyName'] == 'Updated Name'