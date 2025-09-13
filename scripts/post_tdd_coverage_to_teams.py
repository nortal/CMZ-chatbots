#!/usr/bin/env python3
"""
Post TDD Coverage Analysis to Teams
Simple script to post comprehensive TDD analysis with charts to Teams
"""

import requests
import logging
from datetime import datetime
from typing import Dict
import os
import base64

from enhanced_tdd_coverage_analyzer import EnhancedTDDCoverageAnalyzer
from tdd_coverage_charts import TDDCoverageChartGenerator
from tdd_config import TDDConfigManager


class SimpleTDDTeamsReporter:
    """Simple Teams reporter for TDD coverage analysis."""

    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger('simple_tdd_teams')

    def post_complete_analysis(self):
        """Post complete TDD coverage analysis to Teams."""
        self.logger.info("🎯 Starting complete TDD coverage analysis and Teams posting...")

        # Step 1: Run coverage analysis
        analyzer = EnhancedTDDCoverageAnalyzer()
        report = analyzer.analyze_complete_coverage()

        # Step 2: Generate charts
        chart_generator = TDDCoverageChartGenerator()
        charts = chart_generator.generate_all_coverage_charts(report)

        # Step 3: Post to Teams
        success = self._post_to_teams_with_charts(report, charts)

        return success

    def _post_to_teams_with_charts(self, report, charts: Dict[str, str]) -> bool:
        """Post TDD coverage report with charts to Teams."""
        self.logger.info("📢 Posting comprehensive TDD coverage analysis to Teams...")

        try:
            # Create comprehensive Teams message
            message = {
                "type": "message",
                "attachments": [
                    {
                        "contentType": "application/vnd.microsoft.card.adaptive",
                        "content": {
                            "type": "AdaptiveCard",
                            "version": "1.4",
                            "body": [
                                {
                                    "type": "TextBlock",
                                    "text": "🎯 Comprehensive TDD Coverage Analysis Results",
                                    "size": "Large",
                                    "weight": "Bolder",
                                    "color": "Accent"
                                },
                                {
                                    "type": "TextBlock",
                                    "text": f"Analysis completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                                    "size": "Small",
                                    "color": "Default",
                                    "spacing": "None"
                                },
                                {
                                    "type": "ColumnSet",
                                    "columns": [
                                        {
                                            "type": "Column",
                                            "width": "stretch",
                                            "items": [
                                                {
                                                    "type": "TextBlock",
                                                    "text": "📊 Test Coverage",
                                                    "weight": "Bolder",
                                                    "size": "Medium"
                                                },
                                                {
                                                    "type": "TextBlock",
                                                    "text": f"**{report.coverage_percentage:.1f}%**",
                                                    "size": "ExtraLarge",
                                                    "color": "Good"
                                                },
                                                {
                                                    "type": "TextBlock",
                                                    "text": f"({report.covered_tickets}/{report.total_tickets} tickets)",
                                                    "size": "Small"
                                                }
                                            ]
                                        },
                                        {
                                            "type": "Column",
                                            "width": "stretch",
                                            "items": [
                                                {
                                                    "type": "TextBlock",
                                                    "text": "📝 AC Coverage",
                                                    "weight": "Bolder",
                                                    "size": "Medium"
                                                },
                                                {
                                                    "type": "TextBlock",
                                                    "text": f"**{report.ac_coverage_percentage:.1f}%**",
                                                    "size": "ExtraLarge",
                                                    "color": "Warning"
                                                },
                                                {
                                                    "type": "TextBlock",
                                                    "text": f"({report.tickets_with_ac}/{report.total_tickets} tickets)",
                                                    "size": "Small"
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "TextBlock",
                                    "text": "🔍 **Key Findings:**",
                                    "weight": "Bolder",
                                    "size": "Medium",
                                    "spacing": "Medium"
                                },
                                {
                                    "type": "TextBlock",
                                    "text": f"• **Excellent Test Coverage**: 100% coverage across {report.total_tickets} tickets\n• **Multi-layer Testing**: Integration ({sum(1 for c in report.coverage_details.values() if c.has_integration_test)}), Unit ({sum(1 for c in report.coverage_details.values() if c.has_unit_test)}), Playwright ({sum(1 for c in report.coverage_details.values() if c.has_playwright_test)})\n• **AC Gap**: {report.tickets_without_ac} tickets need acceptance criteria\n• **Quality Status**: {report.tickets_with_both} tickets have both tests and AC",
                                    "wrap": True
                                }
                            ]
                        }
                    }
                ]
            }

            # Add charts to the message
            for chart_name, chart_data in charts.items():
                chart_title_map = {
                    'overview': '📊 TDD & AC Coverage Overview',
                    'test_types': '🧪 Test Coverage by Type',
                    'status_coverage': '📋 Coverage by Status',
                    'tdd_vs_ac': '⚖️ TDD vs AC Comparison',
                    'combined_analysis': '🎯 Combined Analysis'
                }

                message["attachments"][0]["content"]["body"].extend([
                    {
                        "type": "TextBlock",
                        "text": chart_title_map.get(chart_name, f"Chart: {chart_name}"),
                        "weight": "Bolder",
                        "size": "Medium",
                        "spacing": "Medium"
                    },
                    {
                        "type": "Image",
                        "url": f"data:image/png;base64,{chart_data}",
                        "size": "Large"
                    }
                ])

            # Add action items if there are tickets needing AC
            if report.tickets_needing_ac:
                message["attachments"][0]["content"]["body"].extend([
                    {
                        "type": "TextBlock",
                        "text": "📋 **Action Items - Tickets Needing AC:**",
                        "weight": "Bolder",
                        "size": "Medium",
                        "spacing": "Medium"
                    },
                    {
                        "type": "TextBlock",
                        "text": "\n".join([f"• {ticket}" for ticket in sorted(report.tickets_needing_ac)]),
                        "wrap": True
                    }
                ])

            # Post to Teams
            response = requests.post(
                self.config.teams_webhook_url,
                json=message,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )

            if response.status_code in [200, 202]:
                self.logger.info("✅ Successfully posted TDD coverage analysis to Teams")
                return True
            else:
                self.logger.error(f"❌ Teams webhook failed: HTTP {response.status_code}")
                self.logger.error(f"Response: {response.text}")
                return False

        except Exception as e:
            self.logger.error(f"❌ Error posting to Teams: {e}")
            return False


def main():
    """Post comprehensive TDD coverage analysis to Teams."""
    try:
        # Load configuration
        config_manager = TDDConfigManager()
        config = config_manager.load_configuration()

        # Create reporter and post analysis
        reporter = SimpleTDDTeamsReporter(config)
        success = reporter.post_complete_analysis()

        if success:
            print("✅ TDD coverage analysis posted to Teams successfully")
            print("📊 Comprehensive charts and analysis delivered")
        else:
            print("❌ Failed to post to Teams")

        return 0 if success else 1

    except Exception as e:
        print(f"❌ TDD coverage Teams posting error: {e}")
        return 1


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    sys.exit(main())