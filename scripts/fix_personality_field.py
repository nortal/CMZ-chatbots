#!/usr/bin/env python3
"""
Script to fix personality field in DynamoDB animal table.
Converts string personality values to Map format expected by PynamoDB.
"""

import boto3
import json
import sys

# Initialize DynamoDB client
dynamodb = boto3.client('dynamodb', region_name='us-west-2')
table_name = 'quest-dev-animal'

def fix_personality_field():
    """Convert string personality fields to Map format"""

    print(f"Scanning {table_name} for animals with string personality fields...")

    # Scan the table
    response = dynamodb.scan(
        TableName=table_name,
        ProjectionExpression="animalId,personality"
    )

    items_to_fix = []

    # Check each item
    for item in response.get('Items', []):
        animal_id = item.get('animalId', {}).get('S', '')
        personality = item.get('personality', {})

        # If personality is stored as a string, it needs fixing
        if 'S' in personality:
            items_to_fix.append({
                'id': animal_id,
                'old_personality': personality['S']
            })

    if not items_to_fix:
        print("No items need fixing. All personality fields are already in Map format.")
        return 0

    print(f"Found {len(items_to_fix)} items to fix:")
    for item in items_to_fix:
        personality_preview = item['old_personality'][:50] + '...' if len(item['old_personality']) > 50 else item['old_personality']
        print(f"  - {item['id']}: '{personality_preview}'")

    print("\nProceeding with conversion...")

    # Fix each item
    success_count = 0
    for item in items_to_fix:
        try:
            # Update to Map format with description field
            update_response = dynamodb.update_item(
                TableName=table_name,
                Key={'animalId': {'S': item['id']}},
                UpdateExpression="SET personality = :personality",
                ExpressionAttributeValues={
                    ':personality': {
                        'M': {
                            'description': {'S': item['old_personality']}
                        }
                    }
                }
            )
            print(f"✓ Fixed {item['id']}")
            success_count += 1
        except Exception as e:
            print(f"✗ Error fixing {item['id']}: {e}")

    print(f"\nFixed {success_count}/{len(items_to_fix)} items.")
    return 0 if success_count == len(items_to_fix) else 1

if __name__ == "__main__":
    sys.exit(fix_personality_field())