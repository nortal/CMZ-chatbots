"""
Animal handlers using hexagonal architecture

All handlers delegate to domain services through the Flask adapter.
Maintains API interface compatibility while providing pure business logic separation.
"""
import logging
from typing import Any, Dict, List, Optional, Tuple
import connexion

# OpenAPI models for API compatibility
from openapi_server.models.animal import Animal
from openapi_server.models.animal_config import AnimalConfig

# Import hexagonal architecture components
from .dependency_injection import create_flask_animal_handler

# Import validation utilities for PR003946-70 and PR003946-82
from .utils.validation import validate_no_client_id, validate_animal_status_filter

log = logging.getLogger(__name__)

# Initialize Flask handler (lazy loaded)
_flask_handler = None


def _get_flask_handler():
    """Get or create Flask animal handler"""
    global _flask_handler
    if _flask_handler is None:
        _flask_handler = create_flask_animal_handler()
    return _flask_handler


# ---------------------------------
# /animals (POST) -> create animal
# ---------------------------------
def handle_create_animal(body: Animal) -> Animal:
    """
    Create a new animal using hexagonal architecture
    
    PR003946-70: Reject client-provided IDs
    
    Args:
        body: Animal OpenAPI model
        
    Returns:
        Animal: Created animal OpenAPI model
        
    Raises:
        Exception: On creation errors (converted to HTTP responses by controller)
    """
    try:
        # PR003946-70: Validate no client-provided ID in raw request
        if hasattr(connexion, 'request') and connexion.request.is_json:
            raw_data = connexion.request.get_json()
            if raw_data:
                id_validation_error = validate_no_client_id(raw_data, 'animalId')
                if id_validation_error:
                    from .error_handler import ValidationError
                    # Use ValidationError to preserve error details and code
                    raise ValidationError(
                        id_validation_error["message"],
                        field_errors=[],
                        details=id_validation_error["details"],
                        error_code=id_validation_error["code"]
                    )
        
        # Delegate to Flask handler which uses domain service
        response, status_code = _get_flask_handler().create_animal(body)
        
        if status_code == 201:
            # Return OpenAPI model (response is already Animal model from Flask handler)
            return response
        else:
            # Convert error response to exception (maintains existing error handling)
            error_msg = response.get("detail", "Animal creation failed") if isinstance(response, dict) else str(response)
            raise Exception(error_msg)
            
    except Exception as e:
        log.exception("Error in handle_create_animal")
        raise


# -----------------------------
# /animals/{animalId} (GET) -> fetch animal
# -----------------------------
def handle_get_animal(animal_id: str) -> Animal:
    """
    Get animal by ID using hexagonal architecture
    
    Args:
        animal_id: Animal identifier
        
    Returns:
        Animal: Animal OpenAPI model
        
    Raises:
        Exception: On retrieval errors (converted to HTTP responses by controller)
    """
    try:
        # Delegate to Flask handler which uses domain service
        response, status_code = _get_flask_handler().get_animal(animal_id)
        
        if status_code == 200:
            # Return OpenAPI model
            return response
        elif status_code == 404:
            # Maintain existing not_found pattern
            from .utils.core import not_found
            return not_found("animalId", animal_id)
        else:
            # Convert error to exception
            error_msg = response.get("detail", "Animal retrieval failed") if isinstance(response, dict) else str(response)
            raise Exception(error_msg)
            
    except Exception as e:
        log.exception(f"Error in handle_get_animal for animalId={animal_id}")
        raise


# ---------------------------------
# /animals (GET) -> list animals
# ---------------------------------
def handle_list_animals(status: Optional[str] = None) -> List[Animal]:
    """
    List animals with optional status filter using hexagonal architecture
    
    PR003946-82: Filter parameter validation
    
    Args:
        status: Optional status filter (e.g., "active", "inactive")
        
    Returns:
        List[Animal]: List of Animal OpenAPI models
        
    Raises:
        Exception: On validation errors (converted to HTTP responses by controller)
    """
    try:
        # PR003946-82: Validate status filter parameter
        if status:
            status_validation_error = validate_animal_status_filter(status)
            if status_validation_error:
                from .error_handler import ValidationError
                # Use ValidationError to preserve error details and code
                raise ValidationError(
                    status_validation_error["message"],
                    field_errors=[],
                    details=status_validation_error["details"],
                    error_code=status_validation_error["code"]
                )
        
        # Delegate to Flask handler which uses domain service
        response, status_code = _get_flask_handler().list_animals(status)
        
        if status_code == 200:
            # Return response directly - Flask handler has already converted domain entities to proper format
            if isinstance(response, list):
                return response
            else:
                return []
        else:
            log.error(f"Error listing animals: {response}")
            return []
            
    except Exception as e:
        log.exception("Error in handle_list_animals")
        raise


