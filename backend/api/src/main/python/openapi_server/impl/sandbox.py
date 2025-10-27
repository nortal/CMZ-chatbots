"""
Sandbox Assistant Implementation

Provides functionality for safely testing assistant configurations
before promoting them to live environments.

Business Logic:
- Create sandbox assistants with 30-minute TTL expiry
- Test conversations with temporary assistant configurations
- Promote tested configurations to live assistants
- Automatic cleanup of expired sandbox entries

T039-T044 - User Story 2: Test Assistant Changes Safely
"""

import os
import uuid
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from botocore.exceptions import ClientError

from .utils.dynamo import (
    table, to_ddb, from_ddb, now_iso,
    model_to_json_keyed_dict, ensure_pk,
    error_response, not_found
)
from .assistants import get_assistant, update_assistant
from .conversation import generate_openai_response
from ..models.sandbox_response import SandboxResponse
from ..models.create_sandbox_request import CreateSandboxRequest
from ..models.promote_sandbox_request import PromoteSandboxRequest

# Environment configuration
SANDBOX_TABLE_NAME = os.getenv('SANDBOX_DYNAMO_TABLE_NAME', 'quest-dev-sandbox')
SANDBOX_PK_NAME = os.getenv('SANDBOX_DYNAMO_PK_NAME', 'sandboxId')
SANDBOX_TTL_MINUTES = int(os.getenv('SANDBOX_TTL_MINUTES', '30'))


def _table():
    """Get sandbox DynamoDB table reference"""
    return table(SANDBOX_TABLE_NAME)


def _generate_sandbox_id() -> str:
    """Generate unique sandbox ID"""
    return f"sandbox-{uuid.uuid4().hex[:16]}"


def _calculate_ttl() -> Tuple[int, str]:
    """
    Calculate TTL timestamp and expiration datetime string

    Returns:
        Tuple of (ttl_timestamp, expires_at_iso_string)
    """
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=SANDBOX_TTL_MINUTES)
    ttl_timestamp = int(expires_at.timestamp())
    expires_at_iso = expires_at.isoformat()

    return ttl_timestamp, expires_at_iso


def _is_expired(ttl_timestamp: int) -> bool:
    """Check if sandbox has expired based on TTL timestamp"""
    return int(datetime.now(timezone.utc).timestamp()) > ttl_timestamp


def _validate_create_request(request_data: Dict[str, Any]) -> Optional[Tuple[Dict[str, Any], int]]:
    """
    Validate sandbox creation request

    Returns:
        None if valid, otherwise (error_response, status_code)
    """
    required_fields = ['personalityId', 'guardrailId']

    for field in required_fields:
        if not request_data.get(field):
            return error_response(
                f"Missing required field: {field}",
                "validation_error",
                {"field": field, "message": "Field is required"}
            ), 400

    # Validate knowledge base file limit
    kb_files = request_data.get('knowledgeBaseFileIds', [])
    if kb_files and len(kb_files) > 10:
        return error_response(
            "Knowledge base file limit exceeded",
            "validation_error",
            {"field": "knowledgeBaseFileIds", "limit": 10, "provided": len(kb_files)}
        ), 400

    return None


# T039 - Create Sandbox Assistant model with TTL
def create_sandbox_assistant(request_data: Dict[str, Any], user_id: str = "test@cmz.org") -> Tuple[Dict[str, Any], int]:
    """
    Create a new sandbox assistant for testing

    Args:
        request_data: Sandbox creation parameters
        user_id: ID of user creating the sandbox

    Returns:
        Tuple of (sandbox_data, status_code)
    """
    try:
        # Validate request
        validation_error = _validate_create_request(request_data)
        if validation_error:
            return validation_error

        # Generate sandbox ID and TTL
        sandbox_id = _generate_sandbox_id()
        ttl_timestamp, expires_at_iso = _calculate_ttl()

        # Create sandbox item
        sandbox_item = {
            SANDBOX_PK_NAME: sandbox_id,
            'animalId': request_data.get('animalId'),
            'personalityId': request_data['personalityId'],
            'guardrailId': request_data['guardrailId'],
            'knowledgeBaseFileIds': request_data.get('knowledgeBaseFileIds', []),
            'createdBy': user_id,
            'ttl': ttl_timestamp,  # DynamoDB TTL field
            'expiresAt': expires_at_iso,
            'conversationCount': 0,
            'isPromoted': False,
            'created': {
                'at': now_iso(),
                'by': user_id
            }
        }

        # Store in DynamoDB
        result = _table().put_item(Item=to_ddb(sandbox_item))

        if result['ResponseMetadata']['HTTPStatusCode'] == 200:
            # Return sandbox response
            response_data = {
                'sandboxId': sandbox_id,
                'animalId': sandbox_item.get('animalId'),
                'personalityId': sandbox_item['personalityId'],
                'guardrailId': sandbox_item['guardrailId'],
                'knowledgeBaseFileIds': sandbox_item['knowledgeBaseFileIds'],
                'createdBy': user_id,
                'expiresAt': expires_at_iso,
                'conversationCount': 0,
                'isPromoted': False,
                'created': sandbox_item['created']
            }

            return response_data, 201
        else:
            return error_response("Failed to create sandbox assistant"), 500

    except ClientError as e:
        return error_response(e), 500
    except Exception as e:
        return error_response(f"Unexpected error: {str(e)}"), 500


