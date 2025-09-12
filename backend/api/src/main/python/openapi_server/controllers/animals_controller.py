import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.animal import Animal  # noqa: E501
from openapi_server.models.animal_config import AnimalConfig  # noqa: E501
from openapi_server.models.animal_config_update import AnimalConfigUpdate  # noqa: E501
from openapi_server.models.animal_details import AnimalDetails  # noqa: E501
from openapi_server.models.animal_input import AnimalInput  # noqa: E501
from openapi_server.models.animal_update import AnimalUpdate  # noqa: E501
from openapi_server import util


def animal_config_get(animal_id):  # noqa: E501
    """Get animal configuration

     # noqa: E501

    :param animal_id: 
    :type animal_id: str

    :rtype: Union[AnimalConfig, Tuple[AnimalConfig, int], Tuple[AnimalConfig, int, Dict[str, str]]
    """
    from openapi_server.impl.animals import handle_get_animal_config
    
    try:
        result = handle_get_animal_config(animal_id)
        return result, 200
    except Exception as e:
        from openapi_server.impl.error_handler import create_error_response
        return create_error_response("not_found", f"Animal config for id {animal_id} not found"), 404


def animal_config_patch(animal_id, body):  # noqa: E501
    """Update animal configuration

     # noqa: E501

    :param animal_id: 
    :type animal_id: str
    :param animal_config_update: 
    :type animal_config_update: dict | bytes

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    from openapi_server.impl.animals import handle_update_animal_config
    
    animal_config_update = body
    if connexion.request.is_json:
        animal_config_update = AnimalConfigUpdate.from_dict(connexion.request.get_json())  # noqa: E501
    
    try:
        # Convert AnimalConfigUpdate to AnimalConfig for the handler
        config_data = animal_config_update.to_dict() if hasattr(animal_config_update, 'to_dict') else animal_config_update
        animal_config = AnimalConfig.from_dict(config_data)
        
        result = handle_update_animal_config(animal_id, animal_config)
        return result, 200
    except Exception as e:
        from openapi_server.impl.error_handler import create_error_response
        return create_error_response("validation_error", f"Failed to update animal config: {str(e)}"), 400


def animal_details_get(animal_id):  # noqa: E501
    """Fetch animal details

     # noqa: E501

    :param animal_id: 
    :type animal_id: str

    :rtype: Union[AnimalDetails, Tuple[AnimalDetails, int], Tuple[AnimalDetails, int, Dict[str, str]]
    """
    from openapi_server.impl.animals import handle_get_animal
    
    try:
        # For now, use the existing get_animal handler and convert to AnimalDetails
        # This is a temporary implementation - animal details should include additional info
        animal = handle_get_animal(animal_id)
        
        # Convert Animal to AnimalDetails (they should have compatible fields based on OpenAPI spec)
        animal_details = AnimalDetails.from_dict(animal.to_dict())
        return animal_details, 200
    except Exception as e:
        from openapi_server.impl.error_handler import create_error_response
        return create_error_response("not_found", f"Animal details for id {animal_id} not found"), 404


def animal_id_delete(id_):  # noqa: E501
    """Delete an animal (soft delete)

     # noqa: E501

    :param id: 
    :type id: str

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    from openapi_server.impl.animals import handle_delete_animal
    
    try:
        result, status_code = handle_delete_animal(id_)
        return result, status_code
    except Exception as e:
        from openapi_server.impl.error_handler import create_error_response
        return create_error_response("not_found", f"Animal with id {id_} not found"), 404


def animal_id_get(id_):  # noqa: E501
    """Get a specific animal by ID

     # noqa: E501

    :param id: 
    :type id: str

    :rtype: Union[Animal, Tuple[Animal, int], Tuple[Animal, int, Dict[str, str]]
    """
    from openapi_server.impl.animals import handle_get_animal
    
    try:
        result = handle_get_animal(id_)
        return result, 200
    except Exception as e:
        from openapi_server.impl.error_handler import create_error_response
        return create_error_response("not_found", f"Animal with id {id_} not found"), 404


def animal_id_put(id_, body):  # noqa: E501
    """Update an existing animal

     # noqa: E501

    :param id: 
    :type id: str
    :param animal_update: 
    :type animal_update: dict | bytes

    :rtype: Union[Animal, Tuple[Animal, int], Tuple[Animal, int, Dict[str, str]]
    """
    from openapi_server.impl.animals import handle_update_animal
    
    animal_update = body
    if connexion.request.is_json:
        animal_update = AnimalUpdate.from_dict(connexion.request.get_json())  # noqa: E501
    
    try:
        result = handle_update_animal(id_, animal_update)
        return result, 200
    except Exception as e:
        from openapi_server.impl.error_handler import create_error_response
        return create_error_response("validation_error", str(e)), 400


def animal_list_get():  # noqa: E501
    """List animals

     # noqa: E501


    :rtype: Union[List[Animal], Tuple[List[Animal], int], Tuple[List[Animal], int, Dict[str, str]]
    """
    from openapi_server.impl.animals import handle_list_animals
    
    try:
        result = handle_list_animals()
        return result, 200
    except Exception as e:
        from openapi_server.impl.error_handler import create_error_response
        return create_error_response("server_error", "Failed to retrieve animals list"), 500


def animal_post(body):  # noqa: E501
    """Create a new animal

     # noqa: E501

    :param animal_input: 
    :type animal_input: dict | bytes

    :rtype: Union[Animal, Tuple[Animal, int], Tuple[Animal, int, Dict[str, str]]
    """
    from openapi_server.impl.animals import handle_create_animal
    
    animal_input = body
    if connexion.request.is_json:
        animal_input = AnimalInput.from_dict(connexion.request.get_json())  # noqa: E501
    
    try:
        result = handle_create_animal(animal_input)
        return result, 201
    except Exception as e:
        from openapi_server.impl.error_handler import create_error_response
        return create_error_response("validation_error", str(e)), 400
