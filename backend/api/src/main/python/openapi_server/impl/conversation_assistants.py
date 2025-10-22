"""
OpenAI Assistants API Integration for Animal Conversations
Handles thread-based conversations with document knowledge retrieval
"""

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
