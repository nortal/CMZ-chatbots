import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.error import Error  # noqa: E501
from openapi_server.models.family import Family  # noqa: E501
from openapi_server import util

from openapi_server.impl.family import (
    handle_list_families,
    handle_create_family,
    handle_get_family,
    handle_update_family,
    handle_delete_family,
)

def create_family(body):  # noqa: E501
    """Create a new family

     # noqa: E501

    :param family: 
    :type family: dict | bytes

    :rtype: Union[Family, Tuple[Family, int], Tuple[Family, int, Dict[str, str]]
    """
    family = body
    if connexion.request.is_json:
        family = Family.from_dict(connexion.request.get_json())  # noqa: E501
    return handle_create_family(family)


def delete_family(family_id):  # noqa: E501
    """Delete a family

     # noqa: E501

    :param family_id: 
    :type family_id: str

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    return handle_delete_family(family_id)


def get_family(family_id):  # noqa: E501
    """Get specific family by ID

     # noqa: E501

    :param family_id: 
    :type family_id: str

    :rtype: Union[Family, Tuple[Family, int], Tuple[Family, int, Dict[str, str]]
    """
    return handle_get_family(family_id)


def list_families():  # noqa: E501
    """Get list of all families

     # noqa: E501


    :rtype: Union[List[Family], Tuple[List[Family], int], Tuple[List[Family], int, Dict[str, str]]
    """
    return handle_list_families()


def update_family(family_id, body):  # noqa: E501
    """Update an existing family

     # noqa: E501

    :param family_id: 
    :type family_id: str
    :param family: 
    :type family: dict | bytes

    :rtype: Union[Family, Tuple[Family, int], Tuple[Family, int, Dict[str, str]]
    """
    family = body
    if connexion.request.is_json:
        family = Family.from_dict(connexion.request.get_json())  # noqa: E501
    return handle_update_family(family_id, family)
