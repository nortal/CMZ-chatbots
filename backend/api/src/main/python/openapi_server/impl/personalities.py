"""
Personality Management Implementation Module

Provides CRUD operations for managing animal personality configurations.
Integrates with the animal assistant system for prompt merging.

This is a basic implementation to support the TDD workflow for assistants.
"""

import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from botocore.exceptions import ClientError

from .utils.dynamo import table, to_ddb, from_ddb, now_iso, error_response, not_found


# DynamoDB table configuration
PERSONALITY_TABLE_NAME = os.getenv('PERSONALITY_DYNAMO_TABLE_NAME', 'quest-dev-personality')
PERSONALITY_PK_NAME = os.getenv('PERSONALITY_DYNAMO_PK_NAME', 'personalityId')


def _table():
    """Get DynamoDB table reference for personalities."""
    return table(PERSONALITY_TABLE_NAME)


def get_personality(personality_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Retrieve a personality by ID.

    Args:
        personality_id: The personality ID

    Returns:
        Tuple of (personality_data, status_code)
    """
    try:
        response = _table().get_item(
            Key={PERSONALITY_PK_NAME: personality_id}
        )

        if 'Item' not in response:
            return not_found("Personality")

        personality_data = from_ddb(response['Item'])
        return personality_data, 200

    except ClientError as e:
        return error_response(e)
    except Exception as e:
        return {"error": f"Failed to retrieve personality: {str(e)}"}, 500


def create_personality(body: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    """
    Create a new personality configuration.

    Args:
        body: Personality creation data

    Returns:
        Tuple of (response_data, status_code)
    """
    try:
        # Generate unique personality ID
        personality_id = str(uuid.uuid4())

        # Prepare personality item
        personality_item = {
            'personalityId': personality_id,
            'name': body.get('name', 'Default Personality'),
            'systemPrompt': body.get('systemPrompt', ''),
            'traits': body.get('traits', []),
            'communicationStyle': body.get('communicationStyle', ''),
            'knowledge': body.get('knowledge', ''),
            'created': {'at': now_iso()},
            'modified': {'at': now_iso()}
        }

        # Save to DynamoDB
        _table().put_item(
            Item=to_ddb(personality_item),
            ConditionExpression='attribute_not_exists(personalityId)'
        )

        return personality_item, 201

    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return {"error": "Personality already exists"}, 409
        return error_response(e)
    except Exception as e:
        return {"error": f"Failed to create personality: {str(e)}"}, 500


def update_personality(personality_id: str, body: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    """
    Update an existing personality.

    Args:
        personality_id: The personality ID
        body: Update data

    Returns:
        Tuple of (updated_personality_data, status_code)
    """
    try:
        # Get existing personality
        existing_response = _table().get_item(
            Key={PERSONALITY_PK_NAME: personality_id}
        )

        if 'Item' not in existing_response:
            return not_found("Personality")

        existing_personality = from_ddb(existing_response['Item'])

        # Update fields
        updatable_fields = ['name', 'systemPrompt', 'traits', 'communicationStyle', 'knowledge']
        for field in updatable_fields:
            if field in body:
                existing_personality[field] = body[field]

        # Update modification timestamp
        existing_personality['modified'] = {'at': now_iso()}

        # Save to DynamoDB
        _table().put_item(Item=to_ddb(existing_personality))

        return existing_personality, 200

    except ClientError as e:
        return error_response(e)
    except Exception as e:
        return {"error": f"Failed to update personality: {str(e)}"}, 500


def delete_personality(personality_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Delete a personality.

    Args:
        personality_id: The personality ID

    Returns:
        Tuple of (empty_response, status_code)
    """
    try:
        _table().delete_item(
            Key={PERSONALITY_PK_NAME: personality_id}
        )

        return {}, 204

    except ClientError as e:
        return error_response(e)
    except Exception as e:
        return {"error": f"Failed to delete personality: {str(e)}"}, 500


def list_personalities() -> Tuple[Dict[str, Any], int]:
    """
    List all personalities.

    Returns:
        Tuple of (personalities_list, status_code)
    """
    try:
        response = _table().scan()

        personalities = []
        for item in response.get('Items', []):
            personalities.append(from_ddb(item))

        return {"personalities": personalities}, 200

    except ClientError as e:
        return error_response(e)
    except Exception as e:
        return {"error": f"Failed to list personalities: {str(e)}"}, 500


# T033 - Automatic Prompt Regeneration When Personality Updated

def trigger_assistant_prompt_regeneration_for_personality(personality_id: str) -> None:
    """
    Trigger automatic prompt regeneration for all assistants using this personality.

    Args:
        personality_id: The personality ID that was updated
    """
    try:
        from .assistants import get_all_assistants, refresh_assistant_prompt

        # Get all assistants
        assistants_response, status = get_all_assistants()
        if status != 200:
            logger.warning(f"Could not get assistants for personality regeneration: {status}")
            return

        assistants = assistants_response.get('assistants', [])

        # Find assistants using this personality
        affected_assistants = [
            assistant for assistant in assistants
            if assistant.get('personalityId') == personality_id
        ]

        logger.info(f"Triggering prompt regeneration for {len(affected_assistants)} assistants using personality {personality_id}")

        # Regenerate prompts for affected assistants
        for assistant in affected_assistants:
            try:
                assistant_id = assistant['assistantId']
                refresh_assistant_prompt(assistant_id)
                logger.info(f"Regenerated prompt for assistant {assistant_id}")
            except Exception as e:
                logger.error(f"Failed to regenerate prompt for assistant {assistant_id}: {e}")

    except Exception as e:
        logger.error(f"Failed to trigger personality-based prompt regeneration: {e}")


# Enhanced update function with auto-regeneration
def update_personality_with_regeneration(personality_id: str, body: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    """
    Update personality and automatically regenerate affected assistant prompts.

    Args:
        personality_id: The personality ID
        body: Updated personality data

    Returns:
        Tuple of (updated_personality, status_code)
    """
    # First, update the personality
    result, status = update_personality(personality_id, body)

    if status == 200:
        # If update was successful, trigger prompt regeneration
        trigger_assistant_prompt_regeneration_for_personality(personality_id)

    return result, status