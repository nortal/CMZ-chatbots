# /nextfive Command

Implement the next 5 high-priority Jira tickets from specified epic or concept, following the same systematic approach we used for PR003946-90, PR003946-72, PR003946-73, PR003946-69, and PR003946-66.

## Usage

### Basic Usage (Discovery Mode)
```
/nextfive
# Discovers and implements next 5 high-priority tickets from API validation epic
```

### Epic-Based Usage
```
# By epic number
/nextfive PR003946-170
# Discovers and implements next 5 tickets from Enable Chat Epic

/nextfive 170
# Short form - assumes PR003946 project prefix
```

### Concept-Based Usage
```
# By keyword or phrase
/nextfive "tickets related to chat"
# Searches for tickets with "chat" in title/description

/nextfive "authentication"
# Finds tickets related to authentication

/nextfive "family management"
# Finds tickets for family management features
```

### Targeted Usage (Specific Ticket Mode)
```
# Single ticket
/nextfive PR003946-91
# Implements PR003946-91 and resolves any blocking dependencies first

# Multiple tickets
/nextfive PR003946-91 PR003946-88 PR003946-75
# Implements specified tickets with combined dependency resolution

# Multiple tickets (comma-separated alternative)
/nextfive PR003946-91,PR003946-88,PR003946-75
# Same as above, supports both space and comma separation

# If dependencies exceed 5 tickets total, reports and continues with priority subset
```

### Mixed Usage
```
# Epic plus specific tickets
/nextfive PR003946-170 PR003946-156
# Prioritizes PR003946-156 from the epic, fills remaining slots from epic

# Concept plus tickets
/nextfive "chat" PR003946-157 PR003946-158
# Ensures these two tickets are included, fills rest from chat-related tickets
```

## Context
- CMZ chatbot backend API using OpenAPI-first development
- Flask/Connexion with DynamoDB persistence
- Docker containerized development environment
- All business logic must go in `impl/` directory (never in generated code)

## Required Process - Discovery-First Approach with TDD

1. **DISCOVERY FIRST**: Run integration tests to identify actual state (never assume based on Jira status)
2. **TDD CHECK**: If ticket doesn't exist in test suite, CREATE TEST FIRST following TDD practices (see below)
3. **ENHANCED DISCOVERY**: Use `scripts/enhanced_discovery.py` for dependency analysis and priority scoring
4. **TWO-PHASE QUALITY GATES**: Execute `scripts/two_phase_quality_gates.sh` for systematic validation
5. **SEQUENTIAL REASONING**: Use MCP to predict outcomes and plan systematic approach
6. **SCOPE ASSESSMENT**: If fewer than 5 failing tickets, identify comprehensive enhancement opportunities
7. **GIT WORKFLOW**: MANDATORY - Always start from dev, create feature branch, target dev for MR
8. **SYSTEMATIC IMPLEMENTATION**: Focus on OpenAPI spec enhancements + model regeneration + infrastructure
9. **SECURITY & QUALITY**: Address GitHub Advanced Security scanner issues systematically
10. **REPOSITORY HYGIENE**: Apply learnings from PR #32 retrospective to prevent test artifact pollution
11. **FEATURE BRANCH MR**: Create MR from feature branch targeting dev (never commit directly to dev)
12. **COPILOT REVIEW**: Add reviewer and address feedback with inline comment resolution
13. **CORRECTIVE JIRA**: Verify ticket mapping before updates, use corrective comments for mistakes

## TDD Process for New Tickets

When a ticket doesn't exist in the test suite (like PR003946-144):

1. **Create Test Structure** (follow .claude/commands/setup-tdd.md):
   ```bash
   mkdir -p tests/integration/PR003946-XXX
   ```

2. **Create Test Specification**:
   - `PR003946-XXX-ADVICE.md` - Feature description & acceptance criteria
   - `PR003946-XXX-howto-test.md` - Explicit test instructions with pass/fail criteria
   - Add test method to `test_api_validation_epic.py` or appropriate test file

3. **Write Failing Test First**:
   ```python
   def test_pr003946_xxx_feature_description(self, client):
       """PR003946-XXX: [Feature description from Jira or inferred from context]"""
       # Test implementation that will initially fail
       response = client.post('/endpoint', ...)
       assert response.status_code == expected_code
   ```

