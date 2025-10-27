import unittest

from flask import json

from openapi_server.models.assistant_response import AssistantResponse  # noqa: E501
from openapi_server.models.chat_request import ChatRequest  # noqa: E501
from openapi_server.models.chat_response import ChatResponse  # noqa: E501
from openapi_server.models.create_sandbox_request import CreateSandboxRequest  # noqa: E501
from openapi_server.models.promote_sandbox_request import PromoteSandboxRequest  # noqa: E501
from openapi_server.models.sandbox_list_response import SandboxListResponse  # noqa: E501
from openapi_server.models.sandbox_response import SandboxResponse  # noqa: E501
from openapi_server.test import BaseTestCase


class TestSandboxTestingController(BaseTestCase):
    """SandboxTestingController integration test stubs"""

    def test_sandbox_chat_post(self):
        """Test case for sandbox_chat_post

        Test conversation with sandbox assistant
        """
        chat_request = {"conversationId":"conversationId","message":"message"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/sandbox/{sandbox_id}/chat'.format(sandbox_id='sandbox_id_example'),
            method='POST',
            headers=headers,
            data=json.dumps(chat_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_sandbox_create_post(self):
        """Test case for sandbox_create_post

        Create sandbox assistant for testing
        """
        create_sandbox_request = {"knowledgeBaseFileIds":["knowledgeBaseFileIds","knowledgeBaseFileIds","knowledgeBaseFileIds","knowledgeBaseFileIds","knowledgeBaseFileIds"],"personalityId":"personalityId","guardrailId":"guardrailId","animalId":"animalId"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/sandbox',
            method='POST',
            headers=headers,
            data=json.dumps(create_sandbox_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_sandbox_delete(self):
        """Test case for sandbox_delete

        Delete sandbox assistant
        """
        headers = { 
        }
        response = self.client.open(
            '/sandbox/{sandbox_id}'.format(sandbox_id='sandbox_id_example'),
            method='DELETE',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_sandbox_get(self):
        """Test case for sandbox_get

        Get sandbox assistant details
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/sandbox/{sandbox_id}'.format(sandbox_id='sandbox_id_example'),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_sandbox_list_get(self):
        """Test case for sandbox_list_get

        List user's sandbox assistants
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/sandbox',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_sandbox_promote_post(self):
        """Test case for sandbox_promote_post

        Promote sandbox to live assistant
        """
        promote_sandbox_request = {"animalId":"animalId"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/sandbox/{sandbox_id}/promote'.format(sandbox_id='sandbox_id_example'),
            method='POST',
            headers=headers,
            data=json.dumps(promote_sandbox_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
