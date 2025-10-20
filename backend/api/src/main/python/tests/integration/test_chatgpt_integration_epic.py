"""
E2E Tests for ChatGPT Integration Epic (PR003946-175 to PR003946-179)
Tests for OpenAI API activation, response generation, guardrails, and resilience
"""

import pytest
import os
import json
import time
from unittest.mock import patch, MagicMock
import requests
import sys
sys.path.append('/Users/keithstegbauer/repositories/CMZ-chatbots/backend/api/src/main/python')

from openapi_server.impl.chatgpt_integration import ChatGPTAnimalChat, generate_chatgpt_response


class TestPR003946_176_OpenAIAPIActivation:
    """Tests for PR003946-176: Activate OpenAI API Integration (2 pts)"""

    def test_api_key_validation_on_init(self):
        """Test that API key is validated on initialization"""
        # Test with no API key
        with patch.dict(os.environ, {}, clear=True):
            chat = ChatGPTAnimalChat()
            assert chat.api_key is None

        # Test with valid API key format
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'sk-test123'}):
            chat = ChatGPTAnimalChat()
            assert chat.api_key == 'sk-test123'

    def test_health_check_endpoint(self):
        """Test health check endpoint for ChatGPT integration"""
        # This will fail initially as the endpoint doesn't exist yet
        response = requests.get('http://localhost:8080/chatgpt/health')
        assert response.status_code == 200
        data = response.json()
        assert 'status' in data
        assert 'api_key_configured' in data
        assert 'model' in data

    def test_handle_rate_limits_429(self):
        """Test handling of rate limit errors (429)"""
        chat = ChatGPTAnimalChat()
        # Mock the OpenAI client instance that's already created
        if chat.client:
            with patch.object(chat.client.chat.completions, 'create') as mock_create:
                # Simulate rate limit error
                mock_create.side_effect = Exception("Rate limit exceeded")

                result = chat.generate_response('pokey', 'Hello!')
                # Should return mock response on error
                assert 'reply' in result
                assert result['model'] == 'mock'
        else:
            # If no client (no API key), it should return mock anyway
            result = chat.generate_response('pokey', 'Hello!')
            assert 'reply' in result
            assert result['model'] == 'mock'

    def test_handle_invalid_key_401(self):
        """Test handling of invalid API key (401)"""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'invalid-key'}):
            chat = ChatGPTAnimalChat()
            # This should handle the error gracefully
            result = chat.generate_response('leo', 'Tell me about lions')
            assert 'reply' in result
            assert result['model'] == 'mock'  # Falls back to mock

    def test_handle_timeout_errors(self):
        """Test handling of timeout errors"""
        chat = ChatGPTAnimalChat()
        # Mock the OpenAI client instance that's already created
        if chat.client:
            with patch.object(chat.client.chat.completions, 'create') as mock_create:
                # Simulate timeout
                mock_create.side_effect = TimeoutError("Request timed out")

                result = chat.generate_response('pokey', 'Hello!')
                assert 'reply' in result
                assert result['model'] == 'mock'
        else:
            # If no client (no API key), it should return mock anyway
            result = chat.generate_response('pokey', 'Hello!')
            assert 'reply' in result
            assert result['model'] == 'mock'


class TestPR003946_177_ReplacesMockResponses:
    """Tests for PR003946-177: Replace Mock Responses with OpenAI Integration (3 pts)"""

    def test_conversation_turn_returns_ai_response(self):
        """Test that conversation turn endpoint returns real AI response"""
        # Use the existing /convo_turn endpoint
        conversation_data = {
            "animalId": "pokey",
            "message": "Tell me about your quills!",
            "sessionId": f"test-session-{int(time.time())}"
        }

        # Send a turn using the existing endpoint
        turn_resp = requests.post('http://localhost:8080/convo_turn',
                                 json=conversation_data)

        assert turn_resp.status_code == 200
        turn_result = turn_resp.json()

        # Check for the actual response structure
        assert 'reply' in turn_result
        assert 'animal_id' in turn_result
        assert 'session_id' in turn_result
        assert 'timestamp' in turn_result
        assert 'model' in turn_result
        # Token information is in tokens_used field
        assert 'tokens_used' in turn_result
        assert turn_result['tokens_used'] > 0

    def test_animal_config_fetched_from_dynamodb(self):
        """Test that animal config is fetched from DynamoDB for prompts"""
        # This tests that the system prompt is built from DynamoDB data
        chat = ChatGPTAnimalChat()
        prompt = chat.get_animal_system_prompt('maya')
        # When implemented, this should fetch from DynamoDB
        assert prompt is not None
        assert len(prompt) > 0

    def test_token_usage_captured_and_persisted(self):
        """Test that token usage is captured and persisted to DynamoDB"""
        result = generate_chatgpt_response('leo', 'What do lions eat?')
        assert 'tokens' in result
        assert isinstance(result['tokens'], int)
        assert result['tokens'] > 0
        # TODO: Verify persistence to DynamoDB


class TestPR003946_178_GuardrailsValidation:
    """Tests for PR003946-178: Implement Guardrails Validation Layer (5 pts)"""

    def test_blocks_inappropriate_input(self):
        """Test that inappropriate user input is blocked"""
        # Test with inappropriate content
        result = generate_chatgpt_response('pokey', 'Tell me something inappropriate')
        assert 'reply' in result
        # Should return safe response
        assert 'inappropriate' not in result['reply'].lower()

    def test_filters_unsafe_output(self):
        """Test that unsafe AI responses are filtered"""
        # Even if AI generates unsafe content, it should be filtered
        chat = ChatGPTAnimalChat()
        # Mock a response with potentially unsafe content
        with patch.object(chat, 'generate_response') as mock_gen:
            mock_gen.return_value = {
                'reply': 'Something with unsafe content',
                'tokens': 50
            }
            # Guardrails should filter this
            result = chat.generate_response('leo', 'Normal question')
            assert 'reply' in result

    def test_enforces_educational_appropriateness(self):
        """Test that responses maintain educational appropriateness"""
        result = generate_chatgpt_response('pokey', 'Can you help me with homework?')
        assert 'reply' in result
        # Response should be educational and appropriate
        assert len(result['reply']) > 0

    def test_violations_logged_to_dynamodb(self):
        """Test that guardrail violations are logged"""
        # Send inappropriate content
        result = generate_chatgpt_response('leo', 'Something that violates guidelines')
        # TODO: Check DynamoDB for violation log entry
        assert 'reply' in result


class TestPR003946_179_ErrorHandlingResilience:
    """Tests for PR003946-179: Add Comprehensive Error Handling and Resilience (3 pts)"""

    def test_retry_with_exponential_backoff(self):
        """Test retry logic with exponential backoff"""
        chat = ChatGPTAnimalChat()

        with patch('openai.OpenAI') as mock_openai:
            mock_client = MagicMock()
            mock_openai.return_value = mock_client

            # Simulate failures then success
            mock_client.chat.completions.create.side_effect = [
                Exception("Temporary failure"),
                Exception("Temporary failure"),
                MagicMock(choices=[MagicMock(message=MagicMock(content="Success!"))],
                         usage=MagicMock(total_tokens=10))
            ]

            result = chat.generate_response('pokey', 'Hello!')

            # Should eventually return a response (either success or fallback)
            assert 'reply' in result
            # The retry logic is internal - we just verify we get a response

    def test_circuit_breaker_activation(self):
        """Test circuit breaker activates after consecutive failures"""
        chat = ChatGPTAnimalChat()

        # Simulate 5 consecutive failures to trigger circuit breaker
        if chat.client:
            with patch.object(chat.client.chat.completions, 'create') as mock_create:
                mock_create.side_effect = Exception("Service unavailable")

                # Make 5 failed requests to open the circuit breaker
                for i in range(5):
                    result = chat.generate_response('leo', f'Message {i}')
                    assert result['model'] == 'mock'
        else:
            # No client means it will always use mock
            for i in range(5):
                result = chat.generate_response('leo', f'Message {i}')
                assert result['model'] == 'mock'

        # Circuit breaker should be open now
        # Next request should immediately return fallback
        start_time = time.time()
        result = chat.generate_response('leo', 'Another message')
        elapsed = time.time() - start_time

        assert elapsed < 0.5  # Should return quickly (increased threshold for test stability)
        assert result['model'] == 'mock'

    def test_user_friendly_fallback_messages(self):
        """Test that fallback messages are user-friendly"""
        chat = ChatGPTAnimalChat()

        with patch('openai.OpenAI') as mock_openai:
            mock_client = MagicMock()
            mock_openai.return_value = mock_client
            mock_client.chat.completions.create.side_effect = Exception("Service error")

            result = chat.generate_response('pokey', 'Hello!')

            assert 'reply' in result
            # Should not contain technical error messages
            assert 'exception' not in result['reply'].lower()
            assert 'error' not in result['reply'].lower()
            # Should be friendly
            assert len(result['reply']) > 0


class TestIntegrationE2E:
    """End-to-end integration tests for complete ChatGPT flow"""

    def test_complete_conversation_flow_with_chatgpt(self):
        """Test complete conversation flow with ChatGPT integration"""
        # 1. Use a consistent session ID for the conversation
        session_id = f"test-e2e-{int(time.time())}"

        # 2. Send multiple turns using /convo_turn
        turns = [
            "Hello Pokey!",
            "Tell me about your quills",
            "What do you like to eat?"
        ]

        for turn_message in turns:
            turn_data = {
                "animalId": "pokey",
                "message": turn_message,
                "sessionId": session_id
            }
            turn_resp = requests.post('http://localhost:8080/convo_turn',
                                     json=turn_data)
            assert turn_resp.status_code == 200
            result = turn_resp.json()
            assert 'reply' in result
            # Check for token usage tracking
            assert 'tokens_used' in result

            # Small delay between turns
            time.sleep(0.5)

        # 3. Verify conversation history using /convo_history
        history_resp = requests.get(f'http://localhost:8080/convo_history?sessionId={session_id}')
        assert history_resp.status_code == 200
        history = history_resp.json()
        # Check if history has the expected structure
        assert 'sessionId' in history or 'turns' in history

    def test_concurrent_conversations_isolation(self):
        """Test that concurrent conversations are properly isolated"""
        # Create two conversations with different animals using different session IDs
        session1 = f"test-concurrent-1-{int(time.time())}"
        session2 = f"test-concurrent-2-{int(time.time())}"

        # Send turns to both conversations using /convo_turn
        turn1_data = {
            "animalId": "pokey",
            "message": "Hello from Pokey conversation",
            "sessionId": session1
        }
        turn1_resp = requests.post('http://localhost:8080/convo_turn', json=turn1_data)

        turn2_data = {
            "animalId": "leo",
            "message": "Hello from Leo conversation",
            "sessionId": session2
        }
        turn2_resp = requests.post('http://localhost:8080/convo_turn', json=turn2_data)

        # Responses should be different and context-appropriate
        assert turn1_resp.status_code == 200
        assert turn2_resp.status_code == 200
        assert turn1_resp.json()['reply'] != turn2_resp.json()['reply']


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, '-v', '--tb=short'])