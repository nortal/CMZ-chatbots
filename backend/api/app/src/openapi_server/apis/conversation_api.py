# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from openapi_server.apis.conversation_api_base import BaseConversationApi
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
from pydantic import Field, StrictStr
from typing import Any, Optional
from typing_extensions import Annotated
from openapi_server.models.convo_history import ConvoHistory
from openapi_server.models.convo_turn_request import ConvoTurnRequest
from openapi_server.models.convo_turn_response import ConvoTurnResponse
from openapi_server.models.error import Error
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
    if not BaseConversationApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseConversationApi.subclasses[0]().convo_history_delete(id)


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
    if not BaseConversationApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseConversationApi.subclasses[0]().convo_history_get(animalid, userid, limit)


@router.post(
    "/convo_turn",
    responses={
        200: {"model": ConvoTurnResponse, "description": "AI response and turn metadata"},
    },
    tags=["Conversation"],
    summary="Send a conversation turn and get AI reply",
    response_model_by_alias=True,
)
async def convo_turn_post(
    convo_turn_request: ConvoTurnRequest = Body(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> ConvoTurnResponse:
    if not BaseConversationApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseConversationApi.subclasses[0]().convo_turn_post(convo_turn_request)


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
    if not BaseConversationApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseConversationApi.subclasses[0]().summarize_convo_post(summarize_request)
