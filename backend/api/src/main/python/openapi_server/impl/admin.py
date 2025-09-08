import os
import uuid
import logging
from typing import Any, Dict, List, Optional, Tuple

from openapi_server.impl.utils import (
    get_store, ensure_pk, model_to_json_keyed_dict, now_iso, error_response, not_found
)

# Output models (responses)
from openapi_server.models.user import User
from openapi_server.models.user_details import UserDetails
from openapi_server.models.paged_users import PagedUsers

from botocore.exceptions import ClientError

# **Input** models (requests)
from openapi_server.models.user_input import UserInput
from openapi_server.models.user_details_input import UserDetailsInput

log = logging.getLogger(__name__)

# ---- env/config
USER_TABLE_NAME = os.getenv("USER_DYNAMO_TABLE_NAME", "quest-dev-user")
USER_PK_NAME = os.getenv("USER_DYNAMO_PK_NAME", "userId")

USER_DETAILS_TABLE_NAME = os.getenv("USER_DETAILS_TABLE_NAME", "quest-dev-user-details")
USER_DETAILS_PK_NAME = os.getenv("USER_DETAILS_PK_NAME", "userDetailsId")
# Attribute name on the Pynamo model used to access the userId GSI (see impl/utils/orm/models/user_details.py)
USER_DETAILS_INDEX_ATTR = os.getenv("USER_DETAILS_INDEX_ATTR", "GSI_userId")

def _user_store():
    return get_store(USER_TABLE_NAME, USER_PK_NAME)

def _details_store():
    return get_store(USER_DETAILS_TABLE_NAME, USER_DETAILS_PK_NAME)

def _audit_by(d: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "userId": d.get("userId"),
        "email": d.get("email"),
        "displayName": d.get("displayName"),
    }

# ---------------------------------
# /users (GET) -> list users (paged)
# ---------------------------------
def handle_list_users(page: Optional[int] = None, page_size: Optional[int] = None) -> PagedUsers:
    rows = _user_store().list(hide_soft_deleted=True)
    users: List[Dict[str, Any]] = []
    for it in rows:
        users.append({
            "userId": it.get("userId"),
            "email": it.get("email"),
            "displayName": it.get("displayName"),
            "role": it.get("role"),
            "userType": it.get("userType", "none"),
            "familyId": it.get("familyId"),
            "softDelete": bool(it.get("softDelete", False)),
            "created": it.get("created"),
            "modified": it.get("modified"),
            "deleted": it.get("deleted"),
        })

    if page and page_size:
        start = (page - 1) * page_size
        users = users[start:start + page_size]

    return PagedUsers.from_dict({"items": users})

# ---------------------------
# /user (POST) -> create user
# ---------------------------
def handle_create_user(body: UserInput) -> User:
    """
    Create a new user from a UserInput payload.
    Respond with a User (full model).
    """
    data = model_to_json_keyed_dict(body) or {}
    ensure_pk(data, USER_PK_NAME)  # allow caller to supply userId, otherwise generate
    data.setdefault("userType", "none")
    data.setdefault("softDelete", False)
    data["created"] = {"at": now_iso(), "by": _audit_by((data.get("created") or {}).get("by", {}))}
    _user_store().create(data)
    return User.from_dict(data)

# -----------------------------
# /user/{userId} (GET) -> fetch
# -----------------------------
def handle_get_user(user_id: str) -> User:
    item = _user_store().get(user_id)
    if not item:
        return not_found(USER_PK_NAME, user_id)

    if item.get("softDelete"):
        return not_found(USER_PK_NAME, user_id)

    return User.from_dict({
        "userId": item.get("userId"),
        "email": item.get("email"),
        "displayName": item.get("displayName"),
        "role": item.get("role"),
        "userType": item.get("userType", "none"),
        "familyId": item.get("familyId"),
        "softDelete": bool(item.get("softDelete", False)),
        "created": item.get("created"),
        "modified": item.get("modified"),
        "deleted": item.get("deleted"),
    })

# ------------------------------------
# /user/{userId} (PUT) -> update user
# ------------------------------------
def handle_update_user(user_id: str, body: User) -> User:
    """
    Updates accept the full User model (not the input model),
    consistent with your controller signatures.
    """
    updates = model_to_json_keyed_dict(body) or {}
    updates[USER_PK_NAME] = user_id
    modified_by = (updates.get("modified") or {}).get("by", {})
    updates["modified"] = {"at": now_iso(), "by": _audit_by(modified_by)}
    _user_store().update_fields(user_id, updates)
    return handle_get_user(user_id)

# -----------------------------
# /user/{userId} (DELETE) soft
# -----------------------------
def handle_delete_user(user_id: str) -> Tuple[None, int]:
    _user_store().soft_delete(user_id, soft_field="softDelete")
    # Cascade soft-delete to details (if any)
    try:
        rows = _details_store().query_gsi(USER_DETAILS_INDEX_ATTR, user_id)
        for d in rows:
            _details_store().soft_delete(getattr(d, USER_DETAILS_PK_NAME), soft_field="softDelete")
    except Exception:
        log.exception("Failed to cascade soft-delete for userId=%s", user_id)
    return None, 204

# ------------------------------------------------------
# /user_details (GET) -> list detailed user information
# ------------------------------------------------------
def handle_list_user_details(page: Optional[int] = None, page_size: Optional[int] = None) -> List[UserDetails]:
    rows = _details_store().list(hide_soft_deleted=True)
    out: List[UserDetails] = []
    for it in rows:
        out.append(UserDetails.from_dict({
            "userDetailsId": it.get("userDetailsId"),
            "userId": it.get("userId"),
            "usage": it.get("usage"),
            "extras": it.get("extras"),
            "softDelete": bool(it.get("softDelete", False)),
            "created": it.get("created"),
            "modified": it.get("modified"),
            "deleted": it.get("deleted"),
        }))
    if page and page_size:
        start = (page - 1) * page_size
        out = out[start:start + page_size]
    return out

