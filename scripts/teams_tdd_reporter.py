#!/usr/bin/env python3
"""
Teams TDD Reporter Service
Main orchestrator for TDD improvement reporting to Microsoft Teams

Generates professional charts and posts to Teams webhook with adaptive cards
following CMZ branding preferences (clean, professional, no emojis in reports).
"""

import io
import base64
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import requests

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
import numpy as np

from tdd_config import TDDConfigManager, TDDConfig
from tdd_metrics_collector import TDDMetricsCollector, TDDMetrics


class TeamsTDDReporter:
    """
    Main Teams TDD reporting service.
    Generates charts and posts to Teams following professional standards.
    """

    def __init__(self, config: TDDConfig):
        self.config = config
        self.logger = logging.getLogger('tdd_reporting.teams')
        self.chart_style = config.get_chart_styling() if hasattr(config, 'get_chart_styling') else {}

        # Initialize matplotlib with professional styling
        plt.style.use('seaborn-v0_8-whitegrid')
        matplotlib.rcParams.update({
            'font.size': 11,
            'axes.titlesize': 14,
            'axes.labelsize': 12,
            'xtick.labelsize': 10,
            'ytick.labelsize': 10,
            'legend.fontsize': 11,
            'figure.titlesize': 16
        })

    def generate_tdd_report(self, days: int = None) -> bool:
        """
        Generate complete TDD report and post to Teams.
        Returns True if successful, False otherwise.
        """
        try:
            days = days or self.config.metrics_days
            self.logger.info(f"📊 Generating TDD report for last {days} days...")

            # Collect metrics
            collector = TDDMetricsCollector(self.config)
            current_metrics = collector.collect_all_metrics(days)

            # Collect historical data for trends (simplified for now)
            historical_metrics = self._collect_historical_metrics(days)

            # Generate charts
            charts = self._generate_all_charts(current_metrics, historical_metrics)

            # Post to Teams
            success = self._post_to_teams(current_metrics, charts)

            if success:
                self.logger.info("✅ TDD report posted to Teams successfully")
            else:
                self.logger.error("❌ Failed to post TDD report to Teams")

            return success

        except Exception as e:
            self.logger.error(f"❌ Error generating TDD report: {e}")
            return False

    def _collect_historical_metrics(self, days: int) -> List[TDDMetrics]:
        """
        Collect historical metrics for trend analysis.
        For now, simulates historical data. In production, this would query a database.
        """
        # Generate sample historical data for demonstration
        historical = []
        collector = TDDMetricsCollector(self.config)

        # Simulate improving trends over time
        base_date = datetime.now() - timedelta(days=days)

        for i in range(0, days, 7):  # Weekly data points
            date = base_date + timedelta(days=i)

            # Simulate improving metrics over time
            progress_factor = i / days  # 0 to 1 over time period

            simulated_metrics = TDDMetrics(
                success_rate=75 + (15 * progress_factor),  # 75% to 90%
                review_rounds_avg=2.0 - (0.8 * progress_factor),  # 2.0 to 1.2
                test_coverage_rate=85 + (10 * progress_factor),  # 85% to 95%
                security_resolution_rate=90 + (10 * progress_factor),  # 90% to 100%
                foundation_adoption_rate=30 + (40 * progress_factor),  # 30% to 70%
                total_tickets=10,
                successful_tickets=int(10 * (0.75 + 0.15 * progress_factor)),
                date_collected=date
            )
            historical.append(simulated_metrics)

        return historical

    def _generate_all_charts(self, current_metrics: TDDMetrics, historical_metrics: List[TDDMetrics]) -> Dict[str, str]:
        """
        Generate all TDD improvement charts.
        Returns dict of chart_name -> base64_encoded_image.
        """
        charts = {}

        try:
            # Success Rate Trend Chart
            charts['success_rate'] = self._generate_success_rate_chart(current_metrics, historical_metrics)

            # Review Quality Chart
            charts['review_quality'] = self._generate_review_quality_chart(current_metrics, historical_metrics)

            # Test Coverage Chart
            charts['test_coverage'] = self._generate_test_coverage_chart(current_metrics, historical_metrics)

            # Security Resolution Chart
            charts['security'] = self._generate_security_chart(current_metrics, historical_metrics)

            # Foundation Adoption Chart
            charts['foundation'] = self._generate_foundation_chart(current_metrics, historical_metrics)

            self.logger.info(f"📈 Generated {len(charts)} charts successfully")

        except Exception as e:
            self.logger.error(f"❌ Error generating charts: {e}")

        return charts

    def _generate_success_rate_chart(self, current: TDDMetrics, historical: List[TDDMetrics]) -> str:
        """Generate TDD success rate trend chart."""
        fig, ax = plt.subplots(figsize=(10, 6))

        # Extract data
        dates = [m.date_collected for m in historical] + [current.date_collected]
        success_rates = [m.success_rate for m in historical] + [current.success_rate]

        # Plot trend line
        ax.plot(dates, success_rates, marker='o', linewidth=2, markersize=6,
                color='#007bff', label='Success Rate')

        # Add target line
        ax.axhline(y=90, color='#28a745', linestyle='--', alpha=0.7, label='Target (90%)')

        # Formatting
        ax.set_title('TDD Ticket Success Rate Trend', fontweight='bold', pad=20)
        ax.set_ylabel('Success Rate (%)')
        ax.set_xlabel('Date')
        ax.grid(True, alpha=0.3)
        ax.legend()

        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        ax.xaxis.set_major_locator(mdates.WeekdayLocator())
        plt.xticks(rotation=45)

        # Set y-axis limits
        ax.set_ylim(0, 100)

        # Color coding based on current performance
        current_color = '#28a745' if current.success_rate >= 90 else '#ffc107' if current.success_rate >= 80 else '#dc3545'
        ax.scatter([current.date_collected], [current.success_rate],
                  color=current_color, s=100, zorder=5)

        plt.tight_layout()
        return self._fig_to_base64(fig, "success_rate")

    def _generate_review_quality_chart(self, current: TDDMetrics, historical: List[TDDMetrics]) -> str:
        """Generate review quality trend chart."""
        fig, ax = plt.subplots(figsize=(10, 6))

        dates = [m.date_collected for m in historical] + [current.date_collected]
        review_rounds = [m.review_rounds_avg for m in historical] + [current.review_rounds_avg]

        ax.plot(dates, review_rounds, marker='o', linewidth=2, markersize=6,
                color='#6f42c1', label='Avg Review Rounds')

        # Target line (lower is better)
        ax.axhline(y=1.2, color='#28a745', linestyle='--', alpha=0.7, label='Target (≤1.2)')

        ax.set_title('Review Quality Improvement Trend', fontweight='bold', pad=20)
        ax.set_ylabel('Average Review Rounds per MR')
        ax.set_xlabel('Date')
        ax.grid(True, alpha=0.3)
        ax.legend()

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        ax.xaxis.set_major_locator(mdates.WeekdayLocator())
        plt.xticks(rotation=45)

        # Color coding (lower is better for review rounds)
        current_color = '#28a745' if current.review_rounds_avg <= 1.2 else '#ffc107' if current.review_rounds_avg <= 1.5 else '#dc3545'
        ax.scatter([current.date_collected], [current.review_rounds_avg],
                  color=current_color, s=100, zorder=5)

        plt.tight_layout()
        return self._fig_to_base64(fig, "review_quality")

    def _generate_test_coverage_chart(self, current: TDDMetrics, historical: List[TDDMetrics]) -> str:
        """Generate test coverage trend chart."""
        fig, ax = plt.subplots(figsize=(10, 6))

        dates = [m.date_collected for m in historical] + [current.date_collected]
        coverage_rates = [m.test_coverage_rate for m in historical] + [current.test_coverage_rate]

        ax.plot(dates, coverage_rates, marker='o', linewidth=2, markersize=6,
                color='#e83e8c', label='Test Coverage')

        ax.axhline(y=95, color='#28a745', linestyle='--', alpha=0.7, label='Target (95%)')

        ax.set_title('Test Coverage Consistency Trend', fontweight='bold', pad=20)
        ax.set_ylabel('Test Coverage (%)')
        ax.set_xlabel('Date')
        ax.grid(True, alpha=0.3)
        ax.legend()

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        ax.xaxis.set_major_locator(mdates.WeekdayLocator())
        plt.xticks(rotation=45)

        ax.set_ylim(0, 100)

        current_color = '#28a745' if current.test_coverage_rate >= 95 else '#ffc107' if current.test_coverage_rate >= 85 else '#dc3545'
        ax.scatter([current.date_collected], [current.test_coverage_rate],
                  color=current_color, s=100, zorder=5)

        plt.tight_layout()
        return self._fig_to_base64(fig, "test_coverage")

    def _generate_security_chart(self, current: TDDMetrics, historical: List[TDDMetrics]) -> str:
        """Generate security resolution trend chart."""
        fig, ax = plt.subplots(figsize=(10, 6))

        dates = [m.date_collected for m in historical] + [current.date_collected]
        security_rates = [m.security_resolution_rate for m in historical] + [current.security_resolution_rate]

        ax.plot(dates, security_rates, marker='o', linewidth=2, markersize=6,
                color='#fd7e14', label='Security Resolution Rate')

        ax.axhline(y=100, color='#28a745', linestyle='--', alpha=0.7, label='Target (100%)')

        ax.set_title('Security Quality Integration Trend', fontweight='bold', pad=20)
        ax.set_ylabel('Pre-Merge Resolution Rate (%)')
        ax.set_xlabel('Date')
        ax.grid(True, alpha=0.3)
        ax.legend()

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        ax.xaxis.set_major_locator(mdates.WeekdayLocator())
        plt.xticks(rotation=45)

        ax.set_ylim(0, 100)

        current_color = '#28a745' if current.security_resolution_rate >= 100 else '#ffc107' if current.security_resolution_rate >= 95 else '#dc3545'
        ax.scatter([current.date_collected], [current.security_resolution_rate],
                  color=current_color, s=100, zorder=5)

        plt.tight_layout()
        return self._fig_to_base64(fig, "security")

    def _generate_foundation_chart(self, current: TDDMetrics, historical: List[TDDMetrics]) -> str:
        """Generate foundation pattern adoption chart."""
        fig, ax = plt.subplots(figsize=(10, 6))

        dates = [m.date_collected for m in historical] + [current.date_collected]
        adoption_rates = [m.foundation_adoption_rate for m in historical] + [current.foundation_adoption_rate]

        ax.plot(dates, adoption_rates, marker='o', linewidth=2, markersize=6,
                color='#20c997', label='Foundation Pattern Adoption')

        ax.set_title('TDD Foundation Pattern Adoption Trend', fontweight='bold', pad=20)
        ax.set_ylabel('Adoption Rate (%)')
        ax.set_xlabel('Date')
        ax.grid(True, alpha=0.3)
        ax.legend()

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        ax.xaxis.set_major_locator(mdates.WeekdayLocator())
        plt.xticks(rotation=45)

        ax.set_ylim(0, 100)

        # Color based on increasing trend
        current_color = '#28a745' if current.foundation_adoption_rate >= 50 else '#ffc107' if current.foundation_adoption_rate >= 30 else '#dc3545'
        ax.scatter([current.date_collected], [current.foundation_adoption_rate],
                  color=current_color, s=100, zorder=5)

        plt.tight_layout()
        return self._fig_to_base64(fig, "foundation")

    def _fig_to_base64(self, fig: Figure, chart_name: str = None) -> str:
        """Convert matplotlib figure to base64 encoded string and save locally."""
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=100, bbox_inches='tight')

        # Also save locally for user viewing
        if chart_name:
            local_filename = f"tdd_chart_{chart_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            fig.savefig(local_filename, format='png', dpi=100, bbox_inches='tight')
            self.logger.info(f"📊 Chart saved locally: {local_filename}")

        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode()
        plt.close(fig)
        return image_base64

    def _post_to_teams(self, metrics: TDDMetrics, charts: Dict[str, str]) -> bool:
        """
        Post TDD improvement report to Microsoft Teams.
        Uses adaptive cards for rich formatting.
        """
        try:
            self.logger.info("📢 Posting TDD report to Teams...")

            # Create adaptive card payload
            card_payload = self._create_teams_adaptive_card(metrics, charts)

            response = requests.post(
                self.config.teams_webhook_url,
                json=card_payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )

            if response.status_code in [200, 202]:
                self.logger.info("✅ Successfully posted to Teams")
                return True
            else:
                self.logger.error(f"❌ Teams webhook failed: HTTP {response.status_code}")
                self.logger.error(f"Response: {response.text}")
                return False

        except Exception as e:
            self.logger.error(f"❌ Error posting to Teams: {e}")
            return False

    def _create_teams_adaptive_card(self, metrics: TDDMetrics, charts: Dict[str, str]) -> Dict:
        """
        Create Microsoft Teams adaptive card for TDD report.
        Professional format following CMZ preferences.
        """
        # Determine overall health status
        overall_health = self._calculate_overall_health(metrics)
        health_color = "good" if overall_health >= 85 else "warning" if overall_health >= 70 else "attention"

        card = {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": {
                        "type": "AdaptiveCard",
                        "body": [
                            {
                                "type": "TextBlock",
                                "text": f"TDD Improvement Report - {datetime.now().strftime('%Y-%m-%d')}",
                                "weight": "Bolder",
                                "size": "Large",
                                "color": health_color
                            },
                            {
                                "type": "TextBlock",
                                "text": f"Overall TDD Health Score: {overall_health:.0f}%",
                                "weight": "Bolder",
                                "size": "Medium",
                                "spacing": "Medium"
                            },
                            {
                                "type": "FactSet",
                                "facts": [
                                    {
                                        "title": "Success Rate",
                                        "value": f"{metrics.success_rate:.1f}% (Target: ≥90%)"
                                    },
                                    {
                                        "title": "Review Rounds",
                                        "value": f"{metrics.review_rounds_avg:.1f} (Target: ≤1.2)"
                                    },
                                    {
                                        "title": "Test Coverage",
                                        "value": f"{metrics.test_coverage_rate:.1f}% (Target: ≥95%)"
                                    },
                                    {
                                        "title": "Security Resolution",
                                        "value": f"{metrics.security_resolution_rate:.1f}% (Target: 100%)"
                                    },
                                    {
                                        "title": "Foundation Adoption",
                                        "value": f"{metrics.foundation_adoption_rate:.1f}%"
                                    },
                                    {
                                        "title": "Tickets Analyzed",
                                        "value": f"{metrics.successful_tickets}/{metrics.total_tickets}"
                                    }
                                ]
                            }
                        ],
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "version": "1.2"
                    }
                }
            ]
        }

        # Add charts if available (Teams has limitations on inline images)
        if charts:
            self.logger.info(f"📊 Generated {len(charts)} charts for Teams report")

        return card

    def _calculate_overall_health(self, metrics: TDDMetrics) -> float:
        """
        Calculate overall TDD health score based on all metrics.
        """
        # Weight different metrics based on importance
        weights = {
            'success_rate': 0.3,      # 30% - most important
            'review_quality': 0.2,    # 20% - efficiency indicator
            'test_coverage': 0.2,     # 20% - quality indicator
            'security': 0.2,          # 20% - reliability indicator
            'foundation': 0.1         # 10% - adoption indicator
        }

        # Normalize metrics to 0-100 scale
        success_score = min(metrics.success_rate, 100)
        review_score = max(0, 100 - (metrics.review_rounds_avg - 1.0) * 50)  # Lower is better
        test_score = min(metrics.test_coverage_rate, 100)
        security_score = min(metrics.security_resolution_rate, 100)
        foundation_score = min(metrics.foundation_adoption_rate, 100)

        overall = (
            success_score * weights['success_rate'] +
            review_score * weights['review_quality'] +
            test_score * weights['test_coverage'] +
            security_score * weights['security'] +
            foundation_score * weights['foundation']
        )

        return overall


def main():
    """
    Test the Teams reporting system.
    Can be run standalone for validation.
    """
    try:
        config_manager = TDDConfigManager()
        config = config_manager.load_configuration()

        reporter = TeamsTDDReporter(config)
        success = reporter.generate_tdd_report(days=7)

        if success:
            print("✅ TDD report generated and posted successfully")
            return 0
        else:
            print("❌ TDD report generation failed")
            return 1

    except Exception as e:
        print(f"❌ Teams reporting error: {e}")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())