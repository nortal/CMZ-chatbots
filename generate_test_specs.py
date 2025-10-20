#!/usr/bin/env python3

"""
Generate comprehensive test specifications for all PR003946 tickets
Categorizes tickets and creates systematic test specs for each type
"""

import json
import os
import re
from pathlib import Path
from datetime import datetime

def load_tickets():
    """Load all ticket data from consolidated JSON"""
    with open('jira_data/all_tickets_consolidated.json', 'r') as f:
        return json.load(f)

def categorize_ticket(ticket):
    """Categorize ticket for appropriate test type"""
    summary = ticket['fields']['summary'].lower()
    issue_type = ticket['fields']['issuetype']['name']

    # API endpoint tickets (integration tests)
    if any(method in summary for method in ['get ', 'post ', 'put ', 'delete ']):
        return 'integration'

    # Security-related tickets
    if any(term in summary for term in ['auth', 'security', 'token', 'permission', 'role']):
        return 'security'

    # UI/Frontend tickets (playwright tests)
    if any(term in summary for term in ['ui', 'frontend', 'page', 'form', 'dashboard']):
        return 'playwright'

    # Bug tickets (mixed based on description)
    if issue_type == 'Bug':
        description = ticket['fields'].get('description', {}).get('content', [{}])[0].get('content', [{}])[0].get('text', '') if ticket['fields'].get('description') else ''
        if any(term in description.lower() for term in ['api', 'endpoint', 'server']):
            return 'integration'
        elif any(term in description.lower() for term in ['ui', 'interface', 'browser']):
            return 'playwright'
        elif any(term in description.lower() for term in ['auth', 'security']):
            return 'security'
        else:
            return 'unit'

    # Default to unit tests for other tasks
    return 'unit'

def extract_description_text(description_field):
    """Extract plain text from Atlassian document format"""
    if not description_field or not isinstance(description_field, dict):
        return ""

    def extract_text_recursive(content):
        text_parts = []
        if isinstance(content, dict):
            if content.get('type') == 'text':
                text_parts.append(content.get('text', ''))
            elif 'content' in content:
                for item in content['content']:
                    text_parts.extend(extract_text_recursive(item))
        elif isinstance(content, list):
            for item in content:
                text_parts.extend(extract_text_recursive(item))
        return text_parts

    content = description_field.get('content', [])
    all_text = extract_text_recursive(content)
    return ' '.join(all_text).strip()

def generate_advice_file(ticket, test_category):
    """Generate ADVICE.md file for a ticket"""
    key = ticket['key']
    fields = ticket['fields']
    summary = fields['summary']
    status = fields['status']['name']
    issue_type = fields['issuetype']['name']
    description = extract_description_text(fields.get('description'))

    # Extract acceptance criteria if present
    acceptance_criteria = []
    if description:
        # Look for acceptance criteria patterns
        ac_patterns = [
            r'acceptance criteria:?\s*(.+?)(?=\n\n|\n[A-Z]|\Z)',
            r'success criteria:?\s*(.+?)(?=\n\n|\n[A-Z]|\Z)',
            r'definition of done:?\s*(.+?)(?=\n\n|\n[A-Z]|\Z)'
        ]
        for pattern in ac_patterns:
            matches = re.findall(pattern, description, re.IGNORECASE | re.DOTALL)
            if matches:
                acceptance_criteria.extend(matches)
                break

    # Generate test scenarios based on category and content
    test_scenarios = generate_test_scenarios(ticket, test_category)

    advice_content = f"""# {key} - Test Specification Analysis

## Ticket Information
- **Ticket**: {key}
- **Summary**: {summary}
- **Type**: {issue_type}
- **Status**: {status}
- **Test Category**: {test_category.title()}

## Description
{description if description else "No detailed description available."}

## Acceptance Criteria
{chr(10).join(f"- {ac.strip()}" for ac in acceptance_criteria) if acceptance_criteria else "- Acceptance criteria to be derived from summary and description"}

## Technical Analysis

### Component Impact
{generate_component_analysis(ticket, test_category)}

### Dependencies
{generate_dependencies_analysis(ticket, test_category)}

### Test Scenarios Identified
{chr(10).join(f"- {scenario}" for scenario in test_scenarios)}

### Success Criteria
{generate_success_criteria(ticket, test_category)}

### Risk Assessment
{generate_risk_assessment(ticket, test_category)}

## Test Strategy
- **Primary Test Type**: {test_category.title()} Test
- **Complexity**: {assess_complexity(ticket)}
- **Priority**: {assess_priority(ticket)}
- **Estimated Effort**: {estimate_effort(ticket, test_category)}

## Notes
- Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Based on systematic analysis of ticket content and CMZ project patterns
- Should be reviewed and refined based on implementation details
"""

    return advice_content

