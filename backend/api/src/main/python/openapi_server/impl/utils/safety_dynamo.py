"""
DynamoDB utilities for CMZ Chatbots safety and personalization tables.

This module provides centralized DynamoDB operations for the 5 new safety tables:
1. GuardrailsConfig - Guardrails configuration and templates
2. ContentValidation - Content moderation logs and validation history
3. UserContextProfile - User personalization data and preferences
4. ConversationAnalytics - Conversation analytics and behavior tracking
5. PrivacyAuditLog - Privacy audit logs for COPPA compliance

Environment Variables:
    AWS_PROFILE - AWS profile for authentication (default: cmz)
    AWS_REGION - AWS region for DynamoDB (default: us-west-2)
    DYNAMODB_ENDPOINT_URL - Override for local DynamoDB testing
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import uuid

import boto3
from botocore.exceptions import ClientError, BotoCoreError
from boto3.dynamodb.conditions import Key, Attr

from .dynamo import (
    to_ddb, from_ddb, now_iso, error_response,
    model_to_json_keyed_dict, ensure_pk
)

# Configure logging
logger = logging.getLogger(__name__)


class SafetyTableName(Enum):
    """Safety table names enumeration."""
    GUARDRAILS_CONFIG = "quest-dev-guardrails-config"
    CONTENT_VALIDATION = "quest-dev-content-validation"
    USER_CONTEXT_PROFILE = "quest-dev-user-context"
    CONVERSATION_ANALYTICS = "quest-dev-conversation-analytics"
    PRIVACY_AUDIT_LOG = "quest-dev-privacy-audit"


@dataclass
class TableInfo:
    """Table configuration information."""
    name: str
    primary_key: str
    sort_key: Optional[str] = None
    gsi_configs: Optional[Dict[str, Dict[str, str]]] = None


class SafetyDynamoClient:
    """Centralized DynamoDB client for safety and personalization tables."""

    def __init__(self, region: str = None, endpoint_url: str = None):
        """
        Initialize DynamoDB client for safety tables.

        Args:
            region: AWS region (defaults to AWS_REGION env var or us-west-2)
            endpoint_url: DynamoDB endpoint URL (for local testing)
        """
        self.region = region or os.getenv('AWS_REGION', 'us-west-2')
        self.endpoint_url = endpoint_url or os.getenv('DYNAMODB_ENDPOINT_URL')

        # Initialize DynamoDB resources
        dynamodb_config = {'region_name': self.region}
        if self.endpoint_url:
            dynamodb_config['endpoint_url'] = self.endpoint_url

        self.dynamodb = boto3.resource('dynamodb', **dynamodb_config)
        self.dynamodb_client = boto3.client('dynamodb', **dynamodb_config)

        # Table configurations
        self.table_configs = {
            SafetyTableName.GUARDRAILS_CONFIG: TableInfo(
                name=SafetyTableName.GUARDRAILS_CONFIG.value,
                primary_key='configId',
                gsi_configs={
                    'AnimalIndex': {'pk': 'animalId'},
                    'TemplateIndex': {'pk': 'templateId'}
                }
            ),
            SafetyTableName.CONTENT_VALIDATION: TableInfo(
                name=SafetyTableName.CONTENT_VALIDATION.value,
                primary_key='validationId',
                gsi_configs={
                    'SessionIndex': {'pk': 'sessionId', 'sk': 'timestamp'},
                    'UserIndex': {'pk': 'userId', 'sk': 'timestamp'}
                }
            ),
            SafetyTableName.USER_CONTEXT_PROFILE: TableInfo(
                name=SafetyTableName.USER_CONTEXT_PROFILE.value,
                primary_key='userId',
                gsi_configs={
                    'ParentIndex': {'pk': 'parentId', 'sk': 'lastUpdated'}
                }
            ),
            SafetyTableName.CONVERSATION_ANALYTICS: TableInfo(
                name=SafetyTableName.CONVERSATION_ANALYTICS.value,
                primary_key='analyticsId',
                gsi_configs={
                    'SessionIndex': {'pk': 'sessionId'},
                    'UserIndex': {'pk': 'userId', 'sk': 'timestamp'},
                    'AnimalIndex': {'pk': 'animalId', 'sk': 'timestamp'}
                }
            ),
            SafetyTableName.PRIVACY_AUDIT_LOG: TableInfo(
                name=SafetyTableName.PRIVACY_AUDIT_LOG.value,
                primary_key='auditId',
                gsi_configs={
                    'UserIndex': {'pk': 'userId', 'sk': 'timestamp'},
                    'ParentIndex': {'pk': 'parentId', 'sk': 'timestamp'},
                    'ActionTypeIndex': {'pk': 'actionType', 'sk': 'timestamp'}
                }
            )
        }

        # Cache for table objects
        self._table_cache = {}

        logger.info(f"SafetyDynamoClient initialized for region: {self.region}")

    def get_table(self, table_name: SafetyTableName) -> Any:
        """Get DynamoDB table object with caching."""
        if table_name not in self._table_cache:
            table_config = self.table_configs[table_name]
            self._table_cache[table_name] = self.dynamodb.Table(table_config.name)

        return self._table_cache[table_name]

    def generate_id(self, prefix: str = "") -> str:
        """Generate unique ID with optional prefix."""
        unique_id = str(uuid.uuid4())
        return f"{prefix}_{unique_id}" if prefix else unique_id

    def create_audit_entry(
        self,
        user_id: str,
        action_type: str,
        action_details: Dict[str, Any],
        parent_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Tuple[Dict[str, Any], int]:
        """
        Create a privacy audit log entry.

        Args:
            user_id: User ID the action was performed on
            action_type: Type of action (DATA_ACCESS, DATA_EXPORT, etc.)
            action_details: Additional details about the action
            parent_id: Parent ID if action was performed by parent
            ip_address: IP address of the client
            user_agent: User agent of the client

        Returns:
            Tuple of (audit_entry, status_code)
        """
        try:
            table = self.get_table(SafetyTableName.PRIVACY_AUDIT_LOG)

            audit_entry = {
                'auditId': self.generate_id('audit'),
                'userId': user_id,
                'actionType': action_type,
                'actionDetails': action_details,
                'timestamp': now_iso(),
                'ipAddress': ip_address,
                'userAgent': user_agent
            }

            if parent_id:
                audit_entry['parentId'] = parent_id

            # Store in DynamoDB
            table.put_item(Item=to_ddb(audit_entry))

            logger.info(f"Created audit entry {audit_entry['auditId']} for user {user_id}")
            return from_ddb(audit_entry), 201

        except ClientError as e:
            logger.error(f"Failed to create audit entry: {e}")
            return error_response(e)
        except Exception as e:
            logger.error(f"Unexpected error creating audit entry: {e}")
            return {"error": "Internal server error"}, 500

    def get_audit_logs(
        self,
        user_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        action_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100
    ) -> Tuple[Dict[str, Any], int]:
        """
        Retrieve privacy audit logs with filtering.

        Args:
            user_id: Filter by user ID
            parent_id: Filter by parent ID
            action_type: Filter by action type
            start_date: Filter from this date (ISO8601)
            end_date: Filter until this date (ISO8601)
            limit: Maximum number of entries to return

        Returns:
            Tuple of (audit_logs, status_code)
        """
        try:
            table = self.get_table(SafetyTableName.PRIVACY_AUDIT_LOG)

            # Determine which index to use based on filters
            if user_id:
                response = self._query_user_audit_logs(table, user_id, start_date, end_date, limit)
            elif parent_id:
                response = self._query_parent_audit_logs(table, parent_id, start_date, end_date, limit)
            elif action_type:
                response = self._query_action_type_audit_logs(table, action_type, start_date, end_date, limit)
            else:
                # Scan with filters (less efficient, use with caution)
                response = self._scan_audit_logs(table, start_date, end_date, limit)

            audit_entries = [from_ddb(item) for item in response.get('Items', [])]

            return {
                'auditEntries': audit_entries,
                'totalCount': len(audit_entries),
                'lastEvaluatedKey': response.get('LastEvaluatedKey')
            }, 200

        except ClientError as e:
            logger.error(f"Failed to get audit logs: {e}")
            return error_response(e)
        except Exception as e:
            logger.error(f"Unexpected error getting audit logs: {e}")
            return {"error": "Internal server error"}, 500

    def _query_user_audit_logs(self, table, user_id: str, start_date: Optional[str], end_date: Optional[str], limit: int):
        """Query audit logs by user ID using UserIndex."""
        key_condition = Key('userId').eq(user_id)

        if start_date and end_date:
            key_condition = key_condition & Key('timestamp').between(start_date, end_date)
        elif start_date:
            key_condition = key_condition & Key('timestamp').gte(start_date)
        elif end_date:
            key_condition = key_condition & Key('timestamp').lte(end_date)

        return table.query(
            IndexName='UserIndex',
            KeyConditionExpression=key_condition,
            Limit=limit,
            ScanIndexForward=False  # Most recent first
        )

    def _query_parent_audit_logs(self, table, parent_id: str, start_date: Optional[str], end_date: Optional[str], limit: int):
        """Query audit logs by parent ID using ParentIndex."""
        key_condition = Key('parentId').eq(parent_id)

        if start_date and end_date:
            key_condition = key_condition & Key('timestamp').between(start_date, end_date)
        elif start_date:
            key_condition = key_condition & Key('timestamp').gte(start_date)
        elif end_date:
            key_condition = key_condition & Key('timestamp').lte(end_date)

        return table.query(
            IndexName='ParentIndex',
            KeyConditionExpression=key_condition,
            Limit=limit,
            ScanIndexForward=False  # Most recent first
        )

    def _query_action_type_audit_logs(self, table, action_type: str, start_date: Optional[str], end_date: Optional[str], limit: int):
        """Query audit logs by action type using ActionTypeIndex."""
        key_condition = Key('actionType').eq(action_type)

        if start_date and end_date:
            key_condition = key_condition & Key('timestamp').between(start_date, end_date)
        elif start_date:
            key_condition = key_condition & Key('timestamp').gte(start_date)
        elif end_date:
            key_condition = key_condition & Key('timestamp').lte(end_date)

        return table.query(
            IndexName='ActionTypeIndex',
            KeyConditionExpression=key_condition,
            Limit=limit,
            ScanIndexForward=False  # Most recent first
        )

    def _scan_audit_logs(self, table, start_date: Optional[str], end_date: Optional[str], limit: int):
        """Scan audit logs with date filters (less efficient)."""
        filter_expression = None

        if start_date and end_date:
            filter_expression = Attr('timestamp').between(start_date, end_date)
        elif start_date:
            filter_expression = Attr('timestamp').gte(start_date)
        elif end_date:
            filter_expression = Attr('timestamp').lte(end_date)

        scan_params = {'Limit': limit}
        if filter_expression:
            scan_params['FilterExpression'] = filter_expression

        return table.scan(**scan_params)

    def store_content_validation(
        self,
        session_id: str,
        user_id: str,
        content: str,
        validation_result: Dict[str, Any],
        moderation_response: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], int]:
        """
        Store content validation result.

        Args:
            session_id: Conversation session ID
            user_id: User ID
            content: Original content that was validated
            validation_result: Validation result summary
            moderation_response: Full OpenAI moderation response

        Returns:
            Tuple of (validation_entry, status_code)
        """
        try:
            table = self.get_table(SafetyTableName.CONTENT_VALIDATION)

            validation_entry = {
                'validationId': self.generate_id('val'),
                'sessionId': session_id,
                'userId': user_id,
                'timestamp': now_iso(),
                'contentHash': str(hash(content)),  # Store hash, not full content
                'contentLength': len(content),
                'validationResult': validation_result,
                'moderationResponse': moderation_response,
                'isContentSafe': validation_result.get('isContentSafe', False)
            }

            table.put_item(Item=to_ddb(validation_entry))

            logger.info(f"Stored content validation {validation_entry['validationId']} for session {session_id}")
            return from_ddb(validation_entry), 201

        except ClientError as e:
            logger.error(f"Failed to store content validation: {e}")
            return error_response(e)
        except Exception as e:
            logger.error(f"Unexpected error storing content validation: {e}")
            return {"error": "Internal server error"}, 500

    def get_user_context(self, user_id: str) -> Tuple[Dict[str, Any], int]:
        """
        Get user context profile.

        Args:
            user_id: User ID

        Returns:
            Tuple of (context_profile, status_code)
        """
        try:
            table = self.get_table(SafetyTableName.USER_CONTEXT_PROFILE)

            response = table.get_item(Key={'userId': user_id})

            if 'Item' in response:
                return from_ddb(response['Item']), 200
            else:
                return {"error": "User context not found"}, 404

        except ClientError as e:
            logger.error(f"Failed to get user context: {e}")
            return error_response(e)
        except Exception as e:
            logger.error(f"Unexpected error getting user context: {e}")
            return {"error": "Internal server error"}, 500

    def update_user_context(
        self,
        user_id: str,
        context_data: Dict[str, Any],
        parent_id: Optional[str] = None
    ) -> Tuple[Dict[str, Any], int]:
        """
        Update user context profile.

        Args:
            user_id: User ID
            context_data: Context data to store
            parent_id: Parent ID if user is a child

        Returns:
            Tuple of (updated_context, status_code)
        """
        try:
            table = self.get_table(SafetyTableName.USER_CONTEXT_PROFILE)

            # Get existing context or create new
            existing_response = table.get_item(Key={'userId': user_id})

            if 'Item' in existing_response:
                context_profile = from_ddb(existing_response['Item'])
                # Merge with existing data
                context_profile.update(context_data)
            else:
                # Create new context profile
                context_profile = {
                    'userId': user_id,
                    'createdAt': now_iso(),
                    **context_data
                }

            # Update timestamps
            context_profile['lastUpdated'] = now_iso()
            if parent_id:
                context_profile['parentId'] = parent_id

            # Store updated context
            table.put_item(Item=to_ddb(context_profile))

            logger.info(f"Updated user context for {user_id}")
            return context_profile, 200

        except ClientError as e:
            logger.error(f"Failed to update user context: {e}")
            return error_response(e)
        except Exception as e:
            logger.error(f"Unexpected error updating user context: {e}")
            return {"error": "Internal server error"}, 500

    def store_conversation_analytics(
        self,
        session_id: str,
        user_id: str,
        animal_id: str,
        analytics_data: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], int]:
        """
        Store conversation analytics data.

        Args:
            session_id: Conversation session ID
            user_id: User ID
            animal_id: Animal ID
            analytics_data: Analytics data to store

        Returns:
            Tuple of (analytics_entry, status_code)
        """
        try:
            table = self.get_table(SafetyTableName.CONVERSATION_ANALYTICS)

            analytics_entry = {
                'analyticsId': self.generate_id('analytics'),
                'sessionId': session_id,
                'userId': user_id,
                'animalId': animal_id,
                'timestamp': now_iso(),
                **analytics_data
            }

            table.put_item(Item=to_ddb(analytics_entry))

            logger.info(f"Stored conversation analytics {analytics_entry['analyticsId']} for session {session_id}")
            return from_ddb(analytics_entry), 201

        except ClientError as e:
            logger.error(f"Failed to store conversation analytics: {e}")
            return error_response(e)
        except Exception as e:
            logger.error(f"Unexpected error storing conversation analytics: {e}")
            return {"error": "Internal server error"}, 500

    def get_guardrails_config(self, config_id: str) -> Tuple[Dict[str, Any], int]:
        """
        Get guardrails configuration.

        Args:
            config_id: Guardrails configuration ID

        Returns:
            Tuple of (config, status_code)
        """
        try:
            table = self.get_table(SafetyTableName.GUARDRAILS_CONFIG)

            response = table.get_item(Key={'configId': config_id})

            if 'Item' in response:
                return from_ddb(response['Item']), 200
            else:
                return {"error": "Guardrails configuration not found"}, 404

        except ClientError as e:
            logger.error(f"Failed to get guardrails config: {e}")
            return error_response(e)
        except Exception as e:
            logger.error(f"Unexpected error getting guardrails config: {e}")
            return {"error": "Internal server error"}, 500

    def store_guardrails_config(self, config_data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """
        Store or update guardrails configuration.

        Args:
            config_data: Configuration data

        Returns:
            Tuple of (stored_config, status_code)
        """
        try:
            table = self.get_table(SafetyTableName.GUARDRAILS_CONFIG)

            # Ensure required fields
            if 'configId' not in config_data:
                config_data['configId'] = self.generate_id('config')

            config_data['lastUpdated'] = now_iso()
            config_data.setdefault('createdAt', now_iso())

            table.put_item(Item=to_ddb(config_data))

            logger.info(f"Stored guardrails config {config_data['configId']}")
            return from_ddb(config_data), 201

        except ClientError as e:
            logger.error(f"Failed to store guardrails config: {e}")
            return error_response(e)
        except Exception as e:
            logger.error(f"Unexpected error storing guardrails config: {e}")
            return {"error": "Internal server error"}, 500

    def health_check(self) -> Tuple[Dict[str, Any], int]:
        """
        Perform health check on all safety tables.

        Returns:
            Tuple of (health_status, status_code)
        """
        try:
            health_status = {
                'status': 'healthy',
                'region': self.region,
                'timestamp': now_iso(),
                'tables': {}
            }

            all_healthy = True

            for table_name in SafetyTableName:
                try:
                    table = self.get_table(table_name)
                    # Simple table access test
                    table.table_status

                    health_status['tables'][table_name.value] = {
                        'status': 'healthy',
                        'name': table.table_name
                    }

                except Exception as e:
                    health_status['tables'][table_name.value] = {
                        'status': 'unhealthy',
                        'error': str(e)
                    }
                    all_healthy = False

            if not all_healthy:
                health_status['status'] = 'degraded'

            status_code = 200 if all_healthy else 503
            return health_status, status_code

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': now_iso()
            }, 503

    def store_analytics_event(self, event_data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """
        Store analytics event in conversation analytics table.

        Args:
            event_data: Analytics event data

        Returns:
            Tuple of (stored_event, status_code)
        """
        try:
            table = self.get_table(SafetyTableName.CONVERSATION_ANALYTICS)

            # Ensure required fields
            event_data.setdefault('eventId', self.generate_id('analytics'))
            event_data.setdefault('timestamp', now_iso())

            # Store the event
            response = table.put_item(Item=to_ddb(event_data))
            logger.info(f"Stored analytics event: {event_data.get('eventId')}")

            return from_ddb(event_data), 201

        except Exception as e:
            logger.error(f"Failed to store analytics event: {e}")
            return error_response(e)

    def get_conversation_history(self, conversation_id: str, user_id: str) -> List[Dict[str, Any]]:
        """
        Get conversation history for a user and conversation.

        Args:
            conversation_id: Conversation ID
            user_id: User ID

        Returns:
            List of conversation turns
        """
        try:
            table = self.get_table(SafetyTableName.CONVERSATION_ANALYTICS)

            # Query for conversation history
            response = table.query(
                IndexName='ConversationIndex',  # Assuming this GSI exists
                KeyConditionExpression=Key('conversationId').eq(conversation_id),
                FilterExpression=Attr('userId').eq(user_id),
                ScanIndexForward=True  # Sort by timestamp ascending
            )

            history = [from_ddb(item) for item in response.get('Items', [])]
            logger.info(f"Retrieved {len(history)} conversation turns for {conversation_id}")

            return history

        except Exception as e:
            logger.error(f"Failed to get conversation history: {e}")
            return []

    def store_conversation_turn(self, turn_data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """
        Store conversation turn in analytics table.

        Args:
            turn_data: Conversation turn data

        Returns:
            Tuple of (stored_turn, status_code)
        """
        try:
            table = self.get_table(SafetyTableName.CONVERSATION_ANALYTICS)

            # Ensure required fields
            turn_data.setdefault('turnId', self.generate_id('turn'))
            turn_data.setdefault('timestamp', now_iso())

            # Store the turn
            response = table.put_item(Item=to_ddb(turn_data))
            logger.info(f"Stored conversation turn: {turn_data.get('turnId')}")

            return from_ddb(turn_data), 201

        except Exception as e:
            logger.error(f"Failed to store conversation turn: {e}")
            return error_response(e)


# Global client instance
_safety_dynamo_client: Optional[SafetyDynamoClient] = None


def get_safety_dynamo_client() -> SafetyDynamoClient:
    """Get singleton SafetyDynamoClient instance."""
    global _safety_dynamo_client

    if _safety_dynamo_client is None:
        _safety_dynamo_client = SafetyDynamoClient()

    return _safety_dynamo_client


# Convenience functions for common operations
def create_audit_log(user_id: str, action_type: str, action_details: Dict[str, Any], **kwargs) -> Tuple[Dict[str, Any], int]:
    """Convenience function to create audit log entry."""
    client = get_safety_dynamo_client()
    return client.create_audit_entry(user_id, action_type, action_details, **kwargs)


def get_user_context_simple(user_id: str) -> Optional[Dict[str, Any]]:
    """Simple function to get user context, returns None if not found."""
    try:
        client = get_safety_dynamo_client()
        context, status = client.get_user_context(user_id)
        return context if status == 200 else None
    except Exception:
        return None


def update_user_context_simple(user_id: str, context_data: Dict[str, Any]) -> bool:
    """Simple function to update user context, returns True if successful."""
    try:
        client = get_safety_dynamo_client()
        _, status = client.update_user_context(user_id, context_data)
        return status == 200
    except Exception:
        return False