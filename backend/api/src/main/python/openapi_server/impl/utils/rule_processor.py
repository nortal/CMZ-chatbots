"""
Rule Processing Utilities for Enhanced Guardrails Feedback.

This module provides utilities for processing, ranking, and filtering triggered
guardrail rules to provide meaningful feedback to users.

Key Features:
- Rule confidence filtering (>=50% threshold)
- Severity-based ranking (critical > high > medium > low)
- Rule type classification and validation
- Context generation for triggered rules
- User-friendly message formatting
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from enum import Enum
from dataclasses import dataclass

from ..models.triggered_rule import TriggeredRule
from ..models.triggered_rules_summary import TriggeredRulesSummary
from ..models.validation_summary import ValidationSummary
from ..models.open_ai_moderation_result import OpenAIModerationResult
from ..models.open_ai_moderation_category import OpenAIModerationCategory

# Configure logging
logger = logging.getLogger(__name__)


class RuleType(Enum):
    """Enumeration of guardrail rule types."""
    ALWAYS = "ALWAYS"
    NEVER = "NEVER"
    ENCOURAGE = "ENCOURAGE"
    DISCOURAGE = "DISCOURAGE"


class RuleSeverity(Enum):
    """Enumeration of rule severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    @property
    def priority(self) -> int:
        """Get numeric priority for sorting (higher = more severe)."""
        return {
            RuleSeverity.LOW: 1,
            RuleSeverity.MEDIUM: 2,
            RuleSeverity.HIGH: 3,
            RuleSeverity.CRITICAL: 4
        }[self]


class RuleCategory(Enum):
    """Enumeration of rule categories."""
    SAFETY = "safety"
    EDUCATIONAL = "educational"
    AGE_APPROPRIATE = "age-appropriate"
    BEHAVIORAL = "behavioral"
    CONTENT_QUALITY = "content-quality"
    PRIVACY = "privacy"


@dataclass
class RuleMatch:
    """Represents a rule match with context."""
    rule_id: str
    rule_text: str
    rule_type: RuleType
    category: RuleCategory
    severity: RuleSeverity
    confidence_score: float
    trigger_context: Optional[str] = None
    keywords_matched: Optional[List[str]] = None
    pattern_matched: Optional[str] = None


def filter_rules_by_confidence(
    rule_matches: List[RuleMatch],
    min_confidence: float = 50.0
) -> List[RuleMatch]:
    """
    Filter rules by minimum confidence threshold.

    Args:
        rule_matches: List of rule matches to filter
        min_confidence: Minimum confidence score (default: 50.0)

    Returns:
        List of rule matches that meet confidence threshold
    """
    filtered = [
        rule for rule in rule_matches
        if rule.confidence_score >= min_confidence
    ]

    logger.debug(
        f"Filtered {len(rule_matches)} rules to {len(filtered)} "
        f"with confidence >= {min_confidence}"
    )

    return filtered


def rank_rules_by_severity_and_confidence(
    rule_matches: List[RuleMatch]
) -> List[RuleMatch]:
    """
    Rank rules by severity (highest first) then confidence (highest first).

    Args:
        rule_matches: List of rule matches to rank

    Returns:
        Sorted list with most severe and confident rules first
    """
    def sort_key(rule: RuleMatch) -> Tuple[int, float]:
        return (-rule.severity.priority, -rule.confidence_score)

    ranked = sorted(rule_matches, key=sort_key)

    logger.debug(f"Ranked {len(rule_matches)} rules by severity and confidence")

    return ranked


