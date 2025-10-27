"""AWS Cognito authentication implementation for CMZ Chatbot Platform

This module provides a complete AWS Cognito authentication system following
hexagonal architecture principles with clean separation of concerns.

Features:
- User registration and authentication via Cognito User Pool
- Token validation and refresh
- Role-based authorization with Cognito groups
- Password reset workflows
- Flask and Lambda deployment support
"""
import os
from typing import Dict, Any, Optional

from .domain.cognito_auth_service import CognitoAuthenticationService
from .adapters.audit_service import StandardAuditService


def create_cognito_auth_service() -> CognitoAuthenticationService:
    """
    Create Cognito authentication service with environment configuration
    
    Required environment variables:
    - COGNITO_USER_POOL_ID: Your Cognito User Pool ID
    - COGNITO_CLIENT_ID: Your Cognito App Client ID
    - COGNITO_CLIENT_SECRET: Your Cognito App Client Secret (optional)
    - AWS_REGION: AWS region for Cognito (default: us-west-2)
    
    Optional environment variables:
    - COGNITO_IDENTITY_POOL_ID: For AWS resource access
    """
    # Get configuration from environment
    user_pool_id = os.getenv("COGNITO_USER_POOL_ID")
    client_id = os.getenv("COGNITO_CLIENT_ID")
    client_secret = os.getenv("COGNITO_CLIENT_SECRET")
    identity_pool_id = os.getenv("COGNITO_IDENTITY_POOL_ID")
    region = os.getenv("AWS_REGION", "us-west-2")
    
    # Validate required configuration
    if not user_pool_id or not client_id:
        raise ValueError("COGNITO_USER_POOL_ID and COGNITO_CLIENT_ID are required")
    
    # Create audit service
    audit_service = StandardAuditService()
    
    # Create and return Cognito authentication service
    return CognitoAuthenticationService(
        user_pool_id=user_pool_id,
        client_id=client_id,
        client_secret=client_secret,
        identity_pool_id=identity_pool_id,
        region=region,
        audit_service=audit_service
    )


def validate_cognito_config() -> Dict[str, Any]:
    """
    Validate Cognito configuration and return status
    
    Returns:
        Dictionary with configuration validation results
    """
    config = {}
    errors = []
    
    # Check required variables
    required = {
        "COGNITO_USER_POOL_ID": os.getenv("COGNITO_USER_POOL_ID"),
        "COGNITO_CLIENT_ID": os.getenv("COGNITO_CLIENT_ID"),
        "AWS_REGION": os.getenv("AWS_REGION", "us-west-2")
    }
    
    for var, value in required.items():
        if value:
            config[var] = value
        else:
            errors.append(f"Missing required environment variable: {var}")
    
    # Check optional variables
    optional = {
        "COGNITO_CLIENT_SECRET": os.getenv("COGNITO_CLIENT_SECRET"),
        "COGNITO_IDENTITY_POOL_ID": os.getenv("COGNITO_IDENTITY_POOL_ID")
    }
    
    for var, value in optional.items():
        if value:
            config[var] = value
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "config": config
    }


# Main authentication functions
def authenticate_user(username: str, password: str, register_if_new: bool = False) -> Dict[str, Any]:
    """
    Authenticate user with Cognito
    
    Args:
        username: Username or email
        password: User password
        register_if_new: Create account if user doesn't exist
        
    Returns:
        Dictionary with authentication result
    """
    try:
        from .domain.common.entities import AuthCredentials
        
        # Create service and credentials
        auth_service = create_cognito_auth_service()
        credentials = AuthCredentials(
            username=username,
            password=password,
            register_if_new=register_if_new
        )
        
        # Authenticate
        user, token = auth_service.authenticate_user(credentials)
        
        return {
            "success": True,
            "user": {
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email,
                "display_name": user.display_name,
                "roles": user.roles,
                "permissions": user.permissions,
                "is_verified": user.is_verified
            },
            "token": {
                "access_token": token.token,
                "token_type": token.token_type,
                "expires_in": token.expires_in,
                "refresh_token": token.refresh_token
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def validate_token(access_token: str) -> Dict[str, Any]:
    """
    Validate Cognito access token
    
    Args:
        access_token: Cognito access token
        
    Returns:
        Dictionary with validation result
    """
    try:
        auth_service = create_cognito_auth_service()
        user = auth_service.validate_token(access_token)
        
        return {
            "success": True,
            "user": {
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email,
                "display_name": user.display_name,
                "roles": user.roles,
                "permissions": user.permissions,
                "is_verified": user.is_verified
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }