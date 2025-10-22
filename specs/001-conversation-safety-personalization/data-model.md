# Data Model Design: Conversation Safety and Personalization

**Branch**: `001-conversation-safety-personalization` | **Date**: 2025-10-22 | **Spec**: [spec.md](./spec.md)

## Overview

Data model design for implementing conversation safety guardrails and cross-conversation user context retention. Extends existing DynamoDB infrastructure with new tables for user context, guardrails configuration, and privacy controls.

## Core Entities

### 1. User Context Profile

**Table**: `quest-dev-user-context`
**Primary Key**: `userId` (String)
**Description**: Stores personal preferences, interests, and behavioral patterns extracted from conversations

```yaml
UserContextProfile:
  userId: String                    # Primary key - links to existing user table
  preferences:
    interests: Array<String>        # ["cats", "conservation", "marine biology"]
    learningLevel: String           # "elementary", "middle", "high", "adult"
    favoriteAnimals: Array<String>  # ["lions", "dolphins", "penguins"]
    topics: Array<String>           # ["habitats", "conservation", "animal behavior"]
  conversationHistory:
    totalConversations: Number      # Count of total conversations
    lastActive: String              # ISO timestamp
    engagementScore: Number         # 0-100 based on interaction quality
  contextSummary:
    recentSummary: String           # Last 5 conversations summarized
    historicalSummary: String       # Older conversations summarized
    keyQuotes: Array<String>        # Memorable user statements
    lastUpdated: String             # ISO timestamp
  metadata:
    created: Object                 # {at: ISO timestamp, by: userId}
    modified: Object                # {at: ISO timestamp, by: userId}
    version: Number                 # For schema evolution
```

### 2. Conversation Analytics

**Table**: `quest-dev-conversation-analytics`
**Primary Key**: `conversationId` (String)
**Description**: Enhanced conversation tracking with safety and personalization metrics

```yaml
ConversationAnalytics:
  conversationId: String            # Primary key - links to existing conversation
  userId: String                    # GSI - for user-specific queries
  animalId: String                  # GSI - for animal-specific analytics
  safety:
    guardrailsApplied: Array<String> # ["content-filter", "educational-redirect"]
    moderationResults: Object       # OpenAI moderation API results
    interventionCount: Number       # Number of safety interventions
    riskScore: Number              # 0-100 calculated risk level
  personalization:
    contextApplied: Boolean         # Whether user context was used
    preferencesReferenced: Array<String> # Which preferences were mentioned
    engagementMetrics: Object       # Response quality, length, follow-ups
    learningOutcomes: Array<String> # Educational goals achieved
  performance:
    responseTime: Number            # Total response time in milliseconds
    tokenUsage: Object             # {input: Number, output: Number, context: Number}
    summarizationTriggered: Boolean # Whether conversation was summarized
  metadata:
    startTime: String              # ISO timestamp
    endTime: String                # ISO timestamp
    duration: Number               # Conversation length in minutes
```

### 3. Guardrails Configuration

**Table**: `quest-dev-guardrails-config`
**Primary Key**: `configId` (String)
**Sort Key**: `version` (Number)
**Description**: Manages safety rules and content filtering policies

```yaml
GuardrailsConfig:
  configId: String                  # Primary key - "default", "elementary", "advanced"
  version: Number                   # Sort key - for versioning
  ageGroup: String                  # Target age group
  contentFilters:
    moderationThresholds: Object    # OpenAI moderation category thresholds
    blockedTopics: Array<String>    # Topics to avoid or redirect
    allowedTopics: Array<String>    # Explicitly safe topics
    educationalRedirects: Object    # Topic -> educational response mapping
  responseGuidelines:
    maxResponseLength: Number       # Character limit for responses
    educationalFocus: Boolean       # Prioritize educational content
    encourageQuestions: Boolean     # Prompt follow-up questions
    parentalNotification: Boolean   # Flag concerning interactions
  prompts:
    systemPrompt: String           # Base system prompt with guidelines
    safetyPrompt: String           # Additional safety instructions
    educationalPrompt: String      # Educational context and mission
  metadata:
    created: Object                # {at: ISO timestamp, by: userId}
    modified: Object               # {at: ISO timestamp, by: userId}
    isActive: Boolean              # Whether this version is active
    description: String            # Version description
```

### 4. Privacy Audit Log

**Table**: `quest-dev-privacy-audit`
**Primary Key**: `auditId` (String)
**Sort Key**: `timestamp` (String)
**Description**: Comprehensive logging of privacy-related operations for COPPA compliance

