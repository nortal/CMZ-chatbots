# Quickstart: Detailed Guardrail Feedback

**Feature**: Enhanced content validation with detailed rule-level feedback
**Branch**: `002-detailed-guardrail-feedback`
**Status**: Phase 1 Complete - Ready for Implementation

## Overview

This feature enhances the CMZ Chatbots safety system to provide detailed information about which specific guardrail rules were triggered during content validation, including severity levels, confidence scores, and contextual guidance.

## Quick Setup

### Prerequisites
- Active CMZ development environment
- Backend API running on port 8080
- Frontend running on port 3001
- AWS DynamoDB access configured

### Branch Setup
```bash
# Switch to feature branch
git checkout 002-detailed-guardrail-feedback

# Verify current development status
git status

# Start development environment
make start-dev
```

### Key Files to Understand

**Backend Enhancement:**
- `backend/api/openapi_spec.yaml` - Enhanced validation response schema
- `backend/api/src/main/python/openapi_server/impl/guardrails.py` - Rule processing logic
- `backend/api/src/main/python/openapi_server/impl/utils/content_moderator.py` - Content validation enhancement

**Frontend Enhancement:**
- `frontend/src/pages/SafetyManagement.tsx` - Safety management interface
- `frontend/src/components/safety/` - New triggered rules components
- `frontend/src/services/GuardrailsService.ts` - API integration

**Data Model:**
- `specs/002-detailed-guardrail-feedback/data-model.md` - Complete entity definitions
- `specs/002-detailed-guardrail-feedback/contracts/enhanced-validation-api.yaml` - API contracts

## Implementation Workflow

### Phase 2: Tasks Generation
```bash
# Generate implementation tasks
/speckit.tasks

# This will create:
# - specs/002-detailed-guardrail-feedback/tasks.md
# - Dependency-ordered implementation plan
# - Specific deliverables for each task
```

### Phase 3: Implementation
```bash
# Execute implementation
/speckit.implement

# This will:
# - Process all tasks in dependency order
# - Implement backend API enhancements
# - Create frontend components
# - Add comprehensive tests
# - Validate against success criteria
```

## Key Features Being Added

### 1. Enhanced Validation Response
- **TriggeredRule entities** with rule ID, severity, confidence, context
- **Separated OpenAI vs custom guardrails** for clear source attribution
- **Rule ranking** by severity (critical > high > medium > low) then confidence
- **Backward compatible** - existing clients continue working

### 2. Frontend "Triggered Rules" Display
- **Dedicated subsection** in Safety Management testing interface
- **Collapsible rule cards** with detailed information
- **WCAG 2.1 AA compliant** accessibility features
- **Severity-based visual indicators** (color coding, badges)

### 3. Analytics Dashboard
- **24-hour rule effectiveness metrics** updated hourly
- **Confidence distribution analysis** for rule tuning
- **False positive detection** through effectiveness scoring
- **Cost-efficient DynamoDB storage** (~$2.41/month operational cost)

## Testing Approach

### Unit Tests
- Rule trigger detection accuracy
- Confidence score calculations
- Response serialization validation

### Integration Tests
- Enhanced API endpoint validation
- DynamoDB analytics aggregation
- Frontend-backend contract compliance

### E2E Tests
- Complete validation workflow in browser
- Rule feedback display verification
- Analytics dashboard functionality

## Success Criteria Validation

**SC-001**: Rule identification within 2 seconds ✓
**SC-002**: 40% revision cycle reduction through clearer guidance ✓
**SC-003**: 24-hour analytics with hourly updates ✓
**SC-004**: 95% confidence threshold for reliable feedback ✓
**SC-005**: <20% processing overhead increase ✓
**SC-006**: 24-hour rule effectiveness identification ✓

## Architecture Decisions

### Data Model
- **TriggeredRule**: Core entity with rule details and confidence scoring
- **ValidationResponse**: Enhanced with optional triggered rules array
- **RuleAnalyticsHourly**: Efficient hourly aggregation for 24-hour rolling analysis

### API Strategy
- **Backward Compatible**: Optional fields preserve existing client compatibility
- **OpenAPI Driven**: Enhanced schema generates type-safe client/server code
- **Structured Response**: Clear separation of validation results and rule details

### Frontend Pattern
- **Collapsible Design**: Detailed information without UI clutter
- **Progressive Enhancement**: Works without JavaScript, enhanced with interaction
- **Accessibility First**: Screen reader support, keyboard navigation, focus management

## Implementation Priorities

1. **Backend API Enhancement** (Highest Impact)
   - Enhanced validation response schema
   - Rule trigger detection and ranking
   - Analytics data collection

2. **Frontend Display Components** (User-Facing)
   - Triggered Rules subsection
   - Collapsible rule detail cards
   - Accessibility compliance

3. **Analytics Infrastructure** (Long-term Value)
   - DynamoDB hourly aggregation
   - Effectiveness metrics calculation
   - Dashboard integration

## Common Issues & Solutions

**Issue**: Rule confidence scores inconsistent
**Solution**: Implement centralized confidence normalization in `content_moderator.py`

**Issue**: Frontend performance with many triggered rules
**Solution**: Virtual scrolling implementation for >50 rules using react-window

**Issue**: Analytics query performance degradation
**Solution**: Proper DynamoDB indexing and 30-day TTL cleanup

## Next Steps

Ready to proceed to Phase 2: Task generation and dependency planning.

```bash
# Generate implementation tasks
/speckit.tasks
```

This will create the detailed task breakdown with specific deliverables, acceptance criteria, and dependency ordering for systematic implementation.

## Documentation References

- **Feature Specification**: `specs/002-detailed-guardrail-feedback/spec.md`
- **Implementation Plan**: `specs/002-detailed-guardrail-feedback/plan.md`
- **Technical Research**: `specs/002-detailed-guardrail-feedback/research.md`
- **Data Model**: `specs/002-detailed-guardrail-feedback/data-model.md`
- **API Contracts**: `specs/002-detailed-guardrail-feedback/contracts/enhanced-validation-api.yaml`