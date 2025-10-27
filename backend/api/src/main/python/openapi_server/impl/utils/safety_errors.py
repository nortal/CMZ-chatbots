"""
Error handling patterns for CMZ Chatbots safety violations and edge cases.

This module provides standardized error handling for:
- Content moderation failures and violations
- Guardrails enforcement errors
- Context summarization failures
- Privacy compliance violations
- OpenAI API errors and rate limiting
- DynamoDB operation failures in safety contexts

Features:
- Structured error responses with user-friendly messages
- Automatic error logging and audit trail
- Escalation patterns for critical safety violations
- Graceful degradation strategies
- COPPA-compliant error handling for child users
"""

import os
import json
import logging
import traceback
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from functools import wraps

from .safety_dynamo import create_audit_log, SafetyTableName

# Configure logging
logger = logging.getLogger(__name__)


class SafetyErrorType(Enum):
    """Categories of safety-related errors."""
    CONTENT_VIOLATION = "content_violation"
    MODERATION_FAILURE = "moderation_failure"
    GUARDRAILS_BREACH = "guardrails_breach"
    PRIVACY_VIOLATION = "privacy_violation"
    CONTEXT_FAILURE = "context_failure"
    API_RATE_LIMIT = "api_rate_limit"
    API_TIMEOUT = "api_timeout"
    DATABASE_ERROR = "database_error"
    CONFIGURATION_ERROR = "configuration_error"
    UNKNOWN_ERROR = "unknown_error"


class SafetySeverity(Enum):
    """Severity levels for safety errors."""
    CRITICAL = "critical"    # Immediate action required, potential harm to users
    HIGH = "high"           # Significant safety concern, requires prompt attention
    MEDIUM = "medium"       # Moderate safety issue, should be addressed
    LOW = "low"            # Minor issue, can be handled gracefully
    INFO = "info"          # Informational, no immediate action needed