def generate_trigger_context(
    rule_match: RuleMatch,
    content: str,
    max_length: int = 500
) -> str:
    """
    Generate contextual information about what triggered a rule.

    Args:
        rule_match: The rule that was triggered
        content: Original content that was validated
        max_length: Maximum length of context string

    Returns:
        Context string explaining what triggered the rule
    """
    context_parts = []

    # Add keywords if available
    if rule_match.keywords_matched:
        keywords_str = ", ".join(rule_match.keywords_matched[:5])  # Limit to 5
        context_parts.append(f"Matched keywords: {keywords_str}")

    # Add pattern if available
    if rule_match.pattern_matched:
        context_parts.append(f"Pattern: {rule_match.pattern_matched}")

    # Add rule type context
    if rule_match.rule_type == RuleType.NEVER:
        context_parts.append("Content violates 'never' rule")
    elif rule_match.rule_type == RuleType.ALWAYS:
        context_parts.append("Content missing required element")
    elif rule_match.rule_type == RuleType.DISCOURAGE:
        context_parts.append("Content contains discouraged elements")

    # Combine and truncate
    context = "; ".join(context_parts)
    if len(context) > max_length:
        context = context[:max_length-3] + "..."

    return context or "Rule triggered by content analysis"


def generate_user_friendly_message(
    rule_match: RuleMatch,
    age_group: Optional[str] = None
) -> str:
    """
    Generate user-friendly message explaining why content was flagged.

    Args:
        rule_match: The rule that was triggered
        age_group: Optional age group for age-appropriate messaging

    Returns:
        User-friendly explanation message
    """
    messages = {
        RuleCategory.SAFETY: [
            "Let's keep our conversation safe and positive!",
            "We focus on safe topics about animals and nature.",
            "Safety first! Let's talk about something else."
        ],
        RuleCategory.EDUCATIONAL: [
            "Let's explore this topic in an educational way!",
            "Here's a great learning opportunity about animals!",
            "Let's discover something educational together!"
        ],
        RuleCategory.AGE_APPROPRIATE: [
            "This topic is better for older students.",
            "Let's find something perfect for your age!",
            "Here's something more suitable for you!"
        ],
        RuleCategory.BEHAVIORAL: [
            "Let's stay kind and respectful in our conversation.",
            "We encourage positive interactions!",
            "Let's keep our chat friendly and helpful."
        ],
        RuleCategory.CONTENT_QUALITY: [
            "Let's make our conversation clear and helpful!",
            "We can explore this topic more effectively.",
            "Let's find a better way to discuss this!"
        ],
        RuleCategory.PRIVACY: [
            "Let's keep personal information private and safe.",
            "We protect privacy in our conversations.",
            "Let's talk about general topics instead!"
        ]
    }

    # Select appropriate message based on category and severity
    category_messages = messages.get(rule_match.category, messages[RuleCategory.SAFETY])

    # Choose message based on severity
    if rule_match.severity == RuleSeverity.CRITICAL:
        return category_messages[2]  # Most serious message
    elif rule_match.severity == RuleSeverity.HIGH:
        return category_messages[1]  # Moderate message
    else:
        return category_messages[0]  # Gentle message


def create_triggered_rule_summary(
    custom_rules: List[RuleMatch],
    openai_moderation: Optional[OpenAIModerationResult] = None
) -> TriggeredRulesSummary:
    """
    Create a summary of all triggered rules.

    Args:
        custom_rules: List of triggered custom guardrail rules
        openai_moderation: Optional OpenAI moderation results

    Returns:
        TriggeredRulesSummary object
    """
    # Calculate total triggered
    total_triggered = len(custom_rules)
    if openai_moderation and openai_moderation.flagged:
        total_triggered += len(openai_moderation.categories or [])

    # Find highest severity
    highest_severity = "none"
    if custom_rules:
        max_severity = max(rule.severity for rule in custom_rules)
        highest_severity = max_severity.value

    # Check OpenAI moderation for higher severity
    if openai_moderation and openai_moderation.categories:
        for category in openai_moderation.categories:
            if category.severity == "critical":
                highest_severity = "critical"
                break
            elif category.severity == "high" and highest_severity not in ["critical"]:
                highest_severity = "high"
            elif category.severity == "medium" and highest_severity not in ["critical", "high"]:
                highest_severity = "medium"

    # Convert custom rules to TriggeredRule objects
    triggered_rule_objects = []
    for rule in custom_rules:
        triggered_rule = TriggeredRule(
            rule_id=rule.rule_id,
            rule_text=rule.rule_text,
            rule_type=rule.rule_type.value,
            category=rule.category.value,
            severity=rule.severity.value,
            confidence_score=rule.confidence_score,
            trigger_context=rule.trigger_context,
            user_message=generate_user_friendly_message(rule),
            detected_at=datetime.utcnow(),
            priority=rule.severity.priority * 25  # Convert to 0-100 scale
        )
        triggered_rule_objects.append(triggered_rule)

    return TriggeredRulesSummary(
        total_triggered=total_triggered,
        highest_severity=highest_severity,
        openai_moderation=openai_moderation,
        custom_guardrails=triggered_rule_objects
    )


