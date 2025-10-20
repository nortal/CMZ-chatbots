# Tasks: CMZ Chatbots Enhancement

**Input**: Design documents from `.specify/memory/`
**Prerequisites**: plan.md (✓), spec.md (✓), constitution.md (✓)
**Organization**: Tasks grouped by phase from improvement plan, then by user story priority

## Format: `[ID] [P?] [Phase] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Phase]**: Which phase/story this task belongs to (PH1, US1, etc.)
- Include exact file paths in descriptions

## Path Conventions
- **Backend**: `backend/api/src/main/python/openapi_server/`
- **Frontend**: `frontend/src/`
- **Tests**: `backend/api/src/main/python/tests/`
- **Scripts**: `scripts/`

---

## Phase 1: Stabilization (Critical Fixes) - Week 1-2

**Purpose**: Fix critical issues blocking development without disrupting service
**Goal**: Zero 501 errors, 85% test coverage, validated forwarding chains

### Handler Forwarding Fixes (CRITICAL - Do First)

- [ ] T001 [PH1] Analyze all impl modules with validate_handler_forwarding_comprehensive.py
- [ ] T002 [PH1] Fix family.py forwarding - remove redundant handle_list_all_families, handle_list_families
- [ ] T003 [PH1] Fix users.py handle_delete_user to properly forward to handlers.py
- [ ] T004 [PH1] Regenerate impl stubs with post_openapi_generation.py for broken modules
- [ ] T005 [PH1] Validate all forwarding chains pass with zero critical failures
- [ ] T006 [P] [PH1] Document forwarding pattern in FORWARDING-PATTERN.md

### Test Coverage Improvements (HIGH Priority)

- [ ] T007 [P] [PH1] Add unit tests for uncovered handlers in `impl/handlers.py`
- [ ] T008 [P] [PH1] Create integration tests for DynamoDB operations in `impl/utils/dynamo.py`
- [ ] T009 [P] [PH1] Add contract tests for auth endpoints in `tests/unit/test_auth_contract.py`
- [ ] T010 [P] [PH1] Create family CRUD tests in `tests/integration/test_family_integration.py`
- [ ] T011 [P] [PH1] Add animal configuration tests in `tests/integration/test_animal_config.py`
- [ ] T012 [PH1] Run coverage report and verify ≥85% coverage achieved

### E2E Test Suite Expansion

- [ ] T013 [P] [PH1] Create Playwright test for admin role login and dashboard
- [ ] T014 [P] [PH1] Create Playwright test for zookeeper animal configuration flow
- [ ] T015 [P] [PH1] Create Playwright test for educator family management
- [ ] T016 [P] [PH1] Create Playwright test for parent viewing children's activity
- [ ] T017 [P] [PH1] Create Playwright test for visitor chat with animal
- [ ] T018 [P] [PH1] Create Playwright test for student educational interaction
- [ ] T019 [PH1] Validate all tests pass in ≥5/6 browsers

---

## Phase 2: Observability (Week 3-4)

**Purpose**: Implement monitoring to understand system behavior
**Goal**: Full request tracing, real-time metrics, <5min detection time

### Structured Logging

- [ ] T020 [PH2] Create logging configuration in `impl/utils/logger.py`
- [ ] T021 [P] [PH2] Add request ID generation middleware in `__main__.py`
- [ ] T022 [P] [PH2] Update all handlers to use structured logging with context
- [ ] T023 [P] [PH2] Add performance timing logs to DynamoDB operations
- [ ] T024 [P] [PH2] Configure JSON formatter for CloudWatch compatibility
- [ ] T025 [PH2] Deploy and verify logs appear in CloudWatch

### Metrics Collection

- [ ] T026 [P] [PH2] Implement metrics utility in `impl/utils/metrics.py`
- [ ] T027 [P] [PH2] Add API response time metrics (p50, p95, p99)
- [ ] T028 [P] [PH2] Add ChatGPT completion duration metrics
- [ ] T029 [P] [PH2] Add DynamoDB operation latency metrics
- [ ] T030 [P] [PH2] Track active user sessions count
- [ ] T031 [P] [PH2] Monitor error rates by endpoint
- [ ] T032 [PH2] Create CloudWatch dashboard with all metrics

### Distributed Tracing

