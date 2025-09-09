"""Flask handlers for Cognito authentication operations using hexagonal architecture"""
from functools import wraps
from typing import Any, Dict
from flask import request, g, jsonify

from ...domain.cognito_auth_service import CognitoAuthenticationService
from ...domain.common.entities import AuthCredentials
from ...domain.common.exceptions import (
    NotFoundError, ConflictError, ValidationError, 
    BusinessRuleError, InvalidStateError
)
from .serializers import FlaskAuthSerializer


class FlaskCognitoAuthHandler:
    """Flask HTTP handler for Cognito authentication operations using domain service"""
    
    def __init__(self, auth_service: CognitoAuthenticationService, auth_serializer: FlaskAuthSerializer):
        self._auth_service = auth_service
        self._auth_serializer = auth_serializer
    
    def authenticate(self, request_data: Dict[str, Any]) -> Any:
        """
        Flask handler for user authentication (login/register)
        
        Args:
            request_data: Flask request data containing authentication info
            
        Returns:
            OpenAPI AuthResponse model or error response
        """
        try:
            # Convert Flask request to business entity
            auth_data = self._auth_serializer.from_openapi(request_data.get('json', {}))
            credentials = AuthCredentials(**auth_data)
            
            # Execute business logic
            authenticated_user, auth_token = self._auth_service.authenticate_user(credentials)
            
            # Convert domain entities to OpenAPI response
            return self._auth_serializer.to_auth_response(authenticated_user, auth_token)
            
        except ValidationError as e:
            return {"error": "Validation error", "detail": str(e)}, 400
        except ConflictError as e:
            return {"error": "Conflict", "detail": str(e)}, 409
        except NotFoundError as e:
            return {"error": "Not found", "detail": str(e)}, 404
        except BusinessRuleError as e:
            return {"error": "Authentication failed", "detail": str(e)}, 401
        except Exception as e:
            return {"error": "Internal server error", "detail": str(e)}, 500
    
    def refresh_token(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Flask handler for token refresh
        
        Args:
            request_data: Flask request data with refresh token info
            
        Returns:
            Token response dict or error
        """
        try:
            # Extract refresh token and username from request
            json_data = request_data.get('json', {})
            refresh_token = json_data.get('refresh_token')
            username = json_data.get('username')
            
            if not refresh_token or not username:
                return {"error": "Refresh token and username required"}, 400
            
            # Execute business logic
            new_token = self._auth_service.refresh_token(refresh_token, username)
            
            # Convert to response
            return self._auth_serializer.to_token_response(new_token)
            
        except ValidationError as e:
            return {"error": "Validation error", "detail": str(e)}, 400
        except BusinessRuleError as e:
            return {"error": "Token refresh failed", "detail": str(e)}, 401
        except NotFoundError as e:
            return {"error": "Session not found", "detail": str(e)}, 404
        except Exception as e:
            return {"error": "Internal server error", "detail": str(e)}, 500
    
    def logout(self, request_data: Dict[str, Any]) -> tuple:
        """
        Flask handler for user logout
        
        Args:
            request_data: Flask request data with authorization header
            
        Returns:
            Empty response or error
        """
        try:
            # Extract and validate token
            token = self._extract_token_from_request(request_data)
            if not token:
                return {"error": "Not authenticated"}, 401
            
            # Execute business logic
            self._auth_service.logout(token)
            
            return "", 204
            
        except ValidationError as e:
            return {"error": "Invalid token", "detail": str(e)}, 401
        except BusinessRuleError as e:
            return {"error": "Authentication failed", "detail": str(e)}, 401
        except Exception as e:
            return {"error": "Internal server error", "detail": str(e)}, 500
    
    def initiate_password_reset(self, request_data: Dict[str, Any]) -> tuple:
        """
        Flask handler for password reset initiation
        
        Args:
            request_data: Flask request data containing email/username
            
        Returns:
            Empty success response (security)
        """
        try:
            # Extract username/email from request
            reset_data = self._auth_serializer.from_openapi(request_data.get('json', {}))
            username = reset_data.get('username') or reset_data.get('email')
            
            if not username:
                return {"error": "Username or email is required"}, 400
            
            # Execute business logic
            self._auth_service.initiate_password_reset(username)
            
            # Always return success for security (don't reveal if user exists)
            return "", 204
            
        except ValidationError as e:
            return {"error": "Validation error", "detail": str(e)}, 400
        except Exception as e:
            return {"error": "Internal server error", "detail": str(e)}, 500
    
    def reset_password(self, request_data: Dict[str, Any]) -> tuple:
        """
        Flask handler for password reset completion
        
        Args:
            request_data: Flask request data with reset details
            
        Returns:
            Empty success response or error
        """
        try:
            # Extract reset data from request
            reset_data = self._auth_serializer.from_openapi(request_data.get('json', {}))
            username = reset_data.get('username')
            confirmation_code = reset_data.get('confirmation_code') or reset_data.get('code')
            new_password = reset_data.get('new_password') or reset_data.get('password')
            
            if not all([username, confirmation_code, new_password]):
                return {"error": "Username, confirmation code, and new password are required"}, 400
            
            # Execute business logic
            self._auth_service.reset_password(username, confirmation_code, new_password)
            
            return "", 204
            
        except ValidationError as e:
            return {"error": "Validation error", "detail": str(e)}, 400
        except BusinessRuleError as e:
            return {"error": "Password reset failed", "detail": str(e)}, 400
        except Exception as e:
            return {"error": "Internal server error", "detail": str(e)}, 500
    
    def _extract_token_from_request(self, request_data: Dict[str, Any]) -> str:
        """Extract Cognito access token from Flask request"""
        # Try Authorization header first
        headers = request_data.get('headers', {})
        auth_header = headers.get('Authorization', '')
        
        if auth_header.startswith('Bearer '):
            return auth_header[7:]  # Remove 'Bearer ' prefix
        
        return None


class FlaskCognitoAuthMiddleware:
    """Flask middleware for Cognito authentication and authorization"""
    
    def __init__(self, auth_service: CognitoAuthenticationService):
        self._auth_service = auth_service
    
    def require_authentication(self, f):
        """
        Decorator to require authentication for Flask routes
        
        Usage:
            @app.route('/protected')
            @auth_middleware.require_authentication
            def protected_endpoint():
                user = g.current_user
                return {"message": f"Hello {user.username}"}
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Extract token from Authorization header
                auth_header = request.headers.get('Authorization', '')
                if not auth_header.startswith('Bearer '):
                    return jsonify({"error": "Missing or invalid authorization header"}), 401
                
                token = auth_header[7:]  # Remove 'Bearer ' prefix
                
                # Validate token and get authenticated user
                authenticated_user = self._auth_service.validate_token(token)
                
                # Store in Flask context for use in route handler
                g.current_user = authenticated_user
                
                return f(*args, **kwargs)
                
            except ValidationError as e:
                return jsonify({"error": "Invalid token", "detail": str(e)}), 401
            except BusinessRuleError as e:
                return jsonify({"error": "Authentication failed", "detail": str(e)}), 401
            except Exception as e:
                return jsonify({"error": "Authentication error", "detail": str(e)}), 401
        
        return decorated_function
    
    def require_permission(self, required_permission: str):
        """
        Decorator to require specific permission for Flask routes
        
        Args:
            required_permission: Permission string required for access
            
        Usage:
            @app.route('/admin')
            @auth_middleware.require_permission('admin:write')
            def admin_endpoint():
                return {"message": "Admin access granted"}
        """
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                try:
                    # First require authentication
                    auth_header = request.headers.get('Authorization', '')
                    if not auth_header.startswith('Bearer '):
                        return jsonify({"error": "Missing or invalid authorization header"}), 401
                    
                    token = auth_header[7:]
                    authenticated_user = self._auth_service.validate_token(token)
                    
                    # Check permission
                    if not self._auth_service.authorize_user(authenticated_user, required_permission):
                        return jsonify({"error": "Insufficient permissions", "required": required_permission}), 403
                    
                    # Store in Flask context
                    g.current_user = authenticated_user
                    
                    return f(*args, **kwargs)
                    
                except ValidationError as e:
                    return jsonify({"error": "Invalid token", "detail": str(e)}), 401
                except BusinessRuleError as e:
                    return jsonify({"error": "Authentication failed", "detail": str(e)}), 401
                except Exception as e:
                    return jsonify({"error": "Authorization error", "detail": str(e)}), 403
            
            return decorated_function
        return decorator
    
    def require_role(self, required_role: str):
        """
        Decorator to require specific role for Flask routes
        
        Args:
            required_role: Role name required for access
            
        Usage:
            @app.route('/educator')
            @auth_middleware.require_role('educator')
            def educator_endpoint():
                return {"message": "Educator access granted"}
        """
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                try:
                    # First require authentication
                    auth_header = request.headers.get('Authorization', '')
                    if not auth_header.startswith('Bearer '):
                        return jsonify({"error": "Missing or invalid authorization header"}), 401
                    
                    token = auth_header[7:]
                    authenticated_user = self._auth_service.validate_token(token)
                    
                    # Check role
                    if required_role not in (authenticated_user.roles or []):
                        return jsonify({"error": "Insufficient role", "required": required_role}), 403
                    
                    # Store in Flask context
                    g.current_user = authenticated_user
                    
                    return f(*args, **kwargs)
                    
                except ValidationError as e:
                    return jsonify({"error": "Invalid token", "detail": str(e)}), 401
                except BusinessRuleError as e:
                    return jsonify({"error": "Authentication failed", "detail": str(e)}), 401
                except Exception as e:
                    return jsonify({"error": "Authorization error", "detail": str(e)}), 403
            
            return decorated_function
        return decorator


def get_current_user_flask():
    """
    Get current authenticated user in Flask context
    
    Returns:
        AuthenticatedUser instance or None
    """
    return getattr(g, 'current_user', None)