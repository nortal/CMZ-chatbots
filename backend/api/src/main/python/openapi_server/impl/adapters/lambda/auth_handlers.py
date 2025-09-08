"""Lambda handlers for authentication operations using hexagonal architecture"""
import json
from typing import Any, Dict
from ...domain.auth_service import AuthenticationService
from ...domain.common.entities import AuthCredentials
from ...domain.common.exceptions import (
    NotFoundError, ConflictError, ValidationError, 
    BusinessRuleError, InvalidStateError
)
from .serializers import LambdaAuthSerializer


class LambdaAuthHandler:
    """Lambda event handler for authentication operations using domain service"""
    
    def __init__(self, auth_service: AuthenticationService, auth_serializer: LambdaAuthSerializer):
        self._auth_service = auth_service
        self._auth_serializer = auth_serializer
    
    def authenticate(self, event: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        Lambda handler for user authentication (login/register)
        
        Args:
            event: Lambda event containing authentication data
            context: Lambda context
            
        Returns:
            Lambda response with auth token or error
        """
        try:
            # Convert Lambda event to business entity
            auth_data = self._auth_serializer.from_lambda_event(event)
            credentials = AuthCredentials(**auth_data)
            
            # Execute business logic
            authenticated_user, auth_token = self._auth_service.authenticate_user(credentials)
            
            # Convert domain entities to Lambda response
            return self._auth_serializer.to_auth_response(authenticated_user, auth_token)
            
        except ValidationError as e:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Validation error", "detail": str(e)})
            }
        except ConflictError as e:
            return {
                "statusCode": 409,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Conflict", "detail": str(e)})
            }
        except NotFoundError as e:
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Not found", "detail": str(e)})
            }
        except BusinessRuleError as e:
            return {
                "statusCode": 401,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Authentication failed", "detail": str(e)})
            }
        except Exception as e:
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Internal server error", "detail": str(e)})
            }
    
    def refresh_token(self, event: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        Lambda handler for token refresh
        
        Args:
            event: Lambda event containing refresh token
            context: Lambda context
            
        Returns:
            Lambda response with new token or error
        """
        try:
            # Extract refresh token from event
            auth_data = self._auth_serializer.from_lambda_event(event)
            refresh_token = self._extract_token_from_event(event)
            
            if not refresh_token:
                return {
                    "statusCode": 401,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({"error": "Missing or invalid authorization header"})
                }
            
            # Execute business logic
            new_token = self._auth_service.refresh_token(refresh_token)
            
            # Convert to response
            return self._auth_serializer.to_token_response(new_token)
            
        except ValidationError as e:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Validation error", "detail": str(e)})
            }
        except BusinessRuleError as e:
            return {
                "statusCode": 401,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Token refresh failed", "detail": str(e)})
            }
        except NotFoundError as e:
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Session not found", "detail": str(e)})
            }
        except Exception as e:
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Internal server error", "detail": str(e)})
            }
    
    def logout(self, event: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        Lambda handler for user logout
        
        Args:
            event: Lambda event
            context: Lambda context
            
        Returns:
            Lambda response indicating logout success or error
        """
        try:
            # Extract and validate token
            token = self._extract_token_from_event(event)
            if not token:
                return {
                    "statusCode": 401,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({"error": "Not authenticated"})
                }
            
            # Validate token to get session info
            authenticated_user = self._auth_service.validate_token(token)
            session_id = authenticated_user.session_id
            
            if not session_id:
                return {
                    "statusCode": 400,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({"error": "No active session"})
                }
            
            # Execute business logic
            self._auth_service.logout(session_id)
            
            return {
                "statusCode": 204,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": ""
            }
            
        except ValidationError as e:
            return {
                "statusCode": 401,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Invalid token", "detail": str(e)})
            }
        except BusinessRuleError as e:
            return {
                "statusCode": 401,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Authentication failed", "detail": str(e)})
            }
        except NotFoundError as e:
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Session not found", "detail": str(e)})
            }
        except Exception as e:
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Internal server error", "detail": str(e)})
            }
    
    def initiate_password_reset(self, event: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        Lambda handler for password reset initiation
        
        Args:
            event: Lambda event containing email
            context: Lambda context
            
        Returns:
            Lambda response indicating reset initiation success
        """
        try:
            # Extract email from event
            reset_data = self._auth_serializer.from_lambda_event(event)
            email = reset_data.get('email')
            
            if not email:
                return {
                    "statusCode": 400,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({"error": "Email is required"})
                }
            
            # Execute business logic
            self._auth_service.initiate_password_reset(email)
            
            # Always return success for security (don't reveal if email exists)
            return {
                "statusCode": 204,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": ""
            }
            
        except ValidationError as e:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Validation error", "detail": str(e)})
            }
        except Exception as e:
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Internal server error", "detail": str(e)})
            }
    
    def reset_password(self, event: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        Lambda handler for password reset completion
        
        Args:
            event: Lambda event containing reset token and new password
            context: Lambda context
            
        Returns:
            Lambda response indicating reset completion success or error
        """
        try:
            # Extract reset data from event
            reset_data = self._auth_serializer.from_lambda_event(event)
            token = reset_data.get('token')
            new_password = reset_data.get('new_password')
            
            if not token or not new_password:
                return {
                    "statusCode": 400,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({"error": "Token and new password are required"})
                }
            
            # Execute business logic
            self._auth_service.reset_password(token, new_password)
            
            return {
                "statusCode": 204,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": ""
            }
            
        except ValidationError as e:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Validation error", "detail": str(e)})
            }
        except BusinessRuleError as e:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Password reset failed", "detail": str(e)})
            }
        except NotFoundError as e:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Invalid reset token", "detail": str(e)})
            }
        except Exception as e:
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Internal server error", "detail": str(e)})
            }
    
    def _extract_token_from_event(self, event: Dict[str, Any]) -> str:
        """Extract JWT token from Lambda event"""
        # Try Authorization header first
        headers = event.get('headers', {})
        auth_header = headers.get('Authorization') or headers.get('authorization', '')
        
        if auth_header.startswith('Bearer '):
            return auth_header[7:]  # Remove 'Bearer ' prefix
        
        # Try query parameter
        query_params = event.get('queryStringParameters', {}) or {}
        if 'token' in query_params:
            return query_params['token']
        
        return None


class LambdaAuthAuthorizer:
    """Lambda authorizer for API Gateway authentication"""
    
    def __init__(self, auth_service: AuthenticationService):
        self._auth_service = auth_service
    
    def authorize(self, event: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        Lambda authorizer function for API Gateway
        
        Args:
            event: Lambda authorizer event
            context: Lambda context
            
        Returns:
            IAM policy document allowing or denying access
        """
        try:
            # Extract token from event
            token = self._extract_token_from_authorizer_event(event)
            
            if not token:
                raise Exception("No token provided")
            
            # Validate token and get authenticated user
            authenticated_user = self._auth_service.validate_token(token)
            
            # Generate allow policy
            policy = self._generate_policy(
                authenticated_user.user_id,
                "Allow",
                event.get('methodArn', '*'),
                authenticated_user
            )
            
            return policy
            
        except Exception as e:
            # Generate deny policy for any authentication failure
            policy = self._generate_policy("user", "Deny", event.get('methodArn', '*'))
            return policy
    
    def authorize_with_permission(self, required_permission: str):
        """
        Create a Lambda authorizer with specific permission requirement
        
        Args:
            required_permission: Permission required for access
            
        Returns:
            Lambda authorizer function
        """
        def authorizer(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
            try:
                # Extract token from event
                token = self._extract_token_from_authorizer_event(event)
                
                if not token:
                    raise Exception("No token provided")
                
                # Validate token and get authenticated user
                authenticated_user = self._auth_service.validate_token(token)
                
                # Check permission
                if not self._auth_service.authorize_user(authenticated_user, required_permission):
                    raise Exception(f"Insufficient permissions: {required_permission}")
                
                # Generate allow policy
                policy = self._generate_policy(
                    authenticated_user.user_id,
                    "Allow",
                    event.get('methodArn', '*'),
                    authenticated_user
                )
                
                return policy
                
            except Exception as e:
                # Generate deny policy for any authentication/authorization failure
                policy = self._generate_policy("user", "Deny", event.get('methodArn', '*'))
                return policy
        
        return authorizer
    
    def _extract_token_from_authorizer_event(self, event: Dict[str, Any]) -> str:
        """Extract token from Lambda authorizer event"""
        # API Gateway authorizer event format
        token = event.get('authorizationToken', '')
        
        if token.startswith('Bearer '):
            return token[7:]  # Remove 'Bearer ' prefix
        
        return token
    
    def _generate_policy(self, principal_id: str, effect: str, resource: str, 
                        authenticated_user=None) -> Dict[str, Any]:
        """Generate IAM policy document for API Gateway"""
        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": effect,
                    "Resource": resource
                }
            ]
        }
        
        response = {
            "principalId": principal_id,
            "policyDocument": policy_document
        }
        
        # Add user context for downstream Lambda functions
        if authenticated_user:
            response["context"] = {
                "userId": authenticated_user.user_id,
                "username": authenticated_user.username,
                "email": authenticated_user.email or "",
                "roles": ",".join(authenticated_user.roles or []),
                "permissions": ",".join(authenticated_user.permissions or []),
                "sessionId": authenticated_user.session_id or "",
                "isVerified": str(authenticated_user.is_verified)
            }
        
        return response


def extract_user_from_lambda_context(event: Dict[str, Any]) -> Dict[str, Any]:
    """Extract authenticated user info from Lambda event context (set by authorizer)"""
    request_context = event.get('requestContext', {})
    authorizer = request_context.get('authorizer', {})
    
    return {
        "user_id": authorizer.get('userId', ''),
        "username": authorizer.get('username', ''),
        "email": authorizer.get('email', ''),
        "roles": authorizer.get('roles', '').split(',') if authorizer.get('roles') else [],
        "permissions": authorizer.get('permissions', '').split(',') if authorizer.get('permissions') else [],
        "session_id": authorizer.get('sessionId', ''),
        "is_verified": authorizer.get('isVerified', '').lower() == 'true'
    }