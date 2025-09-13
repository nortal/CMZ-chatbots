#!/usr/bin/env python3
"""
Teams/Channel ID Discovery
Get the team-id and channel-id needed for Graph API
"""

import re

def extract_teams_ids_from_url():
    """Extract team and channel IDs from Teams URL."""
    print("🔍 Teams/Channel ID Discovery")
    print("=" * 50)

    print("\n📋 Method 1: From Teams URL")
    print("1. Go to your 'TDD reports' channel in Teams")
    print("2. Click the '...' menu next to the channel name")
    print("3. Select 'Get link to channel'")
    print("4. Copy the URL and paste it below")
    print("\nExample URL format:")
    print("https://teams.microsoft.com/l/channel/19%3a[CHANNEL-ID]%40thread.tacv2/TDD%2520reports?groupId=[TEAM-ID]&tenantId=[TENANT-ID]")

    url = input("\nPaste your Teams channel URL here: ").strip()

    if url:
        # Extract team ID (groupId parameter)
        team_match = re.search(r'groupId=([^&]+)', url)
        team_id = team_match.group(1) if team_match else None

        # Extract channel ID (from the path)
        channel_match = re.search(r'/l/channel/([^/]+)', url)
        if channel_match:
            channel_encoded = channel_match.group(1)
            # URL decode the channel ID
            import urllib.parse
            channel_id = urllib.parse.unquote(channel_encoded)
        else:
            channel_id = None

        # Extract tenant ID
        tenant_match = re.search(r'tenantId=([^&]+)', url)
        tenant_id = tenant_match.group(1) if tenant_match else None

        print(f"\n✅ Extracted IDs:")
        print(f"Team ID: {team_id}")
        print(f"Channel ID: {channel_id}")
        print(f"Tenant ID: {tenant_id}")

        return team_id, channel_id, tenant_id

    print("\n📋 Method 2: Manual Discovery")
    print("1. Open Teams in browser (teams.microsoft.com)")
    print("2. Navigate to your channel")
    print("3. Look at the URL bar - the IDs are in the URL")
    print("4. Or use the Graph API discovery script below")

    return None, None, None

def create_graph_discovery_script():
    """Create a script for Graph API team discovery."""
    script = '''
# Graph API Discovery Commands (requires authentication setup first)

# List all teams you're a member of:
GET https://graph.microsoft.com/v1.0/me/joinedTeams

# List channels in a specific team:
GET https://graph.microsoft.com/v1.0/teams/{team-id}/channels

# Find channel by name:
GET https://graph.microsoft.com/v1.0/teams/{team-id}/channels?$filter=displayName eq 'TDD reports'
'''

    with open('graph_api_discovery.txt', 'w') as f:
        f.write(script)

    print("📝 Created 'graph_api_discovery.txt' with Graph API commands")

if __name__ == "__main__":
    team_id, channel_id, tenant_id = extract_teams_ids_from_url()

    if team_id and channel_id:
        # Save to environment file
        env_content = f"""# Teams Configuration for Graph API
TEAMS_TEAM_ID={team_id}
TEAMS_CHANNEL_ID={channel_id}
TEAMS_TENANT_ID={tenant_id}

# You'll need to add these after Azure app registration:
# TEAMS_CLIENT_ID=your-app-client-id
# TEAMS_CLIENT_SECRET=your-app-client-secret
"""

        with open('.teams_config.env', 'w') as f:
            f.write(env_content)

        print(f"\n📄 Saved configuration to '.teams_config.env'")
        print("Next: Set up Azure app registration")

    create_graph_discovery_script()