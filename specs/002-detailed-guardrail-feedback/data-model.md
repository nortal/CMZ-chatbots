# Data Model: Detailed Guardrail Feedback

**Date**: 2025-01-14
**Feature**: Enhanced content validation with detailed rule-level feedback
**Phase**: 1 - Design & Contracts

## Overview

This data model defines the enhanced entities and relationships for providing detailed guardrail feedback in the CMZ Chatbots safety system. The model extends existing ContentValidation data structures while maintaining backward compatibility.

---

## Core Entities

### 1. TriggeredRule

**Purpose**: Represents a single guardrail rule that was violated during content validation.

**Attributes**:
```yaml
TriggeredRule:
  ruleId: string
    description: Unique identifier for the guardrail rule
    format: "rule_<category>_<number>"
    example: "rule_violence_001"
    validation: Required, max 50 characters

  ruleText: string
    description: Full text of the guardrail rule
    example: "Never discuss violence or harm to animals"
    validation: Required, max 500 characters

  ruleType: enum
    values: [ALWAYS, NEVER, ENCOURAGE, DISCOURAGE]
    description: Type of guardrail rule
    validation: Required

  category: string
    description: Category classification for the rule
    enum: [safety, educational, age-appropriate, behavioral, content-quality, privacy]
    validation: Required

  severity: enum
    values: [low, medium, high, critical]
    description: Severity level of rule violation
    validation: Required

  confidenceScore: number
    description: Confidence score (0-100) that rule was violated
    range: 0.0 to 100.0
    validation: Required, must be >= 50.0 for inclusion

  triggerContext: string
    description: Specific content excerpt that triggered the rule
    example: "Matched keywords: violence, harm, fight"
    validation: Optional, max 500 characters

  userMessage: string
    description: User-friendly message explaining why content was flagged
    example: "We don't discuss animals being hurt. Let's learn about how we keep animals safe!"
    validation: Optional, max 200 characters

  detectedAt: string
    description: ISO8601 timestamp when rule was triggered
    format: "YYYY-MM-DDTHH:mm:ss.sssZ"
    validation: Required

  priority: number
    description: Rule priority (0-100, higher = more important)
    range: 0 to 100
    default: 50
    validation: Optional
```

**Relationships**:
- Belongs to one ValidationResponse
- References one GuardrailRule (existing)
- May have multiple RuleAnalyticsHourly records

**State Transitions**:
- Created: When rule confidence >= 50% threshold
- Enhanced: When additional context is added
- Archived: After validation response is processed

**Validation Rules**:
- `confidenceScore >= 50.0` (only reliable triggers included)
- `ruleText.length <= 500` (UI display constraints)
- `userMessage.length <= 200` (chat bubble constraints)
- `detectedAt` must be valid ISO8601 timestamp

---

### 2. ValidationResponse (Enhanced)

**Purpose**: Enhanced content validation response with detailed rule information.

**Attributes**:
```yaml
ValidationResponse:
  # === Existing Fields (Maintained) ===
  valid: boolean
    description: Whether content passes safety validation
    validation: Required

  result: enum
    values: [approved, flagged, blocked, escalated]
    description: Validation outcome
    validation: Required

  riskScore: number
    description: Calculated risk score (0-100)
    range: 0.0 to 100.0
    validation: Required

  requiresEscalation: boolean
    description: Whether validation requires human review
    validation: Required

  userMessage: string
    description: User-facing message about validation result
    validation: Optional, max 200 characters

  safeAlternative: string
    description: Safe alternative content if available
    validation: Optional, max 1000 characters

  # === New Enhanced Fields ===
  validationId: string
    description: Unique identifier for this validation event
    format: UUID v4
    validation: Required

  timestamp: string
    description: ISO8601 timestamp when validation occurred
    format: "YYYY-MM-DDTHH:mm:ss.sssZ"
    validation: Required

  processingTimeMs: number
    description: Processing time in milliseconds
    range: 0 to 60000
    validation: Required

  triggeredRules: TriggeredRulesSummary
    description: Detailed information about triggered rules
    validation: Required

  summary: ValidationSummary
    description: High-level summary of validation results
    validation: Required
```

