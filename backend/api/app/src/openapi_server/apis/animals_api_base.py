# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import StrictStr
from typing import Any, List
from openapi_server.models.animal import Animal
from openapi_server.models.animal_config import AnimalConfig
from openapi_server.models.animal_config_update import AnimalConfigUpdate
from openapi_server.models.animal_details import AnimalDetails
from openapi_server.models.error import Error
from openapi_server.security_api import get_token_bearerAuth

class BaseAnimalsApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseAnimalsApi.subclasses = BaseAnimalsApi.subclasses + (cls,)
    async def animal_config_get(
        self,
        animalid: StrictStr,
    ) -> AnimalConfig:
        ...


    async def animal_config_patch(
        self,
        animalid: StrictStr,
        animal_config_update: AnimalConfigUpdate,
    ) -> object:
        ...


    async def animal_details_get(
        self,
        animalid: StrictStr,
    ) -> AnimalDetails:
        ...


    async def animal_list_get(
        self,
    ) -> List[Animal]:
        ...
