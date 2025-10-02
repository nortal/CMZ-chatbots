"""
Handler module that exposes hexagonal architecture handlers for generated controllers

This module provides a unified interface for the generated OpenAPI controllers
to access the business logic through the hexagonal architecture pattern.
"""

from typing import Any, Tuple, Dict
import inspect
import logging
from .dependency_injection import (
    create_flask_user_handler,
    create_flask_animal_handler,
    create_user_service,
    create_animal_service
)
from .conversation import (
    handle_convo_turn_post,
    handle_convo_history_get,
    handle_convo_history_delete,
    handle_summarize_convo_post,
    handle_conversations_sessions_get,
    handle_conversations_sessions_session_id_get
)

logger = logging.getLogger(__name__)


def handle_(*args, **kwargs) -> Tuple[Any, int]:
    """
    Generic handler function that routes to specific handlers based on caller
    This is a workaround for the controller template bug where it looks for just 'handle_'
    """
    # Get the caller function name to determine which handler to call
    frame = inspect.currentframe()
    try:
        caller_frame = frame.f_back
        caller_name = caller_frame.f_code.co_name

        # Map controller function names to handler functions
        handler_map = {
            'animal_config_get': handle_animal_config_get,
            'animal_config_patch': handle_animal_config_patch,
            'animal_list_get': handle_animal_list_get,
            'animal_details_get': handle_animal_details_get,
            'animal_details_post': handle_animal_details_post,
            'animal_details_patch': handle_animal_details_patch,
            'animal_details_delete': handle_animal_details_delete,
            'animal_get': handle_animal_get,  # Updated from animal_id_get
            'animal_put': handle_animal_put,  # Updated from animal_id_put
            'animal_delete': handle_animal_delete,  # Updated from animal_id_delete
            'animal_post': handle_animal_post,  # Add missing mapping
            'list_users': handle_user_list_get,  # Map list_users to handler
            'user_list_get': handle_user_list_get,
            'user_details_get': handle_user_details_get,
            'user_details_post': handle_user_details_post,
            'user_details_patch': handle_user_details_patch,
            'user_details_delete': handle_user_details_delete,
            'family_list_get': handle_family_list_get,
            'list_all_families': handle_family_list_get,  # New endpoint mapping
            'list_families': handle_family_list_get,  # Controller function name mapping
            'create_family': handle_family_details_post,  # Fix for create_family routing
            'family_details_post': handle_family_details_post,
            'family_details_get': handle_family_details_get,
            'family_details_patch': handle_family_details_patch,
            'family_details_delete': handle_family_details_delete,
            'delete_family': handle_family_details_delete,  # Map delete_family controller function
            'login_post': handle_login_post,
            'logout_post': handle_logout_post,
            # New auth operationIds from OpenAPI spec
            'auth_post': handle_login_post,  # Maps to same login handler
            'auth_logout_post': handle_logout_post,  # Maps to same logout handler
            'auth_refresh_post': handle_auth_refresh_post,
            'auth_reset_password_post': handle_auth_reset_password_post,
            'health_get': handle_health_get,
            'homepage_get': handle_homepage_get,
            'admin_dashboard_get': handle_admin_dashboard_get,
            # Conversation handlers
            'convo_turn_post': handle_convo_turn_post,
            'convo_history_get': handle_convo_history_get,
            'convo_history_delete': handle_convo_history_delete,
            'summarize_convo_post': handle_summarize_convo_post,
            'conversations_sessions_get': handle_conversations_sessions_get,
            'conversations_sessions_session_id_get': handle_conversations_sessions_session_id_get,
        }

        handler_func = handler_map.get(caller_name)
        if handler_func:
            return handler_func(*args, **kwargs)
        else:
            from .error_handler import create_error_response
            return create_error_response(
                "not_implemented",
                f"Handler for {caller_name} not implemented",
                {"caller": caller_name}
            ), 501

    finally:
        del frame