def generate_howto_test_file(ticket, test_category):
    """Generate howto-test.md file for a ticket"""
    key = ticket['key']
    fields = ticket['fields']
    summary = fields['summary']

    # Generate specific test instructions based on category
    # test_instructions = generate_test_instructions(ticket, test_category)  # Not needed

    howto_content = f"""# Test Instructions: {summary}

## Ticket Information
- **Ticket**: {key}
- **Type**: {fields['issuetype']['name']}
- **Priority**: {fields.get('priority', {}).get('name', 'Not Set')}
- **Component**: {test_category.title()}

## Test Objective
{generate_test_objective(ticket, test_category)}

## Prerequisites
{generate_prerequisites(test_category)}

## Test Steps (Sequential Execution Required)

### 1. Setup Phase
{generate_setup_steps(ticket, test_category)}

### 2. Execution Phase
{generate_execution_steps(ticket, test_category)}

### 3. Validation Phase
{generate_validation_steps(ticket, test_category)}

## Pass/Fail Criteria

### ✅ PASS Conditions:
{generate_pass_conditions(ticket, test_category)}

### ❌ FAIL Conditions:
{generate_fail_conditions(ticket, test_category)}

## Substeps and Multiple Test Scenarios
{generate_substeps(ticket, test_category)}

## Evidence Collection
{generate_evidence_requirements(test_category)}

## Sequential Reasoning Checkpoints
- **Pre-Test Prediction**: {generate_prediction(ticket, test_category)}
- **Expected Outcome**: {generate_expected_outcome(ticket, test_category)}
- **Variance Analysis**: Document differences between expected and actual results
- **Root Cause Assessment**: For any failures, analyze underlying causes systematically

## Troubleshooting
{generate_troubleshooting_guide(ticket, test_category)}

---
*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Test Category: {test_category.title()}*
*CMZ TDD Framework v1.0*
"""

    return howto_content

def generate_test_scenarios(ticket, test_category):
    """Generate test scenarios based on ticket content and category"""
    summary = ticket['fields']['summary'].lower()
    scenarios = []

    if test_category == 'integration':
        if 'get' in summary:
            scenarios.extend([
                "Valid GET request returns correct data",
                "Invalid parameters return appropriate error",
                "Authentication required for protected endpoints",
                "Response schema matches OpenAPI specification"
            ])
        elif 'post' in summary:
            scenarios.extend([
                "Valid POST creates resource successfully",
                "Invalid JSON payload rejected with clear error",
                "Required fields validation",
                "Duplicate creation handling"
            ])
        elif 'delete' in summary:
            scenarios.extend([
                "Valid DELETE removes resource",
                "Non-existent resource returns 404",
                "Permission checks for delete operations",
                "Cascading delete behavior validation"
            ])

    elif test_category == 'security':
        scenarios.extend([
            "Authentication mechanisms work correctly",
            "Authorization prevents unauthorized access",
            "Input validation prevents injection attacks",
            "Session management functions properly"
        ])

    elif test_category == 'playwright':
        scenarios.extend([
            "UI elements render correctly across browsers",
            "User interactions trigger expected behaviors",
            "Form submissions work with valid/invalid data",
            "Error messages display appropriately"
        ])

    else:  # unit
        scenarios.extend([
            "Function returns expected output for valid input",
            "Edge cases handled appropriately",
            "Error conditions raise proper exceptions",
            "Business logic follows specifications"
        ])

    return scenarios

