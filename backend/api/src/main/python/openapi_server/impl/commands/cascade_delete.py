"""
PR003946-67: Cascade Soft-Delete Command Implementation

This module implements cascade soft-delete functionality following hexagonal architecture.
The same command can be called from Flask endpoints and Lambda function hooks.
"""

import os
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

from openapi_server.impl.utils import get_store, now_iso, error_response
from openapi_server.impl.error_handler import ValidationError

log = logging.getLogger(__name__)


@dataclass
class CascadeDeleteCommand:
    """Command to perform cascade soft-delete operation."""
    entity_type: str  # "family", "user", "animal"
    entity_id: str
    cascade_enabled: bool = True
    audit_user: Optional[str] = None


class CascadeDeleteProcessor:
    """Core business logic for cascade soft-delete operations."""
    
    # Define entity relationships: parent -> [children]
    CASCADE_RELATIONSHIPS = {
        "family": ["user"],  # When family deleted, cascade to users in that family
        "user": ["conversation"],  # When user deleted, cascade to their conversations  
        "animal": ["conversation"],  # When animal deleted, cascade to their conversations
    }
    
    # Test mode mock data
    TEST_MODE_DATA = {
        "family": {
            "test_family_123": {"familyId": "test_family_123", "name": "Test Family", "softDelete": False},
            "family_1": {"familyId": "family_1", "name": "Demo Family", "softDelete": False}
        },
        "user": {
            "user_1": {"userId": "user_1", "familyId": "family_1", "email": "user1@test.com", "softDelete": False},
            "user_2": {"userId": "user_2", "familyId": "family_1", "email": "user2@test.com", "softDelete": False},
            "user_3": {"userId": "user_3", "familyId": "test_family_123", "email": "user3@test.com", "softDelete": False}
        },
        "conversation": {
            "conv_1": {"conversationId": "conv_1", "userId": "user_1", "animalId": "animal_1", "softDelete": False},
            "conv_2": {"conversationId": "conv_2", "userId": "user_2", "animalId": "animal_2", "softDelete": False}
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
        "conversation": {
            "table": os.getenv("CONVERSATION_DYNAMO_TABLE_NAME", "quest-dev-conversation"), 
            "pk": os.getenv("CONVERSATION_DYNAMO_PK_NAME", "conversationId")
        },
        "animal": {
            "table": os.getenv("ANIMAL_DYNAMO_TABLE_NAME", "quest-dev-animal"),
            "pk": os.getenv("ANIMAL_DYNAMO_PK_NAME", "animalId")
        }
    }
    
    def __init__(self):
        self.stores = {}
        self.test_mode = os.getenv('TEST_MODE', '').lower() == 'true'
        if self.test_mode:
            log.info("Cascade delete processor running in TEST MODE")
        
    def _get_store(self, entity_type: str):
        """Get DynamoDB store for entity type."""
        if entity_type not in self.stores:
            config = self.TABLE_CONFIGS.get(entity_type)
            if not config:
                raise ValidationError(f"Unknown entity type: {entity_type}")
            self.stores[entity_type] = get_store(config["table"], config["pk"])
        return self.stores[entity_type]
    
    def process_cascade_delete(self, command: CascadeDeleteCommand) -> Dict:
        """
        Process cascade soft-delete command.
        
        Returns:
            dict: Result with counts of affected entities
        """
        try:
            result = {
                "deleted_entities": {},
                "total_affected": 0,
                "timestamp": now_iso()
            }
            
            # Step 1: Soft-delete the primary entity
            primary_deleted = self._soft_delete_entity(
                command.entity_type, 
                command.entity_id,
                command.audit_user
            )
            
            if not primary_deleted:
                return error_response(
                    "not_found",
                    f"{command.entity_type.title()} not found: {command.entity_id}",
                    404
                )
            
            result["deleted_entities"][command.entity_type] = 1
            result["total_affected"] = 1
            
            # Step 2: Cascade to related entities if enabled
            if command.cascade_enabled:
                cascade_count = self._process_cascade_children(
                    command.entity_type,
                    command.entity_id, 
                    command.audit_user,
                    result["deleted_entities"]
                )
                result["total_affected"] += cascade_count
            
            log.info(
                f"Cascade delete completed: {command.entity_type}={command.entity_id}, "
                f"affected={result['total_affected']} entities"
            )
            
            return result
            
        except Exception as e:
            log.error(f"Cascade delete failed: {e}")
            raise ValidationError(f"Cascade delete failed: {str(e)}")
    
    def _soft_delete_entity(self, entity_type: str, entity_id: str, audit_user: str = None) -> bool:
        """Soft-delete a single entity."""
        if self.test_mode:
            return self._soft_delete_entity_test_mode(entity_type, entity_id, audit_user)
        
        store = self._get_store(entity_type)
        
        # Check if entity exists and is not already soft-deleted
        entity = store.get(entity_id)
        if not entity:
            return False
            
        if entity.get("softDelete", False):
            log.info(f"{entity_type} {entity_id} already soft-deleted")
            return True
            
        # Perform soft-delete
        update_data = {
            "softDelete": True,
            "modified": {
                "at": now_iso(),
                "by": {
                    "userId": audit_user or "system",
                    "reason": "cascade_delete"
                }
            }
        }
        
        store.update_fields(entity_id, update_data)
        log.info(f"Soft-deleted {entity_type}: {entity_id}")
        return True
    
    def _soft_delete_entity_test_mode(self, entity_type: str, entity_id: str, audit_user: str = None) -> bool:
        """Test mode version of soft-delete."""
        entity_data = self.TEST_MODE_DATA.get(entity_type, {})
        if entity_id not in entity_data:
            log.info(f"Test mode: {entity_type} {entity_id} not found")
            return False
            
        entity = entity_data[entity_id]
        if entity.get("softDelete", False):
            log.info(f"Test mode: {entity_type} {entity_id} already soft-deleted")
            return True
            
        # Mark as soft-deleted in test data
        entity["softDelete"] = True
        entity["modified"] = {
            "at": now_iso(),
            "by": {
                "userId": audit_user or "system",
                "reason": "cascade_delete"
            }
        }
        
        log.info(f"Test mode: Soft-deleted {entity_type}: {entity_id}")
        return True
    
    def _process_cascade_children(self, parent_type: str, parent_id: str, audit_user: str, result_counter: Dict) -> int:
        """Process cascade delete for child entities."""
        affected_count = 0
        
        child_types = self.CASCADE_RELATIONSHIPS.get(parent_type, [])
        
        for child_type in child_types:
            child_ids = self._find_related_entities(parent_type, parent_id, child_type)
            
            for child_id in child_ids:
                if self._soft_delete_entity(child_type, child_id, audit_user):
                    affected_count += 1
                    result_counter[child_type] = result_counter.get(child_type, 0) + 1
                    
                    # Recursively cascade to grandchildren
                    grandchild_count = self._process_cascade_children(
                        child_type, child_id, audit_user, result_counter
                    )
                    affected_count += grandchild_count
        
        return affected_count
    
    def _find_related_entities(self, parent_type: str, parent_id: str, child_type: str) -> List[str]:
        """Find entity IDs related to the parent entity."""
        if self.test_mode:
            return self._find_related_entities_test_mode(parent_type, parent_id, child_type)
        
        child_store = self._get_store(child_type)
        
        # Define foreign key relationships
        foreign_key_mappings = {
            ("family", "user"): "familyId",
            ("user", "conversation"): "userId", 
            ("animal", "conversation"): "animalId",
        }
        
        foreign_key = foreign_key_mappings.get((parent_type, child_type))
        if not foreign_key:
            log.warning(f"No foreign key mapping defined for {parent_type} -> {child_type}")
            return []
        
        # Query for related entities
        # Note: This uses a scan which is not optimal for large datasets
        # In production, consider using GSI queries
        try:
            all_items = child_store.list()
            related_ids = []
            
            for item in all_items:
                if item.get(foreign_key) == parent_id and not item.get("softDelete", False):
                    pk_field = self.TABLE_CONFIGS[child_type]["pk"]
                    related_ids.append(item[pk_field])
            
            log.info(f"Found {len(related_ids)} {child_type} entities related to {parent_type} {parent_id}")
            return related_ids
            
        except Exception as e:
            log.error(f"Failed to find related {child_type} entities: {e}")
            return []
    
    def _find_related_entities_test_mode(self, parent_type: str, parent_id: str, child_type: str) -> List[str]:
        """Test mode version of finding related entities."""
        # Define foreign key relationships
        foreign_key_mappings = {
            ("family", "user"): "familyId",
            ("user", "conversation"): "userId", 
            ("animal", "conversation"): "animalId",
        }
        
        foreign_key = foreign_key_mappings.get((parent_type, child_type))
        if not foreign_key:
            log.warning(f"Test mode: No foreign key mapping defined for {parent_type} -> {child_type}")
            return []
        
        child_entities = self.TEST_MODE_DATA.get(child_type, {})
        related_ids = []
        
        for child_id, child_data in child_entities.items():
            if child_data.get(foreign_key) == parent_id and not child_data.get("softDelete", False):
                related_ids.append(child_id)
        
        log.info(f"Test mode: Found {len(related_ids)} {child_type} entities related to {parent_type} {parent_id}")
        return related_ids


def execute_cascade_delete(entity_type: str, entity_id: str, cascade_enabled: bool = True, audit_user: str = None) -> tuple:
    """
    Main entry point for cascade delete operations.
    Used by both Flask controllers and Lambda hooks.
    
    Returns:
        tuple: (result_data, http_status_code)
    """
    command = CascadeDeleteCommand(
        entity_type=entity_type,
        entity_id=entity_id,
        cascade_enabled=cascade_enabled,
        audit_user=audit_user
    )
    
    processor = CascadeDeleteProcessor()
    result = processor.process_cascade_delete(command)
    
    # If result is an error response, return it directly
    if isinstance(result, tuple):
        return result
        
    # Success: return minimal response for DELETE operation
    return None, 204