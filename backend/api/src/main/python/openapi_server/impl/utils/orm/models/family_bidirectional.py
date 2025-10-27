"""
Family model with bidirectional user references
Stores user IDs instead of names for proper relationships
"""
import os
from typing import Dict, Any, List, Optional
from pynamodb.models import Model
from pynamodb.attributes import (
    UnicodeAttribute,
    BooleanAttribute,
    MapAttribute,
    ListAttribute,
    UnicodeSetAttribute
)

AWS_REGION = os.getenv("AWS_REGION", "us-west-2")
DDB_ENDPOINT = os.getenv("DYNAMODB_ENDPOINT_URL") or None
FAMILY_TABLE_NAME = os.getenv("FAMILY_DYNAMO_TABLE_NAME", "quest-dev-family")

class AuditBy(MapAttribute):
    """Audit trail for who made changes"""
    userId = UnicodeAttribute(null=True)
    email = UnicodeAttribute(null=True)
    displayName = UnicodeAttribute(null=True)

class Audit(MapAttribute):
    """Audit information for tracking changes"""
    at = UnicodeAttribute(null=True)
    by = AuditBy(null=True)

class Address(MapAttribute):
    """Family address information"""
    street = UnicodeAttribute(null=True)
    city = UnicodeAttribute(null=True)
    state = UnicodeAttribute(null=True)
    zip_code = UnicodeAttribute(null=True, attr_name='zipCode')  # Python uses snake_case, DynamoDB uses zipCode

class FamilyModelBidirectional(Model):
    """
    Enhanced Family model with bidirectional user references
    """
    class Meta:
        table_name = FAMILY_TABLE_NAME
        region = AWS_REGION
        host = DDB_ENDPOINT

    # Primary Key
    familyId = UnicodeAttribute(hash_key=True)

    # Family details
    familyName = UnicodeAttribute(null=True)
    address = Address(null=True)
    status = UnicodeAttribute(null=True, default="active")  # active | inactive | pending

    # Bidirectional user references (store user IDs, not names)
    parentIds = UnicodeSetAttribute(null=True)  # Set of parent user IDs
    studentIds = UnicodeSetAttribute(null=True)  # Set of student user IDs

    # Programs and preferences
    preferredPrograms = ListAttribute(of=UnicodeAttribute, null=True)
    memberSince = UnicodeAttribute(null=True)

    # Soft delete and audit trail
    softDelete = BooleanAttribute(default=False, null=True)
    created = Audit(null=True)
    modified = Audit(null=True)
    deleted = Audit(null=True)

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for API responses"""
        return {
            "familyId": self.familyId,
            "familyName": self.familyName,
            "parentIds": list(self.parentIds) if self.parentIds else [],
            "studentIds": list(self.studentIds) if self.studentIds else [],
            "address": self.address.as_dict() if self.address else {},
            "status": self.status,
            "preferredPrograms": list(self.preferredPrograms) if self.preferredPrograms else [],
            "memberSince": self.memberSince,
            "softDelete": bool(self.softDelete) if self.softDelete is not None else False,
            "created": self.created.as_dict() if self.created else None,
            "modified": self.modified.as_dict() if self.modified else None,
            "deleted": self.deleted.as_dict() if self.deleted else None,
        }

    def add_parent(self, user_id: str) -> None:
        """Add a parent user ID to the family"""
        if not self.parentIds:
            self.parentIds = set()
        self.parentIds.add(user_id)

    def remove_parent(self, user_id: str) -> None:
        """Remove a parent user ID from the family"""
        if self.parentIds and user_id in self.parentIds:
            self.parentIds.remove(user_id)

    def add_student(self, user_id: str) -> None:
        """Add a student user ID to the family"""
        if not self.studentIds:
            self.studentIds = set()
        self.studentIds.add(user_id)

    def remove_student(self, user_id: str) -> None:
        """Remove a student user ID from the family"""
        if self.studentIds and user_id in self.studentIds:
            self.studentIds.remove(user_id)

    def has_member(self, user_id: str) -> bool:
        """Check if a user is a member of this family"""
        is_parent = user_id in self.parentIds if self.parentIds else False
        is_student = user_id in self.studentIds if self.studentIds else False
        return is_parent or is_student

    def get_all_member_ids(self) -> List[str]:
        """Get all member IDs (parents and students)"""
        parent_list = list(self.parentIds) if self.parentIds else []
        student_list = list(self.studentIds) if self.studentIds else []
        return parent_list + student_list