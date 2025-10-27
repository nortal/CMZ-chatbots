# Research: Animal Assistant Management System

**Feature**: 003-animal-assistant-mgmt
**Date**: 2025-10-23
**Phase**: 0 - Research and Technology Decisions

## Overview

Research findings for implementing the CMZ Animal Assistant Management System, covering OpenAI API integration, document processing pipelines, and AWS service selection for production deployment.

## Key Technology Decisions

### 1. OpenAI API Integration

**Decision**: Use OpenAI API with streaming responses and multi-model fallback strategy

**Rationale**:
- Production-ready conversational AI with proven quality for educational content
- Streaming provides ChatGPT-like user experience expected by visitors
- Multi-model fallback (GPT-4o → GPT-4o-mini → GPT-3.5-turbo) ensures availability and cost optimization
- Strong content moderation capabilities aligned with zoo safety requirements

**Implementation Pattern**:
- Flask SSE with `stream_with_context` for real-time responses
- System prompt composition: Personality + Guardrails with clear override hierarchy
- Client-side exponential backoff for rate limiting
- 5-layer security defense against prompt injection

**Alternatives Considered**:
- LangChain: Rejected due to excessive abstraction and limited customization
- OpenAI Assistants API: Rejected due to cost and difficulty integrating custom safety layers
- Self-hosted models: Rejected due to quality requirements and infrastructure complexity

### 2. Document Processing Architecture

**Decision**: AWS-native serverless pipeline with Amazon Bedrock Knowledge Bases

**Rationale**:
- Meets 5-minute processing requirement (typical 2-5 minutes)
- Handles 500MB limit with room for growth (supports up to 3,000 page PDFs)
- Managed service reduces maintenance overhead
- Cost-effective at projected scale ($15-30/month total)
- Built-in vector search and RAG capabilities

**Implementation Pattern**:
- Two-bucket S3 architecture: quarantine → malware scan → production
- Event-driven Lambda pipeline: Upload → Validate → Extract → Embed → Index
- Step Functions orchestration with error handling and retry logic
- DynamoDB metadata storage following existing CMZ patterns

**Alternatives Considered**:
- Custom RAG with Pinecone: Rejected due to complexity and 3x cost increase
- Synchronous processing: Rejected due to 5-minute timeout constraints
- File system storage: Rejected due to scalability and backup requirements

### 3. Prompt Merging Strategy

**Decision**: Text-based guardrails appended to personality with clear precedence rules

**Rationale**:
- Simple implementation aligning with clarification responses
- Clear conflict resolution (guardrails override personality)
- Easy for zoo staff to understand and maintain
- Consistent with existing CMZ text-based configuration patterns

**Implementation Pattern**:
```
System Prompt = Base Identity + Animal Personality + Guardrail Rules + Knowledge Context
```

**Alternatives Considered**:
- Structured guardrail categories: Rejected due to added complexity without clear benefit
- JSON-based rule system: Rejected as over-engineered for zoo staff workflow

### 4. Sandbox Management

**Decision**: In-memory storage with DynamoDB expiry tracking

**Rationale**:
- 30-minute expiry requirement suits temporary testing workflow
- No persistence needed for ephemeral testing environments
- DynamoDB TTL handles automatic cleanup
- Isolation from production data ensures safety

**Implementation Pattern**:
- Sandbox assistants stored as temporary records with TTL
- Promotion copies configuration to live assistant table
- Background cleanup process removes expired entries

### 5. Authentication and Access Control

**Decision**: Reuse existing CMZ AUTH_MODE=mock with equal staff access

**Rationale**:
- Aligns with clarification that all zoo staff have equal access
- Leverages existing JWT token patterns
- No additional complexity for role-based permissions
- Consistent with CMZ development workflow

## Research Documents

### Detailed Technical Research

1. **OpenAI Integration Best Practices**: `/docs/openai-integration-best-practices.md`
   - System prompt composition patterns
   - Streaming response implementation
   - Rate limiting and error handling
   - Security and content moderation
   - Cost optimization strategies

2. **Knowledge Base Architecture**: `/claudedocs/knowledge-base-architecture-research.md`
   - Document processing pipeline design
   - AWS service selection and configuration
   - Vector search and RAG implementation
   - Content validation and quality assurance
   - 10-week implementation roadmap

## Architecture Summary

### Core Services Selected
- **OpenAI API**: GPT-4o primary, GPT-4o-mini fallback for conversational AI
- **Amazon S3**: Document storage with two-bucket security pattern
- **AWS Lambda**: Serverless document processing pipeline
- **Amazon Textract**: PDF/DOC text extraction
- **Amazon Bedrock Knowledge Bases**: Managed RAG with vector search
- **AWS GuardDuty**: Malware protection for uploaded documents
- **DynamoDB**: Metadata storage following existing CMZ patterns
- **Step Functions**: Orchestration of async processing workflows

### Performance Characteristics
- **Response Time**: <2 seconds for assistant retrieval, streaming for conversations
- **Document Processing**: 2-5 minutes typical, 5-minute SLA
- **Sandbox Expiry**: 30 minutes with automatic cleanup
- **File Limits**: 50MB per upload, 500MB total per assistant
- **Concurrent Users**: 100+ visitors supported with rate limiting

### Cost Projections
- **OpenAI API**: $9.50-275/month depending on model selection
- **AWS Services**: $15-30/month for document processing and storage
- **Total Operating Cost**: $25-305/month at projected scale

## Risk Mitigation

### Identified Risks and Mitigations
1. **OpenAI API Outages**: Multi-model fallback + static educational responses
2. **Rate Limiting**: Exponential backoff + model downgrade strategy
3. **Document Processing Failures**: Step Functions retry logic + manual review queue
4. **Security**: 5-layer defense including malware scanning and content moderation
5. **Cost Overruns**: Usage monitoring + automatic model fallback triggers

### Performance Safeguards
- Connection pooling for OpenAI API requests
- Redis caching for frequently accessed knowledge base content
- CloudWatch monitoring with automated alerting
- Circuit breaker pattern for external service failures

## Next Phase Requirements

Phase 1 (Design & Contracts) should proceed with:
1. DynamoDB table schema design for all entities
2. OpenAPI specification for assistant management endpoints
3. React component architecture for assistant management UI
4. Integration patterns with existing CMZ conversation system

All technology decisions are final and ready for implementation planning.