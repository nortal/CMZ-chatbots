#!/bin/bash

# Parallel Claude Instance Setup for CMZ Chatbots
# This script sets up 4 parallel work streams with different git branches

echo "🚀 Setting up parallel Claude instances for CMZ Chatbots..."

# Create working branches for each instance
echo "📦 Creating parallel work branches..."

git checkout main 2>/dev/null || git checkout master
git pull origin main 2>/dev/null || git pull origin master

# Branch 1: Handler Fixes
git checkout -b parallel/handlers-$(date +%Y%m%d) 2>/dev/null || git checkout parallel/handlers-$(date +%Y%m%d)
echo "✅ Branch 1: parallel/handlers-$(date +%Y%m%d) created"

git checkout main 2>/dev/null || git checkout master

# Branch 2: Test Coverage
git checkout -b parallel/tests-$(date +%Y%m%d) 2>/dev/null || git checkout parallel/tests-$(date +%Y%m%d)
echo "✅ Branch 2: parallel/tests-$(date +%Y%m%d) created"

git checkout main 2>/dev/null || git checkout master

# Branch 3: E2E Tests
git checkout -b parallel/e2e-$(date +%Y%m%d) 2>/dev/null || git checkout parallel/e2e-$(date +%Y%m%d)
echo "✅ Branch 3: parallel/e2e-$(date +%Y%m%d) created"

git checkout main 2>/dev/null || git checkout master

# Branch 4: Documentation
git checkout -b parallel/docs-$(date +%Y%m%d) 2>/dev/null || git checkout parallel/docs-$(date +%Y%m%d)
echo "✅ Branch 4: parallel/docs-$(date +%Y%m%d) created"

# Create task assignment file
cat > .specify/memory/parallel-assignments.md << 'EOF'
# Parallel Claude Instance Assignments

## Instance 1: Backend Handler Fixes
- **Branch**: parallel/handlers-DATE
- **Tasks**: T001-T006
- **Files**:
  - backend/api/src/main/python/openapi_server/impl/family.py
  - backend/api/src/main/python/openapi_server/impl/users.py
  - backend/api/src/main/python/openapi_server/impl/animals.py
- **Prompt**: "I'm on branch parallel/handlers-DATE. Fix all handler forwarding issues in the impl modules. Tasks T001-T006 from .specify/memory/tasks.md"

## Instance 2: Test Coverage
- **Branch**: parallel/tests-DATE
- **Tasks**: T007-T012
- **Files**:
  - backend/api/src/main/python/openapi_server/test/
  - backend/api/src/main/python/tests/unit/
  - backend/api/src/main/python/tests/integration/
- **Prompt**: "I'm on branch parallel/tests-DATE. Generate unit and integration tests to reach 85% coverage. Tasks T007-T012 from .specify/memory/tasks.md"

## Instance 3: E2E Tests
- **Branch**: parallel/e2e-DATE
- **Tasks**: T013-T019
- **Files**:
  - backend/api/src/main/python/tests/playwright/
  - All test specs for 6 user roles
- **Prompt**: "I'm on branch parallel/e2e-DATE. Create Playwright E2E tests for all user roles. Tasks T013-T019 from .specify/memory/tasks.md"

## Instance 4: Documentation
- **Branch**: parallel/docs-DATE
- **Tasks**: T006, T020-T025
- **Files**:
  - FORWARDING-PATTERN.md
  - API documentation
  - README updates
- **Prompt**: "I'm on branch parallel/docs-DATE. Document patterns and create comprehensive docs. Tasks T006 and T020-T025 from .specify/memory/tasks.md"
EOF

# Replace DATE with actual date
sed -i '' "s/DATE/$(date +%Y%m%d)/g" .specify/memory/parallel-assignments.md

echo ""
echo "📋 Task assignments created in .specify/memory/parallel-assignments.md"
echo ""
echo "🌐 Now open 4 Claude instances:"
echo ""
echo "Option 1: Multiple Chrome Profiles"
echo "  open -na 'Google Chrome' --args --profile-directory='Claude-1' https://claude.ai"
echo "  open -na 'Google Chrome' --args --profile-directory='Claude-2' https://claude.ai"
echo "  open -na 'Google Chrome' --args --profile-directory='Claude-3' https://claude.ai"
echo "  open -na 'Google Chrome' --args --profile-directory='Claude-4' https://claude.ai"
echo ""
echo "Option 2: Different Browsers"
echo "  open -a 'Google Chrome' https://claude.ai"
echo "  open -a 'Safari' https://claude.ai"
echo "  open -a 'Firefox' https://claude.ai"
echo "  open -a 'Arc' https://claude.ai"
echo ""
echo "📝 Copy the prompts from .specify/memory/parallel-assignments.md to each instance"
echo ""
echo "✨ When all instances complete their work, run:"
echo "  ./scripts/merge_parallel_work.sh"