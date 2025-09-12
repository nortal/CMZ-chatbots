import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.auth_request import AuthRequest  # noqa: E501
from openapi_server.models.auth_response import AuthResponse  # noqa: E501
from openapi_server.models.password_reset_request import PasswordResetRequest  # noqa: E501
from openapi_server import util

from openapi_server.impl.auth import authenticate_user, refresh_jwt_token, decode_jwt_token
from openapi_server.impl.error_handler import create_error_response, AuthenticationError


def auth_logout_post():  # noqa: E501
    """Logout current user (invalidate token/session)

     # noqa: E501


    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    return 'do some magic!'


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
        
        # Extract credentials from the request
        username = auth_request.username
        password = auth_request.password
        
        # Authenticate user and get token
        auth_result = authenticate_user(username, password)
        
        # Create response using the AuthResponse model
        response = AuthResponse(
            token=auth_result['token'],
            expires_in=86400  # 24 hours in seconds
        )
        
        return response, 200
        
    except AuthenticationError as e:
        error_response = create_error_response(
            "authentication_failed",
            str(e)
        )
        return error_response, 401
        
    except Exception as e:
        error_response = create_error_response(
            "internal_error",
            "Authentication failed due to server error"
        )
        return error_response, 500


def auth_refresh_post():  # noqa: E501
    """Refresh access token

     # noqa: E501


    :rtype: Union[AuthResponse, Tuple[AuthResponse, int], Tuple[AuthResponse, int, Dict[str, str]]
    """
    return 'do some magic!'


def auth_reset_password_post(body):  # noqa: E501
    """Initiate password reset

     # noqa: E501

    :param password_reset_request: 
    :type password_reset_request: dict | bytes

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    password_reset_request = body
    if connexion.request.is_json:
        password_reset_request = PasswordResetRequest.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
