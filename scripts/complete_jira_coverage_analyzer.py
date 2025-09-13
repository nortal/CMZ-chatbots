#!/usr/bin/env python3
"""
Complete Jira + TDD Coverage Analyzer
Fetches ALL tickets from Jira and analyzes comprehensive test coverage
Uses Basic Auth pattern following project conventions
"""

import re
import json
import requests
import logging
import base64
import os
from datetime import datetime
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class JiraTicket:
    """Complete Jira ticket information."""
    key: str
    status: str
    summary: str
    issue_type: str
    priority: str
    description: str = ""
    acceptance_criteria: str = ""
    assignee: Optional[str] = None
    components: List[str] = field(default_factory=list)
    labels: List[str] = field(default_factory=list)


@dataclass
class TestReference:
    """Test file reference to a ticket."""
    ticket_key: str
    file_path: str
    test_method: str
    test_type: str  # unit, integration, playwright, functional


@dataclass
class CompleteCoverageReport:
    """Complete coverage report including all Jira tickets."""
    # Jira data
    total_jira_tickets: int
    jira_tickets: Dict[str, JiraTicket]

    # Test coverage data
    tickets_with_tests: int
    tickets_without_tests: int
    test_coverage_percentage: float

    # Test references
    test_references: List[TestReference]
    coverage_by_test_type: Dict[str, int]

    # Status analysis
    coverage_by_status: Dict[str, Tuple[int, int]]  # (covered, total)

    # Priority analysis
    coverage_by_priority: Dict[str, Tuple[int, int]]

    # AC analysis
    tickets_with_ac: int
    tickets_without_ac: int
    tickets_needing_ac_proposals: List[str]


