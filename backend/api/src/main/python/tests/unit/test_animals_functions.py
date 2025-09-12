"""
Unit tests for animals.py functions to enable TDD workflow.
PR003946-94: Comprehensive function-level unit tests

Tests animal CRUD operations, status filtering, configuration management,
and business logic for the animals module.
"""
import pytest
from unittest.mock import patch, MagicMock
from typing import List

from openapi_server.impl.animals import (
    handle_create_animal, handle_get_animal, handle_list_animals,
    handle_update_animal, handle_delete_animal, handle_get_animal_config,
    handle_update_animal_config, _get_flask_handler
)
from openapi_server.models.animal import Animal
from openapi_server.models.animal_config import AnimalConfig
from openapi_server.impl.error_handler import ValidationError, NotFoundError


class TestHandleCreateAnimal:
    """Test handle_create_animal function."""
    
    @patch('openapi_server.impl.animals._get_flask_handler')
    def test_handle_create_animal_success(self, mock_handler):
        """Test successful animal creation."""
        animal_data = Animal(
            animal_name='Leo the Lion',
            species='Lion',
            habitat='African Savanna',
            description='A magnificent African lion',
            personality='brave,curious,educational'
        )
        
        created_animal = Animal(
            animal_id='generated_id',
            animal_name='Leo the Lion',
            species='Lion',
            habitat='African Savanna',
            description='A magnificent African lion',
            personality='brave,curious,educational'
        )
        
        mock_flask_handler = MagicMock()
        mock_flask_handler.create_animal.return_value = created_animal
        mock_handler.return_value = mock_flask_handler
        
        result = handle_create_animal(animal_data)
        
        assert isinstance(result, Animal)
        assert result.animal_id == 'generated_id'
        assert result.animal_name == 'Leo the Lion'
        assert result.species == 'Lion'
        mock_flask_handler.create_animal.assert_called_once_with(animal_data)
    
    @patch('openapi_server.impl.animals._get_flask_handler')
    def test_handle_create_animal_with_config(self, mock_handler):
        """Test animal creation with chatbot configuration."""
        animal_data = Animal(
            animal_name='Zara the Zebra',
            species='Zebra',
            habitat='African Plains',
            description='A striped beauty',
            personality='playful,energetic',
            chatbot_config={
                'enabled': True,
                'model': 'claude-3-sonnet',
                'temperature': 0.7,
                'personality_traits': ['playful', 'energetic']
            }
        )
        
        created_animal = Animal(
            animal_id='zebra_id',
            animal_name='Zara the Zebra',
            species='Zebra',
            habitat='African Plains',
            description='A striped beauty',
            personality='playful,energetic',
            chatbot_config=animal_data.chatbot_config
        )
        
        mock_flask_handler = MagicMock()
        mock_flask_handler.create_animal.return_value = created_animal
        mock_handler.return_value = mock_flask_handler
        
        result = handle_create_animal(animal_data)
        
        assert result.animal_id == 'zebra_id'
        assert result.chatbot_config is not None
        assert result.chatbot_config['enabled'] is True
        assert result.chatbot_config['model'] == 'claude-3-sonnet'
    
    @patch('openapi_server.impl.animals._get_flask_handler')
    def test_handle_create_animal_handler_error(self, mock_handler):
        """Test animal creation when handler raises error."""
        animal_data = Animal(
            animal_name='Error Animal',
            species='Unknown',
            habitat='Test Habitat'
        )
        
        mock_flask_handler = MagicMock()
        mock_flask_handler.create_animal.side_effect = ValidationError(
            "Animal creation failed",
            field_errors={'species': ['Unknown species not allowed']}
        )
        mock_handler.return_value = mock_flask_handler
        
        with pytest.raises(ValidationError) as exc_info:
            handle_create_animal(animal_data)
        
        assert "Animal creation failed" in str(exc_info.value)
        assert 'species' in exc_info.value.field_errors


