"""
Guardrails management implementation for ChatGPT safety
"""

import boto3
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import uuid
from botocore.exceptions import ClientError

from .utils.dynamo import (
    to_ddb, from_ddb, now_iso,
    model_to_json_keyed_dict, ensure_pk,
    error_response, not_found
)

# DynamoDB setup
dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
GUARDRAILS_TABLE = 'quest-dev-guardrails'

def _table():
    """Get DynamoDB table for guardrails"""
    return dynamodb.Table(GUARDRAILS_TABLE)


class GuardrailsManager:
    """Manages guardrail rules for AI conversations"""

    # Pre-built templates
    TEMPLATES = {
        'family_friendly': {
            'id': 'family_friendly',
            'name': 'Family Friendly Package',
            'description': 'Ensures all content is appropriate for children and families',
            'rules': [
                {'type': 'ALWAYS', 'rule': 'Always use language appropriate for all ages', 'priority': 100},
                {'type': 'NEVER', 'rule': 'Never discuss violence, weapons, or harmful activities', 'priority': 100},
                {'type': 'NEVER', 'rule': 'Never use profanity or inappropriate language', 'priority': 100},
                {'type': 'ENCOURAGE', 'rule': 'Encourage curiosity and learning', 'priority': 75}
            ]
        },
        'educational_focus': {
            'id': 'educational_focus',
            'name': 'Educational Focus Package',
            'description': 'Promotes educational content and learning',
            'rules': [
                {'type': 'ALWAYS', 'rule': 'Always include educational facts when relevant', 'priority': 80},
                {'type': 'ENCOURAGE', 'rule': 'Encourage questions about wildlife and conservation', 'priority': 75},
                {'type': 'ALWAYS', 'rule': 'Always explain complex concepts in simple terms', 'priority': 85},
                {'type': 'DISCOURAGE', 'rule': 'Discourage off-topic conversations', 'priority': 60}
            ]
        },
        'safety_first': {
            'id': 'safety_first',
            'name': 'Safety First Package',
            'description': 'Prioritizes visitor and animal safety',
            'rules': [
                {'type': 'NEVER', 'rule': 'Never suggest dangerous interactions with animals', 'priority': 100},
                {'type': 'ALWAYS', 'rule': 'Always emphasize zoo safety rules', 'priority': 95},
                {'type': 'NEVER', 'rule': 'Never encourage feeding or touching animals', 'priority': 100},
                {'type': 'ALWAYS', 'rule': 'Always mention proper viewing distances', 'priority': 90}
            ]
        }
    }

    @classmethod
    def create_guardrail(cls, guardrail_data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """Create a new guardrail rule"""
        try:
            # Generate unique ID
            guardrail_id = f"gr_{uuid.uuid4().hex[:12]}"

            # Build item
            item = {
                'guardrailId': guardrail_id,
                'name': guardrail_data['name'],
                'type': guardrail_data['type'],  # ALWAYS, NEVER, ENCOURAGE, DISCOURAGE
                'rule': guardrail_data['rule'],
                'description': guardrail_data.get('description', ''),
                'category': guardrail_data.get('category', 'content_safety'),
                'priority': guardrail_data.get('priority', 50),
                'isActive': guardrail_data.get('isActive', True),
                'isGlobal': guardrail_data.get('isGlobal', False),
                'keywords': guardrail_data.get('keywords', []),
                'examples': guardrail_data.get('examples', {}),
                'created': {
                    'at': now_iso(),
                    'by': guardrail_data.get('createdBy', {'userId': 'system', 'email': 'system@cmz.org', 'displayName': 'System'})
                },
                'modified': {
                    'at': now_iso(),
                    'by': guardrail_data.get('createdBy', {'userId': 'system', 'email': 'system@cmz.org', 'displayName': 'System'})
                },
                'softDelete': False
            }

            # Save to DynamoDB
            _table().put_item(Item=to_ddb(item))
            return from_ddb(item), 201

        except ClientError as e:
            return error_response(e)

    @classmethod
    def list_guardrails(cls, category: Optional[str] = None,
                       is_active: Optional[bool] = None,
                       is_global: Optional[bool] = None) -> Tuple[List[Dict[str, Any]], int]:
        """List all guardrails with optional filters"""
        try:
            # Build filter expression
            filter_expressions = []
            expression_values = {}

            # Always exclude soft-deleted items
            filter_expressions.append('softDelete = :false')
            expression_values[':false'] = False

            if category:
                filter_expressions.append('category = :category')
                expression_values[':category'] = category

            if is_active is not None:
                filter_expressions.append('isActive = :active')
                expression_values[':active'] = is_active

            if is_global is not None:
                filter_expressions.append('isGlobal = :global')
                expression_values[':global'] = is_global

            # Scan with filters
            scan_kwargs = {}
            if filter_expressions:
                scan_kwargs['FilterExpression'] = ' AND '.join(filter_expressions)
                scan_kwargs['ExpressionAttributeValues'] = expression_values

            response = _table().scan(**scan_kwargs)

            # Convert and sort by priority (higher first)
            guardrails = [from_ddb(item) for item in response.get('Items', [])]
            guardrails.sort(key=lambda x: x.get('priority', 50), reverse=True)

            return guardrails, 200

        except ClientError as e:
            return error_response(e)

    @classmethod
    def get_guardrail(cls, guardrail_id: str) -> Tuple[Dict[str, Any], int]:
        """Get specific guardrail by ID"""
        try:
            response = _table().get_item(Key={'guardrailId': guardrail_id})

            if 'Item' not in response:
                return not_found(f"Guardrail {guardrail_id} not found")

            item = from_ddb(response['Item'])

            # Check if soft-deleted
            if item.get('softDelete', False):
                return not_found(f"Guardrail {guardrail_id} not found")

            return item, 200

        except ClientError as e:
            return error_response(e)

    @classmethod
    def update_guardrail(cls, guardrail_id: str, update_data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """Update guardrail"""
        try:
            # Get existing guardrail
            response = _table().get_item(Key={'guardrailId': guardrail_id})

            if 'Item' not in response:
                return not_found(f"Guardrail {guardrail_id} not found")

            existing = from_ddb(response['Item'])

            # Check if soft-deleted
            if existing.get('softDelete', False):
                return not_found(f"Guardrail {guardrail_id} not found")

            # Update allowed fields
            allowed_fields = ['name', 'description', 'category', 'priority', 'isActive', 'keywords', 'examples']

            for field in allowed_fields:
                if field in update_data and update_data[field] is not None:
                    existing[field] = update_data[field]

            # Update modified timestamp
            existing['modified'] = {
                'at': now_iso(),
                'by': update_data.get('modifiedBy', {'userId': 'system', 'email': 'system@cmz.org', 'displayName': 'System'})
            }

            # Save to DynamoDB
            _table().put_item(Item=to_ddb(existing))
            return from_ddb(existing), 200

        except ClientError as e:
            return error_response(e)

    @classmethod
    def delete_guardrail(cls, guardrail_id: str) -> Tuple[None, int]:
        """Soft delete guardrail"""
        try:
            # Get existing guardrail
            response = _table().get_item(Key={'guardrailId': guardrail_id})

            if 'Item' not in response:
                return not_found(f"Guardrail {guardrail_id} not found")

            existing = from_ddb(response['Item'])

            # Mark as soft-deleted and inactive
            existing['softDelete'] = True
            existing['isActive'] = False
            existing['deleted'] = {
                'at': now_iso(),
                'by': {'userId': 'system', 'email': 'system@cmz.org', 'displayName': 'System'}
            }

            # Save to DynamoDB
            _table().put_item(Item=to_ddb(existing))
            return None, 204

        except ClientError as e:
            return error_response(e)

    @classmethod
    def get_templates(cls) -> Tuple[List[Dict[str, Any]], int]:
        """Get pre-built guardrail templates"""
        templates = list(cls.TEMPLATES.values())
        return templates, 200

    @classmethod
    def apply_template(cls, template_id: str, animal_id: str) -> Tuple[Dict[str, Any], int]:
        """Apply a template to an animal"""
        try:
            # Get template
            if template_id not in cls.TEMPLATES:
                return not_found(f"Template {template_id} not found")

            template = cls.TEMPLATES[template_id]

            # Create guardrails from template
            created_ids = []
            for rule in template['rules']:
                guardrail_data = {
                    'name': f"{template['name']} - {rule['rule'][:50]}",
                    'type': rule['type'],
                    'rule': rule['rule'],
                    'category': 'content_safety',
                    'priority': rule.get('priority', 50),
                    'isActive': True,
                    'isGlobal': False,
                    'keywords': [template_id, animal_id]
                }

                result, status = cls.create_guardrail(guardrail_data)
                if status == 201:
                    created_ids.append(result['guardrailId'])

            # Update animal config with new guardrails
            animal_table = dynamodb.Table('quest-dev-animal')
            animal_response = animal_table.get_item(Key={'animalId': animal_id})

            if 'Item' not in animal_response:
                return not_found(f"Animal {animal_id} not found")

            animal = from_ddb(animal_response['Item'])

            # Initialize guardrails if not present
            if 'guardrails' not in animal:
                animal['guardrails'] = {'selected': [], 'custom': []}

            # Add new guardrail IDs
            animal['guardrails']['selected'] = list(set(
                animal['guardrails'].get('selected', []) + created_ids
            ))

            # Update modified timestamp
            animal['modified'] = {'at': now_iso()}

            # Save animal config
            animal_table.put_item(Item=to_ddb(animal))

            return {
                'guardrailsApplied': len(created_ids),
                'animalId': animal_id
            }, 200

        except ClientError as e:
            return error_response(e)

    @classmethod
    def get_guardrails_for_animal(cls, animal_id: str) -> List[Dict[str, Any]]:
        """Get all guardrails for a specific animal"""
        try:
            # Get animal config
            animal_table = dynamodb.Table('quest-dev-animal')
            animal_response = animal_table.get_item(Key={'animalId': animal_id})

            if 'Item' not in animal_response:
                return []

            animal = from_ddb(animal_response['Item'])
            guardrail_ids = []

            # Get selected guardrail IDs
            if 'guardrails' in animal and 'selected' in animal['guardrails']:
                guardrail_ids.extend(animal['guardrails']['selected'])

            # Get global guardrails
            global_response = _table().scan(
                FilterExpression='isGlobal = :true AND isActive = :active AND softDelete = :false',
                ExpressionAttributeValues={':true': True, ':active': True, ':false': False}
            )
            for item in global_response.get('Items', []):
                guardrail_id = item.get('guardrailId')
                if guardrail_id and guardrail_id not in guardrail_ids:
                    guardrail_ids.append(guardrail_id)

            # Fetch all guardrails
            guardrails = []
            for gid in guardrail_ids:
                response = _table().get_item(Key={'guardrailId': gid})
                if 'Item' in response:
                    item = from_ddb(response['Item'])
                    if item.get('isActive') and not item.get('softDelete'):
                        guardrails.append(item)

            # Add custom rules from animal config
            if 'guardrails' in animal and 'custom' in animal['guardrails']:
                for custom in animal['guardrails']['custom']:
                    guardrails.append({
                        'guardrailId': f"custom_{animal_id}_{uuid.uuid4().hex[:6]}",
                        'type': custom['type'],
                        'rule': custom['rule'],
                        'priority': 75,  # Custom rules have medium-high priority
                        'isActive': True,
                        'isGlobal': False,
                        'category': 'animal_specific'
                    })

            # Sort by priority (higher first)
            guardrails.sort(key=lambda x: x.get('priority', 50), reverse=True)

            return guardrails

        except ClientError:
            return []

    @classmethod
    def format_guardrails_for_prompt(cls, guardrails: List[Dict]) -> str:
        """Format guardrails into text for system prompt"""
        if not guardrails:
            return ""

        sections = {
            'ALWAYS': [],
            'NEVER': [],
            'ENCOURAGE': [],
            'DISCOURAGE': []
        }

        for g in guardrails:
            rule_type = g.get('type', 'ALWAYS')
            rule_text = g.get('rule', '')
            if rule_text:
                sections[rule_type].append(f"• {rule_text}")

        prompt_parts = []

        if sections['ALWAYS']:
            prompt_parts.append("IMPORTANT RULES - ALWAYS:")
            prompt_parts.extend(sections['ALWAYS'])
            prompt_parts.append("")

        if sections['NEVER']:
            prompt_parts.append("IMPORTANT RULES - NEVER:")
            prompt_parts.extend(sections['NEVER'])
            prompt_parts.append("")

        if sections['ENCOURAGE']:
            prompt_parts.append("GUIDELINES - ENCOURAGE:")
            prompt_parts.extend(sections['ENCOURAGE'])
            prompt_parts.append("")

        if sections['DISCOURAGE']:
            prompt_parts.append("GUIDELINES - AVOID:")
            prompt_parts.extend(sections['DISCOURAGE'])
            prompt_parts.append("")

        return "\n".join(prompt_parts)


# Handler functions for API endpoints
def handle_list_guardrails(category=None, is_active=None, is_global=None, *args, **kwargs):
    """Handle GET /guardrails"""
    # Convert string parameters to boolean if needed
    if isinstance(is_active, str):
        is_active = is_active.lower() == 'true'
    if isinstance(is_global, str):
        is_global = is_global.lower() == 'true'

    return GuardrailsManager.list_guardrails(category, is_active, is_global)


def handle_create_guardrail(body, *args, **kwargs):
    """Handle POST /guardrails"""
    if not body:
        return {'error': 'Missing request body'}, 400

    # Convert body to dict if it's a model
    guardrail_data = model_to_json_keyed_dict(body) if hasattr(body, 'to_dict') else dict(body)

    # Validate required fields
    required = ['name', 'type', 'rule']
    for field in required:
        if field not in guardrail_data:
            return {'error': f'Missing required field: {field}'}, 400

    # Validate type
    valid_types = ['ALWAYS', 'NEVER', 'ENCOURAGE', 'DISCOURAGE']
    if guardrail_data['type'] not in valid_types:
        return {'error': f'Invalid type. Must be one of: {", ".join(valid_types)}'}, 400

    return GuardrailsManager.create_guardrail(guardrail_data)


def handle_get_guardrail(guardrail_id, *args, **kwargs):
    """Handle GET /guardrails/{guardrailId}"""
    if not guardrail_id:
        return {'error': 'Missing guardrail ID'}, 400

    return GuardrailsManager.get_guardrail(guardrail_id)


def handle_update_guardrail(guardrail_id, body, *args, **kwargs):
    """Handle PATCH /guardrails/{guardrailId}"""
    if not guardrail_id:
        return {'error': 'Missing guardrail ID'}, 400

    if not body:
        return {'error': 'Missing request body'}, 400

    # Convert body to dict if it's a model
    update_data = model_to_json_keyed_dict(body) if hasattr(body, 'to_dict') else dict(body)

    return GuardrailsManager.update_guardrail(guardrail_id, update_data)


def handle_delete_guardrail(guardrail_id, *args, **kwargs):
    """Handle DELETE /guardrails/{guardrailId}"""
    if not guardrail_id:
        return {'error': 'Missing guardrail ID'}, 400

    return GuardrailsManager.delete_guardrail(guardrail_id)


def handle_get_templates(*args, **kwargs):
    """Handle GET /guardrails/templates"""
    return GuardrailsManager.get_templates()


def handle_apply_template(body, *args, **kwargs):
    """Handle POST /guardrails/apply-template"""
    if not body:
        return {'error': 'Missing request body'}, 400

    # Convert body to dict if it's a model
    data = model_to_json_keyed_dict(body) if hasattr(body, 'to_dict') else dict(body)

    # Validate required fields
    if 'templateId' not in data:
        return {'error': 'Missing required field: templateId'}, 400
    if 'animalId' not in data:
        return {'error': 'Missing required field: animalId'}, 400

    return GuardrailsManager.apply_template(data['templateId'], data['animalId'])


def handle_get_animal_effective_guardrails(animal_id, *args, **kwargs):
    """Handle GET /animal/{animalId}/guardrails/effective"""
    if not animal_id:
        return {'error': 'Missing animal ID'}, 400

    guardrails = GuardrailsManager.get_guardrails_for_animal(animal_id)
    return guardrails, 200


def handle_get_animal_system_prompt(animal_id, *args, **kwargs):
    """Handle GET /animal/{animalId}/system-prompt"""
    if not animal_id:
        return {'error': 'Missing animal ID'}, 400

    # Get guardrails for the animal
    guardrails = GuardrailsManager.get_guardrails_for_animal(animal_id)

    # Format as system prompt
    guardrails_text = GuardrailsManager.format_guardrails_for_prompt(guardrails)

    # Get base animal information
    animal_table = dynamodb.Table('quest-dev-animal')
    animal_response = animal_table.get_item(Key={'animalId': animal_id})

    if 'Item' not in animal_response:
        return not_found(f"Animal {animal_id} not found")

    animal = from_ddb(animal_response['Item'])

    # Build complete system prompt
    prompt = f"""You are {animal.get('name', 'an animal')} at Cougar Mountain Zoo.
{animal.get('personality', '')}
Key facts: {animal.get('facts', '')}

{guardrails_text}

Remember to stay in character and make the conversation engaging and educational for zoo visitors."""

    return {
        'prompt': prompt,
        'guardrailCount': len(guardrails)
    }, 200
# Auto-generated handler functions

def handle_apply_guardrail_template(*args, **kwargs) -> Tuple[Any, int]:
    """
    Implementation handler for apply_guardrail_template

    TODO: Implement business logic for this operation
    """
    from ..models.error import Error
    error_obj = Error(
        code="not_implemented",
        message=f"Operation apply_guardrail_template not yet implemented",
        details={"operation": "apply_guardrail_template", "handler": "handle_apply_guardrail_template"}
    )
    return error_obj.to_dict(), 501


def handle_get_guardrail_templates(*args, **kwargs) -> Tuple[Any, int]:
    """
    Implementation handler for get_guardrail_templates

    TODO: Implement business logic for this operation
    """
    from ..models.error import Error
    error_obj = Error(
        code="not_implemented",
        message=f"Operation get_guardrail_templates not yet implemented",
        details={"operation": "get_guardrail_templates", "handler": "handle_get_guardrail_templates"}
    )
    return error_obj.to_dict(), 501

