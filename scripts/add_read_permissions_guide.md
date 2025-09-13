# Adding Read Permissions for Teams Channel Visibility

## Method 1: Extend Existing Azure App (Recommended)

### Step 1: Add Read Permissions to Your Azure App
1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** > **App registrations**
3. Find your `CMZ-TDD-Teams-Reporter` app
4. Go to **"API permissions"**
5. Click **"Add a permission"**
6. Select **"Microsoft Graph"**
7. Choose **"Application permissions"**
8. Add these additional permissions:
   - `ChannelMessage.Read.All` - Read all channel messages
   - `Chat.Read.All` - Read chat messages (optional)
   - `Files.Read.All` - Read uploaded files (optional)
9. Click **"Grant admin consent for [your-org]"**

### Step 2: Update Environment Configuration
No changes needed - uses same client credentials.

### Step 3: Add Read Functionality to Graph Client

```python
# Add to teams_graph_client.py
def get_recent_messages(self, limit: int = 50) -> List[Dict]:
    """Get recent messages from the Teams channel."""
    if not self.access_token:
        if not self.authenticate():
            return []

    messages_url = f"https://graph.microsoft.com/v1.0/teams/{self.config.team_id}/channels/{self.config.channel_id}/messages?$top={limit}"

    headers = {
        'Authorization': f'Bearer {self.access_token}',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.get(messages_url, headers=headers, timeout=30)
        if response.status_code == 200:
            return response.json().get('value', [])
        else:
            self.logger.error(f"Failed to get messages: HTTP {response.status_code}")
            return []
    except Exception as e:
        self.logger.error(f"Error getting messages: {e}")
        return []
```

## Method 2: Create Shared Access Token (Alternative)

### Option A: User Delegated Permissions
Instead of app-only permissions, use user-delegated permissions so I can read as you.

1. **Modify Azure App for Delegated Access:**
   - Change permissions from "Application" to "Delegated"
   - Add: `ChannelMessage.Read`, `Chat.Read` (delegated)
   - Requires user login flow

2. **Authentication Flow Changes:**
   - Use authorization code flow instead of client credentials
   - You'd need to authenticate once and share the refresh token

### Option B: Personal Access Token
Create a personal access token that I can use to read channel content.

## Method 3: Screenshot/Export Based Visibility

### Option A: Automated Screenshots
```python
def capture_teams_channel_screenshot():
    """Capture screenshot of Teams channel for analysis."""
    # Use playwright to take screenshot of Teams channel
    # Requires browser automation
```

### Option B: Export Channel Content
Teams allows channel export - you could periodically export and share the content.

## Method 4: Webhook Notification System

### Create Incoming Webhook for Confirmations
```python
def create_confirmation_webhook():
    """Set up webhook to receive confirmation when messages are posted."""
    # Teams can send webhooks when new messages are posted
    # This would give real-time confirmation
```