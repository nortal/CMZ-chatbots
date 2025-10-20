# CMZ Project - Custom Agent Ideas

## Development Workflow Agents

### 1. openapi-sync-validator
**Purpose**: Ensure OpenAPI spec, generated code, and implementations stay synchronized
**Subagent Type**: quality-engineer
**When to Use**: Before commits, after spec changes, during code review
**Tasks**:
- Compare openapi_spec.yaml with generated controllers
- Verify impl/ modules match all endpoints
- Check handlers.py routing completeness
- Validate request/response schemas match models
**Output**: Sync status report with specific mismatches

### 2. integration-test-generator
**Purpose**: Auto-generate integration tests from OpenAPI spec
**Subagent Type**: quality-engineer
**When to Use**: After implementing new endpoints, during test coverage review
**Tasks**:
- Read OpenAPI spec for endpoint definitions
- Generate pytest test cases for each endpoint
- Include auth scenarios (admin, user, visitor, etc.)
- Add positive and negative test cases
- Mock DynamoDB/external dependencies appropriately
**Output**: Complete test file ready for tests/integration/

### 3. jira-velocity-analyzer
**Purpose**: Analyze completed tickets and calculate velocity metrics
**Subagent Type**: requirements-analyst
**When to Use**: Sprint retrospectives, quarterly reviews
**Tasks**:
- Query Jira for completed tickets in date range
- Read session history files for actual time spent
- Calculate velocity (story points vs. actual hours)
- Identify high-velocity patterns
- Generate velocity trend charts
**Output**: Markdown report with velocity analysis

### 4. session-history-creator
**Purpose**: Auto-generate session history documentation
**Subagent Type**: technical-writer
**When to Use**: At end of development sessions
**Tasks**:
- Review git commits in session timeframe
- List files modified with change summaries
- Document commands executed
- Extract key decisions from conversation
- Note MCP tools used
- Generate formatted session log
**Output**: history/{initials}_{date}_{time}.md file

## Code Quality Agents

### 5. hexagonal-architecture-enforcer
**Purpose**: Ensure hexagonal architecture patterns are followed
**Subagent Type**: system-architect
**When to Use**: During code review, before merging PRs
**Tasks**:
- Verify business logic in impl/ not in generated/ controllers
- Check separation of concerns across layers
- Validate dependency injection patterns
- Ensure proper abstraction boundaries
- Flag domain logic leaking into infrastructure
**Output**: Architecture compliance report with violations

### 6. error-schema-validator
**Purpose**: Ensure consistent Error schema usage across all endpoints
**Subagent Type**: quality-engineer
**When to Use**: During implementation, before PR creation
**Tasks**:
- Check all error responses use Error schema
- Verify HTTP status codes match error types
- Validate error messages are descriptive
- Ensure details field contains useful context
- Check for inconsistent error handling patterns
**Output**: Error handling compliance report

### 7. security-audit-agent
**Purpose**: Automated security checks for API endpoints
**Subagent Type**: security-engineer
**When to Use**: Before deployment, during security reviews
**Tasks**:
- Check JWT authentication on protected endpoints
- Verify RBAC enforcement at API level
- Scan for SQL injection risks (even with DynamoDB)
- Check input validation on all POST/PATCH/PUT
- Verify soft-delete semantics prevent data leaks
- Scan for exposed secrets in code
**Output**: Security audit report with severity ratings

## AI/ChatGPT Integration Agents

### 8. guardrails-tester
**Purpose**: Validate guardrails system effectiveness
**Subagent Type**: quality-engineer
**When to Use**: After guardrails changes, before production deploy
**Tasks**:
- Test each guardrail rule type (ALWAYS, NEVER, etc.)
- Verify priority system works correctly
- Check prompt injection effectiveness
- Test keyword filtering safety net
- Validate circuit breaker triggers
- Test template system completeness
**Output**: Guardrails test report with coverage metrics

### 9. chatgpt-response-quality-checker
**Purpose**: Analyze ChatGPT response quality and appropriateness
**Subagent Type**: quality-engineer
**When to Use**: During development, monitoring production
**Tasks**:
- Sample conversation responses
- Check educational appropriateness
- Verify personality consistency (Simba, Koda, etc.)
- Flag inappropriate content
- Measure response latency
- Check token usage efficiency
**Output**: Response quality metrics report

