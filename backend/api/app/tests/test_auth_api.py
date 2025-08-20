# coding: utf-8

from fastapi.testclient import TestClient


from typing import Any  # noqa: F401
from openapi_server.models.auth_request import AuthRequest  # noqa: F401
from openapi_server.models.auth_response import AuthResponse  # noqa: F401
from openapi_server.models.error import Error  # noqa: F401
from openapi_server.models.password_reset_request import PasswordResetRequest  # noqa: F401


def test_auth_logout_post(client: TestClient):
    """Test case for auth_logout_post

    Logout current user (invalidate token/session)
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/auth/logout",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_auth_post(client: TestClient):
    """Test case for auth_post

    Login or register
    """
    auth_request = {"password":"password","username":"username","register":1}

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/auth",
    #    headers=headers,
    #    json=auth_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_auth_refresh_post(client: TestClient):
    """Test case for auth_refresh_post

    Refresh access token
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/auth/refresh",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_auth_reset_password_post(client: TestClient):
    """Test case for auth_reset_password_post

    Initiate password reset
    """
    password_reset_request = {"email":"email"}

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "POST",
    #    "/auth/reset_password",
    #    headers=headers,
    #    json=password_reset_request,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

