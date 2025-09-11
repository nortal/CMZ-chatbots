import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.feature_flags_document import FeatureFlagsDocument  # noqa: E501
from openapi_server.models.feature_flags_update import FeatureFlagsUpdate  # noqa: E501
from openapi_server.models.feature_flags_value import FeatureFlagsValue  # noqa: E501
from openapi_server.models.system_health import SystemHealth  # noqa: E501
from openapi_server.models.system_health_checks_inner import SystemHealthChecksInner  # noqa: E501
from openapi_server.models.error import Error  # noqa: E501
from openapi_server import util
from datetime import datetime

# In-memory storage for feature flags (in production, this would be in a database)
_feature_flags_store = {
    "chatbot_ai_response": FeatureFlagsValue(enabled=True, rollout=1.0),
    "advanced_analytics": FeatureFlagsValue(enabled=False, rollout=0.0),
    "multi_animal_conversations": FeatureFlagsValue(enabled=True, rollout=0.5),
    "voice_synthesis": FeatureFlagsValue(enabled=False, rollout=0.1),
    "educational_games": FeatureFlagsValue(enabled=True, rollout=0.8)
}

def feature_flags_get():  # noqa: E501
    """Get feature flags

     # noqa: E501


    :rtype: Union[FeatureFlagsDocument, Tuple[FeatureFlagsDocument, int], Tuple[FeatureFlagsDocument, int, Dict[str, str]]
    """
    try:
        # Create audit timestamps
        now = datetime.utcnow().isoformat() + 'Z'
        
        # Create the feature flags document
        return FeatureFlagsDocument(
            flags=_feature_flags_store.copy(),
            created={"at": now, "by": {"userId": "system"}},
            modified={"at": now, "by": {"userId": "system"}},
            deleted=None,
            soft_delete=False
        )
    except Exception as e:
        return Error(code='INTERNAL_ERROR', message=str(e)), 500


def feature_flags_patch(body):  # noqa: E501
    """Update feature flags

     # noqa: E501

    :param feature_flags_update: 
    :type feature_flags_update: dict | bytes

    :rtype: Union[FeatureFlagsDocument, Tuple[FeatureFlagsDocument, int], Tuple[FeatureFlagsDocument, int, Dict[str, str]]
    """
    try:
        feature_flags_update = body
        if connexion.request.is_json:
            feature_flags_update = FeatureFlagsUpdate.from_dict(connexion.request.get_json())  # noqa: E501
        
        # Update the feature flags store with new values
        if hasattr(feature_flags_update, 'flags') and feature_flags_update.flags:
            _feature_flags_store.update(feature_flags_update.flags)
        
        # Return the updated feature flags document
        now = datetime.utcnow().isoformat() + 'Z'
        
        return FeatureFlagsDocument(
            flags=_feature_flags_store.copy(),
            created={"at": now, "by": {"userId": "system"}},
            modified={"at": now, "by": {"userId": "system"}},
            deleted=None,
            soft_delete=False
        )
    except Exception as e:
        return Error(code='INTERNAL_ERROR', message=str(e)), 500


def system_health_get():  # noqa: E501
    """System/health check for status page

     # noqa: E501


    :rtype: Union[SystemHealth, Tuple[SystemHealth, int], Tuple[SystemHealth, int, Dict[str, str]]
    """
    try:
        checks = []
        overall_status = "ok"
        
        # Check 1: Database connectivity (DynamoDB)
        try:
            from openapi_server.impl.utils.orm.store import get_store
            import os
            
            # Test DynamoDB connectivity by trying to access a known table
            table_name = os.getenv("ANIMAL_DYNAMO_TABLE_NAME", "quest-dev-animal")
            pk_name = os.getenv("ANIMAL_DYNAMO_PK_NAME", "animalId")
            store = get_store(table_name, pk_name)
            
            # Perform a simple table operation
            store.list(limit=1)  # Just check if we can connect
            
            checks.append(SystemHealthChecksInner(
                name="DynamoDB", 
                status="ok", 
                detail="Connection successful"
            ))
        except Exception as e:
            checks.append(SystemHealthChecksInner(
                name="DynamoDB", 
                status="fail", 
                detail=f"Connection failed: {str(e)[:100]}"
            ))
            overall_status = "degraded"
        
        # Check 2: Application status
        checks.append(SystemHealthChecksInner(
            name="Application", 
            status="ok", 
            detail="Flask application running"
        ))
        
        # Check 3: Environment configuration
        import os
        required_env_vars = [
            "ANIMAL_DYNAMO_TABLE_NAME",
            "USER_DYNAMO_TABLE_NAME", 
            "FAMILY_DYNAMO_TABLE_NAME"
        ]
        
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        
        if missing_vars:
            checks.append(SystemHealthChecksInner(
                name="Configuration",
                status="warn",
                detail=f"Missing env vars: {', '.join(missing_vars)}"
            ))
            if overall_status == "ok":
                overall_status = "degraded"
        else:
            checks.append(SystemHealthChecksInner(
                name="Configuration",
                status="ok",
                detail="All required environment variables present"
            ))
        
        return SystemHealth(status=overall_status, checks=checks)
        
    except Exception as e:
        return Error(code='INTERNAL_ERROR', message=str(e)), 500
