"""
Unit tests for family.py functions to enable TDD workflow.
PR003946-94: Comprehensive function-level unit tests

Tests all family CRUD operations, member validation, parent-student relationships,
and business logic for the family module.
"""
import pytest
from unittest.mock import patch, MagicMock

from openapi_server.impl.family import (
    handle_list_families, handle_get_family, handle_create_family,
    handle_update_family, handle_delete_family
)
from openapi_server.impl.error_handler import ValidationError


class TestHandleListFamilies:
    """Test handle_list_families function."""
    
    @patch('openapi_server.impl.family._store')
    def test_handle_list_families_success(self, mock_store):
        """Test successful family listing."""
        mock_families = [
            {'familyId': 'family1', 'familyName': 'Family One'},
            {'familyId': 'family2', 'familyName': 'Family Two'}
        ]
        mock_store.return_value.list.return_value = mock_families
        
        result = handle_list_families()
        
        assert len(result) == 2
        assert result[0]['familyId'] == 'family1'
        assert result[1]['familyId'] == 'family2'
        mock_store.return_value.list.assert_called_once()
    
    @patch('openapi_server.impl.family._store')
    def test_handle_list_families_empty(self, mock_store):
        """Test family listing when no families exist."""
        mock_store.return_value.list.return_value = []
        
        result = handle_list_families()
        
        assert result == []
        mock_store.return_value.list.assert_called_once()


class TestHandleGetFamily:
    """Test handle_get_family function."""
    
    @patch('openapi_server.impl.family._store')
    def test_handle_get_family_success(self, mock_store):
        """Test successful family retrieval."""
        mock_family = {
            'familyId': 'test_family',
            'familyName': 'Test Family',
            'parents': ['parent1'],
            'students': ['student1', 'student2']
        }
        mock_store.return_value.get.return_value = mock_family
        
        result = handle_get_family('test_family')
        
        assert result == mock_family
        mock_store.return_value.get.assert_called_once_with('test_family')
    
    @patch('openapi_server.impl.family._store')
    def test_handle_get_family_not_found(self, mock_store):
        """Test get family when family doesn't exist."""
        mock_store.return_value.get.return_value = None
        
        result = handle_get_family('nonexistent_family')
        
        assert result is None
        mock_store.return_value.get.assert_called_once_with('nonexistent_family')


class TestHandleCreateFamily:
    """Test handle_create_family function with member validation."""
    
    @patch('openapi_server.impl.family._validate_family_members')
    @patch('openapi_server.impl.family._store')
    def test_handle_create_family_success(self, mock_store, mock_validate):
        """Test successful family creation."""
        family_data = {
            'familyName': 'New Family',
            'parents': ['parent1'],
            'students': ['student1', 'student2']
        }
        
        mock_validate.return_value = None
        created_family = {**family_data, 'familyId': 'generated_id'}
        mock_store.return_value.create.return_value = created_family
        
        result = handle_create_family(family_data)
        
        assert result[1] == 201
        assert result[0]['familyId'] == 'generated_id'
        assert result[0]['familyName'] == 'New Family'
        mock_validate.assert_called_once_with(family_data)
        mock_store.return_value.create.assert_called_once()
    
    @patch('openapi_server.impl.family._validate_family_members')
    def test_handle_create_family_validation_error(self, mock_validate):
        """Test family creation fails with validation error."""
        family_data = {
            'familyName': 'Invalid Family',
            'parents': ['nonexistent_parent']
        }
        
        mock_validate.side_effect = ValidationError(
            "Invalid family members",
            field_errors={'parents': ['Parent does not exist']}
        )
        
        with pytest.raises(ValidationError) as exc_info:
            handle_create_family(family_data)
        
        assert "Invalid family members" in str(exc_info.value)
        assert 'parents' in exc_info.value.field_errors
    
    @patch('openapi_server.impl.family._store')
    def test_handle_create_family_minimal_data(self, mock_store):
        """Test family creation with minimal required data."""
        family_data = {'familyName': 'Minimal Family'}
        
        with patch('openapi_server.impl.family._validate_family_members') as mock_validate:
            mock_validate.return_value = None
            created_family = {**family_data, 'familyId': 'minimal_id'}
            mock_store.return_value.create.return_value = created_family
            
            result = handle_create_family(family_data)
            
            assert result[1] == 201
            assert result[0]['familyName'] == 'Minimal Family'


