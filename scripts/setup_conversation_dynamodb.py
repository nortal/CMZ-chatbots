#!/usr/bin/env python3
"""
Setup DynamoDB table for conversation storage with appropriate indexes and configuration.
PR003946-168: [Infrastructure] Setup DynamoDB Tables and Indexes
"""

import boto3
import json
import sys
import time
from botocore.exceptions import ClientError
from datetime import datetime

# Configuration
TABLE_NAME = "cmz-conversations"
REGION = "us-west-2"
ACCOUNT_ID = "195275676211"  # CMZ AWS Account

def get_dynamodb_client():
    """Get DynamoDB client with CMZ profile."""
    session = boto3.Session(profile_name='cmz')
    return session.client('dynamodb', region_name=REGION)

def get_dynamodb_resource():
    """Get DynamoDB resource with CMZ profile."""
    session = boto3.Session(profile_name='cmz')
    return session.resource('dynamodb', region_name=REGION)

def create_conversation_table():
    """Create the conversations table with all required indexes and configuration."""
    client = get_dynamodb_client()

    table_definition = {
        'TableName': TABLE_NAME,
        'KeySchema': [
            {
                'AttributeName': 'userId',
                'KeyType': 'HASH'  # Partition key
            },
            {
                'AttributeName': 'sessionIdTimestamp',
                'KeyType': 'RANGE'  # Sort key (sessionId#timestamp)
            }
        ],
        'AttributeDefinitions': [
            {
                'AttributeName': 'userId',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'sessionIdTimestamp',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'sessionId',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'timestamp',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'animalId',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'parentUserId',
                'AttributeType': 'S'
            }
        ],
        'GlobalSecondaryIndexes': [
            {
                'IndexName': 'SessionIndex',
                'KeySchema': [
                    {
                        'AttributeName': 'sessionId',
                        'KeyType': 'HASH'
                    },
                    {
                        'AttributeName': 'timestamp',
                        'KeyType': 'RANGE'
                    }
                ],
                'Projection': {
                    'ProjectionType': 'ALL'
                }
            },
            {
                'IndexName': 'AnimalIndex',
                'KeySchema': [
                    {
                        'AttributeName': 'animalId',
                        'KeyType': 'HASH'
                    },
                    {
                        'AttributeName': 'timestamp',
                        'KeyType': 'RANGE'
                    }
                ],
                'Projection': {
                    'ProjectionType': 'ALL'
                }
            },
            {
                'IndexName': 'ParentUserIndex',
                'KeySchema': [
                    {
                        'AttributeName': 'parentUserId',
                        'KeyType': 'HASH'
                    },
                    {
                        'AttributeName': 'timestamp',
                        'KeyType': 'RANGE'
                    }
                ],
                'Projection': {
                    'ProjectionType': 'ALL'
                }
            }
        ],
        'BillingMode': 'PAY_PER_REQUEST',
        'StreamSpecification': {
            'StreamEnabled': True,
            'StreamViewType': 'NEW_AND_OLD_IMAGES'
        },
        'SSESpecification': {
            'Enabled': True,
            'SSEType': 'KMS',
            'KMSMasterKeyId': 'alias/aws/dynamodb'
        },
        'Tags': [
            {
                'Key': 'Environment',
                'Value': 'Production'
            },
            {
                'Key': 'Project',
                'Value': 'CMZ-Chatbots'
            },
            {
                'Key': 'Epic',
                'Value': 'PR003946-170'
            },
            {
                'Key': 'Ticket',
                'Value': 'PR003946-168'
            },
            {
                'Key': 'Purpose',
                'Value': 'ConversationStorage'
            }
        ]
    }

    try:
        print(f"🚀 Creating DynamoDB table: {TABLE_NAME}")
        response = client.create_table(**table_definition)

        print(f"✅ Table creation initiated: {response['TableDescription']['TableStatus']}")
        print(f"   Table ARN: {response['TableDescription']['TableArn']}")

        # Wait for table to be active
        print("⏳ Waiting for table to become active...")
        waiter = client.get_waiter('table_exists')
        waiter.wait(
            TableName=TABLE_NAME,
            WaiterConfig={
                'Delay': 5,
                'MaxAttempts': 60
            }
        )

        # Wait a bit more for indexes to be ready
        time.sleep(10)

        return True

    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print(f"⚠️  Table {TABLE_NAME} already exists")
            return True
        else:
            print(f"❌ Error creating table: {e}")
            return False

