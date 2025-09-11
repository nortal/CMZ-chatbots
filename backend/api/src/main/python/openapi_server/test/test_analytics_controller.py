import unittest

from flask import json

from openapi_server.models.billing_summary import BillingSummary  # noqa: E501
from openapi_server.models.paged_logs import PagedLogs  # noqa: E501
from openapi_server.models.performance_metrics import PerformanceMetrics  # noqa: E501
from openapi_server.test import BaseTestCase


class TestAnalyticsController(BaseTestCase):
    """AnalyticsController integration test stubs"""

    def test_billing_get(self):
        """Test case for billing_get

        Billing summary
        """
        query_string = [('period', 'period_example')]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/billing',
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_logs_get(self):
        """Test case for logs_get

        Application logs (paged/filtered)
        """
        query_string = [('level', 'level_example'),
                        ('start', '2013-10-20T19:20:30+01:00'),
                        ('end', '2013-10-20T19:20:30+01:00'),
                        ('page', 1),
                        ('pageSize', 200)]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/logs',
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_performance_metrics_get(self):
        """Test case for performance_metrics_get

        Performance metrics between dates
        """
        query_string = [('start', '2013-10-20T19:20:30+01:00'),
                        ('end', '2013-10-20T19:20:30+01:00')]
        headers = { 
            'Accept': 'application/json',
        }
        response = self.client.open(
            '/performance_metrics',
            method='GET',
            headers=headers,
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main()
