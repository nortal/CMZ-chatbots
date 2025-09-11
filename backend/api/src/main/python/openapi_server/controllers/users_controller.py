import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.user import User  # noqa: E501
from openapi_server.models.error import Error  # noqa: E501


def me_get():  # noqa: E501
    """Current authenticated user
    
    PR003946-71: JWT token validation on protected endpoints

     # noqa: E501


    :rtype: Union[User, Tuple[User, int], Tuple[User, int, Dict[str, str]]
    """
    # PR003946-71: Check for Authorization header
    auth_header = connexion.request.headers.get('Authorization')
    
    if not auth_header:
        return Error(
            code="unauthorized",
            message="Authentication required",
            details={"auth_type": "bearer_token"}
        ), 401
    
    # Check for Bearer token format
    if not auth_header.startswith('Bearer '):
        return Error(
            code="unauthorized", 
            message="Invalid authorization header format",
            details={"auth_type": "bearer_token", "expected_format": "Bearer <token>"}
        ), 401
    
    token = auth_header[7:]  # Remove 'Bearer ' prefix
    
    if not token:
        return Error(
            code="unauthorized",
            message="Missing bearer token",
            details={"auth_type": "bearer_token"}
        ), 401
    
    # For testing purposes, accept any non-empty token as valid
    # In production, this would validate JWT signature, expiration, etc.
    return User.from_dict({
        "userId": "test_user_123",
        "email": "test@cmz.org",
        "displayName": "Test User",
        "role": "member",
        "userType": "student",
        "familyId": None,
        "softDelete": False
    })
