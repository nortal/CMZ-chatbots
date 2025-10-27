# Data Model: Animal Assistant Management System

**Feature**: 003-animal-assistant-mgmt
**Date**: 2025-10-23
**Phase**: 1 - Data Model Design

## Overview

Data model for the CMZ Animal Assistant Management System, designed to integrate with existing DynamoDB patterns and support all functional requirements including ephemeral sandbox testing and knowledge base management.

## Entity Definitions

### 1. Animal Assistant

**Purpose**: Live configuration for a specific animal containing merged system prompt and component references

**DynamoDB Table**: `quest-dev-animal-assistant`

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `assistantId` | String (PK) | Unique identifier | UUID format, required |
| `animalId` | String (GSI) | Reference to animal entity | Must exist in animal table |
| `personalityId` | String | Reference to personality configuration | Required, must exist |
| `guardrailId` | String | Reference to guardrail configuration | Required, must exist |
| `mergedPrompt` | String | Combined personality + guardrail system prompt | Auto-generated, 1-10k chars |
| `knowledgeBaseFileIds` | String[] | Array of linked knowledge base file IDs | Max 50 files per assistant |
| `status` | String | Current assistant status | ACTIVE, INACTIVE, ERROR |
| `lastPromptMerge` | Object | Timestamp of last prompt regeneration | ISO datetime |
| `responseTimeP95` | Number | Performance metric for monitoring | Milliseconds, updated hourly |
| `created` | Object | Creation audit | `{at: ISO, by: userId}` |
| `modified` | Object | Last modification audit | `{at: ISO, by: userId}` |

**Indexes**:
- **Primary**: `assistantId`
- **GSI-1**: `animalId` (one assistant per animal constraint)
- **GSI-2**: `personalityId` (find assistants using personality)
- **GSI-3**: `guardrailId` (find assistants using guardrail)

**Business Rules**:
- One active assistant per animal (enforced by GSI-1 unique constraint)
- Personality and guardrail must exist before assistant creation
- Merged prompt auto-regenerated when personality/guardrail updated
- Knowledge base updates trigger prompt refresh

### 2. Personality

**Purpose**: Reusable text configuration defining animal behavior and communication style

**DynamoDB Table**: `quest-dev-personality`

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `personalityId` | String (PK) | Unique identifier | UUID format, required |
| `name` | String | Human-readable personality name | 1-100 chars, unique |
| `description` | String | Purpose and usage description | 1-500 chars |
| `personalityText` | String | Core personality prompt text | 100-5000 chars, required |
| `animalType` | String | Suggested animal categories | MAMMAL, BIRD, REPTILE, etc. |
| `tone` | String | Communication style | PLAYFUL, EDUCATIONAL, CALM, etc. |
| `ageTarget` | String | Target age group | PRESCHOOL, ELEMENTARY, FAMILY |
| `usageCount` | Number | Number of assistants using this | Auto-calculated |
| `isTemplate` | Boolean | Whether this is a starter template | Default false |
| `created` | Object | Creation audit | `{at: ISO, by: userId}` |
| `modified` | Object | Last modification audit | `{at: ISO, by: userId}` |

**Indexes**:
- **Primary**: `personalityId`
- **GSI-1**: `name` (unique lookup)
- **GSI-2**: `animalType` (filter by animal category)
- **GSI-3**: `isTemplate` (find starter templates)

**Business Rules**:
- Name must be unique across all personalities
- Personality text follows guardrail-first merging pattern
- Templates are read-only after creation
- Usage count updated when assistant created/deleted

### 3. Guardrail

**Purpose**: Text-based safety and tone rules ensuring appropriate interactions

**DynamoDB Table**: `quest-dev-guardrail`

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `guardrailId` | String (PK) | Unique identifier | UUID format, required |
| `name` | String | Human-readable guardrail name | 1-100 chars, unique |
| `description` | String | Purpose and scope description | 1-500 chars |
| `guardrailText` | String | Safety rules as text prompts | 50-2000 chars, required |
| `category` | String | Guardrail category | SAFETY, EDUCATION, TONE, CONTENT |
| `severity` | String | Enforcement level | STRICT, MODERATE, GUIDANCE |
| `ageAppropriate` | String[] | Target age groups | Array of age categories |
| `usageCount` | Number | Number of assistants using this | Auto-calculated |
| `isDefault` | Boolean | Whether this is default for new assistants | Only one default per category |
| `created` | Object | Creation audit | `{at: ISO, by: userId}` |
| `modified` | Object | Last modification audit | `{at: ISO, by: userId}` |

**Indexes**:
- **Primary**: `guardrailId`
- **GSI-1**: `name` (unique lookup)
- **GSI-2**: `category` (filter by guardrail type)
- **GSI-3**: `isDefault` (find default guardrails)

**Business Rules**:
- Name must be unique across all guardrails
- Only one default guardrail per category
- Guardrail text takes precedence over personality in conflicts
- Changes trigger prompt regeneration for all using assistants

### 4. Knowledge Base File

**Purpose**: Educational document metadata and processing status for assistant knowledge

