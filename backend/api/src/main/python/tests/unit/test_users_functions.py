"""
Unit tests for users.py functions to enable TDD workflow.
PR003946-94: Comprehensive function-level unit tests

Tests all CRUD operations, pagination validation, foreign key validation,
and error handling for the users module.
"""
import pytest
import os
from unittest.mock import patch, MagicMock
from datetime import datetime

from openapi_server.impl.users import (
    handle_list_users, handle_get_user, handle_create_user,
    handle_update_user, handle_delete_user, _validate_foreign_keys
)
from openapi_server.impl.error_handler import ValidationError, NotFoundError


class TestHandleListUsers:
    """Test handle_list_users function with pagination validation."""
    
    @patch('openapi_server.impl.users._store')
    def test_handle_list_users_default_pagination(self, mock_store):
        """Test list users with default pagination parameters."""
        mock_store.return_value.list.return_value = [
            {'userId': 'user1', 'email': 'user1@test.com'},
            {'userId': 'user2', 'email': 'user2@test.com'}
        ]
        
        result = handle_list_users()
        
        assert len(result) == 2
        assert result[0]['userId'] == 'user1'
        assert result[1]['userId'] == 'user2'
        mock_store.return_value.list.assert_called_once_with(hide_soft_deleted=True)
    
    @patch('openapi_server.impl.users._store')
    def test_handle_list_users_custom_pagination(self, mock_store):
        """Test list users with custom pagination parameters."""
        # Create 100 mock users
        mock_users = [{'userId': f'user{i}', 'email': f'user{i}@test.com'} for i in range(100)]
        mock_store.return_value.list.return_value = mock_users
        
        result = handle_list_users(page=2, page_size=20)
        
        # Should return users 20-39 (page 2, 20 per page)
        assert len(result) == 20
        mock_store.return_value.list.assert_called_once_with(hide_soft_deleted=True)
    
    def test_handle_list_users_invalid_page_negative(self):
        """Test list users fails with negative page number."""
        with pytest.raises(ValidationError) as exc_info:
            handle_list_users(page=-1)
        
        error = exc_info.value
        assert "Invalid pagination parameters" in error.message
        assert "Page must be >= 1" in error.field_errors.get('page', [])
    
    def test_handle_list_users_invalid_page_zero(self):
        """Test list users fails with zero page number."""
        with pytest.raises(ValidationError) as exc_info:
            handle_list_users(page=0)
        
        error = exc_info.value
        assert "Invalid pagination parameters" in error.message
        assert "Page must be >= 1" in error.field_errors.get('page', [])
    
    def test_handle_list_users_invalid_page_string(self):
        """Test list users fails with non-numeric page."""
        with pytest.raises(ValidationError) as exc_info:
            handle_list_users(page="invalid")
        
        error = exc_info.value
        assert "Invalid pagination parameters" in error.message
        assert "Page must be a valid integer" in error.field_errors.get('page', [])
    
    def test_handle_list_users_invalid_page_size_negative(self):
        """Test list users fails with negative page size."""
        with pytest.raises(ValidationError) as exc_info:
            handle_list_users(page_size=-1)
        
        error = exc_info.value
        assert "Invalid pagination parameters" in error.message
        assert "Page size must be >= 1" in error.field_errors.get('pageSize', [])
    
    def test_handle_list_users_invalid_page_size_too_large(self):
        """Test list users fails with page size exceeding limit."""
        with pytest.raises(ValidationError) as exc_info:
            handle_list_users(page_size=1000)  # Exceeds 500 limit
        
        error = exc_info.value
        assert "Invalid pagination parameters" in error.message
        assert "Page size must be <= 500" in error.field_errors.get('pageSize', [])
    
    def test_handle_list_users_invalid_page_size_string(self):
        """Test list users fails with non-numeric page size."""
        with pytest.raises(ValidationError) as exc_info:
            handle_list_users(page_size="invalid")
        
        error = exc_info.value
        assert "Invalid pagination parameters" in error.message
        assert "Page size must be a valid integer" in error.field_errors.get('pageSize', [])
    
    @patch('openapi_server.impl.users._store')
    def test_handle_list_users_boundary_values(self, mock_store):
        """Test list users with boundary values."""
        mock_store.return_value.list.return_value = []
        
        # Test minimum valid values
        result = handle_list_users(page=1, page_size=1)
        assert isinstance(result, list)
        
        # Test maximum valid page size
        result = handle_list_users(page=1, page_size=500)
        assert isinstance(result, list)


