import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.error import Error  # noqa: E501
from openapi_server.models.family import Family  # noqa: E501
from openapi_server import util


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
    return 'do some magic!'


def delete_family(id):  # noqa: E501
    """Delete a family

     # noqa: E501

    :param id: 
    :type id: str

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    return 'do some magic!'


def get_family(id):  # noqa: E501
    """Get specific family by ID

     # noqa: E501

    :param id: 
    :type id: str

    :rtype: Union[Family, Tuple[Family, int], Tuple[Family, int, Dict[str, str]]
    """
    return 'do some magic!'


def list_families():  # noqa: E501
    """Get list of all families

     # noqa: E501


    :rtype: Union[List[Family], Tuple[List[Family], int], Tuple[List[Family], int, Dict[str, str]]
    """
    return 'do some magic!'


def update_family(id, body):  # noqa: E501
    """Update an existing family

     # noqa: E501

    :param id: 
    :type id: str
    :param family: 
    :type family: dict | bytes

    :rtype: Union[Family, Tuple[Family, int], Tuple[Family, int, Dict[str, str]]
    """
    family = body
    if connexion.request.is_json:
        family = Family.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
