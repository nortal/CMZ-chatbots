# GITHUB-ADVICE.md - GitHub CLI Operations and PR Creation Guide

## 🚨 CRITICAL: Target Branch Policy
**ALWAYS create PRs against `dev` branch, NEVER against `main`**
- The `dev` branch is the integration branch for all feature work
- The `main` branch is reserved for production-ready releases
- All PRs should use: `--base dev`

## Quick Start: Use the `/prepare-mr` Command
The project includes a comprehensive `/prepare-mr` command that guides you through the entire MR preparation process:
- Runs all quality checks
- Helps create the PR with proper formatting
- Ensures all criteria are met
- **BUT**: You still need to export the GitHub token first (see below)

## Critical GitHub Token Configuration

### Token Location and Setup
The GitHub token is stored in `.env.local`:
```bash
GITHUB_TOKEN=ghp_[your_token_here]
```

### Using GitHub Token with gh CLI
**IMPORTANT**: The gh CLI doesn't automatically read from `.env.local`. You must explicitly export the token:

```bash
# Always export the token before gh operations
export GITHUB_TOKEN=$(grep GITHUB_TOKEN .env.local | cut -d '=' -f2)

# Or source the entire file
source .env.local

# Then use gh commands
gh pr create ...
```

### Token Scope Requirements
Different GitHub operations require different token scopes:

**For Creating PRs**:
- ✅ `repo` - Required for PR creation
- ✅ `workflow` - Required if repo has GitHub Actions
- ✅ `user` - Basic user information

**For Editing PRs** (additional scopes):
- ⚠️ `read:org` - Required to edit PR descriptions
- ⚠️ `write:discussion` - May be needed for comments

**Token Validation**:
```bash
# Check current auth status and token scopes
export GITHUB_TOKEN=your_token_here
gh auth status
```

## PR Creation Workflow

### Step 1: Prepare Branch
```bash
# Ensure you're on a feature branch
git checkout -b feature/your-feature-name

# Commit all changes
git add -A
git commit -m "feat: Your feature description"

# Push to remote
git push -u origin feature/your-feature-name
```

### Step 2: Create PR with Token
```bash
# Export token first
export GITHUB_TOKEN=$(grep GITHUB_TOKEN .env.local | cut -d '=' -f2)

# Create PR with inline description (ALWAYS use --base dev)
gh pr create --base dev --title "Your PR Title" --body "Your PR description"

# Or create PR with heredoc for complex descriptions
gh pr create --base dev --title "Your PR Title" --body "$(cat <<'EOF'
## Summary
Detailed description here...

## Changes
- Change 1
- Change 2
EOF
)"
```

### Step 3: Handle Common Errors

**Error: "Resource not accessible by personal access token"**
- **Cause**: Token missing required scopes or not exported
- **Fix**:
  1. Export token: `export GITHUB_TOKEN=...`
  2. Check scopes: `gh auth status`
  3. Update token at https://github.com/settings/tokens if needed

**Error: "GraphQL: Your token has not been granted the required scopes"**
- **Cause**: Operation needs additional scopes (like `read:org`)
- **Fix**: Either:
  1. Use web interface for operations requiring extra scopes
  2. Generate new token with required scopes
  3. Use simpler operations that don't need extra scopes

**Warning: "1 uncommitted change"**
- **Cause**: PR created but local file (like PR_DESCRIPTION.md) not committed
- **Fix**: This is just a warning; PR is still created. Commit or discard local changes.

## Best Practices

### 1. Token Management
```bash
# Create a helper script for GitHub operations
cat > gh-with-token.sh << 'EOF'
#!/bin/bash
export GITHUB_TOKEN=$(grep GITHUB_TOKEN .env.local | cut -d '=' -f2)
gh "$@"
EOF
chmod +x gh-with-token.sh

# Use it like: ./gh-with-token.sh pr create ...
```

### 2. PR Description Strategy
When token lacks edit scopes:
1. Create PR with minimal description first
2. Save full description to `PR_DESCRIPTION.md`
3. Update via web interface using saved description
4. This two-step approach always works

### 3. Fallback Workflow
If gh CLI fails completely:
1. Push branch: `git push -u origin feature/branch-name`
2. Note the URL provided in output
3. Visit GitHub web interface
4. Create PR manually with saved description

## Successful PR Creation Example

From our Chat Epic implementation:
```bash
# 1. Export token
export GITHUB_TOKEN=<YOUR_TOKEN_HERE>

# 2. Create PR (succeeded even though description was empty due to file path issue)
gh pr create --base main --title "feat: Implement Chat History Epic (PR003946-170)"
# Result: https://github.com/nortal/CMZ-chatbots/pull/46

# 3. PR was created successfully despite warning about uncommitted changes
```

## Token Security Notes

**NEVER**:
- Commit tokens to repository
- Share tokens in PR descriptions or comments
- Use tokens in client-side code

**ALWAYS**:
- Store tokens in `.env.local` (gitignored)
- Rotate tokens if accidentally exposed
- Use minimal required scopes
- Export token only for current shell session

## Quick Reference Commands

```bash
# Check auth status
export GITHUB_TOKEN=$(grep GITHUB_TOKEN .env.local | cut -d '=' -f2)
gh auth status

# Create simple PR
gh pr create --base main --title "Title" --body "Description"

# List PRs
gh pr list

# View PR
gh pr view 46

# Check PR status
gh pr status

# Close PR (if needed)
gh pr close 46
```

## Troubleshooting Checklist

1. ✅ Is token exported? `echo $GITHUB_TOKEN`
2. ✅ Does token have required scopes? `gh auth status`
3. ✅ Is branch pushed? `git push -u origin branch-name`
4. ✅ Are all changes committed? `git status`
5. ✅ Is base branch correct? (usually `main`)
6. ✅ Is GitHub CLI authenticated? `gh auth status`

## Summary

The key lesson learned: **GitHub CLI requires explicit token export from .env.local**. The CLI doesn't automatically read environment files, so always export the token before operations. When in doubt, use the web interface as a reliable fallback - the branch push provides the URL for easy PR creation.