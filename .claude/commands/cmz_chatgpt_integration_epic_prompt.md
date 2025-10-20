# Epic Generator: CMZ Animal ChatGPT Integration

**Version**: 3.0 (Updated 2025-10-08)
**Purpose**: Generate comprehensive Jira epic and story set for OpenAI integration with DynamoDB RAG pattern
**When to Use**: Planning ChatGPT integration for animal chatbot personalities
**Expected Output**: Production-ready epic with testable stories, acceptance criteria, and data-driven story point estimates

---

## Quick Start

**Context Documents** (Read First):
- `claudedocs/PROJECT-STATE-DESCRIPTION.md` - Current project state and architecture
- `claudedocs/AI-HANDOFF-PROMPT.md` - Development standards and implementation patterns
- `CLAUDE.md` - Complete project guide and development rules
- `AUTH-ADVICE.md` - Authentication patterns and troubleshooting
- `NORTAL-JIRA-ADVICE.md` - **Nortal Jira API patterns (REQUIRED for ticket creation)**

**Your Role**: Senior Python Developer acting as project planner
**Your Task**: Create Jira epic with discrete, testable story deliverables using TDD approach
**Your Approach**:
1. Analyze each story scope with Sequential Thinking MCP
2. Define complete story with technical details
3. **CRITICAL: Write thorough E2E test specifications for EVERY acceptance criterion**
4. THEN estimate points based on analysis (including test-writing time)
5. Use Nortal Jira format for ticket creation

**TDD Requirement**: Every story MUST include detailed E2E test specifications (Playwright test code, exact test data, DynamoDB verification) that will be written BEFORE implementation code.

**You will NOT**: Write implementation code (only planning artifacts and test specifications)

---

## Epic Overview

**Title**: "Epic: Activate OpenAI Integration for Animal Chatbot Personalities"

**Business Value**: Transform mock chatbot responses into dynamic, educational AI conversations that adapt to each animal's unique personality and knowledge base stored in DynamoDB.

**Implementation Strategy - Phase 1 (MVP)**:
- **Direct OpenAI Integration**: Chat Completions API with animal personality prompts
- **Dynamic System Prompts**: Build prompts from DynamoDB animal configurations
- **Full Control**: Direct management of context, costs, and generation strategy
- **Provider-Agnostic Design**: Prepare for future multi-LLM support (OpenAI, Anthropic, local models)
- **Knowledge Base**: OUT OF SCOPE - Will be handled in separate epic

**Future Enhancements** (Phase 2+):
- Assistants API with file upload and persistent assistant objects
- Admin UI for uploading PDFs, research papers, educational materials
- OpenAI-managed file storage and retrieval

---

## Jira Integration Requirements (Nortal-Specific)

**CRITICAL**: Read `NORTAL-JIRA-ADVICE.md` for complete Jira API patterns and proven working scripts.

### Project Configuration
```bash
PROJECT_KEY="PR003946"  # Not "CMZ" - this is critical!
JIRA_BASE_URL="https://nortal.atlassian.net"
JIRA_EMAIL=<from .env.local>
JIRA_API_TOKEN=<from .env.local>
```

### Mandatory Custom Fields
```json
"customfield_10225": {"value": "Billable"}  // REQUIRED - ticket fails without this
"customfield_10014": "PR003946-XXX"         // Epic link (replace XXX with actual epic key)
```

**Note**: Do NOT include "id" field in customfield_10225 - just the value object.

### Description Format (Atlassian Document Format)

**REQUIRED**: Use ADF (Atlassian Document Format), not Markdown or plain text.

**ADF Structure Example** (from NORTAL-JIRA-ADVICE.md lines 36-58):
```json
"description": {
  "type": "doc",
  "version": 1,
  "content": [
    {
      "type": "heading",
      "attrs": {"level": 2},
      "content": [{"type": "text", "text": "Description"}]
    },
    {
      "type": "paragraph",
      "content": [{"type": "text", "text": "Story description text"}]
    },
    {
      "type": "heading",
      "attrs": {"level": 3},
      "content": [{"type": "text", "text": "Acceptance Criteria"}]
    },
    {
      "type": "bulletList",
      "content": [
        {
          "type": "listItem",
          "content": [
            {
              "type": "paragraph",
              "content": [{"type": "text", "text": "Criterion 1"}]
            }
          ]
        }
      ]
    }
  ]
}
```

### Issue Type and Priority
- **Issue Type**: Use `"Task"` (not "Story" - may fail in this project)
- **Priority**: `Medium` (default) or `High`/`Low` as appropriate

### Authentication Pattern
```bash
AUTH=$(echo -n "$JIRA_EMAIL:$JIRA_API_TOKEN" | base64)
curl -H "Authorization: Basic $AUTH" ...
```

### Proven Script Patterns
Reference successful ticket creation scripts:
- `./scripts/create_chat_epic_tickets_v2.sh` - Working example
- All patterns documented in `NORTAL-JIRA-ADVICE.md` sections 7-10

### Common Errors to Avoid
| Error | Cause | Solution |
|-------|-------|----------|
| "valid project is required" | Wrong project key | Use PROJECT_KEY="PR003946" |
| "Please select the Billable value!" | Missing customfield_10225 | Add {"value": "Billable"} |
| "The issue type selected is invalid" | Wrong issue type | Use "Task" not "Story" |
| Markdown in description shows raw | Wrong format | Use ADF format, not Markdown |

