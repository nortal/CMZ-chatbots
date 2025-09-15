# RESOLVE-MR-ADVICE.md - Best Practices and Troubleshooting Guide

## Overview
The `/resolve-mr` command automates the resolution of MR review comments, reducing manual fix time from hours to minutes. This guide provides best practices, common pitfalls, and troubleshooting strategies.

## When to Use /resolve-mr

### Ideal Scenarios
✅ **After Copilot Review**: When you have multiple automated suggestions
✅ **Security Vulnerabilities**: CVE fixes and dependency updates
✅ **Code Quality Issues**: Unused imports, formatting, linting
✅ **Simple Test Failures**: Snapshot updates, assertion value changes
✅ **Documentation Gaps**: Missing docstrings or comments

### When NOT to Use
❌ **Architectural Changes**: Fundamental design issues
❌ **Business Logic Errors**: Incorrect algorithms or data handling
❌ **Complex Test Failures**: Tests failing due to logic errors
❌ **Performance Issues**: Requires profiling and optimization
❌ **Breaking API Changes**: Requires coordination with consumers

## Best Practices

### 1. Pre-Resolution Checklist
```bash
# Always start with a clean working tree
git status  # Should show no uncommitted changes

# Ensure you're on the correct branch
git branch  # Should show feature branch, not main/dev

# Pull latest changes to avoid conflicts
git pull origin $(git branch --show-current)

# Run review-mr first to understand issues
/review-mr ${PR_NUMBER} > review-baseline.json
```

### 2. Incremental Resolution Strategy
Instead of fixing everything at once, use categorical resolution:

```bash
# Phase 1: Security fixes (highest priority)
/resolve-mr ${PR_NUMBER} --only security
git push && sleep 60  # Let CI run

# Phase 2: Code quality (imports, formatting)
/resolve-mr ${PR_NUMBER} --only imports,formatting
git push && sleep 60

# Phase 3: Tests and documentation
/resolve-mr ${PR_NUMBER} --only tests,documentation
git push
```

### 3. Validation Between Fixes
```bash
# After each category of fixes
make test        # Ensure tests still pass
make lint        # Check for new linting issues
make build-api   # Verify build succeeds
```

### 4. Comment Resolution Patterns

#### Effective Resolution Messages
```bash
# Good: Specific and actionable
"✅ Resolved: Removed unused import 'datetime' from auth.py (commit a1b2c3d)"

# Bad: Generic
"Fixed"

# Good: Explains why if not fixing
"ℹ️ Not resolved: This import is used in type hints (line 45). Keeping as-is."

# Bad: Dismissive
"Ignoring this"
```

### 5. Handling Conflicting Suggestions
When reviewers disagree:

```yaml
Priority Order:
  1. Security issues (always fix)
  2. Broken functionality (must fix)
  3. Test failures (should fix)
  4. Code style (nice to fix)
  5. Preferences (optional)

Resolution Strategy:
  - Document the conflict in PR comment
  - Apply higher priority suggestion
  - Explain reasoning for choice
```

## Common Issues and Solutions

### Issue 1: Fixes Break Existing Tests
**Symptom**: Tests pass before resolution, fail after
**Cause**: Automated fixes changed behavior
**Solution**:
```bash
# Rollback the specific fix
git revert HEAD

# Apply fixes more selectively
/resolve-mr ${PR_NUMBER} --skip tests

# Manually fix tests with context
```

### Issue 2: GitHub API Rate Limiting
**Symptom**: "API rate limit exceeded" errors
**Cause**: Too many API calls in short period
**Solution**:
```bash
# Check rate limit status
gh api /rate_limit

# Wait for reset
sleep $(($(gh api /rate_limit --jq '.rate.reset') - $(date +%s)))

# Use authentication for higher limits
export GITHUB_TOKEN=$(gh auth token)
```

