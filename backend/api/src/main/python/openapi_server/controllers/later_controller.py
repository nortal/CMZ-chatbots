import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.convo_history import ConvoHistory  # noqa: E501
from openapi_server.models.media import Media  # noqa: E501
from openapi_server.models.summarize_request import SummarizeRequest  # noqa: E501
from openapi_server.models.summary import Summary  # noqa: E501
from openapi_server import util


def convo_history_delete(id):  # noqa: E501
    """Delete conversation history (GDPR) (backlog)

     # noqa: E501

    :param id: Conversation/session id
    :type id: str

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    return 'do some magic!'


def convo_history_get(animal_id=None, user_id=None, limit=None):  # noqa: E501
    """Get conversation history (backlog)

     # noqa: E501

    :param animal_id: 
    :type animal_id: str
    :param user_id: 
    :type user_id: str
    :param limit: 
    :type limit: int

    :rtype: Union[ConvoHistory, Tuple[ConvoHistory, int], Tuple[ConvoHistory, int, Dict[str, str]]
    """
    return 'do some magic!'


def media_delete(media_id):  # noqa: E501
    """Delete media by id (backlog)

     # noqa: E501

    :param media_id: 
    :type media_id: str

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    return 'do some magic!'


def media_get(media_id):  # noqa: E501
    """Fetch media by id (backlog)

     # noqa: E501

    :param media_id: 
    :type media_id: str

    :rtype: Union[Media, Tuple[Media, int], Tuple[Media, int, Dict[str, str]]
    """
    return 'do some magic!'


def summarize_convo_post(body):  # noqa: E501
    """Summarize conversation for personalization/cost control (backlog)

     # noqa: E501

    :param summarize_request: 
    :type summarize_request: dict | bytes

    :rtype: Union[Summary, Tuple[Summary, int], Tuple[Summary, int, Dict[str, str]]
    """
    summarize_request = body
    if connexion.request.is_json:
        summarize_request = SummarizeRequest.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def upload_media_post(file, title=None, animal_id=None):  # noqa: E501
    """Upload media (image/audio/video) (backlog)

     # noqa: E501

    :param file: 
    :type file: str
    :param title: 
    :type title: str
    :param animal_id: 
    :type animal_id: str

    :rtype: Union[Media, Tuple[Media, int], Tuple[Media, int, Dict[str, str]]
    """
    return 'do some magic!'
