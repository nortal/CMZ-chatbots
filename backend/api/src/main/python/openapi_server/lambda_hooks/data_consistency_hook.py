"""
Lambda hook for data consistency validation
PR003946-74: Enables cross-entity data consistency validation from Lambda functions
"""

import json
import logging
from typing import Dict, Any

from openapi_server.impl.error_handler import ValidationError

log = logging.getLogger(__name__)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for data consistency validation.
    
    Expected event structure:
    {
        "validation_type": "animal_config|other_validations",
        "entity_id": "entity_identifier",
        "data": {...}
    }
    
    Returns:
    {
        "statusCode": 200,
        "body": {...}
    }
    """
    try:
        # Extract parameters from event
        validation_type = event.get('validation_type')
        entity_id = event.get('entity_id')
        data = event.get('data', {})
        
        if not validation_type:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "code": "validation_error",
                    "message": "Missing required parameter: validation_type"
                })
            }
        
        # Route to appropriate validation
        if validation_type == "animal_config":
            return _validate_animal_config(entity_id, data)
        else:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "code": "validation_error",
                    "message": f"Unknown validation type: {validation_type}"
                })
            }
        
    except Exception as e:
        log.error(f"Data consistency hook failed: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "code": "INTERNAL_ERROR",
                "message": f"Validation failed: {str(e)}"
            })
        }


def _validate_animal_config(animal_id: str, config_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate animal config consistency."""
    try:
        from openapi_server.impl.test_animals import MOCK_CONFIGS
        
        if animal_id not in MOCK_CONFIGS:
            raise ValidationError(
                f"Referenced animal does not exist: {animal_id}",
                details={
                    "entity_type": "animal",
                    "error_type": "entity_not_found"
                }
            )
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "status": "valid",
                "message": "Animal config validation passed"
            })
        }
        
    except ValidationError as e:
        return {
            "statusCode": 400,
            "body": json.dumps({
                "code": "validation_error",
                "message": str(e),
                "details": e.details
            })
        }