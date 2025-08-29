import os
import logging
from time import perf_counter
from typing import Any, Dict, List, Union

from botocore.exceptions import ClientError
from openapi_server.models.family import Family

from .utils.dynamo import (
    table, to_ddb, from_ddb, now_iso,
    model_to_json_keyed_dict, ensure_pk,
    error_response, not_found
)


logger = logging.getLogger(__name__)

# ---- Config ----
DYNAMO_TABLE_NAME = os.getenv(
    "FAMILY_DYNAMO_TABLE_NAME",
    os.getenv("DYNAMO_TABLE_NAME", "quest-dev-family"),
)
PK_NAME = os.getenv("FAMILY_DYNAMO_PK_NAME", "familyId")


def _table():
    return table(DYNAMO_TABLE_NAME)


# ---- Handlers ----
def handle_list_families():
    """
    Scan and return all families.
    NOTE: For production-scale datasets, prefer queries (possibly via a GSI) over scans.
    """
    start = perf_counter()
    logger.info("family.list: start scan table=%s", DYNAMO_TABLE_NAME)

    tbl = _table()
    items: List[Dict[str, Any]] = []
    scan_kwargs: Dict[str, Any] = {}
    page = 0

    while True:
        resp = tbl.scan(**scan_kwargs)
        page += 1
        batch = resp.get("Items", [])
        items.extend(batch)

        lek = resp.get("LastEvaluatedKey")
        logger.debug(
            "family.list: scanned page=%d batch_size=%d has_more=%s",
            page, len(batch), bool(lek),
        )
        if not lek:
            break
        scan_kwargs["ExclusiveStartKey"] = lek

    elapsed_ms = round((perf_counter() - start) * 1000, 2)
    logger.info("family.list: done pages=%d total=%d ms=%s", page, len(items), elapsed_ms)
    return [from_ddb(i) for i in items]


def handle_create_family(body: Union[Family, Dict[str, Any]]):
    """
    Create a new family. If familyId is provided, use it; otherwise generate one.
    """
    start = perf_counter()
    data_src = type(body).__name__
    item = model_to_json_keyed_dict(body) if isinstance(body, Family) else dict(body or {})
    ensure_pk(item, PK_NAME)

    family_id = item.get(PK_NAME)
    logger.info("family.create: familyId=%s source=%s", family_id, data_src)
    logger.debug("family.create: request_body_keys=%s", sorted(list(item.keys())))

    # Auditing defaults
    item.setdefault("softDelete", False)
    now = now_iso()
    item.setdefault("created", {"at": now})
    item["modified"] = {"at": now}

    try:
        _table().put_item(
            Item=to_ddb(item),
            ConditionExpression=f"attribute_not_exists({PK_NAME})"
        )
    except ClientError as e:
        code = e.response.get("Error", {}).get("Code")
        if code == "ConditionalCheckFailedException":
            logger.warning("family.create: conflict familyId=%s already exists", family_id)
            return error_response("Conflict", f"Item already exists: {PK_NAME}={item[PK_NAME]}", 409)
        logger.exception("family.create: failed familyId=%s", family_id)
        raise

    elapsed_ms = round((perf_counter() - start) * 1000, 2)
    logger.info("family.create: success familyId=%s ms=%s", family_id, elapsed_ms)
    return from_ddb(item), 201


def handle_get_family(family_id: str):
    start = perf_counter()
    logger.info("family.get: familyId=%s", family_id)

    resp = _table().get_item(Key={PK_NAME: family_id})
    item = resp.get("Item")
    if not item:
        logger.info("family.get: not_found familyId=%s", family_id)
        return not_found(PK_NAME, family_id)

    elapsed_ms = round((perf_counter() - start) * 1000, 2)
    logger.debug("family.get: found familyId=%s keys=%s ms=%s",
                 family_id, sorted(list(item.keys())), elapsed_ms)
    return from_ddb(item)


def handle_update_family(family_id: str, body: Union[Family, Dict[str, Any]]):
    """
    Partial update; allowed fields: parents, students, softDelete.
    Body `familyId` (or `id`) must match the path param if present.
    """
    start = perf_counter()
    data = model_to_json_keyed_dict(body) if isinstance(body, Family) else dict(body or {})
    logger.info("family.update: start familyId=%s", family_id)
    logger.debug("family.update: incoming_keys=%s", sorted(list(data.keys())))

    allowed_fields = ("parents", "students", "softDelete")
    expr_names: Dict[str, str] = {"#modified": "modified"}
    expr_values: Dict[str, Any] = {":modified": to_ddb({"at": now_iso()})}
    set_clauses: List[str] = ["#modified = :modified"]

    updated_fields: List[str] = []
    for f in allowed_fields:
        if f in data:
            expr_names[f"#{f}"] = f
            expr_values[f":{f}"] = to_ddb(data[f])
            set_clauses.append(f"#{f} = :{f}")
            updated_fields.append(f)

    if len(set_clauses) == 1:
        # Nothing to update
        logger.info("family.update: no-op familyId=%s (no allowed fields present)", family_id)
        resp = _table().get_item(Key={PK_NAME: family_id})
        item = resp.get("Item")
        if not item:
            logger.info("family.update: not_found familyId=%s", family_id)
            return not_found(PK_NAME, family_id)
        return from_ddb(item)

    logger.debug(
        "family.update: fields=%s update_expr=%s",
        updated_fields, "SET " + ", ".join(set_clauses),
    )

    try:
        resp = _table().update_item(
            Key={PK_NAME: family_id},
            UpdateExpression="SET " + ", ".join(set_clauses),
            ExpressionAttributeNames=expr_names,
            ExpressionAttributeValues=expr_values,
            ConditionExpression=f"attribute_exists({PK_NAME})",
            ReturnValues="ALL_NEW",
        )
    except ClientError as e:
        code = e.response.get("Error", {}).get("Code")
        if code == "ConditionalCheckFailedException":
            logger.info("family.update: not_found familyId=%s", family_id)
            return not_found(PK_NAME, family_id)
        logger.exception("family.update: failed familyId=%s", family_id)
        raise

    elapsed_ms = round((perf_counter() - start) * 1000, 2)
    logger.info("family.update: success familyId=%s fields=%s ms=%s",
                family_id, updated_fields, elapsed_ms)
    return from_ddb(resp.get("Attributes", {}))


def handle_delete_family(family_id: str):
    """
    Soft-delete a family (sets softDelete=true). Returns 204 on success, 404 if missing.
    """
    start = perf_counter()
    logger.info("family.delete: soft-delete start familyId=%s", family_id)

    try:
        _table().update_item(
            Key={PK_NAME: family_id},
            UpdateExpression="SET #soft = :true, #modified = :m",
            ExpressionAttributeNames={"#soft": "softDelete", "#modified": "modified"},
            ExpressionAttributeValues={
                ":true": True,
                ":m": to_ddb({"at": now_iso()}),
            },
            ConditionExpression=f"attribute_exists({PK_NAME})",
            ReturnValues="NONE",
        )
    except ClientError as e:
        code = e.response.get("Error", {}).get("Code")
        if code == "ConditionalCheckFailedException":
            logger.info("family.delete: not_found familyId=%s", family_id)
            return not_found(PK_NAME, family_id)
        logger.exception("family.delete: failed familyId=%s", family_id)
        raise

    elapsed_ms = round((perf_counter() - start) * 1000, 2)
    logger.info("family.delete: soft-delete success familyId=%s ms=%s", family_id, elapsed_ms)
    return None, 204
