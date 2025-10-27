"""
ContentValidation model mapping for CMZ Chatbots safety system.

This module provides mapping between OpenAPI generated ContentValidation models
and DynamoDB data structures for content moderation and validation tracking.

Key Features:
- Maps OpenAPI models to DynamoDB-compatible format
- Handles content moderation results and validation tracking
- Supports conversation-level and message-level validation
- Provides safety analytics and audit trail management
- Integrates with OpenAI content moderation API results
"""

import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from enum import Enum

from ..utils.dynamo import (
    model_to_json_keyed_dict, ensure_pk, now_iso,
    to_ddb, from_ddb
)
from ..utils.safety_dynamo import get_safety_dynamo_client

# Configure logging
logger = logging.getLogger(__name__)


class ValidationResult(Enum):
    """Content validation result types."""
    APPROVED = "approved"
    FLAGGED = "flagged"
    BLOCKED = "blocked"
    ESCALATED = "escalated"


class ModerationCategory(Enum):
    """OpenAI moderation categories."""
    HATE = "hate"
    HATE_THREATENING = "hate/threatening"
    HARASSMENT = "harassment"
    HARASSMENT_THREATENING = "harassment/threatening"
    SELF_HARM = "self-harm"
    SELF_HARM_INTENT = "self-harm/intent"
    SELF_HARM_INSTRUCTIONS = "self-harm/instructions"
    SEXUAL = "sexual"
    SEXUAL_MINORS = "sexual/minors"
    VIOLENCE = "violence"
    VIOLENCE_GRAPHIC = "violence/graphic"


