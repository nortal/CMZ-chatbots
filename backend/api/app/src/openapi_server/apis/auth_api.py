# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from openapi_server.apis.auth_api_base import BaseAuthApi
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
from typing import Any
from openapi_server.models.auth_request import AuthRequest
from openapi_server.models.auth_response import AuthResponse
from openapi_server.models.error import Error
from openapi_server.models.password_reset_request import PasswordResetRequest
from openapi_server.security_api import get_token_bearerAuth

router = APIRouter()

ns_pkg = openapi_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.post(
    "/auth/logout",
    responses={
        204: {"description": "Logged out"},
    },
    tags=["Auth"],
    summary="Logout current user (invalidate token/session)",
    response_model_by_alias=True,
)
async def auth_logout_post(
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> None:
    if not BaseAuthApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseAuthApi.subclasses[0]().auth_logout_post()


@router.post(
    "/auth",
    responses={
        200: {"model": AuthResponse, "description": "Auth token"},
        401: {"model": Error, "description": "Unauthorized"},
    },
    tags=["Auth"],
    summary="Login or register",
    response_model_by_alias=True,
)
async def auth_post(
    auth_request: AuthRequest = Body(None, description=""),
) -> AuthResponse:
    if not BaseAuthApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseAuthApi.subclasses[0]().auth_post(auth_request)


@router.post(
    "/auth/refresh",
    responses={
        200: {"model": AuthResponse, "description": "New token"},
    },
    tags=["Auth"],
    summary="Refresh access token",
    response_model_by_alias=True,
)
async def auth_refresh_post(
) -> AuthResponse:
    if not BaseAuthApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseAuthApi.subclasses[0]().auth_refresh_post()


@router.post(
    "/auth/reset_password",
    responses={
        204: {"description": "Email sent if account exists"},
    },
    tags=["Auth"],
    summary="Initiate password reset",
    response_model_by_alias=True,
)
async def auth_reset_password_post(
    password_reset_request: PasswordResetRequest = Body(None, description=""),
) -> None:
    if not BaseAuthApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseAuthApi.subclasses[0]().auth_reset_password_post(password_reset_request)
