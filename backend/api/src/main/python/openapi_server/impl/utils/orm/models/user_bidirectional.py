"""
User model with bidirectional family references
Supports multiple family associations per user
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
USER_TABLE_NAME = os.getenv("USER_DYNAMO_TABLE_NAME", "quest-dev-user")

class AuditBy(MapAttribute):
    """Audit trail for who made changes"""
    userId = UnicodeAttribute(null=True)
    email = UnicodeAttribute(null=True)
    displayName = UnicodeAttribute(null=True)

class Audit(MapAttribute):
    """Audit information for tracking changes"""
    at = UnicodeAttribute(null=True)
    by = AuditBy(null=True)

class UserModelBidirectional(Model):
    """
    Enhanced User model with bidirectional family references
    """
    class Meta:
        table_name = USER_TABLE_NAME
        region = AWS_REGION
        host = DDB_ENDPOINT  # None in prod

    # Primary Key
    userId = UnicodeAttribute(hash_key=True)

    # Core user fields
    email = UnicodeAttribute(null=True)
    displayName = UnicodeAttribute(null=True)
    phone = UnicodeAttribute(null=True)

    # Role and permissions
    role = UnicodeAttribute(null=True)  # 'admin' | 'parent' | 'student'
    userType = UnicodeAttribute(null=True)  # DEPRECATED - use role instead

    # Bidirectional family references (multiple families supported)
    familyIds = UnicodeSetAttribute(null=True)  # Set of family IDs

    # Contact preferences
    isPrimaryContact = BooleanAttribute(null=True, default=False)
    isEmergencyContact = BooleanAttribute(null=True, default=False)

    # Student-specific fields
    age = UnicodeAttribute(null=True)
    grade = UnicodeAttribute(null=True)
    interests = UnicodeAttribute(null=True)
    allergies = UnicodeAttribute(null=True)

    # Soft delete and audit trail
    softDelete = BooleanAttribute(null=True, default=False)
    created = Audit(null=True)
    modified = Audit(null=True)
    deleted = Audit(null=True)

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary for API responses"""
        return {
            "userId": self.userId,
            "email": self.email,
            "displayName": self.displayName,
            "phone": self.phone if hasattr(self, 'phone') else None,
            "role": self.role,
            "familyIds": list(self.familyIds) if self.familyIds else [],
            "isPrimaryContact": bool(self.isPrimaryContact) if hasattr(self, 'isPrimaryContact') else False,
            "isEmergencyContact": bool(self.isEmergencyContact) if hasattr(self, 'isEmergencyContact') else False,
            "age": self.age if hasattr(self, 'age') else None,
            "grade": self.grade if hasattr(self, 'grade') else None,
            "interests": self.interests if hasattr(self, 'interests') else None,
            "allergies": self.allergies if hasattr(self, 'allergies') else None,
            "softDelete": bool(self.softDelete),
            "created": self.created.as_dict() if self.created else None,
            "modified": self.modified.as_dict() if self.modified else None,
            "deleted": self.deleted.as_dict() if self.deleted else None,
        }

    def add_family(self, family_id: str) -> None:
        """Add a family ID to the user's family list"""
        if not self.familyIds:
            self.familyIds = set()
        self.familyIds.add(family_id)

    def remove_family(self, family_id: str) -> None:
        """Remove a family ID from the user's family list"""
        if self.familyIds and family_id in self.familyIds:
            self.familyIds.remove(family_id)

    def is_in_family(self, family_id: str) -> bool:
        """Check if user belongs to a specific family"""
        return family_id in self.familyIds if self.familyIds else False

    def can_view_family(self, family_id: str) -> bool:
        """Check if user can view a family (member or admin)"""
        return self.is_in_family(family_id) or self.role == 'admin'

    def can_edit_family(self, family_id: str) -> bool:
        """Check if user can edit a family (admin only)"""
        return self.role == 'admin'