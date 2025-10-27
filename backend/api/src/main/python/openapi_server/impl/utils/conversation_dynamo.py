"""
DynamoDB utilities for conversation management
Implements infrastructure for chat history storage
"""

import os
import boto3
from boto3.dynamodb.conditions import Key, Attr
from typing import Dict, List, Optional, Any
import json
from datetime import datetime
import uuid

# DynamoDB configuration
# Using existing tables: quest-dev-conversation and quest-dev-session
CONVERSATION_TABLE = os.getenv('CONVERSATION_DYNAMO_TABLE_NAME', 'quest-dev-conversation')
CONVERSATION_SESSION_TABLE = os.getenv('CONVERSATION_SESSION_TABLE_NAME', 'quest-dev-session')
AWS_REGION = os.getenv('AWS_REGION', 'us-west-2')

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)

def get_conversations_table():
    """Get reference to conversations table"""
    return dynamodb.Table(CONVERSATION_TABLE)

def get_sessions_table():
    """Get reference to conversation sessions table"""
    return dynamodb.Table(CONVERSATION_SESSION_TABLE)

def create_conversation_session(user_id: str, animal_id: str, animal_name: str = None) -> str:
    """
    Create a new conversation session in quest-dev-conversation table

    Args:
        user_id: ID of the user
        animal_id: ID of the animal
        animal_name: Optional name of the animal

    Returns:
        conversation_id: Unique identifier for the conversation
    """
    conversation_id = f"conv_{animal_id}_{user_id}_{str(uuid.uuid4())[:8]}"
    timestamp = datetime.utcnow().isoformat() + 'Z'

    table = get_conversations_table()

    # Create conversation with proper schema matching quest-dev-conversation
    item = {
        'conversationId': conversation_id,  # Primary key
        'userId': user_id,
        'animalId': animal_id,
        'animalName': animal_name or animal_id,
        'messageCount': 0,
        'startTime': timestamp,
        'endTime': timestamp,
        'status': 'active',
        'messages': []  # Initialize empty messages list
    }

    table.put_item(Item=item)

    # Also create session record for backward compatibility
    try:
        sessions_table = get_sessions_table()
        sessions_table.put_item(
            Item={
                'sessionId': conversation_id,
                'userId': user_id,
                'animalId': animal_id,
                'startTime': timestamp,
                'lastActivity': timestamp,
                'messageCount': 0,
                'status': 'active'
            }
        )
    except Exception:
        # Session table is optional, don't fail if it doesn't exist
        pass

    return conversation_id

