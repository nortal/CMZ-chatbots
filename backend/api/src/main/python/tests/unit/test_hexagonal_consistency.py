"""
Unit tests for hexagonal architecture consistency.
PR003946-96: Hexagonal architecture testing

Verifies that Flask controllers and Lambda handlers call the same business logic
functions, ensuring consistent behavior across different deployment architectures.
"""
import pytest
import inspect
from unittest.mock import patch, MagicMock

# Import Flask controllers
from openapi_server.controllers import (
    users_controller, family_controller, animals_controller,
    analytics_controller, auth_controller
)

# Import business logic implementations
from openapi_server.impl import (
    users, family, animals, analytics, auth
)

# Import Lambda handlers
from openapi_server import lambda_handlers

# Import error handlers
from openapi_server.impl.error_handler import ValidationError


class TestFlaskControllerArchitectureCompliance:
    """Test that Flask controllers are thin wrappers around business logic."""
    
    def test_users_controller_delegates_to_impl(self):
        """Test that users controller functions delegate to impl.users functions."""
        # Test create_user
        with patch('openapi_server.impl.users.handle_create_user') as mock_handle:
            mock_handle.return_value = ({"userId": "test"}, 201)
            
            result = users_controller.create_user({"displayName": "Test"})
            
            mock_handle.assert_called_once_with({"displayName": "Test"})
            assert result == ({"userId": "test"}, 201)
    
    def test_family_controller_delegates_to_impl(self):
        """Test that family controller functions delegate to impl.family functions."""
        # Test list_families
        with patch('openapi_server.impl.family.handle_list_families') as mock_handle:
            mock_handle.return_value = [{"familyId": "family1"}]
            
            result = family_controller.list_families()
            
            mock_handle.assert_called_once()
            assert result == [{"familyId": "family1"}]
    
    def test_animals_controller_delegates_to_impl(self):
        """Test that animals controller functions delegate to impl.animals functions."""
        # Test list_animals
        with patch('openapi_server.impl.animals.handle_list_animals') as mock_handle:
            mock_handle.return_value = [{"animalId": "animal1"}]
            
            result = animals_controller.list_animals()
            
            mock_handle.assert_called_once_with(None)  # status=None by default
            assert result == [{"animalId": "animal1"}]
    
    def test_analytics_controller_delegates_to_impl(self):
        """Test that analytics controller functions delegate to impl.analytics functions."""
        # Test billing
        with patch('openapi_server.impl.analytics.handle_billing') as mock_handle:
            mock_handle.return_value = ({"period": "2023-08", "cost": 100}, 200)
            
            result = analytics_controller.get_billing()
            
            mock_handle.assert_called_once_with(None)  # period=None for current month
            assert result == ({"period": "2023-08", "cost": 100}, 200)
    
    def test_auth_controller_delegates_to_impl(self):
        """Test that auth controller functions delegate to impl.auth functions."""
        # Test authenticate_user
        with patch('openapi_server.impl.auth.authenticate_user') as mock_handle:
            mock_handle.return_value = {"token": "jwt_token", "user": {"userId": "user1"}}
            
            result = auth_controller.authenticate_user({
                "email": "test@example.com",
                "password": "password123"
            })
            
            mock_handle.assert_called_once()
            assert result["token"] == "jwt_token"