4. **Run Test to Verify It Fails**:
   ```bash
   pytest tests/integration/test_api_validation_epic.py::test_pr003946_xxx -xvs
   ```

5. **Implement Feature** to make test pass

6. **Document Results**:
   - `PR003946-XXX-YYYY-MM-DD-HHMMSS-results.md` - Test execution report
   - `PR003946-XXX-history.txt` - Pass/fail history tracking

## Technical Requirements
- **Focus on Endpoint Implementation**: Prioritize new API endpoints over strict business validation
- Follow existing patterns in `openapi_server/impl/`
- Maintain OpenAPI specification compliance
- Use consistent Error schema with code/message/details structure
- Include proper audit timestamps and server-generated IDs
- Basic CRUD operations with DynamoDB integration
- Simple validation (required fields, basic formats) rather than complex business rules

## Complete Workflow

1. **DISCOVERY PHASE**: Run integration tests to identify actual failing tickets
2. **PLANNING PHASE**: List discovered tickets and use sequential reasoning to plan implementation
3. **JIRA START PHASE**: Move selected tickets to "In Progress" status
   - Use `./scripts/manage_jira_tickets.sh batch-start PR003946-XX PR003946-YY ...`
   - Automatic comment added: "🚀 Starting implementation via /nextfive command"
4. **SCOPE EXPANSION**: If fewer than 5 tickets, identify new endpoint opportunities from OpenAPI spec
5. **IMPLEMENTATION PHASE**: Implement systematically with comprehensive testing
6. **QUALITY PHASE**: Address security issues and run quality checks
7. **MR PHASE**: Create MR targeting `dev` branch, then add Copilot reviewer with `gh pr edit <PR_NUMBER> --add-reviewer Copilot`
8. **DOCUMENTATION PHASE**: Add history documentation to MR
9. **REVIEW PHASE**: Wait for and address Copilot review feedback (one round)
   - Address all inline code comments and suggestions
   - **Mark resolved comments**: Use `gh pr comment <comment-id> --body "✅ Resolved: [brief description]"` to mark inline comments as resolved
   - Commit fixes with descriptive messages explaining what was addressed
10. **VALIDATION PHASE**: Re-test and verify all functionality after changes
11. **JIRA DONE PHASE**: Move implemented tickets to "Done" status when MR is ready
   - Use `./scripts/manage_jira_tickets.sh batch-done PR003946-XX PR003946-YY ...`
   - Automatic comment added: "✅ Implementation complete - MR ready for merge"
12. **COMPLETION PHASE**: Use sequential reasoning to validate all steps completed correctly and ensure merge readiness

## Implementation Modes

### Targeted Ticket Mode
**When specific tickets provided, analyze dependencies and implement in priority order:**

#### Single Ticket Mode (e.g., PR003946-91)
1. **Target Analysis**: Verify ticket exists and get current status
2. **Dependency Analysis**: Check if target ticket is blocked by other tickets
3. **Priority Resolution**: Address blocking tickets first, up to 5 total tickets
4. **Systematic Implementation**: Implement in dependency order (blockers first, target last)

#### Multiple Ticket Mode (e.g., PR003946-91 PR003946-88 PR003946-75)
1. **Multi-Target Parsing**: Parse space-separated or comma-separated ticket list
2. **Combined Dependency Analysis**: Build complete dependency graph for all specified tickets
3. **Dependency Deduplication**: Remove duplicate dependencies across multiple tickets
4. **Priority Ordering**: Create implementation sequence (all dependencies first, then targets)
5. **Smart Limiting**: If total >5 tickets, prioritize by dependency depth and user specification order
6. **Systematic Implementation**: Execute in calculated priority order

### Limit Handling
- **≤5 Total Tickets**: Implement all (dependencies + specified + fill remaining with discovery)
- **>5 Total Tickets**: Inform user of total count, implement top 5 priority tickets
- **Dependencies Only >5**: Inform user to re-run after merge, focus on critical dependencies

## Argument Detection Logic

