import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.animal import Animal  # noqa: E501
from openapi_server.models.animal_config import AnimalConfig  # noqa: E501
from openapi_server.models.animal_config_update import AnimalConfigUpdate  # noqa: E501
from openapi_server.models.animal_details import AnimalDetails  # noqa: E501
from openapi_server.models.error import Error  # noqa: E501
from openapi_server import util


def animal_config_get(animalid):  # noqa: E501
    """Get animal configuration

     # noqa: E501

    :param animalid: 
    :type animalid: str

    :rtype: Union[AnimalConfig, Tuple[AnimalConfig, int], Tuple[AnimalConfig, int, Dict[str, str]]
    """
    return 'do some magic!'


def animal_config_patch(animalid, body):  # noqa: E501
    """Update animal configuration

     # noqa: E501

    :param animalid: 
    :type animalid: str
    :param animal_config_update: 
    :type animal_config_update: dict | bytes

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    animal_config_update = body
    if connexion.request.is_json:
        animal_config_update = AnimalConfigUpdate.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def animal_details_get(animalid):  # noqa: E501
    """Fetch animal details

     # noqa: E501

    :param animalid: 
    :type animalid: str

    :rtype: Union[AnimalDetails, Tuple[AnimalDetails, int], Tuple[AnimalDetails, int, Dict[str, str]]
    """
    return 'do some magic!'


def animal_list_get():  # noqa: E501
    """List animals

     # noqa: E501


    :rtype: Union[List[Animal], Tuple[List[Animal], int], Tuple[List[Animal], int, Dict[str, str]]
    """
    return 'do some magic!'
