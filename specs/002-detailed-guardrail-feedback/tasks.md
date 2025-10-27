# Tasks: Detailed Guardrail Feedback

**Input**: Design documents from `/specs/002-detailed-guardrail-feedback/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and OpenAPI schema enhancement

- [X] T001 Update OpenAPI spec with enhanced validation response schema in backend/api/openapi_spec.yaml
- [X] T002 [P] Generate enhanced models using make generate-api and validate TriggeredRule entities
- [X] T003 [P] Verify existing content moderation infrastructure in backend/api/src/main/python/openapi_server/impl/utils/content_moderator.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Create base TriggeredRule model validation logic in backend/api/src/main/python/openapi_server/models/triggered_rule.py
- [X] T005 [P] Enhance ValidationResponse model with triggered rules support in backend/api/src/main/python/openapi_server/models/validation_response.py
- [X] T006 [P] Create rule ranking and confidence filtering utilities in backend/api/src/main/python/openapi_server/impl/utils/rule_processor.py
- [X] T007 Create enhanced content validation service in backend/api/src/main/python/openapi_server/impl/utils/enhanced_content_moderator.py
- [X] T008 [P] Add TypeScript interfaces for triggered rules in frontend/src/types/GuardrailTypes.ts
- [X] T009 [P] Enhance GuardrailsService with detailed validation calls in frontend/src/services/GuardrailsService.ts

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Content Administrator Reviews Triggered Rules (Priority: P1) 🎯 MVP

**Goal**: Enable content administrators to see detailed information about triggered guardrail rules including categories, severity levels, and confidence scores

**Independent Test**: Submit test content "Can you tell me about violence?" in Safety Management interface and verify triggered rule details appear with rule names, categories, severity levels, and confidence scores

### Implementation for User Story 1

- [ ] T010 [P] [US1] Implement detailed rule trigger detection in backend/api/src/main/python/openapi_server/impl/guardrails.py
- [ ] T011 [P] [US1] Add OpenAI moderation result processing in backend/api/src/main/python/openapi_server/impl/utils/content_moderator.py
- [ ] T012 [US1] Integrate enhanced validation in validation controller endpoint in backend/api/src/main/python/openapi_server/controllers/guardrails_controller.py
- [ ] T013 [P] [US1] Create TriggeredRulesDisplay component in frontend/src/components/safety/TriggeredRulesDisplay.tsx
- [ ] T014 [P] [US1] Create CollapsibleRuleCard component in frontend/src/components/safety/CollapsibleRuleCard.tsx
- [ ] T015 [US1] Integrate triggered rules display in SafetyManagement.tsx testing interface
- [ ] T016 [US1] Add severity-based visual indicators and WCAG 2.1 AA accessibility features
- [ ] T017 [US1] Implement rule ranking by severity then confidence in frontend display

**Checkpoint**: At this point, User Story 1 should be fully functional - administrators can see detailed triggered rule information

---

## Phase 4: User Story 2 - Educational Content Creator Understands Rejection Reasons (Priority: P2)

**Goal**: Enable educational content creators to see specific rule text and educational guidance for improvement

**Independent Test**: Submit educational content with questionable elements and verify rule-specific feedback helps creators understand modification needs

### Implementation for User Story 2

- [ ] T018 [P] [US2] Add educational guidance generation logic in backend/api/src/main/python/openapi_server/impl/utils/educational_guidance.py
- [ ] T019 [P] [US2] Enhance triggered rule user messages with educational context in backend/api/src/main/python/openapi_server/impl/guardrails.py
- [ ] T020 [US2] Add safe alternative content suggestions in validation response processing
- [ ] T021 [P] [US2] Create educational guidance display component in frontend/src/components/safety/EducationalGuidance.tsx
- [ ] T022 [US2] Integrate educational guidance in TriggeredRulesDisplay component
- [ ] T023 [US2] Add rule-specific improvement suggestions in CollapsibleRuleCard component

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - educators get specific improvement guidance

---

## Phase 5: User Story 3 - System Administrator Analyzes Rule Effectiveness (Priority: P3)

**Goal**: Enable system administrators to view detailed analytics about rule frequency, accuracy, and effectiveness

**Independent Test**: Review rule trigger analytics over time periods and identify rules that may need adjustment based on frequency and confidence patterns

### Implementation for User Story 3

- [ ] T024 [P] [US3] Create RuleAnalyticsHourly DynamoDB table schema in backend/api/src/main/python/openapi_server/impl/utils/analytics_schema.py
- [ ] T025 [P] [US3] Implement hourly analytics aggregation in backend/api/src/main/python/openapi_server/impl/utils/safety_analytics.py
- [ ] T026 [US3] Create rule effectiveness calculation service in backend/api/src/main/python/openapi_server/impl/analytics.py
- [ ] T027 [P] [US3] Add analytics endpoints for rule effectiveness queries in backend/api/src/main/python/openapi_server/controllers/analytics_controller.py
- [ ] T028 [P] [US3] Create RuleAnalytics component in frontend/src/components/safety/RuleAnalytics.tsx
- [ ] T029 [P] [US3] Add effectiveness metrics dashboard in frontend/src/components/safety/EffectivenessDashboard.tsx
- [ ] T030 [US3] Integrate analytics display in SafetyManagement.tsx interface
- [ ] T031 [US3] Add 24-hour rolling window queries with hourly update polling

**Checkpoint**: All user stories should now be independently functional - complete rule analytics system

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and system optimization

- [ ] T032 [P] Add comprehensive error handling across all validation endpoints
- [ ] T033 [P] Implement performance optimization for rule processing (target <20% overhead increase)
- [ ] T034 [P] Add logging for rule trigger events and analytics processing
- [ ] T035 [P] Create unit tests for rule processing utilities in backend/api/src/main/python/openapi_server/test/test_rule_processor.py
- [ ] T036 [P] Create integration tests for enhanced validation in backend/api/src/main/python/openapi_server/test/test_enhanced_validation.py
- [ ] T037 [P] Create E2E tests for triggered rules display in tests/playwright/specs/ui-features/detailed-guardrail-feedback.spec.js
- [ ] T038 [P] Add accessibility validation for triggered rules components
- [ ] T039 Code cleanup and refactoring for enhanced validation system
- [ ] T040 Run quickstart.md validation and update documentation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Builds on US1 TriggeredRulesDisplay but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Independent analytics system, no dependencies on US1/US2

### Within Each User Story

- Backend model enhancements before frontend components
- Core validation logic before UI integration
- Component creation before integration
- Basic functionality before advanced features

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel
- Backend and frontend tasks within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch backend and frontend models for User Story 1 together:
Task: "Implement detailed rule trigger detection in backend/api/src/main/python/openapi_server/impl/guardrails.py"
Task: "Add OpenAI moderation result processing in backend/api/src/main/python/openapi_server/impl/utils/content_moderator.py"
Task: "Create TriggeredRulesDisplay component in frontend/src/components/safety/TriggeredRulesDisplay.tsx"
Task: "Create CollapsibleRuleCard component in frontend/src/components/safety/CollapsibleRuleCard.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (OpenAPI schema enhancement)
2. Complete Phase 2: Foundational (CRITICAL - core models and utilities)
3. Complete Phase 3: User Story 1 (administrator rule visibility)
4. **STOP and VALIDATE**: Test triggered rules display independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Enhanced validation foundation ready
2. Add User Story 1 → Test triggered rules display → Deploy/Demo (MVP!)
3. Add User Story 2 → Test educational guidance → Deploy/Demo
4. Add User Story 3 → Test analytics dashboard → Deploy/Demo
5. Each story adds value without breaking previous functionality

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (triggered rules display)
   - Developer B: User Story 2 (educational guidance)
   - Developer C: User Story 3 (analytics system)
3. Stories complete and integrate independently

---

## Entity-to-Story Mapping

### Core Entities (from data-model.md)

- **TriggeredRule**: Primary entity for US1, used in US2 for guidance, analyzed in US3
- **ValidationResponse**: Enhanced for US1, educational context in US2, analytics source for US3
- **TriggeredRulesSummary**: Display optimization for US1, guidance context for US2
- **OpenAIModerationResult**: Separated display in US1, educational context in US2
- **RuleAnalyticsHourly**: Exclusively US3 for effectiveness analysis

### API Endpoints (from contracts/)

- **POST /guardrails/validate**: Enhanced for US1, educational guidance for US2
- **GET /analytics/rules/effectiveness**: US3 analytics dashboard
- **GET /analytics/rules/{ruleId}/metrics**: US3 detailed rule analysis

---

## Success Criteria Validation

Each user story maps to specific success criteria from spec.md:

- **US1 → SC-001**: Rule identification within 2 seconds
- **US2 → SC-002**: 40% revision cycle reduction through clearer guidance
- **US3 → SC-003**: 24-hour analytics with hourly updates
- **All → SC-004**: 95% confidence threshold for reliable feedback
- **All → SC-005**: <20% processing overhead increase
- **US3 → SC-006**: 24-hour rule effectiveness identification

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Focus on backward compatibility - existing validation must continue working
- Prioritize performance - validation overhead must stay under 20%