#!/usr/bin/env python3
"""
Prompt Merger Utility for Animal Assistant Management System

Implements the prompt merging strategy: Base Identity + Animal Personality + Guardrail Rules + Knowledge Context
Guardrails take precedence over personality in conflicts as defined in research.md.

Author: CMZ Animal Assistant Management System
Date: 2025-10-23
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import re

# Setup logging
logger = logging.getLogger(__name__)


class PromptMerger:
    """
    Core utility for merging personality, guardrails, and knowledge context into cohesive OpenAI system prompts.

    Implementation follows research.md prompt merging strategy:
    System Prompt = Base Identity + Animal Personality + Guardrail Rules + Knowledge Context

    Key principles:
    - Guardrails override personality in conflicts
    - Clear section separation for maintainability
    - Knowledge context injected last for relevance
    - Maximum 8192 character limit (OpenAI system prompt constraint)
    """

    # Base identity template for all animal assistants
    BASE_IDENTITY_TEMPLATE = """You are a digital ambassador for the Cougar Mountain Zoo. You represent {animal_name}, a {animal_species} at the zoo. Your purpose is to educate visitors about your species, share conservation stories, and create engaging conversations that inspire people to care about wildlife.

Key behaviors:
- Speak as the animal in first person ("I am a {animal_species}")
- Share educational content about your species, habitat, and conservation
- Maintain age-appropriate communication for family audiences
- Stay focused on wildlife education and zoo-related topics
- Be friendly, engaging, and informative"""

    # Standard separators for prompt sections
    SECTION_SEPARATORS = {
        'personality': '\n\n=== PERSONALITY & BEHAVIOR ===\n',
        'guardrails': '\n\n=== SAFETY & CONTENT GUIDELINES ===\n',
        'knowledge': '\n\n=== KNOWLEDGE BASE CONTEXT ===\n'
    }

    # Character limits for each section
    LIMITS = {
        'base_identity': 800,
        'personality': 3000,
        'guardrails': 2000,
        'knowledge': 2000,
        'total': 8192
    }

    def __init__(self):
        """Initialize the PromptMerger with default configuration."""
        self.current_merge_stats = {}

    def merge_prompt(
        self,
        animal_name: str,
        animal_species: str,
        personality_text: str,
        guardrail_text: str,
        knowledge_context: Optional[str] = None,
        animal_id: Optional[str] = None
    ) -> Tuple[str, Dict]:
        """
        Merge all prompt components into final system prompt.

        Args:
            animal_name: Display name of the animal (e.g., "Simba")
            animal_species: Scientific or common species name (e.g., "African Lion")
            personality_text: Core personality configuration text
            guardrail_text: Safety and content guidelines text
            knowledge_context: Optional knowledge base context (truncated if needed)
            animal_id: Optional animal ID for logging/debugging

        Returns:
            Tuple of (merged_prompt_string, merge_statistics_dict)

        Raises:
            ValueError: If required parameters are missing or invalid
            RuntimeError: If merged prompt exceeds character limits
        """
        try:
            # Input validation
            self._validate_inputs(animal_name, animal_species, personality_text, guardrail_text)

            # Generate base identity with animal specifics
            base_identity = self._generate_base_identity(animal_name, animal_species)

            # Process personality section
            personality_section = self._process_personality_section(personality_text)

            # Process guardrails section (takes precedence)
            guardrails_section = self._process_guardrails_section(guardrail_text)

            # Process knowledge context (optional, truncated if needed)
            knowledge_section = self._process_knowledge_section(knowledge_context)

            # Assemble final prompt
            merged_prompt = self._assemble_prompt(
                base_identity, personality_section, guardrails_section, knowledge_section
            )

            # Validate final prompt
            self._validate_final_prompt(merged_prompt)

            # Generate merge statistics
            merge_stats = self._generate_merge_stats(
                base_identity, personality_section, guardrails_section, knowledge_section,
                animal_id, animal_name
            )

            self.current_merge_stats = merge_stats

            logger.info(f"Successfully merged prompt for {animal_name} ({len(merged_prompt)} chars)")

            return merged_prompt, merge_stats

        except Exception as e:
            logger.error(f"Failed to merge prompt for {animal_name}: {str(e)}")
            raise

    def _validate_inputs(self, animal_name: str, animal_species: str,
                        personality_text: str, guardrail_text: str) -> None:
        """Validate required input parameters."""
        if not animal_name or not animal_name.strip():
            raise ValueError("Animal name is required and cannot be empty")

        if not animal_species or not animal_species.strip():
            raise ValueError("Animal species is required and cannot be empty")

        if not personality_text or not personality_text.strip():
            raise ValueError("Personality text is required and cannot be empty")

        if not guardrail_text or not guardrail_text.strip():
            raise ValueError("Guardrail text is required and cannot be empty")

        if len(personality_text) > self.LIMITS['personality']:
            raise ValueError(f"Personality text exceeds {self.LIMITS['personality']} character limit")

        if len(guardrail_text) > self.LIMITS['guardrails']:
            raise ValueError(f"Guardrail text exceeds {self.LIMITS['guardrails']} character limit")

    def _generate_base_identity(self, animal_name: str, animal_species: str) -> str:
        """Generate base identity section with animal specifics."""
        base_identity = self.BASE_IDENTITY_TEMPLATE.format(
            animal_name=animal_name.strip(),
            animal_species=animal_species.strip()
        )

        if len(base_identity) > self.LIMITS['base_identity']:
            logger.warning(f"Base identity truncated from {len(base_identity)} to {self.LIMITS['base_identity']} chars")
            base_identity = base_identity[:self.LIMITS['base_identity']] + "..."

        return base_identity

    def _process_personality_section(self, personality_text: str) -> str:
        """Process and format personality section."""
        processed_text = personality_text.strip()

        # Clean up excessive whitespace
        processed_text = re.sub(r'\n\s*\n\s*\n', '\n\n', processed_text)
        processed_text = re.sub(r' +', ' ', processed_text)

        return self.SECTION_SEPARATORS['personality'] + processed_text

    def _process_guardrails_section(self, guardrail_text: str) -> str:
        """Process and format guardrails section with precedence marking."""
        processed_text = guardrail_text.strip()

        # Clean up excessive whitespace
        processed_text = re.sub(r'\n\s*\n\s*\n', '\n\n', processed_text)
        processed_text = re.sub(r' +', ' ', processed_text)

        # Add precedence note
        precedence_note = "IMPORTANT: These guidelines take precedence over personality traits in case of conflicts.\n\n"

        return self.SECTION_SEPARATORS['guardrails'] + precedence_note + processed_text

    def _process_knowledge_section(self, knowledge_context: Optional[str]) -> str:
        """Process and format knowledge base context section."""
        if not knowledge_context or not knowledge_context.strip():
            return ""

        processed_text = knowledge_context.strip()

        # Clean up excessive whitespace
        processed_text = re.sub(r'\n\s*\n\s*\n', '\n\n', processed_text)
        processed_text = re.sub(r' +', ' ', processed_text)

        # Truncate if needed to stay within limits
        if len(processed_text) > self.LIMITS['knowledge']:
            logger.info(f"Knowledge context truncated from {len(processed_text)} to {self.LIMITS['knowledge']} chars")
            processed_text = processed_text[:self.LIMITS['knowledge']] + "\n\n[Additional content available...]"

        knowledge_intro = "Use the following information to enhance your responses when relevant:\n\n"

        return self.SECTION_SEPARATORS['knowledge'] + knowledge_intro + processed_text

    def _assemble_prompt(self, base_identity: str, personality_section: str,
                        guardrails_section: str, knowledge_section: str) -> str:
        """Assemble final prompt from all sections."""
        sections = [base_identity, personality_section, guardrails_section]

        if knowledge_section:
            sections.append(knowledge_section)

        return ''.join(sections)

    def _validate_final_prompt(self, merged_prompt: str) -> None:
        """Validate the final merged prompt meets requirements."""
        if len(merged_prompt) > self.LIMITS['total']:
            raise RuntimeError(
                f"Merged prompt exceeds {self.LIMITS['total']} character limit: {len(merged_prompt)} chars"
            )

        if len(merged_prompt) < 100:
            raise RuntimeError("Merged prompt is too short to be effective")

    def _generate_merge_stats(self, base_identity: str, personality_section: str,
                             guardrails_section: str, knowledge_section: str,
                             animal_id: Optional[str], animal_name: str) -> Dict:
        """Generate statistics about the merge operation."""
        total_length = len(base_identity) + len(personality_section) + len(guardrails_section) + len(knowledge_section)

        return {
            'merge_timestamp': datetime.utcnow().isoformat(),
            'animal_id': animal_id,
            'animal_name': animal_name,
            'section_lengths': {
                'base_identity': len(base_identity),
                'personality': len(personality_section) - len(self.SECTION_SEPARATORS['personality']),
                'guardrails': len(guardrails_section) - len(self.SECTION_SEPARATORS['guardrails']),
                'knowledge': len(knowledge_section) - len(self.SECTION_SEPARATORS['knowledge']) if knowledge_section else 0
            },
            'total_length': total_length,
            'character_utilization': round((total_length / self.LIMITS['total']) * 100, 1),
            'has_knowledge_context': bool(knowledge_section),
            'sections_included': {
                'base_identity': True,
                'personality': True,
                'guardrails': True,
                'knowledge': bool(knowledge_section)
            }
        }

    def get_merge_stats(self) -> Dict:
        """Get statistics from the most recent merge operation."""
        return self.current_merge_stats.copy()


class PromptValidator:
    """
    Utility for validating merged prompts against CMZ requirements.

    Ensures merged prompts meet zoo educational standards and safety requirements.
    """

    # Required elements that must be present in merged prompts
    REQUIRED_ELEMENTS = [
        r'Cougar Mountain Zoo',  # Zoo identification
        r'educational?|educate',  # Educational purpose
        r'conservation|wildlife',  # Conservation focus
        r'family|age.appropriate',  # Family-friendly
        r'safety|guideline',  # Safety guidelines present
    ]

    # Prohibited content patterns
    PROHIBITED_PATTERNS = [
        r'harmful|dangerous|unsafe',  # Safety violations
        r'inappropriate|adult.only',  # Age-inappropriate content
        r'commercial|advertis|buy|sell',  # Commercial content
        r'political|religion|controversial',  # Controversial topics
    ]

    def validate_prompt(self, merged_prompt: str, animal_name: str) -> Dict:
        """
        Validate merged prompt against CMZ educational and safety standards.

        Args:
            merged_prompt: The merged system prompt to validate
            animal_name: Name of animal for logging context

        Returns:
            Dictionary with validation results and recommendations
        """
        validation_results = {
            'is_valid': True,
            'warnings': [],
            'errors': [],
            'recommendations': [],
            'required_elements_found': [],
            'prohibited_patterns_found': [],
            'character_count': len(merged_prompt),
            'validation_timestamp': datetime.utcnow().isoformat()
        }

        # Check required elements
        for pattern in self.REQUIRED_ELEMENTS:
            if re.search(pattern, merged_prompt, re.IGNORECASE):
                validation_results['required_elements_found'].append(pattern)
            else:
                validation_results['warnings'].append(f"Missing recommended element: {pattern}")

        # Check for prohibited patterns
        for pattern in self.PROHIBITED_PATTERNS:
            matches = re.findall(pattern, merged_prompt, re.IGNORECASE)
            if matches:
                validation_results['prohibited_patterns_found'].extend(matches)
                validation_results['errors'].append(f"Prohibited content found: {', '.join(matches)}")
                validation_results['is_valid'] = False

        # Check character count
        if len(merged_prompt) > 8192:
            validation_results['errors'].append(f"Prompt exceeds 8192 character limit: {len(merged_prompt)}")
            validation_results['is_valid'] = False
        elif len(merged_prompt) > 7500:
            validation_results['warnings'].append("Prompt is approaching character limit")

        # Generate recommendations
        if len(validation_results['required_elements_found']) < 3:
            validation_results['recommendations'].append("Consider adding more educational and conservation content")

        if validation_results['character_count'] < 1000:
            validation_results['recommendations'].append("Prompt may be too brief for effective animal personality")

        logger.info(f"Prompt validation for {animal_name}: {'PASSED' if validation_results['is_valid'] else 'FAILED'}")

        return validation_results


# Convenience functions for common use cases
def merge_assistant_prompt(animal_name: str, animal_species: str,
                          personality_text: str, guardrail_text: str,
                          knowledge_context: Optional[str] = None) -> Tuple[str, Dict]:
    """
    Convenience function to merge an assistant prompt with standard configuration.

    Returns:
        Tuple of (merged_prompt, merge_statistics)
    """
    merger = PromptMerger()
    return merger.merge_prompt(
        animal_name, animal_species, personality_text,
        guardrail_text, knowledge_context
    )


def validate_assistant_prompt(merged_prompt: str, animal_name: str) -> Dict:
    """
    Convenience function to validate a merged assistant prompt.

    Returns:
        Dictionary with validation results
    """
    validator = PromptValidator()
    return validator.validate_prompt(merged_prompt, animal_name)


def create_sandbox_prompt(animal_name: str, animal_species: str,
                         test_personality: str, test_guardrails: str) -> Tuple[str, Dict]:
    """
    Create a sandbox prompt for testing new configurations.

    Sandbox prompts have slightly different base identity to indicate test mode.

    Returns:
        Tuple of (sandbox_prompt, merge_statistics)
    """
    merger = PromptMerger()

    # Modify base identity for sandbox mode
    original_template = merger.BASE_IDENTITY_TEMPLATE
    merger.BASE_IDENTITY_TEMPLATE = original_template.replace(
        "You are a digital ambassador",
        "You are a TEST digital ambassador (this is a sandbox environment)"
    )

    try:
        result = merger.merge_prompt(
            animal_name, animal_species, test_personality, test_guardrails
        )
        return result
    finally:
        # Restore original template
        merger.BASE_IDENTITY_TEMPLATE = original_template


# Module-level logger configuration
if __name__ == '__main__':
    # Configure logging for standalone testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Example usage for testing
    example_prompt, stats = merge_assistant_prompt(
        animal_name="Luna",
        animal_species="Arctic Fox",
        personality_text="I am playful and curious, love to explore snowy environments. I enjoy teaching visitors about Arctic adaptations.",
        guardrail_text="Always maintain educational focus. Keep content appropriate for all ages. No discussions of hunting or predation details."
    )

    print(f"Generated prompt ({len(example_prompt)} chars):")
    print(example_prompt)
    print(f"\nMerge statistics: {stats}")

    validation = validate_assistant_prompt(example_prompt, "Luna")
    print(f"\nValidation results: {validation}")