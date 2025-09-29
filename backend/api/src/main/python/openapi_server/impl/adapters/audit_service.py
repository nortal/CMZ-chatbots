"""Standard audit service implementation supporting both domain audit stamps and logging"""
import logging
from typing import Dict, Any, Optional
from ..ports.audit import AuditService

try:
    # Try to import domain audit functionality (animals implementation)
    from ..domain.common.entities import AuditStamp
    from ..domain.common.audit import (
        create_creation_audit as domain_create_creation_audit,
        create_modification_audit as domain_create_modification_audit,  
        create_deletion_audit as domain_create_deletion_audit,
        extract_audit_by_from_data
    )
    DOMAIN_AUDIT_AVAILABLE = True
except ImportError:
    DOMAIN_AUDIT_AVAILABLE = False


class StandardAuditService(AuditService):
    """Standard implementation of audit service supporting both domain audit stamps and logging"""
    
    def __init__(self):
        self._logger = logging.getLogger("cmz.audit")
    
    def log_event(self, event_type: str, user_id: str, details: Dict[str, Any]) -> None:
        """Log an audit event"""
        self._logger.info(
            "Audit event",
            extra={
                "event_type": event_type,
                "user_id": user_id,
                "details": details
            }
        )
    
    # Domain audit methods (available when domain audit is imported)
    def create_creation_audit(self, actor_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create audit stamps for entity creation"""
        if DOMAIN_AUDIT_AVAILABLE:
            return domain_create_creation_audit(actor_data)
        else:
            # Fallback to simple timestamp audit
            from datetime import datetime
            return {"created": {"at": datetime.utcnow().isoformat() + "Z"}}
    
    def create_modification_audit(self, actor_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create audit stamps for entity modification"""
        if DOMAIN_AUDIT_AVAILABLE:
            return domain_create_modification_audit(actor_data)
        else:
            # Fallback to simple timestamp audit
            return {"modified": {"at": datetime.utcnow().isoformat() + "Z"}}
    
    def create_deletion_audit(self, actor_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create audit stamps for entity deletion"""
        if DOMAIN_AUDIT_AVAILABLE:
            return domain_create_deletion_audit(actor_data)
        else:
            # Fallback to simple timestamp audit
            return {"deleted": {"at": datetime.utcnow().isoformat() + "Z"}}
    
    def extract_actor_data(self, entity_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract actor information from entity data"""
        if DOMAIN_AUDIT_AVAILABLE:
            # Try to extract from 'created' or 'modified' audit fields
            actor_data = extract_audit_by_from_data(entity_data, "created")
            if not actor_data:
                actor_data = extract_audit_by_from_data(entity_data, "modified")
            return actor_data
        else:
            # Simple fallback
            return None
