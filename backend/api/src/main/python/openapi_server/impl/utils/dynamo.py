import os
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, Mapping

import boto3

# ---- Dynamo client helpers ----
_AWS_REGION = os.getenv("AWS_REGION", "us-west-2")
_DDB_ENDPOINT = os.getenv("DYNAMODB_ENDPOINT_URL")

_dynamodb = None
def ddb():
    """Memoized DynamoDB resource (respects local endpoint for tests)."""
    global _dynamodb
    if _dynamodb is None:
        kwargs: Dict[str, Any] = {"region_name": _AWS_REGION}
        if _DDB_ENDPOINT:
            kwargs["endpoint_url"] = _DDB_ENDPOINT
        _dynamodb = boto3.resource("dynamodb", **kwargs)
    return _dynamodb


def table(table_name: str):
    return ddb().Table(table_name)


# ---- Serialization helpers ----
def _to_ddb_scalar(value: Any) -> Any:
    from datetime import datetime
    if isinstance(value, float):
        # Avoid float -> Binary in boto3; use Decimal
        return Decimal(str(value))
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat()
    return value

def to_ddb(value: Any) -> Any:
    """Recursively convert Python/model types -> DynamoDB-safe types."""
    if value is None:
        return None
    if hasattr(value, "to_dict"):  # generated models
        value = value.to_dict()  # type: ignore[attr-defined]
    if isinstance(value, Mapping):
        return {k: to_ddb(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_ddb(v) for v in value]
    return _to_ddb_scalar(value)


def _from_ddb_scalar(value: Any) -> Any:
    if isinstance(value, Decimal):
        # Keep ints as ints when possible
        if value % 1 == 0:
            return int(value)
        return float(value)
    return value

def from_ddb(value: Any) -> Any:
    """Recursively convert DynamoDB types -> Python-native types."""
    if value is None:
        return None
    if isinstance(value, Mapping):
        return {k: from_ddb(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [from_ddb(v) for v in value]
    return _from_ddb_scalar(value)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def ensure_pk(item: Dict[str, Any], pk_name: str) -> Dict[str, Any]:
    """Ensure a PK exists; generate UUIDv4 if missing/empty."""
    if pk_name not in item or not item[pk_name]:
        item[pk_name] = str(uuid.uuid4())
    return item


# ---- Models helpers ----
def model_to_json_keyed_dict(obj: Any) -> Any:
    """
    Convert an OpenAPI model instance (or nested containers) into a dict
    using JSON/camelCase keys from attribute_map rather than snake_case attrs.
    Falls back to to_dict() or returns scalars unchanged.
    """
    if obj is None:
        return None

    # Generated OpenAPI model with attribute_map
    if hasattr(obj, "attribute_map"):
        result = {}
        for attr_name, json_key in getattr(obj, "attribute_map").items():  # type: ignore[assignment]
            if hasattr(obj, attr_name):
                result[json_key] = model_to_json_keyed_dict(getattr(obj, attr_name))
        return result

    # Dicts
    if isinstance(obj, Mapping):
        return {k: model_to_json_keyed_dict(v) for k, v in obj.items()}

    # Sequences
    if isinstance(obj, (list, tuple)):
        return [model_to_json_keyed_dict(v) for v in obj]

    # Fallback to model's to_dict() if present
    if hasattr(obj, "to_dict"):
        return obj.to_dict()  # type: ignore[attr-defined]

    return obj


# ---- Error helpers ----
def error_response(title: str, detail: str, status: int):
    return {"title": title, "detail": detail, "status": status}, status

def not_found(pk_name: str, pk_value: Any):
    return error_response("Not Found", f"Item not found: {pk_name}={pk_value}", 404)
