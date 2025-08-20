import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.auth_request import AuthRequest  # noqa: E501
from openapi_server.models.auth_response import AuthResponse  # noqa: E501
from openapi_server.models.error import Error  # noqa: E501
from openapi_server.models.password_reset_request import PasswordResetRequest  # noqa: E501
from openapi_server import util


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
    auth_request = body
    if connexion.request.is_json:
        auth_request = AuthRequest.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


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