### Intelligent Argument Parser
```bash
# Parse and classify the argument provided to /nextfive
ARGUMENT="$1"

# DETECTION LOGIC:
# 1. Epic Detection (PR003946-XXX where XXX is an epic)
if [[ "$ARGUMENT" =~ ^PR003946-[0-9]+$ ]]; then
    # Check if it's an epic by looking for child tickets
    CHILD_COUNT=$(curl -s -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
        "$JIRA_BASE_URL/rest/api/3/search?jql=parent=$ARGUMENT" | jq '.total')

    if [ "$CHILD_COUNT" -gt 0 ]; then
        echo "✅ Detected Epic: $ARGUMENT with $CHILD_COUNT child tickets"
        MODE="epic"
        EPIC_KEY="$ARGUMENT"
    else
        echo "📋 Detected single ticket: $ARGUMENT"
        MODE="ticket"
        TICKET_KEY="$ARGUMENT"
    fi

# 2. Short Epic Number (just digits, assumes PR003946 prefix)
elif [[ "$ARGUMENT" =~ ^[0-9]+$ ]]; then
    EPIC_KEY="PR003946-$ARGUMENT"
    echo "🔍 Checking if PR003946-$ARGUMENT is an epic..."
    CHILD_COUNT=$(curl -s -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
        "$JIRA_BASE_URL/rest/api/3/search?jql=parent=$EPIC_KEY" | jq '.total')

    if [ "$CHILD_COUNT" -gt 0 ]; then
        echo "✅ Detected Epic: $EPIC_KEY with $CHILD_COUNT child tickets"
        MODE="epic"
    else
        echo "📋 Detected single ticket: $EPIC_KEY"
        MODE="ticket"
        TICKET_KEY="$EPIC_KEY"
    fi

# 3. Concept/Keyword Detection (text search)
elif [[ "$ARGUMENT" =~ [a-zA-Z] ]]; then
    echo "🔍 Searching for tickets related to: $ARGUMENT"
    MODE="concept"
    SEARCH_TERM="$ARGUMENT"

# 4. No Argument (default discovery mode)
else
    echo "📊 No argument provided, using default discovery mode"
    MODE="discovery"
    EPIC_KEY="PR003946-61"  # Default API validation epic
fi
```

### Epic-Based Discovery
```bash
# When epic is detected, find child tickets
if [ "$MODE" = "epic" ]; then
    echo "Discovering tickets from epic: $EPIC_KEY"

    # Get all child tickets of the epic
    TICKETS=$(curl -s -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
        "$JIRA_BASE_URL/rest/api/3/search?jql=parent=$EPIC_KEY AND status!=Done&fields=key,summary,priority,status" \
        | jq -r '.issues[] | "\(.key) - \(.fields.summary) [\(.fields.status.name)]"')

    echo "Found tickets in epic:"
    echo "$TICKETS"

    # Prioritize by status and priority
    HIGH_PRIORITY=$(echo "$TICKETS" | grep -E "Highest|High" | head -5)
    TODO_TICKETS=$(echo "$TICKETS" | grep "To Do" | head -5)
fi
```

### Concept-Based Discovery
```bash
# When searching by concept/keyword
if [ "$MODE" = "concept" ]; then
    # Remove quotes if present
    SEARCH_TERM="${SEARCH_TERM//\"/}"

    echo "Searching for tickets containing: $SEARCH_TERM"

    # JQL search for tickets with the concept in summary or description
    JQL="project=PR003946 AND (summary ~ \"$SEARCH_TERM\" OR description ~ \"$SEARCH_TERM\") AND status!=Done"

    TICKETS=$(curl -s -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
        "$JIRA_BASE_URL/rest/api/3/search?jql=$JQL&fields=key,summary,priority,status" \
        | jq -r '.issues[] | "\(.key) - \(.fields.summary) [\(.fields.status.name)]"')

    if [ -z "$TICKETS" ]; then
        echo "⚠️ No tickets found for concept: $SEARCH_TERM"
        echo "Falling back to discovery mode"
        MODE="discovery"
    else
        echo "Found tickets matching '$SEARCH_TERM':"
        echo "$TICKETS"
    fi
fi
```

## Discovery Commands

