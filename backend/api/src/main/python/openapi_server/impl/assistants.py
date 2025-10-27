"""
Animal Assistant Management Implementation Module

This module provides CRUD operations for managing Animal Assistants,
including personality and guardrail integration with prompt merging.

Follows CMZ patterns:
- Uses impl/utils/dynamo.py for DynamoDB operations
- Integrates with existing personality and guardrail systems
- Implements prompt merging for OpenAI integration
"""

import os
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key

from .utils.dynamo import table, to_ddb, from_ddb, now_iso, error_response, not_found

logger = logging.getLogger(__name__)
from .personalities import get_personality
from .guardrails import get_guardrail
from .utils.prompt_merger import merge_assistant_prompt


# DynamoDB table configuration
ASSISTANT_TABLE_NAME = os.getenv('ASSISTANT_DYNAMO_TABLE_NAME', 'quest-dev-animal-assistant')
ASSISTANT_PK_NAME = os.getenv('ASSISTANT_DYNAMO_PK_NAME', 'assistantId')


def _table():
    """Get DynamoDB table reference for assistants."""
    return table(ASSISTANT_TABLE_NAME)


def validate_assistant_data(data: Dict[str, Any]) -> None:
    """
    Validate assistant data before creation or update.

    Args:
        data: Assistant data dictionary

    Raises:
        ValueError: If validation fails
    """
    required_fields = ['animalId', 'personalityId', 'guardrailId']
    for field in required_fields:
        if field not in data or not data[field]:
            raise ValueError(f"Missing required field: {field}")

    # Validate status
    valid_statuses = ['ACTIVE', 'INACTIVE', 'ERROR']
    if 'status' in data and data['status'] not in valid_statuses:
        raise ValueError(f"Invalid status. Must be one of: {valid_statuses}")

    # Validate knowledge base file limit
    if 'knowledgeBaseFileIds' in data:
        if len(data['knowledgeBaseFileIds']) > 50:
            raise ValueError("Maximum of 50 knowledge base files allowed per assistant")


def merge_personality_and_guardrails(personality_id: str, guardrail_id: str) -> str:
    """
    Merge personality and guardrail prompts into unified system prompt.

    Args:
        personality_id: ID of the personality configuration
        guardrail_id: ID of the guardrail configuration

    Returns:
        Merged system prompt string

    Raises:
        ValueError: If personality or guardrail not found
    """
    # Get personality data
    personality_data, personality_status = get_personality(personality_id)
    if personality_status != 200:
        raise ValueError(f"personality not found: {personality_id}")

    # Get guardrail data
    guardrail_data, guardrail_status = get_guardrail(guardrail_id)
    if guardrail_status != 200:
        raise ValueError(f"Guardrail not found: {guardrail_id}")

    # Extract data for merge_assistant_prompt function
    animal_name = personality_data.get('name', 'Digital Assistant')
    animal_species = 'Digital Ambassador'  # Default for assistants
    personality_text = personality_data.get('systemPrompt', '')

    # Build guardrail text from rules and restrictions
    rules = guardrail_data.get('rules', [])
    restrictions = guardrail_data.get('restrictions', [])
    guardrail_text = guardrail_data.get('systemPrompt', '')

    if rules:
        guardrail_text += '\n\nRules:\n' + '\n'.join([f"- {rule}" for rule in rules])
    if restrictions:
        guardrail_text += '\n\nRestrictions:\n' + '\n'.join([f"- {restriction}" for restriction in restrictions])

    # Merge prompts using the prompt merger utility
    merged_prompt, stats = merge_assistant_prompt(
        animal_name=animal_name,
        animal_species=animal_species,
        personality_text=personality_text,
        guardrail_text=guardrail_text
    )

    return merged_prompt


