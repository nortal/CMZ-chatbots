"""Lambda handlers for animal operations using hexagonal architecture"""
import json
from typing import Any, Dict, List
from ...domain.animal_service import AnimalService
from ...domain.common.exceptions import (
    NotFoundError, ConflictError, ValidationError, 
    BusinessRuleError, InvalidStateError
)
from .serializers import LambdaAnimalSerializer, LambdaAnimalConfigSerializer


class LambdaAnimalHandler:
    """Lambda event handler for animal operations using domain service"""
    
    def __init__(self, animal_service: AnimalService, animal_serializer: LambdaAnimalSerializer,
                 config_serializer: LambdaAnimalConfigSerializer):
        self._animal_service = animal_service
        self._animal_serializer = animal_serializer
        self._config_serializer = config_serializer
    
    def create_animal(self, event: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        Lambda handler for animal creation
        
        Args:
            event: Lambda event containing animal data
            context: Lambda context
            
        Returns:
            Lambda response with animal data or error
        """
        try:
            # Convert Lambda event to business dict
            animal_data = self._animal_serializer.from_lambda_event(event)
            
            # Execute business logic
            animal = self._animal_service.create_animal(animal_data)
            
            # Convert domain entity to Lambda response
            return self._animal_serializer.to_lambda_response(animal)
            
        except ValidationError as e:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Validation error", "detail": str(e)})
            }
        except ConflictError as e:
            return {
                "statusCode": 409,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Conflict", "detail": str(e)})
            }
        except Exception as e:
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Internal server error", "detail": str(e)})
            }
    
    def get_animal(self, event: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        Lambda handler for animal retrieval
        
        Args:
            event: Lambda event containing animal ID
            context: Lambda context
            
        Returns:
            Lambda response with animal data or error
        """
        try:
            # Extract animal ID from Lambda event
            event_data = self._animal_serializer.from_lambda_event(event)
            animal_id = event_data.get("animalId") or event_data.get("id") or event_data.get("animalid")
            
            if not animal_id:
                return {
                    "statusCode": 400,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({"error": "Missing animal ID"})
                }
            
            # Execute business logic
            animal = self._animal_service.get_animal(animal_id)
            
            # Convert domain entity to Lambda response
            return self._animal_serializer.to_lambda_response(animal)
            
        except NotFoundError as e:
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Not found", "detail": str(e)})
            }
        except Exception as e:
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Internal server error", "detail": str(e)})
            }
    
    def list_animals(self, event: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        Lambda handler for animal listing
        
        Args:
            event: Lambda event with optional status filter
            context: Lambda context
            
        Returns:
            Lambda response with list of animals or error
        """
        try:
            # Extract query parameters
            event_data = self._animal_serializer.from_lambda_event(event)
            status = event_data.get("status")
            
            # Execute business logic
            animals = self._animal_service.list_animals(status_filter=status)
            
            # Convert domain entities to response data
            from ...domain.common.serializers import serialize_animal
            animal_list = []
            for animal in animals:
                animal_data = serialize_animal(animal)
                animal_list.append(animal_data)
            
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps(animal_list)
            }
            
        except Exception as e:
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Internal server error", "detail": str(e)})
            }
    
    def update_animal(self, event: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        Lambda handler for animal update
        
        Args:
            event: Lambda event containing animal ID and update data
            context: Lambda context
            
        Returns:
            Lambda response with updated animal data or error
        """
        try:
            # Convert Lambda event to business dict
            event_data = self._animal_serializer.from_lambda_event(event)
            animal_id = event_data.get("animalId") or event_data.get("id") or event_data.get("animalid")
            
            if not animal_id:
                return {
                    "statusCode": 400,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({"error": "Missing animal ID"})
                }
            
            # Execute business logic
            animal = self._animal_service.update_animal(animal_id, event_data)
            
            # Convert domain entity to Lambda response
            return self._animal_serializer.to_lambda_response(animal)
            
        except NotFoundError as e:
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Not found", "detail": str(e)})
            }
        except ValidationError as e:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Validation error", "detail": str(e)})
            }
        except ConflictError as e:
            return {
                "statusCode": 409,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Conflict", "detail": str(e)})
            }
        except InvalidStateError as e:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Invalid state", "detail": str(e)})
            }
        except Exception as e:
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Internal server error", "detail": str(e)})
            }
    
    def delete_animal(self, event: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        Lambda handler for animal soft deletion
        
        Args:
            event: Lambda event containing animal ID
            context: Lambda context
            
        Returns:
            Lambda response indicating success or error
        """
        try:
            # Extract animal ID from Lambda event
            event_data = self._animal_serializer.from_lambda_event(event)
            animal_id = event_data.get("animalId") or event_data.get("id") or event_data.get("animalid")
            
            if not animal_id:
                return {
                    "statusCode": 400,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({"error": "Missing animal ID"})
                }
            
            # Execute business logic
            self._animal_service.soft_delete_animal(animal_id)
            
            return {
                "statusCode": 204,
                "headers": {"Access-Control-Allow-Origin": "*"},
                "body": ""
            }
            
        except NotFoundError as e:
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Not found", "detail": str(e)})
            }
        except ValidationError as e:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Validation error", "detail": str(e)})
            }
        except BusinessRuleError as e:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Business rule violation", "detail": str(e)})
            }
        except Exception as e:
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Internal server error", "detail": str(e)})
            }
    
    def get_animal_config(self, event: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        Lambda handler for animal configuration retrieval
        
        Args:
            event: Lambda event containing animal ID
            context: Lambda context
            
        Returns:
            Lambda response with animal configuration or error
        """
        try:
            # Extract animal ID from Lambda event
            event_data = self._config_serializer.from_lambda_event(event)
            animal_id = event_data.get("animalId") or event_data.get("id") or event_data.get("animalid")
            
            if not animal_id:
                return {
                    "statusCode": 400,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({"error": "Missing animal ID"})
                }
            
            # Execute business logic
            config_data = self._animal_service.get_animal_configuration(animal_id)
            
            # Convert to Lambda response
            return self._config_serializer.to_lambda_response(config_data)
            
        except NotFoundError as e:
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Not found", "detail": str(e)})
            }
        except Exception as e:
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Internal server error", "detail": str(e)})
            }
    
    def update_animal_config(self, event: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        Lambda handler for animal configuration update
        
        Args:
            event: Lambda event containing animal ID and config updates
            context: Lambda context
            
        Returns:
            Lambda response with updated configuration or error
        """
        try:
            # Convert Lambda event to business dict
            event_data = self._config_serializer.from_lambda_event(event)
            animal_id = event_data.get("animalId") or event_data.get("id") or event_data.get("animalid")
            
            if not animal_id:
                return {
                    "statusCode": 400,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({"error": "Missing animal ID"})
                }
            
            # Execute business logic
            updated_config = self._animal_service.update_animal_configuration(animal_id, event_data)
            
            # Convert to Lambda response
            return self._config_serializer.to_lambda_response(updated_config)
            
        except NotFoundError as e:
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Not found", "detail": str(e)})
            }
        except ValidationError as e:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Validation error", "detail": str(e)})
            }
        except Exception as e:
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Internal server error", "detail": str(e)})
            }