"""
OpenAI Integration Utility for CMZ Chatbots Safety and Personalization System.

This module provides centralized OpenAI API integration with:
- Content moderation for safety guardrails
- Context summarization for personalization
- Token counting and optimization
- Retry logic with exponential backoff
- Error handling and rate limiting

Environment Variables:
    OPENAI_API_KEY - OpenAI API key (required)
    OPENAI_MODEL - Primary model for content generation (default: gpt-4-turbo-preview)
    OPENAI_MODERATION_MODEL - Model for content moderation (default: text-moderation-latest)
    OPENAI_MAX_RETRIES - Maximum API call retries (default: 3)
    OPENAI_TIMEOUT_SECONDS - API call timeout (default: 30)
"""

import os
import json
import time
import logging
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum

import openai
import tiktoken
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_log,
    after_log
)
from openai import OpenAI
from openai.types.moderation import Moderation
from openai.types.chat import ChatCompletion

# Configure logging
logger = logging.getLogger(__name__)


class ModerationResult(Enum):
    """Content moderation result categories."""
    SAFE = "safe"
    FLAGGED = "flagged"
    ERROR = "error"


class SummarizationQuality(Enum):
    """Context summarization quality levels."""
    HIGH = "high"          # 90%+ information retention
    MEDIUM = "medium"      # 70-90% information retention
    LOW = "low"           # 50-70% information retention
    FAILED = "failed"     # Summarization failed


@dataclass
class ModerationResponse:
    """Structured response from content moderation."""
    result: ModerationResult
    is_flagged: bool
    categories: Dict[str, bool]
    category_scores: Dict[str, float]
    flagged_categories: List[str]
    max_score: float
    explanation: Optional[str] = None
    recommendation: Optional[str] = None


@dataclass
class SummarizationResponse:
    """Structured response from context summarization."""
    summary: str
    original_tokens: int
    summary_tokens: int
    compression_ratio: float
    quality_score: float
    quality_level: SummarizationQuality
    topics_extracted: List[str]
    preservation_score: float  # How well original meaning is preserved


@dataclass
class TokenAnalysis:
    """Token usage analysis for content optimization."""
    token_count: int
    model: str
    estimated_cost: float
    is_over_limit: bool
    suggested_max_tokens: Optional[int] = None


