import unittest

from flask import json

from openapi_server.models.error import Error  # noqa: E501
from openapi_server.models.list_animal_documents200_response import ListAnimalDocuments200Response  # noqa: E501
from openapi_server.models.upload_animal_document201_response import UploadAnimalDocument201Response  # noqa: E501
from openapi_server.test import BaseTestCase


class TestAnimalController(BaseTestCase):
    """AnimalController integration test stubs"""

    def test_delete_animal_document(self):
        """Test case for delete_animal_document

        Delete document from knowledge base
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/animal/{animal_id}/documents/{document_id}'.format(animal_id='animal_id_example', document_id='document_id_example'),
            method='DELETE',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_list_animal_documents(self):
        """Test case for list_animal_documents

        List documents in animal's knowledge base
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/animal/{animal_id}/documents'.format(animal_id='animal_id_example'),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    @unittest.skip("multipart/form-data not supported by Connexion")
    def test_upload_animal_document(self):
        """Test case for upload_animal_document

        Upload document to animal's knowledge base
        """
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'multipart/form-data',
        }
        data = dict(file='/path/to/file',
                    title='title_example',
                    description='description_example',
                    tags=['tags_example'])
        response = self.client.open(
            '/animal/{animal_id}/documents'.format(animal_id='animal_id_example'),
            method='POST',
            headers=headers,
            data=data,
            content_type='multipart/form-data')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
