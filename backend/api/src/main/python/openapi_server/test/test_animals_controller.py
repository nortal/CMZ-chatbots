import unittest

from flask import json

from openapi_server.models.animal import Animal  # noqa: E501
from openapi_server.models.animal_config import AnimalConfig  # noqa: E501
from openapi_server.models.animal_config_update import AnimalConfigUpdate  # noqa: E501
from openapi_server.models.animal_details import AnimalDetails  # noqa: E501
from openapi_server.models.error import Error  # noqa: E501
from openapi_server.test import BaseTestCase


class TestAnimalsController(BaseTestCase):
    """AnimalsController integration test stubs"""

    def test_animal_config_get(self):
        """Test case for animal_config_get

        Get animal configuration
        """
        query_string = [('animalId', 'animal_id_example')]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/animal_config',
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_animal_config_patch(self):
        """Test case for animal_config_patch

        Update animal configuration
        """
        animal_config_update = {"voice":"voice","animalConfigId":"animalConfigId","deleted":{"at":"2000-01-23T04:56:07.000+00:00","by":{"actorId":"actorId","displayName":"displayName","email":"email"}},"personality":"personality","softDelete":False,"created":{"at":"2000-01-23T04:56:07.000+00:00","by":{"actorId":"actorId","displayName":"displayName","email":"email"}},"temperature":0.1601656380922023,"toolsEnabled":["toolsEnabled","toolsEnabled"],"guardrails":{"key":""},"modified":{"at":"2000-01-23T04:56:07.000+00:00","by":{"actorId":"actorId","displayName":"displayName","email":"email"}},"aiModel":"aiModel","topP":0.6027456183070403}
        query_string = [('animalId', 'animal_id_example')]
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/animal_config',
            method='PATCH',
            headers=headers,
            data=json.dumps(animal_config_update),
            content_type='application/json',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_animal_details_get(self):
        """Test case for animal_details_get

        Fetch animal details
        """
        query_string = [('animalId', 'animal_id_example')]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/animal_details',
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_animal_list_get(self):
        """Test case for animal_list_get

        List animals
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/animal_list',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
