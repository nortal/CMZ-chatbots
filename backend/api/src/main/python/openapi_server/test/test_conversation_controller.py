import unittest

from flask import json

from openapi_server.models.convo_history import ConvoHistory  # noqa: E501
from openapi_server.models.convo_turn_request import ConvoTurnRequest  # noqa: E501
from openapi_server.models.convo_turn_response import ConvoTurnResponse  # noqa: E501
from openapi_server.models.error import Error  # noqa: E501
from openapi_server.models.summarize_request import SummarizeRequest  # noqa: E501
from openapi_server.models.summary import Summary  # noqa: E501
from openapi_server.test import BaseTestCase


class TestConversationController(BaseTestCase):
    """ConversationController integration test stubs"""

    def test_convo_history_delete(self):
        """Test case for convo_history_delete

        Delete conversation history (GDPR) (backlog)
        """
        query_string = [('id', 'id_example')]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/convo_history',
            method='DELETE',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_convo_history_get(self):
        """Test case for convo_history_get

        Get conversation history (backlog)
        """
        query_string = [('animalId', 'animal_id_example'),
                        ('userId', 'user_id_example'),
                        ('limit', 100)]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/convo_history',
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_convo_turn_post(self):
        """Test case for convo_turn_post

        Send a conversation turn and get AI reply
        """
        convo_turn_request = {"metadata":{"key":""},"contextSummary":"contextSummary","sessionId":"sessionId","message":"message","animalId":"animalId"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/convo_turn',
            method='POST',
            headers=headers,
            data=json.dumps(convo_turn_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_summarize_convo_post(self):
        """Test case for summarize_convo_post

        Summarize conversation for personalization/cost control (backlog)
        """
        summarize_request = {"maxChars":0,"sessionId":"sessionId"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/summarize_convo',
            method='POST',
            headers=headers,
            data=json.dumps(summarize_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
