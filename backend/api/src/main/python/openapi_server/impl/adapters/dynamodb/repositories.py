"""DynamoDB repository implementations"""
from typing import List, Optional
from ...ports.repository import UserRepository, UserDetailsRepository, FamilyRepository, AnimalRepository
from ...domain.common.entities import User, UserDetails, Family, Animal
from ...domain.common.serializers import (
    serialize_user, deserialize_user, serialize_user_details, deserialize_user_details,
    serialize_family, deserialize_family, serialize_animal, deserialize_animal
)
from ...domain.common.exceptions import ConflictError
from ...utils.orm.store import DynamoStore
from botocore.exceptions import ClientError


class DynamoUserRepository(UserRepository):
    """DynamoDB implementation of UserRepository"""
    
    def __init__(self, store: DynamoStore):
        self._store = store
    
    def create(self, user: User) -> User:
        """Create a new user in DynamoDB"""
        user_data = serialize_user(user)
        
        try:
            self._store.create(user_data)
        except ClientError as e:
            if e.response.get("Error", {}).get("Code") == "ConditionalCheckFailedException":
                raise ConflictError(f"User already exists: {user.user_id}")
            raise
        
        return user
    
    def get(self, user_id: str) -> Optional[User]:
        """Get user by ID from DynamoDB"""
        user_data = self._store.get(user_id)
        if not user_data:
            return None
        
        return deserialize_user(user_data)
    
    def list(self, hide_soft_deleted: bool = True) -> List[User]:
        """List all users from DynamoDB"""
        user_data_list = self._store.list(hide_soft_deleted=hide_soft_deleted)
        return [deserialize_user(data) for data in user_data_list]
    
    def update(self, user: User) -> User:
        """Update existing user in DynamoDB"""
        user_data = serialize_user(user)
        self._store.update_fields(user.user_id, user_data)
        return user
    
    def soft_delete(self, user_id: str) -> None:
        """Soft delete user in DynamoDB"""
        self._store.soft_delete(user_id, soft_field="softDelete")
    
    def exists(self, user_id: str) -> bool:
        """Check if user exists in DynamoDB"""
        return self._store.get(user_id) is not None


class DynamoUserDetailsRepository(UserDetailsRepository):
    """DynamoDB implementation of UserDetailsRepository"""
    
    def __init__(self, store: DynamoStore, gsi_attr_name: str = "GSI_userId"):
        self._store = store
        self._gsi_attr_name = gsi_attr_name
    
    def create(self, user_details: UserDetails) -> UserDetails:
        """Create new user details in DynamoDB"""
        details_data = serialize_user_details(user_details)
        
        try:
            self._store.create(details_data)
        except ClientError as e:
            if e.response.get("Error", {}).get("Code") == "ConditionalCheckFailedException":
                raise ConflictError(f"User details already exist: {user_details.user_details_id}")
            raise
        
        return user_details
    
    def get_by_user_id(self, user_id: str) -> Optional[UserDetails]:
        """Get user details by user ID using GSI"""
        try:
            results = self._store.query_gsi(self._gsi_attr_name, user_id, limit=1)
            if not results:
                return None
            
            # Convert PynamoDB model to dict using to_details_dict method
            if hasattr(results[0], "to_details_dict"):
                details_data = results[0].to_details_dict()
            else:
                # Fallback to attribute_values
                details_data = results[0].attribute_values
            
            return deserialize_user_details(details_data)
        except Exception:
            return None
    
    def list(self, hide_soft_deleted: bool = True) -> List[UserDetails]:
        """List all user details from DynamoDB"""
        details_data_list = self._store.list(hide_soft_deleted=hide_soft_deleted)
        return [deserialize_user_details(data) for data in details_data_list]
    
    def update(self, user_details: UserDetails) -> UserDetails:
        """Update existing user details in DynamoDB"""
        details_data = serialize_user_details(user_details)
        self._store.update_fields(user_details.user_details_id, details_data)
        return user_details
    
    def soft_delete(self, user_id: str) -> None:
        """Soft delete user details by user ID using GSI"""
        # Find details by user ID first
        results = self._store.query_gsi(self._gsi_attr_name, user_id, limit=10)
        
        for details_model in results:
            # Get the primary key
            if hasattr(details_model, "to_details_dict"):
                details_data = details_model.to_details_dict()
                details_id = details_data["userDetailsId"]
            else:
                details_id = getattr(details_model, "userDetailsId")
            
            self._store.soft_delete(details_id, soft_field="softDelete")
    
    def exists_for_user(self, user_id: str, hide_soft_deleted: bool = True) -> bool:
        """Check if user details exist for user ID using GSI"""
        return self._store.exists_on_gsi(self._gsi_attr_name, user_id, hide_soft_deleted=hide_soft_deleted)


