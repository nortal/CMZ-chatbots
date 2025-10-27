# Implementation Plan: Animal Assistant Management System

**Branch**: `003-animal-assistant-mgmt` | **Date**: 2025-10-23 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/003-animal-assistant-mgmt/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Digital ambassador management system for zoo animals that combines personality, guardrails, and knowledge base into unified AI assistants. Supports ephemeral sandbox testing and automatic prompt merging with OpenAI API integration. Built as API extension to existing CMZ chatbot platform.

## Technical Context

**Language/Version**: Python 3.11+ (existing CMZ backend stack)
**Primary Dependencies**: Flask/Connexion, OpenAPI Generator, boto3, OpenAI SDK
**Storage**: AWS DynamoDB (existing CMZ pattern), S3 for knowledge base files
**Testing**: pytest for unit tests, Playwright for E2E, DynamoDB integration tests
**Target Platform**: Docker containerized API service on AWS
**Project Type**: Web API extension (integrates with existing backend/frontend structure)
**Performance Goals**: <2 seconds response time, 5-minute document processing, 30-minute sandbox expiry
**Constraints**: <200ms p95 for assistant retrieval, 99.9% uptime during zoo hours, 50MB file upload limit
**Scale/Scope**: 50+ animal assistants, 100+ concurrent visitors, 500MB total knowledge base per assistant

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ I. OpenAPI-First Development
- **Compliance**: All new endpoints will be defined in openapi_spec.yaml before implementation
- **Impact**: Animal assistant management APIs will follow existing CMZ pattern
- **Action**: Extend existing spec with new assistant, personality, guardrail, and knowledge base endpoints

### ✅ II. DynamoDB Persistence
- **Compliance**: All entities (assistants, personalities, guardrails, knowledge files) persist to DynamoDB
- **Impact**: Reuse existing impl/utils/dynamo.py patterns for CRUD operations
- **Action**: Create new tables following existing naming conventions (quest-dev-*)

### ✅ III. Hexagonal Architecture
- **Compliance**: Controllers → Impl modules → Handlers pattern maintained
- **Impact**: New assistant management logic goes in impl/assistants.py and impl/sandbox.py
- **Action**: Follow existing impl/animals.py and impl/family.py patterns

### ✅ IV. Test-First with Validation Gates
- **Compliance**: Unit tests (80%+), DynamoDB integration tests, Playwright E2E tests required
- **Impact**: Test sandbox expiry, prompt merging, file upload validation, OpenAI integration
- **Action**: Extend existing test structure in openapi_server/test/

### ✅ V. Mock-First Authentication
- **Compliance**: Use existing AUTH_MODE=mock with JWT tokens for development
- **Impact**: All zoo staff have equal access (from clarifications)
- **Action**: Reuse existing auth patterns, no new roles needed

### ✅ VI. AWS MCP Integration
- **Compliance**: Use MCP servers for S3 operations, DynamoDB, and document processing
- **Impact**: Leverage existing AWS configurations and patterns
- **Action**: Document processing may need new S3 integration patterns

**Gate Status**: ✅ PASS - All constitutional principles align with feature requirements

### ✅ Post-Design Constitution Re-Check

**Re-validation after Phase 1 design completion:**

- **OpenAPI-First**: ✅ Complete OpenAPI extension defined in contracts/openapi-extension.yaml
- **DynamoDB Persistence**: ✅ 5 new tables designed following quest-dev-* naming convention
- **Hexagonal Architecture**: ✅ Implementation modules planned in impl/ following controller→impl→handler pattern
- **Test-First**: ✅ Unit, integration, and E2E test structure defined in quickstart guide
- **Mock Authentication**: ✅ Reuses existing AUTH_MODE patterns, no new complexity
- **AWS MCP Integration**: ✅ S3, DynamoDB, and document processing designed for MCP server usage

**Final Gate Status**: ✅ APPROVED - Design maintains full constitutional compliance

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
├── src/main/python/openapi_server/
│   ├── controllers/                    # Generated - animal_assistant_controller.py
│   ├── models/                         # Generated - assistant models
│   ├── impl/                          # Implementation modules
│   │   ├── assistants.py              # NEW - Assistant CRUD logic
│   │   ├── sandbox.py                 # NEW - Sandbox management
│   │   ├── personalities.py           # NEW - Personality management
│   │   ├── guardrails.py              # NEW - Guardrail management
│   │   ├── knowledge_base.py          # NEW - Knowledge base file handling
│   │   └── utils/
│   │       ├── dynamo.py              # Existing - DynamoDB utilities
│   │       ├── openai_integration.py  # NEW - OpenAI API wrapper
│   │       └── prompt_merger.py       # NEW - Personality + guardrail merging
│   └── test/                          # Generated + implementation tests
│       ├── test_assistants.py         # NEW - Assistant API tests
│       ├── test_sandbox.py            # NEW - Sandbox functionality tests
│       └── test_prompt_merger.py      # NEW - Prompt merging tests
└── openapi_spec.yaml                  # Extended with assistant endpoints

frontend/src/
├── components/
│   ├── assistants/                    # NEW - Assistant management UI
│   │   ├── AssistantForm.tsx          # NEW - Create/edit assistants
│   │   ├── SandboxTester.tsx          # NEW - Sandbox testing interface
│   │   └── KnowledgeBaseUpload.tsx    # NEW - File upload component
│   └── shared/                        # Existing shared components
├── pages/
│   ├── AssistantManagement.tsx        # NEW - Main assistant page
│   └── SandboxTesting.tsx             # NEW - Sandbox testing page
├── services/
│   ├── AssistantService.ts            # NEW - API client for assistants
│   └── SandboxService.ts              # NEW - API client for sandbox
└── types/
    └── AssistantTypes.ts               # NEW - TypeScript interfaces
```

**Structure Decision**: Web application structure extending existing CMZ backend/frontend. New assistant management functionality integrates with existing animal, family, and user management patterns. Backend follows OpenAPI-first with impl/ modules, frontend adds new React components and services.

## Complexity Tracking

*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |

