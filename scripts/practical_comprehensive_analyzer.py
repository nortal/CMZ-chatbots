#!/usr/bin/env python3
"""
Practical Comprehensive TDD Analyzer
Analyzes actual test coverage and provides framework for full Jira integration
"""

import os
import re
import json
import logging
from typing import Dict, List, Set
from dataclasses import dataclass
from datetime import datetime

@dataclass
class TestCoverage:
    """Test coverage analysis results."""
    total_test_files: int
    total_test_methods: int
    ticket_references_found: Set[str]
    test_types: Dict[str, int]
    coverage_gaps: List[str]

class PracticalComprehensiveAnalyzer:
    """Analyzes what we actually have and identifies gaps."""

    def __init__(self):
        self.logger = logging.getLogger('practical_analyzer')

    def analyze_current_state(self) -> Dict:
        """Analyze current test coverage state."""
        self.logger.info("🔍 Analyzing current test coverage state...")

        # Find actual test directory
        repo_root = os.path.dirname(os.getcwd())
        potential_test_dirs = [
            "backend/api/src/main/python/tests",
            "tests",
            "test",
            "spec",
        ]

        test_coverage = None
        for test_dir in potential_test_dirs:
            full_path = os.path.join(repo_root, test_dir)
            if os.path.exists(full_path):
                self.logger.info(f"📁 Found test directory: {test_dir}")
                test_coverage = self._analyze_test_directory(full_path)
                break

        if not test_coverage:
            self.logger.warning("⚠️ No test directory found")
            test_coverage = TestCoverage(0, 0, set(), {}, ["No test directory found"])

        # Analyze current vs required coverage
        analysis = {
            'current_coverage': test_coverage,
            'analysis_timestamp': datetime.now().isoformat(),
            'recommendations': self._generate_recommendations(test_coverage),
            'next_steps': self._generate_next_steps(),
        }

        return analysis

    def _analyze_test_directory(self, test_dir: str) -> TestCoverage:
        """Analyze all tests in a directory."""
        test_files = 0
        test_methods = 0
        ticket_refs = set()
        test_types = {'unit': 0, 'integration': 0, 'e2e': 0, 'functional': 0, 'other': 0}

        for root, dirs, files in os.walk(test_dir):
            for file in files:
                if self._is_test_file(file):
                    file_path = os.path.join(root, file)
                    file_analysis = self._analyze_test_file(file_path)

                    test_files += 1
                    test_methods += file_analysis['test_methods']
                    ticket_refs.update(file_analysis['ticket_refs'])

                    # Categorize test type by directory/file name
                    test_type = self._categorize_test_type(file_path)
                    test_types[test_type] += 1

        coverage_gaps = []
        if test_files < 10:
            coverage_gaps.append("Very few test files found - need more comprehensive testing")
        if len(ticket_refs) < 20:
            coverage_gaps.append("Limited ticket references in tests - need better traceability")

        return TestCoverage(
            total_test_files=test_files,
            total_test_methods=test_methods,
            ticket_references_found=ticket_refs,
            test_types=test_types,
            coverage_gaps=coverage_gaps
        )

    def _is_test_file(self, filename: str) -> bool:
        """Check if file is a test file."""
        test_patterns = [
            '.test.', '.spec.', 'test_', '_test.',
            '.test.py', '.test.js', '.test.ts',
            '.spec.py', '.spec.js', '.spec.ts'
        ]
        return any(pattern in filename.lower() for pattern in test_patterns)

    def _analyze_test_file(self, file_path: str) -> Dict:
        """Analyze a single test file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Count test methods
            test_methods = len(re.findall(r'def test_|it\s*\(|test\s*\(|describe\s*\(', content))

            # Find ticket references
            ticket_patterns = [
                r'PR003946-(\d+)',
                r'CMZ-(\d+)',
                r'JIRA-(\d+)',
                r'#(\d+)',  # GitHub-style issue refs
            ]

            ticket_refs = set()
            for pattern in ticket_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                ticket_refs.update(matches)

            return {
                'test_methods': test_methods,
                'ticket_refs': ticket_refs
            }

        except Exception as e:
            self.logger.warning(f"⚠️ Error analyzing {file_path}: {e}")
            return {'test_methods': 0, 'ticket_refs': set()}

    def _categorize_test_type(self, file_path: str) -> str:
        """Categorize test type based on path/name."""
        path_lower = file_path.lower()

        if 'unit' in path_lower:
            return 'unit'
        elif 'integration' in path_lower:
            return 'integration'
        elif 'e2e' in path_lower or 'end-to-end' in path_lower:
            return 'e2e'
        elif 'functional' in path_lower:
            return 'functional'
        else:
            return 'other'

    def _generate_recommendations(self, coverage: TestCoverage) -> List[str]:
        """Generate recommendations based on current coverage."""
        recommendations = []

        if coverage.total_test_files == 0:
            recommendations.append("🚨 CRITICAL: No test files found. Start with basic unit tests.")

        if coverage.total_test_files < 20:
            recommendations.append("📈 Increase test file count - aim for at least 50+ test files")

        if len(coverage.ticket_references_found) < 10:
            recommendations.append("🎯 Add ticket references to tests for better traceability")

        if coverage.test_types['integration'] < 5:
            recommendations.append("🔗 Add more integration tests for API validation")

        if coverage.test_types['unit'] < coverage.test_types['integration']:
            recommendations.append("⚖️ Balance test pyramid - need more unit tests")

        return recommendations

    def _generate_next_steps(self) -> List[str]:
        """Generate next steps for comprehensive analysis."""
        return [
            "1. **Fix Jira API Access**: Update API endpoints and authentication",
            "2. **Get ALL CMZ Tickets**: Use correct project key and pagination",
            "3. **Extract ALL Acceptance Criteria**: Parse ticket descriptions systematically",
            "4. **Map Each AC to Tests**: Create AC-to-test traceability matrix",
            "5. **Calculate True Coverage**: (Tested ACs / Total ACs) × 100",
            "6. **Identify Coverage Gaps**: List untested ACs and missing tests",
            "7. **Generate Action Items**: Prioritize AC coverage improvements",
        ]

    def create_comprehensive_framework(self) -> str:
        """Create framework for true comprehensive analysis."""
        framework = '''
# Comprehensive TDD Analysis Framework

## Step 1: Jira Integration Fix
```python
# Fix API endpoint (use v3 instead of deprecated v2)
jira_url = "https://nortal.atlassian.net/rest/api/3/search"

# Correct project identification
project_query = "project = 'CMZ' OR project = 'Cougar Mountain Zoo'"

# Get ALL tickets with pagination
for page in range(0, total_pages):
    tickets = get_jira_tickets(start_at=page*50, max_results=50)
```

## Step 2: Acceptance Criteria Extraction
```python
for ticket in all_tickets:
    # Parse description for AC patterns:
    # - "Given/When/Then" scenarios
    # - Bullet points with acceptance criteria
    # - "As a user" stories
    # - Numbered requirements
    acs = extract_all_acceptance_criteria(ticket.description)
```

## Step 3: Test-to-AC Mapping
```python
for ac in all_acceptance_criteria:
    # Find tests that validate this AC:
    # - Keyword matching in test names
    # - Test description analysis
    # - Ticket reference tracing
    covering_tests = find_tests_for_ac(ac)
```

## Step 4: True Coverage Calculation
```python
true_coverage = {
    'total_tickets': len(all_cmz_tickets),
    'total_acs': len(all_acceptance_criteria),
    'tested_acs': len([ac for ac in all_acs if ac.has_tests]),
    'coverage_percentage': (tested_acs / total_acs) * 100,
    'gaps': [ac for ac in all_acs if not ac.has_tests]
}
```

## Expected Results for CMZ Project:
- **100+ tickets** (not 27)
- **500+ acceptance criteria** (estimate 3-5 ACs per ticket)
- **True coverage percentage** (likely 15-30% initially)
- **400+ untested ACs** requiring test creation
'''

        with open('comprehensive_tdd_framework.md', 'w') as f:
            f.write(framework)

        return framework

def main():
    """Run practical comprehensive analysis."""
    try:
        analyzer = PracticalComprehensiveAnalyzer()
        analysis = analyzer.analyze_current_state()

        print("🎯 **Practical TDD Coverage Analysis**")
        print("=" * 50)

        coverage = analysis['current_coverage']

        print(f"\n📊 **Current State:**")
        print(f"• Test Files Found: {coverage.total_test_files}")
        print(f"• Test Methods: {coverage.total_test_methods}")
        print(f"• Ticket References: {len(coverage.ticket_references_found)}")

        print(f"\n🧪 **Test Distribution:**")
        for test_type, count in coverage.test_types.items():
            print(f"• {test_type.title()}: {count}")

        if coverage.ticket_references_found:
            print(f"\n🎫 **Ticket References Found:**")
            sorted_refs = sorted(list(coverage.ticket_references_found))[:10]
            for ref in sorted_refs:
                print(f"• {ref}")
            if len(coverage.ticket_references_found) > 10:
                print(f"• ... and {len(coverage.ticket_references_found) - 10} more")

        print(f"\n⚠️ **Coverage Gaps:**")
        for gap in coverage.coverage_gaps:
            print(f"• {gap}")

        print(f"\n🎯 **Recommendations:**")
        for rec in analysis['recommendations']:
            print(f"{rec}")

        print(f"\n🚀 **Next Steps for TRUE Comprehensive Analysis:**")
        for step in analysis['next_steps']:
            print(f"{step}")

        # Create framework
        framework = analyzer.create_comprehensive_framework()
        print(f"\n📋 **Framework created**: comprehensive_tdd_framework.md")

        # Save analysis
        with open('practical_tdd_analysis.json', 'w') as f:
            # Convert sets to lists for JSON serialization
            coverage.ticket_references_found = list(coverage.ticket_references_found)
            json.dump(analysis, f, indent=2, default=str)

        print(f"\n💾 **Analysis saved**: practical_tdd_analysis.json")

        return 0

    except Exception as e:
        print(f"❌ Analysis error: {e}")
        return 1

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    sys.exit(main())