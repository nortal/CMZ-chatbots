# coding: utf-8

from fastapi.testclient import TestClient


from pydantic import Field, StrictBool, StrictStr, field_validator  # noqa: F401
from typing import Any, Optional  # noqa: F401
from typing_extensions import Annotated  # noqa: F401
from openapi_server.models.error import Error  # noqa: F401
from openapi_server.models.paged_users import PagedUsers  # noqa: F401
from openapi_server.models.user import User  # noqa: F401
from openapi_server.models.user_details import UserDetails  # noqa: F401
from openapi_server.models.userrole_patch_request import UserrolePatchRequest  # noqa: F401


def test_user_delete(client: TestClient):
    """Test case for user_delete

    Delete user
    """
    params = [("id", 'id_example')]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "DELETE",
    #    "/user",
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_userdetails_get(client: TestClient):
    """Test case for userdetails_get

    Fetch specific user details
    """
    params = [("id", 'id_example')]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/userdetails",
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_userlist_get(client: TestClient):
    """Test case for userlist_get

    List users
    """
    params = [("details", False),     ("role", 'role_example'),     ("page", 1),     ("page_size", 50)]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/userlist",
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_userrole_patch(client: TestClient):
    """Test case for userrole_patch

    Change user role
    """
    userrole_patch_request = openapi_server.UserrolePatchRequest()

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "PATCH",
    #    "/userrole",
    #    headers=headers,
    #    json=userrole_patch_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

