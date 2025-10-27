# Phase 3: OpenAI Assistants Chat Integration - Implementation Tasks

## Feature Overview

**Feature**: Migrate conversation handler to use OpenAI Assistants API with streaming support for real-time chat with document knowledge retrieval.

**Context**: Phase 1 (Assistant creation) and Phase 2 (document upload) are complete. Each animal now has a dedicated GPT Assistant with Vector Store for knowledge base documents.

**Goal**: Enable streaming chat conversations that leverage uploaded documents for contextual responses.

---

## Phase 1: Setup & Prerequisites

**Objective**: Verify Phase 1 & 2 completion and prepare for conversation migration.

### Tasks

- [ ] T001 Verify assistant_manager.py has all required methods (create, update, delete, get_info)
- [ ] T002 Verify document_handlers.py endpoints are wired in animals_controller.py
- [ ] T003 Test document upload end-to-end with sample PDF file
- [ ] T004 Review OpenAI Assistants Run API documentation for streaming patterns
- [ ] T005 Review existing streaming_response.py SSE infrastructure

---

## Phase 2: Conversation Handler Migration (User Story 1)

**User Story**: As a zoo visitor, I want to chat with an animal and receive responses that incorporate knowledge from uploaded documents.

**Test Criteria**:
- Conversation endpoint accepts message and returns Assistant response
- Assistant uses vectorStoreId from animal configuration
- Response includes citations from uploaded documents when relevant

### Tasks

- [ ] T006 [US1] Read existing conversation.py implementation to understand current Chat Completions flow
- [ ] T007 [US1] Create conversation_assistants.py with new Assistants API implementation in backend/api/src/main/python/openapi_server/impl/conversation_assistants.py
- [ ] T008 [US1] Implement create_thread() method for new conversation sessions
- [ ] T009 [US1] Implement add_message_to_thread() for user messages
- [ ] T010 [US1] Implement run_assistant() for generating responses
- [ ] T011 [US1] Implement get_assistant_response() to retrieve latest message
- [ ] T012 [US1] Add error handling for missing Assistant ID or Vector Store ID
- [ ] T013 [US1] Update conversation handler routing to use conversation_assistants.py in backend/api/src/main/python/openapi_server/impl/conversation.py
- [ ] T014 [US1] Test non-streaming conversation flow with simple question
- [ ] T015 [US1] Test conversation with document-based question to verify knowledge retrieval

---

## Phase 3: Streaming Implementation (User Story 2)

**User Story**: As a zoo visitor, I want to see the animal's response appear in real-time as it's being generated.

**Test Criteria**:
- Conversation endpoint supports streaming via SSE
- Frontend receives response chunks in real-time
- Stream includes proper event boundaries and error handling

### Tasks

- [ ] T016 [US2] Review OpenAI Assistants streaming API (client.beta.threads.runs.stream())
- [ ] T017 [US2] Implement stream_assistant_response() in conversation_assistants.py
- [ ] T018 [US2] Integrate with existing streaming_response.py SSE infrastructure
- [ ] T019 [US2] Handle streaming events: thread.message.delta, thread.run.completed, thread.run.failed
- [ ] T020 [US2] Add proper event formatting for SSE (data: prefix, double newline)
- [ ] T021 [US2] Test streaming endpoint with curl to verify SSE format
- [ ] T022 [US2] Test streaming with long response to verify chunk delivery
- [ ] T023 [US2] Add error recovery for stream interruptions

---

## Phase 4: Thread Persistence (User Story 3)

**User Story**: As a zoo visitor, I want my conversation history to persist so I can continue conversations across sessions.

**Test Criteria**:
- Thread IDs are stored in DynamoDB conversations table
- Conversations can be retrieved and continued
- Old threads are properly cleaned up

### Tasks

- [ ] T024 [US3] Update DynamoDB conversation schema to include threadId field
- [ ] T025 [US3] Modify create_conversation() to store OpenAI thread ID
- [ ] T026 [US3] Implement get_conversation_thread() to retrieve existing threads
- [ ] T027 [US3] Add conversation history retrieval from thread messages
- [ ] T028 [US3] Test conversation continuation with existing thread
- [ ] T029 [US3] Implement thread cleanup for old conversations (>30 days)

---

## Phase 5: Frontend Integration & Testing (User Story 4)

**User Story**: As a developer, I want comprehensive E2E tests validating the complete chat flow from UI to OpenAI and back.

