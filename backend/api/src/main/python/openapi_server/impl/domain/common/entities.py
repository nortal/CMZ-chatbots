from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime


@dataclass
class AuditStamp:
    """Domain representation of audit information"""
    at: str
    by: Optional['AuditBy'] = None


@dataclass
class AuditBy:
    """Domain representation of audit actor"""
    user_id: Optional[str] = None
    email: Optional[str] = None
    display_name: Optional[str] = None


@dataclass
class User:
    """Domain entity for User"""
    user_id: str
    email: str
    display_name: Optional[str] = None
    role: Optional[str] = None
    user_type: str = "none"
    family_id: Optional[str] = None
    soft_delete: bool = False
    created: Optional[AuditStamp] = None
    modified: Optional[AuditStamp] = None
    deleted: Optional[AuditStamp] = None


@dataclass
class UsageSummary:
    """Domain entity for usage tracking"""
    user_id: Optional[str] = None
    total_sessions: Optional[int] = None
    total_turns: Optional[int] = None
    last_active: Optional[datetime] = None


@dataclass
class UserDetails:
    """Domain entity for User Details"""
    user_details_id: str
    user_id: str
    usage: Optional[UsageSummary] = None
    extras: Optional[Dict[str, Any]] = field(default_factory=dict)
    soft_delete: bool = False
    created: Optional[AuditStamp] = None
    modified: Optional[AuditStamp] = None
    deleted: Optional[AuditStamp] = None


@dataclass
class Family:
    """Domain entity for Family"""
    family_id: str
    name: Optional[str] = None
    description: Optional[str] = None
    soft_delete: bool = False
    created: Optional[AuditStamp] = None
    modified: Optional[AuditStamp] = None
    deleted: Optional[AuditStamp] = None


@dataclass
class Animal:
    """Domain entity for Animal chatbot"""
    animal_id: str
    name: str
    species: Optional[str] = None
    status: Optional[str] = "active"
    personality: Optional[Dict[str, Any]] = field(default_factory=dict)
    configuration: Optional[Dict[str, Any]] = field(default_factory=dict)
    soft_delete: bool = False
    created: Optional[AuditStamp] = None
    modified: Optional[AuditStamp] = None
    deleted: Optional[AuditStamp] = None


@dataclass
class AnimalConfig:
    """Domain entity for Animal Configuration"""
    animal_id: str
    voice: Optional[str] = "default"
    personality: Optional[str] = None
    ai_model: Optional[str] = "claude-3-sonnet"
    temperature: float = 0.7
    top_p: float = 1.0
    tools_enabled: Optional[List[str]] = field(default_factory=list)
    guardrails: Optional[Dict[str, Any]] = field(default_factory=dict)
    status: Optional[str] = "active"
    soft_delete: bool = False
    created: Optional[AuditStamp] = None
    modified: Optional[AuditStamp] = None
    deleted: Optional[AuditStamp] = None


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