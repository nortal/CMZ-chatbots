#!/bin/bash
# Setup script for contract validation pre-commit hooks
# Run this once to install hooks in your local repository

set -e

echo "📦 Installing contract validation pre-commit hooks..."

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Error: Not in a git repository root"
    echo "Please run this script from the repository root directory"
    exit 1
fi

# Check if pre-commit hook script exists
if [ ! -f "scripts/hooks/pre-commit-contract-validation" ]; then
    echo "❌ Error: Pre-commit hook script not found"
    echo "Expected: scripts/hooks/pre-commit-contract-validation"
    exit 1
fi

# Create .git/hooks directory if it doesn't exist
mkdir -p .git/hooks

# Copy hook to .git/hooks
cp scripts/hooks/pre-commit-contract-validation .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

echo "✅ Contract validation hooks installed successfully"
echo ""
echo "The pre-commit hook will now run automatically before each commit."
echo ""
echo "To bypass validation (emergency only):"
echo "  git commit --no-verify"
echo ""
echo "To test the hook manually:"
echo "  .git/hooks/pre-commit"
echo ""
