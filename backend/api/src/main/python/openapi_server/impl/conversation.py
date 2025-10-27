"""
Conversation Management System for CMZ Chatbots with integrated safety.

This module provides comprehensive conversation management with real-time
guardrails validation, content moderation, and educational safety features.

Key Features:
- Real-time content moderation using OpenAI + custom guardrails
- Educational conversation flow with safety-first approach
- Context tracking and conversation history management
- Animal-specific personality and knowledge integration
- Audit trails and safety analytics for compliance
- Parent-friendly content with automatic safety warnings
"""

import logging
from typing import Any, Dict, List, Tuple, Union, Optional
from datetime import datetime
import asyncio
import json

from .utils.dynamo import (
    table, to_ddb, from_ddb, now_iso,
    model_to_json_keyed_dict, ensure_pk,
    error_response, not_found
)
from .utils.openai_integration import OpenAIIntegration
from .utils.content_moderator import (
    get_content_moderator, moderate_content, validate_message_safety,
    ModerationRequest, ModerationResult, ValidationResult
)
from .guardrails import get_guardrails_manager
from .utils.safety_dynamo import get_safety_dynamo_client
from .utils.safety_errors import get_safety_error_handler, log_safety_event

# Configure logging
logger = logging.getLogger(__name__)


class ConversationManager:
    """Comprehensive conversation management with integrated safety."""

    def __init__(self):
        """Initialize conversation manager."""
        self.openai_client = OpenAIIntegration()
        self.content_moderator = get_content_moderator()
        self.guardrails_manager = get_guardrails_manager()
        self.safety_client = get_safety_dynamo_client()

    async def process_conversation_turn(
        self,
        user_message: str,
        user_id: str,
        conversation_id: str,
        animal_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[Dict[str, Any], int]:
        """
        Process a conversation turn with integrated safety validation.

        Args:
            user_message: User's input message
            user_id: User ID
            conversation_id: Conversation ID
            animal_id: Animal ID for personality and guardrails
            context: Optional conversation context

        Returns:
            Tuple of (conversation_response, status_code)
        """
        try:
            logger.info(f"Processing conversation turn: user={user_id}, animal={animal_id}")

            # Step 1: Validate message safety
            is_safe, safety_message, safe_alternative = await validate_message_safety(
                user_message, user_id, conversation_id, animal_id
            )

            if not is_safe:
                # Message blocked by safety checks
                response = {
                    "conversationId": conversation_id,
                    "response": safety_message,
                    "safetyWarning": True,
                    "blocked": True,
                    "timestamp": now_iso()
                }

                # Log safety event
                await log_safety_event(
                    event_type="message_blocked",
                    user_id=user_id,
                    details={
                        "conversation_id": conversation_id,
                        "animal_id": animal_id,
                        "original_message_length": len(user_message),
                        "reason": "safety_validation_failed"
                    }
                )

                return response, 200

            # Step 2: Use safe alternative if available
            processed_message = safe_alternative if safe_alternative else user_message

            # Step 3: Get effective guardrails for animal
            guardrails_config, _ = await self.guardrails_manager.get_effective_guardrails(animal_id)

            # Step 4: Build system prompt with guardrails
            system_prompt = await self._build_system_prompt(animal_id, guardrails_config)

            # Step 5: Get conversation context
            conversation_context = await self._get_conversation_context(conversation_id, user_id)

            # Step 6: Generate AI response
            ai_response = await self._generate_ai_response(
                processed_message, system_prompt, conversation_context, animal_id
            )

            # Step 7: Validate AI response safety
            response_validation = await moderate_content(
                ai_response, user_id, conversation_id, animal_id, "strict"
            )

            # Step 8: Handle AI response safety issues
            if response_validation.result in [ValidationResult.BLOCKED, ValidationResult.ESCALATED]:
                # AI response failed safety - use fallback
                ai_response = await self._generate_safe_fallback_response(animal_id)

                # Log AI safety event
                await log_safety_event(
                    event_type="ai_response_blocked",
                    user_id=user_id,
                    details={
                        "conversation_id": conversation_id,
                        "animal_id": animal_id,
                        "risk_score": response_validation.risk_score,
                        "violations": len(response_validation.guardrails_violations or [])
                    }
                )

            # Step 9: Store conversation turn
            turn_data = await self._store_conversation_turn(
                conversation_id, user_id, animal_id, user_message, ai_response,
                safety_message is not None, response_validation
            )

            # Step 10: Build response
            response = {
                "conversationId": conversation_id,
                "response": ai_response,
                "turnId": turn_data.get("turnId"),
                "safetyWarning": bool(safety_message),
                "safetyMessage": safety_message,
                "blocked": False,
                "timestamp": now_iso(),
                "animalId": animal_id
            }

            logger.info(f"Conversation turn completed: {conversation_id}")
            return response, 200

        except Exception as e:
            logger.error(f"Failed to process conversation turn: {e}")

            # Return educational fallback response
            fallback_response = {
                "conversationId": conversation_id,
                "response": "I'm having trouble right now, but I'd love to tell you about animals! What would you like to learn?",
                "error": True,
                "timestamp": now_iso()
            }
            return fallback_response, 200

    async def get_conversation_history(
        self,
        conversation_id: str,
        user_id: str,
        limit: int = 50
    ) -> Tuple[Dict[str, Any], int]:
        """
        Get conversation history with safety filtering.

        Args:
            conversation_id: Conversation ID
            user_id: User ID for authorization
            limit: Maximum turns to return

        Returns:
            Tuple of (conversation_history, status_code)
        """
        try:
            logger.info(f"Getting conversation history: {conversation_id}")

            # Get conversation turns from DynamoDB
            turns = await self.safety_client.get_conversation_history(
                conversation_id, user_id, limit
            )

            # Filter out any blocked turns for cleaner history
            filtered_turns = []
            for turn in turns:
                if not turn.get("blocked", False):
                    # Remove internal safety fields
                    clean_turn = {
                        "turnId": turn.get("turnId"),
                        "userMessage": turn.get("userMessage"),
                        "aiResponse": turn.get("aiResponse"),
                        "timestamp": turn.get("timestamp"),
                        "animalId": turn.get("animalId")
                    }
                    filtered_turns.append(clean_turn)

            response = {
                "conversationId": conversation_id,
                "turns": filtered_turns,
                "totalTurns": len(filtered_turns),
                "hasMore": len(turns) >= limit
            }

            return response, 200

        except Exception as e:
            logger.error(f"Failed to get conversation history: {e}")
            return error_response(e)

    async def delete_conversation_history(
        self,
        conversation_id: str,
        user_id: str
    ) -> Tuple[Dict[str, Any], int]:
        """
        Delete conversation history (for privacy compliance).

        Args:
            conversation_id: Conversation ID
            user_id: User ID for authorization

        Returns:
            Tuple of (deletion_result, status_code)
        """
        try:
            logger.info(f"Deleting conversation history: {conversation_id}")

            # Verify user owns this conversation
            conversation = await self.safety_client.get_conversation(conversation_id)
            if not conversation or conversation.get("userId") != user_id:
                return {"error": "Conversation not found or access denied"}, 404

            # Delete conversation and all turns
            await self.safety_client.delete_conversation_history(conversation_id)

            # Log deletion for audit trail
            await log_safety_event(
                event_type="conversation_deleted",
                user_id=user_id,
                details={
                    "conversation_id": conversation_id,
                    "deleted_at": now_iso()
                }
            )

            response = {
                "conversationId": conversation_id,
                "deleted": True,
                "timestamp": now_iso()
            }

            return response, 200

        except Exception as e:
            logger.error(f"Failed to delete conversation history: {e}")
            return error_response(e)

    async def summarize_conversation(
        self,
        conversation_id: str,
        user_id: str
    ) -> Tuple[Dict[str, Any], int]:
        """
        Generate educational summary of conversation.

        Args:
            conversation_id: Conversation ID
            user_id: User ID for authorization

        Returns:
            Tuple of (conversation_summary, status_code)
        """
        try:
            logger.info(f"Summarizing conversation: {conversation_id}")

            # Get conversation history
            history_response, status = await self.get_conversation_history(
                conversation_id, user_id, 100
            )

            if status != 200:
                return history_response, status

            turns = history_response.get("turns", [])
            if not turns:
                return {"error": "No conversation to summarize"}, 404

            # Generate educational summary
            summary_text = await self._generate_educational_summary(turns)

            # Validate summary safety
            summary_validation = await moderate_content(
                summary_text, user_id, conversation_id, None, "educational"
            )

            if summary_validation.result == ValidationResult.BLOCKED:
                summary_text = "This conversation covered interesting topics about animals and nature!"

            response = {
                "conversationId": conversation_id,
                "summary": summary_text,
                "turnCount": len(turns),
                "timestamp": now_iso()
            }

            return response, 200

        except Exception as e:
            logger.error(f"Failed to summarize conversation: {e}")
            return error_response(e)

    async def _build_system_prompt(
        self,
        animal_id: str,
        guardrails_config: Optional[Dict[str, Any]]
    ) -> str:
        """Build comprehensive system prompt with guardrails integration."""
        try:
            # First try to get Assistant configuration (new system)
            from .assistants import get_assistant_by_animal

            assistant_data, status = get_assistant_by_animal(animal_id)

            if status == 200 and assistant_data:
                # Use Assistant system (User Story 1 integration)
                logger.info(f"Using Assistant prompt for animal {animal_id}")

                # Check if assistant is active
                if assistant_data.get('status') == 'ACTIVE':
                    base_prompt = assistant_data.get('mergedPrompt', '')

                    if base_prompt:
                        # Add standard educational guidelines to assistant prompt
                        base_prompt += """

ALWAYS REMEMBER:
• Keep conversations appropriate for children of all ages
• Focus on educational content about animals and nature
• Encourage curiosity and respect for wildlife
• Redirect inappropriate topics to educational alternatives
• Be encouraging and positive in all interactions
• Use simple language that children can understand"""

                        logger.info(f"Successfully loaded Assistant prompt for animal {animal_id}")
                        return base_prompt
                    else:
                        logger.warning(f"Assistant found but no merged prompt for animal {animal_id}")
                else:
                    logger.info(f"Assistant exists but status is {assistant_data.get('status')} for animal {animal_id}")

            # Fallback to legacy animal-based prompt system
            logger.info(f"Using legacy animal prompt for animal {animal_id}")

            # Get animal information
            animal_table = table("quest-dev-animal")
            animal_response = animal_table.get_item(Key={"animalId": animal_id})

            if "Item" not in animal_response:
                # Fallback prompt
                return """You are a friendly zoo animal ambassador. Always be educational,
                         appropriate for children, and focus on conservation and animal facts."""

            animal = from_ddb(animal_response["Item"])

            # Build base personality prompt
            base_prompt = f"""You are {animal.get('name', 'a zoo animal')} at Cougar Mountain Zoo.

PERSONALITY: {animal.get('personality', 'Friendly and educational')}

KEY FACTS ABOUT ME:
{animal.get('facts', 'I love teaching people about animals!')}

MY MISSION: Help visitors learn about animals, conservation, and nature in a fun, educational way."""

            # Add guardrails if available
            if guardrails_config and guardrails_config.get("rules"):
                guardrails_text = self._format_guardrails_for_prompt(guardrails_config["rules"])
                base_prompt += f"\n\nIMPORTANT SAFETY GUIDELINES:\n{guardrails_text}"

            # Add standard educational guidelines
            base_prompt += """

ALWAYS REMEMBER:
• Keep conversations appropriate for children of all ages
• Focus on educational content about animals and nature
• Encourage curiosity and respect for wildlife
• Redirect inappropriate topics to educational alternatives
• Be encouraging and positive in all interactions
• Use simple language that children can understand"""

            return base_prompt

        except Exception as e:
            logger.error(f"Failed to build system prompt: {e}")
            return "You are a friendly zoo animal. Be educational and appropriate for children."

    def _format_guardrails_for_prompt(self, rules: List[Dict[str, Any]]) -> str:
        """Format guardrails rules for system prompt."""
        sections = {"ALWAYS": [], "NEVER": [], "ENCOURAGE": [], "DISCOURAGE": []}

        for rule in rules:
            if not rule.get("isActive", True):
                continue

            rule_type = rule.get("type", "ALWAYS")
            rule_text = rule.get("rule", "")

            if rule_text and rule_type in sections:
                sections[rule_type].append(f"• {rule_text}")

        prompt_parts = []
        for section, rules_list in sections.items():
            if rules_list:
                prompt_parts.append(f"{section}:")
                prompt_parts.extend(rules_list)
                prompt_parts.append("")

        return "\n".join(prompt_parts)

    async def _get_conversation_context(
        self,
        conversation_id: str,
        user_id: str
    ) -> List[Dict[str, str]]:
        """Get recent conversation context for AI."""
        try:
            # Get last 10 turns for context
            history_response, _ = await self.get_conversation_history(
                conversation_id, user_id, 10
            )

            context = []
            turns = history_response.get("turns", [])

            # Build context from recent turns
            for turn in turns[-5:]:  # Last 5 turns for context
                context.append({"role": "user", "content": turn.get("userMessage", "")})
                context.append({"role": "assistant", "content": turn.get("aiResponse", "")})

            return context

        except Exception as e:
            logger.error(f"Failed to get conversation context: {e}")
            return []

    async def _generate_ai_response(
        self,
        user_message: str,
        system_prompt: str,
        context: List[Dict[str, str]],
        animal_id: str
    ) -> str:
        """Generate AI response using OpenAI."""
        try:
            # Build messages for OpenAI
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(context)
            messages.append({"role": "user", "content": user_message})

            # Generate response
            response = await self.openai_client.generate_chat_response(
                messages=messages,
                temperature=0.7,
                max_tokens=300
            )

            if response and response.success:
                return response.content
            else:
                logger.warning(f"OpenAI response failed: {response.error if response else 'No response'}")
                return await self._generate_safe_fallback_response(animal_id)

        except Exception as e:
            logger.error(f"Failed to generate AI response: {e}")
            return await self._generate_safe_fallback_response(animal_id)

    async def _generate_safe_fallback_response(self, animal_id: str) -> str:
        """Generate safe fallback response when AI fails."""
        fallbacks = [
            "That's a great question! I love talking about animals. What would you like to know?",
            "I'm excited to share amazing animal facts with you! What's your favorite animal?",
            "There's so much to learn about wildlife! Ask me anything about animals and conservation.",
            "Animals are incredible! What aspect of animal life interests you most?",
        ]

        # Try to get animal name for personalization
        try:
            animal_table = table("quest-dev-animal")
            animal_response = animal_table.get_item(Key={"animalId": animal_id})

            if "Item" in animal_response:
                animal = from_ddb(animal_response["Item"])
                animal_name = animal.get("name", "")
                if animal_name:
                    return f"Hi! I'm {animal_name}. {fallbacks[0]}"

        except Exception:
            pass

        return fallbacks[0]

    async def _store_conversation_turn(
        self,
        conversation_id: str,
        user_id: str,
        animal_id: str,
        user_message: str,
        ai_response: str,
        had_safety_warning: bool,
        validation_result: ModerationResult
    ) -> Dict[str, Any]:
        """Store conversation turn in DynamoDB."""
        try:
            turn_data = {
                "turnId": f"turn_{conversation_id}_{int(datetime.now().timestamp())}",
                "conversationId": conversation_id,
                "userId": user_id,
                "animalId": animal_id,
                "userMessage": user_message,
                "aiResponse": ai_response,
                "timestamp": now_iso(),
                "blocked": validation_result.result == ValidationResult.BLOCKED,
                "hadSafetyWarning": had_safety_warning,
                "riskScore": validation_result.risk_score,
                "validationId": validation_result.validation_id
            }

            # Store turn
            await self.safety_client.store_conversation_turn(turn_data)

            return turn_data

        except Exception as e:
            logger.error(f"Failed to store conversation turn: {e}")
            return {"turnId": "error", "timestamp": now_iso()}

    async def _generate_educational_summary(self, turns: List[Dict[str, Any]]) -> str:
        """Generate educational summary of conversation."""
        try:
            # Extract key educational topics
            topics = []
            animals_mentioned = set()

            for turn in turns:
                user_msg = turn.get("userMessage", "").lower()
                ai_msg = turn.get("aiResponse", "").lower()

                # Simple keyword extraction for educational topics
                educational_keywords = ["animal", "habitat", "food", "conservation", "wild", "zoo"]
                for keyword in educational_keywords:
                    if keyword in user_msg or keyword in ai_msg:
                        topics.append(keyword)

                # Extract animal mentions
                if "animal" in user_msg or "animal" in ai_msg:
                    animals_mentioned.add(turn.get("animalId", ""))

            # Build summary
            summary_parts = []

            if len(turns) > 0:
                summary_parts.append(f"This conversation included {len(turns)} exchanges about animals and nature.")

            if animals_mentioned:
                summary_parts.append("We discussed various animals and their fascinating characteristics.")

            if "conservation" in topics:
                summary_parts.append("We talked about the importance of wildlife conservation.")

            if "habitat" in topics:
                summary_parts.append("We explored different animal habitats and ecosystems.")

            if not summary_parts:
                summary_parts.append("This was a great conversation about animals and learning!")

            return " ".join(summary_parts)

        except Exception as e:
            logger.error(f"Failed to generate educational summary: {e}")
            return "This conversation covered interesting topics about animals and nature!"


# Global manager instance
_conversation_manager: Optional[ConversationManager] = None


def get_conversation_manager() -> ConversationManager:
    """Get singleton ConversationManager instance."""
    global _conversation_manager

    if _conversation_manager is None:
        _conversation_manager = ConversationManager()

    return _conversation_manager


# Handler functions for API endpoints
def handle_convo_turn_post(body: Dict[str, Any], *args, **kwargs) -> Tuple[Any, int]:
    """Handle conversation turn with OpenAI Assistants API."""
    try:
        logger.info("🚀 ROUTING TO ASSISTANTS API HANDLER 🚀")
        # Use modern OpenAI Assistants API instead of deprecated Chat Completions
        from .conversation_assistants import handle_convo_turn_post_assistants
        return handle_convo_turn_post_assistants(body, *args, **kwargs)

    except Exception as e:
        logger.error(f"Failed to handle conversation turn: {e}")
        # Return educational fallback response
        fallback_response = {
            "conversationId": kwargs.get("sessionId", "unknown"),
            "response": "I'm having trouble right now, but I'd love to tell you about animals! What would you like to learn?",
            "error": False,  # Don't show as error to user
            "timestamp": now_iso(),
            "animalId": kwargs.get("animalId", "unknown")
        }
        return fallback_response, 200


def handle_convo_history_get(conversation_id: str, user_id: str, *args, **kwargs) -> Tuple[Any, int]:
    """Handle conversation history retrieval with Assistants API threads."""
    try:
        logger.info("🔍 ROUTING TO ASSISTANTS API HISTORY HANDLER 🔍")
        # Use Assistants API for COPPA-compliant conversation history from threads
        from .conversation_assistants import handle_convo_history_get_assistants

        if not conversation_id or not user_id:
            return {"error": "Missing conversation_id or user_id"}, 400

        limit = kwargs.get("limit", 50)
        return handle_convo_history_get_assistants(conversation_id, user_id, limit, *args, **kwargs)

    except Exception as e:
        logger.error(f"Failed to handle conversation history get: {e}")
        return error_response(e)


def handle_convo_history_delete(conversation_id: str, user_id: str, *args, **kwargs) -> Tuple[Any, int]:
    """Handle conversation history deletion."""
    try:
        manager = get_conversation_manager()

        if not conversation_id or not user_id:
            return {"error": "Missing conversation_id or user_id"}, 400

        # Run async method in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(manager.delete_conversation_history(conversation_id, user_id))
            return result
        finally:
            loop.close()

    except Exception as e:
        logger.error(f"Failed to handle conversation history delete: {e}")
        return error_response(e)


def handle_summarize_convo_post(body: Dict[str, Any], *args, **kwargs) -> Tuple[Any, int]:
    """Handle conversation summarization."""
    try:
        manager = get_conversation_manager()

        conversation_id = body.get("conversationId", "")
        user_id = body.get("userId", "")

        if not conversation_id or not user_id:
            return {"error": "Missing conversationId or userId"}, 400

        # Run async method in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(manager.summarize_conversation(conversation_id, user_id))
            return result
        finally:
            loop.close()

    except Exception as e:
        logger.error(f"Failed to handle conversation summarization: {e}")
        return error_response(e)


# Auto-generated handler functions (2025-10-12: Fixed to forward to handlers.py)

def handle_conversations_sessions_get(*args, **kwargs) -> Tuple[Any, int]:
    """
    Forwarding handler for conversations_sessions_get
    Routes to implementation in handlers.py
    """
    from .handlers import handle_conversations_sessions_get as real_handler
    return real_handler(*args, **kwargs)


def handle_conversations_sessions_session_id_get(*args, **kwargs) -> Tuple[Any, int]:
    """
    Forwarding handler for conversations_sessions_session_id_get
    Routes to implementation in handlers.py
    """
    from .handlers import handle_conversations_sessions_session_id_get as real_handler
    return real_handler(*args, **kwargs)


def handle_convo_turn_stream_get(*args, **kwargs) -> Tuple[Any, int]:
    """
    Implementation handler for convo_turn_stream_get

    TODO: Implement business logic for this operation
    """
    from ..models.error import Error
    error_obj = Error(
        code="not_implemented",
        message=f"Operation convo_turn_stream_get not yet implemented",
        details={"operation": "convo_turn_stream_get", "handler": "handle_convo_turn_stream_get"}
    )
    return error_obj.to_dict(), 501


def generate_openai_response(user_message: str, conversation_context: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate OpenAI response for sandbox testing.

    This function provides a simplified interface to the conversation manager
    for use by sandbox testing functionality.

    Args:
        user_message: The user's input message
        conversation_context: Context about the conversation
        user_context: Context about the user

    Returns:
        Dict containing the AI response and metadata
    """
    try:
        manager = get_conversation_manager()

        # Create a simplified request structure for the conversation manager
        request_body = {
            'message': user_message,
            'conversationId': conversation_context.get('conversationId', 'sandbox-test'),
            'animalId': conversation_context.get('animalId', 'default'),
            'userId': user_context.get('userId', 'sandbox-user')
        }

        # Use the conversation manager to process the turn
        result = asyncio.run(manager.process_conversation_turn(
            user_message=user_message,
            conversation_id=conversation_context.get('conversationId', 'sandbox-test'),
            animal_id=conversation_context.get('animalId', 'default'),
            user_id=user_context.get('userId', 'sandbox-user'),
            context=user_context
        ))

        return {
            'response': result.get('response', 'Sorry, I had trouble generating a response.'),
            'success': True,
            'metadata': result.get('metadata', {})
        }

    except Exception as e:
        logger.error(f"Error generating OpenAI response for sandbox: {e}")
        return {
            'response': 'I apologize, but I encountered an error while processing your message.',
            'success': False,
            'error': str(e)
        }