### 10. animal-personality-designer
**Purpose**: Create and validate new animal personality configurations
**Subagent Type**: requirements-analyst
**When to Use**: Adding new zoo animals to chatbot system
**Tasks**:
- Research animal facts and characteristics
- Design personality traits and speaking style
- Create keyword-response mappings
- Generate educational content prompts
- Define guardrails specific to animal
- Create test conversation scenarios
**Output**: Complete personality configuration + test cases

## DevOps & Infrastructure Agents

### 11. dynamodb-schema-analyzer
**Purpose**: Analyze and optimize DynamoDB table designs
**Subagent Type**: backend-architect
**When to Use**: Before table creation, during performance reviews
**Tasks**:
- Review access patterns for tables
- Validate GSI design for query efficiency
- Check partition key distribution
- Analyze TTL configuration
- Estimate read/write capacity needs
- Recommend optimization strategies
**Output**: DynamoDB schema review with recommendations

### 12. docker-health-checker
**Purpose**: Validate Docker container health and configuration
**Subagent Type**: devops-architect
**When to Use**: Before deployment, troubleshooting issues
**Tasks**:
- Check Dockerfile best practices
- Validate environment variable configuration
- Test container startup and health endpoints
- Verify port mappings and networking
- Check resource limits (memory, CPU)
- Scan for security vulnerabilities
**Output**: Docker health report with action items

### 13. aws-cost-estimator
**Purpose**: Estimate AWS costs for CMZ infrastructure
**Subagent Type**: devops-architect
**When to Use**: Planning deployments, budget reviews
**Tasks**:
- Analyze DynamoDB table usage patterns
- Calculate Lambda invocation costs
- Estimate API Gateway request costs
- Factor in CloudWatch logging costs
- Consider data transfer costs
- Project monthly/annual costs
**Output**: Cost estimate breakdown with optimization tips

## Testing & Quality Agents

### 14. test-coverage-analyzer
**Purpose**: Analyze test coverage and identify gaps
**Subagent Type**: quality-engineer
**When to Use**: Before releases, during sprint reviews
**Tasks**:
- Run pytest coverage report
- Identify untested endpoints
- Find edge cases not covered
- Check error path coverage
- Analyze integration test completeness
- Recommend missing test scenarios
**Output**: Coverage report with specific gap recommendations

### 15. playwright-e2e-generator
**Purpose**: Generate Playwright E2E tests for frontend flows
**Subagent Type**: quality-engineer
**When to Use**: After UI implementation, before release
**Tasks**:
- Analyze React component structure
- Generate user journey test scenarios
- Create accessibility validation tests
- Build form interaction tests
- Test role-based navigation flows
- Validate responsive design breakpoints
**Output**: Playwright test suite for critical user journeys

### 16. regression-detector
**Purpose**: Detect regressions by comparing current vs previous behavior
**Subagent Type**: root-cause-analyst
**When to Use**: After major changes, before releases
**Tasks**:
- Run full integration test suite
- Compare results with previous run
- Identify new failures
- Analyze failure patterns
- Check for performance degradation
- Generate regression report
**Output**: Regression analysis with root cause hypotheses

---

## Root-Cause-Analyst Agent Configuration

### 🔴 CRITICAL BEHAVIOR: Database State Verification
**MANDATORY REQUIREMENT: Always verify actual DynamoDB state before concluding "missing data" or "empty database"**

**Why This Is Critical**:
- Code inspection only shows what SHOULD happen
- Database queries show what DID happen
- Inferring database state from code logic is INSUFFICIENT and DANGEROUS
- Real-world case: Bug #8 was misdiagnosed as "empty database" when table had 33 families

### Database Verification Protocol

**BEFORE concluding any of these:**
- "Empty database"
- "Missing seed data"
- "No test data"
- "Table is empty"
- "Not a bug - needs data"

**YOU MUST run these commands:**

