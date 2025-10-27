# /review-mr - Comprehensive MR Review and Validation Command

## Purpose
Systematically review a GitHub Pull Request (MR) to ensure all comments are resolved, security checks pass, and gating functions are satisfied before merge.

## Usage
```bash
/review-mr <pr-number>
# Example: /review-mr 40
```

## Command Implementation

### Phase 1: Fetch and Validate MR Data

```bash
# Validate PR exists and fetch basic information
PR_NUMBER=$1
echo "🔍 Fetching PR #$PR_NUMBER details..."

# Check if PR exists
gh pr view $PR_NUMBER --json state,title,url,mergeable,author,reviews,statusCheckRollup > /tmp/pr_data.json 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Error: PR #$PR_NUMBER not found or inaccessible"
    exit 1
fi

# Extract PR state
PR_STATE=$(jq -r '.state' /tmp/pr_data.json)
PR_TITLE=$(jq -r '.title' /tmp/pr_data.json)
PR_URL=$(jq -r '.url' /tmp/pr_data.json)
MERGEABLE=$(jq -r '.mergeable' /tmp/pr_data.json)

echo "📋 PR #$PR_NUMBER: $PR_TITLE"
echo "   State: $PR_STATE"
echo "   URL: $PR_URL"
```

### Phase 2: Analyze All Comments

```bash
echo ""
echo "💬 Analyzing comments and reviews..."

# Fetch issue comments (regular PR comments)
gh api repos/nortal/CMZ-chatbots/issues/$PR_NUMBER/comments --paginate > /tmp/issue_comments.json

# Fetch review comments (inline code comments)
gh api repos/nortal/CMZ-chatbots/pulls/$PR_NUMBER/comments --paginate > /tmp/review_comments.json

# Fetch PR reviews
gh api repos/nortal/CMZ-chatbots/pulls/$PR_NUMBER/reviews --paginate > /tmp/reviews.json

# Count Copilot comments (Note: Copilot can appear as "Copilot" or "github-copilot[bot]")
COPILOT_COMMENTS=$(jq '[.[] | select(.user.login == "github-copilot[bot]" or .user.login == "copilot[bot]" or .user.login == "Copilot")] | length' /tmp/issue_comments.json)
COPILOT_INLINE=$(jq '[.[] | select(.user.login == "github-copilot[bot]" or .user.login == "copilot[bot]" or .user.login == "Copilot")] | length' /tmp/review_comments.json)

# Count security bot comments
SECURITY_COMMENTS=$(jq '[.[] | select(.user.login == "github-advanced-security[bot]")] | length' /tmp/issue_comments.json)
SECURITY_INLINE=$(jq '[.[] | select(.user.login == "github-advanced-security[bot]")] | length' /tmp/review_comments.json)

# Check for CodeQL findings in review body
CODEQL_FINDINGS=$(jq -r '.[] | select(.user.login == "github-advanced-security[bot]") | select(.body | contains("CodeQL found")) | .body' /tmp/reviews.json | head -1)

# Find unresolved conversations
UNRESOLVED_THREADS=$(gh api repos/nortal/CMZ-chatbots/pulls/$PR_NUMBER --jq '.mergeable_state' | grep -q "blocked" && echo "Yes" || echo "No")

echo "   Copilot Comments: $COPILOT_COMMENTS regular, $COPILOT_INLINE inline"
echo "   Security Comments: $SECURITY_COMMENTS regular, $SECURITY_INLINE inline"
if [ -n "$CODEQL_FINDINGS" ]; then
    echo "   ⚠️ CodeQL Alert: $CODEQL_FINDINGS"
fi
```

### Phase 3: Check Gating Functions

