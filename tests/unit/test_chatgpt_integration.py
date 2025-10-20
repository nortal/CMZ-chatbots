"""
Unit tests for chatgpt_integration.py
Tests ChatGPT API integration for PR003946-157
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import asyncio
import json
import sys
import os

# Add the src path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../backend/api/src/main/python')))


class TestChatGPTIntegration(unittest.TestCase):
    """Test ChatGPT API integration for animal personalities"""

    def setUp(self):
        """Set up test fixtures"""
        # Import after path setup
        from openapi_server.impl.utils.chatgpt_integration import ChatGPTIntegration
        self.ChatGPTIntegration = ChatGPTIntegration

    def test_build_animal_system_prompt_default(self):
        """Test building system prompt with default animal config"""
        # Setup
        integration = self.ChatGPTIntegration()
        animal_config = {
            'name': 'Leo',
            'chatConfig': {
                'personality': {
                    'traits': ['friendly', 'educational', 'playful'],
                    'knowledge': ['savanna facts', 'lion behavior', 'conservation']
                }
            }
        }

        # Execute
        prompt = integration.build_animal_system_prompt(animal_config)

        # Assert
        self.assertIn('Leo', prompt)
        self.assertIn('friendly', prompt)
        self.assertIn('educational', prompt)
        self.assertIn('savanna facts', prompt)
        self.assertIn('conservation', prompt)
        self.assertIn('Cougar Mountain Zoo', prompt)

    def test_build_animal_system_prompt_custom(self):
        """Test building system prompt with custom prompt"""
        # Setup
        integration = self.ChatGPTIntegration()
        custom_prompt = "You are Max the Tiger, fierce and majestic!"
        animal_config = {
            'name': 'Max',
            'chatConfig': {
                'systemPrompt': custom_prompt
            }
        }

        # Execute
        prompt = integration.build_animal_system_prompt(animal_config)

        # Assert
        self.assertEqual(prompt, custom_prompt)

    @patch('aiohttp.ClientSession')
    async def test_call_chatgpt_success(self, mock_session_class):
        """Test successful ChatGPT API call"""
        # Setup
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value={
            'choices': [{
                'message': {'content': 'Hello! I am Leo the Lion!'}
            }],
            'usage': {
                'prompt_tokens': 50,
                'completion_tokens': 10
            }
        })
        mock_response.raise_for_status = Mock()

        mock_session = AsyncMock()
        mock_session.post.return_value.__aenter__.return_value = mock_response
        mock_session_class.return_value = mock_session

        integration = self.ChatGPTIntegration()
        integration.api_key = 'test-key'
        integration.session = mock_session

        messages = [
            {'role': 'system', 'content': 'You are Leo'},
            {'role': 'user', 'content': 'Hello!'}
        ]

        # Execute
        result = await integration.call_chatgpt(messages)

        # Assert
        self.assertIn('choices', result)
        self.assertEqual(
            result['choices'][0]['message']['content'],
            'Hello! I am Leo the Lion!'
        )

    @patch('aiohttp.ClientSession')
    async def test_get_animal_response_success(self, mock_session_class):
        """Test getting complete animal response"""
        # Setup
        mock_response = AsyncMock()
        mock_response.json = AsyncMock(return_value={
            'model': 'gpt-4',
            'choices': [{
                'message': {'content': 'Roar! I love the savanna!'}
            }],
            'usage': {
                'prompt_tokens': 100,
                'completion_tokens': 20
            }
        })
        mock_response.raise_for_status = Mock()

        mock_session = AsyncMock()
        mock_session.post.return_value.__aenter__.return_value = mock_response
        mock_session_class.return_value = mock_session

        integration = self.ChatGPTIntegration()
        integration.api_key = 'test-key'
        integration.session = mock_session

        animal_config = {
            'name': 'Leo',
            'chatConfig': {
                'personality': {
                    'traits': ['friendly']
                }
            }
        }

        # Execute
        result = await integration.get_animal_response(
            animal_id='lion_001',
            user_message='Tell me about the savanna!',
            conversation_history=[],
            animal_config=animal_config
        )

        # Assert
        self.assertEqual(result['reply'], 'Roar! I love the savanna!')
        self.assertEqual(result['metadata']['animalId'], 'lion_001')
        self.assertEqual(result['metadata']['tokensPrompt'], 100)
        self.assertEqual(result['metadata']['tokensCompletion'], 20)
        self.assertIn('timestamp', result['metadata'])
        self.assertIn('latencyMs', result['metadata'])

    async def test_get_animal_response_no_api_key(self):
        """Test fallback when no API key configured"""
        # Setup
        integration = self.ChatGPTIntegration()
        integration.api_key = ''  # No API key

        # Execute
        result = await integration.get_animal_response(
            animal_id='lion_001',
            user_message='Hello!',
            conversation_history=[],
            animal_config=None
        )

        # Assert - should return fallback response
        self.assertIn('trouble', result['reply'].lower())
        self.assertEqual(result['metadata']['animalId'], 'lion_001')
        self.assertIn('error', result['metadata'])

    @patch('aiohttp.ClientSession')
    async def test_stream_response(self, mock_session_class):
        """Test streaming response from ChatGPT"""
        # Setup streaming response
        async def mock_content_generator():
            chunks = [
                b'data: {"choices":[{"delta":{"content":"Hello "}}]}\n',
                b'data: {"choices":[{"delta":{"content":"there!"}}]}\n',
                b'data: [DONE]\n'
            ]
            for chunk in chunks:
                yield chunk

        mock_response = AsyncMock()
        mock_response.content = mock_content_generator()
        mock_response.raise_for_status = Mock()

        mock_session = AsyncMock()
        mock_session.post.return_value.__aenter__.return_value = mock_response
        mock_session_class.return_value = mock_session

        integration = self.ChatGPTIntegration()
        integration.api_key = 'test-key'
        integration.session = mock_session

        # Execute
        messages = [{'role': 'user', 'content': 'Hi!'}]
        stream_gen = await integration.call_chatgpt(messages, stream=True)

        # Collect streamed chunks
        chunks = []
        async for chunk in stream_gen:
            chunks.append(chunk)

        # Assert
        self.assertEqual(chunks, ['Hello ', 'there!'])

    def test_singleton_instance(self):
        """Test singleton pattern for ChatGPT integration"""
        from openapi_server.impl.utils.chatgpt_integration import get_chatgpt_integration

        # Get two instances
        instance1 = get_chatgpt_integration()
        instance2 = get_chatgpt_integration()

        # Assert they're the same
        self.assertIs(instance1, instance2)


def run_async_test(coro):
    """Helper to run async tests"""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


if __name__ == '__main__':
    # Monkey patch async test methods
    test_methods = [
        'test_call_chatgpt_success',
        'test_get_animal_response_success',
        'test_get_animal_response_no_api_key',
        'test_stream_response'
    ]

    for method_name in test_methods:
        original = getattr(TestChatGPTIntegration, method_name)
        wrapped = lambda self, orig=original: run_async_test(orig(self))
        setattr(TestChatGPTIntegration, method_name, wrapped)

    unittest.main()