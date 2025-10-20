#!/usr/bin/env python3
"""
Initialize DynamoDB with clean, consistent animal test data.
This script creates standardized animal records with proper schema structure.
"""

import boto3
import json
from datetime import datetime

def create_animal_item(animal_id, name, species, personality_description, active=True, educational_focus=True, age_appropriate=True):
    """Create a standardized animal item with consistent schema."""
    timestamp = datetime.utcnow().isoformat() + 'Z'
    
    return {
        'animalId': animal_id,
        'name': name,
        'species': species,
        'personality': {
            'description': personality_description
        },
        'active': active,
        'educational_focus': educational_focus,
        'age_appropriate': age_appropriate,
        'created': {
            'at': timestamp
        },
        'modified': {
            'at': timestamp
        },
        'softDelete': False
    }

def main():
    # Initialize DynamoDB client
    dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
    table = dynamodb.Table('quest-dev-animal')
    
    # Create standardized test animals
    animals = [
        create_animal_item(
            'test_cheetah_001',
            'Test Cheetah',
            'Acinonyx jubatus',
            'Energetic and educational, loves talking about speed and hunting techniques. I can run up to 70 mph and teach kids about conservation!'
        ),
        create_animal_item(
            'leo_001',
            'Leo the Lion',
            'Panthera leo',
            'Majestic and wise, I am the king of the savanna. I love sharing stories about pride life and teaching about leadership in the animal kingdom.'
        ),
        create_animal_item(
            'charlie_003',
            'Charlie the Elephant',
            'Loxodonta africana',
            'Gentle giant with a great memory! I enjoy teaching about elephant family bonds and conservation efforts to protect my species.'
        ),
        create_animal_item(
            'bella_002',
            'Bella the Bear',
            'Ursus americanus',
            'Friendly and curious black bear who loves teaching about forest ecosystems and seasonal changes. I know all about hibernation!'
        )
    ]
    
    # Insert each animal
    for animal in animals:
        try:
            table.put_item(Item=animal)
            print(f"✅ Created animal: {animal['animalId']} - {animal['name']}")
        except Exception as e:
            print(f"❌ Error creating {animal['animalId']}: {e}")
    
    print(f"\n🎉 Successfully initialized {len(animals)} test animals with consistent schema!")
    
    # Verify the data
    print("\n📊 Verifying created animals:")
    try:
        response = table.scan()
        for item in response['Items']:
            print(f"  - {item['animalId']}: {item['name']} ({item['species']})")
            print(f"    Personality: {item['personality']['description'][:50]}...")
            print(f"    Active: {item['active']}, Educational: {item['educational_focus']}")
    except Exception as e:
        print(f"❌ Error verifying data: {e}")

if __name__ == "__main__":
    main()