- [ ] T033 [PH2] Configure AWS X-Ray SDK in `__main__.py`
- [ ] T034 [P] [PH2] Add X-Ray tracing to Flask routes
- [ ] T035 [P] [PH2] Add X-Ray segments for DynamoDB calls
- [ ] T036 [P] [PH2] Add X-Ray segments for ChatGPT API calls
- [ ] T037 [PH2] Create X-Ray service map
- [ ] T038 [PH2] Set up alerts for high latency traces

---

## Phase 3: Performance Optimization (Week 5-6)

**Purpose**: Reduce latency and costs while maintaining quality
**Goal**: API p95 <200ms, 50% DynamoDB cost reduction, <2s page load

### Caching Layer Implementation

- [ ] T039 [PH3] Set up Redis/ElastiCache connection in `impl/utils/cache.py`
- [ ] T040 [P] [PH3] Cache animal list with 1-hour TTL
- [ ] T041 [P] [PH3] Cache animal details with 1-hour TTL
- [ ] T042 [P] [PH3] Cache user sessions with 30-minute TTL
- [ ] T043 [P] [PH3] Cache static configuration with 24-hour TTL
- [ ] T044 [PH3] Implement cache invalidation on configuration updates
- [ ] T045 [PH3] Monitor cache hit rates and adjust TTLs

### Database Optimization

- [ ] T046 [P] [PH3] Add GSI for common query patterns in DynamoDB
- [ ] T047 [P] [PH3] Implement batch get operations in `impl/utils/dynamo.py`
- [ ] T048 [P] [PH3] Implement batch write operations for bulk updates
- [ ] T049 [P] [PH3] Add connection pooling for boto3 clients
- [ ] T050 [PH3] Measure and verify 50% cost reduction

### Frontend Optimization

- [ ] T051 [P] [PH3] Implement code splitting for React routes
- [ ] T052 [P] [PH3] Add lazy loading for route components
- [ ] T053 [P] [PH3] Tree shake unused dependencies
- [ ] T054 [P] [PH3] Convert images to WebP format
- [ ] T055 [P] [PH3] Set up CDN for static assets
- [ ] T056 [PH3] Verify <2 second initial load time

---

## User Story 1: Enhanced Visitor Chat (Priority: P1)

**Goal**: Improve chat experience with context persistence and quick replies
**Independent Test**: Start chat, use quick reply, reload page, continue conversation

- [ ] T057 [US1] Implement conversation context storage in DynamoDB
- [ ] T058 [P] [US1] Add context retrieval on chat session resume
- [ ] T059 [P] [US1] Create quick reply suggestions based on animal type
- [ ] T060 [P] [US1] Add reaction emojis to animal responses in frontend
- [ ] T061 [P] [US1] Implement share conversation link generator
- [ ] T062 [US1] Create E2E test for enhanced chat features

---

## User Story 2: Educational Modules (Priority: P2)

**Goal**: Add structured lessons with progress tracking
**Independent Test**: Start lesson, complete quiz, receive badge, view certificate

- [ ] T063 [US2] Create lesson content schema in `models/lesson.py`
- [ ] T064 [US2] Add lessons table to DynamoDB
- [ ] T065 [P] [US2] Create age-appropriate lesson paths (5-8, 9-12, 13+)
- [ ] T066 [P] [US2] Implement progress tracking in user profile
- [ ] T067 [P] [US2] Create quiz component in `frontend/src/components/Quiz.tsx`
- [ ] T068 [P] [US2] Design achievement badges (10 types)
- [ ] T069 [P] [US2] Generate completion certificates (PDF)
- [ ] T070 [US2] Create E2E test for complete education flow

---

## User Story 3: Multi-Language Support (Priority: P2)

**Goal**: Enable Spanish and Mandarin conversations
**Independent Test**: Switch language, chat in Spanish, verify responses in Spanish

- [ ] T071 [US3] Install and configure react-i18next in frontend
- [ ] T072 [P] [US3] Extract all UI strings to translation files
- [ ] T073 [P] [US3] Translate UI strings to Spanish
- [ ] T074 [P] [US3] Translate UI strings to Mandarin
- [ ] T075 [US3] Add language selector to header component
- [ ] T076 [P] [US3] Configure ChatGPT for multi-language responses
- [ ] T077 [P] [US3] Add language preference to user profile
- [ ] T078 [US3] Create E2E test for language switching

