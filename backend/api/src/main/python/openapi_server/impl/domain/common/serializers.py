"""Centralized serialization utilities for domain entities"""
from typing import Dict, Any, Optional, Type, TypeVar
from dataclasses import asdict
from .entities import (
    User, UserDetails, Family, Animal, 
    AuditStamp, AuditBy, UsageSummary
)
from .audit import create_audit_by, create_audit_stamp

T = TypeVar('T')


def serialize_audit_by(audit_by: Optional[AuditBy]) -> Optional[Dict[str, Any]]:
    """Convert AuditBy domain entity to dict"""
    if not audit_by:
        return None
    
    return {
        "userId": audit_by.user_id,
        "email": audit_by.email,
        "displayName": audit_by.display_name
    }


def deserialize_audit_by(data: Optional[Dict[str, Any]]) -> Optional[AuditBy]:
    """Convert dict to AuditBy domain entity"""
    if not data:
        return None
    
    return AuditBy(
        user_id=data.get("userId"),
        email=data.get("email"),
        display_name=data.get("displayName")
    )


def serialize_audit_stamp(audit_stamp: Optional[AuditStamp]) -> Optional[Dict[str, Any]]:
    """Convert AuditStamp domain entity to dict"""
    if not audit_stamp:
        return None
    
    return {
        "at": audit_stamp.at,
        "by": serialize_audit_by(audit_stamp.by)
    }


def deserialize_audit_stamp(data: Optional[Dict[str, Any]]) -> Optional[AuditStamp]:
    """Convert dict to AuditStamp domain entity"""
    if not data:
        return None
    
    return AuditStamp(
        at=data.get("at", ""),
        by=deserialize_audit_by(data.get("by"))
    )


def serialize_usage_summary(usage: Optional[UsageSummary]) -> Optional[Dict[str, Any]]:
    """Convert UsageSummary domain entity to dict"""
    if not usage:
        return None
    
    return {
        "userId": usage.user_id,
        "totalSessions": usage.total_sessions,
        "totalTurns": usage.total_turns,
        "lastActive": usage.last_active.isoformat() if usage.last_active else None
    }


def deserialize_usage_summary(data: Optional[Dict[str, Any]]) -> Optional[UsageSummary]:
    """Convert dict to UsageSummary domain entity"""
    if not data:
        return None
    
    from datetime import datetime
    last_active = None
    if data.get("lastActive"):
        try:
            last_active = datetime.fromisoformat(data["lastActive"].replace('Z', '+00:00'))
        except (ValueError, TypeError):
            last_active = None
    
    return UsageSummary(
        user_id=data.get("userId"),
        total_sessions=data.get("totalSessions"),
        total_turns=data.get("totalTurns"),
        last_active=last_active
    )


def serialize_user(user: User) -> Dict[str, Any]:
    """Convert User domain entity to dict"""
    return {
        "userId": user.user_id,
        "email": user.email,
        "displayName": user.display_name,
        "role": user.role,
        "userType": user.user_type,
        "familyId": user.family_id,
        "softDelete": user.soft_delete,
        "created": serialize_audit_stamp(user.created),
        "modified": serialize_audit_stamp(user.modified),
        "deleted": serialize_audit_stamp(user.deleted)
    }


def deserialize_user(data: Dict[str, Any]) -> User:
    """Convert dict to User domain entity"""
    return User(
        user_id=data.get("userId", ""),
        email=data.get("email", ""),
        display_name=data.get("displayName"),
        role=data.get("role"),
        user_type=data.get("userType", "none"),
        family_id=data.get("familyId"),
        soft_delete=bool(data.get("softDelete", False)),
        created=deserialize_audit_stamp(data.get("created")),
        modified=deserialize_audit_stamp(data.get("modified")),
        deleted=deserialize_audit_stamp(data.get("deleted"))
    )


def serialize_user_details(user_details: UserDetails) -> Dict[str, Any]:
    """Convert UserDetails domain entity to dict"""
    return {
        "userDetailsId": user_details.user_details_id,
        "userId": user_details.user_id,
        "usage": serialize_usage_summary(user_details.usage),
        "extras": user_details.extras or {},
        "softDelete": user_details.soft_delete,
        "created": serialize_audit_stamp(user_details.created),
        "modified": serialize_audit_stamp(user_details.modified),
        "deleted": serialize_audit_stamp(user_details.deleted)
    }


def deserialize_user_details(data: Dict[str, Any]) -> UserDetails:
    """Convert dict to UserDetails domain entity"""
    return UserDetails(
        user_details_id=data.get("userDetailsId", ""),
        user_id=data.get("userId", ""),
        usage=deserialize_usage_summary(data.get("usage")),
        extras=data.get("extras", {}),
        soft_delete=bool(data.get("softDelete", False)),
        created=deserialize_audit_stamp(data.get("created")),
        modified=deserialize_audit_stamp(data.get("modified")),
        deleted=deserialize_audit_stamp(data.get("deleted"))
    )


def serialize_family(family: Family) -> Dict[str, Any]:
    """Convert Family domain entity to dict"""
    return {
        "familyId": family.family_id,
        "name": family.name,
        "description": family.description,
        "softDelete": family.soft_delete,
        "created": serialize_audit_stamp(family.created),
        "modified": serialize_audit_stamp(family.modified),
        "deleted": serialize_audit_stamp(family.deleted)
    }


def deserialize_family(data: Dict[str, Any]) -> Family:
    """Convert dict to Family domain entity"""
    return Family(
        family_id=data.get("familyId", ""),
        name=data.get("name"),
        description=data.get("description"),
        soft_delete=bool(data.get("softDelete", False)),
        created=deserialize_audit_stamp(data.get("created")),
        modified=deserialize_audit_stamp(data.get("modified")),
        deleted=deserialize_audit_stamp(data.get("deleted"))
    )


def serialize_animal(animal: Animal, include_api_id: bool = True) -> Dict[str, Any]:
    """Convert Animal domain entity to dict"""
    result = {
        "animalId": animal.animal_id,
        "name": animal.name,
        "species": animal.species,
        "status": animal.status,
        "personality": animal.personality or {},
        "configuration": animal.configuration or {},
        "softDelete": animal.soft_delete,
        "created": serialize_audit_stamp(animal.created),
        "modified": serialize_audit_stamp(animal.modified),
        "deleted": serialize_audit_stamp(animal.deleted)
    }
    
    # Only include 'id' field for API responses, not for database persistence
    if include_api_id:
        result["id"] = animal.animal_id
        
    return result


def deserialize_animal(data: Dict[str, Any]) -> Animal:
    """Convert dict to Animal domain entity"""
    # Handle both 'id' and 'animalId' from different sources
    animal_id = data.get("animalId") or data.get("id", "")
    
    return Animal(
        animal_id=animal_id,
        name=data.get("name", ""),
        species=data.get("species"),
        status=data.get("status", "active"),
        personality=data.get("personality", {}),
        configuration=data.get("configuration", {}),
        soft_delete=bool(data.get("softDelete", False)),
        created=deserialize_audit_stamp(data.get("created")),
        modified=deserialize_audit_stamp(data.get("modified")),
        deleted=deserialize_audit_stamp(data.get("deleted"))
    )