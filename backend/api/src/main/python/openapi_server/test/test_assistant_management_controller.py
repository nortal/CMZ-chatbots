import unittest

from flask import json

from openapi_server.models.assistant_list_response import AssistantListResponse  # noqa: E501
from openapi_server.models.assistant_response import AssistantResponse  # noqa: E501
from openapi_server.models.create_assistant_request import CreateAssistantRequest  # noqa: E501
from openapi_server.models.update_assistant_request import UpdateAssistantRequest  # noqa: E501
from openapi_server.test import BaseTestCase


class TestAssistantManagementController(BaseTestCase):
    """AssistantManagementController integration test stubs"""

    def test_assistant_create_post(self):
        """Test case for assistant_create_post

        Create new animal assistant
        """
        create_assistant_request = {"knowledgeBaseFileIds":["knowledgeBaseFileIds","knowledgeBaseFileIds"],"personalityId":"personalityId","guardrailId":"guardrailId","animalId":"animalId"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/assistant',
            method='POST',
            headers=headers,
            data=json.dumps(create_assistant_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_assistant_delete(self):
        """Test case for assistant_delete

        Delete assistant
        """
        headers = { 
        }
        response = self.client.open(
            '/assistant/{assistant_id}'.format(assistant_id='assistant_id_example'),
            method='DELETE',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_assistant_get(self):
        """Test case for assistant_get

        Get assistant by ID
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/assistant/{assistant_id}'.format(assistant_id='assistant_id_example'),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_assistant_list_get(self):
        """Test case for assistant_list_get

        List all assistants
        """
        query_string = [('animalId', 'animal_id_example'),
                        ('status', 'status_example')]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/assistant',
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_assistant_update_put(self):
        """Test case for assistant_update_put

        Update assistant configuration
        """
        update_assistant_request = {"knowledgeBaseFileIds":["knowledgeBaseFileIds","knowledgeBaseFileIds"],"personalityId":"personalityId","guardrailId":"guardrailId","status":"ACTIVE"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/assistant/{assistant_id}'.format(assistant_id='assistant_id_example'),
            method='PUT',
            headers=headers,
            data=json.dumps(update_assistant_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
