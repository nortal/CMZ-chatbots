# DynamoDB Table Creation Request: Guardrails System

## Request Summary
We need a new DynamoDB table created to support the configurable guardrails system for ChatGPT integration in the CMZ chatbot platform. The guardrails system is fully implemented and tested (13/17 tests passing), but requires this table for persistent storage.

## Table Specifications

### Basic Configuration
- **Table Name**: `quest-dev-guardrails`
- **Region**: `us-west-2`
- **Billing Mode**: Pay-per-request (on-demand)
- **Environment**: Development (with path to production)

### Primary Key Structure
- **Partition Key**:
  - Name: `guardrailId`
  - Type: String (S)
  - Format: `guardrail_XXXXXXXXXX` (e.g., `guardrail_1234567890`)

### Attributes Schema
```json
{
  "guardrailId": "String (PK)",
  "name": "String",
  "description": "String",
  "category": "String (content|safety|educational|behavioral)",
  "type": "String (ALWAYS|NEVER|ENCOURAGE|DISCOURAGE)",
  "rule": "String",
  "priority": "Number (0-100)",
  "isActive": "Boolean",
  "isGlobal": "Boolean",
  "animalIds": "List<String>",
  "created": {
    "at": "String (ISO 8601)",
    "by": "String"
  },
  "modified": {
    "at": "String (ISO 8601)",
    "by": "String"
  },
  "softDelete": "Boolean"
}
```

### Global Secondary Indexes (GSIs)

#### GSI 1: By Category
- **Index Name**: `category-index`
- **Partition Key**: `category` (String)
- **Sort Key**: `priority` (Number)
- **Projection**: ALL
- **Purpose**: Query guardrails by category, sorted by priority

#### GSI 2: By Active Status
- **Index Name**: `isActive-index`
- **Partition Key**: `isActive` (Boolean)
- **Sort Key**: `priority` (Number)
- **Projection**: ALL
- **Purpose**: Query only active guardrails, sorted by priority

#### GSI 3: By Global Status
- **Index Name**: `isGlobal-index`
- **Partition Key**: `isGlobal` (Boolean)
- **Sort Key**: `priority` (Number)
- **Projection**: ALL
- **Purpose**: Query global vs animal-specific guardrails

## Sample Data for Initial Testing

```json
{
  "guardrailId": "guardrail_global_001",
  "name": "Family Friendly Language",
  "description": "Ensures all responses use age-appropriate language",
  "category": "content",
  "type": "ALWAYS",
  "rule": "Always use language appropriate for all ages",
  "priority": 100,
  "isActive": true,
  "isGlobal": true,
  "animalIds": [],
  "created": {
    "at": "2025-10-09T11:00:00Z",
    "by": "system"
  },
  "modified": {
    "at": "2025-10-09T11:00:00Z",
    "by": "system"
  },
  "softDelete": false
}
```

## IAM Permissions Required

The application service role needs these permissions:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem",
        "dynamodb:Query",
        "dynamodb:Scan"
      ],
      "Resource": [
        "arn:aws:dynamodb:us-west-2:195275676211:table/quest-dev-guardrails",
        "arn:aws:dynamodb:us-west-2:195275676211:table/quest-dev-guardrails/index/*"
      ]
    }
  ]
}
```

## Environment Variables to Set
```bash
GUARDRAILS_DYNAMO_TABLE_NAME=quest-dev-guardrails
GUARDRAILS_DYNAMO_PK_NAME=guardrailId
```

## Business Context
The guardrails system provides configurable safety rules for AI-generated content in the zoo's educational chatbot platform. It supports:
- **Dynamic prompt injection**: Rules are injected into ChatGPT system prompts to guide behavior
- **Content filtering**: Secondary safety net for inappropriate content
- **Priority-based conflict resolution**: When multiple rules apply, highest priority wins
- **Template system**: Pre-built rule packages (Family Friendly, Educational Focus, Safety First)
- **Per-animal customization**: Different animals can have different guardrail configurations

## Current Status
- ✅ API endpoints implemented (9 endpoints)
- ✅ Business logic complete (GuardrailsManager class)
- ✅ Controller routing fixed and verified
- ✅ 13/17 E2E tests passing
- ⏳ Waiting for DynamoDB table creation
- ⏳ 4 tests fail due to missing table

## Testing Validation
Once the table is created, you can validate it's working by:
```bash
# Test the templates endpoint (doesn't need DynamoDB)
curl -X GET "http://localhost:8080/guardrails/templates"

# Test the list endpoint (should return empty array instead of error)
curl -X GET "http://localhost:8080/guardrails"
```

## Timeline
This is blocking the completion of ticket PR003946-178 (Guardrails Validation). Once the table is created, the remaining 4 E2E tests should pass, bringing us to 100% test coverage.

## Questions/Contact
For any questions about the table schema or requirements, please reach out. The implementation code is in:
- `backend/api/src/main/python/openapi_server/impl/guardrails.py`
- Tests: `backend/api/src/main/python/tests/integration/test_chatgpt_integration_epic.py`

## Production Considerations
When moving to production:
1. Consider changing table name to `quest-prod-guardrails`
2. Enable point-in-time recovery for audit trail
3. Set up CloudWatch alarms for throttling
4. Consider DynamoDB auto-scaling if moving from on-demand to provisioned
5. Implement backup strategy for guardrail configurations

---

**Priority**: High - Blocking feature completion
**Requested by**: Keith Charles Stegbauer
**Date**: 2025-10-09
**Ticket Reference**: PR003946-178