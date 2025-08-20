# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from openapi_server.apis.later_api_base import BaseLaterApi
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
from pydantic import Field, StrictBytes, StrictStr
from typing import Any, Optional, Tuple, Union
from typing_extensions import Annotated
from openapi_server.models.convo_history import ConvoHistory
from openapi_server.models.error import Error
from openapi_server.models.media import Media
from openapi_server.models.summarize_request import SummarizeRequest
from openapi_server.models.summary import Summary
from openapi_server.security_api import get_token_bearerAuth

router = APIRouter()

ns_pkg = openapi_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.delete(
    "/convo_history",
    responses={
        204: {"description": "Deleted"},
        404: {"model": Error, "description": "Resource not found"},
    },
    tags=["Conversation","Later"],
    summary="Delete conversation history (GDPR) (backlog)",
    response_model_by_alias=True,
)
async def convo_history_delete(
    id: Annotated[StrictStr, Field(description="Conversation/session id")] = Query(None, description="Conversation/session id", alias="id"),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> None:
    if not BaseLaterApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseLaterApi.subclasses[0]().convo_history_delete(id)


@router.get(
    "/convo_history",
    responses={
        200: {"model": ConvoHistory, "description": "Conversation turns"},
    },
    tags=["Conversation","Later"],
    summary="Get conversation history (backlog)",
    response_model_by_alias=True,
)
async def convo_history_get(
    animalid: Optional[StrictStr] = Query(None, description="", alias="animalid"),
    userid: Optional[StrictStr] = Query(None, description="", alias="userid"),
    limit: Optional[Annotated[int, Field(le=500, strict=True, ge=1)]] = Query(100, description="", alias="limit", ge=1, le=500),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> ConvoHistory:
    if not BaseLaterApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseLaterApi.subclasses[0]().convo_history_get(animalid, userid, limit)


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
    if not BaseLaterApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseLaterApi.subclasses[0]().media_delete(id)


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
    if not BaseLaterApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseLaterApi.subclasses[0]().media_get(id)


@router.post(
    "/summarize_convo",
    responses={
        200: {"model": Summary, "description": "Summary created"},
    },
    tags=["Conversation","Later"],
    summary="Summarize conversation for personalization/cost control (backlog)",
    response_model_by_alias=True,
)
async def summarize_convo_post(
    summarize_request: SummarizeRequest = Body(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> Summary:
    if not BaseLaterApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseLaterApi.subclasses[0]().summarize_convo_post(summarize_request)


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
    if not BaseLaterApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseLaterApi.subclasses[0]().upload_media_post(file, title, animalid)
