#!/usr/bin/env python3
"""
Animal Assistant OpenAI Integration Wrapper

Extends the existing OpenAI integration with animal assistant-specific features:
- Multi-model fallback strategy (GPT-4o → GPT-4o-mini → GPT-3.5-turbo)
- Streaming conversation responses for real-time chat
- Animal assistant prompt integration with merged system prompts
- Enhanced error handling and rate limiting for production use

Research Requirements:
- Streaming responses (Flask SSE with stream_with_context)
- Multi-model fallback for availability and cost optimization
- Integration with existing conversation system
- <2 second response time for assistant retrieval

Author: CMZ Animal Assistant Management System
Date: 2025-10-23
"""

import logging
import json
import time
from typing import Dict, Any, List, Optional, Tuple, Iterator, Union
from dataclasses import dataclass, asdict
from enum import Enum
import os

from flask import Response, stream_with_context
from openai import OpenAI, Stream
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from openai._exceptions import OpenAIError, RateLimitError, APITimeoutError

from .openai_integration import OpenAIIntegration, TokenAnalysis
from .prompt_merger import PromptMerger, merge_assistant_prompt

# Configure logging
logger = logging.getLogger(__name__)


class ModelTier(Enum):
    """Model tiers for fallback strategy."""
    PRIMARY = "gpt-4o"
    SECONDARY = "gpt-4o-mini"
    FALLBACK = "gpt-3.5-turbo"


class StreamingStatus(Enum):
    """Streaming response status."""
    STARTING = "starting"
    STREAMING = "streaming"
    COMPLETED = "completed"
    ERROR = "error"
    FALLBACK = "fallback"


@dataclass
class ConversationRequest:
    """Structured request for animal assistant conversation."""
    message: str
    animal_id: str
    assistant_id: str
    user_id: Optional[str] = None
    conversation_id: Optional[str] = None
    session_id: Optional[str] = None
    max_tokens: int = 1000
    temperature: float = 0.8
    stream: bool = True


@dataclass
class ConversationResponse:
    """Structured response from animal assistant conversation."""
    response: str
    model_used: str
    tokens_used: int
    response_time_ms: int
    conversation_id: str
    assistant_id: str
    animal_id: str
    timestamp: str
    streaming_status: StreamingStatus
    fallback_used: bool = False
    error_message: Optional[str] = None


@dataclass
class StreamChunk:
    """Individual chunk in streaming response."""
    content: str
    chunk_id: int
    is_final: bool
    model_used: str
    timestamp: str
    error: Optional[str] = None


