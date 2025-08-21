import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.error import Error  # noqa: E501
from openapi_server.models.knowledge_article import KnowledgeArticle  # noqa: E501
from openapi_server.models.knowledge_create import KnowledgeCreate  # noqa: E501
from openapi_server import util


def knowledge_article_delete(id):  # noqa: E501
    """Delete knowledge article

     # noqa: E501

    :param id: 
    :type id: str

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    return 'do some magic!'


def knowledge_article_get(id):  # noqa: E501
    """Get article by id

     # noqa: E501

    :param id: 
    :type id: str

    :rtype: Union[KnowledgeArticle, Tuple[KnowledgeArticle, int], Tuple[KnowledgeArticle, int, Dict[str, str]]
    """
    return 'do some magic!'


def knowledge_article_post(body):  # noqa: E501
    """Create knowledge article

     # noqa: E501

    :param knowledge_create: 
    :type knowledge_create: dict | bytes

    :rtype: Union[KnowledgeArticle, Tuple[KnowledgeArticle, int], Tuple[KnowledgeArticle, int, Dict[str, str]]
    """
    knowledge_create = body
    if connexion.request.is_json:
        knowledge_create = KnowledgeCreate.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
