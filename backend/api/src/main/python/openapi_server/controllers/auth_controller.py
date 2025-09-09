import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.auth_request import AuthRequest  # noqa: E501
from openapi_server.models.auth_response import AuthResponse  # noqa: E501
from openapi_server.models.error import Error  # noqa: E501
from openapi_server.models.password_reset_request import PasswordResetRequest  # noqa: E501
from openapi_server import util

# Import Cognito authentication implementation
from openapi_server.impl.cognito_authentication import create_cognito_auth_service
from openapi_server.impl.adapters.flask.cognito_auth_handlers import FlaskCognitoAuthHandler
from openapi_server.impl.adapters.flask.serializers import FlaskAuthSerializer
from openapi_server.impl.domain.common.entities import AuthCredentials
from openapi_server.impl.domain.common.exceptions import (
    ValidationError, NotFoundError, ConflictError, 
    BusinessRuleError, InvalidStateError
)

# Initialize services
_auth_service = None
_auth_handler = None

def _get_auth_handler():
    """Get initialized auth handler (lazy initialization)"""
    global _auth_service, _auth_handler
    if _auth_handler is None:
        _auth_service = create_cognito_auth_service()
        _auth_serializer = FlaskAuthSerializer()
        _auth_handler = FlaskCognitoAuthHandler(_auth_service, _auth_serializer)
    return _auth_handler


def auth_logout_post():  # noqa: E501
    """Logout current user (invalidate token/session)

     # noqa: E501


    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    try:
        handler = _get_auth_handler()
        request_data = {
            "headers": dict(connexion.request.headers),
            "json": connexion.request.get_json() if connexion.request.is_json else {}
        }
        return handler.logout(request_data)
    except Exception as e:
        return {"error": "Internal server error", "detail": str(e)}, 500


def auth_post(body):  # noqa: E501
    """Login or register

     # noqa: E501

    :param auth_request: 
    :type auth_request: dict | bytes

    :rtype: Union[AuthResponse, Tuple[AuthResponse, int], Tuple[AuthResponse, int, Dict[str, str]]
    """
    try:
        auth_request = body
        if connexion.request.is_json:
            auth_request = AuthRequest.from_dict(connexion.request.get_json())  # noqa: E501
        
        handler = _get_auth_handler()
        return handler.authenticate({"json": auth_request})
        
    except ValidationError as e:
        return {"error": "Validation error", "detail": str(e)}, 400
    except ConflictError as e:
        return {"error": "Conflict", "detail": str(e)}, 409
    except NotFoundError as e:
        return {"error": "Not found", "detail": str(e)}, 404
    except BusinessRuleError as e:
        return {"error": "Authentication failed", "detail": str(e)}, 401
    except Exception as e:
        return {"error": "Internal server error", "detail": str(e)}, 500


def auth_refresh_post():  # noqa: E501
    """Refresh access token

     # noqa: E501


    :rtype: Union[AuthResponse, Tuple[AuthResponse, int], Tuple[AuthResponse, int, Dict[str, str]]
    """
    try:
        handler = _get_auth_handler()
        request_data = {
            "headers": dict(connexion.request.headers),
            "json": connexion.request.get_json() if connexion.request.is_json else {}
        }
        return handler.refresh_token(request_data)
        
    except ValidationError as e:
        return {"error": "Validation error", "detail": str(e)}, 400
    except BusinessRuleError as e:
        return {"error": "Token refresh failed", "detail": str(e)}, 401
    except Exception as e:
        return {"error": "Internal server error", "detail": str(e)}, 500


def auth_reset_password_post(body):  # noqa: E501
    """Initiate password reset

     # noqa: E501

    :param password_reset_request: 
    :type password_reset_request: dict | bytes

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    try:
        password_reset_request = body
        if connexion.request.is_json:
            password_reset_request = PasswordResetRequest.from_dict(connexion.request.get_json())  # noqa: E501
        
        handler = _get_auth_handler()
        request_data = {"json": password_reset_request}
        return handler.initiate_password_reset(request_data)
        
    except ValidationError as e:
        return {"error": "Validation error", "detail": str(e)}, 400
    except NotFoundError as e:
        return {"error": "User not found", "detail": str(e)}, 404
    except Exception as e:
        return {"error": "Internal server error", "detail": str(e)}, 500
