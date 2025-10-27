"""Authentication domain service using AWS Cognito for managed authentication"""
import base64
import hashlib
import hmac
import json
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime

import boto3
from botocore.exceptions import ClientError
import jwt

from .common.entities import (
    AuthCredentials, AuthToken, AuthenticatedUser
)
from .common.exceptions import (
    ValidationError, NotFoundError, ConflictError, 
    BusinessRuleError, InvalidStateError
)
from ..ports.audit import AuditService


class CognitoAuthenticationService:
    """
    Domain service for authentication using AWS Cognito
    
    Provides business logic for:
    - User authentication via Cognito User Pool
    - User registration with Cognito
    - Token validation and refresh
    - Password reset through Cognito
    - Role-based authorization with Cognito groups
    """
    
    def __init__(self, user_pool_id: str, client_id: str, client_secret: Optional[str],
                 identity_pool_id: Optional[str], region: str, audit_service: AuditService):
        self._user_pool_id = user_pool_id
        self._client_id = client_id
        self._client_secret = client_secret
        self._identity_pool_id = identity_pool_id
        self._region = region
        self._audit_service = audit_service
        
        # Initialize Cognito clients
        self._cognito_idp = boto3.client('cognito-idp', region_name=region)
        self._cognito_identity = boto3.client('cognito-identity', region_name=region) if identity_pool_id else None
    
    def authenticate_user(self, credentials: AuthCredentials) -> Tuple[AuthenticatedUser, AuthToken]:
        """
        Authenticate user with Cognito User Pool
        
        Args:
            credentials: Username and password credentials
            
        Returns:
            Tuple of authenticated user and auth token
            
        Raises:
            ValidationError: Invalid credentials format
            BusinessRuleError: Authentication failed
        """
        self._validate_credentials(credentials)
        
        try:
            # Handle registration if requested
            if getattr(credentials, 'register_if_new', False):
                return self._register_and_authenticate(credentials)
            
            # Authenticate with Cognito
            auth_params = {
                'USERNAME': credentials.username,
                'PASSWORD': credentials.password
            }
            
            # Add SECRET_HASH if client secret is configured
            if self._client_secret:
                auth_params['SECRET_HASH'] = self._calculate_secret_hash(credentials.username)
            
            response = self._cognito_idp.initiate_auth(
                ClientId=self._client_id,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters=auth_params
            )
            
            # Handle authentication challenges (MFA, etc.)
            if 'ChallengeName' in response:
                raise BusinessRuleError(f"Authentication challenge required: {response['ChallengeName']}")
            
            # Extract tokens from response
            auth_result = response['AuthenticationResult']
            access_token = auth_result['AccessToken']
            id_token = auth_result['IdToken']
            refresh_token = auth_result.get('RefreshToken')
            
            # Get user info from access token
            user_info = self._get_user_from_token(access_token)
            
            # Create authenticated user entity
            authenticated_user = AuthenticatedUser(
                user_id=user_info['sub'],
                username=user_info.get('cognito:username', credentials.username),
                email=user_info.get('email'),
                display_name=user_info.get('name') or user_info.get('cognito:username'),
                roles=self._extract_cognito_groups(user_info),
                permissions=self._get_permissions_from_groups(user_info),
                is_verified=user_info.get('email_verified', 'false').lower() == 'true',
                session_id=None
            )
            
            # Create auth token entity
            auth_token = AuthToken(
                token=access_token,
                token_type="Bearer",
                expires_in=auth_result.get('ExpiresIn', 3600),
                refresh_token=refresh_token,
                scope="aws.cognito.signin.user.admin"
            )
            
            # Audit successful login
            self._audit_service.log_event(
                event_type="authentication",
                user_id=authenticated_user.user_id,
                details={"action": "login", "method": "cognito", "client_id": self._client_id}
            )
            
            return authenticated_user, auth_token
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NotAuthorizedException':
                raise BusinessRuleError("Invalid username or password")
            elif error_code == 'UserNotFoundException':
                raise BusinessRuleError("Invalid username or password")
            elif error_code == 'UserNotConfirmedException':
                raise BusinessRuleError("User account not confirmed. Please check your email.")
            elif error_code == 'TooManyRequestsException':
                raise BusinessRuleError("Too many requests. Please try again later.")
            else:
                raise BusinessRuleError(f"Authentication failed: {e.response['Error']['Message']}")
    
    def _register_and_authenticate(self, credentials: AuthCredentials) -> Tuple[AuthenticatedUser, AuthToken]:
        """
        Register new user with Cognito and authenticate
        
        Args:
            credentials: User credentials with registration info
            
        Returns:
            Tuple of authenticated user and auth token
        """
        try:
            # Prepare user attributes
            user_attributes = [
                {'Name': 'email', 'Value': credentials.email or credentials.username}
            ]
            
            if getattr(credentials, 'display_name', None):
                user_attributes.append({'Name': 'name', 'Value': credentials.display_name})
            
            # Add SECRET_HASH if client secret is configured
            signup_params = {
                'ClientId': self._client_id,
                'Username': credentials.username,
                'Password': credentials.password,
                'UserAttributes': user_attributes
            }
            
            if self._client_secret:
                signup_params['SecretHash'] = self._calculate_secret_hash(credentials.username)
            
            # Register user with Cognito
            response = self._cognito_idp.sign_up(**signup_params)
            
            # If user needs confirmation, return appropriate message
            if not response.get('UserConfirmed', False):
                # For now, we'll proceed with authentication assuming auto-confirmation
                # In production, you'd handle the confirmation flow
                pass
            
            # Now authenticate the newly registered user
            credentials.register_if_new = False
            return self.authenticate_user(credentials)
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'UsernameExistsException':
                # User already exists, try authentication
                credentials.register_if_new = False
                return self.authenticate_user(credentials)
            elif error_code == 'InvalidPasswordException':
                raise ValidationError(f"Password does not meet requirements: {e.response['Error']['Message']}")
            else:
                raise BusinessRuleError(f"Registration failed: {e.response['Error']['Message']}")
    
    def validate_token(self, token: str) -> AuthenticatedUser:
        """
        Validate Cognito access token and return authenticated user
        
        Args:
            token: Cognito access token to validate
            
        Returns:
            AuthenticatedUser with claims from token
            
        Raises:
            ValidationError: Invalid token format
            BusinessRuleError: Token expired or invalid
        """
        try:
            # Get user info from token (this validates the token)
            user_info = self._get_user_from_token(token)
            
            # Create authenticated user from token claims
            authenticated_user = AuthenticatedUser(
                user_id=user_info['sub'],
                username=user_info.get('cognito:username'),
                email=user_info.get('email'),
                display_name=user_info.get('name') or user_info.get('cognito:username'),
                roles=self._extract_cognito_groups(user_info),
                permissions=self._get_permissions_from_groups(user_info),
                is_verified=user_info.get('email_verified', 'false').lower() == 'true',
                session_id=None
            )
            
            return authenticated_user
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NotAuthorizedException':
                raise BusinessRuleError("Token is invalid or expired")
            else:
                raise BusinessRuleError(f"Token validation failed: {e.response['Error']['Message']}")
    
    def refresh_token(self, refresh_token: str, username: str) -> AuthToken:
        """
        Refresh Cognito tokens using refresh token
        
        Args:
            refresh_token: Cognito refresh token
            username: Username for secret hash calculation
            
        Returns:
            New AuthToken with refreshed access token
            
        Raises:
            BusinessRuleError: Token refresh failed
        """
        try:
            auth_params = {
                'REFRESH_TOKEN': refresh_token
            }
            
            if self._client_secret:
                auth_params['SECRET_HASH'] = self._calculate_secret_hash(username)
            
            response = self._cognito_idp.initiate_auth(
                ClientId=self._client_id,
                AuthFlow='REFRESH_TOKEN_AUTH',
                AuthParameters=auth_params
            )
            
            auth_result = response['AuthenticationResult']
            
            return AuthToken(
                token=auth_result['AccessToken'],
                token_type="Bearer",
                expires_in=auth_result.get('ExpiresIn', 3600),
                refresh_token=auth_result.get('RefreshToken', refresh_token),  # May return new refresh token
                scope="aws.cognito.signin.user.admin"
            )
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NotAuthorizedException':
                raise BusinessRuleError("Refresh token is invalid or expired")
            else:
                raise BusinessRuleError(f"Token refresh failed: {e.response['Error']['Message']}")
    
    def logout(self, access_token: str) -> None:
        """
        Log out user by invalidating tokens
        
        Args:
            access_token: User's access token
            
        Raises:
            BusinessRuleError: Logout failed
        """
        try:
            # Global sign out - invalidates all tokens for the user
            self._cognito_idp.global_sign_out(
                AccessToken=access_token
            )
            
        except ClientError as e:
            # Don't fail logout - log the error but continue
            self._audit_service.log_event(
                event_type="logout_error",
                user_id="unknown",
                details={"error": str(e)}
            )
    
    def initiate_password_reset(self, username: str) -> None:
        """
        Initiate password reset through Cognito
        
        Args:
            username: Username or email for password reset
        """
        try:
            forgot_password_params = {
                'ClientId': self._client_id,
                'Username': username
            }
            
            if self._client_secret:
                forgot_password_params['SecretHash'] = self._calculate_secret_hash(username)
            
            self._cognito_idp.forgot_password(**forgot_password_params)
            
            # Always succeed for security - don't reveal if user exists
            
        except ClientError as e:
            # Log error but don't expose to user
            self._audit_service.log_event(
                event_type="password_reset_error",
                user_id="unknown",
                details={"username": username, "error": str(e)}
            )
    
    def reset_password(self, username: str, confirmation_code: str, new_password: str) -> None:
        """
        Complete password reset with confirmation code
        
        Args:
            username: Username for password reset
            confirmation_code: Code from email/SMS
            new_password: New password to set
            
        Raises:
            BusinessRuleError: Password reset failed
        """
        try:
            confirm_params = {
                'ClientId': self._client_id,
                'Username': username,
                'ConfirmationCode': confirmation_code,
                'Password': new_password
            }
            
            if self._client_secret:
                confirm_params['SecretHash'] = self._calculate_secret_hash(username)
            
            self._cognito_idp.confirm_forgot_password(**confirm_params)
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'CodeMismatchException':
                raise BusinessRuleError("Invalid confirmation code")
            elif error_code == 'ExpiredCodeException':
                raise BusinessRuleError("Confirmation code has expired")
            elif error_code == 'InvalidPasswordException':
                raise ValidationError(f"Password does not meet requirements: {e.response['Error']['Message']}")
            else:
                raise BusinessRuleError(f"Password reset failed: {e.response['Error']['Message']}")
    
    def authorize_user(self, user: AuthenticatedUser, required_permission: str) -> bool:
        """
        Check if user has required permission
        
        Args:
            user: Authenticated user
            required_permission: Required permission string
            
        Returns:
            True if user has permission
        """
        if not user.permissions:
            return False
        
        # Check exact permission match
        if required_permission in user.permissions:
            return True
        
        # Check wildcard permissions
        for permission in user.permissions:
            if permission.endswith('*'):
                if required_permission.startswith(permission[:-1]):
                    return True
        
        return False
    
    def _get_user_from_token(self, access_token: str) -> Dict[str, Any]:
        """Get user information from Cognito access token"""
        response = self._cognito_idp.get_user(AccessToken=access_token)
        
        # Convert attributes to dict
        user_info = {'sub': response['UserSub']}
        for attr in response.get('UserAttributes', []):
            user_info[attr['Name']] = attr['Value']
        
        return user_info
    
    def _extract_cognito_groups(self, user_info: Dict[str, Any]) -> List[str]:
        """Extract Cognito groups from user info"""
        groups_str = user_info.get('cognito:groups', '')
        if not groups_str:
            return ['user']  # Default role
        
        # Groups are comma-separated in cognito:groups attribute
        return groups_str.split(',') if groups_str else ['user']
    
    def _get_permissions_from_groups(self, user_info: Dict[str, Any]) -> List[str]:
        """Map Cognito groups to permissions"""
        groups = self._extract_cognito_groups(user_info)
        
        # Define group to permission mappings
        group_permissions = {
            'admin': ['*'],  # All permissions
            'educator': ['animals:read', 'families:*', 'conversations:*'],
            'parent': ['families:read', 'conversations:read'],
            'student': ['animals:read', 'conversations:read'],
            'user': ['animals:read']  # Default permissions
        }
        
        permissions = set()
        for group in groups:
            permissions.update(group_permissions.get(group, ['animals:read']))
        
        return list(permissions)
    
    def _calculate_secret_hash(self, username: str) -> str:
        """Calculate SECRET_HASH for Cognito client secret"""
        if not self._client_secret:
            return None
        
        message = username + self._client_id
        secret_hash = hmac.new(
            self._client_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).digest()
        
        return base64.b64encode(secret_hash).decode('utf-8')
    
    def _validate_credentials(self, credentials: AuthCredentials) -> None:
        """Validate credential format"""
        if not credentials.username or len(credentials.username.strip()) == 0:
            raise ValidationError("Username is required")
        
        if not credentials.password or len(credentials.password) < 8:
            raise ValidationError("Password must be at least 8 characters")
        
        # Basic email validation if email is provided
        if getattr(credentials, 'email', None):
            if '@' not in credentials.email or '.' not in credentials.email:
                raise ValidationError("Invalid email format")