import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.convo_history import ConvoHistory  # noqa: E501
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
    try:
        # Later functionality not yet implemented
        return {"code": "not_implemented", "message": "Later functionality not yet implemented"}, 501
    except Exception as e:
        return {"code": "internal_error", "message": str(e)}, 500


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
    try:
        # Later functionality not yet implemented
        return {"code": "not_implemented", "message": "Later functionality not yet implemented"}, 501
    except Exception as e:
        return {"code": "internal_error", "message": str(e)}, 500


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
    try:
        # Later functionality not yet implemented
        return {"code": "not_implemented", "message": "Later functionality not yet implemented"}, 501
    except Exception as e:
        return {"code": "internal_error", "message": str(e)}, 500
