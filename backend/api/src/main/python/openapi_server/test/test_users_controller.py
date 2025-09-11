import unittest

from flask import json

from openapi_server.models.user import User  # noqa: E501
from openapi_server.test import BaseTestCase


class TestUsersController(BaseTestCase):
    """UsersController integration test stubs"""

    def test_me_get(self):
        """Test case for me_get

        Current authenticated user
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/me',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
