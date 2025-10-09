# AI Assistant Handoff Prompt

Use this prompt to brief another AI assistant about the CMZ Chatbots project.

---

## Context Brief

You are assisting with the **Cougar Mountain Zoo Digital Ambassador Chatbot Platform**, a production educational application that provides interactive AI-powered chatbot personalities for zoo animals. This is a serious educational project serving real zoo visitors, not a prototype.

## Technical Stack

**Backend:**
- Python 3.11 Flask API server with OpenAPI 3.0 specification-driven development
- OpenAPI Generator for automatic controller/model generation
- AWS DynamoDB for data persistence (10+ production tables)
- Docker containerized with live reloading
- JWT-based authentication with role-based access control

**Frontend:**
- React TypeScript application (localhost:3001)
- Material-UI component library
- Service layer integration with backend API

**Infrastructure:**
- AWS Account 195275676211, us-west-2 region
- DynamoDB pay-per-request billing (~$2.15/month)
- Docker-based local development environment
- 24 MCP servers for AWS integration and development tools

## Critical Architecture Patterns

### OpenAPI-First Development
**SOURCE OF TRUTH**: `backend/api/openapi_spec.yaml` drives ALL API definitions.

**Code Generation Workflow:**
```bash
# ALWAYS use validated generation - NEVER use generate-api alone
make generate-api  # Now includes automatic validation as of 2025-09-17

# Complete deployment cycle
make post-generate && make build-api && make run-api
```

