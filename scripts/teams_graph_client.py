#!/usr/bin/env python3
"""
Microsoft Graph API Client for Teams
Posts messages and images to Teams channels using Graph API
"""

import requests
import json
import os
import mimetypes
from typing import Dict, Optional
from dataclasses import dataclass
import logging

@dataclass
class TeamsConfig:
    """Teams configuration from environment variables."""
    tenant_id: str
    client_id: str
    client_secret: str
    team_id: str
    channel_id: str

class TeamsGraphClient:
    """Microsoft Graph API client for Teams operations."""

    def __init__(self, config: TeamsConfig):
        self.config = config
        self.access_token = None
        self.logger = logging.getLogger('teams_graph')

    def authenticate(self) -> bool:
        """Authenticate with Microsoft Graph using client credentials flow."""
        self.logger.info("🔐 Authenticating with Microsoft Graph...")

        auth_url = f"https://login.microsoftonline.com/{self.config.tenant_id}/oauth2/v2.0/token"

        auth_data = {
            'client_id': self.config.client_id,
            'client_secret': self.config.client_secret,
            'scope': 'https://graph.microsoft.com/.default',
            'grant_type': 'client_credentials'
        }

        try:
            response = requests.post(auth_url, data=auth_data, timeout=30)

            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data['access_token']
                self.logger.info("✅ Successfully authenticated with Microsoft Graph")
                return True
            else:
                self.logger.error(f"❌ Authentication failed: HTTP {response.status_code}")
                self.logger.error(f"Response: {response.text}")
                return False

        except Exception as e:
            self.logger.error(f"❌ Authentication error: {e}")
            return False

    def post_message_with_image(self, message_text: str, image_path: str,
                               image_name: Optional[str] = None) -> bool:
        """Post a message with an image attachment to Teams channel."""
        if not self.access_token:
            if not self.authenticate():
                return False

        self.logger.info(f"📨 Posting message with image to Teams channel...")

        # Step 1: Upload image as file attachment
        file_url = self._upload_file_to_channel(image_path, image_name)
        if not file_url:
            return False

        # Step 2: Send message referencing the uploaded file
        return self._send_message_with_attachment(message_text, file_url, image_name or os.path.basename(image_path))

    def _upload_file_to_channel(self, file_path: str, file_name: Optional[str] = None) -> Optional[str]:
        """Upload file to Teams channel and return the file URL."""
        if not os.path.exists(file_path):
            self.logger.error(f"❌ File not found: {file_path}")
            return None

        file_name = file_name or os.path.basename(file_path)
        mime_type, _ = mimetypes.guess_type(file_path)
        mime_type = mime_type or 'application/octet-stream'

        upload_url = f"https://graph.microsoft.com/v1.0/teams/{self.config.team_id}/channels/{self.config.channel_id}/filesFolder/children"

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

        # Create upload session for large files or direct upload for small files
        file_size = os.path.getsize(file_path)

        if file_size < 4 * 1024 * 1024:  # Less than 4MB - direct upload
            return self._direct_file_upload(file_path, file_name, mime_type)
        else:
            return self._resumable_file_upload(file_path, file_name, mime_type)

    def _direct_file_upload(self, file_path: str, file_name: str, mime_type: str) -> Optional[str]:
        """Direct file upload for small files."""
        upload_url = f"https://graph.microsoft.com/v1.0/teams/{self.config.team_id}/channels/{self.config.channel_id}/filesFolder/children/{file_name}/content"

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': mime_type
        }

        try:
            with open(file_path, 'rb') as file:
                response = requests.put(upload_url, headers=headers, data=file, timeout=60)

            if response.status_code in [200, 201]:
                file_info = response.json()
                self.logger.info(f"✅ File uploaded successfully: {file_name}")
                return file_info.get('webUrl')
            else:
                self.logger.error(f"❌ File upload failed: HTTP {response.status_code}")
                self.logger.error(f"Response: {response.text}")
                return None

        except Exception as e:
            self.logger.error(f"❌ File upload error: {e}")
            return None

    def _resumable_file_upload(self, file_path: str, file_name: str, mime_type: str) -> Optional[str]:
        """Resumable file upload for large files."""
        # Implementation for large file uploads using upload sessions
        # For now, return None as most chart images will be < 4MB
        self.logger.warning("⚠️ Large file upload not implemented - file too large")
        return None

    def _send_message_with_attachment(self, message_text: str, file_url: str, file_name: str) -> bool:
        """Send message with file attachment reference."""
        message_url = f"https://graph.microsoft.com/v1.0/teams/{self.config.team_id}/channels/{self.config.channel_id}/messages"

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

        message_body = {
            "body": {
                "contentType": "html",
                "content": f"""
                <div>
                    <p>{message_text}</p>
                    <p><strong>📊 Chart: <a href="{file_url}">{file_name}</a></strong></p>
                </div>
                """
            }
        }

        try:
            response = requests.post(message_url, headers=headers, json=message_body, timeout=30)

            if response.status_code in [200, 201]:
                self.logger.info("✅ Message with attachment posted successfully")
                return True
            else:
                self.logger.error(f"❌ Message posting failed: HTTP {response.status_code}")
                self.logger.error(f"Response: {response.text}")
                return False

        except Exception as e:
            self.logger.error(f"❌ Message posting error: {e}")
            return False

    def post_simple_message(self, message_text: str) -> bool:
        """Post a simple text message to Teams channel."""
        if not self.access_token:
            if not self.authenticate():
                return False

        message_url = f"https://graph.microsoft.com/v1.0/teams/{self.config.team_id}/channels/{self.config.channel_id}/messages"

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

        message_body = {
            "body": {
                "contentType": "text",
                "content": message_text
            }
        }

        try:
            response = requests.post(message_url, headers=headers, json=message_body, timeout=30)

            if response.status_code in [200, 201]:
                self.logger.info("✅ Simple message posted successfully")
                return True
            else:
                self.logger.error(f"❌ Message posting failed: HTTP {response.status_code}")
                self.logger.error(f"Response: {response.text}")
                return False

        except Exception as e:
            self.logger.error(f"❌ Message posting error: {e}")
            return False

