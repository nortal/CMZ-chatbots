"""User domain service - Pure business logic for user operations"""
import uuid
from typing import List, Optional, Dict, Any, Tuple
from .common.entities import User, UserDetails
from .common.exceptions import (
    NotFoundError, ConflictError, ValidationError, 
    BusinessRuleError, InvalidStateError
)
from .common.validators import (
    validate_user_creation_data, validate_user_details_creation_data,
    validate_soft_delete_allowed, validate_update_allowed
)
from .common.audit import create_creation_audit, create_modification_audit, create_deletion_audit
from .common.serializers import deserialize_user, serialize_user, deserialize_user_details, serialize_user_details
from ..ports.repository import UserRepository, UserDetailsRepository
from ..ports.audit import AuditService


class UserService:
    """Pure business logic for user operations"""
    
    def __init__(self, user_repo: UserRepository, user_details_repo: UserDetailsRepository, audit_service: AuditService):
        self._user_repo = user_repo
        self._user_details_repo = user_details_repo
        self._audit_service = audit_service
    
    def create_user(self, user_data: Dict[str, Any]) -> User:
        """
        Create a new user with business logic validation
        
        Args:
            user_data: Dictionary containing user creation data
            
        Returns:
            User: Created user domain entity
            
        Raises:
            ValidationError: If user data is invalid
            ConflictError: If user already exists
        """
        # Business validation
        validate_user_creation_data(user_data)
        
        # Generate user ID if not provided
        user_id = user_data.get("userId")
        if not user_id:
            user_id = str(uuid.uuid4())
            user_data["userId"] = user_id
        
        # Check for conflicts
        if self._user_repo.exists(user_id):
            raise ConflictError(f"User already exists with ID: {user_id}")
        
        # Apply business defaults
        user_data.setdefault("userType", "none")
        user_data.setdefault("softDelete", False)
        
        # Create audit trail
        actor_data = self._audit_service.extract_actor_data(user_data)
        audit_stamps = self._audit_service.create_creation_audit(actor_data)
        
        # Merge audit data
        user_data.update({
            "created": audit_stamps["created"],
            "modified": audit_stamps["modified"],
            "deleted": None
        })
        
        # Convert to domain entity
        user = deserialize_user(user_data)
        
        # Persist through repository
        created_user = self._user_repo.create(user)
        
        return created_user
    
    def get_user(self, user_id: str) -> User:
        """
        Get user by ID with business logic
        
        Args:
            user_id: User identifier
            
        Returns:
            User: User domain entity
            
        Raises:
            NotFoundError: If user not found or soft deleted
        """
        user = self._user_repo.get(user_id)
        
        if not user:
            raise NotFoundError("User", user_id)
        
        # Business rule: soft deleted users are not accessible
        if user.soft_delete:
            raise NotFoundError("User", user_id)
        
        return user
    
    def list_users(self, page: Optional[int] = None, page_size: Optional[int] = None,
                   query: Optional[str] = None, role: Optional[str] = None) -> List[User]:
        """
        List users with business logic filtering

        Args:
            page: Page number (1-based)
            page_size: Items per page
            query: Search query for name or email
            role: Filter by specific role

        Returns:
            List[User]: List of user domain entities
        """
        # Get all non-deleted users
        users = self._user_repo.list(hide_soft_deleted=True)

        # Apply search filter if query provided
        if query:
            query_lower = query.lower()
            users = [
                user for user in users
                if (user.display_name and query_lower in user.display_name.lower()) or
                   (user.email and query_lower in user.email.lower())
            ]

        # Apply role filter if provided
        if role:
            users = [user for user in users if user.role == role]

        # Apply pagination if requested
        if page and page_size:
            start = (page - 1) * page_size
            end = start + page_size
            users = users[start:end]

        return users
    
    def update_user(self, user_id: str, update_data: Dict[str, Any]) -> User:
        """
        Update user with business logic validation
        
        Args:
            user_id: User identifier
            update_data: Dictionary containing update data
            
        Returns:
            User: Updated user domain entity
            
        Raises:
            NotFoundError: If user not found
            ValidationError: If update data is invalid
            InvalidStateError: If user cannot be updated
        """
        # Get current user
        current_user = self.get_user(user_id)  # This handles not found and soft delete
        current_data = serialize_user(current_user)
        
        # Business rule: cannot update soft deleted users
        validate_update_allowed(current_data, "User")
        
        # Validate role and user_type if provided
        if "role" in update_data and update_data["role"]:
            from .common.validators import validate_user_role
            validate_user_role(update_data["role"])
        
        if "userType" in update_data and update_data["userType"]:
            from .common.validators import validate_user_type
            validate_user_type(update_data["userType"])
        
        # Merge current data with updates
        merged_data = current_data.copy()
        merged_data.update(update_data)
        merged_data["userId"] = user_id  # Ensure ID consistency
        
        # Create modification audit
        actor_data = self._audit_service.extract_actor_data(update_data)
        audit_stamps = self._audit_service.create_modification_audit(actor_data)
        merged_data.update(audit_stamps)
        
        # Convert to domain entity
        updated_user = deserialize_user(merged_data)
        
        # Persist through repository
        saved_user = self._user_repo.update(updated_user)
        
        return saved_user
    
    def soft_delete_user(self, user_id: str, actor_data: Optional[Dict[str, Any]] = None) -> None:
        """
        Soft delete user with business logic
        
        Args:
            user_id: User identifier
            actor_data: Information about who is performing the deletion
            
        Raises:
            NotFoundError: If user not found
            ValidationError: If user already deleted
        """
        # Get current user
        current_user = self.get_user(user_id)  # This handles not found and soft delete
        current_data = serialize_user(current_user)
        
        # Business rule: cannot delete already deleted users
        validate_soft_delete_allowed(current_data, "User")
        
        # Mark as soft deleted
        current_data["softDelete"] = True
        
        # Create deletion audit
        audit_stamps = self._audit_service.create_deletion_audit(actor_data)
        current_data.update(audit_stamps)
        
        # Convert to domain entity and persist
        updated_user = deserialize_user(current_data)
        self._user_repo.update(updated_user)
        
        # Business rule: cascade soft delete to user details
        try:
            user_details = self._user_details_repo.get_by_user_id(user_id)
            if user_details and not user_details.soft_delete:
                self.soft_delete_user_details_by_user_id(user_id, actor_data)
        except NotFoundError:
            # No user details to cascade delete
            pass
    
    def create_user_details(self, user_details_data: Dict[str, Any]) -> UserDetails:
        """
        Create user details with business logic validation
        
        Args:
            user_details_data: Dictionary containing user details creation data
            
        Returns:
            UserDetails: Created user details domain entity
            
        Raises:
            ValidationError: If user details data is invalid
            ConflictError: If user details already exist for user
            NotFoundError: If referenced user doesn't exist
        """
        # Business validation
        validate_user_details_creation_data(user_details_data)
        
        user_id = user_details_data["userId"]
        
        # Business rule: referenced user must exist
        if not self._user_repo.exists(user_id):
            raise NotFoundError("User", user_id)
        
        # Business rule: one details record per user
        if self._user_details_repo.exists_for_user(user_id, hide_soft_deleted=True):
            raise ConflictError(f"User details already exist for user: {user_id}")
        
        # Generate details ID if not provided
        details_id = user_details_data.get("userDetailsId")
        if not details_id:
            details_id = str(uuid.uuid4())
            user_details_data["userDetailsId"] = details_id
        
        # Apply business defaults
        user_details_data.setdefault("softDelete", False)
        user_details_data.setdefault("extras", {})
        
        # Create audit trail
        actor_data = self._audit_service.extract_actor_data(user_details_data)
        audit_stamps = self._audit_service.create_creation_audit(actor_data)
        
        # Merge audit data
        user_details_data.update({
            "created": audit_stamps["created"],
            "modified": audit_stamps["modified"],
            "deleted": None
        })
        
        # Convert to domain entity
        user_details = deserialize_user_details(user_details_data)
        
        # Persist through repository
        created_details = self._user_details_repo.create(user_details)
        
        return created_details
    
    def get_user_details_by_user_id(self, user_id: str) -> UserDetails:
        """
        Get user details by user ID with business logic
        
        Args:
            user_id: User identifier
            
        Returns:
            UserDetails: User details domain entity
            
        Raises:
            NotFoundError: If user details not found or soft deleted
        """
        user_details = self._user_details_repo.get_by_user_id(user_id)
        
        if not user_details:
            raise NotFoundError("UserDetails", user_id)
        
        # Business rule: soft deleted details are not accessible
        if user_details.soft_delete:
            raise NotFoundError("UserDetails", user_id)
        
        return user_details
    
    def list_user_details(self, page: Optional[int] = None, page_size: Optional[int] = None) -> List[UserDetails]:
        """
        List user details with business logic filtering
        
        Args:
            page: Page number (1-based)
            page_size: Items per page
            
        Returns:
            List[UserDetails]: List of user details domain entities
        """
        # Get all non-deleted user details
        details_list = self._user_details_repo.list(hide_soft_deleted=True)
        
        # Apply pagination if requested
        if page and page_size:
            start = (page - 1) * page_size
            end = start + page_size
            details_list = details_list[start:end]
        
        return details_list
    
    def update_user_details_by_user_id(self, user_id: str, update_data: Dict[str, Any]) -> UserDetails:
        """
        Update user details by user ID with business logic validation
        
        Args:
            user_id: User identifier
            update_data: Dictionary containing update data
            
        Returns:
            UserDetails: Updated user details domain entity
            
        Raises:
            NotFoundError: If user details not found
            InvalidStateError: If user details cannot be updated
        """
        # Get current user details
        current_details = self.get_user_details_by_user_id(user_id)  # Handles not found and soft delete
        current_data = serialize_user_details(current_details)
        
        # Business rule: cannot update soft deleted details
        validate_update_allowed(current_data, "UserDetails")
        
        # Merge current data with updates
        merged_data = current_data.copy()
        merged_data.update(update_data)
        
        # Create modification audit
        actor_data = self._audit_service.extract_actor_data(update_data)
        audit_stamps = self._audit_service.create_modification_audit(actor_data)
        merged_data.update(audit_stamps)
        
        # Convert to domain entity
        updated_details = deserialize_user_details(merged_data)
        
        # Persist through repository
        saved_details = self._user_details_repo.update(updated_details)
        
        return saved_details
    
    def soft_delete_user_details_by_user_id(self, user_id: str, actor_data: Optional[Dict[str, Any]] = None) -> None:
        """
        Soft delete user details by user ID with business logic
        
        Args:
            user_id: User identifier
            actor_data: Information about who is performing the deletion
            
        Raises:
            NotFoundError: If user details not found
            ValidationError: If user details already deleted
        """
        # Get current user details
        current_details = self.get_user_details_by_user_id(user_id)  # Handles not found and soft delete
        current_data = serialize_user_details(current_details)
        
        # Business rule: cannot delete already deleted details
        validate_soft_delete_allowed(current_data, "UserDetails")
        
        # Mark as soft deleted
        current_data["softDelete"] = True
        
        # Create deletion audit
        audit_stamps = self._audit_service.create_deletion_audit(actor_data)
        current_data.update(audit_stamps)
        
        # Convert to domain entity and persist
        updated_details = deserialize_user_details(current_data)
        self._user_details_repo.update(updated_details)