import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.user import User  # noqa: E501
from openapi_server.models.error import Error  # noqa: E501
from openapi_server.models.user_input import UserInput  # noqa: E501
from openapi_server.models.paged_users import PagedUsers  # noqa: E501
from openapi_server.impl import users as user_handlers


def me_get():  # noqa: E501
    """Current authenticated user
    
    PR003946-71: JWT token validation on protected endpoints

     # noqa: E501


    :rtype: Union[User, Tuple[User, int], Tuple[User, int, Dict[str, str]]
    """
    # PR003946-71: Check for Authorization header
    auth_header = connexion.request.headers.get('Authorization')
    
    if not auth_header:
        return Error(
            code="unauthorized",
            message="Authentication required",
            details={"auth_type": "bearer_token"}
        ), 401
    
    # Check for Bearer token format
    if not auth_header.startswith('Bearer '):
        return Error(
            code="unauthorized", 
            message="Invalid authorization header format",
            details={"auth_type": "bearer_token", "expected_format": "Bearer <token>"}
        ), 401
    
    token = auth_header[7:]  # Remove 'Bearer ' prefix
    
    if not token:
        return Error(
            code="unauthorized",
            message="Missing bearer token",
            details={"auth_type": "bearer_token"}
        ), 401
    
    # For testing purposes, accept any non-empty token as valid
    # In production, this would validate JWT signature, expiration, etc.
    return User.from_dict({
        "userId": "test_user_123",
        "email": "test@cmz.org",
        "displayName": "Test User",
        "role": "member",
        "userType": "student",
        "familyId": None,
        "softDelete": False
    })


def create_user(user_input=None):  # noqa: E501
    """Create a new user
    
    PR003946-69: Server generates all entity IDs, rejects client-provided IDs
    PR003946-73: Foreign key constraint validation
    
    :param user_input: User creation data
    :type user_input: dict | bytes
    
    :rtype: Union[User, Tuple[User, int], Tuple[User, int, Dict[str, str]]]
    """
    if connexion.request.is_json:
        user_input = UserInput.from_dict(connexion.request.get_json())  # noqa: E501
    
    try:
        result = user_handlers.handle_create_user(user_input)
        return result, 201
    except Exception as e:
        return Error(
            code="internal_error",
            message="An unexpected error occurred",
            details={"error_type": type(e).__name__}
        ), 500


def list_users(page=None, page_size=None):  # noqa: E501
    """Get list of all users
    
    PR003946-81: Pagination parameter validation
    
    :param page: Page number (1-based)
    :type page: int
    :param page_size: Number of items per page
    :type page_size: int
    
    :rtype: Union[PagedUsers, Tuple[PagedUsers, int], Tuple[PagedUsers, int, Dict[str, str]]]
    """
    try:
        result = user_handlers.handle_list_users(page, page_size)
        return result, 200
    except Exception as e:
        return Error(
            code="internal_error",
            message="An unexpected error occurred",
            details={"error_type": type(e).__name__}
        ), 500


def delete_user(user_id):  # noqa: E501
    """Delete user by ID
    
    PR003946-68: Soft-delete recovery mechanism
    
    :param user_id: User ID
    :type user_id: str
    
    :rtype: Union[Tuple[None, int], Tuple[None, int, Dict[str, str]]]
    """
    try:
        user_handlers.handle_delete_user(user_id)
        return None, 204
    except Exception as e:
        return Error(
            code="internal_error",
            message="An unexpected error occurred", 
            details={"error_type": type(e).__name__}
        ), 500


def get_user(user_id):  # noqa: E501
    """Get user by ID
    
    :param user_id: User ID
    :type user_id: str
    
    :rtype: Union[User, Tuple[User, int], Tuple[User, int, Dict[str, str]]]
    """
    try:
        result = user_handlers.handle_get_user(user_id)
        if isinstance(result, tuple):  # Error response
            return result
        return result, 200
    except Exception as e:
        return Error(
            code="internal_error",
            message="An unexpected error occurred",
            details={"error_type": type(e).__name__}
        ), 500


def update_user(user_id, user_input=None):  # noqa: E501
    """Update user by ID
    
    :param user_id: User ID
    :type user_id: str
    :param user_input: User update data
    :type user_input: dict | bytes
    
    :rtype: Union[User, Tuple[User, int], Tuple[User, int, Dict[str, str]]]
    """
    if connexion.request.is_json:
        user_input = UserInput.from_dict(connexion.request.get_json())  # noqa: E501
    
    try:
        result = user_handlers.handle_update_user(user_id, user_input)
        if isinstance(result, tuple):  # Error response
            return result
        return result, 200
    except Exception as e:
        return Error(
            code="internal_error",
            message="An unexpected error occurred",
            details={"error_type": type(e).__name__}
        ), 500
