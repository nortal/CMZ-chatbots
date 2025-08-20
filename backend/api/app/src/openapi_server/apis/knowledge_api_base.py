# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import StrictStr
from typing import Any
from openapi_server.models.error import Error
from openapi_server.models.knowledge_article import KnowledgeArticle
from openapi_server.models.knowledge_create import KnowledgeCreate
from openapi_server.security_api import get_token_bearerAuth

class BaseKnowledgeApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseKnowledgeApi.subclasses = BaseKnowledgeApi.subclasses + (cls,)
    async def knowledge_article_delete(
        self,
        id: StrictStr,
    ) -> None:
        ...


    async def knowledge_article_get(
        self,
        id: StrictStr,
    ) -> KnowledgeArticle:
        ...


    async def knowledge_article_post(
        self,
        knowledge_create: KnowledgeCreate,
    ) -> KnowledgeArticle:
        ...
