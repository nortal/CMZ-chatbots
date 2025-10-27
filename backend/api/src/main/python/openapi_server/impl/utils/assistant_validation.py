#!/usr/bin/env python3
"""
Animal Assistant Management System - Entity Validation and Audit Utilities

Extends existing dynamo.py patterns with animal assistant-specific validation,
audit trails, and business rule enforcement for comprehensive data integrity.

Core Features:
- Entity validation with CMZ constitutional compliance
- Automated audit trails for all operations
- Business rule enforcement (e.g., one assistant per animal)
- Cross-entity relationship validation
- Performance optimization for <200ms assistant retrieval

Author: CMZ Animal Assistant Management System
Date: 2025-10-23
"""

import logging
import uuid
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json
import re

from .dynamo import (
    table, to_ddb, from_ddb, now_iso,
    model_to_json_keyed_dict, ensure_pk,
    error_response, not_found
)

# Configure logging
logger = logging.getLogger(__name__)


class EntityType(Enum):
    """Supported entity types for validation."""
    ANIMAL_ASSISTANT = "animal_assistant"
    PERSONALITY = "personality"
    GUARDRAIL = "guardrail"
    KNOWLEDGE_FILE = "knowledge_file"
    SANDBOX_ASSISTANT = "sandbox_assistant"


class ValidationSeverity(Enum):
    """Validation issue severity levels."""
    ERROR = "error"          # Blocks operation
    WARNING = "warning"      # Logs but allows operation
    INFO = "info"           # Informational only


class OperationType(Enum):
    """Types of operations for audit trails."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    READ = "read"
    PROMOTE = "promote"      # Sandbox → Live
    MERGE = "merge"          # Prompt merging


@dataclass
class ValidationResult:
    """Result of entity validation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    info: List[str]
    entity_type: EntityType
    entity_id: Optional[str] = None
    validation_timestamp: Optional[str] = None

    def __post_init__(self):
        if not self.validation_timestamp:
            self.validation_timestamp = now_iso()


@dataclass
class AuditEntry:
    """Audit trail entry for operations."""
    operation_type: OperationType
    entity_type: EntityType
    entity_id: str
    user_id: Optional[str]
    timestamp: str
    changes: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return asdict(self)