### Discovery Mode (Standard /nextfive)
```bash
# Step 1: ALWAYS run integration tests first to find actual failing tickets
python -m pytest tests/integration/test_api_validation_epic.py -v

# Step 2: Enhanced discovery with dependency analysis and priority scoring
# Now supports dynamic epic selection based on argument
EPIC_TO_SEARCH="${EPIC_KEY:-PR003946-61}"  # Use detected epic or default
python scripts/enhanced_discovery.py --epic "$EPIC_TO_SEARCH" --include-dependencies

# Step 3: Identify specific failing test methods and their associated tickets
grep -A 2 -B 1 "PR003946-" tests/integration/test_api_validation_epic.py

# Step 4: If fewer than 5 failing tickets, examine OpenAPI spec for enhancement opportunities
grep -A 5 -B 5 "paths:" backend/api/openapi_spec.yaml

# Step 5: Execute two-phase quality gates for systematic validation
./scripts/two_phase_quality_gates.sh --phase1-only  # Quick validation first
```

### Targeted Mode (/nextfive PR003946-XX [PR003946-YY ...])
```bash
# Step 1: PARSE MULTIPLE TICKETS
# Parse space-separated or comma-separated ticket arguments
TICKETS_INPUT="$*"  # All arguments after /nextfive
TICKETS=($(echo "$TICKETS_INPUT" | tr ',' ' '))  # Convert comma to space
echo "Target tickets: ${TICKETS[@]}"

# Step 2: MULTI-TARGET VALIDATION
# Verify each target ticket exists and get status
for TICKET in "${TICKETS[@]}"; do
    echo "Analyzing: $TICKET"
    grep -r "$TICKET" tests/integration/ jira_mappings.md 2>/dev/null || echo "⚠️ $TICKET not found"
done

# Step 3: COMBINED DEPENDENCY ANALYSIS
# Build complete dependency graph for ALL specified tickets
DEPENDENCIES=()
for TICKET in "${TICKETS[@]}"; do
    echo "Dependencies for $TICKET:"
    grep -A 3 -B 3 "$TICKET" tests/integration/test_api_validation_epic.py
    # Look for: "depends on", "blocked by", "requires", "after"
    TICKET_DEPS=$(grep -A 5 -B 5 "blocked\|depends\|requires\|after.*$TICKET" tests/integration/test_api_validation_epic.py | grep -o 'PR003946-[0-9]*')
    DEPENDENCIES+=($TICKET_DEPS)
done

# Step 4: DEDUPLICATION & PRIORITY ORDERING
# Remove duplicate dependencies and create implementation sequence
ALL_TICKETS=($(printf '%s\n' "${DEPENDENCIES[@]}" "${TICKETS[@]}" | sort -u))
TOTAL_COUNT=${#ALL_TICKETS[@]}
echo "Total tickets (dependencies + targets): $TOTAL_COUNT"

# Step 5: SMART LIMITING
if [ $TOTAL_COUNT -gt 5 ]; then
    echo "⚠️ $TOTAL_COUNT tickets found (exceeds 5 limit)"
    echo "Prioritizing by dependency depth and specification order"
    echo "Consider re-running /nextfive after merge for remaining tickets"
    # Take first 5 by priority: critical dependencies first, then specified targets
    FINAL_TICKETS=("${ALL_TICKETS[@]:0:5}")
else
    echo "✅ $TOTAL_COUNT tickets within limit, filling remaining slots with discovery"
    FINAL_TICKETS=("${ALL_TICKETS[@]}")
fi

# Step 6: FALLBACK TO DISCOVERY if no valid targets found
if [ ${#FINAL_TICKETS[@]} -eq 0 ]; then
    echo "No valid target tickets found, falling back to discovery mode"
    python -m pytest tests/integration/test_api_validation_epic.py -v
fi
```

### Mandatory Setup (Both Modes)
```bash
# MANDATORY - Create feature branch before any work
git checkout dev && git pull origin dev
git checkout -b feature/api-validation-improvements-$(date +%Y%m%d)
```

**Then use sequential reasoning MCP to plan systematic implementation approach.**

## Enhancement Strategy

**When fewer than 5 failing tickets exist, implement systematic enhancements:**

