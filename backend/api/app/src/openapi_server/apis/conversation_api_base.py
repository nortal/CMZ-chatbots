# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

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

class BaseConversationApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseConversationApi.subclasses = BaseConversationApi.subclasses + (cls,)
    async def convo_history_delete(
        self,
        id: Annotated[StrictStr, Field(description="Conversation/session id")],
    ) -> None:
        ...


    async def convo_history_get(
        self,
        animalid: Optional[StrictStr],
        userid: Optional[StrictStr],
        limit: Optional[Annotated[int, Field(le=500, strict=True, ge=1)]],
    ) -> ConvoHistory:
        ...


    async def convo_turn_post(
        self,
        convo_turn_request: ConvoTurnRequest,
    ) -> ConvoTurnResponse:
        ...


    async def summarize_convo_post(
        self,
        summarize_request: SummarizeRequest,
    ) -> Summary:
        ...