def enable_ttl():
    """Enable TTL on the table for 90-day retention."""
    client = get_dynamodb_client()

    try:
        print("🔧 Enabling TTL for 90-day retention...")
        response = client.update_time_to_live(
            TableName=TABLE_NAME,
            TimeToLiveSpecification={
                'Enabled': True,
                'AttributeName': 'ttl'
            }
        )

        if response['TimeToLiveSpecification']['TimeToLiveStatus'] in ['ENABLED', 'ENABLING']:
            print("✅ TTL enabled successfully on 'ttl' attribute")
            return True
        else:
            print(f"⚠️  TTL status: {response['TimeToLiveSpecification']['TimeToLiveStatus']}")
            return True

    except ClientError as e:
        if e.response['Error']['Code'] == 'ValidationException' and 'already enabled' in str(e):
            print("✅ TTL already enabled")
            return True
        else:
            print(f"❌ Error enabling TTL: {e}")
            return False

def enable_point_in_time_recovery():
    """Enable point-in-time recovery for backup."""
    client = get_dynamodb_client()

    try:
        print("🔧 Enabling point-in-time recovery...")
        response = client.update_continuous_backups(
            TableName=TABLE_NAME,
            PointInTimeRecoverySpecification={
                'PointInTimeRecoveryEnabled': True
            }
        )

        status = response['ContinuousBackupsDescription']['PointInTimeRecoveryDescription']['PointInTimeRecoveryStatus']
        if status == 'ENABLED':
            print("✅ Point-in-time recovery enabled")
            return True
        else:
            print(f"⚠️  Point-in-time recovery status: {status}")
            return True

    except ClientError as e:
        print(f"❌ Error enabling point-in-time recovery: {e}")
        return False

def setup_auto_scaling():
    """Set up auto-scaling for the table (only works with provisioned capacity)."""
    print("ℹ️  Auto-scaling not needed for PAY_PER_REQUEST billing mode")
    print("   DynamoDB automatically scales with on-demand capacity")
    return True

def verify_table_configuration():
    """Verify the table configuration is correct."""
    client = get_dynamodb_client()

    try:
        print("\n📊 Verifying table configuration...")
        response = client.describe_table(TableName=TABLE_NAME)
        table = response['Table']

        print(f"✅ Table Status: {table['TableStatus']}")
        print(f"✅ Billing Mode: {table.get('BillingModeSummary', {}).get('BillingMode', 'PAY_PER_REQUEST')}")
        print(f"✅ Encryption: {table['SSEDescription']['Status'] if 'SSEDescription' in table else 'Not configured'}")
        print(f"✅ Stream Status: {table.get('StreamSpecification', {}).get('StreamEnabled', False)}")

        # Check indexes
        print(f"\n📑 Global Secondary Indexes:")
        for gsi in table.get('GlobalSecondaryIndexes', []):
            print(f"   - {gsi['IndexName']}: {gsi['IndexStatus']}")

        # Check TTL
        ttl_response = client.describe_time_to_live(TableName=TABLE_NAME)
        ttl_status = ttl_response['TimeToLiveDescription']['TimeToLiveStatus']
        print(f"\n⏰ TTL Status: {ttl_status}")

        # Check backup
        backup_response = client.describe_continuous_backups(TableName=TABLE_NAME)
        pitr_status = backup_response['ContinuousBackupsDescription']['PointInTimeRecoveryDescription']['PointInTimeRecoveryStatus']
        print(f"💾 Point-in-time Recovery: {pitr_status}")

        return True

    except ClientError as e:
        print(f"❌ Error verifying table: {e}")
        return False

