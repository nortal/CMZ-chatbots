import unittest

from flask import json

# Removed unused imports as flagged by GitHub Advanced Security
from openapi_server.test import BaseTestCase


class TestUserController(BaseTestCase):
    """UserController integration test stubs"""

    def test_create_user(self):
        """Test case for create_user

        Create a new user
        """
        create_user_request = openapi_server.CreateUserRequest()
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/user',
            method='POST',
            headers=headers,
            data=json.dumps(create_user_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
