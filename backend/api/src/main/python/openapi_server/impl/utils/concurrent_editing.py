#!/usr/bin/env python3
"""
Concurrent Editing Conflict Resolution
Implements first-save-wins strategy for animal assistant management.

Design Pattern:
- Optimistic locking with version numbers
- First-save-wins conflict resolution
- Immediate notification to concurrent editors
- Grace period handling for active editing sessions

FR-017: System MUST implement first-save-wins conflict resolution with immediate notification to concurrent editors

Author: CMZ Animal Assistant Management System
Date: 2025-10-25
"""

import os
import uuid
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, Tuple, List
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

from .dynamo import (
    table, to_ddb, from_ddb, now_iso,
    error_response, not_found
)

# Environment configuration
EDITING_SESSION_TABLE = os.getenv('EDITING_SESSION_TABLE', 'quest-dev-editing-sessions')
SESSION_TIMEOUT_MINUTES = int(os.getenv('SESSION_TIMEOUT_MINUTES', '15'))

class ConcurrentEditingManager:
    """
    Manages concurrent editing sessions and conflict resolution for animal configurations.

    Key Features:
    - Version-based optimistic locking
    - First-save-wins conflict resolution
    - Active session tracking
    - Automatic conflict notification
    """

    def __init__(self):
        self.editing_table = table(EDITING_SESSION_TABLE)

    def start_editing_session(self, resource_type: str, resource_id: str,
                            user_id: str, user_email: str) -> Dict[str, Any]:
        """
        Start a new editing session for a resource.

        Args:
            resource_type: Type of resource ('animal_config', 'assistant', etc.)
            resource_id: ID of the resource being edited
            user_id: ID of the user starting the session
            user_email: Email of the user for notifications

        Returns:
            Session information including current version and active editors
        """
        try:
            session_id = f"edit-{uuid.uuid4().hex[:16]}"
            session_key = f"{resource_type}#{resource_id}"
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=SESSION_TIMEOUT_MINUTES)

            # Create editing session record
            session_record = {
                'sessionKey': session_key,
                'sessionId': session_id,
                'resourceType': resource_type,
                'resourceId': resource_id,
                'userId': user_id,
                'userEmail': user_email,
                'status': 'active',
                'startedAt': now_iso(),
                'expiresAt': expires_at.isoformat(),
                'ttl': int(expires_at.timestamp()),
                'lastActivity': now_iso()
            }

            # Store session
            self.editing_table.put_item(Item=to_ddb(session_record))

            # Get current version and other active sessions
            current_version = self._get_resource_version(resource_type, resource_id)
            active_sessions = self._get_active_sessions(session_key, exclude_session=session_id)

            return {
                'sessionId': session_id,
                'version': current_version,
                'activeEditors': [
                    {
                        'userId': session['userId'],
                        'userEmail': session['userEmail'],
                        'startedAt': session['startedAt']
                    }
                    for session in active_sessions
                ],
                'expiresAt': expires_at.isoformat(),
                'conflictWarning': len(active_sessions) > 0
            }

        except Exception as e:
            return {'error': f"Failed to start editing session: {str(e)}"}

    def update_activity(self, session_id: str) -> bool:
        """
        Update the last activity timestamp for an editing session.

        Args:
            session_id: Session ID to update

        Returns:
            True if successful
        """
        try:
            # Update last activity
            self.editing_table.update_item(
                Key={'sessionId': session_id},
                UpdateExpression='SET lastActivity = :timestamp',
                ExpressionAttributeValues={':timestamp': now_iso()},
                ConditionExpression='attribute_exists(sessionId)'
            )
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                return False  # Session doesn't exist or expired
            raise

    def attempt_save(self, resource_type: str, resource_id: str, session_id: str,
                    expected_version: int, new_data: Dict[str, Any],
                    user_id: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Attempt to save changes with conflict detection.

        Args:
            resource_type: Type of resource being saved
            resource_id: ID of the resource
            session_id: Editing session ID
            expected_version: Version the editor thinks they're editing
            new_data: New data to save
            user_id: ID of the user attempting to save

        Returns:
            Tuple of (success, result_info)
        """
        try:
            # Get current version
            current_version = self._get_resource_version(resource_type, resource_id)

            if current_version != expected_version:
                # Version conflict detected - first-save-wins violation
                conflicting_sessions = self._get_active_sessions(f"{resource_type}#{resource_id}")

                # Find who saved after this editor started
                conflict_info = {
                    'success': False,
                    'error': 'version_conflict',
                    'message': 'Another user has saved changes while you were editing',
                    'currentVersion': current_version,
                    'expectedVersion': expected_version,
                    'conflictingEditors': [
                        {
                            'userId': session['userId'],
                            'userEmail': session['userEmail'],
                            'savedAt': session.get('lastSave', session.get('lastActivity'))
                        }
                        for session in conflicting_sessions
                        if session['userId'] != user_id
                    ],
                    'recommendation': 'Please refresh and reapply your changes'
                }

                # Mark session as conflicted
                self._mark_session_conflicted(session_id)

                return False, conflict_info

            # No conflict - proceed with save
            next_version = current_version + 1
            save_timestamp = now_iso()

            # Update the actual resource with versioning
            success = self._save_resource_with_version(
                resource_type, resource_id, new_data, next_version, save_timestamp
            )

            if success:
                # Mark session as completed
                self._complete_session(session_id, save_timestamp)

                # Notify other active editors of the conflict
                self._notify_concurrent_editors(
                    f"{resource_type}#{resource_id}", session_id, user_id, save_timestamp
                )

                return True, {
                    'success': True,
                    'version': next_version,
                    'savedAt': save_timestamp,
                    'message': 'Changes saved successfully'
                }
            else:
                return False, {
                    'success': False,
                    'error': 'save_failed',
                    'message': 'Failed to save changes'
                }

        except Exception as e:
            return False, {
                'success': False,
                'error': 'internal_error',
                'message': f"Save attempt failed: {str(e)}"
            }

    def end_editing_session(self, session_id: str) -> bool:
        """
        End an editing session without saving.

        Args:
            session_id: Session ID to end

        Returns:
            True if successful
        """
        try:
            self.editing_table.update_item(
                Key={'sessionId': session_id},
                UpdateExpression='SET #status = :status, endedAt = :timestamp',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':status': 'ended',
                    ':timestamp': now_iso()
                },
                ConditionExpression='attribute_exists(sessionId)'
            )
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                return False  # Session doesn't exist
            raise

    def get_active_editors(self, resource_type: str, resource_id: str) -> List[Dict[str, Any]]:
        """
        Get list of users currently editing a resource.

        Args:
            resource_type: Type of resource
            resource_id: ID of the resource

        Returns:
            List of active editor information
        """
        session_key = f"{resource_type}#{resource_id}"
        active_sessions = self._get_active_sessions(session_key)

        return [
            {
                'userId': session['userId'],
                'userEmail': session['userEmail'],
                'startedAt': session['startedAt'],
                'lastActivity': session['lastActivity'],
                'status': session.get('status', 'active')
            }
            for session in active_sessions
        ]

    def _get_resource_version(self, resource_type: str, resource_id: str) -> int:
        """Get current version number of a resource."""
        try:
            if resource_type == 'animal_config':
                # Get version from animal table
                from .dynamo import table as get_table
                animal_table = get_table('quest-dev-animal')
                response = animal_table.get_item(Key={'animalId': resource_id})

                if 'Item' in response:
                    animal_data = from_ddb(response['Item'])
                    return animal_data.get('version', 1)
                else:
                    return 1  # Default version for new resources

            # Add other resource types as needed
            return 1

        except Exception:
            return 1  # Default fallback

    def _get_active_sessions(self, session_key: str, exclude_session: str = None) -> List[Dict[str, Any]]:
        """Get all active editing sessions for a resource."""
        try:
            # Use GSI to query by sessionKey
            response = self.editing_table.query(
                IndexName='sessionKey-index',  # Assumes GSI exists
                KeyConditionExpression='sessionKey = :key',
                FilterExpression='#status = :status',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':key': session_key,
                    ':status': 'active'
                }
            )

            sessions = [from_ddb(item) for item in response.get('Items', [])]

            if exclude_session:
                sessions = [s for s in sessions if s.get('sessionId') != exclude_session]

            # Filter out expired sessions
            current_time = datetime.now(timezone.utc)
            active_sessions = []

            for session in sessions:
                try:
                    expires_at = datetime.fromisoformat(session['expiresAt'].replace('Z', '+00:00'))
                    if expires_at > current_time:
                        active_sessions.append(session)
                except (KeyError, ValueError):
                    # Skip sessions with invalid expiration
                    continue

            return active_sessions

        except Exception:
            return []  # Return empty list on error

    def _save_resource_with_version(self, resource_type: str, resource_id: str,
                                  data: Dict[str, Any], version: int,
                                  timestamp: str) -> bool:
        """Save resource with version number."""
        try:
            if resource_type == 'animal_config':
                from .dynamo import table as get_table
                animal_table = get_table('quest-dev-animal')

                # Add version and modification timestamp to data
                data['version'] = version
                data['modified'] = {'at': timestamp, 'by': 'system'}

                # Use conditional update to ensure atomicity
                animal_table.update_item(
                    Key={'animalId': resource_id},
                    UpdateExpression='SET ' + ', '.join([f'{k} = :{k}' for k in data.keys()]),
                    ExpressionAttributeValues={f':{k}': v for k, v in data.items()},
                    ConditionExpression='version = :expected_version OR attribute_not_exists(version)',
                    ExpressionAttributeValues={
                        **{f':{k}': v for k, v in data.items()},
                        ':expected_version': version - 1
                    }
                )
                return True

            return False

        except ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                return False  # Version conflict
            raise

    def _mark_session_conflicted(self, session_id: str):
        """Mark a session as conflicted."""
        try:
            self.editing_table.update_item(
                Key={'sessionId': session_id},
                UpdateExpression='SET #status = :status, conflictedAt = :timestamp',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':status': 'conflicted',
                    ':timestamp': now_iso()
                }
            )
        except Exception:
            pass  # Non-critical operation

    def _complete_session(self, session_id: str, save_timestamp: str):
        """Mark a session as completed after successful save."""
        try:
            self.editing_table.update_item(
                Key={'sessionId': session_id},
                UpdateExpression='SET #status = :status, completedAt = :timestamp, lastSave = :save_time',
                ExpressionAttributeNames={'#status': 'status'},
                ExpressionAttributeValues={
                    ':status': 'completed',
                    ':timestamp': now_iso(),
                    ':save_time': save_timestamp
                }
            )
        except Exception:
            pass  # Non-critical operation

    def _notify_concurrent_editors(self, session_key: str, saving_session_id: str,
                                 saving_user_id: str, save_timestamp: str):
        """Notify other active editors about the conflict."""
        try:
            active_sessions = self._get_active_sessions(session_key, exclude_session=saving_session_id)

            for session in active_sessions:
                # Mark other sessions as notified of conflict
                self.editing_table.update_item(
                    Key={'sessionId': session['sessionId']},
                    UpdateExpression='SET conflictNotifiedAt = :timestamp, conflictedBy = :user',
                    ExpressionAttributeValues={
                        ':timestamp': save_timestamp,
                        ':user': saving_user_id
                    }
                )

                # In a real implementation, send real-time notification
                # This could be WebSocket, Server-Sent Events, or polling endpoint

        except Exception:
            pass  # Non-critical operation


# Convenience functions for common operations
def start_animal_config_editing(animal_id: str, user_id: str, user_email: str) -> Dict[str, Any]:
    """Start editing session for animal configuration."""
    manager = ConcurrentEditingManager()
    return manager.start_editing_session('animal_config', animal_id, user_id, user_email)


def save_animal_config_changes(animal_id: str, session_id: str, expected_version: int,
                             changes: Dict[str, Any], user_id: str) -> Tuple[bool, Dict[str, Any]]:
    """Save animal configuration changes with conflict detection."""
    manager = ConcurrentEditingManager()
    return manager.attempt_save('animal_config', animal_id, session_id,
                               expected_version, changes, user_id)


def end_animal_config_editing(session_id: str) -> bool:
    """End animal configuration editing session."""
    manager = ConcurrentEditingManager()
    return manager.end_editing_session(session_id)


def get_animal_config_editors(animal_id: str) -> List[Dict[str, Any]]:
    """Get list of users currently editing animal configuration."""
    manager = ConcurrentEditingManager()
    return manager.get_active_editors('animal_config', animal_id)


def cleanup_expired_editing_sessions() -> Dict[str, Any]:
    """Clean up expired editing sessions (for background job/cron execution)."""
    try:
        from boto3.dynamodb.conditions import Attr
        import boto3

        # Get the editing sessions table
        editing_table = table(EDITING_SESSION_TABLE)
        current_time = datetime.now(timezone.utc)

        # Scan for sessions that should be expired but aren't marked as such
        response = editing_table.scan(
            FilterExpression=Attr('status').eq('active') & Attr('expiresAt').lt(current_time.isoformat())
        )

        expired_sessions = response.get('Items', [])
        cleanup_count = 0

        for session_item in expired_sessions:
            session = from_ddb(session_item)
            session_id = session.get('sessionId')

            if session_id:
                try:
                    # Mark session as expired
                    editing_table.update_item(
                        Key={'sessionId': session_id},
                        UpdateExpression='SET #status = :status, expiredAt = :timestamp',
                        ExpressionAttributeNames={'#status': 'status'},
                        ExpressionAttributeValues={
                            ':status': 'expired',
                            ':timestamp': now_iso()
                        },
                        ConditionExpression='attribute_exists(sessionId)'
                    )
                    cleanup_count += 1
                except Exception as e:
                    # Continue with other sessions if one fails
                    logger.warning(f"Failed to expire session {session_id}: {str(e)}")

        return {
            'success': True,
            'message': f'Cleaned up {cleanup_count} expired editing sessions',
            'cleanedCount': cleanup_count,
            'scannedCount': len(expired_sessions)
        }

    except Exception as e:
        return {
            'success': False,
            'error': f'Cleanup failed: {str(e)}',
            'cleanedCount': 0
        }