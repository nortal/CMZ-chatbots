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

## ⚠️ OpenAPI Generation - NOW SAFE BY DEFAULT

**As of 2025-09-17, `make generate-api` automatically includes validation:**
```bash
# ✅ SAFE TO USE - Validation is now automatic:
make generate-api

# This automatically prevents:
# - Lost controller implementations (30+ failures per regeneration)
# - Missing body parameters in function signatures
# - Frontend-backend endpoint mismatches
# - Hours of debugging "do some magic!" placeholders
# - AUTH ENDPOINT REGRESSIONS (previously broke every time!)

# Note: make post-generate still works but is now redundant
# If you need raw generation without fixes (NOT RECOMMENDED):
make generate-api-raw  # WARNING: Will break auth endpoints!
```

**Why validation is CRITICAL:**
- OpenAPI Generator **destroys implementations** without warning
- Body parameters are **systematically omitted** from controllers
- Frontend-backend contracts **drift silently** until runtime failures
- Manual fixing is **error-prone** and takes 1-2 hours per incident
- **AUTH ALWAYS BREAKS**: Generated auth_controller.py routes to generic handler that doesn't exist

**If you see these errors, validation was skipped:**
- `TypeError: auth_login_post() takes 0 positional arguments but 1 was given`
- `"do some magic!"` in any controller
- `501 Not Implemented` responses
- Frontend getting 404s for valid endpoints
- Auth endpoint returning 404 or "not implemented"

### 🔐 Auth Endpoint Architecture (Why It Keeps Breaking)
**The Problem**: Every `make generate-api` overwrites auth_controller.py with broken routing
**Location of Working Code**:
- `impl/handlers.py` - Has correct routing: `'auth_post': handle_login_post`
- `impl/auth.py` - Has working authentication with mock users
- `impl/utils/jwt_utils.py` - JWT token generation/validation
- `impl/utils/auth_decorator.py` - Authentication decorator for endpoints

**The Template Issue**: Even with custom templates in `backend/api/templates/python-flask/`, the generated controller still uses generic routing that fails to find auth handlers.

**Solution**: ALWAYS use `make post-generate` which runs validation scripts that fix the routing

### 🔧 ID Parameter Mismatch (Common Connexion Issue)
**The Problem**: Connexion automatically renames path parameters named `id` to `id_` to avoid shadowing Python's built-in `id()` function. This causes "unexpected keyword argument 'id_'" errors.

**Symptoms**:
- `TypeError: animal_id_put() got an unexpected keyword argument 'id_'. Did you mean 'id'?`
- Endpoints like `/animal/{id}`, `/family/{id}` fail with 500 errors
- Works in tests but fails at runtime

**Root Cause**:
1. OpenAPI spec defines path parameter as `{id}`
2. Generated controller uses `id` as parameter name
3. Connexion renames it to `id_` at runtime to avoid Python builtin conflict
4. Handler expects `id` but receives `id_` → TypeError

**Permanent Solution**:
All handler functions now accept BOTH `id` and `id_` parameters:
```python
def handle_animal_id_get(id: str = None, id_: str = None, **kwargs):
    # Handle both parameter names
    animal_id = id if id is not None else id_
    if animal_id is None:
        return error_response("missing_parameter"), 400
    # ... rest of handler
```

**Automated Fix**: Run `scripts/fix_id_parameter_mismatch.py` after code generation or include in `make post-generate`
**Full Documentation**: See `ID-PARAMETER-MISMATCH-ADVICE.md` for complete solution patterns

### 🎯 Body Parameter Handling Issues
**The Problem**: OpenAPI controllers and handlers often have parameter order/naming mismatches causing body parameters to be lost or misplaced.

**Common Errors**:
- `dictionary update sequence element #0 has length 1; 2 is required`
- `Missing request body`
- Body in wrong parameter position

**Solution**: Use flexible `*args, **kwargs` parameter handling in handlers. See `BODY-PARAMETER-HANDLING-ADVICE.md` for complete patterns.

## Development Commands

