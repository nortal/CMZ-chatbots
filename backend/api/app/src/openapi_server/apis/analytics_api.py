# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from openapi_server.apis.analytics_api_base import BaseAnalyticsApi
import openapi_server.impl

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Response,
    Security,
    status,
)

from openapi_server.models.extra_models import TokenModel  # noqa: F401
from datetime import datetime
from pydantic import Field, StrictStr, field_validator
from typing import Optional
from typing_extensions import Annotated
from openapi_server.models.billing_summary import BillingSummary
from openapi_server.models.paged_logs import PagedLogs
from openapi_server.models.performance_metrics import PerformanceMetrics
from openapi_server.security_api import get_token_bearerAuth

router = APIRouter()

ns_pkg = openapi_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/billing",
    responses={
        200: {"model": BillingSummary, "description": "Billing breakdown"},
    },
    tags=["Analytics"],
    summary="Billing summary",
    response_model_by_alias=True,
)
async def billing_get(
    period: Annotated[Optional[Annotated[str, Field(strict=True)]], Field(description="Billing period (e.g., 2025-08)")] = Query(None, description="Billing period (e.g., 2025-08)", alias="period", regex=r"/^[0-9]{4}-[0-9]{2}$/"),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> BillingSummary:
    if not BaseAnalyticsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseAnalyticsApi.subclasses[0]().billing_get(period)


@router.get(
    "/logs",
    responses={
        200: {"model": PagedLogs, "description": "Paged logs"},
    },
    tags=["Analytics"],
    summary="Application logs (paged/filtered)",
    response_model_by_alias=True,
)
async def logs_get(
    level: Optional[StrictStr] = Query(None, description="", alias="level"),
    start: Optional[datetime] = Query(None, description="", alias="start"),
    end: Optional[datetime] = Query(None, description="", alias="end"),
    page: Optional[Annotated[int, Field(strict=True, ge=1)]] = Query(1, description="", alias="page", ge=1),
    page_size: Optional[Annotated[int, Field(le=1000, strict=True, ge=1)]] = Query(200, description="", alias="pageSize", ge=1, le=1000),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> PagedLogs:
    if not BaseAnalyticsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseAnalyticsApi.subclasses[0]().logs_get(level, start, end, page, page_size)


@router.get(
    "/performance_metrics",
    responses={
        200: {"model": PerformanceMetrics, "description": "Metrics payload"},
    },
    tags=["Analytics"],
    summary="Performance metrics between dates",
    response_model_by_alias=True,
)
async def performance_metrics_get(
    start: Annotated[datetime, Field(description="ISO8601 start (inclusive)")] = Query(None, description="ISO8601 start (inclusive)", alias="start"),
    end: Annotated[datetime, Field(description="ISO8601 end (exclusive)")] = Query(None, description="ISO8601 end (exclusive)", alias="end"),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> PerformanceMetrics:
    if not BaseAnalyticsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseAnalyticsApi.subclasses[0]().performance_metrics_get(start, end)
