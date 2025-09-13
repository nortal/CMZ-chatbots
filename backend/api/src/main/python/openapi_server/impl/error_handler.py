"""
PR003946-90: Consistent Error Schema Implementation

This module provides centralized error handling that ensures all API responses
follow the consistent Error schema with code, message, and details fields.
"""

from flask import jsonify
from werkzeug.exceptions import HTTPException
from connexion.exceptions import BadRequestProblem
from openapi_server.models.error import Error
import logging

logger = logging.getLogger(__name__)


def create_error_response(code: str, message: str, details=None):
    """Create a standardized error response using the Error schema."""
    return {
        "code": code,
        "message": message,
        "details": details or {}
    }


def register_error_handlers(app):
    """Register centralized error handlers for consistent Error schema responses."""
    
    @app.errorhandler(400)
    def handle_bad_request(error):
        """Handle 400 Bad Request errors with consistent schema."""
        code = "invalid_request"
        message = "The request is invalid"
        details = {"field_errors": []}
        
        # Extract validation details if available
        if hasattr(error, 'description') and error.description:
            message = str(error.description)
            
            # PR003946-84: Detect log level enum validation errors
            if "level" in message and ("not one of" in message.lower() or "invalid enum value" in message.lower()):
                code = "invalid_log_level"
                message = "Invalid log level specified"
                details = {
                    "field": "level",
                    "allowed_values": ["debug", "info", "warn", "error"],
                    "error_type": "invalid_log_level"
                }
            # Detect other enum validation patterns from OpenAPI/Connexion
            elif "not one of" in message.lower() or "invalid enum value" in message.lower():
                code = "invalid_enum_value"
                details["validation_detail"] = message
                
        # Handle Connexion validation errors
        if isinstance(error, BadRequestProblem):
            code = "validation_error" 
            if hasattr(error, 'detail'):
                details["validation_detail"] = error.detail
                
                # PR003946-87: Detect password policy validation errors
                detail_str = str(error.detail).lower()
                if "'password'" in detail_str and "too short" in detail_str:
                    code = "invalid_password"
                    message = "Password does not meet security requirements"
                    details = {
                        "field": "password",
                        "validation_detail": error.detail,
                        "policy_violations": ["Password must be at least 6 characters long"]
                    }
                
        error_obj = Error(code=code, message=message, details=details)
        
        logger.warning(f"Bad request error: {message}")
        return jsonify(error_obj.to_dict()), 400

    @app.errorhandler(401)
    def handle_unauthorized(error):
        """Handle 401 Unauthorized errors with consistent schema."""
        error_obj = Error(
            code="unauthorized",
            message="Authentication is required to access this resource",
            details={"auth_required": True}
        )
        
        logger.warning("Unauthorized access attempt")
        return jsonify(error_obj.to_dict()), 401

    @app.errorhandler(403)
    def handle_forbidden(error):
        """Handle 403 Forbidden errors with consistent schema."""
        error_obj = Error(
            code="forbidden",
            message="You do not have permission to access this resource",
            details={"role_required": True}
        )
        
        logger.warning("Forbidden access attempt")
        return jsonify(error_obj.to_dict()), 403

    @app.errorhandler(404)
    def handle_not_found(error):
        """Handle 404 Not Found errors with consistent schema."""
        error_obj = Error(
            code="not_found",
            message="The requested resource was not found",
            details={"resource_type": "unknown"}
        )
        
        logger.info("Resource not found")
        return jsonify(error_obj.to_dict()), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        """Handle 405 Method Not Allowed errors with consistent schema."""
        error_obj = Error(
            code="method_not_allowed",
            message="The HTTP method is not allowed for this resource",
            details={
                "allowed_methods": error.allowed_methods if hasattr(error, 'allowed_methods') else []
            }
        )
        
        logger.info("Method not allowed")
        return jsonify(error_obj.to_dict()), 405

    @app.errorhandler(422)
    def handle_unprocessable_entity(error):
        """Handle 422 Unprocessable Entity errors with consistent schema."""
        error_obj = Error(
            code="validation_error",
            message="The request data failed validation",
            details={"validation_errors": []}
        )
        
        logger.warning("Validation error")
        return jsonify(error_obj.to_dict()), 422

    @app.errorhandler(500)
    def handle_internal_server_error(error):
        """Handle 500 Internal Server Error with consistent schema."""
        error_obj = Error(
            code="internal_error",
            message="An internal server error occurred",
            details={"error_id": "unknown"}
        )
        
        logger.error(f"Internal server error: {str(error)}")
        return jsonify(error_obj.to_dict()), 500

    # ValidationError handler removed - duplicate handler exists in register_custom_error_handlers()

    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        """Handle any unhandled exceptions with consistent schema."""
        # Don't catch HTTP exceptions that should be handled by specific handlers
        if isinstance(error, HTTPException):
            return error
            
        error_obj = Error(
            code="internal_error", 
            message="An unexpected error occurred",
            details={"error_type": type(error).__name__}
        )
        
        logger.error(f"Unhandled exception: {str(error)}", exc_info=True)
        return jsonify(error_obj.to_dict()), 500


