"""
Assistant Management Controller Bridge

This module bridges the OpenAPI controller to the assistants implementation,
following CMZ patterns for controller-to-implementation routing.

Connects assistant_management_controller.py operations to assistants.py functions.
"""

import inspect
from typing import Dict, Any, Tuple, Union
from . import assistants


def handle_(*args, **kwargs) -> Tuple[Dict[str, Any], int]:
    """
    Generic handler that routes controller calls to appropriate assistant functions.

    This function analyzes the calling context to determine which assistant
    operation to execute and routes parameters accordingly.

    Args:
        *args: Positional arguments from controller
        **kwargs: Keyword arguments from controller

    Returns:
        Tuple[Dict[str, Any], int]: Response data and HTTP status code
    """
    # Get the calling function name from stack
    caller_frame = inspect.currentframe().f_back
    caller_name = caller_frame.f_code.co_name

    print(f"🚀 DEBUG assistant_management.handle_(): caller_name={caller_name}, args={args}, kwargs={kwargs}")

    # Route based on controller operation
    if caller_name == 'assistant_create_post':
        # POST /assistant - Create assistant
        body = args[0] if args else kwargs.get('body')
        return assistants.create_assistant(body)

    elif caller_name == 'assistant_list_get':
        # GET /assistant - List assistants with optional filters
        animal_id = args[0] if len(args) > 0 else kwargs.get('animal_id')
        status = args[1] if len(args) > 1 else kwargs.get('status')

        if animal_id:
            # If animal_id provided, get specific assistant for that animal
            return assistants.get_assistant_by_animal(animal_id)
        else:
            # Otherwise list all assistants
            return assistants.list_assistants()

    elif caller_name == 'assistant_get':
        # GET /assistant/{assistantId} - Get specific assistant
        assistant_id = args[0] if args else kwargs.get('assistant_id')
        return assistants.get_assistant(assistant_id)

    elif caller_name == 'assistant_update_put':
        # PUT /assistant/{assistantId} - Update assistant
        assistant_id = args[0] if args else kwargs.get('assistant_id')
        body = args[1] if len(args) > 1 else kwargs.get('body')
        return assistants.update_assistant(assistant_id, body)

    elif caller_name == 'assistant_delete':
        # DELETE /assistant/{assistantId} - Delete assistant
        assistant_id = args[0] if args else kwargs.get('assistant_id')
        return assistants.delete_assistant(assistant_id)

    else:
        # Unknown operation
        return {
            "error": "not_implemented",
            "message": f"No handler found for operation: {caller_name}",
            "details": {
                "caller": caller_name,
                "args": str(args),
                "kwargs": str(kwargs)
            }
        }, 501


# Alternative specific handlers for direct routing
def handle_assistant_create_post(*args, **kwargs) -> Tuple[Union[Dict[str, Any], Any], int]:
    """Create new assistant - forwards to assistants.create_assistant"""
    body = args[0] if args else kwargs.get('body')
    return assistants.create_assistant(body)


def handle_assistant_list_get(*args, **kwargs) -> Tuple[Union[Dict[str, Any], Any], int]:
    """List assistants - forwards to assistants.list_assistants"""
    animal_id = args[0] if len(args) > 0 else kwargs.get('animal_id')
    status = args[1] if len(args) > 1 else kwargs.get('status')

    if animal_id:
        return assistants.get_assistant_by_animal(animal_id)
    else:
        return assistants.list_assistants()


def handle_assistant_get(*args, **kwargs) -> Tuple[Union[Dict[str, Any], Any], int]:
    """Get assistant by ID - forwards to assistants.get_assistant"""
    assistant_id = args[0] if args else kwargs.get('assistant_id')
    return assistants.get_assistant(assistant_id)


def handle_assistant_update_put(*args, **kwargs) -> Tuple[Union[Dict[str, Any], Any], int]:
    """Update assistant - forwards to assistants.update_assistant"""
    assistant_id = args[0] if args else kwargs.get('assistant_id')
    body = args[1] if len(args) > 1 else kwargs.get('body')
    return assistants.update_assistant(assistant_id, body)


def handle_assistant_delete(*args, **kwargs) -> Tuple[Union[Dict[str, Any], Any], int]:
    """Delete assistant - forwards to assistants.delete_assistant"""
    assistant_id = args[0] if args else kwargs.get('assistant_id')
    return assistants.delete_assistant(assistant_id)

