"""Centralized serialization utilities for domain entities"""
from typing import Dict, Any, Optional, Type, TypeVar
from dataclasses import asdict
from .entities import (
    User, UserDetails, Family, Animal, 
    AuditStamp, AuditBy, UsageSummary
)
from .audit import create_audit_by, create_audit_stamp

T = TypeVar('T')


def serialize_audit_by(audit_by: Optional[AuditBy]) -> Dict[str, Any]:
    """Convert AuditBy domain entity to dict"""
    if not audit_by:
        # Provide valid defaults for OpenAPI validation
        return {
            "userId": "system",
            "email": "system@cmz.org",
            "displayName": "System"
        }

    return {
        "userId": audit_by.user_id or "system",
        "email": audit_by.email or "system@cmz.org",
        "displayName": audit_by.display_name or "System"
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


def normalize_personality_field(personality_raw) -> Dict[str, Any]:
    """
    Normalize personality field that can be either string or dict format.
    
    Args:
        personality_raw: Raw personality data (string, dict, or other)
        
    Returns:
        Dict with personality data in standardized format
    """
    if isinstance(personality_raw, str):
        # Convert string personality to dict format for domain entity
        return {"description": personality_raw} if personality_raw else {}
    elif isinstance(personality_raw, dict):
        return personality_raw
    else:
        return {}


def serialize_audit_stamp(audit_stamp: Optional[AuditStamp]) -> Dict[str, Any]:
    """Convert AuditStamp domain entity to dict"""
    if not audit_stamp:
        # Provide valid defaults for OpenAPI validation
        from datetime import datetime, timezone
        return {
            "at": datetime.now(timezone.utc).isoformat(),
            "by": serialize_audit_by(None)
        }

    # Convert datetime to ISO string for JSON serialization
    at_value = audit_stamp.at
    if hasattr(at_value, 'isoformat'):
        at_value = at_value.isoformat()
    elif at_value and not isinstance(at_value, str):
        at_value = str(at_value)

    return {
        "at": at_value,
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
    # Handle personality field - keep as dict for database, string for API
    personality_value = animal.personality or {}

    # For API responses, convert to string
    if include_api_id:
        if isinstance(personality_value, dict) and 'description' in personality_value:
            # Extract description string from dict format
            personality_value = personality_value['description']
        elif isinstance(personality_value, dict) and personality_value:
            # If it's a dict without description, try to get first string value
            for key, val in personality_value.items():
                if isinstance(val, str):
                    personality_value = val
                    break
        elif not isinstance(personality_value, str):
            # Default to empty string if not a string
            personality_value = ""
    else:
        # For database operations, ensure it's a dict with description key
        if isinstance(personality_value, str):
            personality_value = {"description": personality_value}
        elif isinstance(personality_value, dict):
            # Ensure it has a description key
            if 'description' not in personality_value:
                # Try to extract any string value
                desc = ""
                for key, val in personality_value.items():
                    if isinstance(val, str):
                        desc = val
                        break
                personality_value = {"description": desc}
        else:
            personality_value = {"description": ""}

    result = {
        "animalId": animal.animal_id,
        "name": animal.name,
        "species": animal.species,
        "description": animal.description,
        "status": animal.status,
        "personality": personality_value,  # Dict for DB, string for API
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

    # Handle personality field - can be string, dict, or nested DynamoDB Map
    personality_raw = data.get("personality", {})

    # If it's already a string, use it directly
    if isinstance(personality_raw, str):
        personality = {"description": personality_raw} if personality_raw else {}
    # If it's a dict with 'description' key, use as is
    elif isinstance(personality_raw, dict) and 'description' in personality_raw:
        personality = personality_raw
    # If it's a DynamoDB Map structure (M type)
    elif isinstance(personality_raw, dict) and 'M' in personality_raw:
        # Extract from nested Map structure
        map_data = personality_raw['M']
        if 'description' in map_data and 'S' in map_data['description']:
            personality = {"description": map_data['description']['S']}
        else:
            personality = {}
    else:
        # Use the helper function for other cases
        personality = normalize_personality_field(personality_raw)
    
    return Animal(
        animal_id=animal_id,
        name=data.get("name", ""),
        species=data.get("species"),
        description=data.get("description"),
        status=data.get("status", "active"),
        personality=personality,
        configuration=data.get("configuration", {}),
        soft_delete=bool(data.get("softDelete", False)),
        created=deserialize_audit_stamp(data.get("created")),
        modified=deserialize_audit_stamp(data.get("modified")),
        deleted=deserialize_audit_stamp(data.get("deleted"))
    )