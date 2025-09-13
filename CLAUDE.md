# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture Overview

This is a Python Flask-based API server for the Cougar Mountain Zoo digital ambassador chatbot platform. The project uses OpenAPI 3.0 specification-driven development with code generation and comprehensive AWS integration.

**Core Architecture:**
- **OpenAPI-First Development**: `backend/api/openapi_spec.yaml` drives all API definitions and server code generation
- **Generated Flask Server**: OpenAPI Generator creates controllers, models, and test stubs automatically
- **Implementation Layer**: Business logic implemented in `impl/` modules, never in generated code
- **AWS DynamoDB**: Data persistence with 10+ production tables for users, animals, conversations, families
- **Docker-Containerized**: Complete development and deployment workflow with live reloading
- **MCP Integration**: 24 Model Context Protocol servers for AWS services, Python development, and infrastructure

**Key Business Domains:**
- **Animals**: Chatbot personalities, configurations, and animal details
- **Families**: Parent-student group management for zoo educational programs  
- **Users & Auth**: User management with role-based access control
- **Conversations**: Chat session tracking and analytics
- **Knowledge Base**: Educational content and media management

## Development Commands

### Core Workflow
```bash
# Complete regeneration and deployment cycle
make generate-api && make build-api && make run-api

# Quick development iteration (after OpenAPI spec changes)
make generate-api
make build-api
make run-api

# Monitor running container
make logs-api

# Stop and cleanup
make stop-api
make clean-api
```

### Advanced Development
```bash
# Custom port deployment
make run-api PORT=9001

# Debug mode with interactive container
make run-api DEBUG=1

# Different OpenAPI spec
make generate-api OPENAPI_SPEC=path/to/other/spec.yaml

# Custom container/image names
make build-api IMAGE_NAME=myorg/cmz-api
make run-api CONTAINER_NAME=cmz-dev-custom
```

### Testing & Quality

#### Unit & Integration Tests
```bash
# Full test suite with coverage
tox

# Quick unit tests
pytest --cov=openapi_server

# Test specific module
pytest backend/api/src/main/python/openapi_server/test/test_family.py

# Run tests in local virtualenv
make venv-api && make install-api
source .venv/openapi-venv/bin/activate
pytest --cov=openapi_server
```

#### Two-Step Playwright E2E Testing
**IMPORTANT**: Always use two-step approach to catch fundamental issues early

**Step 1: Login Validation** (Required before full suite)
```bash
# Navigate to Playwright directory
cd backend/api/src/main/python/tests/playwright

# Quick validation script
./run-step1-validation.sh

# Manual Step 1 - All 5 test users
FRONTEND_URL=http://localhost:3001 npx playwright test --config config/playwright.config.js --grep "🔐 Login User Validation - STEP 1" --reporter=line --workers=1

# Single user test for debugging
FRONTEND_URL=http://localhost:3001 npx playwright test --config config/playwright.config.js --grep "should successfully validate login for Test Parent One" --reporter=line --workers=1
```

**Step 2: Full Test Suite** (Only after Step 1 passes ≥5/6 browsers)
```bash
# Complete test suite
FRONTEND_URL=http://localhost:3001 npx playwright test --config config/playwright.config.js --reporter=line
```

**Authentication Test Users:**
- `parent1@test.cmz.org` / `testpass123` (parent role)
- `student1@test.cmz.org` / `testpass123` (student role)  
- `student2@test.cmz.org` / `testpass123` (student role)
- `test@cmz.org` / `testpass123` (default user)
- `user_parent_001@cmz.org` / `testpass123` (parent role)

**Success Criteria for Step 1:**
- ≥5/6 browsers passing authentication tests
- Successful JWT token generation and dashboard redirects
- No CORS errors across browsers
- Mobile Safari UI interaction issues acceptable (known frontend styling issue)

### Local Python Environment (Optional)
```bash
# Setup local development (alternative to Docker)
make venv-api           # Create UV virtualenv (.venv/openapi-venv)
make install-api        # Install dependencies
source .venv/openapi-venv/bin/activate

# Rebuild environment from scratch
make rebuild-venv-api
```

## Critical Implementation Rules

