#!/bin/bash
set -e

current_branch=$(git branch --show-current)

# Validate we're on a feature branch
if [[ "$current_branch" == "main" || "$current_branch" == "master" || "$current_branch" == "dev" ]]; then
    echo "❌ Cannot create MR from protected branch: $current_branch"
    echo "   Switch to a feature branch first"
    exit 1
fi

# Ensure we're up to date with dev
echo "🔄 Updating dev branch..."
git fetch origin dev
git rebase origin/dev

# Run quality checks
echo "🔍 Running quality checks..."
if command -v pytest >/dev/null 2>&1; then
    pytest --cov=openapi_server || echo "⚠️  Tests failed - continue with MR creation? (Ctrl+C to abort)"
fi

# Push branch
echo "📤 Pushing branch..."
git push -u origin "$current_branch"

# Create MR targeting dev
echo "📝 Creating MR targeting dev branch..."
gh pr create --base dev --fill

echo "✅ MR created successfully targeting dev branch"
echo "   Add reviewer: gh pr edit \$(gh pr list --state open --head $current_branch --json number --jq '.[0].number') --add-reviewer Copilot"