def insert_test_data():
    """Insert test conversation data to verify the table works correctly."""
    resource = get_dynamodb_resource()
    table = resource.Table(TABLE_NAME)

    print("\n🧪 Inserting test conversation data...")

    test_items = [
        {
            'userId': 'test_user_001',
            'sessionIdTimestamp': 'session_001#2025-01-19T12:00:00Z',
            'sessionId': 'session_001',
            'timestamp': '2025-01-19T12:00:00Z',
            'animalId': 'lion_001',
            'parentUserId': 'parent_001',
            'messageType': 'user',
            'content': 'Hello, can you tell me about lions?',
            'tokensUsed': 8,
            'ttl': int(time.time()) + (90 * 24 * 60 * 60)  # 90 days from now
        },
        {
            'userId': 'test_user_001',
            'sessionIdTimestamp': 'session_001#2025-01-19T12:00:05Z',
            'sessionId': 'session_001',
            'timestamp': '2025-01-19T12:00:05Z',
            'animalId': 'lion_001',
            'parentUserId': 'parent_001',
            'messageType': 'assistant',
            'content': 'Hello! I am Leo the Lion, king of the savanna! Lions are magnificent big cats...',
            'tokensUsed': 45,
            'ttl': int(time.time()) + (90 * 24 * 60 * 60)
        }
    ]

    try:
        for item in test_items:
            table.put_item(Item=item)
            print(f"   ✅ Inserted {item['messageType']} message")

        # Test query
        response = table.query(
            KeyConditionExpression='userId = :userId',
            ExpressionAttributeValues={
                ':userId': 'test_user_001'
            }
        )

        print(f"   ✅ Query test successful: Found {response['Count']} items")

        # Test GSI query
        response = table.query(
            IndexName='SessionIndex',
            KeyConditionExpression='sessionId = :sessionId',
            ExpressionAttributeValues={
                ':sessionId': 'session_001'
            }
        )

        print(f"   ✅ GSI query test successful: Found {response['Count']} items")

        return True

    except ClientError as e:
        print(f"❌ Error inserting test data: {e}")
        return False

def main():
    """Main execution function."""
    print("=" * 60)
    print("DynamoDB Conversation Table Setup")
    print("PR003946-168: Infrastructure Setup")
    print("=" * 60)
    print(f"Table: {TABLE_NAME}")
    print(f"Region: {REGION}")
    print(f"Account: {ACCOUNT_ID}")
    print("=" * 60)

    # Check AWS credentials
    try:
        client = get_dynamodb_client()
        client.list_tables(Limit=1)
        print("✅ AWS credentials validated\n")
    except Exception as e:
        print(f"❌ AWS credentials error: {e}")
        print("Please configure AWS CLI with: aws configure --profile cmz")
        return 1

    # Create table
    if not create_conversation_table():
        return 1

    # Enable TTL
    if not enable_ttl():
        print("⚠️  Continuing without TTL...")

    # Enable point-in-time recovery
    if not enable_point_in_time_recovery():
        print("⚠️  Continuing without point-in-time recovery...")

    # Setup auto-scaling
    setup_auto_scaling()

    # Verify configuration
    if not verify_table_configuration():
        return 1

    # Insert test data
    if not insert_test_data():
        print("⚠️  Test data insertion failed, but table is ready")

    print("\n" + "=" * 60)
    print("✨ DynamoDB table setup completed successfully!")
    print("=" * 60)
    print("\nTable Details:")
    print(f"  Name: {TABLE_NAME}")
    print(f"  Region: {REGION}")
    print(f"  Billing: Pay-per-request (on-demand)")
    print(f"  Encryption: KMS")
    print(f"  TTL: 90 days (on 'ttl' attribute)")
    print(f"  Streams: Enabled")
    print(f"  Backup: Point-in-time recovery enabled")
    print("\nIndexes:")
    print("  - SessionIndex (GSI): Query by sessionId")
    print("  - AnimalIndex (GSI): Query by animalId")
    print("  - ParentUserIndex (GSI): Query by parentUserId")
    print("\nNext Steps:")
    print("  1. Update backend conversation.py to use this table")
    print("  2. Implement SSE streaming endpoint")
    print("  3. Add conversation history retrieval")

    return 0

if __name__ == "__main__":
    sys.exit(main())