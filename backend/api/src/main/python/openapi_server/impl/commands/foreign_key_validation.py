"""
PR003946-73: Foreign Key Validation Command Implementation

This module implements foreign key validation functionality following hexagonal architecture.
The same validation logic can be called from Flask endpoints and Lambda function hooks.
"""

import os
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

from openapi_server.impl.utils import get_store
from openapi_server.impl.error_handler import ValidationError

log = logging.getLogger(__name__)


@dataclass
class ForeignKeyValidationCommand:
    """Command to perform foreign key validation."""
    entity_type: str  # "user", "family", "animal", "conversation"
    entity_data: Dict
    audit_user: Optional[str] = None


class ForeignKeyValidationProcessor:
    """Core business logic for foreign key validation operations."""
    
    # Test mode mock data
    TEST_MODE_DATA = {
        "family": {
            "family_1": {"familyId": "family_1", "name": "Demo Family", "softDelete": False},
            "test_family_123": {"familyId": "test_family_123", "name": "Test Family", "softDelete": False}
        },
        "user": {
            "user_1": {"userId": "user_1", "familyId": "family_1", "softDelete": False},
            "user_2": {"userId": "user_2", "familyId": "family_1", "softDelete": False}, 
            "user_3": {"userId": "user_3", "familyId": "test_family_123", "softDelete": False},
            "valid_parent": {"userId": "valid_parent", "familyId": None, "softDelete": False},
            "valid_student": {"userId": "valid_student", "familyId": None, "softDelete": False}
        },
        "animal": {
            "animal_1": {"animalId": "animal_1", "name": "Simba", "softDelete": False},
            "animal_2": {"animalId": "animal_2", "name": "Koda", "softDelete": False}
        }
    }
    
    # Table configurations
    TABLE_CONFIGS = {
        "family": {
            "table": os.getenv("FAMILY_DYNAMO_TABLE_NAME", "quest-dev-family"),
            "pk": os.getenv("FAMILY_DYNAMO_PK_NAME", "familyId")
        },
        "user": {
            "table": os.getenv("USER_DYNAMO_TABLE_NAME", "quest-dev-user"),
            "pk": os.getenv("USER_DYNAMO_PK_NAME", "userId")
        },
        "animal": {
            "table": os.getenv("ANIMAL_DYNAMO_TABLE_NAME", "quest-dev-animal"),
            "pk": os.getenv("ANIMAL_DYNAMO_PK_NAME", "animalId")
        },
        "conversation": {
            "table": os.getenv("CONVERSATION_DYNAMO_TABLE_NAME", "quest-dev-conversation"),
            "pk": os.getenv("CONVERSATION_DYNAMO_PK_NAME", "conversationId")
        }
    }
    
    def __init__(self):
        self.stores = {}
        self.test_mode = os.getenv('TEST_MODE', '').lower() == 'true'
        if self.test_mode:
            log.info("Foreign key validation processor running in TEST MODE")
        
    def _get_store(self, entity_type: str):
        """Get DynamoDB store for entity type."""
        if entity_type not in self.stores:
            config = self.TABLE_CONFIGS.get(entity_type)
            if not config:
                raise ValidationError(f"Unknown entity type: {entity_type}")
            self.stores[entity_type] = get_store(config["table"], config["pk"])
        return self.stores[entity_type]
    
    def process_foreign_key_validation(self, command: ForeignKeyValidationCommand) -> Dict:
        """
        Process foreign key validation command.
        
        Returns:
            dict: Validation result with any errors found
        """
        try:
            violations = []
            
            # Validate based on entity type
            if command.entity_type == "user":
                violations.extend(self._validate_user_foreign_keys(command.entity_data))
            elif command.entity_type == "family":
                violations.extend(self._validate_family_foreign_keys(command.entity_data))
            elif command.entity_type == "conversation":
                violations.extend(self._validate_conversation_foreign_keys(command.entity_data))
            elif command.entity_type == "animal":
                violations.extend(self._validate_animal_foreign_keys(command.entity_data))
            
            if violations:
                # Group violations by referenced entity type to provide specific error details
                entity_type_violations = self._group_violations_by_entity_type(violations)
                
                # Use the first failed entity type for the primary error
                primary_entity_type = list(entity_type_violations.keys())[0]
                
                raise ValidationError(
                    "Foreign key constraint violations",
                    field_errors=violations,
                    details={
                        "entity_type": primary_entity_type,
                        "error_type": "foreign_key_violation", 
                        "violations": violations
                    }
                )
            
            return {"status": "valid", "violations": []}
            
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            log.error(f"Foreign key validation failed: {e}")
            raise ValidationError(f"Foreign key validation failed: {str(e)}")
    
    def _validate_user_foreign_keys(self, user_data: Dict) -> List[str]:
        """Validate foreign keys for user entity."""
        violations = []
        
        # Validate familyId if present
        family_id = user_data.get('familyId')
        if family_id and not self._entity_exists("family", family_id):
            violations.append(f"Referenced family does not exist: {family_id}")
        
        return violations
    
    def _validate_family_foreign_keys(self, family_data: Dict) -> List[str]:
        """Validate foreign keys for family entity."""
        violations = []
        
        # Validate parent user IDs
        parents = family_data.get('parents', [])
        for parent_id in parents:
            if not self._entity_exists("user", parent_id):
                violations.append(f"Referenced parent user does not exist: {parent_id}")
        
        # Validate student user IDs
        students = family_data.get('students', [])
        for student_id in students:
            if not self._entity_exists("user", student_id):
                violations.append(f"Referenced student user does not exist: {student_id}")
        
        return violations
    
    def _validate_conversation_foreign_keys(self, conversation_data: Dict) -> List[str]:
        """Validate foreign keys for conversation entity."""
        violations = []
        
        # Validate user ID
        user_id = conversation_data.get('userId')
        if user_id and not self._entity_exists("user", user_id):
            violations.append(f"Referenced user does not exist: {user_id}")
        
        # Validate animal ID
        animal_id = conversation_data.get('animalId')
        if animal_id and not self._entity_exists("animal", animal_id):
            violations.append(f"Referenced animal does not exist: {animal_id}")
        
        return violations
    
    def _validate_animal_foreign_keys(self, animal_data: Dict) -> List[str]:
        """Validate foreign keys for animal entity."""
        violations = []
        
        # Animals typically don't have foreign key references in this system
        # This method is here for completeness and future extensions
        
        return violations
    
    def _entity_exists(self, entity_type: str, entity_id: str) -> bool:
        """Check if entity exists and is not soft-deleted."""
        if self.test_mode:
            return self._entity_exists_test_mode(entity_type, entity_id)
        
        try:
            store = self._get_store(entity_type)
            entity = store.get(entity_id)
            return entity and not entity.get("softDelete", False)
        except Exception:
            return False
    
    def _entity_exists_test_mode(self, entity_type: str, entity_id: str) -> bool:
        """Test mode version of entity existence check."""
        entity_data = self.TEST_MODE_DATA.get(entity_type, {})
        if entity_id not in entity_data:
            return False
        
        entity = entity_data[entity_id]
        return not entity.get("softDelete", False)
    
    def _group_violations_by_entity_type(self, violations: List[str]) -> Dict[str, List[str]]:
        """Group violations by referenced entity type."""
        grouped = {}
        
        for violation in violations:
            if "family does not exist" in violation:
                grouped.setdefault("family", []).append(violation)
            elif "user does not exist" in violation:
                grouped.setdefault("user", []).append(violation)
            elif "animal does not exist" in violation:
                grouped.setdefault("animal", []).append(violation)
            else:
                grouped.setdefault("unknown", []).append(violation)
        
        return grouped


def execute_foreign_key_validation(entity_type: str, entity_data: Dict, audit_user: str = None) -> tuple:
    """
    Main entry point for foreign key validation operations.
    Used by both Flask controllers and Lambda hooks.
    
    Returns:
        tuple: (result_data, http_status_code)
    """
    command = ForeignKeyValidationCommand(
        entity_type=entity_type,
        entity_data=entity_data,
        audit_user=audit_user
    )
    
    processor = ForeignKeyValidationProcessor()
    result = processor.process_foreign_key_validation(command)
    
    # Success: validation passed
    return result, 200