class ValidationError(Exception):
    """Custom exception for validation errors that should return 400 with Error schema."""
    
    def __init__(self, message, field_errors=None, details=None, error_code=None):
        self.message = message
        self.field_errors = field_errors or []
        self.details = details or {}
        self.error_code = error_code or "validation_error"
        logger.debug(f"Creating ValidationError with error_code: {self.error_code}")
        super().__init__(message)


class AuthenticationError(Exception):
    """Custom exception for authentication errors that should return 401 with Error schema."""
    
    def __init__(self, message, details=None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


class AuthorizationError(Exception):
    """Custom exception for authorization errors that should return 403 with Error schema."""
    
    def __init__(self, message, required_role=None, details=None):
        self.message = message
        self.required_role = required_role
        self.details = details or {}
        super().__init__(message)


class NotFoundError(Exception):
    """Custom exception for resource not found errors that should return 404 with Error schema."""
    
    def __init__(self, message, resource_type=None, resource_id=None, details=None):
        self.message = message
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.details = details or {}
        super().__init__(message)


def handle_error(message, status_code=500, error_code=None):
    """Generic error handling function for controller imports."""
    from openapi_server.models.error import Error
    from flask import jsonify

    error_code = error_code or ("validation_error" if status_code == 400 else "internal_error")
    error_obj = Error(
        code=error_code,
        message=message,
        details={}
    )

    return jsonify(error_obj.to_dict()), status_code


def register_custom_error_handlers(app):
    """Register handlers for custom exception classes."""
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        """Handle custom ValidationError exceptions."""
        code = error.error_code if hasattr(error, 'error_code') else 'validation_error'
        logger.debug(f"Second ValidationError handler called with code: {code}")
        error_obj = Error(
            code=code,
            message=error.message,
            details={
                "field_errors": error.field_errors,
                **error.details
            }
        )
        
        logger.warning(f"Validation error: {error.message}")
        return jsonify(error_obj.to_dict()), 400

    @app.errorhandler(AuthenticationError)
    def handle_authentication_error(error):
        """Handle custom AuthenticationError exceptions."""
        error_obj = Error(
            code="authentication_failed",
            message=error.message,
            details=error.details
        )
        
        logger.warning(f"Authentication error: {error.message}")
        return jsonify(error_obj.to_dict()), 401

    @app.errorhandler(AuthorizationError)
    def handle_authorization_error(error):
        """Handle custom AuthorizationError exceptions."""
        details = error.details.copy()
        if error.required_role:
            details["required_role"] = error.required_role
            
        error_obj = Error(
            code="insufficient_permissions",
            message=error.message,
            details=details
        )
        
        logger.warning(f"Authorization error: {error.message}")
        return jsonify(error_obj.to_dict()), 403

    @app.errorhandler(NotFoundError)
    def handle_not_found_error(error):
        """Handle custom NotFoundError exceptions."""
        details = error.details.copy()
        if error.resource_type:
            details["resource_type"] = error.resource_type
        if error.resource_id:
            details["resource_id"] = error.resource_id
            
        error_obj = Error(
            code="resource_not_found",
            message=error.message,
            details=details
        )
        
        logger.info(f"Resource not found: {error.message}")
        return jsonify(error_obj.to_dict()), 404