class TestHandleGetAnimal:
    """Test handle_get_animal function."""
    
    @patch('openapi_server.impl.animals._get_flask_handler')
    def test_handle_get_animal_success(self, mock_handler):
        """Test successful animal retrieval."""
        animal = Animal(
            animal_id='test_animal',
            animal_name='Test Animal',
            species='Test Species',
            habitat='Test Habitat',
            description='A test animal'
        )
        
        mock_flask_handler = MagicMock()
        mock_flask_handler.get_animal.return_value = animal
        mock_handler.return_value = mock_flask_handler
        
        result = handle_get_animal('test_animal')
        
        assert isinstance(result, Animal)
        assert result.animal_id == 'test_animal'
        assert result.animal_name == 'Test Animal'
        mock_flask_handler.get_animal.assert_called_once_with('test_animal')
    
    @patch('openapi_server.impl.animals._get_flask_handler')
    def test_handle_get_animal_not_found(self, mock_handler):
        """Test get animal when animal doesn't exist."""
        mock_flask_handler = MagicMock()
        mock_flask_handler.get_animal.side_effect = NotFoundError("Animal not found")
        mock_handler.return_value = mock_flask_handler
        
        with pytest.raises(NotFoundError) as exc_info:
            handle_get_animal('nonexistent_animal')
        
        assert "Animal not found" in str(exc_info.value)
    
    def test_handle_get_animal_empty_id(self):
        """Test get animal with empty animal ID."""
        with patch('openapi_server.impl.animals._get_flask_handler') as mock_handler:
            mock_flask_handler = MagicMock()
            mock_flask_handler.get_animal.side_effect = ValidationError("Invalid animal ID")
            mock_handler.return_value = mock_flask_handler
            
            with pytest.raises(ValidationError):
                handle_get_animal('')


class TestHandleListAnimals:
    """Test handle_list_animals function with status filtering."""
    
    @patch('openapi_server.impl.animals._get_flask_handler')
    def test_handle_list_animals_no_filter(self, mock_handler):
        """Test list animals without status filter."""
        animals = [
            Animal(animal_id='animal1', animal_name='Animal 1', species='Species 1'),
            Animal(animal_id='animal2', animal_name='Animal 2', species='Species 2'),
            Animal(animal_id='animal3', animal_name='Animal 3', species='Species 3')
        ]
        
        mock_flask_handler = MagicMock()
        mock_flask_handler.list_animals.return_value = animals
        mock_handler.return_value = mock_flask_handler
        
        result = handle_list_animals()
        
        assert isinstance(result, list)
        assert len(result) == 3
        assert all(isinstance(animal, Animal) for animal in result)
        mock_flask_handler.list_animals.assert_called_once_with(None)
    
    @patch('openapi_server.impl.animals._get_flask_handler')
    def test_handle_list_animals_with_status_filter(self, mock_handler):
        """Test list animals with status filter."""
        active_animals = [
            Animal(animal_id='active1', animal_name='Active Animal 1', species='Species 1'),
            Animal(animal_id='active2', animal_name='Active Animal 2', species='Species 2')
        ]
        
        mock_flask_handler = MagicMock()
        mock_flask_handler.list_animals.return_value = active_animals
        mock_handler.return_value = mock_flask_handler
        
        result = handle_list_animals(status='active')
        
        assert isinstance(result, list)
        assert len(result) == 2
        assert all('Active' in animal.animal_name for animal in result)
        mock_flask_handler.list_animals.assert_called_once_with('active')
    
    @patch('openapi_server.impl.animals._get_flask_handler')
    def test_handle_list_animals_empty_result(self, mock_handler):
        """Test list animals returns empty list."""
        mock_flask_handler = MagicMock()
        mock_flask_handler.list_animals.return_value = []
        mock_handler.return_value = mock_flask_handler
        
        result = handle_list_animals(status='inactive')
        
        assert isinstance(result, list)
        assert len(result) == 0
        mock_flask_handler.list_animals.assert_called_once_with('inactive')
    
    @patch('openapi_server.impl.animals._get_flask_handler')
    def test_handle_list_animals_invalid_status(self, mock_handler):
        """Test list animals with invalid status filter."""
        mock_flask_handler = MagicMock()
        mock_flask_handler.list_animals.side_effect = ValidationError(
            "Invalid status filter",
            field_errors={'status': ['Status must be active or inactive']}
        )
        mock_handler.return_value = mock_flask_handler
        
        with pytest.raises(ValidationError) as exc_info:
            handle_list_animals(status='invalid_status')
        
        assert "Invalid status filter" in str(exc_info.value)
        assert 'status' in exc_info.value.field_errors


