# Merge Request Preparation Command

## Usage

```
/prepare-mr
```

Use this command to ensure your merge request is fully ready for review and approval according to CMZ project standards.

## Overview

This command guides you through the complete merge request preparation process, ensuring all quality gates are passed, all comments are resolved, and all learnings are captured before submission.

## ⚠️ CRITICAL: GitHub Setup Required

**Before proceeding, you MUST read `GITHUB-ADVICE.md`** which covers:
- How to export GitHub tokens from `.env.local`
- Target branch policy (ALWAYS use `--base dev`, never `main`)
- Common gh CLI errors and solutions
- Token scope requirements

## Prerequisites

Before running this command, ensure:
- You have read `GITHUB-ADVICE.md` for GitHub CLI setup
- GitHub token is properly configured and exported
- You are working on a feature branch (never on `dev` directly)
- All development work is complete
- You have tested your changes locally

## Process

Execute this systematic process to prepare your merge request:

### 1. Quality Gates Validation

Run all quality checks and ensure they pass:

```bash
# Run the complete test suite
python -m pytest tests/integration/test_api_validation_epic.py -v

# Run unit tests with coverage
pytest --cov=openapi_server

# Run Playwright E2E tests (Step 1 validation first)
cd backend/api/src/main/python/tests/playwright
./run-step1-validation.sh

# If Step 1 passes ≥5/6 browsers, run full suite
FRONTEND_URL=http://localhost:3001 npx playwright test --config config/playwright.config.js --reporter=line

# Check for linting and formatting issues
flake8 backend/api/src/main/python/openapi_server/impl/
black --check backend/api/src/main/python/openapi_server/impl/
```

**Success Criteria:**
- All tests passing
- No linting errors
- No formatting issues
- Playwright tests show ≥5/6 browsers passing authentication

### 2. GitHub Advanced Security Review

Address all CodeQL and security scanner issues:

```bash
# Check current security alerts (if you have access to GitHub CLI with proper permissions)
gh api repos/:owner/:repo/code-scanning/alerts

# Common issues to check manually:
# - Unused imports
# - Dead code elimination
# - SQL injection prevention (though we use DynamoDB)
# - Input validation completeness
# - Error message information disclosure
```

**Manual Review Checklist:**
- [ ] No unused imports in modified files
- [ ] All user inputs properly validated
- [ ] Error messages don't expose sensitive information
- [ ] No hardcoded secrets or credentials
- [ ] All database operations use parameterized queries/DynamoDB proper practices

### 3. Pre-MR Code Review

Perform self-review of your changes:

```bash
# Review your changes comprehensively
git diff dev...HEAD

# Check for common issues:
# - Debug statements (console.log, print statements)
# - TODO comments in production code
# - Commented-out code blocks
# - Inconsistent formatting
# - Missing error handling
```

**Self-Review Checklist:**
- [ ] No debug statements or console logs
- [ ] No TODO comments for core functionality
- [ ] No commented-out code blocks
- [ ] Consistent code formatting
- [ ] Proper error handling for all operations
- [ ] All business logic in `impl/` directory (never in generated code)
- [ ] DynamoDB operations use centralized utilities from `impl/utils/dynamo.py`

### 4. Create Merge Request

Create the MR with comprehensive documentation:

```bash
# CRITICAL: Export GitHub token first (see GITHUB-ADVICE.md for details)
export GITHUB_TOKEN=$(grep GITHUB_TOKEN .env.local | cut -d '=' -f2)

# Verify token is exported
echo $GITHUB_TOKEN | head -c 10  # Should show first 10 chars of token

# Ensure you're on your feature branch
git branch --show-current

# Push your changes (if not already pushed)
git push -u origin $(git branch --show-current)

# Create the merge request targeting dev (NEVER use main)
gh pr create --title "Clear, descriptive title" --body "$(cat <<'EOF'
## Summary
Brief description of what this MR implements.

## Changes Made
- Bullet point list of key changes
- API endpoints added/modified
- Database schema changes
- Configuration updates

## Testing Performed
- [ ] Unit tests: All passing
- [ ] Integration tests: All passing
- [ ] Playwright E2E tests: ≥5/6 browsers passing
- [ ] Manual API testing via cURL/Postman
- [ ] Security scan: All issues resolved

## API Verification Examples
```bash
# Example cURL commands demonstrating the functionality
curl -X GET "http://localhost:8080/api/endpoint" -H "Content-Type: application/json"
```

## Related Jira Tickets
- PR003946-XX: Description of what was implemented
- PR003946-YY: Description of what was implemented

## Pre-Review Checklist
- [ ] All comments resolved with documentation
- [ ] All inline comments resolved with documentation
- [ ] All quality gates passed
- [ ] All CodeQL issues addressed
- [ ] Self-review completed
- [ ] API endpoints tested and working
- [ ] Session history documentation included

## Deployment Notes
Any special considerations for deployment or configuration changes.

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)" --base dev
```

