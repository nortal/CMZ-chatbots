#!/bin/bash
#
# Setup Architecture Validation Git Hook
#
# This script installs a pre-commit hook that validates hexagonal architecture
# before allowing commits. This prevents broken forwarding chains from entering
# the codebase and causing Bugs #1 and #7 to recur.
#
# Usage:
#   ./scripts/setup_architecture_validation_hook.sh
#
# What it does:
#   1. Copies scripts/git-hooks/pre-commit to .git/hooks/pre-commit
#   2. Makes the hook executable
#   3. Verifies the hook is working
#
# To remove the hook:
#   rm .git/hooks/pre-commit
#

set -e

echo ""
echo "🔧 Setting up Architecture Validation Git Hook..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Error: Not in a git repository root directory"
    echo "   Please run this script from the project root (where .git/ exists)"
    exit 1
fi

# Check if source hook exists
if [ ! -f "scripts/git-hooks/pre-commit" ]; then
    echo "❌ Error: Source hook not found at scripts/git-hooks/pre-commit"
    exit 1
fi

# Check if validation script exists
if [ ! -f "scripts/validate_handler_forwarding_comprehensive.py" ]; then
    echo "❌ Error: Validation script not found"
    echo "   Expected: scripts/validate_handler_forwarding_comprehensive.py"
    exit 1
fi

# Create .git/hooks directory if it doesn't exist
mkdir -p .git/hooks

# Backup existing pre-commit hook if it exists
if [ -f ".git/hooks/pre-commit" ]; then
    echo "📦 Backing up existing pre-commit hook..."
    cp .git/hooks/pre-commit .git/hooks/pre-commit.backup.$(date +%Y%m%d_%H%M%S)
    echo "   ✓ Backup saved as .git/hooks/pre-commit.backup.*"
    echo ""
fi

# Copy the hook
echo "📋 Installing architecture validation hook..."
cp scripts/git-hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
echo "   ✓ Hook installed at .git/hooks/pre-commit"
echo "   ✓ Hook made executable"
echo ""

# Verify the hook
echo "🧪 Testing the hook..."
if python3 scripts/validate_handler_forwarding_comprehensive.py > /dev/null 2>&1; then
    echo "   ✓ Validation script works correctly"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✅ Architecture validation hook installed successfully!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📋 What happens now:"
    echo ""
    echo "1. Before EVERY commit, the hook will validate the hexagonal architecture"
    echo "2. If forwarding chains are broken, the commit will be BLOCKED"
    echo "3. You'll get clear instructions on how to fix the issue"
    echo "4. Once fixed, you can commit normally"
    echo ""
    echo "🛡️  Protection enabled for:"
    echo "   • Bug #1: systemPrompt persistence (PATCH /animal_config)"
    echo "   • Bug #7: Animal Details save (PUT /animal/{id})"
    echo "   • All 60+ handlers across 12 domains"
    echo ""
    echo "⚠️  To bypass the hook (NOT RECOMMENDED):"
    echo "   git commit --no-verify"
    echo ""
    echo "📄 To remove the hook:"
    echo "   rm .git/hooks/pre-commit"
    echo ""
else
    echo "   ⚠️  Validation script has failures"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "⚠️  Hook installed but validation is currently failing"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "The hook has been installed, but your current codebase has architecture issues."
    echo ""
    echo "📋 Fix the issues before committing:"
    echo "   python3 scripts/validate_handler_forwarding_comprehensive.py"
    echo ""
    echo "Then run the validation again to see what needs fixing."
    echo ""
fi
