# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from openapi_server.apis.media_api_base import BaseMediaApi
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
from pydantic import StrictBytes, StrictStr
from typing import Any, Optional, Tuple, Union
from openapi_server.models.error import Error
from openapi_server.models.media import Media
from openapi_server.security_api import get_token_bearerAuth

router = APIRouter()

ns_pkg = openapi_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.delete(
    "/media",
    responses={
        204: {"description": "Deleted"},
    },
    tags=["Media","Later"],
    summary="Delete media by id (backlog)",
    response_model_by_alias=True,
)
async def media_delete(
    id: StrictStr = Query(None, description="", alias="id"),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> None:
    if not BaseMediaApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseMediaApi.subclasses[0]().media_delete(id)


@router.get(
    "/media",
    responses={
        200: {"model": Media, "description": "Media metadata"},
        404: {"model": Error, "description": "Resource not found"},
    },
    tags=["Media","Later"],
    summary="Fetch media by id (backlog)",
    response_model_by_alias=True,
)
async def media_get(
    id: StrictStr = Query(None, description="", alias="id"),
) -> Media:
    if not BaseMediaApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseMediaApi.subclasses[0]().media_get(id)


@router.post(
    "/upload_media",
    responses={
        201: {"model": Media, "description": "Media created"},
    },
    tags=["Media","Later"],
    summary="Upload media (image/audio/video) (backlog)",
    response_model_by_alias=True,
)
async def upload_media_post(
    file: Union[StrictBytes, StrictStr, Tuple[StrictStr, StrictBytes]] = Form(None, description=""),
    title: Optional[StrictStr] = Form(None, description=""),
    animalid: Optional[StrictStr] = Form(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> Media:
    if not BaseMediaApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseMediaApi.subclasses[0]().upload_media_post(file, title, animalid)