class OpenAIIntegration:
    """Centralized OpenAI API integration for CMZ safety and personalization features."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenAI integration with configuration from environment variables.

        Args:
            api_key: OpenAI API key (if not provided, reads from OPENAI_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key must be provided or set in OPENAI_API_KEY environment variable")

        # Configuration from environment variables
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview')
        self.moderation_model = os.getenv('OPENAI_MODERATION_MODEL', 'text-moderation-latest')
        self.max_retries = int(os.getenv('OPENAI_MAX_RETRIES', '3'))
        self.timeout_seconds = int(os.getenv('OPENAI_TIMEOUT_SECONDS', '30'))

        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key, timeout=self.timeout_seconds)

        # Token encoders for different models
        self.encoders = {}
        self._init_token_encoders()

        logger.info(f"OpenAI integration initialized with model: {self.model}")

    def _init_token_encoders(self):
        """Initialize token encoders for supported models."""
        try:
            # GPT-4 and GPT-3.5 use cl100k_base encoding
            self.encoders['gpt-4'] = tiktoken.get_encoding("cl100k_base")
            self.encoders['gpt-3.5'] = tiktoken.get_encoding("cl100k_base")
            self.encoders['default'] = tiktoken.get_encoding("cl100k_base")
        except Exception as e:
            logger.warning(f"Failed to initialize token encoders: {e}")
            self.encoders['default'] = None

    def count_tokens(self, text: str, model: Optional[str] = None) -> TokenAnalysis:
        """
        Count tokens in text for specified model.

        Args:
            text: Text to analyze
            model: Model name (defaults to configured model)

        Returns:
            TokenAnalysis with token count and cost estimation
        """
        model = model or self.model

        try:
            # Determine appropriate encoder
            encoder_key = 'default'
            if 'gpt-4' in model.lower():
                encoder_key = 'gpt-4'
            elif 'gpt-3.5' in model.lower():
                encoder_key = 'gpt-3.5'

            encoder = self.encoders.get(encoder_key, self.encoders['default'])

            if encoder:
                token_count = len(encoder.encode(text))
            else:
                # Fallback: rough estimation (4 chars per token)
                token_count = len(text) // 4
                logger.warning("Using fallback token counting method")

            # Estimate cost (approximate, based on current OpenAI pricing)
            cost_per_1k_tokens = {
                'gpt-4-turbo-preview': 0.01,  # Input tokens
                'gpt-4': 0.03,
                'gpt-3.5-turbo': 0.001
            }

            rate = cost_per_1k_tokens.get(model, 0.01)
            estimated_cost = (token_count / 1000) * rate

            # Check if over typical limits
            typical_limits = {
                'gpt-4-turbo-preview': 128000,
                'gpt-4': 8192,
                'gpt-3.5-turbo': 4096
            }

            limit = typical_limits.get(model, 4096)
            is_over_limit = token_count > limit

            return TokenAnalysis(
                token_count=token_count,
                model=model,
                estimated_cost=estimated_cost,
                is_over_limit=is_over_limit,
                suggested_max_tokens=limit if is_over_limit else None
            )

        except Exception as e:
            logger.error(f"Error counting tokens: {e}")
            # Return safe fallback
            return TokenAnalysis(
                token_count=len(text) // 4,
                model=model,
                estimated_cost=0.0,
                is_over_limit=False
            )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((openai.RateLimitError, openai.APITimeoutError)),
        before=before_log(logger, logging.INFO),
        after=after_log(logger, logging.INFO)
    )
    def moderate_content(self, content: str, threshold: float = 0.7) -> ModerationResponse:
        """
        Moderate content for safety using OpenAI's moderation API.

        Args:
            content: Text content to moderate
            threshold: Threshold for flagging content (0.0-1.0)

        Returns:
            ModerationResponse with detailed moderation results
        """
        try:
            logger.info(f"Moderating content of length {len(content)} characters")

            # Call OpenAI moderation API
            response: Moderation = self.client.moderations.create(
                input=content,
                model=self.moderation_model
            )

            # Extract moderation result
            result = response.results[0]
            categories = result.categories.__dict__
            category_scores = result.category_scores.__dict__

            # Find flagged categories above threshold
            flagged_categories = [
                category for category, score in category_scores.items()
                if score >= threshold
            ]

            # Determine overall result
            is_flagged = result.flagged or len(flagged_categories) > 0
            max_score = max(category_scores.values()) if category_scores else 0.0

            moderation_result = ModerationResult.FLAGGED if is_flagged else ModerationResult.SAFE

            # Generate explanation and recommendation
            explanation = None
            recommendation = None

            if is_flagged:
                explanation = f"Content flagged for: {', '.join(flagged_categories)}"
                recommendation = "Content should be blocked or require human review"
            else:
                explanation = "Content passed safety moderation"
                recommendation = "Content is safe to display"

            return ModerationResponse(
                result=moderation_result,
                is_flagged=is_flagged,
                categories=categories,
                category_scores=category_scores,
                flagged_categories=flagged_categories,
                max_score=max_score,
                explanation=explanation,
                recommendation=recommendation
            )

        except Exception as e:
            logger.error(f"Content moderation failed: {e}")
            return ModerationResponse(
                result=ModerationResult.ERROR,
                is_flagged=True,  # Fail safe - block content on error
                categories={},
                category_scores={},
                flagged_categories=[],
                max_score=1.0,
                explanation=f"Moderation error: {str(e)}",
                recommendation="Block content due to moderation error"
            )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((openai.RateLimitError, openai.APITimeoutError)),
        before=before_log(logger, logging.INFO),
        after=after_log(logger, logging.INFO)
    )
    def summarize_context(
        self,
        conversations: List[str],
        target_tokens: int = 800,
        preserve_recent: int = 3,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> SummarizationResponse:
        """
        Summarize conversation context for personalization while preserving key information.

        Args:
            conversations: List of conversation texts to summarize
            target_tokens: Target token count for summary
            preserve_recent: Number of recent conversations to preserve with more detail
            user_preferences: User preferences to guide summarization

        Returns:
            SummarizationResponse with summary and quality metrics
        """
        try:
            logger.info(f"Summarizing {len(conversations)} conversations targeting {target_tokens} tokens")

            # Analyze token usage of original content
            combined_text = '\n\n'.join(conversations)
            original_analysis = self.count_tokens(combined_text)

            # If already under target, minimal summarization needed
            if original_analysis.token_count <= target_tokens:
                return SummarizationResponse(
                    summary=combined_text,
                    original_tokens=original_analysis.token_count,
                    summary_tokens=original_analysis.token_count,
                    compression_ratio=1.0,
                    quality_score=1.0,
                    quality_level=SummarizationQuality.HIGH,
                    topics_extracted=[],
                    preservation_score=1.0
                )

            # Prepare conversations with weights (recent conversations get more detail)
            weighted_conversations = []
            for i, conv in enumerate(conversations):
                # Recent conversations get higher weight
                weight = "high" if i >= len(conversations) - preserve_recent else "medium"
                weighted_conversations.append(f"[Weight: {weight}] {conv}")

            # Build summarization prompt
            summarization_prompt = self._build_summarization_prompt(
                weighted_conversations, target_tokens, user_preferences
            )

            # Call OpenAI for summarization
            response: ChatCompletion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at summarizing educational conversations while preserving personalization data and learning preferences."
                    },
                    {
                        "role": "user",
                        "content": summarization_prompt
                    }
                ],
                max_tokens=target_tokens + 200,  # Allow some overhead
                temperature=0.3  # Low temperature for consistent summarization
            )

            summary = response.choices[0].message.content or ""

            # Analyze summary quality
            summary_analysis = self.count_tokens(summary)
            compression_ratio = summary_analysis.token_count / original_analysis.token_count

            # Extract topics and assess quality
            topics_extracted = self._extract_topics_from_summary(summary)
            preservation_score = self._assess_preservation_quality(conversations, summary)

            # Determine quality level
            quality_level = self._determine_quality_level(compression_ratio, preservation_score)

            return SummarizationResponse(
                summary=summary,
                original_tokens=original_analysis.token_count,
                summary_tokens=summary_analysis.token_count,
                compression_ratio=compression_ratio,
                quality_score=preservation_score,
                quality_level=quality_level,
                topics_extracted=topics_extracted,
                preservation_score=preservation_score
            )

        except Exception as e:
            logger.error(f"Context summarization failed: {e}")
            return SummarizationResponse(
                summary="",
                original_tokens=0,
                summary_tokens=0,
                compression_ratio=0.0,
                quality_score=0.0,
                quality_level=SummarizationQuality.FAILED,
                topics_extracted=[],
                preservation_score=0.0
            )

    def _build_summarization_prompt(
        self,
        weighted_conversations: List[str],
        target_tokens: int,
        user_preferences: Optional[Dict[str, Any]]
    ) -> str:
        """Build an effective prompt for context summarization."""

        preferences_text = ""
        if user_preferences:
            preferences_text = f"\nUser Preferences: {json.dumps(user_preferences, indent=2)}"

        return f"""