def generate_component_analysis(ticket, test_category):
    """Analyze which components are affected"""
    summary = ticket['fields']['summary']

    components = []
    if 'api' in summary.lower() or any(method in summary.lower() for method in ['get', 'post', 'put', 'delete']):
        components.append("Backend API (Flask/Connexion)")
    if 'dynamo' in summary.lower() or 'database' in summary.lower():
        components.append("DynamoDB persistence layer")
    if 'auth' in summary.lower():
        components.append("Authentication system")
    if 'frontend' in summary.lower() or 'ui' in summary.lower():
        components.append("Frontend React application")

    if not components:
        components.append("Core business logic")

    return "\n".join(f"- {comp}" for comp in components)

def generate_dependencies_analysis(ticket, test_category):
    """Analyze test dependencies"""
    dependencies = [
        "Backend services running on localhost:8080",
        "DynamoDB tables accessible with quest-dev-* naming",
        "Test user accounts (parent1@test.cmz.org, student1@test.cmz.org, etc.)",
        "Docker environment configured and running"
    ]

    if test_category == 'playwright':
        dependencies.append("Frontend services running on localhost:3001")
        dependencies.append("Browser compatibility testing environment")

    return "\n".join(f"- {dep}" for dep in dependencies)

def generate_success_criteria(ticket, test_category):
    """Generate success criteria"""
    criteria = []

    if test_category == 'integration':
        criteria.extend([
            "API endpoint responds with correct HTTP status codes",
            "Response data matches expected schema and format",
            "Database operations complete successfully",
            "Error handling works for invalid inputs"
        ])
    elif test_category == 'security':
        criteria.extend([
            "Authentication mechanisms prevent unauthorized access",
            "Input validation blocks malicious content",
            "Session management maintains security",
            "Authorization checks enforce role-based permissions"
        ])
    elif test_category == 'playwright':
        criteria.extend([
            "UI functions correctly across target browsers",
            "User workflows complete successfully",
            "Responsive design works on different screen sizes",
            "Accessibility requirements met"
        ])
    else:  # unit
        criteria.extend([
            "Functions produce expected outputs",
            "Edge cases handled without errors",
            "Business logic implemented correctly",
            "Code coverage meets project standards"
        ])

    return "\n".join(f"- {criterion}" for criterion in criteria)

def generate_risk_assessment(ticket, test_category):
    """Generate risk assessment"""
    risks = []

    summary = ticket['fields']['summary'].lower()
    if 'delete' in summary:
        risks.append("**High**: Delete operations could cause data loss")
    if 'auth' in summary:
        risks.append("**High**: Authentication changes affect system security")
    if 'critical' in summary or 'production' in summary:
        risks.append("**Medium**: Production system impact")

    if not risks:
        risks.append("**Low**: Standard development changes with minimal system impact")

    return "\n".join(f"- {risk}" for risk in risks)

def assess_complexity(ticket):
    """Assess test complexity"""
    summary = ticket['fields']['summary'].lower()
    description = extract_description_text(ticket['fields'].get('description', {}))

    if any(term in (summary + description).lower() for term in ['integration', 'multiple', 'complex', 'system']):
        return "High"
    elif any(term in (summary + description).lower() for term in ['api', 'endpoint', 'database']):
        return "Medium"
    else:
        return "Low"

def assess_priority(ticket):
    """Assess test priority"""
    priority = ticket['fields'].get('priority', {}).get('name', 'Medium')
    summary = ticket['fields']['summary'].lower()

    if any(term in summary for term in ['critical', 'security', 'auth']):
        return "High"
    elif any(term in summary for term in ['delete', 'post', 'create']):
        return "Medium"
    else:
        return priority

def estimate_effort(ticket, test_category):
    """Estimate testing effort"""
    complexity = assess_complexity(ticket)

    if test_category == 'playwright':
        base_effort = "4-6 hours"
    elif test_category == 'integration':
        base_effort = "2-4 hours"
    elif test_category == 'security':
        base_effort = "3-5 hours"
    else:  # unit
        base_effort = "1-2 hours"

    if complexity == "High":
        return f"{base_effort} (High complexity)"
    elif complexity == "Low":
        return f"{base_effort} (Low complexity)"
    else:
        return base_effort

