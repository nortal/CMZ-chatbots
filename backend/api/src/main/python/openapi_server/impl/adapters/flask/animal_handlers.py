"""Flask handlers for animal operations using hexagonal architecture"""
from typing import Tuple, Any, List
from ...domain.animal_service import AnimalService
from ...domain.common.exceptions import (
    NotFoundError, ConflictError, ValidationError, 
    BusinessRuleError, InvalidStateError
)
from .serializers import FlaskAnimalSerializer, FlaskAnimalConfigSerializer


class FlaskAnimalHandler:
    """Flask route handler for animal operations using domain service"""
    
    def __init__(self, animal_service: AnimalService, animal_serializer: FlaskAnimalSerializer,
                 config_serializer: FlaskAnimalConfigSerializer):
        self._animal_service = animal_service
        self._animal_serializer = animal_serializer
        self._config_serializer = config_serializer
    
    def create_animal(self, body: Any) -> Tuple[Any, int]:
        """
        Flask handler for animal creation
        
        Args:
            body: OpenAPI Animal model or dict
            
        Returns:
            Tuple of (response_body, http_status_code)
        """
        try:
            # Convert OpenAPI model to business dict
            animal_data = self._animal_serializer.from_openapi(body)
            
            # Execute business logic
            animal = self._animal_service.create_animal(animal_data)
            
            # Convert domain entity to OpenAPI response
            response = self._animal_serializer.to_openapi(animal)
            
            return response, 201
            
        except ValidationError as e:
            return {"error": "Validation error", "detail": str(e)}, 400
        except ConflictError as e:
            return {"error": "Conflict", "detail": str(e)}, 409
        except Exception as e:
            return {"error": "Internal server error", "detail": str(e)}, 500
    
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
            
            return response, 200
            
        except NotFoundError as e:
            return {"error": "Not found", "detail": str(e)}, 404
        except Exception as e:
            return {"error": "Internal server error", "detail": str(e)}, 500
    
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

            # Convert domain entities to OpenAPI response - Use proper serializer like other methods
            response_items = []
            for animal in animals:
                # Use the same serializer pattern as get_animal() for consistency
                openapi_animal = self._animal_serializer.to_openapi(animal)
                response_items.append(openapi_animal)

            return response_items, 200

        except Exception as e:
            return {"error": "Internal server error", "detail": str(e)}, 500
    
    def update_animal(self, animal_id: str, body: Any) -> Tuple[Any, int]:
        """
        Flask handler for animal update
        
        Args:
            animal_id: Animal identifier
            body: OpenAPI Animal model or dict with update data
            
        Returns:
            Tuple of (response_body, http_status_code)
        """
        try:
            # Convert OpenAPI model to business dict
            update_data = self._animal_serializer.from_openapi(body)
            
            # Execute business logic
            animal = self._animal_service.update_animal(animal_id, update_data)
            
            # Convert domain entity to OpenAPI response
            response = self._animal_serializer.to_openapi(animal)
            
            return response, 200
            
        except NotFoundError as e:
            return {"error": "Not found", "detail": str(e)}, 404
        except ValidationError as e:
            return {"error": "Validation error", "detail": str(e)}, 400
        except ConflictError as e:
            return {"error": "Conflict", "detail": str(e)}, 409
        except InvalidStateError as e:
            return {"error": "Invalid state", "detail": str(e)}, 400
        except Exception as e:
            return {"error": "Internal server error", "detail": str(e)}, 500
    
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
            return {"error": "Not found", "detail": str(e)}, 404
        except ValidationError as e:
            return {"error": "Validation error", "detail": str(e)}, 400
        except BusinessRuleError as e:
            return {"error": "Business rule violation", "detail": str(e)}, 400
        except Exception as e:
            return {"error": "Internal server error", "detail": str(e)}, 500
    
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
            return {"error": "Not found", "detail": str(e)}, 404
        except Exception as e:
            return {"error": "Internal server error", "detail": str(e)}, 500
    
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
            # Convert OpenAPI model to business dict
            config_data = self._config_serializer.from_openapi(body)
            
            # Execute business logic
            updated_config = self._animal_service.update_animal_configuration(animal_id, config_data)
            
            # Convert to OpenAPI response
            response = self._config_serializer.to_openapi(updated_config)
            
            return response, 200
            
        except NotFoundError as e:
            return {"error": "Not found", "detail": str(e)}, 404
        except ValidationError as e:
            return {"error": "Validation error", "detail": str(e)}, 400
        except Exception as e:
            return {"error": "Internal server error", "detail": str(e)}, 500