### Issue 3: Merge Conflicts After Fixes
**Symptom**: "Merge conflict" when pushing
**Cause**: Upstream changes during resolution
**Solution**:
```bash
# Stash your fixes
git stash

# Pull and rebase
git pull --rebase origin $(git branch --show-current)

# Reapply fixes
git stash pop

# Resolve any conflicts manually
git mergetool
```

### Issue 4: Circular Fix Dependencies
**Symptom**: Fix A breaks B, fixing B breaks A
**Cause**: Tightly coupled code issues
**Solution**:
```bash
# Identify the coupling
/review-mr ${PR_NUMBER} --analyze-dependencies

# Fix both issues together
git checkout -b fix-coupling
# Make coordinated changes
git commit -m "fix: resolve circular dependency between A and B"
```

### Issue 5: Comments Not Marking as Resolved
**Symptom**: GitHub still shows unresolved comments
**Cause**: API permissions or comment thread structure
**Solution**:
```bash
# Verify permissions
gh api /repos/:owner/:repo/pulls/${PR_NUMBER} --jq '.maintainer_can_modify'

# Use conversation API instead
gh api -X POST /repos/:owner/:repo/issues/${PR_NUMBER}/comments \
  -f body="Marking previous comments as resolved: [list]"

# Or manually resolve in GitHub UI
echo "Please manually resolve comments: ${COMMENT_IDS}"
```

## Advanced Troubleshooting

### Debugging Resolution Failures

#### Enable Verbose Logging
```bash
# Set debug environment variables
export RESOLVE_MR_DEBUG=1
export GH_DEBUG=1

# Run with verbose output
/resolve-mr ${PR_NUMBER} --verbose 2>&1 | tee resolve-debug.log
```

#### Analyze Resolution Patterns
```bash
# Check which fixes were attempted
grep "Attempting fix:" resolve-debug.log

# Check which succeeded
grep "Successfully fixed:" resolve-debug.log

# Check failures
grep -A 5 "Failed to fix:" resolve-debug.log
```

### Custom Fix Strategies

#### Adding New Fix Categories
```python
# In resolve-mr implementation
FIX_STRATEGIES = {
    'custom_issue': {
        'detection': ['pattern1', 'pattern2'],
        'resolution': custom_fix_function
    }
}

def custom_fix_function(issue, context):
    # Implementation
    pass
```

#### Overriding Default Fixes
```bash
# Create custom fix configuration
cat > .resolve-mr-config.json << EOF
{
  "overrides": {
    "formatting": {
      "command": "npm run custom-format",
      "files": "**/*.{js,ts}"
    }
  }
}
EOF

# Use with custom config
/resolve-mr ${PR_NUMBER} --config .resolve-mr-config.json
```

## Performance Optimization

### Parallel Processing
```bash
# Run independent fixes in parallel
/resolve-mr ${PR_NUMBER} --parallel --max-workers 4
```

### Caching API Responses
```bash
# Cache GitHub API responses
export RESOLVE_MR_CACHE_DIR=/tmp/resolve-mr-cache
/resolve-mr ${PR_NUMBER} --use-cache
```

### Batch Operations
```bash
# Batch similar fixes together
/resolve-mr ${PR_NUMBER} --batch-mode
```

## Integration Patterns

### CI/CD Integration
```yaml
# .github/workflows/auto-resolve.yml
name: Auto-Resolve MR Issues
on:
  issue_comment:
    types: [created]
jobs:
  resolve:
    if: |
      github.event.issue.pull_request &&
      contains(github.event.comment.body, '/resolve-mr')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup environment
        run: |
          pip install -r requirements.txt
          npm install
      - name: Run resolution
        run: |
          ./claude/commands/resolve-mr.sh ${{ github.event.issue.number }}
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Pre-commit Hook Integration
```bash
# .git/hooks/pre-push
#!/bin/bash
# Auto-resolve before pushing
if [ -n "$(gh pr view --json number -q .number 2>/dev/null)" ]; then
    /resolve-mr --quick-check
    if [ $? -ne 0 ]; then
        echo "⚠️ Unresolved MR issues detected. Run /resolve-mr to fix."
        exit 1
    fi
