"""
Unit tests for error_handler.py custom exceptions and error creation functions.

Tests custom exception classes, error response creation, and Flask error handlers.
Provides fast feedback loop for red-green-refactor cycles.
"""
import pytest
from unittest.mock import patch, MagicMock
from flask import Flask, jsonify
from werkzeug.exceptions import BadRequest, Unauthorized, Forbidden, NotFound
from connexion.exceptions import BadRequestProblem

from openapi_server.impl.error_handler import (
    create_error_response, ValidationError, AuthenticationError, 
    AuthorizationError, NotFoundError, register_error_handlers,
    register_custom_error_handlers
)
from openapi_server.models.error import Error


class TestCreateErrorResponse:
    """Test error response creation utility."""
    
    def test_create_error_response_basic(self):
        """Test basic error response creation."""
        response = create_error_response("test_code", "Test message")
        
        assert response["code"] == "test_code"
        assert response["message"] == "Test message"
        assert response["details"] == {}
    
    def test_create_error_response_with_details(self):
        """Test error response creation with details."""
        details = {"field": "username", "validation": "required"}
        response = create_error_response("validation_error", "Invalid input", details)
        
        assert response["code"] == "validation_error"
        assert response["message"] == "Invalid input"
        assert response["details"]["field"] == "username"
        assert response["details"]["validation"] == "required"
    
    def test_create_error_response_none_details(self):
        """Test error response creation with None details."""
        response = create_error_response("error", "Message", None)
        
        assert response["details"] == {}


class TestValidationError:
    """Test ValidationError custom exception class."""
    
    def test_validation_error_basic(self):
        """Test basic ValidationError creation."""
        error = ValidationError("Validation failed")
        
        assert str(error) == "Validation failed"
        assert error.message == "Validation failed"
        assert error.field_errors == []
        assert error.details == {}
        assert error.error_code == "validation_error"
    
    def test_validation_error_with_field_errors(self):
        """Test ValidationError with field errors."""
        field_errors = ["Username is required", "Email is invalid"]
        error = ValidationError("Form validation failed", field_errors=field_errors)
        
        assert error.message == "Form validation failed"
        assert error.field_errors == field_errors
        assert len(error.field_errors) == 2
    
    def test_validation_error_with_details(self):
        """Test ValidationError with custom details."""
        details = {"field": "password", "min_length": 6}
        error = ValidationError("Password too short", details=details)
        
        assert error.details["field"] == "password"
        assert error.details["min_length"] == 6
    
    def test_validation_error_with_custom_error_code(self):
        """Test ValidationError with custom error code."""
        error = ValidationError("Invalid password", error_code="invalid_password")
        
        assert error.error_code == "invalid_password"
    
    def test_validation_error_all_parameters(self):
        """Test ValidationError with all parameters."""
        field_errors = ["Password must contain digits"]
        details = {"field": "password", "policy": "digits_required"}
        error = ValidationError(
            "Password policy violation",
            field_errors=field_errors,
            details=details,
            error_code="password_policy_error"
        )
        
        assert error.message == "Password policy violation"
        assert error.field_errors == field_errors
        assert error.details == details
        assert error.error_code == "password_policy_error"


class TestAuthenticationError:
    """Test AuthenticationError custom exception class."""
    
    def test_authentication_error_basic(self):
        """Test basic AuthenticationError creation."""
        error = AuthenticationError("Authentication failed")
        
        assert str(error) == "Authentication failed"
        assert error.message == "Authentication failed"
        assert error.details == {}
    
    def test_authentication_error_with_details(self):
        """Test AuthenticationError with details."""
        details = {"token_expired": True, "expiry_time": "2023-12-01T10:00:00Z"}
        error = AuthenticationError("Token has expired", details=details)
        
        assert error.message == "Token has expired"
        assert error.details["token_expired"] == True
        assert error.details["expiry_time"] == "2023-12-01T10:00:00Z"
    
    def test_authentication_error_inheritance(self):
        """Test AuthenticationError inherits from Exception."""
        error = AuthenticationError("Auth failed")
        
        assert isinstance(error, Exception)
        assert isinstance(error, AuthenticationError)


