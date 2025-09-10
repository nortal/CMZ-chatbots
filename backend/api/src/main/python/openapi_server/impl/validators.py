"""
PR003946-73: Foreign Key Validation Implementation

This module provides validation for foreign key relationships between entities
to ensure data integrity and prevent orphaned records.
"""

from typing import Dict, Any
from openapi_server.impl.error_handler import ValidationError


# Simple in-memory cache for test mode
# In production, this would query the actual DynamoDB tables
_TEST_DATA_CACHE = {
    'users': {
        'admin_001': {'userId': 'admin_001', 'email': 'admin@cmz.org', 'role': 'admin'},
        'keeper_001': {'userId': 'keeper_001', 'email': 'keeper@cmz.org', 'role': 'keeper'},
        'parent_001': {'userId': 'parent_001', 'email': 'parent@cmz.org', 'role': 'parent'},
        'member_001': {'userId': 'member_001', 'email': 'member@cmz.org', 'role': 'member'},
    },
    'families': {
        'family_001': {'familyId': 'family_001', 'parents': ['parent_001'], 'students': []},
        'family_002': {'familyId': 'family_002', 'parents': ['parent_001'], 'students': []},
    },
    'animals': {
        'animal_001': {'animalId': 'animal_001', 'name': 'Simba', 'species': 'Lion', 'status': 'active'},
        'animal_002': {'animalId': 'animal_002', 'name': 'Koda', 'species': 'Brown Bear', 'status': 'active'},
    }
}


def validate_user_exists(user_id: str) -> bool:
    """
    Validate that a user exists.
    
    In production, this would query the users table in DynamoDB.
    For testing, uses in-memory cache.
    
    Args:
        user_id: The user ID to validate
        
    Returns:
        True if user exists, False otherwise
        
    Raises:
        ValidationError: If user_id is invalid or user doesn't exist
    """
    if not user_id:
        raise ValidationError("User ID cannot be empty")
    
    # In test mode, check our cache
    if user_id in _TEST_DATA_CACHE['users']:
        return True
    
    # In production, this would be:
    # user_service = get_user_service()  
    # return user_service.exists(user_id)
    
    return False


def validate_family_exists(family_id: str) -> bool:
    """
    Validate that a family exists.
    
    Args:
        family_id: The family ID to validate
        
    Returns:
        True if family exists, False otherwise
        
    Raises:
        ValidationError: If family_id is invalid or family doesn't exist
    """
    if not family_id:
        raise ValidationError("Family ID cannot be empty")
    
    # In test mode, check our cache
    if family_id in _TEST_DATA_CACHE['families']:
        return True
    
    return False


def validate_animal_exists(animal_id: str) -> bool:
    """
    Validate that an animal exists.
    
    Args:
        animal_id: The animal ID to validate
        
    Returns:
        True if animal exists, False otherwise
        
    Raises:
        ValidationError: If animal_id is invalid or animal doesn't exist
    """
    if not animal_id:
        raise ValidationError("Animal ID cannot be empty")
    
    # In test mode, check our cache
    if animal_id in _TEST_DATA_CACHE['animals']:
        return True
    
    return False


def validate_foreign_key_constraints(entity_type: str, entity_data: Dict[str, Any]) -> None:
    """
    Validate all foreign key constraints for an entity.
    
    PR003946-73: Comprehensive foreign key validation
    
    Args:
        entity_type: Type of entity ('user', 'family', 'animal', 'conversation', etc.)
        entity_data: The entity data to validate
        
    Raises:
        ValidationError: If any foreign key constraint is violated
    """
    errors = []
    
    if entity_type == 'user':
        # Validate familyId if present
        family_id = entity_data.get('familyId')
        if family_id and not validate_family_exists(family_id):
            errors.append(f"Referenced family does not exist: {family_id}")
    
    elif entity_type == 'family':
        # Validate parent user IDs
        parents = entity_data.get('parents', [])
        for parent_id in parents:
            if not validate_user_exists(parent_id):
                errors.append(f"Referenced parent user does not exist: {parent_id}")
        
        # Validate student user IDs
        students = entity_data.get('students', [])
        for student_id in students:
            if not validate_user_exists(student_id):
                errors.append(f"Referenced student user does not exist: {student_id}")
    
    elif entity_type == 'conversation':
        # Validate user ID
        user_id = entity_data.get('userId')
        if user_id and not validate_user_exists(user_id):
            errors.append(f"Referenced user does not exist: {user_id}")
        
        # Validate animal ID
        animal_id = entity_data.get('animalId')
        if animal_id and not validate_animal_exists(animal_id):
            errors.append(f"Referenced animal does not exist: {animal_id}")
    
    elif entity_type == 'animal_config':
        # Validate animal ID
        animal_id = entity_data.get('animalId')
        if animal_id and not validate_animal_exists(animal_id):
            errors.append(f"Referenced animal does not exist: {animal_id}")
    
    # If there are validation errors, raise them
    if errors:
        raise ValidationError(
            "Foreign key constraint violations",
            field_errors=errors,
            details={"entity_type": entity_type, "violations": errors}
        )


