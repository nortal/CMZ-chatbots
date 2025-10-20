# Agent Delegation Templates

Comprehensive delegation patterns for all available agents in the CMZ Chatbots project.

## How to Use This Guide

**When to Delegate:**
- Task requires specialized expertise
- Operation can run in parallel with main work
- Task is well-defined and autonomous
- You want to maintain focus on primary objective

**How to Delegate:**
```python
Task(
    subagent_type="agent-type-here",
    description="Brief 3-5 word description",
    prompt="""Detailed task specification with:
    - Context and background
    - Specific requirements
    - Expected deliverables
    - Success criteria
    """
)
```

---

## Testing & Quality Agents

### quality-engineer
**Purpose**: Ensure software quality through comprehensive testing strategies and systematic edge case detection

**When to Use:**
- Need comprehensive test strategy
- Identifying edge cases
- Quality validation before release
- Test suite design

**Template:**
```python
Task(
    subagent_type="quality-engineer",
    description="Design comprehensive test strategy",
    prompt="""Design a comprehensive testing strategy for {feature_name}.

FEATURE: {description}
ENDPOINTS: {list_endpoints}
BUSINESS LOGIC: {key_logic}

REQUIREMENTS:
1. Identify all edge cases and boundary conditions
2. Design test cases for happy path, error scenarios, edge cases
3. Recommend test types (unit, integration, E2E)
4. Define quality gates and success criteria
5. Consider performance, security, accessibility

DELIVERABLES:
- Test strategy document
- Edge case catalog
- Quality gate definitions
- Test execution plan

FOCUS: Systematic edge case detection and quality validation.
"""
)
```

### test-coverage-verifier
**Purpose**: Verifies test coverage and quality for specific features including unit, integration, and E2E tests

**When to Use:**
- Validate test coverage completeness
- Check test quality
- Verify feature has adequate testing
- Pre-deployment validation

**Template:**
```python
Task(
    subagent_type="test-coverage-verifier",
    description="Verify test coverage for feature",
    prompt="""Verify comprehensive test coverage for {feature_name}.

FEATURE: {description}
CODE LOCATIONS: {file_paths}

VERIFICATION REQUIREMENTS:
1. Check unit test coverage (target: 90%+)
2. Verify integration tests exist for all endpoints
3. Confirm E2E tests cover user workflows
4. Validate edge cases are tested
5. Check test quality (assertions, not just execution)

DELIVERABLES:
- Coverage report by test type
- Gap analysis
- Test quality assessment
- Recommendations for improvement

CRITICAL: Report actual coverage numbers with evidence.
"""
)
```

### Custom: test-generation (via general-purpose)
**Purpose**: Generate comprehensive test suites with DynamoDB verification and authenticity checking

**When to Use:**
- Missing test coverage
- New feature needs tests
- Need DynamoDB persistence verification
- Test authenticity concerns

**Template:**
```python
Task(
    subagent_type="general-purpose",
    description="Generate comprehensive test suite",
    prompt="""You are a seasoned QA engineer. Generate complete test coverage for {feature_name}.

FEATURE: {description}
ENDPOINTS: {list_endpoints}
BUSINESS LOGIC: {key_logic}
DATABASE: {dynamodb_tables}

REQUIREMENTS:
1. Analyze existing test coverage
2. Generate missing tests (unit, integration, E2E, validation)
3. Include edge cases and error scenarios
4. CRITICAL: Verify DynamoDB read/write in ALL tests
5. Create test plan and coverage map
6. Verify test authenticity (no false positives)

DELIVERABLES:
- tests/unit/{test_file}.py
- tests/integration/{test_file}.py
- tests/playwright/specs/{test_file}.spec.js
- test_plan_{feature}.md
- coverage_matrix.md

VERIFICATION:
- Check for "not implemented" responses
- Verify actual DynamoDB operations
- Confirm no stub code in handlers
- Validate test results are real

See .claude/commands/generate-tests.md for complete methodology.
"""
)
```

### persistence-verifier
**Purpose**: Verifies data persistence to DynamoDB including table operations, data validation, and test verification

**When to Use:**
- Validate DynamoDB operations
- Check data persistence
- Verify write operations succeed
- Confirm read operations accurate

**Template:**
```python
Task(
    subagent_type="persistence-verifier",
    description="Verify DynamoDB persistence",
    prompt="""Verify data persistence to DynamoDB for {feature_name}.

FEATURE: {description}
ENDPOINTS: {list_endpoints}
TABLE: {dynamodb_table_name}
PRIMARY KEY: {pk_name}

VERIFICATION REQUIREMENTS:
1. Verify write operations persist data correctly
2. Confirm read operations retrieve accurate data
3. Validate update operations modify existing items
4. Check delete operations (soft delete if applicable)
5. Test error handling (connection failures, conflicts)

DELIVERABLES:
- Persistence verification report
- Data integrity validation results
- Error scenario test results
- Recommendations for improvement

CRITICAL: Query DynamoDB directly to verify, don't trust API responses alone.
"""
)
```

### Custom: test-orchestrator (via general-purpose)
**Purpose**: Comprehensive test coordination with intelligent error classification and regression verification

**When to Use:**
- Need to run all test types (unit, integration, E2E, validation)
- Systematic error analysis required
- Classification of "not implemented" errors needed
- Comprehensive test reporting to Teams
- Coverage gap identification for test generation

**Template:**
```python
Task(
    subagent_type="general-purpose",
    description="Orchestrate comprehensive testing",
    prompt="""You are a Senior QA Test Orchestrator. Coordinate all validation testing with intelligent error classification.

CRITICAL DIRECTIVE:
BEFORE declaring ANY "not implemented" or 501 error as regression:
1. MUST read ENDPOINT-WORK-ADVICE.md to understand OpenAPI generation patterns
2. Check if handler exists in impl/ modules
3. Verify controller routing is correct
4. Classify error with evidence (frequently OpenAPI regeneration disconnects handlers)

ORCHESTRATION PHASES:

Phase 1: Pre-Flight Coverage Analysis
- Delegate to test-coverage-verifier
- Identify gaps in unit, integration, E2E, validation tests
- Report coverage percentages by test type

Phase 2: Multi-Layer Test Execution (PARALLEL)
- Delegate to backend-feature-verifier (all API endpoints)
- Delegate to frontend-feature-verifier (all UI features)
- Delegate to persistence-verifier (all DynamoDB operations)
- Execute in parallel for maximum efficiency

Phase 3: Error Analysis and Root Cause Investigation
- Collect all "not implemented", 501, 404 errors from Phase 2
- READ ENDPOINT-WORK-ADVICE.md for each suspected regression
- Delegate to root-cause-analyst with focus on OpenAPI artifacts
- Investigate handler-controller connections

Phase 4: Regression Verification
For each suspected regression:
- Implementation check: Does handler exist in impl/?
- Controller routing check: Does controller route correctly?
- Git history check: Recent OpenAPI regeneration?
- Classification: TRUE REGRESSION vs OPENAPI ARTIFACT vs TEST ARTIFACT

Phase 5: Reporting and Coverage Notes
- Create comprehensive report (JSON format)
- Delegate to teams-reporting agent (send to Teams)
- Generate notes for test-generation agent (coverage gaps, false regressions)

DELIVERABLES:
1. Coverage analysis report
2. Test execution results (all test types)
3. Error classification with evidence
4. Root cause analysis for all failures
5. Teams notification (via delegation)
6. Test generation notes

FOCUS: {backend|frontend|all}

ERROR INVESTIGATION PROTOCOL:
- "Not implemented" or 501 → STOP → Read ENDPOINT-WORK-ADVICE.md
- Check impl/ for handler
- Check controller routing
- Check git log for recent regeneration
- Classify with evidence

SUCCESS CRITERIA:
- ≥95% test pass rate (excluding known issues)
- 100% of "not implemented" errors investigated
- All 501 errors classified (true vs. artifact)
- Teams notification sent successfully
- Test generation notes created

See .claude/commands/orchestrate-tests.md for complete 5-phase methodology.
"""
)
```

