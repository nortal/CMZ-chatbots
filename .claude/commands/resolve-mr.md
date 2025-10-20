# Resolve MR Issues

**Purpose**: Automatically analyze and resolve issues identified by `/review-mr`, re-validate the fixes, and mark comments as resolved in GitHub.

**Usage**: `/resolve-mr [pr-number]`

## Context
After running `/review-mr` to analyze PR comments and identify issues, this command automates the resolution process. It parses the review report, applies appropriate fixes for different issue categories, validates the corrections, and updates the PR with resolution status. This reduces manual MR resolution time from hours to minutes.

## Sequential Reasoning Approach

Use MCP Sequential Thinking to systematically resolve all MR issues:

### Phase 1: Analysis and Categorization
**Use Sequential Reasoning to:**
1. **Parse Review Report**: Extract structured data from `/review-mr` output
2. **Categorize Issues**: Group issues by type (security, code quality, tests, documentation)
3. **Map Comments**: Associate GitHub comment IDs with specific issues
4. **Assess Fixability**: Determine which issues can be automatically resolved
5. **Create Resolution Plan**: Order fixes to minimize conflicts and dependencies

**Key Questions for Sequential Analysis:**
- Which issues are automatically fixable vs require manual intervention?
- What is the optimal order for applying fixes to avoid conflicts?
- Are there any contradictory suggestions from different reviewers?
- Which fixes might introduce new issues or breaking changes?
- How can we validate each fix before committing?

### Phase 2: Systematic Resolution
**Implementation Order (Follow Exactly):**

#### Step 1: Initial Setup and Backup
```bash
# Get PR number (use current branch if not specified)
PR_NUMBER=${1:-$(gh pr view --json number -q .number)}

# Create backup branch for rollback capability
git checkout -b backup/pr-${PR_NUMBER}-$(date +%Y%m%d-%H%M%S)
git checkout -

# Run initial review to get baseline
./claude/commands/review-mr.md ${PR_NUMBER} > review-baseline.json
```

#### Step 2: Parse and Categorize Issues
```bash
# Extract issues from review report
ISSUES=$(cat review-baseline.json | jq -r '.issues[]')

# Categorize by type
SECURITY_ISSUES=$(echo "$ISSUES" | grep -E "security|vulnerability|CVE")
IMPORT_ISSUES=$(echo "$ISSUES" | grep -E "unused import|never used")
FORMAT_ISSUES=$(echo "$ISSUES" | grep -E "formatting|style|indentation")
TEST_ISSUES=$(echo "$ISSUES" | grep -E "test failed|assertion|coverage")
DOC_ISSUES=$(echo "$ISSUES" | grep -E "documentation|docstring|comment")
```

#### Step 3: Apply Automated Fixes

**Security Fixes:**
```bash
# Update vulnerable dependencies
if [ -n "$SECURITY_ISSUES" ]; then
    # Python dependencies
    pip install --upgrade $(echo "$SECURITY_ISSUES" | grep -oP "package '\K[^']+")
    pip freeze > requirements.txt

    # Node dependencies
    npm audit fix --force

    git add -A
    git commit -m "fix: resolve security vulnerabilities in dependencies"
fi
```

**Import and Code Quality Fixes:**
```bash
# Remove unused imports (Python)
if [ -n "$IMPORT_ISSUES" ]; then
    # Use autoflake for Python
    find . -name "*.py" -exec autoflake --in-place --remove-unused-variables --remove-all-unused-imports {} \;

    # Use ESLint for JavaScript
    npx eslint --fix "**/*.js"

    git add -A
    git commit -m "fix: remove unused imports and variables"
fi
```

**Formatting Fixes:**
```bash
# Apply code formatters
if [ -n "$FORMAT_ISSUES" ]; then
    # Python
    black . --line-length 120
    isort . --profile black

    # JavaScript/TypeScript
    npx prettier --write "**/*.{js,jsx,ts,tsx,json,css,md}"

    git add -A
    git commit -m "style: apply code formatting standards"
fi
```

**Test Fixes:**
```bash
# Fix common test issues
if [ -n "$TEST_ISSUES" ]; then
    # Update test snapshots if needed
    npm test -- --updateSnapshot

    # Fix Python test assertions
    pytest --tb=short --co -q | while read test; do
        # Analyze and fix test (context-specific logic)
        python -m pytest $test --fix-tests
    done

    git add -A
    git commit -m "test: fix failing tests and update snapshots"
fi
```

**Documentation Fixes:**
```bash
# Generate missing documentation
if [ -n "$DOC_ISSUES" ]; then
    # Python docstrings
    python -m pydocstyle --add-missing

    # Generate JSDoc comments
    npx jsdoc-fix "**/*.js"

    git add -A
    git commit -m "docs: add missing documentation and docstrings"
fi
```

### Phase 3: Validation and Verification
**Validation Checklist:**

