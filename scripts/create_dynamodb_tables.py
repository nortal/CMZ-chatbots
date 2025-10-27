#!/usr/bin/env python3
"""
Create DynamoDB tables for Animal Assistant Management System.
Based on data-model.md specifications following quest-dev-* naming convention.
"""
import boto3
import sys
from botocore.exceptions import ClientError

def create_assistant_table(dynamodb):
    """Create quest-dev-animal-assistant table."""
    table_name = "quest-dev-animal-assistant"

    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {'AttributeName': 'assistantId', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'assistantId', 'AttributeType': 'S'},
                {'AttributeName': 'animalId', 'AttributeType': 'S'},
                {'AttributeName': 'personalityId', 'AttributeType': 'S'},
                {'AttributeName': 'guardrailId', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'AnimalIndex',
                    'KeySchema': [{'AttributeName': 'animalId', 'KeyType': 'HASH'}],
                    'Projection': {'ProjectionType': 'ALL'}
                },
                {
                    'IndexName': 'PersonalityIndex',
                    'KeySchema': [{'AttributeName': 'personalityId', 'KeyType': 'HASH'}],
                    'Projection': {'ProjectionType': 'ALL'},
                },
                {
                    'IndexName': 'GuardrailIndex',
                    'KeySchema': [{'AttributeName': 'guardrailId', 'KeyType': 'HASH'}],
                    'Projection': {'ProjectionType': 'ALL'},
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        print(f"✅ Created table: {table_name}")
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"⚠️  Table {table_name} already exists")
            return True
        else:
            print(f"❌ Error creating {table_name}: {e}")
            return False

def create_personality_table(dynamodb):
    """Create quest-dev-personality table."""
    table_name = "quest-dev-personality"

    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {'AttributeName': 'personalityId', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'personalityId', 'AttributeType': 'S'},
                {'AttributeName': 'name', 'AttributeType': 'S'},
                {'AttributeName': 'animalType', 'AttributeType': 'S'},
                {'AttributeName': 'isTemplate', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'NameIndex',
                    'KeySchema': [{'AttributeName': 'name', 'KeyType': 'HASH'}],
                    'Projection': {'ProjectionType': 'ALL'},
                },
                {
                    'IndexName': 'AnimalTypeIndex',
                    'KeySchema': [{'AttributeName': 'animalType', 'KeyType': 'HASH'}],
                    'Projection': {'ProjectionType': 'ALL'},
                },
                {
                    'IndexName': 'TemplateIndex',
                    'KeySchema': [{'AttributeName': 'isTemplate', 'KeyType': 'HASH'}],
                    'Projection': {'ProjectionType': 'ALL'},
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        print(f"✅ Created table: {table_name}")
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"⚠️  Table {table_name} already exists")
            return True
        else:
            print(f"❌ Error creating {table_name}: {e}")
            return False

def create_guardrail_table(dynamodb):
    """Create quest-dev-guardrail table."""
    table_name = "quest-dev-guardrail"

    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {'AttributeName': 'guardrailId', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'guardrailId', 'AttributeType': 'S'},
                {'AttributeName': 'name', 'AttributeType': 'S'},
                {'AttributeName': 'category', 'AttributeType': 'S'},
                {'AttributeName': 'isDefault', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'NameIndex',
                    'KeySchema': [{'AttributeName': 'name', 'KeyType': 'HASH'}],
                    'Projection': {'ProjectionType': 'ALL'},
                },
                {
                    'IndexName': 'CategoryIndex',
                    'KeySchema': [{'AttributeName': 'category', 'KeyType': 'HASH'}],
                    'Projection': {'ProjectionType': 'ALL'},
                },
                {
                    'IndexName': 'DefaultIndex',
                    'KeySchema': [{'AttributeName': 'isDefault', 'KeyType': 'HASH'}],
                    'Projection': {'ProjectionType': 'ALL'},
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        print(f"✅ Created table: {table_name}")
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"⚠️  Table {table_name} already exists")
            return True
        else:
            print(f"❌ Error creating {table_name}: {e}")
            return False

def create_knowledge_file_table(dynamodb):
    """Create quest-dev-knowledge-file table."""
    table_name = "quest-dev-knowledge-file"

    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {'AttributeName': 'fileId', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'fileId', 'AttributeType': 'S'},
                {'AttributeName': 'assistantId', 'AttributeType': 'S'},
                {'AttributeName': 'status', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'AssistantIndex',
                    'KeySchema': [{'AttributeName': 'assistantId', 'KeyType': 'HASH'}],
                    'Projection': {'ProjectionType': 'ALL'},
                },
                {
                    'IndexName': 'StatusIndex',
                    'KeySchema': [{'AttributeName': 'status', 'KeyType': 'HASH'}],
                    'Projection': {'ProjectionType': 'ALL'},
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        print(f"✅ Created table: {table_name}")
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"⚠️  Table {table_name} already exists")
            return True
        else:
            print(f"❌ Error creating {table_name}: {e}")
            return False

def create_sandbox_assistant_table(dynamodb):
    """Create quest-dev-sandbox-assistant table with TTL."""
    table_name = "quest-dev-sandbox-assistant"

    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {'AttributeName': 'sandboxId', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'sandboxId', 'AttributeType': 'S'},
                {'AttributeName': 'createdBy', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'CreatedByIndex',
                    'KeySchema': [{'AttributeName': 'createdBy', 'KeyType': 'HASH'}],
                    'Projection': {'ProjectionType': 'ALL'},
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )

        # Enable TTL on expiresAt field (wait for table to be active first)
        print(f"⏳ Waiting for table {table_name} to be active before enabling TTL...")
        table.wait_until_exists()

        dynamodb.meta.client.update_time_to_live(
            TableName=table_name,
            TimeToLiveSpecification={
                'AttributeName': 'expiresAt',
                'Enabled': True
            }
        )

        print(f"✅ Created table with TTL: {table_name}")
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"⚠️  Table {table_name} already exists")
            return True
        else:
            print(f"❌ Error creating {table_name}: {e}")
            return False

def main():
    """Create all DynamoDB tables for Animal Assistant Management."""
    print("🚀 Creating DynamoDB tables for Animal Assistant Management...")

    # Initialize DynamoDB resource
    dynamodb = boto3.resource('dynamodb', region_name='us-west-2')

    # Create all tables
    tables_created = 0
    tables = [
        ("Animal Assistant", create_assistant_table),
        ("Personality", create_personality_table),
        ("Guardrail", create_guardrail_table),
        ("Knowledge File", create_knowledge_file_table),
        ("Sandbox Assistant", create_sandbox_assistant_table)
    ]

    for table_name, create_func in tables:
        print(f"\n📋 Creating {table_name} table...")
        if create_func(dynamodb):
            tables_created += 1

    print(f"\n🎉 Table creation complete: {tables_created}/{len(tables)} tables ready")

    if tables_created == len(tables):
        print("✅ All DynamoDB tables created successfully!")
        return 0
    else:
        print("⚠️  Some tables had issues - check output above")
        return 1

if __name__ == "__main__":
    sys.exit(main())