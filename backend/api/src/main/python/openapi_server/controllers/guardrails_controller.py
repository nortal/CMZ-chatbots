import connexion
from typing import Dict, List
from typing import Tuple
from typing import Union

from openapi_server.models.error import Error  # noqa: E501
from openapi_server.models.guardrail import Guardrail  # noqa: E501
from openapi_server.models.guardrail_input import GuardrailInput  # noqa: E501
from openapi_server.models.guardrail_template import GuardrailTemplate  # noqa: E501
from openapi_server.models.guardrail_update import GuardrailUpdate  # noqa: E501


def apply_guardrail_template(body=None):  # noqa: E501
    """Apply template to animal

     # noqa: E501

    :param body:
    :type body: dict | bytes

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    if connexion.request.is_json:
        body = connexion.request.get_json()

    from openapi_server.impl.guardrails import handle_apply_template
    return handle_apply_template(body)


def create_guardrail(body=None):  # noqa: E501
    """Create new guardrail

     # noqa: E501

    :param body:
    :type body: dict | bytes

    :rtype: Union[Guardrail, Tuple[Guardrail, int], Tuple[Guardrail, int, Dict[str, str]]
    """
    if connexion.request.is_json:
        body = GuardrailInput.from_dict(connexion.request.get_json())  # noqa: E501

    from openapi_server.impl.guardrails import handle_create_guardrail
    return handle_create_guardrail(body)


def delete_guardrail(guardrail_id):  # noqa: E501
    """Delete guardrail (soft delete)

     # noqa: E501

    :param guardrail_id:
    :type guardrail_id: str

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    from openapi_server.impl.guardrails import handle_delete_guardrail
    return handle_delete_guardrail(guardrail_id)


def get_animal_effective_guardrails(animal_id):  # noqa: E501
    """Get effective guardrails for an animal

     # noqa: E501

    :param animal_id:
    :type animal_id: str

    :rtype: Union[List[Guardrail], Tuple[List[Guardrail], int], Tuple[List[Guardrail], int, Dict[str, str]]
    """
    from openapi_server.impl.guardrails import handle_get_animal_effective_guardrails
    return handle_get_animal_effective_guardrails(animal_id)


def get_animal_system_prompt(animal_id):  # noqa: E501
    """Get system prompt with guardrails

     # noqa: E501

    :param animal_id:
    :type animal_id: str

    :rtype: Union[object, Tuple[object, int], Tuple[object, int, Dict[str, str]]
    """
    from openapi_server.impl.guardrails import handle_get_animal_system_prompt
    return handle_get_animal_system_prompt(animal_id)


def get_guardrail(guardrail_id):  # noqa: E501
    """Get specific guardrail

     # noqa: E501

    :param guardrail_id:
    :type guardrail_id: str

    :rtype: Union[Guardrail, Tuple[Guardrail, int], Tuple[Guardrail, int, Dict[str, str]]
    """
    from openapi_server.impl.guardrails import handle_get_guardrail
    return handle_get_guardrail(guardrail_id)


def get_guardrail_templates():  # noqa: E501
    """Get pre-built guardrail templates

     # noqa: E501


    :rtype: Union[List[GuardrailTemplate], Tuple[List[GuardrailTemplate], int], Tuple[List[GuardrailTemplate], int, Dict[str, str]]
    """
    from openapi_server.impl.guardrails import handle_get_templates
    return handle_get_templates()


def list_guardrails(category=None, is_active=None, is_global=None):  # noqa: E501
    """List all guardrails

     # noqa: E501

    :param category: Filter by category
    :type category: str
    :param is_active: Filter by active status
    :type is_active: bool
    :param is_global: Filter by global status
    :type is_global: bool

    :rtype: Union[List[Guardrail], Tuple[List[Guardrail], int], Tuple[List[Guardrail], int, Dict[str, str]]
    """
    from openapi_server.impl.guardrails import handle_list_guardrails
    return handle_list_guardrails(category, is_active, is_global)


def update_guardrail(guardrail_id, body=None):  # noqa: E501
    """Update guardrail

     # noqa: E501

    :param guardrail_id:
    :type guardrail_id: str
    :param body:
    :type body: dict | bytes

    :rtype: Union[Guardrail, Tuple[Guardrail, int], Tuple[Guardrail, int, Dict[str, str]]
    """
    if connexion.request.is_json:
        body = GuardrailUpdate.from_dict(connexion.request.get_json())  # noqa: E501

    from openapi_server.impl.guardrails import handle_update_guardrail
    return handle_update_guardrail(guardrail_id, body)