def store_conversation_turn(
    session_id: str,
    user_message: str,
    assistant_reply: str,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    Store a conversation turn in DynamoDB by appending to messages list

    Args:
        session_id: Conversation ID (conversationId)
        user_message: User's message
        assistant_reply: Assistant's reply
        metadata: Additional metadata (tokens, latency, etc.)

    Returns:
        message_id: Unique identifier for the user message
    """
    conversation_id = session_id  # session_id is actually conversationId
    user_msg_id = str(uuid.uuid4())
    assistant_msg_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat() + 'Z'

    table = get_conversations_table()

    # Create user message object
    user_msg = {
        'messageId': user_msg_id,
        'role': 'user',
        'text': user_message,
        'timestamp': timestamp
    }

    # Create assistant message object
    assistant_msg = {
        'messageId': assistant_msg_id,
        'role': 'assistant',
        'text': assistant_reply,
        'timestamp': timestamp
    }

    # Add metadata if provided
    if metadata:
        assistant_msg['metadata'] = metadata

    # Append both messages to the conversation
    try:
        table.update_item(
            Key={'conversationId': conversation_id},
            UpdateExpression='SET messages = list_append(messages, :msgs), '
                           'messageCount = messageCount + :count, '
                           'endTime = :time',
            ExpressionAttributeValues={
                ':msgs': [user_msg, assistant_msg],
                ':count': 2,
                ':time': timestamp
            }
        )
    except Exception as e:
        # If conversation doesn't exist, error will be raised
        raise Exception(f"Failed to store conversation turn: {str(e)}")

    # Update session table for backward compatibility
    try:
        sessions_table = get_sessions_table()
        sessions_table.update_item(
            Key={'sessionId': conversation_id},
            UpdateExpression='SET lastActivity = :time, messageCount = messageCount + :inc',
            ExpressionAttributeValues={
                ':time': timestamp,
                ':inc': 2
            }
        )
    except Exception:
        # Session table is optional
        pass

    return user_msg_id

def get_conversation_history(
    session_id: str,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Retrieve conversation history for a session

    Args:
        session_id: Conversation ID (conversationId)
        limit: Maximum number of messages to retrieve

    Returns:
        List of messages from the conversation
    """
    conversation_id = session_id  # session_id is actually conversationId
    table = get_conversations_table()

    try:
        response = table.get_item(Key={'conversationId': conversation_id})
        item = response.get('Item')

        if not item:
            return []

        # Get messages list and apply limit
        messages = item.get('messages', [])

        # Return most recent messages up to limit
        if len(messages) > limit:
            return messages[-limit:]

        return messages

    except Exception:
        return []

def get_user_sessions(
    user_id: str,
    animal_id: Optional[str] = None,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """
    Get conversation sessions for a user

    Args:
        user_id: User ID
        animal_id: Optional animal ID filter
        limit: Maximum number of sessions

    Returns:
        List of conversation sessions
    """
    table = get_sessions_table()

    # Build filter expression
    filter_exp = Attr('userId').eq(user_id)
    if animal_id:
        filter_exp = filter_exp & Attr('animalId').eq(animal_id)

    response = table.scan(
        FilterExpression=filter_exp,
        Limit=limit
    )

    items = response.get('Items', [])
    # Sort by last activity (most recent first)
    items.sort(key=lambda x: x.get('lastActivity', ''), reverse=True)

    return items

def get_session_info(session_id: str) -> Optional[Dict[str, Any]]:
    """
    Get information about a conversation session

    Args:
        session_id: Conversation ID (conversationId)

    Returns:
        Conversation information or None if not found
    """
    conversation_id = session_id  # session_id is actually conversationId
    table = get_conversations_table()

    try:
        response = table.get_item(Key={'conversationId': conversation_id})
        item = response.get('Item')

        if not item:
            # Try session table as fallback for backward compatibility
            try:
                sessions_table = get_sessions_table()
                response = sessions_table.get_item(Key={'sessionId': conversation_id})
                return response.get('Item')
            except Exception:
                return None

        return item
    except Exception:
        return None

def check_user_access_to_session(
    user_id: str,
    session_id: str,
    user_role: str = 'user'
) -> bool:
    """
    Check if a user has access to a conversation session

    Args:
        user_id: User ID
        session_id: Session ID
        user_role: User's role (user, parent, zookeeper, administrator)

    Returns:
        True if user has access, False otherwise
    """
    session_info = get_session_info(session_id)

    if not session_info:
        return False

    # Administrators and zookeepers can access all conversations
    if user_role in ['administrator', 'zookeeper']:
        return True

    # Users can access their own conversations
    if session_info.get('userId') == user_id:
        return True

    # Parents can access their children's conversations
    if user_role == 'parent':
        # TODO: Implement parent-child relationship check
        # For now, return False
        return False

    return False

def archive_old_conversations(days_old: int = 90):
    """
    Archive conversations older than specified days

    Args:
        days_old: Number of days after which to archive
    """
    # Implementation would move old conversations to an archive table
    # This is a placeholder for the actual implementation
    pass

def get_conversation_analytics(session_id: str) -> Dict[str, Any]:
    """
    Get analytics for a conversation session

    Args:
        session_id: Session ID

    Returns:
        Analytics data including message count, duration, etc.
    """
    session_info = get_session_info(session_id)
    if not session_info:
        return {}

    # Get all conversation turns
    history = get_conversation_history(session_id, limit=1000)

    # Calculate analytics
    analytics = {
        'sessionId': session_id,
        'messageCount': len(history),
        'startTime': session_info.get('startTime'),
        'lastActivity': session_info.get('lastActivity'),
        'duration': None,  # Calculate from timestamps
        'averageResponseLength': 0,
        'userEngagement': 'high' if len(history) > 10 else 'medium' if len(history) > 5 else 'low'
    }

    if history and len(history) > 0:
        total_length = sum(len(turn.get('assistantReply', '')) for turn in history)
        analytics['averageResponseLength'] = total_length // len(history)

    return analytics


def get_thread_id(session_id: str) -> Optional[str]:
    """
    Get OpenAI thread ID for a conversation session

    Args:
        session_id: Conversation session ID

    Returns:
        Thread ID or None if not found
    """
    try:
        table = get_conversations_table()

        # Get the conversation item
        response = table.get_item(
            Key={'conversationId': session_id}
        )

        if 'Item' in response:
            return response['Item'].get('threadId')

        return None

    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error getting thread ID for session {session_id}: {e}")
        return None


def store_thread_id(session_id: str, thread_id: str) -> bool:
    """
    Store OpenAI thread ID for a conversation session

    Args:
        session_id: Conversation session ID
        thread_id: OpenAI thread ID

    Returns:
        True if successful, False otherwise
    """
    try:
        table = get_conversations_table()
        timestamp = datetime.utcnow().isoformat() + 'Z'

        # Update the conversation item with thread ID
        table.update_item(
            Key={'conversationId': session_id},
            UpdateExpression='SET threadId = :threadId, lastActivity = :lastActivity',
            ExpressionAttributeValues={
                ':threadId': thread_id,
                ':lastActivity': timestamp
            }
        )

        return True

    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error storing thread ID for session {session_id}: {e}")
        return False