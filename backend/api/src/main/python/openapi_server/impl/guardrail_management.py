"""
Implementation module for guardrail_management
Comprehensive guardrail CRUD operations with DynamoDB persistence
"""

import uuid
import logging
from typing import Any, Dict, List, Tuple, Union
from datetime import datetime
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Attr

from ..models.error import Error
from ..models.create_guardrail_request import CreateGuardrailRequest
from ..models.update_guardrail_request import UpdateGuardrailRequest
from ..models.guardrail_response import GuardrailResponse
from ..models.guardrail_list_response import GuardrailListResponse
from ..models.audit_info import AuditInfo
from .utils.dynamo import table, to_ddb, from_ddb, now_iso, model_to_json_keyed_dict, ensure_pk, error_response, not_found

logger = logging.getLogger(__name__)

# DynamoDB table name for guardrails
GUARDRAILS_TABLE = 'quest-dev-guardrails'
GUARDRAILS_PK = 'guardrailId'


def handle_guardrail_create_post(*args, **kwargs) -> Tuple[Any, int]:
    """
    Create a new guardrail

    Args:
        body: CreateGuardrailRequest model containing guardrail data

    Returns:
        Tuple of (GuardrailResponse, 201) on success or (error_dict, error_code) on failure
    """
    try:
        # Extract body from args/kwargs
        body = None
        if args:
            body = args[0]
        else:
            body = kwargs.get('body') or kwargs.get('create_guardrail_request')

        if not body:
            return error_response(ValueError("Missing request body"))

        logger.info(f"Creating guardrail with data: {type(body)}")

        # Convert to dict if it's a model instance
        guardrail_data = model_to_json_keyed_dict(body) if hasattr(body, 'to_dict') else dict(body)

        # Generate unique ID
        guardrail_id = f"guardrail_{uuid.uuid4().hex[:12]}"
        guardrail_data[GUARDRAILS_PK] = guardrail_id

        # Add audit timestamps
        now = now_iso()
        audit_info = {"at": now}
        guardrail_data["created"] = audit_info
        guardrail_data["modified"] = audit_info

        # Initialize usage count
        guardrail_data.setdefault("usageCount", 0)

        # Validate required fields
        required_fields = ["name", "guardrailText", "category", "severity"]
        for field in required_fields:
            if field not in guardrail_data or not guardrail_data[field]:
                return error_response(ValueError(f"Missing required field: {field}"))

        # Set defaults
        guardrail_data.setdefault("ageAppropriate", ["ALL_AGES"])
        guardrail_data.setdefault("isDefault", False)

        # Save to DynamoDB
        guardrails_table = table(GUARDRAILS_TABLE)
        guardrails_table.put_item(Item=to_ddb(guardrail_data))

        # Convert to response format
        response_data = from_ddb(guardrail_data)

        # Create response object
        response = GuardrailResponse(
            guardrail_id=response_data[GUARDRAILS_PK],
            name=response_data["name"],
            description=response_data.get("description"),
            guardrail_text=response_data["guardrailText"],
            category=response_data["category"],
            severity=response_data["severity"],
            age_appropriate=response_data.get("ageAppropriate", ["ALL_AGES"]),
            usage_count=response_data.get("usageCount", 0),
            is_default=response_data.get("isDefault", False),
            created=AuditInfo(at=response_data["created"]["at"]),
            modified=AuditInfo(at=response_data["modified"]["at"])
        )

        logger.info(f"Successfully created guardrail: {guardrail_id}")
        return response, 201

    except ClientError as e:
        logger.error(f"DynamoDB error creating guardrail: {e}")
        return error_response(e)
    except Exception as e:
        logger.error(f"Error creating guardrail: {e}")
        return error_response(e)


def handle_guardrail_delete(*args, **kwargs) -> Tuple[Any, int]:
    """
    Delete a guardrail by ID

    Args:
        guardrail_id: ID of the guardrail to delete

    Returns:
        Tuple of (None, 204) on success or (error_dict, error_code) on failure
    """
    try:
        # Extract guardrail_id from args/kwargs
        guardrail_id = None
        if args:
            guardrail_id = args[0]
        else:
            guardrail_id = kwargs.get('guardrail_id') or kwargs.get('id') or kwargs.get('id_')

        if not guardrail_id:
            return error_response(ValueError("Missing guardrail_id"))

        logger.info(f"Deleting guardrail: {guardrail_id}")

        # Check if guardrail exists first
        guardrails_table = table(GUARDRAILS_TABLE)
        response = guardrails_table.get_item(Key={GUARDRAILS_PK: guardrail_id})

        if 'Item' not in response:
            return not_found(f"Guardrail not found: {guardrail_id}")

        # Delete the guardrail
        guardrails_table.delete_item(Key={GUARDRAILS_PK: guardrail_id})

        logger.info(f"Successfully deleted guardrail: {guardrail_id}")
        return None, 204

    except ClientError as e:
        logger.error(f"DynamoDB error deleting guardrail: {e}")
        return error_response(e)
    except Exception as e:
        logger.error(f"Error deleting guardrail: {e}")
        return error_response(e)


