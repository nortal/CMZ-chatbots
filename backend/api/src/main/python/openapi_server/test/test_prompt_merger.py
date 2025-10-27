"""
Unit tests for prompt merging functionality.
Tests the logic that combines personality and guardrail prompts into unified system prompts.

Test-Driven Development (TDD) approach:
- These tests MUST FAIL initially before implementation
- Implement prompt_merger.py to make tests pass
- Refactor while maintaining test success
"""

import pytest
from unittest.mock import Mock, patch

from openapi_server.impl.utils.prompt_merger import (
    PromptMerger,
    merge_assistant_prompt,
    validate_assistant_prompt
)


class TestPromptMerger:
    """Test suite for PromptMerger class functionality."""

    def setup_method(self):
        """Set up test data before each test."""
        self.personality_data = {
            "name": "Friendly Lion",
            "systemPrompt": "You are Leo, a majestic lion who loves to teach children about the savanna.",
            "traits": ["confident", "educational", "friendly"],
            "communicationStyle": "Use simple language appropriate for children aged 5-12.",
            "knowledge": "African wildlife, savanna ecosystem, lion behavior"
        }

        self.guardrail_data = {
            "name": "Child Safety Guardrails",
            "systemPrompt": "Always maintain child-appropriate content and language.",
            "rules": [
                "No scary or violent content",
                "No discussion of hunting or predation",
                "Keep responses under 150 words",
                "Use encouraging and positive language"
            ],
            "restrictions": [
                "Avoid topics: death, injury, scary sounds",
                "Redirect inappropriate questions to educational topics"
            ]
        }

        self.expected_merged_sections = [
            "You are Leo, a majestic lion",
            "child-appropriate content",
            "simple language appropriate for children",
            "African wildlife"
        ]

    def test_prompt_merger_initialization(self):
        """Test PromptMerger can be initialized with valid components."""
        merger = PromptMerger(self.personality_data, self.guardrail_data)

        assert merger.personality == self.personality_data
        assert merger.guardrail == self.guardrail_data
        assert merger.template is not None

    def test_merge_prompts_success(self):
        """Test successful merging of personality and guardrail prompts."""
        result, stats = merge_assistant_prompt(
            animal_name="Test Animal",
            animal_species="Test Species",
            personality_text=self.personality_data.get('systemPrompt', ''),
            guardrail_text=self.guardrail_data.get('systemPrompt', '')
        )

        # Verify result structure
        assert isinstance(result, str)
        assert len(result) > 200  # Substantial merged prompt

        # Verify key components are included
        for section in self.expected_merged_sections:
            assert section in result

        # Verify proper formatting
        assert result.strip() == result  # No leading/trailing whitespace
        assert "\n\n" in result  # Proper section separation

    def test_merge_prompts_with_priority_override(self):
        """Test guardrail rules take priority over personality when they conflict."""
        # Create conflicting personality
        conflicting_personality = self.personality_data.copy()
        conflicting_personality["systemPrompt"] = "Tell exciting hunting stories to children."

        result = merge_prompts(conflicting_personality, self.guardrail_data)

        # Guardrail restrictions should override conflicting personality
        assert "hunting" not in result.lower() or "no discussion of hunting" in result
        assert "child-appropriate content" in result

    def test_merge_prompts_preserves_essential_personality(self):
        """Test that essential personality elements are preserved in merge."""
        result, stats = merge_assistant_prompt(
            animal_name="Test Animal",
            animal_species="Test Species",
            personality_text=self.personality_data.get('systemPrompt', ''),
            guardrail_text=self.guardrail_data.get('systemPrompt', '')
        )

        # Essential personality elements should be preserved
        assert "Leo" in result
        assert "lion" in result.lower()
        assert "savanna" in result.lower()
        assert "educational" in result.lower()

    def test_merge_prompts_applies_all_guardrails(self):
        """Test that all guardrail rules are applied in the merged prompt."""
        result, stats = merge_assistant_prompt(
            animal_name="Test Animal",
            animal_species="Test Species",
            personality_text=self.personality_data.get('systemPrompt', ''),
            guardrail_text=self.guardrail_data.get('systemPrompt', '')
        )

        # All guardrail rules should be represented
        assert "child-appropriate" in result
        assert "150 words" in result or "under 150" in result
        assert "positive language" in result or "encouraging" in result

    def test_validate_prompt_components_success(self):
        """Test successful validation using validate_assistant_prompt."""
        result, stats = merge_assistant_prompt(
            animal_name="Test Animal",
            animal_species="Test Species",
            personality_text=self.personality_data.get('systemPrompt', ''),
            guardrail_text=self.guardrail_data.get('systemPrompt', '')
        )

        # Should not raise exception with valid result
        validation = validate_assistant_prompt(result, "Test Animal")
        assert validation is not None

    def test_validate_prompt_components_missing_personality_prompt(self):
        """Test validation with missing personality system prompt."""
        # Test with empty personality text
        try:
            result, stats = merge_assistant_prompt(
                animal_name="Test Animal",
                animal_species="Test Species",
                personality_text="",  # Empty personality
                guardrail_text=self.guardrail_data.get('systemPrompt', '')
            )
            # Should raise ValueError due to empty personality text
            assert False, "Expected ValueError for empty personality text"
        except ValueError as e:
            assert "personality" in str(e).lower() or "required" in str(e).lower()

    def test_validate_prompt_components_missing_guardrail_rules(self):
        """Test validation with missing guardrail rules."""
        # Test with empty guardrail text
        try:
            result, stats = merge_assistant_prompt(
                animal_name="Test Animal",
                animal_species="Test Species",
                personality_text=self.personality_data.get('systemPrompt', ''),
                guardrail_text=""  # Empty guardrail
            )
            # Should raise ValueError due to empty guardrail text
            assert False, "Expected ValueError for empty guardrail text"
        except ValueError as e:
            assert "guardrail" in str(e).lower() or "required" in str(e).lower()

    def test_prompt_merger_template_customization(self):
        """Test PromptMerger with custom template."""
        custom_template = """
ANIMAL ASSISTANT: {personality_name}
PERSONALITY: {personality_prompt}
SAFETY RULES: {guardrail_rules}
COMMUNICATION: {communication_style}
"""

        merger = PromptMerger(self.personality_data, self.guardrail_data, template=custom_template)
        result = merger.merge()

        # Verify custom template is used
        assert "ANIMAL ASSISTANT:" in result
        assert "PERSONALITY:" in result
        assert "SAFETY RULES:" in result
        assert "Friendly Lion" in result

    def test_merge_prompts_with_knowledge_base_integration(self):
        """Test merging includes knowledge base context when provided."""
        knowledge_context = [
            "Lions are the only social cats living in prides",
            "A lion's roar can be heard up to 5 miles away",
            "Lions sleep 16-20 hours per day"
        ]

        result = merge_prompts(
            self.personality_data,
            self.guardrail_data,
            knowledge_context=knowledge_context
        )

        # Verify knowledge context is included
        assert "prides" in result or "social cats" in result
        assert "5 miles" in result or "roar" in result
        assert "16-20 hours" in result or "sleep" in result

    def test_merge_prompts_handles_empty_knowledge_context(self):
        """Test merging works correctly with empty knowledge context."""
        result = merge_prompts(
            self.personality_data,
            self.guardrail_data,
            knowledge_context=[]
        )

        # Should still produce valid merged prompt
        assert isinstance(result, str)
        assert len(result) > 100
        for section in self.expected_merged_sections:
            assert section in result

    def test_prompt_merger_handles_unicode_content(self):
        """Test PromptMerger correctly handles unicode characters."""
        unicode_personality = self.personality_data.copy()
        unicode_personality["systemPrompt"] = "You are León 🦁, un león muy amigable."

        result = merge_prompts(unicode_personality, self.guardrail_data)

        # Verify unicode content is preserved
        assert "León" in result
        assert "🦁" in result
        assert "amigable" in result

    def test_merge_prompts_length_validation(self):
        """Test merged prompt length is within acceptable limits."""
        result, stats = merge_assistant_prompt(
            animal_name="Test Animal",
            animal_species="Test Species",
            personality_text=self.personality_data.get('systemPrompt', ''),
            guardrail_text=self.guardrail_data.get('systemPrompt', '')
        )

        # Verify length constraints
        assert len(result) >= 100  # Minimum substantive content
        assert len(result) <= 10000  # Maximum token limit consideration

        # Verify no excessive repetition
        words = result.lower().split()
        unique_words = set(words)
        repetition_ratio = len(words) / len(unique_words)
        assert repetition_ratio < 3.0  # Reasonable repetition threshold


