"""Business validation rules and utilities"""
import re
from typing import Dict, Any, List, Optional
from .exceptions import ValidationError


def validate_email(email: str) -> None:
    """Validate email format"""
    if not email:
        raise ValidationError("Email is required")
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise ValidationError(f"Invalid email format: {email}")


def validate_user_role(role: str) -> None:
    """Validate user role is in allowed values"""
    allowed_roles = ["visitor", "user", "editor", "admin"]
    if role not in allowed_roles:
        raise ValidationError(f"Invalid role '{role}'. Must be one of: {allowed_roles}")


def validate_user_type(user_type: str) -> None:
    """Validate user type is in allowed values"""
    allowed_types = ["none", "parent", "student"]
    if user_type not in allowed_types:
        raise ValidationError(f"Invalid user_type '{user_type}'. Must be one of: {allowed_types}")


def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> None:
    """Validate that all required fields are present and not empty"""
    missing_fields = []
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == "":
            missing_fields.append(field)
    
    if missing_fields:
        raise ValidationError(f"Missing required fields: {missing_fields}")


def validate_user_creation_data(data: Dict[str, Any]) -> None:
    """Validate data for user creation"""
    validate_required_fields(data, ["email"])
    validate_email(data["email"])
    
    if "role" in data and data["role"]:
        validate_user_role(data["role"])
    
    if "userType" in data and data["userType"]:
        validate_user_type(data["userType"])


def validate_user_details_creation_data(data: Dict[str, Any]) -> None:
    """Validate data for user details creation"""
    validate_required_fields(data, ["userId"])
    
    # Validate userId format if needed
    user_id = data["userId"]
    if not isinstance(user_id, str) or len(user_id.strip()) == 0:
        raise ValidationError("userId must be a non-empty string")


def validate_family_creation_data(data: Dict[str, Any]) -> None:
    """Validate data for family creation"""
    # Family validation rules - adjust based on business requirements
    if "name" in data and data["name"] is not None and len(data["name"].strip()) == 0:
        raise ValidationError("Family name cannot be empty if provided")


def validate_animal_creation_data(data: Dict[str, Any]) -> None:
    """Validate data for animal creation"""
    validate_required_fields(data, ["name"])
    
    name = data["name"]
    if not isinstance(name, str) or len(name.strip()) == 0:
        raise ValidationError("Animal name must be a non-empty string")


def validate_soft_delete_allowed(entity_data: Dict[str, Any], entity_type: str) -> None:
    """Validate that entity can be soft deleted"""
    if entity_data.get("softDelete", False):
        raise ValidationError(f"{entity_type} is already deleted")


def validate_update_allowed(current_data: Dict[str, Any], entity_type: str) -> None:
    """Validate that entity can be updated"""
    validate_soft_delete_allowed(current_data, entity_type)