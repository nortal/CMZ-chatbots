#!/usr/bin/env python3
"""
Send Contract Validation Results to Teams
Reads validation results and formats as Adaptive Card for Teams notification

Usage:
    python3 scripts/send_contract_validation_to_teams.py validation-reports/teams_notification_data.json
"""

import os
import sys
import requests
import json
from datetime import datetime
from pathlib import Path


def send_contract_validation_to_teams(
    total_endpoints: int,
    aligned: int,
    partial: int,
    misaligned: int,
    handler_issues: dict,
    critical_mismatches: list
) -> int:
    """Send contract validation results to Teams using Adaptive Card format"""

    webhook_url = os.getenv('TEAMS_WEBHOOK_URL')
    if not webhook_url:
        print("⚠️ TEAMS_WEBHOOK_URL not set, skipping Teams notification")
        return 1

    # Determine overall status color
    if misaligned > 0:
        color = "Attention"  # Red
        status_emoji = "❌"
        status_text = "Contract Misalignments Detected"
    elif partial > 5:
        color = "Warning"  # Yellow
        status_emoji = "⚠️"
        status_text = "Partial Contract Alignment"
    else:
        color = "Good"  # Green
        status_emoji = "✅"
        status_text = "Contracts Aligned"

    # Calculate success rate
    success_rate = round((aligned / total_endpoints) * 100) if total_endpoints > 0 else 0

    # Build adaptive card body
    body = [
        {
            "type": "TextBlock",
            "text": f"{status_emoji} Contract Validation Report",
            "size": "Large",
            "weight": "Bolder",
            "wrap": True,
            "color": color
        },
        {
            "type": "TextBlock",
            "text": status_text,
            "size": "Medium",
            "wrap": True,
            "spacing": "None",
            "isSubtle": True
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
            "text": "📊 Contract Alignment Summary",
            "size": "Medium",
            "weight": "Bolder",
            "wrap": True,
            "spacing": "Medium"
        },
        {
            "type": "FactSet",
            "facts": [
                {"title": "Total Endpoints", "value": str(total_endpoints)},
                {"title": "✅ Fully Aligned", "value": f"{aligned} ({round(aligned/total_endpoints*100) if total_endpoints > 0 else 0}%)"},
                {"title": "⚠️ Partially Aligned", "value": f"{partial} ({round(partial/total_endpoints*100) if total_endpoints > 0 else 0}%)"},
                {"title": "❌ Misaligned", "value": f"{misaligned} ({round(misaligned/total_endpoints*100) if total_endpoints > 0 else 0}%)"},
                {"title": "Success Rate", "value": f"{success_rate}%"}
            ]
        },
        {
            "type": "TextBlock",
            "text": "🔍 Handler Validation Issues",
            "size": "Medium",
            "weight": "Bolder",
            "wrap": True,
            "spacing": "Medium"
        },
        {
            "type": "FactSet",
            "facts": [
                {"title": "Missing Required Checks", "value": str(handler_issues.get('missing_required', 0))},
                {"title": "No Type Validation", "value": str(handler_issues.get('no_type_validation', 0))},
                {"title": "Response Mismatches", "value": str(handler_issues.get('response_mismatch', 0))},
                {"title": "Proper Error Usage", "value": f"{handler_issues.get('proper_error_usage', 0)} handlers"}
            ]
        }
    ]

    # Add critical mismatches section if any
    if critical_mismatches:
        body.append({
            "type": "TextBlock",
            "text": "🔴 Critical Issues",
            "size": "Medium",
            "weight": "Bolder",
            "wrap": True,
            "spacing": "Medium",
            "color": "Attention"
        })

        issues_text = "\n".join([f"• {issue}" for issue in critical_mismatches[:5]])
        body.append({
            "type": "TextBlock",
            "text": issues_text,
            "wrap": True,
            "spacing": "Small"
        })

    # Add recommendations
    body.append({
        "type": "TextBlock",
        "text": "💡 Recommendations",
        "size": "Medium",
        "weight": "Bolder",
        "wrap": True,
        "spacing": "Medium"
    })

    recommendations = []
    if misaligned > 0:
        recommendations.append("Fix misaligned endpoints immediately")
    if handler_issues.get('missing_required', 0) > 0:
        recommendations.append("Add required field validation to handlers")
    if handler_issues.get('no_type_validation', 0) > 0:
        recommendations.append("Implement type checking in handlers")
    if success_rate < 80:
        recommendations.append("Add contract validation to CI/CD pipeline")

    if not recommendations:
        recommendations.append("No critical recommendations")

    recs_text = "\n".join([f"{i+1}. {rec}" for i, rec in enumerate(recommendations)])
    body.append({
        "type": "TextBlock",
        "text": recs_text,
        "wrap": True,
        "spacing": "Small"
    })

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
    print("📨 Sending contract validation report to Teams...")
    try:
        response = requests.post(
            webhook_url,
            json=card,
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        if response.status_code == 202:
            print("✅ Teams notification sent successfully")
            return 0
        else:
            print(f"❌ Failed to send Teams notification: {response.status_code}")
            print(f"Response: {response.text}")
            return 1
    except Exception as e:
        print(f"❌ Error sending Teams notification: {e}")
        return 1


def main():
    if len(sys.argv) < 2:
        print("Usage: send_contract_validation_to_teams.py <teams_notification_data.json>")
        return 1

    data_file = sys.argv[1]

    if not os.path.exists(data_file):
        print(f"❌ Data file not found: {data_file}")
        return 1

    with open(data_file) as f:
        data = json.load(f)

    return send_contract_validation_to_teams(
        total_endpoints=data['total_endpoints'],
        aligned=data['aligned'],
        partial=data['partial'],
        misaligned=data['misaligned'],
        handler_issues=data['handler_issues'],
        critical_mismatches=data['critical_mismatches']
    )


if __name__ == "__main__":
    sys.exit(main())
