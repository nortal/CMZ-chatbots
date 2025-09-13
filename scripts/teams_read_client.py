#!/usr/bin/env python3
"""
Teams Read Client
Enhanced Graph client with channel reading capabilities
"""

import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

from teams_graph_client import TeamsGraphClient, load_teams_config

class TeamsReadClient(TeamsGraphClient):
    """Extended Teams client with read capabilities."""

    def __init__(self, config):
        super().__init__(config)

    def get_recent_messages(self, hours_back: int = 24, limit: int = 50) -> List[Dict]:
        """Get recent messages from the Teams channel."""
        if not self.access_token:
            if not self.authenticate():
                return []

        self.logger.info(f"📖 Reading recent messages from Teams channel (last {hours_back} hours)...")

        messages_url = f"https://graph.microsoft.com/v1.0/teams/{self.config.team_id}/channels/{self.config.channel_id}/messages"

        # Add query parameters
        params = {
            '$top': limit,
            '$orderby': 'createdDateTime desc',
            '$expand': 'replies'
        }

        # Filter by time if specified
        if hours_back:
            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            # Graph API filter format
            time_filter = cutoff_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            params['$filter'] = f"createdDateTime gt {time_filter}"

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.get(messages_url, headers=headers, params=params, timeout=30)

            if response.status_code == 200:
                messages = response.json().get('value', [])
                self.logger.info(f"✅ Retrieved {len(messages)} messages")
                return messages
            else:
                self.logger.error(f"❌ Failed to get messages: HTTP {response.status_code}")
                self.logger.error(f"Response: {response.text}")
                return []

        except Exception as e:
            self.logger.error(f"❌ Error getting messages: {e}")
            return []

    def get_tdd_analysis_messages(self, hours_back: int = 24) -> List[Dict]:
        """Get TDD analysis related messages."""
        all_messages = self.get_recent_messages(hours_back)

        # Filter for TDD-related messages
        tdd_keywords = ['tdd', 'coverage', 'test', 'analysis', 'chart', 'requirement']
        tdd_messages = []

        for message in all_messages:
            content = message.get('body', {}).get('content', '').lower()
            if any(keyword in content for keyword in tdd_keywords):
                tdd_messages.append(message)

        self.logger.info(f"📊 Found {len(tdd_messages)} TDD-related messages")
        return tdd_messages

    def analyze_posted_content(self, hours_back: int = 2) -> Dict:
        """Analyze what TDD content has been posted recently."""
        messages = self.get_tdd_analysis_messages(hours_back)

        analysis = {
            'total_messages': len(messages),
            'chart_posts': 0,
            'text_posts': 0,
            'success_rate_posts': 0,
            'requirements_posts': 0,
            'coverage_posts': 0,
            'latest_post_time': None,
            'message_summaries': []
        }

        for message in messages:
            content = message.get('body', {}).get('content', '')
            created_time = message.get('createdDateTime', '')

            # Update latest post time
            if not analysis['latest_post_time'] or created_time > analysis['latest_post_time']:
                analysis['latest_post_time'] = created_time

            # Categorize message content
            content_lower = content.lower()

            if 'chart' in content_lower or '📊' in content:
                analysis['chart_posts'] += 1
            if 'success rate' in content_lower or 'test result' in content_lower:
                analysis['success_rate_posts'] += 1
            if 'requirement' in content_lower or 'sequential' in content_lower:
                analysis['requirements_posts'] += 1
            if 'coverage' in content_lower:
                analysis['coverage_posts'] += 1

            # Check if it has attachments (indicating charts/images)
            has_attachments = len(message.get('attachments', [])) > 0
            if has_attachments:
                analysis['chart_posts'] += 1
            else:
                analysis['text_posts'] += 1

            # Create summary
            summary = {
                'time': created_time,
                'preview': content[:100] + '...' if len(content) > 100 else content,
                'has_attachments': has_attachments,
                'author': message.get('from', {}).get('user', {}).get('displayName', 'Unknown')
            }
            analysis['message_summaries'].append(summary)

        return analysis

    def verify_tdd_posting_success(self) -> Dict:
        """Verify that TDD analysis was posted successfully."""
        self.logger.info("🔍 Verifying TDD posting success...")

        # Check last 2 hours for our posts
        analysis = self.analyze_posted_content(hours_back=2)

        verification = {
            'success': False,
            'charts_posted': analysis['chart_posts'] > 0,
            'coverage_analysis_posted': analysis['coverage_posts'] > 0,
            'requirements_posted': analysis['requirements_posts'] > 0,
            'success_rates_posted': analysis['success_rate_posts'] > 0,
            'total_posts': analysis['total_messages'],
            'latest_post': analysis['latest_post_time'],
            'summary': []
        }

        # Determine overall success
        verification['success'] = (
            verification['charts_posted'] and
            verification['coverage_analysis_posted'] and
            analysis['total_messages'] >= 3  # Expect at least 3 posts for complete analysis
        )

        # Create summary
        if verification['success']:
            verification['summary'].append("✅ TDD analysis successfully posted to Teams")
        else:
            verification['summary'].append("⚠️ TDD analysis posting may be incomplete")

        verification['summary'].append(f"📊 Found {analysis['total_messages']} TDD-related messages")

        if analysis['chart_posts'] > 0:
            verification['summary'].append(f"📈 {analysis['chart_posts']} chart posts detected")

        if analysis['latest_post_time']:
            verification['summary'].append(f"⏰ Latest post: {analysis['latest_post_time']}")

        return verification

    def create_posting_report(self) -> str:
        """Create a report of what was posted."""
        verification = self.verify_tdd_posting_success()
        analysis = self.analyze_posted_content(hours_back=2)

        report = f"""📋 **TDD Teams Posting Verification Report**

🎯 **Overall Status**: {'✅ SUCCESS' if verification['success'] else '⚠️ INCOMPLETE'}

📊 **Content Analysis:**
• Total TDD Messages: {analysis['total_messages']}
• Chart Posts: {analysis['chart_posts']}
• Text Posts: {analysis['text_posts']}
• Coverage Posts: {analysis['coverage_posts']}
• Requirements Posts: {analysis['requirements_posts']}
• Success Rate Posts: {analysis['success_rate_posts']}

⏰ **Timing:**
• Latest Post: {analysis['latest_post_time'] or 'None found'}
• Search Window: Last 2 hours

📋 **Recent Messages Summary:**"""

        for i, msg in enumerate(analysis['message_summaries'][:3], 1):
            report += f"\n{i}. [{msg['time']}] {msg['preview']}"
            if msg['has_attachments']:
                report += " 📎"

        return report

def test_read_client():
    """Test the Teams read client."""
    config = load_teams_config()
    if not config:
        print("❌ Teams configuration not found")
        return False

    client = TeamsReadClient(config)

    # Test reading messages
    print("🧪 Testing Teams channel reading...")
    messages = client.get_recent_messages(hours_back=24, limit=10)

    if messages:
        print(f"✅ Successfully read {len(messages)} messages")

        # Show verification report
        print("\n" + client.create_posting_report())
        return True
    else:
        print("❌ Failed to read messages - check permissions")
        return False

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)

    success = test_read_client()
    sys.exit(0 if success else 1)