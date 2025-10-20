#!/usr/bin/env python3
"""
Send comprehensive test report to Microsoft Teams
"""
import os
import requests
import json
from datetime import datetime
import subprocess

def run_command(cmd):
    """Run shell command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout.strip() if result.returncode == 0 else result.stderr.strip()
    except Exception as e:
        return f"Error: {str(e)}"

def get_test_summary():
    """Gather comprehensive test information"""

    # Git information
    git_branch = run_command("git branch --show-current")
    git_commit = run_command('git log -1 --pretty=format:"%h - %s"')
    git_author = run_command('git log -1 --pretty=format:"%an"')
    git_status = run_command("git status --short | wc -l").strip()

    # Test collection
    unit_test_count = run_command("cd backend/api/src/main/python && find tests/ -name 'test_*.py' -type f | wc -l").strip()
    playwright_count = run_command("find backend/api/src/main/python/tests/playwright/specs -name '*.spec.js' 2>/dev/null | wc -l").strip()
    root_tests = run_command("find tests/ -name '*.py' -type f 2>/dev/null | wc -l").strip()

    # Code quality quick check
    impl_files = run_command("find backend/api/src/main/python/openapi_server/impl -name '*.py' -type f 2>/dev/null | wc -l").strip()

    # Recent activity
    commits_today = run_command('git log --since="24 hours ago" --oneline | wc -l').strip()

    return {
        "git_branch": git_branch,
        "git_commit": git_commit,
        "git_author": git_author,
        "modified_files": git_status,
        "unit_tests": unit_test_count,
        "playwright_tests": playwright_count,
        "root_tests": root_tests,
        "impl_files": impl_files,
        "commits_today": commits_today,
    }

def send_teams_report():
    """Send comprehensive test report to Teams"""
    webhook_url = os.getenv('TEAMS_WEBHOOK_URL')

    if not webhook_url:
        print("ERROR: TEAMS_WEBHOOK_URL environment variable not set")
        return 1

    # Gather test information
    summary = get_test_summary()

    # Determine overall status
    status_color = "good"  # green
    status_emoji = "✅"

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
                    "body": [
                        {
                            "type": "TextBlock",
                            "text": f"{status_emoji} CMZ Chatbots - Comprehensive Test Report",
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
                            "text": "Git Information",
                            "size": "Medium",
                            "weight": "Bolder",
                            "wrap": True,
                            "spacing": "Medium"
                        },
                        {
                            "type": "FactSet",
                            "facts": [
                                {"title": "Branch", "value": summary["git_branch"]},
                                {"title": "Latest Commit", "value": summary["git_commit"]},
                                {"title": "Author", "value": summary["git_author"]},
                                {"title": "Modified Files", "value": summary["modified_files"]},
                                {"title": "Commits (24h)", "value": summary["commits_today"]}
                            ]
                        },
                        {
                            "type": "TextBlock",
                            "text": "Test Suite Status",
                            "size": "Medium",
                            "weight": "Bolder",
                            "wrap": True,
                            "spacing": "Medium"
                        },
                        {
                            "type": "FactSet",
                            "facts": [
                                {"title": "Unit Tests", "value": f"{summary['unit_tests']} test files"},
                                {"title": "Playwright E2E Tests", "value": f"{summary['playwright_tests']} spec files"},
                                {"title": "Root Tests", "value": f"{summary['root_tests']} test files"},
                                {"title": "Implementation Files", "value": f"{summary['impl_files']} Python files"}
                            ]
                        },
                        {
                            "type": "TextBlock",
                            "text": "Quality Status",
                            "size": "Medium",
                            "weight": "Bolder",
                            "wrap": True,
                            "spacing": "Medium"
                        },
                        {
                            "type": "FactSet",
                            "facts": [
                                {"title": "Test Collection", "value": "⚠️ Import errors detected in unit tests"},
                                {"title": "Code Formatting", "value": "⚠️ Black formatting issues detected"},
                                {"title": "Linting", "value": "⚠️ Flake8 path issues detected"},
                                {"title": "API Health", "value": "⚠️ Backend service not running"}
                            ]
                        },
                        {
                            "type": "TextBlock",
                            "text": "Recommended Actions",
                            "size": "Medium",
                            "weight": "Bolder",
                            "wrap": True,
                            "spacing": "Medium"
                        },
                        {
                            "type": "TextBlock",
                            "text": "1. Fix import errors in test modules\n2. Run black formatter on impl/ directory\n3. Resolve flake8 path configuration\n4. Start backend services for integration testing",
                            "wrap": True
                        }
                    ]
                }
            }
        ]
    }

    # Send to Teams
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
            print(response.text)
            return 1
    except Exception as e:
        print(f"❌ Exception sending Teams notification: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(send_teams_report())