### 5. Add Reviewer and Handle Feedback

Add reviewer and systematically address all feedback:

```bash
# Get the PR number from the previous command output
PR_NUMBER=$(gh pr list --head $(git branch --show-current) --json number --jq '.[0].number')

# Add Copilot as reviewer
gh pr edit $PR_NUMBER --add-reviewer Copilot

echo "✅ Merge request created: https://github.com/owner/repo/pull/$PR_NUMBER"
echo "✅ Reviewer added: Copilot"
echo ""
echo "⏳ Next steps:"
echo "1. Wait for Copilot review feedback"
echo "2. Address all inline comments systematically"
echo "3. Document resolution for each comment"
echo "4. Use /resolve-comments command to complete the process"
```

## Comment Resolution Process

When you receive review feedback, follow this systematic approach:

### For Each Inline Comment:

1. **Analyze the feedback** - Understand what the reviewer is asking for
2. **Make the necessary changes** - Implement the requested improvements
3. **Document the resolution** - Explain what was changed and why
4. **Mark as resolved** - Use the GitHub CLI to formally resolve the comment

```bash
# For each comment, after making the requested changes:
gh pr comment <COMMENT_ID> --body "✅ Resolved: Brief description of how the issue was addressed"

# Example:
gh pr comment 123456789 --body "✅ Resolved: Added input validation for email field and improved error message clarity"
```

### For General PR Comments:

1. **Address the feedback** in your code
2. **Commit your changes** with clear commit messages
3. **Reply to the comment** explaining what was done

```bash
# After addressing feedback, add a comprehensive reply
gh pr comment $PR_NUMBER --body "All feedback addressed:

- Fixed input validation as suggested in line 45
- Improved error handling in user creation endpoint
- Added missing docstrings to helper functions
- Updated tests to cover edge cases mentioned

All changes committed and ready for re-review."
```

## Final Validation

Before requesting final approval:

```bash
# Re-run critical tests to ensure changes didn't break anything
python -m pytest tests/integration/test_api_validation_epic.py -v

# Verify your API endpoints still work
curl -X GET "http://localhost:8080/api/your-endpoint" -H "Content-Type: application/json"

# Check that all security issues are resolved
# (Manual check or via GitHub security tab)
```

## Success Criteria

Your MR is ready for final approval when:

- [ ] **All Comments Resolved**: Every inline comment has been addressed and marked as resolved with documentation
- [ ] **All Quality Gates Passed**: Tests, security scans, linting all passing
- [ ] **All CodeQL Issues Addressed**: GitHub Advanced Security shows no new issues
- [ ] **Documentation Complete**: MR description is comprehensive and accurate
- [ ] **API Verification**: All new/modified endpoints tested and working
- [ ] **Learnings Captured**: Any new insights documented in MR-ADVICE.md
- [ ] **Session History**: Development session documented in `/history/` directory

## Integration with Other Commands

This command works with other CMZ project commands:

- Use `/nextfive` for systematic ticket implementation
- Use `/validate-frontend-backend-integration` for comprehensive testing
- Follow up with learnings integration using the patterns established in other command files

## Troubleshooting

### Common Issues:

**Tests Failing After Review Changes:**
```bash
# Re-run test suite to identify what broke
python -m pytest tests/integration/test_api_validation_epic.py -v --tb=short

# Check for obvious issues
flake8 backend/api/src/main/python/openapi_server/impl/
```

**CodeQL Issues Not Resolving:**
- Check GitHub Security tab manually
- Review common issues: unused imports, error message disclosure, input validation
- Commit focused fixes and wait for re-scan

**Comment Resolution Not Working:**
```bash
# Get comment IDs from PR
gh pr view $PR_NUMBER --json comments

# Make sure you're using the correct comment ID format
# Comment IDs are usually visible in the GitHub web interface URL
```

## Learning Integration

After your MR is approved and merged:

1. **Update MR-ADVICE.md** with any new patterns or learnings discovered during the process
2. **Document any process improvements** that could help future MRs
3. **Add final learnings comment** to the MR before merge for future reference

Example final comment:
```bash
gh pr comment $PR_NUMBER --body "## Final Learnings

Key insights from this MR process:
- Pattern X worked well for validation logic
- Approach Y simplified error handling
- Configuration Z improved test reliability

These learnings have been added to MR-ADVICE.md for future reference."
```