def generate_test_objective(ticket, test_category):
    """Generate clear test objective"""
    summary = ticket['fields']['summary']

    if test_category == 'integration':
        return f"Validate that {summary} functions correctly through API testing with proper request/response handling and database integration."
    elif test_category == 'security':
        return f"Verify security aspects of {summary} including authentication, authorization, and input validation."
    elif test_category == 'playwright':
        return f"Ensure {summary} provides correct user experience across browsers with functional UI interactions."
    else:  # unit
        return f"Test individual components and business logic related to {summary} in isolation."

def generate_prerequisites(test_category):
    """Generate prerequisites checklist"""
    base_prereqs = [
        "- [ ] Backend services running on localhost:8080",
        "- [ ] DynamoDB tables accessible (quest-dev-* tables)",
        "- [ ] Test user accounts available and authenticated",
        "- [ ] Required test data present in system",
        "- [ ] Environment variables loaded from .env.local"
    ]

    if test_category == 'playwright':
        base_prereqs.extend([
            "- [ ] Frontend services running on localhost:3001",
            "- [ ] Browser testing environment configured",
            "- [ ] Playwright dependencies installed"
        ])

    return "\n".join(base_prereqs)

def generate_setup_steps(ticket, test_category):
    """Generate setup steps"""
    steps = [
        "- Verify all prerequisite services are running",
        "- Confirm test data is available and accessible",
        "- Validate authentication credentials are working"
    ]

    summary = ticket['fields']['summary'].lower()
    if 'database' in summary or 'dynamo' in summary:
        steps.append("- Verify DynamoDB table connectivity and test data setup")

    if test_category == 'playwright':
        steps.append("- Launch browser and navigate to application")
        steps.append("- Verify initial page load and basic functionality")

    return "\n".join(steps)

def generate_execution_steps(ticket, test_category):
    """Generate execution steps"""
    summary = ticket['fields']['summary']

    if test_category == 'integration':
        return generate_api_execution_steps(summary)
    elif test_category == 'security':
        return generate_security_execution_steps(summary)
    elif test_category == 'playwright':
        return generate_ui_execution_steps(summary)
    else:
        return generate_unit_execution_steps(summary)

def generate_api_execution_steps(summary):
    """Generate API-specific execution steps"""
    if 'GET' in summary:
        return """- Execute GET request to the specified endpoint
- Test with valid parameters and authentication
- Test with invalid/missing parameters
- Verify response format and status codes"""
    elif 'POST' in summary:
        return """- Execute POST request with valid JSON payload
- Test with invalid/malformed JSON data
- Test with missing required fields
- Verify resource creation and response data"""
    elif 'DELETE' in summary:
        return """- Execute DELETE request for existing resource
- Test delete of non-existent resource
- Verify cascading delete behavior if applicable
- Confirm resource is properly removed"""
    else:
        return """- Execute the functionality described in ticket summary
- Test with valid inputs and expected conditions
- Test with edge cases and boundary conditions
- Verify all expected behaviors occur"""

def generate_security_execution_steps(summary):
    """Generate security-specific execution steps"""
    return """- Test authentication mechanisms with valid credentials
- Attempt access with invalid/expired credentials
- Verify authorization checks for different user roles
- Test input validation with malicious payloads
- Confirm session management works correctly"""

def generate_ui_execution_steps(summary):
    """Generate UI-specific execution steps"""
    return """- Navigate to the relevant page/component
- Interact with UI elements (buttons, forms, navigation)
- Test with valid and invalid user inputs
- Verify responsive behavior across screen sizes
- Test browser compatibility and accessibility features"""

def generate_unit_execution_steps(summary):
    """Generate unit test execution steps"""
    return """- Execute the function/method with valid inputs
- Test with edge cases and boundary conditions
- Test error conditions and exception handling
- Verify all code paths and business logic branches"""