**CRITICAL RULES:**
1. **NEVER modify generated code**: Controllers, models, test stubs regenerate on every `make generate-api`
2. **ALL business logic in impl/**: Only implement in `backend/api/src/main/python/openapi_server/impl/`
3. **Validation is mandatory**: Post-generation fixes prevent 30+ failures per regeneration
4. **Auth ALWAYS breaks**: Generated auth_controller.py must be manually fixed after every regeneration

### Authentication Architecture (FRAGILE - Handle with Care)
**Known Issue**: Authentication breaks after EVERY OpenAPI regeneration.

**Required Components:**
- `impl/utils/jwt_utils.py` - Centralized JWT token generation (3-part tokens required)
- `impl/auth.py` - Multi-mode auth (mock/dynamodb/cognito)
- Auth controller must route to `handle_()` function in `impl/auth.py`

**Test Users:**
- `parent1@test.cmz.org` / `testpass123` (parent role)
- `student1@test.cmz.org` / `testpass123` (student role)
- `test@cmz.org` / `testpass123` (default user)

**If Auth Breaks**: See `AUTH-ADVICE.md` for complete troubleshooting guide.

### DynamoDB Integration Pattern
All DynamoDB operations use centralized utilities in `impl/utils/dynamo.py`:

```python
from .utils.dynamo import (
    table, to_ddb, from_ddb, now_iso,
    model_to_json_keyed_dict, ensure_pk,
    error_response, not_found
)
```

**Key Patterns:**
- Convert models to dicts with `model_to_json_keyed_dict()`
- Use `ensure_pk()` for primary key validation
- Add audit timestamps with `now_iso()`
- Handle errors with `error_response()`

## Current Branch State

**Branch**: `feature/recurring-issues-automation-2025-10`
**Status**: Active development with uncommitted changes

**Modified Areas:**
- OpenAPI specification updates
- Controller and model regeneration
- Implementation layer changes (animals, family, auth)
- Frontend integration updates
- Test infrastructure improvements

## Development Commands Reference

### Core Workflow
```bash
# Start development environment
make start-dev         # Starts all services with health checks

# API regeneration (after openapi_spec.yaml changes)
make generate-api      # Validated generation (safe)
make build-api         # Build Docker container
make run-api           # Run API server (port 8080)

# Quality checks
make quality-check     # All quality gates
make test             # Unit and integration tests

# Stop environment
make stop-dev          # Clean shutdown
```

### Testing
```bash
# Unit tests with coverage
tox

# Playwright E2E tests (TWO-STEP REQUIRED)
cd backend/api/src/main/python/tests/playwright

# Step 1: Login validation (REQUIRED FIRST)
./run-step1-validation.sh
# Success criteria: ≥5/6 browsers passing

# Step 2: Full test suite (only after Step 1 passes)
FRONTEND_URL=http://localhost:3001 npx playwright test --config config/playwright.config.js --reporter=line
```

## Critical Documentation Files

**Read BEFORE making changes:**
- `CLAUDE.md` - Complete architecture and rules
- `AUTH-ADVICE.md` - Authentication troubleshooting
- `RECURRING-ISSUES-FIX.md` - Known recurring problems and permanent fixes
- `GITHUB-ADVICE.md` - Token configuration for gh CLI

**Implementation Guides:**
- `.claude/commands/validate-data-persistence.md` - E2E data flow validation
- `.claude/commands/validate-backend-health.md` - Service health testing
- `.claude/commands/comprehensive-validation.md` - Complete validation suite

**Common Issues:**
- `ID-PARAMETER-MISMATCH-ADVICE.md` - Connexion ID renaming issue
- `BODY-PARAMETER-HANDLING-ADVICE.md` - Request body parameter issues
- `ANIMAL-CONFIG-FLAKINESS-ADVICE.md` - Controller-handler connection issues

## Quality Standards

**Before ANY commit:**
1. ✅ Run `make quality-check` - all gates must pass
2. ✅ Unit tests: `tox` - 100% pass required
3. ✅ Playwright Step 1: ≥5/6 browsers passing
4. ✅ Auth validation: All test users can login
5. ✅ DynamoDB operations: Data persists correctly
6. ✅ Session history: Document in `/history/{name}_{date}_{time}.md`

**Code Organization:**
- Python: snake_case for functions/variables
- Follow existing project patterns exactly
- Never modify generated code directly
- All business logic in `impl/` modules only

## Environment Configuration

**AWS:**
- Profile: `cmz` (configured in .zshrc)
- Region: `us-west-2`
- Account: `195275676211`

**Key Environment Variables:**
- `AWS_PROFILE=cmz`
- `FAMILY_DYNAMO_TABLE_NAME=quest-dev-family`
- `PORT=8080` (API server)
- `FRONTEND_URL=http://localhost:3001`

## MCP Server Integration

**Available MCP Servers (24 total):**
- **Sequential Thinking**: Complex reasoning and analysis
- **Context7**: Official library documentation
- **Magic**: UI component generation from 21st.dev
- **Playwright**: Browser automation and E2E testing
- **AWS Services**: DynamoDB, S3, Athena, Cognito, Cost Explorer, etc.
- **Python Development**: FastMCP, PRIMS, Jupyter

**Usage Patterns:**
- Use Sequential for complex debugging and multi-step reasoning
- Use Context7 for framework-specific documentation
- Use Magic for React component generation
- Use Playwright for E2E validation

## Working Principles

**From Keith's Standards:**
1. **Evidence > assumptions** - Test everything, verify all claims
2. **Code > documentation** - Working code is the truth
3. **Efficiency > verbosity** - Token-efficient communication
4. **Professional objectivity** - Technical accuracy over validation
5. **Fail fast mindset** - Quick validation over complex patterns
6. **Easy handoff priority** - Clear, maintainable code over clever solutions

**Implementation Completeness:**
- Start it = Finish it - no partial features
- No TODO comments for core functionality
- No mock objects or stub implementations
- Every function must work as specified

**Scope Discipline:**
- Build ONLY what's asked - no feature creep
- MVP first, iterate based on feedback
- No enterprise bloat unless explicitly requested
- YAGNI enforcement - no speculative features

## Common Failure Modes (What to Watch For)

**Post-Generation Issues:**
1. **Auth endpoint regression** - Always validate auth after `make generate-api`
2. **Controller-handler disconnection** - Check `impl/handlers.py` connections
3. **Missing body parameters** - Verify controller function signatures
4. **CORS errors** - Ensure Flask-CORS configuration persists
5. **AWS dependency loss** - Verify boto3/pynamodb in requirements.txt

**Runtime Issues:**
1. **ID parameter mismatch** - Connexion renames `id` to `id_`
2. **JWT token format** - Must be 3-part token (header.payload.signature)
3. **DynamoDB timeouts** - Check AWS credentials and table access
4. **Port conflicts** - Ensure backend (8080) and frontend (3001) available

**Testing Issues:**
1. **Step 1 validation skipped** - Always run login tests before full suite
2. **Browser timing issues** - Playwright needs proper wait strategies
3. **DynamoDB consistency** - Eventually consistent reads may need retry logic

## Success Indicators

**Healthy System:**
- API responds at http://localhost:8080
- Frontend loads at http://localhost:3001
- All test users can authenticate successfully
- DynamoDB operations succeed without errors
- `make quality-check` passes all gates
- Playwright Step 1: ≥5/6 browsers passing

**Ready for MR:**
- All quality gates pass
- Session history documented
- All comments resolved with specific changes
- CodeQL issues addressed
- API endpoints tested via cURL
- No uncommitted debugging code

## Next Steps Guidance

When you start working on this project:

1. **Understand current state**: Run `git status` and read recent commit messages
2. **Validate environment**: Run `make status` and `make health-check`
3. **Review active branch**: Check what's in progress on current feature branch
4. **Read relevant advice files**: Based on the work type (auth, validation, testing, etc.)
5. **Run quality checks**: Establish baseline with `make quality-check`
6. **Document your session**: Create file in `/history/` before making changes

## Getting Help

**For specific issues:**
- Authentication problems → `AUTH-ADVICE.md`
- GitHub operations → `GITHUB-ADVICE.md`
- Recurring issues → `RECURRING-ISSUES-FIX.md`
- Testing strategies → `.claude/commands/validate-*.md`
- MR preparation → `.claude/commands/prepare-merge-request.md`

**For architectural questions:**
- Read `CLAUDE.md` completely
- Check `/claudedocs/` for analysis and reports
- Review `/history/` for similar work sessions
- Examine recent commits for patterns

---

**Remember**: This is a production educational application. Every change must maintain system reliability and user experience quality. Test thoroughly, document completely, and follow established patterns exactly.
