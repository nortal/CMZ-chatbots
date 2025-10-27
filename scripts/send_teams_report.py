#!/usr/bin/env python3
"""
Teams Reporting Agent - Delegatable Script
This script acts as an agent that can be delegated to for sending Teams notifications.
"""
import os
import sys
import json
import requests
from datetime import datetime
from pathlib import Path

def read_teams_webhook_advice():
    """Load Teams webhook formatting requirements"""
    advice_path = Path(__file__).parent.parent / "TEAMS-WEBHOOK-ADVICE.md"
    if advice_path.exists():
        with open(advice_path, 'r') as f:
            return f.read()
    return None

def get_status_emoji(success_rate: float) -> str:
    """Determine appropriate emoji based on success rate"""
    if success_rate >= 0.95:
        return "✅"  # Excellent
    elif success_rate >= 0.80:
        return "⚠️"   # Warning
    elif success_rate >= 0.60:
        return "❌"  # Critical
    else:
        return "🚨"  # Emergency

def format_test_results(data: dict) -> dict:
    """Format test execution results for Teams adaptive card"""
    total = data.get('total', 0)
    passed = data.get('passed', 0)
    failed = data.get('failed', 0)
    success_rate = (passed / total * 100) if total > 0 else 0

    sections = [
        {
            "title": "Execution Summary",
            "facts": [
                {"title": "Total Tests", "value": str(total)},
                {"title": "Passed", "value": f"✅ {passed}"},
                {"title": "Failed", "value": f"❌ {failed}"},
                {"title": "Success Rate", "value": f"{success_rate:.1f}%"},
                {"title": "Duration", "value": data.get('duration', 'N/A')}
            ]
        }
    ]

    # Add quality gates if present
    if 'quality_gates' in data:
        quality_facts = []
        for gate, status in data['quality_gates'].items():
            quality_facts.append({"title": gate, "value": status})
        sections.append({
            "title": "Quality Gates",
            "facts": quality_facts
        })

    # Add git information if present
    if any(key in data for key in ['branch', 'commit', 'author']):
        git_facts = []
        if 'branch' in data:
            git_facts.append({"title": "Branch", "value": data['branch']})
        if 'commit' in data:
            git_facts.append({"title": "Commit", "value": data['commit']})
        if 'author' in data:
            git_facts.append({"title": "Author", "value": data['author']})
        sections.append({
            "title": "Git Information",
            "facts": git_facts
        })

    return {
        "title": f"{get_status_emoji(success_rate)} Test Suite Execution Report",
        "sections": sections,
        "actions": data.get('actions', [])
    }

def format_validation_results(data: dict) -> dict:
    """Format validation suite results for Teams adaptive card"""
    tested = data.get('tested', 0)
    total = data.get('total', 0)
    coverage = (tested / total * 100) if total > 0 else 0

    sections = [
        {
            "title": "Validation Coverage",
            "facts": [
                {"title": "Session ID", "value": data.get('session_id', 'N/A')},
                {"title": "Endpoints Tested", "value": f"{tested}/{total} ({coverage:.1f}%)"},
                {"title": "Duration", "value": data.get('duration', 'N/A')}
            ]
        }
    ]

    # Add priority results if present
    if 'priorities' in data:
        priority_facts = []
        for priority, status in data['priorities'].items():
            priority_facts.append({"title": priority, "value": status})
        sections.append({
            "title": "Results by Priority",
            "facts": priority_facts
        })

    return {
        "title": f"{data.get('status_emoji', '✅')} Comprehensive Validation Report",
        "sections": sections,
        "actions": data.get('actions', [])
    }

def format_custom_report(data: dict) -> dict:
    """Format custom report for Teams adaptive card"""
    return {
        "title": data.get('title', '📊 Custom Report'),
        "sections": data.get('sections', []),
        "actions": data.get('actions', [])
    }

def build_adaptive_card(title: str, sections: list, actions: list = None) -> dict:
    """Build Microsoft Adaptive Card structure"""
    body = [
        {
            "type": "TextBlock",
            "text": title,
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
        }
    ]

    # Add sections
    for section in sections:
        body.append({
            "type": "TextBlock",
            "text": section['title'],
            "size": "Medium",
            "weight": "Bolder",
            "wrap": True,
            "spacing": "Medium"
        })

        if 'facts' in section:
            body.append({
                "type": "FactSet",
                "facts": section['facts']
            })

    # Add action items if present
    if actions:
        body.append({
            "type": "TextBlock",
            "text": "Recommended Actions",
            "size": "Medium",
            "weight": "Bolder",
            "wrap": True,
            "spacing": "Medium"
        })

        action_text = "\n".join(f"{i+1}. {action}" for i, action in enumerate(actions))
        body.append({
            "type": "TextBlock",
            "text": action_text,
            "wrap": True
        })

    return {
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

def send_teams_message(card: dict, webhook_url: str = None) -> int:
    """Send adaptive card to Teams webhook"""
    if not webhook_url:
        webhook_url = os.getenv('TEAMS_WEBHOOK_URL')

    if not webhook_url:
        print("❌ ERROR: TEAMS_WEBHOOK_URL environment variable not set")
        print("Export webhook URL: export TEAMS_WEBHOOK_URL=\"...\"")
        return 1

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
            print(f"❌ Failed to send Teams notification: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return 1

    except requests.exceptions.Timeout:
        print("❌ Request timeout - Teams webhook not responding")
        return 1

    except Exception as e:
        print(f"❌ Exception sending Teams notification: {str(e)}")
        return 1

def main():
    """Main entry point for Teams reporting agent"""
    if len(sys.argv) < 2:
        print("Usage: send_teams_report.py <report-type> [--data file.json] [--title 'Custom Title']")
        print("\nReport Types:")
        print("  test-results   - Test suite execution results")
        print("  validation     - Comprehensive validation results")
        print("  custom         - Custom report with user data")
        print("\nExample:")
        print("  send_teams_report.py test-results --data results.json")
        return 1

    report_type = sys.argv[1]
    data = {}
    custom_title = None

    # Parse arguments
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--data' and i + 1 < len(sys.argv):
            data_file = sys.argv[i + 1]
            with open(data_file, 'r') as f:
                data = json.load(f)
            i += 2
        elif sys.argv[i] == '--title' and i + 1 < len(sys.argv):
            custom_title = sys.argv[i + 1]
            i += 2
        else:
            i += 1

    # Format based on report type
    if report_type == 'test-results':
        formatted = format_test_results(data)
    elif report_type == 'validation':
        formatted = format_validation_results(data)
    elif report_type == 'custom':
        formatted = format_custom_report(data)
    else:
        print(f"❌ Unknown report type: {report_type}")
        return 1

    # Override title if provided
    if custom_title:
        formatted['title'] = custom_title

    # Build adaptive card
    card = build_adaptive_card(
        formatted['title'],
        formatted['sections'],
        formatted.get('actions')
    )

    # Send to Teams
    return send_teams_message(card)

if __name__ == "__main__":
    sys.exit(main())
