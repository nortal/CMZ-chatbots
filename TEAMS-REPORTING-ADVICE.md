# TEAMS-REPORTING-ADVICE.md

## Overview
Best practices, troubleshooting guide, and lessons learned for using the Teams reporting agent (`/teams-report`) to send formatted notifications to Microsoft Teams channels.

## Critical Directive

**🚨 ALWAYS USE /teams-report FOR TEAMS NOTIFICATIONS**

Never send Teams messages manually or directly. The `/teams-report` agent:
- Ensures proper Microsoft Adaptive Card format (required by Teams)
- Applies consistent formatting and branding
- Handles error conditions gracefully
- Validates message structure before sending
- Provides appropriate status indicators and emoji
- Organizes data for maximum readability

## Best Practices

### 1. Report Structure
**DO:**
- Start with clear, descriptive title indicating report type
- Include timestamp for temporal context
- Use FactSet for structured key-value data
- Group related facts into logical sections
- Provide actionable recommendations
- Use appropriate status emoji (✅, ⚠️, ❌, 🚨)

**DON'T:**
- Send unstructured text blocks
- Mix different report types in one message
- Include sensitive data (passwords, tokens, credentials)
- Create overly long messages (>28KB Teams limit)
- Use inconsistent formatting between reports

### 2. Status Indicators
```python
# Use consistent status emoji across all reports
SUCCESS = "✅"      # ≥95% pass rate, green color
WARNING = "⚠️"      # 80-94% pass rate, yellow color
FAILURE = "❌"      # 60-79% pass rate, red color
CRITICAL = "🚨"    # <60% pass rate, urgent attention

# Apply to appropriate metrics
"Passed": "✅ 295/308"
"Failed": "❌ 13/308"
"Coverage": "⚠️ 78.3%"
```

### 3. Data Organization
```python
# Group related information
sections = [
    {
        "title": "Execution Summary",
        "facts": [
            # High-level metrics
            {"title": "Total Tests", "value": "308"},
            {"title": "Success Rate", "value": "95.8%"}
        ]
    },
    {
        "title": "Quality Gates",
        "facts": [
            # Detailed breakdown
            {"title": "Code Formatting", "value": "✅ PASSED"},
            {"title": "Security Scan", "value": "✅ PASSED"}
        ]
    }
]
```

### 4. Actionable Recommendations
```python
# Always include next steps
action_items = [
    "1. Review 13 failed test cases in test_auth.py",
    "2. Improve code coverage from 78% to 80% target",
    "3. Address 2 security warnings before deployment"
]

# Or for success:
action_items = [
    "✅ All quality gates passed - ready for deployment",
    "Consider running load tests for production validation"
]
```

## Common Use Cases

### Test Suite Execution
```bash
# After running comprehensive test suite
make quality-check
/teams-report test-results --data quality_results.json
```

**Expected Sections:**
- Execution Summary (total, passed, failed, success rate)
- Quality Gates (formatting, linting, security)
- Git Information (branch, commit, author)
- Recommended Actions

### Validation Results
```bash
# After comprehensive validation
/comprehensive-validation
/teams-report validation --data validation_report.json
```

**Expected Sections:**
- Validation Coverage (endpoints tested, coverage %)
- Results by Priority (P0-P4 breakdown)
- Failed Tests Analysis
- Re-Test Results (methodology validation)

### Deployment Status
```bash
# After deployment
./deploy.sh production
/teams-report deployment --data deployment_status.json
```

**Expected Sections:**
- Deployment Information (environment, version, status)
- Health Checks (API, database, cache, CDN)
- Deployment Timeline
- Rollback Plan (if applicable)

### Code Review Findings
```bash
# After comprehensive code review
/comprehensive-code-review
/teams-report code-review --data review_findings.json
```

**Expected Sections:**
- Review Summary (files changed, lines added/removed)
- Quality Analysis (security, code smells, duplications)
- Coverage Impact
- Priority Issues

## Troubleshooting

### Issue: No Message Appears in Teams

**Symptoms:**
- HTTP 202 response received
- No error messages
- Message not visible in Teams channel

**Root Causes:**
1. **Incorrect adaptive card format**
   - Missing required fields (type, attachments, content)
   - Wrong contentType (must be "application/vnd.microsoft.card.adaptive")
   - Invalid schema version

2. **Malformed JSON structure**
   - Syntax errors in JSON
   - Incorrect nesting of elements
   - Invalid field types

3. **Message exceeds Teams limits**
   - Message size > 28KB
   - Too many facts in single FactSet
   - Extremely long text in TextBlocks

