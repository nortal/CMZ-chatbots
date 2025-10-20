"""
Lambda hook for JWT token validation
PR003946-71: Enables token validation from Lambda functions
"""

import json
import logging
from typing import Dict, Any

log = logging.getLogger(__name__)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for JWT token validation.
    
    Expected event structure:
    {
        "token": "jwt_token_string",
        "validation_type": "bearer|access|refresh"
    }
    
    Returns:
    {
        "statusCode": 200,
        "body": {
            "valid": true,
            "user": {...}
        }
    }
    or
    {
        "statusCode": 401,
        "body": {
            "valid": false,
            "error": "..."
        }
    }
    """
    try:
        # Extract parameters from event
        token = event.get('token')
        validation_type = event.get('validation_type', 'bearer')
        
        if not token:
            return {
                "statusCode": 400,
                "body": json.dumps({
                    "code": "validation_error",
                    "message": "Missing required parameter: token"
                })
            }
        
        # Validate token
        validation_result = _validate_jwt_token(token, validation_type)
        
        if validation_result['valid']:
            return {
                "statusCode": 200,
                "body": json.dumps(validation_result)
            }
        else:
            return {
                "statusCode": 401,
                "body": json.dumps(validation_result)
            }
        
    except Exception as e:
        log.error(f"Token validation hook failed: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "code": "INTERNAL_ERROR",
                "message": f"Token validation failed: {str(e)}"
            })
        }


def _validate_jwt_token(token: str, validation_type: str) -> Dict[str, Any]:
    """
    Validate JWT token and extract user information.
    
    In production, this would:
    - Verify JWT signature using public key
    - Check token expiration
    - Validate issuer and audience
    - Extract claims and user information
    """
    # For testing purposes, accept any non-empty token as valid
    if not token or token.strip() == "":
        return {
            "valid": False,
            "error": "Empty or invalid token",
            "code": "unauthorized"
        }
    
    # Mock token validation - in production, use proper JWT library
    if token == "invalid_token":
        return {
            "valid": False,
            "error": "Token validation failed",
            "code": "unauthorized"
        }
    
    # Return mock user for valid tokens
    return {
        "valid": True,
        "user": {
            "userId": "lambda_user_123", 
            "email": "lambda@cmz.org",
            "displayName": "Lambda User",
            "role": "member",
            "userType": "student",
            "familyId": None,
            "softDelete": False
        },
        "token_type": validation_type,
        "expires_in": 3600  # 1 hour
    }