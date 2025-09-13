# Azure App Registration for Teams Graph API

## Step-by-Step Setup Process

### 1. Azure Portal Registration
1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** > **App registrations**
3. Click **"New registration"**
4. Configure:
   - **Name**: `CMZ-TDD-Teams-Reporter`
   - **Supported account types**: `Accounts in this organizational directory only`
   - **Redirect URI**: Leave blank (we'll use client credentials flow)
5. Click **"Register"**

### 2. Get Application IDs
After registration, note these values:
- **Application (client) ID**: Copy this - you'll need it as `TEAMS_CLIENT_ID`
- **Directory (tenant) ID**: Copy this - you'll need it as `TEAMS_TENANT_ID`

### 3. Create Client Secret
1. In your app registration, go to **"Certificates & secrets"**
2. Click **"New client secret"**
3. Configure:
   - **Description**: `TDD Reporter Secret`
   - **Expires**: `24 months` (recommended)
4. Click **"Add"**
5. **IMMEDIATELY COPY THE SECRET VALUE** - you'll need it as `TEAMS_CLIENT_SECRET`
   ⚠️ **Important**: You can only see the secret value once!

### 4. Configure API Permissions
1. Go to **"API permissions"**
2. Click **"Add a permission"**
3. Select **"Microsoft Graph"**
4. Choose **"Application permissions"** (not delegated)
5. Add these permissions:
   - `ChannelMessage.Send` - Send messages to channels
   - `Files.ReadWrite.All` - Upload file attachments
   - `Team.ReadBasic.All` - Read team information
   - `Channel.ReadBasic.All` - Read channel information

### 5. Grant Admin Consent
1. After adding permissions, click **"Grant admin consent for [your-org]"**
2. Confirm the consent
3. All permissions should show **"Granted for [your-org]"** with green checkmarks

### 6. Update Environment Configuration

Add these to your `.teams_config.env` file:

```bash
# Teams Configuration for Graph API
TEAMS_TEAM_ID=your-team-id-from-step-1
TEAMS_CHANNEL_ID=your-channel-id-from-step-1
TEAMS_TENANT_ID=your-tenant-id-from-azure
TEAMS_CLIENT_ID=your-application-client-id-from-azure
TEAMS_CLIENT_SECRET=your-client-secret-from-azure
```

## Authentication Flow

The app will use **Client Credentials Flow** (app-only authentication):

```
POST https://login.microsoftonline.com/{tenant-id}/oauth2/v2.0/token
Content-Type: application/x-www-form-urlencoded

client_id={client-id}
&client_secret={client-secret}
&scope=https://graph.microsoft.com/.default
&grant_type=client_credentials
```

## Required Permissions Summary

| Permission | Type | Description |
|------------|------|-------------|
| `ChannelMessage.Send` | Application | Send messages to Teams channels |
| `Files.ReadWrite.All` | Application | Upload file attachments |
| `Team.ReadBasic.All` | Application | Read team information |
| `Channel.ReadBasic.All` | Application | Read channel information |

## Testing Your Setup

Once configured, you can test with:

```bash
python test_graph_auth.py
```

## Security Best Practices

1. **Secure Storage**: Store client secret in environment variables, never in code
2. **Least Privilege**: Only request permissions you actually need
3. **Secret Rotation**: Rotate client secrets before expiration
4. **Monitor Usage**: Review Graph API usage in Azure portal
5. **Environment Separation**: Use different app registrations for dev/prod

## Troubleshooting

### Common Issues:
- **403 Forbidden**: Check admin consent was granted
- **401 Unauthorized**: Verify client ID/secret are correct
- **404 Not Found**: Check team/channel IDs are correct
- **429 Too Many Requests**: Implement retry logic with backoff

### Graph API Endpoints:
- **Authentication**: `https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token`
- **Send Message**: `https://graph.microsoft.com/v1.0/teams/{team-id}/channels/{channel-id}/messages`
- **Upload File**: `https://graph.microsoft.com/v1.0/teams/{team-id}/channels/{channel-id}/filesFolder/children`