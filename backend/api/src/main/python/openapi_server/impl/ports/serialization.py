"""Serialization interfaces for different data formats"""
from abc import ABC, abstractmethod
from typing import Any, Dict, TypeVar, Type
from ..domain.common.entities import User, UserDetails, Family, Animal

T = TypeVar('T')


class EntitySerializer(ABC):
    """Base interface for entity serialization"""
    
    @abstractmethod
    def from_external(self, data: Any) -> Dict[str, Any]:
        """Convert external format to business dict"""
        pass
    
    @abstractmethod
    def to_external(self, entity_data: Dict[str, Any]) -> Any:
        """Convert business dict to external format"""
        pass


class UserSerializer(EntitySerializer):
    """Interface for user serialization operations"""
    
    @abstractmethod
    def from_openapi(self, openapi_model: Any) -> Dict[str, Any]:
        """Convert OpenAPI UserInput model to business dict"""
        pass
    
    @abstractmethod
    def to_openapi(self, user: User) -> Any:
        """Convert User domain entity to OpenAPI User model"""
        pass
    
    @abstractmethod
    def from_lambda_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Lambda event data to business dict"""
        pass
    
    @abstractmethod
    def to_lambda_response(self, user: User) -> Dict[str, Any]:
        """Convert User domain entity to Lambda response dict"""
        pass


class UserDetailsSerializer(EntitySerializer):
    """Interface for user details serialization operations"""
    
    @abstractmethod
    def from_openapi(self, openapi_model: Any) -> Dict[str, Any]:
        """Convert OpenAPI UserDetailsInput model to business dict"""
        pass
    
    @abstractmethod
    def to_openapi(self, user_details: UserDetails) -> Any:
        """Convert UserDetails domain entity to OpenAPI UserDetails model"""
        pass
    
    @abstractmethod
    def from_lambda_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Lambda event data to business dict"""
        pass
    
    @abstractmethod
    def to_lambda_response(self, user_details: UserDetails) -> Dict[str, Any]:
        """Convert UserDetails domain entity to Lambda response dict"""
        pass


class FamilySerializer(EntitySerializer):
    """Interface for family serialization operations"""
    
    @abstractmethod
    def from_openapi(self, openapi_model: Any) -> Dict[str, Any]:
        """Convert OpenAPI Family model to business dict"""
        pass
    
    @abstractmethod
    def to_openapi(self, family: Family) -> Any:
        """Convert Family domain entity to OpenAPI Family model"""
        pass
    
    @abstractmethod
    def from_lambda_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Lambda event data to business dict"""
        pass
    
    @abstractmethod
    def to_lambda_response(self, family: Family) -> Dict[str, Any]:
        """Convert Family domain entity to Lambda response dict"""
        pass


class AnimalSerializer(EntitySerializer):
    """Interface for animal serialization operations"""
    
    @abstractmethod
    def from_openapi(self, openapi_model: Any) -> Dict[str, Any]:
        """Convert OpenAPI Animal model to business dict"""
        pass
    
    @abstractmethod
    def to_openapi(self, animal: Animal) -> Any:
        """Convert Animal domain entity to OpenAPI Animal model"""
        pass
    
    @abstractmethod
    def from_lambda_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Lambda event data to business dict"""
        pass
    
    @abstractmethod
    def to_lambda_response(self, animal: Animal) -> Dict[str, Any]:
        """Convert Animal domain entity to Lambda response dict"""
        pass