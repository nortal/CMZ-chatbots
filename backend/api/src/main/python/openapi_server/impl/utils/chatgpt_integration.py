"""
ChatGPT Integration for Animal Personalities
Implements unique endpoint per animal with system prompts
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Any, AsyncGenerator
import aiohttp
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# OpenAI API configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
OPENAI_API_URL = os.getenv('OPENAI_API_URL', 'https://api.openai.com/v1/chat/completions')
DEFAULT_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4')
DEFAULT_TEMPERATURE = float(os.getenv('OPENAI_TEMPERATURE', '0.7'))
DEFAULT_MAX_TOKENS = int(os.getenv('OPENAI_MAX_TOKENS', '500'))

class ChatGPTIntegration:
    """Handle ChatGPT API integration for animal conversations"""

    def __init__(self):
        self.api_key = OPENAI_API_KEY
        self.base_url = OPENAI_API_URL
        self.session = None

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    def build_animal_system_prompt(self, animal_config: Dict[str, Any]) -> str:
        """
        Build system prompt for animal personality

        Args:
            animal_config: Animal configuration from DynamoDB

        Returns:
            System prompt string
        """
        name = animal_config.get('name', 'Unknown Animal')
        personality = animal_config.get('chatConfig', {}).get('personality', {})
        traits = personality.get('traits', ['friendly', 'educational'])
        knowledge = personality.get('knowledge', [])

        # Build dynamic system prompt
        prompt = f"""You are {name}, an animal at Cougar Mountain Zoo.

Your personality traits: {', '.join(traits)}

You have knowledge about: {', '.join(knowledge) if knowledge else 'general animal facts'}

Important guidelines:
- Be educational and engaging, especially with children
- Share interesting facts about your species when appropriate
- Stay in character as {name}
- Keep responses friendly and age-appropriate
- Never use inappropriate language or discuss harmful topics
- If asked about things outside your knowledge, gently redirect to animal-related topics
- Show enthusiasm about conservation and wildlife protection

