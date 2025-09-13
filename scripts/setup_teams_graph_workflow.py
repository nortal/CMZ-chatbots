#!/usr/bin/env python3
"""
Complete Teams Graph API Setup Workflow
Guides user through entire setup process
"""

import os
import subprocess
import sys

def print_header(title):
    """Print formatted header."""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def check_step_completion(step_name, check_func):
    """Check if a setup step is completed."""
    try:
        result = check_func()
        status = "✅ COMPLETED" if result else "❌ PENDING"
        print(f"{step_name}: {status}")
        return result
    except Exception as e:
        print(f"{step_name}: ❌ ERROR - {e}")
        return False

def check_teams_ids():
    """Check if Teams IDs are configured."""
    return os.path.exists('.teams_config.env')

def check_azure_app():
    """Check if Azure app credentials are configured."""
    env_file = '.teams_config.env'
    if not os.path.exists(env_file):
        return False

    with open(env_file, 'r') as f:
        content = f.read()
        return all(key in content for key in ['TEAMS_CLIENT_ID', 'TEAMS_CLIENT_SECRET', 'TEAMS_TENANT_ID'])

def check_dependencies():
    """Check if required Python packages are installed."""
    try:
        import requests
        import matplotlib
        return True
    except ImportError:
        return False

def setup_workflow():
    """Guide user through complete setup workflow."""
    print_header("Teams Graph API Setup Workflow")

    print("🎯 This workflow will set up professional chart posting to Teams")
    print("📊 You'll be able to post TDD coverage images directly to your Teams channel")

    # Step 1: Check dependencies
    print_header("Step 1: Check Dependencies")
    deps_ok = check_step_completion("Python Dependencies", check_dependencies)

    if not deps_ok:
        print("\n📦 Installing required dependencies...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'requests', 'matplotlib', 'numpy'])
        deps_ok = check_dependencies()

    # Step 2: Teams IDs
    print_header("Step 2: Teams/Channel IDs")
    teams_ids_ok = check_step_completion("Teams Configuration", check_teams_ids)

    if not teams_ids_ok:
        print("\n🔍 Running Teams ID discovery...")
        print("You need to get your Teams channel URL...")
        try:
            subprocess.run([sys.executable, 'get_teams_ids.py'])
            teams_ids_ok = check_teams_ids()
        except Exception as e:
            print(f"❌ Error running Teams ID discovery: {e}")

    # Step 3: Azure App Registration
    print_header("Step 3: Azure App Registration")
    azure_ok = check_step_completion("Azure App Credentials", check_azure_app)

    if not azure_ok:
        print("\n☁️ Azure app registration required...")
        print("📖 Opening setup guide...")

        if sys.platform == "darwin":  # macOS
            subprocess.run(['open', 'azure_app_setup_guide.md'])
        elif sys.platform == "win32":  # Windows
            subprocess.run(['start', 'azure_app_setup_guide.md'], shell=True)
        else:  # Linux
            subprocess.run(['xdg-open', 'azure_app_setup_guide.md'])

        print("\n⏳ Please complete Azure app registration and update .teams_config.env")
        print("Press Enter when you've completed the Azure setup...")
        input()
        azure_ok = check_azure_app()

    # Step 4: Test Connection
    print_header("Step 4: Test Graph API Connection")

    if teams_ids_ok and azure_ok:
        print("🧪 Testing Graph API connection...")
        try:
            result = subprocess.run([sys.executable, 'teams_graph_client.py'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Graph API connection test successful!")
                connection_ok = True
            else:
                print(f"❌ Graph API connection test failed:")
                print(result.stderr)
                connection_ok = False
        except Exception as e:
            print(f"❌ Error testing connection: {e}")
            connection_ok = False
    else:
        print("⏭️ Skipping connection test - prerequisites not met")
        connection_ok = False

    # Step 5: Run Complete Analysis
    print_header("Step 5: Run Complete TDD Analysis")

    if connection_ok:
        print("🎯 Ready to run complete TDD analysis with image posting!")
        run_analysis = input("Run complete analysis now? (y/N): ").lower().startswith('y')

        if run_analysis:
            print("\n🚀 Running complete TDD analysis...")
            try:
                result = subprocess.run([sys.executable, 'tdd_teams_graph_reporter.py'])
                if result.returncode == 0:
                    print("✅ Complete TDD analysis posted to Teams successfully!")
                else:
                    print("❌ TDD analysis posting failed")
            except Exception as e:
                print(f"❌ Error running analysis: {e}")
    else:
        print("⏭️ Complete setup required before running analysis")

    # Summary
    print_header("Setup Summary")

    all_steps = [
        ("Dependencies", deps_ok),
        ("Teams IDs", teams_ids_ok),
        ("Azure App", azure_ok),
        ("Connection", connection_ok)
    ]

    completed_steps = sum(1 for _, ok in all_steps if ok)
    total_steps = len(all_steps)

    print(f"📊 Setup Progress: {completed_steps}/{total_steps} steps completed")

    for step_name, completed in all_steps:
        status = "✅" if completed else "❌"
        print(f"  {status} {step_name}")

    if completed_steps == total_steps:
        print("\n🎉 Complete setup successful!")
        print("📊 You can now run: python tdd_teams_graph_reporter.py")
        print("🔄 Charts will be posted directly to your Teams channel")
    else:
        print(f"\n⚠️ {total_steps - completed_steps} steps remaining")
        print("Please complete the pending steps and run this script again")

def main():
    """Run the setup workflow."""
    try:
        setup_workflow()
        return 0
    except KeyboardInterrupt:
        print("\n⏹️ Setup cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Setup error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())