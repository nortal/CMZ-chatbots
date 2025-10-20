"""Repository interfaces for data access abstraction"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from ..domain.common.entities import User, UserDetails, Family, Animal


class UserRepository(ABC):
    """Interface for user data access operations"""
    
    @abstractmethod
    def create(self, user: User) -> User:
        """Create a new user"""
        pass
    
    @abstractmethod
    def get(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        pass
    
    @abstractmethod
    def list(self, hide_soft_deleted: bool = True) -> List[User]:
        """List all users"""
        pass
    
    @abstractmethod
    def update(self, user: User) -> User:
        """Update existing user"""
        pass
    
    @abstractmethod
    def soft_delete(self, user_id: str) -> None:
        """Soft delete user"""
        pass
    
    @abstractmethod
    def exists(self, user_id: str) -> bool:
        """Check if user exists"""
        pass


class UserDetailsRepository(ABC):
    """Interface for user details data access operations"""
    
    @abstractmethod
    def create(self, user_details: UserDetails) -> UserDetails:
        """Create new user details"""
        pass
    
    @abstractmethod
    def get_by_user_id(self, user_id: str) -> Optional[UserDetails]:
        """Get user details by user ID"""
        pass
    
    @abstractmethod
    def list(self, hide_soft_deleted: bool = True) -> List[UserDetails]:
        """List all user details"""
        pass
    
    @abstractmethod
    def update(self, user_details: UserDetails) -> UserDetails:
        """Update existing user details"""
        pass
    
    @abstractmethod
    def soft_delete(self, user_id: str) -> None:
        """Soft delete user details by user ID"""
        pass
    
    @abstractmethod
    def exists_for_user(self, user_id: str, hide_soft_deleted: bool = True) -> bool:
        """Check if user details exist for user ID"""
        pass


class FamilyRepository(ABC):
    """Interface for family data access operations"""
    
    @abstractmethod
    def create(self, family: Family) -> Family:
        """Create a new family"""
        pass
    
    @abstractmethod
    def get(self, family_id: str) -> Optional[Family]:
        """Get family by ID"""
        pass
    
    @abstractmethod
    def list(self, hide_soft_deleted: bool = True) -> List[Family]:
        """List all families"""
        pass
    
    @abstractmethod
    def update(self, family: Family) -> Family:
        """Update existing family"""
        pass
    
    @abstractmethod
    def soft_delete(self, family_id: str) -> None:
        """Soft delete family"""
        pass
    
    @abstractmethod
    def exists(self, family_id: str) -> bool:
        """Check if family exists"""
        pass


class AnimalRepository(ABC):
    """Interface for animal data access operations"""
    
    @abstractmethod
    def create(self, animal: Animal) -> Animal:
        """Create a new animal"""
        pass
    
    @abstractmethod
    def get(self, animal_id: str) -> Optional[Animal]:
        """Get animal by ID"""
        pass
    
    @abstractmethod
    def list(self, hide_soft_deleted: bool = True) -> List[Animal]:
        """List all animals"""
        pass
    
    @abstractmethod
    def update(self, animal: Animal) -> Animal:
        """Update existing animal"""
        pass
    
    @abstractmethod
    def soft_delete(self, animal_id: str) -> None:
        """Soft delete animal"""
        pass
    
    @abstractmethod
    def exists(self, animal_id: str) -> bool:
        """Check if animal exists"""
        pass