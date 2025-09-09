"""Flask handlers for authentication operations using hexagonal architecture"""
from typing import Tuple, Any
from functools import wraps
from flask import request, jsonify, g

from ...domain.auth_service import AuthenticationService
from ...domain.common.entities import AuthCredentials
from ...domain.common.exceptions import (
    NotFoundError, ConflictError, ValidationError, 
    BusinessRuleError, InvalidStateError
)
from .serializers import FlaskAuthSerializer


class FlaskAuthHandler:
    """Flask route handler for authentication operations using domain service"""
    
    def __init__(self, auth_service: AuthenticationService, auth_serializer: FlaskAuthSerializer):
        self._auth_service = auth_service
        self._auth_serializer = auth_serializer
    
    def authenticate(self, body: Any) -> Tuple[Any, int]:
        """
        Flask handler for user authentication (login/register)
        
        Args:
            body: OpenAPI AuthRequest model or dict
            
        Returns:
            Tuple of (response_body, http_status_code)
        """
        try:
            # Convert OpenAPI model to business entity
            auth_data = self._auth_serializer.from_openapi(body)
            credentials = AuthCredentials(**auth_data)
            
            # Execute business logic
            authenticated_user, auth_token = self._auth_service.authenticate_user(credentials)
            
            # Convert domain entities to OpenAPI response
            response = self._auth_serializer.to_auth_response(authenticated_user, auth_token)
            
            return response, 201
            
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
    
    def refresh_token(self) -> Tuple[Any, int]:
        """
        Flask handler for token refresh
        
        Returns:
            Tuple of (response_body, http_status_code)
        """
        try:
            # Extract refresh token from request
            auth_header = request.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                return {"error": "Missing or invalid authorization header"}, 401
            
            refresh_token = auth_header[7:]  # Remove 'Bearer ' prefix
            
            # Execute business logic
            new_token = self._auth_service.refresh_token(refresh_token)
            
            # Convert to response
            response = self._auth_serializer.to_token_response(new_token)
            
            return response, 200
            
        except ValidationError as e:
            return {"error": "Validation error", "detail": str(e)}, 400
        except BusinessRuleError as e:
            return {"error": "Token refresh failed", "detail": str(e)}, 401
        except NotFoundError as e:
            return {"error": "Session not found", "detail": str(e)}, 404
        except Exception as e:
            return {"error": "Internal server error", "detail": str(e)}, 500
    
    def logout(self) -> Tuple[None, int]:
        """
        Flask handler for user logout
        
        Returns:
            Tuple of (None, http_status_code)
        """
        try:
            # Get current user session from request context
            if not hasattr(g, 'current_user') or not g.current_user:
                return {"error": "Not authenticated"}, 401
            
            session_id = g.current_user.session_id
            if not session_id:
                return {"error": "No active session"}, 400
            
            # Execute business logic
            self._auth_service.logout(session_id)
            
            return None, 204
            
        except NotFoundError as e:
            return {"error": "Session not found", "detail": str(e)}, 404
        except Exception as e:
            return {"error": "Internal server error", "detail": str(e)}, 500
    
    def initiate_password_reset(self, body: Any) -> Tuple[None, int]:
        """
        Flask handler for password reset initiation
        
        Args:
            body: OpenAPI PasswordResetRequest model or dict
            
        Returns:
            Tuple of (None, http_status_code)
        """
        try:
            # Extract email from request body
            reset_data = self._auth_serializer.from_openapi(body)
            email = reset_data.get('email')
            
            if not email:
                return {"error": "Email is required"}, 400
            
            # Execute business logic
            self._auth_service.initiate_password_reset(email)
            
            # Always return success for security (don't reveal if email exists)
            return None, 204
            
        except ValidationError as e:
            return {"error": "Validation error", "detail": str(e)}, 400
        except Exception as e:
            return {"error": "Internal server error", "detail": str(e)}, 500
    
    def reset_password(self, body: Any) -> Tuple[None, int]:
        """
        Flask handler for password reset completion
        
        Args:
            body: Dict containing reset token and new password
            
        Returns:
            Tuple of (None, http_status_code)
        """
        try:
            # Extract reset data from request body
            reset_data = self._auth_serializer.from_openapi(body)
            token = reset_data.get('token')
            new_password = reset_data.get('new_password')
            
            if not token or not new_password:
                return {"error": "Token and new password are required"}, 400
            
            # Execute business logic
            self._auth_service.reset_password(token, new_password)
            
            return None, 204
            
        except ValidationError as e:
            return {"error": "Validation error", "detail": str(e)}, 400
        except BusinessRuleError as e:
            return {"error": "Password reset failed", "detail": str(e)}, 400
        except NotFoundError as e:
            return {"error": "Invalid reset token", "detail": str(e)}, 400
        except Exception as e:
            return {"error": "Internal server error", "detail": str(e)}, 500


class FlaskAuthMiddleware:
    """Flask middleware for authentication and authorization"""
    
    def __init__(self, auth_service: AuthenticationService):
        self._auth_service = auth_service
    
    def require_authentication(self, f):
        """
        Decorator to require authentication for Flask routes
        
        Usage:
            @auth_middleware.require_authentication
            def protected_route():
                # Access authenticated user via g.current_user
                return {"user": g.current_user.username}
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
                
                # Store in request context
                g.current_user = authenticated_user
                
                return f(*args, **kwargs)
                
            except ValidationError as e:
                return jsonify({"error": "Invalid token", "detail": str(e)}), 401
            except BusinessRuleError as e:
                return jsonify({"error": "Authentication failed", "detail": str(e)}), 401
            except NotFoundError as e:
                return jsonify({"error": "Session not found", "detail": str(e)}), 401
            except Exception as e:
                return jsonify({"error": "Authentication error", "detail": str(e)}), 500
        
        return decorated_function
    
    def require_permission(self, required_permission: str):
        """
        Decorator to require specific permission for Flask routes
        
        Args:
            required_permission: Permission name required
            
        Usage:
            @auth_middleware.require_permission('admin:users')
            def admin_route():
                return {"message": "Admin access granted"}
        """
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # First check authentication
                if not hasattr(g, 'current_user') or not g.current_user:
                    return jsonify({"error": "Authentication required"}), 401
                
                # Check authorization
                if not self._auth_service.authorize_user(g.current_user, required_permission):
                    return jsonify({
                        "error": "Insufficient permissions", 
                        "required": required_permission
                    }), 403
                
                return f(*args, **kwargs)
            
            return decorated_function
        return decorator
    
    def optional_authentication(self, f):
        """
        Decorator for optional authentication (sets g.current_user if token present)
        
        Usage:
            @auth_middleware.optional_authentication
            def public_route():
                if hasattr(g, 'current_user') and g.current_user:
                    return {"message": f"Hello {g.current_user.username}"}
                return {"message": "Hello anonymous"}
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                auth_header = request.headers.get('Authorization', '')
                if auth_header.startswith('Bearer '):
                    token = auth_header[7:]
                    authenticated_user = self._auth_service.validate_token(token)
                    g.current_user = authenticated_user
            except Exception:
                # Ignore authentication errors for optional auth
                pass
            
            return f(*args, **kwargs)
        
        return decorated_function


def extract_client_info() -> dict:
    """Extract client information from Flask request"""
    return {
        "ip_address": request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr),
        "user_agent": request.headers.get('User-Agent', ''),
        "origin": request.headers.get('Origin', ''),
        "referer": request.headers.get('Referer', '')
    }