# Animal handlers
def handle_animal_config_get(animal_id: str) -> Tuple[Any, int]:
    """Get animal configuration"""
    try:
        # Check authentication
        from .utils.auth_decorator import requires_auth

        # Apply auth decorator logic manually since we can't use decorators directly
        from flask import request
        from .utils.jwt_utils import verify_jwt_token

        auth_header = request.headers.get('Authorization')
        if not auth_header:
            from openapi_server.models.error import Error
            error = Error(
                code="unauthorized",
                message="Authentication required",
                details={"error": "Missing Authorization header"}
            )
            return error.to_dict(), 401

        # Verify token
        is_valid, payload = verify_jwt_token(auth_header)
        if not is_valid or not payload:
            error = Error(
                code="unauthorized",
                message="Invalid or expired token",
                details={"error": "Token validation failed"}
            )
            return error.to_dict(), 401

        # Check role - allow admin, zookeeper, and member roles
        user_role = payload.get('role', 'visitor')
        allowed_roles = ['admin', 'zookeeper', 'member']
        if user_role not in allowed_roles:
            error = Error(
                code="forbidden",
                message="Insufficient permissions",
                details={
                    "error": f"Role '{user_role}' not allowed. Required roles: {allowed_roles}"
                }
            )
            return error.to_dict(), 403

        # Execute the actual handler
        animal_handler = create_flask_animal_handler()
        return animal_handler.get_animal_config(animal_id)
    except Exception as e:
        from .error_handler import handle_exception_for_controllers
        return handle_exception_for_controllers(e)


def handle_animal_config_patch(animal_id: str, body: Any) -> Tuple[Any, int]:
    """Update animal configuration"""
    try:
        # Convert AnimalConfigUpdate object to dictionary if necessary
        from openapi_server.models.animal_config_update import AnimalConfigUpdate
        from openapi_server.models.error import Error
        from flask import request
        from .utils.jwt_utils import verify_jwt_token
        from .error_handler import handle_exception_for_controllers

        if isinstance(body, AnimalConfigUpdate):
            # Use the model_to_json_keyed_dict to properly convert the object
            from .utils.core import model_to_json_keyed_dict
            body = model_to_json_keyed_dict(body) or {}
        elif not isinstance(body, dict):
            # Fallback for other types
            body = dict(body) if body else {}

        # Fix floating-point precision issues for temperature and topP
        if 'temperature' in body and body['temperature'] is not None:
            # Round to 1 decimal place to avoid floating-point precision issues
            body['temperature'] = round(float(body['temperature']), 1)

        if 'topP' in body and body['topP'] is not None:
            # Round to 2 decimal places for topP
            body['topP'] = round(float(body['topP']), 2)

        # Check authentication

        auth_header = request.headers.get('Authorization')
        if not auth_header:
            error = Error(
                code="unauthorized",
                message="Authentication required",
                details={"error": "Missing Authorization header"}
            )
            return error.to_dict(), 401

        # Verify token
        is_valid, payload = verify_jwt_token(auth_header)
        if not is_valid or not payload:
            error = Error(
                code="unauthorized",
                message="Invalid or expired token",
                details={"error": "Token validation failed"}
            )
            return error.to_dict(), 401

        # Check role - only allow admin and zookeeper roles to update
        user_role = payload.get('role', 'visitor')
        allowed_roles = ['admin', 'zookeeper']
        if user_role not in allowed_roles:
            error = Error(
                code="forbidden",
                message="Insufficient permissions",
                details={
                    "error": f"Role '{user_role}' not allowed. Required roles: {allowed_roles}"
                }
            )
            return error.to_dict(), 403

        # Execute the actual handler
        animal_handler = create_flask_animal_handler()
        return animal_handler.update_animal_config(animal_id, body)
    except Exception as e:
        return handle_exception_for_controllers(e)


def handle_animal_list_get(*args, **kwargs) -> Tuple[Any, int]:
    """Get list of animals"""
    try:
        # Handle optional status parameter from Connexion
        # When status is not provided, Connexion might pass None as the first arg
        if args:
            status = args[0] if args[0] not in (None, '') else None
        else:
            status = kwargs.get('status')

        # Filter out None values that Connexion might pass for optional parameters
        status = status if status not in (None, '') else None

        # Try to use the real handler, fall back to mock if DB not available
        try:
            animal_handler = create_flask_animal_handler()
            return animal_handler.list_animals(status)
        except Exception as db_error:
            # If DynamoDB fails (no credentials), use mock data
            logger.warning(f"Database unavailable, using mock data: {db_error}")
            from .animals_mock import get_mock_animals
            animals = get_mock_animals(status)
            return animals, 200

    except Exception as e:
        from .error_handler import handle_exception_for_controllers
        return handle_exception_for_controllers(e)


