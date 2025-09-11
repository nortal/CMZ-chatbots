import unittest

from flask import json

from openapi_server.models.error import Error  # noqa: E501
from openapi_server.models.family import Family  # noqa: E501
from openapi_server.test import BaseTestCase


class TestFamilyController(BaseTestCase):
    """FamilyController integration test stubs"""

    def test_create_family(self):
        """Test case for create_family

        Create a new family
        """
        family = {"familyId":"familyId","students":["students","students"],"parents":["parents","parents"]}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/family',
            method='POST',
            headers=headers,
            data=json.dumps(family),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_family(self):
        """Test case for delete_family

        Delete a family
        """
        headers = { 
        }
        response = self.client.open(
            '/family/{family_id}'.format(family_id='family_id_example'),
            method='DELETE',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_family(self):
        """Test case for get_family

        Get specific family by ID
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/family/{family_id}'.format(family_id='family_id_example'),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_list_families(self):
        """Test case for list_families

        Get list of all families
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/family',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_family(self):
        """Test case for update_family

        Update an existing family
        """
        family = {"familyId":"familyId","students":["students","students"],"parents":["parents","parents"]}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/family/{family_id}'.format(family_id='family_id_example'),
            method='PATCH',
            headers=headers,
            data=json.dumps(family),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