### Custom: frontend-comprehensive-testing (via general-purpose)
**Purpose**: Systematic UI component testing across all user roles with edge case validation and OpenAPI compliance

**When to Use:**
- Need complete UI component testing
- Test across multiple user roles (admin, zookeeper, parent, student, visitor)
- Validate OpenAPI specifications for inputs
- Test comprehensive edge cases (Unicode, security, large content)
- Monitor backend health during testing
- Stop immediately on "not implemented" errors

**Template:**
```python
Task(
    subagent_type="general-purpose",
    description="Frontend comprehensive testing",
    prompt="""You are a Senior Frontend QA Engineer. Test ALL UI components systematically across all user roles.

CRITICAL DIRECTIVES:
1. Verify backend health BEFORE testing (version, reachability, authentication)
2. STOP IMMEDIATELY if "not implemented" or version mismatch encountered
3. Build complete component inventory for ALL accessible UI elements
4. Test all text inputs with 25+ edge cases
5. Verify all inputs have OpenAPI validation constraints
6. Report bugs for missing OpenAPI validation

6-PHASE METHODOLOGY:

Phase 1: Backend Health Validation
- Check backend reachability and version
- Verify authentication endpoint works
- STOP if any 501, 404, or "not implemented" errors

Phase 2: Component Discovery and Inventory
- Login as each role: {roles}
- Navigate all accessible routes
- Discover all interactive elements (buttons, inputs, selects, dialogs)
- Map components to roles and routes
- Link to OpenAPI spec fields

Phase 3: OpenAPI Specification Validation
- For each input component, verify OpenAPI field exists
- Check validation constraints: minLength, maxLength, min, max, pattern
- Report bugs: CRITICAL (no spec), HIGH (missing constraints), MEDIUM (insufficient)

Phase 4: Text Input Edge Case Testing (25+ cases per field)
- Length boundaries: at_min, at_max, below_min, above_max, empty, single_char
- Unicode: chinese, arabic, russian, japanese, hebrew, emojis
- Security: script_tag, sql_injection, command_injection
- Whitespace: leading, trailing, tabs, newlines, only_spaces
- Large content: lorem_ipsum, five_paragraphs, very_large
- Verify DynamoDB persistence for accepted inputs

Phase 5: Control and Button Testing
- Test toggles: both states, verify persistence
- Test sliders: min, max, midpoint, out-of-range
- Test selects: all options, verify persistence
- Test buttons: expected behavior (dialog, navigation, save)

Phase 6: Multi-Role Testing and Reporting
- Verify role-based access control
- Test allowed/denied routes for each role
- Generate comprehensive report
- Delegate to teams-reporting agent

ROLES TO TEST: {admin, zookeeper, parent, student, visitor}

TEXT EDGE CASES (apply to ALL text inputs):
- empty, single_char, at_min_length, at_max_length, exceed_max
- lorem_ipsum, five_paragraphs, very_large_block
- chinese, arabic, russian, japanese, hebrew, emojis
- script_tag, sql_injection, command_injection
- leading_spaces, trailing_spaces, only_spaces, newlines

STOPPING CONDITIONS (IMMEDIATE STOP):
- Backend not reachable
- Backend version mismatch
- "Not implemented" error
- 501 or 404 on known endpoint
- Authentication broken

DELIVERABLES:
1. Complete component inventory (JSON)
2. OpenAPI validation bug report
3. Edge case test results (all components)
4. Control testing results
5. Role-based access verification
6. Comprehensive test report
7. Teams notification (via delegation)

SUCCESS CRITERIA:
- ≥98% UI components working
- Zero "not implemented" errors
- 100% inputs have OpenAPI spec
- ≥20 edge cases per text input
- Role-based access 100% enforced
- ≥95% cross-browser pass rate

See .claude/commands/frontend-comprehensive-testing.md for complete 6-phase methodology.
"""
)
```

### Custom: document-features (via general-purpose)
**Purpose**: Generate and maintain hierarchical feature documentation from requirements, code, and specifications

**When to Use:**
- Need comprehensive feature documentation
- Document new features or components
- Update existing documentation after code changes
- Generate field-level specifications for testing agents
- Document validation rules and edge cases
- Clarify ambiguous requirements with user

**Template:**
```python
Task(
    subagent_type="general-purpose",
    description="Generate feature documentation",
    prompt="""You are a Senior Technical Writer / Product Documentation Specialist.

Generate comprehensive hierarchical documentation for {feature_name}.

6-PHASE DOCUMENTATION PROCESS:

Phase 1: Source Discovery and Analysis
- Read CLAUDE.md Architecture Overview
- Analyze backend/api/openapi_spec.yaml
- Examine frontend/src/components/
- Review impl/ modules
- Collect existing documentation (*-ADVICE.md files)
- Track all source files examined

Phase 2: Feature Identification and Hierarchy
- Identify business capabilities from OpenAPI endpoint groups
- Map frontend routes to features
- Build feature hierarchy: System → Feature → Component → Field → Test
- Document business value for each feature

Phase 3: Component-Level Documentation
- Document each UI component (dialog, page, form)
- Document each API endpoint from OpenAPI spec
- Include request/response details
- Document data flow: UI → API → DynamoDB
- Link components to OpenAPI spec fields

Phase 4: Field-Level Specifications
- Document EVERY input field with:
  - Purpose (user-facing description)
  - Frontend validation rules
  - Backend validation rules (from OpenAPI)
  - Validation gaps (if frontend/backend differ)
  - Valid/invalid value examples
  - 25+ edge cases (length, Unicode, security, whitespace, large content)
  - DynamoDB persistence details
  - Auto-generation logic (if applicable)

Phase 5: Question Gathering and User Clarification
- Collect questions about:
  - Ambiguous business requirements
  - Unclear validation rules
  - Missing implementation details
  - Edge case handling uncertainties
- Present questions organized by priority:
  - CRITICAL: Blocking documentation
  - HIGH: Affects test scenarios
  - MEDIUM: Improves accuracy
  - LOW: Future enhancements
- Wait for user answers
- Update documentation with user clarifications
- Record answers in sources/user-clarifications.md

Phase 6: Test Documentation and Maintenance
- Generate test scenarios (happy path + failure)
- Create edge case lists for all fields
- Document DynamoDB verification steps
- Create documentation-index.json (master reference)
- Update sources/update-history.md

DOCUMENTATION STRUCTURE:
claudedocs/features/
├── documentation-index.json
├── feature-map.md
├── {feature-name}/
│   ├── README.md (business value, user capabilities)
│   ├── frontend/
│   │   ├── components.md (UI specifications)
│   │   └── fields/
│   │       └── {field-name}.md (validation, edge cases)
│   ├── backend/
│   │   ├── api-endpoints.md (OpenAPI endpoints)
│   │   └── dynamodb-schema.md (persistence)
│   ├── testing/
│   │   ├── test-scenarios.md (happy + failure paths)
│   │   └── edge-cases.md (25+ per field)
│   └── questions.md (user clarifications)
└── sources/
    ├── requirements-consumed.md
    ├── code-analyzed.md
    └── user-clarifications.md

FIELD DOCUMENTATION TEMPLATE:
# {Field Name}

## Purpose
{User-facing description - "This field contains the system prompt..."}

## Validation Rules
### Frontend: minLength, maxLength, pattern
### Backend (OpenAPI): minLength, maxLength, pattern
### Validation Gaps: {If different or missing}

## Edge Cases (25+ categories)
- Length: empty, single_char, at_min, at_max, exceed_max
- Unicode: chinese, arabic, russian, japanese, hebrew, emojis
- Security: HTML tags, SQL injection, XSS
- Whitespace: leading, trailing, only_spaces, newlines
- Large: lorem_ipsum, 2500+ chars

## Data Persistence
- DynamoDB Field: {field name}
- Table: {table name}
- Verification: aws dynamodb get-item...

INTEGRATION WITH OTHER AGENTS:
- Frontend Testing Agent: Reads documentation-index.json for component inventory
- Developer Agents: Reference field docs for validation rules
- Testing Agents: Use edge cases from field documentation

QUESTION EXAMPLE:
## Question 1: Validation Rules - Unicode Support
**Context**: openapi_spec.yaml AnimalConfig.systemPrompt pattern
**Question**: Should system prompts allow Unicode (emoji, non-English)?
**Options**:
  A: Keep ASCII-only for consistency
  B: Allow Unicode for expressiveness
  C: Allow emoji only
**Impact**: Field validation, test edge cases, security
**Priority**: Critical
**Current Assumption**: ASCII-only per pattern, may limit chatbot expressiveness

DELIVERABLES:
1. claudedocs/features/{feature-name}/ (complete hierarchy)
2. documentation-index.json (master reference)
3. questions.md (if clarifications needed)
4. sources/ tracking files

SUCCESS CRITERIA:
- 100% of UI components documented
- All fields have validation rules + 25+ edge cases
- Testing agents can use docs without clarification
- <5% documentation-code mismatches

COMMAND FLAGS:
{feature_name} - Document specific feature
--update - Regenerate existing docs
--component {name} - Document specific component
--all-fields - Generate all field docs
--test-docs - Test documentation only
--verify - Validate against current code

See .claude/commands/document-features.md for complete 6-phase methodology.
See FEATURE-DOCUMENTATION-ADVICE.md for best practices and patterns.
"""
)
```