class AssistantValidator:
    """
    Comprehensive validator for Animal Assistant Management entities.

    Extends existing CMZ patterns with assistant-specific business rules
    and performance optimization for <200ms retrieval requirements.
    """

    # Table name mappings for validation
    TABLE_NAMES = {
        EntityType.ANIMAL_ASSISTANT: "quest-dev-animal-assistant",
        EntityType.PERSONALITY: "quest-dev-personality",
        EntityType.GUARDRAIL: "quest-dev-guardrail",
        EntityType.KNOWLEDGE_FILE: "quest-dev-knowledge-file",
        EntityType.SANDBOX_ASSISTANT: "quest-dev-sandbox-assistant"
    }

    # Field validation patterns
    VALIDATION_PATTERNS = {
        'uuid': re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'),
        'email': re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'),
        'safe_text': re.compile(r'^[a-zA-Z0-9\s\.\,\!\?\-\(\)\[\]]+$'),
        'filename': re.compile(r'^[a-zA-Z0-9\._\-\s]+\.(pdf|doc|docx|txt)$', re.IGNORECASE)
    }

    # Business rule constants
    MAX_KNOWLEDGE_FILES_PER_ASSISTANT = 50
    MAX_SANDBOX_FILES_PER_ASSISTANT = 10
    MAX_FILE_SIZE_BYTES = 52_428_800  # 50MB
    MAX_TOTAL_FILES_SIZE_BYTES = 524_288_000  # 500MB
    SANDBOX_EXPIRY_MINUTES = 30

    def __init__(self):
        """Initialize validator with table references."""
        self.audit_entries = []

    def validate_animal_assistant(self, assistant_data: Dict[str, Any],
                                operation: OperationType = OperationType.CREATE) -> ValidationResult:
        """
        Validate animal assistant entity.

        Business Rules:
        - One active assistant per animal (GSI-1 constraint)
        - Personality and guardrail must exist
        - Assistant ID must be UUID format
        - Knowledge base files ≤ 50 per assistant
        """
        result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=[],
            info=[],
            entity_type=EntityType.ANIMAL_ASSISTANT,
            entity_id=assistant_data.get('assistantId')
        )

        try:
            # Required field validation
            required_fields = ['assistantId', 'animalId', 'personalityId', 'guardrailId']
            for field in required_fields:
                if not assistant_data.get(field):
                    result.errors.append(f"Required field missing: {field}")
                    result.is_valid = False

            # UUID format validation
            for uuid_field in ['assistantId', 'personalityId', 'guardrailId']:
                if assistant_data.get(uuid_field):
                    if not self._validate_uuid_format(assistant_data[uuid_field]):
                        result.errors.append(f"Invalid UUID format for {uuid_field}")
                        result.is_valid = False

            # Business rule: One assistant per animal
            if operation == OperationType.CREATE and assistant_data.get('animalId'):
                existing = self._check_existing_assistant_for_animal(assistant_data['animalId'])
                if existing:
                    result.errors.append(f"Animal {assistant_data['animalId']} already has an assistant: {existing}")
                    result.is_valid = False

            # Validate personality exists
            if assistant_data.get('personalityId'):
                if not self._entity_exists(EntityType.PERSONALITY, assistant_data['personalityId']):
                    result.errors.append(f"Personality {assistant_data['personalityId']} does not exist")
                    result.is_valid = False

            # Validate guardrail exists
            if assistant_data.get('guardrailId'):
                if not self._entity_exists(EntityType.GUARDRAIL, assistant_data['guardrailId']):
                    result.errors.append(f"Guardrail {assistant_data['guardrailId']} does not exist")
                    result.is_valid = False

            # Knowledge base file count validation
            knowledge_files = assistant_data.get('knowledgeBaseFileIds', [])
            if len(knowledge_files) > self.MAX_KNOWLEDGE_FILES_PER_ASSISTANT:
                result.errors.append(f"Too many knowledge files: {len(knowledge_files)} > {self.MAX_KNOWLEDGE_FILES_PER_ASSISTANT}")
                result.is_valid = False

            # Status validation
            valid_statuses = ['ACTIVE', 'INACTIVE', 'ERROR']
            if assistant_data.get('status') and assistant_data['status'] not in valid_statuses:
                result.errors.append(f"Invalid status: {assistant_data['status']}. Must be one of {valid_statuses}")
                result.is_valid = False

            # Performance warning
            if len(knowledge_files) > 25:
                result.warnings.append(f"High knowledge file count ({len(knowledge_files)}) may impact performance")

        except Exception as e:
            logger.error(f"Error validating animal assistant: {str(e)}")
            result.errors.append(f"Validation error: {str(e)}")
            result.is_valid = False

        return result

    def validate_personality(self, personality_data: Dict[str, Any]) -> ValidationResult:
        """
        Validate personality entity.

        Business Rules:
        - Name must be unique across all personalities
        - Personality text 100-5000 characters
        - Valid animal type and tone enums
        """
        result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=[],
            info=[],
            entity_type=EntityType.PERSONALITY,
            entity_id=personality_data.get('personalityId')
        )

        try:
            # Required fields
            required_fields = ['personalityId', 'name', 'personalityText']
            for field in required_fields:
                if not personality_data.get(field):
                    result.errors.append(f"Required field missing: {field}")
                    result.is_valid = False

            # UUID validation
            if personality_data.get('personalityId'):
                if not self._validate_uuid_format(personality_data['personalityId']):
                    result.errors.append("Invalid UUID format for personalityId")
                    result.is_valid = False

            # Name uniqueness (except for updates to same entity)
            if personality_data.get('name'):
                existing_id = self._check_name_uniqueness(EntityType.PERSONALITY,
                                                        personality_data['name'],
                                                        personality_data.get('personalityId'))
                if existing_id:
                    result.errors.append(f"Personality name '{personality_data['name']}' already exists: {existing_id}")
                    result.is_valid = False

            # Personality text length validation
            personality_text = personality_data.get('personalityText', '')
            if len(personality_text) < 100:
                result.errors.append("Personality text must be at least 100 characters")
                result.is_valid = False
            elif len(personality_text) > 5000:
                result.errors.append("Personality text cannot exceed 5000 characters")
                result.is_valid = False

            # Animal type validation
            valid_animal_types = ['MAMMAL', 'BIRD', 'REPTILE', 'AMPHIBIAN', 'FISH', 'INVERTEBRATE']
            if personality_data.get('animalType') and personality_data['animalType'] not in valid_animal_types:
                result.warnings.append(f"Unusual animal type: {personality_data['animalType']}")

            # Tone validation
            valid_tones = ['PLAYFUL', 'EDUCATIONAL', 'CALM', 'ENERGETIC', 'WISE', 'FRIENDLY']
            if personality_data.get('tone') and personality_data['tone'] not in valid_tones:
                result.warnings.append(f"Unusual tone: {personality_data['tone']}")

        except Exception as e:
            logger.error(f"Error validating personality: {str(e)}")
            result.errors.append(f"Validation error: {str(e)}")
            result.is_valid = False

        return result

    def validate_guardrail(self, guardrail_data: Dict[str, Any]) -> ValidationResult:
        """
        Validate guardrail entity.

        Business Rules:
        - Name must be unique across all guardrails
        - Only one default guardrail per category
        - Guardrail text 50-2000 characters
        """
        result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=[],
            info=[],
            entity_type=EntityType.GUARDRAIL,
            entity_id=guardrail_data.get('guardrailId')
        )

        try:
            # Required fields
            required_fields = ['guardrailId', 'name', 'guardrailText', 'category']
            for field in required_fields:
                if not guardrail_data.get(field):
                    result.errors.append(f"Required field missing: {field}")
                    result.is_valid = False

            # UUID validation
            if guardrail_data.get('guardrailId'):
                if not self._validate_uuid_format(guardrail_data['guardrailId']):
                    result.errors.append("Invalid UUID format for guardrailId")
                    result.is_valid = False

            # Name uniqueness
            if guardrail_data.get('name'):
                existing_id = self._check_name_uniqueness(EntityType.GUARDRAIL,
                                                        guardrail_data['name'],
                                                        guardrail_data.get('guardrailId'))
                if existing_id:
                    result.errors.append(f"Guardrail name '{guardrail_data['name']}' already exists: {existing_id}")
                    result.is_valid = False

            # Guardrail text length validation
            guardrail_text = guardrail_data.get('guardrailText', '')
            if len(guardrail_text) < 50:
                result.errors.append("Guardrail text must be at least 50 characters")
                result.is_valid = False
            elif len(guardrail_text) > 2000:
                result.errors.append("Guardrail text cannot exceed 2000 characters")
                result.is_valid = False

            # Category validation
            valid_categories = ['SAFETY', 'EDUCATION', 'TONE', 'CONTENT']
            if guardrail_data.get('category') and guardrail_data['category'] not in valid_categories:
                result.warnings.append(f"Unusual category: {guardrail_data['category']}")

            # Default guardrail uniqueness per category
            if guardrail_data.get('isDefault') and guardrail_data.get('category'):
                existing_default = self._check_default_guardrail_uniqueness(
                    guardrail_data['category'],
                    guardrail_data.get('guardrailId')
                )
                if existing_default:
                    result.errors.append(f"Category '{guardrail_data['category']}' already has default guardrail: {existing_default}")
                    result.is_valid = False

        except Exception as e:
            logger.error(f"Error validating guardrail: {str(e)}")
            result.errors.append(f"Validation error: {str(e)}")
            result.is_valid = False

        return result

    def validate_knowledge_file(self, file_data: Dict[str, Any]) -> ValidationResult:
        """
        Validate knowledge base file entity.

        Business Rules:
        - File size ≤ 50MB per file
        - Total files ≤ 500MB per assistant
        - Supported MIME types: PDF, DOC, DOCX, TXT
        - Processing timeout: 5 minutes
        """
        result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=[],
            info=[],
            entity_type=EntityType.KNOWLEDGE_FILE,
            entity_id=file_data.get('fileId')
        )

        try:
            # Required fields
            required_fields = ['fileId', 'assistantId', 'originalName', 's3Key', 'fileSize', 'mimeType']
            for field in required_fields:
                if not file_data.get(field):
                    result.errors.append(f"Required field missing: {field}")
                    result.is_valid = False

            # File size validation
            file_size = file_data.get('fileSize', 0)
            if file_size > self.MAX_FILE_SIZE_BYTES:
                result.errors.append(f"File size {file_size} exceeds limit {self.MAX_FILE_SIZE_BYTES}")
                result.is_valid = False

            # MIME type validation
            valid_mime_types = [
                'application/pdf',
                'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'text/plain'
            ]
            if file_data.get('mimeType') and file_data['mimeType'] not in valid_mime_types:
                result.errors.append(f"Unsupported MIME type: {file_data['mimeType']}")
                result.is_valid = False

            # Filename validation
            if file_data.get('originalName'):
                if not self.VALIDATION_PATTERNS['filename'].match(file_data['originalName']):
                    result.warnings.append(f"Unusual filename format: {file_data['originalName']}")

            # Processing status validation
            valid_statuses = ['UPLOADED', 'PROCESSING', 'COMPLETED', 'FAILED']
            if file_data.get('processingStatus') and file_data['processingStatus'] not in valid_statuses:
                result.errors.append(f"Invalid processing status: {file_data['processingStatus']}")
                result.is_valid = False

            # Assistant total file size validation
            if file_data.get('assistantId'):
                total_size = self._calculate_assistant_total_file_size(file_data['assistantId'], file_data.get('fileId'))
                if total_size + file_size > self.MAX_TOTAL_FILES_SIZE_BYTES:
                    result.errors.append(f"Total files would exceed {self.MAX_TOTAL_FILES_SIZE_BYTES} bytes")
                    result.is_valid = False

        except Exception as e:
            logger.error(f"Error validating knowledge file: {str(e)}")
            result.errors.append(f"Validation error: {str(e)}")
            result.is_valid = False

        return result

    def validate_sandbox_assistant(self, sandbox_data: Dict[str, Any]) -> ValidationResult:
        """
        Validate sandbox assistant entity.

        Business Rules:
        - 30-minute expiry via TTL
        - Limited knowledge base files (≤ 10)
        - Immutable after creation
        - Must reference valid personality and guardrail
        """
        result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=[],
            info=[],
            entity_type=EntityType.SANDBOX_ASSISTANT,
            entity_id=sandbox_data.get('sandboxId')
        )

        try:
            # Required fields
            required_fields = ['sandboxId', 'createdBy', 'personalityId', 'guardrailId']
            for field in required_fields:
                if not sandbox_data.get(field):
                    result.errors.append(f"Required field missing: {field}")
                    result.is_valid = False

            # Expiry validation (30 minutes from creation)
            if not sandbox_data.get('expiresAt'):
                # Auto-generate expiry if missing
                expiry_time = datetime.utcnow() + timedelta(minutes=self.SANDBOX_EXPIRY_MINUTES)
                sandbox_data['expiresAt'] = int(expiry_time.timestamp())
                result.info.append(f"Auto-generated expiry time: {expiry_time.isoformat()}")

            # Knowledge file count validation (stricter for sandbox)
            knowledge_files = sandbox_data.get('knowledgeBaseFileIds', [])
            if len(knowledge_files) > self.MAX_SANDBOX_FILES_PER_ASSISTANT:
                result.errors.append(f"Too many knowledge files for sandbox: {len(knowledge_files)} > {self.MAX_SANDBOX_FILES_PER_ASSISTANT}")
                result.is_valid = False

            # Reference validation
            if sandbox_data.get('personalityId'):
                if not self._entity_exists(EntityType.PERSONALITY, sandbox_data['personalityId']):
                    result.errors.append(f"Personality {sandbox_data['personalityId']} does not exist")
                    result.is_valid = False

            if sandbox_data.get('guardrailId'):
                if not self._entity_exists(EntityType.GUARDRAIL, sandbox_data['guardrailId']):
                    result.errors.append(f"Guardrail {sandbox_data['guardrailId']} does not exist")
                    result.is_valid = False

        except Exception as e:
            logger.error(f"Error validating sandbox assistant: {str(e)}")
            result.errors.append(f"Validation error: {str(e)}")
            result.is_valid = False

        return result

    # Helper methods for validation checks

    def _validate_uuid_format(self, uuid_string: str) -> bool:
        """Validate UUID format."""
        return bool(self.VALIDATION_PATTERNS['uuid'].match(uuid_string))

    def _entity_exists(self, entity_type: EntityType, entity_id: str) -> bool:
        """Check if entity exists in DynamoDB."""
        try:
            table_name = self.TABLE_NAMES[entity_type]
            table_ref = table(table_name)

            # Determine primary key field based on entity type
            pk_field = {
                EntityType.PERSONALITY: 'personalityId',
                EntityType.GUARDRAIL: 'guardrailId',
                EntityType.ANIMAL_ASSISTANT: 'assistantId',
                EntityType.KNOWLEDGE_FILE: 'fileId',
                EntityType.SANDBOX_ASSISTANT: 'sandboxId'
            }[entity_type]

            response = table_ref.get_item(Key={pk_field: entity_id})
            return 'Item' in response

        except Exception as e:
            logger.warning(f"Error checking entity existence: {str(e)}")
            return False

    def _check_existing_assistant_for_animal(self, animal_id: str) -> Optional[str]:
        """Check if animal already has an assistant."""
        try:
            table_ref = table(self.TABLE_NAMES[EntityType.ANIMAL_ASSISTANT])
            response = table_ref.query(
                IndexName='AnimalIndex',
                KeyConditionExpression='animalId = :animal_id',
                ExpressionAttributeValues={':animal_id': animal_id}
            )

            if response['Items']:
                return response['Items'][0]['assistantId']
            return None

        except Exception as e:
            logger.warning(f"Error checking existing assistant: {str(e)}")
            return None

    def _check_name_uniqueness(self, entity_type: EntityType, name: str, exclude_id: Optional[str] = None) -> Optional[str]:
        """Check if name is unique for the entity type."""
        try:
            table_ref = table(self.TABLE_NAMES[entity_type])
            response = table_ref.query(
                IndexName='NameIndex',
                KeyConditionExpression='#name = :name',
                ExpressionAttributeNames={'#name': 'name'},
                ExpressionAttributeValues={':name': name}
            )

            for item in response['Items']:
                entity_id_field = {
                    EntityType.PERSONALITY: 'personalityId',
                    EntityType.GUARDRAIL: 'guardrailId'
                }[entity_type]

                if item[entity_id_field] != exclude_id:
                    return item[entity_id_field]

            return None

        except Exception as e:
            logger.warning(f"Error checking name uniqueness: {str(e)}")
            return None

    def _check_default_guardrail_uniqueness(self, category: str, exclude_id: Optional[str] = None) -> Optional[str]:
        """Check if category already has a default guardrail."""
        try:
            table_ref = table(self.TABLE_NAMES[EntityType.GUARDRAIL])
            response = table_ref.query(
                IndexName='CategoryIndex',
                KeyConditionExpression='category = :category',
                FilterExpression='isDefault = :is_default',
                ExpressionAttributeValues={
                    ':category': category,
                    ':is_default': True
                }
            )

            for item in response['Items']:
                if item['guardrailId'] != exclude_id:
                    return item['guardrailId']

            return None

        except Exception as e:
            logger.warning(f"Error checking default guardrail uniqueness: {str(e)}")
            return None

    def _calculate_assistant_total_file_size(self, assistant_id: str, exclude_file_id: Optional[str] = None) -> int:
        """Calculate total file size for an assistant."""
        try:
            table_ref = table(self.TABLE_NAMES[EntityType.KNOWLEDGE_FILE])
            response = table_ref.query(
                IndexName='AssistantIndex',
                KeyConditionExpression='assistantId = :assistant_id',
                ExpressionAttributeValues={':assistant_id': assistant_id}
            )

            total_size = 0
            for item in response['Items']:
                if item['fileId'] != exclude_file_id:
                    total_size += item.get('fileSize', 0)

            return total_size

        except Exception as e:
            logger.warning(f"Error calculating total file size: {str(e)}")
            return 0


