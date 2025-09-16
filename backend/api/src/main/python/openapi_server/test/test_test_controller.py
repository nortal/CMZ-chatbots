import unittest

from flask import json

from openapi_server.models.test_stress_body201_response import TestStressBody201Response  # noqa: E501
from openapi_server.models.test_stress_body_request import TestStressBodyRequest  # noqa: E501
from openapi_server.test import BaseTestCase


class TestTestController(BaseTestCase):
    """TestController integration test stubs"""

    def test_test_stress_body(self):
        """Test case for test_stress_body

        Test endpoint for body parameter validation
        """
        test_stress_body_request = openapi_server.TestStressBodyRequest()
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/test/stress/body',
            method='POST',
            headers=headers,
            data=json.dumps(test_stress_body_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
