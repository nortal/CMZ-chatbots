# Quickstart Guide: Animal Assistant Management System

**Feature**: 003-animal-assistant-mgmt
**Date**: 2025-10-23
**Audience**: Developers implementing the Animal Assistant Management System

## Overview

This guide provides step-by-step instructions for implementing the CMZ Animal Assistant Management System, which enables zoo staff to create, test, and manage AI-powered digital ambassadors for zoo animals.

## Prerequisites

Before starting implementation, ensure you have:

- ✅ Existing CMZ chatbot platform running
- ✅ AWS account with DynamoDB and S3 access
- ✅ OpenAI API key for conversational AI
- ✅ Python 3.11+ development environment
- ✅ Docker for containerization
- ✅ Basic familiarity with CMZ OpenAPI-first development patterns

## Implementation Phases

### Phase 1: Foundation Setup (Week 1-2)

#### 1.1 DynamoDB Tables Creation

Create the required DynamoDB tables following CMZ naming conventions:

```bash
# Using AWS CLI or MCP DynamoDB server
aws dynamodb create-table \
  --table-name quest-dev-animal-assistant \
  --attribute-definitions \
    AttributeName=assistantId,AttributeType=S \
    AttributeName=animalId,AttributeType=S \
  --key-schema \
    AttributeName=assistantId,KeyType=HASH \
  --global-secondary-indexes \
    IndexName=AnimalIndex,KeySchema=AttributeName=animalId,KeyType=HASH,Projection=ProjectionType=ALL,ProvisionedThroughput=ReadCapacityUnits=1,WriteCapacityUnits=1 \
  --billing-mode PAY_PER_REQUEST
```

**Tables to Create**:
- `quest-dev-animal-assistant`
- `quest-dev-personality`
- `quest-dev-guardrail`
- `quest-dev-knowledge-file`
- `quest-dev-sandbox-assistant` (with TTL on `expiresAt` field)

#### 1.2 S3 Buckets Configuration

Set up S3 buckets for knowledge base document storage:

```bash
# Knowledge base documents storage
aws s3 mb s3://cmz-knowledge-base-production
aws s3 mb s3://cmz-knowledge-base-quarantine

# Configure lifecycle policies and access controls
```

#### 1.3 OpenAPI Specification Extension

Extend the existing `backend/api/openapi_spec.yaml` with new endpoints:

1. Copy content from `contracts/openapi-extension.yaml`
2. Merge into existing spec following CMZ patterns
3. Run `make post-generate` to generate controllers and models
4. Verify all new endpoints have proper `operationId` fields

### Phase 2: Core Implementation (Week 3-6)

#### 2.1 Implementation Modules

Create the core implementation modules in `backend/api/src/main/python/openapi_server/impl/`:

**assistants.py** - Animal assistant CRUD operations:
```python
from .utils.dynamo import table, to_ddb, from_ddb, now_iso
from .utils.prompt_merger import merge_personality_guardrail

def create_assistant(animal_id, personality_id, guardrail_id, knowledge_file_ids=None):
    """Create new animal assistant with merged prompt"""
    # Implementation following CMZ patterns

def get_assistant(assistant_id):
    """Retrieve assistant by ID"""
    # Implementation with error handling

def update_assistant(assistant_id, updates):
    """Update assistant configuration and regenerate prompt"""
    # Implementation with validation
```

**sandbox.py** - Sandbox management with TTL:
```python
def create_sandbox(personality_id, guardrail_id, created_by, animal_id=None):
    """Create temporary sandbox assistant (30-min TTL)"""
    # Implementation with DynamoDB TTL

def promote_sandbox(sandbox_id, animal_id):
    """Promote sandbox to live assistant"""
    # Implementation with validation and cleanup
```

**personalities.py** - Personality management:
```python
def create_personality(name, personality_text, **attributes):
    """Create reusable personality configuration"""
    # Implementation with uniqueness validation

def list_personalities(filters=None):
    """List personalities with optional filtering"""
    # Implementation with GSI queries
```

**guardrails.py** - Guardrail management:
```python
def create_guardrail(name, guardrail_text, category, **attributes):
    """Create safety guardrail configuration"""
    # Implementation with category defaults

def validate_guardrail_precedence(personality_text, guardrail_text):
    """Validate guardrail override behavior"""
    # Implementation of conflict resolution
```

**knowledge_base.py** - Document processing:
```python
def upload_document(assistant_id, file_data, original_name):
    """Upload and process educational document"""
    # Implementation with S3 upload and async processing

def process_document_async(file_id):
    """Async document processing pipeline"""
    # Implementation with Step Functions integration
```