fi
```

### Slack/Teams Notification
```bash
# After successful resolution
if [ $REMAINING_ISSUES -eq 0 ]; then
    curl -X POST $SLACK_WEBHOOK_URL \
      -H 'Content-Type: application/json' \
      -d "{\"text\":\"✅ PR #${PR_NUMBER} auto-resolved successfully!\"}"
fi
```

## Metrics and Monitoring

### Track Resolution Success Rate
```bash
# Log resolution metrics
echo "$(date),${PR_NUMBER},${RESOLVED_COUNT},${REMAINING_ISSUES}" >> resolution-metrics.csv

# Generate report
awk -F',' '{total+=$3; remaining+=$4} END {
    printf "Average resolution rate: %.1f%%\n", (total/(total+remaining)*100)
}' resolution-metrics.csv
```

### Common Resolution Patterns
```yaml
Most Auto-Fixable (>90% success):
  - Unused imports
  - Code formatting
  - Simple dependency updates
  - Missing docstrings

Moderate Success (50-90%):
  - Test snapshot updates
  - Linting warnings
  - Simple security patches

Usually Manual (<50%):
  - Algorithm errors
  - Performance issues
  - Architectural changes
  - Complex security vulnerabilities
```

## Recovery Procedures

### Full Rollback
```bash
# If everything goes wrong
git checkout backup/pr-${PR_NUMBER}-*
git branch -D feature-branch
git checkout -b feature-branch
git push --force origin HEAD

# Clean up backup branches
git branch -D backup/pr-*
```

### Partial Rollback
```bash
# Rollback specific commits
git revert HEAD~2..HEAD  # Rollback last 2 commits
git push origin HEAD
```

### Manual Resolution Fallback
```bash
# Generate manual fix instructions
/resolve-mr ${PR_NUMBER} --generate-manual-steps > manual-fixes.md

# Follow step-by-step guide
cat manual-fixes.md
```

## Quality Assurance

### Post-Resolution Validation
```bash
# Comprehensive validation script
cat > validate-resolution.sh << 'EOF'
#!/bin/bash
set -e

echo "🔍 Validating resolution..."

# 1. Check build
make build-api || exit 1

# 2. Run tests
pytest --cov || exit 1

# 3. Check security
gh api /repos/:owner/:repo/code-scanning/alerts \
  --jq 'if length > 0 then error("Security issues found") else "✅" end'

# 4. Verify API endpoints
make test-integration || exit 1

echo "✅ All validations passed!"
EOF

chmod +x validate-resolution.sh
./validate-resolution.sh
```

## Learning from Failures

### Document Unfixable Issues
```markdown
## Unfixable Issues Log

### Issue: Complex Type Error in auth.py
- **Date**: 2024-01-14
- **PR**: #123
- **Reason**: Required architectural change
- **Manual Fix**: Refactored authentication flow
- **Time Taken**: 2 hours
- **Lesson**: Add type checking to pre-commit hooks
```

### Improve Detection Patterns
```python
# Add new patterns as you discover them
NEW_PATTERNS = {
    'async_await_issue': {
        'detection': ['await is not used', 'async function called without await'],
        'resolution': 'add_await_to_async_calls'
    }
}
```

## Summary

The `/resolve-mr` command is powerful but requires understanding of its limitations and proper usage patterns. Key takeaways:

1. **Always validate after fixes** - Automated fixes can introduce new issues
2. **Use incremental resolution** - Fix categories separately for easier rollback
3. **Document manual interventions** - Build knowledge base of unfixable patterns
4. **Monitor success metrics** - Track what works and what doesn't
5. **Have rollback plan ready** - Always create backup before resolution

Remember: The goal is to reduce manual work, not eliminate human judgment. Use `/resolve-mr` as a tool to handle routine fixes while focusing human effort on complex issues that require deeper understanding.