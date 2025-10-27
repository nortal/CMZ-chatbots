# Teams Report Agent

**Purpose**: Delegatable agent for formatting and sending reports to Microsoft Teams channel using proper adaptive card format

**Usage**:
- **Delegation (Preferred)**: Use Task tool to delegate to general-purpose agent
- **Direct Execution**: `/teams-report <report-type> [--data json-file] [--title "Custom Title"]`

## ⚠️ CRITICAL REQUIREMENTS

**ALWAYS DELEGATE TEAMS REPORTING TO SUB-AGENT:**
- This agent MUST be used for ALL Teams reporting operations
- NEVER send Teams messages directly without delegating
- Agent has deep knowledge of TEAMS-WEBHOOK-ADVICE.md requirements
- Agent ensures proper adaptive card format (required by Teams webhooks)
- Delegation frees up main Claude instance for other tasks

**Report Types:**
- `test-results` - Test suite execution results
- `validation` - Validation suite results
- `deployment` - Deployment status and metrics
- `code-review` - Code review findings
- `quality-gate` - Quality gate pass/fail status
- `bug-report` - Bug discovery and tracking
- `custom` - Custom report with user-provided data

## Agent Delegation Pattern

### When to Delegate
**ALWAYS delegate Teams reporting** to keep main Claude instance focused on primary tasks:
- After running test suites
- After validation runs
- After deployments
- After code reviews
- Any time a Teams notification is needed

### How to Delegate

#### Method 1: Using Task Tool (Recommended)
```python
# Delegate to general-purpose agent with specialized prompt
Task(
    subagent_type="general-purpose",
    description="Send Teams validation report",
    prompt="""You are a Teams reporting specialist. Your task is to send a comprehensive report to Microsoft Teams.

CRITICAL REQUIREMENTS:
1. Read TEAMS-WEBHOOK-ADVICE.md for adaptive card format requirements
2. Use the Python script: scripts/send_teams_report.py
3. Ensure TEAMS_WEBHOOK_URL environment variable is set
4. Validate message structure before sending

TASK:
Send a validation report with the following data:
{
  "session_id": "val_20251012_1430",
  "tested": 45,
  "total": 63,
  "coverage": 71.4,
  "duration": "18m 23s",
  "priorities": {
    "P0: Architecture": "✅ PASSED",
    "P1: Regressions": "✅ 2/2 passed",
    "P2: Infrastructure": "✅ 3/3 passed",
    "P3: Features": "⚠️ 8/10 passed",
    "P4: Comprehensive": "✅ 2/2 passed"
  },
  "status_emoji": "✅",
  "actions": [
    "Review 2 failed feature tests",
    "Address P3 test failures before deployment"
  ]
}

STEPS:
1. Verify TEAMS_WEBHOOK_URL is set (check environment)
2. Save data to /tmp/validation_report.json
3. Execute: python3 scripts/send_teams_report.py validation --data /tmp/validation_report.json
4. Report back with success/failure status
"""
)
```

#### Method 2: Direct Script Execution
```bash
# For simple cases, execute the script directly
python3 scripts/send_teams_report.py test-results --data results.json
```

## Delegation Templates

### Test Results Report
```python
def delegate_test_results_report(test_data: dict):
    """Delegate test results reporting to sub-agent"""
    Task(
        subagent_type="general-purpose",
        description="Send test results to Teams",
        prompt=f"""You are a Teams reporting specialist. Send test execution results to Microsoft Teams.

CRITICAL: Read TEAMS-WEBHOOK-ADVICE.md for proper adaptive card formatting.

DATA:
{json.dumps(test_data, indent=2)}

STEPS:
1. Verify TEAMS_WEBHOOK_URL environment variable is set
2. Create JSON file: /tmp/test_results.json with the data above
3. Execute: python3 scripts/send_teams_report.py test-results --data /tmp/test_results.json
4. Verify 202 response (success) or report error
5. Clean up temporary file

Report back: "✅ Teams notification sent" or error details
"""
    )
```

