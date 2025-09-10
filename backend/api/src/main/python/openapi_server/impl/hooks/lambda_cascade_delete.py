"""
PR003946-67: Lambda Hook for Cascade Soft-Delete

This module provides AWS Lambda function hooks for cascade delete operations.
Follows hexagonal architecture by using the same command implementation as Flask endpoints.
"""

import json
import logging
from typing import Dict, Any

from openapi_server.impl.commands.cascade_delete import execute_cascade_delete
from openapi_server.impl.error_handler import ValidationError

log = logging.getLogger(__name__)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for cascade delete operations.
    
    Expected event structure:
    {
        "entity_type": "family",
        "entity_id": "family_123",
        "cascade_enabled": true,
        "audit_user": "admin_user_id"
    }
    """
    try:
        # Extract parameters from Lambda event
        entity_type = event.get("entity_type")
        entity_id = event.get("entity_id")
        cascade_enabled = event.get("cascade_enabled", True)
        audit_user = event.get("audit_user", "lambda")
        
        # Validate required parameters
        if not entity_type or not entity_id:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "code": "invalid_request",
                    "message": "Missing required parameters: entity_type, entity_id",
                    "details": {"event": event}
                })
            }
        
        # Execute cascade delete using same command as Flask endpoint
        result, status_code = execute_cascade_delete(
            entity_type=entity_type,
            entity_id=entity_id,
            cascade_enabled=cascade_enabled,
            audit_user=audit_user
        )
        
        response_body = result if result else {"message": "Cascade delete completed"}
        
        return {
            "statusCode": status_code,
            "body": json.dumps(response_body),
            "headers": {
                "Content-Type": "application/json"
            }
        }
        
    except ValidationError as e:
        log.error(f"Lambda cascade delete validation error: {e}")
        return {
            "statusCode": 400,
            "body": json.dumps({
                "code": "validation_error",
                "message": str(e),
                "details": {"event": event}
            })
        }
        
    except Exception as e:
        log.error(f"Lambda cascade delete unexpected error: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "code": "internal_error",
                "message": "An unexpected error occurred during cascade delete",
                "details": {"error_type": type(e).__name__}
            })
        }


def trigger_cascade_delete_lambda(entity_type: str, entity_id: str, cascade_enabled: bool = True, audit_user: str = None) -> Dict[str, Any]:
    """
    Helper function to trigger cascade delete via AWS Lambda from other services.
    
    This can be used by external systems that need to trigger cascade deletes
    without going through the REST API.
    """
    import boto3
    
    lambda_client = boto3.client('lambda')
    
    payload = {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "cascade_enabled": cascade_enabled,
        "audit_user": audit_user
    }
    
    try:
        response = lambda_client.invoke(
            FunctionName='cmz-cascade-delete',  # Adjust function name as needed
            InvocationType='RequestResponse',
            Payload=json.dumps(payload)
        )
        
        result = json.loads(response['Payload'].read())
        return result
        
    except Exception as e:
        log.error(f"Failed to invoke cascade delete Lambda: {e}")
        raise ValidationError(f"Lambda invocation failed: {str(e)}")


# Example usage for testing
def create_test_event(entity_type: str = "family", entity_id: str = "test_family_123") -> Dict[str, Any]:
    """Create a test event for Lambda function testing."""
    return {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "cascade_enabled": True,
        "audit_user": "test_user"
    }


if __name__ == "__main__":
    # Test the Lambda handler locally
    test_event = create_test_event()
    result = lambda_handler(test_event, None)
    print(f"Test result: {json.dumps(result, indent=2)}")