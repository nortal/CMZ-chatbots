"""Standard audit service implementation"""
import logging
from typing import Dict, Any
from ..ports.audit import AuditService


class StandardAuditService(AuditService):
    """Standard implementation of audit service using Python logging"""
    
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