### Validation Results Report
```python
def delegate_validation_report(validation_data: dict):
    """Delegate validation results reporting to sub-agent"""
    Task(
        subagent_type="general-purpose",
        description="Send validation report to Teams",
        prompt=f"""You are a Teams reporting specialist. Send comprehensive validation results to Microsoft Teams.

CRITICAL: Read TEAMS-WEBHOOK-ADVICE.md for proper adaptive card formatting.

DATA:
{json.dumps(validation_data, indent=2)}

STEPS:
1. Check environment: echo $TEAMS_WEBHOOK_URL (must be set)
2. Save data to: /tmp/validation_report.json
3. Execute: python3 scripts/send_teams_report.py validation --data /tmp/validation_report.json
4. Verify HTTP 202 response
5. Clean up: rm /tmp/validation_report.json

Expected output: "✅ Teams notification sent successfully"
Report any errors with full details.
"""
    )
```

### Custom Report
```python
def delegate_custom_report(title: str, sections: list, actions: list = None):
    """Delegate custom report to sub-agent"""
    custom_data = {
        "title": title,
        "sections": sections,
        "actions": actions or []
    }

    Task(
        subagent_type="general-purpose",
        description=f"Send custom Teams report: {title}",
        prompt=f"""You are a Teams reporting specialist. Send a custom report to Microsoft Teams.

CRITICAL: Read TEAMS-WEBHOOK-ADVICE.md for proper adaptive card formatting.

REPORT DATA:
{json.dumps(custom_data, indent=2)}

STEPS:
1. Verify environment: TEAMS_WEBHOOK_URL must be set
2. Create /tmp/custom_report.json with data above
3. Execute: python3 scripts/send_teams_report.py custom --data /tmp/custom_report.json
4. Confirm 202 status code
5. Cleanup temp file

Report: Success message or error details with troubleshooting steps.
"""
    )
```

## Quick Delegation Examples

### After Quality Check
```python
# Main Claude runs quality checks
make quality-check > results.log

# Parse results
quality_data = parse_quality_results('results.log')

# Delegate reporting to sub-agent
Task(
    subagent_type="general-purpose",
    description="Report quality check results",
    prompt=f"""Send quality check results to Teams.

Read TEAMS-WEBHOOK-ADVICE.md, then send these results:
{json.dumps(quality_data, indent=2)}

Use: python3 scripts/send_teams_report.py test-results --data /tmp/results.json
"""
)
```

### After Validation Suite
```python
# Main Claude runs comprehensive validation
/comprehensive-validation

# Delegate reporting
Task(
    subagent_type="general-purpose",
    description="Send validation results to Teams",
    prompt="""Send comprehensive validation results to Teams.

1. Read validation results from: validation-reports/latest/VALIDATION_REPORT.md
2. Read TEAMS-WEBHOOK-ADVICE.md for formatting
3. Extract key metrics (tested, passed, failed, coverage)
4. Send via: python3 scripts/send_teams_report.py validation --data /tmp/val.json

Include P0-P4 priority breakdown in report.
"""
)
```

## Sequential Reasoning Approach

Use MCP Sequential Thinking for systematic report generation and delivery:

### Phase 1: Report Understanding
**Analyze Report Requirements:**
1. **Identify Report Type**: Determine category and expected data structure
2. **Parse Input Data**: Extract metrics, status, and detailed information
3. **Determine Priority**: Assess urgency and importance for color coding
4. **Structure Facts**: Organize data into logical sections for readability

**Key Questions:**
- What is the primary message of this report?
- Who is the target audience (developers, management, QA)?
- What action should recipients take after reading?
- What level of detail is appropriate?

### Phase 2: Adaptive Card Construction
**Build Microsoft Adaptive Card:**

#### Step 1: Read TEAMS-WEBHOOK-ADVICE.md
```bash
# Load Teams webhook formatting requirements
cat TEAMS-WEBHOOK-ADVICE.md
```

**Extract Critical Requirements:**
- Adaptive card structure with proper schema
- contentType: "application/vnd.microsoft.card.adaptive"
- version: "1.4" or compatible
- FactSet for structured data presentation
- Color coding for status (good, warning, attention)

