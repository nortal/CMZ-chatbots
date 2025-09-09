"""Audit service interface for tracking operations"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from ..domain.common.entities import AuditStamp


class AuditService(ABC):
    """Interface for audit trail operations"""
    
    @abstractmethod
    def create_creation_audit(self, actor_data: Optional[Dict[str, Any]] = None) -> Dict[str, AuditStamp]:
        """Create audit stamps for entity creation"""
        pass
    
    @abstractmethod
    def create_modification_audit(self, actor_data: Optional[Dict[str, Any]] = None) -> Dict[str, AuditStamp]:
        """Create audit stamps for entity modification"""
        pass
    
    @abstractmethod
    def create_deletion_audit(self, actor_data: Optional[Dict[str, Any]] = None) -> Dict[str, AuditStamp]:
        """Create audit stamps for entity deletion"""
        pass
    
    @abstractmethod
    def extract_actor_data(self, entity_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract actor information from entity data"""
        pass