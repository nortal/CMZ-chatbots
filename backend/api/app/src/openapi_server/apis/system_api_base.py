# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from openapi_server.models.feature_flags_document import FeatureFlagsDocument
from openapi_server.models.feature_flags_update import FeatureFlagsUpdate
from openapi_server.models.system_health import SystemHealth
from openapi_server.security_api import get_token_bearerAuth

class BaseSystemApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseSystemApi.subclasses = BaseSystemApi.subclasses + (cls,)
    async def feature_flags_get(
        self,
    ) -> FeatureFlagsDocument:
        ...


    async def feature_flags_patch(
        self,
        feature_flags_update: FeatureFlagsUpdate,
    ) -> FeatureFlagsDocument:
        ...


    async def system_health_get(
        self,
    ) -> SystemHealth:
        ...
