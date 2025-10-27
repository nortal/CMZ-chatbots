"""
Content Moderation Service for CMZ Chatbots safety system.

This module provides comprehensive content moderation capabilities combining
OpenAI's moderation API with custom guardrails for educational safety.

Key Features:
- OpenAI content moderation integration with child-focused filtering
- Custom guardrails validation for educational appropriateness
- Risk assessment and escalation logic for safety violations
- Conversation context-aware moderation decisions
- Analytics and audit trail for safety compliance
- Configurable sensitivity levels for different user types
"""

import logging
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass
from datetime import datetime
import asyncio
import hashlib

from .openai_integration import (
    OpenAIIntegration, ModerationResponse
)
from .safety_errors import (
    SafetyError, SafetyErrorType, SafetySeverity as SafetyErrorSeverity
)
from ...models.open_ai_moderation_result import OpenAIModerationResult
from ...models.open_ai_moderation_category import OpenAIModerationCategory
from .safety_dynamo import get_safety_dynamo_client
from .safety_errors import get_safety_error_handler, log_safety_event
from .safety_analytics import get_safety_analytics, SafetyEventType
from ..models.content_validation import (
    get_content_validation_mapper, ValidationResult
)
from ..models.guardrails_config import get_guardrails_config_mapper

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class ModerationRequest:
    """Content moderation request structure."""
    content: str
    user_id: str
    conversation_id: str
    message_id: Optional[str] = None
    animal_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    sensitivity_level: str = "standard"  # standard, strict, educational


@dataclass
class ModerationResult:
    """Content moderation result structure."""
    validation_id: str
    result: ValidationResult
    risk_score: float
    requires_escalation: bool
    openai_moderation: Optional[Dict[str, Any]] = None
    guardrails_violations: Optional[List[Dict[str, Any]]] = None
    safe_content: Optional[str] = None
    user_message: Optional[str] = None
    processing_time_ms: int = 0


@dataclass
class ModerationConfig:
    """Configuration for content moderation behavior."""
    openai_enabled: bool = True
    guardrails_enabled: bool = True
    auto_block_threshold: float = 0.8
    escalation_threshold: float = 0.6
    educational_mode: bool = True
    preserve_educational_value: bool = True
    max_processing_time_ms: int = 5000