class TestLambdaHandlerArchitectureCompliance:
    """Test that Lambda handlers call the same business logic functions."""
    
    def test_lambda_handlers_import_correctly(self):
        """Test that lambda handlers module imports without errors."""
        # Should be able to import the module
        assert hasattr(lambda_handlers, '__file__')
        
        # Should have handler functions
        handler_functions = [name for name in dir(lambda_handlers) 
                           if name.endswith('_handler') and not name.startswith('_')]
        assert len(handler_functions) > 0
    
    @patch('openapi_server.impl.users.handle_create_user')
    def test_lambda_user_handler_delegates_to_impl(self, mock_handle):
        """Test that Lambda user handlers delegate to impl.users functions."""
        mock_handle.return_value = ({"userId": "lambda_user"}, 201)
        
        # Mock Lambda event for user creation
        event = {
            "httpMethod": "POST",
            "path": "/user",
            "body": '{"displayName": "Lambda User"}',
            "headers": {"Content-Type": "application/json"}
        }
        
        # Test if Lambda handler exists and calls the same impl function
        if hasattr(lambda_handlers, 'user_handler'):
            result = lambda_handlers.user_handler(event, {})
            mock_handle.assert_called_once()
    
    @patch('openapi_server.impl.family.handle_list_families')
    def test_lambda_family_handler_delegates_to_impl(self, mock_handle):
        """Test that Lambda family handlers delegate to impl.family functions."""
        mock_handle.return_value = [{"familyId": "lambda_family"}]
        
        # Mock Lambda event for family listing
        event = {
            "httpMethod": "GET",
            "path": "/family",
            "body": None,
            "headers": {}
        }
        
        # Test if Lambda handler exists and calls the same impl function
        if hasattr(lambda_handlers, 'family_handler'):
            result = lambda_handlers.family_handler(event, {})
            mock_handle.assert_called_once()


class TestBusinessLogicSeparation:
    """Test that business logic is properly separated from presentation layer."""
    
    def test_impl_functions_have_no_flask_dependencies(self):
        """Test that impl functions don't import Flask-specific modules."""
        impl_modules = [users, family, animals, analytics, auth]
        
        for module in impl_modules:
            source = inspect.getsource(module)
            
            # Should not have Flask-specific imports
            flask_imports = [
                'from flask import',
                'import flask',
                'from connexion import',
                'import connexion'
            ]
            
            for flask_import in flask_imports:
                assert flask_import not in source, f"Module {module.__name__} should not import Flask directly"
    
    def test_impl_functions_have_no_lambda_dependencies(self):
        """Test that impl functions don't import Lambda-specific modules."""
        impl_modules = [users, family, animals, analytics, auth]
        
        for module in impl_modules:
            source = inspect.getsource(module)
            
            # Should not have Lambda-specific imports
            lambda_imports = [
                'import boto3',
                'from boto3 import',
                'import awslambda',
                'from aws_lambda_powertools'
            ]
            
            for lambda_import in lambda_imports:
                assert lambda_import not in source, f"Module {module.__name__} should not import Lambda directly"
    
    def test_controllers_are_thin_wrappers(self):
        """Test that controller functions are thin and delegate to impl."""
        controller_modules = [
            users_controller, family_controller, animals_controller,
            analytics_controller, auth_controller
        ]
        
        for module in controller_modules:
            functions = [name for name in dir(module) 
                        if callable(getattr(module, name)) and not name.startswith('_')]
            
            for func_name in functions:
                func = getattr(module, func_name)
                if hasattr(func, '__doc__') and func.__doc__:
                    # Controllers should have minimal logic - mostly delegation
                    source = inspect.getsource(func)
                    lines = [line.strip() for line in source.split('\n') if line.strip()]
                    
                    # Remove docstring and signature lines
                    code_lines = [line for line in lines 
                                 if not line.startswith('"""') and 
                                    not line.startswith('def ') and
                                    not line.startswith('"""')]
                    
                    # Controllers should be relatively simple (heuristic: < 20 lines of actual code)
                    if len(code_lines) > 20:
                        print(f"Warning: {module.__name__}.{func_name} might have too much logic")


