# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from typing import Any
from openapi_server.models.auth_request import AuthRequest
from openapi_server.models.auth_response import AuthResponse
from openapi_server.models.error import Error
from openapi_server.models.password_reset_request import PasswordResetRequest
from openapi_server.security_api import get_token_bearerAuth

class BaseAuthApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseAuthApi.subclasses = BaseAuthApi.subclasses + (cls,)
    async def auth_logout_post(
        self,
    ) -> None:
        ...


    async def auth_post(
        self,
        auth_request: AuthRequest,
    ) -> AuthResponse:
        ...


    async def auth_refresh_post(
        self,
    ) -> AuthResponse:
        ...


    async def auth_reset_password_post(
        self,
        password_reset_request: PasswordResetRequest,
    ) -> None:
        ...
