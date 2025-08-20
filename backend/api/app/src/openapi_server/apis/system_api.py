# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from openapi_server.apis.system_api_base import BaseSystemApi
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
from openapi_server.models.feature_flags_document import FeatureFlagsDocument
from openapi_server.models.feature_flags_update import FeatureFlagsUpdate
from openapi_server.models.system_health import SystemHealth
from openapi_server.security_api import get_token_bearerAuth

router = APIRouter()

ns_pkg = openapi_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/feature_flags",
    responses={
        200: {"model": FeatureFlagsDocument, "description": "All flags"},
    },
    tags=["System"],
    summary="Get feature flags",
    response_model_by_alias=True,
)
async def feature_flags_get(
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> FeatureFlagsDocument:
    if not BaseSystemApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseSystemApi.subclasses[0]().feature_flags_get()


@router.patch(
    "/feature_flags",
    responses={
        200: {"model": FeatureFlagsDocument, "description": "Updated flags"},
    },
    tags=["System"],
    summary="Update feature flags",
    response_model_by_alias=True,
)
async def feature_flags_patch(
    feature_flags_update: FeatureFlagsUpdate = Body(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> FeatureFlagsDocument:
    if not BaseSystemApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseSystemApi.subclasses[0]().feature_flags_patch(feature_flags_update)


@router.get(
    "/system_health",
    responses={
        200: {"model": SystemHealth, "description": "Health details"},
    },
    tags=["System"],
    summary="System/health check for status page",
    response_model_by_alias=True,
)
async def system_health_get(
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> SystemHealth:
    if not BaseSystemApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseSystemApi.subclasses[0]().system_health_get()
