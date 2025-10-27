import unittest

from flask import json

from openapi_server.models.create_guardrail_request import CreateGuardrailRequest  # noqa: E501
from openapi_server.models.guardrail_list_response import GuardrailListResponse  # noqa: E501
from openapi_server.models.guardrail_response import GuardrailResponse  # noqa: E501
from openapi_server.models.update_guardrail_request import UpdateGuardrailRequest  # noqa: E501
from openapi_server.test import BaseTestCase


class TestGuardrailManagementController(BaseTestCase):
    """GuardrailManagementController integration test stubs"""

    def test_guardrail_create_post(self):
        """Test case for guardrail_create_post

        Create new guardrail
        """
        create_guardrail_request = {"severity":"STRICT","ageAppropriate":["PRESCHOOL","PRESCHOOL"],"isDefault":True,"name":"name","description":"description","guardrailText":"guardrailText","category":"SAFETY"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/guardrail',
            method='POST',
            headers=headers,
            data=json.dumps(create_guardrail_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_guardrail_delete(self):
        """Test case for guardrail_delete

        Delete guardrail
        """
        headers = { 
        }
        response = self.client.open(
            '/guardrail/{guardrail_id}'.format(guardrail_id='guardrail_id_example'),
            method='DELETE',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_guardrail_get(self):
        """Test case for guardrail_get

        Get guardrail by ID
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/guardrail/{guardrail_id}'.format(guardrail_id='guardrail_id_example'),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_guardrail_list_get(self):
        """Test case for guardrail_list_get

        List all guardrails
        """
        query_string = [('category', 'category_example'),
                        ('isDefault', True)]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/guardrail',
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_guardrail_update_put(self):
        """Test case for guardrail_update_put

        Update guardrail
        """
        update_guardrail_request = {"severity":"STRICT","ageAppropriate":["PRESCHOOL","PRESCHOOL"],"isDefault":True,"name":"name","description":"description","guardrailText":"guardrailText","category":"SAFETY"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/guardrail/{guardrail_id}'.format(guardrail_id='guardrail_id_example'),
            method='PUT',
            headers=headers,
            data=json.dumps(update_guardrail_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
