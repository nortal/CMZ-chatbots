from datetime import datetime, timezone
import uuid
from typing import Any, Dict, List, Tuple

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def ensure_pk(item: Dict[str, Any], pk_name: str) -> Dict[str, Any]:
    if not item.get(pk_name):
        item[pk_name] = str(uuid.uuid4())
    return item

def model_to_json_keyed_dict(obj: Any) -> Any:
    if obj is None:
        return None
    if hasattr(obj, "attribute_map"):
        return {
            json_key: model_to_json_keyed_dict(getattr(obj, attr, None))
            for attr, json_key in obj.attribute_map.items()
        }
    if isinstance(obj, dict):
        return {k: model_to_json_keyed_dict(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [model_to_json_keyed_dict(v) for v in obj]
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    return obj

def error_response(title: str, detail: str, status: int):
    return {"title": title, "detail": detail, "status": status}, status

def not_found(pk_name: str, pk_value: Any):
    return error_response("Not Found", f"Item not found: {pk_name}={pk_value}", 404)

def create_audit_actor(actor_id: str = "system", email: str = "system@cmz.org", display_name: str = "System") -> Dict[str, str]:
    """Create a reusable audit actor object"""
    return {
        'actorId': actor_id,
        'email': email,
        'displayName': display_name
    }

def create_audit_stamp(actor_id: str = "system", email: str = "system@cmz.org", display_name: str = "System") -> Dict[str, Any]:
    """Create a reusable audit stamp with timestamp and actor"""
    return {
        'at': now_iso(),
        'by': create_audit_actor(actor_id, email, display_name)
    }
