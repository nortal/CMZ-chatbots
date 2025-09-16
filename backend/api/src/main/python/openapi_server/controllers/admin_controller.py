import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.controllers import util


 block to insert a comma between parameters except after the last one. }}
def create_user(user_input):  # noqa: E501
    """Create a new user

    :param user_input: 
    :type user_input:  | bytes

    :rtype: Union[User, Tuple[User, int], Tuple[User, int, Dict[str, str]]]
    """
    # Auto-generated parameter handling
    if connexion.request.is_json:
        user_input = UserInput.from_dict(connexion.request.get_json())  # noqa: E501

    # CMZ Auto-Generated Implementation Connection
    # This template automatically connects controllers to impl modules
    try:
        # Dynamic import of implementation module based on controller name
        # Auto-detect implementation module from operationId
        impl_module_name = "admincontroller".replace("_controller", "")
        impl_function_name = "handle_"

        # Try common implementation patterns
        try:
            # Pattern 1: Direct module import
            impl_module = __import__(f"openapi_server.controllers.impl.{impl_module_name}", fromlist=[impl_function_name])
            impl_function = getattr(impl_module, impl_function_name)
        except (ImportError, AttributeError):
            # Pattern 2: Generic handler with hexagonal architecture routing
            from openapi_server.controllers.impl import handlers
            # Use the generic handle_ function that routes based on caller name
            impl_function = handlers.handle_
            if not impl_function:
                # Pattern 3: Default error for missing implementation
                raise NotImplementedError(f"Implementation function 'handle_' not found in handlers module")

        # Call implementation function with processed parameters
        result = impl_function(user_input)

        # Handle different return types
        if isinstance(result, tuple):
            return result  # Already formatted (data, status_code)
        else:
            return result, 201

    except NotImplementedError as e:
        # Development mode: return clear error instead of placeholder
        from openapi_server.controllers.models.error import Error
        error_obj = Error(
            code="not_implemented",
            message=f"Controller create_user implementation not found: {str(e)}",
            details={"controller": "AdminController", "operation": "create_user"}
        )
        return error_obj, 501

    except Exception as e:
        # Use centralized error handler if available
        try:
            from openapi_server.controllers.impl.error_handler import handle_exception_for_controllers
            return handle_exception_for_controllers(e)
        except ImportError:
            # Fallback error response
            from openapi_server.controllers.models.error import Error
            error_obj = Error(
                code="internal_error",
                message=f"Internal server error in create_user: {str(e)}",
                details={"controller": "AdminController", "operation": "create_user"}
            )
            return error_obj, 500


 block to insert a comma between parameters except after the last one. }}
def create_user_details(user_details_input):  # noqa: E501
    """Create user details

    :param user_details_input: 
    :type user_details_input:  | bytes

    :rtype: Union[UserDetails, Tuple[UserDetails, int], Tuple[UserDetails, int, Dict[str, str]]]
    """
    # Auto-generated parameter handling
    if connexion.request.is_json:
        user_details_input = UserDetailsInput.from_dict(connexion.request.get_json())  # noqa: E501

    # CMZ Auto-Generated Implementation Connection
    # This template automatically connects controllers to impl modules
    try:
        # Dynamic import of implementation module based on controller name
        # Auto-detect implementation module from operationId
        impl_module_name = "admincontroller".replace("_controller", "")
        impl_function_name = "handle_"

        # Try common implementation patterns
        try:
            # Pattern 1: Direct module import
            impl_module = __import__(f"openapi_server.controllers.impl.{impl_module_name}", fromlist=[impl_function_name])
            impl_function = getattr(impl_module, impl_function_name)
        except (ImportError, AttributeError):
            # Pattern 2: Generic handler with hexagonal architecture routing
            from openapi_server.controllers.impl import handlers
            # Use the generic handle_ function that routes based on caller name
            impl_function = handlers.handle_
            if not impl_function:
                # Pattern 3: Default error for missing implementation
                raise NotImplementedError(f"Implementation function 'handle_' not found in handlers module")

        # Call implementation function with processed parameters
        result = impl_function(user_details_input)

        # Handle different return types
        if isinstance(result, tuple):
            return result  # Already formatted (data, status_code)
        else:
            return result, 201

    except NotImplementedError as e:
        # Development mode: return clear error instead of placeholder
        from openapi_server.controllers.models.error import Error
        error_obj = Error(
            code="not_implemented",
            message=f"Controller create_user_details implementation not found: {str(e)}",
            details={"controller": "AdminController", "operation": "create_user_details"}
        )
        return error_obj, 501

    except Exception as e:
        # Use centralized error handler if available
        try:
            from openapi_server.controllers.impl.error_handler import handle_exception_for_controllers
            return handle_exception_for_controllers(e)
        except ImportError:
            # Fallback error response
            from openapi_server.controllers.models.error import Error
            error_obj = Error(
                code="internal_error",
                message=f"Internal server error in create_user_details: {str(e)}",
                details={"controller": "AdminController", "operation": "create_user_details"}
            )
            return error_obj, 500


 block to insert a comma between parameters except after the last one. }}
