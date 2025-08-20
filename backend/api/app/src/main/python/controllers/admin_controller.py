import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.error import Error  # noqa: E501
from openapi_server.models.paged_users import PagedUsers  # noqa: E501
from openapi_server.models.user import User  # noqa: E501
from openapi_server.models.user_details import UserDetails  # noqa: E501
from openapi_server.models.userrole_patch_request import UserrolePatchRequest  # noqa: E501
from openapi_server import util


def user_delete(id):  # noqa: E501
    """Delete user

     # noqa: E501

    :param id: 
    :type id: str

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    return 'do some magic!'


def userdetails_get(id):  # noqa: E501
    """Fetch specific user details

     # noqa: E501

    :param id: 
    :type id: str

    :rtype: Union[UserDetails, Tuple[UserDetails, int], Tuple[UserDetails, int, Dict[str, str]]
    """
    return 'do some magic!'


def userlist_get(details=None, role=None, page=None, page_size=None):  # noqa: E501
    """List users

     # noqa: E501

    :param details: 
    :type details: bool
    :param role: 
    :type role: str
    :param page: 
    :type page: int
    :param page_size: 
    :type page_size: int

    :rtype: Union[PagedUsers, Tuple[PagedUsers, int], Tuple[PagedUsers, int, Dict[str, str]]
    """
    return 'do some magic!'


def userrole_patch(body):  # noqa: E501
    """Change user role

     # noqa: E501

    :param userrole_patch_request: 
    :type userrole_patch_request: dict | bytes

    :rtype: Union[User, Tuple[User, int], Tuple[User, int, Dict[str, str]]
    """
    userrole_patch_request = body
    if connexion.request.is_json:
        userrole_patch_request = UserrolePatchRequest.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
