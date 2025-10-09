# CMZ Chatbots Project State Description

**Quick Brief for AI Assistants**

---

## Project Identity

**Name**: Cougar Mountain Zoo Digital Ambassador Chatbot Platform
**Type**: Production educational web application
**Owner**: Keith Charles "KC" Stegbauer, Senior Cloud Architect at Nortal
**Purpose**: Interactive AI-powered chatbot personalities representing zoo animals for educational engagement

## Technical Overview

**Architecture**: OpenAPI-first Python Flask API + React TypeScript frontend
**Persistence**: AWS DynamoDB (10+ tables, pay-per-request)
**Development**: Docker containerized with local dev environment
**Cloud**: AWS Account 195275676211, us-west-2
**Cost**: ~$2.15/month in production

**Key Technologies:**
- Backend: Python 3.11, Flask, OpenAPI Generator, JWT auth
- Frontend: React, TypeScript, Material-UI
- Infrastructure: Docker, AWS DynamoDB, 24 MCP servers
- Testing: pytest, tox, Playwright E2E

## Current State (2025-10-08)

**Active Branch**: `feature/recurring-issues-automation-2025-10`
**Main Branch**: `main` (stable production baseline)

**Work in Progress:**
- OpenAPI specification updates and regeneration
- Backend controller and model modifications
- Frontend integration improvements
- Test infrastructure enhancements
- Multiple uncommitted changes (see git status)

**Health Status:**
- Development environment: Operational
- Authentication: Recently fixed, currently working
- Database: All tables accessible and functioning
- Test Suite: Unit tests passing, E2E tests need validation

## Critical Constraints

**Code Generation Boundaries:**
- OpenAPI spec (`backend/api/openapi_spec.yaml`) is source of truth
- Controllers/models are auto-generated - NEVER edit directly
- ALL business logic must be in `impl/` modules only
- Use `make generate-api` (includes validation) - NEVER standalone generation

**Known Fragile Areas:**
1. **Authentication** - Breaks after every OpenAPI regeneration
2. **Controller-Handler Connections** - Require manual validation post-generation
3. **CORS Configuration** - Must persist through regeneration
4. **AWS Dependencies** - boto3/pynamodb can disappear from requirements.txt

**Quality Gates (Must Pass Before Commit):**
- `make quality-check` - All automated quality gates
- `tox` - Unit and integration tests (100% pass required)
- Playwright Step 1 - Login validation (≥5/6 browsers)
- DynamoDB operations - Data persistence verification
- Session history - Document all work in `/history/`

## Project Structure

```
CMZ-chatbots/
├── backend/api/
│   ├── openapi_spec.yaml           # SOURCE OF TRUTH
│   └── src/main/python/
│       └── openapi_server/
│           ├── controllers/        # GENERATED - DO NOT EDIT
│           ├── models/             # GENERATED - DO NOT EDIT
│           ├── impl/               # IMPLEMENTATION - EDIT HERE ONLY
│           │   ├── animals.py      # Animal chatbot logic
│           │   ├── family.py       # Family management
│           │   ├── auth.py         # Authentication
│           │   └── utils/          # Shared utilities
│           └── test/               # GENERATED - Test stubs
├── frontend/                       # React TypeScript app
├── scripts/                        # Development and deployment scripts
├── .claude/commands/               # Systematic solution prompts
├── claudedocs/                     # AI-generated documentation
└── history/                        # Session history logs (REQUIRED)
```

## Essential Commands

```bash
# Environment management
make start-dev          # Start complete development environment
make stop-dev           # Stop all services
make status             # Show system status

# Development workflow
make generate-api       # Regenerate from OpenAPI spec (validated)
make build-api          # Build Docker container
make run-api            # Start API server (port 8080)

# Quality and testing
make quality-check      # Run all quality gates
tox                     # Unit and integration tests

# E2E testing (TWO-STEP PROCESS)
cd backend/api/src/main/python/tests/playwright
./run-step1-validation.sh           # Step 1: Login validation FIRST
# Then run full suite only after Step 1 passes ≥5/6 browsers
```

## Authentication Test Users

```
parent1@test.cmz.org / testpass123 (parent role)
student1@test.cmz.org / testpass123 (student role)
student2@test.cmz.org / testpass123 (student role)
test@cmz.org / testpass123 (default user)
user_parent_001@cmz.org / testpass123 (parent role)
```

## Key Documentation (READ BEFORE CHANGES)

**Core Architecture:**
- `CLAUDE.md` - Complete project guide and architecture
- `AUTH-ADVICE.md` - Authentication troubleshooting
- `RECURRING-ISSUES-FIX.md` - Known problems and permanent fixes

**Common Issues:**
- `ID-PARAMETER-MISMATCH-ADVICE.md` - Connexion ID renaming
- `BODY-PARAMETER-HANDLING-ADVICE.md` - Request body parameters
- `ANIMAL-CONFIG-FLAKINESS-ADVICE.md` - Controller connections

**Process Guides:**
- `GITHUB-ADVICE.md` - GitHub CLI token configuration
- `.claude/commands/prepare-merge-request.md` - MR preparation workflow
- `.claude/commands/validate-*.md` - Systematic validation commands

## Development Philosophy

