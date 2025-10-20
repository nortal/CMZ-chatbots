#!/usr/bin/env python3
"""
Send FINAL comprehensive validation report to Teams
Based on ENDPOINT-WORK.md testing
"""
import os
import requests
from datetime import datetime

def send_final_report():
    """Send final corrected validation results"""
    webhook_url = os.getenv('TEAMS_WEBHOOK_URL')

    if not webhook_url:
        print("❌ TEAMS_WEBHOOK_URL not set")
        return 1

    body = [
        {
            "type": "TextBlock",
            "text": "✅ ACTUAL Comprehensive CMZ Validation",
            "size": "Large",
            "weight": "Bolder",
            "wrap": True,
            "color": "Good"
        },
        {
            "type": "TextBlock",
            "text": datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " - Based on ENDPOINT-WORK.md",
            "size": "Small",
            "isSubtle": True,
            "wrap": True
        },
        {
            "type": "TextBlock",
            "text": "📊 Actual Test Coverage",
            "size": "Medium",
            "weight": "Bolder",
            "wrap": True,
            "spacing": "Medium"
        },
        {
            "type": "FactSet",
            "facts": [
                {"title": "Documented Endpoints", "value": "37 (from ENDPOINT-WORK.md)"},
                {"title": "Tested", "value": "19 endpoints (51%)"},
                {"title": "Passed", "value": "12/19 (63%)"},
                {"title": "Failed", "value": "7/19 (37%)"}
            ]
        },
        {
            "type": "TextBlock",
            "text": "✅ Category Results",
            "size": "Medium",
            "weight": "Bolder",
            "wrap": True,
            "spacing": "Medium",
            "color": "Good"
        },
        {
            "type": "FactSet",
            "facts": [
                {"title": "Authentication", "value": "4/4 ✅ (100%)"},
                {"title": "System Health", "value": "1/1 ✅ (100%)"},
                {"title": "Guardrails", "value": "2/2 ✅ (100% - limited)"},
                {"title": "User Mgmt", "value": "1/1 ✅ (100% - limited)"},
                {"title": "Animal Mgmt", "value": "3/7 ⚠️ (43%)"},
                {"title": "Family Mgmt", "value": "1/2 ⚠️ (50% - limited)"},
                {"title": "UI Endpoints", "value": "0/2 ❌ (0%)"}
            ]
        },
        {
            "type": "TextBlock",
            "text": "🔍 What This Validation Found",
            "size": "Medium",
            "weight": "Bolder",
            "wrap": True,
            "spacing": "Medium"
        },
        {
            "type": "TextBlock",
            "text": "• Authentication FULLY FUNCTIONAL (100%)\n• Animal reads working (list, get)\n• Animal writes FAILING (PUT/POST 500 errors)\n• UI endpoints NOT IMPLEMENTED (501) despite docs claiming otherwise\n• Guardrails, Users, Family basic operations working",
            "wrap": True,
            "spacing": "Small"
        },
        {
            "type": "TextBlock",
            "text": "🔴 Critical Documentation Error",
            "size": "Medium",
            "weight": "Bolder",
            "wrap": True,
            "spacing": "Medium",
            "color": "Attention"
        },
        {
            "type": "TextBlock",
            "text": "ENDPOINT-WORK.md claims GET / and GET /admin are implemented, but both return 501 Not Implemented. Documentation needs updating.",
            "wrap": True,
            "spacing": "Small"
        },
        {
            "type": "TextBlock",
            "text": "📈 Improvement Over Previous Validation",
            "size": "Medium",
            "weight": "Bolder",
            "wrap": True,
            "spacing": "Medium"
        },
        {
            "type": "FactSet",
            "facts": [
                {"title": "Previous Coverage", "value": "7% (wrong endpoints)"},
                {"title": "Current Coverage", "value": "51% (correct endpoints)"},
                {"title": "Previous Methodology", "value": "Guessed endpoint paths"},
                {"title": "Current Methodology", "value": "Used ENDPOINT-WORK.md"},
                {"title": "Key Discovery", "value": "Auth is 100% functional!"}
            ]
        },
        {
            "type": "TextBlock",
            "text": "🎯 Recommendations",
            "size": "Medium",
            "weight": "Bolder",
            "wrap": True,
            "spacing": "Medium"
        },
        {
            "type": "TextBlock",
            "text": "1. Fix UI endpoints (GET /, GET /admin)\n2. Debug animal write operations (500 errors)\n3. Test remaining 18 untested endpoints\n4. Update ENDPOINT-WORK.md to match reality\n5. Investigate animal_config auth issues",
            "wrap": True,
            "spacing": "Small"
        },
        {
            "type": "TextBlock",
            "text": "📄 Reports",
            "size": "Medium",
            "weight": "Bolder",
            "wrap": True,
            "spacing": "Medium"
        },
        {
            "type": "TextBlock",
            "text": "• validation-reports/val_20251010_123732/ACTUAL_COMPREHENSIVE_REPORT.md\n• validation-reports/val_20251010_123732/ENDPOINT_WORK_COMPARISON.md\n• validation-reports/val_20251010_123732/comprehensive_results.jsonl",
            "wrap": True,
            "fontType": "Monospace",
            "spacing": "Small"
        }
    ]

    card = {
        "type": "message",
        "attachments": [{
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": {
                "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                "type": "AdaptiveCard",
                "version": "1.4",
                "body": body
            }
        }]
    }

    print("Sending final comprehensive validation report to Teams...")
    response = requests.post(webhook_url, json=card, headers={"Content-Type": "application/json"})

    if response.status_code == 202:
        print("✅ Final report sent successfully")
        return 0
    else:
        print(f"❌ Failed: {response.status_code}")
        print(response.text)
        return 1

if __name__ == "__main__":
    exit(send_final_report())
