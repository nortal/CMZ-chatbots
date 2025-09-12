import os
from typing import Any, Dict, List, Optional, Protocol, Tuple, Type
from pynamodb.models import Model
from pynamodb.exceptions import PutError, UpdateError, DoesNotExist
from botocore.exceptions import ClientError

from ..core import now_iso
from .models import FamilyModel, UserModel, UserDetailsModel, AnimalModel
from pynamodb.exceptions import PutError
# PR003946-69: Server-Generated IDs
from ..id_generator import (
    add_audit_timestamps, ensure_user_id, ensure_animal_id, 
    ensure_family_id
)
# PR003946-95: File-based persistence for offline testing
from .file_store import FileStore

class DynamoStore(Protocol):
    def list(self, hide_soft_deleted: bool = True) -> List[Dict[str, Any]]: ...
    def get(self, pk: Any) -> Optional[Dict[str, Any]]: ...
    def create(self, item: Dict[str, Any]) -> None: ...
    def update_fields(self, pk: Any, fields: Dict[str, Any]) -> None: ...
    def soft_delete(self, pk: Any, soft_field: str = "softDelete") -> None: ...

class PynamoStore:
    def __init__(self, model_cls: Type[Model], pk_name: str, id_generator_func=None):
        self._model = model_cls
        self._pk = pk_name
        self._id_generator = id_generator_func
        if not self._model.exists():
            self._model.create_table(read_capacity_units=5, write_capacity_units=5, wait=True)

    def list(self, hide_soft_deleted: bool = True) -> List[Dict[str, Any]]:
        """
        List all entities, optionally filtering soft-deleted ones.
        
        PR003946-66: Soft-delete flag consistency across all entities
        """
        out: List[Dict[str, Any]] = []
        for m in self._model.scan():
            # PR003946-66: Filter soft-deleted records by default
            if hide_soft_deleted and getattr(m, "softDelete", False):
                continue
            # Use model-specific conversion method if available, fallback to generic methods
            if hasattr(m, "to_animal_dict"):
                out.append(m.to_animal_dict())
            elif hasattr(m, "to_user_dict"):
                out.append(m.to_user_dict())
            elif hasattr(m, "to_family_dict"):
                out.append(m.to_family_dict())
            elif hasattr(m, "to_plain_dict"):
                out.append(m.to_plain_dict())
            else:
                out.append(dict(m.attribute_values))
        return out

    def get(self, pk: Any) -> Optional[Dict[str, Any]]:
        try:
            m = self._model.get(pk)
        except DoesNotExist:
            return None
        # Use model-specific conversion method if available, fallback to generic methods
        if hasattr(m, "to_animal_dict"):
            return m.to_animal_dict()
        elif hasattr(m, "to_user_dict"):
            return m.to_user_dict()
        elif hasattr(m, "to_family_dict"):
            return m.to_family_dict()
        elif hasattr(m, "to_plain_dict"):
            return m.to_plain_dict()
        else:
            return dict(m.attribute_values)

    def create(self, item: dict) -> None:
        pk_name = self._pk
        pk_val = item.get(pk_name)

        # PR003946-69: Auto-generate ID if not provided
        if pk_val in (None, ""):
            if self._id_generator:
                item = self._id_generator(item)
                pk_val = item.get(pk_name)
            else:
                raise ClientError(
                    {"Error": {"Code": "ValidationException",
                               "Message": f"Missing required primary key '{pk_name}' and no ID generator configured"}},
                    "PutItem",
                )

        # Add audit timestamps
        item = add_audit_timestamps(item)

        # 2) Preflight: does the item already exist?
        try:
            # strong read to reduce false negatives
            self._model.get(pk_val, consistent_read=True)
        except self._model.DoesNotExist:  # OK, proceed to create
            pass
        else:
            # Found -> treat as duplicate
            raise ClientError(
                {"Error": {"Code": "ConditionalCheckFailedException",
                           "Message": f"Item already exists: {pk_name}={pk_val}"}},
                "PutItem",
            )

        # 3) Create with a conditional write to avoid race conditions
        cond = getattr(self._model, pk_name).does_not_exist()
        try:
            self._model(**item).save(condition=cond)
        except (TypeError, ValueError) as e:
            # Bad payload/types -> 400
            raise ClientError(
                {"Error": {"Code": "ValidationException", "Message": str(e)}},
                "PutItem",
            )
        except PutError as e:
            # Another writer slipped in between (or other conditional failure) -> 409
            raise ClientError(
                {"Error": {"Code": "ConditionalCheckFailedException", "Message": str(e)}},
                "PutItem",
            )

    def update_fields(self, pk: str, updates: dict, *, require_exists: bool = True):
        actions = []
        for key, value in updates.items():
            if key == self._pk:    # don't build actions for the hash key
                continue
            if value is None:
                continue
            try:
                attr = getattr(self._model, key)
            except AttributeError:
                raise ClientError(
                    {"Error": {"Code": "ValidationException", "Message": f"Unknown attribute '{key}'"}},
                    "UpdateItem",
                )
            actions.append(attr.set(value))

        # require the item to exist before updating
        cond = None
        if require_exists:
            cond = getattr(self._model, self._pk).exists()

        try:
            self._model(pk).update(actions=actions, condition=cond)
        except UpdateError as e:
            raise ClientError(
                {"Error": {"Code": "ConditionalCheckFailedException", "Message": str(e)}},
                "UpdateItem",
            )

    def soft_delete(self, pk: Any, soft_field: str = "softDelete") -> None:
        """
        Soft delete an entity by setting the soft delete flag.
        
        PR003946-66: Consistent soft-delete implementation
        """
        cond = getattr(self._model, self._pk).exists()
        try:
            self._model(pk).update(
                actions=[getattr(self._model, soft_field).set(True),
                         self._model.modified.set({"at": now_iso()})],
                condition=cond,
            )
        except UpdateError as e:
            raise ClientError({"Error": {"Code": "ConditionalCheckFailedException", "Message": str(e)}}, "UpdateItem")

    def recover_soft_deleted(self, pk: Any, soft_field: str = "softDelete") -> None:
        """
        Recover a soft-deleted entity by unsetting the soft delete flag.
        
        PR003946-68: Soft-delete recovery functionality
        """
        cond = getattr(self._model, self._pk).exists()
        try:
            self._model(pk).update(
                actions=[getattr(self._model, soft_field).set(False),
                         self._model.modified.set({"at": now_iso()})],
                condition=cond,
            )
        except UpdateError as e:
            raise ClientError({"Error": {"Code": "ConditionalCheckFailedException", "Message": str(e)}}, "UpdateItem")
        
    def exists_on_gsi(self, index_attr_name: str, value: str, *, hide_soft_deleted: bool = True) -> bool:
        """
        Returns True if there's at least one item on the given GSI with the value.
        If hide_soft_deleted is True, ignores items with softDelete == True.
        """
        rows = self.query_gsi(index_attr_name, value, limit=2)  # reuse your fixed query_gsi
        for m in rows:
            sd = getattr(m, "softDelete", False)
            if hide_soft_deleted and sd:
                continue
            return True
        return False

    def query_gsi(self, index_attr_name: str, value: str, *, limit: int = 100):
        index = getattr(self._model, index_attr_name, None)
        if index is None or not hasattr(index, "query"):
            raise ValueError(f"{index_attr_name} is not a GlobalSecondaryIndex on {self._model.__name__}")
        return list(index.query(value, limit=limit))

    

