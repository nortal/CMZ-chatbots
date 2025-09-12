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