**Relationships**:
- Has many TriggeredRule entities
- May reference one ContentValidation record (existing DynamoDB)
- May generate multiple SafetyEvent records (existing analytics)

**Validation Rules**:
- `processingTimeMs <= 60000` (1-minute timeout)
- `validationId` must be unique UUID
- `triggeredRules.totalTriggered` must match actual TriggeredRule count
- If `result == 'blocked'` then `valid == false`

---

### 3. TriggeredRulesSummary

**Purpose**: Summary information about all triggered rules in a validation.

**Attributes**:
```yaml
TriggeredRulesSummary:
  totalTriggered: number
    description: Total number of rules triggered
    range: 0 to 1000
    validation: Required

  highestSeverity: enum
    values: [none, low, medium, high, critical]
    description: Highest severity level among triggered rules
    validation: Required

  openaiModeration: OpenAIModerationResult
    description: OpenAI content moderation results
    validation: Optional

  customGuardrails: array[TriggeredRule]
    description: Custom CMZ guardrails rules that were triggered
    validation: Required (may be empty array)
```

**Derived Attributes**:
- `totalTriggered` = count of all triggered rules
- `highestSeverity` = max severity from all triggered rules
- `customGuardrails` sorted by severity desc, confidence desc

**Validation Rules**:
- `totalTriggered >= 0`
- `customGuardrails.length <= totalTriggered`
- If `totalTriggered == 0` then `highestSeverity == 'none'`

---

### 4. OpenAIModerationResult

**Purpose**: Structured OpenAI moderation results separated from custom guardrails.

**Attributes**:
```yaml
OpenAIModerationResult:
  flagged: boolean
    description: Whether OpenAI flagged the content
    validation: Required

  model: string
    description: OpenAI moderation model used
    example: "text-moderation-latest"
    validation: Required

  categories: array[OpenAIModerationCategory]
    description: Triggered OpenAI moderation categories
    validation: Required (may be empty)
```

**Relationships**:
- Belongs to one TriggeredRulesSummary
- Has many OpenAIModerationCategory entities

---

### 5. OpenAIModerationCategory

**Purpose**: Individual OpenAI moderation category result.

**Attributes**:
```yaml
OpenAIModerationCategory:
  category: enum
    values: [
      hate, hate/threatening,
      harassment, harassment/threatening,
      self-harm, self-harm/intent, self-harm/instructions,
      sexual, sexual/minors,
      violence, violence/graphic
    ]
    description: OpenAI moderation category
    validation: Required

  severity: enum
    values: [low, medium, high, critical]
    description: Severity classification for this category
    validation: Required

  confidenceScore: number
    description: Confidence score (0-100) for this detection
    range: 0.0 to 100.0
    validation: Required

  rawScore: number
    description: Raw OpenAI confidence score (0.0-1.0)
    range: 0.0 to 1.0
    validation: Required

  detectedAt: string
    description: ISO8601 timestamp when category was detected
    validation: Required
```

**Validation Rules**:
- `confidenceScore = rawScore * 100`
- `rawScore` must be valid OpenAI output range
- `detectedAt` must be <= parent validation timestamp

---

### 6. ValidationSummary

**Purpose**: High-level summary of validation results for quick assessment.

**Attributes**:
```yaml
ValidationSummary:
  requiresEscalation: boolean
    description: Whether this validation requires human review
    validation: Required

  blockingViolations: number
    description: Number of violations that block content
    range: 0 to 1000
    validation: Required

  warningViolations: number
    description: Number of violations that generate warnings
    range: 0 to 1000
    validation: Required

  ageGroupApproved: enum
    values: [elementary, middle, high, adult, none]
    description: Minimum age group for which content is appropriate
    validation: Required
```