#### 2.2 Utility Modules

**utils/openai_integration.py** - OpenAI API wrapper:
```python
import openai
from typing import Iterator

class OpenAIClient:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    def chat_stream(self, system_prompt: str, user_message: str) -> Iterator[str]:
        """Stream chat response with error handling"""
        # Implementation with rate limiting and fallback models

    def validate_content(self, text: str) -> dict:
        """Content moderation using OpenAI"""
        # Implementation with safety validation
```

**utils/prompt_merger.py** - Prompt composition:
```python
def merge_personality_guardrail(personality_text: str, guardrail_text: str) -> str:
    """Merge personality and guardrail with precedence rules"""
    return f"""You are a zoo animal assistant with the following characteristics:

PERSONALITY:
{personality_text}

SAFETY GUARDRAILS (ALWAYS FOLLOW THESE RULES):
{guardrail_text}

Remember: Safety guardrails always take precedence over personality traits."""
```

#### 2.3 Generated Controller Integration

Ensure generated controllers properly route to implementation modules:

```python
# In generated animal_assistant_controller.py
from openapi_server.impl import assistants

def assistant_create_post(body):
    """Create new assistant"""
    return assistants.handle_create_assistant(body)
```

### Phase 3: Frontend Integration (Week 7-8)

#### 3.1 React Components

Create assistant management UI components in `frontend/src/components/assistants/`:

**AssistantForm.tsx** - Create/edit assistant form:
```typescript
interface AssistantFormProps {
  animalId?: string;
  onSubmit: (data: CreateAssistantRequest) => void;
}

export const AssistantForm: React.FC<AssistantFormProps> = ({ animalId, onSubmit }) => {
  // Implementation with personality/guardrail selection
  // Form validation and submission handling
};
```

**SandboxTester.tsx** - Sandbox testing interface:
```typescript
export const SandboxTester: React.FC = () => {
  // Implementation with chat interface
  // Real-time conversation testing
  // Promote/discard actions
};
```

**KnowledgeBaseUpload.tsx** - File upload component:
```typescript
export const KnowledgeBaseUpload: React.FC<{ assistantId: string }> = ({ assistantId }) => {
  // Implementation with drag-drop upload
  // Progress tracking and validation
  // File management interface
};
```

#### 3.2 API Services

Create TypeScript API clients in `frontend/src/services/`:

**AssistantService.ts**:
```typescript
import { apiClient } from './base';
import { AssistantResponse, CreateAssistantRequest } from '../types/AssistantTypes';

export class AssistantService {
  static async createAssistant(data: CreateAssistantRequest): Promise<AssistantResponse> {
    const response = await apiClient.post('/assistant', data);
    return response.data;
  }

  static async listAssistants(filters?: any): Promise<AssistantResponse[]> {
    const response = await apiClient.get('/assistant', { params: filters });
    return response.data.assistants;
  }
}
```

#### 3.3 Navigation Integration

Add new routes to `frontend/src/config/navigation.ts`:

```typescript
export const navigation = [
  // ... existing routes
  {
    name: 'Assistant Management',
    path: '/assistants',
    icon: RobotIcon,
    children: [
      { name: 'Active Assistants', path: '/assistants' },
      { name: 'Personalities', path: '/assistants/personalities' },
      { name: 'Guardrails', path: '/assistants/guardrails' },
      { name: 'Sandbox Testing', path: '/assistants/sandbox' },
    ]
  }
];
```

### Phase 4: Testing & Validation (Week 9-10)

#### 4.1 Unit Tests

Create comprehensive unit tests in `backend/api/src/main/python/openapi_server/test/`:

**test_assistants.py**:
```python
import pytest
from openapi_server.impl import assistants

class TestAssistants:
    def test_create_assistant_success(self):
        """Test successful assistant creation"""
        # Test implementation with mocked dependencies

    def test_create_assistant_duplicate_animal(self):
        """Test error when animal already has assistant"""
        # Test constraint validation

    def test_prompt_merging_guardrail_precedence(self):
        """Test that guardrails override personality conflicts"""
        # Test conflict resolution logic
```

**test_sandbox.py**:
```python
class TestSandbox:
    def test_sandbox_expiry(self):
        """Test 30-minute TTL expiration"""
        # Test TTL behavior

    def test_sandbox_promotion(self):
        """Test promoting sandbox to live assistant"""
        # Test promotion logic and cleanup
```

#### 4.2 Integration Tests

Create DynamoDB integration tests:

```python
class TestDynamoDBIntegration:
    def test_assistant_crud_operations(self):
        """Test full CRUD cycle with real DynamoDB"""
        # Test with actual AWS resources

    def test_knowledge_base_file_processing(self):
        """Test document upload and processing pipeline"""
        # Test S3 integration and async processing
```

#### 4.3 Playwright E2E Tests

Create end-to-end tests in `backend/api/src/main/python/tests/playwright/`:

**test_assistant_management.py**:
```python
def test_create_assistant_workflow(page):
    """Test complete assistant creation workflow"""
    # Navigate to assistant management
    # Fill out form with personality and guardrails
    # Upload knowledge base documents
    # Verify assistant creation

def test_sandbox_testing_workflow(page):
    """Test sandbox testing and promotion"""
    # Create sandbox assistant
    # Test conversation interface
    # Promote to live assistant
    # Verify promotion success
```

### Phase 5: Production Deployment (Week 11-12)

#### 5.1 Environment Configuration

Set up production environment variables:

```bash
# OpenAI Integration
OPENAI_API_KEY=sk-...
OPENAI_MODEL_PRIMARY=gpt-4o
OPENAI_MODEL_FALLBACK=gpt-4o-mini

# AWS Resources
ASSISTANT_DYNAMO_TABLE_NAME=quest-prod-animal-assistant
KNOWLEDGE_S3_BUCKET=cmz-knowledge-base-production
BEDROCK_KNOWLEDGE_BASE_ID=...

# Processing Configuration
MAX_FILE_SIZE_MB=50
MAX_TOTAL_SIZE_MB=500
PROCESSING_TIMEOUT_MINUTES=5
SANDBOX_EXPIRY_MINUTES=30
```

#### 5.2 Monitoring & Alerting

Configure CloudWatch monitoring:

```python
# In utils/monitoring.py
import boto3

class AssistantMetrics:
    def __init__(self):
        self.cloudwatch = boto3.client('cloudwatch')

    def record_response_time(self, assistant_id: str, response_time_ms: int):
        """Record assistant response time metric"""
        # CloudWatch metric implementation

    def record_processing_failure(self, file_id: str, error: str):
        """Record document processing failure"""
        # Error tracking and alerting
```

#### 5.3 Performance Optimization

Implement performance optimizations:

- **Connection Pooling**: Reuse OpenAI API connections
- **Response Caching**: Cache frequent personality/guardrail combinations
- **Background Processing**: Use AWS Lambda for document processing
- **Rate Limiting**: Implement client-side backoff for OpenAI API

## Common Issues & Solutions

### Issue 1: OpenAPI Generation Problems

**Problem**: Generated controllers missing implementation connections

**Solution**:
1. Verify all endpoints have unique `operationId` fields
2. Run `make post-generate` (never standalone `make generate-api`)
3. Check that implementation modules are properly imported

### Issue 2: DynamoDB Constraint Violations

**Problem**: Multiple assistants for same animal

**Solution**:
```python
# In assistants.py
def create_assistant(animal_id, ...):
    # Check for existing assistant
    existing = get_assistant_by_animal(animal_id)
    if existing:
        raise ConflictError(f"Animal {animal_id} already has assistant {existing['assistantId']}")
```

### Issue 3: Sandbox TTL Not Working

**Problem**: Sandbox assistants not expiring automatically

**Solution**:
1. Verify TTL is enabled on `quest-dev-sandbox-assistant` table
2. Ensure `expiresAt` field is Unix timestamp (not ISO string)
3. Check DynamoDB TTL processing delay (up to 48 hours)

### Issue 4: File Processing Timeout

**Problem**: Knowledge base documents failing to process within 5 minutes

**Solution**:
1. Implement Step Functions with retry logic
2. Use async Lambda processing for large files
3. Add manual retry mechanism for failed documents

## Next Steps

After completing this implementation:

1. **Performance Testing**: Load test with expected visitor traffic
2. **Security Review**: Audit OpenAI integration and file upload security
3. **Staff Training**: Train zoo staff on assistant management interface
4. **Content Creation**: Help staff create initial personalities and guardrails
5. **Monitoring Setup**: Configure alerts for system health and performance

## Additional Resources

- **CMZ Development Guide**: `/CLAUDE.md`
- **OpenAPI Best Practices**: `/docs/openapi-best-practices.md`
- **DynamoDB Patterns**: `/backend/api/src/main/python/openapi_server/impl/utils/dynamo.py`
- **Testing Strategies**: `/PLAYWRIGHT_TESTING_STRATEGY.md`

For questions or issues during implementation, refer to the session history documentation in `/history/` or consult the feature specification at `/specs/003-animal-assistant-mgmt/spec.md`.