Please summarize these educational zoo conversations while preserving:
1. User's learning interests and preferences
2. Questions they frequently ask
3. Animals they show particular interest in
4. Educational level and comprehension style
5. Any personal information shared (for privacy tracking)

Target length: approximately {target_tokens} tokens

Conversations to summarize:
{chr(10).join(weighted_conversations)}
{preferences_text}

Create a summary that:
- Maintains educational personalization data
- Preserves learning preferences and interests
- Notes any privacy-sensitive information
- Highlights key animal interests and engagement patterns
- Is concise but comprehensive for future conversation context

Summary:"""

    def _extract_topics_from_summary(self, summary: str) -> List[str]:
        """Extract key topics from a summary using basic keyword analysis."""
        # Simple topic extraction - in production, could use more sophisticated NLP
        common_zoo_topics = [
            "mammals", "birds", "reptiles", "conservation", "habitat",
            "feeding", "behavior", "endangered", "climate", "adaptation"
        ]

        summary_lower = summary.lower()
        found_topics = [topic for topic in common_zoo_topics if topic in summary_lower]

        return found_topics

    def _assess_preservation_quality(self, original_conversations: List[str], summary: str) -> float:
        """Assess how well the summary preserves important information."""
        # Simple assessment based on key information preservation
        # In production, could use more sophisticated semantic similarity

        combined_original = ' '.join(original_conversations).lower()
        summary_lower = summary.lower()

        # Check for preservation of key elements
        key_elements = ["like", "interest", "favorite", "learn", "question", "animal"]
        preserved_count = sum(1 for element in key_elements if element in summary_lower and element in combined_original)

        # Simple score based on preserved key elements
        return min(1.0, preserved_count / len(key_elements))

    def _determine_quality_level(self, compression_ratio: float, preservation_score: float) -> SummarizationQuality:
        """Determine summarization quality level based on metrics."""
        if preservation_score >= 0.9:
            return SummarizationQuality.HIGH
        elif preservation_score >= 0.7:
            return SummarizationQuality.MEDIUM
        elif preservation_score >= 0.5:
            return SummarizationQuality.LOW
        else:
            return SummarizationQuality.FAILED

    def validate_api_connection(self) -> Tuple[bool, str]:
        """
        Validate OpenAI API connection and configuration.

        Returns:
            Tuple of (is_valid, message)
        """
        try:
            # Test with a simple moderation call
            test_response = self.client.moderations.create(
                input="Hello, this is a test.",
                model=self.moderation_model
            )

            if test_response and test_response.results:
                return True, "OpenAI API connection validated successfully"
            else:
                return False, "OpenAI API returned unexpected response"

        except openai.AuthenticationError:
            return False, "OpenAI API authentication failed - check API key"
        except openai.RateLimitError:
            return False, "OpenAI API rate limit exceeded"
        except Exception as e:
            return False, f"OpenAI API connection failed: {str(e)}"

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics and configuration."""
        return {
            "model": self.model,
            "moderation_model": self.moderation_model,
            "max_retries": self.max_retries,
            "timeout_seconds": self.timeout_seconds,
            "encoders_available": list(self.encoders.keys()),
            "api_key_configured": bool(self.api_key)
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((openai.RateLimitError, openai.APIConnectionError)),
        before=before_log(logger, logging.INFO),
        after=after_log(logger, logging.INFO)
    )
    async def generate_chat_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 300,
        model: Optional[str] = None
    ) -> str:
        """
        Generate chat response using OpenAI Chat Completions API.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Response creativity (0.0-1.0)
            max_tokens: Maximum response length
            model: Model to use (defaults to configured model)

        Returns:
            Generated response text

        Raises:
            Exception: If API call fails after retries
        """
        try:
            effective_model = model or self.model
            logger.info(f"Generating chat response with {effective_model}, {len(messages)} messages")

            # Note: The OpenAI client doesn't have async methods in the current version
            # This is a synchronous call wrapped for async compatibility
            response = self.client.chat.completions.create(
                model=effective_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=self.timeout_seconds
            )

            # Extract response content
            if response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content
                if content:
                    logger.info(f"Generated response: {len(content)} characters")
                    return content.strip()
                else:
                    logger.warning("Empty response content from OpenAI")
                    return "I'm having trouble generating a response right now. Please try again."
            else:
                logger.error("No choices returned from OpenAI API")
                return "I'm having trouble generating a response right now. Please try again."

        except openai.RateLimitError as e:
            logger.error(f"OpenAI rate limit exceeded: {e}")
            raise
        except openai.APIConnectionError as e:
            logger.error(f"OpenAI API connection error: {e}")
            raise
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            return f"I'm experiencing technical difficulties. Error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error generating chat response: {e}")
            return "I'm having trouble right now. Please try again in a moment."


