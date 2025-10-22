"""Flask handlers for animal operations using hexagonal architecture"""
from typing import Tuple, Any, List
import logging
from openapi_server.models.error import Error
from ...domain.animal_service import AnimalService
from ...domain.common.exceptions import (
    NotFoundError, ConflictError, ValidationError,
    BusinessRuleError, InvalidStateError
)
from .serializers import FlaskAnimalSerializer, FlaskAnimalConfigSerializer
from ...assistant_manager import assistant_manager

logger = logging.getLogger(__name__)


class FlaskAnimalHandler:
    """Flask route handler for animal operations using domain service"""
    
    def __init__(self, animal_service: AnimalService, animal_serializer: FlaskAnimalSerializer,
                 config_serializer: FlaskAnimalConfigSerializer):
        self._animal_service = animal_service
        self._animal_serializer = animal_serializer
        self._config_serializer = config_serializer
    
    def create_animal(self, body: Any) -> Tuple[Any, int]:
        """
        Flask handler for animal creation with OpenAI Assistant integration

        Args:
            body: OpenAPI Animal model or dict

        Returns:
            Tuple of (response_body, http_status_code)
        """
        try:
            # Convert OpenAPI model to business dict
            animal_data = self._animal_serializer.from_openapi(body)

            # Execute business logic (creates animal in DynamoDB)
            animal = self._animal_service.create_animal(animal_data)

            # Extract animal details for Assistant creation
            animal_id = animal.animal_id
            name = animal.name or "Unknown Animal"

            # Get personality description
            personality_desc = ""
            if animal.personality and isinstance(animal.personality, dict):
                personality_desc = animal.personality.get('description', '')

            # Get scientific name
            scientific_name = animal.scientific_name if hasattr(animal, 'scientific_name') else None

            # Create OpenAI Assistant for this animal
            logger.info(f"Creating OpenAI Assistant for animal: {animal_id} ({name})")
            assistant_result = assistant_manager.create_assistant_for_animal(
                animal_id=animal_id,
                name=name,
                personality_description=personality_desc or f"Friendly {name} chatbot",
                scientific_name=scientific_name
            )

            if assistant_result['success']:
                # Store Assistant ID and Vector Store ID in DynamoDB
                logger.info(f"Assistant created successfully: {assistant_result['assistant_id']}")

                # Update animal with Assistant IDs
                update_data = {
                    'assistantId': assistant_result['assistant_id'],
                    'vectorStoreId': assistant_result['vector_store_id'],
                    'assistantModel': assistant_result.get('model', 'gpt-4-turbo')
                }

                # Update the animal with Assistant IDs
                updated_animal = self._animal_service.update_animal(animal_id, update_data)

                # Convert updated entity to OpenAPI response
                response = self._animal_serializer.to_openapi(updated_animal)

                logger.info(f"Animal created with Assistant: {animal_id}")
                return response, 201
            else:
                # Assistant creation failed - log warning but don't fail animal creation
                logger.warning(f"Failed to create Assistant for {animal_id}: {assistant_result.get('error')}")
                logger.warning("Animal created without Assistant - can be added later")

                # Return animal without Assistant IDs
                response = self._animal_serializer.to_openapi(animal)
                return response, 201
            
        except ValidationError as e:
            error_obj = Error(
                code="validation_error",
                message=str(e),
                details={"validation_detail": str(e)}
            )
            return error_obj.to_dict(), 400
        except ConflictError as e:
            error_obj = Error(
                code="conflict",
                message=str(e),
                details={"conflict_detail": str(e)}
            )
            return error_obj.to_dict(), 409
        except Exception as e:
            error_obj = Error(
                code="internal_error",
                message=f"Internal server error: {str(e)}",
                details={"error": str(e)}
            )
            return error_obj.to_dict(), 500
    
    def get_animal(self, animal_id: str) -> Tuple[Any, int]:
        """
        Flask handler for animal retrieval
        
        Args:
            animal_id: Animal identifier
            
        Returns:
            Tuple of (response_body, http_status_code)
        """
        try:
            # Execute business logic
            animal = self._animal_service.get_animal(animal_id)
            
            # Convert domain entity to OpenAPI response
            response = self._animal_serializer.to_openapi(animal)

            # Convert to dict if it's an OpenAPI model
            if hasattr(response, 'to_dict'):
                return response.to_dict(), 200

            return response, 200
            
        except NotFoundError as e:
            error_obj = Error(
                code="not_found",
                message=str(e),
                details={"error": str(e)}
            )
            return error_obj.to_dict(), 404
        except Exception as e:
            error_obj = Error(
                code="internal_error",
                message="Internal server error",
                details={"error": str(e)}
            )
            return error_obj.to_dict(), 500
    
    def list_animals(self, status: str = None) -> Tuple[List[Any], int]:
        """
        Flask handler for animal listing
        
        Args:
            status: Optional status filter
            
        Returns:
            Tuple of (response_body, http_status_code)
        """
        try:
            # Execute business logic
            animals = self._animal_service.list_animals(status_filter=status)
            
            # Convert domain entities to API response format
            response_items = []
            for animal in animals:
                # Use domain serializer directly to get properly formatted dict
                from ...domain.common.serializers import serialize_animal
                animal_dict = serialize_animal(animal, include_api_id=True)
                response_items.append(animal_dict)
            
            return response_items, 200
            
        except Exception as e:
            error_obj = Error(
                code="internal_error",
                message="Internal server error",
                details={"error": str(e)}
            )
            return error_obj.to_dict(), 500
    
    def update_animal(self, animal_id: str, body: Any) -> Tuple[Any, int]:
        """
        Flask handler for animal update

        Args:
            animal_id: Animal identifier
            body: OpenAPI Animal model or dict with update data

        Returns:
            Tuple of (response_body, http_status_code)
        """
        # Import serialize_animal at function start (Bug #7 fix)
        from ...domain.common.serializers import serialize_animal

        try:
            # DEBUG: Trace incoming request
            print(f"DEBUG update_animal: Received body type={type(body)}")
            if hasattr(body, 'to_dict'):
                body_dict = body.to_dict()
                print(f"DEBUG update_animal: body.to_dict() keys={list(body_dict.keys())}")
                print(f"DEBUG update_animal: description in body={body_dict.get('description')}")
            else:
                print(f"DEBUG update_animal: body keys={list(body.keys()) if isinstance(body, dict) else 'not a dict'}")
                print(f"DEBUG update_animal: description in body={body.get('description') if isinstance(body, dict) else 'N/A'}")

            # For PUT requests with partial data, fetch existing data first
            # to merge with the update
            existing_animal = self._animal_service.get_animal(animal_id)

            # Convert OpenAPI model to business dict
            update_data = self._animal_serializer.from_openapi(body)
            print(f"DEBUG update_animal: After from_openapi() keys={list(update_data.keys())}")
            print(f"DEBUG update_animal: description after conversion={update_data.get('description')}")

            # Merge existing data with update data (update_data takes precedence)
            # This allows PUT to work like PATCH for partial updates
            if existing_animal:
                # Get existing data as dict
                existing_data = serialize_animal(existing_animal, include_api_id=False)
                # Update only provided fields
                for key, value in update_data.items():
                    if value is not None:
                        existing_data[key] = value
                update_data = existing_data
                print(f"DEBUG update_animal: After merge keys={list(update_data.keys())}")
                print(f"DEBUG update_animal: description after merge={update_data.get('description')}")

            # Execute business logic
            print(f"DEBUG update_animal: About to call service.update_animal with data keys={list(update_data.keys())}")
            animal = self._animal_service.update_animal(animal_id, update_data)

            # Convert domain entity to dict directly to avoid validation issues
            response_dict = serialize_animal(animal, include_api_id=True)

            return response_dict, 200
            
        except NotFoundError as e:
            error_obj = Error(
                code="not_found",
                message=str(e),
                details={"error": str(e)}
            )
            return error_obj.to_dict(), 404
        except ValidationError as e:
            error_obj = Error(
                code="validation_error",
                message=str(e),
                details={"validation_detail": str(e)}
            )
            return error_obj.to_dict(), 400
        except ConflictError as e:
            error_obj = Error(
                code="conflict",
                message=str(e),
                details={"conflict_detail": str(e)}
            )
            return error_obj.to_dict(), 409
        except InvalidStateError as e:
            error_obj = Error(
                code="invalid_state",
                message=str(e),
                details={"state_detail": str(e)}
            )
            return error_obj.to_dict(), 400
        except Exception as e:
            import traceback
            # Log the full error for debugging
            print(f"ERROR in update_animal: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            error_obj = Error(
                code="internal_error",
                message="Internal server error",
                details={"error": str(e), "type": type(e).__name__}
            )
            return error_obj.to_dict(), 500

    def delete_animal(self, animal_id: str) -> Tuple[None, int]:
        """
        Flask handler for animal soft deletion
        
        Args:
            animal_id: Animal identifier
            
        Returns:
            Tuple of (None, http_status_code)
        """
        try:
            # Execute business logic
            self._animal_service.soft_delete_animal(animal_id)
            
            return None, 204
            
        except NotFoundError as e:
            error_obj = Error(
                code="not_found",
                message=str(e),
                details={"error": str(e)}
            )
            return error_obj.to_dict(), 404
        except ValidationError as e:
            error_obj = Error(
                code="validation_error",
                message=str(e),
                details={"validation_detail": str(e)}
            )
            return error_obj.to_dict(), 400
        except BusinessRuleError as e:
            error_obj = Error(
                code="business_rule_violation",
                message=str(e),
                details={"business_rule": str(e)}
            )
            return error_obj.to_dict(), 400
        except Exception as e:
            error_obj = Error(
                code="internal_error",
                message="Internal server error",
                details={"error": str(e)}
            )
            return error_obj.to_dict(), 500
    
    def get_animal_config(self, animal_id: str) -> Tuple[Any, int]:
        """
        Flask handler for animal configuration retrieval
        
        Args:
            animal_id: Animal identifier
            
        Returns:
            Tuple of (response_body, http_status_code)
        """
        try:
            # Execute business logic
            config_data = self._animal_service.get_animal_configuration(animal_id)
            
            # Convert to OpenAPI response
            response = self._config_serializer.to_openapi(config_data)
            
            return response, 200
            
        except NotFoundError as e:
            error_obj = Error(
                code="not_found",
                message=str(e),
                details={"error": str(e)}
            )
            return error_obj.to_dict(), 404
        except Exception as e:
            error_obj = Error(
                code="internal_error",
                message="Internal server error",
                details={"error": str(e)}
            )
            return error_obj.to_dict(), 500
    
    def update_animal_config(self, animal_id: str, body: Any) -> Tuple[Any, int]:
        """
        Flask handler for animal configuration update

        Args:
            animal_id: Animal identifier
            body: OpenAPI AnimalConfig model or dict with config updates

        Returns:
            Tuple of (response_body, http_status_code)
        """
        try:
            # Debug logging
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Received body type: {type(body)}")
            logger.info(f"Received body: {body}")

            # Convert OpenAPI model to business dict
            config_data = self._config_serializer.from_openapi(body)
            logger.info(f"Converted config_data: {config_data}")

            # Execute business logic
            updated_config = self._animal_service.update_animal_configuration(animal_id, config_data)

            # Convert to OpenAPI response
            response = self._config_serializer.to_openapi(updated_config)

            return response, 200

        except NotFoundError as e:
            error_obj = Error(
                code="not_found",
                message=str(e),
                details={"animal_id": animal_id}
            )
            return error_obj.to_dict(), 404
        except ValidationError as e:
            error_obj = Error(
                code="validation_error",
                message=str(e),
                details={"validation_detail": str(e)}
            )
            return error_obj.to_dict(), 400
        except Exception as e:
            error_obj = Error(
                code="internal_error",
                message=f"Internal server error: {str(e)}",
                details={"error": str(e)}
            )
            return error_obj.to_dict(), 500