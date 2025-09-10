import unittest

from flask import json

from openapi_server.models.error import Error  # noqa: E501
from openapi_server.models.paged_users import PagedUsers  # noqa: E501
from openapi_server.models.user import User  # noqa: E501
from openapi_server.models.user_details import UserDetails  # noqa: E501
from openapi_server.models.userrole_patch_request import UserrolePatchRequest  # noqa: E501
from openapi_server.test import BaseTestCase


class TestAdminController(BaseTestCase):
    """AdminController integration test stubs"""

    def test_user_delete(self):
        """Test case for user_delete

        Delete user
        """
        query_string = [('id', 'id_example')]
        headers = { 
            'Accept': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/user',
            method='DELETE',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_userdetails_get(self):
        """Test case for userdetails_get

        Fetch specific user details
        """
        query_string = [('id', 'id_example')]
        headers = { 
            'Accept': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/userdetails',
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_userlist_get(self):
        """Test case for userlist_get

        List users
        """
        query_string = [('details', False),
                        ('role', 'role_example'),
                        ('page', 1),
                        ('pageSize', 50)]
        headers = { 
            'Accept': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/userlist',
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_userrole_patch(self):
        """Test case for userrole_patch

        Change user role
        """
        userrole_patch_request = openapi_server.UserrolePatchRequest()
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/userrole',
            method='PATCH',
            headers=headers,
            data=json.dumps(userrole_patch_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
