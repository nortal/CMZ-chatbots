"""
General DynamoDB utilities for all tables
Provides common DynamoDB functionality across the application
"""

import os
import boto3
from boto3.dynamodb.conditions import Key, Attr
from typing import Dict, List, Optional, Any
import json
from datetime import datetime

# DynamoDB configuration
AWS_REGION = os.getenv('AWS_REGION', 'us-west-2')

# Initialize DynamoDB resource
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)

def table(table_name: str = None):
    """
    Get a DynamoDB table reference

    Args:
        table_name: Name of the table. If not provided, defaults to animals table

    Returns:
        boto3 DynamoDB Table resource
    """
    if not table_name:
        # Default to animals table for backward compatibility
        table_name = os.getenv('ANIMALS_DYNAMO_TABLE_NAME', 'quest-dev-animals')

    return dynamodb.Table(table_name)


def to_ddb(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert Python dict to DynamoDB format
    Handles None values and other conversions
    """
    # DynamoDB doesn't accept None values
    cleaned = {}
    for key, value in item.items():
        if value is not None:
            if isinstance(value, dict):
                cleaned[key] = to_ddb(value)
            elif isinstance(value, list):
                cleaned[key] = [to_ddb(v) if isinstance(v, dict) else v for v in value if v is not None]
            else:
                cleaned[key] = value
    return cleaned


def from_ddb(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert DynamoDB item to Python dict
    """
    # For now, just return as-is since boto3 handles most conversions
    return item


def now_iso() -> str:
    """
    Get current timestamp in ISO format
    """
    return datetime.utcnow().isoformat() + 'Z'


def model_to_json_keyed_dict(model_instance) -> Dict[str, Any]:
    """
    Convert an OpenAPI model instance to a JSON-serializable dict
    """
    if hasattr(model_instance, 'to_dict'):
        return model_instance.to_dict()
    elif hasattr(model_instance, '__dict__'):
        return model_instance.__dict__
    else:
        return dict(model_instance)


def ensure_pk(item: Dict[str, Any], pk_field: str, prefix: str = None) -> None:
    """
    Ensure primary key exists in item, generate if missing

    Args:
        item: Dictionary to check/update
        pk_field: Name of the primary key field
        prefix: Optional prefix for generated IDs
    """
    import uuid
    if pk_field not in item or not item[pk_field]:
        if prefix:
            item[pk_field] = f"{prefix}_{uuid.uuid4()}"
        else:
            item[pk_field] = str(uuid.uuid4())


def error_response(error: Exception) -> Dict[str, Any]:
    """
    Create standard error response from exception
    """
    return {
        'error': str(error),
        'type': type(error).__name__
    }


def not_found(resource_type: str, resource_id: str) -> Dict[str, Any]:
    """
    Create standard not found response
    """
    return {
        'error': f'{resource_type} not found',
        'id': resource_id
    }


# Table-specific helper functions
def get_animals_table():
    """Get the animals DynamoDB table"""
    return table(os.getenv('ANIMALS_DYNAMO_TABLE_NAME', 'quest-dev-animals'))


def get_families_table():
    """Get the families DynamoDB table"""
    return table(os.getenv('FAMILY_DYNAMO_TABLE_NAME', 'quest-dev-family'))


def get_users_table():
    """Get the users DynamoDB table"""
    return table(os.getenv('USERS_DYNAMO_TABLE_NAME', 'quest-dev-users'))


def get_conversations_table():
    """Get the conversations DynamoDB table"""
    return table(os.getenv('CONVERSATION_DYNAMO_TABLE_NAME', 'quest-dev-conversation'))


def get_sessions_table():
    """Get the conversation sessions DynamoDB table"""
    return table(os.getenv('CONVERSATION_SESSION_TABLE_NAME', 'quest-dev-session'))