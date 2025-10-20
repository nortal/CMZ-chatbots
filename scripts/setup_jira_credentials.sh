#!/bin/bash

# Secure JIRA Credentials Setup Script
# This script helps you securely configure JIRA credentials without exposing them in history

set -e

echo "🔐 JIRA Credentials Setup for CMZ Chatbot Project"
echo "================================================="
echo ""

# Check if .env.local already exists
if [ -f ".env.local" ]; then
    echo "⚠️  .env.local file already exists"
    echo "Current JIRA_EMAIL: $(grep JIRA_EMAIL .env.local | cut -d'=' -f2)"
    echo ""
    read -p "Do you want to update it? (y/n): " update_choice
    if [ "$update_choice" != "y" ]; then
        echo "Keeping existing credentials."
        exit 0
    fi
fi

# Get email (can be visible)
echo "📧 JIRA Email Configuration"
read -p "Enter your Nortal email (e.g., firstname.lastname@nortal.com): " jira_email

# Get API token securely (hidden input)
echo ""
echo "🔑 JIRA API Token Configuration"
echo "To get your API token:"
echo "1. Go to: https://nortal.atlassian.net/"
echo "2. Click your profile → Account Settings"
echo "3. Security → Create and manage API tokens → Create API token"
echo "4. Copy the generated token"
echo ""
read -s -p "Enter your JIRA API token (input will be hidden): " jira_token
echo ""

# Validate inputs
if [ -z "$jira_email" ] || [ -z "$jira_token" ]; then
    echo "❌ Error: Email and token cannot be empty"
    exit 1
fi

# Create .env.local file
cat > .env.local << EOF
# Local environment variables for JIRA integration
# DO NOT COMMIT THIS FILE - it's in .gitignore

# JIRA API Configuration
JIRA_EMAIL=$jira_email
JIRA_API_TOKEN=$jira_token

# Usage: source .env.local or run scripts that auto-source this file
EOF

# Set proper permissions (readable only by user)
chmod 600 .env.local

echo ""
echo "✅ Credentials configured successfully!"
echo "📁 Created: .env.local (secured with 600 permissions)"
echo "🚫 File is in .gitignore - will not be committed"
echo ""
echo "🔧 Usage:"
echo "   ./scripts/update_jira_tickets.sh comment 'Your message here'"
echo "   (The script will automatically load credentials from .env.local)"
echo ""
echo "🧹 To remove credentials later:"
echo "   rm .env.local"