# ------------------------------------
# /animals/{animalId} (PUT) -> update animal
# ------------------------------------
def handle_update_animal(animal_id: str, body: Animal) -> Animal:
    """
    Update animal using hexagonal architecture
    
    Args:
        animal_id: Animal identifier
        body: Animal OpenAPI model with updates
        
    Returns:
        Animal: Updated animal OpenAPI model
        
    Raises:
        Exception: On update errors
    """
    try:
        # Delegate to Flask handler which uses domain service
        response, status_code = _get_flask_handler().update_animal(animal_id, body)
        
        if status_code == 200:
            # Return OpenAPI model
            return response
        elif status_code == 404:
            # Maintain existing not_found pattern
            from .utils.core import not_found
            return not_found("animalId", animal_id)
        else:
            # Convert error to exception
            error_msg = response.get("detail", "Animal update failed") if isinstance(response, dict) else str(response)
            raise Exception(error_msg)
            
    except Exception as e:
        log.exception(f"Error in handle_update_animal for animalId={animal_id}")
        raise


# -----------------------------
# /animals/{animalId} (DELETE) -> soft delete
# -----------------------------
def handle_delete_animal(animal_id: str) -> Tuple[None, int]:
    """
    Soft delete animal using hexagonal architecture
    
    Args:
        animal_id: Animal identifier
        
    Returns:
        Tuple[None, int]: Empty response with 204 status code
        
    Raises:
        Exception: On deletion errors
    """
    try:
        # Delegate to Flask handler which uses domain service
        response, status_code = _get_flask_handler().delete_animal(animal_id)
        
        if status_code == 204:
            return None, 204
        elif status_code == 404:
            # Maintain existing not_found pattern
            from .utils.core import not_found
            return not_found("animalId", animal_id)
        else:
            # Convert error to exception
            error_msg = response.get("detail", "Animal deletion failed") if isinstance(response, dict) else str(response)
            raise Exception(error_msg)
            
    except Exception as e:
        log.exception(f"Error in handle_delete_animal for animalId={animal_id}")
        raise


# ------------------------------------------------------
# /animals/{animalId}/config (GET) -> get animal configuration
# ------------------------------------------------------
def handle_get_animal_config(animal_id: str) -> AnimalConfig:
    """
    Get animal configuration using hexagonal architecture
    
    Args:
        animal_id: Animal identifier
        
    Returns:
        AnimalConfig: Animal configuration OpenAPI model
        
    Raises:
        Exception: On retrieval errors
    """
    try:
        # Delegate to Flask handler which uses domain service
        response, status_code = _get_flask_handler().get_animal_config(animal_id)
        
        if status_code == 200:
            # Return OpenAPI model
            return response
        elif status_code == 404:
            # Maintain existing not_found pattern
            from .utils.core import not_found
            return not_found("animalId", animal_id)
        else:
            # Convert error to exception
            error_msg = response.get("detail", "Animal config retrieval failed") if isinstance(response, dict) else str(response)
            raise Exception(error_msg)
            
    except Exception as e:
        log.exception(f"Error in handle_get_animal_config for animalId={animal_id}")
        raise


# ----------------------------------------------------------
# /animals/{animalId}/config (PUT) -> update animal configuration
# ----------------------------------------------------------
def handle_update_animal_config(animal_id: str, body: AnimalConfig) -> AnimalConfig:
    """
    Update animal configuration using hexagonal architecture
    
    Args:
        animal_id: Animal identifier
        body: AnimalConfig OpenAPI model with updates
        
    Returns:
        AnimalConfig: Updated animal configuration OpenAPI model
        
    Raises:
        Exception: On update errors
    """
    try:
        # Delegate to Flask handler which uses domain service
        response, status_code = _get_flask_handler().update_animal_config(animal_id, body)
        
        if status_code == 200:
            # Return OpenAPI model
            return response
        elif status_code == 404:
            # Maintain existing not_found pattern
            from .utils.core import not_found
            return not_found("animalId", animal_id)
        else:
            # Convert error to exception
            error_msg = response.get("detail", "Animal config update failed") if isinstance(response, dict) else str(response)
            raise Exception(error_msg)
            
    except Exception as e:
        log.exception(f"Error in handle_update_animal_config for animalId={animal_id}")
        raise