#### Step 1: Re-run Review
```bash
# Run review again to check if issues are resolved
./claude/commands/review-mr.md ${PR_NUMBER} > review-after.json

# Compare before and after
REMAINING_ISSUES=$(jq -r '.issues | length' review-after.json)
RESOLVED_COUNT=$(expr $(jq -r '.issues | length' review-baseline.json) - $REMAINING_ISSUES)

echo "Resolved $RESOLVED_COUNT issues, $REMAINING_ISSUES remaining"
```

#### Step 2: Run Quality Gates
```bash
# Run all quality checks
make quality-check

# Run tests
pytest --cov
npm test

# Security scan
gh api /repos/:owner/:repo/code-scanning/alerts --jq '.[] | select(.state=="open")'
```

#### Step 3: Validate No New Issues
```bash
# Check for new issues introduced by fixes
git diff HEAD~$RESOLVED_COUNT..HEAD | grep -E "TODO|FIXME|XXX|HACK" && echo "Warning: New TODOs introduced"

# Verify no breaking changes
make test-integration
```

### Phase 4: GitHub Integration and Documentation
**Mark Comments as Resolved and Document Changes:**

#### Step 1: Mark Inline Comments as Resolved
```bash
# Get all review comments
COMMENTS=$(gh api /repos/:owner/:repo/pulls/${PR_NUMBER}/comments --jq '.[] | {id, path, line, body}')

# Mark resolved comments
echo "$COMMENTS" | while read -r comment; do
    COMMENT_ID=$(echo "$comment" | jq -r '.id')
    COMMENT_BODY=$(echo "$comment" | jq -r '.body')

    # Check if issue was resolved
    if ! grep -q "$COMMENT_BODY" review-after.json; then
        # Mark as resolved using GitHub API
        gh api -X POST /repos/:owner/:repo/pulls/${PR_NUMBER}/comments/${COMMENT_ID}/replies \
            -f body="✅ Resolved: This issue has been automatically fixed in commit $(git rev-parse --short HEAD)"

        # Update comment status
        gh api -X PATCH /repos/:owner/:repo/pulls/comments/${COMMENT_ID} \
            -f resolved=true
    fi
done
```

#### Step 2: Add Summary Comment
```bash
# Create resolution summary
cat > resolution-summary.md << EOF
## 🤖 Automated MR Resolution Report

### Resolution Summary
- **Total Issues Found**: $(jq -r '.issues | length' review-baseline.json)
- **Issues Resolved**: $RESOLVED_COUNT
- **Issues Remaining**: $REMAINING_ISSUES
- **Success Rate**: $(expr $RESOLVED_COUNT \* 100 / $(jq -r '.issues | length' review-baseline.json))%

### Fixes Applied
$(git log --oneline HEAD~$RESOLVED_COUNT..HEAD | sed 's/^/- /')

### Remaining Issues (Require Manual Intervention)
$([ $REMAINING_ISSUES -gt 0 ] && jq -r '.issues[] | "- [ ] " + .' review-after.json || echo "None - all issues resolved! 🎉")

### Quality Gates Status
- Tests: $([ $? -eq 0 ] && echo "✅ Passing" || echo "❌ Failing")
- Linting: $(make lint > /dev/null 2>&1 && echo "✅ Clean" || echo "⚠️ Warnings")
- Security: $([ $(gh api /repos/:owner/:repo/code-scanning/alerts --jq '.[] | select(.state=="open")' | wc -l) -eq 0 ] && echo "✅ No vulnerabilities" || echo "⚠️ Issues detected")

### Next Steps
$([ $REMAINING_ISSUES -eq 0 ] && echo "This PR is ready for merge! All automated checks have passed." || echo "Please manually address the remaining issues listed above.")

---
*Automated by /resolve-mr command • [View Resolution Details]($(git rev-parse HEAD))*
EOF

# Post summary to PR
gh pr comment ${PR_NUMBER} -F resolution-summary.md
```

#### Step 3: Push Changes
```bash
# Push all fixes to the PR branch
git push origin HEAD

# Update PR status
gh pr edit ${PR_NUMBER} --add-label "auto-resolved"
```

## Implementation Details

### Issue Resolution Strategies

#### Category-Specific Fixes
```yaml
security_vulnerabilities:
  detection: ["CVE-", "vulnerability", "security", "GHSA-"]
  resolution:
    - Update affected dependencies to patched versions
    - Apply security patches from advisories
    - Remove vulnerable code patterns
    - Add input validation where missing

unused_imports:
  detection: ["unused import", "imported but never used", "no-unused-vars"]
  resolution:
    - Python: autoflake --remove-all-unused-imports
    - JavaScript: eslint --fix with no-unused-vars rule
    - TypeScript: tsc --noUnusedLocals --noUnusedParameters
    - Go: goimports -w

code_formatting:
  detection: ["formatting", "indentation", "style", "prettier", "black"]
  resolution:
    - Python: black + isort
    - JavaScript/TypeScript: prettier + eslint
    - Go: gofmt + goimports
    - YAML/JSON: prettier

test_failures:
  detection: ["test failed", "assertion error", "expected", "received"]
  resolution:
    - Update test snapshots if output changed intentionally
    - Fix assertion values based on new behavior
    - Add missing test setup/teardown
    - Update mocked values to match reality

documentation:
  detection: ["missing documentation", "undocumented", "no description"]
  resolution:
    - Generate docstrings from function signatures
    - Add JSDoc comments for exported functions
    - Create basic README sections
    - Add inline comments for complex logic
```

