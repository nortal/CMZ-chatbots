"""
Admin handlers using hexagonal architecture - UPDATED VERSION

This is the new hexagonal architecture version of admin.py.
All handlers delegate to domain services through the Flask adapter.
Same API interface, but with pure business logic separation.
"""
import logging
from typing import Any, Dict, List, Optional, Tuple

# OpenAPI models (keep same imports for API compatibility)
from openapi_server.models.user import User
from openapi_server.models.user_details import UserDetails
from openapi_server.models.paged_users import PagedUsers
from openapi_server.models.user_input import UserInput
from openapi_server.models.user_details_input import UserDetailsInput

# Import hexagonal architecture components
from .dependency_injection import create_flask_user_handler
from .utils.core import not_found

log = logging.getLogger(__name__)

# Initialize Flask handler (lazy loaded)
_flask_handler = None


def _get_flask_handler():
    """Get or create Flask handler"""
    global _flask_handler
    if _flask_handler is None:
        _flask_handler = create_flask_user_handler()
    return _flask_handler


# ---------------------------------
# /users (GET) -> list users (paged)
# ---------------------------------
def handle_list_users(page: Optional[int] = None, page_size: Optional[int] = None) -> PagedUsers:
    """
    List users with optional pagination using hexagonal architecture
    
    Args:
        page: Page number (1-based)
        page_size: Items per page
        
    Returns:
        PagedUsers: OpenAPI model with user list
    """
    try:
        # Delegate to Flask handler which uses domain service
        response, status_code = _get_flask_handler().list_users(page, page_size)
        
        if status_code == 200:
            # Convert response to PagedUsers model
            return PagedUsers.from_dict(response)
        else:
            # Handle error response
            log.error(f"Error listing users: {response}")
            return PagedUsers.from_dict({"items": []})
            
    except Exception as e:
        log.exception("Error in handle_list_users")
        return PagedUsers.from_dict({"items": []})


# ---------------------------
# /user (POST) -> create user
# ---------------------------
def handle_create_user(body: UserInput) -> User:
    """
    Create a new user using hexagonal architecture
    
    Args:
        body: UserInput OpenAPI model
        
    Returns:
        User: Created user OpenAPI model
        
    Raises:
        Exception: On creation errors (converted to HTTP responses by controller)
    """
    try:
        # Delegate to Flask handler which uses domain service
        response, status_code = _get_flask_handler().create_user(body)
        
        if status_code == 201:
            # Return OpenAPI model (response is already User model from Flask handler)
            return response
        else:
            # Convert error response to exception (maintains existing error handling)
            error_msg = response.get("detail", "User creation failed") if isinstance(response, dict) else "User creation failed"
            raise Exception(error_msg)
            
    except Exception as e:
        log.exception("Error in handle_create_user")
        raise


# -----------------------------
# /user/{userId} (GET) -> fetch
# -----------------------------
def handle_get_user(user_id: str) -> User:
    """
    Get user by ID using hexagonal architecture
    
    Args:
        user_id: User identifier
        
    Returns:
        User: User OpenAPI model
        
    Raises:
        Exception: On retrieval errors (converted to HTTP responses by controller)
    """
    try:
        # Delegate to Flask handler which uses domain service
        response, status_code = _get_flask_handler().get_user(user_id)
        
        if status_code == 200:
            # Return OpenAPI model
            return response
        elif status_code == 404:
            # Maintain existing not_found pattern
            return not_found("userId", user_id)
        else:
            # Convert error to exception
            error_msg = response.get("detail", "User retrieval failed") if isinstance(response, dict) else "User retrieval failed"
            raise Exception(error_msg)
            
    except Exception as e:
        log.exception(f"Error in handle_get_user for userId={user_id}")
        raise


# ------------------------------------
# /user/{userId} (PUT) -> update user
# ------------------------------------
def handle_update_user(user_id: str, body: User) -> User:
    """
    Update user using hexagonal architecture
    
    Args:
        user_id: User identifier
        body: User OpenAPI model with updates
        
    Returns:
        User: Updated user OpenAPI model
        
    Raises:
        Exception: On update errors
    """
    try:
        # Delegate to Flask handler which uses domain service
        response, status_code = _get_flask_handler().update_user(user_id, body)
        
        if status_code == 200:
            # Return OpenAPI model
            return response
        elif status_code == 404:
            # Maintain existing not_found pattern
            return not_found("userId", user_id)
        else:
            # Convert error to exception
            error_msg = response.get("detail", "User update failed") if isinstance(response, dict) else "User update failed"
            raise Exception(error_msg)
            
    except Exception as e:
        log.exception(f"Error in handle_update_user for userId={user_id}")
        raise