#### Step 2: Structure Card Body
```python
# Card body components in order:
body = [
    {
        "type": "TextBlock",
        "text": title,               # Clear, descriptive title
        "size": "Large",
        "weight": "Bolder",
        "wrap": True
    },
    {
        "type": "TextBlock",
        "text": timestamp,           # When report was generated
        "size": "Small",
        "isSubtle": True,
        "wrap": True
    }
]

# Add sections based on report type
for section in sections:
    body.append({
        "type": "TextBlock",
        "text": section.title,
        "size": "Medium",
        "weight": "Bolder",
        "wrap": True,
        "spacing": "Medium"
    })

    body.append({
        "type": "FactSet",
        "facts": section.facts     # Key-value pairs
    })
```

#### Step 3: Apply Status Color Coding
```python
# Determine accent color based on status
def get_accent_color(status):
    if status == "success" or pass_rate >= 0.9:
        return "good"          # Green - success
    elif status == "warning" or 0.7 <= pass_rate < 0.9:
        return "warning"       # Yellow - needs attention
    else:
        return "attention"     # Red - critical issues
```

#### Step 4: Add Actionable Information
```python
# Always include next steps or recommendations
body.append({
    "type": "TextBlock",
    "text": "Recommended Actions",
    "size": "Medium",
    "weight": "Bolder",
    "wrap": True,
    "spacing": "Medium"
})

body.append({
    "type": "TextBlock",
    "text": "\n".join(action_items),
    "wrap": True
})
```

### Phase 3: Data Formatting
**Format Report Data for Teams Display:**

#### Quality Test Results Format
```yaml
sections:
  - title: "Git Information"
    facts:
      - {title: "Branch", value: "feature/xyz"}
      - {title: "Commit", value: "abc123 - Fix auth bug"}
      - {title: "Author", value: "KC Stegbauer"}

  - title: "Test Execution"
    facts:
      - {title: "Total Tests", value: "308 tests"}
      - {title: "Passed", value: "✅ 295"}
      - {title: "Failed", value: "❌ 13"}
      - {title: "Success Rate", value: "95.8%"}
      - {title: "Duration", value: "4m 23s"}

  - title: "Quality Gates"
    facts:
      - {title: "Code Formatting", value: "✅ PASSED"}
      - {title: "Linting", value: "⚠️ 3 warnings"}
      - {title: "Security Scan", value: "✅ PASSED"}
      - {title: "Coverage", value: "87.3%"}
```

#### Validation Results Format
```yaml
sections:
  - title: "Validation Summary"
    facts:
      - {title: "Session ID", value: "val_20251012_1430"}
      - {title: "Endpoints Tested", value: "45/63 (71%)"}
      - {title: "P0 Architecture", value: "✅ PASSED"}
      - {title: "P1 Regressions", value: "✅ PASSED"}

  - title: "Test Results by Priority"
    facts:
      - {title: "P0: Architecture", value: "✅ PASSED (BLOCKING)"}
      - {title: "P1: Regressions", value: "✅ 2/2 passed"}
      - {title: "P2: Infrastructure", value: "✅ 3/3 passed"}
      - {title: "P3: Features", value: "⚠️ 8/10 passed"}
      - {title: "P4: Comprehensive", value: "✅ 2/2 passed"}
```

#### Deployment Status Format
```yaml
sections:
  - title: "Deployment Information"
    facts:
      - {title: "Environment", value: "Production"}
      - {title: "Version", value: "v2.3.1"}
      - {title: "Status", value: "✅ Successful"}
      - {title: "Duration", value: "8m 12s"}

  - title: "Health Checks"
    facts:
      - {title: "API Health", value: "✅ Healthy"}
      - {title: "Database", value: "✅ Connected"}
      - {title: "Cache", value: "✅ Operational"}
      - {title: "CDN", value: "✅ Serving"}
```

#### Code Review Format
```yaml
sections:
  - title: "Review Summary"
    facts:
      - {title: "Pull Request", value: "#123"}
      - {title: "Files Changed", value: "23 files"}
      - {title: "Lines Added", value: "+456"}
      - {title: "Lines Removed", value: "-234"}

  - title: "Quality Analysis"
    facts:
      - {title: "Security Issues", value: "❌ 2 critical"}
      - {title: "Code Smells", value: "⚠️ 5 medium"}
      - {title: "Duplications", value: "✅ None"}
      - {title: "Coverage Impact", value: "+2.3%"}
```

