#!/usr/bin/env python3
"""
DynamoDB table creation script for CMZ Chatbots safety and personalization features.

Creates 5 new tables required for the conversation safety and personalization system:
1. GuardrailsConfig - Guardrails configuration and templates
2. ContentValidation - Content moderation logs and validation history
3. UserContextProfile - User personalization data and preferences
4. ConversationAnalytics - Conversation analytics and behavior tracking
5. PrivacyAuditLog - Privacy audit logs for COPPA compliance

Usage:
    python create_safety_tables.py [--delete-existing] [--region us-west-2]

Environment Variables:
    AWS_PROFILE - AWS profile to use (default: cmz)
    AWS_REGION - AWS region (default: us-west-2)
"""

import boto3
import json
import sys
import argparse
import time
from typing import Dict, Any, List
from botocore.exceptions import ClientError, BotoCoreError


class SafetyTablesCreator:
    """Creates and manages DynamoDB tables for safety and personalization features."""

    def __init__(self, region: str = "us-west-2"):
        """Initialize DynamoDB client for table creation."""
        self.region = region
        self.dynamodb = boto3.client('dynamodb', region_name=region)

        # Table configurations for all 5 safety tables
        self.table_configs = {
            'GuardrailsConfig': {
                'TableName': 'quest-dev-guardrails-config',
                'KeySchema': [
                    {'AttributeName': 'configId', 'KeyType': 'HASH'}  # Partition key
                ],
                'AttributeDefinitions': [
                    {'AttributeName': 'configId', 'AttributeType': 'S'},
                    {'AttributeName': 'animalId', 'AttributeType': 'S'},
                    {'AttributeName': 'templateId', 'AttributeType': 'S'}
                ],
                'GlobalSecondaryIndexes': [
                    {
                        'IndexName': 'AnimalIndex',
                        'KeySchema': [{'AttributeName': 'animalId', 'KeyType': 'HASH'}],
                        'Projection': {'ProjectionType': 'ALL'}
                    },
                    {
                        'IndexName': 'TemplateIndex',
                        'KeySchema': [{'AttributeName': 'templateId', 'KeyType': 'HASH'}],
                        'Projection': {'ProjectionType': 'ALL'}
                    }
                ]
            },

            'ContentValidation': {
                'TableName': 'quest-dev-content-validation',
                'KeySchema': [
                    {'AttributeName': 'validationId', 'KeyType': 'HASH'}  # Partition key
                ],
                'AttributeDefinitions': [
                    {'AttributeName': 'validationId', 'AttributeType': 'S'},
                    {'AttributeName': 'sessionId', 'AttributeType': 'S'},
                    {'AttributeName': 'timestamp', 'AttributeType': 'S'},
                    {'AttributeName': 'userId', 'AttributeType': 'S'}
                ],
                'GlobalSecondaryIndexes': [
                    {
                        'IndexName': 'SessionIndex',
                        'KeySchema': [
                            {'AttributeName': 'sessionId', 'KeyType': 'HASH'},
                            {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
                        ],
                        'Projection': {'ProjectionType': 'ALL'}
                    },
                    {
                        'IndexName': 'UserIndex',
                        'KeySchema': [
                            {'AttributeName': 'userId', 'KeyType': 'HASH'},
                            {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
                        ],
                        'Projection': {'ProjectionType': 'ALL'}
                    }
                ]
            },

            'UserContextProfile': {
                'TableName': 'quest-dev-user-context',
                'KeySchema': [
                    {'AttributeName': 'userId', 'KeyType': 'HASH'}  # Partition key
                ],
                'AttributeDefinitions': [
                    {'AttributeName': 'userId', 'AttributeType': 'S'},
                    {'AttributeName': 'lastUpdated', 'AttributeType': 'S'},
                    {'AttributeName': 'parentId', 'AttributeType': 'S'}
                ],
                'GlobalSecondaryIndexes': [
                    {
                        'IndexName': 'ParentIndex',
                        'KeySchema': [
                            {'AttributeName': 'parentId', 'KeyType': 'HASH'},
                            {'AttributeName': 'lastUpdated', 'KeyType': 'RANGE'}
                        ],
                        'Projection': {'ProjectionType': 'ALL'}
                    }
                ]
            },

            'ConversationAnalytics': {
                'TableName': 'quest-dev-conversation-analytics',
                'KeySchema': [
                    {'AttributeName': 'analyticsId', 'KeyType': 'HASH'}  # Partition key
                ],
                'AttributeDefinitions': [
                    {'AttributeName': 'analyticsId', 'AttributeType': 'S'},
                    {'AttributeName': 'sessionId', 'AttributeType': 'S'},
                    {'AttributeName': 'userId', 'AttributeType': 'S'},
                    {'AttributeName': 'timestamp', 'AttributeType': 'S'},
                    {'AttributeName': 'animalId', 'AttributeType': 'S'}
                ],
                'GlobalSecondaryIndexes': [
                    {
                        'IndexName': 'SessionIndex',
                        'KeySchema': [{'AttributeName': 'sessionId', 'KeyType': 'HASH'}],
                        'Projection': {'ProjectionType': 'ALL'}
                    },
                    {
                        'IndexName': 'UserIndex',
                        'KeySchema': [
                            {'AttributeName': 'userId', 'KeyType': 'HASH'},
                            {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
                        ],
                        'Projection': {'ProjectionType': 'ALL'}
                    },
                    {
                        'IndexName': 'AnimalIndex',
                        'KeySchema': [
                            {'AttributeName': 'animalId', 'KeyType': 'HASH'},
                            {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
                        ],
                        'Projection': {'ProjectionType': 'ALL'}
                    }
                ]
            },

            'PrivacyAuditLog': {
                'TableName': 'quest-dev-privacy-audit',
                'KeySchema': [
                    {'AttributeName': 'auditId', 'KeyType': 'HASH'}  # Partition key
                ],
                'AttributeDefinitions': [
                    {'AttributeName': 'auditId', 'AttributeType': 'S'},
                    {'AttributeName': 'userId', 'AttributeType': 'S'},
                    {'AttributeName': 'timestamp', 'AttributeType': 'S'},
                    {'AttributeName': 'parentId', 'AttributeType': 'S'},
                    {'AttributeName': 'actionType', 'AttributeType': 'S'}
                ],
                'GlobalSecondaryIndexes': [
                    {
                        'IndexName': 'UserIndex',
                        'KeySchema': [
                            {'AttributeName': 'userId', 'KeyType': 'HASH'},
                            {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
                        ],
                        'Projection': {'ProjectionType': 'ALL'}
                    },
                    {
                        'IndexName': 'ParentIndex',
                        'KeySchema': [
                            {'AttributeName': 'parentId', 'KeyType': 'HASH'},
                            {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
                        ],
                        'Projection': {'ProjectionType': 'ALL'}
                    },
                    {
                        'IndexName': 'ActionTypeIndex',
                        'KeySchema': [
                            {'AttributeName': 'actionType', 'KeyType': 'HASH'},
                            {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
                        ],
                        'Projection': {'ProjectionType': 'ALL'}
                    }
                ]
            }
        }

    def check_table_exists(self, table_name: str) -> bool:
        """Check if a DynamoDB table exists."""
        try:
            self.dynamodb.describe_table(TableName=table_name)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                return False
            else:
                raise

    def delete_table(self, table_name: str) -> bool:
        """Delete a DynamoDB table if it exists."""
        try:
            if self.check_table_exists(table_name):
                print(f"🗑️  Deleting existing table: {table_name}")
                self.dynamodb.delete_table(TableName=table_name)

                # Wait for table deletion
                waiter = self.dynamodb.get_waiter('table_not_exists')
                waiter.wait(TableName=table_name, WaiterConfig={'Delay': 5, 'MaxAttempts': 20})
                print(f"✅ Table {table_name} deleted successfully")
                return True
            return False
        except ClientError as e:
            print(f"❌ Error deleting table {table_name}: {e}")
            return False

    def create_table(self, table_config: Dict[str, Any]) -> bool:
        """Create a single DynamoDB table with proper configuration."""
        table_name = table_config['TableName']

        try:
            print(f"🏗️  Creating table: {table_name}")

            # Base table configuration with pay-per-request billing
            create_params = {
                'TableName': table_name,
                'KeySchema': table_config['KeySchema'],
                'AttributeDefinitions': table_config['AttributeDefinitions'],
                'BillingMode': 'PAY_PER_REQUEST',  # Cost-effective for CMZ usage patterns
                'Tags': [
                    {'Key': 'Project', 'Value': 'CMZ-Chatbots'},
                    {'Key': 'Environment', 'Value': 'Development'},
                    {'Key': 'Feature', 'Value': 'Safety-Personalization'},
                    {'Key': 'CreatedBy', 'Value': 'create_safety_tables.py'}
                ]
            }

            # Add Global Secondary Indexes if defined
            if 'GlobalSecondaryIndexes' in table_config:
                # Configure GSIs with pay-per-request billing
                gsis = []
                for gsi in table_config['GlobalSecondaryIndexes']:
                    gsi_config = {
                        'IndexName': gsi['IndexName'],
                        'KeySchema': gsi['KeySchema'],
                        'Projection': gsi['Projection']
                    }
                    gsis.append(gsi_config)

                create_params['GlobalSecondaryIndexes'] = gsis

            # Create the table
            response = self.dynamodb.create_table(**create_params)

            # Wait for table to become active
            print(f"⏳ Waiting for table {table_name} to become active...")
            waiter = self.dynamodb.get_waiter('table_exists')
            waiter.wait(TableName=table_name, WaiterConfig={'Delay': 10, 'MaxAttempts': 30})

            print(f"✅ Table {table_name} created successfully")
            return True

        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceInUseException':
                print(f"⚠️  Table {table_name} already exists")
                return True
            else:
                print(f"❌ Error creating table {table_name}: {e}")
                return False
        except Exception as e:
            print(f"❌ Unexpected error creating table {table_name}: {e}")
            return False

    def verify_table_structure(self, table_name: str) -> bool:
        """Verify that a table has the expected structure."""
        try:
            response = self.dynamodb.describe_table(TableName=table_name)
            table_desc = response['Table']

            print(f"📋 Table {table_name} structure:")
            print(f"   Status: {table_desc['TableStatus']}")
            print(f"   Billing Mode: {table_desc.get('BillingModeSummary', {}).get('BillingMode', 'PROVISIONED')}")

            # Show primary key
            key_schema = table_desc['KeySchema']
            for key in key_schema:
                key_type = "Partition" if key['KeyType'] == 'HASH' else "Sort"
                print(f"   {key_type} Key: {key['AttributeName']}")

            # Show GSIs
            gsis = table_desc.get('GlobalSecondaryIndexes', [])
            if gsis:
                print(f"   Global Secondary Indexes: {len(gsis)}")
                for gsi in gsis:
                    print(f"     - {gsi['IndexName']}")

            return True

        except ClientError as e:
            print(f"❌ Error verifying table {table_name}: {e}")
            return False

    def create_all_tables(self, delete_existing: bool = False) -> bool:
        """Create all safety and personalization tables."""
        print("🚀 Starting DynamoDB safety tables creation process")
        print(f"📍 Region: {self.region}")

        success_count = 0
        total_tables = len(self.table_configs)

        for table_type, config in self.table_configs.items():
            table_name = config['TableName']
            print(f"\n{'='*60}")
            print(f"Processing {table_type} ({table_name})")
            print(f"{'='*60}")

            # Delete existing table if requested
            if delete_existing:
                self.delete_table(table_name)
                time.sleep(2)  # Brief pause between delete and create

            # Create the table
            if self.create_table(config):
                if self.verify_table_structure(table_name):
                    success_count += 1
                    print(f"🎉 {table_type} setup completed successfully")
                else:
                    print(f"⚠️  {table_type} created but verification failed")
            else:
                print(f"❌ Failed to create {table_type}")

        print(f"\n{'='*60}")
        print(f"📊 SUMMARY")
        print(f"{'='*60}")
        print(f"Tables processed: {total_tables}")
        print(f"Successfully created: {success_count}")
        print(f"Failed: {total_tables - success_count}")

        if success_count == total_tables:
            print("🎉 All safety tables created successfully!")
            print("\n📋 Next Steps:")
            print("1. Run T008: Implement OpenAI integration utility")
            print("2. Run T009: Create base DynamoDB utilities for new tables")
            print("3. Run T010: Implement error handling patterns for safety violations")
            return True
        else:
            print("⚠️  Some tables failed to create. Check errors above.")
            return False


def main():
    """Main function to handle command line arguments and execute table creation."""
    parser = argparse.ArgumentParser(
        description="Create DynamoDB tables for CMZ Chatbots safety and personalization features"
    )
    parser.add_argument(
        '--delete-existing',
        action='store_true',
        help='Delete existing tables before creating new ones'
    )
    parser.add_argument(
        '--region',
        default='us-west-2',
        help='AWS region for table creation (default: us-west-2)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be created without actually creating tables'
    )

    args = parser.parse_args()

    if args.dry_run:
        print("🔍 DRY RUN MODE - No tables will be created")
        creator = SafetyTablesCreator(region=args.region)
        print(f"Would create {len(creator.table_configs)} tables:")
        for table_type, config in creator.table_configs.items():
            print(f"  - {table_type}: {config['TableName']}")
        return True

    try:
        creator = SafetyTablesCreator(region=args.region)
        success = creator.create_all_tables(delete_existing=args.delete_existing)
        sys.exit(0 if success else 1)

    except BotoCoreError as e:
        print(f"❌ AWS configuration error: {e}")
        print("💡 Make sure AWS credentials are configured (AWS_PROFILE=cmz)")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()