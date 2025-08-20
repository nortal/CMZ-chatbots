# coding: utf-8

from fastapi.testclient import TestClient


from datetime import datetime  # noqa: F401
from pydantic import Field, StrictStr, field_validator  # noqa: F401
from typing import Optional  # noqa: F401
from typing_extensions import Annotated  # noqa: F401
from openapi_server.models.billing_summary import BillingSummary  # noqa: F401
from openapi_server.models.paged_logs import PagedLogs  # noqa: F401
from openapi_server.models.performance_metrics import PerformanceMetrics  # noqa: F401


def test_billing_get(client: TestClient):
    """Test case for billing_get

    Billing summary
    """
    params = [("period", 'period_example')]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/billing",
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_logs_get(client: TestClient):
    """Test case for logs_get

    Application logs (paged/filtered)
    """
    params = [("level", 'level_example'),     ("start", '2013-10-20T19:20:30+01:00'),     ("end", '2013-10-20T19:20:30+01:00'),     ("page", 1),     ("page_size", 200)]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/logs",
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_performance_metrics_get(client: TestClient):
    """Test case for performance_metrics_get

    Performance metrics between dates
    """
    params = [("start", '2013-10-20T19:20:30+01:00'),     ("end", '2013-10-20T19:20:30+01:00')]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/performance_metrics",
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

