"""Lambda handlers that use domain services through hexagonal architecture"""
import json
from typing import Dict, Any
from ...domain.user_service import UserService
from ...domain.common.exceptions import (
    NotFoundError, ConflictError, ValidationError, 
    BusinessRuleError, InvalidStateError
)
from .serializers import LambdaUserSerializer, LambdaUserDetailsSerializer


class LambdaUserHandler:
    """Lambda event handler for user operations using domain service"""
    
    def __init__(self, user_service: UserService, user_serializer: LambdaUserSerializer, 
                 user_details_serializer: LambdaUserDetailsSerializer):
        self._user_service = user_service
        self._user_serializer = user_serializer
        self._user_details_serializer = user_details_serializer
    
    def create_user(self, event: Dict[str, Any], context) -> Dict[str, Any]:
        """
        Lambda handler for user creation
        
        Args:
            event: Lambda event dict
            context: Lambda context (unused)
            
        Returns:
            Lambda response dict with statusCode, headers, body
        """
        try:
            # Convert Lambda event to business dict
            user_data = self._user_serializer.from_lambda_event(event)
            
            # Execute business logic
            user = self._user_service.create_user(user_data)
            
            # Convert domain entity to Lambda response
            return self._user_serializer.to_lambda_response(user)
            
        except ValidationError as e:
            return self._create_error_response(400, "Validation error", str(e))
        except ConflictError as e:
            return self._create_error_response(409, "Conflict", str(e))
        except Exception as e:
            return self._create_error_response(500, "Internal server error", str(e))
    
    def get_user(self, event: Dict[str, Any], context) -> Dict[str, Any]:
        """
        Lambda handler for user retrieval
        
        Args:
            event: Lambda event dict with pathParameters.userId
            context: Lambda context (unused)
            
        Returns:
            Lambda response dict
        """
        try:
            # Extract user ID from path parameters
            path_params = event.get("pathParameters", {}) or {}
            user_id = path_params.get("userId") or path_params.get("id")
            
            if not user_id:
                return self._create_error_response(400, "Bad request", "Missing userId in path")
            
            # Execute business logic
            user = self._user_service.get_user(user_id)
            
            # Convert domain entity to Lambda response
            return self._user_serializer.to_lambda_response(user)
            
        except NotFoundError as e:
            return self._create_error_response(404, "Not found", str(e))
        except Exception as e:
            return self._create_error_response(500, "Internal server error", str(e))
    
    def list_users(self, event: Dict[str, Any], context) -> Dict[str, Any]:
        """
        Lambda handler for user listing
        
        Args:
            event: Lambda event dict with optional queryStringParameters
            context: Lambda context (unused)
            
        Returns:
            Lambda response dict
        """
        try:
            # Extract pagination parameters
            query_params = event.get("queryStringParameters") or {}
            page = None
            page_size = None
            
            if query_params.get("page"):
                try:
                    page = int(query_params["page"])
                except ValueError:
                    pass
            
            if query_params.get("pageSize"):
                try:
                    page_size = int(query_params["pageSize"])
                except ValueError:
                    pass
            
            # Execute business logic
            users = self._user_service.list_users(page, page_size)
            
            # Convert domain entities to response format
            from ...domain.common.serializers import serialize_user
            response_items = [serialize_user(user) for user in users]
            response_data = {"items": response_items}
            
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps(response_data)
            }
            
        except Exception as e:
            return self._create_error_response(500, "Internal server error", str(e))
    
    def update_user(self, event: Dict[str, Any], context) -> Dict[str, Any]:
        """
        Lambda handler for user update
        
        Args:
            event: Lambda event dict with pathParameters.userId and body
            context: Lambda context (unused)
            
        Returns:
            Lambda response dict
        """
        try:
            # Extract user ID from path parameters
            path_params = event.get("pathParameters", {}) or {}
            user_id = path_params.get("userId") or path_params.get("id")
            
            if not user_id:
                return self._create_error_response(400, "Bad request", "Missing userId in path")
            
            # Convert Lambda event to business dict
            update_data = self._user_serializer.from_lambda_event(event)
            
            # Execute business logic
            user = self._user_service.update_user(user_id, update_data)
            
            # Convert domain entity to Lambda response
            return self._user_serializer.to_lambda_response(user)
            
        except NotFoundError as e:
            return self._create_error_response(404, "Not found", str(e))
        except ValidationError as e:
            return self._create_error_response(400, "Validation error", str(e))
        except InvalidStateError as e:
            return self._create_error_response(400, "Invalid state", str(e))
        except Exception as e:
            return self._create_error_response(500, "Internal server error", str(e))
    
    def delete_user(self, event: Dict[str, Any], context) -> Dict[str, Any]:
        """
        Lambda handler for user soft deletion
        
        Args:
            event: Lambda event dict with pathParameters.userId
            context: Lambda context (unused)
            
        Returns:
            Lambda response dict
        """
        try:
            # Extract user ID from path parameters
            path_params = event.get("pathParameters", {}) or {}
            user_id = path_params.get("userId") or path_params.get("id")
            
            if not user_id:
                return self._create_error_response(400, "Bad request", "Missing userId in path")
            
            # Execute business logic
            self._user_service.soft_delete_user(user_id)
            
            return {
                "statusCode": 204,
                "headers": {
                    "Access-Control-Allow-Origin": "*"
                },
                "body": ""
            }
            
        except NotFoundError as e:
            return self._create_error_response(404, "Not found", str(e))
        except ValidationError as e:
            return self._create_error_response(400, "Validation error", str(e))
        except Exception as e:
            return self._create_error_response(500, "Internal server error", str(e))
    
    def create_user_details(self, event: Dict[str, Any], context) -> Dict[str, Any]:
        """
        Lambda handler for user details creation
        
        Args:
            event: Lambda event dict with body containing user details data
            context: Lambda context (unused)
            
        Returns:
            Lambda response dict
        """
        try:
            # Convert Lambda event to business dict
            details_data = self._user_details_serializer.from_lambda_event(event)
            
            # Execute business logic
            user_details = self._user_service.create_user_details(details_data)
            
            # Return success response
            response_data = {"title": f"User details created userId={user_details.user_id}"}
            
            return {
                "statusCode": 201,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps(response_data)
            }
            
        except ValidationError as e:
            return self._create_error_response(400, "Validation error", str(e))
        except ConflictError as e:
            return self._create_error_response(409, "Conflict", str(e))
        except NotFoundError as e:
            return self._create_error_response(404, "Not found", str(e))
        except Exception as e:
            return self._create_error_response(500, "Internal server error", str(e))
    
    def get_user_details(self, event: Dict[str, Any], context) -> Dict[str, Any]:
        """
        Lambda handler for user details retrieval
        
        Args:
            event: Lambda event dict with pathParameters.userId
            context: Lambda context (unused)
            
        Returns:
            Lambda response dict
        """
        try:
            # Extract user ID from path parameters
            path_params = event.get("pathParameters", {}) or {}
            user_id = path_params.get("userId") or path_params.get("id")
            
            if not user_id:
                return self._create_error_response(400, "Bad request", "Missing userId in path")
            
            # Execute business logic
            user_details = self._user_service.get_user_details_by_user_id(user_id)
            
            # Convert domain entity to Lambda response
            return self._user_details_serializer.to_lambda_response(user_details)
            
        except NotFoundError as e:
            return self._create_error_response(404, "Not found", str(e))
        except Exception as e:
            return self._create_error_response(500, "Internal server error", str(e))
    
    def list_user_details(self, event: Dict[str, Any], context) -> Dict[str, Any]:
        """
        Lambda handler for user details listing
        
        Args:
            event: Lambda event dict with optional queryStringParameters
            context: Lambda context (unused)
            
        Returns:
            Lambda response dict
        """
        try:
            # Extract pagination parameters
            query_params = event.get("queryStringParameters") or {}
            page = None
            page_size = None
            
            if query_params.get("page"):
                try:
                    page = int(query_params["page"])
                except ValueError:
                    pass
            
            if query_params.get("pageSize"):
                try:
                    page_size = int(query_params["pageSize"])
                except ValueError:
                    pass
            
            # Execute business logic
            details_list = self._user_service.list_user_details(page, page_size)
            
            # Convert domain entities to response format
            from ...domain.common.serializers import serialize_user_details
            response_data = [serialize_user_details(details) for details in details_list]
            
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps(response_data)
            }
            
        except Exception as e:
            return self._create_error_response(500, "Internal server error", str(e))
    
    def update_user_details(self, event: Dict[str, Any], context) -> Dict[str, Any]:
        """
        Lambda handler for user details update
        
        Args:
            event: Lambda event dict with pathParameters.userId and body
            context: Lambda context (unused)
            
        Returns:
            Lambda response dict
        """
        try:
            # Extract user ID from path parameters
            path_params = event.get("pathParameters", {}) or {}
            user_id = path_params.get("userId") or path_params.get("id")
            
            if not user_id:
                return self._create_error_response(400, "Bad request", "Missing userId in path")
            
            # Convert Lambda event to business dict
            update_data = self._user_details_serializer.from_lambda_event(event)
            
            # Execute business logic
            user_details = self._user_service.update_user_details_by_user_id(user_id, update_data)
            
            # Convert domain entity to Lambda response
            return self._user_details_serializer.to_lambda_response(user_details)
            
        except NotFoundError as e:
            return self._create_error_response(404, "Not found", str(e))
        except ValidationError as e:
            return self._create_error_response(400, "Validation error", str(e))
        except InvalidStateError as e:
            return self._create_error_response(400, "Invalid state", str(e))
        except Exception as e:
            return self._create_error_response(500, "Internal server error", str(e))
    
    def delete_user_details(self, event: Dict[str, Any], context) -> Dict[str, Any]:
        """
        Lambda handler for user details soft deletion
        
        Args:
            event: Lambda event dict with pathParameters.userId
            context: Lambda context (unused)
            
        Returns:
            Lambda response dict
        """
        try:
            # Extract user ID from path parameters
            path_params = event.get("pathParameters", {}) or {}
            user_id = path_params.get("userId") or path_params.get("id")
            
            if not user_id:
                return self._create_error_response(400, "Bad request", "Missing userId in path")
            
            # Execute business logic
            self._user_service.soft_delete_user_details_by_user_id(user_id)
            
            return {
                "statusCode": 204,
                "headers": {
                    "Access-Control-Allow-Origin": "*"
                },
                "body": ""
            }
            
        except NotFoundError as e:
            return self._create_error_response(404, "Not found", str(e))
        except ValidationError as e:
            return self._create_error_response(400, "Validation error", str(e))
        except Exception as e:
            return self._create_error_response(500, "Internal server error", str(e))
    
    def _create_error_response(self, status_code: int, error: str, detail: str) -> Dict[str, Any]:
        """Create standardized error response for Lambda"""
        error_data = {
            "error": error,
            "detail": detail
        }
        
        return {
            "statusCode": status_code,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps(error_data)
        }