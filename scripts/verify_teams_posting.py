#!/usr/bin/env python3
"""
Verify Teams Posting Success
Simple script to verify TDD analysis was posted successfully
"""

from teams_read_client import TeamsReadClient, load_teams_config
import logging

def main():
    """Verify TDD posting success."""
    print("🔍 Verifying TDD analysis posting to Teams...")

    # Load configuration
    config = load_teams_config()
    if not config:
        print("❌ Teams configuration not found")
        print("Please ensure read permissions are configured in Azure")
        return 1

    # Create read client
    client = TeamsReadClient(config)

    try:
        # Get verification report
        report = client.create_posting_report()
        print(report)

        # Get detailed verification
        verification = client.verify_tdd_posting_success()

        print(f"\n🎯 **Final Verification**:")
        for summary_item in verification['summary']:
            print(f"  {summary_item}")

        if verification['success']:
            print("\n✅ TDD analysis posting verification: SUCCESS")
            print("📊 All expected content found in Teams channel")
            return 0
        else:
            print("\n⚠️ TDD analysis posting verification: INCOMPLETE")
            print("💡 Some expected content may be missing")
            return 1

    except Exception as e:
        print(f"❌ Verification error: {e}")
        print("💡 This might indicate missing read permissions")
        return 1

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    sys.exit(main())