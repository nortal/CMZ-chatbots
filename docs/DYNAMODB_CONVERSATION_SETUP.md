# DynamoDB Conversation Table Setup Guide

## Overview
This document provides instructions for deploying and managing the DynamoDB table for conversation storage in the CMZ Chat system (PR003946-168).

## Table Architecture

### Primary Table: `cmz-conversations`
- **Partition Key**: `userId` (String) - User who initiated conversation
- **Sort Key**: `sessionIdTimestamp` (String) - Composite key: `sessionId#timestamp`

### Global Secondary Indexes (GSIs)
1. **SessionIndex**: Query conversations by session
   - Partition Key: `sessionId` (String)
   - Sort Key: `timestamp` (String)

2. **AnimalIndex**: Query conversations by animal
   - Partition Key: `animalId` (String)
   - Sort Key: `timestamp` (String)

3. **ParentUserIndex**: Query conversations for family management
   - Partition Key: `parentUserId` (String)
   - Sort Key: `timestamp` (String)

## Deployment Options

### Option 1: CloudFormation (Recommended)
Use this method for production deployments with full AWS resource management.

```bash
# Deploy the stack
aws cloudformation create-stack \
  --stack-name cmz-conversations-table \
  --template-body file://infrastructure/cloudformation/conversation-dynamodb.yaml \
  --parameters ParameterKey=Environment,ParameterValue=production \
  --profile cmz \
  --region us-west-2

# Monitor deployment status
aws cloudformation describe-stacks \
  --stack-name cmz-conversations-table \
  --profile cmz \
  --region us-west-2 \
  --query 'Stacks[0].StackStatus'

# Get outputs (table name, ARNs)
aws cloudformation describe-stacks \
  --stack-name cmz-conversations-table \
  --profile cmz \
  --region us-west-2 \
  --query 'Stacks[0].Outputs'
```

### Option 2: Python Script (Development)
Use this method for local development with appropriate AWS permissions.

```bash
# Ensure AWS credentials are configured
aws configure --profile cmz

# Run the setup script
cd scripts
python setup_conversation_dynamodb.py

# Script will:
# 1. Create table with all indexes
# 2. Enable TTL for 90-day retention
# 3. Enable point-in-time recovery
# 4. Insert test data
# 5. Verify configuration
```

## Table Configuration

### Billing Mode
- **Type**: PAY_PER_REQUEST (On-Demand)
- **Rationale**: Automatic scaling without capacity management
- **Cost**: ~$0.25 per million read/write requests

### Data Retention
- **TTL Attribute**: `ttl`
- **Retention Period**: 90 days
- **Implementation**: Unix timestamp for automatic deletion

### Security
- **Encryption**: AWS KMS with `alias/aws/dynamodb`
- **Point-in-Time Recovery**: Enabled
- **Backup Window**: 35 days of continuous backups

### Capacity & Performance
- **Auto-scaling**: Built-in with on-demand mode
- **Stream**: Enabled for change capture
- **Stream View Type**: NEW_AND_OLD_IMAGES

## Data Model

### Conversation Message Structure
```json
{
  "userId": "student_001",
  "sessionIdTimestamp": "session_001#2025-01-19T12:00:00Z",
  "sessionId": "session_001",
  "timestamp": "2025-01-19T12:00:00Z",
  "animalId": "lion_001",
  "parentUserId": "parent_001",
  "messageType": "user|assistant",
  "content": "Message content here",
  "tokensUsed": 45,
  "ttl": 1747699200
}
```

### Access Patterns
1. **User's Conversations**: Query by `userId`
2. **Session Messages**: Query SessionIndex by `sessionId`
3. **Animal Interactions**: Query AnimalIndex by `animalId`
4. **Family Oversight**: Query ParentUserIndex by `parentUserId`

## Environment Variables

Add these to your backend configuration:

```bash
# DynamoDB Configuration
export CONVERSATION_TABLE_NAME=cmz-conversations
export CONVERSATION_TABLE_REGION=us-west-2
export CONVERSATION_TTL_DAYS=90

# For local development with DynamoDB Local
export DYNAMODB_ENDPOINT_URL=http://localhost:8000  # Optional
```

## Monitoring & Operations

### CloudWatch Metrics
Monitor these key metrics:
- `ConsumedReadCapacityUnits`
- `ConsumedWriteCapacityUnits`
- `SystemErrors`
- `ThrottledRequests`

### Query Examples

```python
# Query user's conversations
response = table.query(
    KeyConditionExpression='userId = :userId',
    ExpressionAttributeValues={':userId': 'student_001'}
)

# Query session messages
response = table.query(
    IndexName='SessionIndex',
    KeyConditionExpression='sessionId = :sessionId',
    ExpressionAttributeValues={':sessionId': 'session_001'}
)

# Query with pagination
response = table.query(
    KeyConditionExpression='userId = :userId',
    ExpressionAttributeValues={':userId': 'student_001'},
    Limit=20,
    ExclusiveStartKey=last_evaluated_key  # From previous response
)
```

## Troubleshooting

### Common Issues

1. **Permission Denied**: Ensure IAM user has `dynamodb:CreateTable` permission
   - Solution: Use CloudFormation deployment or request admin assistance

2. **Table Already Exists**: Table name conflicts with existing resource
   - Solution: Delete existing table or use different environment suffix

3. **TTL Not Working**: TTL attribute not properly configured
   - Solution: Verify `ttl` attribute contains Unix timestamp in seconds

4. **Query Throttling**: Exceeding provisioned capacity
   - Solution: On-demand mode handles this automatically

## Cost Estimation

Based on expected usage:
- **Storage**: ~$0.25/GB/month
- **Read Requests**: $0.25 per million
- **Write Requests**: $1.25 per million
- **Streams**: $0.02 per 100,000 records
- **Backup**: $0.10/GB/month

Estimated monthly cost: $2-5 for moderate usage

## Next Steps

After table deployment:
1. Update backend configuration with table name
2. Implement conversation storage in `impl/conversation.py`
3. Add SSE streaming endpoint
4. Implement history retrieval endpoints
5. Create frontend chat history pages

## References

- [DynamoDB Best Practices](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html)
- [CloudFormation DynamoDB Resource](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-dynamodb-table.html)
- [DynamoDB TTL](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/TTL.html)
- [Global Secondary Indexes](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GSI.html)