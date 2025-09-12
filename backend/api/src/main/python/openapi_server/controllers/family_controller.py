import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.family import Family  # noqa: E501
from openapi_server import util


def create_family(body):  # noqa: E501
    """Create a new family

     # noqa: E501

    :param family: 
    :type family: dict | bytes

    :rtype: Union[Family, Tuple[Family, int], Tuple[Family, int, Dict[str, str]]
    """
    from openapi_server.impl.family import handle_create_family
    
    family = body
    if connexion.request.is_json:
        family = Family.from_dict(connexion.request.get_json())  # noqa: E501
    
    try:
        result, status_code = handle_create_family(family)
        return result, status_code
    except ValueError as e:
        from openapi_server.impl.error_handler import create_error_response
        return create_error_response("validation_error", str(e)), 400
    except Exception as e:
        from openapi_server.impl.error_handler import create_error_response
        return create_error_response("server_error", "Failed to create family"), 500


def delete_family(family_id):  # noqa: E501
    """Delete a family

     # noqa: E501

    :param family_id: 
    :type family_id: str

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    return 'do some magic!'


def get_family(family_id):  # noqa: E501
    """Get specific family by ID

     # noqa: E501

    :param family_id: 
    :type family_id: str

    :rtype: Union[Family, Tuple[Family, int], Tuple[Family, int, Dict[str, str]]
    """
    return 'do some magic!'


def list_families():  # noqa: E501
    """Get list of all families

     # noqa: E501


    :rtype: Union[List[Family], Tuple[List[Family], int], Tuple[List[Family], int, Dict[str, str]]
    """
    return 'do some magic!'


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
    return 'do some magic!'
