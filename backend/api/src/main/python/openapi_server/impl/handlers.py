"""
Handler module that exposes hexagonal architecture handlers for generated controllers

This module provides a unified interface for the generated OpenAPI controllers
to access the business logic through the hexagonal architecture pattern.
"""

from typing import Any, Tuple, Dict
import inspect
from .dependency_injection import (
    create_flask_user_handler,
    create_flask_animal_handler,
    create_user_service,
    create_animal_service
)


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
            'animal_id_get': handle_animal_id_get,  # Add missing GET mapping
            'animal_id_put': handle_animal_id_put,
            'animal_id_delete': handle_animal_id_delete,  # Add missing mapping
            'animal_post': handle_animal_post,  # Add missing mapping
            'user_list_get': handle_user_list_get,
            'user_details_get': handle_user_details_get,
            'user_details_post': handle_user_details_post,
            'user_details_patch': handle_user_details_patch,
            'user_details_delete': handle_user_details_delete,
            'family_list_get': handle_family_list_get,
            'family_details_post': handle_family_details_post,
            'family_details_get': handle_family_details_get,
            'family_details_patch': handle_family_details_patch,
            'family_details_delete': handle_family_details_delete,
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
        animal_handler = create_flask_animal_handler()
        return animal_handler.get_animal_config(animal_id)
    except Exception as e:
        from .error_handler import handle_exception_for_controllers
        return handle_exception_for_controllers(e)


def handle_animal_config_patch(animal_id: str, body: Dict[str, Any]) -> Tuple[Any, int]:
    """Update animal configuration"""
    try:
        animal_handler = create_flask_animal_handler()
        return animal_handler.update_animal_config(animal_id, body)
    except Exception as e:
        from .error_handler import handle_exception_for_controllers
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

        animal_handler = create_flask_animal_handler()
        return animal_handler.list_animals(status)
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
        from .error_handler import handle_exception_for_controllers
        return handle_exception_for_controllers(e)


def handle_animal_details_delete(animal_id: str) -> Tuple[Any, int]:
    """Delete animal"""
    try:
        animal_handler = create_flask_animal_handler()
        return animal_handler.delete_animal(animal_id)
    except Exception as e:
        from .error_handler import handle_exception_for_controllers
        return handle_exception_for_controllers(e)


def handle_animal_id_get(id_: str) -> Tuple[Any, int]:
    """Get animal via GET /animal/{id}"""
    try:
        animal_handler = create_flask_animal_handler()
        # Connexion passes id_ but our handler expects animal_id
        result = animal_handler.get_animal(id_)

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


def handle_animal_id_put(id_: str, body: Dict[str, Any]) -> Tuple[Any, int]:
    """Update animal via PUT /animal/{id}"""
    try:
        animal_handler = create_flask_animal_handler()
        # Connexion passes id_ but our handler expects animal_id
        result = animal_handler.update_animal(id_, body)

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
        logger.error(f"Error in handle_animal_id_put: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        from .error_handler import handle_exception_for_controllers
        return handle_exception_for_controllers(e)


def handle_animal_id_delete(id_: str = None, id: str = None) -> Tuple[Any, int]:
    """Delete animal via DELETE /animal/{id} (soft delete)"""
    try:
        # Handle both parameter names (connexion may pass id_ or id)
        animal_id = id_ if id_ is not None else id
        if animal_id is None:
            from .error_handler import create_error_response
            return create_error_response(
                "missing_parameter",
                "Missing required parameter: id",
                {}
            ), 400
        animal_handler = create_flask_animal_handler()
        return animal_handler.delete_animal(animal_id)
    except Exception as e:
        from .error_handler import handle_exception_for_controllers
        return handle_exception_for_controllers(e)


def handle_animal_post(animal_input: Any = None, body: Dict[str, Any] = None) -> Tuple[Any, int]:
    """Create a new animal via POST /animal"""
    try:
        # Handle both parameter names (controller may pass animal_input or body)
        request_body = animal_input if animal_input is not None else body
        if request_body is None:
            from .error_handler import create_error_response
            return create_error_response(
                "missing_body",
                "Missing request body",
                {}
            ), 400
        animal_handler = create_flask_animal_handler()
        return animal_handler.create_animal(request_body)
    except Exception as e:
        from .error_handler import handle_exception_for_controllers
        return handle_exception_for_controllers(e)


# User handlers
def handle_user_list_get() -> Tuple[Any, int]:
    """Get list of users"""
    try:
        user_handler = create_flask_user_handler()
        return user_handler.list_users()
    except Exception as e:
        from .error_handler import handle_exception_for_controllers
        return handle_exception_for_controllers(e)


def handle_user_details_get(user_id: str) -> Tuple[Any, int]:
    """Get user details"""
    try:
        user_handler = create_flask_user_handler()
        return user_handler.get_user(user_id)
    except Exception as e:
        from .error_handler import handle_exception_for_controllers
        return handle_exception_for_controllers(e)


def handle_user_details_post(body: Dict[str, Any]) -> Tuple[Any, int]:
    """Create new user"""
    try:
        user_handler = create_flask_user_handler()
        return user_handler.create_user(body)
    except Exception as e:
        from .error_handler import handle_exception_for_controllers
        return handle_exception_for_controllers(e)


def handle_user_details_patch(user_id: str, body: Dict[str, Any]) -> Tuple[Any, int]:
    """Update user details"""
    try:
        user_handler = create_flask_user_handler()
        return user_handler.update_user(user_id, body)
    except Exception as e:
        from .error_handler import handle_exception_for_controllers
        return handle_exception_for_controllers(e)


def handle_user_details_delete(user_id: str) -> Tuple[Any, int]:
    """Delete user"""
    try:
        user_handler = create_flask_user_handler()
        return user_handler.delete_user(user_id)
    except Exception as e:
        from .error_handler import handle_exception_for_controllers
        return handle_exception_for_controllers(e)


# Stub handlers for other endpoints that need implementation
def handle_family_list_get() -> Tuple[Any, int]:
    """Get list of families"""
    from .family import family_list_get
    return family_list_get()


def handle_family_details_post(body: Dict[str, Any]) -> Tuple[Any, int]:
    """Create new family"""
    from .family import family_details_post
    return family_details_post(body)


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
    from .auth import authenticate_user
    from openapi_server.models.auth_response import AuthResponse
    try:
        # Handle both dict and model object
        if hasattr(body, 'to_dict'):
            body = body.to_dict()
        elif hasattr(body, 'username') and hasattr(body, 'password'):
            # It's an AuthRequest model object
            body = {'username': body.username, 'password': body.password}

        # Extract email and password from body
        email = body.get('email', body.get('username', ''))
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
    from .auth import logout_post
    return logout_post()


def handle_auth_refresh_post() -> Tuple[Any, int]:
    """Refresh authentication token"""
    from .auth import handle_auth_refresh_post
    return handle_auth_refresh_post()


def handle_auth_reset_password_post(body: Dict[str, Any]) -> Tuple[Any, int]:
    """Reset password"""
    from .auth import handle_auth_reset_password_post
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