@dataclass
class SafetyError:
    """Structured safety error with context and recommendations."""
    error_type: SafetyErrorType
    severity: SafetySeverity
    message: str
    user_message: str
    context: Dict[str, Any]
    recommendations: List[str]
    should_block_content: bool
    should_escalate: bool
    error_code: str
    timestamp: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    animal_id: Optional[str] = None
    trace_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging and API responses."""
        return asdict(self)

    def to_api_response(self) -> Dict[str, Any]:
        """Convert to user-safe API response format."""
        return {
            "error": True,
            "errorCode": self.error_code,
            "message": self.user_message,
            "severity": self.severity.value,
            "shouldRetry": self.severity in [SafetySeverity.LOW, SafetySeverity.INFO],
            "timestamp": self.timestamp
        }


class SafetyErrorHandler:
    """Centralized error handling for safety-related operations."""

    def __init__(self):
        """Initialize error handler with configuration."""
        self.escalation_enabled = os.getenv('SAFETY_ESCALATION_ENABLED', 'true').lower() == 'true'
        self.audit_logging_enabled = os.getenv('AUDIT_LOGGING_ENABLED', 'true').lower() == 'true'
        self.error_count_threshold = int(os.getenv('SAFETY_ERROR_THRESHOLD', '5'))

        # User-friendly messages for different error types
        self.user_messages = {
            SafetyErrorType.CONTENT_VIOLATION: "Your message couldn't be processed because it may contain inappropriate content. Please try rephrasing your question.",
            SafetyErrorType.MODERATION_FAILURE: "We're having trouble checking your message right now. Please try again in a moment.",
            SafetyErrorType.GUARDRAILS_BREACH: "Your request couldn't be completed because it goes against our safety guidelines. Please ask about something else.",
            SafetyErrorType.PRIVACY_VIOLATION: "We can't process this request to protect your privacy. Please contact a parent or teacher for help.",
            SafetyErrorType.CONTEXT_FAILURE: "We're having trouble remembering our previous conversations. Your question is still welcome!",
            SafetyErrorType.API_RATE_LIMIT: "We're experiencing high demand right now. Please wait a moment and try again.",
            SafetyErrorType.API_TIMEOUT: "The animals are taking a little longer to respond than usual. Please try your question again.",
            SafetyErrorType.DATABASE_ERROR: "We're having trouble saving your conversation right now. Please try again in a moment.",
            SafetyErrorType.CONFIGURATION_ERROR: "There's a temporary issue with our system. Please try again later.",
            SafetyErrorType.UNKNOWN_ERROR: "Something unexpected happened. Please try your question again."
        }

        logger.info("SafetyErrorHandler initialized")

    def handle_content_violation(
        self,
        content: str,
        violation_details: Dict[str, Any],
        session_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> SafetyError:
        """Handle content that violates safety guidelines."""

        flagged_categories = violation_details.get('flagged_categories', [])
        max_score = violation_details.get('max_score', 0.0)

        # Determine severity based on violation type and score
        severity = SafetySeverity.HIGH
        if 'sexual/minors' in flagged_categories or 'violence' in flagged_categories:
            severity = SafetySeverity.CRITICAL
        elif max_score > 0.9:
            severity = SafetySeverity.HIGH
        elif max_score > 0.7:
            severity = SafetySeverity.MEDIUM

        error = SafetyError(
            error_type=SafetyErrorType.CONTENT_VIOLATION,
            severity=severity,
            message=f"Content violation detected: {', '.join(flagged_categories)}",
            user_message=self.user_messages[SafetyErrorType.CONTENT_VIOLATION],
            context={
                'content_length': len(content),
                'content_hash': str(hash(content)),
                'flagged_categories': flagged_categories,
                'max_score': max_score,
                'threshold_exceeded': max_score > 0.7
            },
            recommendations=[
                "Block content immediately",
                "Log violation for review",
                "Provide educational guidance to user",
                "Consider temporary conversation restrictions if repeated violations"
            ],
            should_block_content=True,
            should_escalate=severity == SafetySeverity.CRITICAL,
            error_code="SAFETY_001",
            timestamp=self._get_timestamp(),
            session_id=session_id,
            user_id=user_id
        )

        self._log_and_audit_error(error)
        return error

    def handle_moderation_api_failure(
        self,
        exception: Exception,
        content: str,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> SafetyError:
        """Handle failures in OpenAI moderation API calls."""

        # Determine error type and severity based on exception
        if "rate_limit" in str(exception).lower():
            error_type = SafetyErrorType.API_RATE_LIMIT
            severity = SafetySeverity.MEDIUM
            should_block = False  # Allow content through with rate limiting
            error_code = "SAFETY_002"
        elif "timeout" in str(exception).lower():
            error_type = SafetyErrorType.API_TIMEOUT
            severity = SafetySeverity.MEDIUM
            should_block = False
            error_code = "SAFETY_003"
        else:
            error_type = SafetyErrorType.MODERATION_FAILURE
            severity = SafetySeverity.HIGH
            should_block = True  # Fail safe - block content when moderation fails
            error_code = "SAFETY_004"

        error = SafetyError(
            error_type=error_type,
            severity=severity,
            message=f"Moderation API failure: {str(exception)}",
            user_message=self.user_messages[error_type],
            context={
                'exception_type': type(exception).__name__,
                'exception_message': str(exception),
                'content_length': len(content),
                'content_hash': str(hash(content))
            },
            recommendations=[
                "Implement fallback moderation strategy",
                "Monitor API health and quotas",
                "Consider local content filtering as backup",
                "Escalate if repeated failures occur"
            ],
            should_block_content=should_block,
            should_escalate=severity == SafetySeverity.HIGH,
            error_code=error_code,
            timestamp=self._get_timestamp(),
            session_id=session_id,
            user_id=user_id
        )

        self._log_and_audit_error(error)
        return error

    def handle_guardrails_breach(
        self,
        rule_violated: str,
        user_input: str,
        guardrails_config: Dict[str, Any],
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        animal_id: Optional[str] = None
    ) -> SafetyError:
        """Handle violations of specific guardrails rules."""

        # Determine severity based on rule type
        severity = SafetySeverity.MEDIUM
        if 'NEVER' in rule_violated or 'prohibited' in rule_violated.lower():
            severity = SafetySeverity.HIGH

        error = SafetyError(
            error_type=SafetyErrorType.GUARDRAILS_BREACH,
            severity=severity,
            message=f"Guardrails rule violated: {rule_violated}",
            user_message=self.user_messages[SafetyErrorType.GUARDRAILS_BREACH],
            context={
                'rule_violated': rule_violated,
                'user_input_length': len(user_input),
                'user_input_hash': str(hash(user_input)),
                'guardrails_config_id': guardrails_config.get('configId'),
                'animal_specific': bool(animal_id)
            },
            recommendations=[
                "Provide alternative topic suggestions",
                "Explain educational boundaries in age-appropriate way",
                "Redirect to safe, related topics",
                "Update guardrails if rule is too restrictive"
            ],
            should_block_content=True,
            should_escalate=severity == SafetySeverity.HIGH,
            error_code="SAFETY_005",
            timestamp=self._get_timestamp(),
            session_id=session_id,
            user_id=user_id,
            animal_id=animal_id
        )

        self._log_and_audit_error(error)
        return error

    def handle_privacy_violation(
        self,
        violation_type: str,
        personal_info_detected: List[str],
        user_input: str,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        parent_id: Optional[str] = None
    ) -> SafetyError:
        """Handle privacy violations (especially important for COPPA compliance)."""

        # Privacy violations are always high severity for child users
        severity = SafetySeverity.HIGH
        if any(info in ['address', 'phone', 'email', 'school'] for info in personal_info_detected):
            severity = SafetySeverity.CRITICAL

        error = SafetyError(
            error_type=SafetyErrorType.PRIVACY_VIOLATION,
            severity=severity,
            message=f"Privacy violation detected: {violation_type}",
            user_message=self.user_messages[SafetyErrorType.PRIVACY_VIOLATION],
            context={
                'violation_type': violation_type,
                'personal_info_detected': personal_info_detected,
                'user_input_length': len(user_input),
                'user_input_hash': str(hash(user_input)),
                'has_parent': bool(parent_id),
                'coppa_relevant': True
            },
            recommendations=[
                "Block content immediately and do not store",
                "Notify parent if available",
                "Provide privacy education to user",
                "Review conversation for additional privacy concerns",
                "Implement automatic PII detection improvements"
            ],
            should_block_content=True,
            should_escalate=True,  # Always escalate privacy violations
            error_code="SAFETY_006",
            timestamp=self._get_timestamp(),
            session_id=session_id,
            user_id=user_id
        )

        # Special audit log entry for privacy violations
        if self.audit_logging_enabled and user_id:
            create_audit_log(
                user_id=user_id,
                action_type="PRIVACY_VIOLATION_DETECTED",
                action_details={
                    'violation_type': violation_type,
                    'personal_info_types': personal_info_detected,
                    'session_id': session_id,
                    'severity': severity.value
                },
                parent_id=parent_id
            )

        self._log_and_audit_error(error)
        return error

    def handle_context_summarization_failure(
        self,
        exception: Exception,
        conversations_count: int,
        target_tokens: int,
        user_id: Optional[str] = None
    ) -> SafetyError:
        """Handle failures in context summarization process."""

        error = SafetyError(
            error_type=SafetyErrorType.CONTEXT_FAILURE,
            severity=SafetySeverity.LOW,  # Context failures shouldn't block conversations
            message=f"Context summarization failed: {str(exception)}",
            user_message=self.user_messages[SafetyErrorType.CONTEXT_FAILURE],
            context={
                'exception_type': type(exception).__name__,
                'exception_message': str(exception),
                'conversations_count': conversations_count,
                'target_tokens': target_tokens,
                'user_has_context': bool(user_id)
            },
            recommendations=[
                "Continue conversation without context",
                "Fallback to recent conversation history only",
                "Retry summarization with simpler approach",
                "Monitor summarization API health"
            ],
            should_block_content=False,  # Don't block conversations
            should_escalate=False,
            error_code="SAFETY_007",
            timestamp=self._get_timestamp(),
            user_id=user_id
        )

        self._log_and_audit_error(error)
        return error

    def handle_database_error(
        self,
        exception: Exception,
        operation: str,
        table_name: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> SafetyError:
        """Handle DynamoDB and other database errors in safety contexts."""

        # Determine severity based on operation type
        severity = SafetySeverity.MEDIUM
        if 'audit' in operation.lower() or 'privacy' in operation.lower():
            severity = SafetySeverity.HIGH  # Audit/privacy operations are critical

        error = SafetyError(
            error_type=SafetyErrorType.DATABASE_ERROR,
            severity=severity,
            message=f"Database operation failed: {operation} - {str(exception)}",
            user_message=self.user_messages[SafetyErrorType.DATABASE_ERROR],
            context={
                'operation': operation,
                'table_name': table_name,
                'exception_type': type(exception).__name__,
                'exception_message': str(exception),
                'is_safety_critical': severity == SafetySeverity.HIGH
            },
            recommendations=[
                "Retry operation with exponential backoff",
                "Check database connectivity and permissions",
                "Implement graceful degradation",
                "Alert operations team if critical safety data"
            ],
            should_block_content=severity == SafetySeverity.HIGH,
            should_escalate=severity == SafetySeverity.HIGH,
            error_code="SAFETY_008",
            timestamp=self._get_timestamp(),
            user_id=user_id
        )

        self._log_and_audit_error(error)
        return error

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.now(timezone.utc).isoformat()

    def _log_and_audit_error(self, error: SafetyError) -> None:
        """Log error and create audit trail if enabled."""

        # Always log errors
        log_level = logging.ERROR if error.severity in [SafetySeverity.CRITICAL, SafetySeverity.HIGH] else logging.WARNING
        logger.log(log_level, f"Safety error: {error.message}", extra=error.to_dict())

        # Create audit log entry if enabled and user_id is available
        if self.audit_logging_enabled and error.user_id:
            try:
                create_audit_log(
                    user_id=error.user_id,
                    action_type="SAFETY_ERROR_LOGGED",
                    action_details={
                        'error_type': error.error_type.value,
                        'severity': error.severity.value,
                        'error_code': error.error_code,
                        'should_escalate': error.should_escalate,
                        'context': error.context
                    }
                )
            except Exception as audit_error:
                logger.error(f"Failed to create audit log for safety error: {audit_error}")

        # Escalate if required
        if error.should_escalate and self.escalation_enabled:
            self._escalate_error(error)

    def _escalate_error(self, error: SafetyError) -> None:
        """Escalate critical safety errors to appropriate channels."""

        try:
            # In production, this would integrate with alerting systems
            # For now, just log the escalation
            logger.critical(
                f"ESCALATED SAFETY ERROR: {error.error_code} - {error.message}",
                extra={
                    'escalation': True,
                    'error_details': error.to_dict()
                }
            )

            # Here you would integrate with:
            # - PagerDuty for critical alerts
            # - Slack/Teams notifications
            # - Email alerts to safety team
            # - Parent notifications for child safety issues

        except Exception as escalation_error:
            logger.error(f"Failed to escalate safety error: {escalation_error}")


# Global error handler instance
_safety_error_handler: Optional[SafetyErrorHandler] = None


def get_safety_error_handler() -> SafetyErrorHandler:
    """Get singleton SafetyErrorHandler instance."""
    global _safety_error_handler

    if _safety_error_handler is None:
        _safety_error_handler = SafetyErrorHandler()

    return _safety_error_handler


def safety_error_wrapper(error_handler: SafetyErrorHandler = None):
    """
    Decorator to wrap functions with automatic safety error handling.

    Args:
        error_handler: Optional specific error handler instance
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            handler = error_handler or get_safety_error_handler()

            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Create a generic safety error
                error = SafetyError(
                    error_type=SafetyErrorType.UNKNOWN_ERROR,
                    severity=SafetySeverity.MEDIUM,
                    message=f"Unexpected error in {func.__name__}: {str(e)}",
                    user_message=handler.user_messages[SafetyErrorType.UNKNOWN_ERROR],
                    context={
                        'function_name': func.__name__,
                        'exception_type': type(e).__name__,
                        'exception_message': str(e),
                        'traceback': traceback.format_exc()
                    },
                    recommendations=[
                        "Retry operation",
                        "Check function parameters",
                        "Review error logs for root cause"
                    ],
                    should_block_content=False,
                    should_escalate=False,
                    error_code="SAFETY_009",
                    timestamp=handler._get_timestamp()
                )

                handler._log_and_audit_error(error)
                return error.to_api_response(), 500

        return wrapper
    return decorator


