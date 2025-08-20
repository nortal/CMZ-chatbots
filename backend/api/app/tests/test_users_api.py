# coding: utf-8

from fastapi.testclient import TestClient


from openapi_server.models.user import User  # noqa: F401


def test_me_get(client: TestClient):
    """Test case for me_get

    Current authenticated user
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/me",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

