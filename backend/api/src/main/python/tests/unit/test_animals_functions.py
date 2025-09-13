"""
Unit tests for animals.py functions to enable TDD workflow.
PR003946-94: Comprehensive function-level unit tests

Tests animal CRUD operations, status filtering, configuration management,
and business logic for the animals module.
"""
import pytest
from unittest.mock import patch, MagicMock

from openapi_server.impl.animals import (
    handle_create_animal, handle_get_animal, handle_list_animals,
    handle_update_animal, handle_delete_animal, handle_get_animal_config,
    handle_update_animal_config, _get_flask_handler
)
from openapi_server.impl.error_handler import ValidationError, NotFoundError


class TestHandleCreateAnimal:
    """Test handle_create_animal function."""
    
    @patch('openapi_server.impl.animals._get_flask_handler')
    def test_handle_create_animal_success(self, mock_handler):
        """Test successful animal creation."""
        animal_data = {
            'name': 'Leo the Lion',
            'species': 'Lion'
        }
        
        created_animal = {
            'animalId': 'generated_id',
            'name': 'Leo the Lion',
            'species': 'Lion'
        }
        
        mock_flask_handler = MagicMock()
        mock_flask_handler.create_animal.return_value = created_animal
        mock_handler.return_value = mock_flask_handler
        
        result = handle_create_animal(animal_data)
        
        assert result['animalId'] == 'generated_id'
        assert result['name'] == 'Leo the Lion'
        assert result['species'] == 'Lion'
        mock_flask_handler.create_animal.assert_called_once_with(animal_data)
    
    @patch('openapi_server.impl.animals._get_flask_handler')
    def test_handle_create_animal_validation_error(self, mock_handler):
        """Test animal creation fails with validation error."""
        invalid_data = {'name': '', 'species': 'Lion'}  # Empty name
        
        mock_flask_handler = MagicMock()
        mock_flask_handler.create_animal.side_effect = ValidationError("Invalid data")
        mock_handler.return_value = mock_flask_handler
        
        with pytest.raises(ValidationError):
            handle_create_animal(invalid_data)


class TestHandleGetAnimal:
    """Test handle_get_animal function."""
    
    @patch('openapi_server.impl.animals._get_flask_handler')
    def test_handle_get_animal_success(self, mock_handler):
        """Test successful animal retrieval."""
        animal_id = 'test_animal_id'
        expected_animal = {
            'animalId': animal_id,
            'name': 'Test Animal',
            'species': 'Test Species'
        }
        
        mock_flask_handler = MagicMock()
        mock_flask_handler.get_animal.return_value = expected_animal
        mock_handler.return_value = mock_flask_handler
        
        result = handle_get_animal(animal_id)
        
        assert result == expected_animal
        mock_flask_handler.get_animal.assert_called_once_with(animal_id)
    
    @patch('openapi_server.impl.animals._get_flask_handler')
    def test_handle_get_animal_not_found(self, mock_handler):
        """Test animal retrieval when animal doesn't exist."""
        animal_id = 'nonexistent_id'
        
        mock_flask_handler = MagicMock()
        mock_flask_handler.get_animal.side_effect = NotFoundError("Animal not found")
        mock_handler.return_value = mock_flask_handler
        
        with pytest.raises(NotFoundError):
            handle_get_animal(animal_id)


class TestHandleListAnimals:
    """Test handle_list_animals function."""
    
    @patch('openapi_server.impl.animals._get_flask_handler')
    def test_handle_list_animals_success(self, mock_handler):
        """Test successful animal listing."""
        expected_animals = [
            {'animalId': 'animal1', 'name': 'Lion', 'species': 'Lion'},
            {'animalId': 'animal2', 'name': 'Tiger', 'species': 'Tiger'}
        ]
        
        mock_flask_handler = MagicMock()
        mock_flask_handler.list_animals.return_value = expected_animals
        mock_handler.return_value = mock_flask_handler
        
        result = handle_list_animals()
        
        assert result == expected_animals
        mock_flask_handler.list_animals.assert_called_once_with(None)
    
    @patch('openapi_server.impl.animals._get_flask_handler')
    def test_handle_list_animals_with_status_filter(self, mock_handler):
        """Test animal listing with status filter."""
        status = 'active'
        filtered_animals = [
            {'animalId': 'animal1', 'name': 'Lion', 'status': 'active'}
        ]
        
        mock_flask_handler = MagicMock()
        mock_flask_handler.list_animals.return_value = filtered_animals
        mock_handler.return_value = mock_flask_handler
        
        result = handle_list_animals(status)
        
        assert result == filtered_animals
        mock_flask_handler.list_animals.assert_called_once_with(status)