### Custom: backend-testing (via general-purpose)
**Purpose**: Systematic REST API testing with OpenAPI validation, edge case testing, and DynamoDB persistence verification

**When to Use:**
- Need comprehensive backend endpoint testing
- Validate OpenAPI specification completeness
- Test edge cases (Unicode, security, boundaries, large inputs)
- Verify DynamoDB persistence for all successful operations
- Classify "not implemented" errors (true bug vs OpenAPI artifact)
- Ensure 100% test cleanup (no artifacts in production tables)

**Template:**
```python
Task(
    subagent_type="general-purpose",
    description="Backend comprehensive testing",
    prompt="""You are a Senior Backend QA Engineer. Test ALL backend endpoints comprehensively with OpenAPI validation and DynamoDB verification.

CRITICAL DIRECTIVES:
1. Validate OpenAPI spec FIRST - report gaps as bugs BEFORE testing
2. Delegate "not implemented" errors to root-cause-analyst (frequently OpenAPI artifacts)
3. Verify ALL successful requests in DynamoDB with field-level comparison
4. Clean up 100% of test data - zero artifacts in production tables
5. Test edge cases: Unicode, security, boundaries, large inputs, binary data

6-PHASE TESTING METHODOLOGY:

Phase 1: OpenAPI Specification Analysis
- Read backend/api/openapi_spec.yaml
- For EACH endpoint, check ALL fields have validation constraints:
  - minLength, maxLength (string fields)
  - minimum, maximum (numeric fields)
  - pattern (regex validation)
  - enum (allowed values)
  - required fields marked correctly
- Generate OpenAPI Gap Report with severity:
  - CRITICAL: No validation constraints (DoS risk)
  - HIGH: Missing minLength or minimum (empty/negative allowed)
  - MEDIUM: Missing examples or descriptions
- Report gaps as bugs immediately

Phase 2: Edge Case Test Generation
Generate comprehensive edge cases for all field types:

STRING FIELDS (25+ tests):
- Length: empty, single_char, at_min, at_max, below_min, above_max, very_large (100k chars)
- Unicode: chinese, arabic, russian, japanese, hebrew, emojis, mixed, rtl
- Security: script_tag, img_onerror, sql_injection, command_injection, path_traversal, null_bytes
- Whitespace: leading, trailing, multiple_spaces, only_spaces, tabs, newlines, mixed
- Large: lorem_ipsum (500 chars), five_paragraphs (2000 chars), very_large_block (10k chars)

NUMERIC FIELDS (15+ tests):
- Boundaries: zero, negative, at_min, below_min, at_max, above_max
- Very large: 10^100 (should reject)
- Very small: -10^100 (should reject)
- Decimal precision: 0.123456789
- Special: infinity, negative_infinity, nan (should reject)
- Type mismatch: string, array, object (should reject)

BOOLEAN FIELDS (5+ tests):
- Valid: true, false
- Invalid: "true", 1, 0, null (should reject)

ARRAY FIELDS (8+ tests):
- Empty array, single item, at_minItems, above_maxItems, very_large (10k items)
- Invalid item types

ENUM FIELDS (all values + invalid):
- Test ALL valid enum values
- Test invalid values, case mismatch, empty string, null

Phase 3: REST API Testing with DynamoDB Verification
For each test case:
1. Generate unique test ID: TEST_ID="test_$(uuidgen)"
2. Make REST API call:
   curl -X POST http://localhost:8080/{endpoint} \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer $JWT_TOKEN" \
     -d '{{"id": "'$TEST_ID'", "field": "{edge_case_value}"}}'
3. For VALID inputs (expect success):
   - Verify HTTP 200/201
   - Query DynamoDB: aws dynamodb get-item --table-name {table} --key ...
   - Compare ALL fields (not just existence)
   - Verify nested objects preserved
   - Verify arrays contain correct items
   - Verify data types correct (number vs string)
4. For INVALID inputs (expect rejection):
   - Verify HTTP 400
   - Verify error message descriptive
   - Verify NO data in DynamoDB
5. Clean up: aws dynamodb delete-item ... (verify deletion)

Phase 4: Error Classification and Root Cause Investigation
For each failed test:
- Expected failure (invalid input correctly rejected) → TEST PASSED
- Unexpected failure → Investigate:

IF "not implemented" or HTTP 501 encountered:
**DO NOT immediately report as backend bug. DELEGATE:**
Task(
    subagent_type="root-cause-analyst",
    description="Investigate not implemented error",
    prompt="""Investigate 501/not implemented on {endpoint}.

    CRITICAL: Read ENDPOINT-WORK-ADVICE.md for OpenAPI patterns.

    Investigation:
    1. Check if handler exists in impl/ modules
    2. Verify controller routing correct
    3. Check recent OpenAPI generation (git log)
    4. Look for "do some magic!" placeholders

    Classify: TRUE BUG vs OPENAPI ARTIFACT vs TEST ARTIFACT

    Provide evidence: handler location, controller imports, timestamps
    """
)
**WAIT for root-cause-analyst response before classifying error**

Phase 5: Comprehensive Reporting
Generate detailed test report with:
- Executive Summary (total tests, pass/fail rates, critical issues)
- OpenAPI Specification Gaps (CRITICAL, HIGH, MEDIUM with recommendations)
- Test Results by Endpoint (edge cases tested, failures with reproduction steps)
- Failed Tests with Reproduction (exact curl commands, DynamoDB queries)
- DynamoDB Verification Summary (persistence success rate, failures)
- Cleanup Verification (all test data deleted)
- Not Implemented Investigations (classification with evidence)
- Recommendations (prioritized: Critical, High, Medium)

Report structure:
claudedocs/testing/backend/{feature_name}/
├── report.md (complete test report)
├── openapi-gaps.md (specification gaps)
├── reproduction-steps.md (all failed tests)
└── summary.json (metrics for Teams reporting)

Phase 6: Integration with Other Agents
- Report findings to backend-architect (bug fixes needed)
- Update feature-documentation agent (validated edge cases)
- Send Teams notification via teams-reporting agent
- Provide test data to test-generation agent (coverage gaps)

FEATURE TO TEST: {feature_name}
ENDPOINTS: {list_endpoints}
DYNAMODB TABLE: {table_name}
PRIMARY KEY: {pk_name}

TEST DATA CLEANUP PROTOCOL:
1. Use unique UUID for EVERY test: test_$(uuidgen)
2. Delete after EVERY test (success or failure)
3. Verify deletion succeeded (query should return empty)
4. Final scan for remaining test items:
   aws dynamodb scan --table-name {table} \
     --filter-expression "begins_with(pk, :prefix)" \
     --expression-attribute-values '{{":prefix": {{"S": "test_"}}}}' \
     --profile cmz
5. Should return 0 items

SUCCESS CRITERIA:
- ✅ 100% of endpoints tested
- ✅ ≥25 edge cases per text field
- ✅ ≥15 edge cases per numeric field
- ✅ 100% OpenAPI spec validation (gaps documented)
- ✅ 100% DynamoDB persistence verification (field-level comparison)
- ✅ 100% test cleanup (zero artifacts)
- ✅ All "not implemented" errors investigated with evidence
- ✅ Reproduction steps for all failures
- ✅ Teams notification sent

DELIVERABLES:
1. OpenAPI Gap Report (CRITICAL/HIGH/MEDIUM)
2. Complete test report with reproduction steps
3. DynamoDB verification report
4. Cleanup verification (zero artifacts)
5. Error classification with evidence
6. Teams notification (via delegation)
7. Recommendations (prioritized by severity)

See .claude/commands/backend-testing.md for complete 6-phase methodology.
See BACKEND-TESTING-ADVICE.md for best practices and troubleshooting.
"""
)
```