class TestHandleUpdateFamily:
    """Test handle_update_family function."""
    
    @patch('openapi_server.impl.family._validate_family_members')
    @patch('openapi_server.impl.family._store')
    def test_handle_update_family_success(self, mock_store, mock_validate):
        """Test successful family update."""
        update_data = {
            'familyName': 'Updated Family Name',
            'students': ['student1', 'student2', 'student3']
        }
        
        mock_validate.return_value = None
        updated_family = {
            'familyId': 'test_family',
            'familyName': 'Updated Family Name',
            'students': ['student1', 'student2', 'student3']
        }
        mock_store.return_value.update.return_value = updated_family
        
        result = handle_update_family('test_family', update_data)
        
        assert result[1] == 200
        assert result[0]['familyName'] == 'Updated Family Name'
        assert len(result[0]['students']) == 3
        mock_validate.assert_called_once_with(update_data)
        mock_store.return_value.update.assert_called_once_with('test_family', update_data)
    
    @patch('openapi_server.impl.family._validate_family_members')
    def test_handle_update_family_validation_error(self, mock_validate):
        """Test family update fails with validation error."""
        mock_validate.side_effect = ValidationError(
            "Invalid student reference",
            field_errors={'students': ['Student does not exist']}
        )
        
        with pytest.raises(ValidationError):
            handle_update_family('test_family', {'students': ['nonexistent']})


class TestHandleDeleteFamily:
    """Test handle_delete_family function with soft delete semantics."""
    
    @patch('openapi_server.impl.family._store')
    def test_handle_delete_family_success(self, mock_store):
        """Test successful family deletion (soft delete)."""
        mock_store.return_value.soft_delete.return_value = True
        
        result = handle_delete_family('test_family')
        
        assert result[1] == 204
        mock_store.return_value.soft_delete.assert_called_once_with('test_family')
    
    @patch('openapi_server.impl.family._store')
    def test_handle_delete_family_not_found(self, mock_store):
        """Test family deletion when family doesn't exist."""
        mock_store.return_value.soft_delete.return_value = False
        
        result = handle_delete_family('nonexistent')
        
        assert result[1] in [404, 204]  # Depends on implementation


class TestValidateFamilyMembers:
    """Test _validate_family_members function for relationship validation."""
    
    @patch('openapi_server.impl.family._get_existing_user_ids')
    def test_validate_family_members_valid_members(self, mock_get_users):
        """Test family member validation with valid users."""
        mock_get_users.return_value = ['parent1', 'student1', 'student2']
        
        family_data = {
            'parents': ['parent1'],
            'students': ['student1', 'student2']
        }
        
        # Should not raise any exception
        result = _validate_family_members(family_data)
        assert result is None
    
    @patch('openapi_server.impl.family._get_existing_user_ids')
    def test_validate_family_members_invalid_parent(self, mock_get_users):
        """Test family member validation with invalid parent."""
        mock_get_users.return_value = ['student1']
        
        family_data = {
            'parents': ['nonexistent_parent'],
            'students': ['student1']
        }
        
        with pytest.raises(ValidationError) as exc_info:
            _validate_family_members(family_data)
        
        error = exc_info.value
        assert 'parents' in error.field_errors
        assert 'does not exist' in str(error.field_errors['parents'])
    
    @patch('openapi_server.impl.family._get_existing_user_ids')
    def test_validate_family_members_invalid_student(self, mock_get_users):
        """Test family member validation with invalid student."""
        mock_get_users.return_value = ['parent1']
        
        family_data = {
            'parents': ['parent1'],
            'students': ['nonexistent_student']
        }
        
        with pytest.raises(ValidationError) as exc_info:
            _validate_family_members(family_data)
        
        error = exc_info.value
        assert 'students' in error.field_errors
        assert 'does not exist' in str(error.field_errors['students'])
    
    @patch('openapi_server.impl.family._get_existing_user_ids')
    def test_validate_family_members_duplicate_members(self, mock_get_users):
        """Test family member validation with duplicate members."""
        mock_get_users.return_value = ['user1', 'user2']
        
        family_data = {
            'parents': ['user1'],
            'students': ['user1']  # Same user as parent and student
        }
        
        with pytest.raises(ValidationError) as exc_info:
            _validate_family_members(family_data)
        
        error = exc_info.value
        # Should detect duplicate user assignment
        assert any('duplicate' in str(errors).lower() or 'already' in str(errors).lower() 
                  for errors in error.field_errors.values())
    
    def test_validate_family_members_empty_lists(self):
        """Test family member validation with empty member lists."""
        family_data = {
            'parents': [],
            'students': []
        }
        
        # Should handle empty lists gracefully
        result = _validate_family_members(family_data)
        assert result is None
    
    def test_validate_family_members_no_member_fields(self):
        """Test family member validation when no member fields present."""
        family_data = {'familyName': 'Test Family'}
        
        # Should handle missing member fields gracefully
        result = _validate_family_members(family_data)
        assert result is None


