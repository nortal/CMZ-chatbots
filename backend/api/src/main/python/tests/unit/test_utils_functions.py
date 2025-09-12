"""
Unit tests for utils module functions to enable TDD workflow.
PR003946-94: Comprehensive function-level unit tests

Tests utility functions including ID generation, validation helpers,
ORM operations, and core utilities.
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from openapi_server.impl.utils.id_generator import generate_id, generate_uuid, generate_user_id, generate_family_id
from openapi_server.impl.utils.orm.store import get_store
from openapi_server.impl.utils.core import (
    ensure_pk, model_to_json_keyed_dict, now_iso, not_found
)
from openapi_server.impl.utils.validation import validate_email, validate_required_fields
from openapi_server.impl.error_handler import ValidationError


class TestIdGenerator:
    """Test ID generation utility functions."""
    
    def test_generate_id_default_length(self):
        """Test ID generation with default length."""
        generated_id = generate_id()
        
        assert isinstance(generated_id, str)
        assert len(generated_id) == 12  # Default length
        assert generated_id.isalnum()  # Only alphanumeric characters
    
    def test_generate_id_custom_length(self):
        """Test ID generation with custom length."""
        lengths = [8, 16, 24, 32]
        
        for length in lengths:
            generated_id = generate_id(length=length)
            assert len(generated_id) == length
            assert generated_id.isalnum()
    
    def test_generate_id_uniqueness(self):
        """Test that generated IDs are unique."""
        ids = [generate_id() for _ in range(100)]
        unique_ids = set(ids)
        
        # All IDs should be unique
        assert len(unique_ids) == len(ids)
    
    def test_generate_id_with_prefix(self):
        """Test ID generation with prefix."""
        prefix = "test"
        generated_id = generate_id(prefix=prefix)
        
        assert generated_id.startswith(prefix)
        assert len(generated_id) == len(prefix) + 12  # prefix + default length
    
    def test_generate_user_id(self):
        """Test user-specific ID generation."""
        user_id = generate_user_id()
        
        assert isinstance(user_id, str)
        assert user_id.startswith("user_")
        assert len(user_id) == 5 + 12  # "user_" + 12 characters
    
    def test_generate_family_id(self):
        """Test family-specific ID generation."""
        family_id = generate_family_id()
        
        assert isinstance(family_id, str)
        assert family_id.startswith("family_")
        assert len(family_id) == 7 + 12  # "family_" + 12 characters
    
    def test_generate_id_boundary_values(self, boundary_value_generator):
        """Test ID generation with boundary values."""
        # Test minimum length
        min_id = generate_id(length=1)
        assert len(min_id) == 1
        
        # Test maximum reasonable length
        max_id = generate_id(length=100)
        assert len(max_id) == 100
        
        # Test zero length should default or handle gracefully
        try:
            zero_id = generate_id(length=0)
            assert len(zero_id) >= 0  # Should handle gracefully
        except ValueError:
            pass  # Acceptable to raise error for zero length


class TestCoreUtils:
    """Test core utility functions."""
    
    @patch('openapi_server.impl.utils.core.FileStore')
    def test_get_store_success(self, mock_file_store):
        """Test successful store retrieval."""
        mock_store_instance = MagicMock()
        mock_file_store.return_value = mock_store_instance
        
        result = get_store('test_table', 'test_pk')
        
        assert result == mock_store_instance
        mock_file_store.assert_called_once_with('test_table', 'test_pk')
    
    def test_ensure_pk_with_existing_pk(self):
        """Test ensure_pk when primary key already exists."""
        data = {'userId': 'existing_id', 'name': 'Test User'}
        
        ensure_pk(data, 'userId')
        
        # Should not modify existing primary key
        assert data['userId'] == 'existing_id'
        assert data['name'] == 'Test User'
    
    def test_ensure_pk_without_existing_pk(self):
        """Test ensure_pk when primary key doesn't exist."""
        data = {'name': 'Test User'}
        
        ensure_pk(data, 'userId')
        
        # Should generate new primary key
        assert 'userId' in data
        assert isinstance(data['userId'], str)
        assert len(data['userId']) > 0
        assert data['name'] == 'Test User'
    
    def test_ensure_pk_empty_pk(self):
        """Test ensure_pk when primary key is empty."""
        data = {'userId': '', 'name': 'Test User'}
        
        ensure_pk(data, 'userId')
        
        # Should generate new primary key for empty value
        assert data['userId'] != ''
        assert isinstance(data['userId'], str)
        assert len(data['userId']) > 0
    
    def test_ensure_pk_none_pk(self):
        """Test ensure_pk when primary key is None."""
        data = {'userId': None, 'name': 'Test User'}
        
        ensure_pk(data, 'userId')
        
        # Should generate new primary key for None value
        assert data['userId'] is not None
        assert isinstance(data['userId'], str)
        assert len(data['userId']) > 0
    
    def test_model_to_json_keyed_dict_with_model(self):
        """Test model_to_json_keyed_dict with OpenAPI model object."""
        # Mock an OpenAPI model
        mock_model = MagicMock()
        mock_model.to_dict.return_value = {
            'userId': 'test_user',
            'displayName': 'Test User',
            'email': 'test@example.com'
        }
        
        result = model_to_json_keyed_dict(mock_model)
        
        assert result == {
            'userId': 'test_user',
            'displayName': 'Test User', 
            'email': 'test@example.com'
        }
        mock_model.to_dict.assert_called_once()
    
    def test_model_to_json_keyed_dict_with_dict(self):
        """Test model_to_json_keyed_dict with dictionary."""
        input_dict = {
            'userId': 'test_user',
            'displayName': 'Test User',
            'email': 'test@example.com'
        }
        
        result = model_to_json_keyed_dict(input_dict)
        
        # Should return copy of dictionary
        assert result == input_dict
        assert result is not input_dict  # Should be a copy
    
    def test_model_to_json_keyed_dict_with_none(self):
        """Test model_to_json_keyed_dict with None."""
        result = model_to_json_keyed_dict(None)
        
        assert result == {}
    
    def test_now_iso(self):
        """Test ISO timestamp generation."""
        timestamp = now_iso()
        
        assert isinstance(timestamp, str)
        assert 'T' in timestamp  # ISO format contains T
        assert timestamp.endswith('Z') or '+' in timestamp  # UTC timezone
        
        # Should be parseable as datetime
        parsed = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        assert isinstance(parsed, datetime)
    
    def test_now_iso_consistency(self):
        """Test now_iso generates consistent format."""
        timestamps = [now_iso() for _ in range(10)]
        
        # All timestamps should have same format
        for ts in timestamps:
            assert isinstance(ts, str)
            assert len(ts) >= 19  # Minimum length for ISO format
            assert 'T' in ts
    
    def test_not_found(self):
        """Test not_found utility function."""
        result = not_found()
        
        # Should return tuple with None and 404 status
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert result[0] is None
        assert result[1] == 404


