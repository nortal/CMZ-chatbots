# coding: utf-8

from fastapi.testclient import TestClient


from openapi_server.models.admin_shell import AdminShell  # noqa: F401
from openapi_server.models.member_shell import MemberShell  # noqa: F401
from openapi_server.models.public_home import PublicHome  # noqa: F401


def test_admin_get(client: TestClient):
    """Test case for admin_get

    Admin dashboard shell data
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/admin",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_member_get(client: TestClient):
    """Test case for member_get

    User portal shell data
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/member",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_root_get(client: TestClient):
    """Test case for root_get

    Public homepage
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