# --- Factory mapping: add your other models here as you grow ---
FAMILY_TABLE_NAME = os.getenv("FAMILY_DYNAMO_TABLE_NAME", "quest-dev-family")
USER_TABLE_NAME = os.getenv("USER_DYNAMO_TABLE_NAME", "quest-dev-user")
USER_DETAILS_TABLE_NAME = os.getenv("USER_DETAILS_TABLE_NAME", "quest-dev-user-details")
ANIMAL_TABLE_NAME = os.getenv("ANIMAL_DYNAMO_TABLE_NAME", "quest-dev-animal")

_MODEL_MAP: Dict[str, Tuple[type[Model], str]] = {
    FAMILY_TABLE_NAME:       (FamilyModel, "familyId"),
    USER_TABLE_NAME:         (UserModel, "userId"),
    USER_DETAILS_TABLE_NAME: (UserDetailsModel, "userDetailsId"),
    ANIMAL_TABLE_NAME:       (AnimalModel, "animalId"),
}

# PR003946-69: ID generator mapping
_ID_GENERATOR_MAP = {
    FAMILY_TABLE_NAME:       ensure_family_id,
    USER_TABLE_NAME:         ensure_user_id,
    USER_DETAILS_TABLE_NAME: ensure_user_id,  # UserDetails uses userId as foreign key
    ANIMAL_TABLE_NAME:       ensure_animal_id,
}


def get_store(table_name: str, pk_name: str) -> DynamoStore:
    """
    Factory function to get appropriate persistence store implementation.
    
    PR003946-95: Environment variable switchable persistence layer
    - PERSISTENCE_MODE=dynamo (default): Use DynamoDB via PynamoDB
    - PERSISTENCE_MODE=file: Use file-based JSON storage for testing
    """
    # Get persistence mode from environment
    persistence_mode = os.getenv("PERSISTENCE_MODE", "dynamo").lower()
    
    if persistence_mode == "file":
        # PR003946-95: File-based persistence for offline testing
        id_generator = _ID_GENERATOR_MAP.get(table_name)
        return FileStore(table_name, pk_name, id_generator)
    
    # Default DynamoDB persistence
    try:
        model_cls, expected_pk = _MODEL_MAP[table_name]
    except KeyError:
        raise RuntimeError(f"No PynamoDB model mapped for table '{table_name}'. "
                           f"Add it to impl/utils/orm/store.py _MODEL_MAP.")
    if pk_name != expected_pk:
        raise RuntimeError(f"PK mismatch for table '{table_name}': expected '{expected_pk}', got '{pk_name}'.")
    
    # PR003946-69: Get ID generator for this table
    id_generator = _ID_GENERATOR_MAP.get(table_name)
    
    return PynamoStore(model_cls, expected_pk, id_generator)
