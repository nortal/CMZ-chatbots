# coding: utf-8

from fastapi.testclient import TestClient


from pydantic import StrictStr  # noqa: F401
from typing import Any, List  # noqa: F401
from openapi_server.models.animal import Animal  # noqa: F401
from openapi_server.models.animal_config import AnimalConfig  # noqa: F401
from openapi_server.models.animal_config_update import AnimalConfigUpdate  # noqa: F401
from openapi_server.models.animal_details import AnimalDetails  # noqa: F401
from openapi_server.models.error import Error  # noqa: F401


def test_animal_config_get(client: TestClient):
    """Test case for animal_config_get

    Get animal configuration
    """
    params = [("animalid", 'animalid_example')]
    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/animal_config",
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_animal_config_patch(client: TestClient):
    """Test case for animal_config_patch

    Update animal configuration
    """
    animal_config_update = {"voice":"voice","deleted":{"at":"2000-01-23T04:56:07.000+00:00","by":{"display_name":"displayName","id":"id","email":"email"}},"personality":"personality","soft_delete":0,"created":{"at":"2000-01-23T04:56:07.000+00:00","by":{"display_name":"displayName","id":"id","email":"email"}},"temperature":0.1601656380922023,"tools_enabled":["toolsEnabled","toolsEnabled"],"guardrails":{"key":""},"modified":{"at":"2000-01-23T04:56:07.000+00:00","by":{"display_name":"displayName","id":"id","email":"email"}},"ai_model":"aiModel","top_p":0.6027456183070403}
    params = [("animalid", 'animalid_example')]
    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "PATCH",
    #    "/animal_config",
    #    headers=headers,
    #    json=animal_config_update,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_animal_details_get(client: TestClient):
    """Test case for animal_details_get

    Fetch animal details
    """
    params = [("animalid", 'animalid_example')]
    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/animal_details",
    #    headers=headers,
    #    params=params,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_animal_list_get(client: TestClient):
    """Test case for animal_list_get

    List animals
    """

    headers = {
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/animal_list",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

