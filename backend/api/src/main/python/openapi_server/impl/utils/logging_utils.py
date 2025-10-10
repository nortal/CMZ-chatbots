"""
Logging utilities with security protections against log injection attacks

Defense-in-Depth Strategy:
1. Primary: Use .replace("\n", " ").replace("\r", " ") on values (CodeQL-recognized)
2. Secondary: Use sanitize_log_extra() for comprehensive protection

Example:
    logger.warning("User action", extra=sanitize_log_extra({
        "user_id": str(user_id).replace("\n", " ").replace("\r", " "),
        "action": str(action).replace("\n", " ").replace("\r", " ")
    }))

The .replace() calls satisfy CodeQL's static analysis, while sanitize_log_extra()
provides additional protection against:
- ANSI escape sequences (terminal color injection)
- Null bytes (log corruption)
- Excessive length (log flooding)
"""
import re
from typing import Any, Dict


def sanitize_log_value(value: Any) -> str:
    """
    Sanitize a value for safe logging by removing characters that could
    enable log injection attacks.

    Removes/replaces:
    - Newlines (\n, \r)
    - Carriage returns
    - Null bytes
    - ANSI escape sequences

    Args:
        value: The value to sanitize (will be converted to string)

    Returns:
        Sanitized string safe for logging
    """
    if value is None:
        return "None"

    # Convert to string
    str_value = str(value)

    # Remove newlines, carriage returns, and null bytes
    str_value = str_value.replace('\n', ' ').replace('\r', ' ').replace('\0', '')

    # Remove ANSI escape sequences (color codes, etc.)
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    str_value = ansi_escape.sub('', str_value)

    # Limit length to prevent log flooding
    max_length = 500
    if len(str_value) > max_length:
        str_value = str_value[:max_length] + "...[truncated]"

    return str_value


def sanitize_log_extra(extra: Dict[str, Any]) -> Dict[str, str]:
    """
    Sanitize all values in an extra logging dictionary.

    Args:
        extra: Dictionary of extra fields for logging

    Returns:
        Dictionary with all values sanitized
    """
    return {
        key: sanitize_log_value(value)
        for key, value in extra.items()
    }