def delete_user(user_id):  # noqa: E501
    """Delete user

    :param user_id: 
    :type user_id: strstr | bytes

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]]
    """
    # Auto-generated parameter handling

    # CMZ Auto-Generated Implementation Connection
    # This template automatically connects controllers to impl modules
    try:
        # Dynamic import of implementation module based on controller name
        # Auto-detect implementation module from operationId
        impl_module_name = "admincontroller".replace("_controller", "")
        impl_function_name = "handle_"

        # Try common implementation patterns
        try:
            # Pattern 1: Direct module import
            impl_module = __import__(f"openapi_server.controllers.impl.{impl_module_name}", fromlist=[impl_function_name])
            impl_function = getattr(impl_module, impl_function_name)
        except (ImportError, AttributeError):
            # Pattern 2: Generic handler with hexagonal architecture routing
            from openapi_server.controllers.impl import handlers
            # Use the generic handle_ function that routes based on caller name
            impl_function = handlers.handle_
            if not impl_function:
                # Pattern 3: Default error for missing implementation
                raise NotImplementedError(f"Implementation function 'handle_' not found in handlers module")

        # Call implementation function with processed parameters
        result = impl_function(user_id)

        # Handle different return types
        if isinstance(result, tuple):
            return result  # Already formatted (data, status_code)
        else:
            return result, 204

    except NotImplementedError as e:
        # Development mode: return clear error instead of placeholder
        from openapi_server.controllers.models.error import Error
        error_obj = Error(
            code="not_implemented",
            message=f"Controller delete_user implementation not found: {str(e)}",
            details={"controller": "AdminController", "operation": "delete_user"}
        )
        return error_obj, 501

    except Exception as e:
        # Use centralized error handler if available
        try:
            from openapi_server.controllers.impl.error_handler import handle_exception_for_controllers
            return handle_exception_for_controllers(e)
        except ImportError:
            # Fallback error response
            from openapi_server.controllers.models.error import Error
            error_obj = Error(
                code="internal_error",
                message=f"Internal server error in delete_user: {str(e)}",
                details={"controller": "AdminController", "operation": "delete_user"}
            )
            return error_obj, 500


 block to insert a comma between parameters except after the last one. }}