### Code Generation Boundaries
- **NEVER modify generated files**: Controllers, models, and test stubs are regenerated on every `make generate-api`
- **All business logic in impl/**: Only implement functionality in `backend/api/src/main/python/openapi_server/impl/`
- **OpenAPI spec is source of truth**: API changes must start with `openapi_spec.yaml` modifications

### DynamoDB Integration Pattern
All DynamoDB operations use the centralized utilities in `impl/utils/dynamo.py`:

```python
from .utils.dynamo import (
    table, to_ddb, from_ddb, now_iso,
    model_to_json_keyed_dict, ensure_pk,
    error_response, not_found
)

def handle_operation(body):
    # Convert OpenAPI model to dict
    item = model_to_json_keyed_dict(body) if isinstance(body, ModelClass) else dict(body)
    
    # Ensure primary key exists
    ensure_pk(item, "primaryKeyField")
    
    # Add audit timestamps
    item.setdefault("created", {"at": now_iso()})
    item["modified"] = {"at": now_iso()}
    
    # DynamoDB operation with proper error handling
    try:
        result = _table().put_item(Item=to_ddb(item))
        return from_ddb(item), 201
    except ClientError as e:
        return error_response(e)
```

### Environment Configuration
**AWS Integration:**
- `AWS_PROFILE=cmz` (configured in .zshrc)
- `AWS_REGION=us-west-2`
- `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` (configured)

**DynamoDB Tables:**
- `FAMILY_DYNAMO_TABLE_NAME=quest-dev-family`
- `FAMILY_DYNAMO_PK_NAME=familyId`
- Similar patterns for other domain tables

**Local Development:**
- `DYNAMODB_ENDPOINT_URL`: Override for local DynamoDB testing
- `PORT`: API server port (default 8080)

## AWS & MCP Integration

The project includes comprehensive AWS tooling via 24 MCP servers:

**Core AWS Services (11 servers):**
- DynamoDB, S3, Athena, Cognito, Cost Explorer, Resources
- CDK, Terraform, Serverless (SAM), Diagrams

**Python Development (7 servers):**
- FastMCP, PRIMS, Jupyter, Python Interpreter, Django

**API & Development (6 servers):**
- OpenAPI tools, Sequential Thinking, File System access

All AWS MCP servers are configured for the CMZ account (195275676211) in us-west-2 region.

## Project Structure & Generated Code

```
backend/api/
├── openapi_spec.yaml              # SOURCE OF TRUTH - All API definitions
├── src/main/python/               # Generated + implementation code
│   ├── openapi_server/
│   │   ├── controllers/           # GENERATED - Route handlers (DO NOT EDIT)
│   │   ├── models/                # GENERATED - Data models (DO NOT EDIT)  
│   │   ├── impl/                  # IMPLEMENTATION - Business logic only
│   │   │   ├── animals.py         # Animal chatbot logic
│   │   │   ├── family.py          # Family management CRUD
│   │   │   └── utils/
│   │   │       └── dynamo.py      # DynamoDB utilities & patterns
│   │   ├── test/                  # GENERATED - Test stubs (DO NOT EDIT)
│   │   └── openapi/openapi.yaml   # Generated spec copy
│   ├── requirements.txt           # Python dependencies
│   ├── Dockerfile                 # Container definition
│   └── tox.ini                    # Test configuration
└── generated/app/                 # Backup of generated code (timestamped)
```

## OpenAPI Specification Structure

The API includes these major endpoint groups:
- **UI**: Public homepage, admin dashboard
- **Auth**: Authentication and authorization
- **Users**: User management and profiles  
- **Families**: Parent-student group operations
- **Animals**: Chatbot personalities and configurations
- **Conversations**: Chat sessions and history
- **Knowledge**: Educational content management
- **Analytics**: Usage metrics and reporting
- **Media**: Asset management
- **Admin/System**: Administrative operations

## Current Development Context

**Active Branch**: `kcs/POST_animal_details` - Implementing animal details endpoint
**Modified Files**: 
- `openapi_spec.yaml` (API specification updates)
- `impl/animals.py` (business logic implementation in progress)

**AWS Spend**: ~$2.15/month (primarily AWS End User Messaging for chatbot interactions)
**DynamoDB Tables**: 10 active tables with pay-per-request billing

## History Tracking Requirement

**IMPORTANT: All contributors must create session history logs before committing.**

### Process
1. Create file: `/history/{your_name}_{YYYY-MM-DD}_{start_time}h-{end_time}h.md`
2. Document your complete development session including:
   - All user prompts and requests
   - MCP server usage (Sequential, Context7, Magic, etc.)
   - Commands executed (make, git, npm, etc.)
   - Files created, modified, or deleted
   - Technical decisions and problem-solving steps
   - Build/deployment actions
   - Quality checks (lint, test, typecheck)

### Purpose
- Enable seamless project handoff between team members
- Preserve context for Claude Code sessions
- Document decision rationale and problem-solving approaches
- Track MCP integration patterns and tool usage
- Maintain architectural decision records

### Session Window
- Use 4-hour time windows for session tracking
- Start new files for sessions that extend beyond 4 hours
- Include cross-references between related session files

**Example**: See `history/kc.stegbauer_2025-09-07_09h-13h.md` for comprehensive session documentation

## API Validation Implementation Template (/nextfive)

**Use this prompt for systematic implementation of API validation tickets with optional specific ticket targeting:**

### Basic Usage (Discovery Mode)
```
/nextfive
# Discovers and implements next 5 high-priority tickets automatically
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

### Implementation Template
```
Implement the next 5 high-priority Jira tickets from our API validation epic, following the same systematic approach we used for PR003946-90, PR003946-72, PR003946-73, PR003946-69, and PR003946-66.

**TARGETED TICKET MODE**: If specific tickets provided, analyze dependencies and implement in priority order:

### Single Ticket Mode (e.g., PR003946-91)
1. **Target Analysis**: Verify ticket exists and get current status
2. **Dependency Analysis**: Check if target ticket is blocked by other tickets  
3. **Priority Resolution**: Address blocking tickets first, up to 5 total tickets
4. **Systematic Implementation**: Implement in dependency order (blockers first, target last)

### Multiple Ticket Mode (e.g., PR003946-91 PR003946-88 PR003946-75)
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

## Context
- CMZ chatbot backend API using OpenAPI-first development
- Flask/Connexion with DynamoDB persistence
- Docker containerized development environment
- All business logic must go in `impl/` directory (never in generated code)

## Required Process - Discovery-First Approach
1. **DISCOVERY FIRST**: Run integration tests to identify actual state (never assume based on Jira status)
2. **ENHANCED DISCOVERY**: Use `scripts/enhanced_discovery.py` for dependency analysis and priority scoring
3. **TWO-PHASE QUALITY GATES**: Execute `scripts/two_phase_quality_gates.sh` for systematic validation
4. **SEQUENTIAL REASONING**: Use MCP to predict outcomes and plan systematic approach
5. **SCOPE ASSESSMENT**: If fewer than 5 failing tickets, identify comprehensive enhancement opportunities
6. **GIT WORKFLOW**: MANDATORY - Always start from dev, create feature branch, target dev for MR
7. **SYSTEMATIC IMPLEMENTATION**: Focus on OpenAPI spec enhancements + model regeneration + infrastructure
8. **SECURITY & QUALITY**: Address GitHub Advanced Security scanner issues systematically
9. **REPOSITORY HYGIENE**: Apply learnings from PR #32 retrospective to prevent test artifact pollution
10. **FEATURE BRANCH MR**: Create MR from feature branch targeting dev (never commit directly to dev)
11. **COPILOT REVIEW**: Add reviewer and address feedback with inline comment resolution
12. **CORRECTIVE JIRA**: Verify ticket mapping before updates, use corrective comments for mistakes

## Technical Requirements
- **Focus on Endpoint Implementation**: Prioritize new API endpoints over strict business validation
- Follow existing patterns in `openapi_server/impl/`
- Maintain OpenAPI specification compliance
- Use consistent Error schema with code/message/details structure
- Include proper audit timestamps and server-generated IDs
- Basic CRUD operations with DynamoDB integration
- Simple validation (required fields, basic formats) rather than complex business rules

## Git Workflow & MR Process - CRITICAL PATTERN
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

## Jira Integration - VERIFICATION-FIRST APPROACH
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

## Complete Workflow
1. **DISCOVERY PHASE**: Run integration tests to identify actual failing tickets
2. **PLANNING PHASE**: List discovered tickets and use sequential reasoning to plan implementation
3. **SCOPE EXPANSION**: If fewer than 5 tickets, identify new endpoint opportunities from OpenAPI spec
4. **IMPLEMENTATION PHASE**: Implement systematically with comprehensive testing
5. **QUALITY PHASE**: Address security issues and run quality checks
6. **MR PHASE**: Create MR targeting `dev` branch, then add Copilot reviewer with `gh pr edit <PR_NUMBER> --add-reviewer Copilot`
7. **DOCUMENTATION PHASE**: Add history documentation to MR
8. **JIRA PHASE**: Update Jira tickets using automated script: `./scripts/update_jira_simple.sh`
9. **REVIEW PHASE**: Wait for and address Copilot review feedback (one round)
   - Address all inline code comments and suggestions
   - **Mark resolved comments**: Use `gh pr comment <comment-id> --body "✅ Resolved: [brief description]"` to mark inline comments as resolved
   - Commit fixes with descriptive messages explaining what was addressed
10. **VALIDATION PHASE**: Re-test and verify all functionality after changes
11. **COMPLETION PHASE**: Use sequential reasoning to validate all steps completed correctly and ensure merge readiness

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

**START HERE - Discovery-Driven Approach:**

### Discovery Mode (Standard /nextfive)
```bash
# Step 1: ALWAYS run integration tests first to find actual failing tickets
python -m pytest tests/integration/test_api_validation_epic.py -v

# Step 2: Enhanced discovery with dependency analysis and priority scoring
python scripts/enhanced_discovery.py --epic PR003946-61 --include-dependencies

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

**Enhanced Implementation Strategy - Comprehensive Approach:**
When fewer than 5 failing tickets exist, implement systematic enhancements:

1. **OpenAPI Specification Enhancements** (validation patterns, schemas, constraints)
2. **Model Regeneration + Validation Logic** (25+ model files with consistent patterns)
3. **Centralized Infrastructure** (error handling, utilities, common patterns)
4. **Security Scanner Resolution** (CodeQL, unused imports, grammar fixes)
5. **Cross-Domain Validation** (referential integrity, business rules)

**MCP Tool Selection for /nextfive:**
- **Sequential Reasoning**: ALWAYS use for planning and prediction (essential)
- **Context7**: Framework-specific patterns and official documentation
- **Morphllm**: Bulk validation pattern application across multiple files
- **Magic**: Not typically needed for backend API validation work
- **Playwright**: Not needed for API-only validation improvements

**Enhanced /nextfive Integration:**
- **Enhanced Discovery**: Use `scripts/enhanced_discovery.py` for systematic ticket discovery with dependency analysis and priority scoring
- **Two-Phase Quality Gates**: Integrate `scripts/two_phase_quality_gates.sh` for systematic validation (Phase 1: fundamentals, Phase 2: comprehensive)
- **Template-Driven Creation**: Use `scripts/ticket_template_generator.py` for consistent, high-quality ticket generation
- **Repository Hygiene**: Apply learnings from `docs/RETROSPECTIVE_PR32_LEARNINGS.md` to prevent test artifact pollution
- **Quality-First Approach**: Never proceed to Phase 2 comprehensive testing until Phase 1 fundamentals pass

## Dependency Resolution Examples

### Single Ticket Examples

### Example 1: Simple Single Ticket
```bash
/nextfive PR003946-91
# Target found, no dependencies → implement PR003946-91 + discover 4 more tickets
# Result: 5 tickets implemented (1 targeted + 4 discovered)
```

### Example 2: Single Ticket with Dependencies
```bash  
/nextfive PR003946-91
# Analysis finds: PR003946-91 depends on PR003946-88, PR003946-89
# Implementation order: PR003946-88 → PR003946-89 → PR003946-91 + discover 2 more
# Result: 5 tickets implemented (3 dependency chain + 2 discovered)
```

### Multiple Ticket Examples

### Example 3: Simple Multiple Tickets
```bash
/nextfive PR003946-91 PR003946-75 PR003946-72
# 3 targets found, no dependencies → implement all 3 + discover 2 more
# Result: 5 tickets implemented (3 specified + 2 discovered)
```

### Example 4: Multiple Tickets with Shared Dependencies
```bash
/nextfive PR003946-91 PR003946-88 PR003946-75
# Analysis finds: 
#   PR003946-91 depends on PR003946-89
#   PR003946-88 no dependencies  
#   PR003946-75 depends on PR003946-89 (shared dependency)
# Implementation order: PR003946-89 → PR003946-91 → PR003946-88 → PR003946-75 + 1 more
# Result: 5 tickets implemented (1 dependency + 3 specified + 1 discovered)
```

### Example 5: Multiple Tickets with Complex Dependencies
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

### Example 6: Comma-Separated Format
```bash
/nextfive PR003946-91,PR003946-88,PR003946-75
# Same as space-separated, supports both formats
# Parsed as: ["PR003946-91", "PR003946-88", "PR003946-75"]
```

### Error Handling Examples

### Example 7: Mixed Valid/Invalid Tickets
```bash
/nextfive PR003946-91 PR003946-999 PR003946-75
# Analysis: PR003946-91 ✅, PR003946-999 ❌, PR003946-75 ✅
# Result: Process valid tickets (PR003946-91, PR003946-75) + their dependencies
```

### Example 8: No Valid Tickets Found
```bash
/nextfive PR003946-999 PR003946-998
# All target tickets not found → fallback to discovery mode
# Result: Standard /nextfive behavior (discover and implement 5 tickets)
```

**Discovery Commands Reference:**
```bash
# Find failing tickets
python -m pytest tests/integration/test_api_validation_epic.py -v

# Examine OpenAPI spec for new endpoints
grep -A 5 -B 5 "paths:" backend/api/openapi_spec.yaml

# Check implemented vs missing endpoints
ls backend/api/src/main/python/openapi_server/impl/
```
```

## Key Learnings from /nextfive Implementation

**CRITICAL DISCOVERY**: Most tickets were already working - success came from comprehensive enhancement strategy rather than fixing individual failures.

### **Git Workflow Lessons:**
❌ **Never commit directly to dev** - Always use feature branches
✅ **Mandatory Pattern**: `dev` → `feature/branch` → MR to `dev`
✅ **User Feedback**: "We're always starting from dev on this project and always need to create MRs against dev"

### **Jira Automation Lessons:**
❌ **Problem**: Scripts updated wrong tickets (87, 67) with incorrect information
✅ **Solution**: Always verify ticket mapping via test files before automation
✅ **Corrective Action**: Use clarifying comments to fix automation mistakes

### **Implementation Strategy Lessons:**
✅ **Comprehensive Enhancements Work**: OpenAPI spec + model generation + infrastructure
✅ **Sequential Reasoning Essential**: Predict outcomes, plan systematically
✅ **Security Integration**: GitHub Advanced Security scanner resolution is critical
✅ **Review Process**: Copilot review + inline comment resolution pattern

### **Template Success Factors:**
- Discovery-first approach (run tests before assuming failures)
- Systematic enhancement when obvious failures don't exist
- Proper git workflow with feature branches
- Security scanner integration and resolution
- Verification-based Jira automation with corrective capabilities

## Jira Update Script Template

The project includes a working Jira automation script at `/scripts/update_jira_simple.sh`:

**Key Features:**
- **Basic Authentication**: Uses `email:token` encoded with base64 (not Bearer token)
- **Status Transitions**: Automatically moves tickets from "To Do" → "In Progress"
- **Simple Comments**: Avoids complex JSON that causes parsing errors
- **Error Handling**: Provides clear success/failure feedback

**Usage Pattern:**
```bash
# After implementing tickets, update them with:
./scripts/update_jira_simple.sh

# Script will:
# 1. Test API connectivity
# 2. Transition ticket status
# 3. Add implementation comments
# 4. Provide verification links
```

**Authentication Setup:**
- Uses existing `JIRA_API_TOKEN` environment variable
- Requires `kc.stegbauer@nortal.com` email for Basic Auth
- Script handles base64 encoding automatically