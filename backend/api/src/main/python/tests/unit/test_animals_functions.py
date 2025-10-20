"""
Unit tests for animals.py functions to enable TDD workflow.
PR003946-94: Comprehensive function-level unit tests

Tests animal CRUD operations, status filtering, configuration management,
and business logic for the animals module.

FIXED: Updated to handle tuple return types (response, status_code) from API handlers
"""
import pytest
from unittest.mock import patch, MagicMock

from openapi_server.impl.animals import (
    handle_create_animal, handle_get_animal, handle_list_animals,
    handle_update_animal, handle_delete_animal, handle_get_animal_config,
    handle_update_animal_config
)


class TestHandleCreateAnimal:
    """Test handle_create_animal function."""

    @patch('openapi_server.impl.animals.handle_animal_post')
    def test_handle_create_animal_success(self, mock_post):
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

        # Mock returns tuple (response, status_code)
        mock_post.return_value = (created_animal, 201)

        result, status = handle_create_animal(animal_data)

        assert result['animalId'] == 'generated_id'
        assert result['name'] == 'Leo the Lion'
        assert result['species'] == 'Lion'
        assert status == 201
        mock_post.assert_called_once_with(animal_data)

    @patch('openapi_server.impl.animals.handle_animal_post')
    def test_handle_create_animal_validation_error(self, mock_post):
        """Test animal creation fails with validation error."""
        invalid_data = {'name': '', 'species': 'Lion'}  # Empty name

        # Mock returns error response tuple
        error_response = {'error': 'Invalid data', 'code': 'VALIDATION_ERROR'}
        mock_post.return_value = (error_response, 400)

        result, status = handle_create_animal(invalid_data)

        assert status == 400
        assert 'error' in result
        mock_post.assert_called_once_with(invalid_data)


class TestHandleGetAnimal:
    """Test handle_get_animal function."""

    @patch('openapi_server.impl.animals.handle_animal_get')
    def test_handle_get_animal_success(self, mock_get):
        """Test successful animal retrieval."""
        animal_id = 'test_animal_id'
        expected_animal = {
            'animalId': animal_id,
            'name': 'Test Animal',
            'species': 'Test Species'
        }

        # Mock returns tuple (response, status_code)
        mock_get.return_value = (expected_animal, 200)

        result, status = handle_get_animal(animal_id)

        assert result == expected_animal
        assert status == 200
        mock_get.assert_called_once_with(animal_id)

    @patch('openapi_server.impl.animals.handle_animal_get')
    def test_handle_get_animal_not_found(self, mock_get):
        """Test animal retrieval when animal doesn't exist."""
        animal_id = 'nonexistent_id'

        # Mock returns not found response
        error_response = {'error': 'Animal not found', 'code': 'NOT_FOUND'}
        mock_get.return_value = (error_response, 404)

        result, status = handle_get_animal(animal_id)

        assert status == 404
        assert 'error' in result
        mock_get.assert_called_once_with(animal_id)


class TestHandleListAnimals:
    """Test handle_list_animals function."""

    @patch('openapi_server.impl.animals.handle_animal_list_get')
    def test_handle_list_animals_success(self, mock_list):
        """Test successful animal listing."""
        expected_animals = [
            {'animalId': 'animal1', 'name': 'Lion', 'species': 'Lion'},
            {'animalId': 'animal2', 'name': 'Tiger', 'species': 'Tiger'}
        ]

        # Mock returns tuple (response, status_code)
        mock_list.return_value = (expected_animals, 200)

        result, status = handle_list_animals()

        assert result == expected_animals
        assert status == 200
        mock_list.assert_called_once_with()

    @patch('openapi_server.impl.animals.handle_animal_list_get')
    def test_handle_list_animals_with_status_filter(self, mock_list):
        """Test animal listing with status filter."""
        status_filter = 'active'
        filtered_animals = [
            {'animalId': 'animal1', 'name': 'Lion', 'status': 'active'}
        ]

        # Mock returns tuple (response, status_code)
        mock_list.return_value = (filtered_animals, 200)

        result, status = handle_list_animals(status_filter)

        assert result == filtered_animals
        assert status == 200
        mock_list.assert_called_once_with(status_filter)


