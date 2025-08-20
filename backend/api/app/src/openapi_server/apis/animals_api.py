# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from openapi_server.apis.animals_api_base import BaseAnimalsApi
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
from typing import Any, List
from openapi_server.models.animal import Animal
from openapi_server.models.animal_config import AnimalConfig
from openapi_server.models.animal_config_update import AnimalConfigUpdate
from openapi_server.models.animal_details import AnimalDetails
from openapi_server.models.error import Error
from openapi_server.security_api import get_token_bearerAuth

router = APIRouter()

ns_pkg = openapi_server.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/animal_config",
    responses={
        200: {"model": AnimalConfig, "description": "Animal config"},
    },
    tags=["Animals"],
    summary="Get animal configuration",
    response_model_by_alias=True,
)
async def animal_config_get(
    animalid: StrictStr = Query(None, description="", alias="animalid"),
) -> AnimalConfig:
    if not BaseAnimalsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseAnimalsApi.subclasses[0]().animal_config_get(animalid)


@router.patch(
    "/animal_config",
    responses={
        200: {"model": object, "description": "Updated config"},
        400: {"model": Error, "description": "Invalid config"},
    },
    tags=["Animals"],
    summary="Update animal configuration",
    response_model_by_alias=True,
)
async def animal_config_patch(
    animalid: StrictStr = Query(None, description="", alias="animalid"),
    animal_config_update: AnimalConfigUpdate = Body(None, description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
) -> object:
    if not BaseAnimalsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseAnimalsApi.subclasses[0]().animal_config_patch(animalid, animal_config_update)


@router.get(
    "/animal_details",
    responses={
        200: {"model": AnimalDetails, "description": "Animal details"},
        404: {"model": Error, "description": "Resource not found"},
    },
    tags=["Animals"],
    summary="Fetch animal details",
    response_model_by_alias=True,
)
async def animal_details_get(
    animalid: StrictStr = Query(None, description="", alias="animalid"),
) -> AnimalDetails:
    if not BaseAnimalsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseAnimalsApi.subclasses[0]().animal_details_get(animalid)


@router.get(
    "/animal_list",
    responses={
        200: {"model": List[Animal], "description": "List of animals"},
    },
    tags=["Animals"],
    summary="List animals",
    response_model_by_alias=True,
)
async def animal_list_get(
) -> List[Animal]:
    if not BaseAnimalsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseAnimalsApi.subclasses[0]().animal_list_get()