class AssistantOpenAIIntegration:
    """
    Enhanced OpenAI integration for Animal Assistant Management System.

    Provides animal assistant-specific conversation capabilities with streaming,
    multi-model fallback, and integrated prompt merging.
    """

    # Model fallback configuration (from research.md)
    MODEL_FALLBACK_CHAIN = [
        ModelTier.PRIMARY.value,    # gpt-4o
        ModelTier.SECONDARY.value,  # gpt-4o-mini
        ModelTier.FALLBACK.value    # gpt-3.5-turbo
    ]

    # Model-specific configurations
    MODEL_CONFIGS = {
        "gpt-4o": {
            "max_tokens": 4096,
            "context_limit": 128000,
            "cost_per_1k_input": 0.005,
            "cost_per_1k_output": 0.015,
            "timeout_seconds": 30
        },
        "gpt-4o-mini": {
            "max_tokens": 4096,
            "context_limit": 128000,
            "cost_per_1k_input": 0.00015,
            "cost_per_1k_output": 0.0006,
            "timeout_seconds": 20
        },
        "gpt-3.5-turbo": {
            "max_tokens": 4096,
            "context_limit": 16385,
            "cost_per_1k_input": 0.001,
            "cost_per_1k_output": 0.002,
            "timeout_seconds": 15
        }
    }

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize assistant OpenAI integration.

        Args:
            api_key: OpenAI API key (falls back to environment variable)
        """
        # Initialize base OpenAI integration
        self.base_integration = OpenAIIntegration(api_key)

        # Initialize prompt merger
        self.prompt_merger = PromptMerger()

        # Model configuration
        self.primary_model = os.getenv('OPENAI_ASSISTANT_MODEL', ModelTier.PRIMARY.value)
        self.fallback_enabled = os.getenv('OPENAI_FALLBACK_ENABLED', 'true').lower() == 'true'
        self.max_fallback_attempts = int(os.getenv('OPENAI_MAX_FALLBACK_ATTEMPTS', '3'))

        # Performance tracking
        self.model_performance = {}
        self.total_conversations = 0
        self.fallback_usage_count = {model: 0 for model in self.MODEL_FALLBACK_CHAIN}

        logger.info(f"Assistant OpenAI integration initialized with primary model: {self.primary_model}")

    def chat_with_assistant(
        self,
        request: ConversationRequest,
        system_prompt: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Union[ConversationResponse, Iterator[StreamChunk]]:
        """
        Chat with an animal assistant using the specified configuration.

        Args:
            request: Structured conversation request
            system_prompt: Merged system prompt (from PromptMerger)
            conversation_history: Previous conversation context

        Returns:
            ConversationResponse for non-streaming, Iterator[StreamChunk] for streaming
        """
        start_time = time.time()

        try:
            # Prepare conversation messages
            messages = self._prepare_messages(system_prompt, conversation_history, request.message)

            # Validate token count
            token_analysis = self._analyze_token_usage(messages, request.max_tokens)
            if token_analysis.is_over_limit:
                raise ValueError(f"Request exceeds token limit: {token_analysis.token_count} tokens")

            # Execute with fallback strategy
            if request.stream:
                return self._chat_streaming_with_fallback(request, messages, start_time)
            else:
                return self._chat_standard_with_fallback(request, messages, start_time)

        except Exception as e:
            logger.error(f"Failed to chat with assistant {request.assistant_id}: {str(e)}")

            # Return error response
            error_response = ConversationResponse(
                response=f"I'm sorry, I'm having trouble responding right now. Please try again in a moment.",
                model_used="error",
                tokens_used=0,
                response_time_ms=int((time.time() - start_time) * 1000),
                conversation_id=request.conversation_id or "unknown",
                assistant_id=request.assistant_id,
                animal_id=request.animal_id,
                timestamp=time.time(),
                streaming_status=StreamingStatus.ERROR,
                fallback_used=False,
                error_message=str(e)
            )

            if request.stream:
                return self._error_stream_generator(error_response)
            else:
                return error_response

    def _prepare_messages(
        self,
        system_prompt: str,
        conversation_history: Optional[List[Dict[str, str]]],
        user_message: str
    ) -> List[Dict[str, str]]:
        """Prepare messages array for OpenAI API."""
        messages = [{"role": "system", "content": system_prompt}]

        # Add conversation history
        if conversation_history:
            messages.extend(conversation_history)

        # Add current user message
        messages.append({"role": "user", "content": user_message})

        return messages

    def _analyze_token_usage(self, messages: List[Dict[str, str]], max_response_tokens: int) -> TokenAnalysis:
        """Analyze token usage for the conversation."""
        # Estimate total input tokens
        total_content = " ".join([msg["content"] for msg in messages])
        return self.base_integration.count_tokens(total_content + " " * max_response_tokens)

    def _chat_streaming_with_fallback(
        self,
        request: ConversationRequest,
        messages: List[Dict[str, str]],
        start_time: float
    ) -> Iterator[StreamChunk]:
        """Execute streaming chat with model fallback."""

        for attempt, model in enumerate(self.MODEL_FALLBACK_CHAIN):
            try:
                logger.info(f"Attempting streaming chat with {model} (attempt {attempt + 1})")

                # Get model configuration
                model_config = self.MODEL_CONFIGS.get(model, self.MODEL_CONFIGS["gpt-3.5-turbo"])

                # Create streaming chat completion
                stream = self.base_integration.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=min(request.max_tokens, model_config["max_tokens"]),
                    temperature=request.temperature,
                    stream=True,
                    timeout=model_config["timeout_seconds"]
                )

                # Track successful model usage
                self.fallback_usage_count[model] += 1

                # Yield streaming chunks
                chunk_id = 0
                full_response = ""

                for chunk in stream:
                    if chunk.choices and chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        full_response += content

                        yield StreamChunk(
                            content=content,
                            chunk_id=chunk_id,
                            is_final=False,
                            model_used=model,
                            timestamp=time.time()
                        )
                        chunk_id += 1

                # Final chunk
                yield StreamChunk(
                    content="",
                    chunk_id=chunk_id,
                    is_final=True,
                    model_used=model,
                    timestamp=time.time()
                )

                # Update performance tracking
                response_time = int((time.time() - start_time) * 1000)
                self._update_performance_tracking(model, response_time, len(full_response))

                return

            except (RateLimitError, APITimeoutError, OpenAIError) as e:
                logger.warning(f"Model {model} failed: {str(e)}")

                if attempt < len(self.MODEL_FALLBACK_CHAIN) - 1:
                    # Yield fallback notification
                    yield StreamChunk(
                        content="",
                        chunk_id=0,
                        is_final=False,
                        model_used=model,
                        timestamp=time.time(),
                        error=f"Switching to backup model due to: {str(e)}"
                    )
                    continue
                else:
                    # Final failure
                    yield StreamChunk(
                        content="I'm sorry, I'm having trouble responding right now. Please try again in a moment.",
                        chunk_id=0,
                        is_final=True,
                        model_used="error",
                        timestamp=time.time(),
                        error=str(e)
                    )
                    return

    def _chat_standard_with_fallback(
        self,
        request: ConversationRequest,
        messages: List[Dict[str, str]],
        start_time: float
    ) -> ConversationResponse:
        """Execute standard (non-streaming) chat with model fallback."""

        for attempt, model in enumerate(self.MODEL_FALLBACK_CHAIN):
            try:
                logger.info(f"Attempting chat with {model} (attempt {attempt + 1})")

                # Get model configuration
                model_config = self.MODEL_CONFIGS.get(model, self.MODEL_CONFIGS["gpt-3.5-turbo"])

                # Create chat completion
                completion = self.base_integration.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=min(request.max_tokens, model_config["max_tokens"]),
                    temperature=request.temperature,
                    timeout=model_config["timeout_seconds"]
                )

                # Track successful model usage
                self.fallback_usage_count[model] += 1
                response_time = int((time.time() - start_time) * 1000)

                # Extract response
                response_content = completion.choices[0].message.content
                tokens_used = completion.usage.total_tokens if completion.usage else 0

                # Update performance tracking
                self._update_performance_tracking(model, response_time, len(response_content))

                return ConversationResponse(
                    response=response_content,
                    model_used=model,
                    tokens_used=tokens_used,
                    response_time_ms=response_time,
                    conversation_id=request.conversation_id or f"conv_{int(time.time())}",
                    assistant_id=request.assistant_id,
                    animal_id=request.animal_id,
                    timestamp=time.time(),
                    streaming_status=StreamingStatus.COMPLETED,
                    fallback_used=(attempt > 0)
                )

            except (RateLimitError, APITimeoutError, OpenAIError) as e:
                logger.warning(f"Model {model} failed: {str(e)}")

                if attempt < len(self.MODEL_FALLBACK_CHAIN) - 1:
                    continue
                else:
                    # Final failure - return error response
                    response_time = int((time.time() - start_time) * 1000)
                    return ConversationResponse(
                        response="I'm sorry, I'm having trouble responding right now. Please try again in a moment.",
                        model_used="error",
                        tokens_used=0,
                        response_time_ms=response_time,
                        conversation_id=request.conversation_id or "error",
                        assistant_id=request.assistant_id,
                        animal_id=request.animal_id,
                        timestamp=time.time(),
                        streaming_status=StreamingStatus.ERROR,
                        fallback_used=True,
                        error_message=str(e)
                    )

    def _error_stream_generator(self, error_response: ConversationResponse) -> Iterator[StreamChunk]:
        """Generate error stream for streaming requests."""
        yield StreamChunk(
            content=error_response.response,
            chunk_id=0,
            is_final=True,
            model_used=error_response.model_used,
            timestamp=error_response.timestamp,
            error=error_response.error_message
        )

    def _update_performance_tracking(self, model: str, response_time_ms: int, response_length: int):
        """Update performance tracking metrics."""
        if model not in self.model_performance:
            self.model_performance[model] = {
                "total_requests": 0,
                "total_response_time": 0,
                "total_response_length": 0,
                "error_count": 0
            }

        self.model_performance[model]["total_requests"] += 1
        self.model_performance[model]["total_response_time"] += response_time_ms
        self.model_performance[model]["total_response_length"] += response_length
        self.total_conversations += 1

    def create_flask_streaming_response(
        self,
        stream_generator: Iterator[StreamChunk],
        conversation_id: str
    ) -> Response:
        """
        Create Flask SSE streaming response for real-time chat.

        Research requirement: Flask SSE with stream_with_context for ChatGPT-like experience.
        """

        def generate_sse():
            """Generate Server-Sent Events formatted chunks."""
            try:
                for chunk in stream_generator:
                    # Format as SSE
                    chunk_data = {
                        "content": chunk.content,
                        "chunk_id": chunk.chunk_id,
                        "is_final": chunk.is_final,
                        "model": chunk.model_used,
                        "timestamp": chunk.timestamp,
                        "conversation_id": conversation_id
                    }

                    if chunk.error:
                        chunk_data["error"] = chunk.error

                    # SSE format: data: JSON\n\n
                    yield f"data: {json.dumps(chunk_data)}\n\n"

                    if chunk.is_final:
                        yield "data: [DONE]\n\n"
                        break

            except Exception as e:
                logger.error(f"Streaming error: {str(e)}")
                error_data = {
                    "content": "Stream interrupted",
                    "chunk_id": -1,
                    "is_final": True,
                    "model": "error",
                    "timestamp": time.time(),
                    "conversation_id": conversation_id,
                    "error": str(e)
                }
                yield f"data: {json.dumps(error_data)}\n\n"
                yield "data: [DONE]\n\n"

        return Response(
            stream_with_context(generate_sse()),
            mimetype='text/plain',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*'
            }
        )

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics for monitoring."""
        stats = {
            "total_conversations": self.total_conversations,
            "fallback_usage": dict(self.fallback_usage_count),
            "model_performance": {}
        }

        for model, metrics in self.model_performance.items():
            if metrics["total_requests"] > 0:
                stats["model_performance"][model] = {
                    "total_requests": metrics["total_requests"],
                    "avg_response_time_ms": metrics["total_response_time"] / metrics["total_requests"],
                    "avg_response_length": metrics["total_response_length"] / metrics["total_requests"],
                    "error_rate": metrics["error_count"] / metrics["total_requests"],
                    "success_rate": 1 - (metrics["error_count"] / metrics["total_requests"])
                }

        return stats