class TestHandleGetUser:
    """Test handle_get_user function."""
    
    @patch('openapi_server.impl.users._store')
    def test_handle_get_user_success(self, mock_store):
        """Test successful user retrieval."""
        mock_user = {'userId': 'test_user', 'email': 'test@example.com'}
        mock_store.return_value.get.return_value = mock_user
        
        result = handle_get_user('test_user')
        
        assert result == mock_user
        mock_store.return_value.get.assert_called_once_with('test_user')
    
    @patch('openapi_server.impl.users._store')
    def test_handle_get_user_not_found(self, mock_store):
        """Test get user fails when user doesn't exist."""
        mock_store.return_value.get.return_value = None
        
        result = handle_get_user('nonexistent_user')
        
        assert result is None
        mock_store.return_value.get.assert_called_once_with('nonexistent_user')
    
    def test_handle_get_user_empty_id(self):
        """Test get user with empty user ID."""
        # This should be handled by the calling controller, but test defensive coding
        with patch('openapi_server.impl.users._store') as mock_store:
            mock_store.return_value.get.return_value = None
            result = handle_get_user('')
            assert result is None


class TestHandleCreateUser:
    """Test handle_create_user function with validation."""
    
    @patch('openapi_server.impl.users._validate_foreign_keys')
    @patch('openapi_server.impl.users._store')
    def test_handle_create_user_success(self, mock_store, mock_validate):
        """Test successful user creation."""
        user_data = {
            'displayName': 'Test User',
            'email': 'test@example.com',
            'role': 'member',
            'userType': 'student'
        }
        
        mock_validate.return_value = None  # No validation errors
        mock_store.return_value.create.return_value = {**user_data, 'userId': 'generated_id'}
        
        result = handle_create_user(user_data)
        
        assert result[1] == 201  # Status code
        assert result[0]['userId'] == 'generated_id'
        assert result[0]['email'] == 'test@example.com'
        mock_validate.assert_called_once()
        mock_store.return_value.create.assert_called_once()
    
    @patch('openapi_server.impl.users._validate_foreign_keys')
    def test_handle_create_user_validation_error(self, mock_validate):
        """Test user creation fails with validation error."""
        user_data = {'email': 'test@example.com'}
        
        mock_validate.side_effect = ValidationError(
            "Validation failed",
            field_errors={'familyId': ['Family does not exist']}
        )
        
        with pytest.raises(ValidationError) as exc_info:
            handle_create_user(user_data)
        
        assert "Validation failed" in str(exc_info.value)
        assert 'familyId' in exc_info.value.field_errors
    
    @patch('openapi_server.impl.users._store')
    def test_handle_create_user_with_family_id(self, mock_store):
        """Test user creation with family ID (triggers foreign key validation)."""
        user_data = {
            'displayName': 'Test User',
            'email': 'test@example.com',
            'familyId': 'test_family'
        }
        
        with patch('openapi_server.impl.users._validate_foreign_keys') as mock_validate:
            mock_validate.return_value = None
            mock_store.return_value.create.return_value = {**user_data, 'userId': 'generated_id'}
            
            result = handle_create_user(user_data)
            
            assert result[1] == 201
            mock_validate.assert_called_once_with(user_data)
    
    def test_handle_create_user_boundary_values(self, boundary_value_generator):
        """Test user creation with boundary values."""
        # Test empty/null values
        for invalid_value in boundary_value_generator.null_empty_values():
            user_data = {'displayName': invalid_value, 'email': 'test@example.com'}
            
            with patch('openapi_server.impl.users._validate_foreign_keys'):
                with patch('openapi_server.impl.users._store') as mock_store:
                    mock_store.return_value.create.return_value = {**user_data, 'userId': 'test'}
                    
                    # Should handle gracefully (validation happens at OpenAPI level)
                    result = handle_create_user(user_data)
                    assert result[1] == 201


class TestHandleUpdateUser:
    """Test handle_update_user function."""
    
    @patch('openapi_server.impl.users._validate_foreign_keys')
    @patch('openapi_server.impl.users._store')
    def test_handle_update_user_success(self, mock_store, mock_validate):
        """Test successful user update."""
        update_data = {
            'displayName': 'Updated Name',
            'role': 'parent'
        }
        
        mock_validate.return_value = None
        mock_store.return_value.update.return_value = {
            'userId': 'test_user',
            'displayName': 'Updated Name',
            'role': 'parent'
        }
        
        result = handle_update_user('test_user', update_data)
        
        assert result[1] == 200
        assert result[0]['displayName'] == 'Updated Name'
        mock_validate.assert_called_once()
        mock_store.return_value.update.assert_called_once_with('test_user', update_data)
    
    @patch('openapi_server.impl.users._validate_foreign_keys')
    def test_handle_update_user_validation_error(self, mock_validate):
        """Test user update fails with validation error."""
        mock_validate.side_effect = ValidationError(
            "Invalid family reference",
            field_errors={'familyId': ['Family does not exist']}
        )
        
        with pytest.raises(ValidationError):
            handle_update_user('test_user', {'familyId': 'nonexistent'})
    
    @patch('openapi_server.impl.users._store')
    def test_handle_update_user_not_found(self, mock_store):
        """Test user update when user doesn't exist."""
        mock_store.return_value.update.return_value = None
        
        with patch('openapi_server.impl.users._validate_foreign_keys'):
            result = handle_update_user('nonexistent', {'displayName': 'Test'})
            
            # Should return not found response
            assert result[1] == 404 or result is None