### Core Workflow
```bash
# Complete regeneration and deployment cycle (VALIDATED)
make post-generate && make build-api && make run-api

# Quick development iteration (after OpenAPI spec changes)
make post-generate  # NEVER use generate-api alone!
make build-api
make run-api

# Validate without regenerating
make validate-api

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
- **"do some magic!" Placeholder Issue**: If you encounter this placeholder in generated controllers, see `docs/OPENAPI_TEMPLATE_SOLUTION.md` for the complete template-based solution that eliminates this issue permanently
- **Controller-Handler Connection Issues**: If you encounter "cannot import name 'handlers'" or 501 Not Implemented errors after regeneration, see `ANIMAL-CONFIG-FLAKINESS-ADVICE.md` for root cause and permanent fix

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

The project includes comprehensive AWS tooling via 24 MCP servers plus SnapClick MCP for SMS messaging:

**SMS Messaging**: Use SnapClick MCP with CLICKSEND_USERNAME and CLICKSEND_API_KEY environment variables for sending SMS messages to parents/students.
  - **Phone Format**: Use international format with country code (e.g., +1234567890 for US numbers)
  - **Common Issues**: "COUNTRY_NOT_ENABLED" error usually requires account verification in ClickSend dashboard
  - **Troubleshooting**: Check SMS > Countries in ClickSend dashboard to verify destination country is enabled
  - **Documentation**: Additional help available at https://developers.clicksend.com/docs or its links

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

## API Validation Implementation (/nextfive)

For systematic implementation of API validation tickets, use the `/nextfive` command.
See `.claude/commands/nextfive.md` for complete documentation including:
- Basic and targeted usage modes
- Dependency resolution and TDD processes
- Git workflow and Jira integration
- Quality gates and retrospective learnings

## GitHub Operations and Merge Request Preparation

**⚠️ CRITICAL: Read `GITHUB-ADVICE.md` before ANY GitHub CLI operations**
- Contains essential token configuration instructions
- Explains how to properly export tokens from `.env.local`
- Documents common errors and their solutions
- Provides fallback strategies when gh CLI fails

**Before creating any merge request, ALWAYS check:**
1. **GitHub Setup**: `GITHUB-ADVICE.md` - Token configuration and gh CLI usage
2. **Command Guide**: `.claude/commands/prepare-merge-request.md` - Complete step-by-step process
3. **Best Practices**: `MR-ADVICE.md` - Proven patterns and common pitfalls

**MR Ready Criteria (All Must Be True):**
- ✅ GitHub token properly exported (`export GITHUB_TOKEN=...`)
- ✅ All comments resolved with specific documentation
- ✅ All inline comments resolved with specific documentation
- ✅ All quality gates passed (tests, linting, security)
- ✅ All CodeQL issues addressed
- ✅ API endpoints tested and working via cURL
- ✅ Session history documented in `/history/` directory

Use `/prepare-mr` command to systematically verify readiness.


## Jira Management Scripts

The project includes enhanced Jira management scripts. See `.claude/commands/nextfive.md` for full Jira integration documentation.

### Quick Reference: `/scripts/manage_jira_tickets.sh`
```bash
# Batch operations (commonly used with /nextfive)
./scripts/manage_jira_tickets.sh batch-start PR003946-91 PR003946-88
./scripts/manage_jira_tickets.sh batch-done PR003946-91 PR003946-88