# Convenience functions for easy integration
def create_assistant_conversation(
    message: str,
    animal_id: str,
    assistant_id: str,
    system_prompt: str,
    conversation_history: Optional[List[Dict[str, str]]] = None,
    stream: bool = True,
    **kwargs
) -> Union[ConversationResponse, Iterator[StreamChunk]]:
    """
    Convenience function to create an assistant conversation.

    Args:
        message: User's message
        animal_id: ID of the animal
        assistant_id: ID of the assistant configuration
        system_prompt: Merged system prompt (use PromptMerger.merge_prompt)
        conversation_history: Previous conversation context
        stream: Whether to stream the response
        **kwargs: Additional parameters for ConversationRequest

    Returns:
        ConversationResponse or streaming Iterator
    """
    integration = AssistantOpenAIIntegration()

    request = ConversationRequest(
        message=message,
        animal_id=animal_id,
        assistant_id=assistant_id,
        stream=stream,
        **kwargs
    )

    return integration.chat_with_assistant(request, system_prompt, conversation_history)


def create_streaming_flask_response(
    message: str,
    animal_id: str,
    assistant_id: str,
    system_prompt: str,
    conversation_history: Optional[List[Dict[str, str]]] = None,
    conversation_id: Optional[str] = None
) -> Response:
    """
    Convenience function to create Flask streaming response for real-time chat.

    Perfect for implementing the research requirement: "streaming for conversations"
    """
    integration = AssistantOpenAIIntegration()

    request = ConversationRequest(
        message=message,
        animal_id=animal_id,
        assistant_id=assistant_id,
        stream=True,
        conversation_id=conversation_id
    )

    stream_generator = integration.chat_with_assistant(request, system_prompt, conversation_history)

    return integration.create_flask_streaming_response(
        stream_generator,
        conversation_id or f"conv_{int(time.time())}"
    )


