# Quickstart Guide: Conversation Safety and Personalization System

**Branch**: `001-conversation-safety-personalization` | **Date**: 2025-10-22 | **Spec**: [spec.md](./spec.md)

## Overview

This guide provides step-by-step instructions for setting up the development environment and implementing the conversation safety and personalization features for the CMZ Chatbots platform.

## Prerequisites

### Required Tools
- **Docker & Docker Compose**: Container runtime and orchestration
- **Python 3.11+**: Backend development environment
- **Node.js 18+**: Frontend development environment
- **AWS CLI**: Configured with CMZ account credentials (`aws configure --profile cmz`)
- **OpenAPI Generator CLI**: For API code generation

### Required Access
- **AWS Account**: CMZ production account (195275676211) in us-west-2 region
- **DynamoDB Tables**: Access to existing quest-dev-* tables
- **OpenAI API**: API key for content moderation and summarization
- **Environment Variables**: See [Environment Setup](#environment-setup) section

## Environment Setup

### 1. Clone and Configure Repository

```bash
# Clone repository (if not already done)
git clone <repository-url>
cd CMZ-chatbots

# Create feature branch
git checkout -b 001-conversation-safety-personalization

# Verify existing setup
make validate-api
```

### 2. Environment Variables

Create or update `.env.local` with the following additions:

```bash
# Existing CMZ configuration
AWS_PROFILE=cmz
AWS_REGION=us-west-2
DYNAMODB_ENDPOINT_URL=  # Leave empty for production DynamoDB

# New: OpenAI Integration
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_MODERATION_MODEL=text-moderation-latest

# New: Guardrails Configuration
GUARDRAILS_ENABLED=true
GUARDRAILS_CONFIG_ID=default
CONTENT_MODERATION_THRESHOLD=0.7

# New: Context Management
CONTEXT_SUMMARIZATION_ENABLED=true
CONTEXT_MAX_TOKENS=4000
SUMMARIZATION_TRIGGER_CONVERSATIONS=10

# New: Privacy Compliance
COPPA_MODE=true
AUDIT_LOGGING_ENABLED=true
DATA_RETENTION_DAYS=730

# New: Performance Settings
CONTEXT_CACHE_TTL=3600
REDIS_URL=redis://localhost:6379  # Optional for caching
```

### 3. Development Environment Startup

```bash
# Start complete development environment
make start-dev

# This command runs:
# 1. Docker containers for API and dependencies
# 2. Frontend development server
# 3. Database initialization
# 4. Health checks for all services

# Verify all services are running
make status
```

### 4. Database Schema Setup

```bash
# Initialize new DynamoDB tables for safety and personalization
python scripts/create_safety_tables.py

# Tables created:
# - quest-dev-user-context (user preferences and context)
# - quest-dev-conversation-analytics (enhanced conversation tracking)
# - quest-dev-guardrails-config (safety rules and policies)
# - quest-dev-privacy-audit (COPPA compliance logging)
# - quest-dev-context-archive (historical context summaries)
```

## Development Workflow

### 1. OpenAPI-First Development

```bash
# Edit OpenAPI specification
vim backend/api/openapi_spec.yaml

# Add new endpoints for safety and personalization:
# - /api/v1/guardrails/validate
# - /api/v1/context/{userId}
# - /api/v1/privacy/children/{parentId}
# (See contracts/ directory for complete specifications)

# Regenerate API code (SAFE with automatic validation)
make generate-api

# This automatically:
# - Generates new controllers and models
# - Preserves existing implementations
# - Fixes common generation issues
# - Validates endpoint connections
```

### 2. Implementation Structure

```bash
# Business logic implementation (only edit these files)
backend/api/src/main/python/openapi_server/impl/
├── guardrails.py              # Content safety and validation
├── user_context.py            # Context management and summarization
├── privacy_controls.py        # Parent dashboard and COPPA compliance
└── utils/
    ├── openai_integration.py  # OpenAI API wrapper
    ├── content_moderator.py   # Content validation logic
    ├── context_summarizer.py  # Conversation summarization
    └── privacy_audit.py       # Audit logging utilities

# Frontend components (new additions)
frontend/src/
├── components/
│   ├── privacy/               # Parent privacy controls
│   │   ├── PrivacyDashboard.tsx
│   │   ├── ConversationViewer.tsx
│   │   └── DataExportDialog.tsx
│   └── safety/                # Safety indicator components
│       ├── ContentFilter.tsx
│       └── SafetyStatus.tsx
├── services/
│   ├── GuardrailsService.ts   # Safety API integration
│   ├── ContextService.ts      # User context API
│   └── PrivacyService.ts      # Privacy controls API
└── types/
    ├── safety.ts              # Safety-related interfaces
    └── privacy.ts             # Privacy control interfaces
```

### 3. Testing Strategy

```bash
# Unit Testing (Backend)
cd backend/api/src/main/python
pytest tests/unit/test_guardrails.py
pytest tests/unit/test_user_context.py
pytest tests/unit/test_privacy_controls.py

# Integration Testing (API + DynamoDB)
pytest tests/integration/test_safety_integration.py
pytest tests/integration/test_context_integration.py

# E2E Testing (Full System)
cd backend/api/src/main/python/tests/playwright
FRONTEND_URL=http://localhost:3001 npx playwright test specs/safety-personalization.spec.js

# Contract Testing (API Alignment)
/validate-contracts  # Custom command for OpenAPI/API/Frontend alignment
```

### 4. Quality Gates

```bash
# Run all quality checks before committing
make quality-check

# Individual quality checks
make lint           # Code style validation
make typecheck      # TypeScript type checking
make security-scan  # Security vulnerability scan
make test-coverage  # Minimum 80% coverage requirement
```

## Implementation Phases

### Phase 1: Guardrails System (Week 1-2)

**Priority**: P1 (Critical for child safety)

**Implementation Order**:
1. OpenAI Moderation API integration (`impl/utils/openai_integration.py`)
2. Content validation middleware (`impl/guardrails.py`)
3. Guardrails configuration management (`impl/utils/content_moderator.py`)
4. Safety analytics and monitoring

**Key Endpoints**:
- `POST /api/v1/guardrails/validate` - Real-time content validation
- `GET /api/v1/guardrails/config` - Safety configuration retrieval
- `GET /api/v1/guardrails/analytics` - Safety effectiveness metrics

**Testing Focus**:
- Inappropriate content detection (99% accuracy target)
- Educational redirect functionality
- Performance impact (<200ms latency increase)

### Phase 2: User Context System (Week 3-4)

**Priority**: P1 (Critical for personalization)

**Implementation Order**:
1. User context storage schema (`data-model.md` → DynamoDB)
2. Context extraction from conversations (`impl/user_context.py`)
3. AI-powered summarization (`impl/utils/context_summarizer.py`)
4. Context injection into conversation prompts

**Key Endpoints**:
- `GET /api/v1/context/{userId}` - Retrieve user personalization context
- `PUT /api/v1/context/{userId}` - Update context from conversations
- `POST /api/v1/context/{userId}/summarize` - Trigger context compression

**Testing Focus**:
- Context preservation through summarization (95% retention target)
- Token usage optimization (60% reduction target)
- Cross-conversation personalization effectiveness

### Phase 3: Privacy Controls (Week 5-6)

**Priority**: P2 (Important for trust and compliance)

**Implementation Order**:
1. Parent dashboard backend (`impl/privacy_controls.py`)
2. Privacy audit logging (`impl/utils/privacy_audit.py`)
3. Data export and deletion capabilities
4. Parent dashboard UI components

**Key Endpoints**:
- `GET /api/v1/privacy/children/{parentId}` - Parent's children overview
- `GET /api/v1/privacy/conversations/{childId}` - Child's conversation history
- `DELETE /api/v1/privacy/conversations/{childId}` - Selective data deletion

**Testing Focus**:
- COPPA compliance validation
- Data deletion completeness (100% removal verification)
- Parent authorization and audit trails

### Phase 4: Performance Optimization (Week 7)

**Priority**: P2 (Important for scalability)

**Implementation Order**:
1. Redis caching layer for frequent contexts
2. Async background summarization
3. DynamoDB query optimization
4. Response time monitoring

**Performance Targets**:
- <2s conversation response time (including context)
- <100ms context retrieval time
- 40-60% reduction in API costs through optimization

## Monitoring and Validation

### Health Checks

```bash
# System health validation
curl http://localhost:8080/health

# Safety system health
curl http://localhost:8080/api/v1/guardrails/config

# Context system health
curl -X GET "http://localhost:8080/api/v1/context/test-user-id" \
  -H "Authorization: Bearer $JWT_TOKEN"
```

### Key Metrics to Monitor

**Safety Metrics**:
- Guardrails intervention rate (target: 5-15% of conversations)
- Content moderation accuracy (target: >99%)
- Safety response time (target: <200ms)

**Personalization Metrics**:
- Context application rate (target: >90% of returning users)
- Conversation engagement improvement (target: +40%)
- Token usage efficiency (target: 60% reduction)

**Privacy Metrics**:
- Parent dashboard usage (target: >70% of parents)
- Data deletion completion time (target: <5 seconds)
- Audit log completeness (target: 100% of operations)

### Troubleshooting Common Issues

**OpenAI API Rate Limits**:
- Implement exponential backoff in `openai_integration.py`
- Use request queuing for high-traffic periods
- Monitor token usage and implement budgeting

**DynamoDB Throttling**:
- Verify table capacity settings match usage patterns
- Implement request retry logic with jitter
- Consider using DynamoDB auto-scaling

**Context Summarization Quality**:
- Fine-tune summarization prompts for educational content
- Implement quality scoring for summaries
- Add manual review process for edge cases

**COPPA Compliance Issues**:
- Ensure all child data operations are logged
- Verify parent authorization for all privacy operations
- Test data deletion completeness regularly

## Next Steps

After completing the quickstart setup:

1. **Execute** `/speckit.tasks` to generate detailed implementation tasks
2. **Begin** with Phase 1 (Guardrails System) implementation
3. **Test** each phase thoroughly before proceeding to the next
4. **Monitor** system performance and safety metrics continuously
5. **Iterate** based on user feedback and safety observations

For detailed implementation tasks and code examples, proceed to execute the `/speckit.tasks` command which will generate specific, actionable development tasks based on this planning work.