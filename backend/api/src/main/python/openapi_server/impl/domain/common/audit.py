"""Audit trail utilities for domain operations"""
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from .entities import AuditStamp, AuditBy


def now_iso() -> str:
    """Generate current timestamp in ISO format"""
    return datetime.now(timezone.utc).isoformat()


def create_audit_by(audit_data: Optional[Dict[str, Any]] = None) -> AuditBy:
    """Create AuditBy from audit data dict"""
    if not audit_data:
        return AuditBy()
    
    return AuditBy(
        user_id=audit_data.get("userId"),
        email=audit_data.get("email"),
        display_name=audit_data.get("displayName")
    )


def create_audit_stamp(by_data: Optional[Dict[str, Any]] = None) -> AuditStamp:
    """Create audit stamp with current timestamp"""
    return AuditStamp(
        at=now_iso(),
        by=create_audit_by(by_data) if by_data else None
    )


def create_creation_audit(by_data: Optional[Dict[str, Any]] = None) -> Dict[str, AuditStamp]:
    """Create both created and modified audit stamps for new entities"""
    audit_stamp = create_audit_stamp(by_data)
    return {
        "created": audit_stamp,
        "modified": audit_stamp
    }


def create_modification_audit(by_data: Optional[Dict[str, Any]] = None) -> Dict[str, AuditStamp]:
    """Create modified audit stamp for entity updates"""
    return {
        "modified": create_audit_stamp(by_data)
    }


def create_deletion_audit(by_data: Optional[Dict[str, Any]] = None) -> Dict[str, AuditStamp]:
    """Create deleted audit stamp for soft deletes"""
    return {
        "deleted": create_audit_stamp(by_data),
        "modified": create_audit_stamp(by_data)
    }


def extract_audit_by_from_data(data: Dict[str, Any], audit_field: str = "created") -> Optional[Dict[str, Any]]:
    """Extract audit 'by' data from entity data"""
    audit_info = data.get(audit_field)
    if isinstance(audit_info, dict):
        return audit_info.get("by")
    return None


def merge_audit_data(entity_data: Dict[str, Any], audit_updates: Dict[str, Any]) -> Dict[str, Any]:
    """Merge audit updates into entity data"""
    result = entity_data.copy()
    result.update(audit_updates)
    return result