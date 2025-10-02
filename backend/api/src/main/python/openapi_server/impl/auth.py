"""
Auto-generated redirect module to prevent stub conflicts.
This file redirects to real implementations in handlers.py.
"""

from typing import Any, Tuple

# Import real implementations from handlers
from . import handlers


def handle_auth_post(*args, **kwargs) -> Tuple[Any, int]:
    """Redirect to real implementation in handlers.py"""
    return handlers.handle_auth_post(*args, **kwargs)

def handle_auth_refresh_post(*args, **kwargs) -> Tuple[Any, int]:
    """Redirect to real implementation in handlers.py"""
    return handlers.handle_auth_refresh_post(*args, **kwargs)

def handle_auth_reset_password_post(*args, **kwargs) -> Tuple[Any, int]:
    """Redirect to real implementation in handlers.py"""
    return handlers.handle_auth_reset_password_post(*args, **kwargs)


# Default handler for operations not yet implemented
def not_implemented_error(operation: str) -> Tuple[dict, int]:
    """Return not implemented error for operations without implementation."""
    from openapi_server.models.error import Error
    error = Error(
        code="not_implemented",
        message=f"Operation {operation} not yet implemented",
        details={"module": __name__, "operation": operation}
    )
    return error.to_dict(), 501