# ----------------------------------------------------------
# /user_details (POST) -> create details for a given userId
# ----------------------------------------------------------
def handle_create_user_details(body: UserDetailsInput) -> UserDetails:
    """
    POST /user_details
    Mirrors handle_create_user:
    - normalize to JSON keys (camelCase)
    - enforce required fields
    - set defaults + audit
    - ensure uniqueness on userId via GSI
    - conditional create on PK
    """
    # 1) Normalize OpenAPI model -> camelCase dict
    item = model_to_json_keyed_dict(body) or {}

    # Fallbacks for any lingering snake_case
    if "userId" not in item and "user_id" in item:
        item["userId"] = item.pop("user_id")
    if "userDetailsId" not in item and "user_details_id" in item:
        item["userDetailsId"] = item.pop("user_details_id")

    # Normalize nested usage keys if present
    u = item.get("usage")
    if isinstance(u, dict):
        mapping = {
            "user_id": "userId",
            "total_sessions": "totalSessions",
            "total_turns": "totalTurns",
            "last_active": "lastActive",
        }
        for sk, ck in list(mapping.items()):
            if sk in u and ck not in u:
                u[ck] = u.pop(sk)

    # 2) Validate required field(s)
    user_id = item.get("userId")
    if not user_id:
        raise ClientError(
            {"Error": {"Code": "ValidationException", "Message": "Missing required field 'userId'"}},
            "PutItem",
        )

    # 3) Ensure PK present (generate if absent)
    item.setdefault("userDetailsId", str(uuid.uuid4()))

    # 4) Defaults and audit (mirror user create)
    now = now_iso()
    item.setdefault("softDelete", False)
    item["created"]  = {"at": now, "by": _audit_by((item.get("created")  or {}).get("by", {}))}
    item["modified"] = {"at": now, "by": _audit_by((item.get("modified") or {}).get("by", {}))}
    item["deleted"]  = None

    # 5) Uniqueness guard: one details row per userId (ignore soft-deleted)
    if _details_store().exists_on_gsi(USER_DETAILS_INDEX_ATTR, user_id, hide_soft_deleted=True):
        return {"title": "Conflict",
                "detail": f"userId already has details: {user_id}",
                "status": 409}, 409   # ← return 409, don't raise ClientError
    
    # 6) Create (store.create already does conditional write on PK)
    _details_store().create(item)

    # 7) Return the freshly created resource (same pattern as user)
    return {"title": f"User details created userId={item['userId']}"}, 201

# ----------------------------------------------------------
# /user_details/{userId} (GET) -> fetch details by userId
# ----------------------------------------------------------
def handle_get_user_details(user_id: str) -> UserDetails:
    """
    GET /user_details?userId=...
    Mirror of handle_get_user, but reads from the UserDetails GSI (userId_index).
    - Returns 404 if no non–soft-deleted details exist for this userId
    - Includes userDetailsId in the response (model serializer handles it)
    """
    store = _details_store()

    try:
        # Query the GSI for this userId (your store.query_gsi returns model instances)
        rows = store.query_gsi(USER_DETAILS_INDEX_ATTR, user_id, limit=10)
    except Exception:
        logging.exception("Failed to query user details by GSI for userId=%s", user_id)
        # Surface a generic error (or re-raise if you prefer)
        return {"title": "Server Error", "detail": "Failed to read user details", "status": 500}, 500

    # Filter out soft-deleted items
    candidates = [m for m in rows if not getattr(m, "softDelete", False)]

    if not candidates:
        return {"title": "Not Found", "detail": f"userId={user_id}", "status": 404}, 404

    rec = candidates[0]
    # Serialize to API shape
    if hasattr(rec, "to_details_dict"):
        body = rec.to_details_dict()
    else:
        # fallback: raw attribute values (MapAttribute -> dict)
        body = rec.attribute_values

    return body, 200

# --------------------------------------------------------------
# /user_details/{userId} (PUT) -> update details (by userId GSI)
# --------------------------------------------------------------
def handle_update_user_details(user_id: str, body: UserDetailsInput) -> UserDetails:
    rows = _details_store().query_gsi(USER_DETAILS_INDEX_ATTR, user_id, limit=10)
    if not rows:
        return not_found("userId", user_id)

    details_id = rows[0].to_details_dict()[USER_DETAILS_PK_NAME]
    updates = model_to_json_keyed_dict(body) or {}
    updates[USER_DETAILS_PK_NAME] = details_id
    updates["modified"] = {"at": now_iso(), "by": _audit_by((updates.get("modified") or {}).get("by", {}))}
    _details_store().update_fields(details_id, updates)
    return handle_get_user_details(user_id)

# ----------------------------------------------------------
# /user_details/{userId} (DELETE) -> soft delete details
# ----------------------------------------------------------
def handle_delete_user_details(user_id: str) -> Tuple[None, int]:
    rows = _details_store().query_gsi(USER_DETAILS_INDEX_ATTR, user_id, limit=10)
    if not rows:
        return not_found("userId", user_id)

    for elem in rows:
        details_id = elem.to_details_dict()[USER_DETAILS_PK_NAME]
        _details_store().soft_delete(details_id, soft_field="softDelete")
    return None, 204
