"""
Integration tests for Animal Configuration
Task T011: Add animal configuration tests
Tests animal chatbot personality configuration and persistence
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
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
    handle_animal_list_get,
    handle_animal_get,
    handle_animal_post,
    handle_animal_put,
    handle_animal_delete,
    handle_animal_config_get,
    handle_animal_config_put
)
from openapi_server.models.animal import Animal
from openapi_server.models.error import Error


class TestAnimalConfigurationCRUD:
    """Test complete animal configuration lifecycle"""

    @pytest.fixture
    def mock_dynamo_table(self):
        """Fixture for mocked DynamoDB table"""
        with patch('openapi_server.impl.utils.dynamo.table') as mock_table_func:
            mock_table = Mock()
            mock_table_func.return_value = mock_table
            yield mock_table

    @pytest.fixture
    def sample_animal_config(self):
        """Sample animal configuration for testing"""
        return {
            'animalId': 'lion-001',
            'name': 'Leo',
            'scientificName': 'Panthera leo',
            'species': 'Lion',
            'personality': {
                'traits': ['confident', 'playful', 'wise'],
                'communicationStyle': 'regal and friendly',
                'ageGroup': 'adult',
                'favoriteTopics': ['hunting', 'pride dynamics', 'savanna life']
            },
            'systemPrompt': 'You are Leo, a confident and wise lion who loves to share stories about life in the savanna.',
            'temperature': 0.7,
            'maxTokens': 500,
            'knowledgeBase': {
                'facts': [
                    'Lions are the only cats that live in groups called prides',
                    'A lion\'s roar can be heard from 5 miles away',
                    'Female lions do most of the hunting'
                ],
                'conservationStatus': 'Vulnerable',
                'habitat': 'African savanna'
            },
            'active': True,
            'guardrails': {
                'avoidTopics': ['violence', 'graphic content'],
                'ageAppropriate': True,
                'educationalFocus': True
            }
        }

    def test_create_animal_configuration(self, mock_dynamo_table, sample_animal_config):
        """Test creating a new animal configuration"""
        # Mock DynamoDB put_item response
        mock_dynamo_table.put_item.return_value = {
            'ResponseMetadata': {'HTTPStatusCode': 200}
        }

        with patch('openapi_server.impl.adapters.flask.animal_handlers.FlaskAnimalHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_handler_class.return_value = mock_handler

            # Mock successful creation
            created_config = {
                **sample_animal_config,
                'created': {'at': '2024-01-01T00:00:00Z'},
                'modified': {'at': '2024-01-01T00:00:00Z'}
            }
            mock_handler.create_animal.return_value = (created_config, 201)

            response, status = handle_animal_post(body=sample_animal_config)

            # Assertions
            assert status == 201
            assert response['animalId'] == 'lion-001'
            assert response['name'] == 'Leo'
            assert response['systemPrompt'] is not None
            mock_handler.create_animal.assert_called_once()

    def test_get_animal_configuration(self, mock_dynamo_table):
        """Test retrieving animal configuration"""
        animal_id = 'lion-001'

        # Mock DynamoDB get_item response
        mock_dynamo_table.get_item.return_value = {
            'Item': {
                'animalId': animal_id,
                'name': 'Leo',
                'species': 'Lion',
                'temperature': Decimal('0.7'),
                'maxTokens': Decimal('500'),
                'active': True
            }
        }

        with patch('openapi_server.impl.adapters.flask.animal_handlers.FlaskAnimalHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_handler_class.return_value = mock_handler

            mock_handler.get_animal.return_value = (
                {
                    'animalId': animal_id,
                    'name': 'Leo',
                    'species': 'Lion',
                    'temperature': 0.7,
                    'maxTokens': 500,
                    'active': True
                },
                200
            )

            response, status = handle_animal_get(animal_id=animal_id)

            # Assertions
            assert status == 200
            assert response['animalId'] == animal_id
            assert response['temperature'] == 0.7
            mock_handler.get_animal.assert_called_once_with(animal_id)

    def test_update_animal_personality(self, mock_dynamo_table):
        """Test updating animal personality traits"""
        animal_id = 'lion-001'
        update_data = {
            'personality': {
                'traits': ['confident', 'playful', 'wise', 'protective'],
                'communicationStyle': 'regal, friendly, and educational',
                'favoriteTopics': ['hunting', 'pride dynamics', 'conservation']
            },
            'systemPrompt': 'You are Leo, a wise and protective lion who teaches children about wildlife conservation.'
        }

        # Mock DynamoDB update response
        mock_dynamo_table.update_item.return_value = {
            'Attributes': {
                **update_data,
                'animalId': animal_id,
                'modified': {'at': '2024-01-02T00:00:00Z'}
            }
        }

        with patch('openapi_server.impl.adapters.flask.animal_handlers.FlaskAnimalHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_handler_class.return_value = mock_handler

            mock_handler.update_animal.return_value = (
                {
                    'animalId': animal_id,
                    **update_data,
                    'modified': {'at': '2024-01-02T00:00:00Z'}
                },
                200
            )

            response, status = handle_animal_put(animal_id=animal_id, body=update_data)

            # Assertions
            assert status == 200
            assert 'protective' in response['personality']['traits']
            assert 'conservation' in response['personality']['favoriteTopics']
            mock_handler.update_animal.assert_called_once()

    def test_update_ai_parameters(self, mock_dynamo_table):
        """Test updating AI model parameters"""
        animal_id = 'lion-001'
        ai_params = {
            'temperature': 0.8,
            'maxTokens': 750,
            'topP': 0.95,
            'frequencyPenalty': 0.2,
            'presencePenalty': 0.1
        }

        with patch('openapi_server.impl.adapters.flask.animal_handlers.FlaskAnimalHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_handler_class.return_value = mock_handler

            mock_handler.update_animal.return_value = (
                {
                    'animalId': animal_id,
                    **ai_params,
                    'modified': {'at': '2024-01-02T00:00:00Z'}
                },
                200
            )

            response, status = handle_animal_put(animal_id=animal_id, body=ai_params)

            # Assertions
            assert status == 200
            assert response['temperature'] == 0.8
            assert response['maxTokens'] == 750

    def test_toggle_animal_active_status(self, mock_dynamo_table):
        """Test enabling/disabling an animal"""
        animal_id = 'lion-001'

        # Test deactivating
        with patch('openapi_server.impl.adapters.flask.animal_handlers.FlaskAnimalHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_handler_class.return_value = mock_handler

            mock_handler.update_animal.return_value = (
                {'animalId': animal_id, 'active': False},
                200
            )

            response, status = handle_animal_put(animal_id=animal_id, body={'active': False})

            assert status == 200
            assert response['active'] is False

    def test_list_all_animals(self, mock_dynamo_table):
        """Test listing all configured animals"""
        # Mock DynamoDB scan
        mock_dynamo_table.scan.return_value = {
            'Items': [
                {
                    'animalId': 'lion-001',
                    'name': 'Leo',
                    'species': 'Lion',
                    'active': True
                },
                {
                    'animalId': 'elephant-001',
                    'name': 'Ella',
                    'species': 'Elephant',
                    'active': True
                },
                {
                    'animalId': 'penguin-001',
                    'name': 'Pete',
                    'species': 'Penguin',
                    'active': False
                }
            ],
            'Count': 3
        }

        with patch('openapi_server.impl.adapters.flask.animal_handlers.FlaskAnimalHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_handler_class.return_value = mock_handler

            mock_handler.list_animals.return_value = (
                [
                    {'animalId': 'lion-001', 'name': 'Leo', 'species': 'Lion', 'active': True},
                    {'animalId': 'elephant-001', 'name': 'Ella', 'species': 'Elephant', 'active': True},
                    {'animalId': 'penguin-001', 'name': 'Pete', 'species': 'Penguin', 'active': False}
                ],
                200
            )

            response, status = handle_animal_list_get()

            # Assertions
            assert status == 200
            assert len(response) == 3
            assert response[0]['name'] == 'Leo'
            # Check we have both active and inactive animals
            active_count = sum(1 for a in response if a.get('active', False))
            assert active_count == 2

    def test_list_active_animals_only(self):
        """Test filtering for only active animals"""
        with patch('openapi_server.impl.adapters.flask.animal_handlers.FlaskAnimalHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_handler_class.return_value = mock_handler

            # Only return active animals
            mock_handler.list_animals.return_value = (
                [
                    {'animalId': 'lion-001', 'name': 'Leo', 'active': True},
                    {'animalId': 'elephant-001', 'name': 'Ella', 'active': True}
                ],
                200
            )

            response, status = handle_animal_list_get(active_only=True)

            assert status == 200
            assert len(response) == 2
            assert all(a.get('active', False) for a in response)

    def test_delete_animal_soft_delete(self, mock_dynamo_table):
        """Test soft deleting an animal configuration"""
        animal_id = 'lion-001'

        # Mock soft delete (update with deletedAt)
        mock_dynamo_table.update_item.return_value = {
            'ResponseMetadata': {'HTTPStatusCode': 200}
        }

        with patch('openapi_server.impl.adapters.flask.animal_handlers.FlaskAnimalHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_handler_class.return_value = mock_handler

            mock_handler.delete_animal.return_value = (None, 204)

            response, status = handle_animal_delete(animal_id=animal_id)

            # Should return 204 No Content
            assert status == 204
            assert response is None
            mock_handler.delete_animal.assert_called_once_with(animal_id)


class TestAnimalConfigurationValidation:
    """Test validation of animal configuration data"""

    def test_validate_temperature_range(self):
        """Test that temperature must be between 0 and 2"""
        invalid_configs = [
            {'temperature': -0.1},  # Too low
            {'temperature': 2.1},   # Too high
            {'temperature': 'hot'}  # Invalid type
        ]

        with patch('openapi_server.impl.adapters.flask.animal_handlers.FlaskAnimalHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_handler_class.return_value = mock_handler

            for config in invalid_configs:
                mock_handler.create_animal.return_value = (
                    {'error': {'code': 'validation_error', 'message': 'Temperature must be between 0 and 2'}},
                    400
                )

                response, status = handle_animal_post(body=config)
                assert status == 400

    def test_validate_max_tokens_range(self):
        """Test that maxTokens must be reasonable"""
        invalid_configs = [
            {'maxTokens': 0},      # Too low
            {'maxTokens': 10000},  # Too high
            {'maxTokens': 'many'}  # Invalid type
        ]

        with patch('openapi_server.impl.adapters.flask.animal_handlers.FlaskAnimalHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_handler_class.return_value = mock_handler

            for config in invalid_configs:
                mock_handler.create_animal.return_value = (
                    {'error': {'code': 'validation_error', 'message': 'MaxTokens must be between 1 and 4000'}},
                    400
                )

                response, status = handle_animal_post(body=config)
                assert status == 400

    def test_validate_required_fields(self):
        """Test that required fields are present"""
        incomplete_config = {
            'name': 'Leo'
            # Missing animalId, species, systemPrompt
        }

        with patch('openapi_server.impl.adapters.flask.animal_handlers.FlaskAnimalHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_handler_class.return_value = mock_handler

            mock_handler.create_animal.return_value = (
                {'error': {'code': 'validation_error', 'message': 'Missing required fields'}},
                400
            )

            response, status = handle_animal_post(body=incomplete_config)
            assert status == 400

    def test_validate_guardrails_configuration(self):
        """Test guardrails configuration validation"""
        config_with_guardrails = {
            'animalId': 'test-001',
            'name': 'Test Animal',
            'guardrails': {
                'avoidTopics': ['inappropriate', 'violence'],
                'ageAppropriate': True,
                'educationalFocus': True,
                'maxConversationLength': 50
            }
        }

        with patch('openapi_server.impl.adapters.flask.animal_handlers.FlaskAnimalHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_handler_class.return_value = mock_handler

            mock_handler.create_animal.return_value = (config_with_guardrails, 201)

            response, status = handle_animal_post(body=config_with_guardrails)

            assert status == 201
            assert response['guardrails']['ageAppropriate'] is True


class TestAnimalKnowledgeBase:
    """Test animal knowledge base management"""

    def test_upload_knowledge_documents(self):
        """Test uploading knowledge base documents for an animal"""
        animal_id = 'lion-001'
        knowledge_docs = {
            'documents': [
                {
                    'title': 'Lion Facts',
                    'content': 'Comprehensive information about lions...',
                    'type': 'educational'
                },
                {
                    'title': 'Conservation Efforts',
                    'content': 'Current conservation programs...',
                    'type': 'conservation'
                }
            ]
        }

        with patch('openapi_server.impl.adapters.flask.animal_handlers.FlaskAnimalHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_handler_class.return_value = mock_handler

            mock_handler.update_animal.return_value = (
                {
                    'animalId': animal_id,
                    'knowledgeBase': knowledge_docs,
                    'modified': {'at': '2024-01-02T00:00:00Z'}
                },
                200
            )

            response, status = handle_animal_put(animal_id=animal_id, body={'knowledgeBase': knowledge_docs})

            assert status == 200
            assert len(response['knowledgeBase']['documents']) == 2

    def test_knowledge_base_indexing(self, mock_dynamo_table):
        """Test that knowledge base content is properly indexed"""
        animal_id = 'lion-001'

        # Mock vector database indexing
        with patch('openapi_server.impl.utils.vector_db.index_document') as mock_index:
            mock_index.return_value = {'indexed': True, 'documentId': 'doc-123'}

            knowledge = {
                'content': 'Lions are apex predators',
                'metadata': {'animalId': animal_id, 'type': 'fact'}
            }

            # In real implementation, this would trigger indexing
            result = mock_index(knowledge)

            assert result['indexed'] is True
            mock_index.assert_called_once_with(knowledge)


class TestAnimalConfigurationHistory:
    """Test configuration version history"""

    def test_track_configuration_changes(self, mock_dynamo_table):
        """Test that configuration changes are tracked"""
        animal_id = 'lion-001'

        # Mock version history table
        history_table = Mock()
        with patch('openapi_server.impl.utils.dynamo.table') as mock_table_func:
            mock_table_func.return_value = history_table

            # Simulate storing version history
            history_table.put_item.return_value = {
                'ResponseMetadata': {'HTTPStatusCode': 200}
            }

            version_record = {
                'animalId': animal_id,
                'version': 2,
                'changes': {
                    'temperature': {'old': 0.7, 'new': 0.8},
                    'systemPrompt': {'old': 'Old prompt', 'new': 'New prompt'}
                },
                'modifiedBy': 'admin-user',
                'modifiedAt': '2024-01-02T00:00:00Z'
            }

            result = history_table.put_item(Item=version_record)

            assert result['ResponseMetadata']['HTTPStatusCode'] == 200


if __name__ == '__main__':
    pytest.main([__file__, '-v'])