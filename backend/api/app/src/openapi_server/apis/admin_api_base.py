# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import Field, StrictBool, StrictStr, field_validator
from typing import Any, Optional
from typing_extensions import Annotated
from openapi_server.models.error import Error
from openapi_server.models.paged_users import PagedUsers
from openapi_server.models.user import User
from openapi_server.models.user_details import UserDetails
from openapi_server.models.userrole_patch_request import UserrolePatchRequest
from openapi_server.security_api import get_token_bearerAuth

class BaseAdminApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseAdminApi.subclasses = BaseAdminApi.subclasses + (cls,)
    async def user_delete(
        self,
        id: StrictStr,
    ) -> None:
        ...


    async def userdetails_get(
        self,
        id: StrictStr,
    ) -> UserDetails:
        ...


    async def userlist_get(
        self,
        details: Optional[StrictBool],
        role: Optional[StrictStr],
        page: Optional[Annotated[int, Field(strict=True, ge=1)]],
        page_size: Optional[Annotated[int, Field(le=200, strict=True, ge=1)]],
    ) -> PagedUsers:
        ...


    async def userrole_patch(
        self,
        userrole_patch_request: UserrolePatchRequest,
    ) -> User:
        ...
