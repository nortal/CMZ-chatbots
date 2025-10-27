"""
Integration tests for Assistant-Animal relationship and cross-service functionality

Tests the integration between assistants, animals, personalities, and guardrails
to ensure the complete assistant management system works correctly.
"""

import pytest
import uuid
from datetime import datetime
from unittest.mock import patch, MagicMock

# Import the implementation modules
from openapi_server.impl import assistants, animals
from openapi_server.impl.utils.dynamo import table, to_ddb, from_ddb


@pytest.fixture
def mock_animal_data():
    """Mock animal data for integration testing"""
    return {
        "animalId": "test-tiger-001",
        "name": "Bella the Tiger",
        "species": "Panthera tigris",
        "scientificName": "Panthera tigris",
        "habitat": "Asian Forest",
        "status": "active",
        "created": {"at": "2025-10-23T00:00:00Z", "by": "test@cmz.org"},
        "modified": {"at": "2025-10-23T00:00:00Z", "by": "test@cmz.org"}
    }


@pytest.fixture
def mock_personality_data():
    """Mock personality data for integration testing"""
    return {
        "personalityId": "test-personality-001",
        "name": "Friendly and Educational",
        "description": "A warm, friendly personality focused on education",
        "systemPrompt": "You are a friendly tiger who loves teaching children about conservation.",
        "traits": ["friendly", "educational", "patient"],
        "status": "active",
        "created": {"at": "2025-10-23T00:00:00Z", "by": "test@cmz.org"}
    }


@pytest.fixture
def mock_guardrail_data():
    """Mock guardrail data for integration testing"""
    return {
        "guardrailId": "test-guardrail-001",
        "name": "Basic Safety",
        "description": "Basic safety rules for animal assistants",
        "rules": ["No personal information requests", "Keep conversations family-friendly"],
        "priority": 1,
        "status": "active",
        "created": {"at": "2025-10-23T00:00:00Z", "by": "test@cmz.org"}
    }


@pytest.fixture
def mock_assistant_data(mock_animal_data, mock_personality_data, mock_guardrail_data):
    """Mock assistant data that references animal, personality, and guardrail"""
    return {
        "name": "Bella's Assistant",
        "animalId": mock_animal_data["animalId"],
        "personalityId": mock_personality_data["personalityId"],
        "guardrailId": mock_guardrail_data["guardrailId"],
        "description": "Interactive assistant for Bella the Tiger",
        "status": "active"
    }


class TestAssistantAnimalIntegration:
    """Test integration between assistants and animals"""

    @patch('openapi_server.impl.assistants._table')
    @patch('openapi_server.impl.utils.dynamo.table')
    def test_assistant_creation_with_valid_animal_reference(self, mock_table, mock_assistant_table, mock_assistant_data):
        """Test that assistant creation properly validates animal reference"""
        # Mock successful table operations
        mock_table.return_value.get_item.return_value = {'Item': to_ddb({'animalId': 'test-tiger-001', 'status': 'active'})}
        mock_assistant_table.return_value.put_item.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        mock_assistant_table.return_value.get_item.return_value = {'Item': to_ddb({'assistantId': 'test-assistant-001'})}

        # Create assistant with valid animal reference
        result, status_code = assistants.create_assistant(mock_assistant_data)

        # Verify successful creation
        assert status_code == 201
        assert result['animalId'] == mock_assistant_data['animalId']

        # Verify animal lookup was performed
        mock_table.return_value.get_item.assert_called()

    @patch('openapi_server.impl.assistants._table')
    @patch('openapi_server.impl.utils.dynamo.table')
    def test_assistant_creation_with_invalid_animal_reference(self, mock_table, mock_assistant_table, mock_assistant_data):
        """Test that assistant creation fails with invalid animal reference"""
        # Mock animal not found
        mock_table.return_value.get_item.return_value = {}

        # Attempt to create assistant with invalid animal reference
        mock_assistant_data['animalId'] = 'nonexistent-animal'
        result, status_code = assistants.create_assistant(mock_assistant_data)

        # Verify creation failed due to invalid animal reference
        assert status_code == 400
        assert 'error' in result
        assert 'animal' in result['error'].lower()

    @patch('openapi_server.impl.assistants._table')
    @patch('openapi_server.impl.utils.dynamo.table')
    def test_get_assistant_by_animal(self, mock_table, mock_assistant_table):
        """Test retrieving assistant by animal ID"""
        # Mock assistant data with animal reference
        assistant_data = {
            'assistantId': 'test-assistant-001',
            'animalId': 'test-tiger-001',
            'name': 'Bella\'s Assistant',
            'status': 'active'
        }

        # Mock DynamoDB query response
        mock_assistant_table.return_value.query.return_value = {
            'Items': [to_ddb(assistant_data)]
        }

        # Get assistant by animal ID
        result, status_code = assistants.get_assistant_by_animal('test-tiger-001')

        # Verify successful retrieval
        assert status_code == 200
        assert 'assistants' in result
        assert len(result['assistants']) == 1
        assert result['assistants'][0]['animalId'] == 'test-tiger-001'

    @patch('openapi_server.impl.assistants._table')
    def test_assistant_animal_relationship_consistency(self, mock_assistant_table):
        """Test that assistant-animal relationships maintain consistency"""
        # Mock multiple assistants for the same animal
        assistants_data = [
            {'assistantId': 'assistant-1', 'animalId': 'tiger-001', 'status': 'active'},
            {'assistantId': 'assistant-2', 'animalId': 'tiger-001', 'status': 'draft'},
            {'assistantId': 'assistant-3', 'animalId': 'tiger-001', 'status': 'archived'}
        ]

        mock_assistant_table.return_value.query.return_value = {
            'Items': [to_ddb(data) for data in assistants_data]
        }

        # Get all assistants for animal
        result, status_code = assistants.get_assistant_by_animal('tiger-001')

        # Verify all assistants are returned
        assert status_code == 200
        assert len(result['assistants']) == 3

        # Verify all have consistent animal reference
        for assistant in result['assistants']:
            assert assistant['animalId'] == 'tiger-001'


