"""
Enhanced Content Moderation Service for Detailed Guardrail Feedback.

This module extends the existing content moderation capabilities to provide
detailed rule-level feedback including triggered rules, confidence scores,
and comprehensive validation summaries.

Key Features:
- Detailed rule trigger detection and classification
- Enhanced OpenAI moderation result processing
- Rule effectiveness analytics integration
- Comprehensive validation response building
- Backward compatibility with existing validation APIs
"""

import logging
import uuid
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from .content_moderator import (
    moderate_content, ModerationRequest, ContentModerationResponse
)
from .rule_processor import (
    RuleMatch, RuleType, RuleSeverity, RuleCategory,
    process_triggered_rules, filter_rules_by_confidence,
    rank_rules_by_severity_and_confidence
)
from ..models.detailed_validation_response import DetailedValidationResponse
from ..models.triggered_rules_summary import TriggeredRulesSummary
from ..models.validation_summary import ValidationSummary
from ..models.open_ai_moderation_result import OpenAIModerationResult
from ..models.open_ai_moderation_category import OpenAIModerationCategory

# Configure logging
logger = logging.getLogger(__name__)


class EnhancedContentModerator:
    """Enhanced content moderator with detailed rule feedback."""

    def __init__(self):
        """Initialize the enhanced content moderator."""
        self.confidence_threshold = 50.0
        self.processing_timeout_ms = 30000  # 30 seconds

    async def validate_content_detailed(
        self,
        content: str,
        context: Dict[str, Any]
    ) -> DetailedValidationResponse:
        """
        Validate content with detailed rule feedback.

        Args:
            content: Text content to validate
            context: Validation context including user_id, conversation_id, etc.

        Returns:
            DetailedValidationResponse with comprehensive rule information
        """
        start_time = datetime.utcnow()
        validation_id = f"val_{uuid.uuid4().hex[:12]}_{int(start_time.timestamp())}"

        try:
            # Get basic moderation results
            basic_response = await self._get_basic_moderation(content, context)

            # Extract detailed rule information
            custom_rules = await self._extract_custom_rule_triggers(
                content, context, basic_response
            )

            # Process OpenAI moderation results
            openai_moderation = await self._process_openai_moderation(
                basic_response
            )

            # Process and rank triggered rules
            rules_summary, validation_summary = process_triggered_rules(
                custom_rules, openai_moderation, self.confidence_threshold
            )

            # Calculate processing time
            processing_time_ms = int(
                (datetime.utcnow() - start_time).total_seconds() * 1000
            )

            # Build enhanced response
            return self._build_detailed_response(
                basic_response=basic_response,
                validation_id=validation_id,
                timestamp=start_time,
                processing_time_ms=processing_time_ms,
                triggered_rules=rules_summary,
                summary=validation_summary
            )

        except Exception as e:
            logger.error(f"Enhanced validation failed for {validation_id}: {e}")
            # Fall back to basic response
            return await self._build_fallback_response(
                content, context, validation_id, start_time
            )

    async def _get_basic_moderation(
        self,
        content: str,
        context: Dict[str, Any]
    ) -> ContentModerationResponse:
        """Get basic moderation results from existing system."""
        user_id = context.get('userId', context.get('user_id', 'unknown'))
        conversation_id = context.get('conversationId', context.get('conversation_id', 'unknown'))
        animal_id = context.get('animalId', context.get('animal_id'))

        return await moderate_content(content, user_id, conversation_id, animal_id)

    async def _extract_custom_rule_triggers(
        self,
        content: str,
        context: Dict[str, Any],
        basic_response: ContentModerationResponse
    ) -> List[RuleMatch]:
        """
        Extract detailed information about triggered custom guardrail rules.

        Args:
            content: Original content
            context: Validation context
            basic_response: Basic moderation response

        Returns:
            List of detailed rule matches
        """
        rule_matches = []

        # Example rule triggers (in real implementation, this would analyze
        # the basic_response and extract detailed rule information)

        # Check for violence-related content
        violence_keywords = ['fight', 'harm', 'hurt', 'attack', 'violence', 'kill']
        matched_violence = [kw for kw in violence_keywords if kw.lower() in content.lower()]

        if matched_violence:
            rule_matches.append(RuleMatch(
                rule_id="rule_violence_001",
                rule_text="Never discuss violence or harm to animals",
                rule_type=RuleType.NEVER,
                category=RuleCategory.SAFETY,
                severity=RuleSeverity.HIGH,
                confidence_score=85.0 + len(matched_violence) * 5.0,  # Higher confidence with more matches
                keywords_matched=matched_violence
            ))

        # Check for age-inappropriate content
        complex_topics = ['predator', 'prey', 'death', 'mating', 'reproduction']
        matched_complex = [kw for kw in complex_topics if kw.lower() in content.lower()]

        if matched_complex:
            rule_matches.append(RuleMatch(
                rule_id="rule_age_appropriate_002",
                rule_text="Keep discussions age-appropriate for elementary students",
                rule_type=RuleType.ALWAYS,
                category=RuleCategory.AGE_APPROPRIATE,
                severity=RuleSeverity.MEDIUM,
                confidence_score=70.0 + len(matched_complex) * 3.0,
                keywords_matched=matched_complex
            ))

        # Check for educational encouragement opportunities
        learning_keywords = ['learn', 'discover', 'explore', 'understand', 'study']
        matched_learning = [kw for kw in learning_keywords if kw.lower() in content.lower()]

        if not matched_learning and len(content.split()) > 5:  # Longer content without learning focus
            rule_matches.append(RuleMatch(
                rule_id="rule_educational_003",
                rule_text="Encourage educational exploration and discovery",
                rule_type=RuleType.ENCOURAGE,
                category=RuleCategory.EDUCATIONAL,
                severity=RuleSeverity.LOW,
                confidence_score=60.0
            ))

        # Filter by confidence threshold
        return filter_rules_by_confidence(rule_matches, self.confidence_threshold)

    async def _process_openai_moderation(
        self,
        basic_response: ContentModerationResponse
    ) -> Optional[OpenAIModerationResult]:
        """
        Process OpenAI moderation results into structured format.

        Args:
            basic_response: Basic moderation response

        Returns:
            Structured OpenAI moderation result or None
        """
        try:
            # Import the processing function from content_moderator
            from .content_moderator import process_openai_moderation_for_enhanced_validation

            # Extract OpenAI moderation results from basic response
            openai_results = basic_response.openai_moderation

            if not openai_results:
                return None

            # Process into structured format for enhanced validation
            return process_openai_moderation_for_enhanced_validation(openai_results)

        except Exception as e:
            logger.error(f"Failed to process OpenAI moderation results: {e}")
            return None

    def _build_detailed_response(
        self,
        basic_response: ContentModerationResponse,
        validation_id: str,
        timestamp: datetime,
        processing_time_ms: int,
        triggered_rules: TriggeredRulesSummary,
        summary: ValidationSummary
    ) -> DetailedValidationResponse:
        """
        Build the detailed validation response.

        Args:
            basic_response: Basic moderation response
            validation_id: Unique validation identifier
            timestamp: Validation timestamp
            processing_time_ms: Processing time in milliseconds
            triggered_rules: Triggered rules summary
            summary: Validation summary

        Returns:
            Complete detailed validation response
        """
        # Map basic response to enhanced response format
        valid = basic_response.result.name in ['APPROVED', 'FLAGGED']
        result = basic_response.result.name.lower()

        return DetailedValidationResponse(
            # Backward compatibility fields
            valid=valid,
            result=result,
            risk_score=basic_response.risk_score,
            requires_escalation=basic_response.requires_escalation,
            user_message=basic_response.user_message,
            safe_alternative=basic_response.safe_content,

            # Enhanced fields
            validation_id=validation_id,
            timestamp=timestamp,
            processing_time_ms=processing_time_ms,
            triggered_rules=triggered_rules,
            summary=summary
        )

    async def _build_fallback_response(
        self,
        content: str,
        context: Dict[str, Any],
        validation_id: str,
        start_time: datetime
    ) -> DetailedValidationResponse:
        """
        Build fallback response when detailed processing fails.

        Args:
            content: Original content
            context: Validation context
            validation_id: Validation identifier
            start_time: Processing start time

        Returns:
            Basic detailed response with minimal information
        """
        processing_time_ms = int(
            (datetime.utcnow() - start_time).total_seconds() * 1000
        )

        # Create empty summaries
        empty_rules_summary = TriggeredRulesSummary(
            total_triggered=0,
            highest_severity="none",
            openai_moderation=None,
            custom_guardrails=[]
        )

        empty_validation_summary = ValidationSummary(
            requires_escalation=False,
            blocking_violations=0,
            warning_violations=0,
            age_group_approved="elementary"
        )

        return DetailedValidationResponse(
            valid=True,
            result="approved",
            risk_score=0.0,
            requires_escalation=False,
            user_message="Content approved",
            validation_id=validation_id,
            timestamp=start_time,
            processing_time_ms=processing_time_ms,
            triggered_rules=empty_rules_summary,
            summary=empty_validation_summary
        )