**From Keith's Standards (PRINCIPLES.md, RULES.md):**
- Evidence-based development (test everything, verify all claims)
- Implementation completeness (start it = finish it, no TODO comments)
- Scope discipline (build only what's asked, MVP first)
- Professional honesty (no marketing language, realistic assessments)
- Workspace hygiene (clean up temporary files, remove artifacts)
- Git workflow discipline (feature branches only, never work on main)

**Quality Expectations:**
- Production-ready code only (no placeholders, stubs, or mocks)
- Comprehensive error handling and validation
- User-friendly error messages (zoo visitors are end users)
- Cross-browser compatibility (6 browsers: Chrome, Firefox, Safari, Edge, Mobile Chrome, Mobile Safari)
- Data persistence validation (E2E from UI to DynamoDB)

## Recent Significant Changes

**2025-09-17**: Automated post-generation validation now included in `make generate-api`
**2025-09-19**: ID parameter mismatch solution implemented (Connexion `id` → `id_` issue)
**2025-01-14**: Infrastructure hardening with automated environment management
**Recent**: Auth architecture centralization with `jwt_utils.py` and contract tests

## Common Failure Scenarios

**If you see these errors:**
- `TypeError: auth_login_post() takes 0 positional arguments but 1 was given` → Auth regeneration issue
- `"do some magic!"` in controllers → Post-generation validation not run
- `501 Not Implemented` responses → Controller-handler connection broken
- `Invalid email or password` with correct credentials → JWT token generation issue
- CORS errors from frontend → Flask-CORS configuration lost

**Standard Recovery:**
1. Run `make post-generate` to reapply fixes
2. Check `impl/auth.py` for `handle_()` function existence
3. Verify `requirements.txt` includes boto3 and pynamodb
4. Validate controller-handler connections in `impl/handlers.py`
5. Test with known good credentials from test user list

## Success Criteria

**Development Environment Healthy:**
- API responds at http://localhost:8080
- Frontend loads at http://localhost:3001
- All 5 test users authenticate successfully
- DynamoDB operations persist data correctly
- `make quality-check` passes all gates
- Playwright Step 1 validation: ≥5/6 browsers pass

**Ready for Production:**
- All quality gates passing
- E2E tests passing (both Step 1 and full suite)
- Security scan clean (no critical/high CVEs)
- Session history documented
- Code review comments resolved
- API endpoints tested via cURL
- No debugging code or temporary files committed

## Contribution Requirements

**Before ANY commit:**
1. Create session history: `/history/{name}_{YYYY-MM-DD}_{start-end}h.md`
2. Document all user prompts, commands, decisions, and changes
3. Run `make quality-check` and resolve all failures
4. Validate authentication with all test users
5. Ensure no generated code was modified directly
6. Clean up temporary files and debugging artifacts

**Session History Must Include:**
- User prompts and requests
- MCP server usage (Sequential, Context7, Magic, Playwright, etc.)
- Commands executed (make, git, npm, docker, etc.)
- Files created, modified, or deleted
- Technical decisions and problem-solving approach
- Build/deployment actions
- Quality check results

## Environment Variables

**AWS Configuration:**
```bash
AWS_PROFILE=cmz
AWS_REGION=us-west-2
AWS_ACCESS_KEY_ID=(configured)
AWS_SECRET_ACCESS_KEY=(configured)
```

**Application Configuration:**
```bash
PORT=8080                                    # API server port
FRONTEND_URL=http://localhost:3001          # Frontend URL
FAMILY_DYNAMO_TABLE_NAME=quest-dev-family   # DynamoDB table
FAMILY_DYNAMO_PK_NAME=familyId              # Primary key
```

## MCP Server Resources

**24 MCP Servers Available:**
- **Sequential Thinking** - Complex reasoning and debugging
- **Context7** - Official library documentation lookup
- **Magic** - UI component generation (21st.dev patterns)
- **Playwright** - Browser automation and E2E testing
- **AWS Services** - DynamoDB, S3, Athena, Cognito, Cost Explorer
- **Python Tools** - FastMCP, PRIMS, Jupyter, Django
- **Infrastructure** - CDK, Terraform, Serverless (SAM)

## Next Steps for New AI Assistant

1. **Establish baseline**: Run `git status` and `make status`
2. **Understand current work**: Read branch name and recent commits
3. **Validate environment**: Run `make health-check`
4. **Review relevant docs**: Based on task type (auth, validation, etc.)
5. **Plan approach**: Use TodoWrite for >3 step tasks
6. **Execute with quality**: Follow TDD, validate continuously
7. **Document session**: Create history file before committing
8. **Quality gates**: Run `make quality-check` before MR

## Support Resources

**For Help With:**
- Architecture questions → `CLAUDE.md` (complete guide)
- Authentication issues → `AUTH-ADVICE.md` (troubleshooting)
- GitHub operations → `GITHUB-ADVICE.md` (token setup)
- Validation strategies → `.claude/commands/validate-*.md`
- Recurring problems → `RECURRING-ISSUES-FIX.md`

**For Context:**
- Recent work → `/history/` directory (session logs)
- Analysis reports → `/claudedocs/` directory
- Implementation patterns → `backend/api/src/main/python/openapi_server/impl/`

---

**Project Maturity**: Production-ready educational platform with ~1 year active development
**Code Quality**: High standards with automated quality gates and comprehensive testing
**Documentation**: Extensive with 40+ advice files and systematic solution prompts
**Stability**: Core functionality stable, active feature development ongoing