class TestAssistantPersonalityIntegration:
    """Test integration between assistants and personalities"""

    @patch('openapi_server.impl.assistants._table')
    @patch('openapi_server.impl.utils.dynamo.table')
    def test_assistant_personality_reference_validation(self, mock_table, mock_assistant_table, mock_assistant_data):
        """Test that assistant creation validates personality reference"""
        # Mock personality exists
        mock_table.return_value.get_item.return_value = {'Item': to_ddb({'personalityId': 'test-personality-001'})}
        mock_assistant_table.return_value.put_item.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        mock_assistant_table.return_value.get_item.return_value = {'Item': to_ddb({'assistantId': 'test-assistant-001'})}

        # Create assistant
        result, status_code = assistants.create_assistant(mock_assistant_data)

        # Verify successful creation with personality reference
        assert status_code == 201
        assert result['personalityId'] == mock_assistant_data['personalityId']


class TestAssistantGuardrailIntegration:
    """Test integration between assistants and guardrails"""

    @patch('openapi_server.impl.assistants._table')
    @patch('openapi_server.impl.utils.dynamo.table')
    def test_assistant_guardrail_reference_validation(self, mock_table, mock_assistant_table, mock_assistant_data):
        """Test that assistant creation validates guardrail reference"""
        # Mock guardrail exists
        mock_table.return_value.get_item.return_value = {'Item': to_ddb({'guardrailId': 'test-guardrail-001'})}
        mock_assistant_table.return_value.put_item.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        mock_assistant_table.return_value.get_item.return_value = {'Item': to_ddb({'assistantId': 'test-assistant-001'})}

        # Create assistant
        result, status_code = assistants.create_assistant(mock_assistant_data)

        # Verify successful creation with guardrail reference
        assert status_code == 201
        assert result['guardrailId'] == mock_assistant_data['guardrailId']


class TestCompleteAssistantWorkflow:
    """Test complete assistant workflow with all dependencies"""

    @patch('openapi_server.impl.assistants._table')
    @patch('openapi_server.impl.utils.dynamo.table')
    @patch('openapi_server.impl.assistants.merge_personality_and_guardrails')
    def test_end_to_end_assistant_creation_workflow(self, mock_merge, mock_table, mock_assistant_table,
                                                   mock_assistant_data, mock_personality_data, mock_guardrail_data):
        """Test complete assistant creation with personality and guardrail integration"""
        # Mock all dependencies exist
        def mock_get_item_side_effect(Key):
            if 'animalId' in Key:
                return {'Item': to_ddb({'animalId': Key['animalId'], 'status': 'active'})}
            elif 'personalityId' in Key:
                return {'Item': to_ddb(mock_personality_data)}
            elif 'guardrailId' in Key:
                return {'Item': to_ddb(mock_guardrail_data)}
            return {}

        mock_table.return_value.get_item.side_effect = mock_get_item_side_effect
        mock_assistant_table.return_value.put_item.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        mock_assistant_table.return_value.get_item.return_value = {
            'Item': to_ddb({
                'assistantId': 'test-assistant-001',
                **mock_assistant_data,
                'mergedPrompt': 'Test merged prompt'
            })
        }

        # Mock prompt merging
        mock_merge.return_value = "Test merged prompt"

        # Create assistant
        result, status_code = assistants.create_assistant(mock_assistant_data)

        # Verify successful creation
        assert status_code == 201
        assert 'assistantId' in result
        assert result['animalId'] == mock_assistant_data['animalId']
        assert result['personalityId'] == mock_assistant_data['personalityId']
        assert result['guardrailId'] == mock_assistant_data['guardrailId']

        # Verify prompt merging was called
        mock_merge.assert_called_once()

    @patch('openapi_server.impl.assistants._table')
    def test_assistant_status_lifecycle(self, mock_assistant_table):
        """Test assistant status changes throughout lifecycle"""
        assistant_id = 'test-assistant-001'

        # Mock assistant exists
        assistant_data = {
            'assistantId': assistant_id,
            'animalId': 'tiger-001',
            'status': 'draft'
        }
        mock_assistant_table.return_value.get_item.return_value = {'Item': to_ddb(assistant_data)}
        mock_assistant_table.return_value.update_item.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}

        # Update assistant status to active
        update_data = {'status': 'active'}
        result, status_code = assistants.update_assistant(assistant_id, update_data)

        # Verify status update
        assert status_code == 200
        mock_assistant_table.return_value.update_item.assert_called()


if __name__ == '__main__':
    pytest.main([__file__])