1. **OpenAPI Specification Enhancements** (validation patterns, schemas, constraints)
2. **Model Regeneration + Validation Logic** (25+ model files with consistent patterns)
3. **Centralized Infrastructure** (error handling, utilities, common patterns)
4. **Security Scanner Resolution** (CodeQL, unused imports, grammar fixes)
5. **Cross-Domain Validation** (referential integrity, business rules)

## MCP Tool Selection
- **Sequential Reasoning**: ALWAYS use for planning and prediction (essential)
- **Context7**: Framework-specific patterns and official documentation
- **Morphllm**: Bulk validation pattern application across multiple files
- **Magic**: Not typically needed for backend API validation work
- **Playwright**: Not needed for API-only validation improvements

## Integration Features
- **Enhanced Discovery**: Use `scripts/enhanced_discovery.py` for systematic ticket discovery with dependency analysis and priority scoring
- **Two-Phase Quality Gates**: Integrate `scripts/two_phase_quality_gates.sh` for systematic validation (Phase 1: fundamentals, Phase 2: comprehensive)
- **Template-Driven Creation**: Use `scripts/ticket_template_generator.py` for consistent, high-quality ticket generation
- **Repository Hygiene**: Apply learnings from `docs/RETROSPECTIVE_PR32_LEARNINGS.md` to prevent test artifact pollution
- **Quality-First Approach**: Never proceed to Phase 2 comprehensive testing until Phase 1 fundamentals pass

## Dependency Resolution Examples

### Single Ticket Examples

#### Example 1: Simple Single Ticket
```bash
/nextfive PR003946-91
# Target found, no dependencies → implement PR003946-91 + discover 4 more tickets
# Result: 5 tickets implemented (1 targeted + 4 discovered)
```

#### Example 2: Single Ticket with Dependencies
```bash
/nextfive PR003946-91
# Analysis finds: PR003946-91 depends on PR003946-88, PR003946-89
# Implementation order: PR003946-88 → PR003946-89 → PR003946-91 + discover 2 more
# Result: 5 tickets implemented (3 dependency chain + 2 discovered)
```

### Multiple Ticket Examples

#### Example 3: Simple Multiple Tickets
```bash
/nextfive PR003946-91 PR003946-75 PR003946-72
# 3 targets found, no dependencies → implement all 3 + discover 2 more
# Result: 5 tickets implemented (3 specified + 2 discovered)
```

#### Example 4: Multiple Tickets with Shared Dependencies
```bash
/nextfive PR003946-91 PR003946-88 PR003946-75
# Analysis finds:
#   PR003946-91 depends on PR003946-89
#   PR003946-88 no dependencies
#   PR003946-75 depends on PR003946-89 (shared dependency)
# Implementation order: PR003946-89 → PR003946-91 → PR003946-88 → PR003946-75 + 1 more
# Result: 5 tickets implemented (1 dependency + 3 specified + 1 discovered)
```

#### Example 5: Multiple Tickets with Complex Dependencies
```bash
/nextfive PR003946-91 PR003946-88 PR003946-75
# Analysis finds:
#   PR003946-91 depends on PR003946-89, PR003946-87
#   PR003946-88 depends on PR003946-86
#   PR003946-75 depends on PR003946-89 (shared), PR003946-85
# Total: 3 specified + 4 unique dependencies = 7 tickets
# Response: "7 tickets found (exceeds 5 limit). Implementing priority 5:
#           PR003946-87 → PR003946-89 → PR003946-86 → PR003946-91 → PR003946-88"
# Result: 5 highest priority tickets by dependency depth
```

#### Example 6: Comma-Separated Format
```bash
/nextfive PR003946-91,PR003946-88,PR003946-75
# Same as space-separated, supports both formats
# Parsed as: ["PR003946-91", "PR003946-88", "PR003946-75"]
```

### Epic-Based Examples

#### Example 7: Epic Number Detection
```bash
/nextfive PR003946-170
# Detected as Epic: Enable Chat Epic with 14 child tickets
# Filters to non-Done tickets, prioritizes by status and priority
# Result: Implements top 5 tickets from the epic
```

#### Example 8: Short Epic Number
```bash
/nextfive 170
# Expands to PR003946-170, detects as epic
# Same result as full epic number
```

#### Example 9: Epic with Mixed Priorities
```bash
/nextfive PR003946-61
# API Validation Epic with various ticket states
# Prioritizes: In Progress tickets → High/Highest priority → To Do status
# Result: 5 most important tickets from epic
```

