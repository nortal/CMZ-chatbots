import os
from typing import Dict, Any
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, BooleanAttribute, MapAttribute

AWS_REGION = os.getenv("AWS_REGION", "us-west-2")
DDB_ENDPOINT = os.getenv("DYNAMODB_ENDPOINT_URL") or None
USER_TABLE_NAME = os.getenv("USER_DYNAMO_TABLE_NAME", "quest-dev-user")

class AuditBy(MapAttribute):
    userId = UnicodeAttribute(null=True)
    email = UnicodeAttribute(null=True)
    displayName = UnicodeAttribute(null=True)

class Audit(MapAttribute):
    at = UnicodeAttribute(null=True)
    by = AuditBy(null=True)

class UserModel(Model):
    class Meta:
        table_name = USER_TABLE_NAME
        region = AWS_REGION
        host = DDB_ENDPOINT  # None in prod

    # PK
    userId = UnicodeAttribute(hash_key=True)

    # Core fields
    email = UnicodeAttribute(null=True)
    displayName = UnicodeAttribute(null=True)
    role = UnicodeAttribute(null=True)        # 'admin' | 'user' | ...
    userType = UnicodeAttribute(null=True)    # 'parent' | 'student' | 'none'
    familyId = UnicodeAttribute(null=True)

    # Soft delete + audit
    softDelete = BooleanAttribute(null=True, default=False)
    created = Audit(null=True)
    modified = Audit(null=True)
    deleted = Audit(null=True)

    def to_user_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.userId,
            "email": self.email,
            "displayName": self.displayName,
            "role": self.role,
            "userType": self.userType or "none",
            "familyId": self.familyId,
            "softDelete": bool(self.softDelete),
            "created": self.created.as_dict() if self.created else None,
            "modified": self.modified.as_dict() if self.modified else None,
            "deleted": self.deleted.as_dict() if self.deleted else None,
        }
