#!/bin/bash
"""
TDD Reporting Git Hook Setup
Sets up post-merge git hook for automatic TDD reporting to Teams

Follows proven patterns from existing CMZ infrastructure and /nextfive implementations.
"""

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🎯 Setting up TDD Reporting Git Hook...${NC}"

# Get the repository root
REPO_ROOT=$(git rev-parse --show-toplevel)
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Not in a git repository${NC}"
    exit 1
fi

HOOKS_DIR="$REPO_ROOT/.git/hooks"
POST_MERGE_HOOK="$HOOKS_DIR/post-merge"
SCRIPTS_DIR="$REPO_ROOT/scripts"

echo -e "${BLUE}📍 Repository root: $REPO_ROOT${NC}"
echo -e "${BLUE}📍 Hooks directory: $HOOKS_DIR${NC}"

# Check if scripts directory exists
if [ ! -d "$SCRIPTS_DIR" ]; then
    echo -e "${RED}❌ Scripts directory not found: $SCRIPTS_DIR${NC}"
    exit 1
fi

# Check if TDD reporting scripts exist
REQUIRED_SCRIPTS=(
    "run_tdd_reporting.py"
    "tdd_config.py"
    "tdd_metrics_collector.py"
    "teams_tdd_reporter.py"
)

for script in "${REQUIRED_SCRIPTS[@]}"; do
    if [ ! -f "$SCRIPTS_DIR/$script" ]; then
        echo -e "${RED}❌ Required script not found: $SCRIPTS_DIR/$script${NC}"
        exit 1
    fi
done

echo -e "${GREEN}✅ All required TDD reporting scripts found${NC}"

# Create the post-merge hook
echo -e "${BLUE}📝 Creating post-merge hook...${NC}"

cat > "$POST_MERGE_HOOK" << 'EOF'
#!/bin/bash
#
# TDD Reporting Post-Merge Hook
# Automatically generates TDD improvement reports for Teams
#
# This hook runs after every successful merge to track TDD improvements
# following the proven patterns from /nextfive implementations.
#

# Exit on error but don't fail the merge if reporting fails
set +e

# Get the directory where this hook resides
HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$HOOK_DIR/../.." && pwd)"
SCRIPTS_DIR="$REPO_ROOT/scripts"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo -e "${GREEN}🎯 TDD Reporting Hook Triggered${NC}"

# Check if we're on the dev branch (following /nextfive pattern)
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null)

if [ "$CURRENT_BRANCH" != "dev" ]; then
    echo -e "${YELLOW}ℹ️ Skipping TDD reporting - not on dev branch (current: $CURRENT_BRANCH)${NC}"
    exit 0
fi

# Check if this was a merge commit
MERGE_COMMIT=$(git log --merges -1 --pretty=format:"%h %s" 2>/dev/null)

if [ -z "$MERGE_COMMIT" ]; then
    echo -e "${YELLOW}ℹ️ Skipping TDD reporting - no recent merge detected${NC}"
    exit 0
fi

echo -e "${GREEN}📊 Generating TDD improvement report for merge: $MERGE_COMMIT${NC}"

# Run TDD reporting in background to avoid blocking
{
    cd "$REPO_ROOT"

    # Set up environment for Python scripts
    export PYTHONPATH="$SCRIPTS_DIR:$PYTHONPATH"

    # Run TDD reporting with error handling
    if command -v python3 >/dev/null 2>&1; then
        python3 "$SCRIPTS_DIR/run_tdd_reporting.py" >> /tmp/tdd_reporting.log 2>&1
        RESULT=$?
    else
        python "$SCRIPTS_DIR/run_tdd_reporting.py" >> /tmp/tdd_reporting.log 2>&1
        RESULT=$?
    fi

    if [ $RESULT -eq 0 ]; then
        echo -e "${GREEN}✅ TDD report posted to Teams successfully${NC}"
    else
        echo -e "${RED}❌ TDD reporting failed (see /tmp/tdd_reporting.log for details)${NC}"
        echo -e "${YELLOW}ℹ️ This does not affect your merge - TDD reporting is supplementary${NC}"
    fi

} &

echo -e "${GREEN}🚀 TDD reporting started in background${NC}"
echo ""

# Exit successfully - don't fail the merge if reporting has issues
exit 0
EOF

# Make the hook executable
chmod +x "$POST_MERGE_HOOK"

echo -e "${GREEN}✅ Post-merge hook created and made executable${NC}"

# Check for existing hook
if [ -f "$POST_MERGE_HOOK.backup" ]; then
    echo -e "${YELLOW}⚠️ Found existing hook backup at $POST_MERGE_HOOK.backup${NC}"
    echo -e "${YELLOW}ℹ️ Previous hook was backed up before installation${NC}"
fi

# Test the hook setup
echo -e "${BLUE}🧪 Testing hook setup...${NC}"

# Verify hook is executable
if [ -x "$POST_MERGE_HOOK" ]; then
    echo -e "${GREEN}✅ Hook is executable${NC}"
else
    echo -e "${RED}❌ Hook is not executable${NC}"
    exit 1
fi

# Verify Python environment
echo -e "${BLUE}🐍 Checking Python environment...${NC}"

cd "$REPO_ROOT"
export PYTHONPATH="$SCRIPTS_DIR:$PYTHONPATH"

if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
else
    echo -e "${RED}❌ Python not found${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Found Python: $PYTHON_CMD${NC}"

# Test import of TDD modules
echo -e "${BLUE}📦 Testing TDD module imports...${NC}"

$PYTHON_CMD -c "
import sys
sys.path.insert(0, '$SCRIPTS_DIR')
try:
    from tdd_config import TDDConfigManager
    from tdd_metrics_collector import TDDMetricsCollector
    from teams_tdd_reporter import TeamsTDDReporter
    print('✅ All TDD modules imported successfully')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ TDD modules can be imported${NC}"
else
    echo -e "${RED}❌ TDD module import failed${NC}"
    exit 1
fi

# Installation complete
echo ""
echo -e "${GREEN}🎉 TDD Reporting Git Hook Setup Complete!${NC}"
echo ""
echo -e "${BLUE}📋 Next Steps:${NC}"
echo -e "1. Set required environment variables:"
echo -e "   export JIRA_API_TOKEN=your_token"
echo -e "   export JIRA_EMAIL=kc.stegbauer@nortal.com"
echo -e "   export GITHUB_TOKEN=your_token"
echo -e "   export TEAMS_WEBHOOK_URL=your_webhook_url"
echo ""
echo -e "2. Test the setup manually:"
echo -e "   cd $REPO_ROOT"
echo -e "   python3 scripts/run_tdd_reporting.py --test"
echo ""
echo -e "3. The hook will automatically run after merges to the dev branch"
echo ""
echo -e "${YELLOW}💡 Tip: Check /tmp/tdd_reporting.log for detailed logging${NC}"
echo ""