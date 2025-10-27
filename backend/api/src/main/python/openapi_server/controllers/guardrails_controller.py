import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.apply_guardrail_template200_response import ApplyGuardrailTemplate200Response  # noqa: E501
from openapi_server.models.apply_guardrail_template_request import ApplyGuardrailTemplateRequest  # noqa: E501
from openapi_server.models.error import Error  # noqa: E501
from openapi_server.models.get_animal_system_prompt200_response import GetAnimalSystemPrompt200Response  # noqa: E501
from openapi_server.models.guardrail import Guardrail  # noqa: E501
from openapi_server.models.guardrail_input import GuardrailInput  # noqa: E501
from openapi_server.models.guardrail_template import GuardrailTemplate  # noqa: E501
from openapi_server.models.guardrail_update import GuardrailUpdate  # noqa: E501
from openapi_server.models.validate_content200_response import ValidateContent200Response  # noqa: E501
from openapi_server.models.validate_content_request import ValidateContentRequest  # noqa: E501
# from openapi_server import util  # Not used


def apply_guardrail_template(body):  # noqa: E501
    """Apply template to animal

     # noqa: E501

    :param apply_guardrail_template_request: 
    :type apply_guardrail_template_request: dict | bytes

    :rtype: Union[ApplyGuardrailTemplate200Response, Tuple[ApplyGuardrailTemplate200Response, int], Tuple[ApplyGuardrailTemplate200Response, int, Dict[str, str]]
    """
    # Auto-generated parameter handling
    if connexion.request.is_json:
        body = ApplyGuardrailTemplateRequest.from_dict(connexion.request.get_json())  # noqa: E501

    # CMZ Auto-Generated Implementation Connection
    # This template automatically connects controllers to impl modules
    try:
        # Dynamic import of implementation module based on controller name
        # Auto-detect implementation module from operationId
        impl_module_name = "guardrails_controller".replace("_controller", "")
        impl_function_name = "handle_"

        # Try common implementation patterns
        try:
            # Pattern 1: Direct module import
            impl_module = __import__(f"openapi_server.impl.{impl_module_name}", fromlist=[impl_function_name])
            impl_function = getattr(impl_module, impl_function_name)
        except (ImportError, AttributeError):
            # Pattern 2: Generic handler with hexagonal architecture routing
            from openapi_server.impl import handlers
            # Use the generic handle_ function that routes based on caller name
            impl_function = handlers.handle_
            if not impl_function:
                # Pattern 3: Default error for missing implementation
                raise NotImplementedError(
                    f"Implementation function 'handle_' not found in handlers module. "
                    f"Please ensure the following: "
                    f"1. The handlers.py file exists in the impl directory "
                    f"2. The handle_ function is defined in handlers.py "
                    f"3. The function signature matches the controller parameters"
                )

        # Call implementation function with processed parameters
        result = impl_function(body)

        # Handle different return types
        if isinstance(result, tuple):
            return result  # Already formatted (data, status_code)
        else:
            return result, 200

    except NotImplementedError as e:
        # Development mode: return clear error instead of placeholder
        from openapi_server.models.error import Error
        error_obj = Error(
            code="not_implemented",
            message=f"Controller apply_guardrail_template implementation not found: {str(e)}",
            details={"controller": "GuardrailsController", "operation": "apply_guardrail_template"}
        )
        return error_obj, 501

    except Exception as e:
        # Use centralized error handler if available
        try:
            from openapi_server.impl.error_handler import handle_exception_for_controllers
            return handle_exception_for_controllers(e)
        except ImportError:
            # Fallback error response
            from openapi_server.models.error import Error
            error_obj = Error(
                code="internal_error",
                message=f"Internal server error in apply_guardrail_template: {str(e)}",
                details={"controller": "GuardrailsController", "operation": "apply_guardrail_template"}
            )
            return error_obj, 500


