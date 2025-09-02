import os
from typing import Any, Dict, List, Optional, Protocol, Tuple, Type
from pynamodb.models import Model
from pynamodb.exceptions import PutError, UpdateError, DoesNotExist

from ..core import now_iso
from .models import FamilyModel

class DynamoStore(Protocol):
    def list(self, hide_soft_deleted: bool = True) -> List[Dict[str, Any]]: ...
    def get(self, pk: Any) -> Optional[Dict[str, Any]]: ...
    def create(self, item: Dict[str, Any]) -> None: ...
    def update_fields(self, pk: Any, fields: Dict[str, Any]) -> None: ...
    def soft_delete(self, pk: Any, soft_field: str = "softDelete") -> None: ...

class PynamoStore:
    def __init__(self, model_cls: Type[Model], pk_name: str):
        self._model = model_cls
        self._pk = pk_name
        if not self._model.exists():
            self._model.create_table(read_capacity_units=5, write_capacity_units=5, wait=True)

    def list(self, hide_soft_deleted: bool = True) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        for m in self._model.scan():
            if hide_soft_deleted and getattr(m, "softDelete", False):
                continue
            out.append(m.to_plain_dict() if hasattr(m, "to_plain_dict") else dict(m.attribute_values))
        return out

    def get(self, pk: Any) -> Optional[Dict[str, Any]]:
        try:
            m = self._model.get(pk)
        except DoesNotExist:
            return None
        return m.to_plain_dict() if hasattr(m, "to_plain_dict") else dict(m.attribute_values)

    def create(self, item: Dict[str, Any]) -> None:
        cond = getattr(self._model, self._pk).does_not_exist()
        try:
            self._model(**item).save(condition=cond)
        except PutError as e:
            # Shim to keep existing handlers' error handling intact
            from botocore.exceptions import ClientError
            raise ClientError({"Error": {"Code": "ConditionalCheckFailedException", "Message": str(e)}}, "PutItem")

    def update_fields(self, pk: Any, fields: Dict[str, Any]) -> None:
        actions = [getattr(self._model, k).set(v) for k, v in fields.items()]
        actions.append(self._model.modified.set({"at": now_iso()}))
        cond = getattr(self._model, self._pk).exists()
        try:
            self._model(pk).update(actions=actions, condition=cond)
        except UpdateError as e:
            from botocore.exceptions import ClientError
            raise ClientError({"Error": {"Code": "ConditionalCheckFailedException", "Message": str(e)}}, "UpdateItem")

    def soft_delete(self, pk: Any, soft_field: str = "softDelete") -> None:
        cond = getattr(self._model, self._pk).exists()
        try:
            self._model(pk).update(
                actions=[getattr(self._model, soft_field).set(True),
                         self._model.modified.set({"at": now_iso()})],
                condition=cond,
            )
        except UpdateError as e:
            from botocore.exceptions import ClientError
            raise ClientError({"Error": {"Code": "ConditionalCheckFailedException", "Message": str(e)}}, "UpdateItem")

# --- Factory mapping: add your other models here as you grow ---
FAMILY_TABLE_NAME = os.getenv("FAMILY_DYNAMO_TABLE_NAME", "quest-dev-family")
_MODEL_MAP: Dict[str, Tuple[type[Model], str]] = {
    FAMILY_TABLE_NAME: (FamilyModel, "familyId"),
}

def get_store(table_name: str, pk_name: str) -> DynamoStore:
    try:
        model_cls, expected_pk = _MODEL_MAP[table_name]
    except KeyError:
        raise RuntimeError(f"No PynamoDB model mapped for table '{table_name}'. "
                           f"Add it to impl/utils/orm/store.py _MODEL_MAP.")
    if pk_name != expected_pk:
        raise RuntimeError(f"PK mismatch for table '{table_name}': expected '{expected_pk}', got '{pk_name}'.")
    return PynamoStore(model_cls, expected_pk)
