import os
import logging

# users.py - User CRUD operations implementation
from openapi_server.impl.utils import (
    get_store, ensure_pk, model_to_json_keyed_dict, now_iso, not_found
)
from openapi_server.impl.error_handler import ValidationError

log = logging.getLogger(__name__)

DYNAMO_TABLE_NAME = os.getenv("USER_DYNAMO_TABLE_NAME", "quest-dev-user")
PK_NAME = os.getenv("USER_DYNAMO_PK_NAME", "userId")

def _store():
    return get_store(DYNAMO_TABLE_NAME, PK_NAME)

def handle_list_users(page=None, page_size=None):
    """
    PR003946-81: Pagination parameter validation
    
    List users with pagination support and parameter validation.
    """
    # Validate pagination parameters
    if page is not None:
        try:
            page = int(page)
            if page < 1:
                raise ValidationError(
                    "Invalid pagination parameters",
                    field_errors={"page": ["Page must be >= 1"]}
                )
        except (ValueError, TypeError):
            raise ValidationError(
                "Invalid pagination parameters", 
                field_errors={"page": ["Page must be a valid integer"]}
            )
    else:
        page = 1

    if page_size is not None:
        try:
            page_size = int(page_size)
            if page_size < 1:
                raise ValidationError(
                    "Invalid pagination parameters",
                    field_errors={"pageSize": ["Page size must be >= 1"]}
                )
            elif page_size > 500:  # Max page size limit
                raise ValidationError(
                    "Invalid pagination parameters",
                    field_errors={"pageSize": ["Page size must be <= 500"]}
                )
        except (ValueError, TypeError):
            raise ValidationError(
                "Invalid pagination parameters",
                field_errors={"pageSize": ["Page size must be a valid integer"]}
            )
    else:
        page_size = 50

    # Get users from store (with soft-delete filtering)
    items = _store().list(hide_soft_deleted=True)
    
    # Calculate pagination
    total = len(items)
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    page_items = items[start_index:end_index]
    
    return {
        "items": page_items,
        "page": page,
        "pageSize": page_size,
        "total": total
    }

def handle_get_user(user_id: str):
    """Get user by ID with soft-delete handling"""
    item = _store().get(user_id)
    if not item:
        return not_found(PK_NAME, user_id)
    
    # Enforce soft-delete 404s
    if item.get("softDelete"):
        return not_found(PK_NAME, user_id)
    
    return item

def handle_create_user(body):
    """
    PR003946-69: Server generates all entity IDs, rejects client-provided IDs
    PR003946-70: Reject requests with client-provided IDs
    PR003946-73: Foreign key constraint validation
    
    Creates a new user with server-generated ID and validates foreign keys.
    """
    data = model_to_json_keyed_dict(body) if hasattr(body, "attribute_map") else dict(body or {})
    
    # PR003946-70: Reject client-provided IDs
    if "userId" in data and data["userId"]:
        raise ValidationError(
            "Invalid request parameters",
            field_errors={"userId": ["User ID must be server-generated. Do not provide userId in request."]}
        )
    
    # PR003946-69: Generate server-side ID
    ensure_pk(data, PK_NAME)
    
    # Add audit fields
    data["created"] = {"at": now_iso(), "by": {"userId": "system", "displayName": "System", "email": "system@cmz.org"}}
    data["modified"] = {"at": now_iso(), "by": {"userId": "system", "displayName": "System", "email": "system@cmz.org"}}
    data["softDelete"] = False
    
    # PR003946-73: Foreign key validation
    validation_errors = _validate_foreign_keys(data)
    if validation_errors:
        raise ValidationError(
            "Foreign key validation failed",
            field_errors=validation_errors
        )
    
    # Required field validation
    required_fields = ["email", "displayName", "role", "userType"]
    validation_errors = {}
    
    for field in required_fields:
        if not data.get(field):
            validation_errors[field] = [f"{field} is required"]
    
    if validation_errors:
        raise ValidationError(
            "Required field validation failed",
            field_errors=validation_errors
        )
    
    # Email format validation
    email = data.get("email", "")
    if email and "@" not in email:
        validation_errors["email"] = ["Invalid email format"]
        raise ValidationError(
            "Email validation failed",
            field_errors=validation_errors
        )
    
    # Role validation
    valid_roles = ["admin", "member", "editor"]
    if data.get("role") not in valid_roles:
        validation_errors["role"] = [f"Role must be one of: {', '.join(valid_roles)}"]
        raise ValidationError(
            "Role validation failed", 
            field_errors=validation_errors
        )
    
    # UserType validation
    valid_user_types = ["parent", "student", "none"]
    if data.get("userType") not in valid_user_types:
        validation_errors["userType"] = [f"User type must be one of: {', '.join(valid_user_types)}"]
        raise ValidationError(
            "User type validation failed",
            field_errors=validation_errors
        )
    
    # Store in DynamoDB
    _store().create(data)
    return data

def handle_update_user(user_id: str, body):
    """Update existing user with validation"""
    # Check if user exists
    existing = _store().get(user_id)
    if not existing or existing.get("softDelete"):
        return not_found(PK_NAME, user_id)
    
    data = model_to_json_keyed_dict(body) if hasattr(body, "attribute_map") else dict(body or {})
    
    # Don't allow userId changes
    if "userId" in data:
        data.pop("userId")
    
    # Update modified timestamp
    data["modified"] = {"at": now_iso(), "by": {"userId": "system", "displayName": "System", "email": "system@cmz.org"}}
    
    # Foreign key validation
    validation_errors = _validate_foreign_keys(data)
    if validation_errors:
        raise ValidationError(
            "Foreign key validation failed",
            field_errors=validation_errors
        )
    
    # Update in DynamoDB
    _store().update_fields(user_id, data)
    
    # Return updated user
    return _store().get(user_id)

def handle_delete_user(user_id: str):
    """
    PR003946-68: Soft-delete recovery mechanism
    
    Soft delete user (set softDelete flag to true).
    """
    # Check if user exists
    existing = _store().get(user_id)
    if not existing:
        return not_found(PK_NAME, user_id)
    
    if existing.get("softDelete"):
        return not_found(PK_NAME, user_id)  # Already soft-deleted
    
    # Soft delete by setting flag
    update_data = {
        "softDelete": True,
        "deleted": {"at": now_iso(), "by": {"userId": "system", "displayName": "System", "email": "system@cmz.org"}},
        "modified": {"at": now_iso(), "by": {"userId": "system", "displayName": "System", "email": "system@cmz.org"}}
    }
    
    _store().update_fields(user_id, update_data)
    return None

def _validate_foreign_keys(data):
    """
    PR003946-73: Foreign key constraint validation
    
    Validate that referenced entities exist.
    """
    validation_errors = {}
    
    # Validate familyId if provided
    family_id = data.get("familyId")
    if family_id:
        try:
            # Check if family exists using family store
            family_store = get_store(
                os.getenv("FAMILY_DYNAMO_TABLE_NAME", "quest-dev-family"),
                os.getenv("FAMILY_DYNAMO_PK_NAME", "familyId")
            )
            family = family_store.get(family_id)
            if not family or family.get("softDelete"):
                validation_errors["familyId"] = [f"Referenced family does not exist: {family_id}"]
        except Exception as e:
            log.warning(f"Could not validate family reference {family_id}: {e}")
            validation_errors["familyId"] = [f"Could not validate family reference: {family_id}"]
    
    return validation_errors