```bash
echo ""
echo "🚦 Checking gating functions..."

# Check CI/CD status
echo "   CI/CD Checks:"
gh pr checks $PR_NUMBER --json name,state | jq -r '.[] | "     - \(.name): \(.state)"'

# Check for required reviews
REVIEWS_APPROVED=$(jq '[.[] | select(.state == "APPROVED")] | length' /tmp/reviews.json)
REVIEWS_CHANGES_REQUESTED=$(jq '[.[] | select(.state == "CHANGES_REQUESTED")] | length' /tmp/reviews.json)

echo ""
echo "   Review Status:"
echo "     - Approved: $REVIEWS_APPROVED"
echo "     - Changes Requested: $REVIEWS_CHANGES_REQUESTED"

# Check merge conflicts
echo ""
echo "   Merge Status:"
if [ "$MERGEABLE" == "MERGEABLE" ]; then
    echo "     ✅ No merge conflicts"
else
    echo "     ❌ Merge conflicts or not mergeable (state: $MERGEABLE)"
fi

# Security scanning status
echo ""
echo "   Security Scanning:"
SECURITY_CHECKS=$(gh pr checks $PR_NUMBER --json name,state | jq -r '.[] | select(.name | contains("CodeQL") or contains("security") or contains("SAST") or contains("Trivy")) | "\(.name): \(.state)"')
if [ -z "$SECURITY_CHECKS" ]; then
    echo "     ⚠️ No security checks found"
else
    echo "$SECURITY_CHECKS" | sed 's/^/     - /'
fi
```

### Phase 4: Extract Unresolved Items

```bash
echo ""
echo "📝 Extracting unresolved items..."

# Extract unresolved Copilot suggestions
echo "   Copilot Suggestions:"
jq -r '.[] | select(.user.login == "github-copilot[bot]" or .user.login == "copilot[bot]" or .user.login == "Copilot") | "     - [\(.created_at | split("T")[0])]: \(.body | split("\n")[0] | .[0:100])"' /tmp/review_comments.json | head -5

# Extract security findings
echo ""
echo "   Security Findings:"
jq -r '.[] | select(.user.login == "github-advanced-security[bot]") | "     - [\(.created_at | split("T")[0])]: \(.body | split("\n")[0] | .[0:100])"' /tmp/review_comments.json | head -5

# Find conversations needing resolution
echo ""
echo "   Unresolved Conversations:"
gh api repos/nortal/CMZ-chatbots/pulls/$PR_NUMBER/comments | jq -r '.[] | select(.in_reply_to_id == null) | select(.reactions["+1"] == 0) | "     - [\(.path // "general")]: \(.body | split("\n")[0] | .[0:80])"' | head -5
```

### Phase 5: Generate and Post Review Summary

```bash
echo ""
echo "📊 Generating review summary..."

# Determine overall status
READY_TO_MERGE="true"
BLOCKING_ISSUES=""

if [ "$REVIEWS_CHANGES_REQUESTED" -gt 0 ]; then
    READY_TO_MERGE="false"
    BLOCKING_ISSUES="$BLOCKING_ISSUES\n- Changes requested by reviewers"
fi

if [ "$MERGEABLE" != "MERGEABLE" ]; then
    READY_TO_MERGE="false"
    BLOCKING_ISSUES="$BLOCKING_ISSUES\n- Merge conflicts need resolution"
fi

# Check for failing CI checks
FAILING_CHECKS=$(gh pr checks $PR_NUMBER --json state | jq -r '.[] | select(.state == "FAILURE" or .state == "ERROR") | .state' | wc -l)
if [ "$FAILING_CHECKS" -gt 0 ]; then
    READY_TO_MERGE="false"
    BLOCKING_ISSUES="$BLOCKING_ISSUES\n- $FAILING_CHECKS CI/CD checks failing"
fi

# Create the review report
REVIEW_REPORT=$(cat <<EOF
## 🤖 Automated MR Review Report

**PR #$PR_NUMBER**: $PR_TITLE
**Generated**: $(date -u +"%Y-%m-%d %H:%M UTC")

### 📈 Overall Status
$(if [ "$READY_TO_MERGE" == "true" ]; then echo "✅ **Ready to Merge**"; else echo "⚠️ **Blocked - Action Required**"; fi)

### 🚦 Gating Functions Status
- CI/CD Checks: $(if [ "$FAILING_CHECKS" -eq 0 ]; then echo "✅ All passing"; else echo "❌ $FAILING_CHECKS failing"; fi)
- Code Reviews: $(if [ "$REVIEWS_APPROVED" -gt 0 ] && [ "$REVIEWS_CHANGES_REQUESTED" -eq 0 ]; then echo "✅ Approved"; else echo "⚠️ Needs approval"; fi)
- Merge Conflicts: $(if [ "$MERGEABLE" == "MERGEABLE" ]; then echo "✅ None"; else echo "❌ Conflicts present"; fi)
- Security Scanning: $(if [ -n "$SECURITY_CHECKS" ]; then echo "✅ Completed"; else echo "⚠️ Not configured"; fi)

### 💬 Review Analysis
- **Copilot Review**: $COPILOT_COMMENTS comments, $COPILOT_INLINE inline suggestions
- **Security Review**: $SECURITY_COMMENTS comments, $SECURITY_INLINE inline findings
- **Total Reviews**: $REVIEWS_APPROVED approved, $REVIEWS_CHANGES_REQUESTED requesting changes

### 🔧 Action Items
$(if [ "$READY_TO_MERGE" == "false" ]; then echo -e "$BLOCKING_ISSUES"; else echo "None - PR is ready for merge"; fi)

### 📋 Next Steps
$(if [ "$READY_TO_MERGE" == "true" ]; then
    echo "1. Final review of changes"
    echo "2. Merge when ready"
else
    echo "1. Address blocking issues listed above"
    echo "2. Resolve any unaddressed review comments"
    echo "3. Re-run this review after fixes"
fi)

---
*This review was generated automatically using \`/review-mr\` command*
EOF
)

# Post the review to the PR
echo ""
echo "📮 Posting review summary to PR..."
echo "$REVIEW_REPORT" > /tmp/review_report.md
gh pr comment $PR_NUMBER --body-file /tmp/review_report.md

echo "✅ Review complete and posted to PR #$PR_NUMBER"
```

