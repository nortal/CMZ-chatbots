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
