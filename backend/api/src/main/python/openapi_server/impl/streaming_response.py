"""
Server-Sent Events (SSE) streaming implementation for real-time chat responses
"""

import json
import asyncio
from typing import AsyncGenerator, Dict, Any, Optional
from flask import Response, stream_with_context
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class SSEStreamer:
    """Handle Server-Sent Events streaming for chat responses"""

    @staticmethod
    def format_sse(data: str, event: Optional[str] = None, id: Optional[str] = None, retry: Optional[int] = None) -> str:
        """
        Format data for SSE transmission

        Args:
            data: Data to send
            event: Optional event type
            id: Optional event ID
            retry: Optional retry time in milliseconds

        Returns:
            Formatted SSE string
        """
        message = ''
        if id is not None:
            message += f'id: {id}\n'
        if event is not None:
            message += f'event: {event}\n'
        if retry is not None:
            message += f'retry: {retry}\n'

        # Handle multi-line data
        for line in data.split('\n'):
            message += f'data: {line}\n'

        message += '\n'  # Empty line to signal end of event
        return message

    @staticmethod
    async def stream_chat_response(
        chatgpt_stream: AsyncGenerator[str, None],
        session_id: str,
        animal_id: str
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat response with SSE formatting

        Args:
            chatgpt_stream: Async generator from ChatGPT
            session_id: Conversation session ID
            animal_id: Animal ID

        Yields:
            SSE formatted response chunks
        """
        try:
            # Send initial metadata
            metadata = {
                'type': 'start',
                'sessionId': session_id,
                'animalId': animal_id,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
            yield SSEStreamer.format_sse(
                json.dumps(metadata),
                event='metadata'
            )

            # Stream content chunks
            full_response = ''
            chunk_count = 0
            async for chunk in chatgpt_stream:
                chunk_count += 1
                full_response += chunk

                # Send content chunk
                chunk_data = {
                    'type': 'content',
                    'content': chunk,
                    'chunkId': chunk_count
                }
                yield SSEStreamer.format_sse(
                    json.dumps(chunk_data),
                    event='message'
                )

                # Small delay to prevent overwhelming client
                await asyncio.sleep(0.01)

            # Send completion event
            completion_data = {
                'type': 'complete',
                'fullResponse': full_response,
                'chunkCount': chunk_count,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
            yield SSEStreamer.format_sse(
                json.dumps(completion_data),
                event='complete'
            )

        except Exception as e:
            logger.error(f"Error in SSE streaming: {e}")
            # Send error event
            error_data = {
                'type': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
            yield SSEStreamer.format_sse(
                json.dumps(error_data),
                event='error'
            )

    @staticmethod
    def create_sse_response(generator: AsyncGenerator[str, None]) -> Response:
        """
        Create Flask Response for SSE streaming

        Args:
            generator: Async generator producing SSE events

        Returns:
            Flask Response configured for SSE
        """
        def generate():
            """Synchronous wrapper for async generator"""
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                while True:
                    try:
                        yield loop.run_until_complete(generator.__anext__())
                    except StopAsyncIteration:
                        break
            finally:
                loop.close()

        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no',  # Disable Nginx buffering
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*',  # Configure appropriately for production
            }
        )

    @staticmethod
    async def stream_typing_indicator(
        duration_seconds: int = 3
    ) -> AsyncGenerator[str, None]:
        """
        Stream typing indicator events

        Args:
            duration_seconds: How long to show typing indicator

        Yields:
            SSE formatted typing events
        """
        # Send typing start event
        start_event = {
            'type': 'typing',
            'status': 'start',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        yield SSEStreamer.format_sse(
            json.dumps(start_event),
            event='typing'
        )

        # Wait for specified duration
        await asyncio.sleep(duration_seconds)

        # Send typing stop event
        stop_event = {
            'type': 'typing',
            'status': 'stop',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        yield SSEStreamer.format_sse(
            json.dumps(stop_event),
            event='typing'
        )

    @staticmethod
    async def stream_conversation_history(
        history: list[Dict[str, Any]],
        session_id: str
    ) -> AsyncGenerator[str, None]:
        """
        Stream conversation history as SSE events

        Args:
            history: Conversation history items
            session_id: Session ID

        Yields:
            SSE formatted history events
        """
        # Send session info
        session_info = {
            'type': 'session',
            'sessionId': session_id,
            'messageCount': len(history),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        yield SSEStreamer.format_sse(
            json.dumps(session_info),
            event='session'
        )

        # Stream each history item
        for idx, item in enumerate(history):
            history_event = {
                'type': 'history',
                'index': idx,
                'turnId': item.get('turnId'),
                'userMessage': item.get('userMessage'),
                'assistantReply': item.get('assistantReply'),
                'timestamp': item.get('timestamp')
            }
            yield SSEStreamer.format_sse(
                json.dumps(history_event),
                event='history'
            )

            # Small delay between history items
            await asyncio.sleep(0.05)

        # Send end of history event
        end_event = {
            'type': 'history_complete',
            'totalMessages': len(history),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        yield SSEStreamer.format_sse(
            json.dumps(end_event),
            event='history_complete'
        )


class ConversationStreamer:
    """High-level streaming handler for conversations"""

    def __init__(self, chatgpt_integration, conversation_storage):
        """
        Initialize ConversationStreamer

        Args:
            chatgpt_integration: ChatGPT integration instance
            conversation_storage: Conversation storage instance
        """
        self.chatgpt = chatgpt_integration
        self.storage = conversation_storage
        self.sse = SSEStreamer()

    async def stream_conversation_turn(
        self,
        user_id: str,
        animal_id: str,
        user_message: str,
        session_id: Optional[str] = None,
        animal_config: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream a complete conversation turn with SSE

        Args:
            user_id: User ID
            animal_id: Animal ID
            user_message: User's message
            session_id: Optional existing session ID
            animal_config: Animal configuration

        Yields:
            SSE formatted events
        """
        try:
            # Create or get session
            if not session_id:
                session_id = self.storage.create_conversation_session(user_id, animal_id)
                # Send new session event
                new_session_event = {
                    'type': 'new_session',
                    'sessionId': session_id,
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                }
                yield self.sse.format_sse(
                    json.dumps(new_session_event),
                    event='session'
                )

            # Get conversation history
            history = self.storage.get_conversation_history(session_id)

            # Convert history to ChatGPT format
            chat_history = []
            for turn in history:
                chat_history.append({"role": "user", "content": turn.get('userMessage', '')})
                chat_history.append({"role": "assistant", "content": turn.get('assistantReply', '')})

            # Stream typing indicator while preparing
            typing_task = asyncio.create_task(
                self._send_typing_events()
            )

            # Get streaming response from ChatGPT
            chatgpt_stream = self.chatgpt.stream_animal_response(
                animal_id=animal_id,
                user_message=user_message,
                conversation_history=chat_history,
                animal_config=animal_config
            )

            # Cancel typing indicator when response starts
            typing_task.cancel()

            # Stream the response
            full_response = ''
            async for sse_event in self.sse.stream_chat_response(chatgpt_stream, session_id, animal_id):
                yield sse_event

                # Extract full response from completion event
                if 'complete' in sse_event:
                    try:
                        event_data = json.loads(sse_event.split('data: ')[1].split('\n')[0])
                        if event_data.get('type') == 'complete':
                            full_response = event_data.get('fullResponse', '')
                    except:
                        pass

            # Store conversation turn
            if full_response:
                turn_id = self.storage.store_conversation_turn(
                    session_id=session_id,
                    user_message=user_message,
                    assistant_reply=full_response,
                    metadata={
                        'animalId': animal_id,
                        'userId': user_id,
                        'timestamp': datetime.utcnow().isoformat() + 'Z'
                    }
                )

                # Send storage confirmation
                storage_event = {
                    'type': 'stored',
                    'turnId': turn_id,
                    'sessionId': session_id,
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                }
                yield self.sse.format_sse(
                    json.dumps(storage_event),
                    event='storage'
                )

        except Exception as e:
            logger.error(f"Error in conversation streaming: {e}")
            # Send error event
            error_event = {
                'type': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
            yield self.sse.format_sse(
                json.dumps(error_event),
                event='error'
            )

    async def _send_typing_events(self):
        """Send typing indicator events"""
        try:
            async for event in self.sse.stream_typing_indicator(duration_seconds=2):
                yield event
        except asyncio.CancelledError:
            # Normal cancellation when response starts
            pass