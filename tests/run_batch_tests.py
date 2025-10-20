#!/usr/bin/env python3

"""
Batch Test Execution System for CMZ TDD Framework
Executes multiple tickets systematically with comprehensive reporting
"""

import json
import os
import sys
import subprocess
import time
from datetime import datetime
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional

class BatchTestExecutor:
    def __init__(self, max_workers=3):
        self.max_workers = max_workers
        self.results = []
        self.start_time = None
        self.end_time = None
        self.reports_dir = Path('tests/batch_reports')
        self.reports_dir.mkdir(exist_ok=True)

    def load_available_tickets(self) -> List[str]:
        """Load all tickets that have test specifications"""
        tickets = []
        test_categories = ['integration', 'unit', 'playwright', 'security']

        for category in test_categories:
            category_path = Path(f'tests/{category}')
            if category_path.exists():
                for ticket_dir in category_path.iterdir():
                    if ticket_dir.is_dir() and ticket_dir.name.startswith('PR003946-'):
                        howto_file = ticket_dir / f"{ticket_dir.name}-howto-test.md"
                        if howto_file.exists():
                            tickets.append(ticket_dir.name)

        return sorted(list(set(tickets)))

    def execute_single_ticket(self, ticket_key: str) -> Dict[str, Any]:
        """Execute test for a single ticket"""
        print(f"🧪 Executing: {ticket_key}")
        start_time = datetime.now()

        try:
            # Run the test execution script
            result = subprocess.run([
                'python3', 'tests/execute_test.py', ticket_key
            ], capture_output=True, text=True, timeout=300)  # 5 min timeout

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            # Parse exit code for status
            status_map = {0: 'PASS', 1: 'FAIL', 2: 'SKIP', 3: 'ERROR'}
            status = status_map.get(result.returncode, 'ERROR')

            return {
                'ticket': ticket_key,
                'status': status,
                'duration': duration,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'stdout': result.stdout,
                'stderr': result.stderr,
                'exit_code': result.returncode
            }

        except subprocess.TimeoutExpired:
            return {
                'ticket': ticket_key,
                'status': 'TIMEOUT',
                'duration': 300.0,
                'start_time': start_time.isoformat(),
                'end_time': datetime.now().isoformat(),
                'stdout': '',
                'stderr': 'Test execution timed out after 5 minutes',
                'exit_code': 124
            }
        except Exception as e:
            return {
                'ticket': ticket_key,
                'status': 'ERROR',
                'duration': 0.0,
                'start_time': start_time.isoformat(),
                'end_time': datetime.now().isoformat(),
                'stdout': '',
                'stderr': str(e),
                'exit_code': 125
            }

    def run_batch_tests(self, ticket_filter: Optional[str] = None,
                       category_filter: Optional[str] = None,
                       max_tickets: Optional[int] = None) -> Dict[str, Any]:
        """Run batch tests with optional filtering"""

        print("🎯 CMZ TDD BATCH TEST EXECUTION")
        print("=" * 50)

        self.start_time = datetime.now()

        # Load available tickets
        available_tickets = self.load_available_tickets()

        # Apply filters
        if category_filter:
            filtered_tickets = []
            category_path = Path(f'tests/{category_filter}')
            if category_path.exists():
                for ticket in available_tickets:
                    ticket_path = category_path / ticket
                    if ticket_path.exists():
                        filtered_tickets.append(ticket)
            available_tickets = filtered_tickets

        if ticket_filter:
            available_tickets = [t for t in available_tickets if ticket_filter in t]

        if max_tickets:
            available_tickets = available_tickets[:max_tickets]

        print(f"📋 Found {len(available_tickets)} tickets to test")
        if len(available_tickets) == 0:
            print("❌ No tickets match the specified criteria")
            return {'results': [], 'summary': {}}

        print(f"🔧 Using {self.max_workers} parallel workers")
        print(f"⏱️ Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # Execute tests in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all jobs
            future_to_ticket = {
                executor.submit(self.execute_single_ticket, ticket): ticket
                for ticket in available_tickets
            }

            # Collect results as they complete
            completed = 0
            for future in as_completed(future_to_ticket):
                ticket = future_to_ticket[future]
                try:
                    result = future.result()
                    self.results.append(result)
                    completed += 1

                    status_emoji = {
                        'PASS': '✅', 'FAIL': '❌', 'SKIP': '⏭️',
                        'ERROR': '🚨', 'TIMEOUT': '⏰'
                    }
                    emoji = status_emoji.get(result['status'], '❓')

                    print(f"{emoji} {ticket}: {result['status']} ({result['duration']:.1f}s) "
                          f"[{completed}/{len(available_tickets)}]")

                except Exception as e:
                    print(f"🚨 {ticket}: Execution failed - {str(e)}")

        self.end_time = datetime.now()

        # Generate summary
        summary = self.generate_summary()

        # Save results
        self.save_results(summary)

        print()
        print("📊 BATCH EXECUTION SUMMARY")
        print("=" * 50)
        self.print_summary(summary)

        return {
            'results': self.results,
            'summary': summary
        }

    def generate_summary(self) -> Dict[str, Any]:
        """Generate execution summary statistics"""
        if not self.results:
            return {}

        # Count by status
        status_counts = {}
        total_duration = 0

        for result in self.results:
            status = result['status']
            status_counts[status] = status_counts.get(status, 0) + 1
            total_duration += result['duration']

        total_tests = len(self.results)
        pass_rate = (status_counts.get('PASS', 0) / total_tests * 100) if total_tests > 0 else 0

        # Category breakdown
        category_stats = {}
        for result in self.results:
            ticket = result['ticket']
            # Determine category by checking which directory exists
            for category in ['integration', 'unit', 'playwright', 'security']:
                category_path = Path(f'tests/{category}/{ticket}')
                if category_path.exists():
                    if category not in category_stats:
                        category_stats[category] = {'total': 0, 'passed': 0}
                    category_stats[category]['total'] += 1
                    if result['status'] == 'PASS':
                        category_stats[category]['passed'] += 1
                    break

        execution_time = (self.end_time - self.start_time).total_seconds()

        return {
            'execution_summary': {
                'total_tests': total_tests,
                'total_duration': total_duration,
                'execution_time': execution_time,
                'start_time': self.start_time.isoformat(),
                'end_time': self.end_time.isoformat(),
                'parallel_efficiency': (total_duration / execution_time) if execution_time > 0 else 0
            },
            'status_breakdown': status_counts,
            'pass_rate': pass_rate,
            'category_breakdown': category_stats,
            'failed_tickets': [r['ticket'] for r in self.results if r['status'] == 'FAIL'],
            'error_tickets': [r['ticket'] for r in self.results if r['status'] == 'ERROR']
        }

    def print_summary(self, summary: Dict[str, Any]):
        """Print summary to console"""
        exec_summary = summary['execution_summary']
        status_counts = summary['status_breakdown']

        print(f"⏱️ Total Execution Time: {exec_summary['execution_time']:.1f} seconds")
        print(f"🧪 Total Tests: {exec_summary['total_tests']}")
        print(f"📈 Pass Rate: {summary['pass_rate']:.1f}%")
        print(f"⚡ Parallel Efficiency: {exec_summary['parallel_efficiency']:.1f}x")
        print()

        print("📊 Status Breakdown:")
        for status, count in status_counts.items():
            emoji = {'PASS': '✅', 'FAIL': '❌', 'SKIP': '⏭️', 'ERROR': '🚨', 'TIMEOUT': '⏰'}.get(status, '❓')
            print(f"  {emoji} {status}: {count}")
        print()

        if summary['category_breakdown']:
            print("📂 Category Breakdown:")
            for category, stats in summary['category_breakdown'].items():
                rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
                print(f"  {category.title()}: {stats['passed']}/{stats['total']} ({rate:.1f}%)")
            print()

        if summary['failed_tickets']:
            print(f"❌ Failed Tickets ({len(summary['failed_tickets'])}):")
            for ticket in summary['failed_tickets']:
                print(f"  - {ticket}")
            print()

        if summary['error_tickets']:
            print(f"🚨 Error Tickets ({len(summary['error_tickets'])}):")
            for ticket in summary['error_tickets']:
                print(f"  - {ticket}")

    def save_results(self, summary: Dict[str, Any]):
        """Save results and summary to files"""
        timestamp = self.start_time.strftime('%Y-%m-%d-%H%M%S')

        # Save detailed results
        results_file = self.reports_dir / f'batch_results_{timestamp}.json'
        with open(results_file, 'w') as f:
            json.dump({
                'summary': summary,
                'detailed_results': self.results
            }, f, indent=2, default=str)

        # Save summary report
        report_file = self.reports_dir / f'batch_report_{timestamp}.md'
        self.generate_markdown_report(report_file, summary)

        print(f"💾 Results saved:")
        print(f"  📄 Detailed: {results_file}")
        print(f"  📋 Report: {report_file}")

    def generate_markdown_report(self, report_file: Path, summary: Dict[str, Any]):
        """Generate comprehensive markdown report"""
        exec_summary = summary['execution_summary']

        content = f"""# CMZ TDD Batch Test Report

**Generated**: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}
**Execution Time**: {exec_summary['execution_time']:.1f} seconds
**Total Tests**: {exec_summary['total_tests']}
**Overall Pass Rate**: {summary['pass_rate']:.1f}%

## Executive Summary

This batch execution tested {exec_summary['total_tests']} tickets across the CMZ TDD framework with a {summary['pass_rate']:.1f}% pass rate. The parallel execution achieved {exec_summary['parallel_efficiency']:.1f}x efficiency using {self.max_workers} workers.

## Status Breakdown

| Status | Count | Percentage |
|--------|-------|------------|
"""

        total = exec_summary['total_tests']
        for status, count in summary['status_breakdown'].items():
            percentage = (count / total * 100) if total > 0 else 0
            emoji = {'PASS': '✅', 'FAIL': '❌', 'SKIP': '⏭️', 'ERROR': '🚨', 'TIMEOUT': '⏰'}.get(status, '❓')
            content += f"| {emoji} {status} | {count} | {percentage:.1f}% |\n"

        if summary['category_breakdown']:
            content += "\n## Category Performance\n\n"
            content += "| Category | Passed | Total | Pass Rate |\n"
            content += "|----------|--------|-------|----------|\n"

            for category, stats in summary['category_breakdown'].items():
                rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
                content += f"| {category.title()} | {stats['passed']} | {stats['total']} | {rate:.1f}% |\n"

        # Failed tickets section
        if summary['failed_tickets']:
            content += f"\n## Failed Tickets ({len(summary['failed_tickets'])})\n\n"
            for ticket in summary['failed_tickets']:
                ticket_result = next((r for r in self.results if r['ticket'] == ticket), {})
                duration = ticket_result.get('duration', 0)
                content += f"- **{ticket}** ({duration:.1f}s)\n"
                if ticket_result.get('stderr'):
                    content += f"  - Error: {ticket_result['stderr'][:100]}...\n"

        # Error tickets section
        if summary['error_tickets']:
            content += f"\n## Error Tickets ({len(summary['error_tickets'])})\n\n"
            for ticket in summary['error_tickets']:
                ticket_result = next((r for r in self.results if r['ticket'] == ticket), {})
                content += f"- **{ticket}**\n"
                if ticket_result.get('stderr'):
                    content += f"  - Error: {ticket_result['stderr'][:100]}...\n"

        content += f"""
## Performance Metrics

- **Total Test Duration**: {exec_summary['total_duration']:.1f} seconds
- **Wall Clock Time**: {exec_summary['execution_time']:.1f} seconds
- **Parallel Efficiency**: {exec_summary['parallel_efficiency']:.1f}x speedup
- **Average Test Duration**: {exec_summary['total_duration']/exec_summary['total_tests']:.1f} seconds per test

## Sequential Reasoning Assessment

**Pre-Execution Prediction**: Expected systematic test execution across all categories with proper error handling
**Actual Outcomes**: Achieved {summary['pass_rate']:.1f}% pass rate with {exec_summary['parallel_efficiency']:.1f}x parallel efficiency
**Variance Analysis**: {'Results met expectations' if summary['pass_rate'] >= 70 else 'Lower pass rate than expected - investigation needed'}

## Recommendations

{'Continue with systematic testing' if summary['pass_rate'] >= 70 else 'Address failed tests before proceeding with additional tickets'}

---
*Generated by CMZ TDD Batch Framework*
*Execution completed: {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}*
"""

        with open(report_file, 'w') as f:
            f.write(content)

def main():
    """Main execution function with command line argument parsing"""
    import argparse

    parser = argparse.ArgumentParser(description='CMZ TDD Batch Test Execution')
    parser.add_argument('--category', choices=['integration', 'unit', 'playwright', 'security'],
                       help='Filter tests by category')
    parser.add_argument('--filter', type=str, help='Filter tickets by substring match')
    parser.add_argument('--max', type=int, help='Maximum number of tickets to test')
    parser.add_argument('--workers', type=int, default=3, help='Number of parallel workers')
    parser.add_argument('--list', action='store_true', help='List available tickets and exit')

    args = parser.parse_args()

    executor = BatchTestExecutor(max_workers=args.workers)

    if args.list:
        tickets = executor.load_available_tickets()
        print(f"📋 Available tickets ({len(tickets)}):")
        for ticket in tickets:
            print(f"  - {ticket}")
        return

    # Run batch tests
    results = executor.run_batch_tests(
        ticket_filter=args.filter,
        category_filter=args.category,
        max_tickets=args.max
    )

    # Exit with appropriate code based on results
    summary = results['summary']
    if not summary:
        sys.exit(3)  # No tests found
    elif summary['pass_rate'] == 100:
        sys.exit(0)  # All passed
    elif summary['pass_rate'] >= 50:
        sys.exit(1)  # Some failed but >50% passed
    else:
        sys.exit(2)  # Majority failed

if __name__ == "__main__":
    main()