# T041 - Implement sandbox listing and retrieval endpoints
def list_sandbox_assistants(user_id: str = None, assistant_id: str = None) -> Tuple[Dict[str, Any], int]:
    """
    List sandbox assistants with optional filtering

    Args:
        user_id: Filter by creator user ID
        assistant_id: Filter by base assistant ID

    Returns:
        Tuple of (sandbox_list, status_code)
    """
    try:
        # Build scan parameters
        scan_kwargs = {}

        # Add filters
        filter_expressions = []

        if user_id:
            filter_expressions.append("createdBy = :user_id")
            scan_kwargs.setdefault('ExpressionAttributeValues', {})
            scan_kwargs['ExpressionAttributeValues'][':user_id'] = user_id

        if assistant_id:
            filter_expressions.append("assistantId = :assistant_id")
            scan_kwargs.setdefault('ExpressionAttributeValues', {})
            scan_kwargs['ExpressionAttributeValues'][':assistant_id'] = assistant_id

        if filter_expressions:
            scan_kwargs['FilterExpression'] = ' AND '.join(filter_expressions)

        # Scan table
        response = _table().scan(**scan_kwargs)

        # Filter out expired sandboxes and convert to response format
        sandboxes = []
        current_time = int(datetime.now(timezone.utc).timestamp())

        for item in response.get('Items', []):
            sandbox_data = from_ddb(item)

            # Skip expired sandboxes
            if _is_expired(sandbox_data.get('ttl', 0)):
                continue

            # Convert to response format
            sandbox_response = {
                'sandboxId': sandbox_data[SANDBOX_PK_NAME],
                'animalId': sandbox_data.get('animalId'),
                'personalityId': sandbox_data['personalityId'],
                'guardrailId': sandbox_data['guardrailId'],
                'knowledgeBaseFileIds': sandbox_data.get('knowledgeBaseFileIds', []),
                'createdBy': sandbox_data['createdBy'],
                'expiresAt': sandbox_data['expiresAt'],
                'conversationCount': sandbox_data.get('conversationCount', 0),
                'lastConversationAt': sandbox_data.get('lastConversationAt'),
                'isPromoted': sandbox_data.get('isPromoted', False),
                'promotedAt': sandbox_data.get('promotedAt'),
                'created': sandbox_data['created']
            }

            sandboxes.append(sandbox_response)

        return {'sandboxes': sandboxes}, 200

    except ClientError as e:
        return error_response(e), 500
    except Exception as e:
        return error_response(f"Unexpected error: {str(e)}"), 500


