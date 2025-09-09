"""Flask serializers for converting between domain entities and OpenAPI models"""
from typing import Dict, Any, Optional
from datetime import datetime

from ...domain.common.entities import AuthCredentials, AuthToken, AuthenticatedUser
from openapi_server.models.auth_request import AuthRequest
from openapi_server.models.auth_response import AuthResponse
from openapi_server.models.user import User


class FlaskAuthSerializer:
    """Serializer for authentication data between Flask/OpenAPI and domain entities"""
    
    def to_auth_response(self, user: AuthenticatedUser, token: AuthToken) -> AuthResponse:
        """
        Convert domain entities to OpenAPI AuthResponse
        
        Args:
            user: Authenticated user domain entity
            token: Auth token domain entity
            
        Returns:
            OpenAPI AuthResponse model
        """
        # Create User model
        user_model = User(
            user_id=user.user_id,
            email=user.email,
            display_name=user.display_name or user.username,
            role=user.roles[0] if user.roles else "member",  # Use first role as primary
            created={"at": datetime.utcnow().isoformat() + "Z", "by": {"userId": "system", "email": "system@cmz.org"}},
            modified={"at": datetime.utcnow().isoformat() + "Z", "by": {"userId": "system", "email": "system@cmz.org"}},
            soft_delete=False
        )
        
        # Create AuthResponse
        return AuthResponse(
            token=token.token,
            expires_in=token.expires_in,
            user=user_model
        )
    
    def to_token_response(self, token: AuthToken) -> Dict[str, Any]:
        """
        Convert AuthToken to token refresh response
        
        Args:
            token: Auth token domain entity
            
        Returns:
            Dictionary with token response data
        """
        return {
            "token": token.token,
            "expires_in": token.expires_in,
            "token_type": token.token_type
        }
    
    def from_password_reset_request(self, openapi_data: Any) -> Dict[str, Any]:
        """
        Convert OpenAPI PasswordResetRequest to domain data
        
        Args:
            openapi_data: PasswordResetRequest model or dict
            
        Returns:
            Dictionary with domain fields
        """
        if hasattr(openapi_data, 'email'):
            return {"email": openapi_data.email, "username": openapi_data.email}
        elif isinstance(openapi_data, dict):
            email = openapi_data.get("email")
            return {"email": email, "username": email}
        else:
            raise ValueError(f"Unsupported data type: {type(openapi_data)}")
    
    def from_openapi(self, openapi_data: Any) -> Dict[str, Any]:
        """
        Convert OpenAPI data to domain entity data (handles multiple request types)
        
        Args:
            openapi_data: AuthRequest model, PasswordResetRequest model, or dict
            
        Returns:
            Dictionary with domain entity fields
        """
        # Handle AuthRequest
        if hasattr(openapi_data, 'username') and hasattr(openapi_data, 'password'):
            return {
                "username": openapi_data.username,
                "password": openapi_data.password,
                "register_if_new": getattr(openapi_data, 'register', False)
            }
        # Handle PasswordResetRequest
        elif hasattr(openapi_data, 'email'):
            return {"email": openapi_data.email, "username": openapi_data.email}
        # Handle dict data
        elif isinstance(openapi_data, dict):
            if 'password' in openapi_data:
                # Auth request
                return {
                    "username": openapi_data.get("username"),
                    "password": openapi_data.get("password"),
                    "register_if_new": openapi_data.get("register", False)
                }
            elif 'email' in openapi_data:
                # Password reset request
                email = openapi_data.get("email")
                return {"email": email, "username": email}
            else:
                return openapi_data
        else:
            raise ValueError(f"Unsupported data type: {type(openapi_data)}")