def delete_user_details(user_id):  # noqa: E501
    """Delete user details

    :param user_id: 
    :type user_id: strstr | bytes

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]]
    """
    # Auto-generated parameter handling

    # CMZ Auto-Generated Implementation Connection
    # This template automatically connects controllers to impl modules
    try:
        # Dynamic import of implementation module based on controller name
        # Auto-detect implementation module from operationId
        impl_module_name = "admincontroller".replace("_controller", "")
        impl_function_name = "handle_"

        # Try common implementation patterns
        try:
            # Pattern 1: Direct module import
            impl_module = __import__(f"openapi_server.controllers.impl.{impl_module_name}", fromlist=[impl_function_name])
            impl_function = getattr(impl_module, impl_function_name)
        except (ImportError, AttributeError):
            # Pattern 2: Generic handler with hexagonal architecture routing
            from openapi_server.controllers.impl import handlers
            # Use the generic handle_ function that routes based on caller name
            impl_function = handlers.handle_
            if not impl_function:
                # Pattern 3: Default error for missing implementation
                raise NotImplementedError(f"Implementation function 'handle_' not found in handlers module")

        # Call implementation function with processed parameters
        result = impl_function(user_id)

        # Handle different return types
        if isinstance(result, tuple):
            return result  # Already formatted (data, status_code)
        else:
            return result, 204

    except NotImplementedError as e:
        # Development mode: return clear error instead of placeholder
        from openapi_server.controllers.models.error import Error
        error_obj = Error(
            code="not_implemented",
            message=f"Controller delete_user_details implementation not found: {str(e)}",
            details={"controller": "AdminController", "operation": "delete_user_details"}
        )
        return error_obj, 501

    except Exception as e:
        # Use centralized error handler if available
        try:
            from openapi_server.controllers.impl.error_handler import handle_exception_for_controllers
            return handle_exception_for_controllers(e)
        except ImportError:
            # Fallback error response
            from openapi_server.controllers.models.error import Error
            error_obj = Error(
                code="internal_error",
                message=f"Internal server error in delete_user_details: {str(e)}",
                details={"controller": "AdminController", "operation": "delete_user_details"}
            )
            return error_obj, 500


 block to insert a comma between parameters except after the last one. }}
def get_user(user_id):  # noqa: E501
    """Get user by ID

    :param user_id: 
    :type user_id: strstr | bytes

    :rtype: Union[User, Tuple[User, int], Tuple[User, int, Dict[str, str]]]
    """
    # Auto-generated parameter handling

    # CMZ Auto-Generated Implementation Connection
    # This template automatically connects controllers to impl modules
    try:
        # Dynamic import of implementation module based on controller name
        # Auto-detect implementation module from operationId
        impl_module_name = "admincontroller".replace("_controller", "")
        impl_function_name = "handle_"

        # Try common implementation patterns
        try:
            # Pattern 1: Direct module import
            impl_module = __import__(f"openapi_server.controllers.impl.{impl_module_name}", fromlist=[impl_function_name])
            impl_function = getattr(impl_module, impl_function_name)
        except (ImportError, AttributeError):
            # Pattern 2: Generic handler with hexagonal architecture routing
            from openapi_server.controllers.impl import handlers
            # Use the generic handle_ function that routes based on caller name
            impl_function = handlers.handle_
            if not impl_function:
                # Pattern 3: Default error for missing implementation
                raise NotImplementedError(f"Implementation function 'handle_' not found in handlers module")

        # Call implementation function with processed parameters
        result = impl_function(user_id)

        # Handle different return types
        if isinstance(result, tuple):
            return result  # Already formatted (data, status_code)
        else:
            return result, 200

    except NotImplementedError as e:
        # Development mode: return clear error instead of placeholder
        from openapi_server.controllers.models.error import Error
        error_obj = Error(
            code="not_implemented",
            message=f"Controller get_user implementation not found: {str(e)}",
            details={"controller": "AdminController", "operation": "get_user"}
        )
        return error_obj, 501

    except Exception as e:
        # Use centralized error handler if available
        try:
            from openapi_server.controllers.impl.error_handler import handle_exception_for_controllers
            return handle_exception_for_controllers(e)
        except ImportError:
            # Fallback error response
            from openapi_server.controllers.models.error import Error
            error_obj = Error(
                code="internal_error",
                message=f"Internal server error in get_user: {str(e)}",
                details={"controller": "AdminController", "operation": "get_user"}
            )
            return error_obj, 500


 block to insert a comma between parameters except after the last one. }}
