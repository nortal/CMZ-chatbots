import unittest

from flask import json

from openapi_server.models.error import Error  # noqa: E501
from openapi_server.models.knowledge_article import KnowledgeArticle  # noqa: E501
from openapi_server.models.knowledge_create import KnowledgeCreate  # noqa: E501
from openapi_server.test import BaseTestCase


class TestKnowledgeController(BaseTestCase):
    """KnowledgeController integration test stubs"""

    def test_knowledge_article_delete(self):
        """Test case for knowledge_article_delete

        Delete knowledge article
        """
        query_string = [('id', 'id_example')]
        headers = { 
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/knowledge_article',
            method='DELETE',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_knowledge_article_get(self):
        """Test case for knowledge_article_get

        Get article by id
        """
        query_string = [('id', 'id_example')]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/knowledge_article',
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_knowledge_article_post(self):
        """Test case for knowledge_article_post

        Create knowledge article
        """
        knowledge_create = {"visibility":"public","title":"title","body":"body","animalid":"animalid","tags":["tags","tags"]}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/knowledge_article',
            method='POST',
            headers=headers,
            data=json.dumps(knowledge_create),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
