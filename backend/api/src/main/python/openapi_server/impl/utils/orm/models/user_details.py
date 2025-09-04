import os
from typing import Dict, Any
from pynamodb.models import Model
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection
from pynamodb.attributes import (UnicodeAttribute, 
                                 BooleanAttribute, 
                                 MapAttribute, 
                                 NumberAttribute, 
                                 UTCDateTimeAttribute)

AWS_REGION = os.getenv("AWS_REGION", "us-west-2")
DDB_ENDPOINT = os.getenv("DYNAMODB_ENDPOINT_URL") or None
USER_DETAILS_TABLE_NAME = os.getenv("USER_DETAILS_TABLE_NAME", "quest-dev-user-details")
USER_DETAILS_GSI_USERID = os.getenv("USER_DETAILS_GSI_USERID", "userId")

class AuditBy(MapAttribute):
    userId = UnicodeAttribute(null=True)
    email = UnicodeAttribute(null=True)
    displayName = UnicodeAttribute(null=True)

class Audit(MapAttribute):
    at = UnicodeAttribute(null=True)
    by = AuditBy(null=True)

class UsageSummaryMap(MapAttribute):
    userId = UnicodeAttribute(null=True)
    totalSessions = NumberAttribute(null=True)
    totalTurns = NumberAttribute(null=True)
    lastActive = UTCDateTimeAttribute(null=True) 

class UserIdIndex(GlobalSecondaryIndex):
    class Meta:
        index_name = USER_DETAILS_GSI_USERID
        projection = AllProjection()
        region = AWS_REGION
        host = DDB_ENDPOINT  # None in prod

    userId = UnicodeAttribute(hash_key=True)

class UserDetailsModel(Model):
    class Meta:
        table_name = USER_DETAILS_TABLE_NAME
        region = AWS_REGION
        host = DDB_ENDPOINT

    # PK
    userDetailsId = UnicodeAttribute(hash_key=True)

    # Link to user
    userId = UnicodeAttribute(null=False)
    GSI_userId = UserIdIndex()

    # Enforced details payload
    usage = UsageSummaryMap(null=True)

    # Optional, free-form extras (keep if you want an escape hatch)
    extras = MapAttribute(null=True)

    # Soft delete + audit
    softDelete = BooleanAttribute(null=True, default=False)
    created = Audit(null=True)
    modified = Audit(null=True)
    deleted = Audit(null=True)

    def to_details_dict(self) -> Dict[str, Any]:
        return {
            "userDetailsId": self.userDetailsId,
            "userId": self.userId,
            "usage": self.usage.as_dict() if self.usage else None,
            "extras": self.extras.as_dict() if self.extras else None,
            "softDelete": bool(self.softDelete),
            "created": self.created.as_dict() if self.created else None,
            "modified": self.modified.as_dict() if self.modified else None,
            "deleted": self.deleted.as_dict() if self.deleted else None,
        }
