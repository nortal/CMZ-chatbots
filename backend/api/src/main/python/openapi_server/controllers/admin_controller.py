import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.error import Error  # noqa: E501
from openapi_server.models.paged_users import PagedUsers  # noqa: E501
from openapi_server.models.user import User  # noqa: E501
from openapi_server.models.user_details import UserDetails  # noqa: E501
from openapi_server.models.user_details_input import UserDetailsInput  # noqa: E501
from openapi_server.models.user_input import UserInput  # noqa: E501
from openapi_server import util

from openapi_server.impl.admin import (
    handle_create_user,
    handle_create_user_details,
    handle_delete_user,
    handle_delete_user_details,
    handle_get_user,
    handle_get_user_details,
    handle_list_user_details,
    handle_list_users,
    handle_update_user,
    handle_update_user_details,
)


def create_user(body):  # noqa: E501
    """Create a new user

     # noqa: E501

    :param user_input: 
    :type user_input: dict | bytes

    :rtype: Union[User, Tuple[User, int], Tuple[User, int, Dict[str, str]]
    """
    user_input = body
    if connexion.request.is_json:
        user_input = UserInput.from_dict(connexion.request.get_json())  # noqa: E501
    return handle_create_user(user_input)


def create_user_details(body):  # noqa: E501
    """Create user details

     # noqa: E501

    :param user_details_input: 
    :type user_details_input: dict | bytes

    :rtype: Union[UserDetails, Tuple[UserDetails, int], Tuple[UserDetails, int, Dict[str, str]]
    """
    user_details_input = body
    if connexion.request.is_json:
        user_details_input = UserDetailsInput.from_dict(connexion.request.get_json())  # noqa: E501
    return handle_create_user_details(user_details_input)


def delete_user(user_id):  # noqa: E501
    """Delete user

     # noqa: E501

    :param user_id: 
    :type user_id: str

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    return handle_delete_user(user_id)


def delete_user_details(user_id):  # noqa: E501
    """Delete user details

     # noqa: E501

    :param user_id: 
    :type user_id: str

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    return handle_delete_user_details(user_id)


def get_user(user_id):  # noqa: E501
    """Get user by ID

     # noqa: E501

    :param user_id: 
    :type user_id: str

    :rtype: Union[User, Tuple[User, int], Tuple[User, int, Dict[str, str]]
    """
    return handle_get_user(user_id)


def get_user_details(user_id):  # noqa: E501
    """Get user details by ID

     # noqa: E501

    :param user_id: 
    :type user_id: str

    :rtype: Union[UserDetails, Tuple[UserDetails, int], Tuple[UserDetails, int, Dict[str, str]]
    """
    return handle_get_user_details(user_id)


def list_user_details():  # noqa: E501
    """Get list of all user details

     # noqa: E501


    :rtype: Union[List[UserDetails], Tuple[List[UserDetails], int], Tuple[List[UserDetails], int, Dict[str, str]]
    """
    return handle_list_user_details()


def list_users():  # noqa: E501
    """Get list of all users

     # noqa: E501


    :rtype: Union[PagedUsers, Tuple[PagedUsers, int], Tuple[PagedUsers, int, Dict[str, str]]
    """
    return handle_list_users()


def update_user(user_id, body):  # noqa: E501
    """Update a user

     # noqa: E501

    :param user_id: 
    :type user_id: str
    :param user: 
    :type user: dict | bytes

    :rtype: Union[User, Tuple[User, int], Tuple[User, int, Dict[str, str]]
    """
    user = body
    if connexion.request.is_json:
        user = User.from_dict(connexion.request.get_json())  # noqa: E501
    return handle_update_user(user_id, user)


def update_user_details(user_id, body):  # noqa: E501
    """Update user details

     # noqa: E501

    :param user_id: 
    :type user_id: str
    :param user_details_input: 
    :type user_details_input: dict | bytes

    :rtype: Union[UserDetails, Tuple[UserDetails, int], Tuple[UserDetails, int, Dict[str, str]]
    """
    user_details_input = body
    if connexion.request.is_json:
        user_details_input = UserDetailsInput.from_dict(connexion.request.get_json())  # noqa: E501
    return handle_update_user_details(user_id, user_details_input)