def generate_validation_steps(ticket, test_category):
    """Generate validation steps"""
    steps = [
        "- Compare actual results with expected outcomes",
        "- Verify all success criteria are met",
        "- Check for any error conditions or unexpected behavior",
        "- Validate data integrity and system state"
    ]

    if test_category == 'integration':
        steps.append("- Confirm database changes are correct and complete")
    elif test_category == 'playwright':
        steps.append("- Verify UI state matches expected appearance and functionality")
    elif test_category == 'security':
        steps.append("- Confirm security measures are effective and no vulnerabilities exist")

    return "\n".join(steps)

def generate_pass_conditions(ticket, test_category):
    """Generate pass conditions"""
    conditions = []

    if test_category == 'integration':
        conditions.extend([
            "- [ ] API returns correct HTTP status codes for all test cases",
            "- [ ] Response data matches expected schema and content",
            "- [ ] Database operations complete successfully without errors",
            "- [ ] Error handling provides appropriate messages for invalid inputs"
        ])
    elif test_category == 'security':
        conditions.extend([
            "- [ ] Authentication prevents unauthorized access attempts",
            "- [ ] Authorization correctly enforces role-based permissions",
            "- [ ] Input validation blocks malicious content",
            "- [ ] No security vulnerabilities or data exposure detected"
        ])
    elif test_category == 'playwright':
        conditions.extend([
            "- [ ] UI functions correctly across all target browsers",
            "- [ ] User interactions produce expected results",
            "- [ ] Responsive design works on different screen sizes",
            "- [ ] Accessibility requirements are met (WCAG compliance)"
        ])
    else:  # unit
        conditions.extend([
            "- [ ] Function returns expected outputs for all valid inputs",
            "- [ ] Edge cases are handled without throwing unexpected errors",
            "- [ ] Business logic follows specified requirements exactly",
            "- [ ] Code coverage meets or exceeds project standards"
        ])

    return "\n".join(conditions)

def generate_fail_conditions(ticket, test_category):
    """Generate fail conditions"""
    conditions = [
        "- [ ] Any unexpected errors or exceptions occur during execution",
        "- [ ] Results differ from expected outcomes without valid explanation",
        "- [ ] System becomes unstable or unresponsive",
        "- [ ] Data integrity is compromised or corrupted"
    ]

    if test_category == 'security':
        conditions.append("- [ ] Security vulnerabilities or unauthorized access detected")
    elif test_category == 'playwright':
        conditions.append("- [ ] UI breaks or becomes unusable in any supported browser")
    elif test_category == 'integration':
        conditions.append("- [ ] API responses do not match OpenAPI specification")

    return "\n".join(conditions)

def generate_substeps(ticket, test_category):
    """Generate substeps for complex scenarios"""
    summary = ticket['fields']['summary'].lower()

    if 'delete' in summary:
        return """### Substep 1: Delete Existing Resource
- **Test**: Execute delete request for known existing resource
- **Expected**: HTTP 200/204 and resource removed from system
- **Pass Criteria**: Resource no longer accessible via GET request

### Substep 2: Delete Non-Existent Resource
- **Test**: Execute delete request for non-existent resource ID
- **Expected**: HTTP 404 Not Found with appropriate error message
- **Pass Criteria**: Clear error response without system impact"""

    elif any(method in summary for method in ['post', 'create']):
        return """### Substep 1: Valid Resource Creation
- **Test**: POST request with all required fields and valid data
- **Expected**: HTTP 201 Created with new resource data
- **Pass Criteria**: Resource accessible via GET and stored correctly

### Substep 2: Invalid Data Handling
- **Test**: POST request with missing or invalid required fields
- **Expected**: HTTP 400 Bad Request with validation error details
- **Pass Criteria**: No partial resource creation, clear error messaging"""

    else:
        return """### Substep 1: Happy Path Testing
- **Test**: Execute primary functionality with valid inputs
- **Expected**: Successful completion with expected results
- **Pass Criteria**: All outputs match specifications

### Substep 2: Error Path Testing
- **Test**: Execute with invalid or edge case inputs
- **Expected**: Appropriate error handling without system failure
- **Pass Criteria**: Graceful error handling with informative messages"""