---

## Backend Development Agents

### backend-architect
**Purpose**: Design reliable backend systems with focus on data integrity, security, and fault tolerance

**When to Use:**
- Designing new backend services
- Architecture refactoring
- Data model design
- API design and contracts

**Template:**
```python
Task(
    subagent_type="backend-architect",
    description="Design backend architecture",
    prompt="""Design backend architecture for {feature_name}.

REQUIREMENTS:
- {list_functional_requirements}

NON-FUNCTIONAL REQUIREMENTS:
- Data integrity and consistency
- Security and access control
- Fault tolerance and error handling
- Performance and scalability

CONSTRAINTS:
- Tech stack: Python Flask, AWS DynamoDB, OpenAPI
- Existing patterns: {reference_patterns}

DELIVERABLES:
1. Architecture diagram
2. API contract design (OpenAPI spec)
3. Data model design (DynamoDB schema)
4. Error handling strategy
5. Security considerations
6. Implementation plan

FOCUS: Data integrity, security, and fault tolerance.
"""
)
```

### backend-feature-verifier
**Purpose**: Verifies backend endpoint implementation including OpenAPI spec, business logic, and handler routing

**When to Use:**
- Validate backend implementation
- Check endpoint functionality
- Verify OpenAPI compliance
- Pre-deployment validation

**Template:**
```python
Task(
    subagent_type="backend-feature-verifier",
    description="Verify backend implementation",
    prompt="""Verify backend implementation for {feature_name}.

ENDPOINTS: {list_endpoints}
OPENAPI SPEC: backend/api/openapi_spec.yaml

VERIFICATION REQUIREMENTS:
1. Verify OpenAPI spec defines endpoints correctly
2. Check controllers route to correct handlers
3. Validate business logic implementation
4. Confirm error handling present
5. Verify DynamoDB integration

DELIVERABLES:
- Implementation verification report
- OpenAPI compliance check
- Handler routing validation
- Business logic review
- Recommendations

CRITICAL: Check for "not implemented", "do some magic" placeholders.
"""
)
```

### python-expert
**Purpose**: Deliver production-ready, secure, high-performance Python code following SOLID principles and modern best practices

**When to Use:**
- Complex Python implementation
- Performance optimization
- Code review and refactoring
- Python best practices

**Template:**
```python
Task(
    subagent_type="python-expert",
    description="Implement Python feature",
    prompt="""Implement {feature_name} following Python best practices.

REQUIREMENTS:
- {list_requirements}

CONSTRAINTS:
- Python 3.12
- Must follow SOLID principles
- Type hints required
- Comprehensive error handling
- Unit tests included

DELIVERABLES:
1. Implementation code with type hints
2. Unit tests (pytest)
3. Documentation strings
4. Error handling
5. Performance considerations

FOCUS: Production-ready, secure, high-performance code.

EXAMPLE PATTERN:
```python
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class Config:
    temperature: float
    system_prompt: str

    def validate(self) -> None:
        if not 0.0 <= self.temperature <= 1.0:
            raise ValueError("Temperature must be between 0.0 and 1.0")
```
"""
)
```

---

## Frontend Development Agents

### frontend-architect
**Purpose**: Create accessible, performant user interfaces with focus on user experience and modern frameworks

**When to Use:**
- Designing UI components
- Frontend architecture
- User experience optimization
- Accessibility compliance

**Template:**
```python
Task(
    subagent_type="frontend-architect",
    description="Design frontend architecture",
    prompt="""Design frontend architecture for {feature_name}.

REQUIREMENTS:
- {list_user_stories}

CONSTRAINTS:
- Framework: React
- Must be accessible (WCAG 2.1 AA)
- Responsive design (mobile-first)
- Performance: < 3s load time

DELIVERABLES:
1. Component architecture diagram
2. Component specifications
3. State management strategy
4. API integration patterns
5. Accessibility checklist
6. Performance optimization plan

FOCUS: Accessibility, performance, user experience.
"""
)
```

### frontend-feature-verifier
**Purpose**: Verifies frontend implementation including React components, routing, API integration, and UI functionality

**When to Use:**
- Validate frontend implementation
- Check UI functionality
- Verify API integration
- Accessibility validation

**Template:**
```python
Task(
    subagent_type="frontend-feature-verifier",
    description="Verify frontend implementation",
    prompt="""Verify frontend implementation for {feature_name} using ACTUAL browser testing.

COMPONENTS: {list_component_paths}
ENDPOINTS: {api_endpoints_used}
FRONTEND_URL: {frontend_url}

CRITICAL REQUIREMENT: You MUST use Playwright MCP tools for ALL testing.
NEVER rely on static code analysis alone. Code existing ≠ code working.

REQUIRED PLAYWRIGHT MCP TOOLS:
- mcp__playwright__browser_navigate: Navigate to pages
- mcp__playwright__browser_snapshot: Capture page state
- mcp__playwright__browser_click: Click buttons/links
- mcp__playwright__browser_type: Enter text in inputs
- mcp__playwright__browser_evaluate: Execute JavaScript
- mcp__playwright__browser_console_messages: Check for errors

VERIFICATION REQUIREMENTS:
1. **Authenticate** - Use Playwright to login with test credentials
2. **Navigate** - Actually navigate to component pages in browser
3. **Interact** - Click buttons, type in inputs, submit forms
4. **Verify API Calls** - Check network requests succeed (200/201)
5. **Check Console** - Verify no errors in browser console
6. **Accessibility** - Run automated WCAG checks
7. **Responsive Design** - Test multiple viewport sizes

TEST USER CREDENTIALS:
- parent1@test.cmz.org / testpass123 (parent role)
- student1@test.cmz.org / testpass123 (student role)

BROWSER TESTING WORKFLOW:
1. browser_navigate to {frontend_url}
2. Type credentials and click sign in
3. browser_snapshot to verify dashboard loaded
4. Navigate to feature pages
5. Test all interactive elements
6. Check console_messages for errors
7. Verify DynamoDB persistence (if applicable)

DELIVERABLES:
- Browser-based component verification report
- API integration validation (actual network calls)
- Accessibility audit (automated checks)
- Responsive design check (tested viewports)
- User interaction testing results (real clicks/typing)
- Console error report (if any)

CRITICAL: You MUST actually use Playwright MCP. Static code analysis is NOT sufficient.
If you complete without using browser_navigate, browser_click, or browser_type tools, you did it WRONG.
"""
)
```