## Sequential Reasoning Validation

```bash
# Use sequential reasoning to validate review completeness
/sc:think "Validate MR review completeness for PR $PR_NUMBER:
1. Have all Copilot suggestions been identified?
2. Are all security findings documented?
3. Is the gating function status accurate?
4. Are action items clear and actionable?
5. Does the summary provide value for merge decision?"
```

## Error Handling

```bash
# Comprehensive error handling
set -e
trap 'echo "❌ Error occurred at line $LINENO"' ERR

# Validate prerequisites
command -v gh >/dev/null 2>&1 || { echo "❌ GitHub CLI (gh) is required but not installed."; exit 1; }
command -v jq >/dev/null 2>&1 || { echo "❌ jq is required but not installed."; exit 1; }

# Check authentication
gh auth status >/dev/null 2>&1 || { echo "❌ Not authenticated with GitHub. Run 'gh auth login' first."; exit 1; }

# Validate input
if [ -z "$1" ]; then
    echo "❌ Usage: /review-mr <pr-number>"
    echo "   Example: /review-mr 40"
    exit 1
fi

if ! [[ "$1" =~ ^[0-9]+$ ]]; then
    echo "❌ Error: PR number must be a positive integer"
    exit 1
fi
```

## Integration with CMZ Workflow

This command integrates with the CMZ-chatbots development workflow at **Step 9** of the Complete Workflow (CLAUDE.md):

```yaml
workflow_integration:
  stage: "REVIEW PHASE"
  replaces: "Manual Copilot review checking"
  automation: "Systematic review of all feedback sources"

benefits:
  - "Automated detection of unresolved comments"
  - "Comprehensive gating function validation"
  - "Standardized review reports"
  - "Faster merge readiness assessment"

usage_pattern:
  1_create_mr: "gh pr create --title '...' --base dev"
  2_add_reviewer: "gh pr edit $PR --add-reviewer Copilot"
  3_wait_for_review: "Wait for initial feedback"
  4_run_review: "/review-mr $PR"  # THIS COMMAND
  5_address_items: "Fix identified issues"
  6_rerun_review: "/review-mr $PR"  # Verify fixes
  7_merge: "gh pr merge $PR"
```

## Examples

### Example 1: Ready to Merge
```bash
/review-mr 38
# Output: ✅ Ready to Merge - All checks passing, reviews approved
```

### Example 2: Blocked by Reviews
```bash
/review-mr 40
# Output: ⚠️ Blocked - Changes requested by Copilot, 3 unresolved suggestions
```

### Example 3: Security Issues
```bash
/review-mr 42
# Output: ⚠️ Blocked - CodeQL found 2 security vulnerabilities
```

## See Also
- `REVIEW-MR-ADVICE.md` - Best practices and troubleshooting
- `/prepare-mr` - Pre-submission MR preparation
- `/nextfive` - Systematic ticket implementation