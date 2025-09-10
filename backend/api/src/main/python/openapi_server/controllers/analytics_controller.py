import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.billing_summary import BillingSummary  # noqa: E501
from openapi_server.models.paged_logs import PagedLogs  # noqa: E501
from openapi_server.models.performance_metrics import PerformanceMetrics  # noqa: E501
from openapi_server import util


def billing_get(period=None):  # noqa: E501
    """Billing summary

     # noqa: E501

    :param period: Billing period (e.g., 2025-08)
    :type period: str

    :rtype: Union[BillingSummary, Tuple[BillingSummary, int], Tuple[BillingSummary, int, Dict[str, str]]
    """
    from openapi_server.impl.analytics import handle_billing
    return handle_billing(period)


def logs_get(level=None, start=None, end=None, page=None, page_size=None):  # noqa: E501
    """Application logs (paged/filtered)

     # noqa: E501

    :param level: 
    :type level: str
    :param start: 
    :type start: str
    :param end: 
    :type end: str
    :param page: 
    :type page: int
    :param page_size: 
    :type page_size: int

    :rtype: Union[PagedLogs, Tuple[PagedLogs, int], Tuple[PagedLogs, int, Dict[str, str]]
    """
    from openapi_server.impl.analytics import handle_logs
    return handle_logs(level, start, end, page, page_size)


def performance_metrics_get(start, end):  # noqa: E501
    """Performance metrics between dates

     # noqa: E501

    :param start: ISO8601 start (inclusive)
    :type start: str
    :param end: ISO8601 end (exclusive)
    :type end: str

    :rtype: Union[PerformanceMetrics, Tuple[PerformanceMetrics, int], Tuple[PerformanceMetrics, int, Dict[str, str]]
    """
    from openapi_server.impl.analytics import handle_performance_metrics
    return handle_performance_metrics(start, end)