class ContentModerator:
    """Comprehensive content moderation service."""

    def __init__(self, config: Optional[ModerationConfig] = None):
        """
        Initialize content moderator.

        Args:
            config: Optional moderation configuration
        """
        self.config = config or ModerationConfig()
        self.openai_client = OpenAIIntegration()
        self.safety_client = get_safety_dynamo_client()
        self.content_mapper = get_content_validation_mapper()
        self.guardrails_mapper = get_guardrails_config_mapper()
        self.analytics = get_safety_analytics()

        # Cache for guardrails configurations
        self._guardrails_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl: Dict[str, datetime] = {}

    async def moderate_content(self, request: ModerationRequest) -> ModerationResult:
        """
        Perform comprehensive content moderation.

        Args:
            request: Moderation request with content and context

        Returns:
            Complete moderation result with safety recommendations
        """
        start_time = datetime.now()
        validation_id = self._generate_validation_id(request)

        try:
            logger.info(f"Starting content moderation for validation_id: {validation_id}")

            # Initialize result structure
            result = ModerationResult(
                validation_id=validation_id,
                result=ValidationResult.APPROVED,
                risk_score=0.0,
                requires_escalation=False
            )

            # Parallel execution of moderation checks
            moderation_tasks = []

            if self.config.openai_enabled:
                moderation_tasks.append(self._openai_moderation(request))

            if self.config.guardrails_enabled:
                moderation_tasks.append(self._guardrails_moderation(request))

            # Execute moderation checks
            if moderation_tasks:
                moderation_results = await asyncio.gather(*moderation_tasks, return_exceptions=True)

                # Process OpenAI moderation results
                if self.config.openai_enabled and len(moderation_results) > 0:
                    openai_result = moderation_results[0]
                    if not isinstance(openai_result, Exception):
                        result.openai_moderation = openai_result

                # Process guardrails results
                guardrails_index = 1 if self.config.openai_enabled else 0
                if self.config.guardrails_enabled and len(moderation_results) > guardrails_index:
                    guardrails_result = moderation_results[guardrails_index]
                    if not isinstance(guardrails_result, Exception):
                        result.guardrails_violations = guardrails_result

            # Analyze combined results
            result = await self._analyze_moderation_results(request, result)

            # Generate user-appropriate messaging
            result = await self._generate_user_messaging(request, result)

            # Store validation results
            await self._store_validation_results(request, result)

            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            result.processing_time_ms = int(processing_time)

            # Track analytics events
            await self._track_moderation_analytics(request, result)

            logger.info(f"Content moderation completed for {validation_id}: "
                       f"result={result.result.value}, risk_score={result.risk_score}")

            return result

        except Exception as e:
            logger.error(f"Content moderation failed for {validation_id}: {e}")

            # Create error result
            error_result = ModerationResult(
                validation_id=validation_id,
                result=ValidationResult.ESCALATED,
                risk_score=1.0,
                requires_escalation=True,
                user_message="We're having trouble checking your message right now. Please try again."
            )

            # Log safety event
            await log_safety_event(
                event_type="moderation_error",
                user_id=request.user_id,
                details={"error": str(e), "validation_id": validation_id}
            )

            return error_result

    async def _openai_moderation(self, request: ModerationRequest) -> Optional[Dict[str, Any]]:
        """
        Perform OpenAI content moderation.

        Args:
            request: Moderation request

        Returns:
            OpenAI moderation results or None if failed
        """
        try:
            moderation_response = await self.openai_client.moderate_content(request.content)

            if moderation_response and moderation_response.success:
                return {
                    "flagged": moderation_response.flagged,
                    "categories": moderation_response.categories,
                    "category_scores": moderation_response.category_scores,
                    "model": moderation_response.model
                }
            else:
                logger.warning(f"OpenAI moderation failed: {moderation_response.error if moderation_response else 'No response'}")
                return None

        except Exception as e:
            logger.error(f"OpenAI moderation error: {e}")
            return None

    async def _guardrails_moderation(self, request: ModerationRequest) -> Optional[List[Dict[str, Any]]]:
        """
        Perform custom guardrails moderation.

        Args:
            request: Moderation request

        Returns:
            List of guardrails violations or None if failed
        """
        try:
            # Get guardrails configuration
            guardrails_config = await self._get_guardrails_config(request.animal_id)

            if not guardrails_config or not guardrails_config.get("rules"):
                logger.info("No guardrails rules configured")
                return []

            violations = []
            content_lower = request.content.lower()

            # Check each guardrails rule
            for rule in guardrails_config["rules"]:
                violation = await self._check_guardrails_rule(request.content, content_lower, rule)
                if violation:
                    violations.append(violation)

            return violations

        except Exception as e:
            logger.error(f"Guardrails moderation error: {e}")
            return None

    async def _check_guardrails_rule(
        self,
        content: str,
        content_lower: str,
        rule: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Check content against a specific guardrails rule.

        Args:
            content: Original content
            content_lower: Lowercase content for case-insensitive matching
            rule: Guardrails rule configuration

        Returns:
            Violation dictionary if rule violated, None otherwise
        """
        try:
            rule_text = rule.get("rule", "").lower()
            rule_type = rule.get("type", "DISCOURAGE")
            rule_id = rule.get("ruleId", "unknown")
            priority = rule.get("priority", 50)

            if not rule_text:
                return None

            # Simple keyword matching (can be enhanced with NLP)
            confidence = 0.0
            violation_context = ""

            # Check for keyword presence
            keywords = [kw.strip() for kw in rule_text.split(",") if kw.strip()]
            matched_keywords = []

            for keyword in keywords:
                if keyword in content_lower:
                    matched_keywords.append(keyword)
                    # Higher confidence for exact matches
                    confidence = max(confidence, 0.8 if len(keyword) > 3 else 0.6)

            # No violation if no keywords matched
            if not matched_keywords:
                return None

            # Determine severity based on rule type and priority
            severity = self._determine_violation_severity(rule_type, priority, confidence)

            # Only report violations above confidence threshold
            if confidence < 0.5:
                return None

            violation_context = f"Matched keywords: {', '.join(matched_keywords)}"

            return {
                "ruleId": rule_id,
                "ruleType": rule_type,
                "violationType": "content",
                "severity": severity,
                "confidence": confidence,
                "message": self._generate_violation_message(rule_type, matched_keywords),
                "context": violation_context,
                "detectedAt": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error checking guardrails rule {rule.get('ruleId', 'unknown')}: {e}")
            return None

    def _determine_violation_severity(self, rule_type: str, priority: int, confidence: float) -> str:
        """
        Determine violation severity based on rule characteristics.

        Args:
            rule_type: Type of guardrails rule
            priority: Rule priority (0-100)
            confidence: Detection confidence (0.0-1.0)

        Returns:
            Severity level string
        """
        # NEVER rules are always high severity
        if rule_type == "NEVER":
            return "high" if confidence > 0.8 else "medium"

        # High priority rules get elevated severity
        if priority >= 80:
            return "medium" if confidence > 0.7 else "low"

        # Medium priority rules
        if priority >= 50:
            return "low" if confidence > 0.8 else "low"

        # Low priority rules
        return "low"

    def _generate_violation_message(self, rule_type: str, matched_keywords: List[str]) -> str:
        """
        Generate user-friendly violation message.

        Args:
            rule_type: Type of guardrails rule
            matched_keywords: Keywords that triggered the violation

        Returns:
            User-friendly message
        """
        if rule_type == "NEVER":
            return "This topic isn't appropriate for our educational chat."
        elif rule_type == "DISCOURAGE":
            return "Let's focus on learning about animals instead."
        elif rule_type == "ENCOURAGE":
            return "Great question! Let's explore this topic more."
        else:
            return "Let's keep our conversation educational and fun."

    async def _analyze_moderation_results(
        self,
        request: ModerationRequest,
        result: ModerationResult
    ) -> ModerationResult:
        """
        Analyze combined moderation results and determine final decision.

        Args:
            request: Original moderation request
            result: Moderation result with individual check results

        Returns:
            Updated result with final decision
        """
        risk_factors = []
        max_risk_score = 0.0

        # Analyze OpenAI moderation results
        if result.openai_moderation:
            openai_risk = self._calculate_openai_risk(result.openai_moderation)
            max_risk_score = max(max_risk_score, openai_risk)

            if result.openai_moderation.get("flagged", False):
                risk_factors.append("content_moderation")

        # Analyze guardrails violations
        if result.guardrails_violations:
            guardrails_risk = self._calculate_guardrails_risk(result.guardrails_violations)
            max_risk_score = max(max_risk_score, guardrails_risk)

            critical_violations = [v for v in result.guardrails_violations if v.get("severity") == "critical"]
            if critical_violations:
                risk_factors.append("critical_guardrails")

        # Set final risk score
        result.risk_score = max_risk_score

        # Determine final result based on thresholds
        if max_risk_score >= self.config.auto_block_threshold:
            result.result = ValidationResult.BLOCKED
        elif max_risk_score >= self.config.escalation_threshold:
            result.result = ValidationResult.FLAGGED
        elif risk_factors:
            result.result = ValidationResult.FLAGGED
        else:
            result.result = ValidationResult.APPROVED

        # Determine escalation requirement
        result.requires_escalation = (
            max_risk_score >= self.config.escalation_threshold or
            "critical_guardrails" in risk_factors or
            self._requires_manual_review(result.openai_moderation, result.guardrails_violations)
        )

        return result

    def _calculate_openai_risk(self, moderation_results: Dict[str, Any]) -> float:
        """
        Calculate risk score from OpenAI moderation results.

        Args:
            moderation_results: OpenAI moderation response

        Returns:
            Risk score between 0.0 and 1.0
        """
        if not moderation_results.get("flagged", False):
            return 0.0

        category_scores = moderation_results.get("category_scores", {})

        # Weight categories based on risk to children
        category_weights = {
            "sexual": 1.0,
            "sexual/minors": 1.0,
            "violence": 0.8,
            "violence/graphic": 0.9,
            "hate": 0.7,
            "hate/threatening": 0.8,
            "harassment": 0.6,
            "harassment/threatening": 0.7,
            "self-harm": 0.9,
            "self-harm/intent": 1.0,
            "self-harm/instructions": 1.0
        }

        weighted_score = 0.0
        total_weight = 0.0

        for category, score in category_scores.items():
            weight = category_weights.get(category, 0.5)
            weighted_score += score * weight
            total_weight += weight

        return weighted_score / total_weight if total_weight > 0 else 0.0

    def _calculate_guardrails_risk(self, violations: List[Dict[str, Any]]) -> float:
        """
        Calculate risk score from guardrails violations.

        Args:
            violations: List of guardrails violations

        Returns:
            Risk score between 0.0 and 1.0
        """
        if not violations:
            return 0.0

        severity_scores = {"low": 0.25, "medium": 0.5, "high": 0.75, "critical": 1.0}
        max_risk = 0.0

        for violation in violations:
            severity = violation.get("severity", "medium")
            confidence = violation.get("confidence", 0.0)
            risk = severity_scores.get(severity, 0.5) * confidence
            max_risk = max(max_risk, risk)

        return max_risk

    def _requires_manual_review(
        self,
        openai_results: Optional[Dict[str, Any]],
        violations: Optional[List[Dict[str, Any]]]
    ) -> bool:
        """
        Determine if content requires manual review.

        Args:
            openai_results: OpenAI moderation results
            violations: Guardrails violations

        Returns:
            True if manual review required
        """
        # Always escalate certain OpenAI categories
        if openai_results:
            categories = openai_results.get("categories", {})
            escalation_categories = ["sexual/minors", "self-harm/intent", "self-harm/instructions"]

            for category in escalation_categories:
                if categories.get(category, False):
                    return True

        # Always escalate critical guardrails violations
        if violations:
            for violation in violations:
                if violation.get("severity") == "critical":
                    return True

        return False

    async def _generate_user_messaging(
        self,
        request: ModerationRequest,
        result: ModerationResult
    ) -> ModerationResult:
        """
        Generate appropriate user messaging based on moderation results.

        Args:
            request: Original moderation request
            result: Moderation result

        Returns:
            Updated result with user messaging
        """
        if result.result == ValidationResult.APPROVED:
            result.user_message = None  # No message needed for approved content
            result.safe_content = request.content  # Content is safe as-is

        elif result.result == ValidationResult.FLAGGED:
            result.user_message = self._generate_educational_message(result)
            result.safe_content = await self._generate_safe_alternative(request, result)

        elif result.result == ValidationResult.BLOCKED:
            result.user_message = self._generate_blocking_message(result)
            result.safe_content = None  # No safe alternative for blocked content

        elif result.result == ValidationResult.ESCALATED:
            result.user_message = "Let me get a zookeeper to help answer your question!"
            result.safe_content = None

        return result

    def _generate_educational_message(self, result: ModerationResult) -> str:
        """
        Generate educational message for flagged content.

        Args:
            result: Moderation result

        Returns:
            Educational message encouraging appropriate topics
        """
        messages = [
            "That's an interesting question! Let's talk about animals and nature instead.",
            "I love your curiosity! How about we explore something about wildlife?",
            "Great thinking! Let's focus on learning about animals and their habitats.",
            "I'm here to help you learn about amazing animals. What would you like to know?"
        ]

        # Choose message based on violation type
        if result.guardrails_violations:
            for violation in result.guardrails_violations:
                if violation.get("severity") in ["high", "critical"]:
                    return "Let's keep our conversation focused on learning about animals!"

        return messages[0]  # Default educational message

    def _generate_blocking_message(self, result: ModerationResult) -> str:
        """
        Generate blocking message for blocked content.

        Args:
            result: Moderation result

        Returns:
            Age-appropriate blocking message
        """
        return ("I can't help with that topic. Let's talk about something fun and educational "
                "about animals instead! What's your favorite animal?")

    async def _generate_safe_alternative(
        self,
        request: ModerationRequest,
        result: ModerationResult
    ) -> Optional[str]:
        """
        Generate safe alternative content when possible.

        Args:
            request: Original moderation request
            result: Moderation result

        Returns:
            Safe alternative content or None
        """
        if not self.config.preserve_educational_value:
            return None

        try:
            # Simple content sanitization for educational purposes
            safe_content = request.content

            # Remove flagged keywords while preserving educational intent
            if result.guardrails_violations:
                for violation in result.guardrails_violations:
                    context = violation.get("context", "")
                    if "Matched keywords:" in context:
                        keywords_text = context.split("Matched keywords:", 1)[1].strip()
                        keywords = [kw.strip() for kw in keywords_text.split(",")]

                        for keyword in keywords:
                            if keyword in safe_content.lower():
                                # Replace with educational alternative
                                safe_content = safe_content.replace(keyword, "[educational topic]")

            # Only return if substantially different from original
            if safe_content != request.content and len(safe_content) > 10:
                return safe_content

            return None

        except Exception as e:
            logger.error(f"Failed to generate safe alternative: {e}")
            return None

    async def _store_validation_results(
        self,
        request: ModerationRequest,
        result: ModerationResult
    ) -> None:
        """
        Store moderation results in DynamoDB for audit and analytics.

        Args:
            request: Original moderation request
            result: Moderation result
        """
        try:
            validation_data = {
                "validationId": result.validation_id,
                "conversationId": request.conversation_id,
                "messageId": request.message_id or "",
                "userId": request.user_id,
                "animalId": request.animal_id or "",
                "result": result.result.value,
                "riskScore": result.risk_score,
                "requiresEscalation": result.requires_escalation,
                "processingTimeMs": result.processing_time_ms,
                "sensitivityLevel": request.sensitivity_level,
                "moderationResults": result.openai_moderation,
                "guardrailsViolations": result.guardrails_violations or [],
                "contentLength": len(request.content),
                "hasUserMessage": bool(result.user_message),
                "hasSafeAlternative": bool(result.safe_content)
            }

            # Convert to DynamoDB format using mapper
            ddb_item = self.content_mapper.to_dynamodb_format(validation_data)

            # Store in ContentValidation table
            await self.safety_client.store_content_validation(ddb_item)

            logger.info(f"Stored validation results for {result.validation_id}")

        except Exception as e:
            logger.error(f"Failed to store validation results: {e}")
            # Don't fail the moderation process due to storage issues

    async def _get_guardrails_config(self, animal_id: Optional[str]) -> Optional[Dict[str, Any]]:
        """
        Get guardrails configuration for animal or global default.

        Args:
            animal_id: Animal ID for specific configuration

        Returns:
            Guardrails configuration or None
        """
        try:
            cache_key = animal_id or "global"

            # Check cache first
            if cache_key in self._guardrails_cache:
                cache_time = self._cache_ttl.get(cache_key)
                if cache_time and (datetime.now() - cache_time).seconds < 300:  # 5 min TTL
                    return self._guardrails_cache[cache_key]

            # Load from DynamoDB
            config = await self.safety_client.get_guardrails_config(animal_id)

            if config:
                # Cache the configuration
                self._guardrails_cache[cache_key] = config
                self._cache_ttl[cache_key] = datetime.now()

            return config

        except Exception as e:
            logger.error(f"Failed to get guardrails config for {animal_id}: {e}")
            return None

    def _generate_validation_id(self, request: ModerationRequest) -> str:
        """
        Generate unique validation ID for tracking.

        Args:
            request: Moderation request

        Returns:
            Unique validation ID
        """
        content_hash = hashlib.sha256(request.content.encode()).hexdigest()[:8]
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"val_{timestamp}_{content_hash}"

    async def _track_moderation_analytics(
        self,
        request: ModerationRequest,
        result: ModerationResult
    ) -> None:
        """
        Track analytics events for moderation results.

        Args:
            request: Original moderation request
            result: Moderation result
        """
        try:
            # Collect triggered rules for analytics
            triggered_rules = []
            if result.guardrails_violations:
                triggered_rules = [v.get("ruleId", "unknown") for v in result.guardrails_violations]

            # Track primary content validation event
            await self.analytics.track_safety_event(
                event_type=SafetyEventType.CONTENT_VALIDATED,
                user_id=request.user_id,
                conversation_id=request.conversation_id,
                animal_id=request.animal_id,
                content=request.content,
                risk_score=result.risk_score,
                triggered_rules=triggered_rules,
                moderation_result=result.openai_moderation,
                processing_time_ms=result.processing_time_ms,
                escalation_required=result.requires_escalation,
                safe_alternative_provided=bool(result.safe_content),
                additional_data={
                    "validation_id": result.validation_id,
                    "sensitivity_level": request.sensitivity_level,
                    "content_length": len(request.content),
                    "has_user_message": bool(result.user_message)
                }
            )

            # Track specific result-based events
            if result.result == ValidationResult.FLAGGED:
                await self.analytics.track_safety_event(
                    event_type=SafetyEventType.CONTENT_FLAGGED,
                    user_id=request.user_id,
                    conversation_id=request.conversation_id,
                    animal_id=request.animal_id,
                    content=request.content,
                    risk_score=result.risk_score,
                    triggered_rules=triggered_rules,
                    safe_alternative_provided=bool(result.safe_content),
                    additional_data={"validation_id": result.validation_id}
                )

            elif result.result == ValidationResult.BLOCKED:
                await self.analytics.track_safety_event(
                    event_type=SafetyEventType.CONTENT_BLOCKED,
                    user_id=request.user_id,
                    conversation_id=request.conversation_id,
                    animal_id=request.animal_id,
                    content=request.content,
                    risk_score=result.risk_score,
                    triggered_rules=triggered_rules,
                    additional_data={"validation_id": result.validation_id}
                )

            # Track escalation events
            if result.requires_escalation:
                await self.analytics.track_safety_event(
                    event_type=SafetyEventType.ESCALATION_REQUIRED,
                    user_id=request.user_id,
                    conversation_id=request.conversation_id,
                    animal_id=request.animal_id,
                    content=request.content,
                    risk_score=result.risk_score,
                    triggered_rules=triggered_rules,
                    additional_data={
                        "validation_id": result.validation_id,
                        "escalation_reason": self._determine_escalation_reason(result)
                    }
                )

            # Track OpenAI moderation events
            if result.openai_moderation and result.openai_moderation.get("flagged", False):
                await self.analytics.track_safety_event(
                    event_type=SafetyEventType.OPENAI_MODERATION_TRIGGERED,
                    user_id=request.user_id,
                    conversation_id=request.conversation_id,
                    animal_id=request.animal_id,
                    content=request.content,
                    moderation_result=result.openai_moderation,
                    additional_data={
                        "validation_id": result.validation_id,
                        "flagged_categories": [
                            cat for cat, flagged in result.openai_moderation.get("categories", {}).items()
                            if flagged
                        ]
                    }
                )

            # Track guardrails rule triggers
            if result.guardrails_violations:
                for violation in result.guardrails_violations:
                    await self.analytics.track_safety_event(
                        event_type=SafetyEventType.GUARDRAIL_TRIGGERED,
                        user_id=request.user_id,
                        conversation_id=request.conversation_id,
                        animal_id=request.animal_id,
                        content=request.content,
                        triggered_rules=[violation.get("ruleId", "unknown")],
                        additional_data={
                            "validation_id": result.validation_id,
                            "rule_type": violation.get("ruleType"),
                            "severity": violation.get("severity"),
                            "confidence": violation.get("confidence"),
                            "violation_context": violation.get("context")
                        }
                    )

            # Track custom rule triggers separately for detailed analytics
            if result.guardrails_violations:
                await self.analytics.track_safety_event(
                    event_type=SafetyEventType.CUSTOM_RULE_TRIGGERED,
                    user_id=request.user_id,
                    conversation_id=request.conversation_id,
                    animal_id=request.animal_id,
                    content=request.content,
                    triggered_rules=triggered_rules,
                    additional_data={
                        "validation_id": result.validation_id,
                        "total_violations": len(result.guardrails_violations),
                        "max_severity": max(
                            (v.get("severity", "low") for v in result.guardrails_violations),
                            default="low"
                        )
                    }
                )

            # Track safe alternative provision
            if result.safe_content and result.safe_content != request.content:
                await self.analytics.track_safety_event(
                    event_type=SafetyEventType.SAFE_ALTERNATIVE_PROVIDED,
                    user_id=request.user_id,
                    conversation_id=request.conversation_id,
                    animal_id=request.animal_id,
                    content=request.content,
                    safe_alternative_provided=True,
                    additional_data={
                        "validation_id": result.validation_id,
                        "original_length": len(request.content),
                        "safe_length": len(result.safe_content),
                        "preservation_ratio": len(result.safe_content) / len(request.content)
                    }
                )

            # Track performance metrics
            await self.analytics.track_safety_event(
                event_type=SafetyEventType.PERFORMANCE_METRIC,
                user_id=request.user_id,
                conversation_id=request.conversation_id,
                animal_id=request.animal_id,
                processing_time_ms=result.processing_time_ms,
                additional_data={
                    "validation_id": result.validation_id,
                    "openai_enabled": self.config.openai_enabled,
                    "guardrails_enabled": self.config.guardrails_enabled,
                    "content_length": len(request.content),
                    "sensitivity_level": request.sensitivity_level
                }
            )

        except Exception as e:
            logger.error(f"Failed to track moderation analytics: {e}")
            # Don't fail the moderation process due to analytics issues

    def _determine_escalation_reason(self, result: ModerationResult) -> str:
        """
        Determine the primary reason for escalation.

        Args:
            result: Moderation result

        Returns:
            Primary escalation reason
        """
        # Check for critical guardrails violations
        if result.guardrails_violations:
            critical_violations = [v for v in result.guardrails_violations if v.get("severity") == "critical"]
            if critical_violations:
                return "critical_guardrails_violation"

        # Check for high-risk OpenAI categories
        if result.openai_moderation:
            categories = result.openai_moderation.get("categories", {})
            escalation_categories = ["sexual/minors", "self-harm/intent", "self-harm/instructions"]
            for category in escalation_categories:
                if categories.get(category, False):
                    return f"openai_{category.replace('/', '_')}"

        # Check risk score threshold
        if result.risk_score >= 0.8:
            return "high_risk_score"
        elif result.risk_score >= 0.6:
            return "medium_risk_score"

        return "unknown_escalation_trigger"


# Global moderator instance
_content_moderator: Optional[ContentModerator] = None


def get_content_moderator(config: Optional[ModerationConfig] = None) -> ContentModerator:
    """Get singleton ContentModerator instance."""
    global _content_moderator

    if _content_moderator is None:
        _content_moderator = ContentModerator(config)

    return _content_moderator


# Convenience functions for common operations
async def moderate_content(
    content: str,
    user_id: str,
    conversation_id: str,
    animal_id: Optional[str] = None,
    sensitivity_level: str = "standard"
) -> ModerationResult:
    """
    Convenience function for content moderation.

    Args:
        content: Content to moderate
        user_id: User ID
        conversation_id: Conversation ID
        animal_id: Optional animal ID for specific guardrails
        sensitivity_level: Moderation sensitivity level

    Returns:
        Moderation result
    """
    moderator = get_content_moderator()
    request = ModerationRequest(
        content=content,
        user_id=user_id,
        conversation_id=conversation_id,
        animal_id=animal_id,
        sensitivity_level=sensitivity_level
    )
    return await moderator.moderate_content(request)


async def validate_message_safety(
    message: str,
    user_id: str,
    conversation_id: str,
    animal_id: Optional[str] = None
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Quick safety validation for messages.

    Args:
        message: Message to validate
        user_id: User ID
        conversation_id: Conversation ID
        animal_id: Optional animal ID

    Returns:
        Tuple of (is_safe, user_message, safe_alternative)
    """
    result = await moderate_content(message, user_id, conversation_id, animal_id)

    is_safe = result.result in [ValidationResult.APPROVED, ValidationResult.FLAGGED]
    user_message = result.user_message
    safe_alternative = result.safe_content if result.result == ValidationResult.FLAGGED else None

    return is_safe, user_message, safe_alternative


class ContentModerationResponse:
    """Enhanced content moderation response for detailed feedback system."""

    def __init__(self, moderation_result: ModerationResult):
        """Initialize from ModerationResult."""
        self.result = moderation_result.result
        self.risk_score = moderation_result.risk_score
        self.requires_escalation = moderation_result.requires_escalation
        self.safe_content = moderation_result.safe_content
        self.user_message = moderation_result.user_message
        self.validation_id = moderation_result.validation_id
        self.processing_time_ms = moderation_result.processing_time_ms
        self.created_at = datetime.utcnow()

        # Enhanced fields for detailed feedback
        self.openai_moderation = moderation_result.openai_moderation
        self.guardrails_violations = moderation_result.guardrails_violations or []


def process_openai_moderation_for_enhanced_validation(
    moderation_results: Optional[Dict[str, Any]]
) -> Optional[OpenAIModerationResult]:
    """
    Process OpenAI moderation results into enhanced validation format.

    This function bridges the existing content moderation system with the new
    detailed guardrail feedback system by converting OpenAI results into
    the structured format expected by the enhanced validation response.

    Args:
        moderation_results: Raw OpenAI moderation results from content_moderator

    Returns:
        Structured OpenAI moderation result for enhanced validation or None
    """
    if not moderation_results or not isinstance(moderation_results, dict):
        return None

    try:
        # Extract basic moderation information
        flagged = moderation_results.get("flagged", False)
        model = moderation_results.get("model", "text-moderation-latest")

        # Process category results into structured format
        categories = []
        category_scores = moderation_results.get("category_scores", {})
        category_flags = moderation_results.get("categories", {})

        # Map OpenAI categories to our severity levels
        severity_mapping = {
            # Critical - immediate blocking
            "sexual/minors": "critical",
            "self-harm/intent": "critical",
            "self-harm/instructions": "critical",

            # High - strong warning/blocking
            "sexual": "high",
            "violence/graphic": "high",
            "hate/threatening": "high",
            "harassment/threatening": "high",

            # Medium - moderation required
            "violence": "medium",
            "hate": "medium",
            "harassment": "medium",
            "self-harm": "medium",

            # Low - monitoring only
            "harassment": "low"
        }

        for category_name, is_flagged in category_flags.items():
            if is_flagged:  # Only include flagged categories
                raw_score = category_scores.get(category_name, 0.0)
                severity = severity_mapping.get(category_name, "medium")

                # Convert raw score to confidence percentage
                confidence_score = min(raw_score * 100, 100.0)

                category_obj = OpenAIModerationCategory(
                    category=category_name,
                    severity=severity,
                    confidence_score=confidence_score,
                    raw_score=raw_score,
                    detected_at=datetime.utcnow().isoformat()
                )
                categories.append(category_obj)

        # Create structured OpenAI moderation result
        return OpenAIModerationResult(
            flagged=flagged,
            model=model,
            categories=categories
        )

    except Exception as e:
        logger.error(f"Failed to process OpenAI moderation results: {e}")
        return None


async def get_enhanced_moderation_response(
    content: str,
    user_id: str,
    conversation_id: str,
    animal_id: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None
) -> ContentModerationResponse:
    """
    Get enhanced moderation response compatible with detailed feedback system.

    This function provides the bridge between the existing content moderation
    system and the enhanced guardrail feedback system, ensuring that both
    OpenAI moderation results and guardrails violations are available in
    the format expected by the detailed validation components.

    Args:
        content: Content to moderate
        user_id: User ID for the request
        conversation_id: Conversation ID
        animal_id: Animal ID for context-specific moderation
        context: Additional context for moderation

    Returns:
        Enhanced moderation response with detailed rule information
    """
    try:
        # Create moderation request
        moderation_request = ModerationRequest(
            content=content,
            user_id=user_id,
            conversation_id=conversation_id,
            animal_id=animal_id,
            context=context or {},
            sensitivity_level="educational"  # Use educational mode for zoo context
        )

        # Get comprehensive moderation result
        moderator = get_content_moderator()
        moderation_result = await moderator.moderate_content(moderation_request)

        # Create enhanced response
        enhanced_response = ContentModerationResponse(moderation_result)

        logger.info(f"Enhanced moderation completed for validation {moderation_result.validation_id}: "
                   f"result={moderation_result.result.value}, "
                   f"openai_flagged={bool(moderation_result.openai_moderation and moderation_result.openai_moderation.get('flagged'))}, "
                   f"guardrails_violations={len(moderation_result.guardrails_violations or [])}")

        return enhanced_response

    except Exception as e:
        logger.error(f"Enhanced moderation failed: {e}")

        # Create fallback response
        from uuid import uuid4
        fallback_result = ModerationResult(
            validation_id=f"fallback_{uuid4().hex[:8]}",
            result=ValidationResult.ESCALATED,
            risk_score=1.0,
            requires_escalation=True,
            user_message="We're having trouble checking your message right now. Please try again.",
            processing_time_ms=0
        )

        return ContentModerationResponse(fallback_result)