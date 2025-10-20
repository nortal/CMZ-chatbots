"""
Password policy validation utility
Implements PR003946-87: Password policy enforcement
"""

import re
from typing import Tuple, Optional


def validate_password(password: str) -> Tuple[bool, Optional[str]]:
    """
    Validate password against security policy requirements.

    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    - At least one special character

    Args:
        password: The password to validate

    Returns:
        Tuple of (is_valid, error_message)
        If valid: (True, None)
        If invalid: (False, "specific error message")
    """

    if not password:
        return False, "Password is required"

    # Check minimum length
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    # Check for uppercase letter
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"

    # Check for lowercase letter
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"

    # Check for digit
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"

    # Check for special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character (!@#$%^&*(),.?\":{}|<>)"

    # All checks passed
    return True, None


def get_password_policy_description() -> str:
    """
    Get a human-readable description of the password policy.

    Returns:
        String describing the password requirements
    """
    return (
        "Password must meet the following requirements:\n"
        "• At least 8 characters long\n"
        "• At least one uppercase letter (A-Z)\n"
        "• At least one lowercase letter (a-z)\n"
        "• At least one number (0-9)\n"
        "• At least one special character (!@#$%^&*(),.?\":{}|<>)"
    )