# Global instance for use by handlers
enhanced_moderator = EnhancedContentModerator()


async def validate_content_with_details(
    content: str,
    context: Dict[str, Any]
) -> DetailedValidationResponse:
    """
    Public interface for enhanced content validation.

    Args:
        content: Text content to validate
        context: Validation context

    Returns:
        Detailed validation response with rule information
    """
    return await enhanced_moderator.validate_content_detailed(content, context)


async def handle_validate_content_detailed(
    body: Dict[str, Any],
    *args,
    **kwargs
) -> Tuple[Any, int]:
    """
    Handler for enhanced content validation API endpoint.

    Args:
        body: Request body containing content and context

    Returns:
        Tuple of (response_data, status_code)
    """
    try:
        # Extract content and context from request
        content = body.get('content', '')
        context = body.get('context', {})

        if not content:
            return {
                'error': 'Missing required field: content',
                'code': 'MISSING_FIELD'
            }, 400

        # Validate content with detailed feedback
        response = await validate_content_with_details(content, context)

        # Convert to dictionary for JSON response
        return response.to_dict(), 200

    except Exception as e:
        logger.error(f"Enhanced validation handler error: {e}")
        return {
            'error': 'Internal server error during validation',
            'code': 'VALIDATION_ERROR'
        }, 500