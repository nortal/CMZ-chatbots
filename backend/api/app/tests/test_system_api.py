# coding: utf-8

from fastapi.testclient import TestClient


from openapi_server.models.feature_flags_document import FeatureFlagsDocument  # noqa: F401
from openapi_server.models.feature_flags_update import FeatureFlagsUpdate  # noqa: F401
from openapi_server.models.system_health import SystemHealth  # noqa: F401


def test_feature_flags_get(client: TestClient):
    """Test case for feature_flags_get

    Get feature flags
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/feature_flags",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_feature_flags_patch(client: TestClient):
    """Test case for feature_flags_patch

    Update feature flags
    """
    feature_flags_update = {"flags":{"key":{"rollout":0.08008281904610115,"enabled":1}}}

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "PATCH",
    #    "/feature_flags",
    #    headers=headers,
    #    json=feature_flags_update,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200


def test_system_health_get(client: TestClient):
    """Test case for system_health_get

    System/health check for status page
    """

    headers = {
        "Authorization": "Bearer special-key",
    }
    # uncomment below to make a request
    #response = client.request(
    #    "GET",
    #    "/system_health",
    #    headers=headers,
    #)

    # uncomment below to assert the status code of the HTTP response
    #assert response.status_code == 200