```yaml
PrivacyAuditLog:
  auditId: String                   # Primary key - UUID
  timestamp: String                 # Sort key - ISO timestamp
  userId: String                    # GSI - affected user
  parentId: String                  # GSI - parent who performed action
  action: String                    # "view", "delete", "export", "modify"
  dataType: String                  # "conversation", "context", "preferences"
  details:
    resourceId: String              # ID of affected resource
    fieldNames: Array<String>       # Specific fields accessed/modified
    previousValue: String           # For modifications (encrypted)
    newValue: String                # For modifications (encrypted)
    reason: String                  # Parent-provided reason for change
  compliance:
    legalBasis: String              # COPPA compliance basis
    retentionExpiry: String         # When this log entry expires
    dataMinimization: Boolean       # Whether data was minimized
  metadata:
    ipAddress: String               # Requesting IP (hashed)
    userAgent: String               # Browser/app information
    sessionId: String               # Session identifier
    parentConsent: Boolean          # Whether parent consent was verified
```

### 5. Context Summary Archive

**Table**: `quest-dev-context-archive`
**Primary Key**: `userId` (String)
**Sort Key**: `archiveDate` (String)
**Description**: Historical context summaries for long-term personalization

```yaml
ContextSummaryArchive:
  userId: String                    # Primary key
  archiveDate: String               # Sort key - YYYY-MM-DD format
  summaryData:
    conversationCount: Number       # Conversations included in this summary
    timeSpan: Object               # {start: ISO, end: ISO}
    keyInterests: Array<String>     # Interests identified in this period
    learningProgress: Object        # Educational milestones achieved
    behavioralPatterns: Object      # Interaction patterns observed
  compression:
    originalTokens: Number          # Token count before summarization
    compressedTokens: Number        # Token count after summarization
    compressionRatio: Number        # Efficiency metric
    qualityScore: Number            # Preservation of important information
  metadata:
    created: Object                 # {at: ISO timestamp, by: system}
    algorithm: String               # Summarization algorithm used
    ttl: Number                     # DynamoDB TTL for automatic cleanup
```

## Data Relationships

### Primary Relationships
- `UserContextProfile.userId` → `quest-dev-users.userId`
- `ConversationAnalytics.conversationId` → `quest-dev-conversations.conversationId`
- `ConversationAnalytics.userId` → `quest-dev-users.userId`
- `PrivacyAuditLog.userId` → `quest-dev-users.userId`
- `PrivacyAuditLog.parentId` → `quest-dev-users.userId` (where role=parent)

### Access Patterns

#### 1. User Context Retrieval (Real-time)
```yaml
Query: UserContextProfile
Key: userId = "user123"
Use Case: Inject personalization context into conversation
Performance: <50ms via single item query
```

#### 2. Parent Privacy Dashboard
```yaml
Query: PrivacyAuditLog
GSI: parentId = "parent456"
Sort: timestamp DESC
Use Case: Show parent all child data activities
Performance: <100ms with pagination
```

#### 3. Conversation Analytics (Admin)
```yaml
Query: ConversationAnalytics
GSI: animalId = "leo-lion"
Filter: safety.interventionCount > 0
Use Case: Monitor guardrails effectiveness
Performance: <200ms with filtering
```

#### 4. Context Summarization (Background)
```yaml
Query: ConversationAnalytics
GSI: userId = "user123"
Sort: metadata.startTime ASC
Use Case: Batch summarization of user conversations
Performance: <500ms for 50 conversations
```

## Schema Evolution Strategy

### Version Management
- All tables include `version` field for schema evolution
- Backward compatibility maintained for 2 major versions
- Migration scripts handle data transformation
- Blue/green deployment for schema changes

### Data Retention
- **User Context**: Retained until user deletion or account closure
- **Conversation Analytics**: 2-year retention with automated archival
- **Privacy Audit**: 7-year retention for compliance (encrypted)
- **Context Archive**: 1-year retention with TTL cleanup

### Performance Optimization
- **Hot Data**: Recent context and active conversations in DynamoDB
- **Warm Data**: Monthly summaries in DynamoDB with lower throughput
- **Cold Data**: Historical archives in S3 with lifecycle policies
- **Caching**: Redis for frequently accessed user contexts

## Security and Privacy

### Data Classification
- **Personal Data**: Encrypted at rest and in transit
- **Educational Data**: Standard encryption with audit trails
- **Analytics Data**: Anonymized where possible
- **Audit Data**: High security with immutable logging

### Access Controls
- **Students**: Read own conversation history only
- **Parents**: Full read/write access to child data
- **Zookeepers**: Analytics and guardrails management
- **Admins**: System configuration and compliance reporting

### Compliance Features
- **Right to be Forgotten**: Complete data deletion across all tables
- **Data Portability**: Export functionality for all user data
- **Consent Management**: Granular permissions with audit trails
- **Data Minimization**: Automatic cleanup of unnecessary data

This data model provides the foundation for implementing conversation safety and personalization while maintaining COPPA compliance and system performance requirements.