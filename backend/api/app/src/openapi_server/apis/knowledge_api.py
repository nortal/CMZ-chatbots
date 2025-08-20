# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from openapi_server.apis.knowledge_api_base import BaseKnowledgeApi
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
from pydantic import StrictStr
from typing import Any
from openapi_server.models.error import Error
from openapi_server.models.knowledge_article import KnowledgeArticle
from openapi_server.models.knowledge_create import KnowledgeCreate
from openapi_server.security_api import get_token_bearerAuth

router = APIRouter()

ns_pkg = openapi_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.delete(
    "/knowledge_article",
    responses={
        204: {"description": "Deleted"},
    },
    tags=["Knowledge"],
    summary="Delete knowledge article",
    response_model_by_alias=True,
)
async def knowledge_article_delete(
    id: StrictStr = Query(None, description="", alias="id"),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> None:
    if not BaseKnowledgeApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseKnowledgeApi.subclasses[0]().knowledge_article_delete(id)


@router.get(
    "/knowledge_article",
    responses={
        200: {"model": KnowledgeArticle, "description": "Article"},
        404: {"model": Error, "description": "Resource not found"},
    },
    tags=["Knowledge"],
    summary="Get article by id",
    response_model_by_alias=True,
)
async def knowledge_article_get(
    id: StrictStr = Query(None, description="", alias="id"),
) -> KnowledgeArticle:
    if not BaseKnowledgeApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseKnowledgeApi.subclasses[0]().knowledge_article_get(id)


@router.post(
    "/knowledge_article",
    responses={
        201: {"model": KnowledgeArticle, "description": "Created"},
    },
    tags=["Knowledge"],
    summary="Create knowledge article",
    response_model_by_alias=True,
)
async def knowledge_article_post(
    knowledge_create: KnowledgeCreate = Body(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> KnowledgeArticle:
    if not BaseKnowledgeApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseKnowledgeApi.subclasses[0]().knowledge_article_post(knowledge_create)
