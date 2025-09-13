import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.animal import Animal  # noqa: E501
from openapi_server.models.animal_config import AnimalConfig  # noqa: E501
from openapi_server.models.animal_config_update import AnimalConfigUpdate  # noqa: E501
from openapi_server.models.animal_details import AnimalDetails  # noqa: E501
from openapi_server.models.animal_input import AnimalInput  # noqa: E501
from openapi_server.models.animal_update import AnimalUpdate  # noqa: E501
from openapi_server.models.error import Error  # noqa: E501
from openapi_server import util


def animal_config_get(animal_id):  # noqa: E501
    """Get animal configuration

     # noqa: E501

    :param animal_id: 
    :type animal_id: str

    :rtype: Union[AnimalConfig, Tuple[AnimalConfig, int], Tuple[AnimalConfig, int, Dict[str, str]]
    """
    return 'do some magic!'


def animal_config_patch(animal_id, body):  # noqa: E501
    """Update animal configuration

     # noqa: E501

    :param animal_id: 
    :type animal_id: str
    :param animal_config_update: 
    :type animal_config_update: dict | bytes

    :rtype: Union[AnimalConfig, Tuple[AnimalConfig, int], Tuple[AnimalConfig, int, Dict[str, str]]
    """
    animal_config_update = body
    if connexion.request.is_json:
        animal_config_update = AnimalConfigUpdate.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def animal_details_get(animal_id):  # noqa: E501
    """Fetch animal details

     # noqa: E501

    :param animal_id: 
    :type animal_id: str

    :rtype: Union[AnimalDetails, Tuple[AnimalDetails, int], Tuple[AnimalDetails, int, Dict[str, str]]
    """
    return 'do some magic!'


def animal_id_delete(id):  # noqa: E501
    """Delete an animal (soft delete)

     # noqa: E501

    :param id: 
    :type id: str

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    return 'do some magic!'


def animal_id_get(id):  # noqa: E501
    """Get a specific animal by ID

     # noqa: E501

    :param id: 
    :type id: str

    :rtype: Union[Animal, Tuple[Animal, int], Tuple[Animal, int, Dict[str, str]]
    """
    return 'do some magic!'


def animal_id_put(id, body):  # noqa: E501
    """Update an existing animal

     # noqa: E501

    :param id: 
    :type id: str
    :param animal_update: 
    :type animal_update: dict | bytes

    :rtype: Union[Animal, Tuple[Animal, int], Tuple[Animal, int, Dict[str, str]]
    """
    animal_update = body
    if connexion.request.is_json:
        animal_update = AnimalUpdate.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def animal_list_get(status=None):  # noqa: E501
    """List animals

     # noqa: E501

    :param status: Filter animals by status
    :type status: str

    :rtype: Union[List[Animal], Tuple[List[Animal], int], Tuple[List[Animal], int, Dict[str, str]]
    """
    return 'do some magic!'


def animal_post(body):  # noqa: E501
    """Create a new animal

     # noqa: E501

    :param animal_input: 
    :type animal_input: dict | bytes

    :rtype: Union[Animal, Tuple[Animal, int], Tuple[Animal, int, Dict[str, str]]
    """
    animal_input = body
    if connexion.request.is_json:
        animal_input = AnimalInput.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