class TestAuthorizationError:
    """Test AuthorizationError custom exception class."""
    
    def test_authorization_error_basic(self):
        """Test basic AuthorizationError creation."""
        error = AuthorizationError("Access denied")
        
        assert str(error) == "Access denied"
        assert error.message == "Access denied"
        assert error.required_role is None
        assert error.details == {}
    
    def test_authorization_error_with_required_role(self):
        """Test AuthorizationError with required role."""
        error = AuthorizationError("Insufficient permissions", required_role="admin")
        
        assert error.message == "Insufficient permissions"
        assert error.required_role == "admin"
    
    def test_authorization_error_with_details(self):
        """Test AuthorizationError with details."""
        details = {"current_role": "member", "resource": "admin_panel"}
        error = AuthorizationError("Access denied", details=details)
        
        assert error.details["current_role"] == "member"
        assert error.details["resource"] == "admin_panel"
    
    def test_authorization_error_all_parameters(self):
        """Test AuthorizationError with all parameters."""
        details = {"current_role": "parent", "endpoint": "/admin/users"}
        error = AuthorizationError(
            "Admin access required",
            required_role="admin",
            details=details
        )
        
        assert error.message == "Admin access required"
        assert error.required_role == "admin"
        assert error.details == details


class TestNotFoundError:
    """Test NotFoundError custom exception class."""
    
    def test_not_found_error_basic(self):
        """Test basic NotFoundError creation."""
        error = NotFoundError("Resource not found")
        
        assert str(error) == "Resource not found"
        assert error.message == "Resource not found"
        assert error.resource_type is None
        assert error.resource_id is None
        assert error.details == {}
    
    def test_not_found_error_with_resource_info(self):
        """Test NotFoundError with resource type and ID."""
        error = NotFoundError("User not found", resource_type="user", resource_id="user_123")
        
        assert error.message == "User not found"
        assert error.resource_type == "user"
        assert error.resource_id == "user_123"
    
    def test_not_found_error_with_details(self):
        """Test NotFoundError with custom details."""
        details = {"search_criteria": "email=test@example.com", "table": "users"}
        error = NotFoundError("User lookup failed", details=details)
        
        assert error.details["search_criteria"] == "email=test@example.com"
        assert error.details["table"] == "users"
    
    def test_not_found_error_all_parameters(self):
        """Test NotFoundError with all parameters."""
        details = {"query": "SELECT * FROM animals WHERE id = ?"}
        error = NotFoundError(
            "Animal not found",
            resource_type="animal",
            resource_id="animal_456",
            details=details
        )
        
        assert error.message == "Animal not found"
        assert error.resource_type == "animal"
        assert error.resource_id == "animal_456"
        assert error.details == details


class TestFlaskErrorHandlers:
    """Test Flask error handler registration and behavior."""
    
    def setup_method(self):
        """Set up Flask app for testing error handlers."""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        register_error_handlers(self.app)
        register_custom_error_handlers(self.app)
        
        # Create test client
        self.client = self.app.test_client()
    
    def test_register_error_handlers_400(self):
        """Test 400 Bad Request error handler."""
        @self.app.route('/test-400')
        def trigger_400():
            raise BadRequest("Invalid request data")
        
        response = self.client.get('/test-400')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data["code"] == "invalid_request"
        assert "invalid" in data["message"].lower()
    
    def test_register_error_handlers_401(self):
        """Test 401 Unauthorized error handler."""
        @self.app.route('/test-401')
        def trigger_401():
            raise Unauthorized("Authentication required")
        
        response = self.client.get('/test-401')
        
        assert response.status_code == 401
        data = response.get_json()
        assert data["code"] == "unauthorized"
        assert "authentication" in data["message"].lower()
        assert data["details"]["auth_required"] == True
    
    def test_register_error_handlers_403(self):
        """Test 403 Forbidden error handler."""
        @self.app.route('/test-403')
        def trigger_403():
            raise Forbidden("Access denied")
        
        response = self.client.get('/test-403')
        
        assert response.status_code == 403
        data = response.get_json()
        assert data["code"] == "forbidden"
        assert "permission" in data["message"].lower()
        assert data["details"]["role_required"] == True
    
    def test_register_error_handlers_404(self):
        """Test 404 Not Found error handler."""
        # Flask automatically handles 404s for undefined routes
        response = self.client.get('/nonexistent-route')
        
        assert response.status_code == 404
        data = response.get_json()
        assert data["code"] == "not_found"
        assert "not found" in data["message"].lower()
    
    def test_register_error_handlers_500(self):
        """Test 500 Internal Server Error handler."""
        @self.app.route('/test-500')
        def trigger_500():
            raise Exception("Something went wrong")
        
        response = self.client.get('/test-500')
        
        assert response.status_code == 500
        data = response.get_json()
        assert data["code"] == "internal_error"
        assert "internal server error" in data["message"].lower()