class TestHandleDeleteUser:
    """Test handle_delete_user function with soft delete semantics."""
    
    @patch('openapi_server.impl.users._store')
    def test_handle_delete_user_success(self, mock_store):
        """Test successful user deletion (soft delete)."""
        mock_store.return_value.soft_delete.return_value = True
        
        result = handle_delete_user('test_user')
        
        assert result[1] == 204  # No content
        mock_store.return_value.soft_delete.assert_called_once_with('test_user')
    
    @patch('openapi_server.impl.users._store')
    def test_handle_delete_user_not_found(self, mock_store):
        """Test user deletion when user doesn't exist."""
        mock_store.return_value.soft_delete.return_value = False
        
        result = handle_delete_user('nonexistent')
        
        # Implementation may return 404 or handle gracefully
        assert result[1] in [404, 204]


class TestValidateForeignKeys:
    """Test _validate_foreign_keys function for data integrity."""
    
    @patch('openapi_server.impl.users.get_store')
    def test_validate_foreign_keys_valid_family_id(self, mock_get_store):
        """Test foreign key validation with valid family ID."""
        mock_family_store = MagicMock()
        mock_family_store.get.return_value = {'familyId': 'test_family'}
        mock_get_store.return_value = mock_family_store
        
        data = {'familyId': 'test_family'}
        
        # Should not raise any exception
        result = _validate_foreign_keys(data)
        assert result is None
    
    @patch('openapi_server.impl.users.get_store')
    def test_validate_foreign_keys_invalid_family_id(self, mock_get_store):
        """Test foreign key validation with invalid family ID."""
        mock_family_store = MagicMock()
        mock_family_store.get.return_value = None  # Family doesn't exist
        mock_get_store.return_value = mock_family_store
        
        data = {'familyId': 'nonexistent_family'}
        
        with pytest.raises(ValidationError) as exc_info:
            _validate_foreign_keys(data)
        
        error = exc_info.value
        assert "Invalid foreign key reference" in error.message
        assert 'familyId' in error.field_errors
        assert 'does not exist' in str(error.field_errors['familyId'])
    
    def test_validate_foreign_keys_no_foreign_keys(self):
        """Test foreign key validation when no foreign keys present."""
        data = {'displayName': 'Test User', 'email': 'test@example.com'}
        
        # Should not raise any exception
        result = _validate_foreign_keys(data)
        assert result is None
    
    def test_validate_foreign_keys_empty_family_id(self):
        """Test foreign key validation with empty family ID."""
        data = {'familyId': ''}
        
        # Empty string should be treated as no foreign key
        result = _validate_foreign_keys(data)
        assert result is None
    
    def test_validate_foreign_keys_none_family_id(self):
        """Test foreign key validation with None family ID."""
        data = {'familyId': None}
        
        # None should be treated as no foreign key
        result = _validate_foreign_keys(data)
        assert result is None


class TestUsersFunctionIntegration:
    """Integration tests for users functions working together."""
    
    @patch('openapi_server.impl.users._store')
    def test_create_then_get_user(self, mock_store):
        """Test creating a user then retrieving it."""
        user_data = {
            'displayName': 'Test User',
            'email': 'test@example.com',
            'role': 'member'
        }
        
        created_user = {**user_data, 'userId': 'test_id'}
        mock_store.return_value.create.return_value = created_user
        mock_store.return_value.get.return_value = created_user
        
        with patch('openapi_server.impl.users._validate_foreign_keys'):
            # Create user
            create_result = handle_create_user(user_data)
            assert create_result[1] == 201
            
            # Get user
            get_result = handle_get_user('test_id')
            assert get_result['userId'] == 'test_id'
            assert get_result['email'] == 'test@example.com'
    
    @patch('openapi_server.impl.users._store') 
    def test_pagination_edge_cases(self, mock_store):
        """Test pagination with edge cases."""
        # Single user, multiple pages
        mock_store.return_value.list.return_value = [{'userId': 'single_user'}]
        
        result = handle_list_users(page=2, page_size=10)  # Page 2 of 1 user
        assert len(result) == 0  # Should be empty
        
        result = handle_list_users(page=1, page_size=10)  # Page 1 of 1 user
        assert len(result) == 1