**Solutions:**
```python
# Validate message structure
import json

def validate_teams_message(message):
    """Validate Teams message structure"""
    required_fields = ["type", "attachments"]

    # Check top-level structure
    for field in required_fields:
        if field not in message:
            raise ValueError(f"Missing required field: {field}")

    # Check adaptive card structure
    attachment = message["attachments"][0]
    if attachment["contentType"] != "application/vnd.microsoft.card.adaptive":
        raise ValueError("Incorrect contentType")

    # Check content structure
    content = attachment["content"]
    if content["type"] != "AdaptiveCard":
        raise ValueError("Content must be AdaptiveCard")

    # Validate size
    message_size = len(json.dumps(message))
    if message_size > 28 * 1024:  # 28KB limit
        raise ValueError(f"Message too large: {message_size} bytes")

    return True
```

### Issue: 400 Bad Request

**Symptoms:**
- HTTP 400 response
- Error message from Teams webhook

**Root Causes:**
1. **Invalid JSON syntax**
2. **Missing required adaptive card fields**
3. **Incorrect field types (e.g., string instead of boolean)**

**Solutions:**
```bash
# Test JSON structure locally first
python3 << 'EOF'
import json

message = {
    # Your message structure here
}

try:
    # Validate JSON
    json_str = json.dumps(message, indent=2)
    parsed = json.loads(json_str)
    print("✅ Valid JSON structure")

    # Validate adaptive card
    assert parsed["type"] == "message"
    assert "attachments" in parsed
    assert parsed["attachments"][0]["contentType"] == "application/vnd.microsoft.card.adaptive"
    print("✅ Valid adaptive card structure")

except Exception as e:
    print(f"❌ Validation failed: {e}")
EOF
```

### Issue: Message Shows Raw JSON

**Symptoms:**
- Message appears in Teams but displays as code/JSON
- Not rendered as formatted card

**Root Cause:**
- Not using adaptive card format
- Sending plain JSON instead of adaptive card structure

**Solution:**
```python
# WRONG - Plain JSON
wrong_message = {
    "text": "Test results: 95% passed"
}

# RIGHT - Adaptive Card
right_message = {
    "type": "message",
    "attachments": [{
        "contentType": "application/vnd.microsoft.card.adaptive",
        "content": {
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "type": "AdaptiveCard",
            "version": "1.4",
            "body": [
                {
                    "type": "TextBlock",
                    "text": "Test Results",
                    "size": "Large",
                    "weight": "Bolder"
                },
                {
                    "type": "FactSet",
                    "facts": [
                        {"title": "Success Rate", "value": "95%"}
                    ]
                }
            ]
        }
    }]
}
```

### Issue: Webhook URL Not Set

**Symptoms:**
- Error: "TEAMS_WEBHOOK_URL environment variable not set"

**Solution:**
```bash
# Export webhook URL (from TEAMS-WEBHOOK-ADVICE.md)
export TEAMS_WEBHOOK_URL="https://default7c359f6b9f2f4042bf2db08ce16c5c.c1.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/cba76b9b30b644aaae7784ead5b54be4/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=03f33nmke2hKhd0FhZqpLte_NVMWI3MQkd6jqLDAVqA"

# Verify it's set
echo $TEAMS_WEBHOOK_URL

# Add to .env file for persistence
echo "TEAMS_WEBHOOK_URL=\"$TEAMS_WEBHOOK_URL\"" >> .env
```

## Testing Strategy

### Local Testing
```python
# Test message structure without sending
def test_message_structure():
    """Test adaptive card structure locally"""
    message = build_test_results_message(sample_data)

    # Validate structure
    validate_teams_message(message)

    # Print formatted JSON
    print(json.dumps(message, indent=2))

    # Check size
    size_kb = len(json.dumps(message)) / 1024
    print(f"Message size: {size_kb:.2f} KB")
```

### Dry Run Mode
```bash
# Preview message without sending
/teams-report test-results --dry-run --data test_data.json
```

**Output:**
```
=== Teams Message Preview ===

Title: ✅ Test Suite Execution Report

Sections:
  1. Execution Summary
     - Total Tests: 308
     - Passed: ✅ 295
     - Failed: ❌ 13
     - Success Rate: 95.8%

  2. Quality Gates
     - Code Formatting: ✅ PASSED
     - Linting: ✅ PASSED

Message size: 2.3 KB (well under 28KB limit)

Preview complete. Use without --dry-run to send.
```

### Incremental Testing
```bash
# Test with minimal data first
/teams-report custom --title "Test Message" --data minimal.json

# Then add complexity
/teams-report test-results --data small_dataset.json

# Finally full report
/teams-report test-results --data full_results.json
```

## Performance Optimization