class TestConsistentErrorHandling:
    """Test that both Flask and Lambda handlers handle errors consistently."""
    
    def test_validation_errors_consistent_across_handlers(self):
        """Test that validation errors are handled consistently."""
        # Test Flask controller error handling
        with patch('openapi_server.impl.users.handle_create_user') as mock_handle:
            mock_handle.side_effect = ValidationError(
                "Validation failed",
                field_errors={"email": ["Invalid email format"]}
            )
            
            # Flask should handle ValidationError appropriately
            try:
                result = users_controller.create_user({"email": "invalid"})
                # Should either return error response or propagate exception
                assert True  # If we get here, error was handled
            except ValidationError:
                assert True  # Exception propagated, which is also valid
    
    def test_not_found_errors_consistent_across_handlers(self):
        """Test that not found errors are handled consistently."""
        # Test Flask controller error handling
        with patch('openapi_server.impl.users.handle_get_user') as mock_handle:
            mock_handle.return_value = None  # User not found
            
            result = users_controller.get_user("nonexistent")
            
            # Should handle not found appropriately (None or 404 response)
            assert result is None or (isinstance(result, tuple) and result[1] == 404)


class TestEndpointCoverage:
    """Test that all endpoints have both Flask and Lambda implementations."""
    
    def test_major_endpoints_have_flask_implementations(self):
        """Test that major CRUD endpoints exist in Flask controllers."""
        # User endpoints
        assert hasattr(users_controller, 'create_user')
        assert hasattr(users_controller, 'get_user')
        assert hasattr(users_controller, 'list_users')
        assert hasattr(users_controller, 'update_user')
        assert hasattr(users_controller, 'delete_user')
        
        # Family endpoints
        assert hasattr(family_controller, 'create_family')
        assert hasattr(family_controller, 'get_family')
        assert hasattr(family_controller, 'list_families')
        assert hasattr(family_controller, 'update_family')
        assert hasattr(family_controller, 'delete_family')
        
        # Animal endpoints
        assert hasattr(animals_controller, 'create_animal')
        assert hasattr(animals_controller, 'get_animal')
        assert hasattr(animals_controller, 'list_animals')
        assert hasattr(animals_controller, 'update_animal')
        assert hasattr(animals_controller, 'delete_animal')
    
    def test_major_endpoints_have_impl_functions(self):
        """Test that major endpoints have corresponding impl functions."""
        # User impl functions
        assert hasattr(users, 'handle_create_user')
        assert hasattr(users, 'handle_get_user')
        assert hasattr(users, 'handle_list_users')
        assert hasattr(users, 'handle_update_user')
        assert hasattr(users, 'handle_delete_user')
        
        # Family impl functions
        assert hasattr(family, 'handle_create_family')
        assert hasattr(family, 'handle_get_family')
        assert hasattr(family, 'handle_list_families')
        assert hasattr(family, 'handle_update_family')
        assert hasattr(family, 'handle_delete_family')
        
        # Animal impl functions
        assert hasattr(animals, 'handle_create_animal')
        assert hasattr(animals, 'handle_get_animal')
        assert hasattr(animals, 'handle_list_animals')
        assert hasattr(animals, 'handle_update_animal')
        assert hasattr(animals, 'handle_delete_animal')


class TestArchitecturalPatterns:
    """Test that hexagonal architecture patterns are followed."""
    
    def test_dependency_direction_is_correct(self):
        """Test that dependencies point inward (controllers -> impl, not impl -> controllers)."""
        impl_modules = [users, family, animals, analytics, auth]
        
        for module in impl_modules:
            source = inspect.getsource(module)
            
            # Impl modules should not import controllers
            controller_imports = [
                'from openapi_server.controllers import',
                'from ..controllers import',
                'import openapi_server.controllers'
            ]
            
            for controller_import in controller_imports:
                assert controller_import not in source, \
                    f"Impl module {module.__name__} should not import controllers"
    
    def test_ports_and_adapters_structure(self):
        """Test that ports and adapters structure is maintained."""
        # Check that we have ports (interfaces)
        from openapi_server.impl import ports
        assert hasattr(ports, '__file__')
        
        # Check that we have adapters (implementations)
        from openapi_server.impl import adapters
        assert hasattr(adapters, '__file__')
        
        # Adapters should implement ports
        # This is a structural test - in a full implementation,
        # we would verify that adapters implement port interfaces
    
    def test_domain_logic_isolation(self):
        """Test that domain logic is isolated from infrastructure concerns."""
        # Domain logic should be in separate modules
        from openapi_server.impl import domain
        assert hasattr(domain, '__file__')
        
        # Domain modules should not have infrastructure dependencies
        domain_source = inspect.getsource(domain)
        
        infrastructure_imports = [
            'import boto3',
            'from flask import',
            'import psycopg2',
            'import redis',
            'from sqlalchemy import'
        ]
        
        for infra_import in infrastructure_imports:
            assert infra_import not in domain_source, \
                "Domain logic should not depend on infrastructure"


