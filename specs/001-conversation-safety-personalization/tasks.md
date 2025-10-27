# Tasks: Conversation Safety and Personalization System

**Input**: Design documents from `/specs/001-conversation-safety-personalization/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and enhanced structure for safety and personalization features

- [x] T001 Create feature branch 001-conversation-safety-personalization from main
- [x] T002 Add OpenAI dependencies to backend/api/src/main/python/requirements.txt
- [x] T003 [P] Update environment variables in .env.local for OpenAI API and guardrails configuration
- [x] T004 [P] Configure backend/api/src/main/python/openapi_server/impl/ directory structure for new modules

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Update backend/api/openapi_spec.yaml with new guardrails, context, and privacy endpoints from contracts/
- [x] T006 Execute make generate-api to create new controllers and models for safety features
- [x] T007 [P] Create DynamoDB table schema script for 5 new tables in backend/api/scripts/create_safety_tables.py
- [x] T008 [P] Implement OpenAI integration utility in backend/api/src/main/python/openapi_server/impl/utils/openai_integration.py
- [x] T009 [P] Create base DynamoDB utilities for new tables in backend/api/src/main/python/openapi_server/impl/utils/safety_dynamo.py
- [x] T010 [P] Implement error handling patterns for safety violations in backend/api/src/main/python/openapi_server/impl/utils/safety_errors.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Guardrails Protection (Priority: P1) 🎯 MVP

**Goal**: Implement comprehensive content safety system to prevent inappropriate or inaccurate responses in all animal conversations

**Independent Test**: Test by attempting conversations with inappropriate prompts and verifying 100% appropriate educational responses with safety warnings

### Implementation for User Story 1

- [ ] T011 [P] [US1] Create GuardrailsConfig model mapping in backend/api/src/main/python/openapi_server/impl/models/guardrails_config.py
- [ ] T012 [P] [US1] Create ContentValidation model mapping in backend/api/src/main/python/openapi_server/impl/models/content_validation.py
- [ ] T013 [P] [US1] Implement content moderation service in backend/api/src/main/python/openapi_server/impl/utils/content_moderator.py
- [ ] T014 [US1] Implement guardrails configuration management in backend/api/src/main/python/openapi_server/impl/guardrails.py
- [ ] T015 [US1] Integrate guardrails validation into conversation pipeline in backend/api/src/main/python/openapi_server/impl/conversation.py
- [ ] T016 [US1] Implement guardrails controller handlers in backend/api/src/main/python/openapi_server/impl/handlers.py
- [ ] T017 [US1] Add safety analytics tracking in backend/api/src/main/python/openapi_server/impl/utils/safety_analytics.py
- [ ] T018 [US1] Create frontend safety service in frontend/src/services/GuardrailsService.ts
- [ ] T019 [P] [US1] Add safety status component in frontend/src/components/safety/SafetyStatus.tsx
- [ ] T020 [P] [US1] Add content filter indicator in frontend/src/components/safety/ContentFilter.tsx

**Checkpoint**: At this point, all animal conversations should have active safety guardrails with 100% inappropriate content blocking

---

## Phase 4: User Story 2 - Personal Context Retention (Priority: P1)

**Goal**: Implement user context tracking and personalization across conversations to create engaging, personalized educational experiences

**Independent Test**: Have a user share preferences in one conversation, start new conversations, and verify animals reference previous interests appropriately

### Implementation for User Story 2

- [ ] T021 [P] [US2] Create UserContextProfile model mapping in backend/api/src/main/python/openapi_server/impl/models/user_context.py
- [ ] T022 [P] [US2] Create ConversationAnalytics model mapping in backend/api/src/main/python/openapi_server/impl/models/conversation_analytics.py
- [ ] T023 [P] [US2] Implement context extraction utilities in backend/api/src/main/python/openapi_server/impl/utils/context_extractor.py
- [ ] T024 [P] [US2] Implement AI-powered context summarization in backend/api/src/main/python/openapi_server/impl/utils/context_summarizer.py
- [ ] T025 [US2] Implement user context management service in backend/api/src/main/python/openapi_server/impl/user_context.py
- [ ] T026 [US2] Integrate context injection into conversation system in backend/api/src/main/python/openapi_server/impl/conversation.py (enhance existing)
- [ ] T027 [US2] Implement context controller handlers in backend/api/src/main/python/openapi_server/impl/handlers.py (enhance existing)
- [ ] T028 [US2] Add context analytics and tracking in backend/api/src/main/python/openapi_server/impl/utils/context_analytics.py
- [ ] T029 [US2] Create frontend context service in frontend/src/services/ContextService.ts
- [ ] T030 [P] [US2] Add user preferences component in frontend/src/components/context/UserPreferences.tsx
- [ ] T031 [P] [US2] Add context summary viewer in frontend/src/components/context/ContextSummary.tsx

**Checkpoint**: At this point, returning users should experience personalized conversations that reference their interests and previous interactions

---

## Phase 5: User Story 3 - Parent Privacy Controls (Priority: P2)

**Goal**: Provide parents with comprehensive visibility and control over their children's conversation data and personal context for COPPA compliance

**Independent Test**: Have a parent log in, view child's conversation history, delete specific context items, and verify changes take immediate effect

### Implementation for User Story 3

- [ ] T032 [P] [US3] Create PrivacyAuditLog model mapping in backend/api/src/main/python/openapi_server/impl/models/privacy_audit.py
- [ ] T033 [P] [US3] Create ChildSummary model mapping in backend/api/src/main/python/openapi_server/impl/models/child_summary.py
- [ ] T034 [P] [US3] Implement privacy audit logging utilities in backend/api/src/main/python/openapi_server/impl/utils/privacy_audit.py
- [ ] T035 [P] [US3] Implement data deletion utilities in backend/api/src/main/python/openapi_server/impl/utils/data_deletion.py
- [ ] T036 [US3] Implement privacy controls service in backend/api/src/main/python/openapi_server/impl/privacy_controls.py
- [ ] T037 [US3] Implement privacy controller handlers in backend/api/src/main/python/openapi_server/impl/handlers.py (enhance existing)
- [ ] T038 [US3] Add COPPA compliance validation in backend/api/src/main/python/openapi_server/impl/utils/coppa_validator.py
- [ ] T039 [US3] Create frontend privacy service in frontend/src/services/PrivacyService.ts
- [ ] T040 [P] [US3] Create privacy dashboard page in frontend/src/pages/PrivacyDashboard.tsx
- [ ] T041 [P] [US3] Add conversation viewer component in frontend/src/components/privacy/ConversationViewer.tsx
- [ ] T042 [P] [US3] Add data export dialog in frontend/src/components/privacy/DataExportDialog.tsx
- [ ] T043 [P] [US3] Add selective deletion interface in frontend/src/components/privacy/DataDeletionControl.tsx
- [ ] T044 [US3] Add privacy controls to existing parent dashboard integration

**Checkpoint**: At this point, parents should have complete visibility and deletion control over their children's conversation data with full audit trails

---

## Phase 6: User Story 4 - Context Summarization (Priority: P2)

**Goal**: Implement intelligent conversation history compression to maintain personalization effectiveness while optimizing system performance and costs

**Independent Test**: Create extensive conversation history (20+ conversations), verify key information preservation in summaries with 60% token reduction

### Implementation for User Story 4

- [ ] T045 [P] [US4] Create ContextSummaryArchive model mapping in backend/api/src/main/python/openapi_server/impl/models/context_archive.py
- [ ] T046 [P] [US4] Enhance context summarization with archival in backend/api/src/main/python/openapi_server/impl/utils/context_summarizer.py (enhance existing)
- [ ] T047 [P] [US4] Implement summarization quality scoring in backend/api/src/main/python/openapi_server/impl/utils/summarization_quality.py
- [ ] T048 [P] [US4] Add background summarization scheduler in backend/api/src/main/python/openapi_server/impl/utils/summarization_scheduler.py
- [ ] T049 [US4] Integrate automatic summarization triggers in backend/api/src/main/python/openapi_server/impl/user_context.py (enhance existing)
- [ ] T050 [US4] Add summarization monitoring in backend/api/src/main/python/openapi_server/impl/utils/context_analytics.py (enhance existing)
- [ ] T051 [US4] Add manual summarization endpoint in backend/api/src/main/python/openapi_server/impl/handlers.py (enhance existing)
- [ ] T052 [P] [US4] Add summarization status dashboard in frontend/src/components/context/SummarizationStatus.tsx
- [ ] T053 [P] [US4] Add context compression metrics in frontend/src/components/context/CompressionMetrics.tsx

**Checkpoint**: At this point, long-term users should experience efficient context management with preserved personalization and optimized performance

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: System optimization, monitoring, and production readiness improvements

- [ ] T054 [P] Add comprehensive error handling across all safety modules in backend/api/src/main/python/openapi_server/impl/utils/safety_error_handler.py
- [ ] T055 [P] Implement performance monitoring for all safety operations in backend/api/src/main/python/openapi_server/impl/utils/performance_monitor.py
- [ ] T056 [P] Add caching layer for frequent context queries in backend/api/src/main/python/openapi_server/impl/utils/context_cache.py
- [ ] T057 [P] Create comprehensive safety and personalization documentation in docs/safety-personalization-guide.md
- [ ] T058 [P] Add safety configuration management interface in frontend/src/components/admin/SafetyConfigPanel.tsx
- [ ] T059 [P] Implement automated safety testing suite in backend/api/src/main/python/tests/safety/
- [ ] T060 [P] Add context validation and consistency checks in backend/api/src/main/python/tests/context/
- [ ] T061 [P] Create E2E privacy workflow tests in backend/api/src/main/python/tests/playwright/specs/privacy-workflow.spec.js
- [ ] T062 Security audit of all personal data handling and OpenAI integrations
- [ ] T063 Performance optimization based on monitoring data and user feedback
- [ ] T064 Run complete quickstart.md validation with all features enabled

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P1 → P2 → P2)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 - Guardrails (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 - Context Retention (P1)**: Can start after Foundational (Phase 2) - Integrates with US1 guardrails but independently testable
- **User Story 3 - Privacy Controls (P2)**: Can start after Foundational (Phase 2) - Depends on US2 context data but independently testable
- **User Story 4 - Summarization (P2)**: Can start after Foundational (Phase 2) - Enhances US2 context system but independently testable

### Within Each User Story

- Models before services
- Utilities before main implementation
- Services before controllers/handlers
- Backend implementation before frontend integration
- Core functionality before UI components
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, User Stories 1 & 2 (both P1) can start in parallel
- All models within a story marked [P] can run in parallel
- All utility modules within a story marked [P] can run in parallel
- All frontend components within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1 (Guardrails)

```bash
# Launch all models for User Story 1 together:
Task: "Create GuardrailsConfig model mapping in backend/api/src/main/python/openapi_server/impl/models/guardrails_config.py"
Task: "Create ContentValidation model mapping in backend/api/src/main/python/openapi_server/impl/models/content_validation.py"

