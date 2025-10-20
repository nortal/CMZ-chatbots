#!/usr/bin/env python3
"""
Send comprehensive validation report to Teams
"""
import os
import requests
import json
from datetime import datetime

def send_validation_report():
    """Send validation results to Teams channel"""
    webhook_url = os.getenv('TEAMS_WEBHOOK_URL')

    if not webhook_url:
        print("❌ TEAMS_WEBHOOK_URL environment variable not set")
        return 1

    # Build the adaptive card with multiple sections
    body = [
        {
            "type": "TextBlock",
            "text": "🔍 CMZ Comprehensive Validation Report",
            "size": "Large",
            "weight": "Bolder",
            "wrap": True
        },
        {
            "type": "TextBlock",
            "text": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "size": "Small",
            "isSubtle": True,
            "wrap": True
        },
        {
            "type": "TextBlock",
            "text": "📊 Test Results Summary",
            "size": "Medium",
            "weight": "Bolder",
            "wrap": True,
            "spacing": "Medium"
        },
        {
            "type": "FactSet",
            "facts": [
                {"title": "Session ID", "value": "val_20251010_123732"},
                {"title": "Branch", "value": "feature/code-review-fixes-20251010"},
                {"title": "Total Tests", "value": "12"},
                {"title": "Passed", "value": "7 ✅"},
                {"title": "Failed", "value": "4 ❌"},
                {"title": "Skipped", "value": "1 ⚠️"},
                {"title": "Success Rate", "value": "58%"},
                {"title": "Duration", "value": "~5 minutes"}
            ]
        },
        {
            "type": "TextBlock",
            "text": "🏗️ Infrastructure Status",
            "size": "Medium",
            "weight": "Bolder",
            "wrap": True,
            "spacing": "Medium"
        },
        {
            "type": "FactSet",
            "facts": [
                {"title": "Backend API", "value": "✅ Healthy (port 8080)"},
                {"title": "Frontend", "value": "✅ Accessible (port 3001)"},
                {"title": "DynamoDB", "value": "✅ Connected (10 tables)"},
                {"title": "AWS Config", "value": "✅ Valid (cmz profile)"},
                {"title": "Overall", "value": "✅ INFRASTRUCTURE HEALTHY"}
            ]
        },
        {
            "type": "TextBlock",
            "text": "🧪 Test Categories",
            "size": "Medium",
            "weight": "Bolder",
            "wrap": True,
            "spacing": "Medium"
        },
        {
            "type": "FactSet",
            "facts": [
                {"title": "Infrastructure Tests", "value": "3/4 passed"},
                {"title": "Animal Config Tests", "value": "0/3 passed (wrong HTTP method)"},
                {"title": "Family Mgmt Tests", "value": "1/2 passed"},
                {"title": "Data Persistence Tests", "value": "1/3 passed"}
            ]
        },
        {
            "type": "TextBlock",
            "text": "💡 Key Findings",
            "size": "Medium",
            "weight": "Bolder",
            "wrap": True,
            "spacing": "Medium"
        },
        {
            "type": "TextBlock",
            "text": "• Infrastructure is healthy and operational\n• Test failures due to test suite issues, not app problems\n• AWS CLI returning YAML instead of JSON (add --output json)\n• Wrong HTTP methods used in tests (GET vs POST)\n• Tables exist but are empty (need seed data)\n• Test users missing (need initialization)",
            "wrap": True,
            "spacing": "Small"
        },
        {
            "type": "TextBlock",
            "text": "🎯 Assessment",
            "size": "Medium",
            "weight": "Bolder",
            "wrap": True,
            "spacing": "Medium"
        },
        {
            "type": "FactSet",
            "facts": [
                {"title": "Application Status", "value": "✅ OPERATIONAL"},
                {"title": "Test Suite Status", "value": "⚠️ NEEDS REFINEMENT"},
                {"title": "Recommendation", "value": "Fix test infrastructure and re-run"}
            ]
        },
        {
            "type": "TextBlock",
            "text": "📄 Full Report",
            "size": "Medium",
            "weight": "Bolder",
            "wrap": True,
            "spacing": "Medium"
        },
        {
            "type": "TextBlock",
            "text": "validation-reports/val_20251010_123732/VALIDATION_REPORT.md",
            "wrap": True,
            "fontType": "Monospace",
            "spacing": "Small"
        }
    ]

    # Create adaptive card
    card = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.4",
                    "body": body
                }
            }
        ]
    }

    # Send to Teams
    print("Sending validation report to Teams...")
    response = requests.post(
        webhook_url,
        json=card,
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 202:
        print("✅ Teams notification sent successfully")
        print(f"   Status code: {response.status_code}")
        return 0
    else:
        print(f"❌ Failed to send Teams notification")
        print(f"   Status code: {response.status_code}")
        print(f"   Response: {response.text}")
        return 1

if __name__ == "__main__":
    exit(send_validation_report())
