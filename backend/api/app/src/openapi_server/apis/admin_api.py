# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from openapi_server.apis.admin_api_base import BaseAdminApi
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
from pydantic import Field, StrictBool, StrictStr, field_validator
from typing import Any, Optional
from typing_extensions import Annotated
from openapi_server.models.error import Error
from openapi_server.models.paged_users import PagedUsers
from openapi_server.models.user import User
from openapi_server.models.user_details import UserDetails
from openapi_server.models.userrole_patch_request import UserrolePatchRequest
from openapi_server.security_api import get_token_bearerAuth

router = APIRouter()

ns_pkg = openapi_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.delete(
    "/user",
    responses={
        204: {"description": "Deleted"},
        404: {"model": Error, "description": "Resource not found"},
    },
    tags=["Admin"],
    summary="Delete user",
    response_model_by_alias=True,
)
async def user_delete(
    id: StrictStr = Query(None, description="", alias="id"),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> None:
    if not BaseAdminApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseAdminApi.subclasses[0]().user_delete(id)


@router.get(
    "/userdetails",
    responses={
        200: {"model": UserDetails, "description": "User details"},
        404: {"model": Error, "description": "Resource not found"},
    },
    tags=["Admin"],
    summary="Fetch specific user details",
    response_model_by_alias=True,
)
async def userdetails_get(
    id: StrictStr = Query(None, description="", alias="id"),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> UserDetails:
    if not BaseAdminApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseAdminApi.subclasses[0]().userdetails_get(id)


@router.get(
    "/userlist",
    responses={
        200: {"model": PagedUsers, "description": "Paged user list"},
    },
    tags=["Admin"],
    summary="List users",
    response_model_by_alias=True,
)
async def userlist_get(
    details: Optional[StrictBool] = Query(False, description="", alias="details"),
    role: Optional[StrictStr] = Query(None, description="", alias="role"),
    page: Optional[Annotated[int, Field(strict=True, ge=1)]] = Query(1, description="", alias="page", ge=1),
    page_size: Optional[Annotated[int, Field(le=200, strict=True, ge=1)]] = Query(50, description="", alias="pageSize", ge=1, le=200),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> PagedUsers:
    if not BaseAdminApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseAdminApi.subclasses[0]().userlist_get(details, role, page, page_size)


@router.patch(
    "/userrole",
    responses={
        200: {"model": User, "description": "Updated user"},
    },
    tags=["Admin"],
    summary="Change user role",
    response_model_by_alias=True,
)
async def userrole_patch(
    userrole_patch_request: UserrolePatchRequest = Body(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> User:
    if not BaseAdminApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseAdminApi.subclasses[0]().userrole_patch(userrole_patch_request)
