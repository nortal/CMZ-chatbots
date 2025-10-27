"""Authentication domain service using AWS Cognito for managed authentication"""
import boto3
import hashlib
import jwt
import secrets
import uuid
from botocore.exceptions import ClientError
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

from .common.entities import (
    AuthCredentials, AuthToken, AuthenticatedUser,
    PasswordResetToken, AuthSession
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
                 identity_pool_id: str, region: str, audit_service: AuditService):
        self._user_pool_id = user_pool_id
        self._client_id = client_id
        self._client_secret = client_secret
        self._identity_pool_id = identity_pool_id
        self._region = region
        self._audit_service = audit_service
        
        # Initialize Cognito clients
        self._cognito_idp = boto3.client('cognito-idp', region_name=region)
        self._cognito_identity = boto3.client('cognito-identity', region_name=region)
    
    def authenticate_user(self, credentials: AuthCredentials) -> Tuple[AuthenticatedUser, AuthToken]:
        """
        Authenticate user with username/password
        
        Args:
            credentials: Username and password credentials
            
        Returns:
            Tuple of authenticated user and auth token
            
        Raises:
            ValidationError: Invalid credentials format
            NotFoundError: User not found (when register=False)
            ConflictError: User exists (when register=True)
            BusinessRuleError: Authentication failed
        """
        self._validate_credentials(credentials)
        
        # Check if user exists
        existing_user = self._user_repo.find_by_username(credentials.username)
        
        if credentials.register:
            if existing_user:
                raise ConflictError(f"User with username '{credentials.username}' already exists")
            
            # Register new user
            user = self._register_user(credentials)
        else:
            if not existing_user:
                raise NotFoundError(f"User with username '{credentials.username}' not found")
            
            user = existing_user
            
            # Verify password
            if not self._verify_password(credentials.password, user.get("password_hash", "")):
                raise BusinessRuleError("Invalid username or password")
        
        # Create authenticated user
        authenticated_user = self._create_authenticated_user(user)
        
        # Generate tokens
        auth_token = self._generate_tokens(authenticated_user)
        
        # Create session
        session = self._create_session(authenticated_user, auth_token)
        authenticated_user.session_id = session.session_id
        
        # Update last login
        self._user_repo.update_last_login(authenticated_user.user_id)
        
        # Audit log
        self._audit_service.log_event("user_authenticated", {
            "user_id": authenticated_user.user_id,
            "username": authenticated_user.username,
            "session_id": session.session_id
        })
        
        return authenticated_user, auth_token
    
    def validate_token(self, token: str) -> AuthenticatedUser:
        """
        Validate JWT token and return authenticated user
        
        Args:
            token: JWT token to validate
            
        Returns:
            AuthenticatedUser with session context
            
        Raises:
            ValidationError: Invalid token format
            BusinessRuleError: Token expired or invalid
            NotFoundError: Session not found
        """
        try:
            # Decode JWT token
            payload = jwt.decode(token, self._jwt_secret, algorithms=[self._jwt_algorithm])
            
            # Extract claims
            user_id = payload.get("user_id")
            session_id = payload.get("session_id")
            
            if not user_id or not session_id:
                raise BusinessRuleError("Invalid token claims")
            
            # Validate session
            session = self._auth_repo.get_session(session_id)
            if not session or not session.is_active:
                raise NotFoundError("Session not found or inactive")
            
            if session.expires_at and datetime.utcnow() > session.expires_at:
                raise BusinessRuleError("Session expired")
            
            # Update last accessed
            session.last_accessed_at = datetime.utcnow()
            self._auth_repo.update_session(session)
            
            # Create authenticated user from session
            authenticated_user = AuthenticatedUser(
                user_id=session.user_id,
                username=session.username,
                email=session.email,
                roles=session.roles,
                permissions=session.permissions,
                session_id=session.session_id,
                is_verified=True
            )
            
            return authenticated_user
            
        except jwt.ExpiredSignatureError:
            raise BusinessRuleError("Token expired")
        except jwt.InvalidTokenError as e:
            raise ValidationError(f"Invalid token: {str(e)}")
    
    def refresh_token(self, refresh_token: str) -> AuthToken:
        """
        Refresh access token using refresh token
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New auth token
            
        Raises:
            ValidationError: Invalid refresh token
            BusinessRuleError: Refresh token expired
            NotFoundError: Session not found
        """
        try:
            # Decode refresh token
            payload = jwt.decode(refresh_token, self._jwt_secret, algorithms=[self._jwt_algorithm])
            
            session_id = payload.get("session_id")
            token_type = payload.get("type")
            
            if not session_id or token_type != "refresh":
                raise ValidationError("Invalid refresh token")
            
            # Get session
            session = self._auth_repo.get_session(session_id)
            if not session or not session.is_active:
                raise NotFoundError("Session not found or inactive")
            
            # Create authenticated user for token generation
            authenticated_user = AuthenticatedUser(
                user_id=session.user_id,
                username=session.username,
                email=session.email,
                roles=session.roles,
                permissions=session.permissions,
                session_id=session.session_id
            )
            
            # Generate new access token
            new_token = self._generate_tokens(authenticated_user)
            
            # Audit log
            self._audit_service.log_event("token_refreshed", {
                "user_id": session.user_id,
                "session_id": session.session_id
            })
            
            return new_token
            
        except jwt.ExpiredSignatureError:
            raise BusinessRuleError("Refresh token expired")
        except jwt.InvalidTokenError as e:
            raise ValidationError(f"Invalid refresh token: {str(e)}")
    
    def logout(self, session_id: str) -> None:
        """
        Logout user by invalidating session
        
        Args:
            session_id: Session to invalidate
            
        Raises:
            NotFoundError: Session not found
        """
        session = self._auth_repo.get_session(session_id)
        if not session:
            raise NotFoundError(f"Session {session_id} not found")
        
        # Deactivate session
        session.is_active = False
        self._auth_repo.update_session(session)
        
        # Audit log
        self._audit_service.log_event("user_logged_out", {
            "user_id": session.user_id,
            "session_id": session_id
        })
    
    def initiate_password_reset(self, email: str) -> PasswordResetToken:
        """
        Initiate password reset process
        
        Args:
            email: User email address
            
        Returns:
            Password reset token
            
        Raises:
            NotFoundError: User not found
            ValidationError: Invalid email format
        """
        self._validate_email(email)
        
        # Find user by email
        user = self._user_repo.find_by_email(email)
        if not user:
            raise NotFoundError(f"User with email '{email}' not found")
        
        # Generate reset token
        reset_token = PasswordResetToken(
            token_id=str(uuid.uuid4()),
            user_id=user["userId"],
            token=self._generate_reset_token(),
            expires_at=datetime.utcnow() + timedelta(hours=1),  # 1 hour expiry
            created_at=datetime.utcnow()
        )
        
        # Store reset token
        self._auth_repo.store_reset_token(reset_token)
        
        # Audit log
        self._audit_service.log_event("password_reset_initiated", {
            "user_id": user["userId"],
            "email": email,
            "token_id": reset_token.token_id
        })
        
        return reset_token
    
    def reset_password(self, token: str, new_password: str) -> None:
        """
        Reset user password using reset token
        
        Args:
            token: Password reset token
            new_password: New password
            
        Raises:
            ValidationError: Invalid token or password
            BusinessRuleError: Token expired or used
            NotFoundError: Token not found
        """
        self._validate_password(new_password)
        
        # Get reset token
        reset_token = self._auth_repo.get_reset_token(token)
        if not reset_token:
            raise NotFoundError("Invalid reset token")
        
        if reset_token.used:
            raise BusinessRuleError("Reset token already used")
        
        if datetime.utcnow() > reset_token.expires_at:
            raise BusinessRuleError("Reset token expired")
        
        # Hash new password
        password_hash = self._hash_password(new_password)
        
        # Update user password
        self._user_repo.update_password(reset_token.user_id, password_hash)
        
        # Mark token as used
        reset_token.used = True
        self._auth_repo.update_reset_token(reset_token)
        
        # Invalidate all user sessions
        self._auth_repo.invalidate_user_sessions(reset_token.user_id)
        
        # Audit log
        self._audit_service.log_event("password_reset_completed", {
            "user_id": reset_token.user_id,
            "token_id": reset_token.token_id
        })
    
    def authorize_user(self, authenticated_user: AuthenticatedUser, 
                      required_permission: str) -> bool:
        """
        Check if user has required permission
        
        Args:
            authenticated_user: User to check
            required_permission: Permission to validate
            
        Returns:
            True if user has permission
        """
        if not authenticated_user.permissions:
            return False
        
        # Check direct permission
        if required_permission in authenticated_user.permissions:
            return True
        
        # Check role-based permissions (simplified)
        if "admin" in (authenticated_user.roles or []):
            return True
        
        return False
    
    # Private helper methods
    
    def _validate_credentials(self, credentials: AuthCredentials) -> None:
        """Validate credentials format"""
        if not credentials.username or len(credentials.username.strip()) < 3:
            raise ValidationError("Username must be at least 3 characters")
        
        if not credentials.password or len(credentials.password) < 6:
            raise ValidationError("Password must be at least 6 characters")
        
        if credentials.register and credentials.email:
            self._validate_email(credentials.email)
    
    def _validate_email(self, email: str) -> None:
        """Validate email format"""
        if not email or "@" not in email or len(email) < 5:
            raise ValidationError("Invalid email format")
    
    def _validate_password(self, password: str) -> None:
        """Validate password strength"""
        if not password or len(password) < 6:
            raise ValidationError("Password must be at least 6 characters")
    
    def _register_user(self, credentials: AuthCredentials) -> Dict[str, Any]:
        """Register new user"""
        user_data = {
            "userId": str(uuid.uuid4()),
            "username": credentials.username.strip(),
            "email": credentials.email,
            "password_hash": self._hash_password(credentials.password),
            "is_verified": False,
            "roles": ["user"],  # Default role
            "created_at": datetime.utcnow().isoformat()
        }
        
        self._user_repo.create(user_data)
        return user_data
    
    def _hash_password(self, password: str) -> str:
        """Hash password with salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}:{password_hash.hex()}"
    
    def _verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify password against stored hash"""
        if not stored_hash or ":" not in stored_hash:
            return False
        
        salt, hash_hex = stored_hash.split(":", 1)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return password_hash.hex() == hash_hex
    
    def _create_authenticated_user(self, user: Dict[str, Any]) -> AuthenticatedUser:
        """Create authenticated user from user data"""
        return AuthenticatedUser(
            user_id=user["userId"],
            username=user["username"],
            email=user.get("email"),
            display_name=user.get("displayName"),
            roles=user.get("roles", []),
            permissions=user.get("permissions", []),
            is_verified=user.get("is_verified", False)
        )
    
    def _generate_tokens(self, user: AuthenticatedUser) -> AuthToken:
        """Generate JWT access and refresh tokens"""
        # Access token payload
        access_payload = {
            "user_id": user.user_id,
            "username": user.username,
            "session_id": user.session_id,
            "roles": user.roles,
            "permissions": user.permissions,
            "type": "access",
            "exp": datetime.utcnow() + timedelta(hours=1),  # 1 hour
            "iat": datetime.utcnow(),
            "iss": "cmz-chatbots"
        }
        
        # Refresh token payload
        refresh_payload = {
            "user_id": user.user_id,
            "session_id": user.session_id,
            "type": "refresh",
            "exp": datetime.utcnow() + timedelta(days=7),  # 7 days
            "iat": datetime.utcnow(),
            "iss": "cmz-chatbots"
        }
        
        # Generate tokens
        access_token = jwt.encode(access_payload, self._jwt_secret, algorithm=self._jwt_algorithm)
        refresh_token = jwt.encode(refresh_payload, self._jwt_secret, algorithm=self._jwt_algorithm)
        
        return AuthToken(
            token=access_token,
            token_type="Bearer",
            expires_in=3600,  # 1 hour
            refresh_token=refresh_token
        )
    
    def _create_session(self, user: AuthenticatedUser, token: AuthToken) -> AuthSession:
        """Create user session"""
        session = AuthSession(
            session_id=str(uuid.uuid4()),
            user_id=user.user_id,
            username=user.username,
            email=user.email,
            roles=user.roles,
            permissions=user.permissions,
            expires_at=token.expires_at,
            created_at=datetime.utcnow(),
            last_accessed_at=datetime.utcnow(),
            is_active=True
        )
        
        self._auth_repo.create_session(session)
        return session
    
    def _generate_reset_token(self) -> str:
        """Generate secure password reset token"""
        return secrets.token_urlsafe(32)