### Concept-Based Examples

#### Example 10: Keyword Search
```bash
/nextfive "chat"
# Searches for tickets with "chat" in summary or description
# Finds: PR003946-156, PR003946-157, PR003946-158, etc.
# Result: Implements 5 chat-related tickets
```

#### Example 11: Multi-Word Concept
```bash
/nextfive "family management"
# Searches for tickets containing "family management"
# Finds family-related features and bugs
# Result: 5 family management tickets
```

#### Example 12: Concept Not Found
```bash
/nextfive "blockchain"
# No tickets found with "blockchain"
# Falls back to standard discovery mode
# Result: Default /nextfive behavior
```

### Mixed Mode Examples

#### Example 13: Epic Plus Specific Ticket
```bash
/nextfive PR003946-170 PR003946-157
# Epic detected: PR003946-170 (Enable Chat)
# Ensures PR003946-157 is included (if it's in the epic)
# Fills remaining 4 slots from epic tickets
# Result: PR003946-157 + 4 other epic tickets
```

#### Example 14: Concept Plus Tickets
```bash
/nextfive "authentication" PR003946-88 PR003946-91
# Searches for auth-related tickets
# Ensures PR003946-88 and PR003946-91 are included
# Fills remaining slots from auth search results
# Result: 2 specified + 3 auth-related tickets
```

### Error Handling Examples

#### Example 15: Mixed Valid/Invalid Tickets
```bash
/nextfive PR003946-91 PR003946-999 PR003946-75
# Analysis: PR003946-91 ✅, PR003946-999 ❌, PR003946-75 ✅
# Result: Process valid tickets (PR003946-91, PR003946-75) + their dependencies
```

#### Example 16: No Valid Tickets Found
```bash
/nextfive PR003946-999 PR003946-998
# All target tickets not found → fallback to discovery mode
# Result: Standard /nextfive behavior (discover and implement 5 tickets)
```

#### Example 17: Ticket Not in Test Suite (TDD Required)
```bash
/nextfive PR003946-144
# Ticket PR003946-144 not found in test suite
# TDD Process Triggered:
#   1. Create test structure: tests/integration/PR003946-144/
#   2. Write PR003946-144-ADVICE.md with feature requirements
#   3. Write PR003946-144-howto-test.md with test steps
#   4. Add test_pr003946_144_feature() to test_api_validation_epic.py
#   5. Run test to verify it fails
#   6. Implement feature to make test pass
#   7. Document in PR003946-144-YYYY-MM-DD-HHMMSS-results.md
# Result: Test created first, then implementation follows TDD principles
```

## Retrospective Integration (PR #32 Learnings)

**Critical Process Improvements Based on PR #32 Analysis:**

### Repository Hygiene Enforcement
- **Problem**: 72+ test artifact files incorrectly committed (test-failed-*.png, video.webm, error-context.md)
- **Solution**: Enhanced .gitignore patterns and automated cleanup procedures
- **Implementation**: Prevent test artifacts with `**/test-results/`, `**/*.webm`, `**/*.png` exclusions

### Two-Phase Quality Gates
- **Problem**: Tests failing across all 6 browsers but PR still merged
- **Solution**: Systematic validation with `scripts/two_phase_quality_gates.sh`
- **Implementation**: Phase 1 (fundamentals) must pass before Phase 2 (comprehensive)

### Enhanced Discovery
- **Problem**: Ad-hoc ticket selection without dependency analysis
- **Solution**: Intelligent ticket discovery with `scripts/enhanced_discovery.py`
- **Implementation**: Priority scoring, dependency graphing, optimal ordering

### Template-Driven Consistency
- **Problem**: Inconsistent ticket creation and scope creep
- **Solution**: Structured templates with `scripts/ticket_template_generator.py`
- **Implementation**: Proven patterns for TDD, Testing, API, and Playwright tickets

**Reference Documentation**: See `docs/RETROSPECTIVE_PR32_LEARNINGS.md` for complete analysis

## Git Workflow & MR Process

