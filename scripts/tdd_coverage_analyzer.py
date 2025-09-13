#!/usr/bin/env python3
"""
Comprehensive TDD Coverage Analyzer
Analyzes test coverage across all Jira tickets and test types
"""

import re
import json
import requests
import logging
from datetime import datetime
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass
from pathlib import Path
import subprocess
import os

from tdd_config import TDDConfigManager


@dataclass
class TicketInfo:
    """Information about a Jira ticket."""
    key: str
    status: str
    summary: str
    ticket_type: str
    priority: str


@dataclass
class TestCoverage:
    """Test coverage information for a ticket."""
    ticket_key: str
    has_unit_test: bool = False
    has_integration_test: bool = False
    has_playwright_test: bool = False
    has_functional_test: bool = False
    test_files: List[str] = None

    def __post_init__(self):
        if self.test_files is None:
            self.test_files = []

    @property
    def is_covered(self) -> bool:
        """Returns True if ticket has any test coverage."""
        return any([self.has_unit_test, self.has_integration_test,
                   self.has_playwright_test, self.has_functional_test])

    @property
    def coverage_types(self) -> List[str]:
        """Returns list of coverage types for this ticket."""
        types = []
        if self.has_unit_test:
            types.append("Unit")
        if self.has_integration_test:
            types.append("Integration")
        if self.has_playwright_test:
            types.append("Playwright")
        if self.has_functional_test:
            types.append("Functional")
        return types


@dataclass
class CoverageReport:
    """Complete TDD coverage report."""
    total_tickets: int
    covered_tickets: int
    coverage_percentage: float
    tickets_by_status: Dict[str, int]
    coverage_by_status: Dict[str, Tuple[int, int]]  # (covered, total)
    coverage_by_type: Dict[str, int]
    uncovered_tickets: List[str]
    ticket_details: Dict[str, TicketInfo]
    coverage_details: Dict[str, TestCoverage]