# -----------------------------
# /user/{userId} (DELETE) soft
# -----------------------------
def handle_delete_user(user_id: str) -> Tuple[None, int]:
    """
    Soft delete user using hexagonal architecture
    
    Args:
        user_id: User identifier
        
    Returns:
        Tuple[None, int]: Empty response with 204 status code
        
    Raises:
        Exception: On deletion errors
    """
    try:
        # Delegate to Flask handler which uses domain service
        response, status_code = _get_flask_handler().delete_user(user_id)
        
        if status_code == 204:
            return None, 204
        elif status_code == 404:
            # Maintain existing not_found pattern
            return not_found("userId", user_id)
        else:
            # Convert error to exception
            error_msg = response.get("detail", "User deletion failed") if isinstance(response, dict) else "User deletion failed"
            raise Exception(error_msg)
            
    except Exception as e:
        log.exception(f"Error in handle_delete_user for userId={user_id}")
        raise


# ------------------------------------------------------
# /user_details (GET) -> list detailed user information
# ------------------------------------------------------
def handle_list_user_details(page: Optional[int] = None, page_size: Optional[int] = None) -> List[UserDetails]:
    """
    List user details using hexagonal architecture
    
    Args:
        page: Page number (1-based)
        page_size: Items per page
        
    Returns:
        List[UserDetails]: List of UserDetails OpenAPI models
    """
    try:
        # Delegate to Flask handler which uses domain service
        response, status_code = _get_flask_handler().list_user_details(page, page_size)
        
        if status_code == 200:
            # Convert dict responses to UserDetails models
            if isinstance(response, list):
                return [UserDetails.from_dict(item) for item in response]
            else:
                return []
        else:
            log.error(f"Error listing user details: {response}")
            return []
            
    except Exception as e:
        log.exception("Error in handle_list_user_details")
        return []


# ----------------------------------------------------------
# /user_details (POST) -> create details for a given userId
# ----------------------------------------------------------
def handle_create_user_details(body: UserDetailsInput) -> Tuple[Dict[str, str], int]:
    """
    Create user details using hexagonal architecture
    
    Args:
        body: UserDetailsInput OpenAPI model
        
    Returns:
        Tuple[Dict, int]: Response dict and status code
    """
    try:
        # Delegate to Flask handler which uses domain service
        response, status_code = _get_flask_handler().create_user_details(body)
        
        # Return response as-is (maintains existing API format)
        return response, status_code
        
    except Exception as e:
        log.exception("Error in handle_create_user_details")
        return {"title": "Server Error", "detail": "Failed to create user details", "status": 500}, 500


# ----------------------------------------------------------
# /user_details/{userId} (GET) -> fetch details by userId
# ----------------------------------------------------------
def handle_get_user_details(user_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Get user details by user ID using hexagonal architecture
    
    Args:
        user_id: User identifier
        
    Returns:
        Tuple[Dict, int]: Response dict and status code
    """
    try:
        # Delegate to Flask handler which uses domain service
        response, status_code = _get_flask_handler().get_user_details(user_id)
        
        # Return response as-is (maintains existing API format)
        return response, status_code
        
    except Exception as e:
        log.exception(f"Error in handle_get_user_details for userId={user_id}")
        return {"title": "Server Error", "detail": "Failed to read user details", "status": 500}, 500


# --------------------------------------------------------------
# /user_details/{userId} (PUT) -> update details (by userId GSI)
# --------------------------------------------------------------
def handle_update_user_details(user_id: str, body: UserDetailsInput) -> Tuple[Dict[str, Any], int]:
    """
    Update user details using hexagonal architecture
    
    Args:
        user_id: User identifier
        body: UserDetailsInput OpenAPI model with updates
        
    Returns:
        Tuple[Dict, int]: Response dict and status code
    """
    try:
        # Delegate to Flask handler which uses domain service
        response, status_code = _get_flask_handler().update_user_details(user_id, body)
        
        # Return response as-is (maintains existing API format)
        return response, status_code
        
    except Exception as e:
        log.exception(f"Error in handle_update_user_details for userId={user_id}")
        return {"title": "Server Error", "detail": "Failed to update user details", "status": 500}, 500


# ----------------------------------------------------------
# /user_details/{userId} (DELETE) -> soft delete details
# ----------------------------------------------------------
def handle_delete_user_details(user_id: str) -> Tuple[None, int]:
    """
    Soft delete user details using hexagonal architecture
    
    Args:
        user_id: User identifier
        
    Returns:
        Tuple[None, int]: Empty response with status code
    """
    try:
        # Delegate to Flask handler which uses domain service
        response, status_code = _get_flask_handler().delete_user_details(user_id)
        
        # Return response as-is (maintains existing API format)
        return response, status_code
        
    except Exception as e:
        log.exception(f"Error in handle_delete_user_details for userId={user_id}")
        return {"title": "Server Error", "detail": "Failed to delete user details", "status": 500}, 500