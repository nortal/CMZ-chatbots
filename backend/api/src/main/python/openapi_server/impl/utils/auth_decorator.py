"""
Authentication decorator for protecting API endpoints
"""

import functools
import logging
from typing import Any, Callable, Dict, List, Optional, Tuple
from flask import request
from .jwt_utils import verify_jwt_token

logger = logging.getLogger(__name__)


def requires_auth(allowed_roles: Optional[List[str]] = None):
    """
    Decorator to require authentication for an endpoint.

    Args:
        allowed_roles: Optional list of roles that can access the endpoint.
                      If None, any authenticated user can access.

    Returns:
        Decorated function that checks authentication before executing.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Tuple[Any, int]:
            # Get authorization header
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
                from openapi_server.models.error import Error
                error = Error(
                    code="unauthorized",
                    message="Invalid or expired token",
                    details={"error": "Token validation failed"}
                )
                return error.to_dict(), 401

            # Check role if specified
            if allowed_roles:
                user_role = payload.get('role', 'visitor')
                if user_role not in allowed_roles:
                    from openapi_server.models.error import Error
                    error = Error(
                        code="forbidden",
                        message="Insufficient permissions",
                        details={
                            "error": f"Role '{user_role}' not allowed. Required roles: {allowed_roles}"
                        }
                    )
                    return error.to_dict(), 403

            # Add user context to request for use in handlers
            request.user_context = {
                'email': payload.get('email'),
                'role': payload.get('role'),
                'user_id': payload.get('user_id') or payload.get('userId'),
                'authenticated': True
            }

            # Execute the wrapped function
            return func(*args, **kwargs)

        return wrapper
    return decorator


def get_current_user() -> Optional[Dict[str, Any]]:
    """
    Get the current authenticated user from request context.

    Returns:
        User context dictionary or None if not authenticated.
    """
    return getattr(request, 'user_context', None)


def is_admin() -> bool:
    """
    Check if the current user is an admin.

    Returns:
        True if user is authenticated as admin, False otherwise.
    """
    user = get_current_user()
    return user is not None and user.get('role') == 'admin'


def is_authenticated() -> bool:
    """
    Check if the current request is authenticated.

    Returns:
        True if user is authenticated, False otherwise.
    """
    user = get_current_user()
    return user is not None and user.get('authenticated', False)