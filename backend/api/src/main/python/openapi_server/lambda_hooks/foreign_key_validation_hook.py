"""
Lambda hook for foreign key validation command
PR003946-73: Enables foreign key validation from Lambda functions
"""

import json
import logging
from typing import Dict, Any

from openapi_server.impl.commands.foreign_key_validation import execute_foreign_key_validation

log = logging.getLogger(__name__)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for foreign key validation.
    
    Expected event structure:
    {
        "entity_type": "user|family|animal|conversation",
        "entity_data": {...},
        "audit_user": "optional_user_id"
    }
    
    Returns:
    {
        "statusCode": 200,
        "body": {...}
    }
    """
    try:
        # Extract parameters from event
        entity_type = event.get('entity_type')
        entity_data = event.get('entity_data', {})
        audit_user = event.get('audit_user')
        
        if not entity_type:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "code": "validation_error",
                    "message": "Missing required parameter: entity_type"
                })
            }
        
        # Execute validation command
        result, status_code = execute_foreign_key_validation(
            entity_type=entity_type,
            entity_data=entity_data,
            audit_user=audit_user
        )
        
        return {
            "statusCode": status_code,
            "body": json.dumps(result)
        }
        
    except Exception as e:
        log.error(f"Foreign key validation hook failed: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "code": "INTERNAL_ERROR",
                "message": f"Validation failed: {str(e)}"
            })
        }