class TestCustomExceptionHandlers:
    """Test custom exception handlers in Flask context."""
    
    def setup_method(self):
        """Set up Flask app for testing custom exception handlers."""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        register_custom_error_handlers(self.app)
        
        self.client = self.app.test_client()
    
    def test_validation_error_handler(self):
        """Test ValidationError exception handler."""
        @self.app.route('/test-validation')
        def trigger_validation():
            field_errors = ["Username is required", "Password too short"]
            details = {"form_field": "user_form"}
            raise ValidationError("Form validation failed", field_errors=field_errors, details=details)
        
        response = self.client.get('/test-validation')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data["code"] == "validation_error"
        assert data["message"] == "Form validation failed"
        assert data["details"]["field_errors"] == ["Username is required", "Password too short"]
        assert data["details"]["form_field"] == "user_form"
    
    def test_validation_error_handler_with_custom_code(self):
        """Test ValidationError handler with custom error code."""
        @self.app.route('/test-validation-custom')
        def trigger_custom_validation():
            raise ValidationError("Password policy violation", error_code="invalid_password")
        
        response = self.client.get('/test-validation-custom')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data["code"] == "invalid_password"
    
    def test_authentication_error_handler(self):
        """Test AuthenticationError exception handler."""
        @self.app.route('/test-auth')
        def trigger_auth():
            details = {"token_expired": True}
            raise AuthenticationError("Invalid token", details=details)
        
        response = self.client.get('/test-auth')
        
        assert response.status_code == 401
        data = response.get_json()
        assert data["code"] == "authentication_failed"
        assert data["message"] == "Invalid token"
        assert data["details"]["token_expired"] == True
    
    def test_authorization_error_handler(self):
        """Test AuthorizationError exception handler."""
        @self.app.route('/test-authz')
        def trigger_authz():
            details = {"current_role": "member"}
            raise AuthorizationError("Admin required", required_role="admin", details=details)
        
        response = self.client.get('/test-authz')
        
        assert response.status_code == 403
        data = response.get_json()
        assert data["code"] == "insufficient_permissions"
        assert data["message"] == "Admin required"
        assert data["details"]["required_role"] == "admin"
        assert data["details"]["current_role"] == "member"
    
    def test_not_found_error_handler(self):
        """Test NotFoundError exception handler."""
        @self.app.route('/test-notfound')
        def trigger_not_found():
            details = {"query": "id=123"}
            raise NotFoundError("User not found", resource_type="user", resource_id="123", details=details)
        
        response = self.client.get('/test-notfound')
        
        assert response.status_code == 404
        data = response.get_json()
        assert data["code"] == "resource_not_found"
        assert data["message"] == "User not found"
        assert data["details"]["resource_type"] == "user"
        assert data["details"]["resource_id"] == "123"
        assert data["details"]["query"] == "id=123"


class TestSpecializedErrorHandling:
    """Test specialized error handling for specific scenarios."""
    
    def setup_method(self):
        """Set up Flask app with error handlers."""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        register_error_handlers(self.app)
        
        self.client = self.app.test_client()
    
    def test_log_level_enum_validation_error(self):
        """Test specific handling of log level enum validation errors."""
        # Create a BadRequestProblem that looks like enum validation error
        @self.app.route('/test-log-level')
        def trigger_log_level():
            error = BadRequest("'invalid_level' is not one of ['debug', 'info', 'warn', 'error']")
            error.description = "'invalid_level' is not one of ['debug', 'info', 'warn', 'error'] - 'level'"
            raise error
        
        response = self.client.get('/test-log-level')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data["code"] == "invalid_log_level"
        assert "Invalid log level specified" in data["message"]
        assert data["details"]["field"] == "level"
        assert "debug" in data["details"]["allowed_values"]
    
    def test_password_policy_validation_error(self):
        """Test specific handling of password policy validation errors."""
        @self.app.route('/test-password-policy')
        def trigger_password():
            problem = BadRequestProblem(detail="'password' is too short - minimum is 6 characters")
            raise problem
        
        response = self.client.get('/test-password-policy')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data["code"] == "invalid_password"
        assert "Password does not meet security requirements" in data["message"]
        assert data["details"]["field"] == "password"
    
    def test_generic_enum_validation_error(self):
        """Test handling of generic enum validation errors."""
        @self.app.route('/test-generic-enum')
        def trigger_enum():
            error = BadRequest("'invalid_value' is not one of allowed values")
            error.description = "'invalid_value' is not one of allowed values"
            raise error
        
        response = self.client.get('/test-generic-enum')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data["code"] == "invalid_enum_value"
    
    def test_connexion_bad_request_problem(self):
        """Test handling of Connexion BadRequestProblem."""
        @self.app.route('/test-connexion')
        def trigger_connexion():
            raise BadRequestProblem(detail="Request validation failed")
        
        response = self.client.get('/test-connexion')
        
        assert response.status_code == 400
        data = response.get_json()
        assert data["code"] == "validation_error"
        assert data["details"]["validation_detail"] == "Request validation failed"


