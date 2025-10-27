import unittest

from flask import json

from openapi_server.models.error import Error  # noqa: E501
from openapi_server.models.privacy_audit_get200_response import PrivacyAuditGet200Response  # noqa: E501
from openapi_server.models.privacy_children_get200_response import PrivacyChildrenGet200Response  # noqa: E501
from openapi_server.models.privacy_delete_user200_response import PrivacyDeleteUser200Response  # noqa: E501
from openapi_server.models.privacy_delete_user_request import PrivacyDeleteUserRequest  # noqa: E501
from openapi_server.models.privacy_export_post200_response import PrivacyExportPost200Response  # noqa: E501
from openapi_server.models.privacy_export_post_request import PrivacyExportPostRequest  # noqa: E501
from openapi_server.test import BaseTestCase


class TestPrivacyController(BaseTestCase):
    """PrivacyController integration test stubs"""

    def test_privacy_audit_get(self):
        """Test case for privacy_audit_get

        Get privacy audit log for user data access
        """
        query_string = [('userId', 'user_id_example'),
                        ('parentId', 'parent_id_example'),
                        ('startDate', '2013-10-20T19:20:30+01:00'),
                        ('endDate', '2013-10-20T19:20:30+01:00'),
                        ('actionType', 'action_type_example')]
        headers = { 
            'Accept': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/api/v1/privacy/audit',
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_privacy_children_get(self):
        """Test case for privacy_children_get

        Get summary of children's data for parent dashboard
        """
        headers = { 
            'Accept': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/api/v1/privacy/children/{parent_id}'.format(parent_id='parent_id_example'),
            method='GET',
            headers=headers)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_privacy_delete_user(self):
        """Test case for privacy_delete_user

        Delete user data with GDPR/COPPA compliance
        """
        privacy_delete_user_request = openapi_server.PrivacyDeleteUserRequest()
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/api/v1/privacy/delete/{user_id}'.format(user_id='user_id_example'),
            method='DELETE',
            headers=headers,
            data=json.dumps(privacy_delete_user_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_privacy_export_post(self):
        """Test case for privacy_export_post

        Export user data for GDPR/COPPA compliance
        """
        privacy_export_post_request = openapi_server.PrivacyExportPostRequest()
        headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer special-key',
        }
        response = self.client.open(
            '/api/v1/privacy/export/{user_id}'.format(user_id='user_id_example'),
            method='POST',
            headers=headers,
            data=json.dumps(privacy_export_post_request),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
