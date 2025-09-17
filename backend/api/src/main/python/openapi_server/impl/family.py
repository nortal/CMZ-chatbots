"""
Implementation module for family management
Implements CRUD operations for family groups with DynamoDB persistence
"""

import uuid
from typing import Any, Dict, List, Tuple, Union
from datetime import datetime
from ..models.error import Error
from ..models.family import Family
from .utils.orm.models.family import FamilyModel, Audit
from pynamodb.exceptions import PutError, DeleteError, UpdateError, DoesNotExist
import logging

logger = logging.getLogger(__name__)


def family_list_get() -> Tuple[Any, int]:
    """
    Get list of all families

    Returns all active (non-deleted) families from DynamoDB
    """
    try:
        # Query all families that are not soft-deleted
        families = []
        for family in FamilyModel.scan():
            if not family.softDelete:
                family_dict = family.to_plain_dict()
                # Convert to API format
                api_family = {
                    "familyId": family_dict["familyId"],
                    "familyName": family_dict.get("familyName", ""),
                    "parents": family_dict.get("parents", []),
                    "students": family_dict.get("students", []),
                    "address": family_dict.get("address", {}),
                    "preferredPrograms": family_dict.get("preferredPrograms", []),
                    "status": family_dict.get("status", "active"),
                    "memberSince": family_dict.get("memberSince", datetime.utcnow().isoformat()),
                    "created": family_dict.get("created"),
                    "modified": family_dict.get("modified")
                }
                families.append(api_family)

        logger.info(f"Retrieved {len(families)} families from DynamoDB")
        return families, 200

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
    Create a new family

    Creates a new family record in DynamoDB with generated ID
    """
    try:
        # Generate a unique family ID
        family_id = f"family_{uuid.uuid4().hex[:8]}"

        # Create audit stamps
        now = datetime.utcnow().isoformat()
        audit = Audit(
            at=now,
            by="system"  # In production, this would be the authenticated user
        )

        # Create the family model
        family = FamilyModel(
            familyId=family_id,
            parents=body.get("parents", []),
            students=body.get("students", []),
            softDelete=False,
            created=audit,
            modified=audit
        )

        # Additional fields can be stored in a MapAttribute if needed
        # For now, we'll return them in the response

        # Save to DynamoDB
        family.save()

        # Prepare response
        response = {
            "familyId": family_id,
            "familyName": body.get("familyName", ""),
            "parents": body.get("parents", []),
            "students": body.get("students", []),
            "address": body.get("address", {}),
            "preferredPrograms": body.get("preferredPrograms", []),
            "status": body.get("status", "active"),
            "memberSince": body.get("memberSince", now),
            "created": audit.as_dict(),
            "modified": audit.as_dict()
        }

        logger.info(f"Created new family with ID: {family_id}")
        return response, 201

    except PutError as e:
        logger.error(f"DynamoDB error creating family: {str(e)}")
        error = Error(
            code="database_error",
            message="Failed to create family",
            details={"error": str(e)}
        )
        return error.to_dict(), 500
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
    Get family details by ID

    Retrieves a specific family from DynamoDB
    """
    try:
        # Get the family from DynamoDB
        family = FamilyModel.get(family_id)

        # Check if soft deleted
        if family.softDelete:
            error = Error(
                code="not_found",
                message=f"Family {family_id} not found",
                details={"familyId": family_id}
            )
            return error.to_dict(), 404

        # Convert to API format
        family_dict = family.to_plain_dict()
        response = {
            "familyId": family_dict["familyId"],
            "familyName": family_dict.get("familyName", ""),
            "parents": family_dict.get("parents", []),
            "students": family_dict.get("students", []),
            "address": family_dict.get("address", {}),
            "preferredPrograms": family_dict.get("preferredPrograms", []),
            "status": family_dict.get("status", "active"),
            "memberSince": family_dict.get("memberSince", datetime.utcnow().isoformat()),
            "created": family_dict.get("created"),
            "modified": family_dict.get("modified")
        }

        logger.info(f"Retrieved family {family_id}")
        return response, 200

    except DoesNotExist:
        logger.warning(f"Family {family_id} not found")
        error = Error(
            code="not_found",
            message=f"Family {family_id} not found",
            details={"familyId": family_id}
        )
        return error.to_dict(), 404
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
    Update family details

    Updates an existing family in DynamoDB
    """
    try:
        # Get the existing family
        family = FamilyModel.get(family_id)

        # Check if soft deleted
        if family.softDelete:
            error = Error(
                code="not_found",
                message=f"Family {family_id} not found",
                details={"familyId": family_id}
            )
            return error.to_dict(), 404

        # Update fields if provided
        if "parents" in body:
            family.parents = body["parents"]
        if "students" in body:
            family.students = body["students"]

        # Update modified timestamp
        family.modified = Audit(
            at=datetime.utcnow().isoformat(),
            by="system"  # In production, this would be the authenticated user
        )

        # Save updates
        family.save()

        # Prepare response
        family_dict = family.to_plain_dict()
        response = {
            "familyId": family_dict["familyId"],
            "familyName": body.get("familyName", ""),
            "parents": family_dict.get("parents", []),
            "students": family_dict.get("students", []),
            "address": body.get("address", {}),
            "preferredPrograms": body.get("preferredPrograms", []),
            "status": body.get("status", "active"),
            "memberSince": body.get("memberSince", datetime.utcnow().isoformat()),
            "created": family_dict.get("created"),
            "modified": family_dict.get("modified")
        }

        logger.info(f"Updated family {family_id}")
        return response, 200

    except DoesNotExist:
        logger.warning(f"Family {family_id} not found for update")
        error = Error(
            code="not_found",
            message=f"Family {family_id} not found",
            details={"familyId": family_id}
        )
        return error.to_dict(), 404
    except UpdateError as e:
        logger.error(f"DynamoDB error updating family {family_id}: {str(e)}")
        error = Error(
            code="database_error",
            message="Failed to update family",
            details={"error": str(e)}
        )
        return error.to_dict(), 500
    except Exception as e:
        logger.error(f"Unexpected error updating family {family_id}: {str(e)}")
        error = Error(
            code="internal_error",
            message="An unexpected error occurred",
            details={"error": str(e)}
        )
        return error.to_dict(), 500


def family_details_delete(family_id: str) -> Tuple[Any, int]:
    """
    Delete a family (soft delete)

    Marks a family as deleted without removing from database
    """
    try:
        # Get the existing family
        family = FamilyModel.get(family_id)

        # Check if already deleted
        if family.softDelete:
            error = Error(
                code="not_found",
                message=f"Family {family_id} not found",
                details={"familyId": family_id}
            )
            return error.to_dict(), 404

        # Soft delete by setting flag
        family.softDelete = True
        family.modified = Audit(
            at=datetime.utcnow().isoformat(),
            by="system"  # In production, this would be the authenticated user
        )

        # Save the soft delete
        family.save()

        logger.info(f"Soft deleted family {family_id}")
        return "", 204

    except DoesNotExist:
        logger.warning(f"Family {family_id} not found for deletion")
        error = Error(
            code="not_found",
            message=f"Family {family_id} not found",
            details={"familyId": family_id}
        )
        return error.to_dict(), 404
    except Exception as e:
        logger.error(f"Error deleting family {family_id}: {str(e)}")
        error = Error(
            code="internal_error",
            message="Failed to delete family",
            details={"error": str(e)}
        )
        return error.to_dict(), 500


# Keep these for backward compatibility with the generated code
def handle_create_family(*args, **kwargs) -> Tuple[Any, int]:
    """Legacy handler - redirects to family_details_post"""
    if args and len(args) > 0:
        return family_details_post(args[0])
    return family_details_post(kwargs.get('body', {}))


def handle_delete_family(*args, **kwargs) -> Tuple[Any, int]:
    """Legacy handler - redirects to family_details_delete"""
    if args and len(args) > 0:
        return family_details_delete(args[0])
    return family_details_delete(kwargs.get('family_id', ''))


def handle_get_family(*args, **kwargs) -> Tuple[Any, int]:
    """Legacy handler - redirects to family_details_get"""
    if args and len(args) > 0:
        return family_details_get(args[0])
    return family_details_get(kwargs.get('family_id', ''))


def handle_list_families(*args, **kwargs) -> Tuple[Any, int]:
    """Legacy handler - redirects to family_list_get"""
    return family_list_get()


def handle_update_family(*args, **kwargs) -> Tuple[Any, int]:
    """Legacy handler - redirects to family_details_patch"""
    if len(args) >= 2:
        return family_details_patch(args[0], args[1])
    return family_details_patch(kwargs.get('family_id', ''), kwargs.get('body', {}))