def generate_evidence_requirements(test_category):
    """Generate evidence collection requirements"""
    base_evidence = [
        "- Request/response logs for all API calls made during testing",
        "- Screenshots of any error messages or unexpected behavior",
        "- Performance metrics if applicable (response times, resource usage)"
    ]

    if test_category == 'playwright':
        base_evidence.extend([
            "- Screenshots of UI state before/after test actions",
            "- Browser console logs for any JavaScript errors",
            "- Video recordings of user interaction flows"
        ])
    elif test_category == 'integration':
        base_evidence.extend([
            "- Database state before/after test execution",
            "- Complete HTTP request/response pairs",
            "- System logs showing backend processing"
        ])
    elif test_category == 'security':
        base_evidence.extend([
            "- Authentication attempt logs",
            "- Security scan results if applicable",
            "- Network traffic analysis for security testing"
        ])

    return "\n".join(base_evidence)

def generate_prediction(ticket, test_category):
    """Generate pre-test prediction"""
    summary = ticket['fields']['summary']

    if test_category == 'integration':
        return f"API endpoint for {summary} should respond correctly with proper status codes and expected data format"
    elif test_category == 'security':
        return f"Security mechanisms for {summary} should prevent unauthorized access and validate inputs properly"
    elif test_category == 'playwright':
        return f"UI functionality for {summary} should work consistently across browsers with good user experience"
    else:
        return f"Core functionality for {summary} should execute correctly with proper error handling"

def generate_expected_outcome(ticket, test_category):
    """Generate expected outcome"""
    if test_category == 'integration':
        return "All API calls return appropriate status codes, data format matches specifications, database operations complete successfully"
    elif test_category == 'security':
        return "Authentication/authorization works correctly, no security vulnerabilities detected, input validation effective"
    elif test_category == 'playwright':
        return "UI functions properly across browsers, user interactions work as designed, accessibility requirements met"
    else:
        return "Function executes correctly, edge cases handled properly, business logic implemented according to requirements"

def generate_troubleshooting_guide(ticket, test_category):
    """Generate troubleshooting guide"""
    guide = """### Common Issues and Solutions

**Issue**: Test environment not responding
- **Solution**: Verify services are running (make run-api, npm run dev)
- **Check**: Port availability (8080 for backend, 3001 for frontend)

**Issue**: Authentication failures
- **Solution**: Verify test user credentials (parent1@test.cmz.org / testpass123)
- **Check**: JWT token generation and .env.local configuration

**Issue**: Database connectivity problems
- **Solution**: Confirm DynamoDB tables exist with quest-dev-* naming
- **Check**: AWS credentials and region configuration (us-west-2)"""

    if test_category == 'playwright':
        guide += """

**Issue**: Browser test failures
- **Solution**: Update browser drivers, check Playwright configuration
- **Check**: Frontend application accessibility on localhost:3001"""

    return guide

def create_directory_structure(tickets):
    """Create test directory structure for all tickets"""
    categories = {}

    # Categorize all tickets
    for ticket in tickets:
        category = categorize_ticket(ticket)
        if category not in categories:
            categories[category] = []
        categories[category].append(ticket)

    # Create directories and files
    for category, ticket_list in categories.items():
        category_dir = Path(f'tests/{category}')
        category_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n📁 Creating {category.upper()} tests ({len(ticket_list)} tickets)")

        for ticket in ticket_list:
            key = ticket['key']
            ticket_dir = category_dir / key
            ticket_dir.mkdir(exist_ok=True)

            # Generate ADVICE.md
            advice_content = generate_advice_file(ticket, category)
            advice_file = ticket_dir / f"{key}-ADVICE.md"
            advice_file.write_text(advice_content)

            # Generate howto-test.md
            howto_content = generate_howto_test_file(ticket, category)
            howto_file = ticket_dir / f"{key}-howto-test.md"
            howto_file.write_text(howto_content)

            # Create empty history file
            history_file = ticket_dir / f"{key}-history.txt"
            history_file.write_text(f"# Test Execution History for {key}\n# Format: YYYY-MM-DD HH:MM:SS STATUS Brief-Description\n")

            print(f"  ✅ {key}: {ticket['fields']['summary'][:60]}{'...' if len(ticket['fields']['summary']) > 60 else ''}")

    return categories