**Business Rules**:
- `requiresEscalation = true` if any severity == 'critical'
- `blockingViolations` = count where ruleType in ['NEVER'] and severity >= 'medium'
- `warningViolations` = count where ruleType in ['DISCOURAGE'] or severity == 'low'
- `ageGroupApproved` determined by highest severity and content type

---

### 7. RuleAnalyticsHourly (New)

**Purpose**: Hourly aggregated analytics for rule effectiveness tracking.

**Attributes**:
```yaml
RuleAnalyticsHourly:
  # === Primary Key ===
  partitionKey: string
    format: "rule#<ruleId>"
    example: "rule#rule_violence_001"
    validation: Required

  sortKey: string
    format: "hour#<YYYY-MM-DDTHH:00:00Z>"
    example: "hour#2025-01-14T15:00:00Z"
    validation: Required

  # === Analytics Data ===
  triggerCount: number
    description: Number of times rule was triggered this hour
    range: 0 to 10000
    validation: Required

  totalConfidence: number
    description: Sum of all confidence scores (for average calculation)
    range: 0.0 to 1000000.0
    validation: Required

  severityBreakdown: object
    properties:
      critical: number
      high: number
      medium: number
      low: number
    description: Count of triggers by severity level
    validation: Required

  blockingViolations: number
    description: Number of triggers that blocked content
    range: 0 to 10000
    validation: Required

  escalationTriggers: number
    description: Number of triggers that required escalation
    range: 0 to 10000
    validation: Required

  # === DynamoDB Attributes ===
  ttl: number
    description: Unix timestamp for automatic deletion (30 days)
    validation: Required

  lastUpdated: string
    description: ISO8601 timestamp of last update
    validation: Required
```

**Query Patterns**:
```python
# 24-hour rule effectiveness
PK = "rule#rule_violence_001"
SK BETWEEN "hour#2025-01-14T00:00:00Z" AND "hour#2025-01-14T23:00:00Z"

# All rules for specific hour
GSI1PK = "hour#2025-01-14T15:00:00Z"  # Global Secondary Index
```

**Derived Metrics**:
- `averageConfidence = totalConfidence / triggerCount`
- `blockingRate = blockingViolations / triggerCount`
- `escalationRate = escalationTriggers / triggerCount`
- `effectivenessScore = 0.4*avgConfidence + 0.3*blockingRate + 0.2*(1-escalationRate) + 0.1*volumeFactor`

---

## Entity Relationships

```mermaid
erDiagram
    ValidationResponse ||--|| TriggeredRulesSummary : contains
    TriggeredRulesSummary ||--o{ TriggeredRule : has
    TriggeredRulesSummary ||--o| OpenAIModerationResult : includes
    OpenAIModerationResult ||--o{ OpenAIModerationCategory : contains
    ValidationResponse ||--|| ValidationSummary : includes
    TriggeredRule ||--o{ RuleAnalyticsHourly : generates

    ValidationResponse {
        string validationId PK
        boolean valid
        enum result
        number riskScore
        timestamp createdAt
    }

    TriggeredRule {
        string ruleId
        enum ruleType
        enum severity
        number confidenceScore
        string triggerContext
    }

    RuleAnalyticsHourly {
        string partitionKey PK
        string sortKey SK
        number triggerCount
        number totalConfidence
        object severityBreakdown
    }
```

---

## Data Flow Patterns

### 1. Content Validation Flow
```yaml
Input: content + context
Process:
  1. OpenAI moderation check
  2. Custom guardrails evaluation
  3. Confidence scoring and filtering (>= 50%)
  4. Severity-based ranking
  5. Summary generation
Output: ValidationResponse with TriggeredRules
```

### 2. Analytics Aggregation Flow
```yaml
Trigger: DynamoDB Streams from ContentValidation
Process:
  1. Lambda function processes validation events
  2. Extract rule triggers and metadata
  3. Aggregate by hour using atomic ADD operations
  4. Update RuleAnalyticsHourly records
  5. Set TTL for automatic cleanup
Output: Updated hourly analytics
```

