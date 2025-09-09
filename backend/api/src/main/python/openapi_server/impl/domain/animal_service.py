"""Animal domain service - Pure business logic for animal chatbot operations"""
import uuid
from typing import List, Optional, Dict, Any, Tuple
from .common.entities import Animal
from .common.exceptions import (
    NotFoundError, ConflictError, ValidationError, 
    BusinessRuleError, InvalidStateError
)
from .common.validators import validate_animal_creation_data, validate_soft_delete_allowed, validate_update_allowed
from .common.audit import create_creation_audit, create_modification_audit, create_deletion_audit
from .common.serializers import deserialize_animal, serialize_animal
from ..ports.repository import AnimalRepository
from ..ports.audit import AuditService


class AnimalService:
    """Pure business logic for animal chatbot operations"""
    
    def __init__(self, animal_repo: AnimalRepository, audit_service: AuditService):
        self._animal_repo = animal_repo
        self._audit_service = audit_service
    
    def create_animal(self, animal_data: Dict[str, Any]) -> Animal:
        """
        Create a new animal chatbot with business logic validation
        
        Args:
            animal_data: Dictionary containing animal creation data
            
        Returns:
            Animal: Created animal domain entity
            
        Raises:
            ValidationError: If animal data is invalid
            ConflictError: If animal already exists
        """
        # Business validation
        validate_animal_creation_data(animal_data)
        
        # Generate animal ID if not provided
        animal_id = animal_data.get("id") or animal_data.get("animalId")
        if not animal_id:
            animal_id = str(uuid.uuid4())
            animal_data["animalId"] = animal_id
        else:
            animal_data["animalId"] = animal_id
        
        # Check for conflicts
        if self._animal_repo.exists(animal_id):
            raise ConflictError(f"Animal already exists with ID: {animal_id}")
        
        # Apply business defaults
        animal_data.setdefault("status", "active")
        animal_data.setdefault("softDelete", False)
        animal_data.setdefault("personality", {})
        animal_data.setdefault("configuration", {})
        
        # Business rule: Name must be unique (case-insensitive)
        name = animal_data.get("name", "").strip()
        if name:
            existing_animals = self._animal_repo.list(hide_soft_deleted=True)
            for existing in existing_animals:
                if existing.name and existing.name.lower() == name.lower():
                    raise ConflictError(f"Animal name '{name}' already exists")
        
        # Create audit trail
        actor_data = self._audit_service.extract_actor_data(animal_data)
        audit_stamps = self._audit_service.create_creation_audit(actor_data)
        
        # Merge audit data
        animal_data.update({
            "created": audit_stamps["created"],
            "modified": audit_stamps["modified"],
            "deleted": None
        })
        
        # Convert to domain entity
        animal = deserialize_animal(animal_data)
        
        # Persist through repository
        created_animal = self._animal_repo.create(animal)
        
        return created_animal
    
    def get_animal(self, animal_id: str) -> Animal:
        """
        Get animal by ID with business logic
        
        Args:
            animal_id: Animal identifier
            
        Returns:
            Animal: Animal domain entity
            
        Raises:
            NotFoundError: If animal not found or soft deleted
        """
        animal = self._animal_repo.get(animal_id)
        
        if not animal:
            raise NotFoundError("Animal", animal_id)
        
        # Business rule: soft deleted animals are not accessible
        if animal.soft_delete:
            raise NotFoundError("Animal", animal_id)
        
        return animal
    
    def list_animals(self, status_filter: Optional[str] = None) -> List[Animal]:
        """
        List animals with business logic filtering
        
        Args:
            status_filter: Optional status to filter by ('active', 'inactive', etc.)
            
        Returns:
            List[Animal]: List of animal domain entities
        """
        # Get all non-deleted animals
        animals = self._animal_repo.list(hide_soft_deleted=True)
        
        # Apply status filtering if requested
        if status_filter:
            animals = [animal for animal in animals if animal.configuration.get("status") == status_filter]
        
        # Business rule: Sort by name for consistent ordering
        animals.sort(key=lambda a: a.name.lower() if a.name else "")
        
        return animals
    
    def update_animal(self, animal_id: str, update_data: Dict[str, Any]) -> Animal:
        """
        Update animal with business logic validation
        
        Args:
            animal_id: Animal identifier
            update_data: Dictionary containing update data
            
        Returns:
            Animal: Updated animal domain entity
            
        Raises:
            NotFoundError: If animal not found
            ValidationError: If update data is invalid
            InvalidStateError: If animal cannot be updated
            ConflictError: If name conflicts with existing animal
        """
        # Get current animal
        current_animal = self.get_animal(animal_id)  # This handles not found and soft delete
        current_data = serialize_animal(current_animal)
        
        # Business rule: cannot update soft deleted animals
        validate_update_allowed(current_data, "Animal")
        
        # Business rule: Name must be unique (case-insensitive) if being changed
        new_name = update_data.get("name")
        if new_name and new_name.strip():
            new_name = new_name.strip()
            if new_name.lower() != (current_animal.name or "").lower():
                existing_animals = self._animal_repo.list(hide_soft_deleted=True)
                for existing in existing_animals:
                    if existing.animal_id != animal_id and existing.name and existing.name.lower() == new_name.lower():
                        raise ConflictError(f"Animal name '{new_name}' already exists")
        
        # Merge current data with updates
        merged_data = current_data.copy()
        merged_data.update(update_data)
        merged_data["animalId"] = animal_id  # Ensure ID consistency
        
        # Create modification audit
        actor_data = self._audit_service.extract_actor_data(update_data)
        audit_stamps = self._audit_service.create_modification_audit(actor_data)
        merged_data.update(audit_stamps)
        
        # Convert to domain entity
        updated_animal = deserialize_animal(merged_data)
        
        # Persist through repository
        saved_animal = self._animal_repo.update(updated_animal)
        
        return saved_animal
    
    def soft_delete_animal(self, animal_id: str, actor_data: Optional[Dict[str, Any]] = None) -> None:
        """
        Soft delete animal with business logic
        
        Args:
            animal_id: Animal identifier
            actor_data: Information about who is performing the deletion
            
        Raises:
            NotFoundError: If animal not found
            ValidationError: If animal already deleted
            BusinessRuleError: If animal has active conversations
        """
        # Get current animal
        current_animal = self.get_animal(animal_id)  # This handles not found and soft delete
        current_data = serialize_animal(current_animal)
        
        # Business rule: cannot delete already deleted animals
        validate_soft_delete_allowed(current_data, "Animal")
        
        # Business rule: Check for active conversations (would need conversation service)
        # For now, we'll allow deletion but could add this business rule later
        # if self._has_active_conversations(animal_id):
        #     raise BusinessRuleError("cannot_delete_active_animal", 
        #                           f"Animal {animal_id} has active conversations")
        
        # Mark as soft deleted and inactive
        current_data["softDelete"] = True
        current_data.setdefault("configuration", {})
        current_data["configuration"]["status"] = "deleted"
        
        # Create deletion audit
        audit_stamps = self._audit_service.create_deletion_audit(actor_data)
        current_data.update(audit_stamps)
        
        # Convert to domain entity and persist
        updated_animal = deserialize_animal(current_data)
        self._animal_repo.update(updated_animal)
    
    def get_animal_configuration(self, animal_id: str) -> Dict[str, Any]:
        """
        Get animal configuration with business logic
        
        Args:
            animal_id: Animal identifier
            
        Returns:
            Dict[str, Any]: Animal configuration data
            
        Raises:
            NotFoundError: If animal not found
        """
        animal = self.get_animal(animal_id)
        
        # Business rule: Return configuration with defaults
        config = animal.configuration.copy() if animal.configuration else {}
        
        # Apply configuration defaults
        config.setdefault("voice", "default")
        config.setdefault("personality", animal.personality or {})
        config.setdefault("ai_model", "claude-3-sonnet")
        config.setdefault("temperature", 0.7)
        config.setdefault("top_p", 1.0)
        config.setdefault("tools_enabled", [])
        config.setdefault("guardrails", {})
        config.setdefault("status", "active")
        
        return config
    
    def update_animal_configuration(self, animal_id: str, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update animal configuration with business logic validation
        
        Args:
            animal_id: Animal identifier
            config_data: Configuration update data
            
        Returns:
            Dict[str, Any]: Updated configuration
            
        Raises:
            NotFoundError: If animal not found
            ValidationError: If configuration is invalid
        """
        animal = self.get_animal(animal_id)
        
        # Business validation for configuration
        self._validate_configuration(config_data)
        
        # Get current configuration
        current_config = animal.configuration.copy() if animal.configuration else {}
        
        # Merge configuration updates
        current_config.update(config_data)
        
        # Update the animal with new configuration
        update_data = {
            "configuration": current_config,
            "personality": config_data.get("personality", animal.personality)
        }
        
        updated_animal = self.update_animal(animal_id, update_data)
        
        return self.get_animal_configuration(animal_id)
    
    def _validate_configuration(self, config_data: Dict[str, Any]) -> None:
        """
        Validate animal configuration data
        
        Args:
            config_data: Configuration to validate
            
        Raises:
            ValidationError: If configuration is invalid
        """
        # Validate temperature
        if "temperature" in config_data:
            temp = config_data["temperature"]
            if not isinstance(temp, (int, float)) or temp < 0 or temp > 2:
                raise ValidationError("Temperature must be a number between 0 and 2")
        
        # Validate top_p
        if "top_p" in config_data:
            top_p = config_data["top_p"]
            if not isinstance(top_p, (int, float)) or top_p < 0 or top_p > 1:
                raise ValidationError("top_p must be a number between 0 and 1")
        
        # Validate AI model
        if "ai_model" in config_data:
            valid_models = ["claude-3-sonnet", "claude-3-haiku", "claude-3-opus", "gpt-4", "gpt-3.5-turbo"]
            if config_data["ai_model"] not in valid_models:
                raise ValidationError(f"Invalid AI model. Must be one of: {valid_models}")
        
        # Validate status
        if "status" in config_data:
            valid_statuses = ["active", "inactive", "maintenance", "deleted"]
            if config_data["status"] not in valid_statuses:
                raise ValidationError(f"Invalid status. Must be one of: {valid_statuses}")
        
        # Validate tools_enabled is a list
        if "tools_enabled" in config_data:
            if not isinstance(config_data["tools_enabled"], list):
                raise ValidationError("tools_enabled must be a list")
        
        # Validate guardrails is a dict
        if "guardrails" in config_data:
            if not isinstance(config_data["guardrails"], dict):
                raise ValidationError("guardrails must be a dictionary")