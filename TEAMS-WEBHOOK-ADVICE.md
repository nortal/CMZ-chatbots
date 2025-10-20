# TEAMS-WEBHOOK-ADVICE.md

## Overview
Microsoft Teams webhooks require messages to be sent as adaptive cards, not simple text messages. The webhook URL is a Power Automate endpoint that processes the adaptive card format.

## Environment Configuration
```bash
TEAMS_WEBHOOK_URL="https://default7c359f6b9f2f4042bf2db08ce16c5c.c1.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/cba76b9b30b644aaae7784ead5b54be4/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=03f33nmke2hKhd0FhZqpLte_NVMWI3MQkd6jqLDAVqA"
```

## Adaptive Card Format (REQUIRED)
Teams webhooks expect messages in the Microsoft Adaptive Card format, not plain text or simple JSON. The message must include a `type`, `attachments`, and proper card structure.

### Basic Card Structure
```python
message = {
    "type": "message",
    "attachments": [
        {
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": {
                "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                "type": "AdaptiveCard",
                "version": "1.4",
                "body": [
                    {
                        "type": "TextBlock",
                        "text": "Title",
                        "size": "Large",
                        "weight": "Bolder",
                        "wrap": True
                    },
                    {
                        "type": "FactSet",
                        "facts": [
                            {"title": "Key", "value": "Value"},
                            {"title": "Status", "value": "✅ Success"}
                        ]
                    }
                ]
            }
        }
    ]
}
```

## Python Implementation Example
```python
import requests
import json
from datetime import datetime

def send_teams_notification(title, facts_list, color="good"):
    """
    Send a formatted notification to Teams channel

    Args:
        title: Main title of the card
        facts_list: List of dicts with 'title' and 'value' keys
        color: Accent color (good=green, warning=yellow, attention=red)
    """
    webhook_url = os.getenv('TEAMS_WEBHOOK_URL')

    # Build facts for the FactSet
    facts = []
    for fact in facts_list:
        facts.append({
            "title": fact['title'],
            "value": str(fact['value'])
        })

    # Create adaptive card
    card = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.4",
                    "body": [
                        {
                            "type": "TextBlock",
                            "text": title,
                            "size": "Large",
                            "weight": "Bolder",
                            "wrap": True
                        },
                        {
                            "type": "TextBlock",
                            "text": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            "size": "Small",
                            "isSubtle": True,
                            "wrap": True
                        },
                        {
                            "type": "FactSet",
                            "facts": facts
                        }
                    ]
                }
            }
        ]
    }

    # Send to Teams
    response = requests.post(
        webhook_url,
        json=card,
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 202:
        print("✅ Teams notification sent successfully")
    else:
        print(f"❌ Failed to send Teams notification: {response.status_code}")
        print(response.text)

    return response.status_code
```

## Multiple Sections Example
```python
def send_detailed_teams_report(title, sections):
    """
    Send a detailed report with multiple sections to Teams

    Args:
        title: Main title
        sections: List of dicts with 'title' and 'facts' keys
    """
    webhook_url = os.getenv('TEAMS_WEBHOOK_URL')

    body = [
        {
            "type": "TextBlock",
            "text": title,
            "size": "Large",
            "weight": "Bolder",
            "wrap": True
        }
    ]

    for section in sections:
        # Add section header
        body.append({
            "type": "TextBlock",
            "text": section['title'],
            "size": "Medium",
            "weight": "Bolder",
            "wrap": True,
            "spacing": "Medium"
        })

        # Add facts for this section
        facts = []
        for fact in section.get('facts', []):
            facts.append({
                "title": fact['title'],
                "value": str(fact['value'])
            })

        if facts:
            body.append({
                "type": "FactSet",
                "facts": facts
            })

    card = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.4",
                    "body": body
                }
            }
        ]
    }

    response = requests.post(webhook_url, json=card, headers={"Content-Type": "application/json"})
    return response.status_code
```

## Common Issues and Solutions

### Issue: 202 Response but No Message in Teams
- **Cause**: Incorrect message format (not using adaptive card structure)
- **Solution**: Use the proper adaptive card format with type, attachments, and content

### Issue: 400 Bad Request
- **Cause**: Malformed JSON or missing required fields
- **Solution**: Validate JSON structure and ensure all required fields are present

### Issue: Message Shows Raw JSON
- **Cause**: Sending plain JSON instead of adaptive card format
- **Solution**: Wrap content in proper adaptive card structure

## Testing
```bash
# Test with simple message
python3 << 'EOF'
import os
import requests
import json

webhook_url = os.getenv('TEAMS_WEBHOOK_URL')

card = {
    "type": "message",
    "attachments": [{
        "contentType": "application/vnd.microsoft.card.adaptive",
        "content": {
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "type": "AdaptiveCard",
            "version": "1.4",
            "body": [{
                "type": "TextBlock",
                "text": "Test Message",
                "size": "Large",
                "weight": "Bolder"
            }]
        }
    }]
}

response = requests.post(webhook_url, json=card)
print(f"Status: {response.status_code}")
EOF
```

## Best Practices
1. **Always use adaptive card format** - Plain text or simple JSON will not work
2. **Keep messages concise** - Teams has display limits
3. **Use FactSet for structured data** - Better than multiple TextBlocks
4. **Include timestamps** - Helps track when events occurred
5. **Use appropriate colors** - green for success, yellow for warning, red for errors
6. **Test locally first** - Verify card structure before sending to production channel
7. **Handle errors gracefully** - Log failures but don't crash the application

## References
- [Microsoft Adaptive Cards Documentation](https://adaptivecards.io/)
- [Teams Adaptive Card Designer](https://adaptivecards.io/designer/)
- [Power Automate Teams Connector](https://docs.microsoft.com/en-us/power-automate/)