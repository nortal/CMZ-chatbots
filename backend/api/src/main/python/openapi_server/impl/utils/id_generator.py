"""
PR003946-69: Server-Generated IDs Implementation

This module provides utilities for generating unique IDs for entities
when they are not provided by the client.
"""

import uuid
from datetime import datetime, timezone


def generate_uuid():
    """Generate a UUID4 string."""
    return str(uuid.uuid4())


def generate_prefixed_id(prefix):
    """Generate a UUID with a prefix (e.g., 'user_abc123')."""
    short_uuid = str(uuid.uuid4()).replace('-', '')[:8]
    return f"{prefix}_{short_uuid}"


def generate_animal_id():
    """Generate a unique animal ID."""
    return generate_prefixed_id('animal')


def generate_user_id():
    """Generate a unique user ID."""
    return generate_prefixed_id('user')


def generate_family_id():
    """Generate a unique family ID."""
    return generate_prefixed_id('family')


def generate_conversation_id():
    """Generate a unique conversation ID."""
    return generate_prefixed_id('convo')


def generate_knowledge_id():
    """Generate a unique knowledge article ID."""
    return generate_prefixed_id('knowledge')


def ensure_entity_id(item, id_field, id_generator_func):
    """
    Ensure an entity has an ID, generating one if not provided.
    
    PR003946-69: Server-generated IDs for data consistency
    
    Args:
        item: Dictionary containing entity data
        id_field: Name of the ID field (e.g., 'userId', 'animalId')  
        id_generator_func: Function to generate the ID
        
    Returns:
        The item with ID field populated
    """
    if not item.get(id_field):
        item[id_field] = id_generator_func()
    
    return item


def ensure_user_id(user_data):
    """Ensure user data has a userId."""
    return ensure_entity_id(user_data, 'userId', generate_user_id)


def ensure_animal_id(animal_data):
    """Ensure animal data has an animalId.""" 
    return ensure_entity_id(animal_data, 'animalId', generate_animal_id)


def ensure_family_id(family_data):
    """Ensure family data has a familyId."""
    return ensure_entity_id(family_data, 'familyId', generate_family_id)


def ensure_conversation_id(conversation_data):
    """Ensure conversation data has a conversationId."""
    return ensure_entity_id(conversation_data, 'conversationId', generate_conversation_id)


def ensure_knowledge_id(knowledge_data):
    """Ensure knowledge data has a knowledgeId."""
    return ensure_entity_id(knowledge_data, 'knowledgeId', generate_knowledge_id)


def add_audit_timestamps(item, user_info=None):
    """
    Add creation and modification timestamps to an item.
    
    Args:
        item: Dictionary containing entity data
        user_info: Optional dict with user info for audit trail
    
    Returns:
        The item with audit timestamps
    """
    now = datetime.now(timezone.utc).isoformat()
    
    # Default user info for system operations
    default_user = {
        'userId': 'system',
        'email': 'system@cmz.org', 
        'displayName': 'System'
    }
    
    audit_user = user_info or default_user
    
    # Add created timestamp if not exists
    if 'created' not in item:
        item['created'] = {
            'at': now,
            'by': audit_user
        }
    
    # Always update modified timestamp
    item['modified'] = {
        'at': now,
        'by': audit_user
    }
    
    return item


# Mapping of entity types to their ID generators
ENTITY_ID_GENERATORS = {
    'user': ensure_user_id,
    'animal': ensure_animal_id, 
    'family': ensure_family_id,
    'conversation': ensure_conversation_id,
    'knowledge': ensure_knowledge_id
}