Remember, you're talking to zoo visitors who want to learn about you!"""

        # Use custom system prompt if provided
        custom_prompt = animal_config.get('chatConfig', {}).get('systemPrompt')
        if custom_prompt:
            prompt = custom_prompt

        return prompt

    async def call_chatgpt(
        self,
        messages: List[Dict[str, str]],
        animal_config: Optional[Dict[str, Any]] = None,
        stream: bool = False
    ) -> Any:
        """
        Call ChatGPT API with messages

        Args:
            messages: List of message dicts with 'role' and 'content'
            animal_config: Optional animal configuration for customization
            stream: Whether to stream the response

        Returns:
            API response or async generator for streaming
        """
        if not self.api_key:
            raise ValueError("OpenAI API key not configured")

        # Get configuration from animal config or use defaults
        if animal_config and 'chatConfig' in animal_config:
            chat_config = animal_config['chatConfig']
            model = chat_config.get('model', DEFAULT_MODEL)
            temperature = chat_config.get('temperature', DEFAULT_TEMPERATURE)
            max_tokens = chat_config.get('maxTokens', DEFAULT_MAX_TOKENS)
            endpoint = chat_config.get('endpoint', self.base_url)
        else:
            model = DEFAULT_MODEL
            temperature = DEFAULT_TEMPERATURE
            max_tokens = DEFAULT_MAX_TOKENS
            endpoint = self.base_url

        # Prepare request
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        payload = {
            'model': model,
            'messages': messages,
            'temperature': temperature,
            'max_tokens': max_tokens,
            'stream': stream
        }

        if not self.session:
            self.session = aiohttp.ClientSession()

        try:
            if stream:
                return self._stream_response(endpoint, headers, payload)
            else:
                async with self.session.post(endpoint, headers=headers, json=payload) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data
        except aiohttp.ClientError as e:
            logger.error(f"ChatGPT API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error calling ChatGPT: {e}")
            raise

    async def _stream_response(
        self,
        endpoint: str,
        headers: Dict[str, str],
        payload: Dict[str, Any]
    ) -> AsyncGenerator[str, None]:
        """
        Stream response from ChatGPT API

        Args:
            endpoint: API endpoint URL
            headers: Request headers
            payload: Request payload

        Yields:
            Response chunks
        """
        async with self.session.post(endpoint, headers=headers, json=payload) as response:
            response.raise_for_status()

            async for line in response.content:
                line = line.decode('utf-8').strip()
                if line.startswith('data: '):
                    data_str = line[6:]  # Remove 'data: ' prefix
                    if data_str == '[DONE]':
                        break
                    try:
                        data = json.loads(data_str)
                        if 'choices' in data and len(data['choices']) > 0:
                            delta = data['choices'][0].get('delta', {})
                            if 'content' in delta:
                                yield delta['content']
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse streaming data: {data_str}")
                        continue

    async def get_animal_response(
        self,
        animal_id: str,
        user_message: str,
        conversation_history: List[Dict[str, str]] = None,
        animal_config: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Get response from animal personality

        Args:
            animal_id: Animal ID
            user_message: User's message
            conversation_history: Previous conversation messages
            animal_config: Animal configuration

        Returns:
            Response dictionary with reply and metadata
        """
        # Build messages list
        messages = []

        # Add system prompt
        if animal_config:
            system_prompt = self.build_animal_system_prompt(animal_config)
            messages.append({"role": "system", "content": system_prompt})

        # Add conversation history (last 10 messages)
        if conversation_history:
            messages.extend(conversation_history[-10:])

        # Add current user message
        messages.append({"role": "user", "content": user_message})

        # Call ChatGPT
        start_time = datetime.utcnow()

        try:
            response = await self.call_chatgpt(messages, animal_config)

            # Extract reply
            if 'choices' in response and len(response['choices']) > 0:
                reply = response['choices'][0]['message']['content']
            else:
                reply = "I'm sorry, I couldn't understand that. Could you please try again?"

            # Calculate latency
            end_time = datetime.utcnow()
            latency_ms = int((end_time - start_time).total_seconds() * 1000)

            # Extract token usage
            usage = response.get('usage', {})
            tokens_prompt = usage.get('prompt_tokens', 0)
            tokens_completion = usage.get('completion_tokens', 0)

            return {
                'reply': reply,
                'metadata': {
                    'animalId': animal_id,
                    'model': response.get('model', DEFAULT_MODEL),
                    'tokensPrompt': tokens_prompt,
                    'tokensCompletion': tokens_completion,
                    'latencyMs': latency_ms,
                    'timestamp': end_time.isoformat() + 'Z'
                }
            }
        except Exception as e:
            logger.error(f"Failed to get animal response: {e}")
            return {
                'reply': "I'm having a bit of trouble right now. Let's try again in a moment!",
                'metadata': {
                    'animalId': animal_id,
                    'error': str(e),
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                }
            }

    async def stream_animal_response(
        self,
        animal_id: str,
        user_message: str,
        conversation_history: List[Dict[str, str]] = None,
        animal_config: Dict[str, Any] = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream response from animal personality

        Args:
            animal_id: Animal ID
            user_message: User's message
            conversation_history: Previous conversation messages
            animal_config: Animal configuration

        Yields:
            Response chunks
        """
        # Build messages list
        messages = []

        # Add system prompt
        if animal_config:
            system_prompt = self.build_animal_system_prompt(animal_config)
            messages.append({"role": "system", "content": system_prompt})

        # Add conversation history (last 10 messages)
        if conversation_history:
            messages.extend(conversation_history[-10:])

        # Add current user message
        messages.append({"role": "user", "content": user_message})

        # Stream from ChatGPT
        try:
            async for chunk in await self.call_chatgpt(messages, animal_config, stream=True):
                yield chunk
        except Exception as e:
            logger.error(f"Failed to stream animal response: {e}")
            yield "I'm having a bit of trouble streaming my response. Let's try again!"


# Singleton instance
_chatgpt_instance = None

def get_chatgpt_integration() -> ChatGPTIntegration:
    """Get singleton ChatGPT integration instance"""
    global _chatgpt_instance
    if _chatgpt_instance is None:
        _chatgpt_instance = ChatGPTIntegration()
    return _chatgpt_instance