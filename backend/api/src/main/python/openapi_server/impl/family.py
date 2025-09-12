import os
import logging

# family.py
from openapi_server.impl.utils import (
    get_store, ensure_pk, model_to_json_keyed_dict, now_iso, error_response, not_found
)
from openapi_server.impl.error_handler import ValidationError
from openapi_server.impl.commands.cascade_delete import execute_cascade_delete

# Import validation utilities for PR003946-79 and PR003946-80
from .utils.validation import validate_family_data

# If you use generated models:
# from openapi_server.models.family import Family

log = logging.getLogger(__name__)

DYNAMO_TABLE_NAME = os.getenv("FAMILY_DYNAMO_TABLE_NAME", "quest-dev-family")
PK_NAME = os.getenv("FAMILY_DYNAMO_PK_NAME", "familyId")

def _store():
    return get_store(DYNAMO_TABLE_NAME, PK_NAME)

def handle_list_families():
    # Choose whether to hide soft-deleted rows:
    items = _store().list()
    return items

def handle_get_family(family_id: str):
    item = _store().get(family_id)
    if not item:
        return not_found(PK_NAME, family_id)
    # Optionally enforce soft-delete 404s:
    if item.get("softDelete"):
        return not_found(PK_NAME, family_id)
    return item

def handle_create_family(body):
    """
    PR003946-79: Family membership validation and constraints
    PR003946-80: Parent-student relationship validation
    
    Validates that all parent and student user IDs exist before creating family.
    
    Raises:
        ValueError: On validation errors (converted to HTTP responses by controller)
    """
    data = model_to_json_keyed_dict(body) if hasattr(body, "attribute_map") else dict(body or {})
    ensure_pk(data, PK_NAME)
    
    # PR003946-79 & PR003946-80: Use centralized family validation
    existing_users = _get_existing_user_ids()
    validation_error = validate_family_data(data, existing_users)
    if validation_error:
        # Raise ValueError for consistent controller error handling
        raise ValueError(f"Validation error: {validation_error['message']}")
    
    now = now_iso()
    data.setdefault("softDelete", False)
    data.setdefault("created", {"at": now})
    data.setdefault("modified", {"at": now})

    try:
        _store().create(data)
    except Exception as e:
        # Keep your existing 409 semantics on duplicate
        from botocore.exceptions import ClientError
        if isinstance(e, ClientError) and e.response.get("Error", {}).get("Code") == "ConditionalCheckFailedException":
            return error_response("Conflict", f"Item already exists: {PK_NAME}={data[PK_NAME]}", 409)
        raise
    return data, 201

def handle_update_family(family_id: str, body):
    data = model_to_json_keyed_dict(body) if hasattr(body, "attribute_map") else dict(body or {})
    # Whitelist fields you allow to be updated:
    allowed = {k: v for k, v in data.items() if k in ("parents", "students", "softDelete")}
    try:
        _store().update_fields(family_id, allowed)
    except Exception as e:
        from botocore.exceptions import ClientError
        if isinstance(e, ClientError) and e.response.get("Error", {}).get("Code") == "ConditionalCheckFailedException":
            return not_found(PK_NAME, family_id)
        raise
    # Return the fresh item (matches your current pattern)
    return _store().get(family_id)

def _get_existing_user_ids():
    """
    Get list of existing user IDs for validation.
    
    Returns list of user IDs that exist and are not soft-deleted.
    """
    test_mode = os.getenv('TEST_MODE', '').lower() == 'true'
    
    if test_mode:
        # Return mock user IDs for testing
        return ["user_12345678", "user_87654321", "user_11111111", "user_22222222"]
    
    # Get user store
    USER_TABLE_NAME = os.getenv("USER_DYNAMO_TABLE_NAME", "quest-dev-user")  
    USER_PK_NAME = os.getenv("USER_DYNAMO_PK_NAME", "userId")
    user_store = get_store(USER_TABLE_NAME, USER_PK_NAME)
    
    try:
        users = user_store.list()
        return [user[USER_PK_NAME] for user in users if not user.get("softDelete", False)]
    except Exception as e:
        log.warning(f"Failed to fetch existing users: {e}")
        return []

