import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.error import Error  # noqa: E501
from openapi_server.models.knowledge_article import KnowledgeArticle  # noqa: E501
from openapi_server.models.knowledge_create import KnowledgeCreate  # noqa: E501
from openapi_server import util
from datetime import datetime
import uuid

# In-memory storage for knowledge articles (in production, this would be in DynamoDB)
_knowledge_store = {
    "ka_porcupine_diet": {
        "knowledgeId": "ka_porcupine_diet",
        "title": "Porcupine Diet and Feeding Habits",
        "body": "Porcupines are herbivores that primarily eat leaves, herbs, twigs, and bark. They have a particular fondness for salt and may chew on human-made objects to get sodium. Their diet varies seasonally, with more bark consumption in winter and fresh vegetation in summer.",
        "tags": ["diet", "feeding", "herbivore", "seasonal"],
        "visibility": "public",
        "animalId": "animal_porcupine",
        "created": {"at": "2025-09-11T00:00:00Z", "by": {"userId": "system"}},
        "modified": {"at": "2025-09-11T00:00:00Z", "by": {"userId": "system"}},
        "deleted": None,
        "softDelete": False
    },
    "ka_lion_hunting": {
        "knowledgeId": "ka_lion_hunting",
        "title": "Lion Hunting Strategies",
        "body": "Lions are apex predators that use cooperative hunting strategies. Female lions do most of the hunting while males protect the territory. They hunt in groups to take down large prey like zebras, wildebeest, and buffalo. Lions can reach speeds of up to 50 mph in short bursts.",
        "tags": ["hunting", "behavior", "predator", "cooperation"],
        "visibility": "public", 
        "animalId": "animal_1",
        "created": {"at": "2025-09-11T00:00:00Z", "by": {"userId": "system"}},
        "modified": {"at": "2025-09-11T00:00:00Z", "by": {"userId": "system"}},
        "deleted": None,
        "softDelete": False
    }
}

def knowledge_article_delete(knowledge_id):  # noqa: E501
    """Delete knowledge article

     # noqa: E501

    :param knowledge_id: 
    :type knowledge_id: str

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    try:
        if knowledge_id in _knowledge_store:
            # Soft delete - mark as deleted instead of removing
            _knowledge_store[knowledge_id]["softDelete"] = True
            _knowledge_store[knowledge_id]["deleted"] = {
                "at": datetime.utcnow().isoformat() + 'Z', 
                "by": {"userId": "system"}
            }
            return None, 204
        else:
            return Error(code='NOT_FOUND', message=f"Knowledge article {knowledge_id} not found"), 404
    except Exception as e:
        return Error(code='INTERNAL_ERROR', message=str(e)), 500


def knowledge_article_get(knowledge_id):  # noqa: E501
    """Get article by id

     # noqa: E501

    :param knowledge_id: 
    :type knowledge_id: str

    :rtype: Union[KnowledgeArticle, Tuple[KnowledgeArticle, int], Tuple[KnowledgeArticle, int, Dict[str, str]]
    """
    try:
        if knowledge_id in _knowledge_store and not _knowledge_store[knowledge_id].get("softDelete", False):
            article_data = _knowledge_store[knowledge_id].copy()
            return KnowledgeArticle.from_dict(article_data)
        else:
            return Error(code='NOT_FOUND', message=f"Knowledge article {knowledge_id} not found"), 404
    except Exception as e:
        return Error(code='INTERNAL_ERROR', message=str(e)), 500


def knowledge_article_post(body):  # noqa: E501
    """Create knowledge article

     # noqa: E501

    :param knowledge_create: 
    :type knowledge_create: dict | bytes

    :rtype: Union[KnowledgeArticle, Tuple[KnowledgeArticle, int], Tuple[KnowledgeArticle, int, Dict[str, str]]
    """
    try:
        knowledge_create = body
        if connexion.request.is_json:
            knowledge_create = KnowledgeCreate.from_dict(connexion.request.get_json())  # noqa: E501
        
        # Convert to dict for processing
        if hasattr(knowledge_create, 'to_dict'):
            article_data = knowledge_create.to_dict()
        else:
            article_data = dict(knowledge_create)
        
        # Generate unique ID
        knowledge_id = f"ka_{str(uuid.uuid4()).replace('-', '_')}"
        article_data["knowledgeId"] = knowledge_id
        
        # Add audit fields
        now = datetime.utcnow().isoformat() + 'Z'
        article_data["created"] = {"at": now, "by": {"userId": "system"}}
        article_data["modified"] = {"at": now, "by": {"userId": "system"}}
        article_data["deleted"] = None
        article_data["softDelete"] = False
        
        # Store the article
        _knowledge_store[knowledge_id] = article_data
        
        return KnowledgeArticle.from_dict(article_data), 201
        
    except Exception as e:
        return Error(code='INTERNAL_ERROR', message=str(e)), 500