class CompleteJiraCoverageAnalyzer:
    """Complete Jira + TDD coverage analyzer using Basic Auth."""

    def __init__(self):
        self.logger = logging.getLogger('complete_jira_coverage')

        # Get credentials from environment (Basic Auth pattern)
        self.jira_email = os.getenv('JIRA_EMAIL', 'kc.stegbauer@nortal.com')
        self.jira_token = os.getenv('JIRA_API_TOKEN')
        self.jira_base_url = 'https://nortal-cmz.atlassian.net'

        if not self.jira_token:
            raise ValueError("JIRA_API_TOKEN environment variable not set")

        # Create Basic Auth credentials
        credentials = f"{self.jira_email}:{self.jira_token}"
        self.auth_header = base64.b64encode(credentials.encode()).decode()

        # Repository root
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.repo_root = os.path.dirname(current_dir)

        # Test directories
        self.test_directories = {
            'unit': 'backend/api/src/main/python/tests/unit',
            'integration': 'backend/api/src/main/python/tests/integration',
            'playwright': 'backend/api/src/main/python/tests/playwright',
            'functional': 'backend/api/src/main/python/tests/functional'
        }

    def analyze_complete_coverage(self) -> CompleteCoverageReport:
        """Perform complete coverage analysis of ALL Jira tickets."""
        self.logger.info("🔍 Starting complete Jira + TDD coverage analysis...")

        # Step 1: Fetch ALL tickets from Jira
        self.logger.info("📋 Fetching ALL tickets from Jira project...")
        jira_tickets = self._fetch_all_jira_tickets()
        self.logger.info(f"📊 Retrieved {len(jira_tickets)} tickets from Jira")

        # Step 2: Analyze test coverage across all files
        self.logger.info("🧪 Analyzing test coverage across all test types...")
        test_references = self._analyze_all_test_references()
        self.logger.info(f"🔍 Found {len(test_references)} test references")

        # Step 3: Cross-reference and generate report
        self.logger.info("🔗 Cross-referencing Jira tickets with test coverage...")
        report = self._generate_complete_report(jira_tickets, test_references)

        self.logger.info("✅ Complete coverage analysis finished")
        return report

    def _fetch_all_jira_tickets(self) -> Dict[str, JiraTicket]:
        """Fetch all tickets from Jira using Basic Auth and updated API."""
        tickets = {}
        start_at = 0
        max_results = 50

        try:
            while True:
                # Use updated JQL API endpoint
                jql_query = "project = PR003946 ORDER BY key ASC"

                response = requests.get(
                    f"{self.jira_base_url}/rest/api/3/search",
                    headers={
                        "Authorization": f"Basic {self.auth_header}",
                        "Accept": "application/json",
                        "Content-Type": "application/json"
                    },
                    params={
                        'jql': jql_query,
                        'startAt': start_at,
                        'maxResults': max_results,
                        'fields': 'key,status,summary,issuetype,priority,description,assignee,components,labels'
                    },
                    timeout=30
                )

                if response.status_code == 200:
                    data = response.json()
                    issues = data.get('issues', [])

                    if not issues:
                        break

                    # Process this batch of issues
                    for issue in issues:
                        ticket = self._parse_jira_ticket(issue)
                        tickets[ticket.key] = ticket

                    # Check if we have more results
                    if len(issues) < max_results:
                        break

                    start_at += max_results

                elif response.status_code == 410:
                    # Handle deprecated endpoint
                    self.logger.error("❌ Jira API endpoint deprecated. Using alternative approach...")

                    # Try the newer search endpoint format
                    response = requests.post(
                        f"{self.jira_base_url}/rest/api/3/search",
                        headers={
                            "Authorization": f"Basic {self.auth_header}",
                            "Accept": "application/json",
                            "Content-Type": "application/json"
                        },
                        json={
                            'jql': jql_query,
                            'startAt': start_at,
                            'maxResults': max_results,
                            'fields': ['key', 'status', 'summary', 'issuetype', 'priority', 'description', 'assignee', 'components', 'labels']
                        },
                        timeout=30
                    )

                    if response.status_code == 200:
                        data = response.json()
                        issues = data.get('issues', [])

                        for issue in issues:
                            ticket = self._parse_jira_ticket(issue)
                            tickets[ticket.key] = ticket

                        if len(issues) < max_results:
                            break
                        start_at += max_results
                    else:
                        self.logger.error(f"❌ Jira API error: {response.status_code} - {response.text}")
                        break
                else:
                    self.logger.error(f"❌ Jira API error: {response.status_code} - {response.text}")
                    break

        except Exception as e:
            self.logger.error(f"❌ Error fetching Jira tickets: {e}")

        return tickets

    def _parse_jira_ticket(self, issue: dict) -> JiraTicket:
        """Parse Jira issue JSON into JiraTicket object."""
        fields = issue['fields']

        # Extract description and look for acceptance criteria
        description = ""
        acceptance_criteria = ""

        if fields.get('description'):
            # Handle both old and new Jira description formats
            if isinstance(fields['description'], dict):
                # New ADF format
                description = self._extract_adf_text(fields['description'])
            else:
                # Legacy text format
                description = str(fields['description'])

            # Extract AC from description
            acceptance_criteria = self._extract_acceptance_criteria(description)

        # Extract assignee
        assignee = None
        if fields.get('assignee'):
            assignee = fields['assignee'].get('displayName', 'Unassigned')

        # Extract components
        components = []
        if fields.get('components'):
            components = [comp['name'] for comp in fields['components']]

        # Extract labels
        labels = fields.get('labels', [])

        return JiraTicket(
            key=issue['key'],
            status=fields['status']['name'],
            summary=fields['summary'],
            issue_type=fields['issuetype']['name'],
            priority=fields['priority']['name'] if fields.get('priority') else 'None',
            description=description,
            acceptance_criteria=acceptance_criteria,
            assignee=assignee,
            components=components,
            labels=labels
        )

    def _extract_adf_text(self, adf_content: dict) -> str:
        """Extract plain text from Atlassian Document Format (ADF)."""
        if not isinstance(adf_content, dict):
            return str(adf_content)

        text_parts = []

        def extract_text_recursive(node):
            if isinstance(node, dict):
                if node.get('type') == 'text':
                    text_parts.append(node.get('text', ''))
                elif 'content' in node:
                    for child in node['content']:
                        extract_text_recursive(child)
            elif isinstance(node, list):
                for item in node:
                    extract_text_recursive(item)

        extract_text_recursive(adf_content)
        return ' '.join(text_parts)

    def _extract_acceptance_criteria(self, description: str) -> str:
        """Extract acceptance criteria from ticket description."""
        # Common AC patterns
        ac_patterns = [
            r'acceptance criteria:?\s*(.+?)(?=\n\n|\n[A-Z]|$)',
            r'ac:?\s*(.+?)(?=\n\n|\n[A-Z]|$)',
            r'given.+?when.+?then.+',
            r'as a.+?i want.+?so that.+',
        ]

        description_lower = description.lower()

        for pattern in ac_patterns:
            matches = re.findall(pattern, description_lower, re.IGNORECASE | re.DOTALL)
            if matches:
                return matches[0].strip()

        return ""

    def _analyze_all_test_references(self) -> List[TestReference]:
        """Analyze all test files and extract ticket references."""
        test_references = []
        ticket_pattern = r'PR003946-(\d+)'

        for test_type, test_dir in self.test_directories.items():
            full_path = os.path.join(self.repo_root, test_dir)

            if not os.path.exists(full_path):
                self.logger.warning(f"⚠️ Test directory not found: {full_path}")
                continue

            self.logger.info(f"🔍 Analyzing {test_type} tests in {test_dir}")

            # Walk through all files in test directory
            for root, dirs, files in os.walk(full_path):
                for file in files:
                    if file.endswith(('.py', '.js')):
                        file_path = os.path.join(root, file)

                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                lines = content.split('\n')

                                current_test_method = None

                                for line_num, line in enumerate(lines):
                                    # Detect test method definitions
                                    if re.search(r'def test_|test\(.*\)|it\(.*\)', line):
                                        current_test_method = line.strip()

                                    # Find ticket references
                                    matches = re.findall(ticket_pattern, line)
                                    for match in matches:
                                        ticket_key = f"PR003946-{match}"

                                        test_references.append(TestReference(
                                            ticket_key=ticket_key,
                                            file_path=file_path,
                                            test_method=current_test_method or f"Line {line_num + 1}",
                                            test_type=test_type
                                        ))

                        except Exception as e:
                            self.logger.warning(f"⚠️ Error reading {file_path}: {e}")

        return test_references

    def _generate_complete_report(self, jira_tickets: Dict[str, JiraTicket],
                                test_references: List[TestReference]) -> CompleteCoverageReport:
        """Generate complete coverage report."""

        # Build test coverage mapping
        tickets_with_tests = set()
        coverage_by_test_type = {'unit': 0, 'integration': 0, 'playwright': 0, 'functional': 0}

        for ref in test_references:
            tickets_with_tests.add(ref.ticket_key)
            coverage_by_test_type[ref.test_type] += 1

        # Calculate coverage metrics
        total_jira_tickets = len(jira_tickets)
        covered_tickets = len(tickets_with_tests)
        test_coverage_percentage = (covered_tickets / total_jira_tickets * 100) if total_jira_tickets > 0 else 0

        # Coverage by status
        coverage_by_status = {}
        status_counts = {}

        for ticket in jira_tickets.values():
            status = ticket.status
            status_counts[status] = status_counts.get(status, 0) + 1

            if status not in coverage_by_status:
                coverage_by_status[status] = [0, 0]  # [covered, total]

            coverage_by_status[status][1] += 1
            if ticket.key in tickets_with_tests:
                coverage_by_status[status][0] += 1

        # Convert to tuple format
        coverage_by_status = {status: (covered, total)
                            for status, (covered, total) in coverage_by_status.items()}

        # Coverage by priority
        coverage_by_priority = {}
        for ticket in jira_tickets.values():
            priority = ticket.priority
            if priority not in coverage_by_priority:
                coverage_by_priority[priority] = [0, 0]

            coverage_by_priority[priority][1] += 1
            if ticket.key in tickets_with_tests:
                coverage_by_priority[priority][0] += 1

        coverage_by_priority = {priority: (covered, total)
                              for priority, (covered, total) in coverage_by_priority.items()}

        # AC analysis
        tickets_with_ac = sum(1 for ticket in jira_tickets.values() if ticket.acceptance_criteria)
        tickets_without_ac = total_jira_tickets - tickets_with_ac

        # Find tickets needing AC proposals (high priority tickets without AC)
        tickets_needing_ac_proposals = [
            ticket.key for ticket in jira_tickets.values()
            if not ticket.acceptance_criteria and ticket.priority in ['High', 'Highest']
        ]

        return CompleteCoverageReport(
            total_jira_tickets=total_jira_tickets,
            jira_tickets=jira_tickets,
            tickets_with_tests=covered_tickets,
            tickets_without_tests=total_jira_tickets - covered_tickets,
            test_coverage_percentage=test_coverage_percentage,
            test_references=test_references,
            coverage_by_test_type=coverage_by_test_type,
            coverage_by_status=coverage_by_status,
            coverage_by_priority=coverage_by_priority,
            tickets_with_ac=tickets_with_ac,
            tickets_without_ac=tickets_without_ac,
            tickets_needing_ac_proposals=tickets_needing_ac_proposals
        )

    def print_complete_report(self, report: CompleteCoverageReport):
        """Print detailed complete coverage report."""
        print("\n" + "="*120)
        print("🎯 COMPLETE JIRA + TDD COVERAGE ANALYSIS")
        print("="*120)

        print(f"\n📊 JIRA PROJECT OVERVIEW:")
        print(f"   Total Jira Tickets: {report.total_jira_tickets}")
        print(f"   Tickets with Tests: {report.tickets_with_tests}")
        print(f"   Tickets without Tests: {report.tickets_without_tests}")
        print(f"   Test Coverage: {report.test_coverage_percentage:.1f}%")

        print(f"\n🧪 COVERAGE BY TEST TYPE:")
        for test_type, count in report.coverage_by_test_type.items():
            print(f"   {test_type.capitalize()}: {count} references")

        print(f"\n📋 COVERAGE BY STATUS:")
        for status, (covered, total) in sorted(report.coverage_by_status.items()):
            percentage = (covered / total * 100) if total > 0 else 0
            print(f"   {status}: {covered}/{total} ({percentage:.1f}%)")

        print(f"\n⭐ COVERAGE BY PRIORITY:")
        for priority, (covered, total) in sorted(report.coverage_by_priority.items()):
            percentage = (covered / total * 100) if total > 0 else 0
            print(f"   {priority}: {covered}/{total} ({percentage:.1f}%)")

        print(f"\n📝 ACCEPTANCE CRITERIA:")
        print(f"   Tickets with AC: {report.tickets_with_ac}")
        print(f"   Tickets without AC: {report.tickets_without_ac}")
        ac_percentage = (report.tickets_with_ac / report.total_jira_tickets * 100) if report.total_jira_tickets > 0 else 0
        print(f"   AC Coverage: {ac_percentage:.1f}%")

        if report.tickets_needing_ac_proposals:
            print(f"\n🚨 HIGH PRIORITY TICKETS NEEDING AC ({len(report.tickets_needing_ac_proposals)}):")
            for ticket_key in sorted(report.tickets_needing_ac_proposals)[:10]:  # Show first 10
                ticket = report.jira_tickets[ticket_key]
                print(f"   {ticket_key} [{ticket.status}] - {ticket.summary}")

        # Show uncovered tickets by priority
        uncovered_tickets = [ticket for ticket in report.jira_tickets.values()
                           if ticket.key not in {ref.ticket_key for ref in report.test_references}]

        if uncovered_tickets:
            high_priority_uncovered = [t for t in uncovered_tickets if t.priority in ['High', 'Highest']]
            if high_priority_uncovered:
                print(f"\n🚨 HIGH PRIORITY UNCOVERED TICKETS ({len(high_priority_uncovered)}):")
                for ticket in sorted(high_priority_uncovered, key=lambda x: x.key)[:10]:
                    print(f"   {ticket.key} [{ticket.status}] {ticket.priority} - {ticket.summary}")


def main():
    """Run complete Jira + TDD coverage analysis."""
    try:
        analyzer = CompleteJiraCoverageAnalyzer()
        report = analyzer.analyze_complete_coverage()
        analyzer.print_complete_report(report)
        return 0

    except Exception as e:
        print(f"❌ Complete coverage analysis error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    sys.exit(main())