```bash
# 1. Verify table exists
aws dynamodb list-tables \
  --region us-west-2 \
  --profile cmz | grep <table_name>

# 2. Check item count
aws dynamodb scan \
  --table-name <table_name> \
  --region us-west-2 \
  --profile cmz \
  --select "COUNT"

# 3. Sample actual data
aws dynamodb scan \
  --table-name <table_name> \
  --region us-west-2 \
  --profile cmz \
  --max-items 10
```

**Required Documentation**:
- Include actual query output in analysis
- Show item counts and sample data
- State "VERIFIED via DynamoDB query" not "inferred from code"
- Distinguish between:
  * Table doesn't exist (infrastructure issue)
  * Table exists but empty (seed data issue)
  * Table has data but query returns empty (filtering/association bug)

### ⚠️ CRITICAL: Required Reading Before Analysis
When using the root-cause-analyst agent for ANY bug investigation, the agent MUST read these files first:

1. **ENDPOINT-WORK.md** - Source of truth for endpoint implementation status
   - Shows which endpoints are IMPLEMENTED vs NOT IMPLEMENTED
   - Documents hexagonal architecture: handlers.py contains real implementations
   - Prevents false "not implemented" diagnoses

2. **CLAUDE.md** - Project architecture and OpenAPI generation workflow
   - Documents post-generation validation pipeline
   - Explains hexagonal architecture pattern

3. **docs/LESSONS-LEARNED-ROOT-CAUSE-ANALYSIS.md** - Database verification requirements
   - Documents Bug #8 misdiagnosis incident
   - Explains mandatory database verification protocol

### Investigation Pattern
```
1. Read ENDPOINT-WORK.md → Determine true implementation status
2. Read CLAUDE.md → Understand project architecture
3. Check impl/handlers.py → Verify actual implementations exist
4. Check impl/animals.py → Verify forwarding functions exist
5. **IF "empty data" suspected → VERIFY DynamoDB state with actual queries**
6. Diagnose root cause → Identify forwarding chain breakage vs true missing implementation
```

### Analysis Pattern Examples

**❌ WRONG Analysis (Inference-Based)**:
```
Evidence:
1. Backend code looks correct ✓
2. Would return [] if table empty ✓
3. [INFERRED] Table must be empty
Conclusion: Not a bug, needs seed data
```

**✅ CORRECT Analysis (Verification-Based)**:
```
Evidence:
1. Backend code looks correct ✓
2. DynamoDB scan shows 33 families ✓ (VERIFIED)
3. 4+ families have softDelete: false ✓ (VERIFIED)
4. API returns [] despite data existing ✓
Conclusion: Real bug - user filtering or association issue
```

### Common False Positives to Avoid

**1. Empty Database Inference**
- **DON'T**: Conclude database is empty from code inspection
- **DO**: Run aws dynamodb scan to verify actual state
- **Example**: Bug #8 - code looked correct, but assumed empty database without checking

**2. Not Implemented Errors**
- **DON'T**: Assume 501 errors mean "not implemented"
- **DO**: Check ENDPOINT-WORK.md first
- **Pattern**: Endpoint may be implemented in handlers.py but stub doesn't forward
- **Root Cause**: post_openapi_generation.py may have created dead-end stub

**3. Architecture Pattern**:
- Controllers → impl/animals.py (forwarding layer) → impl/handlers.py (actual implementation)
- **If impl/animals.py returns 501 but handlers.py has implementation** = FORWARDING BROKEN
- **If impl/animals.py returns 501 and handlers.py lacks implementation** = TRULY NOT IMPLEMENTED

## Documentation Agents

### 17. api-documentation-generator
**Purpose**: Generate comprehensive API documentation from OpenAPI spec
**Subagent Type**: technical-writer
**When to Use**: After API changes, for developer handoff
**Tasks**:
- Parse OpenAPI specification
- Generate endpoint documentation
- Create request/response examples
- Document authentication flows
- Add error handling examples
- Generate Postman collection
**Output**: Complete API documentation in Markdown + Postman collection

### 18. readme-maintainer
**Purpose**: Keep README files up-to-date with project changes
**Subagent Type**: technical-writer
**When to Use**: After significant changes, before releases
**Tasks**:
- Review recent commits for changes
- Update setup instructions
- Refresh environment variable documentation
- Update dependency versions
- Revise architecture diagrams
- Add new troubleshooting sections
**Output**: Updated README.md with change summary