class AuditTrail:
    """
    Audit trail manager for Animal Assistant Management operations.

    Provides comprehensive audit logging for compliance and debugging.
    """

    def __init__(self):
        """Initialize audit trail manager."""
        self.audit_entries = []

    def log_operation(self, operation_type: OperationType, entity_type: EntityType,
                     entity_id: str, user_id: Optional[str] = None,
                     changes: Optional[Dict[str, Any]] = None,
                     metadata: Optional[Dict[str, Any]] = None) -> AuditEntry:
        """
        Log an operation to the audit trail.

        Args:
            operation_type: Type of operation performed
            entity_type: Type of entity affected
            entity_id: ID of the entity
            user_id: ID of user performing operation
            changes: Dict of field changes (old_value → new_value)
            metadata: Additional operation metadata

        Returns:
            AuditEntry created for the operation
        """
        entry = AuditEntry(
            operation_type=operation_type,
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            timestamp=now_iso(),
            changes=changes,
            metadata=metadata
        )

        self.audit_entries.append(entry)

        logger.info(f"Audit: {operation_type.value} {entity_type.value} {entity_id} by {user_id}")

        return entry

    def get_audit_trail(self, entity_id: Optional[str] = None,
                       entity_type: Optional[EntityType] = None,
                       user_id: Optional[str] = None,
                       limit: int = 100) -> List[AuditEntry]:
        """
        Retrieve audit trail entries with optional filtering.

        Args:
            entity_id: Filter by specific entity ID
            entity_type: Filter by entity type
            user_id: Filter by user ID
            limit: Maximum number of entries to return

        Returns:
            List of matching audit entries
        """
        filtered_entries = self.audit_entries

        if entity_id:
            filtered_entries = [e for e in filtered_entries if e.entity_id == entity_id]

        if entity_type:
            filtered_entries = [e for e in filtered_entries if e.entity_type == entity_type]

        if user_id:
            filtered_entries = [e for e in filtered_entries if e.user_id == user_id]

        # Sort by timestamp (newest first) and limit
        filtered_entries.sort(key=lambda x: x.timestamp, reverse=True)

        return filtered_entries[:limit]


