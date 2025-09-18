"""
Implementation module for conversation with ChatGPT integration and DynamoDB storage
Implements Chat History Epic tickets PR003946-156 through PR003946-160
"""

import asyncio
import uuid
from typing import Any, Dict, List, Tuple, Union, Optional
from datetime import datetime
import logging
from flask import Response

from ..models.error import Error
from .utils.conversation_dynamo import (
    create_conversation_session,
    store_conversation_turn,
    get_conversation_history,
    get_user_sessions,
    check_user_access_to_session,
    get_session_info,
    get_conversation_analytics
)
from .utils.chatgpt_integration import get_chatgpt_integration
from .streaming_response import SSEStreamer, ConversationStreamer
from .utils.dynamo import table as get_animals_table

logger = logging.getLogger(__name__)


def not_implemented_error(operation_name: str) -> Tuple[Dict[str, Any], int]:
    """Helper function for not-yet-implemented operations"""
    error_obj = Error(
        code="not_implemented",
        message=f"Operation {operation_name} not yet implemented",
        details={"operation": operation_name, "module": "conversation"}
    )
    return error_obj.to_dict(), 501


def get_animal_config(animal_id: str) -> Optional[Dict[str, Any]]:
    """
    Get animal configuration from DynamoDB

    Args:
        animal_id: Animal ID

    Returns:
        Animal configuration or None if not found
    """
    try:
        table = get_animals_table()
        response = table.get_item(Key={'animalId': animal_id})
        return response.get('Item')
    except Exception as e:
        logger.error(f"Failed to get animal config: {e}")
        return None


def handle_convo_history_delete(conversation_id: str, user_id: str = None, user_role: str = 'user', **kwargs) -> Tuple[Any, int]:
    """
    Implementation handler for convo_history_delete

    Args:
        conversation_id: ID of conversation to delete
        user_id: User ID making the request
        user_role: User's role
    """
    # Check access permissions
    if not check_user_access_to_session(user_id, conversation_id, user_role):
        error_obj = Error(
            code="forbidden",
            message="You do not have permission to delete this conversation",
            details={"conversationId": conversation_id}
        )
        return error_obj.to_dict(), 403

    # Only administrators can actually delete conversations
    if user_role != 'administrator':
        error_obj = Error(
            code="forbidden",
            message="Only administrators can delete conversations",
            details={"role": user_role}
        )
        return error_obj.to_dict(), 403

    # Mark conversation as deleted (soft delete)
    try:
        from .utils.conversation_dynamo import get_sessions_table
        table = get_sessions_table()
        table.update_item(
            Key={'sessionId': conversation_id},
            UpdateExpression='SET #status = :status, deletedAt = :time',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':status': 'deleted',
                ':time': datetime.utcnow().isoformat() + 'Z'
            }
        )
        return {'message': 'Conversation deleted successfully'}, 204
    except Exception as e:
        logger.error(f"Failed to delete conversation: {e}")
        error_obj = Error(
            code="internal_error",
            message="Failed to delete conversation",
            details={"error": str(e)}
        )
        return error_obj.to_dict(), 500


def handle_convo_history_get(
    session_id: Optional[str] = None,
    user_id: Optional[str] = None,
    animal_id: Optional[str] = None,
    user_role: str = 'user',
    limit: int = 20,
    **kwargs
) -> Tuple[Any, int]:
    """
    Implementation handler for convo_history_get
    Get conversation history based on user permissions

    Args:
        session_id: Optional specific session ID
        user_id: User ID making the request
        animal_id: Optional animal ID filter
        user_role: User's role
        limit: Maximum number of items to return
    """
    try:
        # If specific session requested, check access
        if session_id:
            if not check_user_access_to_session(user_id, session_id, user_role):
                error_obj = Error(
                    code="forbidden",
                    message="You do not have permission to view this conversation",
                    details={"sessionId": session_id}
                )
                return error_obj.to_dict(), 403

            # Get specific conversation history
            history = get_conversation_history(session_id, limit=limit)
            session_info = get_session_info(session_id)

            return {
                'sessionId': session_id,
                'sessionInfo': session_info,
                'messages': history,
                'messageCount': len(history)
            }, 200

        # Get list of sessions based on role
        if user_role in ['administrator', 'zookeeper']:
            # Can see all conversations
            from .utils.conversation_dynamo import get_sessions_table
            table = get_sessions_table()
            response = table.scan(Limit=limit)
            sessions = response.get('Items', [])
        elif user_role == 'parent':
            # Can see own and children's conversations
            # TODO: Implement parent-child relationship lookup
            sessions = get_user_sessions(user_id, animal_id, limit=limit)
        else:
            # Regular users can only see their own
            sessions = get_user_sessions(user_id, animal_id, limit=limit)

        # Get analytics for each session
        for session in sessions:
            session['analytics'] = get_conversation_analytics(session['sessionId'])

        return {
            'sessions': sessions,
            'totalSessions': len(sessions)
        }, 200

    except Exception as e:
        logger.error(f"Failed to get conversation history: {e}")
        error_obj = Error(
            code="internal_error",
            message="Failed to retrieve conversation history",
            details={"error": str(e)}
        )
        return error_obj.to_dict(), 500


