"""
API Validation Utilities

Implements validation logic for API hardening tickets:
- PR003946-70: Reject client-provided IDs  
- PR003946-82: Filter parameter validation
- PR003946-86: Billing period format validation
- PR003946-79: Family membership constraints
- PR003946-80: Parent-student relationship validation
"""

import re
from typing import Dict, Any, List, Optional
from datetime import datetime

from ...impl.error_handler import ValidationError

# Error code constants for consistency
ERROR_INVALID_REQUEST = "invalid_request"
ERROR_INVALID_FILTER = "invalid_filter"
ERROR_INVALID_FORMAT = "invalid_format"
ERROR_INVALID_MONTH = "invalid_month"
ERROR_INVALID_YEAR = "invalid_year"
ERROR_VALIDATION_ERROR = "validation_error"


def create_validation_error(error_type: str, message: str, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Create consistent validation error response.
    
    PR003946-90: Consistent Error schema implementation
    """
    error = {
        "code": error_type,  # Use the specific error type as the code
        "message": message,
        "details": details or {}
    }
    
    if error_type:
        error["details"]["error_type"] = error_type
        
    return error


def validate_no_client_id(data: Dict[str, Any], id_field: str) -> Optional[Dict[str, Any]]:
    """
    PR003946-70: Validate that client has not provided an ID field.
    
    Args:
        data: Request data dictionary
        id_field: ID field name (e.g., 'animalId', 'userId')
        
    Returns:
        Error dict if validation fails, None if valid
    """
    if id_field in data and data[id_field] is not None:
        return create_validation_error(
            ERROR_INVALID_REQUEST,
            f"Client-provided {id_field} not allowed. IDs are server-generated.",
            {"field": id_field, "provided_value": data[id_field]}
        )
    return None


def validate_animal_status_filter(status: str) -> Optional[Dict[str, Any]]:
    """
    PR003946-82: Validate animal status filter parameter.
    
    Args:
        status: Status filter value
        
    Returns:
        Error dict if validation fails, None if valid
    """
    valid_statuses = ["active", "inactive", "hidden", "breeding", "retired"]
    
    if status not in valid_statuses:
        return create_validation_error(
            ERROR_INVALID_FILTER,
            f"Invalid status filter value: {status}",
            {
                "field": "status",
                "provided_value": status,
                "valid_values": valid_statuses
            }
        )
    return None


def validate_billing_period(period: str) -> Optional[Dict[str, Any]]:
    """
    PR003946-86: Validate billing period format (YYYY-MM).
    
    Args:
        period: Period string to validate
        
    Returns:
        Error dict if validation fails, None if valid
    """
    # Check format YYYY-MM
    if not re.match(r'^\d{4}-\d{2}$', period):
        return create_validation_error(
            ERROR_INVALID_FORMAT,
            f"Invalid billing period format: {period}. Expected format: YYYY-MM",
            {
                "field": "period", 
                "provided_value": period,
                "expected_format": "YYYY-MM"
            }
        )
    
    try:
        year_str, month_str = period.split('-')
        year = int(year_str)
        month = int(month_str)
        
        # Validate month range
        if month < 1 or month > 12:
            return create_validation_error(
                ERROR_INVALID_MONTH,
                f"Invalid month: {month}. Month must be 01-12",
                {
                    "field": "period",
                    "provided_value": period,
                    "invalid_month": month
                }
            )
            
        # Validate reasonable year range  
        current_year = datetime.now().year
        if year < 2020 or year > current_year + 5:
            return create_validation_error(
                ERROR_INVALID_YEAR, 
                f"Invalid year: {year}. Year must be between 2020 and {current_year + 5}",
                {
                    "field": "period",
                    "provided_value": period,
                    "invalid_year": year
                }
            )
            
    except ValueError:
        return create_validation_error(
            ERROR_INVALID_FORMAT,
            f"Invalid billing period format: {period}. Expected format: YYYY-MM",
            {
                "field": "period",
                "provided_value": period,
                "expected_format": "YYYY-MM"
            }
        )
    
    return None


def validate_user_references(user_ids: List[str], existing_users: List[str]) -> Optional[Dict[str, Any]]:
    """
    PR003946-79: Validate that user references exist.
    
    Args:
        user_ids: List of user IDs to validate
        existing_users: List of existing user IDs
        
    Returns:
        Error dict if validation fails, None if valid
    """
    if not user_ids:
        return None
        
    missing_users = [uid for uid in user_ids if uid not in existing_users]
    
    if missing_users:
        return create_validation_error(
            ERROR_VALIDATION_ERROR,
            f"Referenced users do not exist: {', '.join(missing_users)}",
            {
                "entity_type": "family",
                "missing_references": missing_users,
                "field": "user_references"
            }
        )
    
    return None


def validate_parent_student_separation(parents: List[str], students: List[str]) -> Optional[Dict[str, Any]]:
    """
    PR003946-80: Validate that no user is both parent and student.
    
    Args:
        parents: List of parent user IDs
        students: List of student user IDs  
        
    Returns:
        Error dict if validation fails, None if valid
    """
    if not parents or not students:
        return None
        
    overlap = set(parents) & set(students)
    
    if overlap:
        return create_validation_error(
            ERROR_VALIDATION_ERROR,
            f"Users cannot be both parent and student: {', '.join(overlap)}",
            {
                "entity_type": "family",
                "conflicting_users": list(overlap),
                "field": "parent_student_relationship"
            }
        )
    
    return None


def validate_family_data(family_data: Dict[str, Any], existing_users: List[str]) -> Optional[Dict[str, Any]]:
    """
    Combined family validation for PR003946-79 and PR003946-80.
    
    Args:
        family_data: Family data to validate
        existing_users: List of existing user IDs
        
    Returns:
        Error dict if validation fails, None if valid
    """
    parents = family_data.get('parents', [])
    students = family_data.get('students', [])
    
    # PR003946-79: Validate user references exist
    all_users = parents + students
    user_ref_error = validate_user_references(all_users, existing_users)
    if user_ref_error:
        return user_ref_error
        
    # PR003946-80: Validate parent-student separation
    separation_error = validate_parent_student_separation(parents, students)
    if separation_error:
        return separation_error
        
    return None


def validate_email(email: str) -> None:
    """
    Validate email format using regex pattern.

    Args:
        email: Email address to validate

    Raises:
        ValidationError: If email format is invalid
    """
    if not email:
        raise ValidationError("Invalid email", field_errors={"email": ["Email is required"]})

    # Check for invalid patterns first
    if '..' in email:  # Double dots are invalid
        raise ValidationError("Invalid email format", field_errors={"email": ["Email format is invalid - consecutive dots not allowed"]})

    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if not re.match(pattern, email):
        raise ValidationError("Invalid email format", field_errors={"email": ["Email format is invalid"]})


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> None:
    """
    Validate that all required fields are present and not empty.
    
    Args:
        data: Data dictionary to validate
        required_fields: List of field names that are required
        
    Raises:
        ValidationError: If any required fields are missing or empty
    """
    if not required_fields:
        return  # No validation needed
    
    missing_fields = []
    empty_fields = []
    
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
        elif not data[field] or (isinstance(data[field], str) and data[field].strip() == ""):
            empty_fields.append(field)
    
    field_errors = {}
    
    if missing_fields:
        for field in missing_fields:
            field_errors[field] = [f"Field '{field}' is required"]
    
    if empty_fields:
        for field in empty_fields:
            field_errors[field] = [f"Field '{field}' cannot be empty"]
    
    if field_errors:
        raise ValidationError("Required field validation failed", field_errors=field_errors)


# ============================================================================
# Contract Validation Decorators (Task 4.1: Prevention Phase 2)
# ============================================================================

import functools
import yaml
from pathlib import Path
from typing import Callable, Tuple
from jsonschema import validate, ValidationError as JsonSchemaValidationError


# Cache for OpenAPI specification
_openapi_spec: Optional[Dict[str, Any]] = None


def _load_openapi_spec() -> Dict[str, Any]:
    """Load and cache OpenAPI specification"""
    global _openapi_spec

    if _openapi_spec is None:
        # Find openapi_spec.yaml relative to this file
        current_file = Path(__file__)
        spec_path = current_file.parent.parent.parent.parent.parent.parent / 'openapi_spec.yaml'

        if not spec_path.exists():
            # Try alternative path
            spec_path = Path.cwd() / 'backend' / 'api' / 'openapi_spec.yaml'

        if not spec_path.exists():
            raise FileNotFoundError(f"OpenAPI spec not found at {spec_path}")

        with open(spec_path) as f:
            _openapi_spec = yaml.safe_load(f)

    return _openapi_spec


def _get_schema_for_endpoint(method: str, path: str, schema_type: str = 'requestBody') -> Optional[Dict[str, Any]]:
    """
    Extract schema from OpenAPI spec for a given endpoint

    Args:
        method: HTTP method (get, post, put, patch, delete)
        path: API path (e.g., '/animal/{id}')
        schema_type: 'requestBody' or 'response'

    Returns:
        Schema dictionary or None if not found
    """
    spec = _load_openapi_spec()

    if path not in spec.get('paths', {}):
        return None

    endpoint = spec['paths'][path].get(method.lower())
    if not endpoint:
        return None

    if schema_type == 'requestBody':
        request_body = endpoint.get('requestBody', {})
        content = request_body.get('content', {})
        json_content = content.get('application/json', {})
        schema_ref = json_content.get('schema', {})

        # Resolve $ref if present
        if '$ref' in schema_ref:
            ref_path = schema_ref['$ref'].split('/')
            schema = spec
            for part in ref_path[1:]:  # Skip leading '#'
                schema = schema.get(part, {})
            return schema

        return schema_ref

    elif schema_type == 'response':
        responses = endpoint.get('responses', {})
        success_response = responses.get('200', {}) or responses.get('201', {})
        content = success_response.get('content', {})
        json_content = content.get('application/json', {})
        schema_ref = json_content.get('schema', {})

        # Resolve $ref if present
        if '$ref' in schema_ref:
            ref_path = schema_ref['$ref'].split('/')
            schema = spec
            for part in ref_path[1:]:
                schema = schema.get(part, {})
            return schema

        return schema_ref

    return None


def validate_request(method: str, path: str):
    """
    Decorator to validate request body against OpenAPI schema

    Usage:
        @validate_request('post', '/animal')
        def handle_animal_post(body):
            # body is guaranteed to match OpenAPI schema
            return create_animal(body)

    Args:
        method: HTTP method (post, put, patch)
        path: API path from OpenAPI spec

    Raises:
        ValidationError: If request body doesn't match schema
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Tuple[Any, int]:
            # Extract body from arguments
            body = None
            if 'body' in kwargs:
                body = kwargs['body']
            elif len(args) > 0:
                # Assume first positional argument is body
                body = args[0]

            if body is None:
                return {"error": "Missing request body"}, 400

            # Get schema and validate
            try:
                schema = _get_schema_for_endpoint(method, path, 'requestBody')
                if schema:
                    # Convert body to dict if it's a model object
                    body_dict = body.to_dict() if hasattr(body, 'to_dict') else body
                    validate(instance=body_dict, schema=schema)
            except JsonSchemaValidationError as e:
                return {
                    "error": "Request validation failed",
                    "details": str(e.message),
                    "path": list(e.path)
                }, 400
            except Exception as e:
                # Schema not found or validation error - log but don't block
                print(f"⚠️ Validation decorator error for {method} {path}: {e}")

            # Call original function
            return func(*args, **kwargs)

        return wrapper
    return decorator


def validate_types(**expected_types):
    """
    Decorator to validate parameter types at runtime

    Usage:
        @validate_types(animal_id=str, body=dict)
        def handle_animal_put(animal_id, body):
            # Parameters guaranteed to have correct types
            return update_animal(animal_id, body)

    Args:
        **expected_types: Keyword arguments mapping parameter names to expected types

    Raises:
        TypeError: If parameter type doesn't match expected type
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Tuple[Any, int]:
            # Get function signature
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            # Validate each parameter
            for param_name, expected_type in expected_types.items():
                if param_name in bound_args.arguments:
                    actual_value = bound_args.arguments[param_name]

                    # Skip None values if Optional type
                    if actual_value is None:
                        continue

                    # Check type
                    if not isinstance(actual_value, expected_type):
                        return {
                            "error": f"Parameter '{param_name}' must be {expected_type.__name__}",
                            "actual_type": type(actual_value).__name__
                        }, 400

            # Call original function
            return func(*args, **kwargs)

        return wrapper
    return decorator


def validate_required_fields_decorator(*required_fields_list):
    """
    Decorator to validate that required fields are present in request body

    Usage:
        @validate_required_fields_decorator('email', 'password')
        def handle_login_post(body):
            # body guaranteed to have email and password fields
            return authenticate(body['email'], body['password'])

    Args:
        *required_fields_list: Field names that must be present in body

    Raises:
        ValidationError: If required field is missing
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Tuple[Any, int]:
            # Extract body
            body = kwargs.get('body') or (args[0] if args else None)

            if body is None:
                return {"error": "Missing request body"}, 400

            # Convert to dict if model
            body_dict = body.to_dict() if hasattr(body, 'to_dict') else body

            # Check required fields
            missing_fields = []
            for field in required_fields_list:
                if field not in body_dict or body_dict[field] is None or body_dict[field] == '':
                    missing_fields.append(field)

            if missing_fields:
                return {
                    "error": "Missing required fields",
                    "missing_fields": missing_fields
                }, 400

            # Call original function
            return func(*args, **kwargs)

        return wrapper
    return decorator


def validate_response_schema(method: str, path: str):
    """
    Decorator to validate response body against OpenAPI schema

    Usage:
        @validate_response_schema('get', '/animal/{id}')
        def handle_animal_get(animal_id):
            animal = get_animal(animal_id)
            return animal, 200  # Validated against OpenAPI response schema

    Args:
        method: HTTP method
        path: API path from OpenAPI spec

    Note: This decorator logs validation failures but doesn't block responses
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Tuple[Any, int]:
            # Call original function
            result = func(*args, **kwargs)

            # Extract response body and status code
            if isinstance(result, tuple) and len(result) == 2:
                response_body, status_code = result
            else:
                response_body = result
                status_code = 200

            # Validate response against schema (non-blocking)
            try:
                schema = _get_schema_for_endpoint(method, path, 'response')
                if schema and response_body:
                    # Convert to dict if model
                    response_dict = response_body.to_dict() if hasattr(response_body, 'to_dict') else response_body
                    validate(instance=response_dict, schema=schema)
            except JsonSchemaValidationError as e:
                # Log but don't block response
                print(f"⚠️ Response validation failed for {method} {path}: {e.message}")
            except Exception as e:
                print(f"⚠️ Response validation error for {method} {path}: {e}")

            return result

        return wrapper
    return decorator