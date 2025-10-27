# Implementation Plan: Detailed Guardrail Feedback

**Branch**: `002-detailed-guardrail-feedback` | **Date**: 2025-01-14 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-detailed-guardrail-feedback/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Enhance the content validation system to provide detailed rule-level feedback in the Safety Management testing interface. System will return comprehensive information about triggered guardrail rules including severity, confidence scores, and contextual guidance. Frontend will display this information in a dedicated "Triggered Rules" subsection with collapsible details, ranked by severity and confidence. Analytics tracking will enable rule effectiveness monitoring with 24-hour data updated hourly.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript/React 18+ (frontend)
**Primary Dependencies**: Flask/Connexion, OpenAPI Generator, React, Tailwind CSS, AWS SDK (boto3)
**Storage**: AWS DynamoDB (existing ContentValidation tables), enhanced response payloads
**Testing**: pytest (backend), Playwright (E2E), existing test infrastructure
**Target Platform**: Docker containers, AWS deployment, web browsers
**Project Type**: Web application (existing CMZ Chatbots system enhancement)
**Performance Goals**: <20% validation processing time increase, 2-second rule identification, hourly analytics updates
**Constraints**: Must preserve existing API contracts, maintain 0.5+ confidence threshold, 95% reliable feedback
**Scale/Scope**: Enhancement to existing safety system, ~5 new/modified API endpoints, 1 enhanced UI component

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**✅ I. OpenAPI-First Development**: Enhancement will modify existing OpenAPI spec for validation responses and follow OpenAPI Generator workflow for any new endpoints

**✅ II. DynamoDB Persistence**: Uses existing ContentValidation DynamoDB tables and centralized dynamo.py utilities, no new storage patterns required

**✅ III. Hexagonal Architecture**: Changes will be in controllers (generated), impl modules (business logic), and handlers.py following existing three-layer pattern

**✅ IV. Test-First with Validation Gates**: Will extend existing pytest unit tests and Playwright E2E tests for rule feedback validation

**✅ V. Mock-First Authentication**: Uses existing AUTH_MODE=mock for development, no auth changes required

**✅ VI. AWS MCP Integration**: Leverages existing MCP server integration, no new AWS services required

**Status**: ✅ **PASS** - All constitutional principles satisfied, no violations requiring justification

## Project Structure

### Documentation (this feature)

```
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```
backend/api/
├── openapi_spec.yaml                    # Enhanced validation response schema
├── src/main/python/openapi_server/
│   ├── controllers/                     # Generated - validation_controller enhanced
│   ├── models/                          # Generated - TriggeredRule, ValidationResponse models
│   ├── impl/
│   │   ├── guardrails.py               # Enhanced - detailed rule feedback logic
│   │   └── utils/
│   │       ├── content_moderator.py    # Enhanced - detailed rule violation tracking
│   │       └── safety_analytics.py     # Enhanced - hourly analytics processing
│   └── test/
│       ├── test_guardrails_feedback.py # New - rule feedback unit tests
│       └── test_validation_response.py  # New - enhanced response validation

frontend/src/
├── pages/
│   └── SafetyManagement.tsx            # Enhanced - triggered rules subsection
├── components/safety/
│   ├── TriggeredRulesDisplay.tsx       # New - collapsible rule details component
│   └── RuleAnalytics.tsx               # Enhanced - hourly analytics display
├── services/
│   └── GuardrailsService.ts            # Enhanced - detailed feedback API calls
└── types/
    └── GuardrailTypes.ts               # Enhanced - triggered rule interfaces

tests/playwright/
└── specs/ui-features/
    └── detailed-guardrail-feedback.spec.js # New - E2E tests for rule feedback display
```

**Structure Decision**: Web application enhancement following existing CMZ Chatbots architecture. Changes are localized to validation components in both backend (content moderation) and frontend (safety management interface), maintaining separation of concerns and existing code organization patterns.

## Complexity Tracking

*No constitutional violations requiring justification*

