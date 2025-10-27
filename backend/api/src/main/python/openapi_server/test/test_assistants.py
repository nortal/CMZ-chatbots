"""
Unit tests for assistant creation and management functionality.
Tests the CRUD operations for Animal Assistant entities.

Test-Driven Development (TDD) approach:
- These tests MUST FAIL initially before implementation
- Implement models and services to make tests pass
- Refactor while maintaining test success
"""

import pytest
import uuid
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from openapi_server.impl.assistants import (
    create_assistant,
    get_assistant,
    update_assistant,
    delete_assistant,
    list_assistants
)
from openapi_server.impl.utils.dynamo import error_response


class TestAssistantCreation:
    """Test suite for assistant creation functionality."""

    def setup_method(self):
        """Set up test data before each test."""
        self.valid_assistant_data = {
            "animalId": "animal_123",
            "personalityId": "personality_456",
            "guardrailId": "guardrail_789",
            "knowledgeBaseFileIds": ["file_001", "file_002"],
            "status": "ACTIVE"
        }

        self.expected_merged_prompt = """You are a friendly zoo animal assistant.

Personality: You are playful and educational.
Guardrails: Always be appropriate for children.

Combined system prompt ready for OpenAI."""

    @patch('openapi_server.impl.assistants._table')
    @patch('openapi_server.impl.assistants.merge_personality_and_guardrails')
    def test_create_assistant_success(self, mock_merge, mock_table):
        """Test successful assistant creation with all required fields."""
        # Arrange
        mock_merge.return_value = self.expected_merged_prompt
        mock_table.return_value.put_item.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}

        # Act
        result, status_code = create_assistant(self.valid_assistant_data)

        # Assert
        assert status_code == 201
        assert "assistantId" in result
        assert result["animalId"] == "animal_123"
        assert result["personalityId"] == "personality_456"
        assert result["guardrailId"] == "guardrail_789"
        assert result["mergedPrompt"] == self.expected_merged_prompt
        assert result["status"] == "ACTIVE"
        assert "created" in result
        assert "modified" in result

        # Verify prompt merging was called
        mock_merge.assert_called_once_with("personality_456", "guardrail_789")

        # Verify DynamoDB put_item was called
        mock_table.return_value.put_item.assert_called_once()

    def test_create_assistant_missing_required_fields(self):
        """Test assistant creation fails with missing required fields."""
        # Test missing animalId
        invalid_data = self.valid_assistant_data.copy()
        del invalid_data["animalId"]

        result, status_code = create_assistant(invalid_data)
        assert status_code == 400
        assert "error" in result
        assert "animalId" in result["error"]

        # Test missing personalityId
        invalid_data = self.valid_assistant_data.copy()
        del invalid_data["personalityId"]

        result, status_code = create_assistant(invalid_data)
        assert status_code == 400
        assert "error" in result
        assert "personalityId" in result["error"]

    @patch('openapi_server.impl.assistants._table')
    @patch('openapi_server.impl.assistants.merge_personality_and_guardrails')
    def test_create_assistant_duplicate_animal(self, mock_merge, mock_table):
        """Test assistant creation fails when animal already has an assistant."""
        # Arrange - simulate successful prompt merging but duplicate assistant
        mock_merge.return_value = self.expected_merged_prompt
        from botocore.exceptions import ClientError
        mock_table.return_value.put_item.side_effect = ClientError(
            error_response={
                'Error': {
                    'Code': 'ConditionalCheckFailedException',
                    'Message': 'Item already exists'
                }
            },
            operation_name='PutItem'
        )

        # Act
        result, status_code = create_assistant(self.valid_assistant_data)

        # Assert
        assert status_code == 409
        assert "error" in result
        assert "already exists" in result["error"]

    @patch('openapi_server.impl.assistants._table')
    def test_get_assistant_success(self, mock_table):
        """Test successful assistant retrieval by ID."""
        # Arrange
        assistant_id = str(uuid.uuid4())
        mock_item = {
            'assistantId': {'S': assistant_id},
            'animalId': {'S': 'animal_123'},
            'personalityId': {'S': 'personality_456'},
            'guardrailId': {'S': 'guardrail_789'},
            'mergedPrompt': {'S': self.expected_merged_prompt},
            'status': {'S': 'ACTIVE'},
            'created': {'M': {'at': {'S': '2025-10-23T10:00:00Z'}}},
            'modified': {'M': {'at': {'S': '2025-10-23T10:00:00Z'}}}
        }
        mock_table.return_value.get_item.return_value = {'Item': mock_item}

        # Act
        result, status_code = get_assistant(assistant_id)

        # Assert
        assert status_code == 200
        assert result["assistantId"] == assistant_id
        assert result["animalId"] == "animal_123"
        assert result["mergedPrompt"] == self.expected_merged_prompt

    @patch('openapi_server.impl.assistants._table')
    def test_get_assistant_not_found(self, mock_table):
        """Test assistant retrieval when assistant doesn't exist."""
        # Arrange
        assistant_id = str(uuid.uuid4())
        mock_table.return_value.get_item.return_value = {}

        # Act
        result, status_code = get_assistant(assistant_id)

        # Assert
        assert status_code == 404
        assert "error" in result
        assert "not found" in result["error"]

    @patch('openapi_server.impl.assistants._table')
    @patch('openapi_server.impl.assistants.merge_personality_and_guardrails')
    def test_update_assistant_success(self, mock_merge, mock_table):
        """Test successful assistant update with prompt regeneration."""
        # Arrange
        assistant_id = str(uuid.uuid4())
        update_data = {
            "personalityId": "new_personality_789",
            "status": "INACTIVE"
        }
        new_merged_prompt = "Updated merged prompt with new personality"
        mock_merge.return_value = new_merged_prompt

        # Mock existing item
        existing_item = {
            'assistantId': {'S': assistant_id},
            'animalId': {'S': 'animal_123'},
            'personalityId': {'S': 'personality_456'},
            'guardrailId': {'S': 'guardrail_789'}
        }
        mock_table.return_value.get_item.return_value = {'Item': existing_item}
        mock_table.return_value.put_item.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}

        # Act
        result, status_code = update_assistant(assistant_id, update_data)

        # Assert
        assert status_code == 200
        assert result["personalityId"] == "new_personality_789"
        assert result["status"] == "INACTIVE"
        assert result["mergedPrompt"] == new_merged_prompt

        # Verify prompt was regenerated
        mock_merge.assert_called_once_with("new_personality_789", "guardrail_789")

    @patch('openapi_server.impl.assistants._table')
    def test_delete_assistant_success(self, mock_table):
        """Test successful assistant deletion."""
        # Arrange
        assistant_id = str(uuid.uuid4())
        mock_table.return_value.delete_item.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}

        # Act
        result, status_code = delete_assistant(assistant_id)

        # Assert
        assert status_code == 204
        mock_table.return_value.delete_item.assert_called_once_with(
            Key={'assistantId': assistant_id}
        )

    @patch('openapi_server.impl.assistants._table')
    def test_list_assistants_success(self, mock_table):
        """Test successful listing of all assistants."""
        # Arrange
        mock_items = [
            {
                'assistantId': {'S': 'assistant_1'},
                'animalId': {'S': 'animal_123'},
                'status': {'S': 'ACTIVE'}
            },
            {
                'assistantId': {'S': 'assistant_2'},
                'animalId': {'S': 'animal_456'},
                'status': {'S': 'INACTIVE'}
            }
        ]
        mock_table.return_value.scan.return_value = {'Items': mock_items}

        # Act
        result, status_code = list_assistants()

        # Assert
        assert status_code == 200
        assert "assistants" in result
        assert len(result["assistants"]) == 2
        assert result["assistants"][0]["assistantId"] == "assistant_1"
        assert result["assistants"][1]["assistantId"] == "assistant_2"