def handle_animal_details_get(animal_id: str) -> Tuple[Any, int]:
    """Get animal details"""
    try:
        animal_handler = create_flask_animal_handler()
        return animal_handler.get_animal(animal_id)
    except Exception as e:
        from .error_handler import handle_exception_for_controllers
        return handle_exception_for_controllers(e)


def handle_animal_details_post(body: Dict[str, Any]) -> Tuple[Any, int]:
    """Create new animal"""
    try:
        animal_handler = create_flask_animal_handler()
        return animal_handler.create_animal(body)
    except Exception as e:
        from .error_handler import handle_exception_for_controllers
        return handle_exception_for_controllers(e)


def handle_animal_details_patch(animal_id: str, body: Dict[str, Any]) -> Tuple[Any, int]:
    """Update animal details"""
    try:
        animal_handler = create_flask_animal_handler()
        return animal_handler.update_animal(animal_id, body)
    except Exception as e:
        return handle_exception_for_controllers(e)


def handle_animal_details_delete(animal_id: str) -> Tuple[Any, int]:
    """Delete animal"""
    try:
        animal_handler = create_flask_animal_handler()
        return animal_handler.delete_animal(animal_id)
    except Exception as e:
        return handle_exception_for_controllers(e)


def handle_animal_get(id: str = None, id_: str = None, animal_id: str = None, **kwargs) -> Tuple[Any, int]:
    """Get animal via GET /animal/{animalId} - handles id, id_ and animal_id parameters"""
    try:
        # Handle all parameter names (Connexion may pass id, id_ or animal_id)
        actual_id = animal_id if animal_id is not None else (id if id is not None else id_)
        if actual_id is None:
            from .error_handler import create_error_response
            return create_error_response(
                "missing_parameter",
                "Missing required parameter: animalId",
                {}
            ), 400

        animal_handler = create_flask_animal_handler()
        result = animal_handler.get_animal(actual_id)

        # If the result is an OpenAPI model, convert to dict
        if isinstance(result, tuple) and len(result) == 2:
            response_data, status_code = result
            if hasattr(response_data, 'to_dict'):
                return response_data.to_dict(), status_code
            return response_data, status_code

        return result
    except Exception as e:
        from .error_handler import handle_exception_for_controllers
        return handle_exception_for_controllers(e)


def handle_animal_put(*args, **kwargs) -> Tuple[Any, int]:
    """Update animal via PUT /animal/{animalId} - handles id, id_ and animal_id parameters"""
    try:
        # Handle positional arguments from controller
        # Controller calls handle_(animal_id, body) so args will be (animal_id, body)
        actual_id = None
        body = None

        if len(args) >= 2:
            # First arg is animal_id
            actual_id = args[0]
            # Second arg is body
            body = args[1]
        elif len(args) == 1:
            # Only one arg, could be id or body - check type
            if isinstance(args[0], str):
                actual_id = args[0]
            else:
                body = args[0]

        # Also check kwargs for any missing parameters
        if actual_id is None:
            actual_id = kwargs.get('animal_id') or kwargs.get('id') or kwargs.get('id_')
        if body is None:
            body = kwargs.get('body') or kwargs.get('animal_update')

        # Validate we have both parameters
        if actual_id is None:
            return create_error_response(
                "missing_parameter",
                "Missing required parameter: animalId",
                {}
            ), 400

        if body is None:
            return create_error_response(
                "missing_body",
                "Missing request body",
                {}
            ), 400

        # Convert body to dict if it's a model object
        if hasattr(body, 'to_dict'):
            body = body.to_dict()

        animal_handler = create_flask_animal_handler()
        result = animal_handler.update_animal(actual_id, body)

        # If the result is an OpenAPI model, convert to dict
        if isinstance(result, tuple) and len(result) == 2:
            response_data, status_code = result

            if hasattr(response_data, 'to_dict'):
                # Debug: Check what to_dict returns before returning it
                import json
                import logging
                logger = logging.getLogger(__name__)

                dict_data = response_data.to_dict()
                logger.info(f"Response data type: {type(dict_data)}")
                logger.info(f"Response data keys: {dict_data.keys() if isinstance(dict_data, dict) else 'NOT A DICT'}")

                # Try to serialize to check for issues
                try:
                    json.dumps(dict_data)
                    logger.info("Response data is JSON serializable")
                except TypeError as e:
                    logger.error(f"Response data is NOT JSON serializable: {e}")
                    # Log each field to find the problematic one
                    if isinstance(dict_data, dict):
                        for key, value in dict_data.items():
                            try:
                                json.dumps({key: value})
                            except TypeError:
                                logger.error(f"Field '{key}' is not JSON serializable. Type: {type(value)}, Value: {value}")

                return dict_data, status_code
            return response_data, status_code

        return result
    except Exception as e:
        import traceback
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in handle_animal_put: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        from .error_handler import handle_exception_for_controllers
        return handle_exception_for_controllers(e)