def get_user_details(user_id):  # noqa: E501
    """Get user details by ID

    :param user_id: 
    :type user_id: strstr | bytes

    :rtype: Union[UserDetails, Tuple[UserDetails, int], Tuple[UserDetails, int, Dict[str, str]]]
    """
    # Auto-generated parameter handling

    # CMZ Auto-Generated Implementation Connection
    # This template automatically connects controllers to impl modules
    try:
        # Dynamic import of implementation module based on controller name
        # Auto-detect implementation module from operationId
        impl_module_name = "admincontroller".replace("_controller", "")
        impl_function_name = "handle_"

        # Try common implementation patterns
        try:
            # Pattern 1: Direct module import
            impl_module = __import__(f"openapi_server.controllers.impl.{impl_module_name}", fromlist=[impl_function_name])
            impl_function = getattr(impl_module, impl_function_name)
        except (ImportError, AttributeError):
            # Pattern 2: Generic handler with hexagonal architecture routing
            from openapi_server.controllers.impl import handlers
            # Use the generic handle_ function that routes based on caller name
            impl_function = handlers.handle_
            if not impl_function:
                # Pattern 3: Default error for missing implementation
                raise NotImplementedError(f"Implementation function 'handle_' not found in handlers module")

        # Call implementation function with processed parameters
        result = impl_function(user_id)

        # Handle different return types
        if isinstance(result, tuple):
            return result  # Already formatted (data, status_code)
        else:
            return result, 200

    except NotImplementedError as e:
        # Development mode: return clear error instead of placeholder
        from openapi_server.controllers.models.error import Error
        error_obj = Error(
            code="not_implemented",
            message=f"Controller get_user_details implementation not found: {str(e)}",
            details={"controller": "AdminController", "operation": "get_user_details"}
        )
        return error_obj, 501

    except Exception as e:
        # Use centralized error handler if available
        try:
            from openapi_server.controllers.impl.error_handler import handle_exception_for_controllers
            return handle_exception_for_controllers(e)
        except ImportError:
            # Fallback error response
            from openapi_server.controllers.models.error import Error
            error_obj = Error(
                code="internal_error",
                message=f"Internal server error in get_user_details: {str(e)}",
                details={"controller": "AdminController", "operation": "get_user_details"}
            )
            return error_obj, 500


 block to insert a comma between parameters except after the last one. }}
def list_user_details():  # noqa: E501
    """Get list of all user details

    :rtype: Union[List[UserDetails], Tuple[List[UserDetails], int], Tuple[List[UserDetails], int, Dict[str, str]]]
    """
    # CMZ Auto-Generated Implementation Connection
    # This template automatically connects controllers to impl modules
    try:
        # Dynamic import of implementation module based on controller name
        # Auto-detect implementation module from operationId
        impl_module_name = "admincontroller".replace("_controller", "")
        impl_function_name = "handle_"

        # Try common implementation patterns
        try:
            # Pattern 1: Direct module import
            impl_module = __import__(f"openapi_server.controllers.impl.{impl_module_name}", fromlist=[impl_function_name])
            impl_function = getattr(impl_module, impl_function_name)
        except (ImportError, AttributeError):
            # Pattern 2: Generic handler with hexagonal architecture routing
            from openapi_server.controllers.impl import handlers
            # Use the generic handle_ function that routes based on caller name
            impl_function = handlers.handle_
            if not impl_function:
                # Pattern 3: Default error for missing implementation
                raise NotImplementedError(f"Implementation function 'handle_' not found in handlers module")

        # Call implementation function with processed parameters
        result = impl_function()

        # Handle different return types
        if isinstance(result, tuple):
            return result  # Already formatted (data, status_code)
        else:
            return result, 200

    except NotImplementedError as e:
        # Development mode: return clear error instead of placeholder
        from openapi_server.controllers.models.error import Error
        error_obj = Error(
            code="not_implemented",
            message=f"Controller list_user_details implementation not found: {str(e)}",
            details={"controller": "AdminController", "operation": "list_user_details"}
        )
        return error_obj, 501

    except Exception as e:
        # Use centralized error handler if available
        try:
            from openapi_server.controllers.impl.error_handler import handle_exception_for_controllers
            return handle_exception_for_controllers(e)
        except ImportError:
            # Fallback error response
            from openapi_server.controllers.models.error import Error
            error_obj = Error(
                code="internal_error",
                message=f"Internal server error in list_user_details: {str(e)}",
                details={"controller": "AdminController", "operation": "list_user_details"}
            )
            return error_obj, 500


 block to insert a comma between parameters except after the last one. }}