class TestHandleUpdateAnimal:
    """Test handle_update_animal function."""
    
    @patch('openapi_server.impl.animals._get_flask_handler')
    def test_handle_update_animal_success(self, mock_handler):
        """Test successful animal update."""
        update_data = Animal(
            animal_name='Updated Lion Name',
            description='Updated description for the lion',
            personality='updated,traits'
        )
        
        updated_animal = Animal(
            animal_id='lion_id',
            animal_name='Updated Lion Name',
            species='Lion',
            habitat='African Savanna',
            description='Updated description for the lion',
            personality='updated,traits'
        )
        
        mock_flask_handler = MagicMock()
        mock_flask_handler.update_animal.return_value = updated_animal
        mock_handler.return_value = mock_flask_handler
        
        result = handle_update_animal('lion_id', update_data)
        
        assert isinstance(result, Animal)
        assert result.animal_id == 'lion_id'
        assert result.animal_name == 'Updated Lion Name'
        assert result.description == 'Updated description for the lion'
        mock_flask_handler.update_animal.assert_called_once_with('lion_id', update_data)
    
    @patch('openapi_server.impl.animals._get_flask_handler')
    def test_handle_update_animal_not_found(self, mock_handler):
        """Test update animal when animal doesn't exist."""
        update_data = Animal(animal_name='Updated Name')
        
        mock_flask_handler = MagicMock()
        mock_flask_handler.update_animal.side_effect = NotFoundError("Animal not found")
        mock_handler.return_value = mock_flask_handler
        
        with pytest.raises(NotFoundError):
            handle_update_animal('nonexistent', update_data)
    
    @patch('openapi_server.impl.animals._get_flask_handler')
    def test_handle_update_animal_validation_error(self, mock_handler):
        """Test update animal with validation error."""
        update_data = Animal(species='InvalidSpecies')
        
        mock_flask_handler = MagicMock()
        mock_flask_handler.update_animal.side_effect = ValidationError(
            "Invalid species",
            field_errors={'species': ['Species not recognized']}
        )
        mock_handler.return_value = mock_flask_handler
        
        with pytest.raises(ValidationError):
            handle_update_animal('animal_id', update_data)


class TestHandleDeleteAnimal:
    """Test handle_delete_animal function with soft delete semantics."""
    
    @patch('openapi_server.impl.animals._get_flask_handler')
    def test_handle_delete_animal_success(self, mock_handler):
        """Test successful animal deletion (soft delete)."""
        mock_flask_handler = MagicMock()
        mock_flask_handler.delete_animal.return_value = (None, 204)
        mock_handler.return_value = mock_flask_handler
        
        result = handle_delete_animal('animal_to_delete')
        
        assert result == (None, 204)
        mock_flask_handler.delete_animal.assert_called_once_with('animal_to_delete')
    
    @patch('openapi_server.impl.animals._get_flask_handler')
    def test_handle_delete_animal_not_found(self, mock_handler):
        """Test delete animal when animal doesn't exist."""
        mock_flask_handler = MagicMock()
        mock_flask_handler.delete_animal.side_effect = NotFoundError("Animal not found")
        mock_handler.return_value = mock_flask_handler
        
        with pytest.raises(NotFoundError):
            handle_delete_animal('nonexistent')
    
    @patch('openapi_server.impl.animals._get_flask_handler')
    def test_handle_delete_animal_already_deleted(self, mock_handler):
        """Test delete animal that's already soft-deleted."""
        mock_flask_handler = MagicMock()
        mock_flask_handler.delete_animal.return_value = (None, 204)  # Still returns 204
        mock_handler.return_value = mock_flask_handler
        
        result = handle_delete_animal('already_deleted')
        
        assert result == (None, 204)