def get_sandbox_assistant(sandbox_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Get sandbox assistant details by ID

    Args:
        sandbox_id: Sandbox ID to retrieve

    Returns:
        Tuple of (sandbox_data, status_code)
    """
    try:
        # Get item from DynamoDB
        response = _table().get_item(
            Key={SANDBOX_PK_NAME: sandbox_id}
        )

        if 'Item' not in response:
            return not_found(f"Sandbox not found: {sandbox_id}"), 404

        sandbox_data = from_ddb(response['Item'])

        # Check if expired
        if _is_expired(sandbox_data.get('ttl', 0)):
            return error_response(
                "Sandbox has expired",
                "expired",
                {"sandboxId": sandbox_id, "expiredAt": sandbox_data.get('expiresAt')}
            ), 410  # Gone

        # Convert to response format
        sandbox_response = {
            'sandboxId': sandbox_data[SANDBOX_PK_NAME],
            'animalId': sandbox_data.get('animalId'),
            'personalityId': sandbox_data['personalityId'],
            'guardrailId': sandbox_data['guardrailId'],
            'knowledgeBaseFileIds': sandbox_data.get('knowledgeBaseFileIds', []),
            'createdBy': sandbox_data['createdBy'],
            'expiresAt': sandbox_data['expiresAt'],
            'conversationCount': sandbox_data.get('conversationCount', 0),
            'lastConversationAt': sandbox_data.get('lastConversationAt'),
            'isPromoted': sandbox_data.get('isPromoted', False),
            'promotedAt': sandbox_data.get('promotedAt'),
            'created': sandbox_data['created'],
            'modified': sandbox_data.get('modified')
        }

        return sandbox_response, 200

    except ClientError as e:
        return error_response(e), 500
    except Exception as e:
        return error_response(f"Unexpected error: {str(e)}"), 500


# T042 - Implement sandbox chat testing endpoint with OpenAI integration
def test_sandbox_chat(sandbox_id: str, chat_request: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    """
    Test conversation with sandbox assistant

    Args:
        sandbox_id: Sandbox ID to test
        chat_request: Chat message and context

    Returns:
        Tuple of (chat_response, status_code)
    """
    try:
        # Get sandbox details
        sandbox_result, status_code = get_sandbox_assistant(sandbox_id)
        if status_code != 200:
            return sandbox_result, status_code

        sandbox_data = sandbox_result

        # Extract message and context
        user_message = chat_request.get('message', '')
        context = chat_request.get('context', {})

        if not user_message:
            return error_response("Message is required", "validation_error"), 400

        # Build conversation context for OpenAI
        conversation_context = {
            'personalityId': sandbox_data['personalityId'],
            'guardrailId': sandbox_data['guardrailId'],
            'animalId': sandbox_data.get('animalId'),
            'knowledgeBaseFileIds': sandbox_data.get('knowledgeBaseFileIds', []),
            'isSandbox': True,
            'sandboxId': sandbox_id
        }

        # Generate AI response using existing conversation logic
        ai_response_result = generate_openai_response(
            user_message=user_message,
            conversation_context=conversation_context,
            user_context=context
        )

        if not ai_response_result or 'response' not in ai_response_result:
            return error_response("Failed to generate AI response"), 500

        # Update sandbox conversation metrics
        try:
            _table().update_item(
                Key={SANDBOX_PK_NAME: sandbox_id},
                UpdateExpression="SET conversationCount = if_not_exists(conversationCount, :zero) + :inc, lastConversationAt = :timestamp",
                ExpressionAttributeValues={
                    ':inc': 1,
                    ':zero': 0,
                    ':timestamp': now_iso()
                }
            )
        except ClientError:
            # Don't fail the response if metrics update fails
            pass

        # Build chat response
        chat_response = {
            'response': ai_response_result['response'],
            'conversationId': f"sandbox-{sandbox_id}-{uuid.uuid4().hex[:8]}",
            'usage': ai_response_result.get('usage', {}),
            'metadata': {
                'model': ai_response_result.get('model', 'gpt-4'),
                'personality': sandbox_data['personalityId'],
                'guardrails': [sandbox_data['guardrailId']],
                'isSandbox': True,
                'sandboxId': sandbox_id
            }
        }

        return chat_response, 200

    except ClientError as e:
        return error_response(e), 500
    except Exception as e:
        return error_response(f"Unexpected error: {str(e)}"), 500


# T043 - Implement sandbox promotion logic
def promote_sandbox_to_live(sandbox_id: str, user_id: str = "test@cmz.org") -> Tuple[Dict[str, Any], int]:
    """
    Promote sandbox configuration to live assistant

    Args:
        sandbox_id: Sandbox ID to promote
        user_id: User promoting the sandbox

    Returns:
        Tuple of (promotion_result, status_code)
    """
    try:
        # Get sandbox details
        sandbox_result, status_code = get_sandbox_assistant(sandbox_id)
        if status_code != 200:
            return sandbox_result, status_code

        sandbox_data = sandbox_result

        # Check if already promoted
        if sandbox_data.get('isPromoted'):
            return error_response(
                "Sandbox has already been promoted",
                "already_promoted",
                {"sandboxId": sandbox_id, "promotedAt": sandbox_data.get('promotedAt')}
            ), 409  # Conflict

        # Get the base assistant to update (if animalId is provided)
        assistant_id = sandbox_data.get('animalId')
        if assistant_id:
            # Update existing assistant
            update_data = {
                'personalityId': sandbox_data['personalityId'],
                'guardrailId': sandbox_data['guardrailId'],
                'knowledgeBaseFileIds': sandbox_data.get('knowledgeBaseFileIds', []),
                'modified': {
                    'at': now_iso(),
                    'by': user_id
                }
            }

            assistant_result, assistant_status = update_assistant(assistant_id, update_data)
            if assistant_status != 200:
                return error_response(
                    f"Failed to update assistant: {assistant_result.get('error', 'Unknown error')}",
                    "assistant_update_failed"
                ), 500
        else:
            # Create new assistant with sandbox configuration
            # This would require implementing create_assistant in assistants.py
            # For now, we'll assume an animalId is always provided
            return error_response(
                "Assistant ID is required for promotion",
                "validation_error",
                {"field": "animalId", "message": "Cannot promote sandbox without target assistant"}
            ), 400

        # Mark sandbox as promoted
        promotion_time = now_iso()
        _table().update_item(
            Key={SANDBOX_PK_NAME: sandbox_id},
            UpdateExpression="SET isPromoted = :promoted, promotedAt = :timestamp, modified = :audit",
            ExpressionAttributeValues={
                ':promoted': True,
                ':timestamp': promotion_time,
                ':audit': {
                    'at': promotion_time,
                    'by': user_id
                }
            }
        )

        # Delete sandbox after successful promotion
        _table().delete_item(Key={SANDBOX_PK_NAME: sandbox_id})

        # Return promotion success
        promotion_result = {
            'message': 'Sandbox successfully promoted to live assistant',
            'sandboxId': sandbox_id,
            'assistantId': assistant_id,
            'promotedAt': promotion_time
        }

        return promotion_result, 200

    except ClientError as e:
        return error_response(e), 500
    except Exception as e:
        return error_response(f"Unexpected error: {str(e)}"), 500


def delete_sandbox_assistant(sandbox_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Delete sandbox assistant

    Args:
        sandbox_id: Sandbox ID to delete

    Returns:
        Tuple of (delete_result, status_code)
    """
    try:
        # Check if sandbox exists first
        sandbox_result, status_code = get_sandbox_assistant(sandbox_id)
        if status_code == 404:
            return not_found(f"Sandbox not found: {sandbox_id}"), 404
        elif status_code != 200:
            return sandbox_result, status_code

        # Delete from DynamoDB
        _table().delete_item(Key={SANDBOX_PK_NAME: sandbox_id})

        return {'message': 'Sandbox deleted successfully', 'sandboxId': sandbox_id}, 204

    except ClientError as e:
        return error_response(e), 500
    except Exception as e:
        return error_response(f"Unexpected error: {str(e)}"), 500


# T044 - Implement automatic sandbox cleanup
def cleanup_expired_sandboxes() -> Dict[str, Any]:
    """
    Clean up expired sandbox entries

    This function is designed to be called by a scheduled job
    or manually for maintenance.

    Returns:
        Dict with cleanup results
    """
    try:
        cleaned_count = 0
        errors = []
        current_time = int(datetime.now(timezone.utc).timestamp())

        # Scan all sandboxes
        response = _table().scan()

        for item in response.get('Items', []):
            sandbox_data = from_ddb(item)
            sandbox_id = sandbox_data[SANDBOX_PK_NAME]

            # Check if expired
            if _is_expired(sandbox_data.get('ttl', 0)):
                try:
                    # Delete expired sandbox
                    _table().delete_item(Key={SANDBOX_PK_NAME: sandbox_id})
                    cleaned_count += 1
                except ClientError as e:
                    errors.append({
                        'sandboxId': sandbox_id,
                        'error': str(e)
                    })

        return {
            'cleaned_count': cleaned_count,
            'errors': errors,
            'timestamp': now_iso()
        }

    except Exception as e:
        return {
            'cleaned_count': 0,
            'errors': [{'error': f"Cleanup failed: {str(e)}"}],
            'timestamp': now_iso()
        }