class TestHandleUpdateAnimal:
    """Test handle_update_animal function."""

    @patch('openapi_server.impl.animals.handle_animal_put')
    def test_handle_update_animal_success(self, mock_put):
        """Test successful animal update."""
        animal_id = 'test_animal_id'
        update_data = {'name': 'Updated Name'}
        updated_animal = {
            'animalId': animal_id,
            'name': 'Updated Name',
            'species': 'Lion'
        }

        # Mock returns tuple (response, status_code)
        mock_put.return_value = (updated_animal, 200)

        result, status = handle_update_animal(animal_id, update_data)

        assert result == updated_animal
        assert status == 200
        mock_put.assert_called_once_with(animal_id, update_data)


class TestHandleDeleteAnimal:
    """Test handle_delete_animal function."""

    @patch('openapi_server.impl.animals.handle_animal_delete')
    def test_handle_delete_animal_success(self, mock_delete):
        """Test successful animal deletion (soft delete)."""
        animal_id = 'test_animal_id'

        # Mock returns tuple (None for 204 No Content, status_code)
        mock_delete.return_value = (None, 204)

        result, status = handle_delete_animal(animal_id)

        assert result is None
        assert status == 204
        mock_delete.assert_called_once_with(animal_id)


class TestAnimalConfiguration:
    """Test animal configuration functions."""

    @patch('openapi_server.impl.animals.handle_animal_config_get')
    def test_handle_get_animal_config_success(self, mock_get_config):
        """Test successful animal config retrieval."""
        animal_id = 'test_animal_id'
        expected_config = {
            'animalConfigId': 'config_id',
            'personality': 'friendly',
            'aiModel': 'claude-3-sonnet'
        }

        # Mock returns tuple (response, status_code)
        mock_get_config.return_value = (expected_config, 200)

        result, status = handle_get_animal_config(animal_id)

        assert result == expected_config
        assert status == 200
        mock_get_config.assert_called_once_with(animal_id)

    @patch('openapi_server.impl.animals.handle_animal_config_patch')
    def test_handle_update_animal_config_success(self, mock_patch_config):
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

        # Mock returns tuple (response, status_code)
        mock_patch_config.return_value = (updated_config, 200)

        result, status = handle_update_animal_config(animal_id, config_data)

        assert result == updated_config
        assert status == 200
        mock_patch_config.assert_called_once_with(animal_id, config_data)


class TestAnimalsBoundaryValues:
    """Test animal functions with boundary values."""

    @patch('openapi_server.impl.animals.handle_animal_get')
    def test_empty_animal_id(self, mock_get):
        """Test with empty animal ID."""
        # Mock returns validation error for empty ID
        mock_get.return_value = ({'error': 'Invalid animal ID'}, 400)

        result, status = handle_get_animal("")
        assert status == 400
        assert 'error' in result

    @patch('openapi_server.impl.animals.handle_animal_get')
    def test_none_animal_id(self, mock_get):
        """Test with None animal ID."""
        # Mock returns validation error for None ID
        mock_get.return_value = ({'error': 'Animal ID is required'}, 400)

        result, status = handle_get_animal(None)
        assert status == 400
        assert 'error' in result

    @patch('openapi_server.impl.animals.handle_animal_list_get')
    def test_invalid_status_filter(self, mock_list):
        """Test with invalid status filter."""
        # Mock returns validation error for invalid status
        mock_list.return_value = ({'error': 'Invalid status filter'}, 400)

        result, status = handle_list_animals("invalid_status_that_doesnt_exist")
        assert status == 400
        assert 'error' in result