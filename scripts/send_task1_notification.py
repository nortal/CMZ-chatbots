#!/usr/bin/env python3
"""Send Teams notification for Task 1 completion"""

import os
import sys
import requests
import json

def send_teams_notification():
    """Send Teams notification about Task 1 completion"""

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
                        "text": "Contract Validation - Task 1 Complete ✅",
                        "size": "Large",
                        "weight": "Bolder",
                        "color": "Good"
                    },
                    {
                        "type": "FactSet",
                        "facts": [
                            {
                                "title": "Task",
                                "value": "Add systemPrompt to OpenAPI spec"
                            },
                            {
                                "title": "Status",
                                "value": "✅ COMPLETED"
                            },
                            {
                                "title": "Time Required",
                                "value": "5 minutes (as estimated)"
                            },
                            {
                                "title": "Change Made",
                                "value": "Added systemPrompt field to AnimalConfigUpdate schema"
                            },
                            {
                                "title": "File Modified",
                                "value": "backend/api/openapi_spec.yaml (lines 2852-2857)"
                            },
                            {
                                "title": "Remaining Tasks",
                                "value": "3, 4, 5 in progress | 2 pending (do last)"
                            }
                        ]
                    },
                    {
                        "type": "TextBlock",
                        "text": "**Details:**",
                        "weight": "Bolder",
                        "spacing": "Medium"
                    },
                    {
                        "type": "TextBlock",
                        "text": "Successfully added systemPrompt field to AnimalConfigUpdate schema with proper validation constraints:\n\n• Type: string\n• Min length: 5 characters\n• Max length: 2000 characters\n• Pattern: Natural language with punctuation support\n• Description: System prompt that defines the AI behavior for this animal",
                        "wrap": True
                    },
                    {
                        "type": "TextBlock",
                        "text": "**Next Steps:**",
                        "weight": "Bolder",
                        "spacing": "Medium"
                    },
                    {
                        "type": "TextBlock",
                        "text": "• Task 3: Implement Prevention Phase 1 (starting now)\n• Task 4: Backend validation hardening\n• Task 5: Scanner improvements\n• Task 2: Create meeting agenda (will do last)",
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