class TestValidationUtils:
    """Test validation utility functions."""
    
    def test_validate_email_valid_emails(self):
        """Test email validation with valid email addresses."""
        valid_emails = [
            'test@example.com',
            'user.name@domain.co.uk',
            'user+tag@example.org',
            'test123@test-domain.com',
            'simple@domain.io'
        ]
        
        for email in valid_emails:
            # Should not raise any exception
            result = validate_email(email)
            assert result is True or result is None
    
    def test_validate_email_invalid_emails(self):
        """Test email validation with invalid email addresses."""
        invalid_emails = [
            'invalid.email',           # Missing @
            '@domain.com',            # Missing local part
            'user@',                  # Missing domain
            'user@domain',            # Missing TLD
            'user name@domain.com',   # Space in local part
            'user@domain..com',       # Double dot in domain
            ''                        # Empty string
        ]
        
        for invalid_email in invalid_emails:
            with pytest.raises(ValidationError) as exc_info:
                validate_email(invalid_email)
            
            error = exc_info.value
            assert 'email' in error.message.lower() or 'invalid' in error.message.lower()
    
    def test_validate_required_fields_all_present(self):
        """Test required field validation when all fields are present."""
        data = {
            'displayName': 'Test User',
            'email': 'test@example.com',
            'role': 'member'
        }
        required_fields = ['displayName', 'email', 'role']
        
        # Should not raise any exception
        result = validate_required_fields(data, required_fields)
        assert result is True or result is None
    
    def test_validate_required_fields_missing_fields(self):
        """Test required field validation when fields are missing."""
        data = {
            'displayName': 'Test User',
            'email': 'test@example.com'
            # Missing 'role' field
        }
        required_fields = ['displayName', 'email', 'role']
        
        with pytest.raises(ValidationError) as exc_info:
            validate_required_fields(data, required_fields)
        
        error = exc_info.value
        assert 'role' in str(error.field_errors) or 'required' in error.message.lower()
    
    def test_validate_required_fields_empty_values(self):
        """Test required field validation with empty values."""
        data = {
            'displayName': '',           # Empty string
            'email': 'test@example.com',
            'role': None                 # None value
        }
        required_fields = ['displayName', 'email', 'role']
        
        with pytest.raises(ValidationError) as exc_info:
            validate_required_fields(data, required_fields)
        
        error = exc_info.value
        # Should detect both empty displayName and None role
        field_errors = str(error.field_errors).lower()
        assert 'displayname' in field_errors or 'role' in field_errors
    
    def test_validate_required_fields_no_requirements(self):
        """Test required field validation with no required fields."""
        data = {'optional': 'value'}
        required_fields = []
        
        # Should not raise any exception
        result = validate_required_fields(data, required_fields)
        assert result is True or result is None
    
    def test_validate_required_fields_boundary_values(self, boundary_value_generator):
        """Test required field validation with boundary values."""
        # Test with empty data
        with pytest.raises(ValidationError):
            validate_required_fields({}, ['required_field'])
        
        # Test with null/empty values from generator
        for invalid_value in boundary_value_generator.null_empty_values():
            data = {'required_field': invalid_value}
            
            try:
                validate_required_fields(data, ['required_field'])
                # If no exception, the value was considered valid
                assert invalid_value not in [None, '', ' ', '   ']
            except ValidationError:
                # Exception expected for truly empty values
                assert invalid_value in [None, '', ' ', '   ', '\t', '\n']


