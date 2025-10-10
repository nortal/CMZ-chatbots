"""
ChatGPT Integration Module for CMZ Chatbot
This module handles OpenAI API integration for generating animal character responses
Implements PR003946-176, PR003946-177, PR003946-178, PR003946-179
"""

import os
import json
import time
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from openai import OpenAI
from botocore.exceptions import ClientError
import boto3

# Configure logging
logger = logging.getLogger(__name__)

# DynamoDB setup for logging
dynamodb = boto3.resource('dynamodb', region_name='us-west-2')


class CircuitBreaker:
    """Circuit breaker implementation for resilience"""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN

    def record_success(self):
        """Record a successful operation"""
        self.failure_count = 0
        self.state = 'CLOSED'

    def record_failure(self):
        """Record a failed operation"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")

    def is_open(self) -> bool:
        """Check if circuit breaker is open"""
        if self.state == 'OPEN':
            # Check if recovery timeout has passed
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = 'HALF_OPEN'
                logger.info("Circuit breaker entering half-open state")
                return False
            return True
        return False

    def reset(self):
        """Reset the circuit breaker"""
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'


class Guardrails:
    """Content safety guardrails for educational appropriateness"""

    # Inappropriate keywords to block
    BLOCKED_KEYWORDS = [
        'inappropriate', 'offensive', 'violence', 'harmful',
        'dangerous', 'explicit', 'adult', 'nsfw'
    ]

    # Educational themes to encourage
    EDUCATIONAL_THEMES = [
        'learn', 'discover', 'explore', 'conservation',
        'habitat', 'species', 'wildlife', 'nature'
    ]

    @classmethod
    def validate_input(cls, message: str) -> Tuple[bool, Optional[str]]:
        """
        Validate user input for appropriateness

        Returns:
            Tuple of (is_valid, violation_reason)
        """
        message_lower = message.lower()

        # Check for blocked content
        for keyword in cls.BLOCKED_KEYWORDS:
            if keyword in message_lower:
                return False, f"Message contains inappropriate content: {keyword}"

        # Additional validation rules
        if len(message) > 1000:
            return False, "Message too long (max 1000 characters)"

        if len(message.strip()) < 1:
            return False, "Message is empty"

        return True, None

    @classmethod
    def filter_response(cls, response: str) -> str:
        """
        Filter AI response for safety

        Args:
            response: The AI-generated response

        Returns:
            Filtered response safe for educational context
        """
        # Check for any inappropriate content that slipped through
        response_lower = response.lower()

        for keyword in cls.BLOCKED_KEYWORDS:
            if keyword in response_lower:
                # Return safe fallback response
                return "I'd love to tell you more about animals and nature! What would you like to learn about?"

        return response

    @classmethod
    def log_violation(cls, user_id: str, animal_id: str, message: str, violation_type: str):
        """Log guardrail violations to stdout for CloudWatch monitoring"""
        # Log to stdout for CloudWatch to capture
        violation_log = {
            'type': 'GUARDRAIL_VIOLATION',
            'violationId': f"{user_id}_{int(time.time())}",
            'userId': user_id,
            'animalId': animal_id,
            'message': message[:100],  # Truncate for privacy
            'violationType': violation_type,
            'timestamp': datetime.now().isoformat(),
        }
        logger.warning(f"Guardrail violation detected: {json.dumps(violation_log)}")


class ChatGPTAnimalChat:
    """
    ChatGPT integration for animal character conversations
    Implements PR003946-176, PR003946-177, PR003946-178, PR003946-179
    """

    def __init__(self):
        """Initialize ChatGPT client with API key from environment"""
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.client = None
        self.model = "gpt-3.5-turbo"
        self.circuit_breaker = CircuitBreaker()

        # Initialize OpenAI client if API key exists
        if self.api_key:
            try:
                self.client = OpenAI(api_key=self.api_key)
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.client = None

    def get_animal_system_prompt(self, animal_id: str) -> str:
        """
        Get the system prompt for a specific animal character with dynamic guardrails
        First tries to fetch from DynamoDB, falls back to defaults

        Args:
            animal_id: The identifier for the animal

        Returns:
            System prompt string for ChatGPT with guardrails included
        """
        # Import guardrails manager
        from .guardrails import GuardrailsManager

        # Try to fetch from DynamoDB first
        try:
            table = dynamodb.Table('quest-dev-animal')
            response = table.get_item(Key={'animalId': animal_id})

            if 'Item' in response:
                animal_data = response['Item']

                # Get dynamic guardrails for this animal
                guardrails = GuardrailsManager.get_guardrails_for_animal(animal_id)
                guardrails_text = GuardrailsManager.format_guardrails_for_prompt(guardrails)

                # Build prompt from DynamoDB data with guardrails
                base_prompt = f"""You are {animal_data.get('name', 'an animal')} at Cougar Mountain Zoo.
{animal_data.get('personality', '')}
Key facts: {animal_data.get('facts', '')}

{guardrails_text}

