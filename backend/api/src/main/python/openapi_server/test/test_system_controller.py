import unittest

from flask import json

from openapi_server.models.feature_flags_document import FeatureFlagsDocument  # noqa: E501
from openapi_server.models.feature_flags_update import FeatureFlagsUpdate  # noqa: E501
from openapi_server.models.system_health import SystemHealth  # noqa: E501
from openapi_server.test import BaseTestCase


class TestSystemController(BaseTestCase):
    """SystemController integration test stubs"""

    def test_feature_flags_get(self):
        """Test case for feature_flags_get

        Get feature flags
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/feature_flags',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_feature_flags_patch(self):
        """Test case for feature_flags_patch

        Update feature flags
        """
        feature_flags_update = {"flags":{"key":{"rollout":0.08008281904610115,"enabled":True}}}
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.client.open(
            '/feature_flags',
            method='PATCH',
            headers=headers,
            data=json.dumps(feature_flags_update),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_system_health_get(self):
        """Test case for system_health_get

        System/health check for status page
        """
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/system_health',
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