---

## System Design & Architecture Agents

### system-architect
**Purpose**: Design scalable system architecture with focus on maintainability and long-term technical decisions

**When to Use:**
- Large-scale system design
- Architecture refactoring
- Technical decision making
- System integration design

**Template:**
```python
Task(
    subagent_type="system-architect",
    description="Design system architecture",
    prompt="""Design system architecture for {system_name}.

REQUIREMENTS:
- {list_business_requirements}

SCALE REQUIREMENTS:
- Users: {expected_users}
- Requests: {requests_per_second}
- Data: {data_volume}

CONSTRAINTS:
- AWS infrastructure
- Budget: {budget_constraint}
- Existing systems: {list_existing_systems}

DELIVERABLES:
1. High-level architecture diagram
2. Component specifications
3. Data flow diagrams
4. Integration patterns
5. Scalability strategy
6. Cost estimation
7. Risk assessment

FOCUS: Scalability, maintainability, long-term viability.
"""
)
```

### devops-architect
**Purpose**: Automate infrastructure and deployment processes with focus on reliability and observability

**When to Use:**
- CI/CD pipeline design
- Infrastructure automation
- Deployment strategies
- Monitoring and observability

**Template:**
```python
Task(
    subagent_type="devops-architect",
    description="Design CI/CD pipeline",
    prompt="""Design CI/CD pipeline and infrastructure automation for {project_name}.

REQUIREMENTS:
- Automated testing
- Deployment to AWS
- Monitoring and alerting
- Rollback capability

CONSTRAINTS:
- GitHub Actions
- AWS infrastructure (Lambda, ECS, etc.)
- Docker containers

DELIVERABLES:
1. CI/CD pipeline design (.github/workflows)
2. Infrastructure as Code (Terraform/CloudFormation)
3. Deployment strategy (blue-green, canary)
4. Monitoring setup (CloudWatch, logs)
5. Alerting configuration
6. Rollback procedures

FOCUS: Reliability, observability, automation.
"""
)
```

---

## Code Quality & Refactoring Agents

### refactoring-expert
**Purpose**: Improve code quality and reduce technical debt through systematic refactoring and clean code principles

**When to Use:**
- Code refactoring needed
- Technical debt reduction
- Code smell elimination
- Design pattern application

**Template:**
```python
Task(
    subagent_type="refactoring-expert",
    description="Refactor code module",
    prompt="""Refactor {module_name} to improve code quality and reduce technical debt.

CODE LOCATION: {file_paths}

ISSUES IDENTIFIED:
- {list_code_smells}
- {list_technical_debt}

REQUIREMENTS:
1. Apply SOLID principles
2. Eliminate code duplication (DRY)
3. Improve naming and clarity
4. Add type hints
5. Enhance error handling
6. Maintain backward compatibility

DELIVERABLES:
1. Refactored code
2. Test updates (if needed)
3. Migration guide (if breaking changes)
4. Technical debt reduction report

FOCUS: Clean code principles, maintainability, testability.

SAFETY: Create git checkpoint before refactoring.
"""
)
```

### security-engineer
**Purpose**: Identify security vulnerabilities and ensure compliance with security standards and best practices

**When to Use:**
- Security audit needed
- Vulnerability assessment
- Security compliance check
- Threat modeling

**Template:**
```python
Task(
    subagent_type="security-engineer",
    description="Security audit",
    prompt="""Conduct security audit for {feature_name}.

CODE LOCATIONS: {file_paths}
ENDPOINTS: {api_endpoints}

AUDIT SCOPE:
1. Authentication and authorization
2. Input validation and sanitization
3. SQL/NoSQL injection vulnerabilities
4. XSS and CSRF protection
5. Secrets management
6. Data encryption
7. Error message disclosure

DELIVERABLES:
1. Security audit report
2. Vulnerability findings (severity ratings)
3. Remediation recommendations
4. Security best practices checklist
5. Compliance status (OWASP Top 10)

CRITICAL: Check for exposed secrets, credentials, API keys.
"""
)
```

### performance-engineer
**Purpose**: Optimize system performance through measurement-driven analysis and bottleneck elimination

**When to Use:**
- Performance issues
- Optimization needed
- Bottleneck identification
- Scalability testing

**Template:**
```python
Task(
    subagent_type="performance-engineer",
    description="Optimize performance",
    prompt="""Optimize performance for {feature_name}.

CURRENT PERFORMANCE:
- Response time: {current_response_time}
- Throughput: {current_throughput}
- Resource usage: {current_resource_usage}

TARGET PERFORMANCE:
- Response time: {target_response_time}
- Throughput: {target_throughput}
- Resource usage: {target_resource_usage}

ANALYSIS REQUIREMENTS:
1. Profile code to identify bottlenecks
2. Analyze database queries
3. Check API call patterns
4. Review caching opportunities
5. Assess algorithm complexity

DELIVERABLES:
1. Performance analysis report
2. Bottleneck identification
3. Optimization recommendations
4. Implementation plan
5. Performance benchmarks (before/after)

FOCUS: Measurement-driven analysis, bottleneck elimination.
"""
)
```

---

## Analysis & Problem-Solving Agents

### root-cause-analyst
**Purpose**: Systematically investigate complex problems to identify underlying causes through evidence-based analysis

**When to Use:**
- Complex bug investigation
- Recurring issues
- Incident analysis
- System failure diagnosis

**Template:**
```python
Task(
    subagent_type="root-cause-analyst",
    description="Investigate root cause",
    prompt="""Investigate root cause of {problem_description}.

SYMPTOMS:
- {list_symptoms}
- {error_messages}
- {reproduction_steps}

CONTEXT:
- When started: {timeline}
- Affected systems: {systems}
- Impact: {impact_description}

INVESTIGATION REQUIREMENTS:
1. Analyze error logs and stack traces
2. Review recent code changes
3. Check configuration changes
4. Examine system metrics
5. Test hypotheses systematically
6. Identify root cause (not just symptoms)

DELIVERABLES:
1. Root cause analysis report
2. Timeline of events
3. Contributing factors
4. Permanent fix recommendations
5. Prevention strategies

FOCUS: Evidence-based analysis, hypothesis testing, root cause identification.
"""
)
```

### requirements-analyst
**Purpose**: Transform ambiguous project ideas into concrete specifications through systematic requirements discovery

**When to Use:**
- Vague requirements
- Project inception
- Feature specification
- Scope definition