def handle_animal_delete(id: str = None, id_: str = None, animal_id: str = None, **kwargs) -> Tuple[Any, int]:
    """Delete animal via DELETE /animal/{animalId} (soft delete) - handles id, id_ and animal_id parameters"""
    try:
        # Handle all parameter names (Connexion may pass id, id_ or animal_id)
        actual_id = animal_id if animal_id is not None else (id if id is not None else id_)
        if actual_id is None:
            from .error_handler import create_error_response
            return create_error_response(
                "missing_parameter",
                "Missing required parameter: animalId",
                {}
            ), 400
        animal_handler = create_flask_animal_handler()
        return animal_handler.delete_animal(actual_id)
    except Exception as e:
        from .error_handler import handle_exception_for_controllers
        return handle_exception_for_controllers(e)


def handle_animal_post(animal_input: Any = None, body: Dict[str, Any] = None) -> Tuple[Any, int]:
    """Create a new animal via POST /animal"""
    try:
        # Handle both parameter names (controller may pass animal_input or body)
        request_body = animal_input if animal_input is not None else body
        if request_body is None:
            return create_error_response(
                "missing_body",
                "Missing request body",
                {}
            ), 400
        animal_handler = create_flask_animal_handler()
        return animal_handler.create_animal(request_body)
    except Exception as e:
        return handle_exception_for_controllers(e)


# User handlers
def handle_user_list_get(query: str = None, role: str = None, page: int = None, page_size: int = None) -> Tuple[Any, int]:
    """Get list of users with optional filtering and pagination"""
    try:
        user_handler = create_flask_user_handler()
        # Pass query and pagination parameters to the handler
        return user_handler.list_users(query=query, role=role, page=page, page_size=page_size)
    except Exception as e:
        return handle_exception_for_controllers(e)


def handle_user_details_get(user_id: str) -> Tuple[Any, int]:
    """Get user details"""
    try:
        user_handler = create_flask_user_handler()
        return user_handler.get_user(user_id)
    except Exception as e:
        return handle_exception_for_controllers(e)


def handle_user_details_post(body: Dict[str, Any]) -> Tuple[Any, int]:
    """Create new user"""
    try:
        user_handler = create_flask_user_handler()
        return user_handler.create_user(body)
    except Exception as e:
        return handle_exception_for_controllers(e)


def handle_user_details_patch(user_id: str, body: Dict[str, Any]) -> Tuple[Any, int]:
    """Update user details"""
    try:
        user_handler = create_flask_user_handler()
        return user_handler.update_user(user_id, body)
    except Exception as e:
        return handle_exception_for_controllers(e)


def handle_user_details_delete(user_id: str) -> Tuple[Any, int]:
    """Delete user"""
    try:
        user_handler = create_flask_user_handler()
        return user_handler.delete_user(user_id)
    except Exception as e:
        return handle_exception_for_controllers(e)


