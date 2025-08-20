# coding: utf-8

from fastapi.testclient import TestClient


from pydantic import StrictBytes, StrictStr  # noqa: F401
from typing import Any, Optional, Tuple, Union  # noqa: F401
from openapi_server.models.error import Error  # noqa: F401
from openapi_server.models.media import Media  # noqa: F401


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