**Template:**
```python
Task(
    subagent_type="requirements-analyst",
    description="Analyze requirements",
    prompt="""Analyze and document requirements for {project_name}.

INITIAL REQUEST:
{vague_description}

DISCOVERY REQUIREMENTS:
1. Identify stakeholders and users
2. Define functional requirements
3. Define non-functional requirements
4. Identify constraints and dependencies
5. Define success criteria
6. Estimate complexity and effort

DELIVERABLES:
1. Requirements specification document
2. User stories with acceptance criteria
3. Data model requirements
4. API contract requirements
5. Quality requirements
6. Risk assessment

FOCUS: Transform ambiguity into concrete, actionable specifications.
"""
)
```

---

## Documentation & Knowledge Transfer Agents

### technical-writer
**Purpose**: Create clear, comprehensive technical documentation tailored to specific audiences

**When to Use:**
- API documentation needed
- Architecture documentation
- User guides
- Developer onboarding docs

**Template:**
```python
Task(
    subagent_type="technical-writer",
    description="Create technical documentation",
    prompt="""Create technical documentation for {subject}.

AUDIENCE: {target_audience}
PURPOSE: {documentation_purpose}

DOCUMENTATION REQUIREMENTS:
1. Clear, concise language
2. Appropriate technical depth
3. Code examples and diagrams
4. Step-by-step instructions
5. Troubleshooting section
6. References and links

DELIVERABLES:
1. {document_type} (README, API docs, architecture guide)
2. Diagrams (architecture, flow, sequence)
3. Code examples
4. Quick start guide
5. FAQ section

FOCUS: Clarity, comprehensiveness, audience-appropriate depth.

FORMAT: Markdown with proper heading structure.
"""
)
```

### learning-guide
**Purpose**: Teach programming concepts and explain code with focus on understanding through progressive learning

**When to Use:**
- Explaining complex code
- Teaching concepts
- Code walkthroughs
- Training materials

**Template:**
```python
Task(
    subagent_type="learning-guide",
    description="Explain code concept",
    prompt="""Explain {concept_or_code} for learning purposes.

CODE/CONCEPT: {subject}
LEARNER LEVEL: {beginner/intermediate/advanced}

TEACHING REQUIREMENTS:
1. Start with high-level overview
2. Break down into digestible parts
3. Use progressive learning (simple → complex)
4. Include practical examples
5. Explain "why" not just "what"
6. Provide exercises for practice

DELIVERABLES:
1. Conceptual explanation
2. Code walkthrough with annotations
3. Practical examples
4. Common pitfalls and mistakes
5. Practice exercises
6. Further reading resources

FOCUS: Understanding through progressive learning and practical examples.
"""
)
```

### socratic-mentor
**Purpose**: Educational guide using Socratic method for programming knowledge through strategic questioning

**When to Use:**
- Interactive learning
- Problem-solving guidance
- Critical thinking development
- Design decisions

**Template:**
```python
Task(
    subagent_type="socratic-mentor",
    description="Guide learning through questions",
    prompt="""Guide learning for {topic} using Socratic method.

TOPIC: {subject}
CONTEXT: {background_information}
LEARNING GOAL: {desired_understanding}

SOCRATIC APPROACH:
1. Ask probing questions to uncover understanding
2. Challenge assumptions
3. Guide to discover answers (don't provide directly)
4. Build on responses progressively
5. Encourage critical thinking

DELIVERABLES:
1. Question sequence
2. Follow-up questions based on likely responses
3. Guiding hints (not answers)
4. Key insights to discover
5. Summary of learning journey

FOCUS: Discovery learning through strategic questioning.
"""
)
```

---

## Custom CMZ Agents

### Custom: teams-reporting (via general-purpose)
**Purpose**: Send formatted reports to Microsoft Teams channel using proper adaptive card format

**When to Use:**
- Test results reporting
- Validation reports
- Deployment notifications
- Code review summaries
- Any Teams notification

**Template:**
```python
Task(
    subagent_type="general-purpose",
    description="Send Teams report",
    prompt="""You are a Teams reporting specialist. Send {report_type} to Microsoft Teams.

CRITICAL: Read TEAMS-WEBHOOK-ADVICE.md for proper adaptive card formatting.

REPORT DATA:
{json_data}

STEPS:
1. Verify TEAMS_WEBHOOK_URL environment variable is set
2. Create JSON file: /tmp/{report_name}.json with data above
3. Execute: python3 scripts/send_teams_report.py {report_type} --data /tmp/{report_name}.json
4. Verify HTTP 202 response (success)
5. Clean up temporary file

Expected output: "✅ Teams notification sent successfully"
Report any errors with full details and troubleshooting steps.

See .claude/commands/teams-report.md for complete methodology.
"""
)
```

### Custom: interface-verification (via general-purpose)
**Purpose**: Three-way contract verification with intelligent drift classification and root cause attribution

**When to Use:**
- Early in test orchestration (BEFORE other testing)
- Detect contract drift between frontend, API, OpenAPI
- Classify errors: FRONTEND_BUG vs API_BUG vs SPEC_BUG
- Document mismatches without fixing them
- Validate OpenAPI spec accuracy
- Pre-deployment contract validation
- After OpenAPI regeneration (detect handler disconnections)

**Template:**
```python
Task(
    subagent_type="general-purpose",
    description="Verify interface contracts",
    prompt="""You are an Interface Verification Specialist. Verify three-way contract alignment between frontend, API, and OpenAPI spec.

CRITICAL DIRECTIVES:
1. READ-ONLY ANALYSIS - Document errors, do NOT fix them
2. Intelligent Classification - Determine which source is wrong with evidence
3. Self-Validation - Verify your analysis before reporting
4. Early Execution - Run BEFORE other testing to prevent cascading failures
5. Evidence-Based - Provide exact file:line references for all mismatches

5-PHASE VERIFICATION METHODOLOGY:

Phase 1: OpenAPI Specification Analysis
- Read backend/api/openapi_spec.yaml completely
- Extract all endpoint definitions with parameters
- Build OpenAPI Contract Map (JSON):
  {{
    "endpoints": [
      {{
        "path": "/animal/{{id}}",
        "method": "PUT",
        "parameters": [
          {{"name": "id", "in": "path", "type": "string"}},
          {{"name": "body", "in": "body", "schema": "AnimalConfig"}}
        ],
        "request_body": {{"animalId": "string", "systemPrompt": "string", ...}},
        "response_200": {{"animalId": "string", "temperature": "number", ...}}
      }}
    ]
  }}
- Note validation constraints (minLength, maxLength, pattern, required)

Phase 2: API Implementation Analysis
- Read backend/api/src/main/python/openapi_server/impl/ modules
- Extract actual API handler contracts
- Build API Implementation Contract Map:
  {{
    "handlers": [
      {{
        "function": "handle_animal_update",
        "file": "impl/animals.py:123",
        "accepts": {{"animalId": "string", "systemPrompt": "string", ...}},
        "returns": {{"animalId": "string", "temperature": "number", ...}},
        "validation": ["checks animalId not empty", "validates temperature 0.0-1.0"]
      }}
    ]
  }}
- Check controller routing to handlers

Phase 3: Frontend Code Analysis
- Read frontend/src/ directories (components, services, utils)
- Extract API usage patterns
- Build Frontend Usage Contract Map:
  {{
    "api_calls": [
      {{
        "file": "frontend/src/services/animalService.js:45",
        "endpoint": "/animal/{{id}}",
        "method": "PUT",
        "sends": {{"animal_id": "string", "system_prompt": "string", ...}},
        "expects": {{"animal_id": "string", "temp": "number", ...}}
      }}
    ]
  }}
- Note TypeScript/JavaScript type definitions

Phase 4: Three-Way Contract Comparison and Classification
For each endpoint, compare all three contracts systematically:

DECISION TREE FOR CLASSIFICATION:
```
IF OpenAPI == API != Frontend:
  → FRONTEND_BUG (2 sources agree, frontend deviates)

