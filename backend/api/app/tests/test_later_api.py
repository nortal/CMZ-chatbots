# coding: utf-8

from fastapi.testclient import TestClient


from pydantic import Field, StrictBytes, StrictStr  # noqa: F401
from typing import Any, Optional, Tuple, Union  # noqa: F401
from typing_extensions import Annotated  # noqa: F401
from openapi_server.models.convo_history import ConvoHistory  # noqa: F401
from openapi_server.models.error import Error  # noqa: F401
from openapi_server.models.media import Media  # noqa: F401
from openapi_server.models.summarize_request import SummarizeRequest  # noqa: F401
from openapi_server.models.summary import Summary  # noqa: F401


def test_convo_history_delete(client: TestClient):
    """Test case for convo_history_delete

    Delete conversation history (GDPR) (backlog)
    """
    params = [("id", 'id_example')]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "DELETE",
    #    "/convo_history",
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_convo_history_get(client: TestClient):
    """Test case for convo_history_get

    Get conversation history (backlog)
    """
    params = [("animalid", 'animalid_example'),     ("userid", 'userid_example'),     ("limit", 100)]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/convo_history",
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_media_delete(client: TestClient):
    """Test case for media_delete

    Delete media by id (backlog)
    """
    params = [("id", 'id_example')]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "DELETE",
    #    "/media",
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_media_get(client: TestClient):
    """Test case for media_get

    Fetch media by id (backlog)
    """
    params = [("id", 'id_example')]
    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/media",
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_summarize_convo_post(client: TestClient):
    """Test case for summarize_convo_post

    Summarize conversation for personalization/cost control (backlog)
    """
    summarize_request = {"max_chars":0,"session_id":"sessionId"}

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/summarize_convo",
    #    headers=headers,
    #    json=summarize_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_upload_media_post(client: TestClient):
    """Test case for upload_media_post

    Upload media (image/audio/video) (backlog)
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    data = {
        "file": '/path/to/file',
        "title": 'title_example',
        "animalid": 'animalid_example'
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/upload_media",
    #    headers=headers,
    #    data=data,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

