import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.feature_flags_document import FeatureFlagsDocument  # noqa: E501
from openapi_server.models.feature_flags_update import FeatureFlagsUpdate  # noqa: E501
from openapi_server.models.system_health import SystemHealth  # noqa: E501
from openapi_server import util


def feature_flags_get():  # noqa: E501
    """Get feature flags

     # noqa: E501


    :rtype: Union[FeatureFlagsDocument, Tuple[FeatureFlagsDocument, int], Tuple[FeatureFlagsDocument, int, Dict[str, str]]
    """
    # System functionality not yet implemented
    return {"code": "not_implemented", "message": "System functionality not yet implemented"}, 501


def feature_flags_patch(body):  # noqa: E501
    """Update feature flags

     # noqa: E501

    :param feature_flags_update: 
    :type feature_flags_update: dict | bytes

    :rtype: Union[FeatureFlagsDocument, Tuple[FeatureFlagsDocument, int], Tuple[FeatureFlagsDocument, int, Dict[str, str]]
    """
    feature_flags_update = body
    if connexion.request.is_json:
        feature_flags_update = FeatureFlagsUpdate.from_dict(connexion.request.get_json())  # noqa: E501
    # System functionality not yet implemented
    return {"code": "not_implemented", "message": "System functionality not yet implemented"}, 501


def system_health_get():  # noqa: E501
    """System/health check for status page

     # noqa: E501


    :rtype: Union[SystemHealth, Tuple[SystemHealth, int], Tuple[SystemHealth, int, Dict[str, str]]
    """
    # System functionality not yet implemented
    return {"code": "not_implemented", "message": "System functionality not yet implemented"}, 501