# Launch all utilities for User Story 1 together:
Task: "Implement content moderation service in backend/api/src/main/python/openapi_server/impl/utils/content_moderator.py"
Task: "Add safety analytics tracking in backend/api/src/main/python/openapi_server/impl/utils/safety_analytics.py"

# Launch all frontend components for User Story 1 together:
Task: "Add safety status component in frontend/src/components/safety/SafetyStatus.tsx"
Task: "Add content filter indicator in frontend/src/components/safety/ContentFilter.tsx"
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only - Both P1)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Guardrails Protection)
4. Complete Phase 4: User Story 2 (Personal Context Retention)
5. **STOP and VALIDATE**: Test both P1 stories independently and together
6. Deploy/demo safety + personalization MVP

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 (Guardrails) → Test independently → Deploy/Demo (Safety MVP!)
3. Add User Story 2 (Context) → Test independently → Deploy/Demo (Personalization MVP!)
4. Add User Story 3 (Privacy) → Test independently → Deploy/Demo (Compliance Complete!)
5. Add User Story 4 (Summarization) → Test independently → Deploy/Demo (Performance Optimized!)
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Guardrails Protection)
   - Developer B: User Story 2 (Personal Context Retention)
   - Developer C: User Story 3 (Privacy Controls) - can start after US2 context models
   - Developer D: User Story 4 (Context Summarization) - can start with US2
3. Stories complete and integrate independently

---

## Success Criteria Mapping

**User Story 1 Success Criteria**:
- SC-001: 100% of AI responses pass guardrails validation ✓
- SC-007: Guardrails intervention rate optimization ✓

**User Story 2 Success Criteria**:
- SC-002: 40% increased engagement with personalization ✓
- SC-006: Sub-2 second response times with context ✓
- SC-008: 95% user satisfaction with memory ✓

**User Story 3 Success Criteria**:
- SC-004: Parent data access within 2 clicks ✓
- SC-005: Privacy deletions under 5 seconds ✓

**User Story 4 Success Criteria**:
- SC-003: 60% token reduction with 90% effectiveness ✓
- SC-006: Performance optimization support ✓

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- OpenAPI-first approach: all endpoints defined before implementation
- DynamoDB integration follows existing CMZ patterns
- All safety features integrate with existing conversation system
- Privacy features ensure COPPA compliance with full audit trails
- Performance monitoring throughout to meet <2s response requirements