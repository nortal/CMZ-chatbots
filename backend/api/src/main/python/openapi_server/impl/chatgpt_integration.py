"""
ChatGPT Integration Module for CMZ Chatbot
This module will handle OpenAI API integration for generating animal character responses
"""

import os
from typing import Dict, Any, Optional, List
# Uncomment when ready to integrate:
# import openai
# from openai import OpenAI

class ChatGPTAnimalChat:
    """
    ChatGPT integration for animal character conversations
    """

    def __init__(self):
        """Initialize ChatGPT client with API key from environment"""
        self.api_key = os.getenv('OPENAI_API_KEY')
        # Uncomment when ready:
        # self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-3.5-turbo"  # or "gpt-4" for better responses

    def get_animal_system_prompt(self, animal_id: str) -> str:
        """
        Get the system prompt for a specific animal character

        Args:
            animal_id: The identifier for the animal

        Returns:
            System prompt string for ChatGPT
        """
        prompts = {
            'pokey': """You are Pokey the Porcupine at Cougar Mountain Zoo. You are friendly,
            educational, and love sharing facts about porcupines. Key facts about you:
            - You have about 30,000 quills
            - Your quills have tiny barbs and are used for defense
            - You're an excellent climber
            - You love sweet potatoes and corn on the cob
            Always respond in a friendly, engaging way suitable for children and families visiting the zoo.""",

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
        max_tokens: int = 150
    ) -> Dict[str, Any]:
        """
        Generate a response using ChatGPT API

        Args:
            animal_id: The animal character identifier
            user_message: The user's message
            conversation_history: Optional previous conversation turns
            temperature: Response creativity (0.0-1.0)
            max_tokens: Maximum response length

        Returns:
            Dict with 'reply' and 'tokens' keys
        """

        # For now, return mock response (uncomment when ready to integrate)
        """
        try:
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

            return {
                'reply': reply,
                'tokens': tokens_used,
                'model': self.model,
                'finish_reason': response.choices[0].finish_reason
            }

        except Exception as e:
            # Fallback to mock response on error
            return self.get_mock_response(animal_id, user_message)
        """

        # Temporary mock implementation
        return self.get_mock_response(animal_id, user_message)

    def get_mock_response(self, animal_id: str, user_message: str) -> Dict[str, Any]:
        """
        Get a mock response for testing without API calls
        """
        responses = {
            'pokey': "Hi there! I'm Pokey the Porcupine! Did you know my quills are actually modified hairs? Pretty cool, right?",
            'leo': "Roar! Welcome to my kingdom at Cougar Mountain Zoo! What would you like to know about the mighty lions?",
            'default': "Hello! I'm so excited to meet you here at Cougar Mountain Zoo!"
        }

        reply = responses.get(animal_id, responses['default'])

        return {
            'reply': reply,
            'tokens': len(reply.split()) * 2,
            'model': 'mock',
            'finish_reason': 'stop'
        }


# Integration function for the conversation handler
def generate_chatgpt_response(
    animal_id: str,
    message: str,
    context_summary: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate a response using ChatGPT for the conversation handler

    This function can be imported and used in conversation.py
    """
    chat_client = ChatGPTAnimalChat()

    # Convert context summary to conversation history if needed
    conversation_history = []
    if context_summary:
        # Could parse context_summary to extract previous turns
        pass

    return chat_client.generate_response(
        animal_id=animal_id,
        user_message=message,
        conversation_history=conversation_history
    )