def handle_guardrail_get(*args, **kwargs) -> Tuple[Any, int]:
    """
    Get a guardrail by ID

    Args:
        guardrail_id: ID of the guardrail to retrieve

    Returns:
        Tuple of (GuardrailResponse, 200) on success or (error_dict, error_code) on failure
    """
    try:
        # Extract guardrail_id from args/kwargs
        guardrail_id = None
        if args:
            guardrail_id = args[0]
        else:
            guardrail_id = kwargs.get('guardrail_id') or kwargs.get('id') or kwargs.get('id_')

        if not guardrail_id:
            return error_response(ValueError("Missing guardrail_id"))

        logger.info(f"Retrieving guardrail: {guardrail_id}")

        # Get from DynamoDB
        guardrails_table = table(GUARDRAILS_TABLE)
        response = guardrails_table.get_item(Key={GUARDRAILS_PK: guardrail_id})

        if 'Item' not in response:
            return not_found(f"Guardrail not found: {guardrail_id}")

        # Convert to response format
        guardrail_data = from_ddb(response['Item'])

        # Create response object
        response_obj = GuardrailResponse(
            guardrail_id=guardrail_data[GUARDRAILS_PK],
            name=guardrail_data["name"],
            description=guardrail_data.get("description"),
            guardrail_text=guardrail_data["guardrailText"],
            category=guardrail_data["category"],
            severity=guardrail_data["severity"],
            age_appropriate=guardrail_data.get("ageAppropriate", ["ALL_AGES"]),
            usage_count=guardrail_data.get("usageCount", 0),
            is_default=guardrail_data.get("isDefault", False),
            created=AuditInfo(at=guardrail_data["created"]["at"]),
            modified=AuditInfo(at=guardrail_data["modified"]["at"])
        )

        logger.info(f"Successfully retrieved guardrail: {guardrail_id}")
        return response_obj, 200

    except ClientError as e:
        logger.error(f"DynamoDB error retrieving guardrail: {e}")
        return error_response(e)
    except Exception as e:
        logger.error(f"Error retrieving guardrail: {e}")
        return error_response(e)


def handle_guardrail_list_get(*args, **kwargs) -> Tuple[Any, int]:
    """
    List all guardrails with optional filtering

    Returns:
        Tuple of (GuardrailListResponse, 200) on success or (error_dict, error_code) on failure
    """
    try:
        logger.info("Listing all guardrails")

        # Get query parameters
        category = kwargs.get('category')
        severity = kwargs.get('severity')
        is_default = kwargs.get('is_default')

        # Scan DynamoDB table
        guardrails_table = table(GUARDRAILS_TABLE)
        scan_kwargs = {}

        # Add filters if provided
        filter_expressions = []
        if category:
            filter_expressions.append(Attr('category').eq(category))
        if severity:
            filter_expressions.append(Attr('severity').eq(severity))
        if is_default is not None:
            filter_expressions.append(Attr('isDefault').eq(is_default))

        if filter_expressions:
            filter_expression = filter_expressions[0]
            for expr in filter_expressions[1:]:
                filter_expression = filter_expression & expr
            scan_kwargs['FilterExpression'] = filter_expression

        response = guardrails_table.scan(**scan_kwargs)
        items = response.get('Items', [])

        # Convert to response format
        guardrails = []
        for item in items:
            guardrail_data = from_ddb(item)
            guardrail_response = GuardrailResponse(
                guardrail_id=guardrail_data[GUARDRAILS_PK],
                name=guardrail_data["name"],
                description=guardrail_data.get("description"),
                guardrail_text=guardrail_data["guardrailText"],
                category=guardrail_data["category"],
                severity=guardrail_data["severity"],
                age_appropriate=guardrail_data.get("ageAppropriate", ["ALL_AGES"]),
                usage_count=guardrail_data.get("usageCount", 0),
                is_default=guardrail_data.get("isDefault", False),
                created=AuditInfo(at=guardrail_data["created"]["at"]),
                modified=AuditInfo(at=guardrail_data["modified"]["at"])
            )
            guardrails.append(guardrail_response)

        # Create list response
        list_response = GuardrailListResponse(
            guardrails=guardrails,
            total_count=len(guardrails)
        )

        logger.info(f"Successfully listed {len(guardrails)} guardrails")
        return list_response, 200

    except ClientError as e:
        logger.error(f"DynamoDB error listing guardrails: {e}")
        return error_response(e)
    except Exception as e:
        logger.error(f"Error listing guardrails: {e}")
        return error_response(e)


