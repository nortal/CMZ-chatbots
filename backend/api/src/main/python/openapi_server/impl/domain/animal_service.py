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
from .common.serializers import deserialize_animal, serialize_animal, serialize_audit_stamp
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
        
        # Merge audit data - serialize audit stamps to dictionaries
        animal_data.update({
            "created": serialize_audit_stamp(audit_stamps["created"]),
            "modified": serialize_audit_stamp(audit_stamps["modified"]),
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
        current_data = serialize_animal(current_animal, include_api_id=False)
        
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
        
        # Serialize audit stamps to dictionaries before merging
        serialized_audit = {
            key: serialize_audit_stamp(stamp) for key, stamp in audit_stamps.items()
        }
        merged_data.update(serialized_audit)
        
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
        current_data = serialize_animal(current_animal, include_api_id=False)
        
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
        
        # Serialize audit stamps to dictionaries before merging
        serialized_audit = {
            key: serialize_audit_stamp(stamp) for key, stamp in audit_stamps.items()
        }
        current_data.update(serialized_audit)
        
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

        # Build configuration response for API matching OpenAPI spec
        config = {
            "animalConfigId": f"config-{animal_id}",
            "voice": animal.configuration.get("voice", "alloy") if animal.configuration else "alloy",
            "personality": animal.personality.get("description", "") if isinstance(animal.personality, dict) else str(animal.personality or ""),
            "aiModel": animal.configuration.get("aiModel", "gpt-4o-mini") if animal.configuration else "gpt-4o-mini",
            "temperature": round(float(animal.configuration.get("temperature", 0.7) or 0.7) * 10) / 10 if animal.configuration else 0.7,
            "topP": round(float(animal.configuration.get("topP", 1.0) or 1.0) * 100) / 100 if animal.configuration else 1.0,
            "toolsEnabled": animal.configuration.get("toolsEnabled", ["facts", "media_lookup"]) if animal.configuration else ["facts", "media_lookup"],
            "guardrails": animal.configuration.get("guardrails", {}) if animal.configuration else {},
            "softDelete": animal.soft_delete
        }

        # Add audit information if available
        if animal.created:
            config["created"] = serialize_audit_stamp(animal.created)
        if animal.modified:
            config["modified"] = serialize_audit_stamp(animal.modified)

        return config
    
    def update_animal_configuration(self, animal_id: str, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update animal configuration with business logic validation

        Args:
            animal_id: Animal identifier
            config_data: Configuration update data from API

        Returns:
            Dict[str, Any]: Updated configuration

        Raises:
            NotFoundError: If animal not found
            ValidationError: If configuration is invalid
        """
        animal = self.get_animal(animal_id)

        # Prepare update data for the animal entity
        update_data = {}

        # Get current configuration
        current_config = animal.configuration.copy() if animal.configuration else {}

        # Map API fields to internal configuration fields
        # Only update fields that are provided and not None
        if "voice" in config_data and config_data["voice"] is not None:
            current_config["voice"] = config_data["voice"]
        if "aiModel" in config_data and config_data["aiModel"] is not None:
            current_config["aiModel"] = config_data["aiModel"]
        if "temperature" in config_data and config_data["temperature"] is not None:
            current_config["temperature"] = float(config_data["temperature"])
        if "topP" in config_data and config_data["topP"] is not None:
            current_config["topP"] = float(config_data["topP"])
        if "toolsEnabled" in config_data and config_data["toolsEnabled"] is not None:
            current_config["toolsEnabled"] = config_data["toolsEnabled"]
        if "guardrails" in config_data and config_data["guardrails"] is not None:
            current_config["guardrails"] = config_data["guardrails"]

        # Handle personality - store as dict with description
        if "personality" in config_data:
            personality_value = config_data["personality"]
            if isinstance(personality_value, str):
                update_data["personality"] = {"description": personality_value}
            else:
                update_data["personality"] = personality_value

        # Business validation for configuration
        self._validate_configuration(current_config)

        # Update the configuration
        update_data["configuration"] = current_config

        # Update the animal entity
        updated_animal = self.update_animal(animal_id, update_data)

        # Return the updated configuration in API format
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
            # Round to nearest 0.1 to handle floating point precision issues
            config_data["temperature"] = round(temp * 10) / 10

        # Validate topP (internal name for top_p)
        if "topP" in config_data:
            top_p = config_data["topP"]
            if not isinstance(top_p, (int, float)) or top_p < 0 or top_p > 1:
                raise ValidationError("topP must be a number between 0 and 1")
            # Round to nearest 0.01 to handle floating point precision issues
            config_data["topP"] = round(top_p * 100) / 100

        # Validate AI model
        if "aiModel" in config_data and config_data["aiModel"] is not None:
            valid_models = ["gpt-4o-mini", "gpt-4", "gpt-3.5-turbo", "claude-3-sonnet", "claude-3-haiku", "claude-3-opus"]
            if config_data["aiModel"] not in valid_models:
                raise ValidationError(f"Invalid AI model. Must be one of: {valid_models}")

        # Validate voice
        if "voice" in config_data and config_data["voice"] is not None:
            valid_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
            if config_data["voice"] not in valid_voices:
                raise ValidationError(f"Invalid voice. Must be one of: {valid_voices}")

        # Validate status (if used in configuration)
        if "status" in config_data and config_data["status"] is not None:
            valid_statuses = ["active", "inactive", "maintenance", "deleted"]
            if config_data["status"] not in valid_statuses:
                raise ValidationError(f"Invalid status. Must be one of: {valid_statuses}")

        # Validate toolsEnabled is a list
        if "toolsEnabled" in config_data and config_data["toolsEnabled"] is not None:
            if not isinstance(config_data["toolsEnabled"], list):
                raise ValidationError("toolsEnabled must be a list")

        # Validate guardrails is a dict
        if "guardrails" in config_data and config_data["guardrails"] is not None:
            if not isinstance(config_data["guardrails"], dict):
                raise ValidationError("guardrails must be a dictionary")