# Module-level logger configuration
if __name__ == '__main__':
    # Configure logging for standalone testing
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Example usage
    integration = AssistantOpenAIIntegration()

    # Test the multi-model fallback system
    test_request = ConversationRequest(
        message="Tell me about your habitat and what makes it special!",
        animal_id="lion_001",
        assistant_id="asst_001",
        stream=False
    )

    test_system_prompt = """You are a digital ambassador for the Cougar Mountain Zoo. You represent Simba, an African Lion at the zoo. Your purpose is to educate visitors about your species, share conservation stories, and create engaging conversations that inspire people to care about wildlife.

=== PERSONALITY & BEHAVIOR ===
I am proud and majestic, but also playful with cubs. I love to roar at dawn and dusk. I enjoy sharing stories about my pride and the African savanna.

=== SAFETY & CONTENT GUIDELINES ===
IMPORTANT: These guidelines take precedence over personality traits in case of conflicts.

Always maintain educational focus. Keep content appropriate for all ages. No discussions of hunting details."""

    print("Testing assistant conversation...")
    try:
        response = integration.chat_with_assistant(test_request, test_system_prompt)
        print(f"Response: {response.response}")
        print(f"Model used: {response.model_used}")
        print(f"Response time: {response.response_time_ms}ms")
    except Exception as e:
        print(f"Test failed: {e}")