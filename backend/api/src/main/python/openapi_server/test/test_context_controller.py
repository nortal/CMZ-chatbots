import unittest

from flask import json

from openapi_server.models.context_summary_archive import ContextSummaryArchive  # noqa: E501
from openapi_server.models.context_summary_post200_response import ContextSummaryPost200Response  # noqa: E501
from openapi_server.models.context_summary_post_request import ContextSummaryPostRequest  # noqa: E501
from openapi_server.models.error import Error  # noqa: E501
from openapi_server.models.get_user_context200_response import GetUserContext200Response  # noqa: E501
from openapi_server.models.update_user_context200_response import UpdateUserContext200Response  # noqa: E501
from openapi_server.models.update_user_context_request import UpdateUserContextRequest  # noqa: E501
from openapi_server.test import BaseTestCase


class TestContextController(BaseTestCase):
    """ContextController integration test stubs"""

    def test_context_summary_get(self):
        """Test case for context_summary_get

        Get summarized user context
        """
        query_string = [('maxTokens', 1000)]
        headers = { 
            'Accept': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/api/v1/context/{user_id}/summary'.format(user_id='user_id_example'),
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_context_summary_post(self):
        """Test case for context_summary_post

        Trigger context summarization
        """
        context_summary_post_request = openapi_server.ContextSummaryPostRequest()
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/api/v1/context/{user_id}/summary'.format(user_id='user_id_example'),
            method='POST',
            headers=headers,
            data=json.dumps(context_summary_post_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_user_context(self):
        """Test case for get_user_context

        Get user conversation context
        """
        query_string = [('includeHistory', False),
                        ('contextDepth', standard)]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/api/v1/context/{user_id}'.format(user_id='user_id_example'),
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_user_context(self):
        """Test case for update_user_context

        Update user conversation context
        """
        update_user_context_request = openapi_server.UpdateUserContextRequest()
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/api/v1/context/{user_id}'.format(user_id='user_id_example'),
            method='PUT',
            headers=headers,
            data=json.dumps(update_user_context_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
