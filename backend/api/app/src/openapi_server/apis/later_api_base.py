# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import Field, StrictBytes, StrictStr
from typing import Any, Optional, Tuple, Union
from typing_extensions import Annotated
from openapi_server.models.convo_history import ConvoHistory
from openapi_server.models.error import Error
from openapi_server.models.media import Media
from openapi_server.models.summarize_request import SummarizeRequest
from openapi_server.models.summary import Summary
from openapi_server.security_api import get_token_bearerAuth

class BaseLaterApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseLaterApi.subclasses = BaseLaterApi.subclasses + (cls,)
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


    async def media_delete(
        self,
        id: StrictStr,
    ) -> None:
        ...


    async def media_get(
        self,
        id: StrictStr,
    ) -> Media:
        ...


    async def summarize_convo_post(
        self,
        summarize_request: SummarizeRequest,
    ) -> Summary:
        ...


    async def upload_media_post(
        self,
        file: Union[StrictBytes, StrictStr, Tuple[StrictStr, StrictBytes]],
        title: Optional[StrictStr],
        animalid: Optional[StrictStr],
    ) -> Media:
        ...
