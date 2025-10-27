#!/bin/bash
# Contract Validation Suite Wrapper Script
# Orchestrates contract validation and Teams notification

set -e  # Exit on error

SESSION_ID="contract_val_$(date +%Y%m%d_%H%M%S)"
REPORT_DIR="validation-reports/$SESSION_ID"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== Contract Validation Suite ==="
echo "Session: $SESSION_ID"
echo "Report directory: $REPORT_DIR"
echo ""

# Create report directory
mkdir -p "$REPO_ROOT/$REPORT_DIR"

# Change to repo root for execution
cd "$REPO_ROOT"

# Run Python validation script
echo "🚀 Running contract validation..."
python3 scripts/validate_contracts.py \
  --openapi backend/api/openapi_spec.yaml \
  --ui frontend/src \
  --api backend/api/src/main/python/openapi_server/impl \
  --output "$REPORT_DIR/contract_report.md" \
  --report-format markdown

VALIDATION_EXIT_CODE=$?

echo ""
echo "📄 Report generated: $REPORT_DIR/contract_report.md"
echo ""

# Send results to Teams if webhook is configured
if [ -f "validation-reports/teams_notification_data.json" ]; then
  echo "📨 Sending results to Teams..."
  python3 scripts/send_contract_validation_to_teams.py validation-reports/teams_notification_data.json
  TEAMS_EXIT_CODE=$?

  if [ $TEAMS_EXIT_CODE -eq 0 ]; then
    echo "✅ Teams notification sent successfully"
  else
    echo "⚠️ Teams notification failed (non-fatal)"
  fi
else
  echo "⚠️ Teams notification data not found, skipping Teams notification"
fi

echo ""
echo "=== Validation Complete ==="
echo "Session ID: $SESSION_ID"
echo "Report: $REPORT_DIR/contract_report.md"
echo ""

# Exit with validation exit code
exit $VALIDATION_EXIT_CODE