# Convenience functions for common validation operations
def validate_entity(entity_type: EntityType, entity_data: Dict[str, Any],
                   operation: OperationType = OperationType.CREATE) -> ValidationResult:
    """
    Convenience function to validate any entity type.

    Args:
        entity_type: Type of entity to validate
        entity_data: Entity data dictionary
        operation: Operation being performed

    Returns:
        ValidationResult with validation details
    """
    validator = AssistantValidator()

    validation_methods = {
        EntityType.ANIMAL_ASSISTANT: validator.validate_animal_assistant,
        EntityType.PERSONALITY: validator.validate_personality,
        EntityType.GUARDRAIL: validator.validate_guardrail,
        EntityType.KNOWLEDGE_FILE: validator.validate_knowledge_file,
        EntityType.SANDBOX_ASSISTANT: validator.validate_sandbox_assistant
    }

    if entity_type not in validation_methods:
        return ValidationResult(
            is_valid=False,
            errors=[f"Unsupported entity type: {entity_type}"],
            warnings=[],
            info=[],
            entity_type=entity_type
        )

    if entity_type == EntityType.ANIMAL_ASSISTANT:
        return validation_methods[entity_type](entity_data, operation)
    else:
        return validation_methods[entity_type](entity_data)


def create_audit_entry(operation_type: OperationType, entity_type: EntityType,
                      entity_id: str, user_id: Optional[str] = None,
                      changes: Optional[Dict[str, Any]] = None) -> AuditEntry:
    """
    Convenience function to create an audit entry.

    Args:
        operation_type: Type of operation
        entity_type: Type of entity
        entity_id: Entity identifier
        user_id: User performing operation
        changes: Changes made (for updates)

    Returns:
        AuditEntry for the operation
    """
    audit_trail = AuditTrail()
    return audit_trail.log_operation(operation_type, entity_type, entity_id, user_id, changes)


# Module-level logger configuration
if __name__ == '__main__':
    # Configure logging for standalone testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Example validation testing
    validator = AssistantValidator()

    # Test animal assistant validation
    test_assistant = {
        'assistantId': 'f47ac10b-58cc-4372-a567-0e02b2c3d479',
        'animalId': 'lion_001',
        'personalityId': 'f47ac10b-58cc-4372-a567-0e02b2c3d478',
        'guardrailId': 'f47ac10b-58cc-4372-a567-0e02b2c3d477',
        'status': 'ACTIVE',
        'knowledgeBaseFileIds': []
    }

    print("Testing animal assistant validation...")
    result = validator.validate_animal_assistant(test_assistant)
    print(f"Valid: {result.is_valid}")
    print(f"Errors: {result.errors}")
    print(f"Warnings: {result.warnings}")

    # Test audit trail
    audit = AuditTrail()
    entry = audit.log_operation(
        OperationType.CREATE,
        EntityType.ANIMAL_ASSISTANT,
        test_assistant['assistantId'],
        'user_123'
    )
    print(f"Audit entry created: {entry.timestamp}")