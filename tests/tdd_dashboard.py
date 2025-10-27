#!/usr/bin/env python3

"""
TDD Dashboard Generator for CMZ Project
Creates comprehensive dashboard views of TDD coverage and test execution
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import glob
import re

class TDDDashboard:
    def __init__(self):
        self.tests_dir = Path('tests')
        self.reports_dir = Path('tests/batch_reports')
        self.dashboard_dir = Path('tests/dashboard')
        self.dashboard_dir.mkdir(exist_ok=True)

        # Load ticket data
        self.all_tickets = self.load_ticket_data()

    def load_ticket_data(self) -> Dict[str, Any]:
        """Load complete ticket dataset"""
        ticket_file = Path('jira_data/all_tickets_consolidated.json')
        if ticket_file.exists():
            with open(ticket_file, 'r') as f:
                return json.load(f)
        return {}

    def get_test_coverage_stats(self) -> Dict[str, Any]:
        """Calculate comprehensive test coverage statistics"""
        stats = {
            'total_tickets': len(self.all_tickets),
            'tickets_with_tests': 0,
            'category_coverage': {},
            'test_files_created': 0,
            'coverage_by_category': {}
        }

        # Count tickets with test specifications
        test_categories = ['integration', 'unit', 'playwright', 'security']

        for category in test_categories:
            category_path = self.tests_dir / category
            category_count = 0
            if category_path.exists():
                for ticket_dir in category_path.iterdir():
                    if ticket_dir.is_dir() and ticket_dir.name.startswith('PR003946-'):
                        howto_file = ticket_dir / f"{ticket_dir.name}-howto-test.md"
                        advice_file = ticket_dir / f"{ticket_dir.name}-ADVICE.md"
                        if howto_file.exists() and advice_file.exists():
                            category_count += 1
                            stats['test_files_created'] += 2  # howto + advice

            stats['category_coverage'][category] = category_count
            stats['tickets_with_tests'] += category_count

        # Calculate coverage percentage
        stats['coverage_percentage'] = (stats['tickets_with_tests'] / stats['total_tickets'] * 100) if stats['total_tickets'] > 0 else 0

        return stats

    def get_recent_execution_results(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get recent batch execution results"""
        results = []

        # Find recent batch result files
        if self.reports_dir.exists():
            result_files = glob.glob(str(self.reports_dir / 'batch_results_*.json'))

            for file_path in result_files:
                try:
                    # Extract timestamp from filename
                    filename = os.path.basename(file_path)
                    timestamp_match = re.search(r'batch_results_(\d{4}-\d{2}-\d{2}-\d{6})\.json', filename)
                    if timestamp_match:
                        timestamp_str = timestamp_match.group(1)
                        file_datetime = datetime.strptime(timestamp_str, '%Y-%m-%d-%H%M%S')

                        # Check if within date range
                        if file_datetime >= datetime.now() - timedelta(days=days):
                            with open(file_path, 'r') as f:
                                data = json.load(f)
                                data['file_datetime'] = file_datetime
                                results.append(data)
                except Exception as e:
                    print(f"Warning: Could not parse {file_path}: {e}")

        # Sort by datetime, most recent first
        results.sort(key=lambda x: x.get('file_datetime', datetime.min), reverse=True)
        return results

    def generate_html_dashboard(self) -> str:
        """Generate comprehensive HTML dashboard"""

        # Get current stats
        coverage_stats = self.get_test_coverage_stats()
        recent_results = self.get_recent_execution_results(days=30)

        # Calculate trend data
        trend_data = self.calculate_trends(recent_results)

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CMZ TDD Dashboard</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            line-height: 1.6;
        }}

        .dashboard {{
            max-width: 1200px;
            margin: 0 auto;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }}

        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .metric-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }}

        .metric-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #333;
            margin: 10px 0;
        }}

        .metric-label {{
            color: #666;
            font-size: 1.1em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        .progress-bar {{
            width: 100%;
            height: 20px;
            background-color: #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
            margin: 15px 0;
        }}

        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #4CAF50, #45a049);
            transition: width 0.5s ease;
        }}

        .section {{
            background: white;
            margin-bottom: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}

        .section-header {{
            background-color: #f8f9fa;
            padding: 20px;
            border-bottom: 1px solid #dee2e6;
            border-radius: 10px 10px 0 0;
            font-size: 1.3em;
            font-weight: bold;
        }}

        .section-content {{
            padding: 20px;
        }}

        .category-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}

        .category-item {{
            padding: 15px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            text-align: center;
        }}

        .category-count {{
            font-size: 2em;
            font-weight: bold;
            color: #495057;
        }}

        .recent-results {{
            overflow-x: auto;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
        }}

        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}

        th {{
            background-color: #f8f9fa;
            font-weight: bold;
        }}

        .status-badge {{
            padding: 4px 8px;
            border-radius: 4px;
            color: white;
            font-size: 0.9em;
            font-weight: bold;
        }}

        .status-pass {{ background-color: #28a745; }}
        .status-fail {{ background-color: #dc3545; }}
        .status-error {{ background-color: #fd7e14; }}
        .status-skip {{ background-color: #6c757d; }}

        .timestamp {{
            color: #666;
            font-size: 0.9em;
        }}

        .trend-indicator {{
            display: inline-block;
            margin-left: 10px;
        }}

        .trend-up {{ color: #28a745; }}
        .trend-down {{ color: #dc3545; }}
        .trend-stable {{ color: #6c757d; }}
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>🎯 CMZ TDD Dashboard</h1>
            <p>Comprehensive Test-Driven Development Coverage & Execution Tracking</p>
            <div class="timestamp">Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>

        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">{coverage_stats['total_tickets']}</div>
                <div class="metric-label">Total Tickets</div>
            </div>

            <div class="metric-card">
                <div class="metric-value">{coverage_stats['tickets_with_tests']}</div>
                <div class="metric-label">Tickets with Tests</div>
            </div>

            <div class="metric-card">
                <div class="metric-value">{coverage_stats['coverage_percentage']:.1f}%</div>
                <div class="metric-label">Test Coverage</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {coverage_stats['coverage_percentage']}%"></div>
                </div>
            </div>

            <div class="metric-card">
                <div class="metric-value">{coverage_stats['test_files_created']}</div>
                <div class="metric-label">Test Files Created</div>
            </div>
        </div>

        <div class="section">
            <div class="section-header">📂 Test Coverage by Category</div>
            <div class="section-content">
                <div class="category-grid">"""

        # Add category coverage
        category_icons = {
            'integration': '🔗',
            'unit': '🧪',
            'playwright': '🎭',
            'security': '🛡️'
        }

        for category, count in coverage_stats['category_coverage'].items():
            icon = category_icons.get(category, '📝')
            html_content += f"""
                    <div class="category-item">
                        <div>{icon}</div>
                        <div class="category-count">{count}</div>
                        <div>{category.title()}</div>
                    </div>"""

        html_content += """
                </div>
            </div>
        </div>"""

        # Recent execution results
        if recent_results:
            latest_result = recent_results[0]
            html_content += f"""
        <div class="section">
            <div class="section-header">🚀 Recent Test Executions {self.get_trend_indicator(trend_data)}</div>
            <div class="section-content">
                <div class="recent-results">
                    <table>
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Tests Run</th>
                                <th>Pass Rate</th>
                                <th>Duration</th>
                                <th>Status Breakdown</th>
                            </tr>
                        </thead>
                        <tbody>"""

            for result in recent_results[:10]:  # Show last 10 results
                summary = result.get('summary', {})
                exec_summary = summary.get('execution_summary', {})
                status_breakdown = summary.get('status_breakdown', {})

                # Format date
                run_date = result.get('file_datetime', datetime.now())
                date_str = run_date.strftime('%Y-%m-%d %H:%M')

                # Status badges
                status_badges = ""
                for status, count in status_breakdown.items():
                    if count > 0:
                        status_class = f"status-{status.lower()}"
                        status_badges += f'<span class="status-badge {status_class}">{status}: {count}</span> '

                html_content += f"""
                            <tr>
                                <td>{date_str}</td>
                                <td>{exec_summary.get('total_tests', 0)}</td>
                                <td>{summary.get('pass_rate', 0):.1f}%</td>
                                <td>{exec_summary.get('execution_time', 0):.1f}s</td>
                                <td>{status_badges}</td>
                            </tr>"""

            html_content += """
                        </tbody>
                    </table>
                </div>
            </div>
        </div>"""

        # Sequential reasoning assessment
        html_content += f"""
        <div class="section">
            <div class="section-header">🧠 Sequential Reasoning Assessment</div>
            <div class="section-content">
                <p><strong>Current TDD Framework Status:</strong> {self.get_framework_status_assessment(coverage_stats, recent_results)}</p>
                <p><strong>Test Coverage Analysis:</strong> {coverage_stats['tickets_with_tests']}/{coverage_stats['total_tickets']} tickets have comprehensive test specifications ({coverage_stats['coverage_percentage']:.1f}% coverage)</p>
                <p><strong>Execution Trends:</strong> {self.get_execution_trend_analysis(recent_results)}</p>
                <p><strong>Recommendations:</strong> {self.get_recommendations(coverage_stats, recent_results)}</p>
            </div>
        </div>

    </div>
</body>
</html>"""

        return html_content

    def get_trend_indicator(self, trend_data: Dict[str, Any]) -> str:
        """Get HTML trend indicator"""
        if not trend_data:
            return ""

        if trend_data['pass_rate_trend'] == 'improving':
            return '<span class="trend-indicator trend-up">📈 Improving</span>'
        elif trend_data['pass_rate_trend'] == 'declining':
            return '<span class="trend-indicator trend-down">📉 Declining</span>'
        else:
            return '<span class="trend-indicator trend-stable">➡️ Stable</span>'

    def calculate_trends(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate trend analysis from recent results"""
        if len(results) < 2:
            return {}

        recent = results[0]['summary']
        previous = results[1]['summary']

        recent_pass_rate = recent.get('pass_rate', 0)
        previous_pass_rate = previous.get('pass_rate', 0)

        if recent_pass_rate > previous_pass_rate + 5:
            trend = 'improving'
        elif recent_pass_rate < previous_pass_rate - 5:
            trend = 'declining'
        else:
            trend = 'stable'

        return {
            'pass_rate_trend': trend,
            'pass_rate_change': recent_pass_rate - previous_pass_rate
        }

    def get_framework_status_assessment(self, coverage_stats: Dict[str, Any], results: List[Dict[str, Any]]) -> str:
        """Generate framework status assessment"""
        coverage = coverage_stats['coverage_percentage']

        if coverage >= 90:
            status = "Excellent - comprehensive test coverage established"
        elif coverage >= 70:
            status = "Good - solid test foundation with room for expansion"
        elif coverage >= 50:
            status = "Developing - basic framework in place, needs enhancement"
        else:
            status = "Initial - framework established, requires systematic expansion"

        if results and results[0]['summary'].get('pass_rate', 0) >= 80:
            status += " with strong execution performance"
        elif results and results[0]['summary'].get('pass_rate', 0) >= 60:
            status += " with moderate execution performance"
        else:
            status += " requiring execution improvements"

        return status

    def get_execution_trend_analysis(self, results: List[Dict[str, Any]]) -> str:
        """Analyze execution trends"""
        if not results:
            return "No recent execution data available"

        if len(results) == 1:
            latest = results[0]['summary']
            return f"Single execution: {latest.get('pass_rate', 0):.1f}% pass rate across {latest.get('execution_summary', {}).get('total_tests', 0)} tests"

        trend_data = self.calculate_trends(results)
        change = trend_data.get('pass_rate_change', 0)

        if abs(change) < 5:
            return f"Stable execution performance with consistent {results[0]['summary'].get('pass_rate', 0):.1f}% pass rate"
        elif change > 0:
            return f"Improving execution performance (+{change:.1f}% pass rate improvement)"
        else:
            return f"Declining execution performance ({change:.1f}% pass rate decrease) - investigate failing tests"

    def get_recommendations(self, coverage_stats: Dict[str, Any], results: List[Dict[str, Any]]) -> str:
        """Generate strategic recommendations"""
        coverage = coverage_stats['coverage_percentage']
        recommendations = []

        if coverage < 90:
            remaining = coverage_stats['total_tickets'] - coverage_stats['tickets_with_tests']
            recommendations.append(f"Expand test coverage to remaining {remaining} tickets")

        if results:
            latest = results[0]['summary']
            if latest.get('pass_rate', 0) < 80:
                failed_count = len(latest.get('failed_tickets', []))
                if failed_count > 0:
                    recommendations.append(f"Address {failed_count} consistently failing tests")

            error_count = len(latest.get('error_tickets', []))
            if error_count > 0:
                recommendations.append(f"Resolve {error_count} tickets with execution errors")

        if not recommendations:
            recommendations.append("Continue systematic testing and maintain current coverage levels")

        return " • ".join(recommendations)

    def generate_markdown_summary(self) -> str:
        """Generate markdown summary report"""
        coverage_stats = self.get_test_coverage_stats()
        recent_results = self.get_recent_execution_results(days=7)

        content = f"""# CMZ TDD Framework Summary

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview

The CMZ TDD framework currently provides comprehensive test coverage for **{coverage_stats['tickets_with_tests']}** of **{coverage_stats['total_tickets']}** total tickets (**{coverage_stats['coverage_percentage']:.1f}%** coverage).

## Test Coverage by Category

| Category | Tests Created | Icon |
|----------|--------------|------|
| Integration | {coverage_stats['category_coverage'].get('integration', 0)} | 🔗 |
| Unit | {coverage_stats['category_coverage'].get('unit', 0)} | 🧪 |
| Playwright | {coverage_stats['category_coverage'].get('playwright', 0)} | 🎭 |
| Security | {coverage_stats['category_coverage'].get('security', 0)} | 🛡️ |

## Recent Execution Summary

"""
        if recent_results:
            latest = recent_results[0]['summary']
            exec_summary = latest['execution_summary']

            content += f"""**Most Recent Execution**: {recent_results[0]['file_datetime'].strftime('%Y-%m-%d %H:%M')}
- **Tests Run**: {exec_summary['total_tests']}
- **Pass Rate**: {latest['pass_rate']:.1f}%
- **Execution Time**: {exec_summary['execution_time']:.1f} seconds
- **Parallel Efficiency**: {exec_summary['parallel_efficiency']:.1f}x

### Status Breakdown
"""
            for status, count in latest['status_breakdown'].items():
                emoji = {'PASS': '✅', 'FAIL': '❌', 'SKIP': '⏭️', 'ERROR': '🚨', 'TIMEOUT': '⏰'}.get(status, '❓')
                content += f"- {emoji} **{status}**: {count}\n"
        else:
            content += "No recent execution data available.\n"

        content += f"""
## Sequential Reasoning Assessment

**Framework Status**: {self.get_framework_status_assessment(coverage_stats, recent_results)}

**Strategic Recommendations**: {self.get_recommendations(coverage_stats, recent_results)}

## Quick Actions

### Run Complete Test Suite
```bash
# Execute all available tests
python3 tests/run_batch_tests.py

# Execute specific category
python3 tests/run_batch_tests.py --category integration

# Execute with filtering
python3 tests/run_batch_tests.py --filter "PR003946-28"
```

### Individual Test Execution
```bash
# Execute single ticket test
python3 tests/execute_test.py PR003946-28
```

### Generate New Dashboard
```bash
# Regenerate dashboard
python3 tests/tdd_dashboard.py
```

---
*Generated by CMZ TDD Dashboard System*
"""

        return content

    def save_dashboard(self):
        """Save HTML dashboard and markdown summary"""
        timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')

        # Save HTML dashboard
        html_content = self.generate_html_dashboard()
        html_file = self.dashboard_dir / 'tdd_dashboard.html'
        with open(html_file, 'w') as f:
            f.write(html_content)

        # Save timestamped version
        html_archive = self.dashboard_dir / f'tdd_dashboard_{timestamp}.html'
        with open(html_archive, 'w') as f:
            f.write(html_content)

        # Save markdown summary
        md_content = self.generate_markdown_summary()
        md_file = self.dashboard_dir / 'TDD_SUMMARY.md'
        with open(md_file, 'w') as f:
            f.write(md_content)

        print(f"📊 Dashboard generated:")
        print(f"  🌐 HTML: {html_file}")
        print(f"  📝 Summary: {md_file}")
        print(f"  📁 Archive: {html_archive}")

        return html_file, md_file

def main():
    """Main function"""
    dashboard = TDDDashboard()
    html_file, md_file = dashboard.save_dashboard()

    print()
    print("✨ TDD Dashboard Ready!")
    print(f"   Open {html_file} in your browser for interactive dashboard")
    print(f"   View {md_file} for markdown summary")

if __name__ == "__main__":
    main()