class TestPromptMergeError:
    """Test suite for PromptMergeError exception handling."""

    def test_prompt_merge_error_creation(self):
        """Test PromptMergeError can be created with message."""
        error = PromptMergeError("Test error message")
        assert str(error) == "Test error message"
        assert isinstance(error, Exception)

    def test_prompt_merge_error_with_details(self):
        """Test PromptMergeError with additional details."""
        details = {"component": "personality", "field": "systemPrompt"}
        error = PromptMergeError("Validation failed", details=details)

        assert "Validation failed" in str(error)
        assert error.details == details


class TestPromptOptimization:
    """Test suite for prompt optimization features."""

    def test_optimize_for_token_efficiency(self):
        """Test prompt optimization for token efficiency."""
        from openapi_server.impl.utils.prompt_merger import optimize_for_tokens

        verbose_personality = {
            "name": "Very Verbose Lion",
            "systemPrompt": "You are a lion that talks a lot and repeats things many times. " * 10,
            "traits": ["verbose", "repetitive"]
        }

        optimized = optimize_for_tokens(verbose_personality, self.guardrail_data)
        original = merge_prompts(verbose_personality, self.guardrail_data)

        # Optimized version should be shorter
        assert len(optimized) < len(original)

        # But still contain essential elements
        assert "lion" in optimized.lower()
        assert "child-appropriate" in optimized

    def test_validate_merged_prompt_quality(self):
        """Test validation of merged prompt quality metrics."""
        from openapi_server.impl.utils.prompt_merger import validate_prompt_quality

        result, stats = merge_assistant_prompt(
            animal_name="Test Animal",
            animal_species="Test Species",
            personality_text=self.personality_data.get('systemPrompt', ''),
            guardrail_text=self.guardrail_data.get('systemPrompt', '')
        )
        quality_score = validate_prompt_quality(result)

        # Quality score should be reasonable
        assert 0.0 <= quality_score <= 1.0
        assert quality_score > 0.7  # High quality threshold

        # Test with poor quality prompt
        poor_prompt = "hi"
        poor_score = validate_prompt_quality(poor_prompt)
        assert poor_score < 0.5