def load_teams_config() -> Optional[TeamsConfig]:
    """Load Teams configuration from environment variables."""
    try:
        # Try to load from .teams_config.env file
        env_file = '.teams_config.env'
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value

        config = TeamsConfig(
            tenant_id=os.environ['TEAMS_TENANT_ID'],
            client_id=os.environ['TEAMS_CLIENT_ID'],
            client_secret=os.environ['TEAMS_CLIENT_SECRET'],
            team_id=os.environ['TEAMS_TEAM_ID'],
            channel_id=os.environ['TEAMS_CHANNEL_ID']
        )

        return config

    except KeyError as e:
        print(f"❌ Missing environment variable: {e}")
        print("Please ensure all Teams configuration variables are set:")
        print("- TEAMS_TENANT_ID")
        print("- TEAMS_CLIENT_ID")
        print("- TEAMS_CLIENT_SECRET")
        print("- TEAMS_TEAM_ID")
        print("- TEAMS_CHANNEL_ID")
        return None

    except Exception as e:
        print(f"❌ Error loading Teams configuration: {e}")
        return None

def test_graph_client():
    """Test the Graph API client."""
    config = load_teams_config()
    if not config:
        return False

    client = TeamsGraphClient(config)

    # Test authentication
    if not client.authenticate():
        return False

    # Test simple message
    test_message = f"🧪 Graph API Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    success = client.post_simple_message(test_message)

    if success:
        print("✅ Graph API client test successful!")
        return True
    else:
        print("❌ Graph API client test failed")
        return False

if __name__ == "__main__":
    from datetime import datetime
    import sys
    logging.basicConfig(level=logging.INFO)

    success = test_graph_client()
    sys.exit(0 if success else 1)