import unittest

from flask import json

from openapi_server.models.convo_history import ConvoHistory  # noqa: E501
from openapi_server.models.error import Error  # noqa: E501
from openapi_server.models.media import Media  # noqa: E501
from openapi_server.models.summarize_request import SummarizeRequest  # noqa: E501
from openapi_server.models.summary import Summary  # noqa: E501
from openapi_server.test import BaseTestCase


class TestLaterController(BaseTestCase):
    """LaterController integration test stubs"""

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

    def test_media_delete(self):
        """Test case for media_delete

        Delete media by id (backlog)
        """
        query_string = [('mediaId', 'media_id_example')]
        headers = { 
        }
        response = self.client.open(
            '/media',
            method='DELETE',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_media_get(self):
        """Test case for media_get

        Fetch media by id (backlog)
        """
        query_string = [('mediaId', 'media_id_example')]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/media',
            method='GET',
            headers=headers,
            query_string=query_string)
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

    @unittest.skip("multipart/form-data not supported by Connexion")
    def test_upload_media_post(self):
        """Test case for upload_media_post

        Upload media (image/audio/video) (backlog)
        """
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'multipart/form-data',
        }
        data = dict(file='/path/to/file',
                    title='title_example',
                    animal_id='animal_id_example')
        response = self.client.open(
            '/upload_media',
            method='POST',
            headers=headers,
            data=data,
            content_type='multipart/form-data')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