# Global instance for easy access
_openai_integration: Optional[OpenAIIntegration] = None


def get_openai_integration() -> OpenAIIntegration:
    """Get singleton OpenAI integration instance."""
    global _openai_integration

    if _openai_integration is None:
        _openai_integration = OpenAIIntegration()

    return _openai_integration


def moderate_content_simple(content: str, threshold: float = 0.7) -> bool:
    """
    Simple content moderation that returns True if content is safe.

    Args:
        content: Text to moderate
        threshold: Safety threshold

    Returns:
        True if content is safe, False if flagged or error
    """
    try:
        integration = get_openai_integration()
        result = integration.moderate_content(content, threshold)
        return result.result == ModerationResult.SAFE
    except Exception as e:
        logger.error(f"Simple content moderation failed: {e}")
        return False  # Fail safe


def summarize_conversations_simple(conversations: List[str], target_tokens: int = 800) -> str:
    """
    Simple conversation summarization that returns summary text.

    Args:
        conversations: List of conversation texts
        target_tokens: Target length for summary

    Returns:
        Summary text (empty string if failed)
    """
    try:
        integration = get_openai_integration()
        result = integration.summarize_context(conversations, target_tokens)
        return result.summary if result.quality_level != SummarizationQuality.FAILED else ""
    except Exception as e:
        logger.error(f"Simple conversation summarization failed: {e}")
        return ""