class ContentValidationMapper:
    """Maps ContentValidation OpenAPI models to DynamoDB format."""

    def __init__(self):
        """Initialize the mapper with safety client."""
        self.safety_client = get_safety_dynamo_client()

    def to_dynamodb_format(self, validation_model: Any) -> Dict[str, Any]:
        """
        Convert OpenAPI ContentValidation model to DynamoDB format.

        Args:
            validation_model: OpenAPI generated ContentValidation model

        Returns:
            Dictionary suitable for DynamoDB storage
        """
        try:
            # Convert model to dictionary
            if hasattr(validation_model, 'to_dict'):
                validation_dict = validation_model.to_dict()
            else:
                validation_dict = model_to_json_keyed_dict(validation_model)

            # Ensure primary key exists
            ensure_pk(validation_dict, "validationId")

            # Add audit timestamps
            current_time = now_iso()
            validation_dict.setdefault("createdAt", current_time)
            validation_dict["lastUpdated"] = current_time

            # Process moderation results if present
            if "moderationResults" in validation_dict and validation_dict["moderationResults"]:
                validation_dict["moderationResults"] = self._process_moderation_results(
                    validation_dict["moderationResults"]
                )

            # Process guardrails violations if present
            if "guardrailsViolations" in validation_dict and validation_dict["guardrailsViolations"]:
                validation_dict["guardrailsViolations"] = self._process_guardrails_violations(
                    validation_dict["guardrailsViolations"]
                )

            # Add computed fields
            validation_dict["hasViolations"] = self._has_violations(validation_dict)
            validation_dict["riskScore"] = self._calculate_risk_score(validation_dict)
            validation_dict["requiresEscalation"] = self._requires_escalation(validation_dict)

            # Ensure required fields have defaults
            validation_dict.setdefault("conversationId", "")
            validation_dict.setdefault("messageId", "")
            validation_dict.setdefault("userId", "")
            validation_dict.setdefault("animalId", "")
            validation_dict.setdefault("result", ValidationResult.APPROVED.value)

            # Convert to DynamoDB format
            return to_ddb(validation_dict)

        except Exception as e:
            logger.error(f"Failed to convert ContentValidation to DynamoDB format: {e}")
            raise ValueError(f"Invalid ContentValidation model: {e}")

    def from_dynamodb_format(self, ddb_item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert DynamoDB item to OpenAPI ContentValidation format.

        Args:
            ddb_item: DynamoDB item dictionary

        Returns:
            Dictionary suitable for OpenAPI response
        """
        try:
            # Convert from DynamoDB format
            validation_dict = from_ddb(ddb_item)

            # Process moderation results for API response
            if "moderationResults" in validation_dict and validation_dict["moderationResults"]:
                validation_dict["moderationResults"] = self._format_moderation_for_api(
                    validation_dict["moderationResults"]
                )

            # Process guardrails violations for API response
            if "guardrailsViolations" in validation_dict and validation_dict["guardrailsViolations"]:
                validation_dict["guardrailsViolations"] = self._format_violations_for_api(
                    validation_dict["guardrailsViolations"]
                )

            # Remove internal computed fields
            internal_fields = ["hasViolations", "riskScore", "requiresEscalation", "lastUpdated"]
            for field in internal_fields:
                validation_dict.pop(field, None)

            return validation_dict

        except Exception as e:
            logger.error(f"Failed to convert DynamoDB item to ContentValidation: {e}")
            raise ValueError(f"Invalid DynamoDB item: {e}")

    def _process_moderation_results(self, moderation_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and validate OpenAI moderation results.

        Args:
            moderation_results: Raw moderation results from OpenAI

        Returns:
            Processed and validated moderation results
        """
        processed = {
            "flagged": moderation_results.get("flagged", False),
            "categories": {},
            "categoryScores": {},
            "model": moderation_results.get("model", "text-moderation-latest"),
            "processedAt": now_iso()
        }

        # Process categories
        categories = moderation_results.get("categories", {})
        for category, flagged in categories.items():
            if category in [cat.value for cat in ModerationCategory]:
                processed["categories"][category] = bool(flagged)
            else:
                logger.warning(f"Unknown moderation category: {category}")

        # Process category scores
        category_scores = moderation_results.get("category_scores", {})
        for category, score in category_scores.items():
            if category in [cat.value for cat in ModerationCategory]:
                try:
                    processed["categoryScores"][category] = max(0.0, min(1.0, float(score)))
                except (ValueError, TypeError):
                    logger.warning(f"Invalid score for category {category}: {score}")
                    processed["categoryScores"][category] = 0.0
            else:
                logger.warning(f"Unknown score category: {category}")

        return processed

    def _process_guardrails_violations(self, violations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process and validate guardrails violations.

        Args:
            violations: List of guardrails violation dictionaries

        Returns:
            Processed and validated violations
        """
        processed_violations = []

        for i, violation in enumerate(violations):
            try:
                processed_violation = {
                    "ruleId": violation.get("ruleId", f"rule_{i}"),
                    "ruleType": violation.get("ruleType", "DISCOURAGE"),
                    "violationType": violation.get("violationType", "content"),
                    "severity": violation.get("severity", "medium"),
                    "confidence": max(0.0, min(1.0, float(violation.get("confidence", 0.0)))),
                    "message": violation.get("message", "Content violates guardrails"),
                    "context": violation.get("context", ""),
                    "detectedAt": violation.get("detectedAt", now_iso())
                }

                # Validate rule type
                valid_types = ["ALWAYS", "NEVER", "ENCOURAGE", "DISCOURAGE"]
                if processed_violation["ruleType"] not in valid_types:
                    logger.warning(f"Invalid rule type: {processed_violation['ruleType']}")
                    processed_violation["ruleType"] = "DISCOURAGE"

                # Validate severity
                valid_severities = ["low", "medium", "high", "critical"]
                if processed_violation["severity"] not in valid_severities:
                    logger.warning(f"Invalid severity: {processed_violation['severity']}")
                    processed_violation["severity"] = "medium"

                processed_violations.append(processed_violation)

            except Exception as e:
                logger.error(f"Failed to process violation {i}: {e}")
                continue

        return processed_violations

    def _has_violations(self, validation_dict: Dict[str, Any]) -> bool:
        """
        Check if validation has any violations.

        Args:
            validation_dict: Validation dictionary

        Returns:
            True if violations exist
        """
        # Check moderation flagging
        moderation = validation_dict.get("moderationResults", {})
        if moderation.get("flagged", False):
            return True

        # Check guardrails violations
        violations = validation_dict.get("guardrailsViolations", [])
        if violations and len(violations) > 0:
            return True

        return False

    def _calculate_risk_score(self, validation_dict: Dict[str, Any]) -> float:
        """
        Calculate overall risk score based on moderation and guardrails.

        Args:
            validation_dict: Validation dictionary

        Returns:
            Risk score between 0.0 and 1.0
        """
        risk_score = 0.0

        # Factor in moderation scores
        moderation = validation_dict.get("moderationResults", {})
        category_scores = moderation.get("categoryScores", {})

        if category_scores:
            # Weight certain categories higher for children's content
            weights = {
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
                weight = weights.get(category, 0.5)
                weighted_score += score * weight
                total_weight += weight

            if total_weight > 0:
                risk_score = max(risk_score, weighted_score / total_weight)

        # Factor in guardrails violations
        violations = validation_dict.get("guardrailsViolations", [])
        if violations:
            severity_scores = {"low": 0.25, "medium": 0.5, "high": 0.75, "critical": 1.0}
            violation_score = 0.0

            for violation in violations:
                severity = violation.get("severity", "medium")
                confidence = violation.get("confidence", 0.0)
                violation_score = max(violation_score, severity_scores.get(severity, 0.5) * confidence)

            risk_score = max(risk_score, violation_score)

        return max(0.0, min(1.0, risk_score))

    def _requires_escalation(self, validation_dict: Dict[str, Any]) -> bool:
        """
        Determine if validation requires human escalation.

        Args:
            validation_dict: Validation dictionary

        Returns:
            True if escalation required
        """
        risk_score = validation_dict.get("riskScore", 0.0)

        # High risk score always requires escalation
        if risk_score >= 0.8:
            return True

        # Critical violations require escalation
        violations = validation_dict.get("guardrailsViolations", [])
        for violation in violations:
            if violation.get("severity") == "critical":
                return True

        # Certain moderation categories require escalation
        moderation = validation_dict.get("moderationResults", {})
        categories = moderation.get("categories", {})
        escalation_categories = ["sexual/minors", "self-harm/intent", "self-harm/instructions"]

        for category in escalation_categories:
            if categories.get(category, False):
                return True

        return False

    def _format_moderation_for_api(self, moderation_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format moderation results for API response.

        Args:
            moderation_results: Processed moderation results

        Returns:
            Moderation results formatted for API
        """
        # Remove internal processing fields, keep only API-relevant data
        formatted = {
            "flagged": moderation_results.get("flagged", False),
            "categories": moderation_results.get("categories", {}),
            "categoryScores": moderation_results.get("categoryScores", {})
        }

        # Only include flagged categories in response to reduce payload
        if formatted["flagged"]:
            flagged_categories = {
                cat: flagged for cat, flagged in formatted["categories"].items() if flagged
            }
            formatted["categories"] = flagged_categories

        return formatted

    def _format_violations_for_api(self, violations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format guardrails violations for API response.

        Args:
            violations: Processed violations list

        Returns:
            Violations formatted for API
        """
        formatted_violations = []

        for violation in violations:
            # Only include high-confidence violations in API response
            if violation.get("confidence", 0.0) >= 0.5:
                formatted_violation = {
                    "ruleType": violation.get("ruleType"),
                    "severity": violation.get("severity"),
                    "message": violation.get("message")
                }

                # Include context for medium+ severity violations
                if violation.get("severity") in ["medium", "high", "critical"]:
                    formatted_violation["context"] = violation.get("context", "")

                formatted_violations.append(formatted_violation)

        return formatted_violations

    def validate_content_validation(self, validation_dict: Dict[str, Any]) -> List[str]:
        """
        Validate content validation configuration.

        Args:
            validation_dict: Validation dictionary to validate

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Check required fields
        required_fields = ["validationId", "conversationId", "result"]
        for field in required_fields:
            if field not in validation_dict or not validation_dict[field]:
                errors.append(f"Missing required field: {field}")

        # Validate result value
        result = validation_dict.get("result")
        valid_results = [res.value for res in ValidationResult]
        if result and result not in valid_results:
            errors.append(f"Invalid result '{result}', must be one of {valid_results}")

        # Validate moderation results structure
        moderation = validation_dict.get("moderationResults")
        if moderation:
            if not isinstance(moderation, dict):
                errors.append("moderationResults must be a dictionary")
            elif "flagged" not in moderation:
                errors.append("moderationResults missing required 'flagged' field")

        # Validate violations structure
        violations = validation_dict.get("guardrailsViolations")
        if violations:
            if not isinstance(violations, list):
                errors.append("guardrailsViolations must be a list")
            else:
                for i, violation in enumerate(violations):
                    violation_errors = self._validate_violation(violation, i)
                    errors.extend(violation_errors)

        return errors

    def _validate_violation(self, violation: Dict[str, Any], index: int) -> List[str]:
        """
        Validate a single guardrails violation.

        Args:
            violation: Violation dictionary to validate
            index: Violation index for error reporting

        Returns:
            List of validation errors for this violation
        """
        errors = []

        # Check required violation fields
        required_fields = ["ruleType", "severity", "message"]
        for field in required_fields:
            if field not in violation or not violation[field]:
                errors.append(f"Violation {index}: Missing required field '{field}'")

        # Validate confidence score
        confidence = violation.get("confidence")
        if confidence is not None:
            try:
                conf_float = float(confidence)
                if conf_float < 0.0 or conf_float > 1.0:
                    errors.append(f"Violation {index}: Confidence must be between 0.0 and 1.0")
            except (ValueError, TypeError):
                errors.append(f"Violation {index}: Confidence must be a number")

        return errors


# Global mapper instance
_content_validation_mapper: Optional[ContentValidationMapper] = None


def get_content_validation_mapper() -> ContentValidationMapper:
    """Get singleton ContentValidationMapper instance."""
    global _content_validation_mapper

    if _content_validation_mapper is None:
        _content_validation_mapper = ContentValidationMapper()

    return _content_validation_mapper


# Convenience functions for common operations
def map_to_dynamodb(validation_model: Any) -> Dict[str, Any]:
    """Convenience function to map validation model to DynamoDB format."""
    mapper = get_content_validation_mapper()
    return mapper.to_dynamodb_format(validation_model)


def map_from_dynamodb(ddb_item: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function to map DynamoDB item to API format."""
    mapper = get_content_validation_mapper()
    return mapper.from_dynamodb_format(ddb_item)


def validate_content_validation(validation_dict: Dict[str, Any]) -> List[str]:
    """Convenience function to validate content validation configuration."""
    mapper = get_content_validation_mapper()
    return mapper.validate_content_validation(validation_dict)