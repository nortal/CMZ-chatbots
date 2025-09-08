"""Audit port interface"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class AuditService(ABC):
    """Port for audit logging"""
    
    @abstractmethod
    def log_event(self, event_type: str, user_id: str, details: Dict[str, Any]) -> None:
        """Log an audit event"""
        pass