def create_guardrail(body):  # noqa: E501
    """Create new guardrail

     # noqa: E501

    :param guardrail_input: 
    :type guardrail_input: dict | bytes

    :rtype: Union[Guardrail, Tuple[Guardrail, int], Tuple[Guardrail, int, Dict[str, str]]
    """
    # Auto-generated parameter handling
    if connexion.request.is_json:
        body = GuardrailInput.from_dict(connexion.request.get_json())  # noqa: E501

    # CMZ Auto-Generated Implementation Connection
    # This template automatically connects controllers to impl modules
    try:
        # Dynamic import of implementation module based on controller name
        # Auto-detect implementation module from operationId
        impl_module_name = "guardrails_controller".replace("_controller", "")
        impl_function_name = "handle_"

        # Try common implementation patterns
        try:
            # Pattern 1: Direct module import
            impl_module = __import__(f"openapi_server.impl.{impl_module_name}", fromlist=[impl_function_name])
            impl_function = getattr(impl_module, impl_function_name)
        except (ImportError, AttributeError):
            # Pattern 2: Generic handler with hexagonal architecture routing
            from openapi_server.impl import handlers
            # Use the generic handle_ function that routes based on caller name
            impl_function = handlers.handle_
            if not impl_function:
                # Pattern 3: Default error for missing implementation
                raise NotImplementedError(
                    f"Implementation function 'handle_' not found in handlers module. "
                    f"Please ensure the following: "
                    f"1. The handlers.py file exists in the impl directory "
                    f"2. The handle_ function is defined in handlers.py "
                    f"3. The function signature matches the controller parameters"
                )

        # Call implementation function with processed parameters
        result = impl_function(body)

        # Handle different return types
        if isinstance(result, tuple):
            return result  # Already formatted (data, status_code)
        else:
            return result, 201

    except NotImplementedError as e:
        # Development mode: return clear error instead of placeholder
        from openapi_server.models.error import Error
        error_obj = Error(
            code="not_implemented",
            message=f"Controller create_guardrail implementation not found: {str(e)}",
            details={"controller": "GuardrailsController", "operation": "create_guardrail"}
        )
        return error_obj, 501

    except Exception as e:
        # Use centralized error handler if available
        try:
            from openapi_server.impl.error_handler import handle_exception_for_controllers
            return handle_exception_for_controllers(e)
        except ImportError:
            # Fallback error response
            from openapi_server.models.error import Error
            error_obj = Error(
                code="internal_error",
                message=f"Internal server error in create_guardrail: {str(e)}",
                details={"controller": "GuardrailsController", "operation": "create_guardrail"}
            )
            return error_obj, 500