```bash
# MANDATORY GIT WORKFLOW - Never commit directly to dev
git checkout dev && git pull origin dev
git checkout -b feature/[descriptive-name]
# Work, commit, test thoroughly
git push -u origin feature/[descriptive-name]
gh pr create --title "..." --body "..." --base dev

# MR REVIEW INTEGRATION
gh pr edit <PR_NUMBER> --add-reviewer Copilot
# Address all feedback systematically
gh pr comment <comment-id> --body "✅ Resolved: [description]"
```

**MR Requirements:**
- **Target Branch**: Always `dev` (never main/master)
- **Feature Branch**: Always work in feature branches, never directly on dev
- **Copilot Review**: Add reviewer via CLI after MR creation
- **Inline Comments**: Mark each resolved comment with specific description
- **Security Scans**: All GitHub Advanced Security checks must pass
- **History Documentation**: Include session file in `/history/` directory
- **Re-test**: Verify all functionality after addressing review feedback

## Jira Integration

**CRITICAL LEARNING**: Always verify ticket mapping before automation

```bash
# 1. DISCOVER correct ticket mapping via test files
grep -r "PR003946-" tests/integration/test_api_validation_epic.py

# 2. VERIFY current ticket status before transitions
curl -H "Authorization: Basic $CREDS" \
  "$JIRA_BASE_URL/rest/api/3/issue/$TICKET?fields=status"

# 3. USE CORRECTIVE COMMENTS for automation mistakes
add_simple_comment "PR003946-XX" "CORRECTION: Previous comment was incorrect..."
```

**Jira Best Practices:**
- **Map Work to Tickets**: Match actual implementation scope to ticket descriptions in test files
- **Status Checking**: Verify current status before attempting transitions
- **Corrective Action**: Add clarifying comments when automation makes mistakes
- **Authentication**: Basic Auth with `email:token` base64 encoded (not Bearer)
- **Ticket Verification**: Never assume ticket numbers - verify against project documentation

### Jira Status Management
The `/nextfive` command now automatically manages Jira ticket statuses:

**Automatic Status Transitions:**
- **Start of work**: Tickets move to "In Progress" (Phase 3)
- **MR ready**: Tickets move to "Done" (Phase 11)

**Manual Status Updates:**
```bash
# Move tickets to In Progress when starting work
./scripts/manage_jira_tickets.sh batch-start PR003946-91 PR003946-88

# Move tickets to Done when MR is ready
./scripts/manage_jira_tickets.sh batch-done PR003946-91 PR003946-88

# Check current status
./scripts/manage_jira_tickets.sh status PR003946-91
```

## Quality Gates
- **API Endpoints Working**: All new endpoints respond correctly via cURL testing
- **CRUD Operations Functional**: Basic create, read, update, delete operations work
- No breaking changes to existing features
- GitHub Advanced Security issues resolved
- Copilot review feedback addressed with inline comments marked as resolved
- Professional MR description with API verification examples
- Clean, maintainable code following project conventions
- Jira tickets updated with implementation status
- Final sequential reasoning validation of all steps completed

## Key Learnings

**CRITICAL DISCOVERY**: Most tickets were already working - success came from comprehensive enhancement strategy rather than fixing individual failures.

### Git Workflow Lessons
❌ **Never commit directly to dev** - Always use feature branches
✅ **Mandatory Pattern**: `dev` → `feature/branch` → MR to `dev`
✅ **User Feedback**: "We're always starting from dev on this project and always need to create MRs against dev"

### Jira Automation Lessons
❌ **Problem**: Scripts updated wrong tickets (87, 67) with incorrect information
✅ **Solution**: Always verify ticket mapping via test files before automation
✅ **Corrective Action**: Use clarifying comments to fix automation mistakes

### Implementation Strategy Lessons
✅ **Comprehensive Enhancements Work**: OpenAPI spec + model generation + infrastructure
✅ **Sequential Reasoning Essential**: Predict outcomes, plan systematically
✅ **Security Integration**: GitHub Advanced Security scanner resolution is critical
✅ **Review Process**: Copilot review + inline comment resolution pattern

### Template Success Factors
- Discovery-first approach (run tests before assuming failures)
- Systematic enhancement when obvious failures don't exist
- Proper git workflow with feature branches
- Security scanner integration and resolution
- Verification-based Jira automation with corrective capabilities