IF OpenAPI == Frontend != API:
  → API_BUG (2 sources agree, API deviates)

IF API == Frontend != OpenAPI:
  → SPEC_BUG (2 sources agree, OpenAPI outdated)

IF OpenAPI != API != Frontend (all different):
  → MULTIPLE (all sources have errors, prioritize fixes)

IF unclear which is authoritative:
  → AMBIGUOUS (delegate to root-cause-analyst)
```

CLASSIFICATION EXAMPLES:

Example 1: FRONTEND_BUG
Field name mismatch:
- OpenAPI:  "animalId" ✅
- API:      "animalId" ✅
- Frontend: "animal_id" ❌
→ Classification: FRONTEND_BUG (frontend uses snake_case, should use camelCase)
→ Evidence: frontend/src/services/animalService.js:45

Example 2: API_BUG
Missing required field:
- OpenAPI:  "systemPrompt" required ✅
- Frontend: sends "systemPrompt" ✅
- API:      doesn't validate "systemPrompt" ❌
→ Classification: API_BUG (API doesn't enforce required field)
→ Evidence: impl/animals.py:123 missing validation

Example 3: SPEC_BUG
OpenAPI outdated after feature addition:
- Frontend: sends "temperature" field ✅
- API:      accepts "temperature" field ✅
- OpenAPI:  "temperature" not in spec ❌
→ Classification: SPEC_BUG (OpenAPI needs update)
→ Evidence: openapi_spec.yaml missing field, impl/animals.py:145 supports it

Example 4: MULTIPLE
Complete mismatch:
- OpenAPI:  "animalId", "config" ❌
- API:      "animal_id", "settings" ❌
- Frontend: "id", "configuration" ❌
→ Classification: MULTIPLE (all sources wrong, needs coordination)
→ Recommendation: Schedule alignment meeting

Example 5: AMBIGUOUS
Unclear which is authoritative:
- OpenAPI:  "temperature" type: string ❓
- API:      "temperature" type: float ❓
- Frontend: "temperature" type: number ❓
→ Classification: AMBIGUOUS
→ Action: Delegate to root-cause-analyst for business logic investigation

Build Drift Report with classifications and evidence:
{{
  "mismatches": [
    {{
      "endpoint": "/animal/{{id}}",
      "field": "animalId",
      "classification": "FRONTEND_BUG",
      "severity": "HIGH",
      "evidence": {{
        "openapi": {{"location": "openapi_spec.yaml:123", "value": "animalId"}},
        "api": {{"location": "impl/animals.py:145", "value": "animalId"}},
        "frontend": {{"location": "services/animalService.js:45", "value": "animal_id"}}
      }},
      "recommendation": "Update frontend to use camelCase: animalId"
    }}
  ]
}}

Phase 5: Self-Validation and Comprehensive Reporting
SELF-VALIDATION CHECKLIST (MANDATORY):

1. Contract Map Completeness:
```python
assert len(openapi_contract_map["endpoints"]) > 0, "OpenAPI map empty"
assert len(api_contract_map["handlers"]) > 0, "API map empty"
assert len(frontend_contract_map["api_calls"]) > 0, "Frontend map empty"
```

2. Classification Evidence:
```python
for mismatch in mismatches:
    assert 'classification' in mismatch, "Missing classification"
    assert 'evidence' in mismatch, "Missing evidence"
    assert mismatch['classification'] in [
        'FRONTEND_BUG', 'API_BUG', 'SPEC_BUG', 'MULTIPLE', 'AMBIGUOUS'
    ], f"Invalid classification: {{mismatch['classification']}}"
```

3. Classification Logic:
```python
if classification == 'FRONTEND_BUG':
    assert evidence['openapi']['value'] == evidence['api']['value'], "Logic error"
    assert evidence['frontend']['value'] != evidence['openapi']['value'], "Logic error"
```

4. Severity Assignment:
```python
severity_map = {{
    "Missing required field": "CRITICAL",
    "Field name mismatch": "HIGH",
    "Type mismatch": "HIGH",
    "Optional field missing": "MEDIUM",
    "Documentation outdated": "LOW"
}}
```

5. Validation Output:
```
✅ Self-Validation Results:
- Contract maps complete: OpenAPI(23 endpoints), API(23 handlers), Frontend(21 calls)
- All mismatches classified: 12 total (5 FRONTEND_BUG, 3 API_BUG, 2 SPEC_BUG, 2 MULTIPLE)
- Evidence provided for all: 12/12 with file:line references
- Classification logic validated: 12/12 correct
- Severity assigned: 3 CRITICAL, 6 HIGH, 2 MEDIUM, 1 LOW
```

Generate comprehensive report:
claudedocs/interface-verification/{{feature_name}}/
├── verification-report.md (complete analysis)
├── openapi-contract-map.json (extracted OpenAPI)
├── api-contract-map.json (extracted API)
├── frontend-contract-map.json (extracted frontend)
├── drift-report.json (all mismatches)
└── recommendations.md (prioritized fixes)

Report Structure:
```markdown
# Interface Verification Report: {{feature_name}}

## Executive Summary
- Total Endpoints Analyzed: {{count}}
- Mismatches Found: {{count}} ({{by_severity}})
- Classification: {{frontend_bugs}} FRONTEND, {{api_bugs}} API, {{spec_bugs}} SPEC

## Critical Issues (IMMEDIATE ATTENTION)
### FRONTEND_BUG: Missing Required Field
**Endpoint**: PUT /animal/{{id}}
**Field**: systemPrompt
**Evidence**:
- OpenAPI (openapi_spec.yaml:234): required field "systemPrompt"
- API (impl/animals.py:145): validates systemPrompt presence
- Frontend (services/animalService.js:67): does NOT send systemPrompt ❌
**Impact**: API rejects requests, frontend shows generic error
**Recommendation**: Update animalService.js line 67 to include systemPrompt

## Detailed Analysis by Endpoint
[For each endpoint with mismatches...]

## Self-Validation Results
✅ All contract maps complete
✅ All classifications have evidence
✅ Classification logic validated
✅ Severity appropriately assigned
```

INTEGRATION WITH TEST ORCHESTRATION:

Test Orchestrator Phase 0 (BEFORE all other testing):
1. Delegate to interface-verification agent
2. Wait for verification report
3. IF CRITICAL issues found:
   - STOP all further testing
   - Report to user: "Contract drift detected, fix before testing"
4. IF only HIGH/MEDIUM/LOW issues:
   - Log warnings but proceed with testing
   - Include contract issues in final report

FEATURE TO VERIFY: {{feature_name}}
ENDPOINTS: {{list_endpoints}}

DELIVERABLES:
1. OpenAPI Contract Map (JSON)
2. API Implementation Contract Map (JSON)
3. Frontend Usage Contract Map (JSON)
4. Drift Report with classifications and evidence (JSON + Markdown)
5. Self-validation results (pass/fail with details)
6. Prioritized recommendations (CRITICAL → LOW)

STOPPING CONDITIONS (BLOCK FURTHER TESTING):
- ≥3 CRITICAL mismatches (contract severely broken)
- Authentication endpoint drift (security risk)
- Required field mismatches (data corruption risk)

SUCCESS CRITERIA:
- ✅ All three contract maps generated successfully
- ✅ 100% of endpoints analyzed
- ✅ All mismatches classified with evidence
- ✅ Self-validation passed (all checks green)
- ✅ Exact file:line references for all findings
- ✅ Classification logic validated
- ✅ Severity appropriately assigned

COMPARISON WITH /validate-contracts COMMAND:
- `/validate-contracts` = User command with generic drift detection
- `interface-verification` = Delegatable agent with intelligent classification
- Agent adds: Root cause attribution, severity classification, self-validation
- Use agent in test orchestration, command for manual validation

See .claude/commands/verify-interface.md for complete 5-phase methodology.
See VERIFY-INTERFACE-ADVICE.md for classification patterns and troubleshooting.
"""
)
```

