#!/bin/bash

# Merge Parallel Claude Work Streams
# This script safely merges all parallel branches back to main

echo "🔄 Merging parallel Claude work streams..."

# Store current branch
CURRENT_BRANCH=$(git branch --show-current)
DATE=$(date +%Y%m%d)

# Ensure we're on main/master
git checkout main 2>/dev/null || git checkout master

# Pull latest changes
echo "📥 Pulling latest changes..."
git pull origin main 2>/dev/null || git pull origin master

# Function to safely merge a branch
merge_branch() {
    local branch=$1
    local description=$2

    echo ""
    echo "🔀 Merging $branch ($description)..."

    if git show-ref --verify --quiet refs/heads/$branch; then
        # Check if branch has changes
        if [ $(git rev-list --count main..$branch 2>/dev/null) -gt 0 ]; then
            git merge $branch --no-ff -m "Merge: $description (Claude parallel work)" || {
                echo "❌ Merge conflict in $branch! Please resolve manually."
                echo "   Run: git status"
                echo "   Fix conflicts, then: git add . && git commit"
                return 1
            }
            echo "✅ Successfully merged $branch"
        else
            echo "⏭️  No changes in $branch, skipping"
        fi
    else
        echo "⏭️  Branch $branch not found, skipping"
    fi
}

# Merge all parallel branches
merge_branch "parallel/handlers-$DATE" "Handler forwarding fixes (T001-T006)"
merge_branch "parallel/tests-$DATE" "Test coverage improvements (T007-T012)"
merge_branch "parallel/e2e-$DATE" "E2E test suite (T013-T019)"
merge_branch "parallel/docs-$DATE" "Documentation updates (T006, T020-T025)"

echo ""
echo "📊 Merge Summary:"
git log --oneline -5

echo ""
echo "🧪 Running validation..."
# Run basic validation
make validate-api 2>/dev/null || echo "⚠️  Validation had issues, please review"

echo ""
echo "📈 Next steps:"
echo "1. Review merged changes: git diff HEAD~4..HEAD"
echo "2. Run full test suite: make test"
echo "3. Push to remote: git push origin main"
echo "4. Clean up branches: ./scripts/cleanup_parallel_branches.sh"

# Create cleanup script
cat > ./scripts/cleanup_parallel_branches.sh << 'CLEANUP'
#!/bin/bash
# Cleanup parallel branches after successful merge
DATE=$(date +%Y%m%d)
echo "🧹 Cleaning up parallel branches..."
git branch -d parallel/handlers-$DATE 2>/dev/null && echo "✅ Deleted parallel/handlers-$DATE"
git branch -d parallel/tests-$DATE 2>/dev/null && echo "✅ Deleted parallel/tests-$DATE"
git branch -d parallel/e2e-$DATE 2>/dev/null && echo "✅ Deleted parallel/e2e-$DATE"
git branch -d parallel/docs-$DATE 2>/dev/null && echo "✅ Deleted parallel/docs-$DATE"
echo "✨ Cleanup complete!"
CLEANUP

chmod +x ./scripts/cleanup_parallel_branches.sh

echo ""
echo "✅ Merge script complete!"