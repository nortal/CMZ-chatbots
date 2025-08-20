# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from datetime import datetime
from pydantic import Field, StrictStr, field_validator
from typing import Optional
from typing_extensions import Annotated
from openapi_server.models.billing_summary import BillingSummary
from openapi_server.models.paged_logs import PagedLogs
from openapi_server.models.performance_metrics import PerformanceMetrics
from openapi_server.security_api import get_token_bearerAuth

class BaseAnalyticsApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseAnalyticsApi.subclasses = BaseAnalyticsApi.subclasses + (cls,)
    async def billing_get(
        self,
        period: Annotated[Optional[Annotated[str, Field(strict=True)]], Field(description="Billing period (e.g., 2025-08)")],
    ) -> BillingSummary:
        ...


    async def logs_get(
        self,
        level: Optional[StrictStr],
        start: Optional[datetime],
        end: Optional[datetime],
        page: Optional[Annotated[int, Field(strict=True, ge=1)]],
        page_size: Optional[Annotated[int, Field(le=1000, strict=True, ge=1)]],
    ) -> PagedLogs:
        ...


    async def performance_metrics_get(
        self,
        start: Annotated[datetime, Field(description="ISO8601 start (inclusive)")],
        end: Annotated[datetime, Field(description="ISO8601 end (exclusive)")],
    ) -> PerformanceMetrics:
        ...