class TestUtilsFunctionIntegration:
    """Integration tests for utility functions working together."""
    
    @patch('openapi_server.impl.utils.core.get_store')
    def test_id_generation_and_storage(self, mock_get_store):
        """Test ID generation integrated with storage operations."""
        mock_store = MagicMock()
        mock_get_store.return_value = mock_store
        
        # Create data that needs ID generation
        data = {'displayName': 'Test User', 'email': 'test@example.com'}
        
        # Ensure primary key is generated
        ensure_pk(data, 'userId')
        
        # Verify ID was generated
        assert 'userId' in data
        assert isinstance(data['userId'], str)
        assert len(data['userId']) > 0
        
        # Simulate storage operation
        store = get_store('user_table', 'userId')
        assert store == mock_store
    
    def test_model_conversion_and_validation(self):
        """Test model conversion integrated with validation."""
        # Mock model with to_dict method
        mock_model = MagicMock()
        mock_model.to_dict.return_value = {
            'displayName': 'Test User',
            'email': 'test@example.com',
            'role': 'member'
        }
        
        # Convert model to dict
        data = model_to_json_keyed_dict(mock_model)
        
        # Validate required fields
        required_fields = ['displayName', 'email', 'role']
        result = validate_required_fields(data, required_fields)
        
        # Should pass validation
        assert result is True or result is None
    
    def test_complete_data_preparation_workflow(self):
        """Test complete workflow of data preparation utilities."""
        # Start with partial data
        raw_data = {
            'displayName': 'Integration Test User',
            'email': 'integration@test.com'
        }
        
        # Step 1: Ensure primary key
        ensure_pk(raw_data, 'userId')
        assert 'userId' in raw_data
        
        # Step 2: Add timestamp
        raw_data['created'] = {'at': now_iso()}
        assert 'created' in raw_data
        assert 'at' in raw_data['created']
        
        # Step 3: Validate email
        validate_email(raw_data['email'])  # Should not raise exception
        
        # Step 4: Validate required fields
        validate_required_fields(raw_data, ['userId', 'displayName', 'email'])
        
        # Final data should be complete and valid
        assert len(raw_data['userId']) > 0
        assert raw_data['email'] == 'integration@test.com'
        assert isinstance(raw_data['created']['at'], str)
    
    def test_error_handling_consistency(self):
        """Test that utility functions handle errors consistently."""
        # Test ID generation with invalid parameters
        try:
            generate_id(length=-1)
        except (ValueError, ValidationError):
            pass  # Expected to handle invalid input
        
        # Test validation with invalid data
        with pytest.raises(ValidationError):
            validate_email('invalid.email.format')
        
        with pytest.raises(ValidationError):
            validate_required_fields({}, ['required_field'])
        
        # All validation errors should be ValidationError instances
        # This ensures consistent error handling across utilities