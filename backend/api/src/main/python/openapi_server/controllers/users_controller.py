import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.user import User  # noqa: E501
from openapi_server import util


def me_get():  # noqa: E501
    """Current authenticated user

     # noqa: E501


    :rtype: Union[User, Tuple[User, int], Tuple[User, int, Dict[str, str]]
    """
    try:
        # User functionality not yet implemented
        return {"code": "not_implemented", "message": "User functionality not yet implemented"}, 501
    except Exception as e:
        return {"code": "internal_error", "message": str(e)}, 500
