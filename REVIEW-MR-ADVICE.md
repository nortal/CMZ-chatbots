# REVIEW-MR-ADVICE.md - MR Review Command Best Practices and Troubleshooting

## Overview
The `/review-mr` command provides automated, comprehensive review of GitHub Pull Requests, focusing on comment resolution, security findings, and merge readiness validation.

## Key Success Patterns

### 1. Complete Review Coverage
**Pattern**: Always check ALL comment sources
```bash
# Sources to check:
- Issue comments (gh api .../issues/$PR/comments)
- Review comments (gh api .../pulls/$PR/comments)
- PR reviews (gh api .../pulls/$PR/reviews)
- Check runs (gh pr checks $PR)
```

**Why It Works**: Different bots and reviewers use different comment mechanisms. Missing any source means incomplete review.

### 2. Bot Identification
**Pattern**: Correctly identify automated reviewers
```json
{
  "copilot": ["github-copilot[bot]", "copilot[bot]"],
  "security": ["github-advanced-security[bot]", "dependabot[bot]"],
  "ci": ["github-actions[bot]", "vercel[bot]"]
}
```

**Common Mistake**: Assuming all bots have consistent naming patterns.

### 3. Gating Function Hierarchy
**Critical Gates** (Block merge):
1. Failing required CI/CD checks
2. Unresolved merge conflicts
3. Changes requested by required reviewers
4. Security vulnerabilities (P0/P1)

**Warning Gates** (Review recommended):
1. Unresolved Copilot suggestions
2. Low-priority security findings
3. Optional check failures
4. Documentation gaps

### 4. Actionable Reporting
**Good Report**:
```markdown
### 🔧 Action Items
- Resolve merge conflict in backend/api/openapi_spec.yaml (lines 245-267)
- Address Copilot suggestion: "Add error handling for null response" (auth_controller.py:45)
- Fix failing test: test_animal_config_update (see CI logs)
```

**Poor Report**:
```markdown
### Issues
- Some problems found
- Review comments exist
- Tests not passing
```

## Common Issues and Solutions

### Issue 1: Rate Limiting
**Symptom**: "API rate limit exceeded for user"
```bash
# Solution: Add delays between API calls
sleep 0.5  # Between each gh api call

# Or use --paginate more efficiently
gh api ... --paginate --jq '.[] | {relevant_fields}'
```

### Issue 2: Large PRs Timeout
**Symptom**: Command hangs or times out on large PRs
```bash
# Solution: Limit comment fetching
gh api ... --paginate --per-page 30 | head -100

# Or process in batches
TOTAL_COMMENTS=$(gh api ... --jq '. | length')
if [ $TOTAL_COMMENTS -gt 100 ]; then
    echo "⚠️ Large PR detected, showing first 100 comments"
fi
```

### Issue 3: Permission Errors
**Symptom**: "Resource not accessible by integration"
```bash
# Solution: Check authentication and permissions
gh auth status
gh auth refresh -h github.com -s repo,read:org

# For private repos, ensure proper access
gh repo view nortal/CMZ-chatbots --json private
```

### Issue 4: Inconsistent Bot Names
**Symptom**: Missing Copilot or security comments
```bash
# Solution: Use flexible matching
jq '.[] | select(.user.login | test("copilot|github-copilot"; "i"))'

# Or check user type
jq '.[] | select(.user.type == "Bot")'
```

## Advanced Usage Patterns

### Pattern 1: Filtered Review
```bash
# Review only security aspects
/review-mr 40 --focus security

# Implementation:
FOCUS="${2:-all}"
if [ "$FOCUS" == "security" ]; then
    # Only check security-related items
fi
```

### Pattern 2: Comparison Review
```bash
# Compare current state with previous review
/review-mr 40 --compare

# Store previous review
gh pr view 40 --json comments --jq '.comments[-1].body' > /tmp/last_review.md
# Compare with new review
diff /tmp/last_review.md /tmp/current_review.md
```

### Pattern 3: Bulk Review
```bash
# Review multiple PRs
for PR in 40 41 42; do
    /review-mr $PR --summary-only
done
```

### Pattern 4: Integration with CI/CD
```yaml
# .github/workflows/pr-review.yml
name: Automated PR Review
on:
  pull_request_review:
    types: [submitted]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run MR Review
        run: |
          .claude/commands/review-mr.sh ${{ github.event.pull_request.number }}
```

## Troubleshooting Guide

### Debug Mode
```bash
# Enable verbose output
DEBUG=1 /review-mr 40

# Implementation:
[ "$DEBUG" == "1" ] && set -x
[ "$DEBUG" == "1" ] && echo "Raw API response: $API_RESPONSE"
```

### Common Error Messages