class TestHandleUpdateAnimal:
    """Test handle_update_animal function."""
    
    @patch('openapi_server.impl.animals._get_flask_handler')
    def test_handle_update_animal_success(self, mock_handler):
        """Test successful animal update."""
        animal_id = 'test_animal_id'
        update_data = {'name': 'Updated Name'}
        updated_animal = {
            'animalId': animal_id,
            'name': 'Updated Name',
            'species': 'Lion'
        }
        
        mock_flask_handler = MagicMock()
        mock_flask_handler.update_animal.return_value = updated_animal
        mock_handler.return_value = mock_flask_handler
        
        result = handle_update_animal(animal_id, update_data)
        
        assert result == updated_animal
        mock_flask_handler.update_animal.assert_called_once_with(animal_id, update_data)


class TestHandleDeleteAnimal:
    """Test handle_delete_animal function."""
    
    @patch('openapi_server.impl.animals._get_flask_handler')
    def test_handle_delete_animal_success(self, mock_handler):
        """Test successful animal deletion."""
        animal_id = 'test_animal_id'
        
        mock_flask_handler = MagicMock()
        mock_flask_handler.delete_animal.return_value = True
        mock_handler.return_value = mock_flask_handler
        
        result = handle_delete_animal(animal_id)
        
        assert result is True
        mock_flask_handler.delete_animal.assert_called_once_with(animal_id)


class TestAnimalConfiguration:
    """Test animal configuration functions."""
    
    @patch('openapi_server.impl.animals._get_flask_handler')
    def test_handle_get_animal_config_success(self, mock_handler):
        """Test successful animal config retrieval."""
        animal_id = 'test_animal_id'
        expected_config = {
            'animalConfigId': 'config_id',
            'personality': 'friendly',
            'aiModel': 'claude-3-sonnet'
        }
        
        mock_flask_handler = MagicMock()
        mock_flask_handler.get_animal_config.return_value = expected_config
        mock_handler.return_value = mock_flask_handler
        
        result = handle_get_animal_config(animal_id)
        
        assert result == expected_config
        mock_flask_handler.get_animal_config.assert_called_once_with(animal_id)
    
    @patch('openapi_server.impl.animals._get_flask_handler')
    def test_handle_update_animal_config_success(self, mock_handler):
        """Test successful animal config update."""
        animal_id = 'test_animal_id'
        config_data = {
            'personality': 'playful',
            'aiModel': 'claude-3-haiku',
            'temperature': 0.8
        }
        updated_config = {
            'animalConfigId': 'config_id',
            'personality': 'playful',
            'aiModel': 'claude-3-haiku',
            'temperature': 0.8
        }
        
        mock_flask_handler = MagicMock()
        mock_flask_handler.update_animal_config.return_value = updated_config
        mock_handler.return_value = mock_flask_handler
        
        result = handle_update_animal_config(animal_id, config_data)
        
        assert result == updated_config
        mock_flask_handler.update_animal_config.assert_called_once_with(animal_id, config_data)


class TestFlaskHandlerIntegration:
    """Test Flask handler integration."""
    
    @patch('openapi_server.impl.animals._get_flask_handler')
    def test_get_flask_handler_returns_handler(self, mock_get_handler):
        """Test that _get_flask_handler returns a valid handler."""
        mock_handler = MagicMock()
        mock_get_handler.return_value = mock_handler
        
        handler = _get_flask_handler()
        
        assert handler == mock_handler
        mock_get_handler.assert_called_once()
    
    def test_animals_functions_boundary_values(self):
        """Test animal functions with boundary values."""
        # Test empty animal IDs
        with pytest.raises((ValidationError, ValueError)):
            handle_get_animal("")
        
        with pytest.raises((ValidationError, ValueError)):
            handle_get_animal(None)
        
        # Test invalid status filters
        with pytest.raises((ValidationError, ValueError)):
            handle_list_animals("invalid_status_that_doesnt_exist")