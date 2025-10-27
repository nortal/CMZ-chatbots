#!/usr/bin/env python3
"""
Create S3 buckets for Animal Assistant Management System knowledge base storage.
Creates production and quarantine buckets with appropriate security configuration.
"""
import boto3
import sys
import json
from botocore.exceptions import ClientError

def create_bucket_with_policy(s3_client, bucket_name, bucket_type="production"):
    """Create S3 bucket with appropriate security policy."""

    try:
        # Create bucket with appropriate location constraint for us-west-2
        s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': 'us-west-2'}
        )
        print(f"✅ Created bucket: {bucket_name}")

        # Block public access
        s3_client.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': True,
                'IgnorePublicAcls': True,
                'BlockPublicPolicy': True,
                'RestrictPublicBuckets': True
            }
        )
        print(f"🔒 Enabled public access block for: {bucket_name}")

        # Enable versioning
        s3_client.put_bucket_versioning(
            Bucket=bucket_name,
            VersioningConfiguration={'Status': 'Enabled'}
        )
        print(f"📝 Enabled versioning for: {bucket_name}")

        # Set lifecycle policy based on bucket type
        if bucket_type == "quarantine":
            lifecycle_policy = {
                'Rules': [
                    {
                        'ID': 'QuarantineCleanup',
                        'Status': 'Enabled',
                        'Filter': {},
                        'Expiration': {'Days': 7},  # Delete quarantine files after 7 days
                        'NoncurrentVersionExpiration': {'NoncurrentDays': 1}
                    }
                ]
            }
        else:
            lifecycle_policy = {
                'Rules': [
                    {
                        'ID': 'ProductionCleanup',
                        'Status': 'Enabled',
                        'Filter': {},
                        'NoncurrentVersionExpiration': {'NoncurrentDays': 30}  # Keep old versions for 30 days
                    }
                ]
            }

        s3_client.put_bucket_lifecycle_configuration(
            Bucket=bucket_name,
            LifecycleConfiguration=lifecycle_policy
        )
        print(f"♻️  Set lifecycle policy for: {bucket_name}")

        # Set server-side encryption
        s3_client.put_bucket_encryption(
            Bucket=bucket_name,
            ServerSideEncryptionConfiguration={
                'Rules': [
                    {
                        'ApplyServerSideEncryptionByDefault': {
                            'SSEAlgorithm': 'AES256'
                        },
                        'BucketKeyEnabled': True
                    }
                ]
            }
        )
        print(f"🔐 Enabled server-side encryption for: {bucket_name}")

        return True

    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'BucketAlreadyExists':
            print(f"⚠️  Bucket {bucket_name} already exists")
            return True
        elif error_code == 'BucketAlreadyOwnedByYou':
            print(f"⚠️  You already own bucket {bucket_name}")
            return True
        else:
            print(f"❌ Error creating bucket {bucket_name}: {e}")
            return False

def main():
    """Create S3 buckets for knowledge base document storage."""
    print("🚀 Creating S3 buckets for Animal Assistant knowledge base...")

    # Initialize S3 client
    s3_client = boto3.client('s3', region_name='us-west-2')

    # Define bucket names
    buckets = [
        ("cmz-knowledge-base-production", "production"),
        ("cmz-knowledge-base-quarantine", "quarantine")
    ]

    buckets_created = 0

    for bucket_name, bucket_type in buckets:
        print(f"\n📦 Creating {bucket_type} bucket: {bucket_name}")
        if create_bucket_with_policy(s3_client, bucket_name, bucket_type):
            buckets_created += 1

    print(f"\n🎉 Bucket creation complete: {buckets_created}/{len(buckets)} buckets ready")

    if buckets_created == len(buckets):
        print("\n✅ All S3 buckets created successfully!")
        print("\n📋 Next steps:")
        print("   1. Configure AWS GuardDuty for malware protection")
        print("   2. Set up Step Functions for document processing pipeline")
        print("   3. Configure IAM roles for Lambda access")
        return 0
    else:
        print("\n⚠️  Some buckets had issues - check output above")
        return 1

if __name__ == "__main__":
    sys.exit(main())