# Stub handlers for other endpoints that need implementation
def handle_family_list_get() -> Tuple[Any, int]:
    """Get list of families"""
    from .family import family_list_get
    return family_list_get()


def handle_family_details_post(body: Any) -> Tuple[Any, int]:
    """Create new family with proper model handling"""
    from .family import family_details_post

    # Convert FamilyInput model object to dict if needed
    if hasattr(body, 'to_dict'):
        body_dict = body.to_dict()
        # The to_dict() method converts to snake_case, but we need camelCase for the family creation
        # Convert family_name back to familyName
        if 'family_name' in body_dict:
            body_dict['familyName'] = body_dict.pop('family_name')
        if 'preferred_programs' in body_dict:
            body_dict['preferredPrograms'] = body_dict.pop('preferred_programs')
    else:
        body_dict = body

    # Ensure all fields are present in the dictionary
    # The model might not include all fields if not regenerated
    if isinstance(body_dict, dict):
        # Log what we received for debugging
        logger = logging.getLogger(__name__)
        logger.info(f"Creating family with data: {body_dict}")

    return family_details_post(body_dict)


def handle_family_details_get(family_id: str) -> Tuple[Any, int]:
    """Get family details"""
    from .family import family_details_get
    return family_details_get(family_id)


def handle_family_details_patch(family_id: str, body: Dict[str, Any]) -> Tuple[Any, int]:
    """Update family details"""
    from .family import family_details_patch
    return family_details_patch(family_id, body)


def handle_family_details_delete(family_id: str) -> Tuple[Any, int]:
    """Delete family"""
    from .family import family_details_delete
    return family_details_delete(family_id)


# Auth handlers
def handle_login_post(body: Dict[str, Any]) -> Tuple[Any, int]:
    """User login"""
    # Use mock authentication for now
    from .auth_mock import authenticate_user
    from openapi_server.models.auth_response import AuthResponse
    try:
        # Handle both dict and model object
        if hasattr(body, 'to_dict'):
            body = body.to_dict()
        elif hasattr(body, 'username') and hasattr(body, 'password'):
            # It's an AuthRequest model object
            body = {'username': body.username, 'password': body.password}

        # Extract email and password from body
        # Frontend sends 'username' field, but we use email
        email = body.get('username', body.get('email', ''))
        password = body.get('password', '')

        # Authenticate user
        result = authenticate_user(email, password)

        # Create response dict with proper field names for OpenAPI validation
        # The OpenAPI spec expects 'expiresIn' (camelCase) not 'expires_in'
        response_dict = {
            'token': result['token'],
            'user': result['user'],
            'expiresIn': 86400  # 24 hours in seconds
        }
        return response_dict, 200
    except Exception as e:
        from openapi_server.models.error import Error
        error = Error(
            code="authentication_failed",
            message=str(e),
            details={"error": "Authentication failed"}
        )
        return error.to_dict(), 401


def handle_auth_post(body: Dict[str, Any]) -> Tuple[Any, int]:
    """User authentication (login/register)"""
    # Reuse handle_login_post since they're the same for now
    return handle_login_post(body)


def handle_logout_post() -> Tuple[Any, int]:
    """User logout"""
    from .auth_mock import handle_auth_logout_post
    return handle_auth_logout_post()


def handle_auth_refresh_post() -> Tuple[Any, int]:
    """Refresh authentication token"""
    from .auth_mock import handle_auth_refresh_post
    return handle_auth_refresh_post()


def handle_auth_reset_password_post(body: Dict[str, Any]) -> Tuple[Any, int]:
    """Reset password"""
    from .auth_mock import handle_auth_reset_password_post
    return handle_auth_reset_password_post(body)


# System handlers
def handle_health_get() -> Tuple[Any, int]:
    """System health check"""
    from .system import health_get
    return health_get()


# UI handlers
def handle_homepage_get() -> Tuple[Any, int]:
    """Homepage"""
    from .ui import homepage_get
    return homepage_get()


def handle_admin_dashboard_get() -> Tuple[Any, int]:
    """Admin dashboard"""
    from .ui import admin_dashboard_get
    return admin_dashboard_get()