def generate_summary_report(categories):
    """Generate summary report of all generated test specifications"""
    total_tickets = sum(len(tickets) for tickets in categories.values())

    report = f"""# TDD Test Specification Generation Summary

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Total Tickets Processed**: {total_tickets}

## Test Category Breakdown

"""

    for category, tickets in sorted(categories.items()):
        report += f"### {category.upper()} Tests ({len(tickets)} tickets)\n"
        report += f"**Directory**: `tests/{category}/`\n\n"

        for ticket in tickets:
            key = ticket['key']
            summary = ticket['fields']['summary']
            status = ticket['fields']['status']['name']
            report += f"- **{key}**: {summary} _(Status: {status})_\n"

        report += "\n"

    report += f"""## Files Generated Per Ticket

For each ticket, the following files are created:
- `{'{TICKET-KEY}'}-ADVICE.md` - Complete analysis and test strategy
- `{'{TICKET-KEY}'}-howto-test.md` - Step-by-step test execution instructions
- `{'{TICKET-KEY}'}-history.txt` - Test execution history tracking

## Directory Structure

```
tests/
├── integration/     # API endpoint and database integration tests
├── unit/           # Business logic and component unit tests
├── playwright/     # End-to-end UI and browser tests
└── security/       # Authentication and security validation tests
```

## Next Steps

1. **Review Generated Specifications**: Examine test specifications for accuracy and completeness
2. **Execute Sample Tests**: Validate the testing framework with a few representative tickets
3. **Refine Templates**: Update test templates based on execution feedback
4. **Begin Systematic Testing**: Execute tests for all tickets following the generated instructions

## Quality Metrics

- **Coverage**: All {total_tickets} tickets have comprehensive test specifications
- **Categorization**: Systematic categorization based on ticket content and type
- **Standardization**: Consistent format and structure across all test specifications
- **Traceability**: Clear mapping between Jira tickets and test specifications

## Integration with CMZ Project

- **Authentication**: Uses existing test users (parent1@test.cmz.org, etc.)
- **Infrastructure**: Leverages current Docker and DynamoDB setup
- **Endpoints**: Tests actual API endpoints at localhost:8080
- **Frontend**: Tests UI at localhost:3001 for Playwright scenarios

---

*Generated by CMZ TDD Framework v1.0*
*Sequential Reasoning Applied Throughout*
"""

    return report

def main():
    """Main execution function"""
    print("🎯 GENERATING COMPREHENSIVE TDD TEST SPECIFICATIONS")
    print("=" * 55)
    print("")

    # Load all tickets
    print("📥 Loading ticket data...")
    tickets = load_tickets()
    print(f"✅ Loaded {len(tickets)} tickets from Jira data")

    # Create directory structure and generate files
    print("\n🏗️ Creating test specifications...")
    categories = create_directory_structure(tickets)

    # Generate summary report
    print(f"\n📊 Generating summary report...")
    summary_report = generate_summary_report(categories)

    # Save summary report
    summary_file = Path('tests/TDD-GENERATION-SUMMARY.md')
    summary_file.write_text(summary_report)
    print(f"✅ Summary report saved: {summary_file}")

    print(f"\n🎉 GENERATION COMPLETE!")
    print("=" * 55)
    print(f"📊 Total tickets processed: {len(tickets)}")
    print(f"📁 Test categories created: {len(categories)}")

    for category, ticket_list in sorted(categories.items()):
        print(f"   - {category.upper()}: {len(ticket_list)} tickets")

    print(f"\n📂 All files created in: tests/ directory")
    print(f"📋 Summary report: tests/TDD-GENERATION-SUMMARY.md")
    print("\n✅ Ready to begin systematic TDD testing!")

if __name__ == "__main__":
    main()