class TestHandleGetAnimalConfig:
    """Test handle_get_animal_config function."""
    
    @patch('openapi_server.impl.animals._get_flask_handler')
    def test_handle_get_animal_config_success(self, mock_handler):
        """Test successful animal configuration retrieval."""
        animal_config = AnimalConfig(
            enabled=True,
            model='claude-3-sonnet',
            temperature=0.7,
            personality_traits=['friendly', 'educational'],
            max_response_length=500
        )
        
        mock_flask_handler = MagicMock()
        mock_flask_handler.get_animal_config.return_value = animal_config
        mock_handler.return_value = mock_flask_handler
        
        result = handle_get_animal_config('animal_with_config')
        
        assert isinstance(result, AnimalConfig)
        assert result.enabled is True
        assert result.model == 'claude-3-sonnet'
        assert result.temperature == 0.7
        assert 'friendly' in result.personality_traits
        mock_flask_handler.get_animal_config.assert_called_once_with('animal_with_config')
    
    @patch('openapi_server.impl.animals._get_flask_handler')
    def test_handle_get_animal_config_not_found(self, mock_handler):
        """Test get animal config when animal doesn't exist."""
        mock_flask_handler = MagicMock()
        mock_flask_handler.get_animal_config.side_effect = NotFoundError("Animal not found")
        mock_handler.return_value = mock_flask_handler
        
        with pytest.raises(NotFoundError):
            handle_get_animal_config('nonexistent_animal')


class TestHandleUpdateAnimalConfig:
    """Test handle_update_animal_config function."""
    
    @patch('openapi_server.impl.animals._get_flask_handler')
    def test_handle_update_animal_config_success(self, mock_handler):
        """Test successful animal configuration update."""
        config_update = AnimalConfig(
            enabled=False,
            temperature=0.5,
            personality_traits=['calm', 'informative'],
            max_response_length=300
        )
        
        updated_config = AnimalConfig(
            enabled=False,
            model='claude-3-sonnet',  # Preserved from existing
            temperature=0.5,
            personality_traits=['calm', 'informative'],
            max_response_length=300
        )
        
        mock_flask_handler = MagicMock()
        mock_flask_handler.update_animal_config.return_value = updated_config
        mock_handler.return_value = mock_flask_handler
        
        result = handle_update_animal_config('animal_id', config_update)
        
        assert isinstance(result, AnimalConfig)
        assert result.enabled is False
        assert result.temperature == 0.5
        assert result.max_response_length == 300
        assert 'calm' in result.personality_traits
        mock_flask_handler.update_animal_config.assert_called_once_with('animal_id', config_update)
    
    @patch('openapi_server.impl.animals._get_flask_handler')
    def test_handle_update_animal_config_validation_error(self, mock_handler):
        """Test update animal config with validation error."""
        invalid_config = AnimalConfig(temperature=2.0)  # Temperature too high
        
        mock_flask_handler = MagicMock()
        mock_flask_handler.update_animal_config.side_effect = ValidationError(
            "Invalid configuration",
            field_errors={'temperature': ['Temperature must be between 0.0 and 1.0']}
        )
        mock_handler.return_value = mock_flask_handler
        
        with pytest.raises(ValidationError) as exc_info:
            handle_update_animal_config('animal_id', invalid_config)
        
        assert "Invalid configuration" in str(exc_info.value)
        assert 'temperature' in exc_info.value.field_errors


class TestGetFlaskHandler:
    """Test _get_flask_handler function."""
    
    @patch('openapi_server.impl.animals.dependency_injection')
    def test_get_flask_handler_success(self, mock_di):
        """Test successful Flask handler retrieval."""
        mock_handler = MagicMock()
        mock_di.get_handler.return_value = mock_handler
        
        result = _get_flask_handler()
        
        assert result == mock_handler
        mock_di.get_handler.assert_called_once_with('flask')
    
    @patch('openapi_server.impl.animals.dependency_injection')
    def test_get_flask_handler_failure(self, mock_di):
        """Test Flask handler retrieval failure."""
        mock_di.get_handler.side_effect = Exception("Handler not available")
        
        with pytest.raises(Exception) as exc_info:
            _get_flask_handler()
        
        assert "Handler not available" in str(exc_info.value)


