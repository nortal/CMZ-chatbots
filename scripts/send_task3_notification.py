#!/usr/bin/env python3
"""Send Teams notification for Task 3 completion"""

import os
import sys
import requests
import json

def send_teams_notification():
    """Send Teams notification about Task 3 completion"""

    webhook_url = os.getenv('TEAMS_WEBHOOK_URL')

    if not webhook_url:
        print("ERROR: TEAMS_WEBHOOK_URL environment variable not set")
        sys.exit(1)

    # Create Adaptive Card payload
    card = {
        "type": "message",
        "attachments": [{
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": {
                "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                "type": "AdaptiveCard",
                "version": "1.4",
                "body": [
                    {
                        "type": "TextBlock",
                        "text": "Contract Validation - Task 3 Complete ✅",
                        "size": "Large",
                        "weight": "Bolder",
                        "color": "Good"
                    },
                    {
                        "type": "FactSet",
                        "facts": [
                            {
                                "title": "Task",
                                "value": "Prevention Phase 1 Implementation"
                            },
                            {
                                "title": "Status",
                                "value": "✅ COMPLETED"
                            },
                            {
                                "title": "Subtasks Completed",
                                "value": "4/4 (Pre-commit hooks, CI/CD, Type generation, Documentation)"
                            },
                            {
                                "title": "Time Required",
                                "value": "Foundation established (full rollout: 2-3 days)"
                            },
                            {
                                "title": "Remaining Tasks",
                                "value": "5 (scanner), 4 (validation), 2 (meeting agenda)"
                            }
                        ]
                    },
                    {
                        "type": "TextBlock",
                        "text": "**Components Delivered:**",
                        "weight": "Bolder",
                        "spacing": "Medium"
                    },
                    {
                        "type": "TextBlock",
                        "text": "✅ **Pre-Commit Hooks**\n• scripts/hooks/pre-commit-contract-validation\n• scripts/setup_contract_validation_hooks.sh\n• Runs contract validation before every commit\n• Blocks commits with contract violations\n\n✅ **CI/CD Integration**\n• .github/workflows/contract-validation.yml\n• Validates on PR and main/dev pushes\n• Posts results to PR comments\n• Blocks merge if critical issues found\n\n✅ **TypeScript Type Generation**\n• Added openapi-typescript to frontend/package.json\n• npm run generate-types command\n• Generates frontend/src/api/types.ts from OpenAPI spec\n• Ensures compile-time contract validation\n\n✅ **Documentation**\n• docs/PREVENTION-PHASE-1-SETUP.md\n• Installation instructions\n• Usage examples\n• Troubleshooting guide",
                        "wrap": True
                    },
                    {
                        "type": "TextBlock",
                        "text": "**Next Actions:**",
                        "weight": "Bolder",
                        "spacing": "Medium"
                    },
                    {
                        "type": "TextBlock",
                        "text": "• Task 5: Scanner improvements (AST parsing, call graph analysis)\n• Task 4: Backend validation hardening (decorators, contract tests)\n• Task 2: Create meeting agenda for unused fields decision",
                        "wrap": True
                    },
                    {
                        "type": "TextBlock",
                        "text": "**Team Rollout Required:**",
                        "weight": "Bolder",
                        "spacing": "Medium",
                        "color": "Attention"
                    },
                    {
                        "type": "TextBlock",
                        "text": "All developers should install pre-commit hooks:\n```bash\n./scripts/setup_contract_validation_hooks.sh\n```",
                        "wrap": True
                    }
                ]
            }
        }]
    }

    try:
        response = requests.post(webhook_url, json=card, timeout=10)

        if response.status_code == 202:
            print("✅ Teams notification sent successfully")
            return True
        else:
            print(f"❌ Teams notification failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error sending Teams notification: {str(e)}")
        return False

if __name__ == "__main__":
    success = send_teams_notification()
    sys.exit(0 if success else 1)