def list_users():  # noqa: E501
    """Get list of all users

    :rtype: Union[PagedUsers, Tuple[PagedUsers, int], Tuple[PagedUsers, int, Dict[str, str]]]
    """
    # CMZ Auto-Generated Implementation Connection
    # This template automatically connects controllers to impl modules
    try:
        # Dynamic import of implementation module based on controller name
        # Auto-detect implementation module from operationId
        impl_module_name = "admincontroller".replace("_controller", "")
        impl_function_name = "handle_"

        # Try common implementation patterns
        try:
            # Pattern 1: Direct module import
            impl_module = __import__(f"openapi_server.controllers.impl.{impl_module_name}", fromlist=[impl_function_name])
            impl_function = getattr(impl_module, impl_function_name)
        except (ImportError, AttributeError):
            # Pattern 2: Generic handler with hexagonal architecture routing
            from openapi_server.controllers.impl import handlers
            # Use the generic handle_ function that routes based on caller name
            impl_function = handlers.handle_
            if not impl_function:
                # Pattern 3: Default error for missing implementation
                raise NotImplementedError(f"Implementation function 'handle_' not found in handlers module")

        # Call implementation function with processed parameters
        result = impl_function()

        # Handle different return types
        if isinstance(result, tuple):
            return result  # Already formatted (data, status_code)
        else:
            return result, 200

    except NotImplementedError as e:
        # Development mode: return clear error instead of placeholder
        from openapi_server.controllers.models.error import Error
        error_obj = Error(
            code="not_implemented",
            message=f"Controller list_users implementation not found: {str(e)}",
            details={"controller": "AdminController", "operation": "list_users"}
        )
        return error_obj, 501

    except Exception as e:
        # Use centralized error handler if available
        try:
            from openapi_server.controllers.impl.error_handler import handle_exception_for_controllers
            return handle_exception_for_controllers(e)
        except ImportError:
            # Fallback error response
            from openapi_server.controllers.models.error import Error
            error_obj = Error(
                code="internal_error",
                message=f"Internal server error in list_users: {str(e)}",
                details={"controller": "AdminController", "operation": "list_users"}
            )
            return error_obj, 500


 block to insert a comma between parameters except after the last one. }}
