import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.error import Error  # noqa: E501
from openapi_server.models.media import Media  # noqa: E501
from openapi_server import util


def media_delete(id):  # noqa: E501
    """Delete media by id (backlog)

     # noqa: E501

    :param id: 
    :type id: str

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    return 'do some magic!'


def media_get(id):  # noqa: E501
    """Fetch media by id (backlog)

     # noqa: E501

    :param id: 
    :type id: str

    :rtype: Union[Media, Tuple[Media, int], Tuple[Media, int, Dict[str, str]]
    """
    return 'do some magic!'


def upload_media_post(file, title=None, animalid=None):  # noqa: E501
    """Upload media (image/audio/video) (backlog)

     # noqa: E501

    :param file: 
    :type file: str
    :param title: 
    :type title: str
    :param animalid: 
    :type animalid: str

    :rtype: Union[Media, Tuple[Media, int], Tuple[Media, int, Dict[str, str]]
    """
    return 'do some magic!'