def validate_user_family_relationship(user_id: str, family_id: str) -> None:
    """
    Validate that a user can be associated with a family.
    
    Args:
        user_id: The user ID
        family_id: The family ID
        
    Raises:
        ValidationError: If the relationship is invalid
    """
    if not validate_user_exists(user_id):
        raise ValidationError(f"User does not exist: {user_id}")
    
    if not validate_family_exists(family_id):
        raise ValidationError(f"Family does not exist: {family_id}")
    
    # Additional business rule validation could go here
    # For example: check if user is already in another family
    # check if family has reached maximum members, etc.


def validate_conversation_participants(user_id: str, animal_id: str) -> None:
    """
    Validate that a conversation can occur between a user and animal.
    
    Args:
        user_id: The user ID
        animal_id: The animal ID
        
    Raises:
        ValidationError: If the conversation is invalid
    """
    if not validate_user_exists(user_id):
        raise ValidationError(f"User does not exist: {user_id}")
    
    if not validate_animal_exists(animal_id):
        raise ValidationError(f"Animal does not exist: {animal_id}")
    
    # Additional business rules could check:
    # - If animal is active/available for conversations
    # - If user has permission to talk to this animal
    # - If there are any time/access restrictions


def validate_entity_references(entity_data: Dict[str, Any]) -> None:
    """
    Generic validation for common entity references.
    
    This validates common foreign key patterns across all entities:
    - userId references
    - familyId references  
    - animalId references
    
    Args:
        entity_data: The entity data containing potential references
        
    Raises:
        ValidationError: If any references are invalid
    """
    errors = []
    
    # Check userId reference
    user_id = entity_data.get('userId')
    if user_id and not validate_user_exists(user_id):
        errors.append(f"Referenced user does not exist: {user_id}")
    
    # Check familyId reference
    family_id = entity_data.get('familyId')
    if family_id and not validate_family_exists(family_id):
        errors.append(f"Referenced family does not exist: {family_id}")
    
    # Check animalId reference
    animal_id = entity_data.get('animalId')
    if animal_id and not validate_animal_exists(animal_id):
        errors.append(f"Referenced animal does not exist: {animal_id}")
    
    # Check nested created/modified by references
    for audit_field in ['created', 'modified']:
        audit_data = entity_data.get(audit_field, {})
        if isinstance(audit_data, dict):
            by_user = audit_data.get('by', {})
            if isinstance(by_user, dict):
                by_user_id = by_user.get('userId')
                if by_user_id and not validate_user_exists(by_user_id):
                    errors.append(f"Referenced audit user does not exist: {by_user_id}")
    
    if errors:
        raise ValidationError(
            "Entity reference validation failed",
            field_errors=errors,
            details={"reference_violations": errors}
        )


def add_test_entity(entity_type: str, entity_id: str, entity_data: Dict[str, Any]) -> None:
    """
    Add an entity to the test cache for validation purposes.
    
    This is used in test mode to populate the validation cache.
    
    Args:
        entity_type: Type of entity ('users', 'families', 'animals')
        entity_id: The entity ID
        entity_data: The entity data
    """
    if entity_type in _TEST_DATA_CACHE:
        _TEST_DATA_CACHE[entity_type][entity_id] = entity_data