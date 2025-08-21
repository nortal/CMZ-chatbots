import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.convo_history import ConvoHistory  # noqa: E501
from openapi_server.models.convo_turn_request import ConvoTurnRequest  # noqa: E501
from openapi_server.models.convo_turn_response import ConvoTurnResponse  # noqa: E501
from openapi_server.models.error import Error  # noqa: E501
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


def convo_history_get(animalid=None, userid=None, limit=None):  # noqa: E501
    """Get conversation history (backlog)

     # noqa: E501

    :param animalid: 
    :type animalid: str
    :param userid: 
    :type userid: str
    :param limit: 
    :type limit: int

    :rtype: Union[ConvoHistory, Tuple[ConvoHistory, int], Tuple[ConvoHistory, int, Dict[str, str]]
    """
    return 'do some magic!'


def convo_turn_post(body):  # noqa: E501
    """Send a conversation turn and get AI reply

     # noqa: E501

    :param convo_turn_request: 
    :type convo_turn_request: dict | bytes

    :rtype: Union[ConvoTurnResponse, Tuple[ConvoTurnResponse, int], Tuple[ConvoTurnResponse, int, Dict[str, str]]
    """
    convo_turn_request = body
    if connexion.request.is_json:
        convo_turn_request = ConvoTurnRequest.from_dict(connexion.request.get_json())  # noqa: E501
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
