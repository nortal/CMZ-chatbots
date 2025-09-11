import unittest

from flask import json

from openapi_server.models.error import Error  # noqa: E501
from openapi_server.models.media import Media  # noqa: E501
from openapi_server.test import BaseTestCase


class TestMediaController(BaseTestCase):
    """MediaController integration test stubs"""

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
