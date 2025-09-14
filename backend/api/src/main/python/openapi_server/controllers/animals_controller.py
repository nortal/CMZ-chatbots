import connexion
import os
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.animal import Animal  # noqa: E501
from openapi_server.models.animal_config import AnimalConfig  # noqa: E501
from openapi_server.models.animal_config_update import AnimalConfigUpdate  # noqa: E501
from openapi_server.models.animal_details import AnimalDetails  # noqa: E501
from openapi_server.models.animal_input import AnimalInput  # noqa: E501
from openapi_server.models.animal_update import AnimalUpdate  # noqa: E501
from openapi_server.models.error import Error  # noqa: E501
from openapi_server import util


def animal_config_get(animal_id):  # noqa: E501
    """Get animal configuration

     # noqa: E501

    :param animal_id: 
    :type animal_id: str

    :rtype: Union[AnimalConfig, Tuple[AnimalConfig, int], Tuple[AnimalConfig, int, Dict[str, str]]
    """
    return 'do some magic!'


def animal_config_patch(animal_id, body):  # noqa: E501
    """Update animal configuration

     # noqa: E501

    :param animal_id: 
    :type animal_id: str
    :param animal_config_update: 
    :type animal_config_update: dict | bytes

    :rtype: Union[AnimalConfig, Tuple[AnimalConfig, int], Tuple[AnimalConfig, int, Dict[str, str]]
    """
    animal_config_update = body
    if connexion.request.is_json:
        animal_config_update = AnimalConfigUpdate.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def animal_details_get(animal_id):  # noqa: E501
    """Fetch animal details

     # noqa: E501

    :param animal_id: 
    :type animal_id: str

    :rtype: Union[AnimalDetails, Tuple[AnimalDetails, int], Tuple[AnimalDetails, int, Dict[str, str]]
    """
    return 'do some magic!'


def animal_id_delete(id):  # noqa: E501
    """Delete an animal (soft delete)

     # noqa: E501

    :param id:
    :type id: str

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    # PR003946-66: Soft Delete Consistency - Implement soft delete for animals
    from openapi_server.impl.utils.orm.store import get_store
    from datetime import datetime, timezone

    try:
        # Get the store for animals
        table_name = os.getenv('ANIMAL_DYNAMO_TABLE_NAME', 'quest-dev-animal')
        pk_name = os.getenv('ANIMAL_DYNAMO_PK_NAME', 'animalId')
        store = get_store(table_name, pk_name)

        # Check if animal exists
        animal = store.get(id)
        if not animal:
            return {
                'code': 'not_found',
                'message': f'Animal with ID {id} not found'
            }, 404

        # Check if already soft deleted
        if animal.get('softDelete', False):
            return {
                'code': 'already_deleted',
                'message': f'Animal with ID {id} is already deleted'
            }, 410

        # Perform soft delete by setting softDelete flag and deleted audit timestamp
        from openapi_server.impl.utils.core import create_audit_stamp

        # Update the animal with soft delete markers
        update_data = {
            'softDelete': True,
            'deleted': create_audit_stamp(),
            'modified': create_audit_stamp()
        }

        # Apply the soft delete update
        store.update(id, update_data)

        # Return success with no content (204)
        return None, 204

    except Exception as e:
        from openapi_server.impl.error_handler import handle_exception_for_controllers
        return handle_exception_for_controllers(e)


def animal_id_get(id):  # noqa: E501
    """Get a specific animal by ID

     # noqa: E501

    :param id: 
    :type id: str

    :rtype: Union[Animal, Tuple[Animal, int], Tuple[Animal, int, Dict[str, str]]
    """
    return 'do some magic!'


def animal_id_put(id, body):  # noqa: E501
    """Update an existing animal

     # noqa: E501

    :param id: 
    :type id: str
    :param animal_update: 
    :type animal_update: dict | bytes

    :rtype: Union[Animal, Tuple[Animal, int], Tuple[Animal, int, Dict[str, str]]
    """
    animal_update = body
    if connexion.request.is_json:
        animal_update = AnimalUpdate.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def animal_list_get(status=None):  # noqa: E501
    """List animals

    PR003946-66: Soft delete flag consistency across all entities
    PR003946-71: JWT Token Validation

     # noqa: E501

    :param status: Filter animals by status
    :type status: str

    :rtype: Union[List[Animal], Tuple[List[Animal], int], Tuple[List[Animal], int, Dict[str, str]]
    """
    try:
        from openapi_server.impl.auth import get_current_user, extract_token_from_request
        from openapi_server.impl.animals import handle_list_animals

        # PR003946-71: Validate JWT token if present (optional for this endpoint)
        token = extract_token_from_request()
        if token:
            try:
                user = get_current_user()  # Validate token if provided
            except Exception as auth_error:
                # If token is provided but invalid, return auth error
                from openapi_server.impl.error_handler import handle_exception_for_controllers
                return handle_exception_for_controllers(auth_error)

        # PR003946-66: Get animals with soft delete filtering
        animals = handle_list_animals(status=status)

        return animals, 200

    except Exception as e:
        from openapi_server.impl.error_handler import handle_exception_for_controllers
        return handle_exception_for_controllers(e)


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

    # PR003946-69: Server-generated IDs with client ID rejection
    result = handle_create_animal(animal_input)
    return result, 201