---

## Existing Implementation (Build Upon This)

**OpenAI Integration Framework** (Partially Complete):

`impl/utils/chatgpt_integration.py`:
- `ChatGPTIntegration` class - Async OpenAI client with streaming support
- `build_animal_system_prompt()` - System prompt construction from config
- `get_animal_response()` - Async OpenAI API calls (currently commented out)
- `stream_animal_response()` - SSE streaming support (ready to activate)
- **Status**: Complete implementation using mock data, needs OpenAI activation

`impl/conversation.py`:
- `handle_convo_turn_post()` - Processes user messages and manages conversation flow
- `generate_ai_response()` - Currently returns mock responses, needs OpenAI integration
- DynamoDB persistence to `quest-dev-conversation-turn` table
- **Status**: Needs replacement of mock logic with RAG + OpenAI pattern

`impl/chatgpt_integration.py`:
- `ChatGPTAnimalChat` class - Simple synchronous version
- Mock response generation for testing
- **Status**: Stub implementation, may be deprecated in favor of async version

---

## API Endpoints (DO NOT Change)

These endpoints already exist and have frontend integration:

```yaml
# Chat Interaction
POST /convo_turn
  Request: { sessionId, animalId, message, contextSummary, metadata }
  Response: { reply, sessionId, turnId, timestamp, metadata }

# Conversation History
GET /convo_history?sessionId={id}&animalId={id}&userId={id}
  Response: { sessionId, animalId, userId, messages[], metadata }

# Animal Configuration
GET /animal_config?animalId={id}
  Response: AnimalConfig object with AI parameters

PATCH /animal_config?animalId={id}
  Request: AnimalConfigUpdate object
  Response: Updated AnimalConfig object
```

See `backend/api/openapi_spec.yaml` for complete API specification.

---

## Data Architecture

**DynamoDB Tables** (Already Exist):

**Animal Domain**:
- `quest-dev-animal` - Animal records (PK: animalId)
- `quest-dev-animal-config` - AI configurations (PK: animalConfigId, indexed by animalId)
- `quest-dev-animal-details` - Extended information (PK: animalDetailId, indexed by animalId)

**Conversation Domain**:
- `quest-dev-conversation` - Conversation sessions (PK: sessionId)
- `quest-dev-conversation-turn` - Individual messages (PK: turnId, indexed by sessionId)

**Note**: Knowledge Base implementation is OUT OF SCOPE for this epic and will be handled separately.

**Key Data Models**:

See `openapi_spec.yaml` lines 2491-2612 for complete `AnimalConfig` schema including:
- `systemPrompt` - AI behavior definition
- `personality` - Personality description for prompt construction
- `aiModel` - Model selection (gpt-4o-mini, gpt-4o, claude-3-sonnet, etc.)
- `temperature` - Creativity parameter (0.0-2.0, increments of 0.1)
- `topP` - Sampling parameter (0.0-1.0, increments of 0.01)
- `maxTokens` - Max response length (1-4096)
- `toolsEnabled` - Array of enabled capabilities
- `responseFormat` - Output format (text, json, markdown)
- `guardrails` - Safety and content filtering configuration

---

## Environment Configuration

**Required New Variables**:
```bash
OPENAI_API_KEY=<api-key>                    # Required for OpenAI integration
OPENAI_API_URL=https://api.openai.com/v1/chat/completions  # Optional override
OPENAI_MODEL=gpt-4o-mini                    # Default model
OPENAI_TEMPERATURE=0.7                      # Default temperature
OPENAI_MAX_TOKENS=500                       # Default max tokens
```

**Existing AWS Configuration** (Already Set):
```bash
AWS_REGION=us-west-2
AWS_PROFILE=cmz
# DynamoDB table names configured per domain
```

---

## Quality Standards & Testing Requirements

**Quality Gates** (MUST Pass Before Commit):
```bash
make quality-check    # All automated quality gates
tox                   # Unit and integration tests (100% pass required)
```

**Playwright E2E Testing** (TWO-STEP PROCESS - MANDATORY):
```bash
cd backend/api/src/main/python/tests/playwright

# Step 1: Login validation (REQUIRED FIRST)
./run-step1-validation.sh
# Success criteria: ≥5/6 browsers passing

# Step 2: Full test suite (only after Step 1 passes)
FRONTEND_URL=http://localhost:3001 npx playwright test --config config/playwright.config.js
```

**Test Users**:
- `parent1@test.cmz.org` / `testpass123` (parent role)
- `student1@test.cmz.org` / `testpass123` (student role)
- `test@cmz.org` / `testpass123` (default user)

**Test Data**:
- Test animal: `animal_1` (Pokey the Porcupine)
- Test animal config must exist in `quest-dev-animal-config`
- Test conversations in `quest-dev-conversation`

---

## CMZ Development Standards (Strict Enforcement)

