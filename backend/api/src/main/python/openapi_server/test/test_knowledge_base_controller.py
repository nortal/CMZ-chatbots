import unittest

from flask import json

from openapi_server.models.knowledge_file_list_response import KnowledgeFileListResponse  # noqa: E501
from openapi_server.models.knowledge_file_response import KnowledgeFileResponse  # noqa: E501
from openapi_server.test import BaseTestCase


class TestKnowledgeBaseController(BaseTestCase):
    """KnowledgeBaseController integration test stubs"""

    def test_knowledge_file_delete(self):
        """Test case for knowledge_file_delete

        Delete knowledge base file
        """
        headers = { 
        }
        response = self.client.open(
            '/assistant/{assistant_id}/knowledge/{file_id}'.format(assistant_id='assistant_id_example', file_id='file_id_example'),
            method='DELETE',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_knowledge_file_get(self):
        """Test case for knowledge_file_get

        Get knowledge file details
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/assistant/{assistant_id}/knowledge/{file_id}'.format(assistant_id='assistant_id_example', file_id='file_id_example'),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_knowledge_list_get(self):
        """Test case for knowledge_list_get

        List knowledge base files
        """
        query_string = [('status', 'status_example')]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/assistant/{assistant_id}/knowledge'.format(assistant_id='assistant_id_example'),
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    @unittest.skip("multipart/form-data not supported by Connexion")
    def test_knowledge_upload_post(self):
        """Test case for knowledge_upload_post

        Upload knowledge base file
        """
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'multipart/form-data',
        }
        data = dict(file='/path/to/file',
                    description='description_example')
        response = self.client.open(
            '/assistant/{assistant_id}/knowledge'.format(assistant_id='assistant_id_example'),
            method='POST',
            headers=headers,
            data=data,
            content_type='multipart/form-data')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