**"PR not found"**
- Check PR number exists: `gh pr list --state all | grep "#40"`
- Verify repo context: `git remote -v`
- Check authentication: `gh auth status`

**"No comments found"**
- PR might be too new (wait for bots to run)
- Check if bots are enabled for the repo
- Verify API endpoints are correct

**"Cannot determine merge status"**
- Fetch latest: `git fetch origin`
- Update PR: `gh pr view 40 --json mergeable`
- Check branch protection rules

### Performance Optimization

**Slow API Calls**:
```bash
# Cache responses for repeated runs
CACHE_DIR="/tmp/mr-review-cache"
CACHE_FILE="$CACHE_DIR/pr-$PR_NUMBER-$(date +%s).json"

if [ -f "$CACHE_FILE" ] && [ $(find "$CACHE_FILE" -mmin -5) ]; then
    echo "Using cached data (< 5 minutes old)"
    cat "$CACHE_FILE"
else
    gh api ... > "$CACHE_FILE"
fi
```

**Parallel Processing**:
```bash
# Fetch multiple data sources in parallel
{
    gh api .../comments > /tmp/comments.json &
    gh api .../reviews > /tmp/reviews.json &
    gh pr checks $PR > /tmp/checks.json &
    wait
}
```

## Integration Examples

### With /prepare-mr
```bash
# Complete MR preparation workflow
/prepare-mr              # Prepare the MR
gh pr create ...         # Create PR
/review-mr $PR_NUMBER    # Review automatically
```

### With /nextfive
```bash
# After implementing tickets
/nextfive PR003946-91    # Implement tickets
git push                 # Push changes
gh pr create ...         # Create PR
/review-mr $PR_NUMBER    # Validate implementation
```

### With TodoWrite
```bash
# Track review tasks
TodoWrite([
  "Run /review-mr on PR #40",
  "Address Copilot feedback",
  "Resolve security findings",
  "Re-run review after fixes"
])
```

## Best Practices Checklist

### Before Running Review
- [ ] PR has been open for >5 minutes (bots need time)
- [ ] All commits are pushed
- [ ] CI/CD has started running
- [ ] Reviewers have been added

### During Review
- [ ] Check all comment sources
- [ ] Validate gating functions
- [ ] Generate actionable items
- [ ] Post summary to PR

### After Review
- [ ] Address blocking issues first
- [ ] Mark resolved comments
- [ ] Re-run review after fixes
- [ ] Document resolution in PR

## Gotchas and Edge Cases

### 1. Draft PRs
Draft PRs may not trigger all checks:
```bash
STATE=$(gh pr view $PR --json isDraft --jq '.isDraft')
[ "$STATE" == "true" ] && echo "⚠️ Draft PR - some checks may be skipped"
```

### 2. Force Pushes
Force pushes invalidate previous reviews:
```bash
# Check for force pushes
gh pr view $PR --json commits --jq '.commits[-1].messageHeadline' | grep -q "force push"
```

### 3. Stale Reviews
Reviews before last push are outdated:
```bash
LAST_PUSH=$(gh pr view $PR --json updatedAt --jq '.updatedAt')
# Compare with review timestamps
```

### 4. Hidden Comments
Some comments are collapsed or hidden:
```bash
# Include hidden/resolved comments
gh api ... --include=hidden,resolved
```

## Metrics and Success Criteria

### Review Completeness Score
```bash
SCORE=100
[ $UNRESOLVED_COMMENTS -gt 0 ] && SCORE=$((SCORE - 20))
[ $FAILING_CHECKS -gt 0 ] && SCORE=$((SCORE - 30))
[ "$MERGEABLE" != "true" ] && SCORE=$((SCORE - 25))
[ $SECURITY_FINDINGS -gt 0 ] && SCORE=$((SCORE - 25))

echo "Review Completeness: $SCORE%"
```

### Time to Merge Estimation
```bash
# Estimate based on historical data
AVG_COMMENT_RESOLUTION_TIME=30  # minutes per comment
AVG_CONFLICT_RESOLUTION_TIME=45  # minutes
AVG_TEST_FIX_TIME=60            # minutes per failing test

ESTIMATED_TIME=$((
    UNRESOLVED_COMMENTS * AVG_COMMENT_RESOLUTION_TIME +
    ([ "$MERGEABLE" != "true" ] && echo $AVG_CONFLICT_RESOLUTION_TIME || echo 0) +
    FAILING_TESTS * AVG_TEST_FIX_TIME
))

echo "Estimated time to merge-ready: $ESTIMATED_TIME minutes"
```

## Related Documentation
- `.claude/commands/review-mr.md` - Command implementation
- `.claude/commands/prepare-mr.md` - Pre-submission preparation
- `MR-ADVICE.md` - General MR best practices
- `CLAUDE.md` - Complete workflow integration