class TestErrorResponseConsistency:
    """Test that all error responses follow consistent schema."""
    
    def setup_method(self):
        """Set up Flask app with all error handlers."""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        register_error_handlers(self.app)
        register_custom_error_handlers(self.app)
        
        self.client = self.app.test_client()
    
    def test_error_schema_consistency(self):
        """Test that all error responses follow Error schema."""
        # Define routes that trigger different error types
        @self.app.route('/test-validation')
        def trigger_validation():
            raise ValidationError("Validation failed")
            
        @self.app.route('/test-auth')
        def trigger_auth():
            raise AuthenticationError("Auth failed")
            
        @self.app.route('/test-authz')
        def trigger_authz():
            raise AuthorizationError("Access denied")
            
        @self.app.route('/test-notfound')
        def trigger_notfound():
            raise NotFoundError("Not found")
            
        @self.app.route('/test-500')
        def trigger_500():
            raise Exception("Internal error")
        
        # Test each error type
        test_routes = [
            '/test-validation',
            '/test-auth', 
            '/test-authz',
            '/test-notfound',
            '/test-500'
        ]
        
        for route in test_routes:
            response = self.client.get(route)
            data = response.get_json()
            
            # All responses should have consistent schema
            assert "code" in data, f"Missing 'code' in response from {route}"
            assert "message" in data, f"Missing 'message' in response from {route}"
            assert "details" in data, f"Missing 'details' in response from {route}"
            
            # Code and message should be non-empty strings
            assert isinstance(data["code"], str), f"Code not string in {route}"
            assert len(data["code"]) > 0, f"Empty code in {route}"
            assert isinstance(data["message"], str), f"Message not string in {route}"
            assert len(data["message"]) > 0, f"Empty message in {route}"
            
            # Details should be a dict
            assert isinstance(data["details"], dict), f"Details not dict in {route}"
    
    def test_error_model_compatibility(self):
        """Test that error responses are compatible with Error model."""
        @self.app.route('/test-model')
        def trigger_model():
            raise ValidationError("Test error")
        
        response = self.client.get('/test-model')
        data = response.get_json()
        
        # Should be able to create Error model from response
        try:
            error_model = Error(
                code=data["code"],
                message=data["message"],
                details=data["details"]
            )
            
            # Verify model has expected attributes
            assert error_model.code == data["code"]
            assert error_model.message == data["message"]
            assert error_model.details == data["details"]
            
        except Exception as e:
            pytest.fail(f"Error response not compatible with Error model: {e}")


class TestErrorHandlerLogging:
    """Test that error handlers properly log errors."""
    
    def setup_method(self):
        """Set up Flask app for logging tests."""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        register_error_handlers(self.app)
        register_custom_error_handlers(self.app)
        
        self.client = self.app.test_client()
    
    @patch('openapi_server.impl.error_handler.logger')
    def test_error_logging_levels(self, mock_logger):
        """Test that different error types use appropriate logging levels."""
        # Define routes for different error types
        @self.app.route('/test-validation')
        def trigger_validation():
            raise ValidationError("Validation failed")
            
        @self.app.route('/test-auth')  
        def trigger_auth():
            raise AuthenticationError("Auth failed")
            
        @self.app.route('/test-500')
        def trigger_500():
            raise Exception("Internal error")
        
        # Test validation error (should be warning)
        self.client.get('/test-validation')
        mock_logger.warning.assert_called()
        
        # Test authentication error (should be warning)
        mock_logger.reset_mock()
        self.client.get('/test-auth')
        mock_logger.warning.assert_called()
        
        # Test internal error (should be error with exc_info)
        mock_logger.reset_mock()
        self.client.get('/test-500')
        mock_logger.error.assert_called()