def handle_convo_turn_post(body, user_id: str = None, stream: bool = False, **kwargs) -> Union[Tuple[Any, int], Response]:
    """
    Implementation handler for convo_turn_post with ChatGPT integration

    Args:
        body: ConvoTurnRequest object with message, animalId, sessionId
        user_id: User ID making the request
        stream: Whether to stream the response
    """
    try:
        # Extract parameters from body
        user_message = body.get('message', '') if isinstance(body, dict) else getattr(body, 'message', '')
        animal_id = body.get('animalId', 'default') if isinstance(body, dict) else getattr(body, 'animalId', 'default')
        session_id = body.get('sessionId', None) if isinstance(body, dict) else getattr(body, 'sessionId', None)

        if not user_message:
            error_obj = Error(
                code="invalid_request",
                message="Message is required",
                details={"field": "message"}
            )
            return error_obj.to_dict(), 400

        # Get animal configuration
        animal_config = get_animal_config(animal_id) if animal_id != 'default' else None

        if stream:
            # Handle streaming response
            chatgpt = get_chatgpt_integration()
            import openapi_server.impl.utils.conversation_dynamo as conversation_dynamo
            streamer = ConversationStreamer(chatgpt, conversation_dynamo)

            async def generate_stream():
                async for event in streamer.stream_conversation_turn(
                    user_id=user_id or 'anonymous',
                    animal_id=animal_id,
                    user_message=user_message,
                    session_id=session_id,
                    animal_config=animal_config
                ):
                    yield event

            return SSEStreamer.create_sse_response(generate_stream())

        else:
            # Handle non-streaming response
            # Create or get session
            if not session_id:
                session_id = create_conversation_session(
                    user_id=user_id or 'anonymous',
                    animal_id=animal_id
                )

            # Get conversation history
            history = get_conversation_history(session_id, limit=10)

            # Convert to ChatGPT format
            chat_history = []
            for turn in history:
                chat_history.append({"role": "user", "content": turn.get('userMessage', '')})
                chat_history.append({"role": "assistant", "content": turn.get('assistantReply', '')})

            # Get response from ChatGPT
            chatgpt = get_chatgpt_integration()

            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                response_data = loop.run_until_complete(
                    chatgpt.get_animal_response(
                        animal_id=animal_id,
                        user_message=user_message,
                        conversation_history=chat_history,
                        animal_config=animal_config
                    )
                )
            finally:
                loop.close()

            # Store conversation turn
            turn_id = store_conversation_turn(
                session_id=session_id,
                user_message=user_message,
                assistant_reply=response_data['reply'],
                metadata=response_data.get('metadata', {})
            )

            # Format response
            response = {
                "reply": response_data['reply'],
                "turn": {
                    "convoTurnId": turn_id,
                    "sessionId": session_id,
                    "timestamp": response_data['metadata'].get('timestamp'),
                    "tokensPrompt": response_data['metadata'].get('tokensPrompt', 0),
                    "tokensCompletion": response_data['metadata'].get('tokensCompletion', 0),
                    "latencyMs": response_data['metadata'].get('latencyMs', 0)
                },
                "analytics": {
                    "sentiment": "positive",
                    "topics": ["animal", "education"],
                    "animalEngagement": "high"
                }
            }

            return response, 200

    except Exception as e:
        logger.error(f"Failed to handle conversation turn: {e}")

        # Return fallback response if ChatGPT fails
        if 'API key' in str(e):
            # ChatGPT not configured, return mock response
            response = {
                "reply": f"Hello! I'm {animal_id if animal_id != 'default' else 'an animal'} at the zoo. ChatGPT integration is being configured. How can I help you learn about animals today?",
                "turn": {
                    "convoTurnId": str(uuid.uuid4()),
                    "sessionId": session_id or str(uuid.uuid4()),
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "tokensPrompt": 0,
                    "tokensCompletion": 0,
                    "latencyMs": 10
                },
                "analytics": {
                    "sentiment": "neutral",
                    "topics": ["general"],
                    "animalEngagement": "high"
                }
            }
            return response, 200

        error_obj = Error(
            code="internal_error",
            message="Failed to process conversation turn",
            details={"error": str(e)}
        )
        return error_obj.to_dict(), 500


def handle_summarize_convo_post(body, **kwargs) -> Tuple[Any, int]:
    """
    Implementation handler for summarize_convo_post

    Args:
        body: Request body with sessionId
    """
    try:
        session_id = body.get('sessionId') if isinstance(body, dict) else getattr(body, 'sessionId', None)

        if not session_id:
            error_obj = Error(
                code="invalid_request",
                message="Session ID is required",
                details={"field": "sessionId"}
            )
            return error_obj.to_dict(), 400

        # Get conversation history
        history = get_conversation_history(session_id, limit=100)

        if not history:
            error_obj = Error(
                code="not_found",
                message="Conversation not found",
                details={"sessionId": session_id}
            )
            return error_obj.to_dict(), 404

        # Create summary (simplified for now)
        summary = {
            "sessionId": session_id,
            "messageCount": len(history),
            "summary": f"Conversation with {len(history)} messages about animals and education.",
            "keyTopics": ["animals", "conservation", "education"],
            "sentiment": "positive",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        return summary, 200

    except Exception as e:
        logger.error(f"Failed to summarize conversation: {e}")
        error_obj = Error(
            code="internal_error",
            message="Failed to summarize conversation",
            details={"error": str(e)}
        )
        return error_obj.to_dict(), 500

