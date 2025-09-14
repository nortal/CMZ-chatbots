import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.user import User  # noqa: E501
from openapi_server import util


def me_get():  # noqa: E501
    """Current authenticated user

    PR003946-71: JWT token validation on protected endpoints

     # noqa: E501


    :rtype: Union[User, Tuple[User, int], Tuple[User, int, Dict[str, str]]
    """
    try:
        from openapi_server.impl.auth import get_current_user
        from openapi_server.impl.users import handle_get_user

        # This will raise AuthenticationError if no valid token
        current_user = get_current_user()

        # Get full user data
        user_data = handle_get_user(current_user['user_id'])

        return user_data, 200

    except Exception as e:
        from openapi_server.impl.error_handler import handle_exception_for_controllers
        return handle_exception_for_controllers(e)