### Phase 4: Message Delivery
**Send to Teams Channel:**

#### Step 1: Retrieve Webhook URL
```python
import os

webhook_url = os.getenv('TEAMS_WEBHOOK_URL')

if not webhook_url:
    raise ValueError(
        "TEAMS_WEBHOOK_URL environment variable not set. "
        "Export webhook URL before sending reports."
    )
```

#### Step 2: Construct Complete Message
```python
import requests
from datetime import datetime

message = {
    "type": "message",
    "attachments": [
        {
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": {
                "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                "type": "AdaptiveCard",
                "version": "1.4",
                "body": body  # Constructed in Phase 2
            }
        }
    ]
}
```

#### Step 3: Send with Error Handling
```python
try:
    response = requests.post(
        webhook_url,
        json=message,
        headers={"Content-Type": "application/json"},
        timeout=10
    )

    if response.status_code == 202:
        print("✅ Teams notification sent successfully")
        return 0
    else:
        print(f"❌ Failed to send: HTTP {response.status_code}")
        print(response.text)
        return 1

except requests.exceptions.Timeout:
    print("❌ Request timeout - Teams webhook not responding")
    return 1

except Exception as e:
    print(f"❌ Exception: {str(e)}")
    return 1
```

#### Step 4: Verify Delivery
```python
# 202 Accepted means Teams received the message
# Message should appear in channel within 1-2 seconds
# If no message appears:
# 1. Check webhook URL is correct
# 2. Verify adaptive card format
# 3. Check Teams channel permissions
```

## Report Type Templates

### Test Results Template
```python
def format_test_results(data):
    """Format test execution results for Teams"""
    return {
        "title": f"{data['status_emoji']} Test Suite Execution Report",
        "sections": [
            {
                "title": "Execution Summary",
                "facts": [
                    {"title": "Total Tests", "value": str(data['total'])},
                    {"title": "Passed", "value": f"✅ {data['passed']}"},
                    {"title": "Failed", "value": f"❌ {data['failed']}"},
                    {"title": "Success Rate", "value": f"{data['success_rate']}%"},
                    {"title": "Duration", "value": data['duration']}
                ]
            },
            {
                "title": "Quality Gates",
                "facts": [
                    {"title": gate, "value": status}
                    for gate, status in data['quality_gates'].items()
                ]
            }
        ]
    }
```

### Validation Results Template
```python
def format_validation_results(data):
    """Format validation suite results for Teams"""
    return {
        "title": f"{data['status_emoji']} Comprehensive Validation Report",
        "sections": [
            {
                "title": "Validation Coverage",
                "facts": [
                    {"title": "Session ID", "value": data['session_id']},
                    {"title": "Endpoints Tested", "value": f"{data['tested']}/{data['total']} ({data['coverage']}%)"},
                    {"title": "Duration", "value": data['duration']}
                ]
            },
            {
                "title": "Results by Priority",
                "facts": [
                    {"title": f"P{i}: {name}", "value": status}
                    for i, (name, status) in enumerate(data['priorities'].items())
                ]
            }
        ]
    }
```

### Deployment Status Template
```python
def format_deployment_status(data):
    """Format deployment status for Teams"""
    return {
        "title": f"{data['status_emoji']} Deployment {data['status']}",
        "sections": [
            {
                "title": "Deployment Information",
                "facts": [
                    {"title": "Environment", "value": data['environment']},
                    {"title": "Version", "value": data['version']},
                    {"title": "Status", "value": data['status']},
                    {"title": "Duration", "value": data['duration']}
                ]
            },
            {
                "title": "Health Checks",
                "facts": [
                    {"title": check, "value": status}
                    for check, status in data['health_checks'].items()
                ]
            }
        ]
    }
```

## Implementation Guidelines

### Status Emoji Selection
```python
def get_status_emoji(pass_rate: float) -> str:
    """Determine appropriate emoji based on success rate"""
    if pass_rate >= 0.95:
        return "✅"  # Excellent - green checkmark
    elif pass_rate >= 0.80:
        return "⚠️"   # Warning - needs attention
    elif pass_rate >= 0.60:
        return "❌"  # Critical - red X
    else:
        return "🚨"  # Emergency - siren
```