class DynamoFamilyRepository(FamilyRepository):
    """DynamoDB implementation of FamilyRepository"""
    
    def __init__(self, store: DynamoStore):
        self._store = store
    
    def create(self, family: Family) -> Family:
        """Create a new family in DynamoDB"""
        family_data = serialize_family(family)
        
        try:
            self._store.create(family_data)
        except ClientError as e:
            if e.response.get("Error", {}).get("Code") == "ConditionalCheckFailedException":
                raise ConflictError(f"Family already exists: {family.family_id}")
            raise
        
        return family
    
    def get(self, family_id: str) -> Optional[Family]:
        """Get family by ID from DynamoDB"""
        family_data = self._store.get(family_id)
        if not family_data:
            return None
        
        return deserialize_family(family_data)
    
    def list(self, hide_soft_deleted: bool = True) -> List[Family]:
        """List all families from DynamoDB"""
        family_data_list = self._store.list(hide_soft_deleted=hide_soft_deleted)
        return [deserialize_family(data) for data in family_data_list]
    
    def update(self, family: Family) -> Family:
        """Update existing family in DynamoDB"""
        family_data = serialize_family(family)
        self._store.update_fields(family.family_id, family_data)
        return family
    
    def soft_delete(self, family_id: str) -> None:
        """Soft delete family in DynamoDB"""
        self._store.soft_delete(family_id, soft_field="softDelete")
    
    def exists(self, family_id: str) -> bool:
        """Check if family exists in DynamoDB"""
        return self._store.get(family_id) is not None


class DynamoAnimalRepository(AnimalRepository):
    """DynamoDB implementation of AnimalRepository"""
    
    def __init__(self, store: DynamoStore):
        self._store = store
    
    def create(self, animal: Animal) -> Animal:
        """Create a new animal in DynamoDB"""
        animal_data = serialize_animal(animal, include_api_id=False)
        
        try:
            self._store.create(animal_data)
        except ClientError as e:
            if e.response.get("Error", {}).get("Code") == "ConditionalCheckFailedException":
                raise ConflictError(f"Animal already exists: {animal.animal_id}")
            raise
        
        return animal
    
    def get(self, animal_id: str) -> Optional[Animal]:
        """Get animal by ID from DynamoDB"""
        animal_data = self._store.get(animal_id)
        if not animal_data:
            return None
        
        return deserialize_animal(animal_data)
    
    def list(self, hide_soft_deleted: bool = True) -> List[Animal]:
        """List all animals from DynamoDB"""
        animal_data_list = self._store.list(hide_soft_deleted=hide_soft_deleted)
        return [deserialize_animal(data) for data in animal_data_list]
    
    def update(self, animal: Animal) -> Animal:
        """Update existing animal in DynamoDB"""
        animal_data = serialize_animal(animal, include_api_id=False)
        self._store.update_fields(animal.animal_id, animal_data)
        return animal
    
    def soft_delete(self, animal_id: str) -> None:
        """Soft delete animal in DynamoDB"""
        self._store.soft_delete(animal_id, soft_field="softDelete")
    
    def exists(self, animal_id: str) -> bool:
        """Check if animal exists in DynamoDB"""
        return self._store.get(animal_id) is not None