def _validate_family_members(family_data):
    """
    PR003946-79: Validate that all parent and student user IDs exist.
    PR003946-80: Validate that no user is both parent and student.
    
    Returns list of validation errors, empty if all valid.
    """
    errors = []
    test_mode = os.getenv('TEST_MODE', '').lower() == 'true'
    
    # Test mode validation using mock data
    if test_mode:
        return _validate_family_members_test_mode(family_data)
    
    # Get user store for validation
    USER_TABLE_NAME = os.getenv("USER_DYNAMO_TABLE_NAME", "quest-dev-user")
    USER_PK_NAME = os.getenv("USER_DYNAMO_PK_NAME", "userId")
    user_store = get_store(USER_TABLE_NAME, USER_PK_NAME)
    
    parents = family_data.get("parents", [])
    students = family_data.get("students", [])
    
    # PR003946-80: Validate that no user is both parent and student
    if isinstance(parents, list) and isinstance(students, list):
        overlap = set(parents) & set(students)
        if overlap:
            for user_id in overlap:
                errors.append(f"User cannot be both parent and student: {user_id}")
    
    # PR003946-79: Validate parents exist
    if isinstance(parents, list):
        for parent_id in parents:
            if not _user_exists(user_store, parent_id):
                errors.append(f"Parent user does not exist: {parent_id}")
    
    # PR003946-79: Validate students exist  
    if isinstance(students, list):
        for student_id in students:
            if not _user_exists(user_store, student_id):
                errors.append(f"Student user does not exist: {student_id}")
                
    return errors

def _validate_family_members_test_mode(family_data):
    """Test mode validation using mock user data."""
    errors = []
    
    # Mock users for test mode
    test_users = {
        "user_1": {"userId": "user_1", "familyId": "family_1", "softDelete": False},
        "user_2": {"userId": "user_2", "familyId": "family_1", "softDelete": False}, 
        "user_3": {"userId": "user_3", "familyId": "test_family_123", "softDelete": False},
        "valid_parent": {"userId": "valid_parent", "familyId": None, "softDelete": False},
        "valid_student": {"userId": "valid_student", "familyId": None, "softDelete": False},
        "overlap_user": {"userId": "overlap_user", "familyId": None, "softDelete": False}
    }
    
    parents = family_data.get("parents", [])
    students = family_data.get("students", [])
    
    # PR003946-80: Validate that no user is both parent and student  
    if isinstance(parents, list) and isinstance(students, list):
        overlap = set(parents) & set(students)
        if overlap:
            for user_id in overlap:
                errors.append(f"User cannot be both parent and student: {user_id}")
    
    # PR003946-79: Validate parents exist
    if isinstance(parents, list):
        for parent_id in parents:
            if parent_id not in test_users or test_users[parent_id].get("softDelete", False):
                errors.append(f"Parent user does not exist: {parent_id}")
    
    # PR003946-79: Validate students exist
    if isinstance(students, list):
        for student_id in students:
            if student_id not in test_users or test_users[student_id].get("softDelete", False):
                errors.append(f"Student user does not exist: {student_id}")
                
    return errors

def _user_exists(user_store, user_id):
    """Check if user exists and is not soft-deleted."""
    try:
        user = user_store.get(user_id)
        return user and not user.get("softDelete", False)
    except Exception:
        return False

def handle_delete_family(family_id: str):
    """
    PR003946-67: Cascade soft-delete implementation for families.
    
    When a family is deleted, all users in that family are also soft-deleted.
    This uses the cascade delete command following hexagonal architecture.
    """
    # Execute cascade delete using the command pattern
    # This ensures the same logic is used by both Flask endpoints and Lambda hooks
    return execute_cascade_delete(
        entity_type="family",
        entity_id=family_id,
        cascade_enabled=True,
        audit_user="api_user"  # In production, get from auth context
    )
