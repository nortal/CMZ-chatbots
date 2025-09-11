# CMZ API Validation Scripts and Prompts

This directory contains automation scripts and standardized prompts for the CMZ Chatbots API validation epic implementation.

## Files

### Scripts
- `update_jira_tickets.sh` - Comprehensive Jira ticket management script with history tracking and status updates

### Prompts
- This README contains the `/nextfive` command prompt for systematic API validation implementation

## /nextfive Command Prompt

**Use this prompt for systematic implementation of API validation tickets:**

```
Implement the next 5 high-priority Jira tickets from our API validation epic, following the same systematic approach we used for PR003946-90, PR003946-72, PR003946-73, PR003946-69, and PR003946-66.

## Context
- CMZ chatbot backend API using OpenAPI-first development
- Flask/Connexion with DynamoDB persistence
- Docker containerized development environment
- All business logic must go in `impl/` directory (never in generated code)

## Required Process
1. **Use sequential reasoning MCP** to predict test outcomes and plan implementation
2. **Implement all tickets systematically** with proper error handling
3. **Verify functionality via cURL testing** against running Docker container
4. **Address any GitHub Advanced Security scanner issues** (unused imports, etc.)
5. **Create and submit MR** with Copilot review workflow
6. **Update Jira tickets** with implementation status and MR links
7. **Handle review feedback** and iterate until approval

## Technical Requirements
- Follow existing patterns in `openapi_server/impl/`
- Maintain OpenAPI specification compliance
- Use consistent Error schema with code/message/details structure
- Include proper audit timestamps and server-generated IDs
- Implement foreign key validation where applicable
- Ensure soft-delete semantics consistency

## MR Creation and Review Process
- **Target Branch**: `dev`
- **Add Reviewer**: @github-actions[bot] (Copilot) - add as reviewer on the MR/PR
- **MR Description**: Include comprehensive implementation documentation with API verification examples
- **Include History File**: Add session documentation to `/history/` directory
- **Single Review Round**: Address Copilot feedback once, don't iterate endlessly
- **Re-test After Changes**: Verify all functionality still works after addressing feedback
- **Security Scans**: Ensure all GitHub Advanced Security checks pass

## Jira Integration
- **Status Update**: Transition all implemented tickets to "In Progress" 
- **Activity Comments**: Add implementation details and MR links to ticket history
- **Use Script**: Run `./scripts/update_jira_tickets.sh comment` with new MR URLs

## Quality Gates
- All functionality verified working via API testing
- No breaking changes to existing features
- GitHub Advanced Security issues resolved
- Copilot review feedback addressed (one round)
- Professional MR description with API verification examples
- Clean, maintainable code following project conventions
- Jira tickets updated with implementation status
- Final sequential reasoning validation of all steps completed

## Complete Workflow
1. List next 5 tickets and use sequential reasoning to plan
2. Implement systematically with comprehensive testing
3. Address security issues and run quality checks
4. Create MR targeting `dev` branch with Copilot as reviewer
5. Add history documentation to MR
6. Update Jira tickets to "In Progress" with MR links using script
7. Wait for and address Copilot review feedback (one round)
8. Re-test and verify all functionality after changes
9. **Use sequential reasoning to validate all steps were completed correctly**
10. Ensure final approval and merge readiness

Please start by listing the next 5 tickets, then use sequential reasoning to plan the implementation approach.
```

## Why This Template Works

- References proven successful implementation pattern
- Emphasizes systematic sequential reasoning + implementation + testing workflow
- Captures key architectural constraints (impl/ directory, OpenAPI-first)
- Includes security scanning and professional documentation requirements
- Provides clear actionable starting steps
- Includes comprehensive MR creation and review process
- Integrates Jira automation for ticket management
- Self-validates with sequential reasoning at completion

## Jira Script Usage

The `update_jira_tickets.sh` script supports multiple modes:

```bash
# Add activity comments and set status to In Progress (default)
./update_jira_tickets.sh comment

# Show edit history for all tickets
./update_jira_tickets.sh history

# Restore original descriptions from Jira history
./update_jira_tickets.sh restore

# Show current ticket information
./update_jira_tickets.sh info

# Restore descriptions and add comments in one operation
./update_jira_tickets.sh restore-and-comment
```

### Environment Setup

```bash
export JIRA_EMAIL='your.email@nortal.com'
export JIRA_API_TOKEN='your_jira_api_token'
chmod +x scripts/update_jira_tickets.sh
```

To get API token: Jira Settings > Security > Create API Token

## Integration with Development Workflow

1. Use `/nextfive` prompt to implement tickets systematically
2. Create MR with proper reviewer assignment (Copilot)
3. Use Jira script to update ticket status and add activity comments
4. Address single round of Copilot feedback
5. Validate completion with sequential reasoning
6. Ensure merge readiness

This creates a complete end-to-end workflow from implementation to production deployment.