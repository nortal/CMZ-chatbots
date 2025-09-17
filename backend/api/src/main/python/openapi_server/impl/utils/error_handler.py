"""
Centralized error handler utility for consistent error responses
Ensures all errors follow the Error schema
"""

from typing import Dict, Any, Optional, Tuple
from openapi_server.models.error import Error
import logging
import re

logger = logging.getLogger(__name__)

# Patterns for sensitive information that should not be logged
SENSITIVE_PATTERNS = [
    r'password',
    r'passwd',
    r'pwd',
    r'token',
    r'api_key',
    r'apikey',
    r'secret',
    r'authorization',
    r'auth',
    r'credential',
    r'private_key',
    r'private',
    r'key'
]

def sanitize_for_logging(data: Any) -> Any:
    """
    Sanitize sensitive information from data before logging.

    Args:
        data: Data to sanitize (dict, list, or primitive)

    Returns:
        Sanitized copy of the data
    """
    if data is None:
        return None

    if isinstance(data, dict):
        sanitized = {}
        for key, value in data.items():
            # Check if key contains sensitive pattern
            key_lower = key.lower()
            is_sensitive = any(pattern in key_lower for pattern in SENSITIVE_PATTERNS)

            if is_sensitive:
                sanitized[key] = "[REDACTED]"
            elif isinstance(value, (dict, list)):
                sanitized[key] = sanitize_for_logging(value)
            else:
                # Also check if string value looks like a token/password
                if isinstance(value, str) and len(value) > 20 and (
                    value.startswith(('eyJ', 'Bearer ', 'github_pat_', 'gho_', 'ghp_', 'ATATT')) or
                    re.match(r'^[A-Za-z0-9+/]{20,}={0,2}$', value)  # Base64-like
                ):
                    sanitized[key] = "[REDACTED]"
                else:
                    sanitized[key] = value
        return sanitized

    elif isinstance(data, list):
        return [sanitize_for_logging(item) for item in data]

    # For strings that look like tokens
    elif isinstance(data, str) and len(data) > 20 and (
        data.startswith(('eyJ', 'Bearer ', 'github_pat_', 'gho_', 'ghp_', 'ATATT')) or
        re.match(r'^[A-Za-z0-9+/]{20,}={0,2}$', data)
    ):
        return "[REDACTED]"

    return data


def create_error_response(
    code: str,
    message: str,
    status_code: int,
    details: Optional[Dict[str, Any]] = None
) -> Tuple[Dict[str, Any], int]:
    """
    Create a standardized error response using the Error schema.

    Args:
        code: Error code (e.g., 'validation_error', 'not_found', 'server_error')
        message: Human-readable error message
        status_code: HTTP status code
        details: Optional additional details about the error

    Returns:
        Tuple of (error_dict, status_code)
    """
    error = Error(
        code=code,
        message=message,
        details=details or {}
    )

    # Sanitize details before logging to prevent sensitive information exposure
    sanitized_details = sanitize_for_logging(details) if details else None
    # Also sanitize the message to ensure no sensitive data in error messages
    sanitized_message = sanitize_for_logging(message) if isinstance(message, str) else message

    # Log the error for monitoring with sanitized details
    if status_code >= 500:
        logger.error(f"Server error: {code} - {sanitized_message}", extra={"details": sanitized_details})
    elif status_code >= 400:
        logger.warning(f"Client error: {code} - {sanitized_message}", extra={"details": sanitized_details})

    return error.to_dict(), status_code


def validation_error(message: str, field: Optional[str] = None, value: Optional[Any] = None) -> Tuple[Dict[str, Any], int]:
    """
    Create a validation error response (400).

    Args:
        message: Validation error message
        field: Optional field name that failed validation
        value: Optional invalid value

    Returns:
        Tuple of (error_dict, 400)
    """
    details = {}
    if field:
        details['field'] = field
    if value is not None:
        details['invalid_value'] = str(value)

    return create_error_response(
        code='validation_error',
        message=message,
        status_code=400,
        details=details
    )


def not_found_error(resource: str, identifier: Optional[str] = None) -> Tuple[Dict[str, Any], int]:
    """
    Create a not found error response (404).

    Args:
        resource: Type of resource not found
        identifier: Optional resource identifier

    Returns:
        Tuple of (error_dict, 404)
    """
    message = f"{resource} not found"
    details = {'resource': resource}
    if identifier:
        details['identifier'] = identifier
        message = f"{resource} with identifier '{identifier}' not found"

    return create_error_response(
        code='not_found',
        message=message,
        status_code=404,
        details=details
    )


def unauthorized_error(message: str = "Authentication required") -> Tuple[Dict[str, Any], int]:
    """
    Create an unauthorized error response (401).

    Args:
        message: Error message

    Returns:
        Tuple of (error_dict, 401)
    """
    return create_error_response(
        code='unauthorized',
        message=message,
        status_code=401
    )


def forbidden_error(message: str = "Access denied") -> Tuple[Dict[str, Any], int]:
    """
    Create a forbidden error response (403).

    Args:
        message: Error message

    Returns:
        Tuple of (error_dict, 403)
    """
    return create_error_response(
        code='forbidden',
        message=message,
        status_code=403
    )


def conflict_error(message: str, resource: Optional[str] = None) -> Tuple[Dict[str, Any], int]:
    """
    Create a conflict error response (409).

    Args:
        message: Conflict description
        resource: Optional resource type

    Returns:
        Tuple of (error_dict, 409)
    """
    details = {}
    if resource:
        details['resource'] = resource

    return create_error_response(
        code='conflict',
        message=message,
        status_code=409,
        details=details
    )


def server_error(message: str = "Internal server error", exception: Optional[Exception] = None) -> Tuple[Dict[str, Any], int]:
    """
    Create a server error response (500).

    Args:
        message: Error message
        exception: Optional exception that caused the error

    Returns:
        Tuple of (error_dict, 500)
    """
    details = {}
    if exception:
        details['error_type'] = type(exception).__name__
        # Don't expose sensitive exception details in production
        import os
        if os.environ.get('ENVIRONMENT') != 'production':
            details['error_details'] = str(exception)

    return create_error_response(
        code='server_error',
        message=message,
        status_code=500,
        details=details
    )


def not_implemented_error(operation: str) -> Tuple[Dict[str, Any], int]:
    """
    Create a not implemented error response (501).

    Args:
        operation: Operation name that is not implemented

    Returns:
        Tuple of (error_dict, 501)
    """
    return create_error_response(
        code='not_implemented',
        message=f"Operation '{operation}' is not yet implemented",
        status_code=501,
        details={'operation': operation}
    )


def bad_request_error(message: str, details: Optional[Dict[str, Any]] = None) -> Tuple[Dict[str, Any], int]:
    """
    Create a bad request error response (400).

    Args:
        message: Error message
        details: Optional additional error details

    Returns:
        Tuple of (error_dict, 400)
    """
    return create_error_response(
        code='bad_request',
        message=message,
        status_code=400,
        details=details
    )