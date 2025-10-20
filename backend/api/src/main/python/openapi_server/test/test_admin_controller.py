import unittest

from flask import json

from openapi_server.models.error import Error  # noqa: E501
from openapi_server.models.paged_users import PagedUsers  # noqa: E501
from openapi_server.models.user import User  # noqa: E501
from openapi_server.models.user_details import UserDetails  # noqa: E501
from openapi_server.models.user_details_input import UserDetailsInput  # noqa: E501
from openapi_server.models.user_input import UserInput  # noqa: E501
from openapi_server.test import BaseTestCase


class TestAdminController(BaseTestCase):
    """AdminController integration test stubs"""

    def test_create_user(self):
        """Test case for create_user

        Create a new user
        """
        user_input = {"familyId":"familyId","role":"visitor","deleted":{"at":"2000-01-23T04:56:07.000+00:00","by":{"actorId":"actorId","displayName":"displayName","email":"email"}},"softDelete":False,"displayName":"displayName","created":{"at":"2000-01-23T04:56:07.000+00:00","by":{"actorId":"actorId","displayName":"displayName","email":"email"}},"modified":{"at":"2000-01-23T04:56:07.000+00:00","by":{"actorId":"actorId","displayName":"displayName","email":"email"}},"userType":"none","userId":"userId","email":"email"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/user',
            method='POST',
            headers=headers,
            data=json.dumps(user_input),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_create_user_details(self):
        """Test case for create_user_details

        Create user details
        """
        user_details_input = {"usage":{"totalSessions":0,"lastActive":"2000-01-23T04:56:07.000+00:00","totalTurns":6,"userId":"userId"},"userId":"userId"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/user_details',
            method='POST',
            headers=headers,
            data=json.dumps(user_details_input),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_user(self):
        """Test case for delete_user

        Delete user
        """
        headers = { 
        }
        response = self.client.open(
            '/user/{user_id}'.format(user_id='user_id_example'),
            method='DELETE',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_user_details(self):
        """Test case for delete_user_details

        Delete user details
        """
        headers = { 
        }
        response = self.client.open(
            '/user_details/{user_id}'.format(user_id='user_id_example'),
            method='DELETE',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_user(self):
        """Test case for get_user

        Get user by ID
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/user/{user_id}'.format(user_id='user_id_example'),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_user_details(self):
        """Test case for get_user_details

        Get user details by ID
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/user_details/{user_id}'.format(user_id='user_id_example'),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_list_user_details(self):
        """Test case for list_user_details

        Get list of all user details
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/user_details',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_list_users(self):
        """Test case for list_users

        Get list of all users
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/user',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_user(self):
        """Test case for update_user

        Update a user
        """
        user = {"familyId":"familyId","role":"visitor","deleted":{"at":"2000-01-23T04:56:07.000+00:00","by":{"actorId":"actorId","displayName":"displayName","email":"email"}},"softDelete":False,"displayName":"displayName","created":{"at":"2000-01-23T04:56:07.000+00:00","by":{"actorId":"actorId","displayName":"displayName","email":"email"}},"modified":{"at":"2000-01-23T04:56:07.000+00:00","by":{"actorId":"actorId","displayName":"displayName","email":"email"}},"userType":"none","userId":"userId","email":"email"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/user/{user_id}'.format(user_id='user_id_example'),
            method='PATCH',
            headers=headers,
            data=json.dumps(user),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_user_details(self):
        """Test case for update_user_details

        Update user details
        """
        user_details_input = {"usage":{"totalSessions":0,"lastActive":"2000-01-23T04:56:07.000+00:00","totalTurns":6,"userId":"userId"},"userId":"userId"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/user_details/{user_id}'.format(user_id='user_id_example'),
            method='PATCH',
            headers=headers,
            data=json.dumps(user_details_input),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
