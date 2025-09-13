#!/usr/bin/env python3
"""
TDD Reporting Entry Point
Triggered by git post-merge hook to generate Teams TDD improvement reports

Follows proven patterns from /nextfive implementations and existing script structure.
"""

import sys
import os
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add the scripts directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent))

from tdd_config import TDDConfigManager
from teams_tdd_reporter import TeamsTDDReporter


def setup_logging(debug_mode: bool = False) -> logging.Logger:
    """Setup logging for TDD reporting."""
    logger = logging.getLogger('tdd_reporting')

    if not logger.handlers:  # Avoid duplicate handlers
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(logging.DEBUG if debug_mode else logging.INFO)
    return logger


def get_current_branch() -> Optional[str]:
    """Get the current git branch name."""
    try:
        result = subprocess.run(
            ['git', 'branch', '--show-current'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


def is_merge_to_dev() -> bool:
    """
    Check if this is a merge to the dev branch.
    Following /nextfive pattern of focusing on dev branch merges.
    """
    current_branch = get_current_branch()
    if current_branch != 'dev':
        return False

    # Check if this was a merge commit (has multiple parents)
    try:
        result = subprocess.run(
            ['git', 'rev-list', '--parents', '-n', '1', 'HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        parents = result.stdout.strip().split()
        return len(parents) > 2  # More than 2 means it's a merge commit
    except subprocess.CalledProcessError:
        return False


def check_recent_merge() -> Optional[str]:
    """
    Check for recent merge information.
    Returns merge information if this appears to be a merge to dev.
    """
    try:
        # Get the last commit message
        result = subprocess.run(
            ['git', 'log', '--oneline', '-1'],
            capture_output=True,
            text=True,
            check=True
        )
        last_commit = result.stdout.strip()

        # Check if it looks like a merge commit
        if 'merge' in last_commit.lower() or 'pull request' in last_commit.lower():
            return last_commit

        return None
    except subprocess.CalledProcessError:
        return None


def validate_environment() -> bool:
    """
    Validate that all required environment variables are present.
    """
    required_vars = [
        'JIRA_API_TOKEN',
        'JIRA_EMAIL',
        'GITHUB_TOKEN',
        'TEAMS_WEBHOOK_URL'
    ]

    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these variables before running TDD reporting.")
        return False

    return True


def main():
    """
    Main entry point for TDD reporting.

    Can be called in multiple ways:
    1. From git post-merge hook (automatic)
    2. Manually for testing: python run_tdd_reporting.py
    3. With force flag: python run_tdd_reporting.py --force
    4. With specific days: python run_tdd_reporting.py --days 14
    """

    # Parse command line arguments
    force_run = '--force' in sys.argv
    test_mode = '--test' in sys.argv

    days = 30  # default
    if '--days' in sys.argv:
        try:
            days_index = sys.argv.index('--days') + 1
            if days_index < len(sys.argv):
                days = int(sys.argv[days_index])
        except (ValueError, IndexError):
            print("❌ Invalid --days argument. Using default of 30.")

    # Setup logging
    logger = setup_logging(debug_mode=('--debug' in sys.argv))

    logger.info("🎯 TDD Reporting System Starting...")
    logger.info(f"Force run: {force_run}, Test mode: {test_mode}, Days: {days}")

    try:
        # Validate environment
        if not validate_environment():
            return 1

        # Check if we should run (merge to dev or force)
        current_branch = get_current_branch()
        merge_info = check_recent_merge()

        should_run = False
        run_reason = ""

        if force_run:
            should_run = True
            run_reason = "forced execution"
        elif test_mode:
            should_run = True
            run_reason = "test mode"
        elif current_branch == 'dev' and merge_info:
            should_run = True
            run_reason = f"merge to dev detected: {merge_info}"
        elif current_branch == 'dev':
            should_run = True
            run_reason = "manual execution on dev branch"

        if not should_run:
            logger.info(f"ℹ️ Skipping TDD reporting - not a dev branch merge (current: {current_branch})")
            logger.info("Use --force to run anyway or --test for test mode")
            return 0

        logger.info(f"🚀 Running TDD reporting - {run_reason}")

        # Load configuration
        config_manager = TDDConfigManager()
        config = config_manager.load_configuration()

        # Test API connectivity
        if not test_mode:  # Skip connectivity test in test mode
            logger.info("🔌 Testing API connectivity...")
            success, status = config_manager.validate_api_connectivity()

            if not success:
                logger.error("❌ API connectivity check failed:")
                for service, status_msg in status.items():
                    logger.error(f"  {service}: {status_msg}")
                return 1

        # Generate and post TDD report
        logger.info("📊 Generating TDD improvement report...")
        reporter = TeamsTDDReporter(config)

        if test_mode:
            # In test mode, just validate configuration and generate metrics
            from tdd_metrics_collector import TDDMetricsCollector
            collector = TDDMetricsCollector(config)

            logger.info("🧪 Test mode - collecting sample metrics...")
            metrics = collector.collect_all_metrics(days=7)

            logger.info("📊 Sample metrics collected:")
            logger.info(f"  Success Rate: {metrics.success_rate:.1f}%")
            logger.info(f"  Review Rounds: {metrics.review_rounds_avg:.1f}")
            logger.info(f"  Test Coverage: {metrics.test_coverage_rate:.1f}%")
            logger.info(f"  Security Resolution: {metrics.security_resolution_rate:.1f}%")
            logger.info(f"  Foundation Adoption: {metrics.foundation_adoption_rate:.1f}%")
            logger.info(f"  Total Tickets: {metrics.total_tickets}")

            logger.info("✅ Test mode completed successfully")
            return 0
        else:
            # Full execution - generate report and post to Teams
            success = reporter.generate_tdd_report(days=days)

        if success:
            logger.info("🎉 TDD report generated and posted to Teams successfully")

            # Log completion for audit trail
            completion_msg = f"TDD report completed at {datetime.now().isoformat()}"
            if merge_info:
                completion_msg += f" - triggered by: {merge_info}"
            logger.info(completion_msg)

            return 0
        else:
            logger.error("❌ TDD report generation failed")
            return 1

    except KeyboardInterrupt:
        logger.info("⏸️ TDD reporting interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"❌ Unexpected error in TDD reporting: {e}")
        if '--debug' in sys.argv:
            import traceback
            logger.error(traceback.format_exc())
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)