---

## User Story 4: Admin Analytics Dashboard (Priority: P3)

**Goal**: Provide real-time insights on usage and engagement
**Independent Test**: View dashboard, filter by date, export report

- [ ] T079 [US4] Create analytics aggregation Lambda function
- [ ] T080 [P] [US4] Design analytics dashboard UI in `frontend/src/pages/Analytics.tsx`
- [ ] T081 [P] [US4] Implement date range filtering
- [ ] T082 [P] [US4] Add usage metrics visualization (Chart.js)
- [ ] T083 [P] [US4] Create engagement heatmap component
- [ ] T084 [P] [US4] Add CSV export functionality
- [ ] T085 [US4] Create E2E test for analytics features

---

## Phase 5: Innovation Features (Week 11-12)

**Goal**: Differentiate with voice and AR capabilities
**Note**: These are stretch goals after core improvements

### Voice Interaction (Optional)

- [ ] T086 [P] [PH5] Integrate Amazon Polly for TTS
- [ ] T087 [P] [PH5] Configure unique voice per animal
- [ ] T088 [P] [PH5] Implement Web Speech API for STT
- [ ] T089 [PH5] Add voice toggle button to chat interface
- [ ] T090 [PH5] Ensure WCAG AAA compliance

### AR Integration (Optional)

- [ ] T091 [PH5] Set up AR.js or 8th Wall framework
- [ ] T092 [P] [PH5] Create AR markers for exhibits
- [ ] T093 [P] [PH5] Design 3D animal models
- [ ] T094 [PH5] Implement AR chat overlay
- [ ] T095 [PH5] Test on iOS and Android devices

---

## Dependencies & Execution Order

### Critical Path
```
Phase 1 (Stabilization) → Phase 2 (Observability) → Phase 3 (Performance)
                      ↓
              User Stories (can start after Phase 1)
                      ↓
              Phase 5 (Innovation - optional)
```

### Parallel Execution Opportunities

**Phase 1 Parallel Groups:**
- Group A: Handler forwarding fixes (T001-T006)
- Group B: Test improvements (T007-T012)
- Group C: E2E tests (T013-T019)

**Phase 2 Parallel Groups:**
- Group A: Logging (T020-T025)
- Group B: Metrics (T026-T032)
- Group C: Tracing (T033-T038)

**Phase 3 Parallel Groups:**
- Group A: Caching (T039-T045)
- Group B: Database (T046-T050)
- Group C: Frontend (T051-T056)

**User Stories:** Each story (US1-US4) can be implemented independently in parallel

---

## Implementation Strategy

### MVP Delivery Approach
1. **Week 1-2**: Complete Phase 1 - System is stable, tests pass
2. **Week 3-4**: Complete Phase 2 - Full visibility into system behavior
3. **Week 5-6**: Complete Phase 3 - Performance optimized, costs reduced
4. **Week 7-8**: Implement P1 user stories (Enhanced Chat)
5. **Week 9-10**: Implement P2 user stories (Education, Multi-language)
6. **Week 11-12**: Implement P3 stories and innovation features

### Success Metrics
- **Phase 1**: ✅ 0 handler errors, 85% test coverage, 95% E2E pass rate
- **Phase 2**: ✅ All requests traced, <5min incident detection
- **Phase 3**: ✅ API p95 <200ms, 50% cost reduction, <2s load time
- **User Stories**: ✅ Each story independently testable and deployable
- **Overall**: ✅ 30% engagement increase, 4.5/5 user satisfaction

---

## Task Summary

**Total Tasks**: 95
- Phase 1 (Stabilization): 19 tasks
- Phase 2 (Observability): 19 tasks
- Phase 3 (Performance): 18 tasks
- User Story 1 (Chat): 6 tasks
- User Story 2 (Education): 8 tasks
- User Story 3 (Multi-language): 8 tasks
- User Story 4 (Analytics): 7 tasks
- Phase 5 (Innovation): 10 tasks

**Parallel Opportunities**: 70+ tasks can run in parallel within their groups
**Independent Stories**: 4 user stories can be developed simultaneously
**Critical Path Length**: 6 weeks for core improvements, 12 weeks total