# Check ticket status
./scripts/manage_jira_tickets.sh status PR003946-91
```

## Version Tracking System
For comprehensive API version validation and frontend compatibility checking, see:
- `.claude/commands/create_tracking_version.md` - Implementation command with sequential reasoning
- `CREATE-TRACKING-VERSION-ADVICE.md` - Best practices and troubleshooting guide.  Use this system in testing to validate that tests are being done on the correct version of the code.

## Data Persistence Validation
For comprehensive end-to-end validation of data flow from UI interactions to DynamoDB storage, see:
- `.claude/commands/validate-data-persistence.md` - Complete data persistence validation with systematic 4-phase approach
- `VALIDATE-DATA-PERSISTENCE-ADVICE.md` - Implementation guidance, troubleshooting, and best practices for data integrity testing
- `.claude/commands/validate-animal-config-persistence.md` - Focused validation for Animal Config endpoint data persistence
- `VALIDATE-ANIMAL-CONFIG-PERSISTENCE-ADVICE.md` - Best practices for Animal Config persistence validation
- `.claude/commands/validate-animal-config-fields.md` - Systematic field-level testing of Animal Name, Scientific Name, and Temperature controls with visible DynamoDB validation
- `VALIDATE-ANIMAL-CONFIG-FIELDS-ADVICE.md` - Comprehensive testing best practices for individual field validation
- `.claude/commands/validate-full-animal-config.md` - Comprehensive E2E testing of all 30 Animal Config dialog components with TDD approach
- `VALIDATE-ANIMAL-CONFIG-COMPONENTS-ADVICE.md` - Component-specific testing advice and valid values discovered during validation

## Backend Health Validation
For systematic validation of backend service health and user-friendly error messaging, see:
- `.claude/commands/validate-backend-health.md` - Comprehensive backend health detection with error message differentiation
- `VALIDATE-BACKEND-HEALTH-ADVICE.md` - Testing methodology, service management, and troubleshooting guide for backend health validation

## Family Dialog Validation
For comprehensive E2E validation of the Add Family dialog with field testing and database verification:
- `.claude/commands/validate-family-dialog.md` - Playwright validation with visible browser for all family dialog fields
- `VALIDATE-FAMILY-DIALOG-ADVICE.md` - Best practices, troubleshooting, and advanced testing scenarios for family dialog validation

## Chat and Chat History Validation
For comprehensive E2E validation of chat functionality with DynamoDB persistence verification:
- `.claude/commands/validate-chat-dynamodb.md` - Complete chat and chat history validation with visible Playwright browser
- `VALIDATE-CHAT-DYNAMODB-ADVICE.md` - Best practices, timing considerations, and troubleshooting for chat validation

## Comprehensive Validation Suite
For orchestrating all validation commands and generating consolidated reports:
- `.claude/commands/comprehensive-validation.md` - Run all validate*.md commands with parallel execution and reporting
- `COMPREHENSIVE-VALIDATION-ADVICE.md` - Optimization strategies, CI/CD integration, and performance tuning

### Backend Health Testing Overview
The backend health validation system ensures users receive appropriate error messages based on actual system status:

**Key Scenarios Validated**:
- **Healthy Backend + Valid Credentials**: Successful login with dashboard redirect
- **Healthy Backend + Invalid Credentials**: "Invalid email or password" message
- **Backend Down + Any Credentials**: "Service temporarily unavailable" message
- **Service Recovery**: Automatic detection when backend comes back online

**Critical Success Criteria**:
- Users never see authentication errors when the backend is down
- Clear distinction between login failures and service unavailability
- User-friendly messaging appropriate for zoo visitors
- Fast health check responses (< 2 seconds)
- Cross-browser compatibility for error message display

**Testing Requirements**:
- Must use Playwright MCP with visible browser for user confidence
- Service start/stop simulation for realistic failure scenarios
- Performance benchmarking for health check endpoints
- Error message consistency validation across browsers

## Meta-Prompt System
For generating new systematic command prompts with sequential reasoning and comprehensive documentation:
- `.claude/commands/create-solution.md` - Meta-prompt generator using `/create-solution <description>`
- `CREATE-SOLUTION-ADVICE.md` - Best practices and lessons learned for prompt creation

## Authentication Architecture Fix
For resolving persistent JWT token issues and auth endpoint regressions:
- `.claude/commands/fix-auth-architecture.md` - Comprehensive auth architecture solution using `/fix-auth-architecture`
- `FIX-AUTH-ARCHITECTURE-ADVICE.md` - Implementation guidance, troubleshooting, and best practices
- **Key Components**:
  - `impl/utils/jwt_utils.py` - Centralized JWT token generation ensuring frontend compatibility
  - `impl/auth.py` - Multi-mode authentication (mock/dynamodb/cognito) with environment switching
  - `tests/test_auth_contract.py` - Contract tests preventing auth regressions
- **Critical Success Factors**:
  - Always generate 3-part JWT tokens (header.payload.signature)
  - Use AUTH_MODE environment variable for auth backend selection
  - Run contract tests after any auth changes
  - Use `make post-generate` after OpenAPI regeneration (never standalone generate)

## MR Review System
For automated review and validation of GitHub Pull Requests:
- `.claude/commands/review-mr.md` - Comprehensive MR review command using `/review-mr <pr-number>`
- `REVIEW-MR-ADVICE.md` - Best practices for automated PR review and comment resolution
- **Key Features**: Analyzes Copilot/security comments, validates gating functions, generates actionable reports
- **Integration**: Use after Step 9 (Review Phase) in Complete Workflow to automate review checking

## MR Resolution System
For automated resolution of issues identified in PR reviews:
- `.claude/commands/resolve-mr.md` - Automated issue resolution using `/resolve-mr [pr-number]`
- `RESOLVE-MR-ADVICE.md` - Best practices for automated fix application and comment resolution
- **Key Features**: Parses review-mr output, applies categorized fixes, validates corrections, marks comments resolved
- **Integration**: Use after `/review-mr` to automatically fix identified issues before merge

## Infrastructure Hardening (Updated 2025-01-14)
For systematic resolution of recurring development workflow issues:
- `.claude/commands/systematic-cmz-infrastructure-hardening.md` - Permanent infrastructure improvements with TDD validation
- `SYSTEMATIC-CMZ-INFRASTRUCTURE-HARDENING-ADVICE.md` - Implementation guidance and troubleshooting

### Automated Environment Management
- `make start-dev` - Start complete development environment with health checks
- `make stop-dev` - Stop all development services
- `make status` - Show complete system status
- `make health-check` - Verify all services are healthy

### Quality Automation
- `make quality-check` - Run all quality gates before MR creation
- `make fix-common` - Automatically fix common development issues
- `make pre-mr` - Complete pre-MR workflow (quality + branch creation)

### Infrastructure Commands
- `scripts/start_development_environment.sh` - Comprehensive startup with validation
- `scripts/stop_development_environment.sh` - Clean shutdown of all services
- `scripts/quality_gates.sh` - Complete quality validation
- `scripts/fix_common_issues.sh` - Automated issue resolution
- `scripts/create_mr.sh` - Proper MR creation targeting dev branch

### Key Improvements
- **OpenAPI Template Fix**: Uses custom templates to eliminate controller-implementation mismatches permanently
- **Automated Environment**: No more manual service startup or port conflicts
- **Quality Gates**: Proactive issue detection and automated fixes
- **Git Workflow**: Enforced branch targeting and naming conventions with pre-commit hooks