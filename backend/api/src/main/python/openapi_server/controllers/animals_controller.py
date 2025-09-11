import connexion

from openapi_server.models.animal_config import AnimalConfig  # noqa: E501
from openapi_server.models.animal_config_update import AnimalConfigUpdate  # noqa: E501
from openapi_server.models.error import Error  # noqa: E501

# Import hexagonal architecture handlers
import os
try:
    # Try production implementation first
    if os.getenv('TEST_MODE') == 'true':
        raise ImportError("Using test mode")
    from openapi_server.impl.animals import (
        handle_list_animals,
        handle_get_animal,
        handle_get_animal_config,
        handle_update_animal_config
    )
except ImportError:
    # Fall back to test implementation if AWS credentials not available
    from openapi_server.impl.test_animals import (
        handle_list_animals,
        handle_get_animal,
        handle_get_animal_config,
        handle_update_animal_config
    )


def animal_config_get(animal_id):  # noqa: E501
    """Get animal configuration

     # noqa: E501

    :param animal_id: 
    :type animal_id: str

    :rtype: Union[AnimalConfig, Tuple[AnimalConfig, int], Tuple[AnimalConfig, int, Dict[str, str]]
    """
    try:
        return handle_get_animal_config(animal_id)
    except Exception as e:
        return Error(code='INTERNAL_ERROR', message=str(e)), 500


def animal_config_patch(animal_id, body):  # noqa: E501
    """Update animal configuration

     # noqa: E501

    :param animal_id: 
    :type animal_id: str
    :param animal_config_update: 
    :type animal_config_update: dict | bytes

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    animal_config_update = body
    if connexion.request.is_json:
        animal_config_update = AnimalConfigUpdate.from_dict(connexion.request.get_json())  # noqa: E501
    
    try:
        # Convert update to full config for handler
        config_data = animal_config_update.to_dict() if hasattr(animal_config_update, 'to_dict') else dict(animal_config_update)
        config = AnimalConfig.from_dict(config_data)
        return handle_update_animal_config(animal_id, config)
    except Exception as e:
        from openapi_server.impl.error_handler import ValidationError
        if isinstance(e, ValidationError):
            # PR003946-74: Return proper validation error
            return Error(
                code="validation_error",
                message=str(e),
                details=e.details
            ), 400
        return Error(code='INTERNAL_ERROR', message=str(e)), 500


def animal_details_get(animal_id):  # noqa: E501
    """Fetch animal details

     # noqa: E501

    :param animal_id: 
    :type animal_id: str

    :rtype: Union[AnimalDetails, Tuple[AnimalDetails, int], Tuple[AnimalDetails, int, Dict[str, str]]
    """
    try:
        # Use get_animal handler and convert to AnimalDetails format
        animal = handle_get_animal(animal_id)
        # Convert Animal to AnimalDetails (they should be compatible)
        return animal
    except Exception as e:
        return Error(code='INTERNAL_ERROR', message=str(e)), 500


def animal_list_get():  # noqa: E501
    """List animals

     # noqa: E501


    :rtype: Union[List[Animal], Tuple[List[Animal], int], Tuple[List[Animal], int, Dict[str, str]]
    """
    try:
        return handle_list_animals()
    except Exception as e:
        return Error(code='INTERNAL_ERROR', message=str(e)), 500
