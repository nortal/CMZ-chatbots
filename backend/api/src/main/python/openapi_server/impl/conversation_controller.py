"""
Conversation Controller Implementation for OpenAI Assistants API Integration

This module provides the implementation layer for conversation controllers,
routing to the modern OpenAI Assistants API system.
"""

from typing import Any, Tuple
import logging

# Import our conversation handlers that now use Assistants API
from .conversation import (
    handle_convo_turn_post,
    handle_convo_history_get,
    handle_convo_history_delete,
    handle_summarize_convo_post
)

logger = logging.getLogger(__name__)

def handle_(body=None, *args, **kwargs) -> Tuple[Any, int]:
    """
    Generic handler routing for conversation controller.
    Routes to the appropriate conversation handler based on the function name.
    """
    # Get the caller function name to determine routing
    import inspect
    caller_frame = inspect.currentframe().f_back
    caller_name = caller_frame.f_code.co_name

    try:
        if caller_name == 'convo_turn_post':
            logger.info("🚀 CONVERSATION CONTROLLER: Routing to Assistants API handler 🚀")
            return handle_convo_turn_post(body, *args, **kwargs)
        elif caller_name == 'convo_history_get':
            logger.info("🔍 CONVERSATION CONTROLLER: Routing to history handler 🔍")
            return handle_convo_history_get(*args, **kwargs)
        elif caller_name == 'convo_history_delete':
            logger.info("🗑️ CONVERSATION CONTROLLER: Routing to delete handler 🗑️")
            return handle_convo_history_delete(*args, **kwargs)
        elif caller_name == 'summarize_convo_post':
            logger.info("📝 CONVERSATION CONTROLLER: Routing to summarize handler 📝")
            return handle_summarize_convo_post(body, *args, **kwargs)
        else:
            logger.warning(f"Unknown conversation operation: {caller_name}")
            return {"error": f"Unknown conversation operation: {caller_name}"}, 501

    except Exception as e:
        logger.error(f"Failed to route conversation operation {caller_name}: {e}")
        return {"error": f"Internal error in conversation controller: {str(e)}"}, 500