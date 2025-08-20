# coding: utf-8

from fastapi.testclient import TestClient


from pydantic import StrictStr  # noqa: F401
from typing import Any  # noqa: F401
from openapi_server.models.error import Error  # noqa: F401
from openapi_server.models.knowledge_article import KnowledgeArticle  # noqa: F401
from openapi_server.models.knowledge_create import KnowledgeCreate  # noqa: F401


def test_knowledge_article_delete(client: TestClient):
    """Test case for knowledge_article_delete

    Delete knowledge article
    """
    params = [("id", 'id_example')]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "DELETE",
    #    "/knowledge_article",
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_knowledge_article_get(client: TestClient):
    """Test case for knowledge_article_get

    Get article by id
    """
    params = [("id", 'id_example')]
    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/knowledge_article",
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_knowledge_article_post(client: TestClient):
    """Test case for knowledge_article_post

    Create knowledge article
    """
    knowledge_create = {"visibility":"public","title":"title","body":"body","animalid":"animalid","tags":["tags","tags"]}

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/knowledge_article",
    #    headers=headers,
    #    json=knowledge_create,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

