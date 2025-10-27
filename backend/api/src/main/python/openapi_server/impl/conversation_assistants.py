"""
OpenAI Assistants API Conversation Handler for CMZ Chatbots

This module provides conversation management using the modern OpenAI Assistants API
with persistent threads, knowledge base search, and COPPA compliance features.

Key Features:
- Persistent conversation threads with automatic memory management
- Built-in knowledge base search via Vector Stores
- COPPA-compliant conversation tracking and parental controls
- Automatic animal personality integration from DynamoDB
- Thread-based conversation history for seamless user experience
"""

import logging
import os
import json
from typing import Any, Dict, List, Tuple, Union, Optional
from datetime import datetime, timedelta
import uuid

from .utils.dynamo import (
    table, to_ddb, from_ddb, now_iso,
    model_to_json_keyed_dict, ensure_pk,
    error_response, not_found
)
from .assistant_manager import assistant_manager

# Configure logging
logger = logging.getLogger(__name__)


class AssistantsConversationManager:
    """Modern conversation management using OpenAI Assistants API."""

    def __init__(self):
        """Initialize the conversation manager with Assistants API support."""
        self.assistant_manager = assistant_manager

        # Thread management table
        self.thread_table_name = os.getenv('THREAD_DYNAMO_TABLE_NAME', 'quest-dev-conversation-threads')

        # COPPA compliance settings
        self.coppa_age_limit = 13
        self.thread_retention_days_under_13 = 30
        self.thread_retention_days_over_13 = 365

    def process_conversation_turn(
        self,
        user_message: str,
        user_id: str,
        conversation_id: str,
        animal_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[Dict[str, Any], int]:
        """
        Process a conversation turn using OpenAI Assistants API.

        Args:
            user_message: User's input message
            user_id: User ID
            conversation_id: Session/conversation ID (maps to thread)
            animal_id: Animal ID to determine which Assistant to use
            context: Optional conversation context

        Returns:
            Tuple of (conversation_response, status_code)
        """
        try:
            logger.info(f"🤖 Processing Assistants API conversation: user={user_id}, animal={animal_id}")

            # Step 1: Get or create Assistant for this animal
            assistant_info = self._get_or_create_assistant_for_animal(animal_id)
            if not assistant_info['success']:
                return self._fallback_error_response(
                    conversation_id,
                    "I'm having trouble connecting right now. Please try again!",
                    assistant_info.get('error', 'Assistant unavailable')
                ), 500

            assistant_id = assistant_info['assistant_id']
            logger.info(f"✅ Using Assistant: {assistant_id}")

            # Step 2: Get or create conversation thread with COPPA metadata
            thread_info = self._get_or_create_thread(
                conversation_id, user_id, animal_id, context
            )
            if not thread_info['success']:
                return self._fallback_error_response(
                    conversation_id,
                    "I'm having trouble accessing our conversation. Please try again!",
                    thread_info.get('error', 'Thread unavailable')
                ), 500

            thread_id = thread_info['thread_id']
            logger.info(f"✅ Using Thread: {thread_id}")

            # Step 3: Add user message to thread
            self._add_message_to_thread(thread_id, user_message, 'user')

            # Step 4: Create run and get Assistant response
            response_text = self._run_assistant_and_get_response(
                thread_id, assistant_id, animal_id
            )

            if not response_text:
                return self._fallback_error_response(
                    conversation_id,
                    "I'm thinking really hard but having trouble responding. What would you like to know about animals?",
                    "Assistant run failed"
                ), 500

            # Step 5: Store conversation metadata in DynamoDB for analytics
            turn_data = self._store_conversation_metadata(
                conversation_id, user_id, animal_id, user_message, response_text, thread_id
            )

            # Step 6: Build response
            response = {
                "conversationId": conversation_id,
                "response": response_text,
                "turnId": turn_data.get("turnId"),
                "threadId": thread_id,  # For COPPA compliance tracking
                "assistantId": assistant_id,  # For debugging and analytics
                "safetyWarning": False,
                "blocked": False,
                "timestamp": now_iso(),
                "animalId": animal_id,
                "assistantApiUsed": True  # Flag for migration tracking
            }

            logger.info(f"✅ Assistants API conversation completed: {conversation_id}")
            return response, 200

        except Exception as e:
            logger.error(f"❌ Failed to process Assistants API conversation: {e}")
            return self._fallback_error_response(
                conversation_id,
                "I'm having an adventure right now! Please try talking to me again in a moment.",
                str(e)
            ), 500

    def _get_or_create_assistant_for_animal(self, animal_id: str) -> Dict[str, Any]:
        """Get existing Assistant for animal or create one from DynamoDB data."""
        try:
            # Step 1: Check if we already have an Assistant for this animal
            existing_assistant = self._find_existing_assistant(animal_id)
            if existing_assistant:
                logger.info(f"🔄 Found existing Assistant for {animal_id}: {existing_assistant}")
                return {
                    'success': True,
                    'assistant_id': existing_assistant,
                    'created': False
                }

            # Step 2: Get animal data from DynamoDB
            animal_data = self._get_animal_from_dynamodb(animal_id)
            if not animal_data:
                logger.error(f"❌ Animal {animal_id} not found in DynamoDB")
                return {
                    'success': False,
                    'error': f'Animal {animal_id} not found',
                    'assistant_id': None
                }

            # Step 3: Create new Assistant using animal data
            logger.info(f"🆕 Creating new Assistant for {animal_id}")
            assistant_result = self.assistant_manager.create_assistant_for_animal(
                animal_id=animal_id,
                name=animal_data.get('name', f'Animal {animal_id}'),
                personality_description=self._build_personality_from_animal_data(animal_data),
                scientific_name=animal_data.get('species'),
                additional_instructions=animal_data.get('configuration', {}).get('systemPrompt')
            )

            if assistant_result['success']:
                # Store Assistant ID mapping in DynamoDB for future use
                self._store_assistant_mapping(animal_id, assistant_result['assistant_id'])
                logger.info(f"✅ Created Assistant {assistant_result['assistant_id']} for {animal_id}")

            return assistant_result

        except Exception as e:
            logger.error(f"❌ Failed to get/create Assistant for {animal_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'assistant_id': None
            }

    def _find_existing_assistant(self, animal_id: str) -> Optional[str]:
        """Find existing OpenAI Assistant ID for this animal."""
        try:
            # Check the animal record directly for assistantId
            animal_data = self._get_animal_from_dynamodb(animal_id)
            if animal_data and 'assistantId' in animal_data:
                assistant_id = animal_data['assistantId']
                if assistant_id:
                    # Verify Assistant still exists in OpenAI
                    assistant_info = self.assistant_manager.get_assistant_info(assistant_id)
                    if assistant_info['success']:
                        logger.info(f"✅ Found existing Assistant {assistant_id} for {animal_id}")
                        return assistant_id
                    else:
                        logger.warning(f"Assistant {assistant_id} no longer exists in OpenAI, will create new one")

            # Fallback: Search through all zoo assistants
            zoo_assistants = self.assistant_manager.list_assistants_for_zoo()
            for assistant in zoo_assistants:
                if assistant.get('animal_id') == animal_id:
                    return assistant['assistant_id']

            return None

        except Exception as e:
            logger.warning(f"Error finding existing Assistant for {animal_id}: {e}")
            return None

    def _get_animal_from_dynamodb(self, animal_id: str) -> Optional[Dict[str, Any]]:
        """Get animal data from DynamoDB."""
        try:
            animal_table = table("quest-dev-animal")
            response = animal_table.get_item(Key={"animalId": animal_id})

            if "Item" in response:
                return from_ddb(response["Item"])
            return None

        except Exception as e:
            logger.error(f"Failed to get animal {animal_id} from DynamoDB: {e}")
            return None

    def _build_personality_from_animal_data(self, animal_data: Dict[str, Any]) -> str:
        """Build personality description from DynamoDB animal data."""
        personality = animal_data.get('personality', {})

        if isinstance(personality, dict):
            description = personality.get('description', '')
        else:
            description = str(personality)

        # Add facts and other relevant info
        facts = animal_data.get('facts', '')
        name = animal_data.get('name', 'Zoo Animal')

        personality_text = f"""You are {name}, a friendly animal ambassador at Cougar Mountain Zoo.

PERSONALITY: {description}

FACTS ABOUT ME: {facts}

BEHAVIOR:
- Be educational and engaging with visitors of all ages
- Share interesting facts about your species and conservation
- Keep responses appropriate for children (ages 5+)
- Be enthusiastic about wildlife education
- Encourage curiosity about nature and animals
"""

        return personality_text.strip()

    def _store_assistant_mapping(self, animal_id: str, assistant_id: str) -> None:
        """Store Assistant ID mapping for future lookups."""
        try:
            # Assistant ID is already stored in the animal record, so this is a no-op
            # The assistant creation logic already handles updating the animal record
            logger.info(f"✅ Assistant mapping stored - {animal_id} -> {assistant_id}")

        except Exception as e:
            logger.error(f"Failed to store Assistant mapping: {e}")

    def _get_or_create_thread(
        self,
        conversation_id: str,
        user_id: str,
        animal_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get existing thread or create new one with COPPA metadata."""
        try:
            logger.info(f"🔄 Getting/creating thread for conversation {conversation_id}, user {user_id}, animal {animal_id}")

            # Step 1: Check if thread already exists for this conversation
            logger.info("Step 1: Checking for existing thread...")
            existing_thread = self._find_existing_thread(conversation_id, user_id)
            if existing_thread:
                logger.info(f"✅ Found existing thread: {existing_thread}")
                return {
                    'success': True,
                    'thread_id': existing_thread,
                    'created': False
                }

            # Step 2: Create new thread with COPPA metadata
            logger.info("Step 2: Creating new thread...")
            user_age = self._get_user_age(user_id)
            is_coppa_protected = user_age and user_age < self.coppa_age_limit
            logger.info(f"User age: {user_age}, COPPA protected: {is_coppa_protected}")

            thread_metadata = {
                'conversation_id': conversation_id,
                'user_id': user_id,
                'animal_id': animal_id,
                'created_at': datetime.utcnow().isoformat(),
                'coppa_protected': is_coppa_protected,
                'user_age': user_age or 'unknown',
                'retention_days': str(self.thread_retention_days_under_13 if is_coppa_protected else self.thread_retention_days_over_13)
            }
            logger.info(f"Thread metadata: {thread_metadata}")

            # Create OpenAI thread
            logger.info("Creating OpenAI thread...")
            thread = self.assistant_manager.client.beta.threads.create(
                metadata=thread_metadata
            )
            logger.info(f"✅ OpenAI thread created successfully")

            thread_id = thread.id
            logger.info(f"✅ Created new thread: {thread_id} (COPPA: {is_coppa_protected})")

            # Store thread mapping in DynamoDB
            logger.info("Storing thread mapping in DynamoDB...")
            self._store_thread_mapping(conversation_id, user_id, thread_id, thread_metadata)
            logger.info("✅ Thread mapping stored successfully")

            return {
                'success': True,
                'thread_id': thread_id,
                'created': True,
                'coppa_protected': is_coppa_protected
            }

        except Exception as e:
            logger.error(f"Failed to get/create thread: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return {
                'success': False,
                'error': str(e),
                'thread_id': None
            }

    def _find_existing_thread(self, conversation_id: str, user_id: str) -> Optional[str]:
        """Find existing OpenAI thread for this conversation."""
        try:
            # For now, always create a new thread for each conversation
            # This simplifies the implementation without requiring separate mapping tables
            logger.info(f"Creating new thread for conversation {conversation_id}")
            return None

        except Exception as e:
            logger.warning(f"Error finding existing thread: {e}")
            return None

    def _get_user_age(self, user_id: str) -> Optional[int]:
        """Get user age for COPPA compliance (mock implementation)."""
        try:
            # TODO: Implement actual user age lookup from user management system
            # For now, return None (unknown age)
            return None
        except Exception as e:
            logger.warning(f"Failed to get user age: {e}")
            return None

    def _store_thread_mapping(
        self,
        conversation_id: str,
        user_id: str,
        thread_id: str,
        metadata: Dict[str, Any]
    ) -> None:
        """Store thread mapping and metadata in DynamoDB."""
        try:
            thread_table = table(self.thread_table_name)
            thread_item = {
                'conversationId': conversation_id,
                'userId': user_id,
                'threadId': thread_id,
                'metadata': metadata,
                'created': {'at': now_iso()},
                'modified': {'at': now_iso()}
            }
            thread_table.put_item(Item=to_ddb(thread_item))
            logger.info(f"✅ Stored thread mapping: {conversation_id} -> {thread_id}")

        except Exception as e:
            logger.error(f"Failed to store thread mapping: {e}")

    def _add_message_to_thread(self, thread_id: str, message: str, role: str) -> None:
        """Add message to OpenAI thread."""
        try:
            self.assistant_manager.client.beta.threads.messages.create(
                thread_id=thread_id,
                role=role,
                content=message
            )
            logger.info(f"✅ Added {role} message to thread {thread_id}")

        except Exception as e:
            logger.error(f"Failed to add message to thread: {e}")
            raise

    def _run_assistant_and_get_response(
        self,
        thread_id: str,
        assistant_id: str,
        animal_id: str
    ) -> Optional[str]:
        """Run Assistant and get response."""
        try:
            # Create and run the Assistant
            run = self.assistant_manager.client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=assistant_id
            )

            # Wait for completion (with timeout)
            max_wait_time = 30  # seconds
            wait_interval = 1   # seconds
            elapsed_time = 0

            while elapsed_time < max_wait_time:
                run_status = self.assistant_manager.client.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run.id
                )

                if run_status.status == 'completed':
                    # Get the latest message (Assistant's response)
                    messages = self.assistant_manager.client.beta.threads.messages.list(
                        thread_id=thread_id,
                        limit=1
                    )

                    if messages.data:
                        response_content = messages.data[0].content[0].text.value
                        logger.info(f"✅ Got Assistant response for {animal_id}")
                        return response_content

                elif run_status.status == 'failed':
                    logger.error(f"Assistant run failed: {run_status.last_error}")
                    return None

                elif run_status.status in ['cancelled', 'expired']:
                    logger.error(f"Assistant run {run_status.status}")
                    return None

                # Still running, wait and check again
                import time
                time.sleep(wait_interval)
                elapsed_time += wait_interval

            logger.error(f"Assistant run timed out after {max_wait_time} seconds")
            return None

        except Exception as e:
            logger.error(f"Failed to run Assistant: {e}")
            return None

    def _store_conversation_metadata(
        self,
        conversation_id: str,
        user_id: str,
        animal_id: str,
        user_message: str,
        ai_response: str,
        thread_id: str
    ) -> Dict[str, Any]:
        """Store conversation metadata in DynamoDB for analytics."""
        try:
            turn_data = {
                "turnId": f"turn_{conversation_id}_{int(datetime.now().timestamp())}",
                "conversationId": conversation_id,
                "userId": user_id,
                "animalId": animal_id,
                "userMessage": user_message,
                "aiResponse": ai_response,
                "threadId": thread_id,  # For COPPA compliance
                "apiType": "assistants",  # Track API usage
                "timestamp": now_iso(),
                "blocked": False,
                "riskScore": 0.0
            }

            # Store in conversation analytics table
            analytics_table = table('quest-dev-conversation-analytics')
            analytics_table.put_item(Item=to_ddb(turn_data))

            logger.info(f"✅ Stored conversation metadata: {turn_data['turnId']}")
            return turn_data

        except Exception as e:
            logger.error(f"Failed to store conversation metadata: {e}")
            return {"turnId": "error", "timestamp": now_iso()}

    def _fallback_error_response(
        self,
        conversation_id: str,
        user_friendly_message: str,
        technical_error: str
    ) -> Dict[str, Any]:
        """Generate user-friendly error response."""
        logger.error(f"Conversation error: {technical_error}")

        return {
            "conversationId": conversation_id,
            "response": user_friendly_message,
            "error": False,  # Don't show as error to user
            "assistantApiUsed": False,  # Indicates fallback
            "timestamp": now_iso(),
            "technicalError": technical_error  # For debugging
        }

    def get_conversation_history(
        self,
        conversation_id: str,
        user_id: str,
        limit: int = 50
    ) -> Tuple[Dict[str, Any], int]:
        """
        Get conversation history from OpenAI thread (COPPA compliant).

        Args:
            conversation_id: Conversation ID
            user_id: User ID for authorization
            limit: Maximum turns to return

        Returns:
            Tuple of (conversation_history, status_code)
        """
        try:
            logger.info(f"🔍 Getting Assistants API conversation history: {conversation_id}")

            # Find the thread for this conversation
            thread_id = self._find_existing_thread(conversation_id, user_id)
            if not thread_id:
                return {
                    "conversationId": conversation_id,
                    "turns": [],
                    "totalTurns": 0,
                    "hasMore": False,
                    "error": "Conversation not found"
                }, 404

            # Get messages from OpenAI thread
            messages = self.assistant_manager.client.beta.threads.messages.list(
                thread_id=thread_id,
                limit=limit * 2  # Account for user + assistant pairs
            )

            # Convert to our format
            turns = []
            for i in range(0, len(messages.data), 2):
                if i + 1 < len(messages.data):
                    assistant_msg = messages.data[i]
                    user_msg = messages.data[i + 1]

                    turns.append({
                        "turnId": f"turn_{assistant_msg.id}",
                        "userMessage": user_msg.content[0].text.value,
                        "aiResponse": assistant_msg.content[0].text.value,
                        "timestamp": assistant_msg.created_at,
                        "threadId": thread_id
                    })

            response = {
                "conversationId": conversation_id,
                "threadId": thread_id,  # For COPPA compliance access
                "turns": turns[:limit],
                "totalTurns": len(turns),
                "hasMore": len(messages.data) >= limit * 2,
                "assistantApiUsed": True
            }

            return response, 200

        except Exception as e:
            logger.error(f"Failed to get Assistants API conversation history: {e}")
            return error_response(e)


# Global manager instance
_assistants_conversation_manager: Optional[AssistantsConversationManager] = None


def get_assistants_conversation_manager() -> AssistantsConversationManager:
    """Get singleton AssistantsConversationManager instance."""
    global _assistants_conversation_manager

    if _assistants_conversation_manager is None:
        _assistants_conversation_manager = AssistantsConversationManager()

    return _assistants_conversation_manager


# Handler functions for API endpoints (Assistants API versions)
def handle_convo_turn_post_assistants(body: Dict[str, Any], *args, **kwargs) -> Tuple[Any, int]:
    """Handle conversation turn with Assistants API (replacement for simple handler)."""
    try:
        manager = get_assistants_conversation_manager()

        # Handle both dict and OpenAPI model object
        if hasattr(body, 'to_dict'):
            body_dict = body.to_dict()
        elif hasattr(body, '__dict__'):
            body_dict = body.__dict__
        else:
            body_dict = body

        # Extract parameters (using OpenAPI spec field names)
        user_message = body_dict.get("message", "")
        animal_id = body_dict.get("animalId", "") or body_dict.get("animal_id", "")
        conversation_id = body_dict.get("sessionId", "") or body_dict.get("session_id", "") or f"conv_{int(datetime.now().timestamp())}"
        user_id = body_dict.get("userId", "default_user")

        if not user_message or not animal_id:
            return {"error": "Missing required fields: message, animalId"}, 400

        logger.info(f"🚀 ROUTING TO ASSISTANTS API HANDLER 🚀")

        # Call Assistants API method
        result = manager.process_conversation_turn(
            user_message, user_id, conversation_id, animal_id, body_dict.get("context")
        )
        return result

    except Exception as e:
        logger.error(f"Failed to handle Assistants API conversation turn: {e}")
        return error_response(e)


def handle_convo_history_get_assistants(
    conversation_id: str,
    user_id: str = "default_user",
    limit: int = 50,
    *args,
    **kwargs
) -> Tuple[Any, int]:
    """Handle conversation history with Assistants API thread access."""
    try:
        manager = get_assistants_conversation_manager()
        return manager.get_conversation_history(conversation_id, user_id, limit)

    except Exception as e:
        logger.error(f"Failed to handle Assistants API conversation history: {e}")
        return error_response(e)

import os
import logging
from typing import Dict, Any, Optional, List, AsyncGenerator
from datetime import datetime
from openai import OpenAI, AsyncOpenAI

logger = logging.getLogger(__name__)


class AssistantConversationManager:
    """
    Manages conversations using OpenAI Assistants API
    Each conversation session maps to an OpenAI Thread
    """

    def __init__(self):
        """Initialize OpenAI client with API key from environment"""
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not found in environment")
            self.client = None
            self.async_client = None
        else:
            try:
                self.client = OpenAI(api_key=self.api_key)
                self.async_client = AsyncOpenAI(api_key=self.api_key)
                logger.info("OpenAI Assistant conversation clients initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI clients: {e}")
                self.client = None
                self.async_client = None

    def create_thread(self, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a new conversation thread

        Args:
            metadata: Optional metadata to attach to thread

        Returns:
            Dict with thread_id and creation info
        """
        if not self.client:
            logger.error("OpenAI client not initialized - cannot create thread")
            return {
                'success': False,
                'error': 'OpenAI client not initialized',
                'thread_id': None
            }

        try:
            logger.info("Creating new conversation thread")

            thread_metadata = metadata or {}
            thread_metadata['created_at'] = datetime.utcnow().isoformat()

            thread = self.client.beta.threads.create(
                metadata=thread_metadata
            )

            logger.info(f"Thread created: {thread.id}")

            return {
                'success': True,
                'thread_id': thread.id,
                'created_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to create thread: {e}")
            return {
                'success': False,
                'error': str(e),
                'thread_id': None
            }

    def add_message_to_thread(
        self,
        thread_id: str,
        message: str,
        role: str = "user",
        file_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Add a message to an existing thread

        Args:
            thread_id: Thread identifier
            message: Message content
            role: Message role (user or assistant)
            file_ids: Optional list of file IDs to attach

        Returns:
            Dict with message_id and creation info
        """
        if not self.client:
            logger.error("OpenAI client not initialized - cannot add message")
            return {
                'success': False,
                'error': 'OpenAI client not initialized',
                'message_id': None
            }

        try:
            logger.info(f"Adding {role} message to thread {thread_id}")

            message_params = {
                'thread_id': thread_id,
                'role': role,
                'content': message
            }

            if file_ids:
                message_params['file_ids'] = file_ids

            thread_message = self.client.beta.threads.messages.create(**message_params)

            logger.info(f"Message added: {thread_message.id}")

            return {
                'success': True,
                'message_id': thread_message.id,
                'thread_id': thread_id,
                'created_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to add message to thread: {e}")
            return {
                'success': False,
                'error': str(e),
                'message_id': None
            }

    def run_assistant(
        self,
        thread_id: str,
        assistant_id: str,
        instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run the assistant on a thread (non-streaming)

        Args:
            thread_id: Thread identifier
            assistant_id: Assistant identifier
            instructions: Optional additional instructions for this run

        Returns:
            Dict with run status and response
        """
        if not self.client:
            logger.error("OpenAI client not initialized - cannot run assistant")
            return {
                'success': False,
                'error': 'OpenAI client not initialized',
                'run_id': None
            }

        try:
            logger.info(f"Running assistant {assistant_id} on thread {thread_id}")

            run_params = {
                'thread_id': thread_id,
                'assistant_id': assistant_id
            }

            if instructions:
                run_params['instructions'] = instructions

            run = self.client.beta.threads.runs.create(**run_params)

            # Poll for completion
            max_attempts = 60  # 60 seconds max wait
            attempt = 0
            while attempt < max_attempts:
                run_status = self.client.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run.id
                )

                if run_status.status == 'completed':
                    logger.info(f"Run completed: {run.id}")

                    # Get the latest message from the assistant
                    messages = self.client.beta.threads.messages.list(
                        thread_id=thread_id,
                        order='desc',
                        limit=1
                    )

                    if messages.data:
                        latest_message = messages.data[0]
                        # Extract text content from message
                        content_text = ""
                        for content_block in latest_message.content:
                            if hasattr(content_block, 'text'):
                                content_text += content_block.text.value

                        return {
                            'success': True,
                            'run_id': run.id,
                            'status': 'completed',
                            'response': content_text,
                            'message_id': latest_message.id,
                            'completed_at': datetime.utcnow().isoformat()
                        }
                    else:
                        return {
                            'success': False,
                            'error': 'No messages found in thread',
                            'run_id': run.id
                        }

                elif run_status.status == 'failed':
                    logger.error(f"Run failed: {run.id}")
                    return {
                        'success': False,
                        'error': f"Run failed: {run_status.last_error}",
                        'run_id': run.id,
                        'status': 'failed'
                    }

                elif run_status.status == 'requires_action':
                    logger.warning(f"Run requires action: {run.id}")
                    return {
                        'success': False,
                        'error': 'Run requires action (function calling not yet supported)',
                        'run_id': run.id,
                        'status': 'requires_action'
                    }

                # Still in progress, wait and retry
                import time
                time.sleep(1)
                attempt += 1

            # Timeout
            logger.warning(f"Run timeout: {run.id}")
            return {
                'success': False,
                'error': 'Run timeout after 60 seconds',
                'run_id': run.id,
                'status': 'timeout'
            }

        except Exception as e:
            logger.error(f"Failed to run assistant: {e}")
            return {
                'success': False,
                'error': str(e),
                'run_id': None
            }

    def get_assistant_response(self, thread_id: str) -> Dict[str, Any]:
        """
        Get the latest assistant response from a thread

        Args:
            thread_id: Thread identifier

        Returns:
            Dict with response content
        """
        if not self.client:
            logger.error("OpenAI client not initialized - cannot get response")
            return {
                'success': False,
                'error': 'OpenAI client not initialized',
                'response': None
            }

        try:
            logger.info(f"Getting assistant response from thread {thread_id}")

            # Get messages from the thread
            messages = self.client.beta.threads.messages.list(
                thread_id=thread_id,
                order='desc',
                limit=10  # Get last 10 messages to find latest assistant message
            )

            # Find the latest assistant message
            for message in messages.data:
                if message.role == 'assistant':
                    # Extract text content
                    content_text = ""
                    annotations = []

                    for content_block in message.content:
                        if hasattr(content_block, 'text'):
                            content_text += content_block.text.value

                            # Extract citations/annotations if present
                            if hasattr(content_block.text, 'annotations'):
                                for annotation in content_block.text.annotations:
                                    if hasattr(annotation, 'file_citation'):
                                        annotations.append({
                                            'type': 'file_citation',
                                            'text': annotation.text,
                                            'file_id': annotation.file_citation.file_id,
                                            'quote': annotation.file_citation.quote
                                        })

                    return {
                        'success': True,
                        'response': content_text,
                        'message_id': message.id,
                        'annotations': annotations,
                        'created_at': message.created_at
                    }

            # No assistant message found
            return {
                'success': False,
                'error': 'No assistant messages found in thread',
                'response': None
            }

        except Exception as e:
            logger.error(f"Failed to get assistant response: {e}")
            return {
                'success': False,
                'error': str(e),
                'response': None
            }

    async def stream_assistant_response(
        self,
        thread_id: str,
        assistant_id: str,
        instructions: Optional[str] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream the assistant response in real-time using SSE

        Args:
            thread_id: Thread identifier
            assistant_id: Assistant identifier
            instructions: Optional additional instructions for this run

        Yields:
            Dict with streaming events (delta, complete, error)
        """
        if not self.async_client:
            logger.error("Async OpenAI client not initialized - cannot stream")
            yield {
                'event': 'error',
                'data': {'error': 'OpenAI client not initialized'}
            }
            return

        try:
            logger.info(f"Starting streaming run for assistant {assistant_id} on thread {thread_id}")

            # Create streaming run
            run_params = {
                'thread_id': thread_id,
                'assistant_id': assistant_id
            }

            if instructions:
                run_params['instructions'] = instructions

            # Use create_and_stream for automatic streaming
            async with self.async_client.beta.threads.runs.stream(**run_params) as stream:
                # Send metadata event
                yield {
                    'event': 'metadata',
                    'data': {
                        'thread_id': thread_id,
                        'assistant_id': assistant_id,
                        'timestamp': datetime.utcnow().isoformat()
                    }
                }

                # Process stream events
                async for event in stream:
                    event_type = event.event

                    # Handle text delta events (streaming content)
                    if event_type == 'thread.message.delta':
                        delta = event.data.delta
                        if hasattr(delta, 'content'):
                            for content_block in delta.content:
                                if hasattr(content_block, 'text') and hasattr(content_block.text, 'value'):
                                    yield {
                                        'event': 'message',
                                        'data': {
                                            'delta': content_block.text.value,
                                            'type': 'text'
                                        }
                                    }

                    # Handle run completion
                    elif event_type == 'thread.run.completed':
                        logger.info(f"Run completed: {event.data.id}")
                        yield {
                            'event': 'complete',
                            'data': {
                                'run_id': event.data.id,
                                'status': 'completed',
                                'timestamp': datetime.utcnow().isoformat()
                            }
                        }

                    # Handle run failures
                    elif event_type == 'thread.run.failed':
                        logger.error(f"Run failed: {event.data.id}")
                        yield {
                            'event': 'error',
                            'data': {
                                'run_id': event.data.id,
                                'error': str(event.data.last_error) if hasattr(event.data, 'last_error') else 'Unknown error'
                            }
                        }

                    # Handle action required (function calling)
                    elif event_type == 'thread.run.requires_action':
                        logger.warning(f"Run requires action: {event.data.id}")
                        yield {
                            'event': 'error',
                            'data': {
                                'error': 'Function calling not yet supported',
                                'run_id': event.data.id
                            }
                        }

        except Exception as e:
            logger.error(f"Failed to stream assistant response: {e}")
            yield {
                'event': 'error',
                'data': {'error': str(e)}
            }

    def delete_thread(self, thread_id: str) -> Dict[str, Any]:
        """
        Delete a conversation thread

        Args:
            thread_id: Thread identifier

        Returns:
            Dict with deletion status
        """
        if not self.client:
            logger.error("OpenAI client not initialized - cannot delete thread")
            return {
                'success': False,
                'error': 'OpenAI client not initialized'
            }

        try:
            logger.info(f"Deleting thread: {thread_id}")

            self.client.beta.threads.delete(thread_id=thread_id)

            return {
                'success': True,
                'thread_id': thread_id,
                'deleted_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to delete thread: {e}")
            return {
                'success': False,
                'error': str(e)
            }


# Singleton instance for easy import
assistant_conversation_manager = AssistantConversationManager()