# Convenience functions for common error scenarios
def handle_content_violation_simple(content: str, violation_details: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    """Simple content violation handler that returns API response."""
    handler = get_safety_error_handler()
    error = handler.handle_content_violation(content, violation_details)
    return error.to_api_response(), 400


def handle_api_failure_simple(exception: Exception, operation: str) -> Tuple[Dict[str, Any], int]:
    """Simple API failure handler that returns appropriate response."""
    handler = get_safety_error_handler()

    if "moderation" in operation.lower():
        error = handler.handle_moderation_api_failure(exception, "")
    else:
        error = SafetyError(
            error_type=SafetyErrorType.UNKNOWN_ERROR,
            severity=SafetySeverity.MEDIUM,
            message=f"API operation failed: {operation}",
            user_message=handler.user_messages[SafetyErrorType.UNKNOWN_ERROR],
            context={'operation': operation, 'exception': str(exception)},
            recommendations=["Retry operation", "Check API connectivity"],
            should_block_content=False,
            should_escalate=False,
            error_code="SAFETY_010",
            timestamp=handler._get_timestamp()
        )
        handler._log_and_audit_error(error)

    status_code = 503 if error.error_type == SafetyErrorType.API_TIMEOUT else 500
    return error.to_api_response(), status_code


def create_safety_error(
    error_type: SafetyErrorType,
    message: str,
    severity: SafetySeverity = SafetySeverity.MEDIUM,
    context: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    animal_id: Optional[str] = None,
    should_block: bool = False
) -> SafetyError:
    """
    Convenience function to create a SafetyError with default values.

    Args:
        error_type: Type of safety error
        message: Detailed error message for logging
        severity: Severity level (defaults to MEDIUM)
        context: Additional context information
        user_id: Optional user identifier
        session_id: Optional session identifier
        animal_id: Optional animal identifier
        should_block: Whether content should be blocked

    Returns:
        SafetyError: Configured safety error instance
    """
    handler = get_safety_error_handler()
    user_message = handler.user_messages.get(error_type, handler.user_messages[SafetyErrorType.UNKNOWN_ERROR])

    error = SafetyError(
        error_type=error_type,
        severity=severity,
        message=message,
        user_message=user_message,
        context=context or {},
        recommendations=["Review and retry", "Contact support if issue persists"],
        should_block_content=should_block,
        should_escalate=severity in [SafetySeverity.CRITICAL, SafetySeverity.HIGH],
        error_code=f"SAFETY_{error_type.value.upper()[:3]}",
        timestamp=handler._get_timestamp(),
        session_id=session_id,
        user_id=user_id,
        animal_id=animal_id
    )

    return error


def log_safety_event(
    event_type: str,
    message: str,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    severity: str = "info"
) -> None:
    """
    Log a safety-related event for audit and monitoring purposes.

    Args:
        event_type: Type of safety event (e.g., "content_filtered", "guardrails_applied")
        message: Descriptive message about the event
        user_id: Optional user identifier
        session_id: Optional session identifier
        context: Additional context information
        severity: Event severity level ("info", "warning", "error", "critical")
    """
    log_data = {
        'event_type': event_type,
        'message': message,
        'user_id': user_id,
        'session_id': session_id,
        'context': context or {},
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'severity': severity
    }

    # Log at appropriate level based on severity
    if severity == "critical":
        logger.critical(f"Safety event: {message}", extra=log_data)
    elif severity == "error":
        logger.error(f"Safety event: {message}", extra=log_data)
    elif severity == "warning":
        logger.warning(f"Safety event: {message}", extra=log_data)
    else:
        logger.info(f"Safety event: {message}", extra=log_data)

    # Create audit log if user_id is available
    if user_id:
        try:
            create_audit_log(
                user_id=user_id,
                action_type=f"SAFETY_EVENT_{event_type.upper()}",
                action_details={
                    'message': message,
                    'context': context or {},
                    'severity': severity,
                    'session_id': session_id
                }
            )
        except Exception as audit_error:
            logger.error(f"Failed to create audit log for safety event: {audit_error}")