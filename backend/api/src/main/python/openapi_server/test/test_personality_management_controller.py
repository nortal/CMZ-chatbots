import unittest

from flask import json

from openapi_server.models.create_personality_request import CreatePersonalityRequest  # noqa: E501
from openapi_server.models.personality_list_response import PersonalityListResponse  # noqa: E501
from openapi_server.models.personality_response import PersonalityResponse  # noqa: E501
from openapi_server.models.update_personality_request import UpdatePersonalityRequest  # noqa: E501
from openapi_server.test import BaseTestCase


class TestPersonalityManagementController(BaseTestCase):
    """PersonalityManagementController integration test stubs"""

    def test_personality_create_post(self):
        """Test case for personality_create_post

        Create new personality
        """
        create_personality_request = {"personalityText":"personalityText","tone":"PLAYFUL","isTemplate":True,"name":"name","animalType":"MAMMAL","description":"description","ageTarget":"PRESCHOOL"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/personality',
            method='POST',
            headers=headers,
            data=json.dumps(create_personality_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_personality_delete(self):
        """Test case for personality_delete

        Delete personality
        """
        headers = { 
        }
        response = self.client.open(
            '/personality/{personality_id}'.format(personality_id='personality_id_example'),
            method='DELETE',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_personality_get(self):
        """Test case for personality_get

        Get personality by ID
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/personality/{personality_id}'.format(personality_id='personality_id_example'),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_personality_list_get(self):
        """Test case for personality_list_get

        List all personalities
        """
        query_string = [('animalType', 'animal_type_example'),
                        ('isTemplate', True)]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/personality',
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_personality_update_put(self):
        """Test case for personality_update_put

        Update personality
        """
        update_personality_request = {"personalityText":"personalityText","tone":"PLAYFUL","name":"name","animalType":"MAMMAL","description":"description","ageTarget":"PRESCHOOL"}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/personality/{personality_id}'.format(personality_id='personality_id_example'),
            method='PUT',
            headers=headers,
            data=json.dumps(update_personality_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
