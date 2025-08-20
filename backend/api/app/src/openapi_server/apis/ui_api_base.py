# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from openapi_server.models.admin_shell import AdminShell
from openapi_server.models.member_shell import MemberShell
from openapi_server.models.public_home import PublicHome
from openapi_server.security_api import get_token_bearerAuth

class BaseUIApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseUIApi.subclasses = BaseUIApi.subclasses + (cls,)
    async def admin_get(
        self,
    ) -> AdminShell:
        ...


    async def member_get(
        self,
    ) -> MemberShell:
        ...


    async def root_get(
        self,
    ) -> PublicHome:
        ...
