# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from openapi_server.apis.ui_api_base import BaseUIApi
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
from openapi_server.models.admin_shell import AdminShell
from openapi_server.models.member_shell import MemberShell
from openapi_server.models.public_home import PublicHome
from openapi_server.security_api import get_token_bearerAuth

router = APIRouter()

ns_pkg = openapi_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/admin",
    responses={
        200: {"model": AdminShell, "description": "Admin shell data/widgets"},
    },
    tags=["UI"],
    summary="Admin dashboard shell data",
    response_model_by_alias=True,
)
async def admin_get(
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> AdminShell:
    if not BaseUIApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseUIApi.subclasses[0]().admin_get()


@router.get(
    "/member",
    responses={
        200: {"model": MemberShell, "description": "Portal shell data/widgets"},
    },
    tags=["UI"],
    summary="User portal shell data",
    response_model_by_alias=True,
)
async def member_get(
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> MemberShell:
    if not BaseUIApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseUIApi.subclasses[0]().member_get()


@router.get(
    "/",
    responses={
        200: {"model": PublicHome, "description": "Health/info banner"},
    },
    tags=["UI"],
    summary="Public homepage",
    response_model_by_alias=True,
)
async def root_get(
) -> PublicHome:
    if not BaseUIApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseUIApi.subclasses[0]().root_get()
