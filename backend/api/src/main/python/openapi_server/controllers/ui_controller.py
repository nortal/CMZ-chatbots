import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.admin_shell import AdminShell  # noqa: E501
from openapi_server.models.member_shell import MemberShell  # noqa: E501
from openapi_server.models.public_home import PublicHome  # noqa: E501
from openapi_server import util


def admin_get():  # noqa: E501
    """Admin dashboard shell data

     # noqa: E501


    :rtype: Union[AdminShell, Tuple[AdminShell, int], Tuple[AdminShell, int, Dict[str, str]]
    """
    # UI functionality not yet implemented
    return {"code": "not_implemented", "message": "UI functionality not yet implemented"}, 501


def member_get():  # noqa: E501
    """User portal shell data

     # noqa: E501


    :rtype: Union[MemberShell, Tuple[MemberShell, int], Tuple[MemberShell, int, Dict[str, str]]
    """
    # UI functionality not yet implemented
    return {"code": "not_implemented", "message": "UI functionality not yet implemented"}, 501


def root_get():  # noqa: E501
    """Public homepage

     # noqa: E501


    :rtype: Union[PublicHome, Tuple[PublicHome, int], Tuple[PublicHome, int, Dict[str, str]]
    """
    # UI functionality not yet implemented
    return {"code": "not_implemented", "message": "UI functionality not yet implemented"}, 501
