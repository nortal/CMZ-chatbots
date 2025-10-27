"""
OpenAI Assistants API Manager for Animal Chatbots
Handles creation, configuration, and management of GPT Assistants with Vector Stores
"""

import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from openai import OpenAI, AsyncOpenAI

logger = logging.getLogger(__name__)


class AssistantManager:
    """
    Manages OpenAI Assistants for animal chatbot personalities
    Each animal gets a dedicated Assistant with its own Vector Store for knowledge
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
                logger.info("OpenAI Assistant clients initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI clients: {e}")
                self.client = None
                self.async_client = None

        # Default model for assistants
        self.default_model = os.getenv('ASSISTANT_MODEL', 'gpt-4-turbo')

    def create_assistant_for_animal(
        self,
        animal_id: str,
        name: str,
        personality_description: str,
        scientific_name: Optional[str] = None,
        additional_instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new OpenAI Assistant for an animal chatbot

        Args:
            animal_id: Unique animal identifier
            name: Animal's display name (e.g., "Leo the Lion")
            personality_description: Character personality and traits
            scientific_name: Scientific species name
            additional_instructions: Extra instructions for the assistant

        Returns:
            Dict with assistant_id, vector_store_id, and metadata
        """
        if not self.client:
            logger.error("OpenAI client not initialized - cannot create assistant")
            return {
                'success': False,
                'error': 'OpenAI client not initialized',
                'assistant_id': None,
                'vector_store_id': None
            }

        try:
            # Step 1: Create Vector Store for this animal's knowledge base
            logger.info(f"Creating Vector Store for animal: {animal_id}")
            vector_store = self.client.vector_stores.create(
                name=f"{name} Knowledge Base",
                metadata={
                    'animal_id': animal_id,
                    'created_at': datetime.utcnow().isoformat()
                }
            )
            vector_store_id = vector_store.id
            logger.info(f"Vector Store created: {vector_store_id}")

            # Step 2: Build comprehensive instructions
            instructions = self._build_assistant_instructions(
                name=name,
                personality_description=personality_description,
                scientific_name=scientific_name,
                additional_instructions=additional_instructions
            )

            # Step 3: Create Assistant with file_search tool
            logger.info(f"Creating Assistant for animal: {animal_id}")
            assistant = self.client.beta.assistants.create(
                name=name,
                instructions=instructions,
                model=self.default_model,
                tools=[{"type": "file_search"}],
                tool_resources={
                    "file_search": {
                        "vector_store_ids": [vector_store_id]
                    }
                },
                metadata={
                    'animal_id': animal_id,
                    'scientific_name': scientific_name or '',
                    'created_at': datetime.utcnow().isoformat()
                }
            )
            assistant_id = assistant.id
            logger.info(f"Assistant created: {assistant_id}")

            return {
                'success': True,
                'assistant_id': assistant_id,
                'vector_store_id': vector_store_id,
                'model': self.default_model,
                'created_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to create assistant for {animal_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'assistant_id': None,
                'vector_store_id': None
            }

    def update_assistant(
        self,
        assistant_id: str,
        name: Optional[str] = None,
        personality_description: Optional[str] = None,
        scientific_name: Optional[str] = None,
        additional_instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update an existing Assistant's configuration

        Args:
            assistant_id: OpenAI Assistant ID
            name: Updated animal name
            personality_description: Updated personality
            scientific_name: Updated scientific name
            additional_instructions: Updated instructions

        Returns:
            Dict with success status and updated metadata
        """
        if not self.client:
            logger.error("OpenAI client not initialized - cannot update assistant")
            return {'success': False, 'error': 'OpenAI client not initialized'}

        try:
            # Build update parameters
            update_params = {}

            if name:
                update_params['name'] = name

            if personality_description or additional_instructions:
                # Rebuild instructions if personality changed
                instructions = self._build_assistant_instructions(
                    name=name or "Animal",
                    personality_description=personality_description or "",
                    scientific_name=scientific_name,
                    additional_instructions=additional_instructions
                )
                update_params['instructions'] = instructions

            if not update_params:
                return {
                    'success': True,
                    'message': 'No updates needed',
                    'assistant_id': assistant_id
                }

            # Update the assistant
            logger.info(f"Updating Assistant: {assistant_id}")
            assistant = self.client.beta.assistants.update(
                assistant_id=assistant_id,
                **update_params
            )

            return {
                'success': True,
                'assistant_id': assistant.id,
                'updated_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to update assistant {assistant_id}: {e}")
            return {'success': False, 'error': str(e)}

    def delete_assistant(self, assistant_id: str, vector_store_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Delete an Assistant and optionally its Vector Store

        Args:
            assistant_id: OpenAI Assistant ID to delete
            vector_store_id: Optional Vector Store ID to delete

        Returns:
            Dict with success status
        """
        if not self.client:
            logger.error("OpenAI client not initialized - cannot delete assistant")
            return {'success': False, 'error': 'OpenAI client not initialized'}

        try:
            # Delete assistant
            logger.info(f"Deleting Assistant: {assistant_id}")
            self.client.beta.assistants.delete(assistant_id=assistant_id)

            # Delete vector store if provided
            if vector_store_id:
                logger.info(f"Deleting Vector Store: {vector_store_id}")
                self.client.vector_stores.delete(vector_store_id=vector_store_id)

            return {
                'success': True,
                'deleted_assistant_id': assistant_id,
                'deleted_vector_store_id': vector_store_id,
                'deleted_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to delete assistant {assistant_id}: {e}")
            return {'success': False, 'error': str(e)}

    def get_assistant_info(self, assistant_id: str) -> Dict[str, Any]:
        """
        Retrieve information about an Assistant

        Args:
            assistant_id: OpenAI Assistant ID

        Returns:
            Dict with assistant details
        """
        if not self.client:
            logger.error("OpenAI client not initialized - cannot get assistant info")
            return {'success': False, 'error': 'OpenAI client not initialized'}

        try:
            assistant = self.client.beta.assistants.retrieve(assistant_id=assistant_id)

            return {
                'success': True,
                'assistant_id': assistant.id,
                'name': assistant.name,
                'model': assistant.model,
                'instructions': assistant.instructions,
                'tools': [tool.type for tool in assistant.tools],
                'metadata': assistant.metadata,
                'created_at': assistant.created_at
            }

        except Exception as e:
            logger.error(f"Failed to retrieve assistant {assistant_id}: {e}")
            return {'success': False, 'error': str(e)}

    def _build_assistant_instructions(
        self,
        name: str,
        personality_description: str,
        scientific_name: Optional[str] = None,
        additional_instructions: Optional[str] = None
    ) -> str:
        """
        Build comprehensive instructions for the Assistant

        Args:
            name: Animal's name
            personality_description: Personality traits and character
            scientific_name: Scientific species name
            additional_instructions: Extra instructions

        Returns:
            Complete instruction string for the Assistant
        """
        # Import guardrails for educational safety
        from .guardrails import GuardrailsManager

        # Get educational guardrails
        guardrails_text = """
EDUCATIONAL SAFETY GUIDELINES:
- Keep all content appropriate for children and families (ages 5+)
- Focus on education, conservation, and wildlife appreciation
- Avoid scary, violent, or inappropriate topics
- Encourage curiosity and learning about nature
- Be friendly, welcoming, and patient with all questions
"""

        # Build the base instruction
        species_info = f" You are a {scientific_name}." if scientific_name else ""

        instructions = f"""You are {name}, an animal chatbot at Cougar Mountain Zoo.{species_info}

PERSONALITY & CHARACTER:
{personality_description}

YOUR ROLE:
- Engage visitors in educational conversations about your species
- Share interesting facts from your knowledge base
- Answer questions about wildlife, conservation, and zoo life
- Make learning fun and memorable for all ages
- Cite sources from your knowledge base when providing detailed information

{guardrails_text}

INTERACTION STYLE:
- Stay in character as {name}
- Use first-person perspective ("I", "my", "me")
- Be conversational and friendly, not lecture-like
- Adapt complexity to the visitor's questions
- Show enthusiasm for your species and conservation

{additional_instructions or ''}

Remember: You have access to a comprehensive knowledge base through file_search.
When visitors ask detailed questions, use your knowledge base to provide accurate,
well-cited information while maintaining your engaging personality.
"""

        return instructions.strip()

    def upload_document_to_vector_store(
        self,
        vector_store_id: str,
        file_path: str,
        file_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload a document to an Assistant's Vector Store

        Args:
            vector_store_id: Vector Store ID
            file_path: Path to the file to upload (or file-like object)
            file_name: Optional display name for the file

        Returns:
            Dict with upload status and file metadata
        """
        if not self.client:
            logger.error("OpenAI client not initialized - cannot upload document")
            return {
                'success': False,
                'error': 'OpenAI client not initialized',
                'file_id': None
            }

        try:
            # Step 1: Upload file to OpenAI Files API
            logger.info(f"Uploading file to OpenAI: {file_name or file_path}")

            # Open file and upload
            with open(file_path, 'rb') as file_stream:
                file_response = self.client.files.create(
                    file=file_stream,
                    purpose='assistants'
                )

            file_id = file_response.id
            logger.info(f"File uploaded to OpenAI: {file_id}")

            # Step 2: Add file to Vector Store
            logger.info(f"Adding file {file_id} to Vector Store: {vector_store_id}")
            vector_store_file = self.client.vector_stores.files.create(
                vector_store_id=vector_store_id,
                file_id=file_id
            )

            # Step 3: Wait for file to be processed (polling)
            max_attempts = 60  # 60 seconds max wait
            attempt = 0
            while attempt < max_attempts:
                file_status = self.client.vector_stores.files.retrieve(
                    vector_store_id=vector_store_id,
                    file_id=file_id
                )

                if file_status.status == 'completed':
                    logger.info(f"File processing completed: {file_id}")
                    break
                elif file_status.status == 'failed':
                    logger.error(f"File processing failed: {file_id}")
                    return {
                        'success': False,
                        'error': 'File processing failed',
                        'file_id': file_id
                    }

                # Still processing, wait 1 second
                import time
                time.sleep(1)
                attempt += 1

            if attempt >= max_attempts:
                logger.warning(f"File processing timeout: {file_id}")
                # Still return success, it may complete later

            return {
                'success': True,
                'file_id': file_id,
                'vector_store_id': vector_store_id,
                'file_name': file_name or file_path,
                'status': file_status.status if attempt < max_attempts else 'processing',
                'uploaded_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to upload document to vector store: {e}")
            return {
                'success': False,
                'error': str(e),
                'file_id': None
            }

    def list_vector_store_files(self, vector_store_id: str) -> List[Dict[str, Any]]:
        """
        List all files in a Vector Store

        Args:
            vector_store_id: Vector Store ID

        Returns:
            List of file metadata
        """
        if not self.client:
            logger.error("OpenAI client not initialized")
            return []

        try:
            files = self.client.vector_stores.files.list(
                vector_store_id=vector_store_id
            )

            file_list = []
            for file in files.data:
                file_list.append({
                    'file_id': file.id,
                    'status': file.status,
                    'created_at': file.created_at,
                    'vector_store_id': vector_store_id
                })

            return file_list

        except Exception as e:
            logger.error(f"Failed to list vector store files: {e}")
            return []

    def delete_document_from_vector_store(
        self,
        vector_store_id: str,
        file_id: str
    ) -> Dict[str, Any]:
        """
        Delete a document from Vector Store

        Args:
            vector_store_id: Vector Store ID
            file_id: OpenAI File ID

        Returns:
            Dict with deletion status
        """
        if not self.client:
            logger.error("OpenAI client not initialized")
            return {'success': False, 'error': 'OpenAI client not initialized'}

        try:
            # Remove from vector store
            self.client.vector_stores.files.delete(
                vector_store_id=vector_store_id,
                file_id=file_id
            )

            # Delete the file itself
            self.client.files.delete(file_id=file_id)

            return {
                'success': True,
                'file_id': file_id,
                'deleted_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to delete document: {e}")
            return {'success': False, 'error': str(e)}

    def list_assistants_for_zoo(self) -> List[Dict[str, Any]]:
        """
        List all Assistants created for the zoo (for admin dashboard)

        Returns:
            List of assistant summaries
        """
        if not self.client:
            logger.error("OpenAI client not initialized")
            return []

        try:
            assistants = self.client.beta.assistants.list(limit=100)

            zoo_assistants = []
            for assistant in assistants.data:
                # Filter to only our zoo assistants (have animal_id in metadata)
                if assistant.metadata and 'animal_id' in assistant.metadata:
                    zoo_assistants.append({
                        'assistant_id': assistant.id,
                        'name': assistant.name,
                        'animal_id': assistant.metadata.get('animal_id'),
                        'model': assistant.model,
                        'created_at': assistant.created_at
                    })

            return zoo_assistants

        except Exception as e:
            logger.error(f"Failed to list assistants: {e}")
            return []


# Singleton instance for easy import
assistant_manager = AssistantManager()
