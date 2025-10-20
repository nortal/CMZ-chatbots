"""Flask handlers that use domain services through hexagonal architecture"""
from typing import Tuple, Any, List
from ...domain.user_service import UserService
from ...domain.common.exceptions import (
    NotFoundError, ConflictError, ValidationError,
    BusinessRuleError, InvalidStateError
)
from ...domain.common.serializers import serialize_user_details
from .serializers import FlaskUserSerializer, FlaskUserDetailsSerializer


class FlaskUserHandler:
    """Flask route handler for user operations using domain service"""
    
    def __init__(self, user_service: UserService, user_serializer: FlaskUserSerializer, 
                 user_details_serializer: FlaskUserDetailsSerializer):
        self._user_service = user_service
        self._user_serializer = user_serializer
        self._user_details_serializer = user_details_serializer
    
    def create_user(self, body: Any) -> Tuple[Any, int]:
        """
        Flask handler for user creation
        
        Args:
            body: OpenAPI UserInput model or dict
            
        Returns:
            Tuple of (response_body, http_status_code)
        """
        try:
            # Convert OpenAPI model to business dict
            user_data = self._user_serializer.from_openapi(body)
            
            # Execute business logic
            user = self._user_service.create_user(user_data)
            
            # Convert domain entity to OpenAPI response
            response = self._user_serializer.to_openapi(user)
            
            return response, 201
            
        except ValidationError as e:
            return {"error": "Validation error", "detail": str(e)}, 400
        except ConflictError as e:
            return {"error": "Conflict", "detail": str(e)}, 409
        except Exception as e:
            return {"error": "Internal server error", "detail": str(e)}, 500
    
    def get_user(self, user_id: str) -> Tuple[Any, int]:
        """
        Flask handler for user retrieval
        
        Args:
            user_id: User identifier
            
        Returns:
            Tuple of (response_body, http_status_code)
        """
        try:
            # Execute business logic
            user = self._user_service.get_user(user_id)
            
            # Convert domain entity to OpenAPI response
            response = self._user_serializer.to_openapi(user)
            
            return response, 200
            
        except NotFoundError as e:
            return {"error": "Not found", "detail": str(e)}, 404
        except Exception as e:
            return {"error": "Internal server error", "detail": str(e)}, 500
    
    def list_users(self, page: int = None, page_size: int = None,
                   query: str = None, role: str = None) -> Tuple[Any, int]:
        """
        Flask handler for user listing

        Args:
            page: Page number (optional)
            page_size: Items per page (optional)
            query: Search query for name or email (optional)
            role: Filter by specific role (optional)

        Returns:
            Tuple of (response_body, http_status_code)
        """
        try:
            # Execute business logic
            users = self._user_service.list_users(page, page_size, query, role)
            
            # Convert domain entities to OpenAPI response
            response_items = []
            for user in users:
                user_dict = self._user_serializer.to_openapi(user)
                # Convert OpenAPI model back to dict for JSON response
                if hasattr(user_dict, "to_dict"):
                    response_items.append(user_dict.to_dict())
                else:
                    response_items.append(user_dict)
            
            # Return in PagedUsers format (matching existing pattern)
            response = {"items": response_items}
            
            return response, 200
            
        except Exception as e:
            return {"error": "Internal server error", "detail": str(e)}, 500
    
    def update_user(self, user_id: str, body: Any) -> Tuple[Any, int]:
        """
        Flask handler for user update
        
        Args:
            user_id: User identifier
            body: OpenAPI User model or dict with update data
            
        Returns:
            Tuple of (response_body, http_status_code)
        """
        try:
            # Convert OpenAPI model to business dict
            update_data = self._user_serializer.from_openapi(body)
            
            # Execute business logic
            user = self._user_service.update_user(user_id, update_data)
            
            # Convert domain entity to OpenAPI response
            response = self._user_serializer.to_openapi(user)
            
            return response, 200
            
        except NotFoundError as e:
            return {"error": "Not found", "detail": str(e)}, 404
        except ValidationError as e:
            return {"error": "Validation error", "detail": str(e)}, 400
        except InvalidStateError as e:
            return {"error": "Invalid state", "detail": str(e)}, 400
        except Exception as e:
            return {"error": "Internal server error", "detail": str(e)}, 500
    
    def delete_user(self, user_id: str) -> Tuple[None, int]:
        """
        Flask handler for user soft deletion
        
        Args:
            user_id: User identifier
            
        Returns:
            Tuple of (None, http_status_code)
        """
        try:
            # Execute business logic
            self._user_service.soft_delete_user(user_id)
            
            return None, 204
            
        except NotFoundError as e:
            return {"error": "Not found", "detail": str(e)}, 404
        except ValidationError as e:
            return {"error": "Validation error", "detail": str(e)}, 400
        except Exception as e:
            return {"error": "Internal server error", "detail": str(e)}, 500
    
    def create_user_details(self, body: Any) -> Tuple[Any, int]:
        """
        Flask handler for user details creation
        
        Args:
            body: OpenAPI UserDetailsInput model or dict
            
        Returns:
            Tuple of (response_body, http_status_code)
        """
        try:
            # Convert OpenAPI model to business dict
            details_data = self._user_details_serializer.from_openapi(body)
            
            # Execute business logic
            user_details = self._user_service.create_user_details(details_data)
            
            # Return success message (matching existing pattern)
            response = {"title": f"User details created userId={user_details.user_id}"}
            
            return response, 201
            
        except ValidationError as e:
            return {"error": "Validation error", "detail": str(e)}, 400
        except ConflictError as e:
            return {"title": "Conflict", "detail": str(e), "status": 409}, 409
        except NotFoundError as e:
            return {"error": "Not found", "detail": str(e)}, 404
        except Exception as e:
            return {"error": "Internal server error", "detail": str(e)}, 500
    
    def get_user_details(self, user_id: str) -> Tuple[Any, int]:
        """
        Flask handler for user details retrieval
        
        Args:
            user_id: User identifier
            
        Returns:
            Tuple of (response_body, http_status_code)
        """
        try:
            # Execute business logic
            user_details = self._user_service.get_user_details_by_user_id(user_id)

            # Convert domain entity to dict response (matching existing pattern)
            response = serialize_user_details(user_details)
            
            return response, 200
            
        except NotFoundError as e:
            return {"title": "Not Found", "detail": f"userId={user_id}", "status": 404}, 404
        except Exception as e:
            return {"title": "Server Error", "detail": "Failed to read user details", "status": 500}, 500
    
    def list_user_details(self, page: int = None, page_size: int = None) -> Tuple[List[Any], int]:
        """
        Flask handler for user details listing
        
        Args:
            page: Page number (optional)
            page_size: Items per page (optional)
            
        Returns:
            Tuple of (response_body, http_status_code)
        """
        try:
            # Execute business logic
            details_list = self._user_service.list_user_details(page, page_size)
            
            # Convert domain entities to response format
            response = [serialize_user_details(details) for details in details_list]
            
            return response, 200
            
        except Exception as e:
            return {"error": "Internal server error", "detail": str(e)}, 500
    
    def update_user_details(self, user_id: str, body: Any) -> Tuple[Any, int]:
        """
        Flask handler for user details update
        
        Args:
            user_id: User identifier
            body: OpenAPI UserDetailsInput model or dict with update data
            
        Returns:
            Tuple of (response_body, http_status_code)
        """
        try:
            # Convert OpenAPI model to business dict
            update_data = self._user_details_serializer.from_openapi(body)
            
            # Execute business logic
            user_details = self._user_service.update_user_details_by_user_id(user_id, update_data)
            
            # Convert domain entity to dict response
            response = serialize_user_details(user_details)
            
            return response, 200
            
        except NotFoundError as e:
            return {"title": "Not Found", "detail": f"userId={user_id}", "status": 404}, 404
        except ValidationError as e:
            return {"error": "Validation error", "detail": str(e)}, 400
        except InvalidStateError as e:
            return {"error": "Invalid state", "detail": str(e)}, 400
        except Exception as e:
            return {"title": "Server Error", "detail": "Failed to update user details", "status": 500}, 500
    
    def delete_user_details(self, user_id: str) -> Tuple[None, int]:
        """
        Flask handler for user details soft deletion
        
        Args:
            user_id: User identifier
            
        Returns:
            Tuple of (None, http_status_code)
        """
        try:
            # Execute business logic
            self._user_service.soft_delete_user_details_by_user_id(user_id)
            
            return None, 204
            
        except NotFoundError as e:
            return {"title": "Not Found", "detail": f"userId={user_id}", "status": 404}, 404
        except ValidationError as e:
            return {"error": "Validation error", "detail": str(e)}, 400
        except Exception as e:
            return {"title": "Server Error", "detail": "Failed to delete user details", "status": 500}, 500