class TestAnimalsFunctionIntegration:
    """Integration tests for animals functions working together."""
    
    @patch('openapi_server.impl.animals._get_flask_handler')
    def test_create_then_get_animal_workflow(self, mock_handler):
        """Test creating an animal then retrieving it."""
        # Create animal
        animal_data = Animal(
            animal_name='Integration Test Lion',
            species='Lion',
            habitat='Test Savanna',
            description='A test lion for integration testing'
        )
        
        created_animal = Animal(
            animal_id='integration_id',
            animal_name='Integration Test Lion',
            species='Lion',
            habitat='Test Savanna',
            description='A test lion for integration testing'
        )
        
        mock_flask_handler = MagicMock()
        mock_flask_handler.create_animal.return_value = created_animal
        mock_flask_handler.get_animal.return_value = created_animal
        mock_handler.return_value = mock_flask_handler
        
        # Create
        create_result = handle_create_animal(animal_data)
        assert create_result.animal_id == 'integration_id'
        assert create_result.animal_name == 'Integration Test Lion'
        
        # Get
        get_result = handle_get_animal('integration_id')
        assert get_result.animal_id == 'integration_id'
        assert get_result.animal_name == 'Integration Test Lion'
        assert get_result.species == 'Lion'
    
    @patch('openapi_server.impl.animals._get_flask_handler')
    def test_animal_config_workflow(self, mock_handler):
        """Test complete animal configuration workflow."""
        animal_id = 'config_test_animal'
        
        # Initial config
        initial_config = AnimalConfig(
            enabled=True,
            model='claude-3-sonnet',
            temperature=0.8,
            personality_traits=['playful']
        )
        
        # Updated config
        updated_config = AnimalConfig(
            enabled=True,
            model='claude-3-sonnet',
            temperature=0.6,
            personality_traits=['playful', 'educational'],
            max_response_length=400
        )
        
        mock_flask_handler = MagicMock()
        mock_flask_handler.get_animal_config.return_value = initial_config
        mock_flask_handler.update_animal_config.return_value = updated_config
        mock_handler.return_value = mock_flask_handler
        
        # Get initial config
        get_result = handle_get_animal_config(animal_id)
        assert get_result.temperature == 0.8
        assert len(get_result.personality_traits) == 1
        
        # Update config
        update_result = handle_update_animal_config(animal_id, updated_config)
        assert update_result.temperature == 0.6
        assert len(update_result.personality_traits) == 2
        assert update_result.max_response_length == 400
    
    @patch('openapi_server.impl.animals._get_flask_handler')
    def test_list_and_filter_animals(self, mock_handler):
        """Test listing and filtering animals by status."""
        all_animals = [
            Animal(animal_id='active1', animal_name='Active Lion', species='Lion'),
            Animal(animal_id='active2', animal_name='Active Tiger', species='Tiger'),
            Animal(animal_id='inactive1', animal_name='Inactive Bear', species='Bear')
        ]
        
        active_animals = [animal for animal in all_animals if 'Active' in animal.animal_name]
        
        mock_flask_handler = MagicMock()
        # Mock different responses for different status filters
        mock_flask_handler.list_animals.side_effect = lambda status: {
            None: all_animals,
            'active': active_animals,
            'inactive': [animal for animal in all_animals if 'Inactive' in animal.animal_name]
        }.get(status, [])
        mock_handler.return_value = mock_flask_handler
        
        # List all
        all_result = handle_list_animals()
        assert len(all_result) == 3
        
        # List active only
        active_result = handle_list_animals(status='active')
        assert len(active_result) == 2
        assert all('Active' in animal.animal_name for animal in active_result)
        
        # List inactive only
        inactive_result = handle_list_animals(status='inactive')
        assert len(inactive_result) == 1
        assert inactive_result[0].animal_name == 'Inactive Bear'