def handle_guardrail_update_put(*args, **kwargs) -> Tuple[Any, int]:
    """
    Update an existing guardrail

    Args:
        guardrail_id: ID of the guardrail to update
        body: UpdateGuardrailRequest model containing updated data

    Returns:
        Tuple of (GuardrailResponse, 200) on success or (error_dict, error_code) on failure
    """
    try:
        # Extract parameters
        guardrail_id = None
        body = None

        if args:
            if len(args) >= 2:
                guardrail_id = args[0]
                body = args[1]
            else:
                guardrail_id = args[0]

        if not guardrail_id:
            guardrail_id = kwargs.get('guardrail_id') or kwargs.get('id') or kwargs.get('id_')
        if not body:
            body = kwargs.get('body') or kwargs.get('update_guardrail_request')

        if not guardrail_id:
            return error_response(ValueError("Missing guardrail_id"))
        if not body:
            return error_response(ValueError("Missing request body"))

        logger.info(f"Updating guardrail: {guardrail_id}")

        # Convert to dict if it's a model instance
        update_data = model_to_json_keyed_dict(body) if hasattr(body, 'to_dict') else dict(body)

        # Get existing guardrail
        guardrails_table = table(GUARDRAILS_TABLE)
        response = guardrails_table.get_item(Key={GUARDRAILS_PK: guardrail_id})

        if 'Item' not in response:
            return not_found(f"Guardrail not found: {guardrail_id}")

        existing_data = from_ddb(response['Item'])

        # Update fields
        for field in ['name', 'description', 'guardrailText', 'category', 'severity', 'ageAppropriate', 'isDefault']:
            if field in update_data and update_data[field] is not None:
                existing_data[field] = update_data[field]

        # Update modified timestamp
        existing_data["modified"] = {"at": now_iso()}

        # Save updated data
        guardrails_table.put_item(Item=to_ddb(existing_data))

        # Create response object
        response_obj = GuardrailResponse(
            guardrail_id=existing_data[GUARDRAILS_PK],
            name=existing_data["name"],
            description=existing_data.get("description"),
            guardrail_text=existing_data["guardrailText"],
            category=existing_data["category"],
            severity=existing_data["severity"],
            age_appropriate=existing_data.get("ageAppropriate", ["ALL_AGES"]),
            usage_count=existing_data.get("usageCount", 0),
            is_default=existing_data.get("isDefault", False),
            created=AuditInfo(at=existing_data["created"]["at"]),
            modified=AuditInfo(at=existing_data["modified"]["at"])
        )

        logger.info(f"Successfully updated guardrail: {guardrail_id}")
        return response_obj, 200

    except ClientError as e:
        logger.error(f"DynamoDB error updating guardrail: {e}")
        return error_response(e)
    except Exception as e:
        logger.error(f"Error updating guardrail: {e}")
        return error_response(e)


def handle_(*args, **kwargs) -> Tuple[Any, int]:
    """
    Generic handler routing function for guardrail management operations
    Routes to specific handler functions based on calling context
    """
    import inspect

    # Get caller information to determine which operation to route to
    caller_frame = inspect.currentframe().f_back
    caller_name = caller_frame.f_code.co_name

    logger.info(f"Routing guardrail operation: {caller_name}")

    # Route to specific handler based on caller
    if caller_name == "guardrail_create_post":
        return handle_guardrail_create_post(*args, **kwargs)
    elif caller_name == "guardrail_delete":
        return handle_guardrail_delete(*args, **kwargs)
    elif caller_name == "guardrail_get":
        return handle_guardrail_get(*args, **kwargs)
    elif caller_name == "guardrail_list_get":
        return handle_guardrail_list_get(*args, **kwargs)
    elif caller_name == "guardrail_update_put":
        return handle_guardrail_update_put(*args, **kwargs)
    else:
        # Fallback for unknown operations
        logger.error(f"Unknown guardrail operation: {caller_name}")
        return error_response(ValueError(f"Unknown operation: {caller_name}"))