**DynamoDB Table**: `quest-dev-knowledge-file`

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `fileId` | String (PK) | Unique identifier | UUID format, required |
| `assistantId` | String (GSI) | Associated assistant | Required, must exist |
| `originalName` | String | User-provided filename | 1-255 chars, preserve extension |
| `s3Key` | String | S3 object key for original file | S3 path format |
| `s3ProcessedKey` | String | S3 key for extracted text | S3 path format, nullable |
| `fileSize` | Number | Original file size in bytes | Max 50MB (52,428,800 bytes) |
| `mimeType` | String | File content type | PDF, DOC, DOCX, TXT only |
| `processingStatus` | String | Current processing state | UPLOADED, PROCESSING, COMPLETED, FAILED |
| `processingError` | String | Error message if failed | Nullable, 1-1000 chars |
| `extractedTextLength` | Number | Length of extracted text | Characters count |
| `vectorEmbeddingId` | String | Reference to vector store | Bedrock Knowledge Base ID |
| `contentValidation` | Object | Validation results | `{safe: boolean, educational: boolean, ageAppropriate: boolean}` |
| `processingStarted` | String | Processing start time | ISO datetime |
| `processingCompleted` | String | Processing completion time | ISO datetime |
| `created` | Object | Upload audit | `{at: ISO, by: userId}` |
| `modified` | Object | Last modification audit | `{at: ISO, by: userId}` |

**Indexes**:
- **Primary**: `fileId`
- **GSI-1**: `assistantId` (list files for assistant)
- **GSI-2**: `processingStatus` (find failed/processing files)
- **GSI-3**: `processingStarted` (cleanup old processing files)

**Business Rules**:
- Maximum 500MB total files per assistant (enforced at upload)
- Processing must complete within 5 minutes or marked as FAILED
- Failed files can be retried or deleted
- Content validation required before assistant integration

### 5. Sandbox Assistant

**Purpose**: Temporary, ephemeral assistant for testing new configurations

**DynamoDB Table**: `quest-dev-sandbox-assistant`

| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| `sandboxId` | String (PK) | Unique identifier | UUID format, required |
| `createdBy` | String (GSI) | Zoo staff member who created | UserId, required |
| `animalId` | String | Associated animal (optional) | Reference for context |
| `personalityId` | String | Test personality configuration | Required, must exist |
| `guardrailId` | String | Test guardrail configuration | Required, must exist |
| `mergedPrompt` | String | Combined test system prompt | Auto-generated |
| `knowledgeBaseFileIds` | String[] | Test knowledge base files | Max 10 files for testing |
| `expiresAt` | Number | TTL expiration timestamp | Unix timestamp, 30 min from creation |
| `conversationCount` | Number | Number of test conversations | For usage tracking |
| `lastConversationAt` | String | Most recent test interaction | ISO datetime |
| `isPromoted` | Boolean | Whether promoted to live | Default false |
| `promotedAt` | String | Promotion timestamp | ISO datetime, nullable |
| `created` | Object | Creation audit | `{at: ISO, by: userId}` |

**Indexes**:
- **Primary**: `sandboxId`
- **GSI-1**: `createdBy` (list user's sandboxes)
- **GSI-2**: `expiresAt` (TTL cleanup)
- **TTL**: `expiresAt` (automatic DynamoDB expiration)

**Business Rules**:
- Automatic expiration after 30 minutes via DynamoDB TTL
- Cannot be modified after creation (immutable testing)
- Promotion creates new live assistant or updates existing
- Limited knowledge base files to reduce testing complexity

## Relationships

### Entity Relationships

```
Animal (existing)
    ↓ 1:1
Animal Assistant ←→ Personality (reusable)
    ↓              ←→ Guardrail (reusable)
    ↓ 1:many
Knowledge Base File

Zoo Staff (existing)
    ↓ 1:many
Sandbox Assistant ←→ Personality (reusable)
                  ←→ Guardrail (reusable)
```

### Data Flow

1. **Assistant Creation**: Animal + Personality + Guardrail → Merged Prompt
2. **Knowledge Upload**: File → S3 → Processing → Embedding → Assistant Link
3. **Sandbox Testing**: Personality + Guardrail → Temporary Assistant → Expiry/Promotion
4. **Prompt Updates**: Personality/Guardrail Change → Regenerate All Using Assistants

## Storage Considerations

### DynamoDB Optimization

- **Pay-per-request billing** aligns with existing CMZ pattern
- **Global Secondary Indexes** support common query patterns
- **TTL** for automatic sandbox cleanup reduces maintenance
- **Item size limits**: All entities well under 400KB DynamoDB limit

### S3 Integration

- **Knowledge base files**: Original documents in S3, metadata in DynamoDB
- **Processed text**: Cached in S3 to avoid reprocessing
- **Lifecycle policies**: Move old files to IA storage after 90 days

### Performance Characteristics

- **Assistant retrieval**: <200ms via primary key lookup
- **Knowledge base search**: <500ms via Bedrock vector search
- **Prompt merging**: <100ms in-memory string concatenation
- **File processing**: 2-5 minutes average, 5 minute SLA

## Migration Strategy

### Phase 1: Core Tables
1. Create DynamoDB tables with indexes
2. Implement basic CRUD operations in `impl/` modules
3. Unit tests for data model operations

### Phase 2: Integration
1. Connect to existing animal entities
2. Implement prompt merging logic
3. Integration tests with existing conversation system

### Phase 3: Knowledge Base
1. S3 bucket configuration
2. Document processing pipeline
3. Bedrock Knowledge Base integration

### Phase 4: Production
1. Performance optimization
2. Monitoring and alerting
3. Data backup and recovery procedures

This data model supports all functional requirements while maintaining consistency with existing CMZ DynamoDB patterns and constitutional requirements.