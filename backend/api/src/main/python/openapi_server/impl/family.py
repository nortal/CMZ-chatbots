"""
Implementation module for family management
Implements CRUD operations for family groups with DynamoDB persistence
Now with bidirectional user references and role-based access control
"""

import uuid
from typing import Any, Dict, List, Tuple, Union
from datetime import datetime
from ..models.error import Error
from ..models.family import Family
from .utils.orm.models.family import FamilyModel, Audit

# Import bidirectional implementation
from .family_bidirectional import (
    create_family_bidirectional,
    get_family_bidirectional,
    update_family_bidirectional,
    delete_family_bidirectional,
    list_families_for_user
)

from pynamodb.exceptions import PutError, DeleteError, UpdateError, DoesNotExist
import logging

logger = logging.getLogger(__name__)


def family_list_get() -> Tuple[Any, int]:
    """
    Get list of all families with bidirectional references

    Returns all active (non-deleted) families from DynamoDB with proper user references
    """
    try:
        # Get requesting user from headers (in production, get from JWT)
        import connexion
        request_headers = connexion.request.headers
        requesting_user_id = request_headers.get('X-User-Id', 'anonymous')

        # Use bidirectional implementation
        return list_families_for_user(requesting_user_id)

    except Exception as e:
        logger.error(f"Error retrieving families: {str(e)}")
        error = Error(
            code="internal_error",
            message="Failed to retrieve families",
            details={"error": str(e)}
        )
        return error.to_dict(), 500


def family_details_post(body: Dict[str, Any]) -> Tuple[Any, int]:
    """
    Create a new family with bidirectional references

    Creates a new family record in DynamoDB with user ID references
    """
    try:
        # Get requesting user from headers
        import connexion
        request_headers = connexion.request.headers
        requesting_user_id = request_headers.get('X-User-Id', 'anonymous')

        # Use bidirectional implementation
        return create_family_bidirectional(body, requesting_user_id)

    except Exception as e:
        logger.error(f"Unexpected error creating family: {str(e)}")
        error = Error(
            code="internal_error",
            message="An unexpected error occurred",
            details={"error": str(e)}
        )
        return error.to_dict(), 500


def family_details_get(family_id: str) -> Tuple[Any, int]:
    """
    Get family details by ID with bidirectional references

    Retrieves a specific family from DynamoDB with user details populated
    """
    try:
        # Get requesting user from headers
        import connexion
        request_headers = connexion.request.headers
        requesting_user_id = request_headers.get('X-User-Id', 'anonymous')

        # Use bidirectional implementation
        return get_family_bidirectional(family_id, requesting_user_id)

    except Exception as e:
        logger.error(f"Error retrieving family {family_id}: {str(e)}")
        error = Error(
            code="internal_error",
            message="Failed to retrieve family",
            details={"error": str(e)}
        )
        return error.to_dict(), 500


def family_details_patch(family_id: str, body: Dict[str, Any]) -> Tuple[Any, int]:
    """
    Update family details with bidirectional references

    Updates a family record in DynamoDB, maintaining bidirectional references
    """
    try:
        # Get requesting user from headers
        import connexion
        request_headers = connexion.request.headers
        requesting_user_id = request_headers.get('X-User-Id', 'anonymous')

        # Use bidirectional implementation
        return update_family_bidirectional(family_id, body, requesting_user_id)

    except Exception as e:
        logger.error(f"Error updating family {family_id}: {str(e)}")
        error = Error(
            code="internal_error",
            message="Failed to update family",
            details={"error": str(e)}
        )
        return error.to_dict(), 500


def family_details_delete(family_id: str) -> Tuple[Any, int]:
    """
    Delete a family (soft delete) with bidirectional reference cleanup

    Marks a family as deleted in DynamoDB and removes family references from users
    """
    try:
        # Get requesting user from headers
        import connexion
        request_headers = connexion.request.headers
        requesting_user_id = request_headers.get('X-User-Id', 'anonymous')

        # Use bidirectional implementation
        return delete_family_bidirectional(family_id, requesting_user_id)

    except Exception as e:
        logger.error(f"Error deleting family {family_id}: {str(e)}")
        error = Error(
            code="internal_error",
            message="Failed to delete family",
            details={"error": str(e)}
        )
        return error.to_dict(), 500