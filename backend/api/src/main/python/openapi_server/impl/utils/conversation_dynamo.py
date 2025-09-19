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

def create_conversation_session(user_id: str, animal_id: str) -> str:
    """
    Create a new conversation session

    Args:
        user_id: ID of the user
        animal_id: ID of the animal

    Returns:
        session_id: Unique identifier for the session
    """
    session_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat() + 'Z'

    table = get_sessions_table()
    table.put_item(
        Item={
            'sessionId': session_id,
            'userId': user_id,
            'animalId': animal_id,
            'startTime': timestamp,
            'lastActivity': timestamp,
            'messageCount': 0,
            'status': 'active'
        }
    )

    return session_id

def store_conversation_turn(
    session_id: str,
    user_message: str,
    assistant_reply: str,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    Store a conversation turn in DynamoDB

    Args:
        session_id: Conversation session ID
        user_message: User's message
        assistant_reply: Assistant's reply
        metadata: Additional metadata (tokens, latency, etc.)

    Returns:
        turn_id: Unique identifier for the turn
    """
    turn_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat() + 'Z'

    table = get_conversations_table()

    item = {
        'sessionId': session_id,
        'turnId': turn_id,
        'timestamp': timestamp,
        'userMessage': user_message,
        'assistantReply': assistant_reply,
        'metadata': metadata or {}
    }

    table.put_item(Item=item)

    # Update session last activity and message count
    sessions_table = get_sessions_table()
    sessions_table.update_item(
        Key={'sessionId': session_id},
        UpdateExpression='SET lastActivity = :time, messageCount = messageCount + :inc',
        ExpressionAttributeValues={
            ':time': timestamp,
            ':inc': 1
        }
    )

    return turn_id

def get_conversation_history(
    session_id: str,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Retrieve conversation history for a session

    Args:
        session_id: Conversation session ID
        limit: Maximum number of turns to retrieve

    Returns:
        List of conversation turns
    """
    table = get_conversations_table()

    response = table.query(
        KeyConditionExpression=Key('sessionId').eq(session_id),
        ScanIndexForward=False,  # Most recent first
        Limit=limit
    )

    # Reverse to get chronological order
    items = response.get('Items', [])
    items.reverse()

    return items

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
        session_id: Session ID

    Returns:
        Session information or None if not found
    """
    table = get_sessions_table()

    try:
        response = table.get_item(Key={'sessionId': session_id})
        return response.get('Item')
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