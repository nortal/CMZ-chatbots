#!/usr/bin/env python3
"""
Comprehensive Jira TDD Analyzer
Evaluates ALL CMZ Jira tickets and their ACs against ALL existing tests
"""

import requests
import logging
import os
import re
import json
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import base64

@dataclass
class AcceptanceCriteria:
    """Represents a single acceptance criteria."""
    id: str
    text: str
    ticket_key: str
    has_test: bool = False
    test_references: List[str] = None

    def __post_init__(self):
        if self.test_references is None:
            self.test_references = []

@dataclass
class JiraTicket:
    """Represents a Jira ticket with full analysis."""
    key: str
    summary: str
    description: str
    status: str
    issue_type: str
    acceptance_criteria: List[AcceptanceCriteria]
    has_any_tests: bool = False
    test_coverage_percentage: float = 0.0
    test_references: List[str] = None

    def __post_init__(self):
        if self.test_references is None:
            self.test_references = []

@dataclass
class TestFile:
    """Represents a test file with its content."""
    path: str
    content: str
    test_methods: List[str]
    ticket_references: Set[str]

class ComprehensiveJiraTDDAnalyzer:
    """Analyzes ALL Jira tickets against ALL tests comprehensively."""

    def __init__(self):
        self.logger = logging.getLogger('comprehensive_jira_tdd')
        self.jira_base_url = "https://nortal.atlassian.net"
        self.jira_auth = self._get_jira_auth()
        self.project_key = "PR003946"  # CMZ project key

        # Test discovery
        self.test_files: List[TestFile] = []
        self.all_tickets: List[JiraTicket] = []

    def _get_jira_auth(self) -> Optional[str]:
        """Get Jira authentication from environment."""
        email = os.environ.get('JIRA_EMAIL', 'kc.stegbauer@nortal.com')
        token = os.environ.get('JIRA_API_TOKEN')

        if not token:
            self.logger.error("❌ JIRA_API_TOKEN environment variable not set")
            return None

        # Create basic auth header
        auth_string = f"{email}:{token}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        return f"Basic {auth_b64}"

    def analyze_comprehensive_coverage(self) -> Dict:
        """Perform comprehensive analysis of ALL tickets vs ALL tests."""
        self.logger.info("🔍 Starting comprehensive Jira TDD analysis...")

        # Step 1: Discover all test files
        self._discover_all_test_files()

        # Step 2: Get ALL Jira tickets
        self._get_all_jira_tickets()

        # Step 3: Analyze AC to test mapping
        self._analyze_ac_to_test_mapping()

        # Step 4: Calculate comprehensive coverage metrics
        coverage_metrics = self._calculate_comprehensive_metrics()

        self.logger.info("✅ Comprehensive analysis completed")
        return coverage_metrics

    def _discover_all_test_files(self):
        """Discover all test files in the project."""
        self.logger.info("🔍 Discovering all test files...")

        test_directories = [
            "backend/api/src/main/python/tests/unit",
            "backend/api/src/main/python/tests/integration",
            "backend/api/src/main/python/tests/playwright",
            "backend/api/src/main/python/tests/functional",
            "tests",  # Alternative test directory
        ]

        repo_root = os.path.dirname(os.getcwd())

        for test_dir in test_directories:
            full_test_dir = os.path.join(repo_root, test_dir)
            if os.path.exists(full_test_dir):
                self._scan_test_directory(full_test_dir)

        self.logger.info(f"📁 Discovered {len(self.test_files)} test files")

    def _scan_test_directory(self, directory: str):
        """Scan a directory for test files."""
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(('.py', '.js', '.ts', '.spec.js', '.spec.ts', '.test.js', '.test.ts')):
                    file_path = os.path.join(root, file)
                    self._analyze_test_file(file_path)

    def _analyze_test_file(self, file_path: str):
        """Analyze a single test file for ticket references and test methods."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Find test methods
            test_methods = []
            # Python test methods
            test_methods.extend(re.findall(r'def (test_\w+)', content))
            # JavaScript/TypeScript test methods
            test_methods.extend(re.findall(r'(?:it|test)\s*\(\s*[\'"`]([^\'"`]+)[\'"`]', content))

            # Find ticket references
            ticket_refs = set(re.findall(r'PR003946-(\d+)', content))

            test_file = TestFile(
                path=file_path,
                content=content,
                test_methods=test_methods,
                ticket_references=ticket_refs
            )

            self.test_files.append(test_file)

        except Exception as e:
            self.logger.warning(f"⚠️ Error analyzing test file {file_path}: {e}")

    def _get_all_jira_tickets(self):
        """Get ALL tickets from the CMZ Jira project."""
        self.logger.info("📋 Fetching ALL CMZ Jira tickets...")

        if not self.jira_auth:
            self.logger.error("❌ Cannot fetch Jira tickets - authentication not configured")
            return

        # Get all tickets from the project using JQL
        jql_query = f"project = {self.project_key} ORDER BY key ASC"

        start_at = 0
        max_results = 50
        all_tickets = []

        while True:
            try:
                url = f"{self.jira_base_url}/rest/api/3/search"
                params = {
                    'jql': jql_query,
                    'startAt': start_at,
                    'maxResults': max_results,
                    'fields': 'key,summary,description,status,issuetype,customfield_10028'  # customfield for AC
                }

                headers = {
                    'Authorization': self.jira_auth,
                    'Content-Type': 'application/json'
                }

                response = requests.get(url, params=params, headers=headers, timeout=30)

                if response.status_code == 200:
                    data = response.json()
                    issues = data.get('issues', [])

                    if not issues:
                        break  # No more tickets

                    for issue in issues:
                        ticket = self._parse_jira_ticket(issue)
                        if ticket:
                            all_tickets.append(ticket)

                    start_at += max_results

                    if len(issues) < max_results:
                        break  # Last page

                else:
                    self.logger.error(f"❌ Jira API error: HTTP {response.status_code}")
                    break

            except Exception as e:
                self.logger.error(f"❌ Error fetching Jira tickets: {e}")
                break

        self.all_tickets = all_tickets
        self.logger.info(f"📊 Fetched {len(all_tickets)} total CMZ tickets")

    def _parse_jira_ticket(self, issue: Dict) -> Optional[JiraTicket]:
        """Parse a Jira issue into a JiraTicket object."""
        try:
            fields = issue.get('fields', {})

            # Extract basic fields
            key = issue.get('key', '')
            summary = fields.get('summary', '')
            description = fields.get('description', {})
            status = fields.get('status', {}).get('name', '')
            issue_type = fields.get('issuetype', {}).get('name', '')

            # Parse description content
            desc_text = self._extract_description_text(description)

            # Extract acceptance criteria
            ac_list = self._extract_acceptance_criteria(desc_text, key)

            ticket = JiraTicket(
                key=key,
                summary=summary,
                description=desc_text,
                status=status,
                issue_type=issue_type,
                acceptance_criteria=ac_list
            )

            return ticket

        except Exception as e:
            self.logger.warning(f"⚠️ Error parsing ticket: {e}")
            return None

    def _extract_description_text(self, description: Dict) -> str:
        """Extract plain text from Jira description content."""
        if not description:
            return ""

        try:
            # Handle Atlassian Document Format (ADF)
            if isinstance(description, dict) and 'content' in description:
                return self._extract_adf_text(description)
            elif isinstance(description, str):
                return description
            else:
                return str(description)
        except Exception:
            return str(description)

    def _extract_adf_text(self, adf_content: Dict) -> str:
        """Extract text from Atlassian Document Format."""
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

    def _extract_acceptance_criteria(self, description: str, ticket_key: str) -> List[AcceptanceCriteria]:
        """Extract acceptance criteria from ticket description."""
        ac_list = []

        # Common AC patterns
        ac_patterns = [
            r'(?:Acceptance Criteria|AC|Given|When|Then)[:.]?\s*(.+?)(?=\n(?:Acceptance Criteria|AC|Given|When|Then)|$)',
            r'(?:✓|✔|☑|\*|\-|\d+\.)\s*(.+?)(?=\n(?:✓|✔|☑|\*|\-|\d+\.)|$)',
            r'(?:As a|I want|So that)\s+(.+?)(?=\n(?:As a|I want|So that)|$)'
        ]

        for i, pattern in enumerate(ac_patterns):
            matches = re.findall(pattern, description, re.IGNORECASE | re.DOTALL)
            for j, match in enumerate(matches):
                ac_text = match.strip()
                if len(ac_text) > 10:  # Filter out too short matches
                    ac = AcceptanceCriteria(
                        id=f"{ticket_key}-AC-{i+1}-{j+1}",
                        text=ac_text,
                        ticket_key=ticket_key
                    )
                    ac_list.append(ac)

        # If no AC found, create placeholder
        if not ac_list:
            ac = AcceptanceCriteria(
                id=f"{ticket_key}-AC-IMPLIED",
                text="Implied acceptance criteria based on ticket summary",
                ticket_key=ticket_key
            )
            ac_list.append(ac)

        return ac_list

    def _analyze_ac_to_test_mapping(self):
        """Map acceptance criteria to existing tests."""
        self.logger.info("🔗 Analyzing AC to test mapping...")

        for ticket in self.all_tickets:
            # Check if ticket is referenced in any test file
            for test_file in self.test_files:
                ticket_num = ticket.key.split('-')[-1]
                if ticket_num in test_file.ticket_references:
                    ticket.has_any_tests = True
                    ticket.test_references.append(test_file.path)

            # Analyze each AC for test coverage
            covered_acs = 0
            for ac in ticket.acceptance_criteria:
                # Look for tests that might cover this AC
                ac_keywords = self._extract_ac_keywords(ac.text)

                for test_file in self.test_files:
                    # Check if test methods match AC keywords
                    for test_method in test_file.test_methods:
                        if self._test_covers_ac(test_method, ac_keywords):
                            ac.has_test = True
                            ac.test_references.append(f"{test_file.path}::{test_method}")
                            covered_acs += 1
                            break

            # Calculate coverage percentage for this ticket
            if ticket.acceptance_criteria:
                ticket.test_coverage_percentage = (covered_acs / len(ticket.acceptance_criteria)) * 100

    def _extract_ac_keywords(self, ac_text: str) -> List[str]:
        """Extract keywords from acceptance criteria text."""
        # Remove common words and extract meaningful terms
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'should', 'will', 'can', 'must'}

        # Extract words, convert to lowercase, filter stop words
        words = re.findall(r'\b\w+\b', ac_text.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 3]

        return keywords[:5]  # Return top 5 keywords

    def _test_covers_ac(self, test_method: str, ac_keywords: List[str]) -> bool:
        """Check if a test method likely covers an acceptance criteria."""
        test_method_lower = test_method.lower()

        # Check if test method contains AC keywords
        keyword_matches = sum(1 for keyword in ac_keywords if keyword in test_method_lower)

        # Consider it a match if 2+ keywords match
        return keyword_matches >= 2

    def _calculate_comprehensive_metrics(self) -> Dict:
        """Calculate comprehensive coverage metrics."""
        total_tickets = len(self.all_tickets)
        total_acs = sum(len(ticket.acceptance_criteria) for ticket in self.all_tickets)

        tickets_with_tests = sum(1 for ticket in self.all_tickets if ticket.has_any_tests)
        acs_with_tests = sum(1 for ticket in self.all_tickets for ac in ticket.acceptance_criteria if ac.has_test)

        # Calculate coverage by status
        status_breakdown = {}
        for ticket in self.all_tickets:
            status = ticket.status
            if status not in status_breakdown:
                status_breakdown[status] = {'total': 0, 'with_tests': 0}
            status_breakdown[status]['total'] += 1
            if ticket.has_any_tests:
                status_breakdown[status]['with_tests'] += 1

        # Calculate coverage by issue type
        type_breakdown = {}
        for ticket in self.all_tickets:
            issue_type = ticket.issue_type
            if issue_type not in type_breakdown:
                type_breakdown[issue_type] = {'total': 0, 'with_tests': 0}
            type_breakdown[issue_type]['total'] += 1
            if ticket.has_any_tests:
                type_breakdown[issue_type]['with_tests'] += 1

        metrics = {
            'total_tickets': total_tickets,
            'total_acceptance_criteria': total_acs,
            'tickets_with_tests': tickets_with_tests,
            'acs_with_tests': acs_with_tests,
            'ticket_coverage_percentage': (tickets_with_tests / total_tickets * 100) if total_tickets > 0 else 0,
            'ac_coverage_percentage': (acs_with_tests / total_acs * 100) if total_acs > 0 else 0,
            'status_breakdown': status_breakdown,
            'type_breakdown': type_breakdown,
            'test_files_analyzed': len(self.test_files),
            'analysis_timestamp': datetime.now().isoformat(),
            'uncovered_tickets': [ticket.key for ticket in self.all_tickets if not ticket.has_any_tests],
            'high_coverage_tickets': [ticket.key for ticket in self.all_tickets if ticket.test_coverage_percentage >= 80],
            'low_coverage_tickets': [ticket.key for ticket in self.all_tickets if ticket.test_coverage_percentage < 30 and ticket.has_any_tests]
        }

        return metrics

def main():
    """Run comprehensive Jira TDD analysis."""
    try:
        analyzer = ComprehensiveJiraTDDAnalyzer()
        metrics = analyzer.analyze_comprehensive_coverage()

        print("🎯 **Comprehensive CMZ TDD Coverage Analysis**")
        print("=" * 60)

        print(f"\n📊 **Overall Metrics:**")
        print(f"• Total CMZ Tickets: {metrics['total_tickets']}")
        print(f"• Total Acceptance Criteria: {metrics['total_acceptance_criteria']}")
        print(f"• Tickets with Tests: {metrics['tickets_with_tests']}")
        print(f"• ACs with Tests: {metrics['acs_with_tests']}")

        print(f"\n📈 **Coverage Percentages:**")
        print(f"• Ticket Coverage: {metrics['ticket_coverage_percentage']:.1f}%")
        print(f"• AC Coverage: {metrics['ac_coverage_percentage']:.1f}%")

        print(f"\n📋 **Status Breakdown:**")
        for status, data in metrics['status_breakdown'].items():
            coverage = (data['with_tests'] / data['total'] * 100) if data['total'] > 0 else 0
            print(f"• {status}: {data['with_tests']}/{data['total']} ({coverage:.1f}%)")

        print(f"\n🏷️ **Issue Type Breakdown:**")
        for issue_type, data in metrics['type_breakdown'].items():
            coverage = (data['with_tests'] / data['total'] * 100) if data['total'] > 0 else 0
            print(f"• {issue_type}: {data['with_tests']}/{data['total']} ({coverage:.1f}%)")

        print(f"\n❌ **Uncovered Tickets:** {len(metrics['uncovered_tickets'])}")
        if len(metrics['uncovered_tickets']) <= 20:
            for ticket in metrics['uncovered_tickets'][:10]:
                print(f"  - {ticket}")
            if len(metrics['uncovered_tickets']) > 10:
                print(f"  ... and {len(metrics['uncovered_tickets']) - 10} more")

        # Save detailed report
        with open('comprehensive_tdd_analysis.json', 'w') as f:
            json.dump(metrics, f, indent=2)

        print(f"\n📄 Detailed report saved to: comprehensive_tdd_analysis.json")

        return 0

    except Exception as e:
        print(f"❌ Comprehensive analysis error: {e}")
        return 1

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    sys.exit(main())