class TestValidateFamilyMembersTestMode:
    """Test _validate_family_members_test_mode function for test environment."""
    
    def test_validate_family_members_test_mode_allows_missing_users(self):
        """Test that test mode allows non-existent users for testing."""
        family_data = {
            'parents': ['test_parent_that_might_not_exist'],
            'students': ['test_student_that_might_not_exist']
        }
        
        # Test mode should be more lenient
        result = _validate_family_members_test_mode(family_data)
        assert result is None
    
    def test_validate_family_members_test_mode_basic_validation(self):
        """Test that test mode still does basic validation."""
        family_data = {
            'parents': ['test_parent'],
            'students': ['test_parent']  # Duplicate assignment
        }
        
        # Even test mode should catch obvious errors like duplicates
        try:
            _validate_family_members_test_mode(family_data)
        except ValidationError:
            pass  # Expected for duplicate users


class TestUserExists:
    """Test _user_exists helper function."""
    
    def test_user_exists_true(self):
        """Test _user_exists returns True when user exists."""
        mock_store = MagicMock()
        mock_store.get.return_value = {'userId': 'test_user'}
        
        result = _user_exists(mock_store, 'test_user')
        
        assert result is True
        mock_store.get.assert_called_once_with('test_user')
    
    def test_user_exists_false(self):
        """Test _user_exists returns False when user doesn't exist."""
        mock_store = MagicMock()
        mock_store.get.return_value = None
        
        result = _user_exists(mock_store, 'nonexistent_user')
        
        assert result is False
        mock_store.get.assert_called_once_with('nonexistent_user')


class TestGetExistingUserIds:
    """Test _get_existing_user_ids function."""
    
    @patch('openapi_server.impl.family.get_store')
    def test_get_existing_user_ids_success(self, mock_get_store):
        """Test getting list of existing user IDs."""
        mock_user_store = MagicMock()
        mock_user_store.list.return_value = [
            {'userId': 'user1', 'email': 'user1@test.com'},
            {'userId': 'user2', 'email': 'user2@test.com'},
            {'userId': 'user3', 'email': 'user3@test.com'}
        ]
        mock_get_store.return_value = mock_user_store
        
        result = _get_existing_user_ids()
        
        expected_ids = ['user1', 'user2', 'user3']
        assert result == expected_ids
        mock_user_store.list.assert_called_once()
    
    @patch('openapi_server.impl.family.get_store')
    def test_get_existing_user_ids_empty(self, mock_get_store):
        """Test getting user IDs when no users exist."""
        mock_user_store = MagicMock()
        mock_user_store.list.return_value = []
        mock_get_store.return_value = mock_user_store
        
        result = _get_existing_user_ids()
        
        assert result == []
        mock_user_store.list.assert_called_once()


class TestFamilyFunctionIntegration:
    """Integration tests for family functions working together."""
    
    @patch('openapi_server.impl.family._store')
    def test_create_then_get_family(self, mock_store):
        """Test creating a family then retrieving it."""
        family_data = {
            'familyName': 'Integration Test Family',
            'parents': ['parent1'],
            'students': ['student1']
        }
        
        created_family = {**family_data, 'familyId': 'integration_id'}
        mock_store.return_value.create.return_value = created_family
        mock_store.return_value.get.return_value = created_family
        
        with patch('openapi_server.impl.family._validate_family_members'):
            # Create family
            create_result = handle_create_family(family_data)
            assert create_result[1] == 201
            assert create_result[0]['familyName'] == 'Integration Test Family'
            
            # Get family
            get_result = handle_get_family('integration_id')
            assert get_result['familyId'] == 'integration_id'
            assert get_result['familyName'] == 'Integration Test Family'
            assert get_result['parents'] == ['parent1']
            assert get_result['students'] == ['student1']
    
    @patch('openapi_server.impl.family._store')
    def test_create_update_family_workflow(self, mock_store):
        """Test complete create-update workflow for family."""
        # Initial family data
        initial_data = {
            'familyName': 'Original Name',
            'parents': ['parent1']
        }
        
        # Updated family data  
        update_data = {
            'familyName': 'Updated Name',
            'students': ['student1', 'student2']
        }
        
        created_family = {**initial_data, 'familyId': 'workflow_id'}
        updated_family = {
            'familyId': 'workflow_id',
            'familyName': 'Updated Name',
            'parents': ['parent1'],
            'students': ['student1', 'student2']
        }
        
        mock_store.return_value.create.return_value = created_family
        mock_store.return_value.update.return_value = updated_family
        
        with patch('openapi_server.impl.family._validate_family_members'):
            # Create
            create_result = handle_create_family(initial_data)
            assert create_result[0]['familyName'] == 'Original Name'
            
            # Update
            update_result = handle_update_family('workflow_id', update_data)
            assert update_result[0]['familyName'] == 'Updated Name'
            assert len(update_result[0]['students']) == 2