### Message Size Reduction
```python
# If approaching 28KB limit, reduce verbosity
def truncate_long_lists(facts, max_items=20):
    """Truncate long fact lists"""
    if len(facts) > max_items:
        truncated = facts[:max_items]
        truncated.append({
            "title": "Additional Items",
            "value": f"... and {len(facts) - max_items} more"
        })
        return truncated
    return facts

# Summarize detailed logs
def summarize_errors(errors):
    """Summarize error list instead of full details"""
    error_counts = {}
    for error in errors:
        error_type = error.get("type", "Unknown")
        error_counts[error_type] = error_counts.get(error_type, 0) + 1

    return [
        {"title": error_type, "value": f"{count} occurrences"}
        for error_type, count in error_counts.items()
    ]
```

### Batching Reports
```python
# For large datasets, send multiple focused reports
def send_batch_reports(all_data):
    """Send multiple reports instead of one huge message"""
    # Summary report
    send_teams_report("test-results", summary_data(all_data))

    # Detailed failures report (if needed)
    if all_data['failed'] > 0:
        send_teams_report("test-failures", failure_details(all_data))

    # Performance metrics report
    if all_data['slow_tests']:
        send_teams_report("performance", performance_data(all_data))
```

## Integration Patterns

### CI/CD Pipeline Integration
```yaml
# .github/workflows/test.yml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Run tests
        run: make quality-check > test_output.log 2>&1
        continue-on-error: true

      - name: Parse results
        run: |
          python3 scripts/parse_test_results.py test_output.log > results.json

      - name: Send Teams notification
        env:
          TEAMS_WEBHOOK_URL: ${{ secrets.TEAMS_WEBHOOK_URL }}
        run: |
          /teams-report test-results --data results.json
```

### Scheduled Reports
```bash
# Daily validation report (cron job)
0 9 * * * cd /path/to/cmz && /comprehensive-validation && /teams-report validation
```

### On-Demand Reports
```bash
# Interactive command for developers
alias teams-status='/teams-report test-results --data $(make quality-check && cat latest_results.json)'
```

## Security Considerations

### Sensitive Data Protection
```python
# Never include in Teams messages
SENSITIVE_PATTERNS = [
    r'password',
    r'token',
    r'api[_-]?key',
    r'secret',
    r'credential',
    r'AWS_[A-Z_]+',
    r'GITHUB_TOKEN'
]

def sanitize_data(data):
    """Remove sensitive information"""
    import re

    sanitized = str(data)
    for pattern in SENSITIVE_PATTERNS:
        sanitized = re.sub(pattern, '[REDACTED]', sanitized, flags=re.IGNORECASE)

    return sanitized
```

### Webhook URL Protection
```bash
# Store webhook URL securely
# ✅ GOOD: Environment variable or secure vault
export TEAMS_WEBHOOK_URL="..."

# ❌ BAD: Hardcoded in scripts
webhook="https://..." # Never do this

# ❌ BAD: Committed to git
echo "TEAMS_WEBHOOK_URL=..." >> .env  # Add .env to .gitignore!
```

## Monitoring and Debugging

### Enable Debug Logging
```python
# Add debug output to teams reporting
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def send_teams_message(message):
    logger.debug("Message structure: %s", json.dumps(message, indent=2))
    logger.debug("Message size: %d bytes", len(json.dumps(message)))

    response = requests.post(webhook_url, json=message)

    logger.debug("Response status: %d", response.status_code)
    logger.debug("Response body: %s", response.text)
```

### Track Message Delivery
```python
# Log all Teams notifications
def log_notification(report_type, status, response_code):
    """Track notification history"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "report_type": report_type,
        "status": status,
        "response_code": response_code
    }

    with open("teams_notifications.log", "a") as f:
        f.write(json.dumps(log_entry) + "\n")
```

## Success Metrics

### Message Quality KPIs
- **Delivery Rate**: > 99% (202 responses / attempts)
- **Format Errors**: < 1% (400 responses / attempts)
- **Message Size**: < 10KB average (well under 28KB limit)
- **Delivery Time**: < 2 seconds per message

### Content Quality Metrics
- **Readability**: Clear title, organized sections, proper emoji usage
- **Actionability**: Specific recommendations in > 90% of reports
- **Accuracy**: < 1% false positive/negative in status indicators
- **Completeness**: All required sections present in reports

## References
- `/teams-report` - Main Teams reporting agent command
- `TEAMS-WEBHOOK-ADVICE.md` - Technical webhook formatting guide
- [Microsoft Adaptive Cards](https://adaptivecards.io/)
- [Adaptive Card Designer](https://adaptivecards.io/designer/) - Visual testing tool
- [Teams Webhook Documentation](https://docs.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/)