### Fact Formatting
```python
def format_fact(key: str, value: any) -> dict:
    """Format data as Teams FactSet entry"""
    # Convert all values to strings
    value_str = str(value)

    # Add appropriate emoji for common statuses
    if "passed" in key.lower() or "success" in key.lower():
        value_str = f"✅ {value_str}"
    elif "failed" in key.lower() or "error" in key.lower():
        value_str = f"❌ {value_str}"
    elif "warning" in key.lower():
        value_str = f"⚠️ {value_str}"

    return {"title": key, "value": value_str}
```

### Action Items Generation
```python
def generate_action_items(data) -> list:
    """Generate actionable recommendations"""
    items = []

    if data['failed_tests'] > 0:
        items.append(f"Review {data['failed_tests']} failed test(s)")

    if data['coverage'] < 80:
        items.append(f"Improve test coverage from {data['coverage']}% to 80%")

    if data['security_issues'] > 0:
        items.append(f"Address {data['security_issues']} security issue(s)")

    if not items:
        items.append("✅ All quality gates passed - ready for deployment")

    return items
```

## Error Handling

### Common Issues and Solutions

**Issue: 202 Response but No Message**
- **Cause**: Incorrect adaptive card format
- **Solution**: Validate against adaptive card schema
- **Check**: Ensure all required fields present (type, attachments, content)

**Issue: 400 Bad Request**
- **Cause**: Malformed JSON structure
- **Solution**: Validate JSON syntax before sending
- **Check**: Use `json.dumps()` with `indent=2` to verify structure

**Issue: Message Shows Raw JSON**
- **Cause**: Not using adaptive card format
- **Solution**: Wrap in proper contentType and structure
- **Check**: Verify "contentType": "application/vnd.microsoft.card.adaptive"

**Issue: Webhook URL Not Found**
- **Cause**: TEAMS_WEBHOOK_URL environment variable not set
- **Solution**: Export webhook URL before running
- **Check**: `echo $TEAMS_WEBHOOK_URL`

## Quality Standards

### Message Quality Checklist
- [ ] Clear, descriptive title
- [ ] Timestamp included
- [ ] Appropriate status emoji
- [ ] Facts organized in logical sections
- [ ] Key metrics highlighted
- [ ] Actionable recommendations provided
- [ ] Proper color coding applied
- [ ] No sensitive data exposed
- [ ] Message length < 28KB (Teams limit)

### Testing Before Sending
```bash
# Test message structure locally
python3 << 'EOF'
import json

# Your message structure
message = {...}

# Validate JSON
try:
    json_str = json.dumps(message, indent=2)
    print("✅ Valid JSON structure")
    print(json_str)
except Exception as e:
    print(f"❌ Invalid JSON: {e}")
EOF
```

## Integration with Other Commands

### Use with Comprehensive Validation
```bash
# Run validation and send results to Teams
/comprehensive-validation && /teams-report validation
```

### Use with Quality Checks
```bash
# Run quality gates and report to Teams
make quality-check && /teams-report test-results
```

### Use with Deployments
```bash
# Deploy and notify Teams of status
./deploy.sh && /teams-report deployment --data deployment.json
```

## Success Criteria
1. **Message Delivered**: 202 status code from Teams webhook
2. **Proper Format**: Adaptive card displays correctly in Teams
3. **Readable**: Information organized and easy to understand
4. **Actionable**: Clear next steps provided
5. **Timely**: Message sent within 2 seconds
6. **Reliable**: No errors during formatting or sending

## Command Options

### --data
Provide data from JSON file:
```bash
/teams-report test-results --data test_report.json
```

### --title
Custom report title:
```bash
/teams-report custom --title "Daily Regression Test Results"
```

### --priority
Set message priority/color:
```bash
/teams-report validation --priority critical
```

### --dry-run
Preview message without sending:
```bash
/teams-report test-results --dry-run
```

## References
- `TEAMS-WEBHOOK-ADVICE.md` - Complete Teams webhook formatting guide
- `TEAMS-REPORTING-ADVICE.md` - Best practices and troubleshooting
- [Microsoft Adaptive Cards Documentation](https://adaptivecards.io/)
- [Adaptive Card Designer](https://adaptivecards.io/designer/)