---

## Agent Selection Guide

### By Task Category

**Testing:**
- Comprehensive test strategy → `quality-engineer`
- Verify test coverage → `test-coverage-verifier`
- Generate new tests → `general-purpose` (test-generation)
- Backend endpoint testing with edge cases → `general-purpose` (backend-testing)
- Check DynamoDB persistence → `persistence-verifier`
- Orchestrate all test types with error classification → `general-purpose` (test-orchestrator)
- Frontend UI comprehensive testing → `general-purpose` (frontend-comprehensive-testing)

**Backend Development:**
- Design architecture → `backend-architect`
- Implement Python code → `python-expert`
- Verify implementation → `backend-feature-verifier`

**Frontend Development:**
- Design UI architecture → `frontend-architect`
- Verify UI implementation → `frontend-feature-verifier`

**System Design:**
- Overall architecture → `system-architect`
- Infrastructure/DevOps → `devops-architect`

**Code Quality:**
- Refactoring → `refactoring-expert`
- Security audit → `security-engineer`
- Performance optimization → `performance-engineer`

**Problem Solving:**
- Debug complex issues → `root-cause-analyst`
- Define requirements → `requirements-analyst`

**Documentation:**
- Technical docs → `technical-writer`
- Teaching/explaining → `learning-guide` or `socratic-mentor`

**Reporting:**
- Teams notifications → `general-purpose` (teams-reporting)

---

## Multi-Agent Workflows

### Complete Feature Development
```python
# Phase 1: Requirements
Task(subagent_type="requirements-analyst", description="Analyze feature requirements", ...)

# Phase 2: Design
Task(subagent_type="backend-architect", description="Design backend", ...)
Task(subagent_type="frontend-architect", description="Design frontend", ...)

# Phase 3: Implementation
Task(subagent_type="python-expert", description="Implement backend", ...)

# Phase 4: Testing
Task(subagent_type="general-purpose", description="Generate test suite", ...)
Task(subagent_type="general-purpose", description="Backend comprehensive testing", ...)

# Phase 5: Verification
Task(subagent_type="backend-feature-verifier", description="Verify backend", ...)
Task(subagent_type="test-coverage-verifier", description="Verify coverage", ...)
Task(subagent_type="persistence-verifier", description="Verify DynamoDB", ...)

# Phase 6: Reporting
Task(subagent_type="general-purpose", description="Send completion report", ...)
```

### Bug Investigation & Fix
```python
# Phase 1: Investigation
Task(subagent_type="root-cause-analyst", description="Investigate root cause", ...)

# Phase 2: Fix Implementation
Task(subagent_type="python-expert", description="Implement fix", ...)

# Phase 3: Testing
Task(subagent_type="general-purpose", description="Generate regression tests", ...)

# Phase 4: Verification
Task(subagent_type="test-coverage-verifier", description="Verify test coverage", ...)

# Phase 5: Reporting
Task(subagent_type="general-purpose", description="Send bug fix report", ...)
```

### Security Audit & Remediation
```python
# Phase 1: Audit
Task(subagent_type="security-engineer", description="Conduct security audit", ...)

# Phase 2: Fix
Task(subagent_type="python-expert", description="Implement security fixes", ...)

# Phase 3: Verification
Task(subagent_type="security-engineer", description="Verify fixes", ...)

# Phase 4: Documentation
Task(subagent_type="technical-writer", description="Document security measures", ...)

# Phase 5: Reporting
Task(subagent_type="general-purpose", description="Send security report", ...)
```

### Backend Comprehensive Testing
```python
# Phase 1: OpenAPI Validation
Task(subagent_type="general-purpose", description="Backend comprehensive testing",
     prompt="""Backend Testing Agent - validate OpenAPI spec for {feature}.
     Read backend/api/openapi_spec.yaml
     Report missing validation constraints as bugs
     Generate OpenAPI Gap Report (CRITICAL/HIGH/MEDIUM)""")

# Phase 2: Edge Case Testing (if OpenAPI validation passes)
Task(subagent_type="general-purpose", description="Execute edge case tests",
     prompt="""Backend Testing Agent - test all edge cases.
     25+ edge cases per text field (Unicode, security, boundaries)
     15+ edge cases per numeric field
     Verify DynamoDB persistence for all successful operations
     Clean up 100% of test data""")

# Phase 3: Error Investigation (if "not implemented" errors found)
Task(subagent_type="root-cause-analyst", description="Investigate not implemented",
     prompt="""Investigate 501 errors. Read ENDPOINT-WORK-ADVICE.md.
     Classify: TRUE BUG vs OPENAPI ARTIFACT""")

# Phase 4: Reporting
Task(subagent_type="general-purpose", description="Send backend test results",
     prompt="""Teams Reporting - send backend test results.
     Include OpenAPI gaps, edge case results, cleanup verification""")
```

### Comprehensive Test Orchestration
```python
# Phase 1: Coverage Analysis
Task(subagent_type="test-coverage-verifier", description="Analyze test coverage", ...)

# Phase 2: Multi-Layer Testing (PARALLEL)
Task(subagent_type="general-purpose", description="Backend comprehensive testing", ...)
Task(subagent_type="backend-feature-verifier", description="Verify all backends", ...)
Task(subagent_type="frontend-feature-verifier", description="Verify all frontends", ...)
Task(subagent_type="persistence-verifier", description="Verify DynamoDB ops", ...)

# Phase 3: Error Analysis
Task(subagent_type="root-cause-analyst", description="Investigate failures", ...)

# Phase 4: Orchestration (Complete Coordination)
Task(subagent_type="general-purpose", description="Orchestrate comprehensive testing",
     prompt="""Senior QA Test Orchestrator - coordinate all testing with error classification.
     Read ENDPOINT-WORK-ADVICE.md before declaring regressions.
     See .claude/commands/orchestrate-tests.md for methodology.""")

# Phase 5: Reporting
Task(subagent_type="general-purpose", description="Send test results to Teams", ...)
```

---

## Best Practices

**1. Clear Descriptions**
- Use 3-5 word descriptions
- Be specific about the task
- Example: "Generate unit tests" not "Do testing"

**2. Detailed Prompts**
- Provide context and background
- List specific requirements
- Define success criteria
- Reference relevant documentation

**3. Appropriate Agent Selection**
- Choose agent matching task domain
- Use specialized agents when available
- Use general-purpose for custom CMZ agents

**4. Parallel Execution**
- Delegate independent tasks in single message
- Use multiple Task calls for parallel work
- Example: Delegate frontend + backend verification simultaneously

**5. Result Verification**
- Always check agent deliverables
- Validate against requirements
- Don't blindly trust results

**6. Documentation References**
- Point agents to relevant docs
- Include file paths and locations
- Reference methodology documents

---

## References

- **Agent Documentation**: This file (AGENT-DELEGATION-TEMPLATES.md)
- **Teams Reporting**: `.claude/commands/teams-report.md`, `TEAMS-REPORTING-ADVICE.md`
- **Test Generation**: `.claude/commands/generate-tests.md`, `TEST-GENERATION-ADVICE.md`
- **Test Orchestration**: `.claude/commands/orchestrate-tests.md`, `TEST-ORCHESTRATION-ADVICE.md`
- **Project Context**: `CLAUDE.md`
- **Task Tool Documentation**: Claude Code built-in help