def create_validation_summary(
    triggered_rules: List[RuleMatch],
    openai_flagged: bool = False
) -> ValidationSummary:
    """
    Create a high-level validation summary.

    Args:
        triggered_rules: List of triggered rules
        openai_flagged: Whether OpenAI moderation flagged content

    Returns:
        ValidationSummary object
    """
    # Count blocking violations (NEVER rules with medium+ severity)
    blocking_violations = sum(
        1 for rule in triggered_rules
        if rule.rule_type == RuleType.NEVER and rule.severity.priority >= 2
    )

    # Count warning violations (DISCOURAGE rules or low severity)
    warning_violations = sum(
        1 for rule in triggered_rules
        if rule.rule_type == RuleType.DISCOURAGE or rule.severity == RuleSeverity.LOW
    )

    # Determine if escalation is required
    requires_escalation = (
        openai_flagged or
        any(rule.severity == RuleSeverity.CRITICAL for rule in triggered_rules)
    )

    # Determine age group approval
    age_group_approved = "elementary"
    if any(rule.severity.priority >= 3 for rule in triggered_rules):  # high or critical
        age_group_approved = "adult"
    elif any(rule.severity.priority >= 2 for rule in triggered_rules):  # medium
        age_group_approved = "high"
    elif any(rule.category == RuleCategory.AGE_APPROPRIATE for rule in triggered_rules):
        age_group_approved = "middle"

    return ValidationSummary(
        requires_escalation=requires_escalation,
        blocking_violations=blocking_violations,
        warning_violations=warning_violations,
        age_group_approved=age_group_approved
    )


def process_triggered_rules(
    rule_matches: List[RuleMatch],
    openai_moderation: Optional[OpenAIModerationResult] = None,
    min_confidence: float = 50.0
) -> Tuple[TriggeredRulesSummary, ValidationSummary]:
    """
    Process triggered rules into structured summary objects.

    Args:
        rule_matches: List of rule matches from guardrails evaluation
        openai_moderation: Optional OpenAI moderation results
        min_confidence: Minimum confidence threshold for inclusion

    Returns:
        Tuple of (TriggeredRulesSummary, ValidationSummary)
    """
    # Filter and rank rules
    filtered_rules = filter_rules_by_confidence(rule_matches, min_confidence)
    ranked_rules = rank_rules_by_severity_and_confidence(filtered_rules)

    # Generate context for each rule
    for rule in ranked_rules:
        if not rule.trigger_context:
            rule.trigger_context = generate_trigger_context(rule, "")

    # Create summaries
    rules_summary = create_triggered_rule_summary(ranked_rules, openai_moderation)
    validation_summary = create_validation_summary(
        ranked_rules,
        openai_moderation.flagged if openai_moderation else False
    )

    logger.info(
        f"Processed {len(rule_matches)} rule matches into "
        f"{len(ranked_rules)} filtered rules with "
        f"highest severity: {rules_summary.highest_severity}"
    )

    return rules_summary, validation_summary