### 19. changelog-generator
**Purpose**: Auto-generate CHANGELOG from git commits and PRs
**Subagent Type**: technical-writer
**When to Use**: Before releases, sprint end
**Tasks**:
- Parse git commit messages
- Categorize changes (features, fixes, breaking)
- Extract PR descriptions
- Format in Keep a Changelog style
- Link to relevant Jira tickets
- Generate version comparison
**Output**: CHANGELOG.md with version entries

## Jira Integration Agents

### 20. jira-ticket-creator
**Purpose**: Create properly formatted Jira tickets from requirements
**Subagent Type**: requirements-analyst
**When to Use**: Sprint planning, feature brainstorming
**Tasks**:
- Parse requirement descriptions
- Generate technical requirements
- Create acceptance criteria
- Estimate story points based on complexity
- Set proper priority and labels
- Link to epic/parent tickets
**Output**: Created Jira tickets with proper formatting

### 21. pr-to-jira-updater
**Purpose**: Automatically update Jira tickets when PRs are merged
**Subagent Type**: general-purpose
**When to Use**: After PR merge, in CI/CD pipeline
**Tasks**:
- Extract ticket IDs from PR title/commits
- Add PR link to ticket comments
- Update ticket status to appropriate workflow state
- Add implementation details comment
- Update affected tickets for bulk PRs
**Output**: Updated Jira tickets with PR information

### 22. epic-progress-tracker
**Purpose**: Track and report on epic completion progress
**Subagent Type**: requirements-analyst
**When to Use**: Daily standups, sprint planning
**Tasks**:
- Query all tickets in epic
- Calculate completion percentage
- Identify blockers
- Show velocity trends
- Project completion date
- Generate burn-down chart data
**Output**: Epic progress report with visualizations

## Specialized CMZ Agents

### 23. knowledge-base-curator
**Purpose**: Manage and validate educational knowledge articles
**Subagent Type**: technical-writer
**When to Use**: Adding educational content, content review
**Tasks**:
- Validate knowledge article structure
- Check educational appropriateness
- Verify facts and citations
- Categorize by topic and difficulty
- Tag for searchability
- Generate related article links
**Output**: Curated knowledge base with metadata

### 24. family-permission-validator
**Purpose**: Validate family relationship and permission logic
**Subagent Type**: security-engineer
**When to Use**: Testing RBAC, before releases
**Tasks**:
- Test parent-child relationship lookup
- Verify parent access to child conversations
- Check permission boundaries
- Test edge cases (multiple families, etc.)
- Validate data isolation
**Output**: Family permission test report

### 25. conversation-analytics
**Purpose**: Analyze conversation patterns and engagement metrics
**Subagent Type**: general-purpose
**When to Use**: Monthly reviews, feature planning
**Tasks**:
- Query conversation sessions from DynamoDB
- Calculate engagement metrics (turns, duration)
- Identify popular animals
- Analyze conversation topics
- Track user retention
- Generate insights for improvement
**Output**: Analytics dashboard report

---

## Priority Recommendations

### High Priority (Implement First)
1. **openapi-sync-validator** - Critical for maintaining consistency
2. **integration-test-generator** - Speeds up test coverage
3. **session-history-creator** - Automates tedious documentation
4. **hexagonal-architecture-enforcer** - Maintains code quality

### Medium Priority (Useful for Velocity)
5. **jira-velocity-analyzer** - Supports your current presentation work
6. **pr-to-jira-updater** - Reduces manual Jira updates
7. **security-audit-agent** - Important for production readiness
8. **test-coverage-analyzer** - Identifies quality gaps

### Low Priority (Nice to Have)
9. **aws-cost-estimator** - Useful for budgeting
10. **changelog-generator** - Good for releases

---

## Next Steps

1. Review this list and prioritize which agents would provide most value
2. Start with 2-3 high-priority agents
3. Create agent configuration files in `.claude/agents/`
4. Test agents on real CMZ tasks
5. Iterate and refine based on results
6. Add new agents as patterns emerge

Would you like me to implement any of these agents?