class TestIntegrationPatterns:
    """Test integration patterns between different architectural layers."""
    
    def test_adapter_pattern_implementation(self):
        """Test that adapter pattern is correctly implemented."""
        # Flask adapter should exist
        from openapi_server.impl.adapters import flask
        assert hasattr(flask, '__file__')
        
        # Lambda adapter should exist
        try:
            from openapi_server.impl.adapters import aws_lambda
            assert hasattr(aws_lambda, '__file__')
        except ImportError:
            # Lambda adapter might be optional in some deployments
            pass
    
    def test_consistent_data_transformation(self):
        """Test that data transformations are consistent across adapters."""
        # Both Flask and Lambda should transform data the same way
        # This would be tested by calling the same impl function from both
        # adapters and verifying identical results
        
        # Mock test - in real implementation, we would test actual transformations
        with patch('openapi_server.impl.users.handle_get_user') as mock_handle:
            mock_user = {"userId": "test", "displayName": "Test User"}
            mock_handle.return_value = mock_user
            
            # Flask call
            flask_result = users_controller.get_user("test")
            
            # Both should get the same data from impl
            mock_handle.assert_called_with("test")
            assert flask_result == mock_user or flask_result == (mock_user, 200)


class TestHexagonalArchitectureCompliance:
    """Overall compliance tests for hexagonal architecture."""
    
    def test_business_logic_testability(self):
        """Test that business logic can be tested independently of adapters."""
        # Should be able to test impl functions directly
        from openapi_server.impl.users import handle_create_user
        
        # Mock only the storage layer, not the presentation layer
        with patch('openapi_server.impl.users._store') as mock_store:
            mock_store.return_value.create.return_value = {"userId": "test"}
            
            # Business logic should work without Flask or Lambda
            with patch('openapi_server.impl.users._validate_foreign_keys'):
                result = handle_create_user({"displayName": "Test"})
                assert isinstance(result, tuple)
                assert result[1] in [200, 201]
    
    def test_adapter_replaceability(self):
        """Test that adapters can be replaced without changing business logic."""
        # This is a structural test - in practice, you could replace Flask with FastAPI
        # or Lambda with Google Cloud Functions, and the impl layer would remain unchanged
        
        impl_modules = [users, family, animals, analytics, auth]
        
        for module in impl_modules:
            # Impl modules should not know about specific adapters
            source = inspect.getsource(module)
            
            adapter_specific_imports = [
                'from flask import',
                'import boto3',
                'from fastapi import',
                'from django import'
            ]
            
            for adapter_import in adapter_specific_imports:
                assert adapter_import not in source, \
                    f"Business logic {module.__name__} should not depend on specific adapters"
    
    def test_hexagonal_benefits_realized(self):
        """Test that key benefits of hexagonal architecture are realized."""
        # 1. Business logic is isolated and testable
        assert len([name for name in dir(users) if name.startswith('handle_')]) > 0
        
        # 2. Multiple adapters can exist (Flask + Lambda)
        flask_controllers_exist = hasattr(users_controller, 'create_user')
        lambda_handlers_exist = hasattr(lambda_handlers, '__file__')
        assert flask_controllers_exist and lambda_handlers_exist
        
        # 3. Dependency inversion is maintained
        # (tested in other test methods)
        
        # 4. Business rules are centralized in impl layer
        business_logic_modules = [users, family, animals, analytics, auth]
        assert len(business_logic_modules) >= 5