def delete_guardrail(guardrail_id):  # noqa: E501
    """Delete guardrail (soft delete)

     # noqa: E501

    :param guardrail_id: 
    :type guardrail_id: str

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    # Auto-generated parameter handling

    # CMZ Auto-Generated Implementation Connection
    # This template automatically connects controllers to impl modules
    try:
        # Dynamic import of implementation module based on controller name
        # Auto-detect implementation module from operationId
        impl_module_name = "guardrails_controller".replace("_controller", "")
        impl_function_name = "handle_"

        # Try common implementation patterns
        try:
            # Pattern 1: Direct module import
            impl_module = __import__(f"openapi_server.impl.{impl_module_name}", fromlist=[impl_function_name])
            impl_function = getattr(impl_module, impl_function_name)
        except (ImportError, AttributeError):
            # Pattern 2: Generic handler with hexagonal architecture routing
            from openapi_server.impl import handlers
            # Use the generic handle_ function that routes based on caller name
            impl_function = handlers.handle_
            if not impl_function:
                # Pattern 3: Default error for missing implementation
                raise NotImplementedError(
                    f"Implementation function 'handle_' not found in handlers module. "
                    f"Please ensure the following: "
                    f"1. The handlers.py file exists in the impl directory "
                    f"2. The handle_ function is defined in handlers.py "
                    f"3. The function signature matches the controller parameters"
                )

        # Call implementation function with processed parameters
        result = impl_function(guardrail_id)

        # Handle different return types
        if isinstance(result, tuple):
            return result  # Already formatted (data, status_code)
        else:
            return result, 204

    except NotImplementedError as e:
        # Development mode: return clear error instead of placeholder
        from openapi_server.models.error import Error
        error_obj = Error(
            code="not_implemented",
            message=f"Controller delete_guardrail implementation not found: {str(e)}",
            details={"controller": "GuardrailsController", "operation": "delete_guardrail"}
        )
        return error_obj, 501

    except Exception as e:
        # Use centralized error handler if available
        try:
            from openapi_server.impl.error_handler import handle_exception_for_controllers
            return handle_exception_for_controllers(e)
        except ImportError:
            # Fallback error response
            from openapi_server.models.error import Error
            error_obj = Error(
                code="internal_error",
                message=f"Internal server error in delete_guardrail: {str(e)}",
                details={"controller": "GuardrailsController", "operation": "delete_guardrail"}
            )
            return error_obj, 500


def get_animal_effective_guardrails(animal_id):  # noqa: E501
    """Get effective guardrails for an animal

     # noqa: E501

    :param animal_id: 
    :type animal_id: str

    :rtype: Union[List[Guardrail], Tuple[List[Guardrail], int], Tuple[List[Guardrail], int, Dict[str, str]]
    """
    # Auto-generated parameter handling

    # CMZ Auto-Generated Implementation Connection
    # This template automatically connects controllers to impl modules
    try:
        # Dynamic import of implementation module based on controller name
        # Auto-detect implementation module from operationId
        impl_module_name = "guardrails_controller".replace("_controller", "")
        impl_function_name = "handle_"

        # Try common implementation patterns
        try:
            # Pattern 1: Direct module import
            impl_module = __import__(f"openapi_server.impl.{impl_module_name}", fromlist=[impl_function_name])
            impl_function = getattr(impl_module, impl_function_name)
        except (ImportError, AttributeError):
            # Pattern 2: Generic handler with hexagonal architecture routing
            from openapi_server.impl import handlers
            # Use the generic handle_ function that routes based on caller name
            impl_function = handlers.handle_
            if not impl_function:
                # Pattern 3: Default error for missing implementation
                raise NotImplementedError(
                    f"Implementation function 'handle_' not found in handlers module. "
                    f"Please ensure the following: "
                    f"1. The handlers.py file exists in the impl directory "
                    f"2. The handle_ function is defined in handlers.py "
                    f"3. The function signature matches the controller parameters"
                )

        # Call implementation function with processed parameters
        result = impl_function(animal_id)

        # Handle different return types
        if isinstance(result, tuple):
            return result  # Already formatted (data, status_code)
        else:
            return result, 200

    except NotImplementedError as e:
        # Development mode: return clear error instead of placeholder
        from openapi_server.models.error import Error
        error_obj = Error(
            code="not_implemented",
            message=f"Controller get_animal_effective_guardrails implementation not found: {str(e)}",
            details={"controller": "GuardrailsController", "operation": "get_animal_effective_guardrails"}
        )
        return error_obj, 501

    except Exception as e:
        # Use centralized error handler if available
        try:
            from openapi_server.impl.error_handler import handle_exception_for_controllers
            return handle_exception_for_controllers(e)
        except ImportError:
            # Fallback error response
            from openapi_server.models.error import Error
            error_obj = Error(
                code="internal_error",
                message=f"Internal server error in get_animal_effective_guardrails: {str(e)}",
                details={"controller": "GuardrailsController", "operation": "get_animal_effective_guardrails"}
            )
            return error_obj, 500


def get_animal_system_prompt(animal_id):  # noqa: E501
    """Get system prompt with guardrails

     # noqa: E501

    :param animal_id: 
    :type animal_id: str

    :rtype: Union[GetAnimalSystemPrompt200Response, Tuple[GetAnimalSystemPrompt200Response, int], Tuple[GetAnimalSystemPrompt200Response, int, Dict[str, str]]
    """
    # Auto-generated parameter handling

    # CMZ Auto-Generated Implementation Connection
    # This template automatically connects controllers to impl modules
    try:
        # Dynamic import of implementation module based on controller name
        # Auto-detect implementation module from operationId
        impl_module_name = "guardrails_controller".replace("_controller", "")
        impl_function_name = "handle_"

        # Try common implementation patterns
        try:
            # Pattern 1: Direct module import
            impl_module = __import__(f"openapi_server.impl.{impl_module_name}", fromlist=[impl_function_name])
            impl_function = getattr(impl_module, impl_function_name)
        except (ImportError, AttributeError):
            # Pattern 2: Generic handler with hexagonal architecture routing
            from openapi_server.impl import handlers
            # Use the generic handle_ function that routes based on caller name
            impl_function = handlers.handle_
            if not impl_function:
                # Pattern 3: Default error for missing implementation
                raise NotImplementedError(
                    f"Implementation function 'handle_' not found in handlers module. "
                    f"Please ensure the following: "
                    f"1. The handlers.py file exists in the impl directory "
                    f"2. The handle_ function is defined in handlers.py "
                    f"3. The function signature matches the controller parameters"
                )

        # Call implementation function with processed parameters
        result = impl_function(animal_id)

        # Handle different return types
        if isinstance(result, tuple):
            return result  # Already formatted (data, status_code)
        else:
            return result, 200

    except NotImplementedError as e:
        # Development mode: return clear error instead of placeholder
        from openapi_server.models.error import Error
        error_obj = Error(
            code="not_implemented",
            message=f"Controller get_animal_system_prompt implementation not found: {str(e)}",
            details={"controller": "GuardrailsController", "operation": "get_animal_system_prompt"}
        )
        return error_obj, 501

    except Exception as e:
        # Use centralized error handler if available
        try:
            from openapi_server.impl.error_handler import handle_exception_for_controllers
            return handle_exception_for_controllers(e)
        except ImportError:
            # Fallback error response
            from openapi_server.models.error import Error
            error_obj = Error(
                code="internal_error",
                message=f"Internal server error in get_animal_system_prompt: {str(e)}",
                details={"controller": "GuardrailsController", "operation": "get_animal_system_prompt"}
            )
            return error_obj, 500


def get_guardrail(guardrail_id):  # noqa: E501
    """Get specific guardrail

     # noqa: E501

    :param guardrail_id: 
    :type guardrail_id: str

    :rtype: Union[Guardrail, Tuple[Guardrail, int], Tuple[Guardrail, int, Dict[str, str]]
    """
    # Auto-generated parameter handling

    # CMZ Auto-Generated Implementation Connection
    # This template automatically connects controllers to impl modules
    try:
        # Dynamic import of implementation module based on controller name
        # Auto-detect implementation module from operationId
        impl_module_name = "guardrails_controller".replace("_controller", "")
        impl_function_name = "handle_"

        # Try common implementation patterns
        try:
            # Pattern 1: Direct module import
            impl_module = __import__(f"openapi_server.impl.{impl_module_name}", fromlist=[impl_function_name])
            impl_function = getattr(impl_module, impl_function_name)
        except (ImportError, AttributeError):
            # Pattern 2: Generic handler with hexagonal architecture routing
            from openapi_server.impl import handlers
            # Use the generic handle_ function that routes based on caller name
            impl_function = handlers.handle_
            if not impl_function:
                # Pattern 3: Default error for missing implementation
                raise NotImplementedError(
                    f"Implementation function 'handle_' not found in handlers module. "
                    f"Please ensure the following: "
                    f"1. The handlers.py file exists in the impl directory "
                    f"2. The handle_ function is defined in handlers.py "
                    f"3. The function signature matches the controller parameters"
                )

        # Call implementation function with processed parameters
        result = impl_function(guardrail_id)

        # Handle different return types
        if isinstance(result, tuple):
            return result  # Already formatted (data, status_code)
        else:
            return result, 200

    except NotImplementedError as e:
        # Development mode: return clear error instead of placeholder
        from openapi_server.models.error import Error
        error_obj = Error(
            code="not_implemented",
            message=f"Controller get_guardrail implementation not found: {str(e)}",
            details={"controller": "GuardrailsController", "operation": "get_guardrail"}
        )
        return error_obj, 501

    except Exception as e:
        # Use centralized error handler if available
        try:
            from openapi_server.impl.error_handler import handle_exception_for_controllers
            return handle_exception_for_controllers(e)
        except ImportError:
            # Fallback error response
            from openapi_server.models.error import Error
            error_obj = Error(
                code="internal_error",
                message=f"Internal server error in get_guardrail: {str(e)}",
                details={"controller": "GuardrailsController", "operation": "get_guardrail"}
            )
            return error_obj, 500


def get_guardrail_templates():  # noqa: E501
    """Get pre-built guardrail templates

     # noqa: E501


    :rtype: Union[List[GuardrailTemplate], Tuple[List[GuardrailTemplate], int], Tuple[List[GuardrailTemplate], int, Dict[str, str]]
    """
    # Auto-generated parameter handling

    # CMZ Auto-Generated Implementation Connection
    # This template automatically connects controllers to impl modules
    try:
        # Dynamic import of implementation module based on controller name
        # Auto-detect implementation module from operationId
        impl_module_name = "guardrails_controller".replace("_controller", "")
        impl_function_name = "handle_"

        # Try common implementation patterns
        try:
            # Pattern 1: Direct module import
            impl_module = __import__(f"openapi_server.impl.{impl_module_name}", fromlist=[impl_function_name])
            impl_function = getattr(impl_module, impl_function_name)
        except (ImportError, AttributeError):
            # Pattern 2: Generic handler with hexagonal architecture routing
            from openapi_server.impl import handlers
            # Use the generic handle_ function that routes based on caller name
            impl_function = handlers.handle_
            if not impl_function:
                # Pattern 3: Default error for missing implementation
                raise NotImplementedError(
                    f"Implementation function 'handle_' not found in handlers module. "
                    f"Please ensure the following: "
                    f"1. The handlers.py file exists in the impl directory "
                    f"2. The handle_ function is defined in handlers.py "
                    f"3. The function signature matches the controller parameters"
                )

        # Call implementation function with processed parameters
        result = impl_function()

        # Handle different return types
        if isinstance(result, tuple):
            return result  # Already formatted (data, status_code)
        else:
            return result, 200

    except NotImplementedError as e:
        # Development mode: return clear error instead of placeholder
        from openapi_server.models.error import Error
        error_obj = Error(
            code="not_implemented",
            message=f"Controller get_guardrail_templates implementation not found: {str(e)}",
            details={"controller": "GuardrailsController", "operation": "get_guardrail_templates"}
        )
        return error_obj, 501

    except Exception as e:
        # Use centralized error handler if available
        try:
            from openapi_server.impl.error_handler import handle_exception_for_controllers
            return handle_exception_for_controllers(e)
        except ImportError:
            # Fallback error response
            from openapi_server.models.error import Error
            error_obj = Error(
                code="internal_error",
                message=f"Internal server error in get_guardrail_templates: {str(e)}",
                details={"controller": "GuardrailsController", "operation": "get_guardrail_templates"}
            )
            return error_obj, 500


def list_guardrails(category=None, is_active=None, is_global=None):  # noqa: E501
    """List all guardrails

     # noqa: E501

    :param category: Filter by category
    :type category: str
    :param is_active: Filter by active status
    :type is_active: bool
    :param is_global: Filter by global status
    :type is_global: bool

    :rtype: Union[List[Guardrail], Tuple[List[Guardrail], int], Tuple[List[Guardrail], int, Dict[str, str]]
    """
    # Auto-generated parameter handling

    # CMZ Auto-Generated Implementation Connection
    # This template automatically connects controllers to impl modules
    try:
        # Dynamic import of implementation module based on controller name
        # Auto-detect implementation module from operationId
        impl_module_name = "guardrails_controller".replace("_controller", "")
        impl_function_name = "handle_"

        # Try common implementation patterns
        try:
            # Pattern 1: Direct module import
            impl_module = __import__(f"openapi_server.impl.{impl_module_name}", fromlist=[impl_function_name])
            impl_function = getattr(impl_module, impl_function_name)
        except (ImportError, AttributeError):
            # Pattern 2: Generic handler with hexagonal architecture routing
            from openapi_server.impl import handlers
            # Use the generic handle_ function that routes based on caller name
            impl_function = handlers.handle_
            if not impl_function:
                # Pattern 3: Default error for missing implementation
                raise NotImplementedError(
                    f"Implementation function 'handle_' not found in handlers module. "
                    f"Please ensure the following: "
                    f"1. The handlers.py file exists in the impl directory "
                    f"2. The handle_ function is defined in handlers.py "
                    f"3. The function signature matches the controller parameters"
                )

        # Call implementation function with processed parameters
        result = impl_function(category, is_active, is_global)

        # Handle different return types
        if isinstance(result, tuple):
            return result  # Already formatted (data, status_code)
        else:
            return result, 200

    except NotImplementedError as e:
        # Development mode: return clear error instead of placeholder
        from openapi_server.models.error import Error
        error_obj = Error(
            code="not_implemented",
            message=f"Controller list_guardrails implementation not found: {str(e)}",
            details={"controller": "GuardrailsController", "operation": "list_guardrails"}
        )
        return error_obj, 501

    except Exception as e:
        # Use centralized error handler if available
        try:
            from openapi_server.impl.error_handler import handle_exception_for_controllers
            return handle_exception_for_controllers(e)
        except ImportError:
            # Fallback error response
            from openapi_server.models.error import Error
            error_obj = Error(
                code="internal_error",
                message=f"Internal server error in list_guardrails: {str(e)}",
                details={"controller": "GuardrailsController", "operation": "list_guardrails"}
            )
            return error_obj, 500


def update_guardrail(guardrail_id, body):  # noqa: E501
    """Update guardrail

     # noqa: E501

    :param guardrail_id: 
    :type guardrail_id: str
    :param guardrail_update: 
    :type guardrail_update: dict | bytes

    :rtype: Union[Guardrail, Tuple[Guardrail, int], Tuple[Guardrail, int, Dict[str, str]]
    """
    # Auto-generated parameter handling
    if connexion.request.is_json:
        body = GuardrailUpdate.from_dict(connexion.request.get_json())  # noqa: E501

    # CMZ Auto-Generated Implementation Connection
    # This template automatically connects controllers to impl modules
    try:
        # Dynamic import of implementation module based on controller name
        # Auto-detect implementation module from operationId
        impl_module_name = "guardrails_controller".replace("_controller", "")
        impl_function_name = "handle_"

        # Try common implementation patterns
        try:
            # Pattern 1: Direct module import
            impl_module = __import__(f"openapi_server.impl.{impl_module_name}", fromlist=[impl_function_name])
            impl_function = getattr(impl_module, impl_function_name)
        except (ImportError, AttributeError):
            # Pattern 2: Generic handler with hexagonal architecture routing
            from openapi_server.impl import handlers
            # Use the generic handle_ function that routes based on caller name
            impl_function = handlers.handle_
            if not impl_function:
                # Pattern 3: Default error for missing implementation
                raise NotImplementedError(
                    f"Implementation function 'handle_' not found in handlers module. "
                    f"Please ensure the following: "
                    f"1. The handlers.py file exists in the impl directory "
                    f"2. The handle_ function is defined in handlers.py "
                    f"3. The function signature matches the controller parameters"
                )

        # Call implementation function with processed parameters
        result = impl_function(guardrail_id, body)

        # Handle different return types
        if isinstance(result, tuple):
            return result  # Already formatted (data, status_code)
        else:
            return result, 200

    except NotImplementedError as e:
        # Development mode: return clear error instead of placeholder
        from openapi_server.models.error import Error
        error_obj = Error(
            code="not_implemented",
            message=f"Controller update_guardrail implementation not found: {str(e)}",
            details={"controller": "GuardrailsController", "operation": "update_guardrail"}
        )
        return error_obj, 501

    except Exception as e:
        # Use centralized error handler if available
        try:
            from openapi_server.impl.error_handler import handle_exception_for_controllers
            return handle_exception_for_controllers(e)
        except ImportError:
            # Fallback error response
            from openapi_server.models.error import Error
            error_obj = Error(
                code="internal_error",
                message=f"Internal server error in update_guardrail: {str(e)}",
                details={"controller": "GuardrailsController", "operation": "update_guardrail"}
            )
            return error_obj, 500


def validate_content(body):  # noqa: E501
    """Validate content against safety guardrails

    Validates user input and AI responses against configured safety rules with real-time content moderation # noqa: E501

    :param validate_content_request: 
    :type validate_content_request: dict | bytes

    :rtype: Union[ValidateContent200Response, Tuple[ValidateContent200Response, int], Tuple[ValidateContent200Response, int, Dict[str, str]]
    """
    # Auto-generated parameter handling
    if connexion.request.is_json:
        body = ValidateContentRequest.from_dict(connexion.request.get_json())  # noqa: E501

    # CMZ Auto-Generated Implementation Connection
    # This template automatically connects controllers to impl modules
    try:
        # Dynamic import of implementation module based on controller name
        # Auto-detect implementation module from operationId
        impl_module_name = "guardrails_controller".replace("_controller", "")
        impl_function_name = "handle_"

        # Try common implementation patterns
        try:
            # Pattern 1: Direct module import
            impl_module = __import__(f"openapi_server.impl.{impl_module_name}", fromlist=[impl_function_name])
            impl_function = getattr(impl_module, impl_function_name)
        except (ImportError, AttributeError):
            # Pattern 2: Generic handler with hexagonal architecture routing
            from openapi_server.impl import handlers
            # Use the generic handle_ function that routes based on caller name
            impl_function = handlers.handle_
            if not impl_function:
                # Pattern 3: Default error for missing implementation
                raise NotImplementedError(
                    f"Implementation function 'handle_' not found in handlers module. "
                    f"Please ensure the following: "
                    f"1. The handlers.py file exists in the impl directory "
                    f"2. The handle_ function is defined in handlers.py "
                    f"3. The function signature matches the controller parameters"
                )

        # Call implementation function with processed parameters
        result = impl_function(body)

        # Handle different return types
        if isinstance(result, tuple):
            return result  # Already formatted (data, status_code)
        else:
            return result, 200

    except NotImplementedError as e:
        # Development mode: return clear error instead of placeholder
        from openapi_server.models.error import Error
        error_obj = Error(
            code="not_implemented",
            message=f"Controller validate_content implementation not found: {str(e)}",
            details={"controller": "GuardrailsController", "operation": "validate_content"}
        )
        return error_obj, 501

    except Exception as e:
        # Use centralized error handler if available
        try:
            from openapi_server.impl.error_handler import handle_exception_for_controllers
            return handle_exception_for_controllers(e)
        except ImportError:
            # Fallback error response
            from openapi_server.models.error import Error
            error_obj = Error(
                code="internal_error",
                message=f"Internal server error in validate_content: {str(e)}",
                details={"controller": "GuardrailsController", "operation": "validate_content"}
            )
            return error_obj, 500