def update_user(user_id, user):  # noqa: E501
    """Update a user

    :param user_id: 
    :type user_id: strstr | bytes

    :param user: 
    :type user:  | bytes

    :rtype: Union[User, Tuple[User, int], Tuple[User, int, Dict[str, str]]]
    """
    # Auto-generated parameter handling
    if connexion.request.is_json:
        user = User.from_dict(connexion.request.get_json())  # noqa: E501

    # CMZ Auto-Generated Implementation Connection
    # This template automatically connects controllers to impl modules
    try:
        # Dynamic import of implementation module based on controller name
        # Auto-detect implementation module from operationId
        impl_module_name = "admincontroller".replace("_controller", "")
        impl_function_name = "handle_"

        # Try common implementation patterns
        try:
            # Pattern 1: Direct module import
            impl_module = __import__(f"openapi_server.controllers.impl.{impl_module_name}", fromlist=[impl_function_name])
            impl_function = getattr(impl_module, impl_function_name)
        except (ImportError, AttributeError):
            # Pattern 2: Generic handler with hexagonal architecture routing
            from openapi_server.controllers.impl import handlers
            # Use the generic handle_ function that routes based on caller name
            impl_function = handlers.handle_
            if not impl_function:
                # Pattern 3: Default error for missing implementation
                raise NotImplementedError(f"Implementation function 'handle_' not found in handlers module")

        # Call implementation function with processed parameters
        result = impl_function(user_iduser)

        # Handle different return types
        if isinstance(result, tuple):
            return result  # Already formatted (data, status_code)
        else:
            return result, 200

    except NotImplementedError as e:
        # Development mode: return clear error instead of placeholder
        from openapi_server.controllers.models.error import Error
        error_obj = Error(
            code="not_implemented",
            message=f"Controller update_user implementation not found: {str(e)}",
            details={"controller": "AdminController", "operation": "update_user"}
        )
        return error_obj, 501

    except Exception as e:
        # Use centralized error handler if available
        try:
            from openapi_server.controllers.impl.error_handler import handle_exception_for_controllers
            return handle_exception_for_controllers(e)
        except ImportError:
            # Fallback error response
            from openapi_server.controllers.models.error import Error
            error_obj = Error(
                code="internal_error",
                message=f"Internal server error in update_user: {str(e)}",
                details={"controller": "AdminController", "operation": "update_user"}
            )
            return error_obj, 500


 block to insert a comma between parameters except after the last one. }}
def update_user_details(user_id, user_details_input):  # noqa: E501
    """Update user details

    :param user_id: 
    :type user_id: strstr | bytes

    :param user_details_input: 
    :type user_details_input:  | bytes

    :rtype: Union[UserDetails, Tuple[UserDetails, int], Tuple[UserDetails, int, Dict[str, str]]]
    """
    # Auto-generated parameter handling
    if connexion.request.is_json:
        user_details_input = UserDetailsInput.from_dict(connexion.request.get_json())  # noqa: E501

    # CMZ Auto-Generated Implementation Connection
    # This template automatically connects controllers to impl modules
    try:
        # Dynamic import of implementation module based on controller name
        # Auto-detect implementation module from operationId
        impl_module_name = "admincontroller".replace("_controller", "")
        impl_function_name = "handle_"

        # Try common implementation patterns
        try:
            # Pattern 1: Direct module import
            impl_module = __import__(f"openapi_server.controllers.impl.{impl_module_name}", fromlist=[impl_function_name])
            impl_function = getattr(impl_module, impl_function_name)
        except (ImportError, AttributeError):
            # Pattern 2: Generic handler with hexagonal architecture routing
            from openapi_server.controllers.impl import handlers
            # Use the generic handle_ function that routes based on caller name
            impl_function = handlers.handle_
            if not impl_function:
                # Pattern 3: Default error for missing implementation
                raise NotImplementedError(f"Implementation function 'handle_' not found in handlers module")

        # Call implementation function with processed parameters
        result = impl_function(user_iduser_details_input)

        # Handle different return types
        if isinstance(result, tuple):
            return result  # Already formatted (data, status_code)
        else:
            return result, 200

    except NotImplementedError as e:
        # Development mode: return clear error instead of placeholder
        from openapi_server.controllers.models.error import Error
        error_obj = Error(
            code="not_implemented",
            message=f"Controller update_user_details implementation not found: {str(e)}",
            details={"controller": "AdminController", "operation": "update_user_details"}
        )
        return error_obj, 501

    except Exception as e:
        # Use centralized error handler if available
        try:
            from openapi_server.controllers.impl.error_handler import handle_exception_for_controllers
            return handle_exception_for_controllers(e)
        except ImportError:
            # Fallback error response
            from openapi_server.controllers.models.error import Error
            error_obj = Error(
                code="internal_error",
                message=f"Internal server error in update_user_details: {str(e)}",
                details={"controller": "AdminController", "operation": "update_user_details"}
            )
            return error_obj, 500