def create_assistant(body: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    """
    Create a new animal assistant.

    Args:
        body: Assistant creation data

    Returns:
        Tuple of (response_data, status_code)
    """
    try:
        # Validate input data
        validate_assistant_data(body)

        # Generate unique assistant ID
        assistant_id = str(uuid.uuid4())

        # Merge personality and guardrails
        try:
            merged_prompt = merge_personality_and_guardrails(
                body['personalityId'],
                body['guardrailId']
            )
        except ValueError as e:
            # If personality or guardrail not found, return 400 error
            return {"error": str(e)}, 400

        # Prepare assistant item
        assistant_item = {
            'assistantId': assistant_id,
            'animalId': body['animalId'],
            'personalityId': body['personalityId'],
            'guardrailId': body['guardrailId'],
            'mergedPrompt': merged_prompt,
            'knowledgeBaseFileIds': body.get('knowledgeBaseFileIds', []),
            'status': body.get('status', 'ACTIVE'),
            'lastPromptMerge': {'at': now_iso()},
            'responseTimeP95': 0,  # Initial value
            'created': {'at': now_iso()},
            'modified': {'at': now_iso()}
        }

        # Save to DynamoDB
        _table().put_item(
            Item=to_ddb(assistant_item),
            ConditionExpression='attribute_not_exists(assistantId)'
        )

        return assistant_item, 201

    except ValueError as e:
        return {"error": str(e)}, 400
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            return {"error": "Assistant already exists"}, 409
        return error_response(e)
    except Exception as e:
        return {"error": f"Failed to create assistant: {str(e)}"}, 500


def get_assistant(assistant_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Retrieve an assistant by ID.

    Args:
        assistant_id: The assistant ID

    Returns:
        Tuple of (assistant_data, status_code)
    """
    try:
        response = _table().get_item(
            Key={ASSISTANT_PK_NAME: assistant_id}
        )

        if 'Item' not in response:
            return not_found("Assistant", assistant_id), 404

        assistant_data = from_ddb(response['Item'])
        return assistant_data, 200

    except ClientError as e:
        return error_response(e)
    except Exception as e:
        return {"error": f"Failed to retrieve assistant: {str(e)}"}, 500


def update_assistant(assistant_id: str, body: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    """
    Update an existing assistant.

    Args:
        assistant_id: The assistant ID
        body: Update data

    Returns:
        Tuple of (updated_assistant_data, status_code)
    """
    try:
        # Get existing assistant
        existing_response = _table().get_item(
            Key={ASSISTANT_PK_NAME: assistant_id}
        )

        if 'Item' not in existing_response:
            return not_found("Assistant", assistant_id), 404

        existing_assistant = from_ddb(existing_response['Item'])

        # Update fields
        updated_assistant = existing_assistant.copy()
        updatable_fields = [
            'personalityId', 'guardrailId', 'knowledgeBaseFileIds', 'status'
        ]

        for field in updatable_fields:
            if field in body:
                updated_assistant[field] = body[field]

        # Validate updated data
        validate_assistant_data(updated_assistant)

        # Check if personality or guardrail changed - regenerate prompt if so
        personality_changed = (
            'personalityId' in body and
            body['personalityId'] != existing_assistant['personalityId']
        )
        guardrail_changed = (
            'guardrailId' in body and
            body['guardrailId'] != existing_assistant['guardrailId']
        )

        if personality_changed or guardrail_changed:
            updated_assistant['mergedPrompt'] = merge_personality_and_guardrails(
                updated_assistant['personalityId'],
                updated_assistant['guardrailId']
            )
            updated_assistant['lastPromptMerge'] = {'at': now_iso()}

        # Update modification timestamp
        updated_assistant['modified'] = {'at': now_iso()}

        # Save to DynamoDB
        _table().put_item(Item=to_ddb(updated_assistant))

        return updated_assistant, 200

    except ValueError as e:
        return {"error": str(e)}, 400
    except ClientError as e:
        return error_response(e)
    except Exception as e:
        return {"error": f"Failed to update assistant: {str(e)}"}, 500


def delete_assistant(assistant_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Delete an assistant.

    Args:
        assistant_id: The assistant ID

    Returns:
        Tuple of (empty_response, status_code)
    """
    try:
        _table().delete_item(
            Key={ASSISTANT_PK_NAME: assistant_id}
        )

        return {}, 204

    except ClientError as e:
        return error_response(e)
    except Exception as e:
        return {"error": f"Failed to delete assistant: {str(e)}"}, 500


def list_assistants() -> Tuple[Dict[str, Any], int]:
    """
    List all assistants.

    Returns:
        Tuple of (assistants_list, status_code)
    """
    try:
        response = _table().scan()

        assistants = []
        for item in response.get('Items', []):
            assistants.append(from_ddb(item))

        return {"assistants": assistants}, 200

    except ClientError as e:
        return error_response(e)
    except Exception as e:
        return {"error": f"Failed to list assistants: {str(e)}"}, 500


def get_assistant_by_animal(animal_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Get assistant by animal ID.

    Args:
        animal_id: The animal ID

    Returns:
        Tuple of (assistant_data, status_code)
    """
    try:
        # Use scan since GSI doesn't exist yet (fallback implementation)
        # TODO: Add animalId-index GSI to quest-dev-animal-assistant table for better performance
        response = _table().scan(
            FilterExpression='animalId = :animal_id',
            ExpressionAttributeValues={':animal_id': animal_id}
        )

        items = response.get('Items', [])
        if not items:
            return not_found("Assistant for animal", animal_id), 404

        # Should only be one assistant per animal
        assistant_data = from_ddb(items[0])
        return assistant_data, 200

    except ClientError as e:
        return error_response(e)
    except Exception as e:
        return {"error": f"Failed to get assistant by animal: {str(e)}"}, 500


def refresh_assistant_prompt(assistant_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Refresh the merged prompt for an assistant.

    This is called when personality or guardrail configurations are updated.

    Args:
        assistant_id: The assistant ID

    Returns:
        Tuple of (updated_assistant_data, status_code)
    """
    try:
        # Get existing assistant
        existing_response = _table().get_item(
            Key={ASSISTANT_PK_NAME: assistant_id}
        )

        if 'Item' not in existing_response:
            return not_found("Assistant", assistant_id), 404

        existing_assistant = from_ddb(existing_response['Item'])

        # Regenerate merged prompt
        new_merged_prompt = merge_personality_and_guardrails(
            existing_assistant['personalityId'],
            existing_assistant['guardrailId']
        )

        # Update assistant
        existing_assistant['mergedPrompt'] = new_merged_prompt
        existing_assistant['lastPromptMerge'] = {'at': now_iso()}
        existing_assistant['modified'] = {'at': now_iso()}

        # Save to DynamoDB
        _table().put_item(Item=to_ddb(existing_assistant))

        return existing_assistant, 200

    except ClientError as e:
        return error_response(e)
    except Exception as e:
        return {"error": f"Failed to refresh assistant prompt: {str(e)}"}, 500


# T032 - Assistant Status Monitoring and Performance Metrics Tracking

def get_assistant_metrics(assistant_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Get performance metrics and status information for an assistant.

    Args:
        assistant_id: The assistant ID

    Returns:
        Tuple of (metrics_data, status_code)
    """
    try:
        from .utils.safety_dynamo import get_safety_dynamo_client

        # Get assistant details
        assistant_response = _table().get_item(
            Key={ASSISTANT_PK_NAME: assistant_id}
        )

        if 'Item' not in assistant_response:
            return not_found("Assistant", assistant_id), 404

        assistant = from_ddb(assistant_response['Item'])

        # Get analytics data from conversation analytics table
        safety_client = get_safety_dynamo_client()

        # Calculate metrics (last 24 hours)
        metrics = {
            'assistantId': assistant_id,
            'status': assistant.get('status', 'UNKNOWN'),
            'lastModified': assistant.get('modified', {}).get('at'),
            'lastPromptMerge': assistant.get('lastPromptMerge', {}).get('at'),
            'conversationMetrics': {
                'totalConversations': 0,
                'totalTurns': 0,
                'averageResponseTime': 0,
                'successRate': 100.0,
                'errorRate': 0.0
            },
            'healthChecks': {
                'promptMergeValid': bool(assistant.get('mergedPrompt')),
                'personalityLinked': bool(assistant.get('personalityId')),
                'guardrailLinked': bool(assistant.get('guardrailId')),
                'animalLinked': bool(assistant.get('animalId'))
            },
            'usage': {
                'last24Hours': 0,
                'lastWeek': 0,
                'totalLifetime': 0
            },
            'performance': {
                'averageRating': 0.0,
                'responseQuality': 'UNKNOWN',
                'guardrailTriggers': 0
            }
        }

        # Try to get conversation analytics
        try:
            # This would query the conversation analytics table for this assistant
            # For now, we'll provide placeholder metrics
            # In a full implementation, this would aggregate real conversation data
            conversation_history = safety_client.get_conversation_history(
                conversation_id=f"assistant_{assistant_id}",
                user_id="system"
            )

            metrics['conversationMetrics']['totalTurns'] = len(conversation_history)

        except Exception as analytics_error:
            logger.warning(f"Could not get conversation analytics for {assistant_id}: {analytics_error}")

        # Health score calculation
        health_checks = metrics['healthChecks']
        health_score = sum([
            health_checks['promptMergeValid'],
            health_checks['personalityLinked'],
            health_checks['guardrailLinked'],
            health_checks['animalLinked']
        ]) / 4 * 100

        metrics['healthScore'] = health_score
        metrics['overallStatus'] = 'HEALTHY' if health_score >= 75 else 'DEGRADED' if health_score >= 50 else 'UNHEALTHY'

        return metrics, 200

    except ClientError as e:
        return error_response(e)
    except Exception as e:
        return {"error": f"Failed to get assistant metrics: {str(e)}"}, 500


def get_all_assistants_status() -> Tuple[Dict[str, Any], int]:
    """
    Get status overview for all assistants.

    Returns:
        Tuple of (status_overview, status_code)
    """
    try:
        # Get all assistants
        response = _table().scan()
        assistants = [from_ddb(item) for item in response.get('Items', [])]

        overview = {
            'timestamp': now_iso(),
            'totalAssistants': len(assistants),
            'statusCounts': {
                'ACTIVE': 0,
                'INACTIVE': 0,
                'ERROR': 0
            },
            'healthOverview': {
                'healthy': 0,
                'degraded': 0,
                'unhealthy': 0
            },
            'assistantSummaries': []
        }

        for assistant in assistants:
            status = assistant.get('status', 'UNKNOWN')
            if status in overview['statusCounts']:
                overview['statusCounts'][status] += 1

            # Get health metrics for each assistant
            metrics, _ = get_assistant_metrics(assistant['assistantId'])
            if 'healthScore' in metrics:
                health_score = metrics['healthScore']
                if health_score >= 75:
                    overview['healthOverview']['healthy'] += 1
                elif health_score >= 50:
                    overview['healthOverview']['degraded'] += 1
                else:
                    overview['healthOverview']['unhealthy'] += 1

            # Add summary
            overview['assistantSummaries'].append({
                'assistantId': assistant['assistantId'],
                'animalId': assistant.get('animalId'),
                'status': status,
                'healthScore': metrics.get('healthScore', 0),
                'lastModified': assistant.get('modified', {}).get('at')
            })

        return overview, 200

    except ClientError as e:
        return error_response(e)
    except Exception as e:
        return {"error": f"Failed to get assistants status: {str(e)}"}, 500


def record_assistant_usage(assistant_id: str, event_type: str, metadata: Optional[Dict[str, Any]] = None) -> None:
    """
    Record usage event for an assistant (for metrics tracking).

    Args:
        assistant_id: The assistant ID
        event_type: Type of event (conversation_start, turn_completed, error, etc.)
        metadata: Optional metadata about the event
    """
    try:
        from .utils.safety_dynamo import get_safety_dynamo_client

        safety_client = get_safety_dynamo_client()

        event_data = {
            'assistantId': assistant_id,
            'eventType': event_type,
            'timestamp': now_iso(),
            'metadata': metadata or {}
        }

        safety_client.store_analytics_event(event_data)

    except Exception as e:
        logger.warning(f"Failed to record usage for assistant {assistant_id}: {e}")


def update_assistant_performance_metrics(assistant_id: str, response_time: float, success: bool) -> None:
    """
    Update performance metrics for an assistant.

    Args:
        assistant_id: The assistant ID
        response_time: Response time in seconds
        success: Whether the response was successful
    """
    try:
        # Record the performance event
        record_assistant_usage(assistant_id, 'performance_metric', {
            'responseTime': response_time,
            'success': success,
            'timestamp': now_iso()
        })

        # Update assistant status if there are repeated failures
        if not success:
            # TODO: Implement failure threshold logic
            # If failure rate exceeds threshold, mark assistant as ERROR status
            pass

    except Exception as e:
        logger.warning(f"Failed to update performance metrics for assistant {assistant_id}: {e}")