### GitHub API Integration

#### Comment Resolution API
```bash
# Mark comment as resolved
gh api -X PATCH /repos/:owner/:repo/pulls/comments/${COMMENT_ID} \
  -f resolved=true \
  -f resolved_by="@me"

# Add resolution reply
gh api -X POST /repos/:owner/:repo/pulls/${PR_NUMBER}/comments/${COMMENT_ID}/replies \
  -f body="✅ Resolved: [description of fix]"

# Update review status
gh api -X POST /repos/:owner/:repo/pulls/${PR_NUMBER}/reviews \
  -f event="APPROVE" \
  -f body="All automated issues have been resolved"
```

### Rollback Capability
```bash
# If fixes cause issues, rollback to backup
git checkout backup/pr-${PR_NUMBER}-*
git branch -D feature-branch
git checkout -b feature-branch
git push --force origin HEAD
```

## Integration Points

### CMZ Project Integration
- **OpenAPI Compliance**: Ensures fixes don't break API contracts
- **Docker Environment**: Runs fixes within containerized environment
- **DynamoDB**: Validates data persistence after fixes
- **Make Commands**: Uses project's make targets for validation
- **Git Workflow**: Follows feature branch pattern

### MCP Server Usage
- **Sequential Thinking**: For analyzing and planning fixes
- **Morphllm**: For bulk code pattern fixes
- **Context7**: For framework-specific fix patterns
- **Playwright**: For UI test validation after fixes

## Quality Gates

### Mandatory Validation Before Completion
- [ ] All automated fixes compile/run without errors
- [ ] No new test failures introduced
- [ ] Security scan shows no new vulnerabilities
- [ ] Linting passes or has fewer warnings
- [ ] API endpoints still respond correctly
- [ ] Docker containers build successfully
- [ ] No git conflicts with upstream changes

### Success Metrics
- [ ] ≥80% of issues automatically resolved
- [ ] All resolved comments marked in GitHub
- [ ] Summary comment posted to PR
- [ ] No breaking changes introduced
- [ ] Quality gates still passing

## Error Handling

### Common Failure Scenarios

#### Conflicting Reviewer Suggestions
**Problem**: Two reviewers suggest opposite changes
**Solution**:
- Prioritize security > functionality > style
- Add comment explaining conflict
- Request manual clarification

#### Fix Introduces New Issues
**Problem**: Automated fix breaks something else
**Solution**:
- Rollback to backup branch
- Apply fixes incrementally
- Test after each fix category

#### API Rate Limiting
**Problem**: GitHub API rate limit exceeded
**Solution**:
- Cache API responses
- Batch API calls
- Add exponential backoff

#### Merge Conflicts
**Problem**: Upstream changes conflict with fixes
**Solution**:
- Pull latest changes first
- Rebase fixes on top
- Re-run validation

## Advanced Usage

### Selective Resolution
```bash
# Only fix specific categories
/resolve-mr ${PR_NUMBER} --only security,imports

# Exclude certain categories
/resolve-mr ${PR_NUMBER} --skip documentation,tests

# Dry run without committing
/resolve-mr ${PR_NUMBER} --dry-run
```

### Custom Fix Patterns
```bash
# Use custom formatter configuration
/resolve-mr ${PR_NUMBER} --formatter-config .custom-prettierrc

# Custom security patch source
/resolve-mr ${PR_NUMBER} --security-patches custom-patches.json
```

### Integration with CI/CD
```yaml
# GitHub Actions workflow
on:
  pull_request_review_comment:
    types: [created]
jobs:
  auto-resolve:
    if: contains(github.event.comment.body, '/resolve-mr')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: ./claude/commands/resolve-mr.sh ${{ github.event.pull_request.number }}
```

## Success Criteria
1. **Automation Rate**: ≥80% of common issues resolved automatically
2. **Time Savings**: Reduce resolution time from hours to <10 minutes
3. **Quality Maintenance**: No degradation in code quality metrics
4. **Reviewer Satisfaction**: Positive feedback on automated resolutions
5. **Process Integration**: Seamless workflow with existing MR process

## References
- `/review-mr` command - Prerequisite analysis command
- `RESOLVE-MR-ADVICE.md` - Best practices and troubleshooting guide
- GitHub API documentation for comment management
- CMZ project standards for code quality and testing