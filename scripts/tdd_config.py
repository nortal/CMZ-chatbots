#!/usr/bin/env python3
"""
TDD Configuration Management Service
Based on proven patterns from update_jira_simple.sh and /nextfive implementations

Handles environment variables, API connectivity, and configuration validation
for Teams TDD reporting system.
"""

import os
import sys
import base64
import logging
from typing import Dict, Optional, Tuple
import requests
from dataclasses import dataclass


@dataclass
class TDDConfig:
    """Configuration class for TDD reporting system."""

    # Jira Configuration (reusing existing patterns)
    jira_base_url: str
    jira_email: str
    jira_api_token: str
    jira_credentials: str  # Base64 encoded email:token

    # GitHub Configuration
    github_token: str
    github_repo: str
    github_base_url: str

    # Teams Configuration
    teams_webhook_url: str

    # Chart Configuration
    chart_storage_url: Optional[str] = None
    chart_style: str = "professional"

    # Operational Configuration
    metrics_days: int = 30
    chart_width: int = 800
    chart_height: int = 600
    debug_mode: bool = False


class TDDConfigManager:
    """
    Configuration manager following patterns from update_jira_simple.sh
    """

    def __init__(self):
        self.logger = self._setup_logging()
        self.config: Optional[TDDConfig] = None

    def _setup_logging(self) -> logging.Logger:
        """Setup logging with appropriate level."""
        logger = logging.getLogger('tdd_reporting')
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    def load_configuration(self) -> TDDConfig:
        """
        Load and validate configuration from environment variables.
        Uses same patterns as update_jira_simple.sh for authentication.
        """
        self.logger.info("🔧 Loading TDD reporting configuration...")

        # Validate required environment variables
        required_vars = [
            'JIRA_API_TOKEN', 'JIRA_EMAIL', 'GITHUB_TOKEN', 'TEAMS_WEBHOOK_URL'
        ]

        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        if missing_vars:
            error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
            self.logger.error(f"❌ {error_msg}")
            raise EnvironmentError(error_msg)

        # Create Jira credentials following update_jira_simple.sh pattern
        jira_email = os.getenv('JIRA_EMAIL')
        jira_api_token = os.getenv('JIRA_API_TOKEN')
        jira_credentials = base64.b64encode(
            f"{jira_email}:{jira_api_token}".encode()
        ).decode()

        # Build configuration
        self.config = TDDConfig(
            # Jira configuration (following existing patterns)
            jira_base_url=os.getenv('JIRA_BASE_URL', 'https://nortal.atlassian.net'),
            jira_email=jira_email,
            jira_api_token=jira_api_token,
            jira_credentials=jira_credentials,

            # GitHub configuration
            github_token=os.getenv('GITHUB_TOKEN'),
            github_repo=os.getenv('GITHUB_REPO', 'nortal/CMZ-chatbots'),
            github_base_url='https://api.github.com',

            # Teams configuration
            teams_webhook_url=os.getenv('TEAMS_WEBHOOK_URL'),

            # Optional configuration
            chart_storage_url=os.getenv('CHART_STORAGE_URL'),
            chart_style=os.getenv('CHART_STYLE', 'professional'),
            metrics_days=int(os.getenv('TDD_METRICS_DAYS', '30')),
            chart_width=int(os.getenv('CHART_WIDTH', '800')),
            chart_height=int(os.getenv('CHART_HEIGHT', '600')),
            debug_mode=os.getenv('DEBUG', '').lower() in ('true', '1', 'yes')
        )

        if self.config.debug_mode:
            self.logger.setLevel(logging.DEBUG)
            self.logger.debug("🐛 Debug mode enabled")

        self.logger.info("✅ Configuration loaded successfully")
        return self.config

    def validate_api_connectivity(self) -> Tuple[bool, Dict[str, str]]:
        """
        Test connectivity to all required APIs.
        Returns (success, status_dict)
        """
        self.logger.info("🔌 Testing API connectivity...")

        if not self.config:
            raise RuntimeError("Configuration not loaded. Call load_configuration() first.")

        status = {}
        all_success = True

        # Test Jira API (following update_jira_simple.sh pattern)
        try:
            jira_response = requests.get(
                f"{self.config.jira_base_url}/rest/api/3/myself",
                headers={
                    "Authorization": f"Basic {self.config.jira_credentials}",
                    "Content-Type": "application/json"
                },
                timeout=10
            )

            if jira_response.status_code == 200:
                status['jira'] = "✅ Connected"
                self.logger.info("✅ Jira API connectivity confirmed")
            else:
                status['jira'] = f"❌ HTTP {jira_response.status_code}"
                all_success = False
                self.logger.error(f"❌ Jira API failed: HTTP {jira_response.status_code}")

        except Exception as e:
            status['jira'] = f"❌ Error: {str(e)[:50]}"
            all_success = False
            self.logger.error(f"❌ Jira API error: {e}")

        # Test GitHub API
        try:
            github_response = requests.get(
                f"{self.config.github_base_url}/repos/{self.config.github_repo}",
                headers={
                    "Authorization": f"token {self.config.github_token}",
                    "Accept": "application/vnd.github.v3+json"
                },
                timeout=10
            )

            if github_response.status_code == 200:
                status['github'] = "✅ Connected"
                self.logger.info("✅ GitHub API connectivity confirmed")
            else:
                status['github'] = f"❌ HTTP {github_response.status_code}"
                all_success = False
                self.logger.error(f"❌ GitHub API failed: HTTP {github_response.status_code}")

        except Exception as e:
            status['github'] = f"❌ Error: {str(e)[:50]}"
            all_success = False
            self.logger.error(f"❌ GitHub API error: {e}")

        # Test Teams webhook
        try:
            # Send a simple test message to verify webhook is accessible
            test_payload = {
                "type": "message",
                "text": "🧪 TDD Reporting System - Connectivity Test"
            }

            teams_response = requests.post(
                self.config.teams_webhook_url,
                json=test_payload,
                timeout=10
            )

            if teams_response.status_code in [200, 202]:
                status['teams'] = "✅ Connected"
                self.logger.info("✅ Teams webhook connectivity confirmed")
            else:
                status['teams'] = f"❌ HTTP {teams_response.status_code}"
                all_success = False
                self.logger.error(f"❌ Teams webhook failed: HTTP {teams_response.status_code}")

        except Exception as e:
            status['teams'] = f"❌ Error: {str(e)[:50]}"
            all_success = False
            self.logger.error(f"❌ Teams webhook error: {e}")

        if all_success:
            self.logger.info("🎉 All API connectivity tests passed")
        else:
            self.logger.warning("⚠️ Some API connectivity tests failed")

        return all_success, status

    def get_chart_styling(self) -> Dict:
        """
        Get chart styling configuration for consistent professional appearance.
        Following CMZ branding preferences (no emojis, clean professional style).
        """
        return {
            'style': 'seaborn-v0_8-whitegrid',
            'figure_size': (self.config.chart_width/100, self.config.chart_height/100),
            'dpi': 100,
            'colors': {
                'success': '#28a745',     # Green for meeting targets
                'warning': '#ffc107',     # Yellow for close to target
                'danger': '#dc3545',      # Red for needs improvement
                'primary': '#007bff',     # Blue for neutral metrics
                'secondary': '#6c757d'    # Gray for supporting data
            },
            'font_size': {
                'title': 14,
                'axis': 12,
                'tick': 10,
                'legend': 11
            },
            'target_lines': {
                'success_rate': 90,       # ≥90% target
                'review_rounds': 1.2,     # ≤1.2 target
                'test_coverage': 95,      # ≥95% target
                'security_resolution': 100  # 100% target
            }
        }


def main():
    """
    Test the configuration management system.
    Can be run standalone for validation.
    """
    try:
        config_manager = TDDConfigManager()
        config = config_manager.load_configuration()

        print("🔧 TDD Configuration Test")
        print(f"Jira URL: {config.jira_base_url}")
        print(f"GitHub Repo: {config.github_repo}")
        print(f"Metrics Days: {config.metrics_days}")
        print(f"Chart Size: {config.chart_width}x{config.chart_height}")
        print(f"Debug Mode: {config.debug_mode}")

        success, status = config_manager.validate_api_connectivity()

        print("\n🔌 API Connectivity Status:")
        for service, status_msg in status.items():
            print(f"  {service.title()}: {status_msg}")

        if success:
            print("\n🎉 Configuration validation successful!")
            return 0
        else:
            print("\n❌ Configuration validation failed!")
            return 1

    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())