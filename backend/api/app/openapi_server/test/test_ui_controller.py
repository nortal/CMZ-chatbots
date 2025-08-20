import unittest

from flask import json

from openapi_server.models.admin_shell import AdminShell  # noqa: E501
from openapi_server.models.member_shell import MemberShell  # noqa: E501
from openapi_server.models.public_home import PublicHome  # noqa: E501
from openapi_server.test import BaseTestCase


class TestUIController(BaseTestCase):
    """UIController integration test stubs"""

    def test_admin_get(self):
        """Test case for admin_get

        Admin dashboard shell data
        """
        headers = { 
            'Accept': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/admin',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_member_get(self):
        """Test case for member_get

        User portal shell data
        """
        headers = { 
            'Accept': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/member',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_root_get(self):
        """Test case for root_get

        Public homepage
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
