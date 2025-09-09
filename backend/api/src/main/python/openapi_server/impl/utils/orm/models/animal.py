import os
from typing import Dict, Any
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, BooleanAttribute, MapAttribute

AWS_REGION = os.getenv("AWS_REGION", "us-west-2")
DDB_ENDPOINT = os.getenv("DYNAMODB_ENDPOINT_URL") or None
ANIMAL_TABLE_NAME = os.getenv("ANIMAL_DYNAMO_TABLE_NAME", "quest-dev-animal")

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
        return {
            "id": self.animalId,
            "animalId": self.animalId,
            "name": self.name,
            "species": self.species,
            "status": self.status or "active",
            "personality": self.personality.as_dict() if self.personality else {},
            "configuration": self.configuration.as_dict() if self.configuration else {},
            "softDelete": bool(self.softDelete),
            "created": self.created.as_dict() if self.created else None,
            "modified": self.modified.as_dict() if self.modified else None,
            "deleted": self.deleted.as_dict() if self.deleted else None,
        }