### 3. Rule Effectiveness Calculation
```yaml
Input: 24-hour RuleAnalyticsHourly records
Process:
  1. Sum triggerCount, totalConfidence, blockingViolations
  2. Calculate averageConfidence = totalConfidence / triggerCount
  3. Calculate blockingRate = blockingViolations / triggerCount
  4. Calculate escalationRate = escalationTriggers / triggerCount
  5. Apply effectiveness formula with weights
Output: EffectivenessScore (0.0 to 1.0)
```

---

## Storage Considerations

### DynamoDB Table Design

**Primary Table: ContentValidation (Enhanced)**
- Partition Key: `validationId` (UUID)
- Sort Key: None (single item per validation)
- TTL: 90 days
- Size Estimate: +30% for enhanced fields (~1KB → ~1.3KB per record)

**Analytics Table: RuleAnalyticsHourly (New)**
- Partition Key: `rule#<ruleId>`
- Sort Key: `hour#<timestamp>`
- Global Secondary Index: `hour#<timestamp>` (for cross-rule queries)
- TTL: 30 days
- Size Estimate: ~100 bytes per record
- Volume: 24 hours × 50 rules × 30 days = 36,000 records max

### Performance Characteristics

**Read Patterns**:
- Single validation lookup: 1 read unit (by validationId)
- 24-hour rule analytics: 24 read units (1 per hour)
- Cross-rule hour analytics: Query GSI (varies by rules)

**Write Patterns**:
- Validation response: 1 write unit (enhanced payload)
- Hourly analytics: Batch atomic ADD operations
- Cleanup: Automatic via TTL (no additional writes)

---

## Migration Strategy

### Phase 1: Schema Enhancement (Backward Compatible)
1. Add optional `triggeredRules` field to ValidationResponse
2. Maintain all existing required fields
3. Deploy enhanced backend with feature flag
4. Verify existing clients continue working

### Phase 2: Analytics Infrastructure
1. Create RuleAnalyticsHourly DynamoDB table
2. Deploy Lambda aggregation function
3. Enable DynamoDB Streams on ContentValidation
4. Test analytics pipeline with sample data

### Phase 3: Frontend Integration
1. Update TypeScript interfaces
2. Enhance validation response handling
3. Add triggered rules display components
4. Integrate analytics dashboard

### Phase 4: Full Activation
1. Enable detailed feedback for all validations
2. Monitor performance and cost metrics
3. Adjust aggregation parameters if needed
4. Document new capabilities

---

## Validation & Constraints

### Business Rule Validation
- Confidence threshold: Only rules with >= 50% confidence included
- Severity ranking: critical > high > medium > low
- Age appropriateness: Based on highest severity and content type
- Escalation triggers: Any critical severity or specific OpenAI categories

### Technical Constraints
- Response payload size: Must remain < 1MB for API gateway
- Processing timeout: Complete validation within 30 seconds
- Analytics latency: Hourly updates within 5 minutes of hour boundary
- Storage efficiency: 30-day TTL on analytics, 90-day on validations

### Performance Requirements
- Validation response time: < 2 seconds (SC-001)
- Processing overhead: < 20% increase (SC-005)
- Analytics availability: 99.9% uptime for dashboard queries
- Cost efficiency: < $10/month operational cost for analytics

---

## Testing Considerations

### Unit Testing
- Entity validation rules
- Confidence score calculations
- Severity ranking algorithms
- Analytics aggregation logic

### Integration Testing
- DynamoDB table operations
- Lambda function triggers
- API response serialization
- Analytics query patterns

### Performance Testing
- Validation response times under load
- Analytics query performance
- DynamoDB capacity utilization
- Lambda function cold start times

### Data Quality Testing
- Confidence score accuracy
- Rule trigger reliability
- Analytics data consistency
- TTL cleanup verification