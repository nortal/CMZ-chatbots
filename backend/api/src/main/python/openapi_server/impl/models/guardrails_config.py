"""
GuardrailsConfig model mapping for CMZ Chatbots safety system.

This module provides mapping between OpenAPI generated GuardrailsConfig models
and DynamoDB data structures for guardrails configuration management.

Key Features:
- Maps OpenAPI models to DynamoDB-compatible format
- Handles guardrails rule processing and validation
- Supports animal-specific and global configurations
- Provides rule priority and inheritance logic
"""

import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from ..utils.dynamo import (
    model_to_json_keyed_dict, ensure_pk, now_iso,
    to_ddb, from_ddb
)
from ..utils.safety_dynamo import get_safety_dynamo_client

# Configure logging
logger = logging.getLogger(__name__)


class GuardrailsConfigMapper:
    """Maps GuardrailsConfig OpenAPI models to DynamoDB format."""

    def __init__(self):
        """Initialize the mapper with safety client."""
        self.safety_client = get_safety_dynamo_client()

    def to_dynamodb_format(self, config_model: Any) -> Dict[str, Any]:
        """
        Convert OpenAPI GuardrailsConfig model to DynamoDB format.

        Args:
            config_model: OpenAPI generated GuardrailsConfig model

        Returns:
            Dictionary suitable for DynamoDB storage
        """
        try:
            # Convert model to dictionary
            if hasattr(config_model, 'to_dict'):
                config_dict = config_model.to_dict()
            else:
                config_dict = model_to_json_keyed_dict(config_model)

            # Ensure primary key exists
            ensure_pk(config_dict, "configId")

            # Add audit timestamps
            current_time = now_iso()
            config_dict.setdefault("createdAt", current_time)
            config_dict["lastUpdated"] = current_time

            # Process rules if present
            if "rules" in config_dict and config_dict["rules"]:
                config_dict["rules"] = self._process_rules(config_dict["rules"])

            # Add computed fields
            config_dict["ruleCount"] = len(config_dict.get("rules", []))
            config_dict["isActive"] = config_dict.get("isActive", True)

            # Convert to DynamoDB format
            return to_ddb(config_dict)

        except Exception as e:
            logger.error(f"Failed to convert GuardrailsConfig to DynamoDB format: {e}")
            raise ValueError(f"Invalid GuardrailsConfig model: {e}")

    def from_dynamodb_format(self, ddb_item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert DynamoDB item to OpenAPI GuardrailsConfig format.

        Args:
            ddb_item: DynamoDB item dictionary

        Returns:
            Dictionary suitable for OpenAPI response
        """
        try:
            # Convert from DynamoDB format
            config_dict = from_ddb(ddb_item)

            # Process rules for API response
            if "rules" in config_dict and config_dict["rules"]:
                config_dict["rules"] = self._format_rules_for_api(config_dict["rules"])

            # Remove internal fields
            internal_fields = ["ruleCount", "lastUpdated"]
            for field in internal_fields:
                config_dict.pop(field, None)

            return config_dict

        except Exception as e:
            logger.error(f"Failed to convert DynamoDB item to GuardrailsConfig: {e}")
            raise ValueError(f"Invalid DynamoDB item: {e}")

    def _process_rules(self, rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process and validate guardrails rules.

        Args:
            rules: List of rule dictionaries

        Returns:
            Processed and validated rules
        """
        processed_rules = []

        for i, rule in enumerate(rules):
            try:
                processed_rule = {
                    "ruleId": rule.get("ruleId", f"rule_{i}"),
                    "type": rule.get("type", "DISCOURAGE"),
                    "rule": rule.get("rule", ""),
                    "priority": rule.get("priority", 50),
                    "isActive": rule.get("isActive", True),
                    "category": rule.get("category", "general"),
                    "severity": rule.get("severity", "medium")
                }

                # Validate rule type
                valid_types = ["ALWAYS", "NEVER", "ENCOURAGE", "DISCOURAGE"]
                if processed_rule["type"] not in valid_types:
                    logger.warning(f"Invalid rule type: {processed_rule['type']}, defaulting to DISCOURAGE")
                    processed_rule["type"] = "DISCOURAGE"

                # Validate priority range
                priority = processed_rule["priority"]
                if not isinstance(priority, int) or priority < 0 or priority > 100:
                    logger.warning(f"Invalid priority: {priority}, defaulting to 50")
                    processed_rule["priority"] = 50

                # Ensure rule text is not empty
                if not processed_rule["rule"].strip():
                    logger.warning(f"Empty rule text for rule {processed_rule['ruleId']}")
                    continue

                processed_rules.append(processed_rule)

            except Exception as e:
                logger.error(f"Failed to process rule {i}: {e}")
                continue

        return processed_rules

    def _format_rules_for_api(self, rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format rules for API response.

        Args:
            rules: List of processed rule dictionaries

        Returns:
            Rules formatted for API response
        """
        formatted_rules = []

        for rule in rules:
            # Only include active rules in API response unless explicitly requested
            if not rule.get("isActive", True):
                continue

            formatted_rule = {
                "type": rule.get("type"),
                "rule": rule.get("rule"),
                "priority": rule.get("priority", 50)
            }

            # Include optional fields if present
            if "category" in rule:
                formatted_rule["category"] = rule["category"]

            formatted_rules.append(formatted_rule)

        # Sort by priority (highest first)
        formatted_rules.sort(key=lambda x: x.get("priority", 0), reverse=True)

        return formatted_rules

    def validate_config(self, config_dict: Dict[str, Any]) -> List[str]:
        """
        Validate guardrails configuration.

        Args:
            config_dict: Configuration dictionary to validate

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Check required fields
        required_fields = ["configId", "animalId"]
        for field in required_fields:
            if field not in config_dict or not config_dict[field]:
                errors.append(f"Missing required field: {field}")

        # Validate animalId format
        animal_id = config_dict.get("animalId")
        if animal_id and not isinstance(animal_id, str):
            errors.append("animalId must be a string")

        # Validate rules
        rules = config_dict.get("rules", [])
        if not isinstance(rules, list):
            errors.append("rules must be a list")
        elif len(rules) == 0:
            errors.append("At least one rule is required")
        else:
            for i, rule in enumerate(rules):
                rule_errors = self._validate_rule(rule, i)
                errors.extend(rule_errors)

        return errors

    def _validate_rule(self, rule: Dict[str, Any], index: int) -> List[str]:
        """
        Validate a single guardrails rule.

        Args:
            rule: Rule dictionary to validate
            index: Rule index for error reporting

        Returns:
            List of validation errors for this rule
        """
        errors = []

        # Check required rule fields
        required_fields = ["type", "rule"]
        for field in required_fields:
            if field not in rule or not rule[field]:
                errors.append(f"Rule {index}: Missing required field '{field}'")

        # Validate rule type
        valid_types = ["ALWAYS", "NEVER", "ENCOURAGE", "DISCOURAGE"]
        rule_type = rule.get("type")
        if rule_type and rule_type not in valid_types:
            errors.append(f"Rule {index}: Invalid type '{rule_type}', must be one of {valid_types}")

        # Validate priority
        priority = rule.get("priority")
        if priority is not None:
            if not isinstance(priority, int) or priority < 0 or priority > 100:
                errors.append(f"Rule {index}: Priority must be an integer between 0 and 100")

        # Validate rule text length
        rule_text = rule.get("rule", "")
        if len(rule_text.strip()) < 5:
            errors.append(f"Rule {index}: Rule text must be at least 5 characters")
        elif len(rule_text) > 500:
            errors.append(f"Rule {index}: Rule text must be less than 500 characters")

        return errors

    def merge_configs(self, animal_config: Dict[str, Any], global_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge animal-specific config with global config.

        Args:
            animal_config: Animal-specific guardrails configuration
            global_config: Global guardrails configuration

        Returns:
            Merged configuration with proper rule precedence
        """
        try:
            # Start with global config as base
            merged_config = global_config.copy()

            # Override with animal-specific settings
            merged_config.update({
                "configId": animal_config.get("configId"),
                "animalId": animal_config.get("animalId"),
                "lastUpdated": animal_config.get("lastUpdated", now_iso())
            })

            # Merge rules with proper precedence
            global_rules = global_config.get("rules", [])
            animal_rules = animal_config.get("rules", [])

            # Animal rules take precedence, then global rules
            all_rules = animal_rules + global_rules

            # Remove duplicates (animal rules override global rules with same category)
            seen_categories = set()
            merged_rules = []

            for rule in all_rules:
                category = rule.get("category", "general")
                if category not in seen_categories:
                    merged_rules.append(rule)
                    seen_categories.add(category)

            merged_config["rules"] = merged_rules
            merged_config["ruleCount"] = len(merged_rules)

            return merged_config

        except Exception as e:
            logger.error(f"Failed to merge configs: {e}")
            # Fallback to animal config if merge fails
            return animal_config


# Global mapper instance
_guardrails_config_mapper: Optional[GuardrailsConfigMapper] = None


def get_guardrails_config_mapper() -> GuardrailsConfigMapper:
    """Get singleton GuardrailsConfigMapper instance."""
    global _guardrails_config_mapper

    if _guardrails_config_mapper is None:
        _guardrails_config_mapper = GuardrailsConfigMapper()

    return _guardrails_config_mapper


# Convenience functions for common operations
def map_to_dynamodb(config_model: Any) -> Dict[str, Any]:
    """Convenience function to map config model to DynamoDB format."""
    mapper = get_guardrails_config_mapper()
    return mapper.to_dynamodb_format(config_model)


def map_from_dynamodb(ddb_item: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function to map DynamoDB item to API format."""
    mapper = get_guardrails_config_mapper()
    return mapper.from_dynamodb_format(ddb_item)


def validate_guardrails_config(config_dict: Dict[str, Any]) -> List[str]:
    """Convenience function to validate guardrails configuration."""
    mapper = get_guardrails_config_mapper()
    return mapper.validate_config(config_dict)