**Test Criteria**:
- Frontend successfully initiates conversations
- Streaming responses display correctly in UI
- Document knowledge is visible in responses
- Error states are handled gracefully

### Tasks

- [ ] T030 [P] [US4] Update frontend chat component to use new streaming endpoint
- [ ] T031 [P] [US4] Test chat UI with real Assistant responses
- [ ] T032 [P] [US4] Verify document citations appear in chat UI
- [ ] T033 [US4] Create E2E Playwright test for complete chat flow
- [ ] T034 [US4] Test chat with multiple document uploads
- [ ] T035 [US4] Test error handling (no Assistant, API errors, stream failures)
- [ ] T036 [US4] Performance test: response time with large knowledge base
- [ ] T037 [US4] Load test: concurrent chat sessions

---

## Phase 6: Polish & Cross-Cutting Concerns

**Objective**: Production readiness, monitoring, and documentation.

### Tasks

- [ ] T038 [P] Add comprehensive logging for all Assistant API calls
- [ ] T039 [P] Implement usage tracking for OpenAI API costs
- [ ] T040 [P] Add monitoring for conversation success/failure rates
- [ ] T041 [P] Document Assistant API integration in CLAUDE.md
- [ ] T042 [P] Create admin guide for document management
- [ ] T043 [P] Add rate limiting for chat endpoints
- [ ] T044 Conduct security review of API key handling
- [ ] T045 Create rollback plan if Assistant API fails
- [ ] T046 Final integration test with all features enabled

---

## Dependencies

```
Phase 1 (Setup)
    ↓
Phase 2 (Conversation Migration - US1)
    ↓
Phase 3 (Streaming - US2)
    ↓
Phase 4 (Thread Persistence - US3)
    ↓
Phase 5 (Frontend Integration - US4)
    ↓
Phase 6 (Polish)
```

**Note**: Phases 2, 3, and 4 are sequential. Phase 5 tasks can run in parallel with Phase 6 polish tasks.

---

## Parallel Execution Opportunities

**Within Phase 2 (US1)**:
- T007-T011 (implementation methods) can be built in parallel
- T014-T015 (testing) must be sequential

**Within Phase 3 (US2)**:
- T016-T020 (streaming implementation) sequential
- T021-T023 (testing) sequential after implementation

**Within Phase 4 (US3)**:
- T024-T027 (implementation) can be parallelized by concern
- T028-T029 (testing) sequential

**Within Phase 5 (US4)**:
- T030-T032 (frontend) can be parallel
- T033-T037 (testing) sequential

**Phase 6**:
- T038-T043 are fully parallelizable
- T044-T046 must be sequential

---

## Implementation Strategy

**MVP Scope** (Minimum Viable Product):
- Phase 1: Setup verification
- Phase 2: Basic conversation with Assistant (US1)
- Test: Single conversation with document-based question works

**Incremental Delivery**:
1. **Week 1**: Phases 1-2 (Basic conversation working)
2. **Week 2**: Phase 3 (Streaming enabled)
3. **Week 3**: Phase 4 (Persistence working)
4. **Week 4**: Phases 5-6 (Frontend integration + polish)

**Testing Approach**:
- Contract tests for each Assistant API method
- Integration tests for conversation flow
- E2E tests for complete user journey
- Performance benchmarks before production

---

## Task Summary

- **Total Tasks**: 46
- **Phase 1 (Setup)**: 5 tasks
- **Phase 2 (US1 - Conversation)**: 10 tasks
- **Phase 3 (US2 - Streaming)**: 8 tasks
- **Phase 4 (US3 - Persistence)**: 6 tasks
- **Phase 5 (US4 - Frontend/Testing)**: 8 tasks
- **Phase 6 (Polish)**: 9 tasks
- **Parallelizable Tasks**: 15 (marked with [P])

**Estimated Completion**: 3-4 weeks with systematic implementation

---

## Next Steps

1. Start with Phase 1 verification tasks (T001-T005)
2. Move to Phase 2 conversation migration (T006-T015)
3. Add streaming support in Phase 3 (T016-T023)
4. Implement persistence in Phase 4 (T024-T029)
5. Complete frontend integration and testing (T030-T037)
6. Polish and production prep (T038-T046)

**Ready to begin**: All prerequisites from Phase 1 & 2 are complete. Start with T001.