**Critical Constraints**:
1. **Never modify generated code** - Controllers/models regenerate on every `make generate-api`
2. **All business logic in impl/** - Only implement in `backend/api/src/main/python/openapi_server/impl/`
3. **OpenAPI spec is source of truth** - API changes require `openapi_spec.yaml` updates first
4. **Authentication always breaks** - Validate auth after ANY OpenAPI regeneration

**Code Quality**:
- No TODO comments for core functionality
- No mock objects in production code paths
- Complete error handling with user-friendly messages (zoo visitors are end users)
- Professional language (no marketing superlatives)
- Follow existing CMZ patterns exactly

**Git Workflow**:
- Feature branches only (never main/master)
- Commit message format: `feat: [description]` with Claude Code attribution
- Session history required: `/history/{initials}_{date}_{time}.md`

**Testing Requirements**:
- Unit tests for all new functions (pytest)
- Integration tests for DynamoDB operations
- Playwright Step 1 validation before full E2E suite
- Coverage target: ≥90% for new integration code

**Test-Driven Development (TDD)**:
- **CRITICAL**: Write E2E tests BEFORE implementing code
- Acceptance criteria MUST be testable with E2E tests (Playwright)
- Development sequence: E2E test → Implementation → Test passes
- E2E tests verify acceptance criteria directly
- No acceptance criteria that cannot be E2E tested

---

## Definition of Done (All Jira Stories)

**CRITICAL**: Every story in this epic MUST meet these criteria before being marked as complete.

**Test-Driven Development (TDD)**:
- ✅ **E2E tests written BEFORE implementation code**
- ✅ **Every acceptance criterion has thorough E2E test specification** including:
  - Exact Playwright test code or cURL examples
  - Specific test data values (user credentials, DynamoDB records)
  - Precise assertions and expected outcomes
  - DynamoDB verification steps explicitly documented
- ✅ Tests fail initially (proving they test the right thing)
- ✅ Tests pass after implementation
- ✅ **Demonstrate test progression**: Run E2E tests and show:
  - Tests failed before implementation (screenshot/log)
  - Tests pass after implementation (screenshot/log)
  - No other test regressions (all other tests still pass)
  - Test results documented in session history

**Quality & Testing**:
- ✅ All quality gates pass (`tox`, `make quality-check`)
- ✅ Playwright Step 1 validation passes (≥5/6 browsers)
- ✅ Unit test coverage ≥90% for new code
- ✅ Integration tests verify functionality

**Code Standards**:
- ✅ Code committed only in feature branches (never main/master)
- ✅ No TODO comments for core functionality
- ✅ No debug artifacts (console.log, debugging code, temporary files)
- ✅ No mock objects in production code paths

**Functional Verification**:
- ✅ Authentication tested with all 5 sample users:
  - `parent1@test.cmz.org` / `testpass123`
  - `student1@test.cmz.org` / `testpass123`
  - `student2@test.cmz.org` / `testpass123`
  - `test@cmz.org` / `testpass123`
  - `user_parent_001@cmz.org` / `testpass123`
- ✅ DynamoDB read/write operations verified:
  - Data persists correctly to appropriate tables
  - Data retrieval returns expected results
  - No data corruption or loss

**Documentation**:
- ✅ Code comments added for complex logic
- ✅ API documentation updated if endpoints changed
- ✅ Session history documented in `/history/` directory
- ✅ README or relevant docs updated if needed

**Deployment Readiness**:
- ✅ All environment variables documented
- ✅ Configuration changes documented
- ✅ Migration scripts (if any) tested
- ✅ Rollback strategy documented for risky changes

**Story Completion Reporting**:
- ✅ **After E2E tests pass**, report completion to Teams channel:
  - Read appropriate ADVICE documentation for Teams reporting
  - **CRITICAL**: Send adaptive cards (NOT plain text) to Teams webhook REST endpoint
  - Include test progression summary (failing → passing, no regressions)
  - Include story key, acceptance criteria met, and session history link
  - Example: See Teams reporting patterns in project scripts

---

## Story Point Estimation Framework

### Estimation Philosophy: Analysis Before Estimation

**CRITICAL RULE**: Define complete story BEFORE estimating points.

**Correct Sequence:**
1. **Analyze** - Use Sequential Thinking MCP for complex stories
2. **Define** - Write complete description with technical approach
3. **Detail** - Write full acceptance criteria and integration tests
4. **THEN Estimate** - Points based on complete understanding of scope

**Anti-Pattern to Avoid:**
❌ "This should be 6 points, so let me define a 6-point story"
✅ "After analysis, this is 5-8 points depending on approach chosen"

### Fibonacci Point Scale

**Use Fibonacci Sequence**: 1, 2, 3, 5, 8, 13

**Point Calibration**:
- **1 point** - Trivial change, < 2 hours (config update, simple fix)
- **2 points** - Simple implementation, ~1 dev day (4-6 hours focused work)
- **3 points** - Straightforward with some complexity, ~1.5 dev days
- **5 points** - Moderate complexity, ~2.5 dev days (requires design)
- **8 points** - Significant complexity, ~4 dev days (architectural decisions)
- **13 points** - Very complex, ~6.5 dev days (break into smaller stories)

**Red Flag**: If story > 13 points, break into smaller stories

### Soft Story Pointing

**When to Use Ranges**:
- Complex stories with unknown technical challenges: **5-8 points**
- Stories dependent on external API behavior: **3-5 points**
- Stories requiring architectural decisions: **Use Sequential Thinking to refine**
- Novel implementations without established patterns: **Range + spike story**

**When to Use Specific Points**:
- Well-understood, isolated changes: **2 points**, **3 points**
- Following established patterns exactly: **2 points**
- Straightforward configuration or integration: **1-2 points**

### Confidence Levels

**High Confidence** (use specific point value):
- Existing code to activate with minimal changes
- Clear requirements, established patterns
- Similar work completed recently

**Medium Confidence** (use narrow range like 3-5):
- New code but established patterns exist
- Some unknowns but manageable scope
- Standard complexity for team

**Low Confidence** (use wide range like 5-13 or recommend spike):
- Novel implementation without patterns
- Unknown complexity or architectural questions
- Multiple dependencies or external factors
- **Recommendation**: Spike story (1-2 points) to research approach first

### Estimation Assumptions

**Document What Could Change Estimate**:
- Technical assumptions (e.g., "assumes keyword matching, not semantic search")
- Dependency assumptions (e.g., "assumes DynamoDB schema remains unchanged")
- Scope boundaries (e.g., "excludes multi-language support")
- Risk factors (e.g., "OpenAI API rate limits could require additional work")

**Example**:
```markdown
**Story Points:** 5-8 (Medium confidence)
**Assumptions:**
- Simple keyword matching: 5 points
- With caching and optimization: 6 points
- If semantic search needed: 8 points
- If custom ML model required: 13 points (recommend separate story)
**Recommendation**: Start with keyword approach (5 points), spike semantic if insufficient
```

---

## MCP Tool Usage Guidance

### Sequential Thinking MCP - Required for Story Definition

**Use `mcp__sequential-thinking__sequentialthinking` BEFORE estimating:**

**Required For:**
- Designing RAG pattern architecture and retrieval strategy
- Analyzing trade-offs between knowledge retrieval approaches
- Planning guardrails validation logic with edge cases
- Architecting provider abstraction layer
- Complex error handling and resilience strategies
- Performance analysis and optimization approaches

**Process**:
1. Read suggested story scope
2. **Invoke Sequential Thinking MCP** to analyze technical approach
3. Identify complexity factors, edge cases, unknowns
4. Evaluate alternative implementation strategies
5. Define complete story based on analysis
6. **THEN estimate points** based on discoveries from analysis

**Example Sequential Thinking Analysis**:
```
Story: Knowledge Base Retrieval (RAG Pattern)

Sequential Thinking Analysis:
Thought 1: Need to retrieve relevant knowledge from DynamoDB for user messages
Thought 2: Retrieval strategies: keyword matching, semantic search, hybrid approach
Thought 3: Keyword matching simpler but less accurate; semantic needs embeddings
Thought 4: Consider performance - 10K+ articles, query speed critical
Thought 5: Token budget management - can only include top N results in prompt
Thought 6: Edge cases - no relevant knowledge, ambiguous queries, multiple animals
Thought 7: Caching strategy could improve performance significantly
Thought 8: Recommendation - start with keyword + caching, measure accuracy

Based on Analysis:
- Chosen approach: Keyword matching with relevance scoring and caching
- Complexity: Moderate (need scoring algorithm + caching layer)
- Edge cases: 4 identified, need explicit handling
- Performance: Caching essential for < 500ms target

ESTIMATED POINTS: 5 (keyword + caching) or 8 (if semantic search needed after testing)
```

**Do NOT Use Sequential Thinking For:**
- Simple code generation or straightforward implementations
- Direct file modifications or basic CRUD operations
- Running tests or quality checks
- Stories with High confidence and clear patterns

---

## Story Template (Define Before Estimate)

### Template Structure

```markdown
#### Story N: [Concise Title]

**Description:**
Detailed explanation of functionality to build and problem it solves.
Include specific files to modify, endpoints to update, DynamoDB operations required.

**Use Sequential Thinking MCP:**
[If Medium or Low confidence - analyze approach before defining details]

**Existing Code Reference:**
- `impl/path/to/file.py` - `ClassName` or `function_name()` to build upon
- Specific functionality to activate, enhance, or replace

**Technical Approach:**
[Based on Sequential Thinking analysis if used]
- Architecture decisions
- Algorithm or pattern choices
- Performance considerations
- Database query strategy
- Error handling approach
- Edge cases identified

**Acceptance Criteria:**
1. [Testable, numbered criteria in behavioral form — "Given X, When Y, Then Z"]
2. OpenAI API responds successfully with real completions
3. DynamoDB persistence verified with data in correct tables
4. [Additional criteria based on story scope]

**CRITICAL**: Each acceptance criterion MUST map directly to an E2E test scenario below.

**E2E Acceptance Tests** (TDD - Write BEFORE Implementation):

**REQUIRED**: Provide thorough, detailed E2E test specifications for EVERY acceptance criterion.

**Test Scenario 1: [Maps to Acceptance Criterion 1]**
```javascript
// Playwright E2E Test - tests/playwright/specs/[feature-name].spec.js
test('should [specific behavior from acceptance criterion]', async ({ page }) => {
  // Setup: Detailed test data and preconditions
  // - Specific user authentication (which of the 5 test users)
  // - Required DynamoDB test data with exact values
  // - Any required API state or configuration

  // Execute: Exact user interactions and API calls
  // - Navigate to specific URL
  // - Click specific UI elements
  // - Enter specific test data
  // - Submit forms or trigger actions

  // Assert: Precise expected outcomes
  // - Verify specific UI elements appear/disappear
  // - Check exact text content or values
  // - Validate DynamoDB data changes
  // - Confirm API responses match expectations
  // - Verify no error states
});
```

**Test Scenario 2: [Maps to Acceptance Criterion 2]**
```javascript
test('should [another specific behavior]', async ({ page }) => {
  // Repeat thorough specification pattern for each criterion
});
```

**cURL Integration Test Example** (for API-only stories):
```bash
# Test Case: [Specific acceptance criterion]
# Prerequisites: [Exact test data needed in DynamoDB]

# Execute API call with specific test data
curl -X POST http://localhost:8080/convo_turn \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer [test-user-token]" \
  -d '{
    "animalId": "animal_1",
    "message": "Tell me about porcupine quills",
    "sessionId": "test-session-123"
  }'

# Expected Response (exact format):
{
  "reply": "Porcupines have about 30,000 quills...",
  "sessionId": "test-session-123",
  "turnId": "[generated-uuid]",
  "timestamp": "[iso-timestamp]",
  "metadata": {
    "tokenUsage": {"prompt": 150, "completion": 75},
    "knowledgeSourcesUsed": ["article_quills_001", "article_defense_002"]
  }
}

# DynamoDB Verification:
# - Check quest-dev-conversation-turn table for new turn record
# - Verify turn contains reply text and metadata
# - Confirm sessionId matches request
```

**Test Coverage Requirements**:
- ✅ Every acceptance criterion has dedicated E2E test
- ✅ All test scenarios include specific test data values
- ✅ All assertions verify exact expected outcomes
- ✅ Tests specify which of the 5 test users to use
- ✅ DynamoDB verification steps explicitly documented
- ✅ Error scenarios tested (if applicable to criterion)

**TDD Workflow for This Story**:
1. **Write E2E tests first** (using specifications above) → Tests fail
2. **Implement code** (following Technical Approach above)
3. **Run E2E tests** → Tests pass
4. **Document test progression**:
   - Screenshot/log of failing tests (before implementation)
   - Screenshot/log of passing tests (after implementation)
   - Verify no other test regressions
5. **Report to Teams channel**:
   - Read appropriate ADVICE for Teams reporting format
   - Send adaptive card (NOT plain text) to Teams webhook
   - Include: Story key, test progression summary, session history link

**Definition of Done** (applies to ALL stories - see "Definition of Done" section):
- ✅ All quality gates pass (`make quality-check`, `tox`)
- ✅ Playwright Step 1 validation: ≥5/6 browsers passing
- ✅ Auth tested with 5 sample users
- ✅ DynamoDB read/write verified
- ✅ Documentation updated
- ✅ No debug artifacts or TODOs remain
- ✅ Code in feature branch only

**Environment Setup:**
- Required environment variables: OPENAI_API_KEY, AWS credentials
- Test data prerequisites: Test animal, test config, test knowledge articles
- DynamoDB table requirements: Tables exist with proper indexes

---

**ESTIMATION (After Complete Analysis Above):**

**Story Points:** [Fibonacci estimate: 1, 2, 3, 5, 8, 13 or range like 5-8]

**Confidence:** [High/Medium/Low]
- **High**: Clear requirements, existing patterns, minimal unknowns
- **Medium**: Some unknowns, new code but established patterns
- **Low**: Novel implementation, architectural decisions, multiple unknowns

**Estimation Assumptions:**
- [List key assumptions affecting this estimate]
- [Note dependencies that could change complexity]
- [Identify risks that could expand scope]

**If Low Confidence:**
[Recommend spike story or further research before implementation]

**Estimation Reasoning:**
- [Explain why this point value or range]
- [What could make it lower bound vs upper bound]
- [What unknowns could change estimate]

---

**Files to Modify:**
- `impl/path/to/file.py`
- `tests/path/to/test_file.py`

**Nortal Jira Fields** (for automated ticket creation):
```json
{
  "project": {"key": "PR003946"},
  "issuetype": {"name": "Task"},
  "summary": "[Story title from above]",
  "description": {ADF format with above content},
  "customfield_10225": {"value": "Billable"},
  "customfield_10014": "PR003946-[EPIC-KEY]",
  "priority": {"name": "Medium"}
}
```
```

---

## Suggested Story Breakdown (Analyze and Refine)

**IMPORTANT**: The story point estimates below are PRELIMINARY suggestions based on typical complexity.

**Your Process:**
1. Read the suggested story scope
2. **Use Sequential Thinking MCP** to analyze technical approach (required for Medium/Low confidence stories)
3. Define complete story with full technical details
4. **THEN estimate points** based on YOUR analysis
5. Adjust estimates up or down based on discoveries
6. Document assumptions and confidence level

**DO NOT treat suggested points as fixed requirements.** They may be wrong once you analyze implementation details.

---

### Phase 1: Core OpenAI Integration with DynamoDB RAG (MVP)

#### Story 1: Activate OpenAI API Integration

**Suggested Scope:** Uncomment and activate existing OpenAI API calls in `ChatGPTIntegration`

**Before Estimating:**
1. Review existing `ChatGPTIntegration.get_animal_response()` implementation
2. Analyze commented-out OpenAI API calls
3. Evaluate error handling needs (rate limits, timeouts, invalid keys, network failures)
4. Consider connection testing and validation approach
5. Plan environment variable validation strategy

**After Sequential Thinking Analysis, Define:**
- Complete technical approach for activation
- Comprehensive error handling strategy
- Connection validation and health check approach
- Full acceptance criteria
- Integration test approach

**Preliminary Estimate:** 3-5 points
**Confidence:** Medium (depends on existing code quality and error handling needs)
**Files**: `impl/utils/chatgpt_integration.py`

**THEN Provide Your Actual Estimate After Analysis**

---

#### Story 2: Replace Mock Responses with OpenAI Integration

**Suggested Scope:** Update `handle_convo_turn_post()` to use real OpenAI API calls

**Before Estimating:**
1. Review existing `handle_convo_turn_post()` and `generate_ai_response()` implementation
2. Design integration flow: (1) Build prompt from animal config, (2) Call OpenAI, (3) Return response
3. Plan metadata capture: token usage, latency, model version
4. Consider error handling at each stage
5. Plan DynamoDB persistence strategy

**After Analysis, Define:**
- Complete OpenAI integration flow
- Metadata collection and storage approach
- Error handling at each stage
- Rollback strategy if OpenAI fails
- Full acceptance criteria

**Preliminary Estimate:** 3-5 points
**Reasoning:**
- Straightforward integration with existing patterns: 3 points
- With comprehensive metadata and error handling: 4 points
- With advanced features and monitoring: 5 points

**Confidence:** High (clear requirements, existing code to build on)
**Files**: `impl/conversation.py`, `impl/utils/chatgpt_integration.py`

**THEN Provide Your Actual Estimate After Analysis**

---

#### Story 3: Implement Guardrails Validation Layer

**Suggested Scope:** Create guardrails enforcement for content safety and appropriateness

**REQUIRED: Use Sequential Thinking MCP to analyze:**
- Guardrails enforcement strategy: pre-generation (input) vs post-generation (output) vs both
- Multi-layer validation: safe mode, content filtering, educational appropriateness, topic relevance
- Performance impact of validation on response latency
- Logging and monitoring strategy for violations
- User experience considerations (blocked content messaging)

**Questions for Sequential Analysis:**
1. Should we validate user input before sending to OpenAI, or only validate AI responses?
2. What's the right balance between safety and user experience?
3. How do we handle false positives in content filtering?

**After Sequential Thinking Analysis, Define:**
- Complete validation architecture (pre/post or both)
- Validation rules and implementation
- Response sanitization approach
- Violation logging and monitoring
- User-friendly error messaging
- Full acceptance criteria

**Preliminary Estimate:** 4-8 points (UNCERTAINTY in validation complexity)
**Reasoning:**
- Simple length limits and basic filtering: 4 points
- Multi-layer validation with logging: 6 points
- Advanced content analysis with educational appropriateness: 8 points

**Confidence:** Low (validation complexity unknown until analyzed)
**Files**: New `impl/validators/guardrails.py`, update `impl/conversation.py`

**THEN Provide Your Actual Estimate After Sequential Analysis**

---

#### Story 4: Add Comprehensive Error Handling and Resilience

**Suggested Scope:** Implement error handling, retry logic, and graceful fallbacks

**Before Estimating:**
1. Identify all error scenarios: OpenAI API failures, rate limits, timeouts, invalid responses
2. Design retry strategy with exponential backoff
3. Consider circuit breaker pattern for sustained outages
4. Plan user-friendly error messages appropriate for zoo visitors
5. Design logging and alerting strategy

**After Analysis, Define:**
- Complete error handling strategy
- Retry logic with backoff algorithm
- Circuit breaker implementation
- Fallback messaging strategy
- Logging and monitoring approach
- Full acceptance criteria

**Preliminary Estimate:** 3-5 points
**Reasoning:**
- Basic error handling and retries: 3 points
- With circuit breaker and comprehensive logging: 4 points
- With advanced resilience patterns and monitoring: 5 points

**Confidence:** High (established patterns exist)
**Files**: `impl/utils/chatgpt_integration.py`, `impl/conversation.py`

**THEN Provide Your Actual Estimate After Analysis**

---

### Phase 1B: Streaming and Monitoring (Optional for MVP)

#### Story 5: Activate Streaming Response Support

**Suggested Scope:** Enable Server-Sent Events (SSE) streaming for real-time responses

**Before Estimating:**
1. Review existing `stream_animal_response()` implementation
2. Plan SSE response format and chunking strategy
3. Consider knowledge retrieval integration in streaming context
4. Plan DynamoDB persistence after streaming completes
5. Design frontend integration requirements

**Preliminary Estimate:** 5-8 points
**Confidence:** Medium
**Files**: `impl/utils/chatgpt_integration.py`, `impl/conversation.py`

**THEN Provide Your Actual Estimate After Analysis**

---

#### Story 6: Implement Token Usage Tracking and Cost Monitoring

**Suggested Scope:** Track and analyze token usage and costs per conversation

**Before Estimating:**
1. Design token tracking strategy (per turn, per session, per animal)
2. Plan cost calculation based on model pricing
3. Design metadata storage in DynamoDB
4. Plan analytics endpoint for usage reporting
5. Consider budget alerts and optimization triggers

**Preliminary Estimate:** 3-5 points
**Confidence:** High (straightforward implementation)
**Files**: `impl/conversation.py`, `impl/analytics.py`

**THEN Provide Your Actual Estimate After Analysis**

---

### Phase 2: Advanced Features (Future Enhancement)

#### Story 7: Assistants API Integration (Optional - Phase 2)
**Preliminary Estimate:** 18-20 points (break into 3-4 smaller stories)
**Note**: This should be a separate epic, not part of Phase 1

---

### Phase 3: Provider Abstraction (Optional)

#### Story 8: Provider Abstraction Layer

**Suggested Scope:** Create interface for multi-provider support (OpenAI, Anthropic, local models)

**Before Estimating:**
1. Design `AbstractChatProvider` interface
2. Plan provider selection mechanism
3. Consider configuration strategy
4. Design provider-specific error handling

**Preliminary Estimate:** 5-8 points
**Confidence:** Medium
**Files**: New `impl/ports/chat_provider.py`, update `impl/utils/chatgpt_integration.py`

**THEN Provide Your Actual Estimate After Analysis**

---

### Phase 4: Testing and Documentation

#### Story 9: Comprehensive Integration Tests

**Suggested Scope:** pytest integration tests for RAG pattern and OpenAI integration

**Before Estimating:**
1. Identify all test scenarios (knowledge retrieval, prompt building, guardrails, errors)
2. Plan mocking strategy for OpenAI and DynamoDB
3. Design test data and fixtures
4. Plan coverage measurement approach

**Preliminary Estimate:** 5-8 points
**Reasoning:**
- Basic integration tests: 5 points
- With comprehensive mocking and edge cases: 6 points
- With 90%+ coverage and advanced scenarios: 8 points

**Confidence:** Medium
**Files**: New test files in `impl/test_*.py`
**Coverage Target**: ≥90%

**THEN Provide Your Actual Estimate After Analysis**

---

#### Story 10: Playwright E2E Validation

**Suggested Scope:** End-to-end browser tests for chat functionality

**Before Estimating:**
1. Design E2E test scenarios (chat interaction, history, errors)
2. Plan cross-browser validation strategy
3. Consider real OpenAI vs mocked responses in tests
4. Design test data setup and teardown

**Preliminary Estimate:** 3-5 points
**Confidence:** High (established Playwright patterns)
**Files**: New tests in `tests/playwright/`

**THEN Provide Your Actual Estimate After Analysis**

---

#### Story 11: Documentation and Handoff

**Suggested Scope:** Comprehensive documentation with architecture diagrams

**Before Estimating:**
1. Plan documentation structure
2. Design architecture diagrams (RAG flow, system components, data flow)
3. Create troubleshooting guide
4. Document environment setup
5. Plan handoff materials

**Preliminary Estimate:** 2-3 points
**Confidence:** High (straightforward documentation)
**Files**: New `claudedocs/CHATGPT-INTEGRATION-GUIDE.md`

**THEN Provide Your Actual Estimate After Analysis**

---

## Story Point Summary (Update After Analysis)

**Phase 1 (MVP - Direct OpenAI Integration)**: TBD after story analysis
- Preliminary estimate: 15-25 points (7-12 dev days)
- Stories: 1-4 (OpenAI activation, mock replacement, guardrails, error handling)
- Update after Sequential Thinking analysis of each story

**Phase 1B (Streaming + Monitoring)**: TBD after analysis
- Preliminary estimate: 8-13 points (4-6.5 dev days)
- Stories: 5-6 (Streaming support, token tracking)

**Phase 2 (Assistants API)**: Future epic
- Preliminary estimate: 18-20 points (separate epic recommended)
- Story: 7

**Phase 3 (Provider Abstraction)**: Optional
- Preliminary estimate: 5-8 points (2.5-4 dev days)
- Story: 8

**Phase 4 (Testing & Documentation)**: TBD after analysis
- Preliminary estimate: 10-16 points (5-8 dev days)
- Stories: 9-11 (Integration tests, E2E tests, documentation)

**Recommended First Release**: Phase 1 only (15-25 points after analysis)

**Total Epic Range** (All Phases): 38-62 points depending on analysis outcomes
**Note**: Knowledge Base RAG pattern removed from scope - will be separate epic

---

## Epic Acceptance Criteria (Definition of Done)

**Epic-Level Success Criteria:**
1. ✅ OpenAI Chat Completions API integrated and responding to user messages
2. ✅ System prompts dynamically generated from AnimalConfig DynamoDB records
3. ✅ Guardrails enforced per animal configuration
4. ✅ Conversation history persisted to DynamoDB with AI responses and metadata
5. ✅ All mock responses removed from production code paths
6. ✅ All existing Playwright Step 1 tests pass (≥5/6 browsers)
7. ✅ Unit test coverage ≥90% for new integration code
8. ✅ `make quality-check` passes all gates
9. ✅ Documentation complete with architecture diagrams and troubleshooting guide
10. ✅ Token usage tracking and cost monitoring operational
11. ✅ Error handling provides graceful fallbacks with user-friendly messages
12. ✅ Knowledge Base integration explicitly OUT OF SCOPE for this epic

---

## Success Metrics

### User Engagement
- Conversation turn count increases (more engaging responses than mocks)
- Session duration increases (users stay longer in chat)
- Return visit rate for chat feature improves

### Conversation Quality
- Reduction in error messages or confused user responses
- Knowledge base facts successfully incorporated into responses
- Guardrails violations logged and minimized
- Educational appropriateness maintained (suitable for children)

### System Reliability
- API error rate remains low (< 1% of requests)
- Response latency acceptable (< 3 seconds for standard responses)
- DynamoDB operations succeed consistently
- Circuit breaker activates and recovers gracefully

### Cost Efficiency
- Cost per conversation within acceptable range (target: < $0.05 per conversation)
- Token usage optimized through effective retrieval strategy
- Model selection appropriate for use case (gpt-4o-mini for most interactions)
- Budget alerts trigger before overspend

---

## Additional Context

### Project Context
- Production educational application serving zoo visitors (children and families)
- Quality and reliability critical (end users are not technical)
- Changes must maintain backward compatibility with existing React frontend
- All stories must reference existing CMZ implementation patterns

### Technical Debt Considerations
- All mock responses must be completely removed (no partial migration)
- No new mock/stub code should be introduced
- Provider abstraction prepares for future multi-LLM support
- Token tracking enables cost optimization and budget management

### Known Risks
- OpenAI API rate limits during high traffic periods
- Knowledge retrieval performance with large knowledge bases (> 10K articles)
- Token budget management complexity with long conversations
- Guardrails enforcement may increase response latency
- Cost overruns if token usage not properly monitored

### Risk Mitigation Strategies
- Implement robust caching for knowledge retrieval
- Use circuit breaker for API failures
- Start with conservative token limits and expand based on metrics
- Monitor costs per conversation with alerting
- Spike stories for high-uncertainty technical decisions

---

---

## EXECUTION INSTRUCTIONS

**When this command is invoked, you MUST:**

### Step 1: Read NORTAL-JIRA-ADVICE.md
```
Read NORTAL-JIRA-ADVICE.md completely to understand:
- Nortal Jira API authentication patterns
- Required custom fields (customfield_10225 for Billable)
- ADF description format requirements
- Project key: PR003946
- Proven script patterns from successful ticket creation
```

### Step 2: Analyze Stories with Sequential Thinking
```
For each story (1-11):
1. Use mcp__sequential-thinking__sequentialthinking to analyze technical approach
2. Define complete story with full acceptance criteria
3. Estimate story points based on analysis
4. Document assumptions and confidence level
```

### Step 3: Generate Epic Ticket
```
Use mcp__jira-mcp__create-ticket to create the epic:
- issue_type: "Task" (epics may not be available)
- summary: "Epic: Activate OpenAI Integration for Animal Chatbot Personalities"
- description: Include business value, implementation strategy, success criteria (in ADF format)
- customfield_10225: {"value": "Billable"}
- story_points: Sum of all Phase 1 stories
```

### Step 4: Generate Story Tickets
```
For each story in Phase 1 (Stories 1-4):
1. Use mcp__jira-mcp__create-ticket:
   - issue_type: "Task"
   - summary: Story title from analysis
   - description: Complete story details in ADF format including:
     * Description
     * Technical Approach
     * Acceptance Criteria
     * E2E Test Specifications (detailed)
     * Definition of Done checklist
     * Files to Modify
   - customfield_10225: {"value": "Billable"}
   - customfield_10014: [Epic key from Step 3]
   - story_points: From analysis
2. Capture ticket key for reporting
```

### Step 5: Generate Summary Report
```
Create markdown report:
- Epic ticket key and link
- All story ticket keys and links
- Total story points for Phase 1
- Phase 1B, 2, 3, 4 stories marked as "Future - Not Created"
- Next steps for team
```

### Step 6: Validate Ticket Creation
```
For each created ticket:
1. Use mcp__jira-mcp__get-ticket to verify creation
2. Confirm all required fields populated
3. Confirm epic linkage working
4. Report any issues
```

---

**Remember:**
1. **Knowledge Base is OUT OF SCOPE** - Only create tickets for Stories 1-4 in Phase 1
2. Use Sequential Thinking MCP to analyze complex stories BEFORE estimating
3. Define complete stories with technical details FIRST
4. THEN estimate points based on analysis
5. Use Fibonacci scale with ranges for uncertainty
6. Document assumptions and confidence levels
7. Follow Nortal Jira format from NORTAL-JIRA-ADVICE.md
8. Reference existing CMZ patterns and code
9. **Include Definition of Done in EVERY story** (quality gates, auth testing, DynamoDB verification, documentation, no debug artifacts)
10. **CRITICAL: Provide thorough E2E test specifications for EVERY acceptance criterion** (Playwright test code, exact test data, DynamoDB verification steps, specific assertions)
11. **TDD Approach: E2E tests written BEFORE implementation** - Every story must specify tests to write first
12. **Document test progression**: Show tests failing before implementation, passing after, with no regressions
13. **Teams reporting after completion**: Send adaptive cards (NOT plain text) to Teams webhook with test progression summary
14. Ensure all testing requirements are included (tox, make quality-check, Playwright Step 1)
