import unittest

from flask import json

from openapi_server.models.apply_guardrail_template200_response import ApplyGuardrailTemplate200Response  # noqa: E501
from openapi_server.models.apply_guardrail_template_request import ApplyGuardrailTemplateRequest  # noqa: E501
from openapi_server.models.error import Error  # noqa: E501
from openapi_server.models.get_animal_system_prompt200_response import GetAnimalSystemPrompt200Response  # noqa: E501
from openapi_server.models.guardrail import Guardrail  # noqa: E501
from openapi_server.models.guardrail_input import GuardrailInput  # noqa: E501
from openapi_server.models.guardrail_template import GuardrailTemplate  # noqa: E501
from openapi_server.models.guardrail_update import GuardrailUpdate  # noqa: E501
from openapi_server.test import BaseTestCase


class TestGuardrailsController(BaseTestCase):
    """GuardrailsController integration test stubs"""

    def test_apply_guardrail_template(self):
        """Test case for apply_guardrail_template

        Apply template to animal
        """
        apply_guardrail_template_request = openapi_server.ApplyGuardrailTemplateRequest()
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/guardrails/apply-template',
            method='POST',
            headers=headers,
            data=json.dumps(apply_guardrail_template_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_create_guardrail(self):
        """Test case for create_guardrail

        Create new guardrail
        """
        guardrail_input = {"keywords":["keywords","keywords","keywords","keywords","keywords"],"examples":{"bad":["bad","bad"],"good":["good","good"]},"name":"name","isGlobal":False,"rule":"rule","description":"description","type":"ALWAYS","category":"content_safety","priority":8,"isActive":True}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/guardrails',
            method='POST',
            headers=headers,
            data=json.dumps(guardrail_input),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_guardrail(self):
        """Test case for delete_guardrail

        Delete guardrail (soft delete)
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/guardrails/{guardrail_id}'.format(guardrail_id='guardrail_id_example'),
            method='DELETE',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_animal_effective_guardrails(self):
        """Test case for get_animal_effective_guardrails

        Get effective guardrails for an animal
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/animal/{animal_id}/guardrails/effective'.format(animal_id='animal_id_example'),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_animal_system_prompt(self):
        """Test case for get_animal_system_prompt

        Get system prompt with guardrails
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/animal/{animal_id}/system-prompt'.format(animal_id='animal_id_example'),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_guardrail(self):
        """Test case for get_guardrail

        Get specific guardrail
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/guardrails/{guardrail_id}'.format(guardrail_id='guardrail_id_example'),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_guardrail_templates(self):
        """Test case for get_guardrail_templates

        Get pre-built guardrail templates
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/guardrails/templates',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_list_guardrails(self):
        """Test case for list_guardrails

        List all guardrails
        """
        query_string = [('category', 'category_example'),
                        ('isActive', True),
                        ('isGlobal', True)]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/guardrails',
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_guardrail(self):
        """Test case for update_guardrail

        Update guardrail
        """
        guardrail_update = {"keywords":["keywords","keywords","keywords","keywords","keywords"],"examples":{"bad":["bad","bad"],"good":["good","good"]},"name":"name","description":"description","category":"content_safety","priority":8,"isActive":True}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/guardrails/{guardrail_id}'.format(guardrail_id='guardrail_id_example'),
            method='PATCH',
            headers=headers,
            data=json.dumps(guardrail_update),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