class TDDCoverageAnalyzer:
    """Comprehensive TDD coverage analyzer."""

    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger('tdd_coverage')

        # Patterns for ticket extraction
        self.ticket_pattern = r'PR003946-(\d+)'

        # Test file patterns
        self.test_patterns = {
            'unit': r'test_.*\.py$',
            'integration': r'test_.*\.py$',
            'playwright': r'.*\.spec\.js$',
            'functional': r'test_.*\.py$'
        }

        # Test directories
        self.test_directories = {
            'unit': 'backend/api/src/main/python/tests/unit',
            'integration': 'backend/api/src/main/python/tests/integration',
            'playwright': 'backend/api/src/main/python/tests/playwright',
            'functional': 'backend/api/src/main/python/tests/functional'
        }

    def analyze_complete_coverage(self) -> CoverageReport:
        """Perform complete TDD coverage analysis."""
        self.logger.info("🔍 Starting comprehensive TDD coverage analysis...")

        # Step 1: Get all tickets from Jira
        self.logger.info("📋 Querying Jira for all tickets...")
        all_tickets = self._get_all_jira_tickets()
        self.logger.info(f"📊 Found {len(all_tickets)} total tickets in Jira")

        # Step 2: Analyze test coverage for all tickets
        self.logger.info("🧪 Analyzing test coverage across all test types...")
        coverage_data = self._analyze_test_coverage()

        # Step 3: Cross-reference tickets with coverage
        self.logger.info("🔗 Cross-referencing tickets with test coverage...")
        coverage_report = self._generate_coverage_report(all_tickets, coverage_data)

        self.logger.info("✅ TDD coverage analysis completed")
        return coverage_report

    def _get_all_jira_tickets(self) -> Dict[str, TicketInfo]:
        """Get all tickets from Jira project regardless of status."""
        try:
            jql = 'project = PR003946 ORDER BY key ASC'

            response = requests.get(
                f"{self.config.jira_base_url}/rest/api/3/search",
                headers={
                    "Authorization": f"Basic {self.config.jira_credentials}",
                    "Content-Type": "application/json"
                },
                params={
                    'jql': jql,
                    'fields': 'key,status,summary,issuetype,priority',
                    'maxResults': 1000  # Get all tickets
                },
                timeout=30
            )

            if response.status_code != 200:
                self.logger.error(f"❌ Jira API error: HTTP {response.status_code}")
                return {}

            tickets_data = response.json()
            tickets = {}

            for issue in tickets_data.get('issues', []):
                key = issue['key']
                tickets[key] = TicketInfo(
                    key=key,
                    status=issue['fields']['status']['name'],
                    summary=issue['fields']['summary'],
                    ticket_type=issue['fields']['issuetype']['name'],
                    priority=issue['fields']['priority']['name'] if issue['fields']['priority'] else 'None'
                )

            self.logger.info(f"📋 Retrieved {len(tickets)} tickets from Jira")
            return tickets

        except Exception as e:
            self.logger.error(f"❌ Error querying Jira: {e}")
            return {}

    def _analyze_test_coverage(self) -> Dict[str, TestCoverage]:
        """Analyze test coverage across all test types."""
        coverage_data = {}

        # Get repository root
        current_dir = os.path.dirname(os.path.abspath(__file__))
        repo_root = os.path.dirname(current_dir)

        # Search each test directory type
        for test_type, test_dir in self.test_directories.items():
            full_test_path = os.path.join(repo_root, test_dir)

            if not os.path.exists(full_test_path):
                self.logger.warning(f"⚠️ Test directory not found: {full_test_path}")
                continue

            self.logger.info(f"🔍 Analyzing {test_type} tests in {test_dir}")

            # Find all test files in directory
            test_files = self._find_test_files(full_test_path, self.test_patterns[test_type])

            for test_file in test_files:
                # Extract ticket references from each test file
                tickets_in_file = self._extract_tickets_from_file(test_file)

                for ticket_num in tickets_in_file:
                    ticket_key = f"PR003946-{ticket_num}"

                    if ticket_key not in coverage_data:
                        coverage_data[ticket_key] = TestCoverage(ticket_key=ticket_key)

                    # Mark coverage type
                    if test_type == 'unit':
                        coverage_data[ticket_key].has_unit_test = True
                    elif test_type == 'integration':
                        coverage_data[ticket_key].has_integration_test = True
                    elif test_type == 'playwright':
                        coverage_data[ticket_key].has_playwright_test = True
                    elif test_type == 'functional':
                        coverage_data[ticket_key].has_functional_test = True

                    coverage_data[ticket_key].test_files.append(test_file)

        self.logger.info(f"📊 Found test coverage for {len(coverage_data)} tickets")
        return coverage_data

    def _find_test_files(self, directory: str, pattern: str) -> List[str]:
        """Find all test files matching pattern in directory."""
        test_files = []

        try:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if re.search(pattern, file):
                        test_files.append(os.path.join(root, file))
        except Exception as e:
            self.logger.warning(f"⚠️ Error searching {directory}: {e}")

        return test_files

    def _extract_tickets_from_file(self, file_path: str) -> Set[str]:
        """Extract PR003946-XX ticket numbers from a file."""
        tickets = set()

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

                # Find all PR003946-XX patterns
                matches = re.findall(self.ticket_pattern, content)
                tickets.update(matches)

        except Exception as e:
            self.logger.warning(f"⚠️ Error reading {file_path}: {e}")

        return tickets

    def _generate_coverage_report(self, tickets: Dict[str, TicketInfo],
                                coverage_data: Dict[str, TestCoverage]) -> CoverageReport:
        """Generate comprehensive coverage report."""

        # Count tickets by status
        tickets_by_status = {}
        for ticket in tickets.values():
            status = ticket.status
            tickets_by_status[status] = tickets_by_status.get(status, 0) + 1

        # Count coverage by status
        coverage_by_status = {}
        for status in tickets_by_status.keys():
            status_tickets = [t for t in tickets.values() if t.status == status]
            covered_count = sum(1 for t in status_tickets
                              if t.key in coverage_data and coverage_data[t.key].is_covered)
            coverage_by_status[status] = (covered_count, len(status_tickets))

        # Count coverage by test type
        coverage_by_type = {
            'Unit': sum(1 for c in coverage_data.values() if c.has_unit_test),
            'Integration': sum(1 for c in coverage_data.values() if c.has_integration_test),
            'Playwright': sum(1 for c in coverage_data.values() if c.has_playwright_test),
            'Functional': sum(1 for c in coverage_data.values() if c.has_functional_test)
        }

        # Find uncovered tickets
        uncovered_tickets = []
        for ticket_key, ticket_info in tickets.items():
            if ticket_key not in coverage_data or not coverage_data[ticket_key].is_covered:
                uncovered_tickets.append(ticket_key)

        # Calculate overall coverage
        covered_count = len([t for t in tickets.keys()
                           if t in coverage_data and coverage_data[t].is_covered])
        total_count = len(tickets)
        coverage_percentage = (covered_count / total_count * 100) if total_count > 0 else 0

        return CoverageReport(
            total_tickets=total_count,
            covered_tickets=covered_count,
            coverage_percentage=coverage_percentage,
            tickets_by_status=tickets_by_status,
            coverage_by_status=coverage_by_status,
            coverage_by_type=coverage_by_type,
            uncovered_tickets=uncovered_tickets,
            ticket_details=tickets,
            coverage_details=coverage_data
        )

    def print_coverage_report(self, report: CoverageReport):
        """Print detailed coverage report."""
        print("\n" + "="*80)
        print("🎯 COMPREHENSIVE TDD COVERAGE REPORT")
        print("="*80)

        print(f"\n📊 OVERALL COVERAGE:")
        print(f"   Total Tickets: {report.total_tickets}")
        print(f"   Covered Tickets: {report.covered_tickets}")
        print(f"   Coverage Percentage: {report.coverage_percentage:.1f}%")

        print(f"\n📋 TICKETS BY STATUS:")
        for status, count in sorted(report.tickets_by_status.items()):
            covered, total = report.coverage_by_status.get(status, (0, count))
            coverage_pct = (covered / total * 100) if total > 0 else 0
            print(f"   {status}: {covered}/{total} covered ({coverage_pct:.1f}%)")

        print(f"\n🧪 COVERAGE BY TEST TYPE:")
        for test_type, count in report.coverage_by_type.items():
            print(f"   {test_type}: {count} tickets")

        print(f"\n❌ UNCOVERED TICKETS ({len(report.uncovered_tickets)}):")
        for ticket_key in sorted(report.uncovered_tickets):
            if ticket_key in report.ticket_details:
                ticket = report.ticket_details[ticket_key]
                print(f"   {ticket_key} [{ticket.status}]: {ticket.summary}")
            else:
                print(f"   {ticket_key}: (Referenced in tests but not found in Jira)")


def main():
    """Test the coverage analyzer."""
    try:
        config_manager = TDDConfigManager()
        config = config_manager.load_configuration()

        analyzer = TDDCoverageAnalyzer(config)
        report = analyzer.analyze_complete_coverage()
        analyzer.print_coverage_report(report)

        return 0

    except Exception as e:
        print(f"❌ Coverage analysis error: {e}")
        return 1


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    sys.exit(main())