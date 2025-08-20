# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import StrictBytes, StrictStr
from typing import Any, Optional, Tuple, Union
from openapi_server.models.error import Error
from openapi_server.models.media import Media
from openapi_server.security_api import get_token_bearerAuth

class BaseMediaApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseMediaApi.subclasses = BaseMediaApi.subclasses + (cls,)
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


    async def upload_media_post(
        self,
        file: Union[StrictBytes, StrictStr, Tuple[StrictStr, StrictBytes]],
        title: Optional[StrictStr],
        animalid: Optional[StrictStr],
    ) -> Media:
        ...