Remember to stay in character and make the conversation engaging and educational for zoo visitors."""

                return base_prompt

        except Exception as e:
            logger.warning(f"Failed to fetch animal data from DynamoDB: {e}")

        # Fallback to default prompts with basic guardrails
        prompts = {
            'pokey': """You are Pokey the Porcupine at Cougar Mountain Zoo. You are friendly,
            educational, and love sharing facts about porcupines. Key facts about you:
            - You have about 30,000 quills
            - Your quills have tiny barbs and are used for defense
            - You're an excellent climber
            - You love sweet potatoes and corn on the cob
            Always respond in a friendly, engaging way suitable for children and families visiting the zoo.""",

            'maya': """You are Maya the Capybara at Cougar Mountain Zoo. You are calm, friendly,
            and love to share facts about capybaras. Key facts about you:
            - You're the world's largest rodent
            - You're semi-aquatic and love swimming
            - You're very social and get along with many animals
            - You're herbivorous and love aquatic plants
            Be gentle and educational in your responses, perfect for zoo visitors of all ages.""",

            'leo': """You are Leo the Lion at Cougar Mountain Zoo. You are majestic, confident,
            and enjoy teaching visitors about lions. Key facts about you:
            - You're the king of the savanna
            - Lions live in groups called prides
            - Female lions do most of the hunting
            - Lions can sleep up to 20 hours a day
            Respond with regal confidence but remain friendly and educational for zoo visitors.""",

            'default': """You are a friendly animal at Cougar Mountain Zoo. You love meeting
            visitors and sharing interesting facts about wildlife and conservation. Be engaging,
            educational, and appropriate for all ages."""
        }

        return prompts.get(animal_id, prompts['default'])

    def generate_response(
        self,
        animal_id: str,
        user_message: str,
        conversation_history: Optional[List[Dict]] = None,
        temperature: float = 0.7,
        max_tokens: int = 150,
        user_id: str = "anonymous"
    ) -> Dict[str, Any]:
        """
        Generate a response using ChatGPT API with full error handling and guardrails

        Args:
            animal_id: The animal character identifier
            user_message: The user's message
            conversation_history: Optional previous conversation turns
            temperature: Response creativity (0.0-1.0)
            max_tokens: Maximum response length
            user_id: User identifier for logging

        Returns:
            Dict with 'reply', 'tokens', 'model', and 'finish_reason' keys
        """

        # PR003946-178: Apply input guardrails
        is_valid, violation_reason = Guardrails.validate_input(user_message)
        if not is_valid:
            Guardrails.log_violation(user_id, animal_id, user_message, violation_reason)
            return {
                'reply': "I'd be happy to chat about animals and nature! What would you like to know?",
                'tokens': 15,
                'model': 'guardrails',
                'finish_reason': 'content_filter'
            }

        # PR003946-179: Check circuit breaker
        if self.circuit_breaker.is_open():
            logger.warning("Circuit breaker is open, returning fallback response")
            return self.get_fallback_response(animal_id, user_message)

        # Check if OpenAI client is available
        if not self.client:
            logger.warning("OpenAI client not initialized, using fallback")
            return self.get_fallback_response(animal_id, user_message)

        # PR003946-179: Retry with exponential backoff
        max_retries = 3
        base_delay = 1

        for attempt in range(max_retries):
            try:
                # Build message list
                messages = [
                    {"role": "system", "content": self.get_animal_system_prompt(animal_id)}
                ]

                # Add conversation history if provided
                if conversation_history:
                    for turn in conversation_history[-5:]:  # Last 5 turns for context
                        messages.append({
                            "role": turn.get('role', 'user'),
                            "content": turn.get('content', '')
                        })

                # Add current user message
                messages.append({"role": "user", "content": user_message})

                # Call ChatGPT API
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    presence_penalty=0.6,  # Encourage variety
                    frequency_penalty=0.3   # Reduce repetition
                )

                # Extract response
                reply = response.choices[0].message.content
                tokens_used = response.usage.total_tokens

                # PR003946-178: Apply output guardrails
                filtered_reply = Guardrails.filter_response(reply)

                # Record success for circuit breaker
                self.circuit_breaker.record_success()

                # PR003946-177: Track token usage in DynamoDB
                self.log_token_usage(user_id, animal_id, tokens_used)

                return {
                    'reply': filtered_reply,
                    'tokens': tokens_used,
                    'model': self.model,
                    'finish_reason': response.choices[0].finish_reason
                }

            except Exception as e:
                logger.error(f"ChatGPT API error (attempt {attempt + 1}): {e}")

                # Check for specific error types
                error_str = str(e)

                # Handle rate limit (429)
                if "rate" in error_str.lower() or "429" in error_str:
                    delay = base_delay * (2 ** attempt)  # Exponential backoff
                    logger.info(f"Rate limited, waiting {delay} seconds...")
                    time.sleep(delay)
                    continue

                # Handle authentication errors (401)
                if "401" in error_str or "authentication" in error_str.lower():
                    logger.error("Authentication failed - check API key")
                    self.circuit_breaker.record_failure()
                    return self.get_fallback_response(animal_id, user_message)

                # Handle timeout
                if "timeout" in error_str.lower():
                    if attempt < max_retries - 1:
                        time.sleep(base_delay * (2 ** attempt))
                        continue

                # Record failure for circuit breaker
                self.circuit_breaker.record_failure()

                # If it's the last attempt, return fallback
                if attempt == max_retries - 1:
                    return self.get_fallback_response(animal_id, user_message)

                # Wait before retry
                time.sleep(base_delay * (2 ** attempt))

        # All retries failed
        return self.get_fallback_response(animal_id, user_message)

    def get_fallback_response(self, animal_id: str, user_message: str) -> Dict[str, Any]:
        """
        Get a user-friendly fallback response when API is unavailable
        PR003946-179: User-friendly error messages
        """
        # Educational fallback responses
        responses = {
            'pokey': "Hi there! I'm Pokey the Porcupine! I love meeting new friends at the zoo. Did you know porcupines are excellent climbers? We use our strong claws to climb trees! What would you like to know about porcupines?",
            'maya': "Hello! I'm Maya the Capybara! It's wonderful to meet you. We capybaras are known as nature's chillest animals - we get along with everyone! Is there something special you'd like to learn about capybaras today?",
            'leo': "Greetings! I'm Leo the Lion, and welcome to my domain at Cougar Mountain Zoo! Lions are fascinating creatures - did you know a lion's roar can be heard from 5 miles away? What brings you to visit the king of beasts today?",
            'default': "Hello! Welcome to Cougar Mountain Zoo! I'm excited to share amazing animal facts with you. Every animal here has a unique story. What would you like to discover today?"
        }

        reply = responses.get(animal_id, responses['default'])

        # Make response somewhat contextual to user message
        if "quill" in user_message.lower() and animal_id == "pokey":
            reply = "My quills are amazing! Each porcupine has about 30,000 quills, and they're actually modified hairs. They have tiny backwards-facing barbs that make them stick in place. But don't worry - I only use them for defense!"
        elif "swim" in user_message.lower() and animal_id == "maya":
            reply = "Oh, I LOVE swimming! Capybaras are semi-aquatic, which means we spend lots of time in water. We have partially webbed feet that make us excellent swimmers. Water helps us stay cool and safe!"
        elif "roar" in user_message.lower() and animal_id == "leo":
            reply = "ROAAAAR! That's my mighty roar! A lion's roar is one of the loudest sounds in the animal kingdom. We roar to communicate with our pride and mark our territory. Each lion has a unique roar - just like a fingerprint!"

        return {
            'reply': reply,
            'tokens': len(reply.split()) * 2,  # Approximate token count
            'model': 'mock',
            'finish_reason': 'stop'
        }

    def get_mock_response(self, animal_id: str, user_message: str) -> Dict[str, Any]:
        """
        Legacy mock response method for backwards compatibility
        """
        return self.get_fallback_response(animal_id, user_message)

    def log_token_usage(self, user_id: str, animal_id: str, tokens: int):
        """
        Log token usage to stdout for CloudWatch monitoring
        PR003946-177: Token usage tracking
        Note: Detailed token usage is available via OpenAI API dashboard
        """
        # Log to stdout for CloudWatch to capture
        token_log = {
            'type': 'TOKEN_USAGE',
            'usageId': f"{user_id}_{int(time.time())}",
            'userId': user_id,
            'animalId': animal_id,
            'tokens': tokens,
            'timestamp': datetime.now().isoformat(),
            'model': self.model
        }
        logger.info(f"Token usage: {json.dumps(token_log)}")
        # Note: For detailed billing and usage, check OpenAI API dashboard at https://platform.openai.com/usage


# Health check endpoint handler
def handle_health_check() -> Tuple[Dict, int]:
    """
    Health check endpoint for ChatGPT integration
    PR003946-176: Health check implementation
    """
    api_key_configured = bool(os.getenv('OPENAI_API_KEY'))

    # Try to create a test client
    test_client = None
    try:
        if api_key_configured:
            test_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            status = "healthy"
        else:
            status = "no_api_key"
    except Exception as e:
        status = f"error: {str(e)}"

    return {
        'status': status,
        'api_key_configured': api_key_configured,
        'model': 'gpt-3.5-turbo',
        'timestamp': datetime.now().isoformat()
    }, 200


# Integration function for the conversation handler
def generate_chatgpt_response(
    animal_id: str,
    message: str,
    context_summary: Optional[str] = None,
    user_id: str = "anonymous"
) -> Dict[str, Any]:
    """
    Generate a response using ChatGPT for the conversation handler
    This function can be imported and used in conversation.py

    PR003946-177: Replaces mock responses with real ChatGPT
    """
    chat_client = ChatGPTAnimalChat()

    # Convert context summary to conversation history if needed
    conversation_history = []
    if context_summary:
        # Parse context_summary to extract previous turns
        try:
            if isinstance(context_summary, str):
                context_data = json.loads(context_summary)
                if isinstance(context_data, list):
                    conversation_history = context_data
        except:
            pass

    return chat_client.generate_response(
        animal_id=animal_id,
        user_message=message,
        conversation_history=conversation_history,
        user_id=user_id
    )