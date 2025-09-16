import os
from typing import Dict, Any, Optional
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, BooleanAttribute, MapAttribute, Attribute
from pynamodb.constants import STRING

AWS_REGION = os.getenv("AWS_REGION", "us-west-2")
DDB_ENDPOINT = os.getenv("DYNAMODB_ENDPOINT_URL") or None
ANIMAL_TABLE_NAME = os.getenv("ANIMAL_DYNAMO_TABLE_NAME", "quest-dev-animal")

# PersonalityMap removed - using regular MapAttribute

class AuditBy(MapAttribute):
    userId = UnicodeAttribute(null=True)
    email = UnicodeAttribute(null=True)
    displayName = UnicodeAttribute(null=True)

class Audit(MapAttribute):
    at = UnicodeAttribute(null=True)
    by = AuditBy(null=True)

class AnimalModel(Model):
    class Meta:
        table_name = ANIMAL_TABLE_NAME
        region = AWS_REGION
        host = DDB_ENDPOINT  # None in prod

    # PK
    animalId = UnicodeAttribute(hash_key=True)

    # Core fields
    name = UnicodeAttribute(null=True)
    species = UnicodeAttribute(null=True)
    status = UnicodeAttribute(null=True, default="active")

    # JSON fields for complex data
    personality = MapAttribute(null=True)
    configuration = MapAttribute(null=True)

    # Soft delete + audit
    softDelete = BooleanAttribute(null=True, default=False)
    created = Audit(null=True)
    modified = Audit(null=True)
    deleted = Audit(null=True)

    def to_animal_dict(self) -> Dict[str, Any]:
        # Handle personality field - extract from MapAttribute
        personality_value = ""
        if self.personality:
            # personality is a MapAttribute
            if hasattr(self.personality, 'as_dict'):
                # Try to get it as dict
                p_dict = self.personality.as_dict()
                personality_value = p_dict.get('description', "") if p_dict else ""
            elif hasattr(self.personality, 'attribute_values'):
                # Get from attribute_values
                av = self.personality.attribute_values
                if 'description' in av:
                    personality_value = av.get('description') or ""

        # Safely handle configuration
        config_value = {}
        if self.configuration:
            try:
                config_value = self.configuration.as_dict()
            except Exception as e:
                print(f"Error converting configuration to dict: {e}")
                config_value = {}

        # Safely handle audit fields
        def safe_audit_dict(audit_field):
            if not audit_field:
                return None
            try:
                audit_dict = audit_field.as_dict()
                # Ensure all values are serializable
                if audit_dict and 'by' in audit_dict and audit_dict['by']:
                    # Make sure 'by' is a dict, not a callable or object
                    if not isinstance(audit_dict['by'], dict):
                        if hasattr(audit_dict['by'], 'as_dict'):
                            audit_dict['by'] = audit_dict['by'].as_dict()
                return audit_dict
            except Exception as e:
                print(f"Error converting audit field to dict: {e}")
                return None

        return {
            "id": self.animalId,
            "animalId": self.animalId,
            "name": self.name,
            "species": self.species,
            "status": self.status or "active",
            "personality": personality_value,
            "configuration": config_value,
            "softDelete": bool(self.softDelete),
            "created": safe_audit_dict(self.created),
            "modified": safe_audit_dict(self.modified),
            "deleted": safe_audit_dict(self.deleted),
        }