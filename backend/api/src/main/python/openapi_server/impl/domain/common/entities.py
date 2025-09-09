"""Domain entities for authentication system"""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class AuthCredentials:
    """User authentication credentials"""
    username: str
    password: str
    email: Optional[str] = None
    display_name: Optional[str] = None
    register_if_new: bool = False


@dataclass
class AuthToken:
    """Authentication token information"""
    token: str
    token_type: str = "Bearer"
    expires_in: int = 3600
    expires_at: Optional[datetime] = None
    scope: Optional[str] = None
    refresh_token: Optional[str] = None


@dataclass
class AuthenticatedUser:
    """Authenticated user with session context"""
    user_id: str
    username: Optional[str] = None
    email: Optional[str] = None
    display_name: Optional[str] = None
    roles: Optional[List[str]] = None
    permissions: Optional[List[str]] = None
    is_verified: bool = False
    session_id: Optional[str] = None