class TestPromptMerging:
    """Test suite for personality and guardrail prompt merging."""

    @patch('openapi_server.impl.assistants.get_personality')
    @patch('openapi_server.impl.assistants.get_guardrail')
    def test_merge_personality_and_guardrails_success(self, mock_get_guardrail, mock_get_personality):
        """Test successful merging of personality and guardrail prompts."""
        from openapi_server.impl.assistants import merge_personality_and_guardrails

        # Arrange
        mock_personality = {
            "name": "Playful Educator",
            "systemPrompt": "You are a playful and educational assistant.",
            "traits": ["friendly", "curious"]
        }
        mock_guardrail = {
            "name": "Child Safety",
            "rules": ["Keep content appropriate for children", "No scary topics"],
            "systemPrompt": "Always maintain child-appropriate content."
        }

        mock_get_personality.return_value = (mock_personality, 200)
        mock_get_guardrail.return_value = (mock_guardrail, 200)

        # Act
        result = merge_personality_and_guardrails("personality_123", "guardrail_456")

        # Assert
        assert "playful and educational" in result
        assert "child-appropriate content" in result
        assert isinstance(result, str)
        assert len(result) > 100  # Ensure substantial merged prompt

        # Verify dependencies were called
        mock_get_personality.assert_called_once_with("personality_123")
        mock_get_guardrail.assert_called_once_with("guardrail_456")

    @patch('openapi_server.impl.assistants.get_personality')
    def test_merge_personality_and_guardrails_personality_not_found(self, mock_get_personality):
        """Test merging fails when personality doesn't exist."""
        from openapi_server.impl.assistants import merge_personality_and_guardrails

        # Arrange
        mock_get_personality.return_value = ({"error": "not found"}, 404)

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            merge_personality_and_guardrails("invalid_personality", "guardrail_456")

        assert "personality not found" in str(exc_info.value)


class TestAssistantValidation:
    """Test suite for assistant data validation."""

    def test_validate_assistant_data_success(self):
        """Test successful validation of assistant data."""
        from openapi_server.impl.assistants import validate_assistant_data

        valid_data = {
            "animalId": "animal_123",
            "personalityId": "personality_456",
            "guardrailId": "guardrail_789",
            "knowledgeBaseFileIds": ["file_001"],
            "status": "ACTIVE"
        }

        # Should not raise exception
        validate_assistant_data(valid_data)

    def test_validate_assistant_data_invalid_status(self):
        """Test validation fails with invalid status."""
        from openapi_server.impl.assistants import validate_assistant_data

        invalid_data = {
            "animalId": "animal_123",
            "personalityId": "personality_456",
            "guardrailId": "guardrail_789",
            "status": "INVALID_STATUS"
        }

        with pytest.raises(ValueError) as exc_info:
            validate_assistant_data(invalid_data)

        assert "status" in str(exc_info.value)

    def test_validate_assistant_data_too_many_knowledge_files(self):
        """Test validation fails with too many knowledge base files."""
        from openapi_server.impl.assistants import validate_assistant_data

        invalid_data = {
            "animalId": "animal_123",
            "personalityId": "personality_456",
            "guardrailId": "guardrail_789",
            "knowledgeBaseFileIds": [f"file_{i}" for i in range(51)],  # Max is 50
            "status": "ACTIVE"
        }

        with pytest.raises(ValueError) as exc_info:
            validate_assistant_data(invalid_data)

        assert "50 knowledge base files" in str(exc_info.value)