import os
from typing import Dict, Any, List
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, BooleanAttribute, ListAttribute, MapAttribute

AWS_REGION = os.getenv("AWS_REGION", "us-west-2")
DDB_ENDPOINT = os.getenv("DYNAMODB_ENDPOINT_URL") or None
FAMILY_TABLE_NAME = os.getenv("FAMILY_DYNAMO_TABLE_NAME", "quest-dev-family")

class Audit(MapAttribute):
    at = UnicodeAttribute(null=True)
    by = UnicodeAttribute(null=True)

class FamilyModel(Model):
    class Meta:
        table_name = FAMILY_TABLE_NAME
        region = AWS_REGION
        host = DDB_ENDPOINT

    familyId = UnicodeAttribute(hash_key=True)
    parents = ListAttribute(of=UnicodeAttribute, null=True)
    students = ListAttribute(of=UnicodeAttribute, null=True)
    softDelete = BooleanAttribute(default=False, null=True)
    created = Audit(null=True)
    modified = Audit(null=True)

    def to_plain_dict(self) -> Dict[str, Any]:
        return {
            "familyId": self.familyId,
            "parents": list(self.parents or []),
            "students": list(self.students or []),
            "softDelete": bool(self.softDelete) if self.softDelete is not None else False,
            "created": dict(self.created.as_dict()) if self.created else None,
            "modified": dict(self.modified.as_dict()) if self.modified else None,
        }
