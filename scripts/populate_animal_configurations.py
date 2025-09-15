#!/usr/bin/env python3
"""
Populate all animals in DynamoDB with complete configuration data.
This ensures animals have all the fields needed for the Animal Config UI.
"""

import boto3
import json
from decimal import Decimal

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
table = dynamodb.Table('quest-dev-animal')

# Default configuration values that comply with OpenAPI constraints
DEFAULT_CONFIG = {
    'voice': 'alloy',
    'aiModel': 'gpt-4o-mini',
    'temperature': Decimal('0.7'),  # Use Decimal to ensure exact 0.7
    'topP': Decimal('1.0'),
    'toolsEnabled': ['facts', 'media_lookup'],
    'guardrails': {
        'contentFiltering': True,
        'ageAppropriate': True,
        'maxResponseLength': 500
    },
    'status': 'active'
}

# Different configurations for variety
VOICE_OPTIONS = ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer']
MODEL_OPTIONS = ['gpt-4o-mini', 'gpt-4', 'gpt-3.5-turbo']
TEMP_OPTIONS = [Decimal('0.5'), Decimal('0.7'), Decimal('0.9'), Decimal('1.0')]

def get_all_animals():
    """Scan table to get all animals"""
    response = table.scan()
    animals = response['Items']

    # Handle pagination
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        animals.extend(response['Items'])

    return animals

def update_animal_configuration(animal):
    """Update an animal with configuration data if missing"""
    animal_id = animal['animalId']

    # Check if configuration already exists
    if 'configuration' in animal and animal['configuration']:
        print(f"Animal {animal_id} already has configuration, checking for missing fields...")
        config = animal['configuration']
        updated = False

        # Ensure all required fields exist
        if 'voice' not in config:
            config['voice'] = DEFAULT_CONFIG['voice']
            updated = True
        if 'aiModel' not in config:
            config['aiModel'] = DEFAULT_CONFIG['aiModel']
            updated = True
        if 'temperature' not in config:
            config['temperature'] = DEFAULT_CONFIG['temperature']
            updated = True
        if 'topP' not in config:
            config['topP'] = DEFAULT_CONFIG['topP']
            updated = True
        if 'toolsEnabled' not in config:
            config['toolsEnabled'] = DEFAULT_CONFIG['toolsEnabled']
            updated = True
        if 'guardrails' not in config:
            config['guardrails'] = DEFAULT_CONFIG['guardrails']
            updated = True
        if 'status' not in config:
            config['status'] = DEFAULT_CONFIG['status']
            updated = True

        if not updated:
            print(f"  ✓ All configuration fields present")
            return False
    else:
        # Create new configuration with some variety
        idx = hash(animal_id) % len(VOICE_OPTIONS)
        config = {
            'voice': VOICE_OPTIONS[idx % len(VOICE_OPTIONS)],
            'aiModel': MODEL_OPTIONS[idx % len(MODEL_OPTIONS)],
            'temperature': TEMP_OPTIONS[idx % len(TEMP_OPTIONS)],
            'topP': DEFAULT_CONFIG['topP'],
            'toolsEnabled': DEFAULT_CONFIG['toolsEnabled'],
            'guardrails': DEFAULT_CONFIG['guardrails'],
            'status': DEFAULT_CONFIG['status']
        }
        print(f"Animal {animal_id} missing configuration, adding new config...")

    # Update the animal in DynamoDB
    try:
        response = table.update_item(
            Key={'animalId': animal_id},
            UpdateExpression='SET configuration = :config',
            ExpressionAttributeValues={
                ':config': config
            },
            ReturnValues='UPDATED_NEW'
        )
        print(f"  ✓ Updated {animal_id} with configuration")
        print(f"    - voice: {config['voice']}")
        print(f"    - aiModel: {config['aiModel']}")
        print(f"    - temperature: {config['temperature']}")
        print(f"    - topP: {config['topP']}")
        return True
    except Exception as e:
        print(f"  ✗ Error updating {animal_id}: {e}")
        return False

def main():
    print("=== Populating Animal Configurations ===\n")

    # Get all animals
    animals = get_all_animals()
    print(f"Found {len(animals)} animals in database\n")

    # Update each animal
    updated_count = 0
    for animal in animals:
        if update_animal_configuration(animal):
            updated_count += 1
        print()

    print(f"\n=== Summary ===")
    print(f"Total animals: {len(animals)}")
    print(f"Updated: {updated_count}")
    print(f"Already configured: {len(animals) - updated_count}")

if __name__ == '__main__':
    main()