import os
import logging

# family.py
from openapi_server.impl.utils import (
    get_store, ensure_pk, model_to_json_keyed_dict, now_iso, error_response, not_found
)

# If you use generated models:
# from openapi_server.models.family import Family

log = logging.getLogger(__name__)

DYNAMO_TABLE_NAME = os.getenv("FAMILY_DYNAMO_TABLE_NAME", "quest-dev-family")
PK_NAME = os.getenv("FAMILY_DYNAMO_PK_NAME", "familyId")

def _store():
    return get_store(DYNAMO_TABLE_NAME, PK_NAME)

def handle_list_families():
    # Choose whether to hide soft-deleted rows:
    items = _store().list()
    return items

def handle_get_family(family_id: str):
    item = _store().get(family_id)
    if not item:
        return not_found(PK_NAME, family_id)
    # Optionally enforce soft-delete 404s:
    if item.get("softDelete"):
        return not_found(PK_NAME, family_id)
    return item

def handle_create_family(body):
    data = model_to_json_keyed_dict(body) if hasattr(body, "attribute_map") else dict(body or {})
    ensure_pk(data, PK_NAME)
    now = now_iso()
    data.setdefault("softDelete", False)
    data.setdefault("created", {"at": now})
    data.setdefault("modified", {"at": now})

    try:
        _store().create(data)
    except Exception as e:
        # Keep your existing 409 semantics on duplicate
        from botocore.exceptions import ClientError
        if isinstance(e, ClientError) and e.response.get("Error", {}).get("Code") == "ConditionalCheckFailedException":
            return error_response("Conflict", f"Item already exists: {PK_NAME}={data[PK_NAME]}", 409)
        raise
    return data, 201

def handle_update_family(family_id: str, body):
    data = model_to_json_keyed_dict(body) if hasattr(body, "attribute_map") else dict(body or {})
    # Whitelist fields you allow to be updated:
    allowed = {k: v for k, v in data.items() if k in ("parents", "students", "softDelete")}
    try:
        _store().update_fields(family_id, allowed)
    except Exception as e:
        from botocore.exceptions import ClientError
        if isinstance(e, ClientError) and e.response.get("Error", {}).get("Code") == "ConditionalCheckFailedException":
            return not_found(PK_NAME, family_id)
        raise
    # Return the fresh item (matches your current pattern)
    return _store().get(family_id)

def handle_delete_family(family_id: str):
    try:
        _store().soft_delete(family_id)
    except Exception as e:
        from botocore.exceptions import ClientError
        if isinstance(e, ClientError) and e.response.get("Error", {}).get("Code") == "ConditionalCheckFailedException":
            return not_found(PK_NAME, family_id)
        raise
    return None, 204
