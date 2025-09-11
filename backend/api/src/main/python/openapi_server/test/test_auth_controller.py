import unittest

from flask import json

from openapi_server.models.auth_request import AuthRequest  # noqa: E501
from openapi_server.models.auth_response import AuthResponse  # noqa: E501
from openapi_server.models.error import Error  # noqa: E501
from openapi_server.models.password_reset_request import PasswordResetRequest  # noqa: E501
from openapi_server.test import BaseTestCase


class TestAuthController(BaseTestCase):
    """AuthController integration test stubs"""

    def test_auth_logout_post(self):
        """Test case for auth_logout_post

        Logout current user (invalidate token/session)
        """
        headers = { 
        }
        response = self.client.open(
            '/auth/logout',
            method='POST',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_auth_post(self):
        """Test case for auth_post

        Login or register
        """
        auth_request = {"password":"password","username":"username","register":True}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/auth',
            method='POST',
            headers=headers,
            data=json.dumps(auth_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_auth_refresh_post(self):
        """Test case for auth_refresh_post

        Refresh access token
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/auth/refresh',
            method='POST',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_auth_reset_password_post(self):
        """Test case for auth_reset_password_post

        Initiate password reset
        """
        password_reset_request = {"email":"email"}
        headers = { 
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/auth/reset_password',
            method='POST',
            headers=headers,
            data=json.dumps(password_reset_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
